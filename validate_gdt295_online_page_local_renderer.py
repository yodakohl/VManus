#!/usr/bin/env python3
"""Independent reconstruction of GDT295."""
from __future__ import annotations
import csv,hashlib,itertools,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt295_result.json';OUT=R/'gdt295_validation.json';MODELS=('CROSS_FOLIO_HOST_X_POSITION','PAGE_LOCAL_HOST','PAGE_LOCAL_HOST_X_POSITION');C=('wrapper','local_frame','inner_d','right_family','dy_closure','b3');ALPHA=.5
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=3e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def ob(v):
 n=int(v);return '1' if n==1 else '2' if n==2 else '3_4' if n<=4 else '5_PLUS'
def gp(r):
 i=int(r['group_index']);n=int(r['group_count']);return 'ONLY' if n==1 else 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def y(r):return '|'.join(r[x] for x in C)
def lk(r):return r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r),int(r['host_length'])
def bk(r):return lk(r)+(r['line_close'],r['paragraph_close'],r['known_label_renderer'])
def pk(r):return r['page_host'],r['within_field_position']
def rebuild(ev,prior=11.,retain=False):
 alphabet=sorted({y(r) for r in ev});rank={z:i for i,z in enumerate(alphabet)};folios=[]
 for r in ev:
  if r['physical_folio'] not in folios:folios.append(r['physical_folio'])
 bits=Counter();top=Counter();fr=[];pred=[];pages=defaultdict(float);sections=defaultdict(float);hands=defaultdict(float);eligible=0
 for held in folios:
  train=[r for r in ev if r['physical_folio']!=held];test=[r for r in ev if r['physical_folio']==held];th=Counter(r['page_host'] for r in train);g=Counter();a=defaultdict(Counter);b=defaultdict(Counter);h=defaultdict(Counter);p=defaultdict(Counter)
  for r in train:
   z=y(r);g[z]+=1;a[lk(r)][z]+=1;b[bk(r)][z]+=1;h[r['page_host']][z]+=1;p[pk(r)][z]+=1
  ph=defaultdict(Counter);php=defaultdict(Counter);fb=Counter();ft=Counter();fn=0
  for locus,group in itertools.groupby(test,key=lambda r:r['locus']):
   line=list(group)
   for r in line:
    if th[r['page_host']]==0 or sum(ph[r['page'],r['page_host']].values())==0:continue
    actual=y(r);pp={m:{} for m in MODELS};K=len(alphabet)
    for z in alphabet:
     p0=(g[z]+ALPHA)/(len(train)+ALPHA*K);q=a[lk(r)];p1=(q[z]+prior*p0)/(sum(q.values())+prior);q=b[bk(r)];p2=(q[z]+prior*p1)/(sum(q.values())+prior);q=h[r['page_host']];p3=(q[z]+prior*p2)/(sum(q.values())+prior);q=p[pk(r)];pc=(q[z]+prior*p3)/(sum(q.values())+prior);q=ph[r['page'],r['page_host']];pv=(q[z]+prior*pc)/(sum(q.values())+prior);q=php[r['page'],r['page_host'],r['within_field_position']];px=(q[z]+prior*pv)/(sum(q.values())+prior);pp['CROSS_FOLIO_HOST_X_POSITION'][z]=pc;pp['PAGE_LOCAL_HOST'][z]=pv;pp['PAGE_LOCAL_HOST_X_POSITION'][z]=px
    for m in MODELS:
     v=-math.log2(pp[m][actual]);bits[m]+=v;fb[m]+=v;hit=int(max(alphabet,key=lambda z:(pp[m][z],-rank[z]))==actual);top[m]+=hit;ft[m]+=hit
    v=math.log2(pp['PAGE_LOCAL_HOST_X_POSITION'][actual]/pp['CROSS_FOLIO_HOST_X_POSITION'][actual]);pages[r['page']]+=v;sections[r['section']]+=v;hands[r['hand']]+=v;eligible+=1;fn+=1
    if retain:pred.append((actual,pp['CROSS_FOLIO_HOST_X_POSITION'],pp['PAGE_LOCAL_HOST_X_POSITION'],(r['page'],r['page_host'])))
   for r in line:
    z=y(r);ph[r['page'],r['page_host']][z]+=1;php[r['page'],r['page_host'],r['within_field_position']][z]+=1
  for m in MODELS:fr.append((held,m,fn,fb[m],ft[m]))
 return {'classes':alphabet,'bits':dict(bits),'top':dict(top),'folds':fr,'pred':pred,'pages':dict(pages),'sections':dict(sections),'hands':dict(hands),'n':eligible}
