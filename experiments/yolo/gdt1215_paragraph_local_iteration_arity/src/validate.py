#!/usr/bin/env python3
"""Separate interval reconstruction; no runner import."""
import csv,hashlib,io,json,subprocess
from collections import defaultdict,Counter
from datetime import datetime,timezone
from pathlib import Path
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 fields='source_group_id,edition,page,locus,kind,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw'
 cmd=[str(ROOT/'vmanus-exp'),'query-tsv',str(ROOT/'experiments/semantic_assumptions/results/source_separator_transcription.tsv'),'--selector','page','--columns',fields]
 pages=sorted(r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t'))
 for p in pages:cmd.extend(['--allow',p])
 q=subprocess.run(cmd,text=True,capture_output=True,check=True);rows=list(csv.DictReader(io.StringIO(q.stdout),delimiter='\t'));raw={r['source_group_id']:r for r in rows}
 report=json.loads((A/'RESULT.json').read_text());ctx=json.loads((A/'RETAINED_CONTEXTS.json').read_text());run=json.loads((A/'RUN_RECEIPT.json').read_text())
 assert hashlib.sha256(q.stdout.encode()).hexdigest()==run['projection_sha256'] and len(raw)==len(rows)==report['groups_queried']
 lines=defaultdict(list);page_lines=defaultdict(list)
 for r in rows:lines[(r['edition'],r['page'],int(r['source_row_index']))].append(r)
 for key,line in lines.items():
  line.sort(key=lambda r:int(r['source_group_index']))
  if line[0]['kind']=='P':page_lines[key[:2]].append((key[2],line))
 units={};bindings={}
 for (ed,page),plines in page_lines.items():
  ordered=[x[1] for x in sorted(plines)]
  for start,line in enumerate(ordered):
   if line[0]['paragraph_start']!='1':continue
   end=None
   for j in range(start,len(ordered)):
    if j>start and ordered[j][0]['paragraph_start']=='1':break
    if ordered[j][0]['paragraph_end']=='1':end=j;break
   if end is None:continue
   window=ordered[start:end+1];nums=[int(x[0]['locus'].split('.')[-1]) for x in window]
   if nums!=list(range(nums[0],nums[0]+len(nums))):continue
   uid=ed+'|'+page+'|'+window[0][0]['locus']+'-'+window[-1][0]['locus'];flat=sum(window,[]);units[uid]=flat
   for i,r in enumerate(flat):bindings[r['source_group_id']]=(uid,i,len(flat)-i-1)
 assert report['complete_paragraphs']=={e:sum(u.startswith(e+'|') for u in units) for e in ['ZL3b','IT2a','RF1b']}
 exact={k for k,r in raw.items() if r['ivtff_group_raw']=='olol'};assert exact=={c['source_group_id'] for c in report['cases']}
 for c in report['cases']:
  r=raw[c['source_group_id']];b=bindings.get(c['source_group_id']);reasons=[]
  if r['kind']!='P':reasons.append('NON_PROSE')
  if not(r['left_separator'] in ['LINE_START','DEFINITE_SPACE'] and r['right_separator'] in ['LINE_END','DEFINITE_SPACE']):reasons.append('UNCERTAIN_WORD_BOUNDARY')
  if b is None:reasons.append('NO_COMPLETE_NATIVE_PARAGRAPH')
  expected='UNTESTABLE' if reasons else ('RIGHT_SPACE_PRESENT' if b[2]>=1 else 'CONTRADICTION')
  assert c['outcome']==expected and c['reasons']==reasons and c['unit_id']==(b[0] if b else '') and c['position']==(b[1]+1 if b else None)
  assert c['right_group_count']==(b[2] if b else None) and c['first_right_id']==(units[b[0]][b[1]+1]['source_group_id'] if b and b[2] else None)
  assert c['whole_line']==' '.join(x['ivtff_group_raw'] for x in lines[(r['edition'],r['page'],int(r['source_row_index']))])
 for line in ctx['occurrence_lines']:assert line==[raw[r['source_group_id']] for r in line]
 for u,flat in ctx['paragraphs'].items():assert flat==units[u]
 assert set(ctx['paragraphs'])=={c['unit_id'] for c in report['cases'] if c['unit_id']}
 for e,counts in report['outcomes'].items():assert counts==dict(Counter(c['outcome'] for c in report['cases'] if c['edition']==e))
 expected='PARAGRAPH_LOCAL_ITERATION_CONTRADICTED' if any(c['outcome']=='CONTRADICTION' for c in report['cases']) else 'NO_ELIGIBLE_PARAGRAPH_END_CONTRADICTION';assert report['status']==expected
 proof=json.loads((D/'src/SPEC.json').read_text());assert min(proof['known_repeatable_arities'].values())==1 and proof['short_square_signs']==4 and proof['minimum_open_head_signs']==5
 prior=json.loads((ROOT/'experiments/yolo/gdt1214_short_square_fixed_grammar/artifacts/RESULT.json').read_text());assert prior['double_readable_pairs']==0
 out={'status':'PASS','checked_occurrences':len(exact),'checked_complete_paragraphs':len(units),'source_guard_repeated':True,'separate_interval_algorithm':True,'runner_imported':False,'meaning_validation':False,'completed_utc':datetime.now(timezone.utc).isoformat()}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
