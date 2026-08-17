#!/usr/bin/env python3
"""Run the frozen GDT276 instrument on five matched ground-truth controls."""
from __future__ import annotations
import csv,gzip,hashlib,json,math,random,statistics,unicodedata
from collections import Counter,defaultdict,deque
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import run_gdt276_residual_channel_world_comparison as frozen

R=Path(__file__).resolve().parent
DESIGN=R/'gdt277_design.json';DVALID=R/'gdt277_design_validation.json';METHOD=R/'GDT277_GDT276_SIGNATURE_CALIBRATION_METHOD.md'
VMS=R/'gdt276_event_inventory.tsv';VMS_RESULT=R/'gdt276_result.json'
MODELS=tuple(frozen.MODELS);BOOKS=('Band2','Band3','Band4','Band5')
OUT_INV=R/'gdt277_matched_event_inventory.tsv';OUT_CAP=R/'gdt277_capacity_audit.tsv';OUT_WORLD=R/'gdt277_world_scores.tsv';OUT_FOLIO=R/'gdt277_folio_scores.tsv';OUT_NULL=R/'gdt277_null_results.tsv';OUT_LEAK=R/'gdt277_representation_leakage.tsv';OUT_LEAK_FOLD=R/'gdt277_representation_fold_scores.tsv';OUT_SIG=R/'gdt277_signature_summary.tsv';OUT_COUNTER=R/'gdt277_counterexamples.tsv';REPORT=R/'GDT277_GDT276_SIGNATURE_CALIBRATION_REPORT.md';RESULT=R/'gdt277_result.json'
CONTROL_ORDER=('ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND')
GROUND={
 'ORDINARY_NATURAL_LANGUAGE':'KNOWN_EXPANDED_NATURAL_LANGUAGE',
 'ABBREVIATION_HEAVY_MEDIEVAL':'KNOWN_MEDIEVAL_DIPLOMATIC_ABBREVIATION',
 'ARBITRARY_LOCAL_CODEBOOK':'KNOWN_REVERSIBLE_LEXICAL_ID_CODEBOOK',
 'COMPOSITIONAL_TECHNICAL_NOTATION':'KNOWN_REVERSIBLE_FACTORIAL_NOTATION',
 'HYBRID_SHORTHAND':'KNOWN_REVERSIBLE_HUMAN_GROWN_DISTRIBUTED_SHORTHAND',
 'VOYNICH_MATCHED_REFERENCE':'UNKNOWN_VOYNICH_ARCHITECTURE'}
FOLD_MAP=str.maketrans({'ſ':'s','ı':'i','ȷ':'j','ẜ':'s'})

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read_tsv(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(path,rows):
 fields=[]
 for x in rows:
  for k in x:
   if k not in fields:fields.append(k)
 with path.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:x.get(k,'') for k in fields} for x in rows])
def normalize_group(text,marked=True):
 text=unicodedata.normalize('NFC',text).translate(FOLD_MAP).lower()
 return ''.join(ch for ch in text if ch.isalnum() or (marked and ch=='¤'))
def groups(text,marked=True):return [z for p in text.split() if (z:=normalize_group(p,marked))]
def clean_host(x):return '?' if x in ('','EMPTY') else x

def discover(tokens,folios,style):
 counts=Counter(tokens);where=defaultdict(set)
 for t,f in zip(tokens,folios):where[t].add(f)
 vocab=set(counts);stats={};env=Counter()
 for word in sorted(vocab):
  if len(word)<2:continue
  for n in range(1,min(3,len(word)-1)+1):
   base=word[n:]
   if base in vocab:
    q=stats.setdefault(('LEFT',word[:n]),{'hosts':set(),'folios':set(),'pairs':set(),'occ':0});q['hosts'].add(base);q['folios'].update(where[base]|where[word]);q['pairs'].add((base,word));q['occ']+=counts[word];env[base]+=1
   base=word[:-n]
   if base in vocab:
    q=stats.setdefault(('RIGHT',word[-n:]),{'hosts':set(),'folios':set(),'pairs':set(),'occ':0});q['hosts'].add(base);q['folios'].update(where[base]|where[word]);q['pairs'].add((base,word));q['occ']+=counts[word];env[base]+=1
 rows=[]
 for (side,op),q in stats.items():rows.append((side,op,len(q['hosts']),len(q['pairs']),len(q['folios'])))
 rows.sort(key=lambda z:(z[0],-z[2],-z[3],z[1]));left=[x[1] for x in rows if x[0]=='LEFT' and x[2]>=8 and x[4]>=5][:12];right=[x[1] for x in rows if x[0]=='RIGHT' and x[2]>=8 and x[4]>=5][:12]
 return counts,left,right,env

