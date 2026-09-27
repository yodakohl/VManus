#!/usr/bin/env python3
"""Check all frozen input rows, nine complete decision cells and hashes."""
import csv, hashlib, json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parents[1];ART=HERE/'artifacts'
SOURCE=ROOT/'experiments/yolo/gdt1057_quality_full_source_orientation/artifacts/RESULT.json'
TARGET=ROOT/'experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/ORIENTATION_FREQUENCY_COMPARISON.tsv'
Q=('hot_dry','hot_moist','cold_dry','cold_moist')
def read(p):
 with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 checks=0
 def test(value,msg):
  nonlocal checks
  assert value,msg
  checks+=1
 result=json.loads((ART/'RESULT.json').read_text());source=json.loads(SOURCE.read_text())
 test(result['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source hash')
 test(result['target_sha256']==hashlib.sha256(TARGET.read_bytes()).hexdigest(),'target hash')
 test(result['source_counts']==source['source_counts'],'counts')
 src=source['source_counts'];sp={q:(src[q]+.5)/(sum(src.values())+2) for q in Q}
 frozen=read(TARGET);scored=read(ART/'ALL_72_RESCORINGS.tsv');decisions=read(ART/'NINE_CELL_DECISIONS.tsv')
 test(len(frozen)==len(scored)==72 and len(decisions)==9,'completeness')
 ids=Counter((r['scope'],r['mode']) for r in scored)
 test(len(ids)==9 and set(ids.values())=={8},'8 per cell')
 byid={(r['scope'],r['mode'],r['assignment_id']):r for r in scored}
 test(len(byid)==72,'unique cells')
 for r in frozen:
  key=(r['scope'],r['mode'],r['assignment_id']);out=byid[key]
  n=sum(int(r[q]) for q in Q)
  tv=sum(abs(sp[q]-(int(r[q])+.5)/(n+2)) for q in Q)/2
  test(int(out['target_n'])==n and abs(float(out['tv'])-tv)<.0000006,'row '+str(key))
 for d in decisions:
  group=[r for r in scored if (r['scope'],r['mode'])==(d['scope'],d['mode'])]
  sorted_group=sorted(group,key=lambda x:(float(x['tv']),x['assignment_id']))
  test([int(r['rank']) for r in sorted_group]==list(range(1,9)),'ranks')
  test(d['overall_winner']==sorted_group[0]['assignment_id'],'overall winner')
  thermal=[r for r in group if r['assignment_id'].startswith('KT_THERMAL') and r['assignment_id'].endswith('CH_DRY')]
  test(len(thermal)==2 and d['thermal_winner']==min(thermal,key=lambda x:float(x['tv']))['assignment_id'],'thermal pair')
 test(Counter(d['thermal_winner'] for d in decisions)=={'KT_THERMAL__K_HOT__CH_DRY':3,'KT_THERMAL__K_COLD__CH_DRY':6},'3/6 split')
 output={'status':'PASS','checks':checks,'rows':len(scored),'cells':len(decisions)}
 (ART/'VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
