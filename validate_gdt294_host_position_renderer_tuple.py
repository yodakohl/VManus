#!/usr/bin/env python3
"""Independent reconstruction of GDT294."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt294_result.json';OUT=R/'gdt294_validation.json';MODELS=('LAYOUT_CONTEXT','BOUNDARY_CONTEXT','EXACT_HOST','HOST_X_POSITION','HOST_X_RECORD_SLOT');C=('wrapper','local_frame','inner_d','right_family','dy_closure','b3');ALPHA=.5
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
def lk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r),int(r['host_length']))
def bk(r):return lk(r)+(r['line_close'],r['paragraph_close'],r['known_label_renderer'])
def pk(r):return r['page_host'],r['within_field_position']
def sk(r):return r['page_host'],r['within_field_position'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r)
def nk(r):return r['physical_folio'],r['page_host'],r['section'],r['currier'],r['hand'],r['register'],ob(r['record_ordinal']),ob(r['field_ordinal']),gp(r),int(r['host_length']),r['line_close'],r['paragraph_close'],r['known_label_renderer']
def rebuild(ev,split='physical_folio',prior=11.,retain=False):
 alphabet=sorted({y(r) for r in ev});rank={x:i for i,x in enumerate(alphabet)};folds=defaultdict(list)
 for i,r in enumerate(ev):folds[r[split]].append(i)
 bits=Counter();top=Counter();fr=[];pred=[];fg={};eligible=0
 for held,test in sorted(folds.items()):
  train=[i for i,r in enumerate(ev) if r[split]!=held];th=Counter(ev[i]['page_host'] for i in train);g=Counter();a=defaultdict(Counter);b=defaultdict(Counter);h=defaultdict(Counter);p=defaultdict(Counter);s=defaultdict(Counter)
  for i in train:
   r=ev[i];z=y(r);g[z]+=1;a[lk(r)][z]+=1;b[bk(r)][z]+=1;h[r['page_host']][z]+=1;p[pk(r)][z]+=1;s[sk(r)][z]+=1
  test=[i for i in test if th[ev[i]['page_host']]>0];eligible+=len(test);fb=Counter();ft=Counter()
  for i in test:
   r=ev[i];actual=y(r);pp={m:{} for m in MODELS};K=len(alphabet)
   for z in alphabet:
    p0=(g[z]+ALPHA)/(len(train)+ALPHA*K);q=a[lk(r)];p1=(q[z]+prior*p0)/(sum(q.values())+prior);q=b[bk(r)];p2=(q[z]+prior*p1)/(sum(q.values())+prior);q=h[r['page_host']];p3=(q[z]+prior*p2)/(sum(q.values())+prior);q=p[pk(r)];p4=(q[z]+prior*p3)/(sum(q.values())+prior);q=s[sk(r)];p5=(q[z]+prior*p4)/(sum(q.values())+prior)
    for m,v in zip(MODELS,(p1,p2,p3,p4,p5)):pp[m][z]=v
   for m in MODELS:
    v=-math.log2(pp[m][actual]);bits[m]+=v;fb[m]+=v;hit=int(max(alphabet,key=lambda z:(pp[m][z],-rank[z]))==actual);top[m]+=hit;ft[m]+=hit
   if retain:pred.append((actual,pp['EXACT_HOST'],pp['HOST_X_POSITION'],nk(r)))
  fg[held]=fb['EXACT_HOST']-fb['HOST_X_POSITION']
  for m in MODELS:fr.append((held,m,len(test),fb[m],ft[m]))
 return {'classes':alphabet,'bits':dict(bits),'top':dict(top),'folds':fr,'pred':pred,'folio_gain':fg,'n':eligible}
def inc(q):return {'BOUNDARY_GIVEN_LAYOUT':(q['bits']['LAYOUT_CONTEXT']-q['bits']['BOUNDARY_CONTEXT'])/q['n'],'HOST_GIVEN_BOUNDARY':(q['bits']['BOUNDARY_CONTEXT']-q['bits']['EXACT_HOST'])/q['n'],'HOST_POSITION_GIVEN_HOST':(q['bits']['EXACT_HOST']-q['bits']['HOST_X_POSITION'])/q['n'],'RECORD_SLOT_GIVEN_HOST_POSITION':(q['bits']['HOST_X_POSITION']-q['bits']['HOST_X_RECORD_SLOT'])/q['n']}
def null(q,panel,worlds):
 st=defaultdict(list)
 for i,x in enumerate(q['pred']):st[x[3]].append(i)
 out=[];mobile=0;swap=sum(len(v) for v in st.values() if len(v)>1)
 for world in range(worlds):
  labels=[x[0] for x in q['pred']]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT294_HELD_HOST_POSITION_RENDERER_ALIGNMENT|{panel}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[labels[i] for i in ids];rng.shuffle(v)
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
 d=json.loads((R/'gdt294_design.json').read_text());res=json.loads(RESULT.read_text());pt=rows(R/'gdt294_panel_scores.tsv');ft=rows(R/'gdt294_folio_scores.tsv');it=rows(R/'gdt294_nested_increments.tsv');nt=rows(R/'gdt294_null_results.tsv');st=rows(R/'gdt294_voynich_sensitivities.tsv');ck('design',d['content_sha256']==csha(d) and d['status']=='FROZEN_BEFORE_GDT294_SCORING');mf=rows(R/'gdt294_freeze_manifest.tsv');ck('freeze',len(mf)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('events',all(len(v)==8448 for v in panels.values()));ck('tables',len(pt)==40 and len(it)==32 and len(nt)==512 and len(st)==8);rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(task,(p,e,d['null_worlds'])):p for p,e in panels.items()}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z[1:]
 obs={};means={};sds={}
 for p in d['panels']:
  q,n,mob,swap=rr[p];z=inc(q);obs[p]=z['HOST_POSITION_GIVEN_HOST'];means[p]=statistics.mean(n);sds[p]=statistics.pstdev(n);tab=[x for x in pt if x['control_id']==p];ck('panel_shape:'+p,len(tab)==5)
  for model in MODELS:
   x=next(x for x in tab if x['model']==model);ck('panel:'+p+':'+model,int(x['eligible_events'])==q['n'] and int(x['classes'])==len(q['classes']) and close(x['bits'],q['bits'][model]) and int(x['top1'])==q['top'][model])
  stored=[x for x in ft if x['control_id']==p];ck('fold_shape:'+p,len(stored)==len(q['folds']));ck('fold_values:'+p,all(int(next(x for x in stored if x['held_value']==h and x['model']==m)['eligible_events'])==nn and close(next(x for x in stored if x['held_value']==h and x['model']==m)['bits'],b) and int(next(x for x in stored if x['held_value']==h and x['model']==m)['top1'])==t for h,m,nn,b,t in q['folds']));ck('increments:'+p,all(close(next(x for x in it if x['control_id']==p and x['increment']==k)['gain_bits_per_event'],v) for k,v in z.items()));sn=sorted((x for x in nt if x['control_id']==p),key=lambda x:int(x['world_index']));ck('null:'+p,len(sn)==64 and all(close(x['host_position_gain_bits_per_event'],v) for x,v in zip(sn,n)));s=next(x for x in res['summary'] if x['control_id']==p);ck('summary:'+p,int(s['eligible_events'])==q['n'] and int(s['classes'])==len(q['classes']) and all(close(s['increments'][k],v) for k,v in z.items()) and int(s['positive_folios'])==sum(v>0 for v in q['folio_gain'].values()) and close(s['null_mean'],means[p]) and close(s['null_sd'],sds[p]) and int(s['null_mobile_events_world0'])==mob and int(s['null_swappable_events'])==swap)
 variable=[p for p in d['panels'] if sds[p]>1e-15];zs={p:(obs[p]-means[p])/sds[p] for p in variable};mx=[max((rr[p][1][i]-means[p])/sds[p] for p in variable) for i in range(64)]
 for p in d['panels']:
  s=next(x for x in res['summary'] if x['control_id']==p)
  if p in variable:
   lp=(1+sum(v>=obs[p]-1e-15 for v in rr[p][1]))/65;mp=(1+sum(v>=zs[p]-1e-15 for v in mx))/65;ck('pvalues:'+p,close(s['observed_z'],zs[p]) and close(s['local_p'],lp) and close(s['max_variable_family_p'],mp))
  else:ck('pvalues:'+p,s['observed_z']==s['local_p']==s['max_variable_family_p']=='NA_ZERO_NULL_VARIANCE')
 ck('panel_lists',res['variable_null_panels']==variable and res['zero_null_variance_panels']==[p for p in d['panels'] if p not in variable]);voy=panels['VOYNICH_REFERENCE']
 for prior in d['voynich_prior_sensitivities']:
  q=rebuild(voy,prior=prior);z=inc(q)
  for name in ('HOST_POSITION_GIVEN_HOST','RECORD_SLOT_GIVEN_HOST_POSITION'):
   x=next(x for x in st if x['split']=='HELD_PHYSICAL_FOLIO' and float(x['prior_mass'])==prior and x['increment']==name);ck('prior:'+str(prior)+':'+name,int(x['eligible_events'])==q['n'] and close(x['gain_bits_per_event'],z[name]))
 for split in ('section','hand'):
  q=rebuild(voy,split=split);z=inc(q)
  for name in ('HOST_POSITION_GIVEN_HOST','RECORD_SLOT_GIVEN_HOST_POSITION'):
   x=next(x for x in st if x['split']=='HELD_'+split.upper() and x['increment']==name);ck('split:'+split+':'+name,int(x['eligible_events'])==q['n'] and close(x['gain_bits_per_event'],z[name]))
 v=res['voynich_summary'];sg={x['split']:float(x['gain_bits_per_event']) for x in st if x['increment']=='HOST_POSITION_GIVEN_HOST'};gates={'host_position_gain_positive':v['increments']['HOST_POSITION_GIVEN_HOST']>0,'at_least_sixty_of_ninety_one_folios_positive':v['folios']==91 and v['positive_folios']>=60,'held_section_gain_positive':sg['HELD_SECTION']>0,'held_hand_gain_positive':sg['HELD_HAND']>0,'maxT_p_le_0_05':float(v['max_variable_family_p'])<=.05};status=d['decision']['support'] if all(gates.values()) else d['decision']['fail'];ck('decision',res['frozen_gates']==gates and res['status']==status);ck('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('content',res['content_sha256']==csha(res));ck('hashes',all(sha(R/k)==v for sec in ('inputs','documents','implementation','outputs') for k,v in res[sec].items()));ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));o={'schema':'GDT294_HOST_POSITION_RENDERER_TUPLE_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_ALL_PANEL_NESTED_FOLDS_NULLS_MAXT_VOYNICH_PRIORS_SECTION_HAND_DECISION_AND_HASHES','checks_passed':len(cc),'checks_total':len(cc),'checks':cc,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};o['content_sha256']=csha(o);OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(cc)},sort_keys=True))
if __name__=='__main__':main()
