from common import *
def compare(title,body,vs):
 if not all(title['valid']):return 'UNKNOWN',[]
 n=len(title['values']);hits=[];possible=False
 for j in range(len(body['values'])-n+1):
  vals=body['values'][j:j+n];known=body['valid'][j:j+n]
  for k,v in enumerate(vs):
   if vals==v and all(known):hits.append({'start_1based':j+1,'variant_index':k,'variant':v})
   if all(not ok or a==b for a,b,ok in zip(v,vals,known)):possible=True
 if hits:return 'PRESENT',hits
 return ('UNKNOWN' if possible or body['uncertain_seams'] or not body['count_ok'] else 'ABSENT'),[]
def tsv(path,rows):
 with path.open('w') as f:
  w=csv.DictWriter(f,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def run():
 for rel,h in load(E/'PREREG_LOCK.json')['files'].items():assert sha(R/rel)==h,rel
 prior=parent();spec=load(P/'src/SPEC.json');source=load(P/'src/SOURCE.json');data=load(P/'artifacts/INPUT.json');spec=dict(spec,models=['LITERAL']);records=prior.line_records(data,spec)
 predictions=load(E/'artifacts/FROZEN_TITLE_PREDICTIONS.json');pd={(x['edition'],x['model'],x['sector']):x for x in predictions}
 edges=[(source['names'].index(a),source['names'].index(b)) for a,b in source['mandatory_edges']]
 cells=[];graphs=[];cases=[];candidates=[];allbodies=[];newedges=[]
 for ed in spec['editions']:
  bodies=[]
  for sec in spec['sectors']:
   parts=[records[ed,l,'LITERAL'] for l in sec['body']]
   body={'values':sum((p['values'] for p in parts),[]),'valid':sum((p['valid'] for p in parts),[]),'uncertain_seams':any(p['uncertain_seams'] for p in parts),'count_ok':all(p['count_ok'] for p in parts)};bodies.append(body);allbodies.append({'edition':ed,'sector':sec['sector'],'loci':sec['body'],'body':body})
  for model in MODELS:
   states=[];added=0
   for i,body in enumerate(bodies):
    row=[]
    for j in range(12):
     x=pd[ed,model,j+1];title=x['title'];state,hits=compare(title,body,x['variants']);baseline,_=prior.compare(title,body);row.append(state)
     c={'edition':ed,'model':model,'body_sector':i+1,'title_sector':j+1,'title_locus':x['locus'],'title_raw':' '.join(title['values']),'variant_count':len(x['variants']),'status':state,'literal_status':baseline,'new_definite_offdiagonal':state=='PRESENT' and baseline!='PRESENT' and i!=j,'hits':hits}
     if c['new_definite_offdiagonal']:newedges.append(c);added+=1
     cells.append(c)
    states.append(row)
   bnds={}
   for bound in ['lower','upper']:
    adj=[[s=='PRESENT' if bound=='lower' else s!='ABSENT' for s in row] for row in states]
    answer=prior.solve(12,edges,adj);bnds[bound]=answer;graphs.append({'edition':ed,'model':model,'bound':bound,'adjacency':adj,**answer})
   case={'edition':ed,'model':model,'status':'CONTRADICTED' if not bnds['upper']['count'] else 'COMPATIBLE_CONDITIONAL_GRAPH' if bnds['lower']['count'] else 'UNRESOLVED_ONLY','lower_assignments':bnds['lower']['count'],'upper_assignments':bnds['upper']['count'],'definite_offdiagonal':sum(s=='PRESENT' for i,row in enumerate(states) for j,s in enumerate(row) if i!=j),'unknown_offdiagonal':sum(s=='UNKNOWN' for i,row in enumerate(states) for j,s in enumerate(row) if i!=j),'new_definite_offdiagonal':added,'expanded_titles':sum(len(pd[ed,model,j+1]['variants'])>1 for j in range(12)),'independent_confirmation_leaves':0};cases.append(case)
   for ni,name in enumerate(source['names']):
    for j in range(12):candidates.append({'edition':ed,'model':model,'name_hypothesis':name,'title_sector':j+1,'title_locus':pd[ed,model,j+1]['locus'],'title_raw':' '.join(pd[ed,model,j+1]['title']['values']),'definite_assignments':bnds['lower']['marginals'][ni][j],'possible_assignments_upper':bnds['upper']['marginals'][ni][j],'meaning_confirmed':False})
 save(E/'artifacts/ALL_CELLS.json',cells);save(E/'artifacts/GRAPHS.json',{'source_edges':edges,'graphs':graphs});save(E/'artifacts/COMPLETE_BODIES.json',allbodies);save(E/'artifacts/NEW_OBSERVED_EDGES.json',newedges)
 tsv(E/'artifacts/CANDIDATE_TABLE.tsv',cases);tsv(E/'artifacts/ALL_NAME_CANDIDATES.tsv',candidates)
 result={'status':'NO_ADDED_REFERENCE_NO_MEANING_GAIN' if not newedges else 'CONDITIONAL_FORM_REFERENCE_COMPARISON','cases':cases,'candidate_name_sector_rows':len(candidates),'title_body_cells':len(cells),'new_observed_edges':len(newedges),'confirmed_words':0,'independent_confirmation_leaves':0,'new_pages':0,'GDT388':'NO_NEW_RELATION_EVIDENCE' if not newedges else 'INELIGIBLE_EXPOSED_SINGLE_LEAF_PACKET_GATE_REQUIRED','significance_claim':False,'meaning_limit':'Known written variants are not established meaning equivalences; upper assignments are generous uncertainty bounds only.','source_and_parent':'GDT952 bytes unchanged; early historical source graph unchanged; no new decoder.'}
 save(E/'artifacts/RESULT.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