def parse_surface(surface,model,style):
 counts,left,right,env=model;base=surface.replace('¤','');marked=int('¤' in surface);states={(base,(),())};front=set(states);depth=4 if style=='GDT155' else 3
 for _ in range(depth):
  nxt=set()
  for host,ls,rs in front:
   if len(ls)<2 and (style=='GDT155' or len(ls)+len(rs)<3):
    for op in left:
     if host.startswith(op) and len(host)>len(op):
      z=host[len(op):]
      if counts[z] or env.get(z,0)>=2:nxt.add((z,ls+(op,),rs))
   if len(rs)<2 and (style=='GDT155' or len(ls)+len(rs)<3):
    for op in right:
     if host.endswith(op) and len(host)>len(op):
      z=host[:-len(op)]
      if counts[z] or env.get(z,0)>=2:nxt.add((z,ls,rs+(op,)))
  nxt-=states
  if not nxt:break
  states|=nxt;front=nxt
 def rank(z):
  host,ls,rs=z;rec=counts[host]+.25*env.get(host,0)
  return (-rec,len(ls)+len(rs),-len(host),ls,rs,host)
 host,ls,rs=min(states,key=rank)
 return {'host':clean_host(host),'wrapper':ls[0] if ls else 'NONE','local_frame':ls[1] if len(ls)>1 else 'NONE','right_family':rs[0] if rs else 'NONE','b3':int(len(rs)>1),'display_renderer':'ABBREVIATION_MARKED' if marked else 'NONE'}

def load_nuremberg(expanded):
 meta=read_tsv(R/'gdt155_blinded_diplomatic.tsv');meta=[x for x in meta if x['corpus']=='NUREMBERG'];truth={x['line_id']:x['expanded_diplomatic'] for x in read_tsv(R/'gdt155_unblinded_lines.tsv') if x['corpus']=='NUREMBERG'}
 parse_maps=defaultdict(dict)
 if not expanded:
  for x in read_tsv(R/'gdt155_blind_group_parses.tsv'):
   if x['fold'] in BOOKS:parse_maps[x['fold']][x['surface_group']]={'host':clean_host(x['page_host']),'wrapper':x['outer_left'],'local_frame':x['local_left'],'right_family':x['right_outer'],'b3':int(x['right_inner']!='NONE'),'display_renderer':'ABBREVIATION_MARKED' if x['abbreviation_marker']=='1' else 'NONE'}
 else:
  bybook=defaultdict(list)
  for x in meta:
   for t in groups(truth[x['line_id']],False):bybook[x['book_or_ms']].append((t,x['record_id']))
  for held in BOOKS:
   toks=[];fol=[]
   for b,z in bybook.items():
    if b!=held:
     for t,r in z:toks.append(t);fol.append(r)
   model=discover(toks,fol,'GDT155')
   for t in sorted({q[0] for q in bybook[held]}):parse_maps[held][t]=parse_surface(t,model,'GDT155')
 out=[];order=0
 for x in meta:
  text=truth[x['line_id']] if expanded else x['diplomatic_marked'];toks=groups(text,not expanded)
  for gi,t in enumerate(toks,1):
   order+=1;q=parse_maps[x['book_or_ms']][t]
   out.append({'source_observation_id':f"{x['line_id']}:G{gi:03d}",'source_order':order,'source_folio':x['page_id'],'source_line':x['line_id'],'source_register':x['book_or_ms'],'surface':t,**q})
 return out

def load_synthetic(path,world):
 with gzip.open(R/path,'rt',encoding='utf8') as h:rows=json.load(h)['rows']
 out=[]
 for i,x in enumerate(rows):
  if x['parser_level']!='SURFACE_ONLY' or x['world_view']!=world:continue
  out.append({'source_observation_id':x['observation_id'],'source_order':i,'source_folio':x['folio_id'],'source_line':x['physical_line_id'],'source_register':x['register'],'surface':x['surface_group'],'host':clean_host(x['inferred_host']),'wrapper':x['outer_left'],'local_frame':x['local_left'],'right_family':x['right_outer'],'b3':int(x['right_inner']!='NONE'),'display_renderer':'NONE'})
 return out

