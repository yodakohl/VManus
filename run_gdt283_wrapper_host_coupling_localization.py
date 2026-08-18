#!/usr/bin/env python3
"""Run frozen GDT283 wrapper/host coupling localization."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent
DESIGN=R/'gdt283_design.json';METHOD=R/'GDT283_WRAPPER_HOST_COUPLING_LOCALIZATION_METHOD.md';REPORT=R/'GDT283_WRAPPER_HOST_COUPLING_LOCALIZATION_REPORT.md';RESULT=R/'gdt283_result.json'
OUT_COMP=R/'gdt283_component_scores.tsv';OUT_BUCKET=R/'gdt283_host_bucket_folds.tsv';OUT_NULL=R/'gdt283_null_results.tsv';OUT_SUM=R/'gdt283_summary.tsv';OUT_COUNTER=R/'gdt283_counterexamples.tsv'
PANELS=('LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE');MODELS=('BASE_NO_WRAPPER','FULL_WRAPPER_IDENTITY');COMPS=('INITIAL','INTERNAL','FINAL','EOS');FIELDS=(('register',str),('record_ordinal',int),('field_ordinal',int),('within_field_position',str),('local_frame',str),('inner_d',str),('right_family',str),('dy_closure',str),('b3',str),('line_close',int),('paragraph_close',int),('known_label_renderer',str))
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
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'') for k in ff} for r in rr])
def key(r,model,wrapper=None):
 z=tuple(conv(r[n]) for n,conv in FIELDS)
 return z if model=='BASE_NO_WRAPPER' else z+((r['wrapper'] if wrapper is None else wrapper),)
def bucket(host):return int(hashlib.sha256(('GDT283_HOST_FOLD|'+host).encode()).hexdigest()[:16],16)%8
def chars(host):
 h='^^';n=len(host)
 for i,c in enumerate(host):
  comp='INITIAL' if i==0 else 'FINAL' if i==n-1 else 'INTERNAL';yield h[-2:],c,comp;h+=c
 yield h[-2:],'<EOS>','EOS'
def standard_score(events,model,wrappers=None):
 d=json.loads((R/'gdt276_design.json').read_text());K=len(d['alphabet']);prior=d['capacity']['character_context_prior_mass'];foldids=defaultdict(list);ga=defaultdict(Counter);gf=defaultdict(lambda:defaultdict(Counter));ca=defaultdict(Counter);cf=defaultdict(lambda:defaultdict(Counter));trip=[];keys=[]
 for i,r in enumerate(events):
  fold=r['physical_folio'];foldids[fold].append(i);z=list(chars(r['page_host']));trip.append(z);k=key(r,model,None if wrappers is None else wrappers[i]);keys.append(k)
  for h,c,_ in z:ga[h][c]+=1;gf[fold][h][c]+=1;ca[k,h][c]+=1;cf[fold][k,h][c]+=1
 total=Counter();byfold={}
 for held,ids in sorted(foldids.items()):
  pc=defaultdict(lambda:defaultdict(Counter));bits=Counter()
  for i in ids:
   r=events[i];k=keys[i]
   for h,c,comp in trip[i]:
    a=ga[h];f=gf[held][h];gn=sum(a.values())-sum(f.values());gc=a[c]-f[c];pb=(gc+.5)/(gn+.5*K);p=pc[r['page']][h];pp=(p[c]+prior*pb)/(sum(p.values())+prior);a=ca[k,h];f=cf[held][k,h];cn=sum(a.values())-sum(f.values());cc=a[c]-f[c];prob=(cc+prior*pp)/(cn+prior);v=-math.log2(prob);bits[comp]+=v;p[c]+=1
  byfold[held]=dict(bits);total.update(bits)
 return dict(total),byfold
def nested_score(events,model):
 d=json.loads((R/'gdt276_design.json').read_text());K=len(d['alphabet']);prior=d['capacity']['character_context_prior_mass'];foldids=defaultdict(list);trip=[list(chars(r['page_host'])) for r in events];hb=[bucket(r['page_host']) for r in events];keys=[key(r,model) for r in events]
 for i,r in enumerate(events):foldids[r['physical_folio']].append(i)
 total=Counter();bybucket=defaultdict(Counter);byfold={}
 for held,testids in sorted(foldids.items()):
  ga=defaultdict(Counter);gb=defaultdict(lambda:defaultdict(Counter));ca=defaultdict(Counter);cb=defaultdict(lambda:defaultdict(Counter))
  for i,r in enumerate(events):
   if r['physical_folio']==held:continue
   b=hb[i];k=keys[i]
   for h,c,_ in trip[i]:ga[h][c]+=1;gb[b][h][c]+=1;ca[k,h][c]+=1;cb[b][k,h][c]+=1
  pc=defaultdict(lambda:defaultdict(Counter));fb=Counter()
  for i in testids:
   r=events[i];b=hb[i];k=keys[i]
   for h,c,comp in trip[i]:
    a=ga[h];x=gb[b][h];gn=sum(a.values())-sum(x.values());gc=a[c]-x[c];pb=(gc+.5)/(gn+.5*K);p=pc[r['page']][h];pp=(p[c]+prior*pb)/(sum(p.values())+prior);a=ca[k,h];x=cb[b][k,h];cn=sum(a.values())-sum(x.values());cc=a[c]-x[c];prob=(cc+prior*pp)/(cn+prior);v=-math.log2(prob);fb[comp]+=v;bybucket[b][comp]+=v;p[c]+=1
  byfold[held]=dict(fb);total.update(fb)
 return dict(total),byfold,{b:dict(bybucket[b]) for b in range(8)}
def permuted_wrappers(events,panel,world):
 st=defaultdict(list)
 for i,r in enumerate(events):st[(r['section'],r['currier'],r['hand'],r['within_field_position'],int(r['host_length']),r['page_host'][:1])].append(i)
 rng=random.Random(int(hashlib.sha256(f'GDT283_FIRSTCHAR_LENGTH_MATCHED_V1|{panel}|{world}'.encode()).hexdigest()[:16],16));out=[r['wrapper'] for r in events]
 for ids in st.values():
  v=[out[i] for i in ids];rng.shuffle(v)
  for i,w in zip(ids,v):out[i]=w
 return out
def mobile(events):
 st=defaultdict(list)
 for r in events:st[(r['section'],r['currier'],r['hand'],r['within_field_position'],int(r['host_length']),r['page_host'][:1])].append(r)
 return sum(len(v) for v in st.values() if len({x['wrapper'] for x in v})>1)
def job(item):
 panel,events=item;base,bf=standard_score(events,'BASE_NO_WRAPPER');full,ff=standard_score(events,'FULL_WRAPPER_IDENTITY');nb,nfb,nbuck=nested_score(events,'BASE_NO_WRAPPER');nf,nff,nfbuck=nested_score(events,'FULL_WRAPPER_IDENTITY');null=[]
 for world in range(64):
  q,_=standard_score(events,'FULL_WRAPPER_IDENTITY',permuted_wrappers(events,panel,world));null.append(q)
 return panel,base,full,bf,ff,nb,nf,nfb,nff,nbuck,nfbuck,null,mobile(events)
def total(d):return sum(d.get(c,0.) for c in COMPS)
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='FROZEN_BEFORE_GDT283_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt283_gdt282_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');panels={p:[x for x in native if x['control_id']==p] for p in PANELS};assert all(len(v)==8448 for v in panels.values()) and all(not x['page'].startswith('f84') and not x['locus'].startswith('f84') for x in native)
 results={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  jobs={ex.submit(job,x):x[0] for x in panels.items()}
  for f in as_completed(jobs):q=f.result();results[q[0]]=q;print(json.dumps({'scored':q[0]},sort_keys=True),flush=True)
 comp=[];buckets=[];nullrows=[];summ=[];nullgain={};observed={}
 for panel in PANELS:
  _,base,full,bf,ff,nb,nf,nfb,nff,nbuck,nfbuck,null,mob=results[panel];observed[panel]=(total(base)-total(full))/len(panels[panel]);nullgain[panel]=[]
  for mode,a,z in [('STANDARD_HELD_FOLIO',base,full),('NESTED_UNSEEN_HOST_BUCKET',nb,nf)]:
   for c in COMPS:comp.append({'control_id':panel,'mode':mode,'component':c,'base_bits':f"{a.get(c,0.):.12f}",'wrapper_bits':f"{z.get(c,0.):.12f}",'gain_bits':f"{a.get(c,0.)-z.get(c,0.):.12f}",'gain_bits_per_event':f"{(a.get(c,0.)-z.get(c,0.))/len(panels[panel]):.12f}"})
  for b in range(8):
   ev=sum(bucket(x['page_host'])==b for x in panels[panel]);g={c:nbuck[b].get(c,0.)-nfbuck[b].get(c,0.) for c in COMPS};buckets.append({'control_id':panel,'host_bucket':b,'events':ev,'host_types':len({x['page_host'] for x in panels[panel] if bucket(x['page_host'])==b}),'gain_total_bits':f'{sum(g.values()):.12f}',**{'gain_'+c.lower()+'_bits':f'{g[c]:.12f}' for c in COMPS}})
  for world,q in enumerate(null):
   row={'control_id':panel,'world_index':world}
   for c in COMPS:row['gain_'+c.lower()+'_bits_per_event']=f"{(base.get(c,0.)-q.get(c,0.))/len(panels[panel]):.12f}"
   g=(total(base)-total(q))/len(panels[panel]);row['gain_total_bits_per_event']=f'{g:.12f}';nullgain[panel].append(g);nullrows.append(row)
 # Shared-world max-four standardized total statistic.
 means={p:statistics.mean(nullgain[p]) for p in PANELS};sds={p:statistics.pstdev(nullgain[p]) for p in PANELS};obsz={p:(observed[p]-means[p])/sds[p] for p in PANELS};worldmax=[max((nullgain[p][w]-means[p])/sds[p] for p in PANELS) for w in range(64)]
 for panel in PANELS:
  _,base,full,bf,ff,nb,nf,nfb,nff,nbuck,nfbuck,null,mob=results[panel];ng=(total(nb)-total(nf))/len(panels[panel]);pos=sum(float(x['gain_total_bits'])>0 for x in buckets if x['control_id']==panel);local=(1+sum(x>=observed[panel]-1e-15 for x in nullgain[panel]))/65;maxp=(1+sum(x>=obsz[panel]-1e-15 for x in worldmax))/65
  summ.append({'control_id':panel,'events':len(panels[panel]),'folios':len({x['physical_folio'] for x in panels[panel]}),'mobile_events':mob,'standard_gain_bits_per_event':f'{observed[panel]:.12f}','nested_gain_bits_per_event':f'{ng:.12f}','nested_internal_gain_bits_per_event':f"{(nb.get('INTERNAL',0.)-nf.get('INTERNAL',0.))/len(panels[panel]):.12f}",'positive_host_buckets':pos,'null_mean_gain_bits_per_event':f'{means[panel]:.12f}','null_sd_gain_bits_per_event':f'{sds[panel]:.12f}','observed_z':f'{obsz[panel]:.12f}','local_p':f'{local:.12f}','max4_p':f'{maxp:.12f}'})
 v=next(x for x in summ if x['control_id']=='VOYNICH_REFERENCE');gates={'nested_total_positive':float(v['nested_gain_bits_per_event'])>0,'nested_internal_positive':float(v['nested_internal_gain_bits_per_event'])>0,'positive_buckets_at_least_6_of_8':int(v['positive_host_buckets'])>=6,'matched_null_max4_p_le_0_05':float(v['max4_p'])<=d['alpha']};status='WRAPPER_CHANNEL_SURVIVES_UNSEEN_HOST_TYPES_AND_INTERNAL_POSITIONS' if all(gates.values()) else 'WRAPPER_CHANNEL_DOMINATED_BY_BOUNDARY_OR_HOST_LEXICON'
 comp.sort(key=lambda x:(x['control_id'],x['mode'],COMPS.index(x['component'])));buckets.sort(key=lambda x:(x['control_id'],int(x['host_bucket'])));nullrows.sort(key=lambda x:(x['control_id'],int(x['world_index'])));summ.sort(key=lambda x:PANELS.index(x['control_id']))
 counters=[{'counterexample':'WRAPPER_SIGNAL_IS_ONLY_FIRST_CHARACTER','evidence':f"nested internal gain {v['nested_internal_gain_bits_per_event']} bits/event",'impact':'a nonpositive internal component fails the frozen gate'}, {'counterexample':'EXACT_HOST_MEMORIZATION_EXPLAINS_GAIN','evidence':f"nested unseen-bucket total gain {v['nested_gain_bits_per_event']} bits/event across {v['positive_host_buckets']}/8 positive buckets",'impact':'training excludes every host identity in the target bucket'}, {'counterexample':'BOUNDARY_AND_LENGTH_EXPLAIN_GAIN','evidence':f"first-character/length-matched max4 p {v['max4_p']}",'impact':'null preserves the direct opportunity variables'}, {'counterexample':'PUBLISHED_HOST_BUCKETS_ARE_PARSER_INDEPENDENT','evidence':'host buckets use the frozen published PAGE_HOST parse','impact':'nested test is identity-transfer sensitivity, not independent parser recovery'}, {'counterexample':'FORM_COUPLING_EQUALS_MORPHOLOGY','evidence':'endpoint is character compression under opaque classes','impact':'no linguistic function follows'}, {'counterexample':'F84_USED','evidence':'only the frozen f84-free native inventory is read','impact':'no f84 access'}]
 write(OUT_COMP,comp);write(OUT_BUCKET,buckets);write(OUT_NULL,nullrows);write(OUT_SUM,summ);write(OUT_COUNTER,counters)
 report=['# GDT283 — wrapper/host coupling localization','',f'Status: **{status}**.','','## Summary','', '| panel | standard gain | unseen-host gain | unseen internal | positive buckets | local p | max4 p |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summ:report.append(f"| {x['control_id']} | {float(x['standard_gain_bits_per_event']):+.4f} | {float(x['nested_gain_bits_per_event']):+.4f} | {float(x['nested_internal_gain_bits_per_event']):+.4f} | {x['positive_host_buckets']}/8 | {float(x['local_p']):.4f} | {float(x['max4_p']):.4f} |")
 report +=['','## Positional fingerprints','', '| panel | mode | initial | internal | final | EOS | total |','|---|---|---:|---:|---:|---:|---:|']
 for panel in PANELS:
  for mode in ('STANDARD_HELD_FOLIO','NESTED_UNSEEN_HOST_BUCKET'):
   rr=[x for x in comp if x['control_id']==panel and x['mode']==mode];vals={x['component']:float(x['gain_bits_per_event']) for x in rr};report.append(f"| {panel} | {mode} | {vals['INITIAL']:+.4f} | {vals['INTERNAL']:+.4f} | {vals['FINAL']:+.4f} | {vals['EOS']:+.4f} | {sum(vals.values()):+.4f} |")
 report +=['','Voynich differs visibly from all three Latin controls in the standard endpoint: its wrapper channel is strongly initial and modestly internal, but final-character and EOS contributions are negative. The Latin wrapper channels are positive at all four positions. This makes the Voynich coupling less consistent with the calibrated Latin abbreviation edge profile, even though it is not confined to the first character.','','## Frozen gates','']+[f"- `{k}`: **{'PASS' if z else 'FAIL'}**" for k,z in gates.items()]+['','The nested endpoint excludes all exact PAGE_HOST identities in each target host bucket from training but uses the frozen published parser. The matched null preserves section, Currier, hand, position, host length and first host character.','','## Claim ceiling','','At most this localizes an opaque same-group wrapper/host form coupling. It does not establish productive morphology, abbreviation, lexical identity, function, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_COMP,OUT_BUCKET,OUT_NULL,OUT_SUM,OUT_COUNTER,REPORT];inputs=['gdt283_design.json','gdt283_design_validation.json','gdt283_gdt282_freeze_manifest.tsv','gdt282_result.json','gdt278_native_event_inventory.tsv'];result={'schema':'GDT283_WRAPPER_HOST_COUPLING_LOCALIZATION_RESULT_V1','status':status,'panels':len(PANELS),'events_per_panel':8448,'components':list(COMPS),'host_buckets':8,'null_worlds':64,'frozen_gates':gates,'voynich_summary':v,'new_corpora':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':'Localization of opaque same-group wrapper/host character coupling only; no morphology language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'gdt282_immutable':all(sha(R/x['artifact'])==x['frozen_sha256'] for x in read(R/'gdt283_gdt282_freeze_manifest.tsv')),'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};result['content_sha256']=rcsha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'gates':gates},sort_keys=True))
if __name__=='__main__':main()
