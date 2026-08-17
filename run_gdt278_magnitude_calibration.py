#!/usr/bin/env python3
"""Run the frozen GDT278 compiler-conditioned magnitude calibration."""
from __future__ import annotations
import csv,gzip,hashlib,json,math,statistics
from collections import Counter,defaultdict,deque
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import run_gdt276_residual_channel_world_comparison as frozen
import run_gdt277_signature_calibration as g277
import run_gdt158_structured_medieval_residual as g158

R=Path(__file__).resolve().parent
DESIGN=R/'gdt278_magnitude_design.json';DVALID=R/'gdt278_magnitude_design_validation.json';CFREEZE=R/'gdt278_control_source_freeze.json';CVALID=R/'gdt278_control_source_validation.json';MANIFEST=R/'gdt278_control_manifest.tsv';METHOD=R/'GDT278_GDT277_MAGNITUDE_CALIBRATION_METHOD.md';AUDIT=R/'GDT278_CONTROL_SOURCE_AUDIT.md'
VMS=R/'gdt276_event_inventory.tsv';AUG=R/'.gdt176/Augsburger_Baumeisterbuecher_1320_1440.xlsx'
OUT_CAP=R/'gdt278_control_capacity.tsv';OUT_SCORE=R/'gdt278_magnitude_scores.tsv';OUT_NULL=R/'gdt278_null_results.tsv';OUT_FOLD=R/'gdt278_folio_scores.tsv';OUT_MATCH=R/'gdt278_matched_event_inventory.tsv';OUT_NATIVE=R/'gdt278_native_event_inventory.tsv';OUT_COUNTER=R/'gdt278_counterexamples.tsv';REPORT=R/'GDT278_GDT277_MAGNITUDE_CALIBRATION_REPORT.md';RESULT=R/'gdt278_result.json'
MODEL='ABBREVIATION_HEAVY_LANGUAGE';TARGET_NATIVE=8448;MIN_NATIVE=.8

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for x in rows:
  for k in x:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:x.get(k,'') for k in fields} for x in rows])
def h12(x):return hashlib.sha256(x.encode()).hexdigest()[:12]
def clean(x):return g277.clean_host(x)

def base_row(obs,order,folio,page,line,record,register,surface,gi,gc,paragraph_start=0,paragraph_end=0):
 return {'source_observation_id':obs,'source_order':order,'source_folio':folio,'source_page':page,'source_line':line,'source_record':record,'source_register':register,'surface':surface,'source_group_index':gi,'source_group_count':gc,'source_paragraph_start':paragraph_start,'source_paragraph_end':paragraph_end}
def parse_generic(rows,style='GDT155'):
 toks=[x['surface'].replace('¤','') for x in rows];fol=[x['source_folio'] for x in rows];model=g277.discover(toks,fol,style);cache={}
 for x in rows:
  q=cache.setdefault(x['surface'],g277.parse_surface(x['surface'],model,style));x.update(q)
 return rows

def load_parallel(corpus,expanded):
 meta=[x for x in read(R/'gdt155_blinded_diplomatic.tsv') if x['corpus']==corpus];truth={x['line_id']:x['expanded_diplomatic'] for x in read(R/'gdt155_unblinded_lines.tsv') if x['corpus']==corpus};out=[];order=0
 if corpus=='NUREMBERG':
  source=g277.load_nuremberg(expanded);byid={x['source_observation_id']:x for x in source}
 for x in meta:
  text=truth[x['line_id']] if expanded else x['diplomatic_marked'];toks=g277.groups(text,not expanded)
  for gi,t in enumerate(toks,1):
   order+=1;z=base_row(f"{x['line_id']}:G{gi:03d}",order,x['book_or_ms'] if corpus=='NUREMBERG' else x['record_id'],x['page_id'],x['line_id'],x['record_id'],x['book_or_ms'],t,gi,len(toks),int(x['line_index'])==1,int(x['line_index'])==int(x['record_line_count']))
   if corpus=='NUREMBERG':z.update({k:byid[z['source_observation_id']][k] for k in ('host','wrapper','local_frame','right_family','b3','display_renderer')})
   out.append(z)
 return out if corpus=='NUREMBERG' else parse_generic(out)

