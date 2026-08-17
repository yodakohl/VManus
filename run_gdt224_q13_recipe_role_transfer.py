#!/usr/bin/env python3
"""Apply frozen GDT176 recipe-role instrument to q13 and Herbal-B."""
import csv,hashlib,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
FRAME=R/'gdt046_line_frames.tsv';GROUPS=R/'gdt016_group_state_inventory.tsv';EXT=R/'gdt176_external_role_units.tsv';OLD=R/'gdt176_result.json'
FREEZE=R/'gdt224_prediction_freeze.json';FV=R/'gdt224_freeze_validation.json';METHOD=R/'GDT224_Q13_RECIPE_ROLE_TRANSFER_FREEZE_METHOD.md';REPORT=R/'GDT224_Q13_RECIPE_ROLE_TRANSFER_REPORT.md'
PROJ=R/'gdt224_field_role_projection.tsv';RECS=R/'gdt224_record_role_summary.tsv';SCORES=R/'gdt224_scope_comparison.tsv';NULL=R/'gdt224_null_results.tsv';COUNTER=R/'gdt224_counterexamples.tsv';RESULT=R/'gdt224_result.json'
CLASSES=('OPENER','OPERATION','INGREDIENT','TOOL','CLOSER');AB={'OPENER':'UNRESOLVED_EDGE_CLASS','OPERATION':'INSTRUCTION_CLAUSE_LIKE','INGREDIENT':'SHORT_ARGUMENT_LIKE','TOOL':'SHORT_ARGUMENT_LIKE','CLOSER':'RECORD_CLOSER_LIKE'}
FREEZE_COMMIT='f51a140'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def pn(p):return int(re.match(r'f(\d+)',p).group(1))
def ln(l):return int(l.split('.')[1])
def fit(X,y):
 mean=X.mean(0);scale=X.std(0);scale[scale<1e-9]=1;Z=np.column_stack([np.ones(len(X)),(X-mean)/scale]);Y=np.eye(5)[y];b=np.zeros((5,5));b[0]=np.log(np.bincount(y,minlength=5)/len(y)+1e-12);m=np.zeros_like(b);v=np.zeros_like(b)
 for step in range(1,801):
  z=Z@b;z-=z.max(1,keepdims=True);p=np.exp(z);p/=p.sum(1,keepdims=True);g=Z.T@(p-Y)/len(y);g[1:]+=.001*b[1:];m=.9*m+.1*g;v=.999*v+.001*g*g;mh=m/(1-.9**step);vh=v/(1-.999**step);b-=.03*mh/(np.sqrt(vh)+1e-8)
 return b,mean,scale
def probs(X,model):
 b,m,s=model;Z=np.column_stack([np.ones(len(X)),np.clip((X-m)/s,-4,4)]);z=Z@b;z-=z.max(1,keepdims=True);p=np.exp(z);return p/p.sum(1,keepdims=True)
def js(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);a/=a.sum();b/=b.sum();m=(a+b)/2
 def kl(x,y):return float(sum(v*math.log2(v/w) for v,w in zip(x,y) if v>0 and w>0))
 return (kl(a,m)+kl(b,m))/2