def char_map(pool,target_chars,training_ids=None):
 counts=Counter()
 for x in pool:
  if training_ids is None or x['physical_folio'] in training_ids:
   counts.update(clean_host(x.get('_reparsed_host',x.get('_primary_unmapped_host',x.get('host','?')))))
 ranked=sorted(counts,key=lambda c:(-counts[c],c));top=ranked[:20];mapping={c:t for c,t in zip(top,target_chars)}
 return mapping,counts
def map_host(host,mapping):return ''.join(mapping.get(c,'?') for c in clean_host(host))

def scaffold(design):
 rows=read_tsv(VMS);assert rows and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows)
 quotas={int(k):int(v) for k,v in design['matched_view']['length_quotas'].items()};chosen=set()
 for n,q in quotas.items():
  z=[x for x in rows if int(x['host_length'])==n];z.sort(key=lambda x:hashlib.sha256(('GDT277_SCAFFOLD|'+x['observation_id']).encode()).hexdigest());assert len(z)>=q;chosen.update(x['observation_id'] for x in z[:q])
 out=[x for x in rows if x['observation_id'] in chosen];assert len(out)==sum(quotas.values())
 return out,rows

def compilerize(base,control,source,host):
 x=dict(base);x['control_id']=control;x['ground_truth_architecture']=GROUND[control];x['source_observation_id']=source['source_observation_id'];x['source_folio_hash']=hashlib.sha256(source['source_folio'].encode()).hexdigest()[:20];x['source_line_hash']=hashlib.sha256(source['source_line'].encode()).hexdigest()[:20];x['source_surface_sha256']=hashlib.sha256(source['surface'].encode()).hexdigest();x['_surface']=source['surface'];x['_parser_style']='GDT155' if control in CONTROL_ORDER[:2] else 'GDT170';x['_primary_unmapped_host']=source['host'];x['page_host']=host;x['raw_token']=source['surface'];x['register']=source['source_register'];x['wrapper']=source['wrapper'];x['q_flag']=0;x['local_frame']=source['local_frame'];x['inner_d']=0;x['right_family']=source['right_family'];x['dy_closure']=0;x['b3']=source['b3'];x['known_label_renderer']=source['display_renderer'];x['host_length']=len(host);return x

def rebuild_context(rows):
 prev={};out=[]
 for x0 in rows:
  x=dict(x0);key=x['locus'];p=prev.get(key,'<LINE_BOS>');x['previous_page_host']=p
  comp=(x['register'],int(x['record_ordinal']),int(x['field_ordinal']),x['within_field_position'],x['wrapper'],int(x['q_flag']),x['local_frame'],str(x['inner_d']),x['right_family'],str(x['dy_closure']),str(x['b3']),int(x['line_close']),int(x['paragraph_close']),x['known_label_renderer'])
  nl=(x['register'],int(x['record_ordinal']),int(x['field_ordinal']),x['within_field_position'],int(x['line_close']),p[-2:]);x['compiler_key']=json.dumps(comp,separators=(',',':'));x['nl_bucket']=frozen.bucket('NL',nl);x['compiler_bucket']=frozen.bucket('COMPILER',comp);x['hybrid_bucket']=frozen.bucket('HYBRID',(comp,p));x['host_length']=len(x['page_host']);prev[key]=x['page_host'];out.append(x)
 return out

def make_panel(control,pool,scaf,target_chars):
 mapping,counts=char_map([{'host':x['host'],'physical_folio':x['source_folio']} for x in pool],target_chars);queues={}
 for n in sorted({int(x['host_length']) for x in scaf}):
  z=[x for x in pool if len(clean_host(x['host']))==n];z.sort(key=lambda x:hashlib.sha256((f'GDT277_CONTROL_SELECT|{control}|'+x['source_observation_id']).encode()).hexdigest());need=sum(int(x['host_length'])==n for x in scaf);assert len(z)>=need,(control,n,len(z),need);sel=sorted(z[:need],key=lambda x:x['source_order']);queues[n]=deque(sel)
 out=[]
 for b in scaf:
  n=int(b['host_length']);s=queues[n].popleft();out.append(compilerize(b,control,s,map_host(s['host'],mapping)))
 out=rebuild_context(out);unknown=sum(c not in mapping for x in pool for c in clean_host(x['host']));chars=sum(len(clean_host(x['host'])) for x in pool);sel_unknown=sum('?' in x['page_host'] for x in out);unique_before=len({clean_host(x['host']) for x in pool});unique_after=len({map_host(x['host'],mapping) for x in pool})
 cap={'control_id':control,'native_events':len(pool),'native_folios':len({x['source_folio'] for x in pool}),'native_lines':len({x['source_line'] for x in pool}),'native_registers':len({x['source_register'] for x in pool}),'native_alphabet_codepoints':len(counts),'matched_events':len(out),'matched_folios':len({x['physical_folio'] for x in out}),'matched_pages':len({x['page'] for x in out}),'matched_lines':len({x['locus'] for x in out}),'top20_character_coverage':f'{1-unknown/chars:.12f}','matched_hosts_with_unknown':sel_unknown,'unique_unmapped_hosts':unique_before,'unique_capacity_hosts':unique_after,'alphabet_map_sha256':csha(mapping),'oracle_fields_used_for_scoring':0}
 return out,cap,mapping