def load_synthetic(path,world):
 with gzip.open(R/path,'rt',encoding='utf8') as h:rows=json.load(h)['rows']
 out=[];rec=defaultdict(int);last_line={}
 for i,x in enumerate(rows):
  if x['parser_level']!='SURFACE_ONLY' or x['world_view']!=world:continue
  fol=x['folio_id'];line=x['physical_line_id']
  if last_line.get(fol)!=line and int(x['paragraph_start']):rec[fol]+=1
  last_line[fol]=line;rid=f'{fol}:R{max(1,rec[fol]):03d}'
  z=base_row(x['observation_id'],i,fol,fol,line,rid,x['register'],x['surface_group'],int(x['group_index']),int(x['group_count']),int(x['paragraph_start']),int(x['paragraph_end']))
  z.update({'host':clean(x['inferred_host']),'wrapper':x['outer_left'],'local_frame':x['local_left'],'right_family':x['right_outer'],'b3':int(x['right_inner']!='NONE'),'display_renderer':'NONE'});out.append(z)
 return out

def load_gdt159(cid):
 with gzip.open(R/'gdt159_diplomatic_corpora.json.gz','rt',encoding='utf8') as h:raw=[x for x in json.load(h)['records'] if x['corpus_id']==cid]
 raw.sort(key=lambda x:(x['unit_id'],int(x['occurrence_index']),int(x['sample_rank'])));counts=Counter(x['unit_id'] for x in raw);seen=Counter();out=[]
 for i,x in enumerate(raw):
  t=g277.normalize_group(x['form'],True)
  if not t:continue
  seen[x['unit_id']]+=1;out.append(base_row(f"{cid}:{i:06d}",i,x['fold_id'],x['unit_id'],x['unit_id'],x['unit_id'],cid,t,seen[x['unit_id']],counts[x['unit_id']],int(seen[x['unit_id']]==1),int(seen[x['unit_id']]==counts[x['unit_id']])))
 return parse_generic(out)

def load_generated(field,cid):
 meta={x['line_id']:x for x in read(R/'gdt155_blinded_diplomatic.tsv') if x['corpus']=='NUREMBERG'};out=[];order=0
 for x in read(R/'gdt157_generated_diplomatic.tsv'):
  m=meta[x['line_id']];toks=g277.groups(x[field],False)
  for gi,t in enumerate(toks,1):
   order+=1;out.append(base_row(f"{cid}:{x['line_id']}:G{gi:03d}",order,x['book'],m['page_id'],x['line_id'],x['record_id'],x['book'],t,gi,len(toks),int(x['line_index'])==1,int(x['line_index'])==int(m['record_line_count'])))
 return parse_generic(out)

def stable_fold(x):return f"F{int(hashlib.sha256((x+'|GDT158').encode()).hexdigest()[:12],16)%12:02d}"
def load_augsburg():
 assert AUG.is_file() and sha(AUG)=='bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1'
 out=[];order=0
 for line in g158.augsburg_lines(AUG):
  for gi,t in enumerate(line.toks,1):
   order+=1;out.append(base_row(f"{line.line_id}:G{gi:03d}",order,stable_fold(line.parent),line.parent,line.line_id,line.parent,line.fold,t,gi,len(line.toks),int(line.order==1),0))
 return parse_generic(out)

def load_pools():
 pools={
 'ORDINARY_NATURAL_LANGUAGE':load_parallel('NUREMBERG',True),'ABBREVIATION_HEAVY_MEDIEVAL':load_parallel('NUREMBERG',False),
 'STE1_EXPANDED_RECIPES':load_parallel('STE1',True),'STE1_DIPLOMATIC_RECIPES':load_parallel('STE1',False),
 'AUGSBURG_ACCOUNTS_1402_1424':load_augsburg(),
 'LEARNED_ABBREVIATION_MAP':load_generated('generated_map','LEARNED_ABBREVIATION_MAP'),'LEARNED_ABBREVIATION_SAMPLED':load_generated('generated_sampled','LEARNED_ABBREVIATION_SAMPLED'),
 'ARBITRARY_LOCAL_CODEBOOK':load_synthetic('gdt172_blind_parses.json.gz','CONTROL_P'),'COMPOSITIONAL_TECHNICAL_NOTATION':load_synthetic('gdt172_blind_parses.json.gz','CONTROL_Q'),'HYBRID_SHORTHAND':load_synthetic('gdt173_blind_parses.json.gz','CONTROL_R')}
 for cid in ('LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','LATIN_SCHOLASTIC_GRAPHEMATIC','IFORAL_1395_1411_GRAPHEMATIC','LATIN_GERMAN_APOTHECARY_LATE15'):pools[cid]=load_gdt159(cid)
 return pools

def char_map(pool,target,train_folios=None):
 cc=Counter()
 for x in pool:
  if train_folios is None or x['physical_folio'] in train_folios:cc.update(clean(x.get('_reparsed_host',x.get('host',x.get('page_host','?')))))
 top=sorted(cc,key=lambda c:(-cc[c],c))[:20];return {c:t for c,t in zip(top,target)},cc
