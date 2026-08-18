#!/usr/bin/env python3
"""Independent primary-mechanism validation for GDT285."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt285_result.json';OUT=R/'gdt285_validation.json';COMPS=('INITIAL','INTERNAL','FINAL','EOS');MODES=('STANDARD','EXACT_HOST_EXCLUDED','MATCHED_NONHOST_EXCLUDED');BINS=('ZERO','ONE','TWO_TO_THREE','FOUR_TO_SEVEN','EIGHT_PLUS');FIELDS=(('register',str),('record_ordinal',int),('field_ordinal',int),('within_field_position',str),('local_frame',str),('inner_d',str),('right_family',str),('dy_closure',str),('b3',str),('line_close',int),('paragraph_close',int),('known_label_renderer',str))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=2e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def key(r,full):
 z=tuple(conv(r[n]) for n,conv in FIELDS);return z+((r['wrapper'],) if full else ())
def chars(host):
 h='^^';n=len(host)
 for i,c in enumerate(host):yield h[-2:],c,'INITIAL' if i==0 else 'FINAL' if i==n-1 else 'INTERNAL';h+=c
 yield h[-2:],'<EOS>','EOS'
def rbin(n):return 'ZERO' if n==0 else 'ONE' if n==1 else 'TWO_TO_THREE' if n<=3 else 'FOUR_TO_SEVEN' if n<=7 else 'EIGHT_PLUS'
def tierkey(r,t):
 b=(r['section'],r['currier'],r['hand'])
 return b+(r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['wrapper']) if t==0 else b+(int(r['host_length']),r['page_host'][:1],r['wrapper']) if t==1 else (int(r['host_length']),r['page_host'][:1],r['wrapper']) if t==2 else (int(r['host_length']),r['page_host'][:1]) if t==3 else ('ALL',)
def donors(events,trainids,targets,panel,held):
 pools=[defaultdict(list) for _ in range(5)];byhost=defaultdict(list)
 for i in trainids:
  byhost[events[i]['page_host']].append(i)
  for t in range(5):pools[t][tierkey(events[i],t)].append(i)
 for t in range(5):
  for k in pools[t]:pools[t][k].sort(key=lambda i:hashlib.sha256(f"GDT285_DONOR_ORDER|{panel}|{held}|{events[i]['observation_id']}".encode()).hexdigest())
 out={};tc={}
 for host in sorted(targets):
  used=set();chosen=[];cnt=Counter()
  for si in sorted(byhost[host],key=lambda i:events[i]['observation_id']):
   pick=None
   for t in range(5):
    p=pools[t][tierkey(events[si],t)]
    if not p:continue
    off=int(hashlib.sha256(f"GDT285_DONOR_START|{panel}|{held}|{host}|{events[si]['observation_id']}|{t}".encode()).hexdigest()[:16],16)%len(p)
    for j in range(len(p)):
     q=p[(off+j)%len(p)]
     if q not in used and events[q]['page_host']!=host:pick=q;break
    if pick is not None:cnt[t]+=1;break
   assert pick is not None;used.add(pick);chosen.append(pick)
  out[host]=chosen;tc[host]=cnt
 return out,tc
def model(events,testids,trip,keys,ga,ca,hga,hca,dga,dca,mode,K,prior):
 pc=defaultdict(lambda:defaultdict(Counter));out={}
 for i in testids:
  r=events[i];host=r['page_host'];k=keys[i];bits=Counter();xg=hga[host] if mode=='EXACT_HOST_EXCLUDED' else dga[host] if mode=='MATCHED_NONHOST_EXCLUDED' else {};xc=hca[host] if mode=='EXACT_HOST_EXCLUDED' else dca[host] if mode=='MATCHED_NONHOST_EXCLUDED' else {}
  for hist,c,z in trip[i]:
   a=ga[hist];x=xg.get(hist,{});pb=(a[c]-x.get(c,0)+.5)/(sum(a.values())-sum(x.values())+.5*K);p=pc[r['page']][hist];pp=(p[c]+prior*pb)/(sum(p.values())+prior);a=ca[k,hist];x=xc.get((k,hist),{});prob=(a[c]-x.get(c,0)+prior*pp)/(sum(a.values())-sum(x.values())+prior);bits[z]+=-math.log2(prob);p[c]+=1
  out[i]=dict(bits)
 return out
def rescore_voynich(events):
 d=json.loads((R/'gdt276_design.json').read_text());K=len(d['alphabet']);prior=d['capacity']['character_context_prior_mass'];trip=[list(chars(r['page_host'])) for r in events];by=defaultdict(list)
 for i,r in enumerate(events):by[r['physical_folio']].append(i)
 agg=defaultdict(lambda:{'events':0,'rs':0,**{c:0. for c in COMPS}});cap=[]
 for held,testids in sorted(by.items()):
  train=[i for f,ids in by.items() if f!=held for i in ids];hc=Counter(events[i]['page_host'] for i in train);targets={events[i]['page_host'] for i in testids};dm,tc=donors(events,train,targets,'VOYNICH_REFERENCE',held);ct=Counter();[ct.update(tc[h]) for h in targets];cap.append((held,len(targets),sum(hc[h]==0 for h in targets),sum(hc[h] for h in targets),tuple(ct[t] for t in range(5))))
  scores={}
  for full in (False,True):
   keys=[key(r,full) for r in events];ga=defaultdict(Counter);ca=defaultdict(Counter);hga=defaultdict(lambda:defaultdict(Counter));hca=defaultdict(lambda:defaultdict(Counter));dga=defaultdict(lambda:defaultdict(Counter));dca=defaultdict(lambda:defaultdict(Counter))
   for i in train:
    hst=events[i]['page_host'];k=keys[i]
    for hist,c,_ in trip[i]:ga[hist][c]+=1;ca[k,hist][c]+=1;hga[hst][hist][c]+=1;hca[hst][(k,hist)][c]+=1
   for hst,ids in dm.items():
    for i in ids:
     k=keys[i]
     for hist,c,_ in trip[i]:dga[hst][hist][c]+=1;dca[hst][(k,hist)][c]+=1
   for mode in MODES:scores[full,mode]=model(events,testids,trip,keys,ga,ca,hga,hca,dga,dca,mode,K,prior)
  for i in testids:
   bn=rbin(hc[events[i]['page_host']])
   for mode in MODES:
    a=agg[mode,bn];a['events']+=1;a['rs']+=hc[events[i]['page_host']]
    for c in COMPS:a[c]+=scores[False,mode][i].get(c,0)-scores[True,mode][i].get(c,0)
 return agg,cap
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt285_design.json').read_text());res=json.loads(RESULT.read_text());br=rows(R/'gdt285_recurrence_bins.tsv');fr=rows(R/'gdt285_folio_scores.tsv');cr=rows(R/'gdt285_donor_capacity.tsv');sm=rows(R/'gdt285_summary.tsv')
 ck('design',d['status']=='FROZEN_BEFORE_GDT285_SCORING' and d['content_sha256']==csha(d));mf=rows(R/'gdt285_freeze_manifest.tsv');ck('freeze',len(mf)==7 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('counts',len(br)==60 and len(fr)==357 and len(cr)==119 and len(sm)==4)
 native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('events',all(len(x)==8448 for x in panels.values()))
 for p in d['panels']:
  for mode in MODES:
   q=[x for x in br if x['control_id']==p and x['mode']==mode];ck('bin_census:'+p+':'+mode,len(q)==5 and sum(int(x['events']) for x in q)==8448)
   for c in COMPS:ck('bin_arithmetic:'+p+':'+mode+':'+c,all(close(x['gain_'+c.lower()+'_bits_per_event'],float(x['gain_'+c.lower()+'_bits'])/int(x['events'])) for x in q if int(x['events'])>0))
  z=[x for x in br if x['control_id']==p and x['recurrence_bin']=='ZERO'];ck('zero_modes_identical:'+p,all(all(close(x['gain_'+c.lower()+'_bits'],z[0]['gain_'+c.lower()+'_bits']) for c in COMPS) for x in z[1:]))
  for c in COMPS:
   got=sum(float(x['gain_'+c.lower()+'_bits']) for x in br if x['control_id']==p and x['mode']=='STANDARD')/8448;old=float(next(x for x in rows(R/'gdt284_component_scores.tsv') if x['control_id']==p and x['mode']=='STANDARD_HELD_FOLIO' and x['component']==c)['gain_bits_per_event']);ck('standard_anchor:'+p+':'+c,close(got,old))
 agg,cap=rescore_voynich(panels['VOYNICH_REFERENCE'])
 for mode in MODES:
  for bn in BINS:
   a=agg[mode,bn];x=next(q for q in br if q['control_id']=='VOYNICH_REFERENCE' and q['mode']==mode and q['recurrence_bin']==bn);ck('direct_bin:'+mode+':'+bn,int(x['events'])==a['events'] and close(x['mean_training_recurrence'],a['rs']/a['events']) and all(close(x['gain_'+c.lower()+'_bits'],a[c]) for c in COMPS))
 for held,nh,nz,nd,tc in cap:
  x=next(q for q in cr if q['control_id']=='VOYNICH_REFERENCE' and q['held_folio']==held);ck('direct_donor:'+held,int(x['target_host_cases'])==nh and int(x['zero_recurrence_cases'])==nz and int(x['donor_events'])==nd and all(int(x[f'tier_{i}_events'])==tc[i] for i in range(5)))
 v=next(x for x in sm if x['control_id']=='VOYNICH_REFERENCE');vals={}
 for mode in MODES:
  n=sum(agg[mode,b]['events'] for b in BINS if b!='ZERO');z={c:sum(agg[mode,b][c] for b in BINS if b!='ZERO')/n for c in COMPS};vals[mode]=(z['INITIAL']+z['INTERNAL'],z['FINAL']+z['EOS'],sum(z.values()));ck('direct_summary:'+mode,close(v[mode.lower()+'_onset_body'],vals[mode][0]) and close(v[mode.lower()+'_terminal'],vals[mode][1]) and close(v[mode.lower()+'_total'],vals[mode][2]))
 st=vals['STANDARD'][1];et=vals['EXACT_HOST_EXCLUDED'][1];mt=vals['MATCHED_NONHOST_EXCLUDED'][1];g={'standard_recurrent_terminal_lt_zero':st<0,'exact_excluded_recurrent_terminal_gte_zero':et>=0,'exact_terminal_improvement_gt_matched_terminal_improvement':et-st>mt-st,'exact_excluded_recurrent_onset_body_gt_zero':vals['EXACT_HOST_EXCLUDED'][0]>0};ck('gates',g==res['frozen_gates'] and all(g));ck('status',res['status']==d['decision']['pass']);ck('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));ck('inputs',all(sha(R/k)==v for k,v in res['inputs'].items()));ck('docs',all(sha(R/k)==v for k,v in res['documents'].items()));ck('impl',all(sha(R/k)==v for k,v in res['implementation'].items()));ck('outputs',all(sha(R/k)==v for k,v in res['outputs'].items()));ck('content',res['content_sha256']==csha(res))
 out={'schema':'GDT285_EXACT_HOST_REUSE_TERMINAL_LOCALIZATION_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_VOYNICH_ALL_MODE_BIN_AND_DONOR_RESCORE_PLUS_ALL_PANEL_ACCOUNTING_AND_STANDARD_ANCHORS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
