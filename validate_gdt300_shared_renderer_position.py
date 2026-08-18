#!/usr/bin/env python3
"""Independent reconstruction of GDT300 retained scores and nulls."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;Y=('FIRST','MIDDLE','LAST');checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def canon(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def close(a,b,t=2e-10):return abs(float(a)-float(b))<=t
def out(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def lay(x):return x['section'],x['currier'],x['hand'],x['group_count']
def rend(x,F):return tuple(x[k] for k in F)
def elig(rows,p):
 base=[x for x in rows if x['control_id']==p and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in base if len(hf[x['page_host']])>1 and len(sf[x['source_surface_sha256']])>1]
def smooth(c,b,k):
 n=sum(c.values());return {z:(c[z]+k*b[z])/(n+k) for z in Y}
def calc(E,RR,F,k):
 N=F+['renderer_tuple'];G=Counter();L=defaultdict(Counter);H=defaultdict(Counter);C={n:defaultdict(Counter) for n in N};P=defaultdict(Counter);FG=defaultdict(Counter);FL=defaultdict(lambda:defaultdict(Counter));FH=defaultdict(lambda:defaultdict(Counter));FC={n:defaultdict(lambda:defaultdict(Counter)) for n in N};FP=defaultdict(lambda:defaultdict(Counter));FN=Counter()
 for x,r in zip(E,RR):
  y=out(x);f=x['physical_folio'];G[y]+=1;L[lay(x)][y]+=1;H[x['page_host']][y]+=1;P[(x['page_host'],r)][y]+=1;FG[f][y]+=1;FL[f][lay(x)][y]+=1;FH[f][x['page_host']][y]+=1;FP[f][(x['page_host'],r)][y]+=1;FN[f]+=1
  for i,n in enumerate(F):C[n][r[i]][y]+=1;FC[n][f][r[i]][y]+=1
  C['renderer_tuple'][r][y]+=1;FC['renderer_tuple'][f][r][y]+=1
 B=Counter();T=Counter();fold=defaultdict(Counter)
 for x,r in zip(E,RR):
  y=out(x);f=x['physical_folio'];ng=len(E)-FN[f];g={z:G[z]-FG[f][z] for z in Y};p0={z:(g[z]+.5)/(ng+1.5) for z in Y};a={z:L[lay(x)][z]-FL[f][lay(x)][z] for z in Y};pl=smooth(a,p0,k);a={z:H[x['page_host']][z]-FH[f][x['page_host']][z] for z in Y};ph=smooth(a,pl,k);Q={'HOST':ph}
  for i,n in enumerate(F):
   a={z:C[n][r[i]][z]-FC[n][f][r[i]][z] for z in Y};pc=smooth(a,pl,k);u={z:ph[z]*pc[z]/pl[z] for z in Y};s=sum(u.values());Q['SHARED_'+n]={z:u[z]/s for z in Y}
  a={z:C['renderer_tuple'][r][z]-FC['renderer_tuple'][f][r][z] for z in Y};pc=smooth(a,pl,k);u={z:ph[z]*pc[z]/pl[z] for z in Y};s=sum(u.values());Q['SHARED_renderer_tuple']={z:u[z]/s for z in Y};a={z:P[(x['page_host'],r)][z]-FP[f][(x['page_host'],r)][z] for z in Y};Q['HOST_X_RENDERER']=smooth(a,ph,k)
  for n,p in Q.items():B[n]+=-math.log2(p[y]);fold[f][n]+=-math.log2(p[y]);w=max(Y,key=lambda z:(p[z],-Y.index(z)));T[n]+=w==y;fold[f][n+'_TOP1']+=w==y
 return B,T,fold
def shuffle(E,RR,w,seed):
 q=defaultdict(list)
 for i,x in enumerate(E):q[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(i)
 z=list(RR)
 for key,ix in sorted(q.items(),key=lambda a:str(a[0])):
  vals=[RR[i] for i in ix];s=int(hashlib.sha256((seed+'|'+str(w)+'|'+json.dumps(key)).encode()).hexdigest()[:16],16);random.Random(s).shuffle(vals)
  for i,v in zip(ix,vals):z[i]=v
 return z
d=json.loads((R/'gdt300_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('design_content',d['content_sha256']==canon(q));r=json.loads((R/'gdt300_result.json').read_text());q=dict(r);q.pop('content_sha256');ck('result_content',r['content_sha256']==canon(q));
for group in ('inputs','documents','implementation','outputs'):
 for n,h in r[group].items():ck(group+'_'+n,sha(R/n)==h)
rows=read(R/'gdt278_native_event_inventory.tsv');ck('f84_source',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));F=d['renderer_fields'];caps={x['control_id']:x for x in read(R/'gdt300_capacity.tsv')};Ps={p:elig(rows,p) for p in sorted(caps)};storedp={x['control_id']:x for x in read(R/'gdt300_panel_scores.tsv')};storedc={(x['control_id'],x['component']):x for x in read(R/'gdt300_component_scores.tsv')};storedf={(x['control_id'],x['held_folio']):x for x in read(R/'gdt300_folio_scores.tsv')};obs={}
for p,E in Ps.items():
 if caps[p]['score_capacity']!='POWERED':continue
 RR=[rend(x,F) for x in E];B,T,fold=calc(E,RR,F,d['prior_mass']);obs[p]=(B,T,fold);n=len(E);sp=storedp[p];sg=(B['HOST']-B['SHARED_renderer_tuple'])/n;eg=(B['HOST']-B['HOST_X_RENDERER'])/n;ck('panel_n_'+p,int(sp['events'])==n);ck('panel_sg_'+p,close(sp['shared_gain_bits_per_event'],sg));ck('panel_eg_'+p,close(sp['exact_pair_gain_bits_per_event'],eg));ck('panel_top_'+p,close(sp['shared_top1'],T['SHARED_renderer_tuple']/n));ck('panel_pos_'+p,int(sp['positive_shared_folios'])==sum(v['HOST']-v['SHARED_renderer_tuple']>0 for v in fold.values()))
 for nme in F+['renderer_tuple']:
  sc=storedc[(p,nme)];ck('component_'+p+'_'+nme,close(sc['gain_vs_host_bits_per_event'],(B['HOST']-B['SHARED_'+nme])/n))
 for f,v in fold.items():
  sf=storedf[(p,f)];ck('fold_s_'+p+'_'+f,close(sf['shared_gain_bits'],v['HOST']-v['SHARED_renderer_tuple']));ck('fold_e_'+p+'_'+f,close(sf['exact_pair_gain_bits'],v['HOST']-v['HOST_X_RENDERER']))
null={(x['control_id'],x['component'],int(x['world_index'])):x for x in read(R/'gdt300_null_results.tsv')};NV=defaultdict(list)
for p in sorted(obs):
 if caps[p]['null_capacity']!='VARIABLE':continue
 E=Ps[p];RR=[rend(x,F) for x in E]
 for w in range(d['null_worlds']):
  zz=shuffle(E,RR,w,d['null_seed']+'|'+p);B,T,fold=calc(E,zz,F,d['prior_mass'])
  for nme in F+['renderer_tuple']:
   g=(B['HOST']-B['SHARED_'+nme])/len(E);NV[(p,nme)].append(g);ck('null_'+p+'_'+nme+'_'+str(w),close(null[(p,nme,w)]['gain_vs_host_bits_per_event'],g))
means={k:statistics.mean(v) for k,v in NV.items()};sds={k:statistics.pstdev(v) for k,v in NV.items()};zs={}
for k,v in NV.items():
 o=float(storedc[k]['gain_vs_host_bits_per_event']);ck('nullmean_'+str(k),close(storedc[k]['null_mean'],means[k]));ck('nullsd_'+str(k),close(storedc[k]['null_sd'],sds[k]));zs[k]=(o-means[k])/sds[k] if sds[k] else None
wm=[max((NV[k][w]-means[k])/sds[k] for k in zs if sds[k]) for w in range(d['null_worlds'])]
for k,z in zs.items():
 if z is not None:ck('maxp_'+str(k),close(storedc[k]['max_family_p'],(1+sum(x>=z-1e-15 for x in wm))/(1+d['null_worlds'])))
v=storedp['VOYNICH_REFERENCE'];vc=storedc[('VOYNICH_REFERENCE','renderer_tuple')];sens=read(R/'gdt300_prior_sensitivity.tsv');g={'gdt299_exact_pair_reproduced':abs(float(v['exact_pair_gain_bits_per_event'])-float(json.loads((R/'gdt299_result.json').read_text())['voynich_summary']['whole_form_gain_vs_host_bits_per_event']))<=d['decision']['gdt299_reproduction_tolerance_bits_per_event'],'shared_gain_positive':float(v['shared_gain_bits_per_event'])>0,'minimum_positive_folios':int(v['positive_shared_folios'])>=60,'both_prior_sensitivities_positive':all(float(x['shared_gain_bits_per_event'])>0 for x in sens),'max_seven_p_le_0_05':float(vc['max_family_p'])<=.05,'shared_fraction_at_least_half':float(v['shared_fraction_of_exact_pair_gain'])>=.5};ck('gates',g==r['gates']);status=d['decision']['support'] if all(g.values()) else d['decision']['host_specific'] if g['gdt299_exact_pair_reproduced'] and float(v['exact_pair_gain_bits_per_event'])>0 else d['decision']['reproduction_fail'];ck('status',status==r['status']);ck('report',status in (R/'GDT300_SHARED_RENDERER_POSITIONAL_GRAMMAR_REPORT.md').read_text());val={'schema':'GDT300_VALIDATION_V1','status':'PASS','checks':len(checks),'result_sha256':sha(R/'gdt300_result.json'),'result_content_sha256':r['content_sha256'],'scope':'INDEPENDENT_SOURCE_SCORE_FOLD_NULL_DECISION_HASH_RECONSTRUCTION'};(R/'gdt300_validation.json').write_text(json.dumps(val,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