def make_vms_panel(scaf):
 out=[]
 for b in scaf:
  x=dict(b);x['control_id']='VOYNICH_MATCHED_REFERENCE';x['ground_truth_architecture']=GROUND[x['control_id']];x['source_observation_id']=b['observation_id'];x['source_folio_hash']=hashlib.sha256(b['physical_folio'].encode()).hexdigest()[:20];x['source_line_hash']=hashlib.sha256(b['locus'].encode()).hexdigest()[:20];x['source_surface_sha256']=hashlib.sha256(b['raw_token'].encode()).hexdigest();x['_surface']=b['raw_token'];x['_primary_unmapped_host']=b['page_host'];x['_parser_style']='VMS_O_OT';out.append(x)
 out=rebuild_context(out);cap={'control_id':'VOYNICH_MATCHED_REFERENCE','native_events':8448,'native_folios':91,'native_lines':1143,'native_registers':len({x['register'] for x in out}),'native_alphabet_codepoints':len(set(''.join(x['page_host'] for x in out))),'matched_events':len(out),'matched_folios':len({x['physical_folio'] for x in out}),'matched_pages':len({x['page'] for x in out}),'matched_lines':len({x['locus'] for x in out}),'top20_character_coverage':'1.000000000000','matched_hosts_with_unknown':0,'unique_unmapped_hosts':len({x['page_host'] for x in out}),'unique_capacity_hosts':len({x['page_host'] for x in out}),'alphabet_map_sha256':'IDENTITY_SOURCE_NATIVE','oracle_fields_used_for_scoring':0};return out,cap

def primary_scores(panel,design):
 observed=frozen.score_models(panel,design);null={m:[] for m in MODELS if m!='LOCAL_CODEBOOK'};nr=[]
 for wi in range(design['matched_control_worlds']):
  z=frozen.score_models(panel,design,frozen.random_buckets(panel,wi))
  for m in null:null[m].append(z[m]['bits']);nr.append({'control_id':panel[0]['control_id'],'world_index':wi,'model':m,'held_bits':f"{z[m]['bits']:.12f}"})
 rows=[];fr=[];selector=design['capacity']['world_selector_bits'];symbols=sum(len(x['page_host'])+1 for x in panel)
 for m in MODELS:
  q=observed[m];vals=null.get(m,[]);mean=statistics.mean(vals) if vals else q['bits'];sd=statistics.pstdev(vals) if vals else 0.;p=(1+sum(v<=q['bits']+1e-12 for v in vals))/(1+len(vals)) if vals else 1.
  rows.append({'control_id':panel[0]['control_id'],'representation_view':'PUBLISHED_FULL_INVENTORY','model':m,'held_bits':f"{q['bits']:.12f}",'selector_paid_bits':f"{q['bits']+selector:.12f}",'bits_per_group':f"{q['bits']/len(panel):.12f}",'bits_per_host_symbol_including_eos':f"{q['bits']/symbols:.12f}",'matched_null_mean_bits':f'{mean:.12f}','matched_null_sd_bits':f'{sd:.12f}','matched_savings_bits':f"{mean-q['bits']:.12f}",'matched_lower_tail_p':f'{p:.12f}','rank':0})
  for fol,b in q['folds'].items():fr.append({'control_id':panel[0]['control_id'],'representation_view':'PUBLISHED_FULL_INVENTORY','model':m,'held_folio':fol,'groups':sum(x['physical_folio']==fol for x in panel),'held_bits':f'{b:.12f}'})
 rows.sort(key=lambda x:float(x['selector_paid_bits']));
 for i,x in enumerate(rows,1):x['rank']=i
 return observed,rows,fr,nr

