#!/usr/bin/env python3
"""Retain whole admitted f9v and all exact singleton contexts; no decoder."""
import csv,hashlib,io,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
source='experiments/semantic_assumptions/results/source_separator_transcription.tsv'
cols='source_group_id,edition,page,locus,kind,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw'
cmd=['./vmanus-exp','query-tsv',source,'--selector','page','--allow','f9v','--columns',cols]
p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
rows=list(csv.DictReader(io.StringIO(p.stdout),delimiter='\t'))
assert all(r['page']=='f9v' for r in rows)
frames=[]
for e in ['ZL3b','IT2a','RF1b']:
 for n in range(1,13):
  rs=[r for r in rows if r['edition']==e and r['locus']=='f9v.'+str(n)]
  assert rs
  frames.append({'edition':e,'locus':'f9v.'+str(n),'groups':rs})
packet={'scope':'all12 f9v native prose loci, both complete ZL/IT paragraphs; RF matched windows no native paragraph flags','command':cmd,'guard_receipt':p.stderr.strip(),'source_sha256':hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),'rows':rows,'lines':frames}
(B/'CE_SOURCE.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
lines=['# CE all f9v native lines','No preceding image-name gloss, body lexicon, crop or smoothed transcription.']
for x in frames:
 lines += ['',f"## {x['edition']} {x['locus']}",'`'+' '.join(r['ivtff_group_raw'] for r in x['groups'])+'`']
(B/'CE_CONTEXTS.md').write_text('\n'.join(lines)+'\n')
print('Retained',len(rows),'groups in',len(frames),'whole native lines.')
