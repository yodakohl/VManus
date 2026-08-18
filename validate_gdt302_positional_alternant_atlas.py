#!/usr/bin/env python3
"""Independent reconstruction of GDT302 positional alternant atlas."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;Y=('FIRST','MIDDLE','LAST');checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def close(a,b,t=2e-10):return abs(float(a)-float(b))<=t
def yy(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def lay(x):return x['section'],x['currier'],x['hand'],x['group_count']
def sm(c,b,k):
 n=sum(c.values());return {z:(c[z]+k*b[z])/(n+k) for z in Y}
def pop(rows):
 b=[x for x in rows if x['control_id']=='VOYNICH_REFERENCE' and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in b:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in b if len(hf[x['page_host']])>1 and len(sf[x['source_surface_sha256']])>1]
def gains(E):
 G=Counter();L=defaultdict(Counter);H=defaultdict(Counter);W=defaultdict(Counter);FG=defaultdict(Counter);FL=defaultdict(lambda:defaultdict(Counter));FH=defaultdict(lambda:defaultdict(Counter));FW=defaultdict(lambda:defaultdict(Counter));FN=Counter()
 for x in E:
  z=yy(x);f=x['physical_folio'];G[z]+=1;L[lay(x)][z]+=1;H[x['page_host']][z]+=1;W[x['source_surface_sha256']][z]+=1;FG[f][z]+=1;FL[f][lay(x)][z]+=1;FH[f][x['page_host']][z]+=1;FW[f][x['source_surface_sha256']][z]+=1;FN[f]+=1
 ans=[]
 for x in E:
  z=yy(x);f=x['physical_folio'];g={q:G[q]-FG[f][q] for q in Y};p0={q:(g[q]+.5)/(len(E)-FN[f]+1.5) for q in Y};a={q:L[lay(x)][q]-FL[f][lay(x)][q] for q in Y};pl=sm(a,p0,11);a={q:H[x['page_host']][q]-FH[f][x['page_host']][q] for q in Y};ph=sm(a,pl,11);a={q:W[x['source_surface_sha256']][q]-FW[f][x['source_surface_sha256']][q] for q in Y};pw=sm(a,ph,11);ans.append(math.log2(pw[z]/ph[z]))
 return ans
d=json.loads((R/'gdt302_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('design',d['content_sha256']==can(q));r=json.loads((R/'gdt302_result.json').read_text());q=dict(r);q.pop('content_sha256');ck('result',r['content_sha256']==can(q));
for g in ('inputs','documents','implementation','outputs'):
 for n,h in r[g].items():ck(g+'_'+n,sha(R/n)==h)
nr=read(R/'gdt278_native_event_inventory.tsv');rawrows=read(R/'gdt276_event_inventory.tsv');ck('f84n',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in nr));ck('f84r',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rawrows));raw={x['observation_id']:x for x in rawrows};E=pop(nr);ck('population',len(E)==6844);gg=gains(E);hc=Counter(x['page_host'] for x in E);fc=Counter((x['page_host'],x['source_surface_sha256']) for x in E);ff=defaultdict(set);forms=defaultdict(list);hosts=defaultdict(list)
for i,x in enumerate(E):ff[(x['page_host'],x['source_surface_sha256'])].add(x['physical_folio']);forms[(x['page_host'],x['source_surface_sha256'])].append((i,x));hosts[x['page_host']].append((i,x));ck('join_'+x['observation_id'],hashlib.sha256(raw[x['observation_id']]['raw_token'].encode()).hexdigest()==x['source_surface_sha256'])
ok={(h,s) for h,s in fc if fc[(h,s)]>=8 and len(ff[(h,s)])>=4 and hc[h]>=20};bc=Counter(h for h,s in ok);ok={q for q in ok if bc[q[0]]>=2};A={(x['page_host'],x['surface_sha256']):x for x in read(R/'gdt302_positional_alternants.tsv')};ck('form_keys',set(A)==ok)
for h,s in sorted(ok):
 F=forms[(h,s)];O=[q for q in hosts[h] if q not in F];cy=Counter(yy(x) for i,x in F);hy=Counter(yy(x) for i,x in hosts[h]);rat={z:((cy[z]+.5)/(len(F)+1.5))/((hy[z]+.5)/(len(hosts[h])+1.5)) for z in Y};role=max(Y,key=lambda z:(rat[z],-Y.index(z)));powered=positive=0
 for ax in ('section','hand'):
  for v in sorted({x[ax] for i,x in F}):
   a=[x for i,x in F if x[ax]==v];b=[x for i,x in O if x[ax]==v]
   if len(a)>=2 and len(b)>=2:powered+=1;positive+=sum(yy(x)==role for x in a)/len(a)>sum(yy(x)==role for x in b)/len(b)
 gain=sum(gg[i] for i,x in F);cl='STABLE_POSITIONAL_ALTERNANT' if gain>0 and rat[role]>=1.5 and powered>=2 and positive==powered else 'PROVISIONAL' if gain>0 and rat[role]>=1.25 else 'WEAK' if gain>0 else 'COUNTEREXAMPLE';z=A[(h,s)];ck('raw_'+h+s,z['raw_token']==raw[F[0][1]['observation_id']]['raw_token']);ck('role_'+h+s,z['preferred_physical_role']==role);ck('ratio_'+h+s,close(z['role_likelihood_ratio'],rat[role]));ck('gain_'+h+s,close(z['lofo_gain_bits'],gain));ck('class_'+h+s,z['classification']==cl);ck('strata_'+h+s,int(z['powered_section_hand_strata'])==powered and int(z['positive_role_strata'])==positive)
P=read(R/'gdt302_contrast_pairs.tsv');expected=0;stable=0;by=defaultdict(list)
for x in A.values():by[x['page_host']].append(x)
for h,v in by.items():
 for i,a in enumerate(v):
  for b in v[i+1:]:
   if a['preferred_physical_role']!=b['preferred_physical_role']:expected+=1;stable+=a['classification']==b['classification']=='STABLE_POSITIONAL_ALTERNANT'
ck('pairs',len(P)==expected);ck('stable_pairs',sum(x['classification']=='STABLE_CONTRAST' for x in P)==stable);conc=read(R/'gdt302_gain_concentration.tsv');pos=sorted((float(x['lofo_gain_bits']) for x in A.values() if float(x['lofo_gain_bits'])>0),reverse=True);ck('conc10',close(conc[0]['share_of_positive_gain'],sum(pos[:10])/sum(pos)));ck('conc20',close(conc[1]['share_of_positive_gain'],sum(pos[:20])/sum(pos)));ck('summary',int(r['summary']['forms'])==len(A) and int(r['summary']['stable_contrasts'])==stable);ck('report',r['status'] in (R/'GDT302_HOST_POSITIONAL_ALTERNANT_ATLAS_REPORT.md').read_text());val={'schema':'GDT302_VALIDATION_V1','status':'PASS','checks':len(checks),'result_sha256':sha(R/'gdt302_result.json'),'result_content_sha256':r['content_sha256'],'scope':'INDEPENDENT_JOIN_POPULATION_LOFO_GAIN_CLASSIFICATION_PAIR_CONCENTRATION_HASH_RECONSTRUCTION'};(R/'gdt302_validation.json').write_text(json.dumps(val,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
