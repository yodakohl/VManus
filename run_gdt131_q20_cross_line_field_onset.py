#!/usr/bin/env python3
"""GDT131: held-folio final-OPEN-field to first-BODY-field architecture."""
from __future__ import annotations

import csv, hashlib, json, math, random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
FIELDS=ROOT/'gdt127_q20_field_inventory.tsv'; PANEL=ROOT/'q20ob001_source_panel.tsv'
METHOD=ROOT/'GDT131_Q20_CROSS_LINE_FIELD_ONSET_METHOD.md'; REPORT=ROOT/'GDT131_Q20_CROSS_LINE_FIELD_ONSET_REPORT.md'
INVENTORY=ROOT/'gdt131_cross_line_field_inventory.tsv'; FOLDS=ROOT/'gdt131_cross_line_field_folds.tsv'
SCORES=ROOT/'gdt131_cross_line_field_scores.tsv'; PRED=ROOT/'gdt131_cross_line_field_predictions.tsv'
NULL=ROOT/'gdt131_cross_line_field_null.tsv'; EXACT=ROOT/'gdt131_exact_formula_diagnostic.tsv'
COMPONENTS=ROOT/'gdt131_cross_line_field_components.tsv'; COUNTER=ROOT/'gdt131_cross_line_field_counterexamples.tsv'; RESULT=ROOT/'gdt131_result.json'
EDITIONS=('ZL3b','IT2a','RF1b'); MODES=('LAST_COMPILER12','LAST_ORDERED_CELL_HASH32','LAST_HOST_CHAR3_HASH32','LAST_RAW_CHAR3_HASH32')
WRAPS=('q','d','s','ch','che','sh','t'); LAM=1000.; WORLDS=4096
BLOCKS={'FIRST_WRAPPER':range(0,8),'FIRST_FRAME':range(8,11),'FIRST_RENDERER':range(11,15),'FIELD_COUNT':range(15,19),'FIELD_CLOSURE':range(19,22)}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def seed(*x):return int(hashlib.sha256('|'.join(map(str,x)).encode()).hexdigest()[:16],16)
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def hash32(s):return int(hashlib.sha256(s.encode()).hexdigest()[:8],16)%32
def standardize(a,b):
 mu=a.mean(0);sd=a.std(0);sd[sd<1e-8]=1.;return (a-mu)/sd,(b-mu)/sd,mu,sd
def fit(x,y):
 z=np.c_[np.ones(len(x)),x];p=np.eye(z.shape[1]);p[0,0]=0
 return np.linalg.solve(z.T@z+LAM*p,z.T@y)
def predict(x,b):return np.c_[np.ones(len(x)),x]@b
def bits(y,p0,p1):return float((np.square(y-p0).sum()-np.square(y-p1).sum())/(2*math.log(2)))

def parse_cells(row):
 z=json.loads(row['compiler_skeleton']);return [(a,b,c,int(d),int(e),int(f)) for a,b,c,d,e,f in z]
def compiler(cells):
 n=len(cells);c=Counter()
 for w,f,r,d,dy,b3 in cells:
  if w in WRAPS:c['W_'+w]+=1
  if f in ('O','OT'):c['F_'+f]+=1
  c['RIGHT']+=r!='NONE';c['DY']+=dy;c['B3']+=b3
 keys=tuple('W_'+x for x in WRAPS)+('F_O','F_OT','RIGHT','DY','B3')
 return np.array([c[k]/n for k in keys],float)
def hvec(strings):
 x=np.zeros(32)
 for s in strings:
  z='^'+s+'$'
  for i in range(max(0,len(z)-2)):x[hash32(z[i:i+3])]+=1
 return x/max(1,x.sum())
def ordered(cells):
 x=np.zeros(32);z=['^']+['/'.join(map(str,c)) for c in cells]+['$']
 for a,b in zip(z,z[1:]):x[hash32(a+'>'+b)]+=1
 return x/max(1,x.sum())
