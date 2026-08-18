#!/usr/bin/env python3
"""Nested held-folio exact joint-tuple retrieval from line placement."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;INTER=R/'gdt327_joint_tuple_interlinear.tsv';METHOD=R/'GDT336_PLACEMENT_CONDITIONED_TUPLE_RETRIEVAL_METHOD.md';FOLDS=R/'gdt336_folds.tsv';REGS=R/'gdt336_register_scores.tsv';REPORT=R/'GDT336_PLACEMENT_CONDITIONED_TUPLE_RETRIEVAL_REPORT.md';RESULT=R/'gdt336_result.json';ALPHAS=(32,64,128,256,512,1024)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def place(x):
 gi=int(x['group_index']);gc=int(x['group_count']);return (x['line_first'],x['within_field_position'],str(min(3,int(4*(gi-1)/max(1,gc)))))
def cache(rows):
 total=Counter();folio=defaultdict(Counter);events=defaultdict(list);candidates=defaultdict(set)
 for x in rows:
  f=x['physical_folio'];c=x['coordinate_id'];p=place(x);y=x['joint_tuple_id'];events[f].append(x);candidates[c].add(y)
  for q in (total,folio[f]):q['B',c,y]+=1;q['B',c,'#']+=1;q['P',c,p,y]+=1;q['P',c,p,'#']+=1
 return total,folio,events,candidates
def score(cached,excluded,test,top=False):
 total,folio,_,candidates=cached;bits0=0.;bits={a:0. for a in ALPHAS};n=0;top0={a:0 for a in (0,)};topm={a:0 for a in ALPHAS};memo={};base={}
 for x in test:
  c=x['coordinate_id'];p=place(x);y=x['joint_tuple_id'];key=(c,p)
  if c not in base:
   cand=[q for q in candidates[c] if total['B',c,q]-sum(folio[f]['B',c,q] for f in excluded)>0];bn=total['B',c,'#']-sum(folio[f]['B',c,'#'] for f in excluded);base[c]=(cand,bn)
  cand,bn=base[c]
  if y not in cand:continue
  pn=total['P',c,p,'#']-sum(folio[f]['P',c,p,'#'] for f in excluded);by=total['B',c,y]-sum(folio[f]['B',c,y] for f in excluded);py=total['P',c,p,y]-sum(folio[f]['P',c,p,y] for f in excluded);pby=(by+.5)/(bn+.5*len(cand));n+=1;bits0-=math.log2(pby)
  for a in ALPHAS:bits[a]-=math.log2((py+a*pby)/(pn+a))
  if top:
   if key not in memo:
    pb={q:(total['B',c,q]-sum(folio[f]['B',c,q] for f in excluded)+.5)/(bn+.5*len(cand)) for q in cand};pm={a:{q:(total['P',c,p,q]-sum(folio[f]['P',c,p,q] for f in excluded)+a*pb[q])/(pn+a) for q in cand} for a in ALPHAS};memo[key]=(pb,pm)
   pb,pm=memo[key]
   top0[0]+=max(pb,key=lambda q:(pb[q],q))==y
   for a in ALPHAS:topm[a]+=max(pm[a],key=lambda q:(pm[a][q],q))==y
 return n,bits0,bits,top0[0],topm
def main():
 rows=read(INTER);assert len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);folds=[]
 for reg in sorted({x['register'] for x in rows}):
  rr=[x for x in rows if x['register']==reg];cached=cache(rr);folios=sorted(cached[2])
  for hold in folios:
   inner=Counter()
   for iv in (f for f in folios if f!=hold):
    _,_,b,_,_=score(cached,{hold,iv},cached[2][iv])
    for a in ALPHAS:inner[a]+=b[a]
   alpha=min(ALPHAS,key=lambda a:(inner[a],a));n,b0,b,top0,top=score(cached,{hold},cached[2][hold],True);folds.append({'register':reg,'held_folio':hold,'scored_events':n,'selected_alpha':alpha,'coordinate_bits':f'{b0:.12f}','placement_bits':f'{b[alpha]:.12f}','placement_gain':f'{b0-b[alpha]:.12f}','coordinate_top1':top0,'placement_top1':top[alpha],'positive_gain':int(b0>b[alpha])})
 write(FOLDS,folds);regrows=[]
 for reg in sorted({x['register'] for x in rows}):
  z=[x for x in folds if x['register']==reg];regrows.append({'register':reg,'folds':len(z),'scored_events':sum(int(x['scored_events']) for x in z),'coordinate_bits':f"{sum(float(x['coordinate_bits']) for x in z):.12f}",'placement_bits':f"{sum(float(x['placement_bits']) for x in z):.12f}",'placement_gain':f"{sum(float(x['placement_gain']) for x in z):.12f}",'coordinate_top1':sum(int(x['coordinate_top1']) for x in z),'placement_top1':sum(int(x['placement_top1']) for x in z),'positive_folds':sum(int(x['positive_gain']) for x in z),'alpha_choices':'|'.join(f"{a}:{sum(int(x['selected_alpha'])==a for x in z)}" for a in ALPHAS)})
 write(REGS,regrows);summary={'folds':len(folds),'scored_events':sum(int(x['scored_events']) for x in folds),'coordinate_bits':sum(float(x['coordinate_bits']) for x in folds),'placement_bits':sum(float(x['placement_bits']) for x in folds),'placement_gain':sum(float(x['placement_gain']) for x in folds),'coordinate_top1':sum(int(x['coordinate_top1']) for x in folds),'placement_top1':sum(int(x['placement_top1']) for x in folds),'positive_folds':sum(int(x['positive_gain']) for x in folds),'positive_registers':sum(float(x['placement_gain'])>0 for x in regrows)};status='LINE_PLACEMENT_WEAKLY_IMPROVES_EXACT_TUPLE_RETRIEVAL' if summary['placement_gain']>0 and summary['positive_registers']>=4 else ('PLACEMENT_TUPLE_RETRIEVAL_AGGREGATE_ONLY' if summary['placement_gain']>0 else 'PLACEMENT_TUPLE_RETRIEVAL_NOT_SUPPORTED');detail=', '.join(f"{x['register']} {float(x['placement_gain']):+.2f}" for x in regrows)
 report=f'''# GDT336 — placement-conditioned exact tuple retrieval

Status: **{status}**.

Nested held-folio evaluation scores {summary['scored_events']:,} recurrent-tuple events. Line placement saves {summary['placement_gain']:+.3f} bits over coordinate frequency, improves {summary['positive_folds']}/{summary['folds']} folio folds and {summary['positive_registers']}/5 registers, and changes exact top-1 retrieval from {summary['coordinate_top1']}/{summary['scored_events']} to {summary['placement_top1']}/{summary['scored_events']}.

Per-register held gains: {detail}.

The large selected concentrations mean placement is a weak correction to a dominant coordinate-specific tuple prior, not a standalone decoder.  It is nevertheless executable and held-folio transferable.

No tuple meaning, semantic role, word, POS, sound, language, plaintext, or translation is assigned. No f84 row was opened, retained, joined, or scored.
''';REPORT.write_text(report)
 result={'schema':'GDT336_PLACEMENT_CONDITIONED_TUPLE_RETRIEVAL_RESULT_V1','status':status,'summary':summary,'registers':regrows,'claim_ceiling':'Weak held-folio formal tuple retrieval prior only; no semantics meaning plaintext or translation.','f84':{'input_rows':0,'opened':False,'retained':False,'joined':False,'scored':False},'inputs':{INTER.name:sha(INTER),R.name if False else 'gdt335_result.json':sha(R/'gdt335_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{FOLDS.name:sha(FOLDS),REGS.name:sha(REGS)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'summary':summary,'registers':regrows},sort_keys=True))
if __name__=='__main__':main()
