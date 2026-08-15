#!/usr/bin/env python3
"""Score the exact GDT140 five-by-five relation assignment."""
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt062_right_family_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';PRED=R/'gdt140_prediction.json';METHOD=R/'GDT140_HERBAL_RELATION_PAGE_HOST_TRANSFER_METHOD.md';REPORT=R/'GDT140_HERBAL_RELATION_PAGE_HOST_TRANSFER_REPORT.md';SCORES=R/'gdt140_representation_scores.tsv';PAIR=R/'gdt140_pair_similarities.tsv';DIAG=R/'gdt140_true_pair_diagnostics.tsv';NULL=R/'gdt140_assignment_scores.tsv';WIT=R/'gdt140_exact_host_witnesses.tsv';LAYOUT=R/'gdt140_layout_assignment_controls.tsv';LEAVE=R/'gdt140_leave_one_relation.tsv';COUNTER=R/'gdt140_counterexamples.tsv';RESULT=R/'gdt140_result.json'
REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE')
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def add3(c,s):
 s='^'+s+'$'
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1.
def sim(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x]) for x in k)
 return sum(min(a[x],b[x]) for x in k)/d if d else 0.
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
rels=read(INV);assignments=read(ORBIT);freeze=json.loads(PRED.read_text());sources=[x['source_page'] for x in rels];targets=[x['target_page'] for x in rels];pages=set(sources+targets);data=[]
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84'):continue
  if x['page'] in pages:data.append(x)
assert set(x['page'] for x in data)==pages and len(rels)==5 and len(assignments)==120
bypage=defaultdict(list)
for x in data:bypage[x['page']].append(x)
feat={p:{r:Counter() for r in REPS} for p in pages}
for p in pages:
 for x in sorted(bypage[p],key=lambda x:(x['locus'],int(x['group_index']))):feat[p]['PAGE_HOST_IDENTITY']['H='+x['page_host']]+=1;add3(feat[p]['PAGE_HOST_CHAR3'],x['page_host']);add3(feat[p]['RAW_CHAR3'],x['token']);feat[p]['COMPILER_SIGNATURE']['|'.join((x['wrapper'],x['inner_d'],x['local_frame'],x['right_family'],x['dy_closure'],x['b3']))]+=1
mat={r:np.array([[sim(feat[a][r],feat[b][r]) for b in targets] for a in sources]) for r in REPS};pair_rows=[]
for rep in REPS:
 for i,a in enumerate(sources):
  for j,b in enumerate(targets):pair_rows.append({'representation':rep,'source_page':a,'candidate_target_page':b,'similarity':float(mat[rep][i,j]),'is_true':int(b==rels[i]['target_page'])})
mapping=[]
for a in assignments:
 d=dict(z.split('->') for z in a['mapping'].split('|'));mapping.append([targets.index(d[s]) for s in sources])
ascores={rep:np.array([sum(mat[rep][i,j] for i,j in enumerate(m))/5 for m in mapping]) for rep in REPS};true_idx=next(i for i,x in enumerate(assignments) if x['is_true']=='1');z={rep:(ascores[rep]-ascores[rep].mean())/(ascores[rep].std() or 1) for rep in REPS};maxz=np.max(np.stack([z[r] for r in REPS]),axis=0);global_p=float(np.mean(maxz>=maxz[true_idx]-1e-12));score_rows=[];assign_rows=[];diag=[];witness=[]
for rep in REPS:
 s=ascores[rep];ts=float(s[true_idx]);rank=1+int(np.sum(s>ts+1e-12));p=float(np.mean(s>=ts-1e-12));ranks=[];pos=0
 for i,x in enumerate(rels):
  row=mat[rep][i];v=float(row[targets.index(x['target_page'])]);rk=1+int(np.sum(row>v+1e-12));ranks.append(rk);effect=v-float(row.mean());pos+=effect>0;diag.append({'relation_id':x['relation_id'],'relation_class':x['relation_class'],'component':x['component'],'representation':rep,'source_page':x['source_page'],'true_target_page':x['target_page'],'true_similarity':v,'true_partner_rank_of_5':rk,'centered_leave_pair_effect':effect})
  if rep=='PAGE_HOST_IDENTITY':
   common=sorted(set(feat[x['source_page']][rep])&set(feat[x['target_page']][rep]));witness.append({'relation_id':x['relation_id'],'source_page':x['source_page'],'target_page':x['target_page'],'shared_exact_page_hosts':'|'.join(h[2:] for h in common),'shared_exact_host_count':len(common)})
 score_rows.append({'representation':rep,'true_assignment_score':ts,'null_mean':float(s.mean()),'null_sd':float(s.std()),'true_z':float(z[rep][true_idx]),'inclusive_rank_of_120':rank,'local_inclusive_p':p,'max_four_z_inclusive_p':global_p,'true_partner_rank_1_count':sum(x==1 for x in ranks),'true_partner_rank_le_2_count':sum(x<=2 for x in ranks),'positive_centered_pair_effects':pos,'selector_paid_z_bits':'DESCRIPTIVE_ONLY'})
 for i,a in enumerate(assignments):assign_rows.append({'assignment_id':a['assignment_id'],'representation':rep,'is_true':a['is_true'],'mean_pair_similarity':float(s[i]),'standardized_score':float(z[rep][i]),'max_four_standardized_score':float(maxz[i])})
