#!/usr/bin/env python3
"""One source-faithful masked occurrence census; capacity, not an outcome test."""
import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
MASK_COLUMNS = ['occurrence_id','edition','page','leaf','locus','source_group_index','family_id','body_json','left_json','right_json','primary_certain']
LAYOUT_COLUMNS = ['occurrence_id','edition','family_id','line_final','hand','segment_id','window_start','window_end']
PAIR_COLUMNS = ['edition','family_id','occurrence_1','occurrence_2','same_known_hand','primary_certain']
COMP_COLUMNS = ['edition','component_id','families_json','leaves_json','selected_pair_json']


def need(value, message):
    if not value:
        raise ValueError(message)


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(data):
    return hashlib.sha256(data.encode()).hexdigest()


def table(rows, columns):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=columns, delimiter='\t', lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue()


def atoms(raw):
    """Return lossless opaque or character atoms with raw half-open offsets."""
    result = []; i = 0; closing = {'[':']', '{':'}', '<':'>'}
    while i < len(raw):
        start = i
        if raw[i] == '@':
            match = re.match(r'@\d+;', raw[i:])
            need(match is not None, 'Malformed extended entity')
            i += len(match.group())
        elif raw[i] in closing:
            stack = [closing[raw[i]]]; i += 1
            while i < len(raw) and stack:
                char = raw[i]
                if char in closing:
                    stack.append(closing[char])
                elif char in ']}>':
                    need(char == stack[-1], 'Mismatched opaque delimiter')
                    stack.pop()
                i += 1
            need(not stack, 'Unclosed opaque atom')
        else:
            need(raw[i] not in ']}>', 'Unexpected closing delimiter')
            i += 1
        result.append((raw[start:i], start, i))
    need(''.join(x[0] for x in result) == raw, 'Lossy atomization')
    return result


