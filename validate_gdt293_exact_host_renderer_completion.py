#!/usr/bin/env python3
"""Independent reconstruction of GDT293 scores, nulls, and decision."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt293_result.json';OUT=R/'gdt293_validation.json';COMP=('wrapper','local_frame','inner_d','right_family','dy_closure','b3');ENDS=('JOINT_RENDERER',)+tuple(x.upper() for x in COMP);MODELS=('LAYOUT_CONTEXT','EXACT_HOST');ALPHA=.5
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=3e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def ob(x):
 n=int(x);return '1' if n==1 else '2' if n==2 else '3_4' if n<=4 else '5_PLUS'
def pos(r):
 i=int(r['group_index']);n=int(r['group_count']);return 'ONLY' if n==1 else 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def layout(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],ob(r['record_ordinal']),ob(r['field_ordinal']),pos(r),int(r['host_length']))
def values(r):
 q={x.upper():r[x] for x in COMP};q['JOINT_RENDERER']='|'.join(r[x] for x in COMP);return q
def nkey(r):return (r['physical_folio'],)+layout(r)
def rebuild(ev,split='physical_folio',prior=11.,retain=False):
 alphabet={e:sorted({values(r)[e] for r in ev}) for e in ENDS};rank={e:{x:i for i,x in enumerate(alphabet[e])} for e in ENDS};folds=defaultdict(list)
 for i,r in enumerate(ev):folds[r[split]].append(i)
 bits=defaultdict(Counter);top=defaultdict(Counter);fr=[];pred=[];fg={};eligible_total=0
 for held,test in sorted(folds.items()):
  train=[i for i,r in enumerate(ev) if r[split]!=held];th=Counter(ev[i]['page_host'] for i in train);g={e:Counter() for e in ENDS};lc={e:defaultdict(Counter) for e in ENDS};hc={e:defaultdict(Counter) for e in ENDS}
  for i in train:
   r=ev[i];q=values(r)
   for e in ENDS:g[e][q[e]]+=1;lc[e][layout(r)][q[e]]+=1;hc[e][r['page_host']][q[e]]+=1
  test=[i for i in test if th[ev[i]['page_host']]>0];eligible_total+=len(test);fb=defaultdict(Counter);ft=defaultdict(Counter)
  for i in test:
   r=ev[i];q=values(r);jp=None
   for e in ENDS:
    pp={m:{} for m in MODELS};K=len(alphabet[e])
    for y in alphabet[e]:
     p0=(g[e][y]+ALPHA)/(len(train)+ALPHA*K);a=lc[e][layout(r)];pl=(a[y]+prior*p0)/(sum(a.values())+prior);a=hc[e][r['page_host']];ph=(a[y]+prior*pl)/(sum(a.values())+prior);pp['LAYOUT_CONTEXT'][y]=pl;pp['EXACT_HOST'][y]=ph
    for m in MODELS:
     z=-math.log2(pp[m][q[e]]);bits[e][m]+=z;fb[e][m]+=z;hit=int(max(alphabet[e],key=lambda y:(pp[m][y],-rank[e][y]))==q[e]);top[e][m]+=hit;ft[e][m]+=hit
    if e=='JOINT_RENDERER':jp=pp
   if retain:pred.append((q['JOINT_RENDERER'],jp['LAYOUT_CONTEXT'],jp['EXACT_HOST'],nkey(r)))
  fg[held]=fb['JOINT_RENDERER']['LAYOUT_CONTEXT']-fb['JOINT_RENDERER']['EXACT_HOST']
  for e in ENDS:
   for m in MODELS:fr.append((held,e,m,len(test),fb[e][m],ft[e][m]))
 return {'alphabet':alphabet,'bits':{e:dict(bits[e]) for e in ENDS},'top':{e:dict(top[e]) for e in ENDS},'folds':fr,'pred':pred,'folio_gain':fg,'n':eligible_total}
def gain(q,e='JOINT_RENDERER'):return (q['bits'][e]['LAYOUT_CONTEXT']-q['bits'][e]['EXACT_HOST'])/q['n']
def null(q,panel,worlds):
 st=defaultdict(list)
 for i,x in enumerate(q['pred']):st[x[3]].append(i)
 out=[];mobile=0;swap=sum(len(v) for v in st.values() if len(v)>1)
 for world in range(worlds):
  yy=[x[0] for x in q['pred']]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT293_HELD_RENDERER_ALIGNMENT|{panel}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[yy[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=yy[i]:mobile+=1
    yy[i]=x
  out.append(sum(math.log2(x[2][y]/x[1][y]) for x,y in zip(q['pred'],yy))/q['n'])
 return out,mobile,swap
def task(item):
 p,e,w=item;q=rebuild(e,retain=True);n,m,s=null(q,p,w);return p,q,n,m,s
def main():
 cc=[]
 def ck(n,v):cc.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt293_design.json').read_text());res=json.loads(RESULT.read_text());pt=rows(R/'gdt293_panel_scores.tsv');ft=rows(R/'gdt293_folio_scores.tsv');nt=rows(R/'gdt293_null_results.tsv');st=rows(R/'gdt293_voynich_sensitivities.tsv');ck('design',d['content_sha256']==csha(d) and d['status']=='FROZEN_BEFORE_GDT293_SCORING');mf=rows(R/'gdt293_freeze_manifest.tsv');ck('freeze',len(mf)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};ck('events',all(len(v)==8448 for v in panels.values()));ck('table_shapes',len(pt)==112 and len(nt)==512 and len(st)==4)
 rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(task,(p,e,d['null_worlds'])):p for p,e in panels.items()}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z[1:]
 obs={};means={};sds={}
 for p in d['panels']:
  q,n,mob,swap=rr[p];obs[p]=gain(q);means[p]=statistics.mean(n);sds[p]=statistics.pstdev(n);tab=[x for x in pt if x['control_id']==p];ck('panel_shape:'+p,len(tab)==14)
  for e in ENDS:
   for model in MODELS:
    x=next(x for x in tab if x['endpoint']==e and x['model']==model);ck('score:'+p+':'+e+':'+model,int(x['eligible_events'])==q['n'] and int(x['classes'])==len(q['alphabet'][e]) and close(x['bits'],q['bits'][e][model]) and int(x['top1'])==q['top'][e][model])
  stored=[x for x in ft if x['control_id']==p];ck('fold_shape:'+p,len(stored)==len(q['folds']));ck('fold_values:'+p,all(int(next(x for x in stored if x['held_value']==h and x['endpoint']==e and x['model']==m)['eligible_events'])==nn and close(next(x for x in stored if x['held_value']==h and x['endpoint']==e and x['model']==m)['bits'],b) and int(next(x for x in stored if x['held_value']==h and x['endpoint']==e and x['model']==m)['top1'])==t for h,e,m,nn,b,t in q['folds']));sn=sorted((x for x in nt if x['control_id']==p),key=lambda x:int(x['world_index']));ck('null:'+p,len(sn)==64 and all(close(x['joint_gain_bits_per_event'],v) for x,v in zip(sn,n)));s=next(x for x in res['summary'] if x['control_id']==p);cg={e:gain(q,e) for e in ENDS[1:]};ck('summary:'+p,close(s['joint_gain_bits_per_event'],obs[p]) and close(s['null_mean'],means[p]) and close(s['null_sd'],sds[p]) and int(s['eligible_events'])==q['n'] and int(s['joint_classes'])==len(q['alphabet']['JOINT_RENDERER']) and int(s['positive_components'])==sum(v>0 for v in cg.values()) and int(s['positive_folios'])==sum(v>0 for v in q['folio_gain'].values()) and int(s['null_mobile_events_world0'])==mob and int(s['null_swappable_events'])==swap and all(close(s['component_gains'][e],v) for e,v in cg.items()))
 variable=[p for p in d['panels'] if sds[p]>1e-15];z={p:(obs[p]-means[p])/sds[p] for p in variable};mx=[max((rr[p][1][i]-means[p])/sds[p] for p in variable) for i in range(64)]
 for p in d['panels']:
  s=next(x for x in res['summary'] if x['control_id']==p)
  if p in variable:
   lp=(1+sum(v>=obs[p]-1e-15 for v in rr[p][1]))/65;mp=(1+sum(v>=z[p]-1e-15 for v in mx))/65;ck('pvalues:'+p,close(s['observed_z'],z[p]) and close(s['local_p'],lp) and close(s['max_variable_family_p'],mp))
  else:ck('pvalues:'+p,s['observed_z']==s['local_p']==s['max_variable_family_p']=='NA_ZERO_NULL_VARIANCE')
 ck('panel_lists',res['variable_null_panels']==variable and res['zero_null_variance_panels']==[p for p in d['panels'] if p not in variable]);voy=panels['VOYNICH_REFERENCE']
 for prior in d['voynich_prior_sensitivities']:
  q=rebuild(voy,prior=prior);x=next(x for x in res['voynich_sensitivities'] if x['split']=='HELD_PHYSICAL_FOLIO' and float(x['prior_mass'])==prior);ck('prior:'+str(prior),int(x['eligible_events'])==q['n'] and close(x['joint_gain_bits_per_event'],gain(q)))
 for split in ('section','hand'):
  q=rebuild(voy,split=split);x=next(x for x in res['voynich_sensitivities'] if x['split']=='HELD_'+split.upper());ck('split:'+split,int(x['eligible_events'])==q['n'] and close(x['joint_gain_bits_per_event'],gain(q)))
 v=res['voynich_summary'];sg={x['split']:float(x['joint_gain_bits_per_event']) for x in res['voynich_sensitivities']};gates={'joint_gain_positive':float(v['joint_gain_bits_per_event'])>0,'at_least_four_of_six_components_positive':int(v['positive_components'])>=4,'at_least_sixty_of_ninety_one_folios_positive':int(v['folios'])==91 and int(v['positive_folios'])>=60,'held_section_gain_positive':sg['HELD_SECTION']>0,'held_hand_gain_positive':sg['HELD_HAND']>0,'maxT_p_le_0_05':float(v['max_variable_family_p'])<=.05};status=d['decision']['support'] if all(gates.values()) else d['decision']['fail'];ck('decision',res['frozen_gates']==gates and res['status']==status);ck('next_host_not_rerun',res['prior_next_host_result']=='GDT165_NEGATIVE_NOT_RERUN');ck('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('content',res['content_sha256']==csha(res));ck('hashes',all(sha(R/k)==v for sec in ('inputs','documents','implementation','outputs') for k,v in res[sec].items()));ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));out={'schema':'GDT293_EXACT_HOST_RENDERER_COMPLETION_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_ALL_PANEL_JOINT_AND_COMPONENT_FOLDS_NULLS_MAXT_VOYNICH_PRIORS_SECTION_HAND_DECISION_AND_HASHES','checks_passed':len(cc),'checks_total':len(cc),'checks':cc,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(cc)},sort_keys=True))
if __name__=='__main__':main()