def inc(q):return {'PAGE_HOST_GIVEN_CROSS_FOLIO_POSITION':(q['bits']['CROSS_FOLIO_HOST_X_POSITION']-q['bits']['PAGE_LOCAL_HOST'])/q['n'],'PAGE_POSITION_GIVEN_PAGE_HOST':(q['bits']['PAGE_LOCAL_HOST']-q['bits']['PAGE_LOCAL_HOST_X_POSITION'])/q['n'],'TOTAL_PAGE_LOCAL_GAIN':(q['bits']['CROSS_FOLIO_HOST_X_POSITION']-q['bits']['PAGE_LOCAL_HOST_X_POSITION'])/q['n']}
def null(q,panel,worlds):
 st=defaultdict(list)
 for i,x in enumerate(q['pred']):st[x[3]].append(i)
 out=[];mobile=0;swap=sum(len(v) for v in st.values() if len(v)>1)
 for world in range(worlds):
  labels=[x[0] for x in q['pred']]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT295_ONLINE_PAGE_RENDERER_ALIGNMENT|{panel}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[labels[i] for i in ids];rng.shuffle(v)
   for i,z in zip(ids,v):
    if world==0 and z!=labels[i]:mobile+=1
    labels[i]=z
  out.append(sum(math.log2(x[2][z]/x[1][z]) for x,z in zip(q['pred'],labels))/q['n'])
 return out,mobile,swap
def task(item):
 p,e,w=item;q=rebuild(e,retain=True);n,m,s=null(q,p,w);return p,q,n,m,s