def single_fold_scores(train,test,design):
 cap=design['capacity'];pri={'char':cap['character_context_prior_mass'],'global':cap['global_token_prior_mass'],'page':cap['page_token_prior_mass'],'ctx':cap['context_token_prior_mass']};alphabet=design['alphabet'];K=len(alphabet)
 globchar=defaultdict(Counter)
 for x in train:
  for h,c,z in frozen.chars(x['page_host']):globchar[h][c]+=1
 pagechar=defaultdict(lambda:defaultdict(Counter));literal={};litbits=0.
 for x in test:
  p=1.
  for h,c,z in frozen.chars(x['page_host']):
   pb=frozen.cprob(globchar,h,c,K,0);pp=frozen.cprob(pagechar[x['page']],h,c,K,pri['char'],pb);p*=pp;litbits-=math.log2(pp);pagechar[x['page']][h][c]+=1
  literal[x['observation_id']]=p
 def schar(key):
  gc=defaultdict(Counter);cc=defaultdict(Counter)
  for x in train:
   b=x[key]
   for h,c,z in frozen.chars(x['page_host']):gc[h][c]+=1;cc[b,h][c]+=1
  pc=defaultdict(lambda:defaultdict(Counter));bits=0.
  for x in test:
   b=x[key]
   for h,c,z in frozen.chars(x['page_host']):
    pb=frozen.cprob(gc,h,c,K,0);pp=frozen.cprob(pc[x['page']],h,c,K,pri['char'],pb);q=cc[b,h];p=(q[c]+pri['char']*pp)/(sum(q.values())+pri['char']);bits-=math.log2(p);pc[x['page']][h][c]+=1
  return bits
 def stok(key=None):
  gg=Counter(x['page_host'] for x in train);ctx=defaultdict(Counter)
  if key:
   for x in train:ctx[x[key]][x['page_host']]+=1
  pc=defaultdict(Counter);N=sum(gg.values());bits=0.
  for x in test:
   y=x['page_host'];pl=literal[x['observation_id']];pg=(gg[y]+pri['global']*pl)/(N+pri['global']);q=pc[x['page']];pp=(q[y]+pri['page']*pg)/(sum(q.values())+pri['page'])
   if key:
    z=ctx[x[key]];p=(z[y]+pri['ctx']*pp)/(sum(z.values())+pri['ctx'])
   else:p=pp
   bits-=math.log2(p);q[y]+=1
  return bits
 return {'COMPRESSED_NATURAL_LANGUAGE':schar('nl_bucket'),'ABBREVIATION_HEAVY_LANGUAGE':schar('compiler_bucket'),'LOCAL_CODEBOOK':stok(),'TECHNICAL_NOTATION':stok('compiler_bucket'),'HYBRID':stok('hybrid_bucket')}

