#!/usr/bin/env python3
"""Independent GDT1084 checks against the guarded target selection."""
import csv
import hashlib
import io
import itertools
import json
import math
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[4]
base=root/'experiments/yolo/gdt1084_source_native_four_plant_bridge'
result=json.loads((base/'artifacts/RESULT.json').read_text())
capacity_path=root/'experiments/semantic_assumptions/results/public_repeated_plant_source_native_capacity.json'
groups_path=root/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv'
capacity=json.loads(capacity_path.read_text())
for path,key in [(base/'METHOD.md','method_sha256'),(capacity_path,'capacity_sha256'),(groups_path,'groups_sha256')]:
    assert hashlib.sha256(path.read_bytes()).hexdigest()==result[key]
assert result['decision']=='NO_FOUR_PAIR_FORMAL_SIGNAL'
assert result['labels']==['f89v2.6','f102r2.21','f102r2.22','f102v1.17']
assert result['pages']==['f48v','f18v','f23r','f19r']
cmd=['./vmanus-exp','query-tsv',str(groups_path.relative_to(root)),'--selector','page']
for page in result['pages']:cmd+=['--allow',page]
cmd+=['--columns','locus,page,section,grammar_scope,strict_zero_alternative,currier,hand,zl_sta_codes,it_sta_codes,rf_sta_codes','--forbid-prefix','f84']
proc=subprocess.run(cmd,cwd=root,text=True,capture_output=True,check=True)
rows=list(csv.DictReader(io.StringIO(proc.stdout),delimiter='\t'))
assert len(rows)==303 and all(r['page'] in result['pages'] for r in rows)
assert proc.stderr.strip()==result['guard']
rows=[r for r in rows if (r['section'],r['grammar_scope'],r['strict_zero_alternative'])==('H','CONFIRMED_PROSE','1')]
assert {p:sum(r['page']==p for r in rows) for p in result['pages']}==result['admissible_prose_groups']
checks=0
for reader,column in [('ZL3b','zl_sta_codes'),('IT2a','it_sta_codes'),('RF1b','rf_sta_codes')]:
    data=result['readings'][reader]
    for i,label in enumerate(result['labels']):
        specs=capacity['label_inventory'][label]['readings'][reader]['motifs']
        for j,page in enumerate(result['pages']):
            scores=[]
            for spec in specs:
                motif=spec['motif'].split()
                for row in rows:
                    if row['page']!=page:continue
                    seq=row[column].split()
                    if any(seq[k:k+len(motif)]==motif for k in range(len(seq)-len(motif)+1)):
                        scores.append(spec['width']*math.log(93/(spec['page_document_frequency']['A_hand1']+1)))
            expected=max(scores,default=0.0)
            assert math.isclose(data['matrix'][i][j]['score'],expected,abs_tol=1e-10)
            assert data['matrix'][i][j]['hit_count']==len(scores)
            checks+=2
    sums=[sum(data['matrix'][i][perm[i]]['score'] for i in range(4)) for perm in itertools.permutations(range(4))]
    observed=sums[0]
    assert math.isclose(data['observed_total'],observed,abs_tol=1e-10)
    assert data['greater']==sum(s>observed+1e-12 for s in sums)
    assert data['ties']==sum(abs(s-observed)<=1e-12 for s in sums)
    assert math.isclose(data['one_sided_p'],sum(s>=observed-1e-12 for s in sums)/24)
    assert data['positive_own_pairs']==sum(data['matrix'][i][i]['score']>0 for i in range(4))
    assert not data['pass']
    three=[sum(data['matrix'][i][j]['score'] for i,j in enumerate(perm,start=1)) for perm in itertools.permutations((1,2,3))]
    assert math.isclose(data['three_explicit_owner_p_descriptive'],sum(s>=three[0]-1e-12 for s in three)/6)
    checks+=7
report=(base/'REPORT.md').read_text()
assert 'NO_FOUR_PAIR_FORMAL_SIGNAL' in report and 'No plant name' in report
(base/'artifacts/VALIDATION.json').write_text(json.dumps({'experiment':'GDT1084','status':'PASS','independent_checks':checks,'selected_rows':result['selected_rows'],'decision':result['decision']},indent=2)+'\n')
print(f'PASS: {checks} independent matrix/orbit checks; guarded rows {result["selected_rows"]}; decision {result["decision"]}')