def mapped(host,m):return ''.join(m.get(c,'?') for c in clean(host))

def compilerize(base,cid,ground,s,host):
 x=dict(base);x.update({'control_id':cid,'ground_truth_architecture':ground,'source_observation_id':s['source_observation_id'],'source_folio_hash':h12(s['source_folio']),'source_line_hash':h12(s['source_line']),'source_surface_sha256':hashlib.sha256(s['surface'].encode()).hexdigest(),'page_host':host,'raw_token':s['surface'],'register':s['source_register'],'wrapper':s['wrapper'],'q_flag':0,'local_frame':s['local_frame'],'inner_d':0,'right_family':s['right_family'],'dy_closure':0,'b3':s['b3'],'known_label_renderer':s['display_renderer'],'host_length':len(host),'_surface':s['surface'],'_primary_unmapped_host':s['host'],'_parser_style':'GDT170' if cid in ('ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND') else 'GDT155'});return x

def make_matched(cid,ground,pool,scaf,target):
 quotas=Counter(int(x['host_length']) for x in scaf);avail=Counter(len(clean(x['host'])) for x in pool);missing={n:q-avail[n] for n,q in quotas.items() if avail[n]<q}
 if missing:return None,{'control_id':cid,'view':'LENGTH_MATCHED_OVERLAY','eligible':0,'reason':'INSUFFICIENT_EXACT_HOST_LENGTH_CAPACITY:'+json.dumps(missing,sort_keys=True),'native_events':len(pool),'selected_events':0}
 m,cc=char_map([{'host':x['host'],'physical_folio':x['source_folio']} for x in pool],target);queues={}
 for n,q in quotas.items():
  z=[x for x in pool if len(clean(x['host']))==n]
  legacy=cid in ('ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND')
  salt='GDT277_CONTROL_SELECT' if legacy else 'GDT278_MATCH'
  z.sort(key=lambda x:hashlib.sha256((f'{salt}|{cid}|'+x['source_observation_id']).encode()).hexdigest());queues[n]=deque(sorted(z[:q],key=lambda x:x['source_order']))
 out=[compilerize(b,cid,ground,queues[int(b['host_length'])].popleft(),mapped(queues[int(b['host_length'])][0]['host'],m)) for b in []] # construction below avoids double-pop
 out=[]
 for b in scaf:
  s=queues[int(b['host_length'])].popleft();out.append(compilerize(b,cid,ground,s,mapped(s['host'],m)))
 out=g277.rebuild_context(out);chars=sum(cc.values());covered=sum(v for k,v in cc.items() if k in m)/max(1,chars)
 return out,{'control_id':cid,'view':'LENGTH_MATCHED_OVERLAY','eligible':1,'reason':'EXACT_GDT277_QUOTAS_MET','native_events':len(pool),'selected_events':len(out),'source_folds':len({x['source_folio'] for x in pool}),'scoring_folds':len({x['physical_folio'] for x in out}),'alphabet_codepoints':len(cc),'top20_character_coverage':f'{covered:.12f}','alphabet_map_sha256':csha(m)}

def select_native(cid,pool):
 if len(pool)<=TARGET_NATIVE:return list(pool),'ALL_ELIGIBLE_EVENTS'
 by=defaultdict(list)
 for x in pool:by[x['source_line']].append(x)
 keys=sorted(by,key=lambda z:hashlib.sha256((f'GDT278_NATIVE_UNIT|{cid}|'+z).encode()).hexdigest());sel=[]
 for k in keys:
  need=TARGET_NATIVE-len(sel)
  if need<=0:break
  z=sorted(by[k],key=lambda x:x['source_order']);sel.extend(z[:need])
 return sorted(sel,key=lambda x:x['source_order']),'SHA256_SOURCE_LINE_SELECTION_NATIVE_ORDER_RESTORED'

