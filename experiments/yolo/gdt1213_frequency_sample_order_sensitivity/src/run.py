#!/usr/bin/env python3
"""Fixed selection sensitivity of two existing frequency bands."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import csv,hashlib,io,json,random,subprocess,sys
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
OLD=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison'
sys.path.insert(0,str(OLD/'src'));import metrics
SOURCE='experiments/yolo/gdt1170_repetition_context_neutral_copy/artifacts/GUARDED.tsv'
SPEC='experiments/yolo/gdt1170_repetition_context_neutral_copy/src/SPEC.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def save(n,x):(A/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def main():
 started=datetime.now(timezone.utc).isoformat()
 for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert sha(ROOT/rel)==h,rel
 allowed=json.loads((ROOT/SPEC).read_text())['allowed'];assert len(allowed)==179
 assert all(not x.startswith('f84') and x!='f116v' for x in allowed)
 cmd=['./vmanus-exp','query-tsv',SOURCE,'--selector','page']
 for page in allowed:cmd+=['--allow',page]
 cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
 call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
 rows=[r for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t') if r['kind']=='P']
 pages=sorted({r['page'] for r in rows});eligible=defaultdict(list)
 for r in rows:
  boundary=r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END')
  if boundary and metrics.glyphs(r['ivtff_group_raw']):eligible[r['edition']].append(r)
 target=json.loads((OLD/'artifacts/RESULT.json').read_text())['targets']
 scope=json.loads((OLD/'artifacts/RESULT.json').read_text())['scope']
 assert set(eligible)==set(target)
 for ed,rs in eligible.items():assert len(rs)==scope[ed]['eligible_groups']
 def sample(seed):
  order=pages.copy();random.Random(seed).shuffle(order);rank={p:i for i,p in enumerate(order)};out={}
  for ed,rs in sorted(eligible.items()):
   selected=sorted(rs,key=lambda r:(rank[r['page']],r['locus'],int(r['source_group_index'])))[:8000]
   assert len(selected)==8000
   c=Counter(r['ivtff_group_raw'] for r in selected);top=sum(sorted(c.values(),reverse=True)[:10]);t=target[ed]
   ids=[f"{ed}|{r['locus']}|G{int(r['source_group_index']):03d}" for r in selected]
   out[ed]={'types':len(c),'top10_count':top,'types_within':abs(len(c)-t['types'])<=400,'top10_within':abs(top-round(8000*t['top10_share']))<=400,'sample_ids_sha256':digest(ids),'pages_touched':len({r['page'] for r in selected}),'last_group_id':ids[-1]}
  return {'seed':seed,'readers':out,'all_six_within':all(r['types_within'] and r['top10_within'] for r in out.values())}
 anchor=sample(1174)
 for ed,m in anchor['readers'].items():assert m['types']==target[ed]['types'] and m['top10_count']==round(8000*target[ed]['top10_share'])
 oldids=json.loads((ROOT/'experiments/yolo/gdt1211_one_variant_per_line_capacity/artifacts/TARGET_SAMPLE_IDS.json').read_text())
 for ed in target:assert anchor['readers'][ed]['sample_ids_sha256']==digest(oldids[ed])
 samples=[sample(seed) for seed in range(128)]
 joint=sum(r['all_six_within'] for r in samples)
 summary={ed:{'types_range':[min(r['readers'][ed]['types'] for r in samples),max(r['readers'][ed]['types'] for r in samples)],'top10_range':[min(r['readers'][ed]['top10_count'] for r in samples),max(r['readers'][ed]['top10_count'] for r in samples)],'type_failures':sum(not r['readers'][ed]['types_within'] for r in samples),'top10_failures':sum(not r['readers'][ed]['top10_within'] for r in samples)} for ed in target}
 result={'experiment':'GDT1213','status':'FREQUENCY_SELECTION_OPERATIONALLY_STABLE' if joint>=122 else 'FREQUENCY_SELECTION_OPERATIONALLY_UNSTABLE','registered_seeds':128,'joint_passes':joint,'required_joint_passes':122,'summary':summary,'anchor':anchor,'samples':samples,'eligible_groups':{ed:len(rs) for ed,rs in eligible.items()},'prose_page_universe':len(pages),'claim_ceiling':'Selection sensitivity on an exposed, filtered common cache only; overlapping samples and alternate readings are not independent, no source attribution or candidate retest.'}
 save('RESULT',result);save('RUN_RECEIPT',{'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'guard_command':cmd,'guard_receipt':call.stderr.strip(),'guard_output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()})
 print(json.dumps({k:result[k] for k in ('status','joint_passes','summary','eligible_groups','prose_page_universe')},indent=2))
if __name__=='__main__':main()
