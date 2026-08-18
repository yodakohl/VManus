#!/usr/bin/env python3
"""Independent score and accounting validation for GDT284."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt284_result.json';OUT=R/'gdt284_validation.json';COMPS=('INITIAL','INTERNAL','FINAL','EOS');FIELDS=(('register',str),('record_ordinal',int),('field_ordinal',int),('within_field_position',str),('local_frame',str),('inner_d',str),('right_family',str),('dy_closure',str),('b3',str),('line_close',int),('paragraph_close',int),('known_label_renderer',str))
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
 total=Counter()
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
    a=ga[h];x=gb[b][h];pb=(a[c]-x[c]+.5)/(sum(a.values())-sum(x.values())+.5*K);p=pc[r['page']][h];pp=(p[c]+prior*pb)/(sum(p.values())+prior);a=ca[k,h];x=cb[b][k,h];prob=(a[c]-x[c]+prior*pp)/(sum(a.values())-sum(x.values())+prior);total[z]+=-math.log2(prob);p[c]+=1
 return dict(total)
def wrappers(events,panel,world):
 st=defaultdict(list)
 for i,r in enumerate(events):st[(r['section'],r['currier'],r['hand'],r['within_field_position'],int(r['host_length']),r['page_host'][:1])].append(i)
 rng=random.Random(int(hashlib.sha256(f'GDT283_FIRSTCHAR_LENGTH_MATCHED_V1|{panel}|{world}'.encode()).hexdigest()[:16],16));out=[r['wrapper'] for r in events]
 for ids in st.values():v=[out[i] for i in ids];rng.shuffle(v);[out.__setitem__(i,w) for i,w in zip(ids,v)]
 return out
def mobile(events):
 st=defaultdict(set)
 for r in events:st[(r['section'],r['currier'],r['hand'],r['within_field_position'],int(r['host_length']),r['page_host'][:1])].add(r['wrapper'])
 keys={k for k,v in st.items() if len(v)>1};return sum(1 for r in events if (r['section'],r['currier'],r['hand'],r['within_field_position'],int(r['host_length']),r['page_host'][:1]) in keys)
def sign(v):return ''.join('+' if v[c]>0 else '-' if v[c]<0 else '0' for c in COMPS)
def rank(v):return '>'.join(sorted(COMPS,key=lambda c:(-v[c],COMPS.index(c))))
def tot(x):return sum(x.get(c,0.) for c in COMPS)
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt284_design.json').read_text());res=json.loads(RESULT.read_text());comp=rows(R/'gdt284_component_scores.tsv');dist=rows(R/'gdt284_profile_distances.tsv');nr=rows(R/'gdt284_null_results.tsv');sm=rows(R/'gdt284_summary.tsv')
 ck('design',d['status']=='CORRECTED_FROZEN_BEFORE_AUTHORITATIVE_GDT284_SCORING' and d['content_sha256']==csha(d));fr=rows(R/'gdt284_freeze_manifest.tsv');ck('freeze',len(fr)==11 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in fr));ck('counts',len(comp)==96 and len(dist)==24 and len(nr)==768 and len(sm)==12)
 native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('events',all(len(x)==8448 for x in panels.values()))
 vec={};mob={}
 for panel,events in panels.items():
  b=standard(events,False);f=standard(events,True);nb=nested(events,False);nf=nested(events,True);vec[panel]={};mob[panel]=mobile(events)
  for mode,a,z in [('STANDARD_HELD_FOLIO',b,f),('NESTED_UNSEEN_HOST_BUCKET',nb,nf)]:
   v={c:(a.get(c,0)-z.get(c,0))/8448 for c in COMPS};vec[panel][mode]=v
   for c in COMPS:
    x=next(q for q in comp if q['control_id']==panel and q['mode']==mode and q['component']==c);ck('component:'+panel+':'+mode+':'+c,close(x['base_bits'],a.get(c,0)) and close(x['wrapper_bits'],z.get(c,0)) and close(x['gain_bits_per_event'],v[c]))
  q=standard(events,True,wrappers(events,panel,0));x=next(z for z in nr if z['control_id']==panel and z['world_index']=='0');ck('null0:'+panel,close(x['gain_total_bits_per_event'],(tot(b)-tot(q))/8448) and all(close(x['gain_'+c.lower()+'_bits_per_event'],(b.get(c,0)-q.get(c,0))/8448) for c in COMPS))
  s=next(x for x in sm if x['control_id']==panel);expected='UNSCORED_NO_WRAPPER_CAPACITY' if mob[panel]==0 else 'UNSCORED_NO_CONTEXT_REUSE' if panel in d['capacity_rule']['known_zero_context_reuse_panels'] else 'SCORED';ck('summary:'+panel,s['capacity_status']==expected and int(s['mobile_events'])==mob[panel] and s['standard_sign_pattern']==(sign(vec[panel]['STANDARD_HELD_FOLIO']) if expected=='SCORED' else 'UNSCORED') and s['nested_sign_pattern']==(sign(vec[panel]['NESTED_UNSEEN_HOST_BUCKET']) if expected=='SCORED' else 'UNSCORED'))
 vms=vec['VOYNICH_REFERENCE'];scored=[x['control_id'] for x in sm if x['capacity_status']=='SCORED']
 for x in dist:
  v=vec[x['control_id']][x['mode']];dv=math.sqrt(sum((v[c]-vms[x['mode']][c])**2 for c in COMPS));ck('distance:'+x['control_id']+':'+x['mode'],close(x['euclidean_distance_to_voynich'],dv) and int(x['exact_sign_match'])==int(x['control_id'] in scored and sign(v)==sign(vms[x['mode']])) and int(x['component_rank_match'])==int(x['control_id'] in scored and rank(v)==rank(vms[x['mode']])))
 for mode in d['modes']:
  q=sorted([x for x in dist if x['mode']==mode and x['control_id']!='VOYNICH_REFERENCE' and x['capacity_status']=='SCORED'],key=lambda x:(float(x['euclidean_distance_to_voynich']),x['control_id']));ck('distance_ranks:'+mode,all(int(x['rank_among_scored_controls'])==i for i,x in enumerate(q,1)))
 ng=defaultdict(list)
 for x in nr:ng[x['control_id']].append(float(x['gain_total_bits_per_event']))
 active=[p for p in scored];means={p:statistics.mean(ng[p]) for p in active};sds={p:statistics.pstdev(ng[p]) for p in active};oz={p:(sum(vec[p]['STANDARD_HELD_FOLIO'].values())-means[p])/sds[p] for p in active};wm=[max((ng[p][i]-means[p])/sds[p] for p in active) for i in range(64)]
 for p in active:
  s=next(x for x in sm if x['control_id']==p);local=(1+sum(v>=sum(vec[p]['STANDARD_HELD_FOLIO'].values())-1e-15 for v in ng[p]))/65;mp=(1+sum(v>=oz[p]-1e-15 for v in wm))/65;ck('pvalues:'+p,close(s['local_p'],local) and close(s['max12_p'],mp))
 stdpat=sign(vms['STANDARD_HELD_FOLIO']);nestpat=sign(vms['NESTED_UNSEEN_HOST_BUCKET']);matches=[p for p in d['panels'] if p!='VOYNICH_REFERENCE' and p in scored and sign(vec[p]['STANDARD_HELD_FOLIO'])==stdpat];nmatches=[p for p in d['panels'] if p!='VOYNICH_REFERENCE' and p in scored and sign(vec[p]['NESTED_UNSEEN_HOST_BUCKET'])==nestpat];manifest={x['control_id']:x for x in rows(R/'gdt278_control_manifest.tsv')};cats=sorted({manifest[p]['architecture_category'] for p in matches});ncats=sorted({manifest[p]['architecture_category'] for p in nmatches});status=d['classification']['two_or_more_architecture_categories_exact_standard_sign_match'] if len(cats)>=2 else d['classification']['one_architecture_category_exact_standard_sign_match'] if cats else d['classification']['zero_control_exact_standard_sign_match'];ck('decision',res['status']==status and res['voynich_standard_sign_pattern']==stdpat and res['exact_matching_controls']==matches and res['exact_matching_architecture_categories']==cats and res['voynich_nested_sign_pattern']==nestpat and res['nested_exact_matching_controls']==nmatches and res['nested_exact_matching_architecture_categories']==ncats)
 old=rows(R/'gdt283_component_scores.tsv');ck('gdt283_anchor',all(close(x['gain_bits_per_event'],next(z for z in comp if z['control_id']==x['control_id'] and z['mode']==x['mode'] and z['component']==x['component'])['gain_bits_per_event']) for x in old));ck('capacity_lists',res['zero_wrapper_capacity_panels']==d['capacity_rule']['known_zero_wrapper_capacity_panels'] and res['zero_context_reuse_panels']==d['capacity_rule']['known_zero_context_reuse_panels']);ck('prohibitions',res['semantic_assignments']==res['page_host_substrings_mined']==res['new_synthetic_worlds']==res['oracle_fields_scored']==0);ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));ck('inputs',all(sha(R/k)==v for k,v in res['inputs'].items()));ck('docs',all(sha(R/k)==v for k,v in res['documents'].items()));ck('impl',all(sha(R/k)==v for k,v in res['implementation'].items()));ck('outputs',all(sha(R/k)==v for k,v in res['outputs'].items()));ck('content',res['content_sha256']==csha(res))
 out={'schema':'GDT284_WRAPPER_POSITIONAL_PROFILE_CALIBRATION_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_ALL_PANEL_STANDARD_NESTED_COMPONENT_AND_WORLD0_RESCORE_PLUS_FULL_ACCOUNTING','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