def make_native(cid,ground,pool,target):
 sel,rule=select_native(cid,pool);m,cc=char_map([{'host':x['host'],'physical_folio':x['source_folio']} for x in sel],target);records=defaultdict(dict);out=[]
 for s in sel:
  pkey=(s['source_folio'],s['source_page']);rmap=records[pkey]
  if s['source_record'] not in rmap:rmap[s['source_record']]=len(rmap)+1
  gi=int(s['source_group_index']);gc=int(s['source_group_count']);pos='ONLY' if gc==1 else 'FIRST' if gi==1 else 'LAST' if gi==gc else 'MIDDLE';page=f"P:{cid}:{h12(s['source_page'])}";line=f"L:{cid}:{h12(s['source_line'])}";fol=f"F:{cid}:{s['source_folio']}";host=mapped(s['host'],m);line_close=int(gi==gc);para_close=int(line_close and s['source_paragraph_end'])
  comp=(s['source_register'],rmap[s['source_record']],1,pos,s['wrapper'],0,s['local_frame'],'0',s['right_family'],'0',str(s['b3']),line_close,para_close,s['display_renderer']);nl=(s['source_register'],rmap[s['source_record']],1,pos,line_close,'<LINE_BOS>' if gi==1 else 'XX')
  out.append({'observation_id':f"GDT278N:{cid}:{s['source_observation_id']}",'control_id':cid,'ground_truth_architecture':ground,'page':page,'physical_folio':fol,'locus':line,'group_index':gi,'group_count':gc,'register':s['source_register'],'section':ground,'currier':'CONTROL','hand':'CONTROL','record_ordinal':rmap[s['source_record']],'field_ordinal':1,'within_field_position':pos,'wrapper':s['wrapper'],'q_flag':0,'local_frame':s['local_frame'],'inner_d':0,'right_family':s['right_family'],'dy_closure':0,'b3':s['b3'],'line_close':line_close,'paragraph_close':para_close,'known_label_renderer':s['display_renderer'],'page_host':host,'raw_token':s['surface'],'previous_page_host':'','compiler_key':json.dumps(comp,separators=(',',':')),'nl_bucket':frozen.bucket('NL',nl),'compiler_bucket':frozen.bucket('COMPILER',comp),'hybrid_bucket':0,'host_length':len(host),'source_observation_id':s['source_observation_id'],'source_folio_hash':h12(s['source_folio']),'source_line_hash':h12(s['source_line']),'source_surface_sha256':hashlib.sha256(s['surface'].encode()).hexdigest(),'_surface':s['surface'],'_primary_unmapped_host':s['host'],'_parser_style':'GDT170' if cid in ('ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND') else 'GDT155'})
 out=g277.rebuild_context(out);chars=sum(cc.values());covered=sum(v for k,v in cc.items() if k in m)/max(1,chars)
 return out,{'control_id':cid,'view':'NATIVE_ORDER','eligible':1,'reason':rule,'native_events':len(pool),'selected_events':len(out),'source_folds':len({x['source_folio'] for x in pool}),'scoring_folds':len({x['physical_folio'] for x in out}),'alphabet_codepoints':len(cc),'top20_character_coverage':f'{covered:.12f}','alphabet_map_sha256':csha(m),'powered_for_gate':int(len(out)>=MIN_NATIVE*TARGET_NATIVE)}

def vms_panels(scaf,full):
 m,_=g277.make_vms_panel(scaf)
 for x in m:x['_surface']=x['raw_token'];x['_primary_unmapped_host']=x['page_host'];x['_parser_style']='VMS_O_OT'
 n=[]
 for b in full:
  x=dict(b);x.update({'control_id':'VOYNICH_REFERENCE','ground_truth_architecture':'UNKNOWN_VOYNICH_ARCHITECTURE','source_observation_id':b['observation_id'],'source_folio_hash':h12(b['physical_folio']),'source_line_hash':h12(b['locus']),'source_surface_sha256':hashlib.sha256(b['raw_token'].encode()).hexdigest(),'_surface':b['raw_token'],'_primary_unmapped_host':b['page_host'],'_parser_style':'VMS_O_OT'});n.append(x)
 return m,n

def one_score(events,buckets=None):
 cap=json.loads((R/'gdt276_design.json').read_text())['capacity'];pri={'char':cap['character_context_prior_mass']};bm=buckets or {x['observation_id']:x['compiler_bucket'] for x in events};return frozen.score_char(events,MODEL,bm,json.loads((R/'gdt276_design.json').read_text())['alphabet'],pri)
def score_published(cid,view,panel):
 q=one_score(panel);vals=[];nr=[]
 for wi in range(64):
  b=frozen.random_buckets(panel,wi)[MODEL];v=one_score(panel,b)['bits'];vals.append(v);nr.append({'control_id':cid,'view':view,'representation':'PUBLISHED_FULL_INVENTORY','world_index':wi,'held_bits':f'{v:.12f}'})
 return summarize(cid,view,'PUBLISHED_FULL_INVENTORY',panel,q,vals),nr,[{'control_id':cid,'view':view,'representation':'PUBLISHED_FULL_INVENTORY','held_folio':f,'events':sum(x['physical_folio']==f for x in panel),'held_bits':f'{b:.12f}'} for f,b in q['folds'].items()]

