#!/usr/bin/env python3
"""Independent reconstruction of GDT301 folds, nulls, and decision."""
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;Y=('FIRST','MIDDLE','LAST');META=('register','section','currier','hand');checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def close(a,b,t=2e-10):return abs(float(a)-float(b))<=t
def yy(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def key(x,a):return (x['section'],x['currier'],x['hand'],x['group_count']) if a=='physical_folio' else tuple(x[k] for k in META if k!=a)+(x['group_count'],)
def sm(c,b,k):
 n=sum(c.values());return {z:(c[z]+k*b[z])/(n+k) for z in Y}
def calc(E,S,A,k,fixed=False):
 G=Counter();L=defaultdict(Counter);H=defaultdict(Counter);W=defaultdict(Counter);FG=defaultdict(Counter);FL=defaultdict(lambda:defaultdict(Counter));FH=defaultdict(lambda:defaultdict(Counter));FW=defaultdict(lambda:defaultdict(Counter));FN=Counter();B=Counter();T=Counter();fold=defaultdict(Counter)
 for x,s in zip(E,S):
  z=yy(x);v=x[A];G[z]+=1;L[key(x,A)][z]+=1;H[x['page_host']][z]+=1;W[s][z]+=1;FG[v][z]+=1;FL[v][key(x,A)][z]+=1;FH[v][x['page_host']][z]+=1;FW[v][s][z]+=1;FN[v]+=1
 for x,s in zip(E,S):
  v=x[A]
  if not fixed and (sum(H[x['page_host']].values())-sum(FH[v][x['page_host']].values())<=0 or sum(W[s].values())-sum(FW[v][s].values())<=0):continue
  z=yy(x);n=len(E)-FN[v];g={q:G[q]-FG[v][q] for q in Y};p0={q:(g[q]+.5)/(n+1.5) for q in Y};a={q:L[key(x,A)][q]-FL[v][key(x,A)][q] for q in Y};pl=sm(a,p0,k);a={q:H[x['page_host']][q]-FH[v][x['page_host']][q] for q in Y};ph=sm(a,pl,k);a={q:W[s][q]-FW[v][s][q] for q in Y};pw=sm(a,ph,k)
  for name,p in [('LAYOUT',pl),('PAGE_HOST',ph),('WHOLE_FORM',pw)]:loss=-math.log2(p[z]);B[name]+=loss;fold[v][name]+=loss;pred=max(Y,key=lambda q:(p[q],-Y.index(q)));T[name]+=pred==z;fold[v][name+'_TOP1']+=pred==z
  fold[v]['events']+=1
 return {'events':sum(q['events'] for q in fold.values()),'bits':B,'top':T,'fold':fold}
def pop(E):
 hf=defaultdict(set);sf=defaultdict(set)
 for x in E:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in E if len(hf[x['page_host']])>1 and len(sf[x['source_surface_sha256']])>1]
