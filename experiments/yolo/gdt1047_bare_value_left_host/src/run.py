#!/usr/bin/env python3
"""Fixed source-marked boundary capacity; no words are translated."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
SOURCE = 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
ALLOW = 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
OLD = ['experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv',
       'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv']
COLUMNS = ['source_group_id','edition','page','locus','source_row_index',
           'source_group_index','source_group_count','kind','paragraph_start',
           'paragraph_end','left_separator','right_separator','ivtff_group_raw']
INVENTORIES = {'FAMILY': ['dan','dain','daiin','daiiin'], 'DAIIN':['daiin'], 'AIIN':['aiin']}
EDITIONS = ['ZL3b','IT2a','RF1b']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path):
    with (ROOT / path).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def check_lock():
    lock = json.loads((EXP / 'src/PREREG_LOCK.json').read_text())
    for item in lock['fixed_files'] + lock['inputs']:
        if sha(ROOT / item['path']) != item['sha256']:
            raise ValueError('Frozen input changed: ' + item['path'])
    return lock


def project(pages, fetch):
    runtime = EXP / 'runtime'
    runtime.mkdir(exist_ok=True)
    path = runtime / 'PROJECTION.tsv'
    receipt = runtime / 'PROJECTION_RECEIPT.json'
    if fetch or not path.exists():
        command = ['./vmanus-exp','query-tsv',SOURCE,'--selector','page']
        for page in pages:
            command += ['--allow', page]
        command += ['--columns', ','.join(COLUMNS),'--forbid-prefix','f84','--forbid-prefix','f84r']
        proc = subprocess.run(command,cwd=ROOT,capture_output=True,check=True)
        stats = [json.loads(line[12:]) for line in proc.stderr.decode().splitlines()
                 if line.startswith('GUARD_STATS ')]
        assert len(stats) == 1
        path.write_bytes(proc.stdout)
        receipt.write_text(json.dumps({'command':command,'stats':stats[0],
                                      'projection_sha256':sha(path)},indent=2)+'\n')
    provenance = json.loads(receipt.read_text())
    assert sha(path) == provenance['projection_sha256']
    reader = csv.DictReader(io.StringIO(path.read_text()), delimiter='\t')
    assert reader.fieldnames == COLUMNS
    rows = list(reader)
    assert len(rows) == provenance['stats']['selected']
    assert all(r['page'] in pages and not r['page'].startswith('f84') and r['page'] != 'f116v' for r in rows)
    assert set(r['edition'] for r in rows) == set(EDITIONS)
    assert len(set(r['source_group_id'] for r in rows)) == len(rows)
    return rows, provenance


def blocks_from(rows):
    loci = defaultdict(list)
    for r in rows:
        for key in ('source_row_index','source_group_index','source_group_count'):
            r[key] = int(r[key])
        assert r['paragraph_start'] in ('0','1') and r['paragraph_end'] in ('0','1')
        loci[(r['edition'],r['page'],r['locus'])].append(r)
    by_page = defaultdict(list)
    for (edition,page,locus), groups in loci.items():
        groups.sort(key=lambda r:r['source_group_index'])
        assert [r['source_group_index'] for r in groups] == list(range(1,len(groups)+1))
        assert all(r['source_group_count'] == len(groups) for r in groups)
        keys = ('source_row_index','kind','paragraph_start','paragraph_end')
        assert all(all(r[k] == groups[0][k] for k in keys) for r in groups)
        line = {'locus':locus, **{k:groups[0][k] for k in keys},
                'groups': [{k:r[k] for k in ('source_group_id','source_group_index',
                           'left_separator','right_separator','ivtff_group_raw')} for r in groups]}
        by_page[(edition,page)].append(line)
    blocks = []
    for (edition,page), lines in sorted(by_page.items()):
        lines.sort(key=lambda x:x['source_row_index'])
        assert len({x['source_row_index'] for x in lines}) == len(lines)
        current = []
        def flush():
            if current:
                blocks.append({'block_id':f'{edition}:{page}:{current[0]["locus"]}',
                               'edition':edition,'page':page,
                               'left_marked':current[0]['paragraph_start']=='1',
                               'right_marked':current[-1]['paragraph_end']=='1',
                               'lines':current.copy()})
                current.clear()
        for line in lines:
            if line['kind'] != 'P':
                flush()
                continue
            if line['paragraph_start'] == '1':
                flush()
            current.append(line)
            if line['paragraph_end'] == '1':
                flush()
        flush()
    assert sum(len(line['groups']) for b in blocks for line in b['lines']) == sum(r['kind']=='P' for r in rows)
    return blocks


def evaluate(rows, old):
    blocks = blocks_from(rows)
    runs = []
    summaries = {(inv,ed,st):{'inventory':inv,'edition':ed,'stratum':st,
                  'occurrences':0,'runs':0,'left':Counter(),'right':Counter()}
                 for inv in INVENTORIES for ed in EDITIONS for st in ('old_overlap27','additional152')}
    conflict_ids = set()
    for block in blocks:
        flat = [g for line in block['lines'] for g in line['groups']]
        stratum = 'old_overlap27' if block['page'] in old else 'additional152'
        for inv, forms in INVENTORIES.items():
            i = 0
            while i < len(flat):
                if flat[i]['ivtff_group_raw'] not in forms:
                    i += 1
                    continue
                start = i
                while i < len(flat) and flat[i]['ivtff_group_raw'] in forms:
                    i += 1
                end = i - 1
                left = 'CAPACITY' if start else 'CONTRADICTION' if block['left_marked'] else 'UNKNOWN'
                right = 'CAPACITY' if i < len(flat) else 'CONTRADICTION' if block['right_marked'] else 'UNKNOWN'
                r = {'inventory':inv,'edition':block['edition'],'page':block['page'],
                     'stratum':stratum,'block_id':block['block_id'],
                     'start_group_id':flat[start]['source_group_id'],
                     'end_group_id':flat[end]['source_group_id'],
                     'start_index_0based':start,'end_index_0based':end,
                     'forms':[g['ivtff_group_raw'] for g in flat[start:i]],
                     'left_status':left,'right_status':right}
                runs.append(r)
                s = summaries[(inv,block['edition'],stratum)]
                s['occurrences'] += i-start
                s['runs'] += 1
                s['left'][left] += 1
                s['right'][right] += 1
                if 'CONTRADICTION' in (left,right):
                    conflict_ids.add(block['block_id'])
    for s in summaries.values():
        for direction in ('left','right'):
            s[direction] = {k:s[direction][k] for k in ('CAPACITY','CONTRADICTION','UNKNOWN')}
    row_counts = {ed:dict(sorted(Counter(r['kind'] for r in rows if r['edition']==ed).items())) for ed in EDITIONS}
    boundaries = {ed:{'blocks':sum(b['edition']==ed for b in blocks),
                     'left_marked':sum(b['edition']==ed and b['left_marked'] for b in blocks),
                     'right_marked':sum(b['edition']==ed and b['right_marked'] for b in blocks)} for ed in EDITIONS}
    decisions = []
    for inv in INVENTORIES:
        for ed in EDITIONS:
            ss=[s for s in summaries.values() if s['inventory']==inv and s['edition']==ed]
            for direction in ('left','right'):
                total={k:sum(s[direction][k] for s in ss) for k in ('CAPACITY','CONTRADICTION','UNKNOWN')}
                verdict = 'CONTRADICTED_FIXED_HOST_CONDITION' if total['CONTRADICTION'] else 'COMPATIBLE_NECESSARY_CONDITION_WITH_UNKNOWNS' if total['UNKNOWN'] else 'COMPATIBLE_NECESSARY_CONDITION_ONLY'
                if boundaries[ed]['left_marked'] == 0 and boundaries[ed]['right_marked'] == 0:
                    verdict = 'NO_SOURCE_MARKED_PARAGRAPH_CAPACITY'
                decisions.append({'inventory':inv,'edition':ed,'direction':direction,
                                  'counts':total,'verdict':verdict})
    return runs, [b for b in blocks if b['block_id'] in conflict_ids], list(summaries.values()), row_counts, boundaries, decisions


def build(fetch=False):
    lock = check_lock()
    addendum = json.loads((EXP/'src/SCOPE_ADDENDUM_LOCK.json').read_text())
    assert sha(ROOT/addendum['path']) == addendum['sha256']
    admitted = metadata(ALLOW)
    assert len(admitted)==179
    # Admission files contain selectors only; reading them does not decode source rows.
    page_key = 'page' if 'page' in admitted[0] else 'source_selector'
    pages = sorted(r[page_key] for r in admitted)
    assert len(set(pages))==179 and not any(p.startswith('f84') or p=='f116v' for p in pages)
    old = {r['source_selector'] for path in OLD for r in metadata(path)}
    assert len(old)==39
    excluded_old = sorted(old - set(pages))
    old = old & set(pages)
    assert len(old)==27 and len(excluded_old)==12
    rows, provenance = project(pages, fetch)
    runs, blocks, summary, row_counts, boundaries, decisions = evaluate(rows, old)
    result = {'experiment_id':'GDT1047','status':'FIXED_PARAGRAPH_HOST_CAPACITY_ONLY',
              'registered_utc':lock['registered_utc'],'allowlist_sha256':sha(ROOT/ALLOW),
              'source_sha256':sha(ROOT/SOURCE),'prereg_lock_sha256':sha(EXP/'src/PREREG_LOCK.json'),
              'scope_addendum_lock_sha256':sha(EXP/'src/SCOPE_ADDENDUM_LOCK.json'),
              'guarded_query':provenance,'selectors':179,'old_selectors':sorted(old),
              'extra_selector_count':152,'old_outside_current_selectors':excluded_old,'row_counts':row_counts,'paragraph_boundary_counts':boundaries,
              'summary':summary,'decisions':decisions,'contradiction_blocks':len(blocks),
              'total_runs':len(runs),'confirmed_words':0,'new_access':0,
              'statistical_significance_claimed':False,'independent_confirmation':False,
              'ceiling':'Source-marked boundary capacity, not a host interpretation or semantic choice.'}
    return {'RUNS.json':runs,'BLOCKS.json':blocks,'RESULT.json':result}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    artifacts=build(args.fetch)
    for name,value in artifacts.items():
        data=json.dumps(value,indent=2,ensure_ascii=False)+'\n'
        path=EXP/'artifacts'/name
        if args.check:
            assert path.read_text()==data, f'Replay mismatch: {name}'
        else:
            path.write_text(data)
    r=artifacts['RESULT.json']
    print(json.dumps({k:r[k] for k in ('row_counts','paragraph_boundary_counts','decisions','contradiction_blocks','total_runs')},indent=2))


if __name__=='__main__':
    main()
