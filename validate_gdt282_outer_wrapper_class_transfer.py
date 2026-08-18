#!/usr/bin/env python3
"""Independent published-score and retained-transfer validation for GDT282."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
RESULT=R/'gdt282_result.json';OUT=R/'gdt282_validation.json';SCORE=R/'gdt282_model_scores.tsv';FOLD=R/'gdt282_transfer_folds.tsv';NULL=R/'gdt282_null_results.tsv';PROBE=R/'gdt282_wrapper_class_probes.tsv'
MODELS=('BASE_NO_WRAPPER','WRAPPER_PRESENCE','Q_BINARY','FULL_WRAPPER_IDENTITY','FULL_WRAPPER_PLUS_Q_REDUNDANCY');WRAPPERS=('NONE','q','ch','d','sh','che','t','s');CONTROLS=('LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE')
FIELDS=(('register',str),('record_ordinal',int),('field_ordinal',int),('within_field_position',str),('local_frame',str),('inner_d',str),('right_family',str),('dy_closure',str),('b3',str),('line_close',int),('paragraph_close',int),('known_label_renderer',str))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=8e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def state(r,m):
 w=r['wrapper'];q=int(r['q_flag'])
 if m=='BASE_NO_WRAPPER':return ()
 if m=='WRAPPER_PRESENCE':return (int(w!='NONE'),)
 if m=='Q_BINARY':return (int(w=='q'),)
 if m=='FULL_WRAPPER_IDENTITY':return (w,)
 if m=='FULL_WRAPPER_PLUS_Q_REDUNDANCY':return (w,q)
 if m.startswith('CLASS_BINARY_'):return (int(w==m[13:]),)
 raise ValueError(m)
def key(r,m,s=None):return tuple(conv(r[n]) for n,conv in FIELDS)+state(r if s is None else s,m)
def chars(host):
 h='^^'
 for c in list(host)+['<EOS>']:yield h[-2:],c;h+='$' if c=='<EOS>' else c
def split_score(train,test,mapping):
 d=json.loads((R/'gdt276_design.json').read_text());K=len(d['alphabet']);prior=d['capacity']['character_context_prior_mass'];glob=defaultdict(Counter);ctx=defaultdict(Counter)
 for r in train:
  z=mapping[r['observation_id']]
  for h,c in chars(r['page_host']):glob[h][c]+=1;ctx[z,h][c]+=1
 pc=defaultdict(lambda:defaultdict(Counter));bits=0.
 for r in test:
  z=mapping[r['observation_id']]
  for h,c in chars(r['page_host']):
   g=glob[h];pb=(g[c]+.5)/(sum(g.values())+.5*K);p=pc[r['page']][h];pp=(p[c]+prior*pb)/(sum(p.values())+prior);q=ctx[z,h];prob=(q[c]+prior*pp)/(sum(q.values())+prior);bits-=math.log2(prob);p[c]+=1
 return bits
def lofo_score(events,mapping,field='physical_folio',allowed=None):
 vals={};keys=sorted(set(r[field] for r in events)) if allowed is None else allowed
 for held in keys:vals[held]=split_score([r for r in events if r[field]!=held],[r for r in events if r[field]==held],mapping)
 return sum(vals.values()),vals
def perm_indices(events,world):
 st=defaultdict(list)
 for i,r in enumerate(events):st[(r['register'],int(r['record_ordinal']),r['within_field_position'],int(r['host_length']))].append(i)
 rng=random.Random(int(hashlib.sha256(f'GDT276_MATCHED_CONTEXT_V1|{world}|ABBREVIATION_HEAVY_LANGUAGE'.encode()).hexdigest()[:16],16));src=list(range(len(events)))
 for ids in st.values():v=list(ids);rng.shuffle(v);[src.__setitem__(a,b) for a,b in zip(ids,v)]
 return src
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt282_design.json').read_text());res=json.loads(RESULT.read_text());score=rows(SCORE);fold=rows(FOLD);null=rows(NULL);probe=rows(PROBE)
 ck('design',d['status']=='FROZEN_BEFORE_GDT282_SCORING' and d['content_sha256']==csha(d) and d['class_probe_rule']=='EXHAUSTIVE_ONE_VS_REST_BINARY');fr=rows(R/'gdt282_gdt281_freeze_manifest.tsv');ck('parent_frozen',len(fr)==15 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in fr));ck('status',res['status']=='OUTER_WRAPPER_IDENTITY_TRANSFERS_ACROSS_REGISTERS')
 ck('counts',len(score)==50 and len(null)==4*5*64 and len(probe)==32 and len(rows(R/'gdt282_wrapper_counts.tsv'))==8 and len(fold)==2285)
 bynull=defaultdict(list)
 for x in null:bynull[(x['control_id'],x['regime'],x['model'])].append(float(x['held_bits']))
 ck('null_groups',len(bynull)==20 and all(len(v)==64 for v in bynull.values()))
 for x in score:
  k=(x['control_id'],x['regime'],x['model'])
  if k in bynull:
   v=bynull[k];m=statistics.mean(v);sd=statistics.pstdev(v);sv=m-float(x['observed_bits']);ck('null:'+':'.join(k),close(x['null_mean_bits'],m) and close(x['null_sd_bits'],sd) and close(x['null_saving_bits_per_event'],sv/int(x['events'])) and (x['null_z']=='NA' if sd==0 else close(x['null_z'],sv/sd)))
  else:ck('no_null:'+':'.join(k),x['null_worlds']=='0' and x['null_mean_bits']=='NA')
 base={(x['control_id'],x['regime']):float(x['observed_bits']) for x in score if x['model']=='BASE_NO_WRAPPER'}
 for x in score:ck('gain:'+x['control_id']+':'+x['regime']+':'+x['model'],close(x['base_minus_model_bits_per_event'],(base[(x['control_id'],x['regime'])]-float(x['observed_bits']))/int(x['events'])))
 foldbase={(x['control_id'],x['regime'],x['held_stratum']):float(x['held_bits']) for x in fold if x['model']=='BASE_NO_WRAPPER'}
 for x in fold:ck('fold_gain:'+x['control_id']+':'+x['regime']+':'+x['held_stratum']+':'+x['model'],close(x['base_minus_model_bits'],foldbase[(x['control_id'],x['regime'],x['held_stratum'])]-float(x['held_bits'])))
 for x in score:
  vals=[float(q['held_bits']) for q in fold if q['control_id']==x['control_id'] and q['regime']==x['regime'] and q['model']==x['model']]
  ck('fold_sum:'+x['control_id']+':'+x['regime']+':'+x['model'],vals and close(sum(vals),x['observed_bits']))
 native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));by=defaultdict(list)
 for x in native:
  if x['control_id'] in CONTROLS:by[x['control_id']].append(x)
 vms=by['VOYNICH_REFERENCE'];ck('vms',len(vms)==8448 and {x['wrapper'] for x in vms}==set(WRAPPERS));ck('q_exact',all(int(x['q_flag'])==int(x['wrapper']=='q') for x in vms))
 artifacts={(x['control_id'],x['model']):x for x in score if x['regime']=='PUBLISHED_HELD_FOLIO'}
 null0={(x['control_id'],x['model']):x for x in null if x['regime']=='PUBLISHED_HELD_FOLIO' and x['world_index']=='0'}
 for control in CONTROLS:
  events=by[control]
  for model in MODELS:
   bm={x['observation_id']:key(x,model) for x in events};bits,_=lofo_score(events,bm);ck('direct:'+control+':'+model,close(bits,artifacts[(control,model)]['observed_bits']))
   src=perm_indices(events,0);nm={r['observation_id']:key(r,model,events[src[i]]) for i,r in enumerate(events)};nb,_=lofo_score(events,nm);ck('null0:'+control+':'+model,close(nb,null0[(control,model)]['held_bits']))
  pub={x['held_stratum']:float(x['held_bits']) for x in fold if x['control_id']==control and x['regime']=='PUBLISHED_HELD_FOLIO' and x['model']=='FULL_WRAPPER_IDENTITY'};red={x['held_stratum']:float(x['held_bits']) for x in fold if x['control_id']==control and x['regime']=='PUBLISHED_HELD_FOLIO' and x['model']=='FULL_WRAPPER_PLUS_Q_REDUNDANCY'};safe={x['held_stratum']:float(x['held_bits']) for x in fold if x['control_id']==control and x['regime']=='LOFO_SAFE_HELD_FOLIO' and x['model']=='FULL_WRAPPER_IDENTITY'};sred={x['held_stratum']:float(x['held_bits']) for x in fold if x['control_id']==control and x['regime']=='LOFO_SAFE_HELD_FOLIO' and x['model']=='FULL_WRAPPER_PLUS_Q_REDUNDANCY'};ck('redundant:'+control,pub==red and safe==sred)
 # Independently reconstruct section/hand published scores and every binary probe.
 for regime,field,allowed in [('HELD_SECTION_PUBLISHED','section',d['powered_sections']),('HELD_HAND_PUBLISHED','hand',d['powered_hands']+d['descriptive_hands'])]:
  models=MODELS+tuple('CLASS_BINARY_'+w for w in WRAPPERS)
  direct={}
  for model in models:
   bm={x['observation_id']:key(x,model) for x in vms};bits,_=lofo_score(vms,bm,field,allowed);direct[model]=bits
   if model in MODELS:ck('external:'+regime+':'+model,close(bits,next(x for x in score if x['control_id']=='VOYNICH_REFERENCE' and x['regime']==regime and x['model']==model)['observed_bits']))
  for w in WRAPPERS:
   x=next(q for q in probe if q['regime']==regime and q['wrapper_class']==w);ck('probe:'+regime+':'+w,close(x['class_binary_bits'],direct['CLASS_BINARY_'+w]) and close(x['base_minus_class_binary_bits_per_event'],(direct['BASE_NO_WRAPPER']-direct['CLASS_BINARY_'+w])/len(vms)))
 # Published probes are direct; safe probes reconstruct from retained fold sums.
 base_pub=float(artifacts[('VOYNICH_REFERENCE','BASE_NO_WRAPPER')]['observed_bits'])
 for w in WRAPPERS:
  model='CLASS_BINARY_'+w;bm={x['observation_id']:key(x,model) for x in vms};bits,_=lofo_score(vms,bm);x=next(q for q in probe if q['regime']=='PUBLISHED_HELD_FOLIO' and q['wrapper_class']==w);ck('probe:published:'+w,close(x['class_binary_bits'],bits) and close(x['base_minus_class_binary_bits_per_event'],(base_pub-bits)/len(vms)))
  sb=sum(float(q['held_bits']) for q in fold if q['control_id']=='VOYNICH_REFERENCE' and q['regime']=='LOFO_SAFE_HELD_FOLIO' and q['model']==model);bs=sum(float(q['held_bits']) for q in fold if q['control_id']=='VOYNICH_REFERENCE' and q['regime']=='LOFO_SAFE_HELD_FOLIO' and q['model']=='BASE_NO_WRAPPER');x=next(q for q in probe if q['regime']=='LOFO_SAFE_HELD_FOLIO' and q['wrapper_class']==w);ck('probe:safe:'+w,close(x['class_binary_bits'],sb) and close(x['base_minus_class_binary_bits_per_event'],(bs-sb)/len(vms)))
 sf=[x for x in fold if x['control_id']=='VOYNICH_REFERENCE' and x['regime']=='HELD_SECTION_PUBLISHED' and x['model']=='FULL_WRAPPER_IDENTITY' and x['held_stratum'] in d['powered_sections']];hf=[x for x in fold if x['control_id']=='VOYNICH_REFERENCE' and x['regime']=='HELD_HAND_PUBLISHED' and x['model']=='FULL_WRAPPER_IDENTITY' and x['held_stratum'] in d['powered_hands']];ck('positive_counts',sum(float(x['base_minus_model_bits'])>0 for x in sf)==res['positive_sections']==5 and sum(float(x['base_minus_model_bits'])>0 for x in hf)==res['positive_hands']==3)
 ck('gates',all(res['frozen_gates'].values()));ck('probe_rule',res['class_probe_rule']=='EXHAUSTIVE_ONE_VS_REST_BINARY' and res['superseded_invalid_probe']=='UNIQUE_RENAME_IS_BIJECTIVE_ZERO_INFORMATION');ck('no_semantics',res['semantic_assignments']==res['hpr1_semantics_used']==res['page_host_substrings_mined']==0);ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));ck('inputs',all(sha(R/k)==v for k,v in res['inputs'].items()));ck('docs',all(sha(R/k)==v for k,v in res['documents'].items()));ck('impl',all(sha(R/k)==v for k,v in res['implementation'].items()));ck('outputs',all(sha(R/k)==v for k,v in res['outputs'].items()));ck('content',res['content_sha256']==csha(res))
 out={'schema':'GDT282_OUTER_WRAPPER_CLASS_TRANSFER_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_PUBLISHED_AND_CROSS_SECTION_HAND_RESCORE_PLUS_RETAINED_SAFE_ACCOUNTING','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