def fold_char(train,test,buckets):
 design=json.loads((R/'gdt276_design.json').read_text());K=len(design['alphabet']);prior=design['capacity']['character_context_prior_mass'];glob=defaultdict(Counter);ctx=defaultdict(Counter)
 for x in train:
  b=buckets[x['observation_id']]
  for h,c,z in frozen.chars(x['page_host']):glob[h][c]+=1;ctx[b,h][c]+=1
 pagec=defaultdict(lambda:defaultdict(Counter));bits=0.
 for x in test:
  b=buckets[x['observation_id']]
  for h,c,z in frozen.chars(x['page_host']):
   pb=frozen.cprob(glob,h,c,K,0);pp=frozen.cprob(pagec[x['page']],h,c,K,prior,pb);q=ctx[b,h];p=(q[c]+prior*pp)/(sum(q.values())+prior);bits-=math.log2(p);pagec[x['page']][h][c]+=1
 return bits

def safe_reparse(panel,cid,held,target):
 all0=[dict(x) for x in panel];train0=[x for x in all0 if x['physical_folio']!=held]
 if cid=='VOYNICH_REFERENCE':
  prec=[]
  for x in train0:
   h=x['_primary_unmapped_host'];prec.append(('ot'+h) if x['local_frame']=='OT' else ('o'+h) if x['local_frame']=='O' else h)
  ct=Counter(prec);licensed={h for h in ct if ct[h] and ct['o'+h] and ct['ot'+h]}|{'ar','al','ol'}
  for x in all0:
   h=x['_primary_unmapped_host'];pre=('ot'+h) if x['local_frame']=='OT' else ('o'+h) if x['local_frame']=='O' else h;frame='NONE'
   if pre.startswith('ot') and pre[2:] in licensed:host=pre[2:];frame='OT'
   elif pre.startswith('o') and pre[1:] in licensed:host=pre[1:];frame='O'
   else:host=pre
   x['page_host']=host;x['local_frame']=frame;x['_reparsed_host']=host
  amap={c:c for c in target}
 else:
  style=all0[0]['_parser_style'];model=g277.discover([x['_surface'].replace('¤','') for x in train0],[x['physical_folio'] for x in train0],style);cache={}
  for x in all0:
   q=cache.setdefault(x['_surface'],g277.parse_surface(x['_surface'],model,style));x.update({'page_host':q['host'],'_reparsed_host':q['host'],'wrapper':q['wrapper'],'local_frame':q['local_frame'],'right_family':q['right_family'],'b3':q['b3'],'known_label_renderer':q['display_renderer']})
  amap,_=char_map(all0,target,{x['physical_folio'] for x in train0})
 for x in all0:x['page_host']=mapped(x['page_host'],amap)
 return g277.rebuild_context(all0)

def score_safe(cid,view,panel,target):
 folds=sorted({x['physical_folio'] for x in panel});obs=0.;null=[0.]*64;fr=[];changes=0
 for held in folds:
  z=safe_reparse(panel,cid,held,target);changes+=sum(a['page_host']!=b['page_host'] or a['compiler_key']!=b['compiler_key'] for a,b in zip(z,panel));train=[x for x in z if x['physical_folio']!=held];test=[x for x in z if x['physical_folio']==held];bm={x['observation_id']:x['compiler_bucket'] for x in z};b=fold_char(train,test,bm);obs+=b;fr.append({'control_id':cid,'view':view,'representation':'LOFO_SAFE','held_folio':held,'events':len(test),'held_bits':f'{b:.12f}'})
  for wi in range(64):null[wi]+=fold_char(train,test,frozen.random_buckets(z,wi)[MODEL])
 q={'bits':obs,'folds':{x['held_folio']:float(x['held_bits']) for x in fr}}
 nr=[{'control_id':cid,'view':view,'representation':'LOFO_SAFE','world_index':wi,'held_bits':f'{v:.12f}'} for wi,v in enumerate(null)]
 row=summarize(cid,view,'LOFO_SAFE',panel,q,null);row['representation_changes_across_folds']=changes
 return row,nr,fr