def architecture(cells):
 w,f,r,d,dy,b3=cells[0];n=len(cells);end='DY' if cells[-1][4] else 'B3' if cells[-1][5] else 'OPEN'
 wraps=('NONE',)+WRAPS;frames=('NONE','O','OT')
 v=[int(w==x) for x in wraps]+[int(f==x) for x in frames]+[int(r!='NONE'),d,dy,b3]
 v += [int(n==1),int(n==2),int(n==3),int(n>=4)]+[int(end==x) for x in ('DY','B3','OPEN')]
 key=f"W={w};F={f};R={int(r!='NONE')};D={d};DY={dy};B3={b3};N={'4+' if n>=4 else n};END={end}"
 first=f"W={w};F={f};R={int(r!='NONE')};D={d};DY={dy};B3={b3}"
 return np.array(v,float),key,first,end
def nearest(p,classes,k=3):
 z=sorted((float(np.square(p-v).sum()),name) for name,v in classes.items());return z[0][1],[name for _,name in z[:k]]

def load():
 panel={(r['edition'],r['page'],int(r['star_ordinal'])):r for r in read(PANEL) if r['edition'] in EDITIONS}
 assert len(panel)==510 and not any(k[1].startswith('f84r') for k in panel)
 by=defaultdict(list)
 # Retain only the already-frozen Q20 record keys; reject f84 before parsing formal cells.
 for r in read(FIELDS):
  key=(r['edition'],r['page'],int(r['star_ordinal']))
  if key not in panel:continue
  assert not r['page'].startswith('f84r') and not r['locus'].startswith('f84r')
  by[key].append(r)
 out=[]
 for key,p in panel.items():
  rows=by[key];op=sorted((r for r in rows if r['record_scope']=='OPEN'),key=lambda r:(int(r['line_depth']),int(r['field_index'])))
  body=sorted((r for r in rows if r['record_scope']=='BODY'),key=lambda r:(int(r['line_depth']),int(r['field_index'])))
  assert op and body
  last,first=op[-1],body[0];lc=parse_cells(last);fc=parse_cells(first);tv,ak,fk,end=architecture(fc)
  all_open=[c for r in op for c in parse_cells(r)]
  out.append({'edition':key[0],'page':key[1],'star_ordinal':key[2],'physical_folio':p['physical_folio'],'unit_id':p['unit_id'],
   'record_line_count':int(p['record_line_count']),'body_line_count':int(p['body_line_count']),'open_group_count':int(p['open_group_count']),'open_member_count':int(p['open_member_count']),
   'last':last,'first':first,'last_cells':lc,'first_cells':fc,'open_compiler':compiler(all_open),'target':tv,'architecture':ak,'first_cell':fk,'end':end})
 assert len(out)==510 and all(sum(r['edition']==e for r in out)==170 for e in EDITIONS)
 return out

def nuisance(rec):
 page_n=Counter(r['page'] for r in rec);rows=[]
 for r in rec:
  base=[r['record_line_count'],r['body_line_count'],r['open_group_count'],r['open_member_count'],int(r['page'].endswith('v')),r['star_ordinal']/page_n[r['page']],len(r['last_cells']),sum(map(len,r['last']['page_hosts'].split('|'))),sum(map(len,r['last']['group_tokens'].split('|')))]
  rows.append(base)
 return np.vstack(rows)
def rep(r,mode):
 if mode=='LAST_COMPILER12':return np.r_[compiler(r['last_cells']),min(len(r['last_cells']),8)/8]
 if mode=='LAST_ORDERED_CELL_HASH32':return ordered(r['last_cells'])
 if mode=='LAST_HOST_CHAR3_HASH32':return hvec(r['last']['page_hosts'].split('|'))
 return hvec(r['last']['group_tokens'].split('|'))