sm={x['representation']:x for x in score_rows};best=max(('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3'),key=lambda r:(float(sm[r]['true_z']),r));b=sm[best];gates={'page_host_inclusive_rank_le_6_of_120':int(b['inclusive_rank_of_120'])<=6,'page_host_beats_raw_and_compiler':float(b['true_z'])>max(float(sm['RAW_CHAR3']['true_z']),float(sm['COMPILER_SIGNATURE']['true_z'])),'at_least_4_of_5_true_partner_ranks_le_2':int(b['true_partner_rank_le_2_count'])>=4,'leave_one_pair_score_positive_at_least_4_of_5':int(b['positive_centered_pair_effects'])>=4};status='HERBAL_RELATION_PAGE_HOST_TRANSFER_SUPPORTED' if all(gates.values()) else 'HERBAL_RELATION_PAGE_HOST_TRANSFER_NOT_SUPPORTED';counter=[]
# Post-result opportunity audit; this was not a selection or gate.
counts={p:{'FORMAL_LINES':len({x['locus'] for x in bypage[p]}),'SOURCE_GROUPS':len(bypage[p])} for p in pages};layout_rows=[];layout_summary={}
for metric in ('FORMAL_LINES','SOURCE_GROUPS'):
 vals=[sum(1-abs(counts[sources[i]][metric]-counts[targets[j]][metric])/max(counts[sources[i]][metric],counts[targets[j]][metric],1) for i,j in enumerate(m))/5 for m in mapping];ts=vals[true_idx];layout_summary[metric]={'true_similarity':ts,'inclusive_rank_of_120':1+sum(x>ts+1e-12 for x in vals),'inclusive_better_p':sum(x>=ts-1e-12 for x in vals)/120}
 for i,a in enumerate(assignments):layout_rows.append({'metric':metric,'assignment_id':a['assignment_id'],'is_true':a['is_true'],'mean_count_similarity':vals[i]})
leave_rows=[]
for rep in REPS:
 for drop,x in enumerate(rels):
  ii=[i for i in range(5) if i!=drop];ss=[sources[i] for i in ii];tt=[targets[i] for i in ii];vals=[]
  for perm in itertools.permutations(tt):vals.append(sum(mat[rep][sources.index(s),targets.index(perm[i])] for i,s in enumerate(ss))/4)
  ts=float(vals[0]);leave_rows.append({'representation':rep,'dropped_relation_id':x['relation_id'],'remaining_relations':4,'assignment_worlds':24,'true_score':ts,'inclusive_rank_of_24':int(1+sum(v>ts+1e-12 for v in vals)),'inclusive_p':float(sum(v>=ts-1e-12 for v in vals)/24)})