def shuf(E,S,w,seed):
 q=defaultdict(list)
 for i,x in enumerate(E):q[(x['physical_folio'],x['register'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(i)
 out=list(S)
 for k,ix in sorted(q.items(),key=lambda z:str(z[0])):
  v=[S[i] for i in ix];h=int(hashlib.sha256((seed+'|'+str(w)+'|'+json.dumps(k)).encode()).hexdigest()[:16],16);random.Random(h).shuffle(v)
  for i,a in zip(ix,v):out[i]=a
 return out
d=json.loads((R/'gdt301_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('design_content',d['content_sha256']==can(q));r=json.loads((R/'gdt301_result.json').read_text());q=dict(r);q.pop('content_sha256');ck('result_content',r['content_sha256']==can(q));
for g in ('inputs','documents','implementation','outputs'):
 for n,h in r[g].items():ck(g+'_'+n,sha(R/n)==h)
rows=read(R/'gdt278_native_event_inventory.tsv');ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));caps={(x['control_id'],x['held_axis']):x for x in read(R/'gdt301_capacity.tsv')};pan={p:[x for x in rows if x['control_id']==p and int(x['group_count'])>=2] for p in sorted({x['control_id'] for x in rows})};SS={(x['control_id'],x['held_axis']):x for x in read(R/'gdt301_axis_scores.tsv')};FF={(x['control_id'],x['held_axis'],x['held_level']):x for x in read(R/'gdt301_held_level_scores.tsv')}
for (p,a),c in caps.items():
 if c['capacity']!='POWERED':continue
 E=pop(pan[p]) if a=='physical_folio' else pan[p];S=[x['source_surface_sha256'] for x in E];z=calc(E,S,a,d['prior_mass'],a=='physical_folio');st=SS[(p,a)];ck('n_'+p+a,z['events']==int(st['events']));ck('gain_'+p+a,close(st['whole_form_gain_bits_per_event'],(z['bits']['PAGE_HOST']-z['bits']['WHOLE_FORM'])/z['events']));ck('top_'+p+a,close(st['whole_form_top1'],z['top']['WHOLE_FORM']/z['events']))
 for v,f in z['fold'].items():q=FF[(p,a,v)];ck('fold_'+p+a+v,close(q['gain_bits'],f['PAGE_HOST']-f['WHOLE_FORM']))
NN={(x['control_id'],x['held_axis'],int(x['world_index'])):x for x in read(R/'gdt301_null_results.tsv')};NV=defaultdict(list);E0=pan['VOYNICH_REFERENCE']
for a in d['axes']:
 E=pop(E0) if a=='physical_folio' else E0;S=[x['source_surface_sha256'] for x in E]
 for w in range(d['null_worlds']):
  P=shuf(E,S,w,d['null_seed']+'|VOYNICH_REFERENCE');z=calc(E,P,a,d['prior_mass'],a=='physical_folio');g=(z['bits']['PAGE_HOST']-z['bits']['WHOLE_FORM'])/z['events'];NV[a].append(g);ck('null_'+a+str(w),close(NN[('VOYNICH_REFERENCE',a,w)]['gain_bits_per_event'],g))
means={a:statistics.mean(v) for a,v in NV.items()};sds={a:statistics.pstdev(v) for a,v in NV.items()};wm=[max((NV[a][w]-means[a])/sds[a] for a in d['axes']) for w in range(d['null_worlds'])]
for a in d['axes']:
 q=SS[('VOYNICH_REFERENCE',a)];o=float(q['whole_form_gain_bits_per_event']);ck('mean_'+a,close(q['null_mean'],means[a]));z=(o-means[a])/sds[a];ck('max_'+a,close(q['max_five_p'],(1+sum(x>=z-1e-15 for x in wm))/65))
sens=read(R/'gdt301_prior_sensitivity.tsv')
for x in sens:
 z=calc(E0,[q['source_surface_sha256'] for q in E0],x['held_axis'],float(x['prior_mass']));ck('sens_'+x['held_axis']+x['prior_mass'],close(x['gain_bits_per_event'],(z['bits']['PAGE_HOST']-z['bits']['WHOLE_FORM'])/z['events']))
V={a:SS[('VOYNICH_REFERENCE',a)] for a in d['axes']};old=float(json.loads((R/'gdt299_result.json').read_text())['voynich_summary']['whole_form_gain_vs_host_bits_per_event']);gates={'folio_reproduced':abs(float(V['physical_folio']['whole_form_gain_bits_per_event'])-old)<=1e-9,'required_axes_positive':all(float(V[a]['whole_form_gain_bits_per_event'])>0 for a in d['decision']['required_positive_axes']),'minimum_four_positive_axes':sum(float(V[a]['whole_form_gain_bits_per_event'])>0 for a in d['axes'])>=4,'required_axes_prior_sensitivities_positive':all(float(x['gain_bits_per_event'])>0 for x in sens),'required_axes_max_five_p_le_0_05':all(float(V[a]['max_five_p'])<=.05 for a in d['decision']['required_positive_axes'])};ck('gates',gates==r['gates']);status=d['decision']['support'] if all(gates.values()) else d['decision']['local'] if gates['folio_reproduced'] and sum(float(V[a]['whole_form_gain_bits_per_event'])<=0 for a in ('register','section','currier','hand'))>=2 else d['decision']['mixed'];ck('status',status==r['status']);ck('report',status in (R/'GDT301_WHOLE_FORM_DOMAIN_TRANSFER_REPORT.md').read_text());val={'schema':'GDT301_VALIDATION_V1','status':'PASS','checks':len(checks),'result_sha256':sha(R/'gdt301_result.json'),'result_content_sha256':r['content_sha256'],'scope':'INDEPENDENT_SOURCE_SCORE_FOLD_NULL_SENSITIVITY_DECISION_HASH_RECONSTRUCTION'};(R/'gdt301_validation.json').write_text(json.dumps(val,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