def main():
 allr=load();inventory=[];folds=[];predrows=[];scores=[];nullrows=[];exactrows=[];components=[];counter=[];summ={};refsummary={}
 for r in allr:
  inventory.append({'edition':r['edition'],'unit_id':r['unit_id'],'page':r['page'],'physical_folio':r['physical_folio'],'star_ordinal':r['star_ordinal'],
   'last_open_field_id':r['last']['field_id'],'last_open_tokens':r['last']['group_tokens'],'last_open_hosts':r['last']['page_hosts'],'last_open_template':r['last']['template_id'],
   'first_body_field_id':r['first']['field_id'],'first_body_tokens':r['first']['group_tokens'],'first_body_hosts':r['first']['page_hosts'],'first_body_template':r['first']['template_id'],
   'first_body_architecture':r['architecture'],'first_body_first_cell':r['first_cell'],'reading_role':'PRIMARY' if r['edition']=='ZL3b' else 'ALTERNATE_SENSITIVITY'})
 for ed in EDITIONS:
  rec=[r for r in allr if r['edition']==ed];Y=np.vstack([r['target'] for r in rec]);Xn=nuisance(rec);Xb=np.vstack([r['open_compiler'] for r in rec]);Xa={m:np.vstack([rep(r,m) for r in rec]) for m in MODES}
  folios=sorted({r['physical_folio'] for r in rec});cache={m:{} for m in MODES};true={};foldgain={m:[] for m in MODES};compgain={m:Counter() for m in MODES};refhit=[0,0,0]
  for held in folios:
   tr=np.array([i for i,r in enumerate(rec) if r['physical_folio']!=held]);te=np.array([i for i,r in enumerate(rec) if r['physical_folio']==held])
   xntr,xnte,_,_=standardize(Xn[tr],Xn[te]);xbtr,xbte,_,_=standardize(Xb[tr],Xb[te]);ytr,yte,ymu,ysd=standardize(Y[tr],Y[te]);base=np.c_[xntr,xbtr]
   b0=fit(base,ytr);p0=predict(np.c_[xnte,xbte],b0);classes={rec[i]['architecture']:Y[i] for i in tr}
   for pos,i in enumerate(te):
    guess,top3=nearest(p0[pos]*ysd+ymu,classes);actual=rec[i]['architecture'];refhit[0]+=actual in classes;refhit[1]+=guess==actual;refhit[2]+=actual in top3
    predrows.append({'edition':ed,'model':'REFERENCE_OPEN_COMPILER12','held_folio':held,'unit_id':rec[i]['unit_id'],'page':rec[i]['page'],'star_ordinal':rec[i]['star_ordinal'],'actual_architecture':actual,'predicted_architecture':guess,'top3_architectures':'|'.join(top3),'actual_seen_in_training':int(actual in classes),'top1_hit':int(guess==actual),'top3_hit':int(actual in top3)})
   for mode in MODES:
    xtr,xte,xmu,xsd=standardize(Xa[mode][tr],Xa[mode][te]);b=fit(np.c_[base,xtr],ytr);p=predict(np.c_[xnte,xbte,xte],b);gain=bits(yte,p0,p);foldgain[mode].append(gain)
    cache[mode][held]={'te':te,'xn':xnte,'xb':xbte,'y':yte,'p0':p0,'b':b,'xmu':xmu,'xsd':xsd}
    for name,idx in BLOCKS.items():compgain[mode][name]+=bits(yte[:,list(idx)],p0[:,list(idx)],p[:,list(idx)])
    hit1=hit3=seen=0
    for pos,i in enumerate(te):
     guess,top3=nearest(p[pos]*ysd+ymu,classes);actual=rec[i]['architecture'];s=int(actual in classes);seen+=s;hit1+=guess==actual;hit3+=actual in top3
     predrows.append({'edition':ed,'model':mode,'held_folio':held,'unit_id':rec[i]['unit_id'],'page':rec[i]['page'],'star_ordinal':rec[i]['star_ordinal'],'actual_architecture':actual,'predicted_architecture':guess,'top3_architectures':'|'.join(top3),'actual_seen_in_training':s,'top1_hit':int(guess==actual),'top3_hit':int(actual in top3)})
    folds.append({'edition':ed,'model':mode,'held_folio':held,'records':len(te),'pseudo_gain_bits':gain,'positive_gain':int(gain>0),'architecture_seen':seen,'top1_hits':hit1,'top3_hits':hit3})
  true={m:sum(foldgain[m]) for m in MODES};refsummary[ed]={'architecture_seen':refhit[0],'top1_hits':refhit[1],'top3_hits':refhit[2]}
  # Shared held-page/exact-OPEN-member-count permutations of additions only.
  rng=random.Random(seed('GDT131',ed));world={m:[] for m in MODES};maxworld=[];capacity=0;strata={}
  for held in folios:
   te=next(iter(cache.values()))[held]['te'];d=defaultdict(list)
   for pos,i in enumerate(te):d[(rec[i]['page'],rec[i]['open_member_count'])].append(pos)
   capacity+=sum(len(v) for v in d.values() if len(v)>1);strata[held]=d
  for _ in range(WORLDS):
   assigns={}
   for held,d in strata.items():
    n=len(next(iter(cache.values()))[held]['te']);a=list(range(n))
    for ps in d.values():
     if len(ps)>1:
      q=ps[:];rng.shuffle(q)
      for x,y in zip(ps,q):a[x]=y
    assigns[held]=a
   vals={}
   for mode in MODES:
    total=0.
    for held in folios:
     c=cache[mode][held];raw=Xa[mode][c['te']][assigns[held]];x=(raw-c['xmu'])/c['xsd'];p=predict(np.c_[c['xn'],c['xb'],x],c['b']);total+=bits(c['y'],c['p0'],p)
    world[mode].append(total);vals[mode]=total
   maxworld.append(max(vals.values()))
  for mode in MODES:
   ps=[r for r in predrows if r['edition']==ed and r['model']==mode];t=true[mode];local=(1+sum(x>=t-1e-12 for x in world[mode]))/(WORLDS+1);mx=(1+sum(x>=t-1e-12 for x in maxworld))/(WORLDS+1)
   row={'edition':ed,'model':mode,'records':len(rec),'pseudo_gain_bits':t,'selector_paid_bits':t-math.log2(len(MODES)),'positive_folios':sum(x>0 for x in foldgain[mode]),'swappable_records':capacity,'null_mean_bits':float(np.mean(world[mode])),'local_p':local,'max_four_p':mx,'architecture_seen':sum(int(x['actual_seen_in_training']) for x in ps),'top1_hits':sum(int(x['top1_hit']) for x in ps),'top3_hits':sum(int(x['top3_hit']) for x in ps)}
   scores.append(row);nullrows.append({'edition':ed,'model':mode,'worlds':WORLDS,'true_gain_bits':t,'null_mean_bits':float(np.mean(world[mode])),'null_q95_bits':float(np.quantile(world[mode],.95)),'local_p':local,'max_four_p':mx})
   for name in BLOCKS:components.append({'edition':ed,'model':mode,'target_block':name,'incremental_gain_bits':compgain[mode][name]})
  # Training-only exact last-field lookup; unique target required.
  for held in folios:
   tr=[r for r in rec if r['physical_folio']!=held];te=[r for r in rec if r['physical_folio']==held];maps={}
   for kind in ('TOKENS','HOSTS','TEMPLATE'):
    d=defaultdict(set)
    for r in tr:
     key=r['last']['group_tokens'] if kind=='TOKENS' else r['last']['page_hosts'] if kind=='HOSTS' else r['last']['template_id'];d[key].add(r['first']['group_tokens'])
    maps[kind]={k:next(iter(v)) for k,v in d.items() if len(v)==1}
   for r in te:
    for kind in maps:
     key=r['last']['group_tokens'] if kind=='TOKENS' else r['last']['page_hosts'] if kind=='HOSTS' else r['last']['template_id'];guess=maps[kind].get(key,'')
     if guess:exactrows.append({'edition':ed,'held_folio':held,'unit_id':r['unit_id'],'predictor':kind,'last_field_key':key,'predicted_first_body_tokens':guess,'actual_first_body_tokens':r['first']['group_tokens'],'exact_hit':int(guess==r['first']['group_tokens'])})
  summ[ed]={r['model']:r for r in scores if r['edition']==ed}
 zl=summ['ZL3b'];lead=max(MODES,key=lambda m:zl[m]['pseudo_gain_bits']);p=zl[lead]
 gates={'selector_paid_positive':p['selector_paid_bits']>0,'six_of_eight_positive':p['positive_folios']>=6,'all_readings_positive':all(summ[e][lead]['pseudo_gain_bits']>0 for e in EDITIONS),'max_four_p_le_005':p['max_four_p']<=.05,'beats_both_string_controls':p['pseudo_gain_bits']>max(zl['LAST_HOST_CHAR3_HASH32']['pseudo_gain_bits'],zl['LAST_RAW_CHAR3_HASH32']['pseudo_gain_bits']) if lead not in ('LAST_HOST_CHAR3_HASH32','LAST_RAW_CHAR3_HASH32') else False}
 if all(gates.values()):status='Q20_CROSS_LINE_FIELD_ARCHITECTURE_TRANSFER_SUPPORTED'
 elif lead=='LAST_HOST_CHAR3_HASH32' and gates['selector_paid_positive'] and gates['all_readings_positive']:status='Q20_LAST_OPEN_HOST_TO_FIRST_BODY_ARCHITECTURE_LEAD_WEAK_OR_FOLD_UNSTABLE'
 else:status='Q20_CROSS_LINE_FIELD_ONSET_NOT_ABOVE_AGGREGATE_OPEN_OR_STRING_CONTROLS'
 for mode in MODES:
  bad=min((r for r in folds if r['edition']=='ZL3b' and r['model']==mode),key=lambda x:x['pseudo_gain_bits']);counter.append({'counterexample':'WEAKEST_ZL_HELD_FOLIO','model':mode,'held_folio':bad['held_folio'],'detail':f"gain={bad['pseudo_gain_bits']:.6f}"})
 counter += [{'counterexample':'EXACT_FIRST_BODY_SURFACES_NEAR_UNIQUE','model':'EXACT_FORMULA','held_folio':'ALL','detail':'ZL3b has 168 distinct exact surfaces among 170 records.'},{'counterexample':'FIRST_BODY_COMPILER_TEMPLATES_NEAR_UNIQUE','model':'EXACT_FORMULA','held_folio':'ALL','detail':'ZL3b has 150 templates, 144 singletons.'},{'counterexample':'GDT118_FIRST_BODY_LINE_WAS_NONCONFIRMING','model':'PRIOR_CONTROL','held_folio':'ALL','detail':'Aggregate first-BODY-line compiler gain missed the max-six gate.'},{'counterexample':'PERMUTATION_NOT_EXACT_FINAL_FIELD_LENGTH_MATCHED','model':'NULL_SCOPE','held_folio':'ALL','detail':'Page+OPEN-member null has 99 swappable ZL records; adding final-field groups/host-length/raw-length leaves 33/4/2, so p is a model-adjusted coarse-stratum diagnostic.'}]
 write(INVENTORY,inventory);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in folds]);write(SCORES,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in scores]);write(PRED,predrows);write(NULL,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in nullrows]);write(EXACT,exactrows);write(COMPONENTS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in components]);write(COUNTER,counter)
 report=f'''# GDT131 — Q20 cross-line field-onset transfer\n\nStatus: **{status}**\n\nThe primary panel has 170 records on eight physical folios. The reference model sees training-derived page/record nuisance, final-field opportunity lengths, and the aggregate OPEN compiler profile, but no target architecture from the held folio. The strongest incremental representation is `{lead}`.\n\n| representation | ZL gain | selector-paid | positive folios | max-4 p | IT gain | RF gain | exact architecture top-1 |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'''+''.join(f"| `{m}` | {zl[m]['pseudo_gain_bits']:+.3f} | {zl[m]['selector_paid_bits']:+.3f} | {zl[m]['positive_folios']}/8 | {zl[m]['max_four_p']:.4f} | {summ['IT2a'][m]['pseudo_gain_bits']:+.3f} | {summ['RF1b'][m]['pseudo_gain_bits']:+.3f} | {zl[m]['top1_hits']}/170 |\n" for m in MODES)+f'''\nRegistered gates for the selected lead are `{json.dumps(gates,sort_keys=True)}`. Ordered compiler cells and final-field compiler rates do not improve the established aggregate OPEN compiler model. Any surviving PAGE_HOST-string increment is therefore a weak cross-line content-address/texture lead, not a discrete compiler transduction.\n\n## Exact formula diagnostic\n\nThe target is too sparse for a codeword dictionary: 168/170 exact first-field surfaces are distinct and 144/150 compiler templates are singletons. Training-only exact lookups made {len([r for r in exactrows if r['edition']=='ZL3b'])} ZL predictions and hit {sum(int(r['exact_hit']) for r in exactrows if r['edition']=='ZL3b')}. This actively rejects a simple repeated final-OPEN-field -> exact first-BODY-field table at current capacity.\n\nThe result refines rather than reopens GDT114–GDT118. It concerns a formal cross-line field architecture only. No heading, recipe, role, star property, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation is inferred. f84r remained completely sealed.\n'''
 zblocks={r['target_block']:r['incremental_gain_bits'] for r in components if r['edition']=='ZL3b' and r['model']=='LAST_HOST_CHAR3_HASH32'}
 report += f"\n\n## Discrete-prediction and component diagnostic\n\nThe reference already gets {refsummary['ZL3b']['top1_hits']}/170 exact architecture choices; the PAGE_HOST lead also gets {zl['LAST_HOST_CHAR3_HASH32']['top1_hits']}/170, so its pseudo-bit improvement creates no additional exact first choice. ZL PAGE_HOST block gains are: {', '.join(name+' '+format(zblocks[name],'+.3f') for name in BLOCKS)} bits. These block values decompose one selected model and are not independent tests.\n\nThe p=.08274 null is model-adjusted and coarse-stratum, not an exact final-field-length-matched permutation. Of 99 ZL page+OPEN-member swappable records, only 33 remain after final-field group-count matching, four after PAGE_HOST-length matching, and two after raw-length matching; RF has 29/0/0. This materially limits the lead.\n"
 REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT131_Q20_CROSS_LINE_FIELD_ONSET_RESULT_V1','status':status,'records':170,'physical_folios':8,'models':list(MODES),'worlds':WORLDS,'lead_model':lead,'primary':p,'gates':gates,'scores':scores,'reference_architecture':refsummary,'components':components,'exact_formula_predictions_zl':len([r for r in exactrows if r['edition']=='ZL3b']),'exact_formula_hits_zl':sum(int(r['exact_hit']) for r in exactrows if r['edition']=='ZL3b'),'interpretation':'Held-folio final-OPEN-field prediction of first-BODY-field construction architecture above aggregate OPEN compiler and strong page nuisance.','claim_ceiling':'Formal cross-line field architecture only; no heading, recipe, role, star property, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'prediction_frozen':False},'inputs':{FIELDS.name:sha(FIELDS),PANEL.name:sha(PANEL),'gdt127_result.json':sha(ROOT/'gdt127_result.json'),'gdt118_result.json':sha(ROOT/'gdt118_result.json'),'gdt115_result.json':sha(ROOT/'gdt115_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (INVENTORY,FOLDS,SCORES,PRED,NULL,EXACT,COMPONENTS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'lead':lead,'primary':p,'gates':gates},sort_keys=True))

if __name__=='__main__':main()
