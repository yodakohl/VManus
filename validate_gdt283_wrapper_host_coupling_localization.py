#!/usr/bin/env python3
"""Independent primary-score validation for GDT283."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt283_result.json';OUT=R/'gdt283_validation.json';PANELS=('LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE');COMPS=('INITIAL','INTERNAL','FINAL','EOS');FIELDS=(('register',str),('record_ordinal',int),('field_ordinal',int),('within_field_position',str),('local_frame',str),('inner_d',str),('right_family',str),('dy_closure',str),('b3',str),('line_close',int),('paragraph_close',int),('known_label_renderer',str))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=9e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def key(r,full,wrapper=None):
 z=tuple(conv(r[n]) for n,conv in FIELDS);return z+(((r['wrapper'] if wrapper is None else wrapper),) if full else ())
def bucket(h):return int(hashlib.sha256(('GDT283_HOST_FOLD|'+h).encode()).hexdigest()[:16],16)%8
def chars(host):
 h='^^';n=len(host)
 for i,c in enumerate(host):yield h[-2:],c,'INITIAL' if i==0 else 'FINAL' if i==n-1 else 'INTERNAL';h+=c
 yield h[-2:],'<EOS>','EOS'
def standard(events,full,wrappers=None):
 d=json.loads((R/'gdt276_design.json').read_text());K=len(d['alphabet']);prior=d['capacity']['character_context_prior_mass'];by=defaultdict(list);trip=[list(chars(r['page_host'])) for r in events];keys=[key(r,full,None if wrappers is None else wrappers[i]) for i,r in enumerate(events)]
 for i,r in enumerate(events):by[r['physical_folio']].append(i)
 total=Counter()
 for held,ids in sorted(by.items()):
  ga=defaultdict(Counter);ca=defaultdict(Counter)
  for fold,jj in by.items():
   if fold==held:continue
   for i in jj:
    for h,c,_ in trip[i]:ga[h][c]+=1;ca[keys[i],h][c]+=1
  pc=defaultdict(lambda:defaultdict(Counter))
  for i in ids:
   r=events[i];k=keys[i]
   for h,c,z in trip[i]:
    g=ga[h];pb=(g[c]+.5)/(sum(g.values())+.5*K);p=pc[r['page']][h];pp=(p[c]+prior*pb)/(sum(p.values())+prior);q=ca[k,h];prob=(q[c]+prior*pp)/(sum(q.values())+prior);total[z]+=-math.log2(prob);p[c]+=1
 return dict(total)
def nested(events,full):
 d=json.loads((R/'gdt276_design.json').read_text());K=len(d['alphabet']);prior=d['capacity']['character_context_prior_mass'];by=defaultdict(list);trip=[list(chars(r['page_host'])) for r in events];keys=[key(r,full) for r in events];hb=[bucket(r['page_host']) for r in events]
 for i,r in enumerate(events):by[r['physical_folio']].append(i)
 total=Counter();bb=defaultdict(Counter)
 for held,ids in sorted(by.items()):
  ga=defaultdict(Counter);gb=defaultdict(lambda:defaultdict(Counter));ca=defaultdict(Counter);cb=defaultdict(lambda:defaultdict(Counter))
  for i,r in enumerate(events):
   if r['physical_folio']==held:continue
   b=hb[i];k=keys[i]
   for h,c,_ in trip[i]:ga[h][c]+=1;gb[b][h][c]+=1;ca[k,h][c]+=1;cb[b][k,h][c]+=1
  pc=defaultdict(lambda:defaultdict(Counter))
  for i in ids:
   r=events[i];b=hb[i];k=keys[i]
   for h,c,z in trip[i]:
    a=ga[h];x=gb[b][h];pb=(a[c]-x[c]+.5)/(sum(a.values())-sum(x.values())+.5*K);p=pc[r['page']][h];pp=(p[c]+prior*pb)/(sum(p.values())+prior);a=ca[k,h];x=cb[b][k,h];prob=(a[c]-x[c]+prior*pp)/(sum(a.values())-sum(x.values())+prior);v=-math.log2(prob);total[z]+=v;bb[b][z]+=v;p[c]+=1
 return dict(total),{b:dict(bb[b]) for b in range(8)}
def wrappers(events,panel,world):
 st=defaultdict(list)
 for i,r in enumerate(events):st[(r['section'],r['currier'],r['hand'],r['within_field_position'],int(r['host_length']),r['page_host'][:1])].append(i)
 rng=random.Random(int(hashlib.sha256(f'GDT283_FIRSTCHAR_LENGTH_MATCHED_V1|{panel}|{world}'.encode()).hexdigest()[:16],16));out=[r['wrapper'] for r in events]
 for ids in st.values():v=[out[i] for i in ids];rng.shuffle(v);[out.__setitem__(i,w) for i,w in zip(ids,v)]
 return out
def tot(x):return sum(x.get(c,0.) for c in COMPS)
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt283_design.json').read_text());res=json.loads(RESULT.read_text());comp=rows(R/'gdt283_component_scores.tsv');br=rows(R/'gdt283_host_bucket_folds.tsv');nr=rows(R/'gdt283_null_results.tsv');sm=rows(R/'gdt283_summary.tsv')
 ck('design',d['status']=='FROZEN_BEFORE_GDT283_SCORING' and d['content_sha256']==csha(d));fr=rows(R/'gdt283_gdt282_freeze_manifest.tsv');ck('parent',len(fr)==15 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in fr));ck('status',res['status']=='WRAPPER_CHANNEL_SURVIVES_UNSEEN_HOST_TYPES_AND_INTERNAL_POSITIONS');ck('counts',len(comp)==32 and len(br)==32 and len(nr)==256 and len(sm)==4)
 for x in comp:ck('component:'+x['control_id']+':'+x['mode']+':'+x['component'],close(x['gain_bits'],float(x['base_bits'])-float(x['wrapper_bits'])) and close(x['gain_bits_per_event'],float(x['gain_bits'])/8448))
 for x in br:ck('bucket_sum:'+x['control_id']+':'+x['host_bucket'],close(x['gain_total_bits'],sum(float(x['gain_'+c.lower()+'_bits']) for c in COMPS)))
 ng=defaultdict(list)
 for x in nr:ng[x['control_id']].append(float(x['gain_total_bits_per_event']))
 means={p:statistics.mean(ng[p]) for p in PANELS};sds={p:statistics.pstdev(ng[p]) for p in PANELS};obs={x['control_id']:float(x['standard_gain_bits_per_event']) for x in sm};oz={p:(obs[p]-means[p])/sds[p] for p in PANELS};wm=[max((ng[p][i]-means[p])/sds[p] for p in PANELS) for i in range(64)]
 for x in sm:
  p=x['control_id'];local=(1+sum(v>=obs[p]-1e-15 for v in ng[p]))/65;mp=(1+sum(v>=oz[p]-1e-15 for v in wm))/65;ck('summary:'+p,close(x['null_mean_gain_bits_per_event'],means[p]) and close(x['null_sd_gain_bits_per_event'],sds[p]) and close(x['observed_z'],oz[p]) and close(x['local_p'],local) and close(x['max4_p'],mp) and int(x['positive_host_buckets'])==sum(float(q['gain_total_bits'])>0 for q in br if q['control_id']==p))
 native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in PANELS};ck('events',all(len(x)==8448 for x in panels.values()))
 for p,events in panels.items():
  base=standard(events,False);full=standard(events,True);nested_base,bb=nested(events,False);nested_full,fb=nested(events,True);s=next(x for x in sm if x['control_id']==p)
  ck('direct_standard:'+p,close(s['standard_gain_bits_per_event'],(tot(base)-tot(full))/8448));ck('direct_nested:'+p,close(s['nested_gain_bits_per_event'],(tot(nested_base)-tot(nested_full))/8448));ck('direct_internal:'+p,close(s['nested_internal_gain_bits_per_event'],(nested_base.get('INTERNAL',0)-nested_full.get('INTERNAL',0))/8448))
  for mode,a,z in [('STANDARD_HELD_FOLIO',base,full),('NESTED_UNSEEN_HOST_BUCKET',nested_base,nested_full)]:
   for c in COMPS:
    x=next(q for q in comp if q['control_id']==p and q['mode']==mode and q['component']==c);ck('direct_component:'+p+':'+mode+':'+c,close(x['base_bits'],a.get(c,0)) and close(x['wrapper_bits'],z.get(c,0)))
  for b in range(8):
   x=next(q for q in br if q['control_id']==p and q['host_bucket']==str(b));ck('direct_bucket:'+p+':'+str(b),int(x['events'])==sum(bucket(r['page_host'])==b for r in events) and int(x['host_types'])==len({r['page_host'] for r in events if bucket(r['page_host'])==b}) and all(close(x['gain_'+c.lower()+'_bits'],bb[b].get(c,0)-fb[b].get(c,0)) for c in COMPS))
  q=standard(events,True,wrappers(events,p,0));x=next(y for y in nr if y['control_id']==p and y['world_index']=='0');ck('null0:'+p,close(x['gain_total_bits_per_event'],(tot(base)-tot(q))/8448) and all(close(x['gain_'+c.lower()+'_bits_per_event'],(base.get(c,0)-q.get(c,0))/8448) for c in COMPS))
 v=next(x for x in sm if x['control_id']=='VOYNICH_REFERENCE');g={'nested_total_positive':float(v['nested_gain_bits_per_event'])>0,'nested_internal_positive':float(v['nested_internal_gain_bits_per_event'])>0,'positive_buckets_at_least_6_of_8':int(v['positive_host_buckets'])>=6,'matched_null_max4_p_le_0_05':float(v['max4_p'])<=d['alpha']};ck('gates',g==res['frozen_gates'] and all(g.values()));rv=res['voynich_summary'];ck('summary_result',rv['control_id']==v['control_id'] and int(rv['events'])==int(v['events']) and int(rv['folios'])==int(v['folios']) and int(rv['positive_host_buckets'])==int(v['positive_host_buckets']) and all(close(rv[k],v[k]) for k in ('local_p','max4_p','nested_gain_bits_per_event','nested_internal_gain_bits_per_event','null_mean_gain_bits_per_event','null_sd_gain_bits_per_event','observed_z','standard_gain_bits_per_event')));ck('no_semantics',res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));ck('inputs',all(sha(R/k)==v for k,v in res['inputs'].items()));ck('docs',all(sha(R/k)==v for k,v in res['documents'].items()));ck('impl',all(sha(R/k)==v for k,v in res['implementation'].items()));ck('outputs',all(sha(R/k)==v for k,v in res['outputs'].items()));ck('content',res['content_sha256']==csha(res))
 out={'schema':'GDT283_WRAPPER_HOST_COUPLING_LOCALIZATION_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_STANDARD_NESTED_COMPONENT_BUCKET_AND_WORLD0_RESCORE','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
