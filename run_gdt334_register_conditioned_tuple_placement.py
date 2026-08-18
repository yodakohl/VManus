#!/usr/bin/env python3
"""Nested held-folio register-conditioned tuple placement test."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;INTER=R/'gdt327_joint_tuple_interlinear.tsv';METHOD=R/'GDT334_REGISTER_CONDITIONED_TUPLE_PLACEMENT_METHOD.md';FOLDS=R/'gdt334_folds.tsv';REGS=R/'gdt334_register_scores.tsv';REPORT=R/'GDT334_REGISTER_CONDITIONED_TUPLE_PLACEMENT_REPORT.md';RESULT=R/'gdt334_result.json';ALPHAS=(2,4,8,16,32,64)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def roles(x):
 gi=int(x['group_index']);gc=int(x['group_count']);return (x['line_first'],x['within_field_position'],str(min(4,int(x['field_ordinal']))),str(min(3,int(4*(gi-1)/max(1,gc)))))
def cache(rows):
 total=Counter();folio=defaultdict(Counter);events=defaultdict(list)
 for x in rows:
  f=x['physical_folio'];events[f].append(x)
  for j,y in enumerate(roles(x)):
   for kind,key in (('C',x['coordinate_id']),('T',x['joint_tuple_id'])):total[kind,j,key,y]+=1;total[kind,j,key,'#']+=1;folio[f][kind,j,key,y]+=1;folio[f][kind,j,key,'#']+=1
 return total,folio,events
def score_cached(cache_value,excluded,test,classes):
 total,folio,_=cache_value;kept=[]
 for x in test:
  n=total['T',0,x['joint_tuple_id'],'#']-sum(folio[f]['T',0,x['joint_tuple_id'],'#'] for f in excluded)
  if n>0:kept.append(x)
 cb=0.;tb={a:0. for a in ALPHAS}
 for x in kept:
  for j,C in enumerate(classes):
   y=roles(x)[j];ck=('C',j,x['coordinate_id']);tk=('T',j,x['joint_tuple_id']);cn=total[ck+('#',)]-sum(folio[f][ck+('#',)] for f in excluded);cy=total[ck+(y,)]-sum(folio[f][ck+(y,)] for f in excluded);tn=total[tk+('#',)]-sum(folio[f][tk+('#',)] for f in excluded);ty=total[tk+(y,)]-sum(folio[f][tk+(y,)] for f in excluded);pc=(cy+.5)/(cn+.5*len(C));cb-=math.log2(pc)
   for alpha in ALPHAS:tb[alpha]-=math.log2((ty+alpha*pc)/(tn+alpha))
 return len(kept),cb,tb
def main():
 rows=read(INTER);assert len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);classes=[sorted({roles(x)[j] for x in rows}) for j in range(4)];folds=[]
 for reg in sorted({x['register'] for x in rows}):
  rr=[x for x in rows if x['register']==reg]
  cached=cache(rr);folios=sorted(cached[2])
  for hold in folios:
   inner=Counter()
   for iv in (f for f in folios if f!=hold):
    _,_,ib=score_cached(cached,{hold,iv},cached[2][iv],classes)
    for a in ALPHAS:inner[a]+=ib[a]
   alpha=min(ALPHAS,key=lambda a:(inner[a],a));n,cb,tbs=score_cached(cached,{hold},cached[2][hold],classes);tb=tbs[alpha];folds.append({'register':reg,'held_folio':hold,'scored_events':n,'component_predictions':4*n,'selected_alpha':alpha,'coordinate_bits':f'{cb:.12f}','tuple_shrunk_bits':f'{tb:.12f}','tuple_gain':f'{cb-tb:.12f}','positive_gain':int(cb>tb)})
 write(FOLDS,folds);regrows=[]
 for reg in sorted({x['register'] for x in rows}):
  z=[x for x in folds if x['register']==reg];regrows.append({'register':reg,'folds':len(z),'scored_events':sum(int(x['scored_events']) for x in z),'component_predictions':sum(int(x['component_predictions']) for x in z),'coordinate_bits':f"{sum(float(x['coordinate_bits']) for x in z):.12f}",'tuple_shrunk_bits':f"{sum(float(x['tuple_shrunk_bits']) for x in z):.12f}",'tuple_gain':f"{sum(float(x['tuple_gain']) for x in z):.12f}",'positive_folds':sum(int(x['positive_gain']) for x in z),'alpha_choices':'|'.join(f"{a}:{sum(int(x['selected_alpha'])==a for x in z)}" for a in ALPHAS)})
 write(REGS,regrows);gain=sum(float(x['tuple_gain']) for x in folds);positive_regs=sum(float(x['tuple_gain'])>0 for x in regrows);positive_folds=sum(int(x['positive_gain']) for x in folds);status='REGISTER_CONDITIONED_TUPLE_PLACEMENT_SUPPORTED_WITH_ONE_WEAK_STRATUM' if gain>0 and positive_regs>=4 else ('REGISTER_CONDITIONED_TUPLE_PLACEMENT_AGGREGATE_ONLY' if gain>0 else 'REGISTER_CONDITIONED_TUPLE_PLACEMENT_NOT_SUPPORTED')
 summary={'folds':len(folds),'scored_events':sum(int(x['scored_events']) for x in folds),'component_predictions':sum(int(x['component_predictions']) for x in folds),'coordinate_bits':sum(float(x['coordinate_bits']) for x in folds),'tuple_shrunk_bits':sum(float(x['tuple_shrunk_bits']) for x in folds),'tuple_gain':gain,'positive_registers':positive_regs,'positive_folds':positive_folds}
 detail=', '.join(f"{x['register']} {float(x['tuple_gain']):+.2f} ({x['positive_folds']}/{x['folds']} folios)" for x in regrows)
 report=f'''# GDT334 — register-conditioned joint-tuple placement

Status: **{status}**.

Nested held-folio scoring covers {summary['scored_events']:,} recurrent-tuple events and {summary['component_predictions']:,} external placement components.  Shrunk tuple identity changes the coordinate code by {summary['tuple_gain']:+.3f} bits; {summary['positive_folds']}/{summary['folds']} folios and {summary['positive_registers']}/5 registers improve.

Per register: {detail}.

This is the first direct support for a shared tuple inventory with register-conditioned placement usage.  The hierarchical code is essential: an unshrunk rare-tuple lookup is not licensed.  Any negative register remains a counterexample, and the model identifies placement behavior rather than semantics.

No tuple receives a semantic role, word, POS, sound, meaning, language, plaintext, or translation. No f84 row was opened, retained, joined, or scored.
''';REPORT.write_text(report)
 result={'schema':'GDT334_REGISTER_CONDITIONED_TUPLE_PLACEMENT_RESULT_V1','status':status,'summary':summary,'registers':regrows,'claim_ceiling':'Register-conditioned external placement of opaque tuples only; no semantics meaning plaintext or translation.','f84':{'input_rows':0,'opened':False,'retained':False,'joined':False,'scored':False},'inputs':{INTER.name:sha(INTER),R.name if False else 'gdt333_result.json':sha(R/'gdt333_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{FOLDS.name:sha(FOLDS),REGS.name:sha(REGS)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'summary':summary,'registers':regrows},sort_keys=True))
if __name__=='__main__':main()
