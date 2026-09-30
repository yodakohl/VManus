#!/usr/bin/env python3
"""Retain admitted caption pairs; no decoding, scoring or owner inference."""
import csv, hashlib, io, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
B=Path(__file__).resolve().parent
packet=B/'BX_SOURCE.json'
rows=json.loads(packet.read_text())['queries'][3]['rows']
command=['./vmanus-exp','query-tsv','experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv','--selector','page','--allow','f75v','--columns','page,locus,unit,local_comment,unit_description']
p=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True)
annotations=[]
for row in csv.DictReader(io.StringIO(p.stdout),delimiter='\t'):
 if row['unit']!='N1': continue
 match=re.search(r'Label L(\d+), line ([12])\.$',row['local_comment'])
 if match: annotations.append(dict(row,label=int(match[1]),line=int(match[2])))
assert len(annotations)==20
captions=[]
for n in range(1,11):
 pair=sorted([r for r in annotations if r['label']==n],key=lambda r:r['line'])
 assert [r['line'] for r in pair]==[1,2]
 loci=[r['locus'] for r in pair]
 item={'label':n,'loci':loci,'readings':{}}
 for e in ['ZL3b','IT2a','RF1b']:
  fields=[[r for r in rows if r['edition']==e and r['locus']==l] for l in loci]
  assert all(fields) and all(r['kind']=='L' and r['page']=='f75v' for f in fields for r in f)
  item['readings'][e]={'fields':fields,'display':[' '.join(r['ivtff_group_raw'] for r in f) for f in fields]}
 captions.append(item)
repeated={}
for e in ['ZL3b','IT2a','RF1b']:
 repeated[e]={}
 for line in [0,1]:
  by={}
  for c in captions:
   key=tuple(r['ivtff_group_raw'] for r in c['readings'][e]['fields'][line])
   by.setdefault(key,[]).append(c['label'])
  repeated[e][str(line+1)]=[{'groups':list(k),'labels':v} for k,v in by.items() if len(v)>1]
result={'question':'complete caption field-role capacity; exposed exploration','source_packet':str(packet.relative_to(ROOT)),'source_packet_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'pairing_command':command,'guard_receipt':p.stderr.strip(),'annotations':annotations,'captions':captions,'exact_field_repetitions':repeated,'confirmed_words':0,'independent_meaning_confirmation_leaves':0,'decision':'NO_FIELD_MEANING_SELECTED; retain prior twin-fan stop; no mirror key'}
(B/'BZ_CAPTIONS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# BZ complete caption table','', 'Raw groups are displayed with spaces; authoritative groups/separators remain in BZ_CAPTIONS.json. No RF entities or IT splits are repaired.','', '| Label | Loci | ZL top / bottom | IT top / bottom | RF top / bottom |','|---|---|---|---|---|']
for c in captions:
 lines.append('| L'+str(c['label'])+' | '+', '.join(c['loci'])+' | '+' | '.join(' / '.join(c['readings'][e]['display']) for e in ['ZL3b','IT2a','RF1b'])+' |')
(B/'BZ_CAPTION_TABLE.md').write_text('\n'.join(lines)+'\n')
print('Retained ten pairs, all three readings, exact repetitions; no meaning inference.')
