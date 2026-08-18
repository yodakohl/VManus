#!/usr/bin/env python3
"""Independent reconstruction of GDT299 scores and nulls."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt299_design.json';RESULT=R/'gdt299_result.json';OUT=R/'gdt299_validation.json';Y=('FIRST','MIDDLE','LAST')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def out(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def lk(x):return (x['section'],x['currier'],x['hand'],x['group_count'])
def eligible(rows):
 b=[x for x in rows if int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in b:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in b if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2]
def calc(ev,ids,prior):
 G=Counter();L=defaultdict(Counter);H=defaultdict(Counter);S=defaultdict(Counter);FG=defaultdict(Counter);FL=defaultdict(lambda:defaultdict(Counter));FH=defaultdict(lambda:defaultdict(Counter));FS=defaultdict(lambda:defaultdict(Counter));FN=Counter()
 for x,s in zip(ev,ids):
  y=out(x);f=x['physical_folio'];G[y]+=1;L[lk(x)][y]+=1;H[x['page_host']][y]+=1;S[s][y]+=1;FG[f][y]+=1;FL[f][lk(x)][y]+=1;FH[f][x['page_host']][y]+=1;FS[f][s][y]+=1;FN[f]+=1
 bits=Counter();top=Counter();fold=defaultdict(Counter)
 for x,s in zip(ev,ids):
  y=out(x);f=x['physical_folio'];ng=len(ev)-FN[f];p0={z:(G[z]-FG[f][z]+.5)/(ng+1.5) for z in Y};a={z:L[lk(x)][z]-FL[f][lk(x)][z] for z in Y};pa={z:(a[z]+prior*p0[z])/(sum(a.values())+prior) for z in Y};b={z:H[x['page_host']][z]-FH[f][x['page_host']][z] for z in Y};pb={z:(b[z]+prior*pa[z])/(sum(b.values())+prior) for z in Y};c={z:S[s][z]-FS[f][s][z] for z in Y};pc={z:(c[z]+prior*pb[z])/(sum(c.values())+prior) for z in Y}
  for n,p in (('LAYOUT',pa),('PAGE_HOST',pb),('WHOLE_FORM',pc)):
   q=-math.log2(p[y]);bits[n]+=q;fold[f][n]+=q;pred=max(Y,key=lambda z:(p[z],-Y.index(z)));top[n]+=pred==y;fold[f][n+'_TOP1']+=pred==y
 return bits,top,fold
def perm(ev,wi,seed):
 original=[x['source_surface_sha256'] for x in ev];groups=defaultdict(list)
 for i,x in enumerate(ev):groups[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(i)
 ans=list(original)
 for key,idx in sorted(groups.items(),key=lambda z:str(z[0])):
  vals=[original[i] for i in idx];n=int(hashlib.sha256((seed+'|'+str(wi)+'|'+json.dumps(key)).encode()).hexdigest()[:16],16);random.Random(n).shuffle(vals)
  for i,v in zip(idx,vals):ans[i]=v
 return ans
def close(a,b,tol=5e-12):return abs(float(a)-float(b))<=tol
def main():
 checks=[]
 def ck(n,v):checks.append((n,bool(v)));assert v,n
 d=json.loads(D.read_text());r=json.loads(RESULT.read_text());ck('design_content',d['content_sha256']==rch(d));ck('result_content',r['content_sha256']==rch(r));ck('status',r['status']=='WHOLE_FORM_PHYSICAL_ROLE_TRANSFERS');ck('f84_flags',not any(r['f84'].values()));ck('prohibitions',r['source_strings_inspected']==r['page_host_substrings_mined']==r['semantic_assignments']==0)
 for group in ('inputs','documents','implementation','outputs'):
  for name,digest in r[group].items():ck(f'{group}:{name}',sha(R/name)==digest)
 rows=read(R/'gdt278_native_event_inventory.tsv');ck('source_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));cap={x['control_id']:x for x in read(R/'gdt299_capacity.tsv')};panels={p:eligible([x for x in rows if x['control_id']==p]) for p in cap};pub={x['control_id']:x for x in read(R/'gdt299_panel_scores.tsv')};pf={(x['control_id'],x['held_folio']):x for x in read(R/'gdt299_folio_scores.tsv')};pn={(x['control_id'],int(x['world_index'])):x for x in read(R/'gdt299_null_results.tsv')};observed={};nulls=defaultdict(list);mobile0={}
 for panel,ev in panels.items():
  ck(f'capacity_events:{panel}',len(ev)==int(cap[panel]['eligible_events']))
  if cap[panel]['score_capacity']!='POWERED':ck(f'unscored:{panel}',pub[panel]['whole_form_gain_vs_host_bits_per_event']=='NA');continue
  ids=[x['source_surface_sha256'] for x in ev];bits,top,fold=calc(ev,ids,float(d['prior_mass']));gain=(bits['PAGE_HOST']-bits['WHOLE_FORM'])/len(ev);observed[panel]=gain;p=pub[panel];ck(f'score:{panel}',int(p['events'])==len(ev) and int(p['folios'])==len(fold) and close(p['layout_bits_per_event'],bits['LAYOUT']/len(ev)) and close(p['host_bits_per_event'],bits['PAGE_HOST']/len(ev)) and close(p['whole_form_bits_per_event'],bits['WHOLE_FORM']/len(ev)) and close(p['host_gain_vs_layout_bits_per_event'],(bits['LAYOUT']-bits['PAGE_HOST'])/len(ev)) and close(p['whole_form_gain_vs_host_bits_per_event'],gain) and close(p['layout_top1'],top['LAYOUT']/len(ev)) and close(p['host_top1'],top['PAGE_HOST']/len(ev)) and close(p['whole_form_top1'],top['WHOLE_FORM']/len(ev)) and int(p['positive_folios'])==sum(z['PAGE_HOST']-z['WHOLE_FORM']>0 for z in fold.values()))
  for f,z in fold.items():
   q=pf[panel,f];ck(f'fold:{panel}:{f}',int(q['events'])==sum(x['physical_folio']==f for x in ev) and close(q['layout_bits'],z['LAYOUT']) and close(q['host_bits'],z['PAGE_HOST']) and close(q['whole_form_bits'],z['WHOLE_FORM']) and close(q['whole_form_gain_bits'],z['PAGE_HOST']-z['WHOLE_FORM']) and int(q['layout_top1'])==z['LAYOUT_TOP1'] and int(q['host_top1'])==z['PAGE_HOST_TOP1'] and int(q['whole_form_top1'])==z['WHOLE_FORM_TOP1'])
  for wi in range(int(d['null_worlds'])):
   qids=perm(ev,wi,d['null_seed']+'|'+panel);b,t,f=calc(ev,qids,float(d['prior_mass']));g=(b['PAGE_HOST']-b['WHOLE_FORM'])/len(ev);nulls[panel].append(g);q=pn[panel,wi];ck(f'null:{panel}:{wi}',close(q['whole_form_gain_vs_host_bits_per_event'],g) and int(q['mobile_events'])==sum(a!=b for a,b in zip(ids,qids)))
   if wi==0:mobile0[panel]=int(q['mobile_events'])
 variable=[p for p in observed if cap[p]['null_capacity']=='VARIABLE'];means={p:statistics.mean(nulls[p]) for p in variable};sds={p:statistics.pstdev(nulls[p]) for p in variable};zs={p:(observed[p]-means[p])/sds[p] for p in variable if sds[p]>0};worldmax=[max((nulls[p][wi]-means[p])/sds[p] for p in zs) for wi in range(int(d['null_worlds']))]
 for p in observed:
  q=pub[p];ck(f'inference:{p}',close(q['null_mean_gain'],statistics.mean(nulls[p])) and close(q['null_sd_gain'],statistics.pstdev(nulls[p])) and (q['observed_z']=='NA' if p not in zs else close(q['observed_z'],zs[p])) and (q['local_p']=='NA' if p not in variable else close(q['local_p'],(1+sum(x>=observed[p]-1e-15 for x in nulls[p]))/65)) and (q['max_family_p']=='NA' if p not in zs else close(q['max_family_p'],(1+sum(x>=zs[p]-1e-15 for x in worldmax))/65)) and int(q['null_mobile_events_world0'])==mobile0[p])
 sens=read(R/'gdt299_prior_sensitivity.tsv');
 for q in sens:
  ev=panels['VOYNICH_REFERENCE'];b,t,f=calc(ev,[x['source_surface_sha256'] for x in ev],float(q['prior_mass']));ck(f"sensitivity:{q['prior_mass']}",close(q['whole_form_gain_vs_host_bits_per_event'],(b['PAGE_HOST']-b['WHOLE_FORM'])/len(ev)) and int(q['positive_folios'])==sum(x['PAGE_HOST']-x['WHOLE_FORM']>0 for x in f.values()))
 v=pub['VOYNICH_REFERENCE'];g={'gain_positive':float(v['whole_form_gain_vs_host_bits_per_event'])>0,'positive_folios_at_least_60':int(v['positive_folios'])>=60,'both_prior_sensitivities_positive':all(float(x['whole_form_gain_vs_host_bits_per_event'])>0 for x in sens),'max_family_p_le_0_05':float(v['max_family_p'])<=.05};ck('gates',g==r['gates'] and all(g.values()));js=r['voynich_summary'];text_fields=('capacity_status','control_id','null_capacity');int_fields=('events','folios','positive_folios','null_mobile_events_world0');num_fields=tuple(k for k in v if k not in text_fields+int_fields);ck('summary_text',all(str(js[k])==v[k] for k in text_fields));ck('summary_int',all(int(js[k])==int(v[k]) for k in int_fields));ck('summary_numeric',all(close(js[k],v[k]) for k in num_fields));text=(R/'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_REPORT.md').read_text();ck('report',r['status'] in text and 'No source string was inspected' in text and 'no f84 row' in text)
 result={'schema':'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_SOURCE_ELIGIBILITY_FOLDS_SCORES_64_WORLD_NULL_RECONSTRUCTION','checks_total':len(checks),'checks_passed':sum(v for n,v in checks),'check_categories':dict(sorted(Counter(n.split(':',1)[0] for n,v in checks).items())),'failed_checks':[n for n,v in checks if not v],'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};result['content_sha256']=rch(result);OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