def main():
 cc=[]
 def ck(n,v):cc.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt295_design.json').read_text());res=json.loads(RESULT.read_text());pt=rows(R/'gdt295_panel_scores.tsv');ft=rows(R/'gdt295_folio_scores.tsv');bt=rows(R/'gdt295_breakdown.tsv');nt=rows(R/'gdt295_null_results.tsv');st=rows(R/'gdt295_voynich_sensitivities.tsv');ck('design',d['content_sha256']==csha(d) and d['status']=='FROZEN_BEFORE_GDT295_SCORING');mf=rows(R/'gdt295_freeze_manifest.tsv');ck('freeze',len(mf)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('events',all(len(v)==8448 for v in panels.values()));ck('tables',len(pt)==24 and len(nt)==320 and len(st)==2);rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(task,(p,panels[p],d['null_worlds'])):p for p in d['powered_panels']}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z[1:]
 obs={};means={};sds={}
 for p in d['panels']:
  tab=[x for x in pt if x['control_id']==p];ck('panel_shape:'+p,len(tab)==3)
  if p not in rr:
   ck('unscored:'+p,all(x['capacity_status']=='UNSCORED_ZERO_ONLINE_CAPACITY' and int(x['eligible_events'])==0 and x['bits']=='NA' for x in tab));continue
  q,n,mob,swap=rr[p];z=inc(q);obs[p]=z['TOTAL_PAGE_LOCAL_GAIN'];means[p]=statistics.mean(n);sds[p]=statistics.pstdev(n)
  for model in MODELS:
   x=next(x for x in tab if x['model']==model);ck('panel:'+p+':'+model,x['capacity_status']=='SCORED' and int(x['eligible_events'])==q['n'] and int(x['classes'])==len(q['classes']) and close(x['bits'],q['bits'][model]) and int(x['top1'])==q['top'][model])
  stored=[x for x in ft if x['control_id']==p];ck('fold_shape:'+p,len(stored)==len(q['folds']));ck('fold_values:'+p,all(int(next(x for x in stored if x['held_folio']==h and x['model']==m)['eligible_events'])==nn and close(next(x for x in stored if x['held_folio']==h and x['model']==m)['bits'],b) and int(next(x for x in stored if x['held_folio']==h and x['model']==m)['top1'])==t for h,m,nn,b,t in q['folds']));storedb=[x for x in bt if x['control_id']==p];ck('breakdowns:'+p,all(close(next(x for x in storedb if x['breakdown']==kind and x['value']==key)['gain_bits'],value) for kind,data in (('PAGE',q['pages']),('SECTION',q['sections']),('HAND',q['hands'])) for key,value in data.items()));sn=sorted((x for x in nt if x['control_id']==p),key=lambda x:int(x['world_index']));ck('null:'+p,len(sn)==64 and all(close(x['page_local_gain_bits_per_event'],v) for x,v in zip(sn,n)));s=next(x for x in res['summary'] if x['control_id']==p);ck('summary:'+p,int(s['eligible_events'])==q['n'] and int(s['pages'])==len(q['pages']) and int(s['sections'])==len(q['sections']) and int(s['positive_pages'])==sum(v>0 for v in q['pages'].values()) and int(s['positive_sections'])==sum(v>0 for v in q['sections'].values()) and all(close(s['increments'][k],v) for k,v in z.items()) and close(s['null_mean'],means[p]) and close(s['null_sd'],sds[p]) and int(s['null_mobile_events_world0'])==mob and int(s['null_swappable_events'])==swap)
 variable=[p for p in d['powered_panels'] if sds[p]>1e-15];zs={p:(obs[p]-means[p])/sds[p] for p in variable};mx=[max((rr[p][1][i]-means[p])/sds[p] for p in variable) for i in range(64)]
 for p in d['powered_panels']:
  s=next(x for x in res['summary'] if x['control_id']==p)
  if p in variable:
   lp=(1+sum(v>=obs[p]-1e-15 for v in rr[p][1]))/65;mp=(1+sum(v>=zs[p]-1e-15 for v in mx))/65;ck('pvalues:'+p,close(s['observed_z'],zs[p]) and close(s['local_p'],lp) and close(s['max_variable_family_p'],mp))
  else:ck('pvalues:'+p,s['observed_z']==s['local_p']==s['max_variable_family_p']=='NA_ZERO_NULL_VARIANCE')
 ck('panel_lists',res['variable_null_panels']==variable and res['zero_null_variance_panels']==[p for p in d['powered_panels'] if p not in variable] and res['unscored_zero_capacity_panels']==d['unscored_zero_capacity_panels']);voy=panels['VOYNICH_REFERENCE']
 for prior in d['voynich_prior_sensitivities']:
  q=rebuild(voy,prior=prior);z=inc(q);x=next(x for x in res['voynich_sensitivities'] if float(x['prior_mass'])==prior);ck('prior:'+str(prior),int(x['eligible_events'])==q['n'] and all(close(x[k],v) for k,v in z.items()))
 v=res['voynich_summary'];gates={'total_gain_positive':v['increments']['TOTAL_PAGE_LOCAL_GAIN']>0,'at_least_one_hundred_of_one_hundred_fifty_three_pages_positive':v['pages']==153 and v['positive_pages']>=100,'at_least_four_of_six_sections_positive':v['sections']==6 and v['positive_sections']>=4,'both_prior_sensitivities_positive':all(x['TOTAL_PAGE_LOCAL_GAIN']>0 for x in res['voynich_sensitivities']),'maxT_p_le_0_05':float(v['max_variable_family_p'])<=.05};status=d['decision']['support'] if all(gates.values()) else d['decision']['fail'];ck('decision',res['frozen_gates']==gates and res['status']==status);ck('history_scope',res['same_line_update_forbidden'] is True and res['uses_earlier_held_folio_lines'] is True);ck('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('content',res['content_sha256']==csha(res));ck('hashes',all(sha(R/k)==v for sec in ('inputs','documents','implementation','outputs') for k,v in res[sec].items()));ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));o={'schema':'GDT295_ONLINE_PAGE_LOCAL_RENDERER_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_POWERED_PANEL_ONLINE_LINE_SAFE_SCORES_FOLDS_BREAKDOWNS_NULLS_MAXT_PRIORS_DECISION_AND_HASHES','checks_passed':len(cc),'checks_total':len(cc),'checks':cc,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};o['content_sha256']=csha(o);OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(cc)},sort_keys=True))
if __name__=='__main__':main()
