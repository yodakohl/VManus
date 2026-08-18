#!/usr/bin/env python3
"""Independent primary validation for GDT286."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt286_result.json';OUT=R/'gdt286_validation.json';MODELS=('SHAPE_CONTEXT','EXACT_HOST','EXACT_HOST_X_POSITION')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=2e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def bk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['page_host'][-1:])
def perm(events,panel,world):
 st=defaultdict(list)
 for i,r in enumerate(events):st[(r['physical_folio'],)+bk(r)].append(i)
 rng=random.Random(int(hashlib.sha256(f'GDT286_WITHIN_FOLIO_SHAPE_HOST_ID|{panel}|{world}'.encode()).hexdigest()[:16],16));out=[r['page_host'] for r in events]
 for k in sorted(st):
  ids=st[k];v=[out[i] for i in ids];rng.shuffle(v)
  for i,x in zip(ids,v):out[i]=x
 return out
def score(events,split,ids=None):
 prior=11.;ids=ids or [r['page_host'] for r in events];wr=sorted({r['wrapper'] for r in events});K=len(wr);folds=defaultdict(list)
 for i,r in enumerate(events):folds[r[split]].append(i)
 g=Counter();fg=defaultdict(Counter);gb=defaultdict(Counter);fb=defaultdict(lambda:defaultdict(Counter));gh=defaultdict(Counter);fh=defaultdict(lambda:defaultdict(Counter));gp=defaultdict(Counter);fp=defaultdict(lambda:defaultdict(Counter))
 for i,r in enumerate(events):
  f=r[split];w=r['wrapper'];b=bk(r);h=ids[i];p=(h,r['within_field_position']);g[w]+=1;fg[f][w]+=1;gb[b][w]+=1;fb[f][b][w]+=1;gh[h][w]+=1;fh[f][h][w]+=1;gp[p][w]+=1;fp[f][p][w]+=1
 bits=Counter();top=Counter();covered=0;foldrows=[]
 for held,ii in sorted(folds.items()):
  page=defaultdict(Counter);bb=Counter();tt=Counter();cc=0;ntrain=len(events)-len(ii)
  for i in ii:
   r=events[i];actual=r['wrapper'];b=bk(r);h=ids[i];p=(h,r['within_field_position']);past=page[r['page']];prob={m:{} for m in MODELS}
   for w in wr:
    p0=(g[w]-fg[held][w]+.5)/(ntrain+.5*K);pp=(past[w]+prior*p0)/(sum(past.values())+prior);nb=sum(gb[b].values())-sum(fb[held][b].values());pb=(gb[b][w]-fb[held][b][w]+prior*pp)/(nb+prior);nh=sum(gh[h].values())-sum(fh[held][h].values());ph=(gh[h][w]-fh[held][h][w]+prior*pb)/(nh+prior);np=sum(gp[p].values())-sum(fp[held][p].values());php=(gp[p][w]-fp[held][p][w]+prior*ph)/(np+prior);prob['SHAPE_CONTEXT'][w]=pb;prob['EXACT_HOST'][w]=ph;prob['EXACT_HOST_X_POSITION'][w]=php
   nh=sum(gh[h].values())-sum(fh[held][h].values());cc+=int(nh>0)
   for m in MODELS:
    v=-math.log2(prob[m][actual]);bits[m]+=v;bb[m]+=v;ok=int(max(wr,key=lambda w:(prob[m][w],-wr.index(w)))==actual);top[m]+=ok;tt[m]+=ok
   past[actual]+=1
  covered+=cc
  for m in MODELS:foldrows.append((held,m,len(ii),cc,bb[m],tt[m]))
 return dict(bits),dict(top),covered,foldrows
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt286_design.json').read_text());res=json.loads(RESULT.read_text());pr=rows(R/'gdt286_panel_scores.tsv');fr=rows(R/'gdt286_folio_scores.tsv');nr=rows(R/'gdt286_null_results.tsv');sr=rows(R/'gdt286_voynich_transfer_sensitivities.tsv')
 ck('design',d['status']=='FROZEN_BEFORE_GDT286_SCORING' and d['content_sha256']==csha(d));mf=rows(R/'gdt286_freeze_manifest.tsv');ck('freeze',len(mf)==5 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('counts',len(pr)==24 and len(fr)==1974 and len(nr)==512 and len(sr)==4)
 native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('events',all(len(x)==8448 for x in panels.values()))
 for p in d['panels']:
  q=[x for x in pr if x['control_id']==p];ck('panel_rows:'+p,len(q)==3 and all(int(x['events'])==8448 and close(x['bits_per_event'],float(x['bits'])/8448) and close(x['top1_rate'],int(x['top1'])/8448) for x in q));z=[x for x in fr if x['control_id']==p];ck('fold_sum:'+p,all(close(next(x for x in q if x['model']==m)['bits'],sum(float(x['bits']) for x in z if x['model']==m)) and int(next(x for x in q if x['model']==m)['top1'])==sum(int(x['top1']) for x in z if x['model']==m) for m in MODELS))
 v=panels['VOYNICH_REFERENCE'];bits,top,cov,folds=score(v,'physical_folio')
 for m in MODELS:
  x=next(q for q in pr if q['control_id']=='VOYNICH_REFERENCE' and q['model']==m);ck('direct_voynich:'+m,close(x['bits'],bits[m]) and int(x['top1'])==top[m] and int(x['covered_exact_host_events'])==cov)
 for held,m,n,cc,b,t in folds:
  x=next(q for q in fr if q['control_id']=='VOYNICH_REFERENCE' and q['held_value']==held and q['model']==m);ck('direct_fold:'+held+':'+m,int(x['events'])==n and int(x['covered_exact_host_events'])==cc and close(x['bits'],b) and int(x['top1'])==t)
 p0=perm(v,'VOYNICH_REFERENCE',0);nb,nt,nc,nf=score(v,'physical_folio',p0);x=next(q for q in nr if q['control_id']=='VOYNICH_REFERENCE' and q['world_index']=='0');ck('null0',close(x['exact_host_gain_bits_per_event'],(bits['SHAPE_CONTEXT']-nb['EXACT_HOST'])/8448));ck('null_mobile',int(res['voynich_summary']['null_mobile_events_world0'])==sum(a!=b['page_host'] for a,b in zip(p0,v)))
 for split in ('section','hand'):
  b,t,c,f=score(v,split)
  for m in MODELS[:2]:
   x=next(q for q in sr if q['split']=='HELD_'+split.upper() and q['model']==m);ck('sensitivity:'+split+':'+m,close(x['bits'],b[m]) and int(x['top1'])==t[m] and int(x['covered_exact_host_events'])==c)
 ng=defaultdict(list)
 for x in nr:ng[x['control_id']].append(float(x['exact_host_gain_bits_per_event']))
 observed={p:(float(next(x for x in pr if x['control_id']==p and x['model']=='SHAPE_CONTEXT')['bits'])-float(next(x for x in pr if x['control_id']==p and x['model']=='EXACT_HOST')['bits']))/8448 for p in d['panels']};means={p:statistics.mean(ng[p]) for p in d['panels']};sds={p:statistics.pstdev(ng[p]) for p in d['panels']};oz={p:(observed[p]-means[p])/sds[p] for p in d['panels']};wm=[max((ng[p][i]-means[p])/sds[p] for p in d['panels']) for i in range(64)]
 rv=res['voynich_summary'];p='VOYNICH_REFERENCE';local=(1+sum(x>=observed[p]-1e-15 for x in ng[p]))/65;mp=(1+sum(x>=oz[p]-1e-15 for x in wm))/65;ck('summary',close(rv['exact_host_gain_bits_per_event'],observed[p]) and close(rv['null_mean'],means[p]) and close(rv['null_sd'],sds[p]) and close(rv['host_gain_above_null_mean_bits_per_event'],observed[p]-means[p]) and close(rv['local_p'],local) and close(rv['max8_p'],mp))
 hostbits=float(next(x for x in pr if x['control_id']==p and x['model']=='EXACT_HOST')['bits']);hpbits=float(next(x for x in pr if x['control_id']==p and x['model']=='EXACT_HOST_X_POSITION')['bits']);pos=(hostbits-hpbits)/8448;sec={x['model']:x for x in sr if x['split']=='HELD_SECTION'};hand={x['model']:x for x in sr if x['split']=='HELD_HAND'};sg=(float(sec['SHAPE_CONTEXT']['bits'])-float(sec['EXACT_HOST']['bits']))/8448;hg=(float(hand['SHAPE_CONTEXT']['bits'])-float(hand['EXACT_HOST']['bits']))/8448;g={'held_folio_exact_host_gain_positive':observed[p]>0,'max8_p_le_0_05':mp<=.05,'host_position_increment_nonpositive':pos<=0,'held_section_or_hand_gain_positive':sg>0 or hg>0};status=d['decision']['stable'] if g['held_folio_exact_host_gain_positive'] and g['max8_p_le_0_05'] and g['host_position_increment_nonpositive'] and g['held_section_or_hand_gain_positive'] else d['decision']['contextual'] if g['held_folio_exact_host_gain_positive'] and g['max8_p_le_0_05'] and pos>0 else d['decision']['fail'];ck('decision',g==res['frozen_gates'] and res['status']==status and close(res['voynich_held_section_gain_bits_per_event'],sg) and close(res['voynich_held_hand_gain_bits_per_event'],hg));ck('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));ck('inputs',all(sha(R/k)==v for k,v in res['inputs'].items()));ck('docs',all(sha(R/k)==v for k,v in res['documents'].items()));ck('impl',all(sha(R/k)==v for k,v in res['implementation'].items()));ck('outputs',all(sha(R/k)==v for k,v in res['outputs'].items()));ck('content',res['content_sha256']==csha(res))
 out={'schema':'GDT286_HOST_TO_WRAPPER_TRANSFER_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_VOYNICH_ALL_SPLIT_AND_WORLD0_RESCORE_PLUS_ALL_PANEL_ACCOUNTING_AND_NULL_DECISION','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
