#!/usr/bin/env python3
"""Independent guarded conservation and exact-contrast replay; not semantics."""
import csv,io,json,subprocess,hashlib
from collections import defaultdict,Counter
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file() and (p/'.git').exists())
BASE=Path(__file__).resolve().parents[1]
packet=json.loads((BASE/'artifacts/CONTEXTS.json').read_text())
result=json.loads((BASE/'artifacts/RESULT.json').read_text())
assert packet['selectors']==['f22r','f32r','f42v','f14r','f56r','f8r','f29v','f11r']
assert not any(p.startswith('f84') for p in packet['selectors'])
cmd=[str(ROOT/'vmanus-exp'),'query-tsv',str(ROOT/'experiments/semantic_assumptions/results/source_separator_transcription.tsv'),'--selector','page','--columns',','.join(packet['projected_columns'])]
for page in packet['selectors']:cmd += ['--allow',page]
rows=list(csv.DictReader(io.StringIO(subprocess.check_output(cmd,text=True)),delimiter='\t'))
assert len(rows)==packet['queried_groups']
original=defaultdict(list)
for row in rows:
 assert row['page'] in packet['selectors']
 original[(row['edition'],row['page'],row['locus'],row['kind'])].append(row)
expected=[];events=[]
for key in sorted(original):
 line=sorted(original[key],key=lambda r:int(r['source_group_index']))
 words=[r['ivtff_group_raw'] for r in line]
 matches=[]
 for i,w in enumerate(words):
  if w in ['schor','schol']:matches.append({'form':w,'positions':[line[i]['source_group_index']]})
  if words[i:i+2]==['s','chol']:
   assert int(line[i+1]['source_group_index'])==int(line[i]['source_group_index'])+1
   matches.append({'form':'s chol','positions':[line[i]['source_group_index'],line[i+1]['source_group_index']]})
 if matches:
  expected.append({'edition':key[0],'page':key[1],'locus':key[2],'kind':key[3],'groups':line,'matches':matches})
  events += [{'edition':key[0],'page':key[1],'locus':key[2],**m} for m in matches]
assert expected==packet['selected_complete_lines'] and events==packet['events']
assert len(expected)==24 and len(events)==24
for e,cs in result['counts'].items():
 c=Counter(x['form'] for x in events if x['edition']==e)
 assert all(c[f]==n for f,n in cs.items())
physical=Counter(x['locus'] for x in events)
assert len(physical)==8 and all(n==3 for n in physical.values())
v={'status':'PASS','coverage':'guarded8selector provenance; all24selected whole native lines and24events independently replayed;8physicalpositions','queried_groups':len(rows),'semantic_truth_checked':False,'organ_owner_checked':False,'independent_confirmation_leaves':0}
(BASE/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