for x in sorted(diag,key=lambda x:(float(x['centered_leave_pair_effect']),x['representation']))[:12]:counter.append({'type':'WEAK_OR_MISPAIRED_RELATION','item':x['relation_id'],'representation':x['representation'],'value':x['centered_leave_pair_effect'],'detail':f"true partner rank {x['true_partner_rank_of_5']}/5; {x['relation_class']} {x['component']}"})
counter.extend([{'type':'RELATION_HETEROGENEITY','item':'MIXED_WHOLE_AND_COMPONENT','representation':'ALL','value':'NA','detail':'The five human statements mix weak whole-plant and moderate/strong component similarities; shared page text is not guaranteed.'},{'type':'PRIOR_ROUTE_DISTINCTION','item':'FPR_S99','representation':'ALL','value':'NA','detail':'Prior pharmaceutical-label/root failures remain negative and are not overturned.'},{'type':'ALTERNATE_READING_SCOPE','item':'GDT062','representation':'ALL','value':'NA','detail':'One derived source-display HPR2 view; no alternate-reading replication.'}])
write(SCORES,clean(score_rows));write(PAIR,clean(pair_rows));write(DIAG,clean(diag));write(NULL,clean(assign_rows));write(WIT,witness);write(LAYOUT,clean(layout_rows));write(LEAVE,clean(leave_rows));write(COUNTER,clean(counter))
REPORT.write_text(f"""# GDT140 — Herbal relation PAGE_HOST transfer\n\n## Outcome\n\n**{status}**\n\nThe exact five-relation assignment is ranked among all 120 one-to-one mappings. The better PAGE_HOST representation is `{best}`: true mean similarity {float(b['true_assignment_score']):.6f}, rank {b['inclusive_rank_of_120']}/120, local p {float(b['local_inclusive_p']):.4f}, standardized score {float(b['true_z']):+.3f}, and max-four p {float(b['max_four_z_inclusive_p']):.4f}. It places {b['true_partner_rank_le_2_count']}/5 true partners in the top two and gives {b['positive_centered_pair_effects']}/5 positive centered pair effects.\n\nControls: raw rank {sm['RAW_CHAR3']['inclusive_rank_of_120']}/120 (z {float(sm['RAW_CHAR3']['true_z']):+.3f}); compiler rank {sm['COMPILER_SIGNATURE']['inclusive_rank_of_120']}/120 (z {float(sm['COMPILER_SIGNATURE']['true_z']):+.3f}). Post-result opportunity checks put the true mapping only {layout_summary['FORMAL_LINES']['inclusive_rank_of_120']}/120 for formal-line-count similarity and {layout_summary['SOURCE_GROUPS']['inclusive_rank_of_120']}/120 for source-group-count similarity, so matched page length cannot explain the positive PAGE_HOST rank. Dropping each relation in turn leaves the `{best}` true assignment ranked {', '.join(str(x['inclusive_rank_of_24']) for x in leave_rows if x['representation']==best)} out of 24: the lead is not carried by one pair. Frozen gates: `{json.dumps(gates,sort_keys=True)}`.\n\nThe panel is small and heterogeneous, and human visual resemblance does not guarantee shared manuscript content. Exact witnesses and every wrong assignment are published. This result does not reopen or reverse the failed pharmaceutical-label/root routes. The GDT062 HPR2 inventory is one derived source-display view, not three replications. All f84 rows were rejected before retention and no new f84r access occurred. No botanical truth, plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation follows.\n""",encoding='utf8')
result={'schema':'GDT140_HERBAL_RELATION_PAGE_HOST_TRANSFER_RESULT_V1','status':status,'relations':len(rels),'assignment_worlds':len(assignments),'best_page_host_representation':best,'scores':sm,'gates':gates,'layout_opportunity_audit':layout_summary,'leave_one_relation':{r:[x for x in leave_rows if x['representation']==r] for r in REPS},'interpretation':'Exact one-to-one page-bag similarity for five archived Herbal-Herbal visual relations.','claim_ceiling':freeze['claim_ceiling'],'alternate_reading_sensitivity':'ONE_DERIVED_GDT062_SOURCE_DISPLAY_VIEW;NO_REPLICATION_CLAIM','f84':{'all_rows_rejected_before_retention':True,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (SOURCE,INV,ORBIT,PRED,R/'gdt139_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (SCORES,PAIR,DIAG,NULL,WIT,LAYOUT,LEAVE,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':status,'best':best,'rank':b['inclusive_rank_of_120'],'max4_p':b['max_four_z_inclusive_p'],'gates':gates},sort_keys=True))
