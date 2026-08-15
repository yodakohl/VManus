#!/usr/bin/env python3
"""GDT123: sparse exact-PAGE_HOST atlas on archived Q20 visual states."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g
import run_gdt119_q20_visual_compiler_association as v
ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT123_Q20_PAGE_HOST_CODEWORD_ATLAS_METHOD.md';REPORT=ROOT/'GDT123_Q20_PAGE_HOST_CODEWORD_ATLAS_REPORT.md';INV=ROOT/'gdt123_q20_page_host_codeword_inventory.tsv';ATLAS=ROOT/'gdt123_q20_page_host_codeword_atlas.tsv';NULL=ROOT/'gdt123_q20_page_host_codeword_null.tsv';COUNTER=ROOT/'gdt123_q20_page_host_codeword_counterexamples.tsv';RESULT=ROOT/'gdt123_result.json';SCOPES=('OPEN','BODY','OPEN_BODY');WORLDS=4096
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def hosts(r,scope):
 z=r['open'] if scope=='OPEN' else r['body'] if scope=='BODY' else r['open']+r['body']
 return {q['page_host'] for q in z if q['page_host']}
def design(rec,ids):
 pages=sorted({rec[i]['page'] for i in ids});pc=Counter(rec[i]['page'] for i in ids);z=[]
 for i in ids:
  r=rec[i];z.append([1.,r['star_ordinal']%2,r['star_ordinal']/pc[r['page']],pc[r['page']],float(r['page'].endswith('v')),r['record_line_count'],r['open_group_count'],r['open_member_count'],r['body_group_count'],r['body_member_count']]+[float(r['page']==p) for p in pages[1:]])
 return np.asarray(z,float)
def resid(A,Z):return A-Z@np.linalg.pinv(Z)@A
def effects(X,y,Z):
 xr=resid(X,Z);yr=resid(y,Z);num=xr.T@yr;den=np.sqrt((xr*xr).sum(0)*float(yr@yr));return np.divide(num,den,out=np.zeros_like(num),where=den>1e-15)
def main():
 allr=g.load_records();bind={r['unit_id']:r for r in read(v.BIND)};src={(r['page'],r['star_ordinal']):r for r in read(v.SOURCE)};assert len(bind)==156 and not any(r['page'].startswith('f84r') for r in bind.values());joined={}
 for uid,b in bind.items():
  s=src[b['page'],b['star_ordinal']];assert s['locus']==b['locus'];joined[uid]={**b,'color':s['color'],'provenance':'EXISTING_HUMAN_ANNOTATION_STOLFI_STAR_PROPS'}
 recs={ed:[r for r in allr if r['edition']==ed and r['unit_id'] in joined] for ed in g.EDITIONS};assert all(len(x)==156 for x in recs.values());zl=recs['ZL3b'];byuid={ed:{r['unit_id']:r for r in recs[ed]} for ed in g.EDITIONS};uids=[r['unit_id'] for r in zl];assert all([r['unit_id'] for r in recs[e]]==uids for e in g.EDITIONS)
 # ZL-only, target-blind support library.
 feats=[]
 for scope in SCOPES:
  support=defaultdict(list);folios=defaultdict(set)
  for i,r in enumerate(zl):
   for h in hosts(r,scope):support[h].append(i);folios[h].add(r['physical_folio'])
  for h in sorted(support):
   if len(support[h])>=5 and len(folios[h])>=2:feats.append((scope,h))
 Xed={}
 for ed in g.EDITIONS:
  rr=recs[ed];Xed[ed]=np.asarray([[float(h in hosts(r,scope)) for scope,h in feats] for r in rr],float)
 inv=[]
 for j,(scope,h) in enumerate(feats):
  masks={e:{uids[i] for i,x in enumerate(Xed[e][:,j]) if x} for e in g.EDITIONS};inter=len(masks['ZL3b']&masks['IT2a']&masks['RF1b']);union=len(masks['ZL3b']|masks['IT2a']|masks['RF1b'])
  inv.append({'feature_index':j,'scope':scope,'page_host':h,'zl_records':len(masks['ZL3b']),'zl_folios':len({zl[i]['physical_folio'] for i,x in enumerate(Xed['ZL3b'][:,j]) if x}),'it_records':len(masks['IT2a']),'rf_records':len(masks['RF1b']),'all_reading_mask_jaccard':inter/union if union else 1.,'feature_id':hashlib.sha256(f'{scope}|{h}'.encode()).hexdigest()[:16],'claim_state':'EXACT_PAGE_HOST_CANDIDATE_UNASSIGNED'})
 real=[];keymeta=[];ed_effect={}
 for ed in g.EDITIONS:
  rr=recs[ed];X=Xed[ed]
  for axis in v.AXES:
   ids=[i for i,r in enumerate(rr) if v.yval(joined[r['unit_id']],axis) is not None];y=np.array([v.yval(joined[rr[i]['unit_id']],axis) for i in ids],float);Z=design(rr,ids);eff=effects(X[ids],y,Z);ed_effect[ed,axis]=eff
   if ed=='ZL3b':
    for j,e in enumerate(eff):real.append(abs(float(e)));keymeta.append((axis,j,float(e),len(ids)))
 # Shared whole-profile null over the complete postselection library.
 strata=defaultdict(list)
 for i,r in enumerate(zl):strata[r['page'],r['open_member_count']].append(i)
 capacity=sum(len(q) for q in strata.values() if len(q)>1);rng=random.Random(g.seed('GDT123_NULL'));null=np.zeros((WORLDS,len(real)));maxout=[]
 axis_cache={}
 for axis in v.AXES:
  ids=[i for i,r in enumerate(zl) if v.yval(joined[r['unit_id']],axis) is not None];axis_cache[axis]=(ids,np.array([v.yval(joined[zl[i]['unit_id']],axis) for i in ids],float),design(zl,ids))
 for w in range(WORLDS):
  a=list(range(len(zl)))
  for ps in strata.values():
   if len(ps)>1:
    q=ps[:];rng.shuffle(q)
    for x,y in zip(ps,q):a[x]=y
  vals=[]
  for axis in v.AXES:
   ids,y,Z=axis_cache[axis];vals.extend(abs(effects(Xed['ZL3b'][a][ids],y,Z)))
  null[w]=vals;maxout.append(float(np.max(vals)))
 atlas=[];selector=math.log2(2*len(real));counter=[]
 for q,(axis,j,signed,nrows) in enumerate(keymeta):
  scope,h=feats[j];obs=abs(signed);local=(1+int(np.sum(null[:,q]>=obs-1e-12)))/(WORLDS+1);maxt=(1+sum(x>=obs-1e-12 for x in maxout))/(WORLDS+1);gain=-.5*nrows*math.log2(max(1e-12,1-signed*signed));lo=[]
  for held in sorted({r['physical_folio'] for r in zl}):
   ids,y,Z=axis_cache[axis];keep=[p for p,i in enumerate(ids) if zl[i]['physical_folio']!=held];lo.append(float(effects(Xed['ZL3b'][ids][keep,j,None],y[keep],Z[keep])[0]))
  same=sum((x>0)==(signed>0) for x in lo);ite=float(ed_effect['IT2a',axis][j]);rfe=float(ed_effect['RF1b',axis][j]);allread=(ite>0)==(signed>0) and (rfe>0)==(signed>0)
  if maxt<=.1 and gain-selector>0 and same>=5 and allread:label='INTERESTING_EXPLORATORY'
  elif local<=.1 and same>=5:label='WEAK'
  elif same<=3:label='LIKELY_PAGE_CONFOUND'
  elif not allread:label='UNSTABLE'
  else:label='NO_SIGNAL'
  row={'candidate_id':hashlib.sha256(f'{axis}|{scope}|{h}'.encode()).hexdigest()[:16],'axis':axis,'scope':scope,'page_host':h,'records_with_host':int(Xed['ZL3b'][:,j].sum()),'folios_with_host':inv[j]['zl_folios'],'effect_signed':signed,'effect_abs':obs,'gaussian_gain_bits':gain,'selector_cost_bits':selector,'selector_paid_gain_bits':gain-selector,'local_p':local,'max_library_p':maxt,'same_direction_leave_one_folio':same,'leave_one_folio_effects':'|'.join(f'{x:.6f}' for x in lo),'it_effect':ite,'rf_effect':rfe,'all_readings_same_direction':int(allread),'reading_mask_jaccard':inv[j]['all_reading_mask_jaccard'],'label':label,'claim_state':'EXPLORATORY_EXACT_HOST_ASSOCIATION_NO_MEANING'};atlas.append(row)
 atlas.sort(key=lambda x:(float(x['max_library_p']),-float(x['effect_abs']),x['candidate_id']));top=atlas[0];interesting=[x for x in atlas if x['label']=='INTERESTING_EXPLORATORY']
 for row in atlas:
  if row['local_p']<=.1 and row['label']!='INTERESTING_EXPLORATORY':counter.append({'candidate_id':row['candidate_id'],'axis':row['axis'],'scope':row['scope'],'page_host':row['page_host'],'local_p':row['local_p'],'max_library_p':row['max_library_p'],'leave_one_folio_direction':row['same_direction_leave_one_folio'],'all_readings_same_direction':row['all_readings_same_direction'],'counterexample':'LOCALLY_ATTRACTIVE_BUT_FAILS_GLOBAL_STABILITY_OR_SELECTOR'})
 write(INV,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in inv]);write(ATLAS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in atlas]);write(NULL,[{'world':i,'max_abs_partial_correlation':f'{x:.12f}'} for i,x in enumerate(maxout)]);write(COUNTER,counter or [{'candidate_id':'NONE','counterexample':'NO_LOCAL_ATTRACTION'}])
 labels=Counter(x['label'] for x in atlas);status='Q20_EXACT_PAGE_HOST_VISUAL_CODEWORD_LEAD' if interesting else 'Q20_EXACT_PAGE_HOST_VISUAL_ATLAS_NO_GLOBAL_SURVIVOR'
 report=f'''# GDT123 — Q20 exact PAGE_HOST codeword atlas\n\nStatus: **{status}**\n\nThe target-blind ZL3b library contains {len(feats)} exact host/scope candidates and {len(real)} host/scope/visual-axis tests. Whole-profile permutations retain {capacity}/156 records in movable page+OPEN-length strata. The top candidate is `{top['scope']}:{top['page_host']}` on `{top['axis']}`: signed partial r={top['effect_signed']:+.3f}, {top['gaussian_gain_bits']:.3f} Gaussian bits, selector-paid {top['selector_paid_gain_bits']:+.3f}, local p={top['local_p']:.4f}, max-library p={top['max_library_p']:.4f}, leave-one-folio direction {top['same_direction_leave_one_folio']}/7, IT/RF effects {top['it_effect']:+.3f}/{top['rf_effect']:+.3f}. {len(interesting)} candidates receive `INTERESTING_EXPLORATORY`.\n\n| candidate | axis | support | effect | selector-paid | local p | max p | LOFO | IT/RF | label |\n|---|---|---:|---:|---:|---:|---:|---:|---|---|\n'''+''.join(f"| `{x['scope']}:{x['page_host']}` | `{x['axis']}` | {x['records_with_host']} | {x['effect_signed']:+.3f} | {x['selector_paid_gain_bits']:+.3f} | {x['local_p']:.4f} | {x['max_library_p']:.4f} | {x['same_direction_leave_one_folio']}/7 | {x['it_effect']:+.3f}/{x['rf_effect']:+.3f} | `{x['label']}` |\n" for x in atlas[:15])+f'''\nLabel counts: `{json.dumps(dict(labels),sort_keys=True)}`. These are postselected codeword hypotheses only. A host may correlate because of record order, page ecology, transcription, or co-occurring compiler structure despite the residual controls. The archived exact-host/global visual failures remain counterevidence. No host receives a star attribute, semantic role, word value, morpheme, POS, sound, language, plaintext, meaning, or translation. f84r remained absent and unpredicted.\n''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT123_Q20_PAGE_HOST_CODEWORD_ATLAS_RESULT_V1','status':status,'joined_units':156,'physical_folios':7,'features':len(feats),'tests':len(real),'worlds':WORLDS,'swappable_records':capacity,'top_candidate':top,'interesting_candidates':interesting,'label_counts':dict(labels),'interpretation':'Postselection-controlled exact PAGE_HOST presence atlas over archived Q20 star morphology.','claim_ceiling':'Sparse exact-host hypothesis generation only; no star/PAGE_HOST meaning, role, word, morpheme, POS, sound, language, plaintext or translation.','historical_controls':['GDT088_NO_GLOBAL_EXACT_HOST_SURVIVOR','SME_TARGET_FREE_CALIBRATION_FAILED','GDT119_GLOBAL_COMPILER_VISUAL_NEGATIVE','GDT122_GLOBAL_PAGE_HOST_VISUAL_NEGATIVE'],'f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'assigned':False,'predicted':False},'inputs':{'gdt122_result.json':sha(ROOT/'gdt122_result.json'),'gdt088_result.json':sha(ROOT/'gdt088_result.json'),str(v.BIND.relative_to(ROOT)):sha(v.BIND),str(v.SOURCE.relative_to(ROOT)):sha(v.SOURCE)},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{x.name:sha(x) for x in (INV,ATLAS,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'features':len(feats),'tests':len(real),'top':top,'interesting':len(interesting),'labels':dict(labels)},sort_keys=True))
if __name__=='__main__':main()
