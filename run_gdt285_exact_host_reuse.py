#!/usr/bin/env python3
"""Run frozen GDT285 exact-host reuse localization."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;DESIGN=R/'gdt285_design.json';METHOD=R/'GDT285_EXACT_HOST_REUSE_TERMINAL_LOCALIZATION_METHOD.md';REPORT=R/'GDT285_EXACT_HOST_REUSE_TERMINAL_LOCALIZATION_REPORT.md';RESULT=R/'gdt285_result.json'
OUT_BIN=R/'gdt285_recurrence_bins.tsv';OUT_FOLD=R/'gdt285_folio_scores.tsv';OUT_CAP=R/'gdt285_donor_capacity.tsv';OUT_SUM=R/'gdt285_summary.tsv';OUT_COUNTER=R/'gdt285_counterexamples.tsv'
COMPS=('INITIAL','INTERNAL','FINAL','EOS');FIELDS=(('register',str),('record_ordinal',int),('field_ordinal',int),('within_field_position',str),('local_frame',str),('inner_d',str),('right_family',str),('dy_closure',str),('b3',str),('line_close',int),('paragraph_close',int),('known_label_renderer',str));MODES=('STANDARD','EXACT_HOST_EXCLUDED','MATCHED_NONHOST_EXCLUDED');BINS=('ZERO','ONE','TWO_TO_THREE','FOUR_TO_SEVEN','EIGHT_PLUS')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rcsha(v):q=dict(v);q.pop('content_sha256',None);return csha(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rr):
 ff=[]
 for r in rr:
  for k in r:
   if k not in ff:ff.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'NA') for k in ff} for r in rr])
def key(r,full):
 z=tuple(conv(r[n]) for n,conv in FIELDS);return z+((r['wrapper'],) if full else ())
def chars(host):
 h='^^';n=len(host)
 for i,c in enumerate(host):yield h[-2:],c,'INITIAL' if i==0 else 'FINAL' if i==n-1 else 'INTERNAL';h+=c
 yield h[-2:],'<EOS>','EOS'
def rbin(n):return 'ZERO' if n==0 else 'ONE' if n==1 else 'TWO_TO_THREE' if n<=3 else 'FOUR_TO_SEVEN' if n<=7 else 'EIGHT_PLUS'
def tierkey(r,t):
 base=(r['section'],r['currier'],r['hand'])
 if t==0:return base+(r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['wrapper'])
 if t==1:return base+(int(r['host_length']),r['page_host'][:1],r['wrapper'])
 if t==2:return (int(r['host_length']),r['page_host'][:1],r['wrapper'])
 if t==3:return (int(r['host_length']),r['page_host'][:1])
 return ('ALL',)
def donor_map(events,trainids,target_hosts,panel,held):
 pools=[defaultdict(list) for _ in range(5)]
 for i in trainids:
  for t in range(5):pools[t][tierkey(events[i],t)].append(i)
 for t in range(5):
  for k in pools[t]:pools[t][k].sort(key=lambda i:hashlib.sha256(f"GDT285_DONOR_ORDER|{panel}|{held}|{events[i]['observation_id']}".encode()).hexdigest())
 byhost=defaultdict(list)
 for i in trainids:byhost[events[i]['page_host']].append(i)
 out={};tc={}
 for host in sorted(target_hosts):
  src=sorted(byhost[host],key=lambda i:events[i]['observation_id']);used=set();chosen=[];cnt=Counter()
  for si in src:
   pick=None
   for t in range(5):
    pool=pools[t][tierkey(events[si],t)]
    if not pool:continue
    off=int(hashlib.sha256(f"GDT285_DONOR_START|{panel}|{held}|{host}|{events[si]['observation_id']}|{t}".encode()).hexdigest()[:16],16)%len(pool)
    for j in range(len(pool)):
     q=pool[(off+j)%len(pool)]
     if q not in used and events[q]['page_host']!=host:pick=q;break
    if pick is not None:cnt[t]+=1;break
   assert pick is not None;used.add(pick);chosen.append(pick)
  assert len(chosen)==len(src);out[host]=chosen;tc[host]=cnt
 return out,tc
def score_model(events,testids,trip,keys,ga,ca,hga,hca,dga,dca,mode,K,prior):
 pc=defaultdict(lambda:defaultdict(Counter));out={}
 for i in testids:
  r=events[i];host=r['page_host'];k=keys[i];bits=Counter();xg=hga[host] if mode=='EXACT_HOST_EXCLUDED' else dga[host] if mode=='MATCHED_NONHOST_EXCLUDED' else {};xc=hca[host] if mode=='EXACT_HOST_EXCLUDED' else dca[host] if mode=='MATCHED_NONHOST_EXCLUDED' else {}
  for hist,c,z in trip[i]:
   a=ga[hist];x=xg.get(hist,{});gn=sum(a.values())-sum(x.values());gc=a[c]-x.get(c,0);pb=(gc+.5)/(gn+.5*K);p=pc[r['page']][hist];pp=(p[c]+prior*pb)/(sum(p.values())+prior);a=ca[k,hist];x=xc.get((k,hist),{});cn=sum(a.values())-sum(x.values());cc=a[c]-x.get(c,0);prob=(cc+prior*pp)/(cn+prior);bits[z]+=-math.log2(prob);p[c]+=1
  out[i]=dict(bits)
 return out
def panel_job(item):
 panel,events=item;d=json.loads((R/'gdt276_design.json').read_text());K=len(d['alphabet']);prior=d['capacity']['character_context_prior_mass'];trip=[list(chars(r['page_host'])) for r in events];by=defaultdict(list)
 for i,r in enumerate(events):by[r['physical_folio']].append(i)
 agg=defaultdict(lambda:{'events':0,'recurrence_sum':0,**{c:0. for c in COMPS}});foldagg=defaultdict(lambda:{'events':0,'recurrent_events':0,**{c:0. for c in COMPS}});cap=[]
 for held,testids in sorted(by.items()):
  trainids=[i for f,ids in by.items() if f!=held for i in ids];hc=Counter(events[i]['page_host'] for i in trainids);targets={events[i]['page_host'] for i in testids};dm,tiers=donor_map(events,trainids,targets,panel,held)
  ct=Counter();
  for h in targets:ct.update(tiers[h])
  cap.append({'control_id':panel,'held_folio':held,'target_host_cases':len(targets),'zero_recurrence_cases':sum(hc[h]==0 for h in targets),'donor_events':sum(hc[h] for h in targets),**{f'tier_{t}_events':ct[t] for t in range(5)}})
  scores={}
  for full in (False,True):
   keys=[key(r,full) for r in events];ga=defaultdict(Counter);ca=defaultdict(Counter);hga=defaultdict(lambda:defaultdict(Counter));hca=defaultdict(lambda:defaultdict(Counter));dga=defaultdict(lambda:defaultdict(Counter));dca=defaultdict(lambda:defaultdict(Counter))
   for i in trainids:
    hst=events[i]['page_host'];k=keys[i]
    for hist,c,_ in trip[i]:ga[hist][c]+=1;ca[k,hist][c]+=1;hga[hst][hist][c]+=1;hca[hst][(k,hist)][c]+=1
   for hst,ids in dm.items():
    for i in ids:
     k=keys[i]
     for hist,c,_ in trip[i]:dga[hst][hist][c]+=1;dca[hst][(k,hist)][c]+=1
   for mode in MODES:scores[full,mode]=score_model(events,testids,trip,keys,ga,ca,hga,hca,dga,dca,mode,K,prior)
  for i in testids:
   bn=rbin(hc[events[i]['page_host']])
   for mode in MODES:
    a=agg[mode,bn];f=foldagg[mode,held];a['events']+=1;a['recurrence_sum']+=hc[events[i]['page_host']];f['events']+=1;f['recurrent_events']+=int(hc[events[i]['page_host']]>0)
    for c in COMPS:
     g=scores[False,mode][i].get(c,0)-scores[True,mode][i].get(c,0);a[c]+=g;f[c]+=g
 return panel,{k:dict(v) for k,v in agg.items()},{k:dict(v) for k,v in foldagg.items()},cap
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='FROZEN_BEFORE_GDT285_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt285_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(x)==8448 for x in panels.values())
 results={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(panel_job,x):x[0] for x in panels.items()}
  for f in as_completed(fs):q=f.result();results[q[0]]=q;print(json.dumps({'scored':q[0]},sort_keys=True),flush=True)
 bins=[];folds=[];caps=[];summary=[]
 for panel in d['panels']:
  _,agg,fa,cp=results[panel];caps.extend(cp)
  for mode in MODES:
   for bn in BINS:
    x=agg[mode,bn];n=x['events'];bins.append({'control_id':panel,'mode':mode,'recurrence_bin':bn,'events':n,'mean_training_recurrence':f"{(x['recurrence_sum']/n if n else 0):.12f}",**{f'gain_{c.lower()}_bits':f"{x[c]:.12f}" for c in COMPS},**{f'gain_{c.lower()}_bits_per_event':f"{(x[c]/n if n else 0):.12f}" for c in COMPS},'gain_onset_body_bits_per_event':f"{((x['INITIAL']+x['INTERNAL'])/n if n else 0):.12f}",'gain_terminal_bits_per_event':f"{((x['FINAL']+x['EOS'])/n if n else 0):.12f}",'gain_total_bits_per_event':f"{(sum(x[c] for c in COMPS)/n if n else 0):.12f}"})
   for held in sorted({x['physical_folio'] for x in panels[panel]}):
    x=fa[mode,held];n=x['events'];folds.append({'control_id':panel,'mode':mode,'held_folio':held,'events':n,'recurrent_events':x['recurrent_events'],**{f'gain_{c.lower()}_bits_per_event':f"{x[c]/n:.12f}" for c in COMPS},'gain_onset_body_bits_per_event':f"{(x['INITIAL']+x['INTERNAL'])/n:.12f}",'gain_terminal_bits_per_event':f"{(x['FINAL']+x['EOS'])/n:.12f}",'gain_total_bits_per_event':f"{sum(x[c] for c in COMPS)/n:.12f}"})
  row={'control_id':panel,'events':8448,'recurrent_events':sum(agg[m,b]['events'] for b in BINS if b!='ZERO' for m in ['STANDARD'])}
  for mode in MODES:
   n=sum(agg[mode,b]['events'] for b in BINS if b!='ZERO');z={c:sum(agg[mode,b][c] for b in BINS if b!='ZERO')/n for c in COMPS};row[mode.lower()+'_onset_body']=f"{z['INITIAL']+z['INTERNAL']:.12f}";row[mode.lower()+'_terminal']=f"{z['FINAL']+z['EOS']:.12f}";row[mode.lower()+'_total']=f"{sum(z.values()):.12f}"
  summary.append(row)
 # Exact standard all-event anchor to GDT284.
 old=read(R/'gdt284_component_scores.tsv')
 for panel in d['panels']:
  for c in COMPS:
   x=next(q for q in bins if q['control_id']==panel and q['mode']=='STANDARD' and q['recurrence_bin'] in BINS) # existence
   got=sum(float(q['gain_'+c.lower()+'_bits']) for q in bins if q['control_id']==panel and q['mode']=='STANDARD')/8448;want=float(next(q for q in old if q['control_id']==panel and q['mode']=='STANDARD_HELD_FOLIO' and q['component']==c)['gain_bits_per_event']);assert abs(got-want)<2e-10
 v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');st=float(v['standard_terminal']);et=float(v['exact_host_excluded_terminal']);mt=float(v['matched_nonhost_excluded_terminal']);gates={'standard_recurrent_terminal_lt_zero':st<0,'exact_excluded_recurrent_terminal_gte_zero':et>=0,'exact_terminal_improvement_gt_matched_terminal_improvement':et-st>mt-st,'exact_excluded_recurrent_onset_body_gt_zero':float(v['exact_host_excluded_onset_body'])>0};status=d['decision']['pass'] if all(gates.values()) else d['decision']['fail']
 vc=[x for x in caps if x['control_id']=='VOYNICH_REFERENCE'];vt=[sum(int(x[f'tier_{i}_events']) for x in vc) for i in range(5)];vd=sum(int(x['donor_events']) for x in vc);assert sum(vt)==vd
 counters=[{'counterexample':'TERMINAL_SHIFT_IS_ONLY_LOST_TRAINING_VOLUME','evidence':f'exact removal shift {et-st:+.6f} versus matched equal-count shift {mt-st:+.6f} bits/event','impact':'the frozen matched deletion is the direct volume control'}, {'counterexample':'WRAPPER_ONSET_SIGNAL_DISAPPEARS_WITH_EXACT_HOSTS','evidence':f'exact-excluded recurrent onset/body {float(v["exact_host_excluded_onset_body"]):+.6f} bits/event','impact':'a nonpositive value fails the frozen gate'}, {'counterexample':'PAGE_HOST_IS_A_LEXEME','evidence':'host identity is the frozen parser output only','impact':'mechanism localization gives no lexical or semantic status'}, {'counterexample':'DONOR_MATCHING_IS_ALWAYS_EXACT','evidence':f'Voynich donor tiers {vt}; tier4 any-nonhost share {vt[4]/vd:.6f}','impact':'equal volume is exact but opportunity matching is frequently coarse'}, {'counterexample':'EXACT_HOST_IS_ABSENT_FROM_ALL_TARGET_HISTORY','evidence':'training-fold exact-host occurrences are removed but ordinary past-within-page held history remains','impact':'this is a training-support sensitivity rather than a sealed first-occurrence test'}, {'counterexample':'F84_USED','evidence':'only the frozen f84-free native inventory is read','impact':'no f84 access'}]
 write(OUT_BIN,bins);write(OUT_FOLD,folds);write(OUT_CAP,caps);write(OUT_SUM,summary);write(OUT_COUNTER,counters)
 report=['# GDT285 — exact-host reuse and terminal localization','',f'Status: **{status}**.','','## Recurrent-host endpoint','', '| panel | recurrent events | standard onset | standard terminal | exact-excluded onset | exact-excluded terminal | matched-excluded terminal |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summary:report.append(f"| {x['control_id']} | {x['recurrent_events']} | {float(x['standard_onset_body']):+.4f} | {float(x['standard_terminal']):+.4f} | {float(x['exact_host_excluded_onset_body']):+.4f} | {float(x['exact_host_excluded_terminal']):+.4f} | {float(x['matched_nonhost_excluded_terminal']):+.4f} |")
 report +=['','## Frozen gates','']+[f"- `{k}`: **{'PASS' if x else 'FAIL'}**" for k,x in gates.items()]+['','The five recurrence bins, every held folio, and the exact donor-tier capacity are exported. Standard all-event component scores reproduce GDT284 exactly. The Voynich matched control removes exactly '+str(vd)+' events across target-host/fold cases; tier counts are `'+str(vt)+'`, so '+f'{vt[4]/vd:.1%}'+' use the coarsest any-nonhost fallback. Equal removal volume is exact, but opportunity matching is not uniformly exact. Ordinary past-within-page held history remains available in all modes.','','## Claim ceiling','','At most this localizes an opaque wrapper-conditioned terminal penalty to reuse of exact parsed host identities in this scorer. It establishes no morphology, abbreviation, lexicon, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_BIN,OUT_FOLD,OUT_CAP,OUT_SUM,OUT_COUNTER,REPORT];inputs=['gdt285_design.json','gdt285_design_validation.json','gdt285_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt284_result.json','gdt284_component_scores.tsv'];res={'schema':'GDT285_EXACT_HOST_REUSE_TERMINAL_LOCALIZATION_RESULT_V1','status':status,'panels':4,'events_per_panel':8448,'frozen_gates':gates,'voynich_summary':v,'voynich_matched_donor_tier_events':vt,'voynich_matched_donor_events':vd,'within_page_target_history_retained':True,'standard_gdt284_anchor_exact':True,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'gates':gates},sort_keys=True))
if __name__=='__main__':main()
