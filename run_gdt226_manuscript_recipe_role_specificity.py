#!/usr/bin/env python3
"""Apply the frozen GDT176 role instrument across six non-f84 Voynich scopes."""
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
FRAME=R/'gdt046_line_frames.tsv';GROUPS=R/'gdt016_group_state_inventory.tsv';EXT=R/'gdt176_external_role_units.tsv';OLD=R/'gdt176_result.json';G224=R/'gdt224_result.json';FREEZE=R/'gdt226_prediction_freeze.json';FV=R/'gdt226_freeze_validation.json';METHOD=R/'GDT226_MANUSCRIPT_RECIPE_ROLE_SPECIFICITY_FREEZE_METHOD.md';REPORT=R/'GDT226_MANUSCRIPT_RECIPE_ROLE_SPECIFICITY_REPORT.md'
PROJ=R/'gdt226_field_role_projection.tsv';PROFILES=R/'gdt226_scope_profiles.tsv';PAIR=R/'gdt226_pairwise_distances.tsv';SIZE=R/'gdt226_size_matched.tsv';LOFO=R/'gdt226_lofo.tsv';COUNTER=R/'gdt226_counterexamples.tsv';RESULT=R/'gdt226_result.json';FREEZE_COMMIT='80181f9'
CLASSES=('OPENER','OPERATION','INGREDIENT','TOOL','CLOSER');AB={'OPENER':'UNRESOLVED_EDGE_CLASS','OPERATION':'INSTRUCTION_CLAUSE_LIKE','INGREDIENT':'SHORT_ARGUMENT_LIKE','TOOL':'SHORT_ARGUMENT_LIKE','CLOSER':'RECORD_CLOSER_LIKE'}
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def pn(p):return int(re.match(r'f(\d+)',p).group(1))
def ln(l):return int(l.split('.')[1])
def scope(r):
 if r['register']=='HA':return 'HERBAL_A'
 if r['register']=='HB':return 'HERBAL_B'
 if r['register']=='SB':return 'STARS_B'
 if r['register']=='OA':return 'OTHER_A'
 if r['register']=='OB' and 75<=pn(r['page'])<=83:return 'Q13'
 if r['register']=='OB':return 'OTHER_B'
 raise AssertionError(r['register'])
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
 freeze=json.loads(FREEZE.read_text());assert freeze['status']=='FROZEN_BEFORE_SIX_SCOPE_ROLE_PROJECTION'
 er=read(EXT);X=np.array([[float(r['relative_position']),float(r['relative_position'])**2,math.log2(1+int(r['span_token_count'])),math.log2(1+int(r['record_unit_count']))] for r in er]);y=np.array([CLASSES.index(r['oracle_role']) for r in er]);model=fit(X,y);ep=probs(X,model);external=np.bincount(ep.argmax(1),minlength=5)
 frames=[]
 with FRAME.open(encoding='utf8',newline='') as h:
  for r in csv.DictReader(h,delimiter='\t'):
   if r['page'].startswith('f84'):continue
   frames.append(dict(r,scope=scope(r)))
 assert Counter(r['scope'] for r in frames)==Counter(freeze['line_counts'])
 wanted={r['locus'] for r in frames};groups=defaultdict(list)
 with GROUPS.open(encoding='utf8',newline='') as h:
  for r in csv.DictReader(h,delimiter='\t'):
   if r['page'].startswith('f84'):continue
   if r['locus'] in wanted:groups[r['locus']].append(r)
 assert all(len(groups[r['locus']])==int(r['group_count']) for r in frames)
 records=[]
 for sc in sorted({r['scope'] for r in frames}):
  for page in sorted({r['page'] for r in frames if r['scope']==sc},key=lambda p:(pn(p),p)):
   lines=sorted((r for r in frames if r['scope']==sc and r['page']==page),key=lambda z:ln(z['locus']));rid=1;cur=[]
   for i,line in enumerate(lines):
    if i and line['paragraph_start']=='1':records.append((sc,page,line['physical_folio'],rid,cur));rid+=1;cur=[]
    cur.append(line)
   records.append((sc,page,lines[0]['physical_folio'],rid,cur))
 units=[]
 for sc,page,folio,rid,lines in records:
  fields=[]
  for line in lines:
   cur=[]
   for g in sorted(groups[line['locus']],key=lambda z:int(z['group_index'])):
    cur.append(g)
    if g['dy_closure']=='1':fields.append((line['locus'],cur));cur=[]
   if cur:fields.append((line['locus'],cur))
  n=len(fields);record_id=f'{sc}|{page}|R{rid:02d}'
  for i,(locus,gg) in enumerate(fields,1):units.append({'scope':sc,'page':page,'physical_folio':folio,'record_id':record_id,'field_ordinal':i,'record_field_count':n,'relative_position':i/n,'field_group_count':len(gg),'locus':locus,'line_field_end':'DY' if gg[-1]['dy_closure']=='1' else 'LINE_END'})
 UX=np.array([[u['relative_position'],u['relative_position']**2,math.log2(1+u['field_group_count']),math.log2(1+u['record_field_count'])] for u in units]);up=probs(UX,model)
 projection=[]
 for u,p in zip(units,up):
  role=CLASSES[int(p.argmax())];u['role']=role;u['abstract']=AB[role];projection.append({k:u[k] for k in ('scope','page','physical_folio','record_id','field_ordinal','record_field_count','relative_position','field_group_count','locus','line_field_end')}|{'predicted_role_like':role,'supported_abstract_role_like':AB[role]}|{f'p_{c.lower()}':f'{p[i]:.9f}' for i,c in enumerate(CLASSES)}|{'claim_state':'EXTERNAL_POSITION_LENGTH_ROLE_LIKENESS_ONLY'})
 scopes=sorted({u['scope'] for u in units});counts={s:np.array([sum(u['scope']==s and u['role']==c for u in units) for c in CLASSES]) for s in scopes};div={s:js(counts[s],external) for s in scopes};rank={s:i+1 for i,s in enumerate(sorted(scopes,key=lambda z:(div[z],z)))}
 profiles=[]
 for s in sorted(scopes,key=lambda z:rank[z]):
  rr=[r for r in records if r[0]==s];profiles.append({'scope':s,'lines':sum(1 for x in frames if x['scope']==s),'pages':len({x['page'] for x in frames if x['scope']==s}),'folios':len({x['physical_folio'] for x in frames if x['scope']==s}),'records':len(rr),'fields':int(counts[s].sum()),**{c.lower()+'_fields':int(counts[s][i]) for i,c in enumerate(CLASSES)},'recipe_js_divergence':f'{div[s]:.12g}','recipe_js_rank':rank[s]})
 pairs=[];pd={}
 for i,a in enumerate(scopes):
  for b in scopes[i+1:]:
   d=js(counts[a],counts[b]);pd[tuple(sorted((a,b)))]=d;pairs.append({'scope_a':a,'scope_b':b,'js_divergence':f'{d:.12g}','includes_q13':int('Q13' in (a,b))})
 size=[];size_summary={}
 q_sizes={u['record_field_count'] for u in units if u['scope']=='Q13'}
 for s in scopes:
  if s=='Q13':continue
  shared=sorted(q_sizes&{u['record_field_count'] for u in units if u['scope']==s});effects=[]
  for n in shared:
   qc=np.array([sum(u['scope']=='Q13' and u['record_field_count']==n and u['role']==c for u in units) for c in CLASSES]);sc=np.array([sum(u['scope']==s and u['record_field_count']==n and u['role']==c for u in units) for c in CLASSES]);qj=js(qc,external);sj=js(sc,external);effects.append(sj-qj);size.append({'comparator_scope':s,'exact_record_field_count':n,'q13_records':len({u['record_id'] for u in units if u['scope']=='Q13' and u['record_field_count']==n}),'comparator_records':len({u['record_id'] for u in units if u['scope']==s and u['record_field_count']==n}),'q13_recipe_js':f'{qj:.12g}','comparator_recipe_js':f'{sj:.12g}','q13_advantage':f'{sj-qj:.12g}'})
  size_summary[s]={'shared_size_strata':len(shared),'mean_q13_advantage':sum(effects)/len(effects) if effects else 0,'positive_strata':sum(x>0 for x in effects)}
 qnear=min((s for s in scopes if s!='Q13'),key=lambda s:(pd[tuple(sorted(('Q13',s)))],s))
 basehits={'P1':div['Q13']<div['HERBAL_A'] and div['Q13']<div['HERBAL_B'],'P2':rank['Q13']<=2,'P3':qnear=='STARS_B'}
 lofo=[]
 for f in sorted({u['physical_folio'] for u in units if u['scope']=='Q13'}):
  qc=np.array([sum(u['scope']=='Q13' and u['physical_folio']!=f and u['role']==c for u in units) for c in CLASSES]);qd=js(qc,external);dr={s:(qd if s=='Q13' else div[s]) for s in scopes};qr=1+sum(dr[s]<qd-1e-15 for s in scopes if s!='Q13');nearest=min((s for s in scopes if s!='Q13'),key=lambda s:(js(qc,counts[s]),s));p1=qd<div['HERBAL_A'] and qd<div['HERBAL_B'];p2=qr<=2;p3=nearest=='STARS_B';lofo.append({'held_q13_folio':f,'q13_recipe_js':f'{qd:.12g}','q13_rank':qr,'nearest_other_scope':nearest,'p1_hit':int(p1),'p2_hit':int(p2),'p3_hit':int(p3),'all_three_hit':int(p1 and p2 and p3)})
 gates=basehits|{'at_least_eight_lofo':sum(int(x['all_three_hit']) for x in lofo)>=8};status='Q13_RECIPE_ROLE_SPECIFICITY_PROVISIONAL' if all(gates.values()) else 'Q13_RECIPE_ROLE_LIKENESS_GENERIC_OR_UNSTABLE'
 counter=[{'counterexample':'POSITION_LENGTH_DETERMINISM','value':'4_FEATURES','detail':'Every projected class is determined only by record position and field span.'},{'counterexample':'EDITORIAL_RECORD_BOUNDARY','value':'PAGE_OR_PARAGRAPH_START','detail':'Record boundaries use editor paragraph starts and are not translated authorial headings.'},{'counterexample':'PRIOR_EXPOSURE','value':'GDT224_AND_GDT176','detail':'Q13 versus Herbal-B and the published Stars projection were known before this synthesis.'},{'counterexample':'SCOPE_REGISTER_CONFOUND','value':'B_SCOPES_RANK_1_TO_4_A_SCOPES_RANK_5_TO_6','detail':'All Currier-B scopes outrank both A scopes, so register and content are not separated.'},{'counterexample':'SIZE_MATCH_REVERSAL','value':f"STARS_{size_summary['STARS_B']['mean_q13_advantage']:.6f}_OTHER_B_{size_summary['OTHER_B']['mean_q13_advantage']:.6f}",'detail':'After exact record-size matching q13 is farther from the recipe profile than Stars-B and Other-B on average.'},{'counterexample':'OTHER_B_LOW_CAPACITY','value':f"{sum(x[0]=='OTHER_B' for x in records)}_RECORDS_{freeze['folio_counts']['OTHER_B']}_FOLIOS",'detail':'The non-q13 Other-B comparator has only three physical folios.'},{'counterexample':'NO_LEXICAL_ENDPOINT','value':'ZERO','detail':'No token host wrapper family or visual annotation enters the score.'}]
 write(PROJ,projection);write(PROFILES,profiles);write(PAIR,pairs);write(SIZE,size);write(LOFO,lofo);write(COUNTER,counter)
 result={'schema':'GDT226_MANUSCRIPT_RECIPE_ROLE_SPECIFICITY_RESULT_V1','status':status,'secondary_status':'REGISTER_AND_RECORD_SIZE_CONFOUNDED','freeze_commit':FREEZE_COMMIT,'external_training_units':len(er),'external_predicted_class_counts':dict(zip(CLASSES,map(int,external))),'scope_profiles':{x['scope']:{k:(float(v) if k=='recipe_js_divergence' else int(v) if k not in ('scope',) else v) for k,v in x.items() if k!='scope'} for x in profiles},'size_matched_sensitivity':size_summary,'q13_recipe_js_rank':rank['Q13'],'q13_nearest_other_scope':qnear,'q13_nearest_other_js':pd[tuple(sorted(('Q13',qnear)))],'prediction_hits':basehits,'lofo_all_three_hits':sum(int(x['all_three_hit']) for x in lofo),'lofo_total':len(lofo),'gates':gates,'interpretation':'q13 and Stars-B share a recipe-like position-length architecture, but Currier/register and record-size confounding prevent semantic identification.','claim_ceiling':'Manuscript-scope position-length architecture only; no ingredient tool action object token word language plaintext or translation.','f84':{'public_metadata_previously_exposed':True,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False},'inputs':{p.name:sha(p) for p in (FRAME,GROUPS,EXT,OLD,G224,FREEZE,FV)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (PROJ,PROFILES,PAIR,SIZE,LOFO,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'q13_rank':rank['Q13'],'q13_nearest':qnear,'hits':basehits,'lofo':result['lofo_all_three_hits'],'profiles':{s:round(div[s],6) for s in scopes}},sort_keys=True))
if __name__=='__main__':main()
