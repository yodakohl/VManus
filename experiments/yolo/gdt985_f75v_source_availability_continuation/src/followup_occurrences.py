# Post-result exploratory census, not a preregistered semantic test.
import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];rows=[];counts={};sources={}
for ed in ['ZL3b','IT2a','RF1b']:
 counts[ed]={'groups':0,'lines':0,'hits':0}
 for split in ['DISCOVERY','EVALUATION']:
  p=R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{ed}.json'
  sources[p.relative_to(R).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
  d=json.loads(p.read_text());cols=d['group_columns']
  for line in d['lines']:
   counts[ed]['lines']+=1;counts[ed]['groups']+=len(line['groups'])
   groups=[dict(zip(cols,g)) for g in line['groups']]
   hits=[g['source_group_id'] for g in groups if g['ivtff_group_raw']=='sheolo']
   if hits:
    counts[ed]['hits']+=len(hits);rows.append({'metadata':line['metadata'],'groups':groups,'hits':hits})
# Independent aggregate count via raw array index, without importing main loop.
for ed in counts:
 independent=0
 for split in ['DISCOVERY','EVALUATION']:
  d=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{ed}.json').read_text());k=d['group_columns'].index('ivtff_group_raw')
  independent+=sum(g[k]=='sheolo' for row in d['lines'] for g in row['groups'])
 assert independent==counts[ed]['hits']
assert {r['metadata']['locus'] for r in rows}=={'f75v.41'}
result={'status':'SINGLE_KNOWN_LOCUS','phase':'post-result exploration','counts':counts,'rows':rows,'sources':sources,'independent_confirmation':0,'meaning_contradiction':False,'validation':'PASS'}
(E/'artifacts/FOLLOWUP_OCCURRENCES.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','sources']},indent=2))
