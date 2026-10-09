#!/usr/bin/env python3
"""Independent regexp eligibility and page-by-page counter; no runner import."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import csv,hashlib,io,json,random,re,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def main():
 for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
 old=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json';prior=json.loads(old.read_text());target=prior['targets']
 allowed=json.loads((ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/src/SPEC.json').read_text())['allowed'];assert all(not x.startswith('f84') and x!='f116v' for x in allowed)
 cmd=['./vmanus-exp','query-tsv','experiments/yolo/gdt1170_repetition_context_neutral_copy/artifacts/GUARDED.tsv','--selector','page']
 for p in allowed:cmd+=['--allow',p]
 cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
 call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
 pages=set();by=defaultdict(list);count=defaultdict(int)
 for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
  if r['kind']!='P':continue
  pages.add(r['page'])
  if r['left_separator'] not in {'DEFINITE_SPACE','LINE_START'} or r['right_separator'] not in {'DEFINITE_SPACE','LINE_END'}:continue
  if re.fullmatch(r'(?:ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf])+',r['ivtff_group_raw']) is None:continue
  by[r['edition'],r['page']].append((r['locus'],int(r['source_group_index']),r['ivtff_group_raw']));count[r['edition']]+=1
 for rows in by.values():rows.sort(key=lambda x:(x[0],x[1]))
 for ed in target:assert count[ed]==prior['scope'][ed]['eligible_groups']
 result=json.loads((A/'RESULT.json').read_text());assert result['eligible_groups']==dict(count)
 assert result['prose_page_universe']==len(pages)
 assert [r['seed'] for r in result['samples']]==list(range(128))
 joint=0
 oldids=json.loads((ROOT/'experiments/yolo/gdt1211_one_variant_per_line_capacity/artifacts/TARGET_SAMPLE_IDS.json').read_text())
 for record in result['samples']+[result['anchor']]:
  order=sorted(pages);random.Random(record['seed']).shuffle(order);passes=[]
  for ed,t in target.items():
   freqs={};ids=[];touched=set()
   for page in order:
    for loc,idx,word in by[ed,page]:
     if len(ids)==8000:break
     freqs[word]=freqs.get(word,0)+1;ids.append(f'{ed}|{loc}|G{idx:03d}');touched.add(page)
    if len(ids)==8000:break
   assert len(ids)==8000
   head=sum(sorted(freqs.values())[-10:]);types_ok=t['types']-400<=len(freqs)<=t['types']+400;top_ok=round(8000*t['top10_share'])-400<=head<=round(8000*t['top10_share'])+400
   expected={'types':len(freqs),'top10_count':head,'types_within':types_ok,'top10_within':top_ok,'sample_ids_sha256':digest(ids),'pages_touched':len(touched),'last_group_id':ids[-1]}
   assert record['readers'][ed]==expected
   if record['seed']==1174:assert ids==oldids[ed]
   passes.append(types_ok and top_ok)
  assert record['all_six_within']==all(passes)
  if record['seed']!=1174:joint+=all(passes)
 assert result['joint_passes']==joint and result['required_joint_passes']==122
 assert result['status']==('FREQUENCY_SELECTION_OPERATIONALLY_STABLE' if joint>=122 else 'FREQUENCY_SELECTION_OPERATIONALLY_UNSTABLE')
 for ed in target:
  records=[r['readers'][ed] for r in result['samples']]
  expected={'types_range':[min(r['types'] for r in records),max(r['types'] for r in records)],'top10_range':[min(r['top10_count'] for r in records),max(r['top10_count'] for r in records)],'type_failures':sum(not r['types_within'] for r in records),'top10_failures':sum(not r['top10_within'] for r in records)}
  assert result['summary'][ed]==expected
 out={'status':'PASS','same_author':True,'runner_imported':False,'samples_verified':128,'anchor_ids_verified':24000,'source_guard_output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest(),'method':'Independent regex parser, within-page sorting, incremental frequency accumulation, every sample-ID digest and metric replay.','claim_ceiling':'Implementation and selection accounting, not independent confirmation or statistical error-rate calibration.','completed_utc':datetime.now(timezone.utc).isoformat()}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