def main():
 freeze=json.loads(FREEZE.read_text());assert freeze['status']=='FROZEN_BEFORE_Q13_FIELD_ROLE_PROJECTION'
 er=read(EXT);X=np.array([[float(r['relative_position']),float(r['relative_position'])**2,math.log2(1+int(r['span_token_count'])),math.log2(1+int(r['record_unit_count']))] for r in er]);y=np.array([CLASSES.index(r['oracle_role']) for r in er]);model=fit(X,y);ep=probs(X,model);external_pred=np.bincount(ep.argmax(1),minlength=5)
 frames=[]
 with FRAME.open() as h:
  for r in csv.DictReader(h,delimiter='\t'):
   if r['page'].startswith('f84'):continue
   if 75<=pn(r['page'])<=83 and r['register']=='OB' and r['hand']=='2':r=dict(r,scope='Q13')
   elif r['register']=='HB' and r['hand']=='2':r=dict(r,scope='HERBAL_B2')
   else:continue
   frames.append(r)
 assert Counter(r['scope'] for r in frames)=={'Q13':240,'HERBAL_B2':61}
 wanted={r['locus'] for r in frames};groups=defaultdict(list)
 with GROUPS.open() as h:
  for r in csv.DictReader(h,delimiter='\t'):
   if r['page'].startswith('f84'):continue
   if r['locus'] in wanted:groups[r['locus']].append(r)
 assert all(len(groups[r['locus']])==int(r['group_count']) for r in frames)
 records=[]
 for scope in ('Q13','HERBAL_B2'):
  for page in sorted({r['page'] for r in frames if r['scope']==scope}):
   lines=sorted((r for r in frames if r['scope']==scope and r['page']==page),key=lambda z:ln(z['locus']));rid=1;current=[]
   for i,line in enumerate(lines):
    if i and line['paragraph_start']=='1':records.append((scope,page,line['physical_folio'],rid,current));rid+=1;current=[]
    current.append(line)
   records.append((scope,page,lines[0]['physical_folio'],rid,current))
 assert Counter(x[0] for x in records)=={'Q13':33,'HERBAL_B2':22}
 units=[]
 for scope,page,folio,rid,lines in records:
  fs=[]
  for line in lines:
   cur=[]
   for g in sorted(groups[line['locus']],key=lambda z:int(z['group_index'])):
    cur.append(g)
    if g['dy_closure']=='1':fs.append((line['locus'],len(fs)+1,cur));cur=[]
   if cur:fs.append((line['locus'],len(fs)+1,cur))
  n=len(fs)
  for i,(locus,_,gg) in enumerate(fs,1):units.append({'scope':scope,'page':page,'physical_folio':folio,'record_id':f'{scope}|{page}|R{rid:02d}','record_ordinal':rid,'field_ordinal':i,'record_field_count':n,'relative_position':i/n,'field_group_count':len(gg),'locus':locus,'line_field_end':'DY' if gg[-1]['dy_closure']=='1' else 'LINE_END'})
 UX=np.array([[u['relative_position'],u['relative_position']**2,math.log2(1+u['field_group_count']),math.log2(1+u['record_field_count'])] for u in units]);up=probs(UX,model)
 proj=[]
 for u,p in zip(units,up):
  role=CLASSES[int(p.argmax())];u['role']=role;u['abstract']=AB[role]
  proj.append({k:u[k] for k in ('scope','page','physical_folio','record_id','record_ordinal','field_ordinal','record_field_count','relative_position','field_group_count','locus','line_field_end')}|{'predicted_role_like':role,'supported_abstract_role_like':AB[role]}|{f'p_{c.lower()}':f'{p[i]:.9f}' for i,c in enumerate(CLASSES)}|{'claim_state':'EXTERNAL_POSITION_LENGTH_ROLE_LIKENESS_ONLY'})
 byrec=defaultdict(list)
 for u in units:byrec[u['record_id']].append(u)
 recrows=[]
 for rid,rr in sorted(byrec.items()):
  rr.sort(key=lambda z:z['field_ordinal']);ab=[z['abstract'] for z in rr];recrows.append({'scope':rr[0]['scope'],'page':rr[0]['page'],'physical_folio':rr[0]['physical_folio'],'record_id':rid,'field_count':len(rr),'mixed_clause_argument':int('INSTRUCTION_CLAUSE_LIKE'in ab and 'SHORT_ARGUMENT_LIKE'in ab),'final_closer_like':int(ab[-1]=='RECORD_CLOSER_LIKE'),'instruction_fields':ab.count('INSTRUCTION_CLAUSE_LIKE'),'argument_fields':ab.count('SHORT_ARGUMENT_LIKE'),'closer_fields':ab.count('RECORD_CLOSER_LIKE'),'unresolved_fields':ab.count('UNRESOLVED_EDGE_CLASS'),'abstract_sequence':'|'.join(ab)})
 def metrics(rows,folio_bal=True):
  if folio_bal:
   folios=sorted({r['physical_folio'] for r in rows});mixed=sum(sum(int(x['mixed_clause_argument']) for x in rows if x['physical_folio']==f)/sum(1 for x in rows if x['physical_folio']==f) for f in folios)/len(folios);closer=sum(sum(int(x['final_closer_like']) for x in rows if x['physical_folio']==f)/sum(1 for x in rows if x['physical_folio']==f) for f in folios)/len(folios)
  else:mixed=sum(int(x['mixed_clause_argument']) for x in rows)/len(rows);closer=sum(int(x['final_closer_like']) for x in rows)/len(rows)
  uc=[u for u in units if u['record_id'] in {r['record_id'] for r in rows}];cc=Counter(u['role'] for u in uc);div=js([cc[c] for c in CLASSES],external_pred)
  return mixed,closer,div
 Q=[r for r in recrows if r['scope']=='Q13'];H=[r for r in recrows if r['scope']=='HERBAL_B2'];qm,qc,qj=metrics(Q);hm,hc,hj=metrics(H);raw=[qm-hm,qc-hc,hj-qj]
 shared=sorted(set(int(r['field_count']) for r in Q)&set(int(r['field_count']) for r in H))
 size_rows=[];sd=[]
 for endpoint in ('MIXED_CLAUSE_ARGUMENT','FINAL_CLOSER','RECIPE_JS_ADVANTAGE'):
  vals=[]
  for n in shared:
   q=[r for r in Q if int(r['field_count'])==n];h=[r for r in H if int(r['field_count'])==n]
   if endpoint=='MIXED_CLAUSE_ARGUMENT':v=sum(int(r['mixed_clause_argument']) for r in q)/len(q)-sum(int(r['mixed_clause_argument']) for r in h)/len(h)
   elif endpoint=='FINAL_CLOSER':v=sum(int(r['final_closer_like']) for r in q)/len(q)-sum(int(r['final_closer_like']) for r in h)/len(h)
   else:v=metrics(h,False)[2]-metrics(q,False)[2]
   vals.append(v)
  sd.append(sum(vals)/len(vals) if vals else 0)
 # LOFO requires all three raw directions after removing one q13 folio.
 lofo=[]
 for f in sorted({r['physical_folio'] for r in Q}):
  qq=[r for r in Q if r['physical_folio']!=f];a,b,c=metrics(qq);ds=[a-hm,b-hc,hj-c];lofo.append({'held_q13_folio':f,'mixed_effect':f'{ds[0]:.12g}','closer_effect':f'{ds[1]:.12g}','recipe_js_advantage':f'{ds[2]:.12g}','all_three_positive':int(all(x>0 for x in ds))})
 # Size-stratified label permutations, record-weighted diagnostic.
 rng=random.Random(224);obs_simple=metrics(Q,False);ctl_simple=metrics(H,False);obs=[obs_simple[0]-ctl_simple[0],obs_simple[1]-ctl_simple[1],ctl_simple[2]-obs_simple[2]];world=[]
 for _ in range(4096):
  qids=set()
  for n in sorted(set(int(r['field_count']) for r in recrows)):
   rr=[r for r in recrows if int(r['field_count'])==n];k=sum(r['scope']=='Q13' for r in rr);ids=[r['record_id'] for r in rr];rng.shuffle(ids);qids.update(ids[:k])
  q=[r for r in recrows if r['record_id'] in qids];h=[r for r in recrows if r['record_id'] not in qids];a=metrics(q,False);b=metrics(h,False);world.append([a[0]-b[0],a[1]-b[1],b[2]-a[2]])
 ps=[sum(w[i]>=obs[i]-1e-15 for w in world)/len(world) for i in range(3)];means=[sum(w[i] for w in world)/len(world) for i in range(3)];ss=[(sum((w[i]-means[i])**2 for w in world)/len(world))**.5 or 1 for i in range(3)];oz=[(obs[i]-means[i])/ss[i] for i in range(3)];mx=[max((w[i]-means[i])/ss[i] for i in range(3)) for w in world];maxp=[sum(x>=oz[i]-1e-15 for x in mx)/len(mx) for i in range(3)]
 names=('MIXED_CLAUSE_ARGUMENT','FINAL_CLOSER','RECIPE_JS_ADVANTAGE');score=[];null=[]
 for i,n in enumerate(names):score.append({'endpoint':n,'q13_value':f'{(qm,qc,qj)[i]:.12g}','herbal_b2_value':f'{(hm,hc,hj)[i]:.12g}','raw_directional_effect':f'{raw[i]:.12g}','exact_size_controlled_effect':f'{sd[i]:.12g}','raw_direction_hit':int(raw[i]>0),'size_direction_hit':int(sd[i]>0)});null.append({'endpoint':n,'worlds':4096,'record_weighted_observed_effect':f'{obs[i]:.12g}','local_p':f'{ps[i]:.12g}','max_three_p':f'{maxp[i]:.12g}'})
 write(PROJ,proj);write(RECS,recrows);write(SCORES,score);write(NULL,null)
 gates={'all_three_raw_directions':all(x>0 for x in raw),'at_least_two_size_directions':sum(x>0 for x in sd)>=2,'at_least_eight_lofo_all_three':sum(int(x['all_three_positive']) for x in lofo)>=8};status='Q13_RECIPE_ROLE_ARCHITECTURE_PROVISIONAL' if all(gates.values()) else 'Q13_RECIPE_ROLE_ARCHITECTURE_WEAK_OR_GENERIC' if any(x>0 for x in raw) else 'Q13_RECIPE_ROLE_ARCHITECTURE_NOT_SUPPORTED'
 counter=[{'counterexample':'POSITION_LENGTH_ONLY','value':'4_FEATURES','detail':'The role instrument sees only field position and span; it cannot identify content.'},{'counterexample':'HERBAL_CONTROL','value':json.dumps({'mixed':hm,'closer':hc,'js':hj},sort_keys=True,separators=(',',':')),'detail':'Same-hand Herbal-B receives the identical external projection.'},{'counterexample':'EDITORIAL_RECORDS','value':'33_Q13_22_HERBAL','detail':'Records begin at page starts and editor-marked paragraph starts, not translated authorial headings.'},{'counterexample':'FIELD_RULE','value':'DY_OR_LINE_END','detail':'Fields are formal HPR2-like segments; this is not a linguistic word or clause boundary.'},{'counterexample':'CLASS_LIMIT','value':'TOOL_AND_OPENER_UNRECOVERED','detail':'External calibration cannot distinguish tools from ingredients and nearly fails openers.'}]
 write(COUNTER,counter)
 result={'schema':'GDT224_Q13_RECIPE_ROLE_TRANSFER_RESULT_V1','status':status,'freeze_commit':FREEZE_COMMIT,'external_training_units':len(er),'external_predicted_class_counts':dict(zip(CLASSES,map(int,external_pred))),'target':{'records':len(Q),'fields':sum(int(r['field_count']) for r in Q),'folios':9},'control':{'records':len(H),'fields':sum(int(r['field_count']) for r in H),'folios':10},'raw_effects':dict(zip(names,raw)),'exact_size_controlled_effects':dict(zip(names,sd)),'shared_exact_record_sizes':shared,'lofo_all_three_positive':sum(int(x['all_three_positive']) for x in lofo),'lofo_positive_by_endpoint':{names[i]:sum(float(x[('mixed_effect','closer_effect','recipe_js_advantage')[i]])>0 for x in lofo) for i in range(3)},'lofo_total':len(lofo),'lofo':lofo,'gates':gates,'interpretation':'q13 has a recipe-like aggregate clause/argument balance but lacks the expected final closer architecture; this is a partial position-length scaffold, not lexical semantics.','claim_ceiling':'Coarse position-length record-role likeness only; no ingredient tool action object source-group role word language plaintext or translation.','f84':{'accessed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (FRAME,GROUPS,EXT,OLD,FREEZE,FV)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (PROJ,RECS,SCORES,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'raw':raw,'size':sd,'lofo':result['lofo_all_three_positive'],'q_fields':result['target']['fields'],'h_fields':result['control']['fields']},sort_keys=True))
if __name__=='__main__':main()