def query(spec):
    argv = ['./vmanus-exp','query-tsv',spec['source_atlas'],'--selector','page']
    for page in spec['allowed_selectors']:
        argv += ['--allow',page]
    argv += ['--columns',','.join(spec['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
    proc = subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,check=True)
    guards = [json.loads(x.removeprefix('GUARD_STATS ')) for x in proc.stderr.splitlines() if x.startswith('GUARD_STATS ')]
    reader = csv.DictReader(io.StringIO(proc.stdout),delimiter='\t')
    need(reader.fieldnames == spec['columns'] and len(guards) == 1,'Guard schema')
    rows = list(reader)
    need(len(rows) == guards[0]['selected'],'Guard count')
    need({r['page'] for r in rows} <= set(spec['allowed_selectors']),'Scope')
    need(not any(r['page'].startswith('f84') for r in rows),'Sealed page')
    return rows, dict(command=argv,stats=guards[0],projection_sha256=digest(proc.stdout))


def records(rows):
    grouped = defaultdict(list)
    seen = set()
    for row in rows:
        need(row['source_group_id'] not in seen,'Duplicate source group')
        seen.add(row['source_group_id'])
        grouped[(row['edition'],row['locus'])].append(row)
    output = {}
    metadata = ['page','section','currier','hand','code','kind','source_row_index','paragraph_start','paragraph_end','source_group_count']
    for key, groups in grouped.items():
        groups.sort(key=lambda r:int(r['source_group_index']))
        need([int(g['source_group_index']) for g in groups] == list(range(1,len(groups)+1)),'Group indices')
        need(all(int(g['source_group_count']) == len(groups) for g in groups),'Group count')
        need(all(all(g[k] == groups[0][k] for k in metadata) for g in groups),'Line metadata')
        need(groups[0]['left_separator'] == 'LINE_START' and groups[-1]['right_separator'] == 'LINE_END','Line boundaries')
        need(all(a['right_separator'] == b['left_separator'] for a,b in zip(groups,groups[1:])),'Gap adjacency')
        output[key] = dict(groups[0], groups=groups)
    return output


def adjacent(a,b):
    if a['page'] != b['page'] or int(b['source_row_index']) != int(a['source_row_index'])+1:
        return False
    x = re.fullmatch(r'(.+)\.(\d+)',a['locus']); y = re.fullmatch(r'(.+)\.(\d+)',b['locus'])
    return bool(x and y and x[1] == y[1] and int(y[2]) == int(x[2])+1)


def scaffold(recs):
    bypage = defaultdict(list); segments = []; stats = Counter()
    for (edition,locus), record in recs.items():
        if edition == 'ZL3b':
            bypage[record['page']].append(record)
    for page in sorted(bypage):
        pending = None
        for record in sorted(bypage[page], key=lambda r:int(r['source_row_index'])):
            if record['kind'] == 'P' and record['paragraph_start'] == '1':
                if pending is not None:
                    stats['unclosed_paragraphs'] += 1
                pending = []
            if pending is None:
                stats['records_outside_bounded_start'] += 1
                continue
            pending.append(record)
            if record['kind'] == 'P' and record['paragraph_end'] == '1':
                stats['bounded_paragraphs'] += 1
                segment = []
                for item in pending:
                    if item['kind'] != 'P':
                        if segment: segments.append(segment); segment = []
                        stats['non_P_barriers'] += 1
                        continue
                    if segment and not adjacent(segment[-1],item):
                        segments.append(segment); segment = []
                        stats['nonadjacency_barriers'] += 1
                    segment.append(item)
                if segment: segments.append(segment)
                pending = None
        if pending is not None:
            stats['unclosed_paragraphs'] += 1
    stats['scaffold_segments'] = len(segments)
    stats['scaffold_P_records'] = sum(map(len,segments))
    return segments,dict(sorted(stats.items()))


def edition_segments(recs, base, edition):
    output = []; stats = Counter()
    for segment in base:
        records_here = [recs.get((edition,r['locus'])) for r in segment]
        if any(r is None or r['kind'] != 'P' for r in records_here):
            stats['missing_or_non_P_segments'] += 1
            continue
        if any(not adjacent(a,b) for a,b in zip(records_here,records_here[1:])):
            stats['nonadjacent_native_segments'] += 1
            continue
        stats['paragraph_marker_disagreements'] += sum((r['paragraph_start'],r['paragraph_end']) != (z['paragraph_start'],z['paragraph_end']) for r,z in zip(records_here,segment))
        output.append(records_here)
    stats['retained_segments'] = len(output)
    stats['retained_P_records'] = sum(map(len,output))
    return output,dict(sorted(stats.items()))


def streams(segment):
    chunks = []; groups = []; gaps = []
    for line in segment:
        for group in line['groups']:
            if groups:
                separator = group['left_separator']
                if separator.startswith('DRAWING_INTERRUPTION'):
                    chunks.append((groups,gaps)); groups = []; gaps = []
                else:
                    need(separator in ['LINE_START','DEFINITE_SPACE','UNCERTAIN_SMALL_SPACE'],'Unknown gap kind')
                    gaps.append('GAP' if separator != 'UNCERTAIN_SMALL_SPACE' else separator)
            groups.append(group)
    if groups: chunks.append((groups,gaps))
    return chunks


def occurrences(segments, edition, flank):
    found = []; layouts = {}; stats = Counter()
    for segment in segments:
        for groups,gaps in streams(segment):
            stats['drawing_split_streams'] += 1
            sid = edition + ':' + groups[0]['source_group_id'] + '--' + groups[-1]['source_group_id']
            tokens = []; targets = []
            for i, group in enumerate(groups):
                if i: tokens.append(('g',gaps[i-1]))
                parsed = atoms(group['ivtff_group_raw'])
                values = [a[0] for a in parsed]
                tokens += [('a',a) for a in values]
                if len(values) >= 2 and values[-1] in ['l','m']:
                    targets.append((len(tokens)-1,group,values[:-1]))
                    stats['eligible_literal_terminals_before_flanks'] += 1
            for target,group,body in targets:
                left = target-1; n = 0
                while left >= 0:
                    n += tokens[left][0] == 'a'
                    if n == flank: break
                    left -= 1
                if n != flank:
                    stats['insufficient_left_flank'] += 1; continue
                right = target+1; n = 0
                while right < len(tokens):
                    n += tokens[right][0] == 'a'
                    if n == flank: break
                    right += 1
                if n != flank:
                    stats['insufficient_right_flank'] += 1; continue
                ls = tokens[left:target]; rs = tokens[target+1:right+1]
                signature = dict(body=body,left=ls,right=rs)
                family = digest(compact(signature))
                certain = all(re.fullmatch(r'[A-Za-z]|@\d+;',a) for a in body)
                certain = certain and all((kind == 'a' and re.fullmatch(r'[A-Za-z]|@\d+;',a)) or (kind == 'g' and a == 'GAP') for kind,a in ls+rs)
                leaf_match = re.match(r'f\d+',group['page']); need(leaf_match,'Folio leaf key')
                oid = group['source_group_id']
                found.append(dict(occurrence_id=oid,edition=edition,page=group['page'],leaf=leaf_match[0],locus=group['locus'],source_group_index=group['source_group_index'],family_id=family,body_json=compact(body),left_json=compact(ls),right_json=compact(rs),primary_certain=int(bool(certain))))
                layouts[oid] = dict(occurrence_id=oid,edition=edition,family_id=family,line_final=int(group['source_group_index'] == group['source_group_count']),hand=group['hand'],segment_id=sid,window_start=left,window_end=right)
    found.sort(key=lambda r:r['occurrence_id'])
    need(len(found) == len({r['occurrence_id'] for r in found}),'Duplicate window')
    stats['complete_masked_windows'] = len(found)
    return found,layouts,dict(sorted(stats.items()))


def capacity(masked, layouts, spec):
    family = defaultdict(list)
    for row in masked: family[(row['edition'],row['family_id'])].append(row)
    family = {key:rows for key,rows in family.items() if len(rows) > 1}
    recurrent = sorted((row for rows in family.values() for row in rows),key=lambda r:r['occurrence_id'])
    pairs = []
    for (edition,fid),rows in sorted(family.items()):
        for a,b in itertools.combinations(sorted(rows,key=lambda r:r['occurrence_id']),2):
            la,lb = layouts[a['occurrence_id']],layouts[b['occurrence_id']]
            if la['line_final'] == lb['line_final']: continue
            known = la['hand'] == lb['hand'] and la['hand'] not in spec['known_hand_exclusions']
            pairs.append(dict(edition=edition,family_id=fid,occurrence_1=a['occurrence_id'],occurrence_2=b['occurrence_id'],same_known_hand=int(known),primary_certain=int(a['primary_certain'] and b['primary_certain'])))
    components = []; byedition = {}
    for edition in spec['editions']:
        ef = {fid:rows for (ed,fid),rows in family.items() if ed == edition}
        parent = {fid:fid for fid in ef}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        leafowner = {}
        for fid, rows in sorted(ef.items()):
            for row in rows:
                leaf = row['leaf']
                if leaf in leafowner: parent[find(fid)] = find(leafowner[leaf])
                leafowner[leaf] = fid
        blocks = defaultdict(list)
        for fid in ef: blocks[find(fid)].append(fid)
        ep = [p for p in pairs if p['edition'] == edition]
        for number,fids in enumerate(sorted(sorted(fs) for fs in blocks.values()),1):
            leaves = sorted({r['leaf'] for fid in fids for r in ef[fid]})
            eligible = sorted((p['family_id'],p['occurrence_1'],p['occurrence_2']) for p in ep if p['family_id'] in fids and p['same_known_hand'] and p['primary_certain'])
            components.append(dict(edition=edition,component_id=f'{edition}:C{number:04d}',families_json=compact(fids),leaves_json=compact(leaves),selected_pair_json=compact(eligible[0] if eligible else [])))
        u = sum(bool(json.loads(c['selected_pair_json'])) for c in components if c['edition'] == edition)
        byedition[edition] = dict(masked_occurrences=sum(r['edition'] == edition for r in masked),recurrent_families=len(ef),recurrent_occurrences=sum(len(x) for x in ef.values()),cross_layout_pairs=len(ep),same_known_hand_certain_pairs=sum(p['same_known_hand'] and p['primary_certain'] for p in ep),components=len(blocks),independent_primary_upper_bound=u,status='CAPACITY_FAIL_UPPER_BOUND' if u < 32 else 'POTENTIALLY_FEASIBLE_ONLY')
    return recurrent,pairs,components,byedition


def exact_power(n):
    cut = next((k for k in range(n//2+1,n+1) if 2*sum(math.comb(n,j) for j in range(k,n+1))/2**n <= .01),None)
    if cut is None: return dict(n=n,upper_critical=None,size=0.0,power=0.0)
    tails = [j for j in range(n+1) if j >= cut or j <= n-cut]
    return dict(n=n,upper_critical=cut,size=sum(math.comb(n,j) for j in tails)/2**n,power=sum(math.comb(n,j)*4**j for j in tails)/5**n)


def publish(path,content,check):
    if check: need(path.read_text() == content,'Replay differs: '+path.name)
    else: path.write_text(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check',action='store_true'); args = parser.parse_args()
    spec = json.loads((EXP/'src/SPEC.json').read_text())
    lock = json.loads((EXP/'src/PREREG_LOCK.json').read_text())
    for path,expected in lock.items(): need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected,'Preregistration drift')
    need(len(spec['allowed_selectors']) == len(set(spec['allowed_selectors'])) == 179,'Allowlist size')
    rows,guard = query(spec); recs = records(rows); base,scaffold_stats = scaffold(recs)
    masked = []; layouts = {}; edition_stats = {}
    for edition in spec['editions']:
        segments,es = edition_segments(recs,base,edition)
        windows,wl,ws = occurrences(segments,edition,spec['flank_atoms'])
        masked += windows; layouts.update(wl); edition_stats[edition] = dict(scaffold=es,extraction=ws)
    masked.sort(key=lambda r:r['occurrence_id'])
    freq = Counter((r['edition'],r['family_id']) for r in masked)
    recurrent = [r for r in masked if freq[(r['edition'],r['family_id'])] > 1]
    # Persist/hash the entire outcome- and finality-masked selection BEFORE layout pairing.
    frozen = {'MASKED_OCCURRENCES.tsv':table(masked,MASK_COLUMNS),'RECURRENT_CONTEXTS.tsv':table(recurrent,MASK_COLUMNS)}
    for name,content in frozen.items(): publish(EXP/'artifacts'/name,content,args.check)
    freeze = dict(preregistration_hashes=lock,selection_hashes={name:digest(content) for name,content in frozen.items()},target_outcomes_exposed=False,cryptographic_blinding=False,line_finality_exposed=False)
    publish(EXP/'artifacts/MASKED_FREEZE.json',json.dumps(freeze,indent=2,sort_keys=True)+'\n',args.check)
    # Geometry only: l/m values are not passed to this capacity computation.
    recurrent2,pairs,components,counts = capacity(masked,layouts,spec)
    need(recurrent == recurrent2,'Selection changed at layout release')
    selected_layout = [layouts[r['occurrence_id']] for r in recurrent]
    result = dict(experiment_id='GDT829',status=counts['ZL3b']['status'],stage=spec['stage'],source_groups=len(rows),source_records=len(recs),guarded_query=guard,scaffold=scaffold_stats,edition_details=edition_stats,by_edition=counts,power_design=[exact_power(n) for n in [29,30,31,32,33,34]],selection_hashes=freeze['selection_hashes'],target_outcomes_exposed=False,cryptographic_blinding=False,direction_test_run=False,new_admissions=0,confirmed_lexemes=0,sealed_data=spec['sealed_data'],alternate_readings_independent=False)
    outputs={'LAYOUT.tsv':table(selected_layout,LAYOUT_COLUMNS),'PAIRS.tsv':table(pairs,PAIR_COLUMNS),'COMPONENTS.tsv':table(components,COMP_COLUMNS),'RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}
    for name,content in outputs.items(): publish(EXP/'artifacts'/name,content,args.check)
    print(compact(dict(status=result['status'],scaffold=scaffold_stats,by_edition=counts,target_outcomes_exposed=False)))


if __name__ == '__main__':
    main()
