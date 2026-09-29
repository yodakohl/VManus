#!/usr/bin/env python3
"""Eight-selector, raw-whole/split documentary audit. No decoder or parser."""
import csv,hashlib,io,json,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file() and (p/'.git').exists())
BASE=Path(__file__).resolve().parents[1]
PAGES=('f22r','f32r','f42v','f14r','f56r','f8r','f29v','f11r')
SOURCE=ROOT/'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
ALLOW=ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
COLS='source_group_id,edition,page,locus,kind,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw'
allowed={r['page'] for r in csv.DictReader(ALLOW.open(),delimiter='\t')}
assert set(PAGES)<=allowed and not any(p.startswith('f84') for p in PAGES)
cmd=[str(ROOT/'vmanus-exp'),'query-tsv',str(SOURCE),'--selector','page','--columns',COLS]
for p in PAGES:cmd+=['--allow',p]
raw=subprocess.check_output(cmd,text=True)
rows=list(csv.DictReader(io.StringIO(raw),delimiter='\t'))
lines=defaultdict(list)
for r in rows:
 assert r['page'] in PAGES
 lines[(r['edition'],r['page'],r['locus'],r['kind'])].append(r)
selected=[];events=[]
for key,rs in sorted(lines.items()):
 rs.sort(key=lambda r:int(r['source_group_index']))
 found=[]
 for i,r in enumerate(rs):
  w=r['ivtff_group_raw']
  if w in ('schor','schol'):found.append({'form':w,'positions':[r['source_group_index']]})
  if w=='s' and i+1<len(rs) and rs[i+1]['ivtff_group_raw']=='chol' and int(rs[i+1]['source_group_index'])==int(r['source_group_index'])+1:
   found.append({'form':'s chol','positions':[r['source_group_index'],rs[i+1]['source_group_index']]})
 if found:
  selected.append({'edition':key[0],'page':key[1],'locus':key[2],'kind':key[3],'groups':rs,'matches':found})
  for f in found:events.append({'edition':key[0],'page':key[1],'locus':key[2],**f})
counts={e:{f:sum(x['edition']==e and x['form']==f for x in events) for f in ('schor','schol','s chol')} for e in ('ZL3b','IT2a','RF1b')}
out=BASE/'artifacts';out.mkdir(exist_ok=True)
packet={'selectors':list(PAGES),'projected_columns':COLS.split(','),'queried_groups':len(rows),'selected_complete_lines':selected,'events':events}
(out/'CONTEXTS.json').write_text(json.dumps(packet,indent=2)+'\n')
text=['# Complete selected native physical lines','No inferred sentence/paragraph boundaries or meanings.']
for x in selected:text += ['',f"## {x['edition']} {x['locus']} ({x['kind']})",'`'+' '.join(r['ivtff_group_raw'] for r in x['groups'])+'`',json.dumps(x['matches'])]
(out/'CONTEXTS.md').write_text('\n'.join(text)+'\n')
result={'status':'DOCUMENTARY_AUDIT_NOT_MEANING_TEST','counts':counts,'selected_lines':len(selected),'events':len(events),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'allowlist_sha256':hashlib.sha256(ALLOW.read_bytes()).hexdigest(),'confirmed_words':0,'independent_confirmation_leaves':0,'global_census':False}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
