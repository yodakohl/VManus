#!/usr/bin/env python3
"""Independent GDT1037 audit. Synthetic-only unless explicitly --execute.

No primary program is read or imported. Hash verification treats bound programs
as opaque bytes. Real paragraph content is accessed only after public lock audit.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = Path(__file__).resolve().parents[1]
STATES = ('LINE_START', 'PREV_DY', 'OTHER')
PANELS = ('RAW_EXACT', 'LITERAL_LINES')
SHARED = ['aiin','al','chedy','cheey','chey','daiin','dal','or','qokeedy','qokey','qoky','shedy','y']

class Invalid(Exception):
    pass

def need(ok, reason):
    if not ok:
        raise Invalid(reason)

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def same(actual, expected, where='root'):
    need(type(actual) is type(expected), where+': type differs')
    if isinstance(expected, dict):
        need(actual.keys() == expected.keys(), where+': keys differ')
        for k in expected:
            same(actual[k], expected[k], where+'.'+str(k))
    elif isinstance(expected, list):
        need(len(actual) == len(expected), where+': length differs')
        for i,(a,b) in enumerate(zip(actual,expected)):
            same(a,b,where+f'[{i}]')
    else:
        need(actual == expected, where+': '+repr(actual)+' != '+repr(expected))

def git(*args):
    result = subprocess.run(['git',*args], cwd=ROOT, capture_output=True, check=False)
    need(result.returncode == 0, 'git verification failed: '+' '.join(args[:2]))
    return result.stdout

def public_lock(spec):
    lockpath = EXP/'PREREG_LOCK.json'
    lockbytes = lockpath.read_bytes()
    lock = json.loads(lockbytes)
    receipt = load(EXP/'artifacts/PUBLIC_REGISTRATION.json')
    commit = receipt['public_commit']
    need(isinstance(commit,str) and re.fullmatch('[0-9a-f]{40}',commit), 'public commit shape')
    need(receipt['lock_sha256'] == sha(lockbytes), 'receipt lock hash')
    need(isinstance(receipt['verified_utc'],str) and receipt['verified_utc'], 'receipt verification time')
    rel = lockpath.relative_to(ROOT).as_posix()
    need(git('show',commit+':'+rel) == lockbytes, 'public committed lock differs')
    registration = spec['registration']
    remote = git('ls-remote',registration['remote'],registration['public_ref']).decode().splitlines()
    refs = [x.split() for x in remote if x.strip()]
    need(len(refs) == 1 and refs[0][1] == registration['public_ref'], 'public main ref unavailable')
    tip = refs[0][0]
    need(re.fullmatch('[0-9a-f]{40}',tip), 'public ref hash malformed')
    git('merge-base','--is-ancestor',commit,tip)
    expected = {spec['packet']['path']:spec['packet']['sha256']}
    expected.update({r['path']:r['sha256'] for r in spec['records']})
    expected.update({r['path']:r['sha256'] for r in spec['bound_metadata']})
    required = set(expected)
    required.update((EXP/p).relative_to(ROOT).as_posix() for p in registration['required_experiment_files'])
    need(required <= set(lock['files']), 'required files absent from public lock')
    for name, digest in lock['files'].items():
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts, 'unsafe lock path')
        content = (ROOT/path).read_bytes()
        need(sha(content) == digest, 'local lock hash '+name)
        need(sha(git('show',commit+':'+name)) == digest, 'committed lock hash '+name)
        if name in expected:
            need(digest == expected[name], 'SPEC hash differs '+name)
    registration_result = dict(public_commit=commit,
        lock_sha256=sha(lockbytes),verified_utc=receipt['verified_utc'],
        remote_reachability_verified=True,all_locked_current_and_commit_hashes_verified=True)
    return registration_result, len(lock['files'])

def entries_from_sources(spec):
    docs = {r['section']:load(ROOT/r['path']) for r in spec['records']}
    old = docs['II']['lexicon']
    new = docs['III']['new_lexicon']
    need(len(old) == 36 and len(new) == 31, 'A source entry counts')
    A = {e['form']:dict(e) for e in old+new}
    need(len(A) == 67, 'duplicate A form')
    change = docs['III']['explicit_new_branch_before_any_semantic_test']['changed_entry']
    need(change['form'] == 'qoky', 'qoky amendment selector')
    for key in ('value','type','denotation'):
        A['qoky'][key] = change['new_'+key]
    parent = docs['V']['frozen_parent_lexicon']
    same({e['form']:e for e in parent},{e['form']:e for e in docs['IV']['lexicon']},'38 B inherited entries')
    need(len(parent) == 38 and len(docs['V']['new_lexicon']) == 21, 'B source entry counts')
    B = {e['form']:dict(e) for e in parent+docs['V']['new_lexicon']}
    need(len(B) == 59, 'duplicate B form')
    entries = {'A':A,'B':B}
    need(sorted(set(A)&set(B)) == SHARED == spec['semantic_conflict_forms'], 'complete13 semantic conflicts')
    need(len(set(A)|set(B)) == 113, '113 whole forms')
    for family in entries:
        for form,entry in entries[family].items():
            need(entry['form'] == form, 'entry form mismatch')
            need(all(isinstance(entry.get(k),str) and entry[k] for k in ('value','type','denotation')), 'incomplete typed entry')
    review = load(ROOT/spec['semantic_review']['receipt'])
    need(review['intersection'] == 13 and review['union'] == 113, 'semantic review scope')
    same(review['inputs'],{r['path']:r['sha256'] for r in spec['records']},'semantic receipt hashes')
    need([x['form'] for x in review['rows']] == SHARED, 'semantic receipt all shared forms')
    for row in review['rows']:
        for family in ('A','B'):
            same(row[family],{k:entries[family][row['form']][k] for k in ('value','type','denotation')},'semantic reviewed fixed entry')
        need(row['literal_fields_identical'] is False, 'review identity flag')
    return entries,docs

def selector_guard(page,leaf):
    need(isinstance(page,str) and not page.startswith('f84') and page != 'f116v', 'forbidden page')
    match = re.fullmatch(r'f([0-9]+)[rv][0-9]*',page)
    need(match is not None and type(leaf) is int and int(match.group(1)) == leaf, 'page/leaf mismatch')

def context(index, words):
    if index == 0:
        return 'LINE_START',True,False,None
    previous = words[index-1]
    isdy = previous.endswith('dy')
    return ('PREV_DY' if isdy else 'OTHER'),False,isdy,previous

def paragraph_positions(p):
    # Guard raw selectors before accessing any line contents.
    selector_guard(p['page'],p['leaf'])
    lines = p['lines']
    need(lines and p['id'] == p['page']+'|'+lines[0]['locus']+'-'+lines[-1]['locus'], 'complete paragraph boundary')
    out = []
    for line in lines:
        need(line['locus'].startswith(p['page']+'.'), 'line selector')
        need(type(line['offset']) is int and line['offset'] == len(out), 'original line offset')
        words,ids = line['words'],line['source_ids']
        need(len(words) == len(ids) and all(isinstance(w,str) for w in words), 'line groups/IDs')
        need(ids == [f"ZL3b|{line['locus']}|G{i+1:03d}" for i in range(len(words))], 'original IDs')
        flag = line.get('anchor_eligible')
        if flag is True:
            need(all(re.fullmatch('[a-z]+',w) for w in words), 'literal flag/nonliteral group disagreement')
        for i,word in enumerate(words):
            state,first,dy,prev = context(i,words)
            out.append(dict(word=word,source_id=ids[i],locus=line['locus'],line_position=i+1,
                            position=len(out)+1,anchor_eligible=flag,context=state,
                            line_start=first,prev_literal_dy=dy,predecessor_raw=prev))
    need(type(p['groups']) is int and p['groups'] == len(out), 'whole paragraph count')
    need(len({x['source_id'] for x in out}) == len(out), 'duplicate source IDs')
    return out

def reconstruct_scope(spec,entries,docs,packet):
    need(set(packet) == {'ZL3b','IT2a','RF1b'}, 'packet reader schema')
    # Only metadata is inspected to select the already frozen four paragraphs.
    by_id = {}
    for p in packet['ZL3b']:
        need(p['id'] not in by_id, 'duplicate paragraph ID')
        by_id[p['id']] = p
    scope = []
    for rec in spec['records']:
        section,family = rec['section'],rec['family']
        need(rec['paragraph'] in by_id, 'fixed paragraph missing')
        p = by_id[rec['paragraph']]
        positions = paragraph_positions(p)
        receipt = docs[section][rec['receipt']]
        need(len(positions) == len(receipt) == rec['groups'], 'complete receipt length '+section)
        need([x['position'] for x in receipt] == list(range(1,rec['groups']+1)), 'receipt index sequence')
        physical_lines = {line['locus']:i+1 for i,line in enumerate(p['lines'])}
        rows = []
        for pos,source in zip(positions,receipt):
            form = source.get('form',source.get('raw_form'))
            need(form == pos['word'] and form in entries[family], 'whole literal receipt identity '+section)
            entry = entries[family][form]
            need(source['value'] == entry['value'], 'receipt fixed value '+section)
            for key in ('source_id','locus'):
                if key in source:
                    need(source[key] == pos[key], 'receipt identity '+key)
            rows.append(dict(section=section,family=family,paragraph=p['id'],page=p['page'],
                locus=pos['locus'],physical_line_index=physical_lines[pos['locus']],
                index_in_line=pos['line_position'],paragraph_position=pos['position'],
                source_id=pos['source_id'],raw=form,predecessor_raw=pos['predecessor_raw'],
                anchor_eligible=pos['anchor_eligible'],state=pos['context'],
                context=dict(LINE_START=pos['line_start'],PREV_LITERAL_DY=pos['prev_literal_dy']),
                fixed_entry={k:entry[k] for k in ('value','type','denotation')}))
        scope.append(dict(section=section,family=family,paragraph=p['id'],page=p['page'],
                          leaf=p['leaf'],groups=p['groups'],positions=rows))
    flat = [r for p in scope for r in p['positions']]
    need(len(flat) == 183 and len({r['source_id'] for r in flat}) == 183, '183 unique positions')
    need(Counter(r['family'] for r in flat) == {'A':95,'B':88}, 'family position counts')
    for family in ('A','B'):
        need({r['raw'] for r in flat if r['family'] == family} == set(entries[family]), 'complete family form inventory')
    return scope

def context_features(state):
    need(state in STATES, 'unknown context state')
    return dict(LINE_START=state == 'LINE_START',PREV_LITERAL_DY=state == 'PREV_DY')

def build_cells(rows,forms,conflicts,panel):
    selected = [row for row in rows if panel == 'RAW_EXACT' or row['anchor_eligible'] is True]
    buckets = {}
    for row in selected:
        key = (row['raw'],row['state'],row['family'])
        buckets.setdefault(key,[]).append(row['source_id'])
    output = []
    for form in sorted(forms):
        for state in STATES:
            a = buckets.get((form,state,'A'),[])
            b = buckets.get((form,state,'B'),[])
            conflict = form in conflicts
            output.append(dict(form=form,state=state,context=context_features(state),
                A_count=len(a),B_count=len(b),A_source_ids=a,B_source_ids=b,
                semantic_pair_conflict=conflict,collision=bool(a and b and conflict)))
    return output

def products(scope,entries,spec,registration):
    rows = [r for p in scope for r in p['positions']]
    forms = set(entries['A'])|set(entries['B'])
    all_cells,shared,collisions,panels = {},{},{},{}
    for panel in PANELS:
        cells = build_cells(rows,forms,set(SHARED),panel)
        all_cells[panel] = cells
        shared[panel] = [cell for cell in cells if cell['semantic_pair_conflict']]
        collision_rows = []
        for cell in cells:
            if not cell['collision']:
                continue
            x = dict(cell)
            for family in ('A','B'):
                x[family+'_entry'] = {k:entries[family][cell['form']][k] for k in ('value','type','denotation')}
            x['cross_family_pairs'] = [dict(A_source_id=a,B_source_id=b)
                for a in cell['A_source_ids'] for b in cell['B_source_ids']]
            collision_rows.append(x)
        collisions[panel] = collision_rows
        chosen = [r for r in rows if panel == 'RAW_EXACT' or r['anchor_eligible'] is True]
        counts = Counter(r['family'] for r in chosen)
        if panel == 'RAW_EXACT':
            decision = 'REFUTED_FIXED_CONTEXT_JOIN' if collision_rows else 'COMPATIBLE_FIXED_CONTEXT_TABLE'
        else:
            decision = 'REFUTED_FIXED_CONTEXT_JOIN_ON_LITERAL_LINES' if collision_rows else 'NO_LITERAL_CONFLICT_NOT_FULL_CODE'
        panels[panel] = dict(positions=len(chosen),A_positions=counts['A'],B_positions=counts['B'],
            fixed_form_denominator=113,fixed_shared_form_denominator=13,context_cell_denominator=339,
            shared_context_cell_denominator=39,collision_cells=len(collision_rows),
            colliding_forms=sorted({c['form'] for c in collision_rows}),
            cross_family_collision_pairs=sum(len(c['cross_family_pairs']) for c in collision_rows),decision=decision)
    result = dict(experiment='GDT1037',panels=panels,source_positions=dict(A=95,B=88),
        source_forms=dict(A=67,B=59,union=113,shared=13),states=list(STATES),registration=registration,
        confirmed_words=0,independent_meaning_capacity=0,semantic_inequality_basis=spec['semantic_review'],
        significance_claim=False)
    return {'SCOPE.json':scope,'ENTRIES.json':entries,'ALL_CONTEXT_CELLS.json':all_cells,
            'SHARED_CONTEXT_CELLS.json':shared,'COLLISIONS.json':collisions,'RESULT.json':result}

def self_test():
    checks = 0
    def check(condition,label):
        nonlocal checks
        need(condition,'synthetic '+label)
        checks += 1
    variants = ['dy','chdy','?dy','@163;dy','adyx','DY','dY','dy ','@100;','']
    for word in variants:
        for before in ('x','dy'):
            words = [before,word,'z']
            state,first,dy,prev = context(2,words)
            check((state,first,dy,prev) == ('PREV_DY' if word[-2:] == 'dy' else 'OTHER',False,word[-2:] == 'dy',word),'literal suffix')
    check(context(0,['dy']) == ('LINE_START',True,False,None),'first resets')
    p = dict(id='f1r|f1r.1-f1r.2',page='f1r',leaf=1,groups=3,lines=[
        dict(locus='f1r.1',anchor_eligible=False,offset=0,words=['?dy'],source_ids=['ZL3b|f1r.1|G001']),
        dict(locus='f1r.2',anchor_eligible=True,offset=1,words=['x','y'],source_ids=['ZL3b|f1r.2|G001','ZL3b|f1r.2|G002'])])
    positions = paragraph_positions(p)
    check([r['context'] for r in positions] == ['LINE_START','LINE_START','OTHER'],'physical line seam')
    check(positions[1]['predecessor_raw'] is None,'no previous line leakage')
    class Poison(dict):
        def __getitem__(self,key):
            if key == 'lines':
                raise AssertionError('sealed contents touched')
            return super().__getitem__(key)
    for page,leaf in [('f84',84),('f84r',84),('f84v',84),('f116v',116)]:
        try:
            paragraph_positions(Poison(page=page,leaf=leaf))
        except Invalid:
            check(True,'sealed selector before words')
        else:
            check(False,'sealed accepted')
    for flag in (True,False,None,1,'True'):
        rows = [dict(raw='x',state='OTHER',family='A',source_id='a',anchor_eligible=True),
                dict(raw='x',state='OTHER',family='B',source_id='b',anchor_eligible=flag)]
        raw = build_cells(rows,['x','zero'],{'x'},'RAW_EXACT')
        literal = build_cells(rows,['x','zero'],{'x'},'LITERAL_LINES')
        check(len(raw) == 6 and raw[2]['collision'] is True,'all states and zero forms')
        check(literal[2]['collision'] is (flag is True),'literal exact boolean')
    rows = [dict(raw='x',state='LINE_START',family='A',source_id='a',anchor_eligible=True),
            dict(raw='x',state='OTHER',family='B',source_id='b',anchor_eligible=True)]
    check(not any(x['collision'] for x in build_cells(rows,['x'],{'x'},'RAW_EXACT')),'different context separates')
    rows[1]['state'] = 'LINE_START'
    check(not any(x['collision'] for x in build_cells(rows,['x'],set(),'RAW_EXACT')),'unreviewed label not semantic conflict')
    return dict(status='PASS',synthetic_checks=checks,target_data_read=False)

def execute():
    spec = load(EXP/'src/SPEC.json')
    need(spec['experiment'] == 'GDT1037', 'experiment identity')
    same([r['id'] for r in spec['context']['states']],list(STATES),'fixed state order')
    same([(r['section'],r['family'],r['groups']) for r in spec['records']],
         [('II','A',49),('III','A',46),('IV','B',55),('V','B',33)],'fixed complete scope')
    registration,locks = public_lock(spec)
    entries,docs = entries_from_sources(spec)
    packet = load(ROOT/spec['packet']['path'])
    scope = reconstruct_scope(spec,entries,docs,packet)
    expected = products(scope,entries,spec,registration)
    same(spec['output_files'],list(expected),'complete artifact list')
    for filename,value in expected.items():
        same(load(EXP/'artifacts'/filename),value,filename)
    return dict(status='PASS',success=True,reasons=[],experiment='GDT1037',locked_files=locks,
        public_commit=registration['public_commit'],positions=183,forms=113,shared_forms=13,
        panels=expected['RESULT.json']['panels'],artifacts_verified=list(expected),
        independent_reconstruction=True,primary_code_read_or_imported=False,
        confirmed_words=0,independent_meaning_capacity=0,significance_claim=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--self-test',action='store_true')
    mode.add_argument('--execute',action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),sort_keys=True))
        return 0
    try:
        result = execute()
    except Exception as exc:
        result = dict(status='FAIL',success=False,reasons=[type(exc).__name__+': '+str(exc)],
                      experiment='GDT1037',confirmed_words=0,independent_meaning_capacity=0)
    output = EXP/'artifacts/VALIDATION.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,sort_keys=True))
    return 0 if result['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
