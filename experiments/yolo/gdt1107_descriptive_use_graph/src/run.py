#!/usr/bin/env python3
"""Run the registered multi-clause graph on every admitted Herbal page."""
import csv
import gzip
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path
from graph import search

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
SOURCE=ROOT/'experiments/yolo/gdt1106_frozen_domain_transfer/artifacts/SOURCE.tsv.gz'

def main():
    lock=json.loads((BASE/'PREREG_LOCK.json').read_text())
    for path,digest in lock['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    spec=json.loads((BASE/'src/MODEL.json').read_text())
    rows=list(csv.DictReader(io.StringIO(gzip.decompress(SOURCE.read_bytes()).decode()),delimiter='\t'))
    lines=defaultdict(list)
    for r in rows:
        if r['section']!='Herbal':continue
        assert r['kind']=='P' and not r['page'].startswith('f84') and r['page']!='f116v'
        lines[(r['edition'],r['page'],r['locus'])].append(r)
    pages=defaultdict(list)
    for (edition,page,locus),groups in lines.items():pages[(edition,page)].append({'locus':locus,'groups':groups})
    results=[];witnesses=[];partials=[]
    for (edition,page),page_lines in sorted(pages.items()):
        outcome=search(page_lines,spec)
        case={'edition':edition,'page':page,'physical_leaf':page.split('r')[0].split('v')[0],
            'source_groups':sum(len(x['groups']) for x in page_lines),'full_lines':len(page_lines),
            **{k:outcome[k] for k in ('literal_triples','excluded_triples','literal_fives','excluded_fives','stage_counts')},
            'full_bindings':len(outcome['solutions']),'status':'C0_GRAPH_BINDING' if outcome['solutions'] else 'NO_FIXED_REALIZATION_GRAPH'}
        results.append(case)
        witnesses.extend({'edition':edition,'page':page,**s} for s in outcome['solutions'])
        partials.append({'edition':edition,'page':page,'induce_forks':outcome['induce_forks'],'linked_use_forks':outcome['linked_use_forks']})
    (BASE/'artifacts/CASES.json').write_text(json.dumps(results,indent=2)+'\n')
    (BASE/'artifacts/WITNESSES.json.gz').write_bytes(gzip.compress(json.dumps(witnesses,sort_keys=True).encode(),mtime=0))
    (BASE/'artifacts/PARTIALS.json.gz').write_bytes(gzip.compress(json.dumps(partials,sort_keys=True).encode(),mtime=0))
    with (BASE/'artifacts/CANDIDATE_TABLE.tsv').open('w',newline='') as f:
        columns=['candidate','edition','page','comparison_orientation','induce_orientation','use_orientation',*spec['atom_roles']]
        w=csv.DictWriter(f,fieldnames=columns,delimiter='\t',lineterminator='\n');w.writeheader()
        for i,s in enumerate(witnesses):w.writerow({'candidate':i,'edition':s['edition'],'page':s['page'],**{k:s[k] for k in columns[3:6]},**s['values']})
    status='C0_JOINT_GRAPH_BINDINGS_RETAINED' if witnesses else 'NO_FIXED_DESCRIPTIVE_USE_GRAPH'
    result={'status':status,'all_page_reader_cases':len(results),'source_groups':sum(r['source_groups'] for r in results),
        'whole_group_realization_contracts':4320,'full_bindings':len(witnesses),
        'stage_counts':{k:sum(r['stage_counts'].get(k,0) for r in results) for k in ('induce_forks','linked_use_forks','head_leaf_comparison_links')},
        'confirmed_words':0,'independent_meaning_confirmation_leaves':0,'reserved_pages_opened':[], 'semantic_score':None,'significance':None,
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'ceiling':'Necessary relation topology under a13whole-form injective writer; no word identified'}
    (BASE/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