def leakage_safe(panel,control,design,target_chars):
 folds=sorted({x['physical_folio'] for x in panel});tot=Counter();foldrows=[];changed=0;ophashes=[];alphashes=[]
 for held in folds:
  train0=[x for x in panel if x['physical_folio']!=held];all0=[dict(x) for x in panel]
  if control=='VOYNICH_MATCHED_REFERENCE':
   prec=[]
   for x in train0:
    h=x['_primary_unmapped_host'];prec.append(('ot'+h) if x['local_frame']=='OT' else ('o'+h) if x['local_frame']=='O' else h)
   ct=Counter(prec);licensed={h for h in ct if ct[h] and ct['o'+h] and ct['ot'+h]}|{'ar','al','ol'};ophashes.append(csha(sorted(licensed)))
   for x in all0:
    h=x['_primary_unmapped_host'];pre=('ot'+h) if x['local_frame']=='OT' else ('o'+h) if x['local_frame']=='O' else h;frame='NONE'
    if pre.startswith('ot') and pre[2:] in licensed:host=pre[2:];frame='OT'
    elif pre.startswith('o') and pre[1:] in licensed:host=pre[1:];frame='O'
    else:host=pre
    x['_reparsed_host']=host;x['local_frame']=frame;x['page_host']=host
   amap={c:c for c in target_chars};alphashes.append('IDENTITY_SOURCE_NATIVE')
  else:
   style=panel[0]['_parser_style'];tokens=[x['_surface'].replace('¤','') for x in train0];folios=[x['physical_folio'] for x in train0];model=discover(tokens,folios,style);ophashes.append(csha({'left':model[1],'right':model[2]}))
   for x in all0:
    q=parse_surface(x['_surface'],model,style);x['_reparsed_host']=q['host'];x['wrapper']=q['wrapper'];x['local_frame']=q['local_frame'];x['right_family']=q['right_family'];x['b3']=q['b3'];x['known_label_renderer']=q['display_renderer'];x['page_host']=q['host']
   train_ids={x['physical_folio'] for x in train0};amap,_=char_map(all0,target_chars,train_ids);alphashes.append(csha(amap))
  for x in all0:x['page_host']=map_host(x['page_host'],amap)
  all0=rebuild_context(all0);changed+=sum(x['page_host']!=y['page_host'] or x['compiler_key']!=y['compiler_key'] for x,y in zip(all0,panel));train=[x for x in all0 if x['physical_folio']!=held];test=[x for x in all0 if x['physical_folio']==held];bits=single_fold_scores(train,test,design)
  for m,b in bits.items():tot[m]+=b;foldrows.append({'control_id':control,'held_folio':held,'model':m,'groups':len(test),'held_bits':f'{b:.12f}','training_folios':len(folds)-1,'held_folio_in_training':0,'operation_inventory_sha256':ophashes[-1],'alphabet_map_sha256':alphashes[-1]})
 rows=[];selector=design['capacity']['world_selector_bits']
 for m,b in tot.items():rows.append({'control_id':control,'model':m,'published_inventory_bits':'','lofo_safe_bits':f'{b:.12f}','lofo_safe_selector_paid_bits':f'{b+selector:.12f}','lofo_safe_rank':0,'fold_event_representation_changes':changed,'distinct_operation_inventory_hashes':len(set(ophashes)),'distinct_alphabet_map_hashes':len(set(alphashes))})
 rows.sort(key=lambda x:float(x['lofo_safe_selector_paid_bits']));
 for i,x in enumerate(rows,1):x['lofo_safe_rank']=i
 return rows,foldrows

def primary_job(args):
 cid,panel,design=args
 return cid,primary_scores(panel,design)

def leakage_job(args):
 cid,panel,design,target_chars=args
 return cid,leakage_safe(panel,cid,design,target_chars)