def summarize(cid,view,rep,panel,q,vals):
 mean=statistics.mean(vals);sd=statistics.pstdev(vals);saving=mean-q['bits'];z=saving/sd if sd else float('-inf');refview='LENGTH_MATCHED_OVERLAY' if view=='LENGTH_MATCHED_OVERLAY' else 'NATIVE_ORDER';refs={x['view']:x for x in read(R/'gdt278_reference_magnitude.tsv')};rv=refs[refview];se=saving/len(panel);powered=int(view=='LENGTH_MATCHED_OVERLAY' or len(panel)>=MIN_NATIVE*TARGET_NATIVE);repro=int(powered and se>=float(rv['saving_bits_per_event']) and z>=float(rv['null_z']))
 return {'control_id':cid,'view':view,'representation':rep,'events':len(panel),'scoring_folds':len({x['physical_folio'] for x in panel}),'observed_bits':f"{q['bits']:.12f}",'null_mean_bits':f'{mean:.12f}','null_sd_bits':f'{sd:.12f}','saving_bits':f'{saving:.12f}','saving_bits_per_event':f'{se:.12f}','null_z':f'{z:.12f}' if math.isfinite(z) else 'NA','ratio_s_event_to_voynich':f"{se/float(rv['saving_bits_per_event']):.12f}",'ratio_z_to_voynich':f"{z/float(rv['null_z']):.12f}" if math.isfinite(z) else 'NA','powered_for_gate':powered,'reproduces_voynich_magnitude':repro,'lower_tail_p':f"{(1+sum(v<=q['bits']+1e-12 for v in vals))/65:.12f}"}

def job(args):
 cid,view,panel,target=args;p,n1,f1=score_published(cid,view,panel);s,n2,f2=score_safe(cid,view,panel,target);return [p,s],n1+n2,f1+f2

def public_event(x):return {k:v for k,v in x.items() if not k.startswith('_') and k not in ('raw_token','compiler_key')}

