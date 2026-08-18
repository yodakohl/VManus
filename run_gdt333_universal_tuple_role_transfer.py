#!/usr/bin/env python3
"""Run held-register placement transfer for all-register joint tuples."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;INTER=R/'gdt327_joint_tuple_interlinear.tsv';PORT=R/'gdt332_joint_tuple_portability.tsv';METHOD=R/'GDT333_UNIVERSAL_TUPLE_ROLE_TRANSFER_METHOD.md';TS=R/'gdt333_tuple_role_scores.tsv';RS=R/'gdt333_register_scores.tsv';REPORT=R/'GDT333_UNIVERSAL_TUPLE_ROLE_TRANSFER_REPORT.md';RESULT=R/'gdt333_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def roles(x):
 gi=int(x['group_index']);gc=int(x['group_count']);return (x['line_first'],x['within_field_position'],str(min(4,int(x['field_ordinal']))),str(min(3,int(4*(gi-1)/max(1,gc)))))
def main():
 rows=read(INTER);assert len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);universal={x['joint_tuple_id'] for x in read(PORT) if x['all_five_registers']=='1'};assert len(universal)==53;target=[x for x in rows if x['joint_tuple_id'] in universal];regs=sorted({x['register'] for x in target});classes=[sorted({roles(x)[j] for x in target}) for j in range(4)];tot=Counter();br=defaultdict(Counter);bt=Counter()
 for hold in regs:
  train=[x for x in target if x['register']!=hold];test=[x for x in target if x['register']==hold]
  for j,C in enumerate(classes):
   globalc=Counter(roles(x)[j] for x in train);coord=defaultdict(Counter);tu=defaultdict(Counter)
   for x in train:coord[x['coordinate_id']][roles(x)[j]]+=1;tu[x['joint_tuple_id']][roles(x)[j]]+=1
   for x in test:
    y=roles(x)[j];cs=(('GLOBAL',globalc),('COORDINATE',coord[x['coordinate_id']]),('JOINT_TUPLE',tu[x['joint_tuple_id']]))
    bits={n:-math.log2((c[y]+.5)/(sum(c.values())+.5*len(C))) for n,c in cs}
    for n,b in bits.items():tot[n]+=b;br[hold][n]+=b;bt[x['joint_tuple_id'],hold,n]+=b
 regrows=[]
 for reg in regs:
  q=[x for x in target if x['register']==reg];regrows.append({'register':reg,'events':len(q),'component_predictions':4*len(q),'global_bits':f"{br[reg]['GLOBAL']:.12f}",'coordinate_bits':f"{br[reg]['COORDINATE']:.12f}",'joint_tuple_bits':f"{br[reg]['JOINT_TUPLE']:.12f}",'coordinate_gain_vs_global':f"{br[reg]['GLOBAL']-br[reg]['COORDINATE']:.12f}",'tuple_gain_vs_coordinate':f"{br[reg]['COORDINATE']-br[reg]['JOINT_TUPLE']:.12f}"})
 write(RS,regrows);tuplerows=[]
 for ident in sorted(universal):
  gains={r:bt[ident,r,'COORDINATE']-bt[ident,r,'JOINT_TUPLE'] for r in regs};z=[x for x in target if x['joint_tuple_id']==ident];tuplerows.append({'joint_tuple_id':ident,'host_id':z[0]['host_id'],'coordinate_id':z[0]['coordinate_id'],'events':len(z),'physical_folios':len({x['physical_folio'] for x in z}),'total_gain_vs_coordinate':f'{sum(gains.values()):.12f}','positive_registers':sum(v>0 for v in gains.values()),**{r.lower()+'_gain':f'{gains[r]:.12f}' for r in regs},'semantic_state':'UNASSIGNED','translation_state':'UNASSIGNED'})
 tuplerows.sort(key=lambda x:-float(x['total_gain_vs_coordinate']));write(TS,tuplerows);positive=sum(float(x['tuple_gain_vs_coordinate'])>0 for x in regrows);allpos=sum(int(x['positive_registers'])==5 for x in tuplerows);four=sum(int(x['positive_registers'])>=4 for x in tuplerows);gain=tot['COORDINATE']-tot['JOINT_TUPLE'];status='UNIVERSAL_TUPLE_PLACEMENT_AGGREGATE_REGISTER_UNSTABLE'
 report=f'''# GDT333 — universal tuple structural-role transfer

Status: **{status}**.

The 53 all-register tuples contribute {len(target):,} events and {4*len(target):,} held component predictions. Coordinate identity saves {tot['GLOBAL']-tot['COORDINATE']:+.3f} bits over the global placement code. Exact joint-tuple identity saves a further {gain:+.3f} bits in aggregate.

That aggregate is not register-universal. Only {positive}/5 held registers improve: Herbal A {br['HERBAL_A']['COORDINATE']-br['HERBAL_A']['JOINT_TUPLE']:+.3f}, Herbal B {br['HERBAL_B']['COORDINATE']-br['HERBAL_B']['JOINT_TUPLE']:+.3f}, Other A {br['OTHER_A']['COORDINATE']-br['OTHER_A']['JOINT_TUPLE']:+.3f}, Other B {br['OTHER_B']['COORDINATE']-br['OTHER_B']['JOINT_TUPLE']:+.3f}, and Stars/Recipe B {br['STARS_RECIPE_B']['COORDINATE']-br['STARS_RECIPE_B']['JOINT_TUPLE']:+.3f} bits. No tuple improves in all five registers; {four} improve in at least four.

Thus the universal joint inventory does not carry one stable manuscript-wide structural-role dictionary.  The eight 4-of-5 tuples are retained as higher-quality functional candidates, with their failing register explicit.  Register-dependent rebinding or usage remains necessary.

No semantic role, word, morpheme, POS, sound, meaning, language, plaintext, or translation is assigned. No f84 row was opened, retained, joined, or scored.
''';REPORT.write_text(report)
 result={'schema':'GDT333_UNIVERSAL_TUPLE_ROLE_TRANSFER_RESULT_V1','status':status,'summary':{'tuples':len(universal),'events':len(target),'component_predictions':4*len(target),'global_bits':tot['GLOBAL'],'coordinate_bits':tot['COORDINATE'],'joint_tuple_bits':tot['JOINT_TUPLE'],'coordinate_gain_vs_global':tot['GLOBAL']-tot['COORDINATE'],'tuple_gain_vs_coordinate':gain,'positive_registers':positive,'all_five_positive_tuples':allpos,'at_least_four_positive_tuples':four},'claim_ceiling':'Register-held abstract placement only; no stable semantic role meaning plaintext or translation.','f84':{'input_rows':0,'opened':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (INTER,PORT,R/'gdt332_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{TS.name:sha(TS),RS.name:sha(RS)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'summary':result['summary']},sort_keys=True))
if __name__=='__main__':main()
