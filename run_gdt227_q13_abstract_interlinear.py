#!/usr/bin/env python3
"""Build a nonsemantic q13 field interlinear and exact-identity role atlas."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt016_group_state_inventory.tsv';PROJ=R/'gdt226_field_role_projection.tsv';OLD=R/'gdt226_result.json';METHOD=R/'GDT227_Q13_ABSTRACT_INTERLINEAR_METHOD.md';REPORT=R/'GDT227_Q13_ABSTRACT_INTERLINEAR_REPORT.md';INTER=R/'gdt227_q13_abstract_interlinear.tsv';ATLAS=R/'gdt227_identity_role_atlas.tsv';TRANSFER=R/'gdt227_cross_register_transfer.tsv';COUNTER=R/'gdt227_counterexamples.tsv';RESULT=R/'gdt227_result.json'
RIGHT=('aiin','air','ain','ar','al');ROLES=('INSTRUCTION_CLAUSE_LIKE','SHORT_ARGUMENT_LIKE','RECORD_CLOSER_LIKE','UNRESOLVED_EDGE_CLASS')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def pre(r):
 h=r['residual_host'];b3=int(h.endswith('m') and len(h)>1);h=h[:-1] if b3 else h;right='NONE'
 for s in RIGHT:
  if h.endswith(s) and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(r['stripped_prefix'] in {'ch','che','sh'} and h.startswith('d') and len(h)>1);h=h[1:] if inner else h
 return h,b3,right,inner
def main():
 projection=[x for x in read(PROJ) if x['scope'] in ('Q13','STARS_B')];assert projection and not any(x['page'].startswith('f84') for x in projection);wanted={x['locus'] for x in projection};source=[]
 with SOURCE.open(encoding='utf8') as h:
  header=h.readline().rstrip('\n').split('\t')
  for line in h:
   if line.startswith('f84'):continue
   x=dict(zip(header,line.rstrip('\n').split('\t')))
   source.append(x)
 counts=Counter(pre(x)[0] for x in source);licensed={h for h in counts if counts[h] and counts['o'+h] and counts['ot'+h]}|{'ar','al','ol'}
 def parse(x):
  h,b3,right,inner=pre(x);frame='NONE'
  if h.startswith('ot') and h[2:] in licensed:h=h[2:];frame='OT'
  elif h.startswith('o') and h[1:] in licensed:h=h[1:];frame='O'
  return {'page_host':h or 'EMPTY','b3':b3,'right':right,'inner_d':inner,'frame':frame,'wrapper':x['stripped_prefix']}
 byloc=defaultdict(list)
 for x in source:
  if x['locus'] in wanted:byloc[x['locus']].append(x)
 role_by_field={(x['record_id'],int(x['field_ordinal'])):x for x in projection};field_groups=defaultdict(list)
 for x in projection:
  line=sorted(byloc[x['locus']],key=lambda z:int(z['group_index']));fields=[];cur=[]
  for g in line:
   cur.append(g)
   if g['dy_closure']=='1':fields.append(cur);cur=[]
  if cur:fields.append(cur)
  same=[z for z in projection if z['record_id']==x['record_id'] and z['locus']==x['locus']]
  for z,gg in zip(same,fields):field_groups[(z['record_id'],int(z['field_ordinal']))]=gg
 assert set(field_groups)==set(role_by_field)
 inter=[];occ=[]
 for key,x in sorted(role_by_field.items()):
  gg=field_groups[key];pp=[parse(g) for g in gg];sc=x['scope'];role=x['supported_abstract_role_like'];inter.append({'scope':sc,'page':x['page'],'physical_folio':x['physical_folio'],'record_id':x['record_id'],'field_ordinal':x['field_ordinal'],'record_field_count':x['record_field_count'],'relative_position':x['relative_position'],'field_group_count':x['field_group_count'],'locus':x['locus'],'line_field_end':x['line_field_end'],'abstract_role_like':role,'source_tokens':'|'.join(g['token'] for g in gg),'page_hosts':'|'.join(p['page_host'] for p in pp),'compiler_cells':'|'.join(f"{p['wrapper']}:{p['frame']}:{p['inner_d']}:{p['right']}:{g['dy_closure']}:{p['b3']}" for p,g in zip(pp,gg)),'claim_state':'OPAQUE_ABSTRACT_INTERLINEAR_NO_GLOSS'})
  for g,p in zip(gg,pp):
   for level,val in (('RAW_TOKEN',g['token']),('PAGE_HOST',p['page_host'])):occ.append({'scope':sc,'page':x['page'],'folio':x['physical_folio'],'record':x['record_id'],'field':x['field_ordinal'],'role':role,'level':level,'identity':val})
 def modal(z):
  c=Counter(x['role'] for x in z);return min(ROLES,key=lambda a:(-c[a],a)),c
 atlas=[]
 for sc in ('Q13','STARS_B'):
  for level in ('RAW_TOKEN','PAGE_HOST'):
   for ident in sorted({x['identity'] for x in occ if x['scope']==sc and x['level']==level}):
    z=[x for x in occ if x['scope']==sc and x['level']==level and x['identity']==ident];m,c=modal(z);atlas.append({'scope':sc,'identity_level':level,'identity':ident,'occurrences':len(z),'fields':len({(x['record'],x['field']) for x in z}),'pages':len({x['page'] for x in z}),'folios':len({x['folio'] for x in z}),'instruction':c['INSTRUCTION_CLAUSE_LIKE'],'argument':c['SHORT_ARGUMENT_LIKE'],'closer':c['RECORD_CLOSER_LIKE'],'unresolved':c['UNRESOLVED_EDGE_CLASS'],'dominant_role':m,'dominant_purity':f'{c[m]/len(z):.12g}','cross_folio':int(len({x['folio'] for x in z})>=2)})
 transfer=[];summary={}
 for level in ('RAW_TOKEN','PAGE_HOST'):
  for train_scope,test_scope in (('Q13','STARS_B'),('STARS_B','Q13')):
   pred=correct=baseline=0;covered=set();train_all=[x for x in occ if x['scope']==train_scope and x['level']==level];prior=modal(train_all)[0]
   for f in sorted({x['folio'] for x in occ if x['scope']==test_scope and x['level']==level}):
    train=train_all;test=[x for x in occ if x['scope']==test_scope and x['level']==level and x['folio']==f];modes={i:modal([x for x in train if x['identity']==i])[0] for i in {x['identity'] for x in train}}
    for x in test:
     if x['identity'] in modes:pred+=1;correct+=modes[x['identity']]==x['role'];baseline+=prior==x['role'];covered.add(x['identity'])
   acc=correct/pred if pred else 0;base=baseline/pred if pred else 0;transfer.append({'identity_level':level,'train_scope':train_scope,'test_scope':test_scope,'predictions':pred,'correct':correct,'accuracy':f'{acc:.12g}','training_prior_correct':baseline,'training_prior_accuracy':f'{base:.12g}','gain_over_training_prior':f'{acc-base:.12g}','shared_identities':len(covered)})
   summary[f'{level}_{train_scope}_TO_{test_scope}']={'predictions':pred,'correct':correct,'accuracy':acc,'training_prior_accuracy':base,'gain_over_training_prior':acc-base,'shared_identities':len(covered)}
 # Within-q13 leave-one-folio exact-identity role placement.
 for level in ('RAW_TOKEN','PAGE_HOST'):
  pred=correct=baseline=0;ids=set()
  for f in sorted({x['folio'] for x in occ if x['scope']=='Q13' and x['level']==level}):
   train=[x for x in occ if x['scope']=='Q13' and x['level']==level and x['folio']!=f];test=[x for x in occ if x['scope']=='Q13' and x['level']==level and x['folio']==f];modes={i:modal([x for x in train if x['identity']==i])[0] for i in {x['identity'] for x in train}};prior=modal(train)[0]
   for x in test:
    if x['identity'] in modes:pred+=1;correct+=modes[x['identity']]==x['role'];baseline+=prior==x['role'];ids.add(x['identity'])
  acc=correct/pred if pred else 0;base=baseline/pred if pred else 0;transfer.append({'identity_level':level,'train_scope':'Q13_OTHER_FOLIOS','test_scope':'Q13_HELD_FOLIO','predictions':pred,'correct':correct,'accuracy':f'{acc:.12g}','training_prior_correct':baseline,'training_prior_accuracy':f'{base:.12g}','gain_over_training_prior':f'{acc-base:.12g}','shared_identities':len(ids)});summary[f'{level}_Q13_LOFO']={'predictions':pred,'correct':correct,'accuracy':acc,'training_prior_accuracy':base,'gain_over_training_prior':acc-base,'shared_identities':len(ids)}
 counter=[{'counterexample':'ROLE_IS_POSITION_LENGTH_DERIVED','value':'YES','detail':'Identity placement predicts a projected class, not external semantic truth.'},{'counterexample':'Q13_STARS_HAND_SECTION_CONFOUND','value':'Q13_HAND2_STARS_HAND3_DOMINANT','detail':'Cross-register placement cannot separate content from hand or section.'},{'counterexample':'EXACT_IDENTITY_COVERAGE','value':json.dumps(summary,sort_keys=True,separators=(',',':')),'detail':'Only occurrences whose exact identity is present in training receive a prediction.'},{'counterexample':'MULTIPLE_GROUP_WEIGHTING','value':str(len(occ)//2),'detail':'Identity placement is group-weighted; fields with more groups contribute more observations.'},{'counterexample':'NO_VISUAL_ORACLE','value':'ZERO','detail':'No diagram or semantic annotation is joined.'}]
 write(INTER,[x for x in inter if x['scope']=='Q13']);write(ATLAS,atlas);write(TRANSFER,transfer);write(COUNTER,counter)
 qhosts=[x for x in atlas if x['scope']=='Q13' and x['identity_level']=='PAGE_HOST' and int(x['cross_folio'])];stable=[x for x in qhosts if int(x['occurrences'])>=5 and float(x['dominant_purity'])>=.8]
 result={'schema':'GDT227_Q13_ABSTRACT_INTERLINEAR_RESULT_V1','status':'ABSTRACT_Q13_INTERLINEAR_BUILT_IDENTITY_PLACEMENT_DESCRIPTIVE','secondary_status':'Q13_IDENTITY_SLOT_STABLE_CROSS_REGISTER_PAGE_HOST_TRANSFER_NULL','q13_fields':sum(x['scope']=='Q13' for x in inter),'q13_group_occurrences':sum(1 for x in occ if x['scope']=='Q13' and x['level']=='PAGE_HOST'),'stars_group_occurrences':sum(1 for x in occ if x['scope']=='STARS_B' and x['level']=='PAGE_HOST'),'licensed_o_ot_hosts_non_f84':len(licensed),'q13_cross_folio_page_hosts':len(qhosts),'q13_recurrent_role_stable_page_hosts':len(stable),'top_q13_role_stable_hosts':sorted([{'page_host':x['identity'],'occurrences':int(x['occurrences']),'folios':int(x['folios']),'dominant_role':x['dominant_role'],'purity':float(x['dominant_purity'])} for x in stable],key=lambda x:(-x['occurrences'],x['page_host']))[:30],'placement_scores':summary,'interpretation':'A complete opaque q13 field interlinear: exact identities have stable q13 slot placement, while PAGE_HOST role mapping does not transfer beyond the prior to Stars-B.','claim_ceiling':'Abstract field-role likeness and opaque identity placement only; no host meaning word language plaintext or translation.','f84':{'public_metadata_previously_exposed':True,'raw_rows_rejected_before_parse':True,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False},'inputs':{p.name:sha(p) for p in (SOURCE,PROJ,OLD)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (INTER,ATLAS,TRANSFER,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'q13_fields':result['q13_fields'],'q13_groups':result['q13_group_occurrences'],'cross_folio_hosts':len(qhosts),'stable_hosts':len(stable),'scores':summary},sort_keys=True))
if __name__=='__main__':main()