def main():
 d=json.loads(DESIGN.read_text());cf=json.loads(CFREEZE.read_text());assert d['status']=='FROZEN_BEFORE_EXPANDED_CONTROL_ADMISSION_OR_SCORING' and cf['status']=='CONTROL_PANEL_FROZEN_BEFORE_GDT278_SCORING'
 full=read(VMS);assert len(full)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in full);target=sorted(set(''.join(x['page_host'] for x in full)));assert len(target)==20
 scaf,_=g277.scaffold(json.loads((R/'gdt277_design.json').read_text()));mp=read(MANIFEST);ground={x['control_id']:x['ground_truth_basis'] for x in mp};pools=load_pools();assert set(pools)==set(ground)
 panels={};caps=[];mi=[];ni=[]
 vm,vn=vms_panels(scaf,full);panels['VOYNICH_REFERENCE:LENGTH_MATCHED_OVERLAY']=vm;panels['VOYNICH_REFERENCE:NATIVE_ORDER']=vn
 caps += [{'control_id':'VOYNICH_REFERENCE','view':'LENGTH_MATCHED_OVERLAY','eligible':1,'reason':'FROZEN_GDT277_REFERENCE','native_events':8448,'selected_events':len(vm),'source_folds':91,'scoring_folds':91,'powered_for_gate':1},{'control_id':'VOYNICH_REFERENCE','view':'NATIVE_ORDER','eligible':1,'reason':'FROZEN_GDT276_REFERENCE','native_events':8448,'selected_events':len(vn),'source_folds':91,'scoring_folds':91,'powered_for_gate':1}]
 mi += [public_event(x) for x in vm];ni += [public_event(x) for x in vn]
 for cid in [x['control_id'] for x in mp]:
  m,cap=make_matched(cid,ground[cid],pools[cid],scaf,target);caps.append(cap)
  if m is not None:panels[cid+':LENGTH_MATCHED_OVERLAY']=m;mi += [public_event(x) for x in m]
  n,cap=make_native(cid,ground[cid],pools[cid],target);caps.append(cap);panels[cid+':NATIVE_ORDER']=n;ni += [public_event(x) for x in n]
 print(json.dumps({'controls_loaded':len(pools),'score_panels':len(panels),'matched_eligible':sum(k.endswith(':LENGTH_MATCHED_OVERLAY') for k in panels)},sort_keys=True),flush=True)
 scores=[];nulls=[];folds=[]
 with ProcessPoolExecutor(max_workers=min(16,len(panels))) as ex:
  fs={ex.submit(job,(k.rsplit(':',1)[0],k.rsplit(':',1)[1],v,target)):k for k,v in panels.items()}
  for f in as_completed(fs):
   sr,nr,fr=f.result();scores+=sr;nulls+=nr;folds+=fr;print(json.dumps({'scored':fs[f]}),flush=True)
 # Published anchors must reproduce GDT277/GDT276 exactly.
 old={x['control_id']:x for x in read(R/'gdt277_world_scores.tsv') if x['model']==MODEL};
 for cid in ('ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND'):
  q=next(x for x in scores if x['control_id']==cid and x['view']=='LENGTH_MATCHED_OVERLAY' and x['representation']=='PUBLISHED_FULL_INVENTORY');assert abs(float(q['saving_bits'])-float(old[cid]['matched_savings_bits']))<1e-7,(cid,q['saving_bits'],old[cid]['matched_savings_bits'])
 vmp=next(x for x in scores if x['control_id']=='VOYNICH_REFERENCE' and x['view']=='NATIVE_ORDER' and x['representation']=='PUBLISHED_FULL_INVENTORY');assert abs(float(vmp['saving_bits'])-3080.522234827527)<1e-7
 scores.sort(key=lambda x:(x['view'],x['representation'],-float(x['saving_bits_per_event'])));ranks=defaultdict(int)
 for x in scores:ranks[(x['view'],x['representation'])]+=1;x['rank_by_saving_bits_per_event']=ranks[(x['view'],x['representation'])]
 write(OUT_CAP,caps);write(OUT_SCORE,scores);write(OUT_NULL,nulls);write(OUT_FOLD,folds);write(OUT_MATCH,mi);write(OUT_NATIVE,ni)
 counter=[
 {'counterexample':'SIGN_OR_RANK_EQUALS_MAGNITUDE','evidence':'GDT277 already showed the sign/rank in A B B2','impact':'GDT278 uses only preregistered bits/event and null-z equality-or-exceedance'},
 {'counterexample':'NULL_Z_IS_SAMPLE_SIZE_FREE','evidence':'z grows with information and event count','impact':'native controls below 80 percent of 8448 cannot pass the native gate'},
 {'counterexample':'MATCHED_OVERLAY_PRESERVES_NATIVE_ORDER','evidence':'exact length queues break cross-length adjacency','impact':'native order is a separate sensitivity'},
 {'counterexample':'NATIVE_PANELS_SHARE_IDENTICAL_LAYOUT','evidence':'real controls keep their source units and synthetic controls keep generated lines','impact':'native differences may reflect layout as intended sensitivity'},
 {'counterexample':'ALPHABET_MAPPING_IS_LOSSLESS','evidence':'only the top 20 visible host characters have named capacity','impact':'coverage and collisions accompany every control'},
 {'counterexample':'FOxton_is_a_scored_nomenclator','evidence':'mechanism audit lacks complete machine-readable diplomatic surfaces','impact':'excluded rather than fabricated'},
 {'counterexample':'GDT156_IS_AN_INDEPENDENT_CONTROL','evidence':'its encoder deliberately imports Voynich HPR2 rules','impact':'excluded'},
 {'counterexample':'ALTERNATE_READINGS_ARE_REPLICATIONS','evidence':'Voynich reference is one manuscript panel','impact':'no alternate reading multiplication'},
 {'counterexample':'F84_USED','evidence':'only frozen gdt276 event inventory supplies Voynich rows and contains zero f84','impact':'no f84 access'},
 {'counterexample':'MAGNITUDE_IDENTIFIES_PAYLOAD','evidence':'endpoint is opaque compiler-conditioned character compression','impact':'no language code meaning plaintext or translation'}];write(OUT_COUNTER,counter)
 pub=[x for x in scores if x['representation']=='PUBLISHED_FULL_INVENTORY' and x['control_id']!='VOYNICH_REFERENCE'];safe=[x for x in scores if x['representation']=='LOFO_SAFE' and x['control_id']!='VOYNICH_REFERENCE'];rob=[]
 for cid in ground:
  qs=[x for x in safe if x['control_id']==cid];views={x['view']:x for x in qs};
  if len(views)==2 and all(int(x['reproduces_voynich_magnitude']) for x in views.values()):rob.append(cid)
 matched_repro=[x for x in safe if x['view']=='LENGTH_MATCHED_OVERLAY' and int(x['reproduces_voynich_magnitude'])];native_repro=[x for x in safe if x['view']=='NATIVE_ORDER' and int(x['reproduces_voynich_magnitude'])]
 if rob:status='VOYNICH_MAGNITUDE_REPRODUCED_BY_KNOWN_ARCHITECTURE'
 elif matched_repro or native_repro:status='VOYNICH_MAGNITUDE_ORDER_OR_MATCHING_SENSITIVE'
 else:status='VOYNICH_MAGNITUDE_OUTSIDE_CURRENT_GROUND_TRUTH_ENVELOPE'
 report=['# GDT278 — frozen magnitude calibration of the GDT277 residual','',f'Status: **{status}**.','','GDT277 remained byte-identical. The endpoint and equality-or-exceedance rule were published before the 15-control panel was admitted. Only compiler-conditioned character-form savings are scored.','','## LOFO-safe magnitude','','| control | architecture | matched bits/event | matched z | matched reproduces | native bits/event | native z | native reproduces |','|---|---|---:|---:|---|---:|---:|---|']
 for cid in ['VOYNICH_REFERENCE']+[x['control_id'] for x in mp]:
  q={x['view']:x for x in scores if x['control_id']==cid and x['representation']=='LOFO_SAFE'};cat='UNKNOWN' if cid=='VOYNICH_REFERENCE' else next(x['architecture_category'] for x in mp if x['control_id']==cid);a=q.get('LENGTH_MATCHED_OVERLAY');b=q.get('NATIVE_ORDER');fmt=lambda x,k:'NA' if x is None else x[k]
  report.append(f"| {cid} | {cat} | {fmt(a,'saving_bits_per_event')} | {fmt(a,'null_z')} | {('NA' if a is None else 'YES' if int(a['reproduces_voynich_magnitude']) else 'NO')} | {fmt(b,'saving_bits_per_event')} | {fmt(b,'null_z')} | {('NA' if b is None else 'YES' if int(b['reproduces_voynich_magnitude']) else 'NO')} |")
 report += ['','A control reproduces a view only when both its normalized saving and null-z equal or exceed the frozen Voynich coordinate. Low-capacity native panels cannot pass. Published-representation anchors, per-fold values, all 64 null worlds, alphabet coverage, and excluded controls are exported separately.','',f"Robust reproductions: **{', '.join(rob) if rob else 'none'}**. Matched-only or native-only reproductions are reported as sensitivity, not combined into a score.",'','## Interpretation','','This is an exposed instrument calibration. A Voynich value outside the admitted envelope means only that these controls do not reproduce its magnitude under the fixed observation/scoring pipeline. It does not identify a language, abbreviation system, codebook, notation, meaning, plaintext, or translation. HPR1 semantics and Voynich substring mining were not used. No f84 source was opened, parsed, retained, joined, or scored.',''];REPORT.write_text('\n'.join(report),encoding='utf8')
 outputs=[OUT_CAP,OUT_SCORE,OUT_NULL,OUT_FOLD,OUT_MATCH,OUT_NATIVE,OUT_COUNTER,REPORT];inputs=['gdt278_magnitude_design.json','gdt278_magnitude_design_validation.json','gdt278_gdt277_freeze_manifest.tsv','gdt278_reference_magnitude.tsv','gdt278_control_manifest.tsv','gdt278_control_source_freeze.json','gdt278_control_source_validation.json','gdt276_event_inventory.tsv','gdt277_world_scores.tsv','gdt276_world_scores.tsv','gdt155_blinded_diplomatic.tsv','gdt155_unblinded_lines.tsv','gdt155_blind_group_parses.tsv','gdt157_generated_diplomatic.tsv','gdt159_diplomatic_corpora.json.gz','gdt159_diplomatic_source_provenance.json','gdt172_blind_parses.json.gz','gdt172_sealed_oracle.json.gz','gdt173_blind_parses.json.gz','gdt173_b2_sealed_oracle.json.gz','gdt158_source_freeze.json']
 result={'schema':'GDT278_MAGNITUDE_CALIBRATION_RESULT_V1','status':status,'controls_admitted':len(mp),'score_panels':len(panels),'robust_reproductions':rob,'matched_safe_reproductions':[x['control_id'] for x in matched_repro],'native_safe_reproductions':[x['control_id'] for x in native_repro],'endpoint':'COMPILER_CONDITIONED_CHARACTER_MATCHED_SAVING_BITS_PER_EVENT_AND_NULL_Z','threshold_tuned':False,'composite_score':False,'hpr1_semantics_used':0,'voynich_substrings_mined':0,'semantic_assignments':0,'oracle_fields_scored':0,'gdt277_immutable':all(sha(R/x['artifact'])==x['frozen_sha256'] for x in read(R/'gdt278_gdt277_freeze_manifest.tsv')),'claim_ceiling':'Magnitude calibration of opaque compiler-conditioned character compression among admitted known architectures only; no language code notation identity meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p:sha(R/p) for p in inputs},'external_source':{'Augsburg_workbook_sha256':sha(AUG),'path_published':False},'documents':{METHOD.name:sha(METHOD),AUDIT.name:sha(AUDIT),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in outputs}};result['content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'robust_reproductions':rob,'matched_reproductions':result['matched_safe_reproductions'],'native_reproductions':result['native_safe_reproductions']},sort_keys=True))
if __name__=='__main__':main()