def main():
 design=json.loads(DESIGN.read_text());assert design['status']=='FROZEN_BEFORE_GDT277_SCORING';base=json.loads((R/'gdt276_design.json').read_text());assert base['capacity']['context_buckets']==256 and base['matched_control_worlds']==64
 scaf,fullv=scaffold(design);target_chars=sorted(set(''.join(x['page_host'] for x in fullv)));assert len(target_chars)==20 and not any(x['page'].startswith('f84') for x in fullv)
 pools={'ORDINARY_NATURAL_LANGUAGE':load_nuremberg(True),'ABBREVIATION_HEAVY_MEDIEVAL':load_nuremberg(False),'ARBITRARY_LOCAL_CODEBOOK':load_synthetic('gdt172_blind_parses.json.gz','CONTROL_P'),'COMPOSITIONAL_TECHNICAL_NOTATION':load_synthetic('gdt172_blind_parses.json.gz','CONTROL_Q'),'HYBRID_SHORTHAND':load_synthetic('gdt173_blind_parses.json.gz','CONTROL_R')}
 panels={};caps=[];maps={}
 for cid in CONTROL_ORDER:panels[cid],cap,maps[cid]=make_panel(cid,pools[cid],scaf,target_chars);caps.append(cap)
 panels['VOYNICH_MATCHED_REFERENCE'],cap=make_vms_panel(scaf);caps.append(cap)
 ids=CONTROL_ORDER+('VOYNICH_MATCHED_REFERENCE',);worldrows=[];folrows=[];nullrows=[];observed={}
 with ProcessPoolExecutor(max_workers=6) as ex:
  futures=[ex.submit(primary_job,(cid,panels[cid],base)) for cid in ids]
  for f in as_completed(futures):
   cid,(obs,wr,fr,nr)=f.result();print(json.dumps({'primary_complete':cid}),flush=True);observed[cid]=obs;worldrows+=wr;folrows+=fr;nullrows+=nr
 leakrows=[];leakfold=[];leak_out={}
 with ProcessPoolExecutor(max_workers=6) as ex:
  futures=[ex.submit(leakage_job,(cid,panels[cid],base,target_chars)) for cid in ids]
  for f in as_completed(futures):
   cid,(lr,lf)=f.result();print(json.dumps({'leakage_complete':cid}),flush=True);leak_out[cid]=(lr,lf)
 for cid in ids:
  lr,lf=leak_out[cid];pub={x['model']:x for x in worldrows if x['control_id']==cid}
  for x in lr:x['published_inventory_bits']=pub[x['model']]['held_bits'];x['safe_minus_published_bits']=f"{float(x['lofo_safe_bits'])-float(x['published_inventory_bits']):.12f}"
  leakrows+=lr;leakfold+=lf
 sig=[]
 for cid in CONTROL_ORDER+('VOYNICH_MATCHED_REFERENCE',):
  q={x['model']:x for x in worldrows if x['control_id']==cid};a=q['ABBREVIATION_HEAVY_LANGUAGE'];flags={'abbreviation_rank_1':int(a['rank']==1),'abbreviation_beats_compressed':int(float(a['held_bits'])<float(q['COMPRESSED_NATURAL_LANGUAGE']['held_bits'])),'abbreviation_matched_saving_positive':int(float(a['matched_savings_bits'])>0)};safe={x['model']:x for x in leakrows if x['control_id']==cid};safe_a=safe['ABBREVIATION_HEAVY_LANGUAGE'];safe_flags={'safe_abbreviation_rank_1':int(safe_a['lofo_safe_rank']==1),'safe_abbreviation_beats_compressed':int(float(safe_a['lofo_safe_bits'])<float(safe['COMPRESSED_NATURAL_LANGUAGE']['lofo_safe_bits']))}
  sig.append({'control_id':cid,'ground_truth_architecture':GROUND[cid],'signature_all_three':int(all(flags.values())),'published_leading_world':min(q.values(),key=lambda x:int(x['rank']))['model'],'abbreviation_minus_compressed_bits':f"{float(a['held_bits'])-float(q['COMPRESSED_NATURAL_LANGUAGE']['held_bits']):.12f}",'abbreviation_matched_savings_bits':a['matched_savings_bits'],**flags,**safe_flags,'lofo_safe_signature_rank_and_direction':int(all(safe_flags.values())),'interpretation':'CALIBRATION_ONLY_NO_SEMANTIC_ASSIGNMENT'})
 nons=[x for x in sig if x['control_id'] in ('ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND') and x['signature_all_three']];lang=[x for x in sig if x['control_id'] in ('ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL') and x['signature_all_three']];v=next(x for x in sig if x['control_id']=='VOYNICH_MATCHED_REFERENCE')
 if nons:status='GDT276_SIGNATURE_NOT_ARCHITECTURE_SPECIFIC'
 elif v['signature_all_three'] and lang:status='GDT276_SIGNATURE_LANGUAGE_ABBREVIATION_SELECTIVE_IN_FROZEN_CONTROLS'
 else:status='GDT276_SIGNATURE_DIAGNOSTICITY_UNRESOLVED'
 safe_nons=[x for x in sig if x['control_id'] in ('ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND') and x['lofo_safe_signature_rank_and_direction']]
 outinv=[]
 for cid,z in panels.items():
  for x in z:outinv.append({k:v for k,v in x.items() if not k.startswith('_') and k not in ('raw_token','compiler_key')})
 write(OUT_INV,outinv);write(OUT_CAP,caps);write(OUT_WORLD,worldrows);write(OUT_FOLIO,folrows);write(OUT_NULL,nullrows);write(OUT_LEAK,leakrows);write(OUT_LEAK_FOLD,leakfold);write(OUT_SIG,sig)
 counter=[
 {'counterexample':'MATCHED_SCAFFOLD_BREAKS_NATIVE_CROSS_LENGTH_ADJACENCY','evidence':'source order retained only within exact host-length queues','impact':'HYBRID sequential score is descriptive and excluded from signature'},
 {'counterexample':'ALPHABET_CAPACITY_MAPPING_IS_LOSSY','evidence':'characters outside each global top20 map to ?','impact':'coverage and unique-host collisions must accompany every control score'},
 {'counterexample':'SYNTHETIC_CONTROLS_ARE_CONSTRUCTED','evidence':'A factorial B and B2 share a frozen medieval-source schedule but are not historical documents','impact':'they calibrate architecture not historical prevalence'},
 {'counterexample':'Nuremberg_views_are_paired','evidence':'ordinary and abbreviated controls are two representations of the same four books','impact':'they are a causal contrast not independent corpora'},
 {'counterexample':'GDT276_PANEL_EXPOSED','evidence':'Voynich five-world result predates this calibration','impact':'calibration diagnoses an existing signature and is not a new confirmatory Voynich test'},
 {'counterexample':'REPRESENTATION_SENSITIVITY_CHANGES_TARGET_ENCODING','evidence':'fold-local parser and alphabet are not rematched after reparse','impact':'safe score is a leakage stress test rather than a replacement primary panel'},
 {'counterexample':'NO_SEMANTIC_ENDPOINT','evidence':'all targets are opaque represented hosts','impact':'no language notation meaning plaintext or translation follows'}];write(OUT_COUNTER,counter)
 rows_by={cid:sorted([x for x in worldrows if x['control_id']==cid],key=lambda x:int(x['rank'])) for cid in panels};report=['# GDT277 — calibration of the frozen GDT276 MDL signature','',f'Status: **{status}**.','','GDT276 remained byte-identical. Five known control architectures were passed through the frozen five-world scorer on one exact 4,476-event length/structure/alphabet-capacity view.','','| architecture | leading world | abbreviation − compressed bits | matched saving | signature | LOFO-safe rank+direction |','|---|---|---:|---:|---|---|']
 for x in sig:report.append(f"| {x['control_id']} | {x['published_leading_world']} | {float(x['abbreviation_minus_compressed_bits']):+.1f} | {float(x['abbreviation_matched_savings_bits']):+.1f} | {'YES' if x['signature_all_three'] else 'NO'} | {'YES' if x['lofo_safe_signature_rank_and_direction'] else 'NO'} |")
 report += ['','The fixed signature requires the abbreviation-heavy character world to rank first, beat the compressed character world, and save bits against its matched context permutation. The table is a diagnostic calibration, not a model posterior.','',f"Known non-language code/notation systems with the full fixed signature: **{len(nons)}** ({', '.join(x['control_id'] for x in nons) or 'none'}). Known language/abbreviation controls with it: **{len(lang)}** ({', '.join(x['control_id'] for x in lang) or 'none'}). Under the strict fold-local representation, non-language systems retaining rank+direction: **{len(safe_nons)}** ({', '.join(x['control_id'] for x in safe_nons) or 'none'}).",'','## Limits','','The capacity overlay exactly matches host length at each retained Voynich structural opportunity, but necessarily breaks native adjacency across length queues. Alphabet normalization is lossy and reported. Expanded and diplomatic Nuremberg are paired views, while A/B/B2 are constructed controls. These facts prevent a cultural or linguistic inference even if the signature is selective.','','No PAGE_HOST substring was mined. No meaning, language, notation identity, plaintext, or translation is assigned. The only Voynich input was the published f84-free GDT276 event inventory; no f84 row or source was opened, parsed, retained, joined, or scored.',''];REPORT.write_text('\n'.join(report),encoding='utf8')
 outputs=[OUT_INV,OUT_CAP,OUT_WORLD,OUT_FOLIO,OUT_NULL,OUT_LEAK,OUT_LEAK_FOLD,OUT_SIG,OUT_COUNTER,REPORT]
 inputs=['gdt276_event_inventory.tsv','gdt276_result.json','gdt276_design.json','gdt277_design.json','gdt277_design_validation.json','gdt277_gdt276_freeze_manifest.tsv','gdt277_control_manifest.tsv','gdt155_blinded_diplomatic.tsv','gdt155_unblinded_lines.tsv','gdt155_blind_group_parses.tsv','gdt172_blind_parses.json.gz','gdt172_sealed_oracle.json.gz','gdt173_blind_parses.json.gz','gdt173_b2_sealed_oracle.json.gz']
 result={'schema':'GDT277_GDT276_SIGNATURE_CALIBRATION_RESULT_V1','status':status,'matched_events_per_panel':len(scaf),'panels':len(panels),'signature_summary':sig,'known_nonlanguage_full_signature_count':len(nons),'known_language_full_signature_count':len(lang),'safe_nonlanguage_rank_direction_count':len(safe_nons),'gdt276_immutable':all(sha(R/x['artifact'])==x['frozen_sha256'] for x in read_tsv(R/'gdt277_gdt276_freeze_manifest.tsv')),'oracle_fields_used_for_scoring':0,'semantic_assignments':0,'claim_ceiling':'Diagnostic selectivity of the frozen GDT276 operational MDL signature across five known architectures only; no language notation identity meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p:sha(R/p) for p in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in outputs}};result['content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'nonspecific_controls':[x['control_id'] for x in nons],'language_controls':[x['control_id'] for x in lang],'vms_signature':v['signature_all_three']},sort_keys=True))
if __name__=='__main__':main()
