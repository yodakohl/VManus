#!/usr/bin/env python3
"""Independent reconstruction checks for GDT003 formal prediction."""
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results';EDS=('ZL3b','IT2a','RF1b')
checks=[]
def check(name,ok,detail=''):
 checks.append({'check':name,'pass':bool(ok),'detail':str(detail)})
 if not ok:raise AssertionError(f'{name}: {detail}')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def guarded(p,col='locus'):
 out=[]
 with p.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');i=h.index(col)
  for line in f:
   c=line.rstrip('\n').split('\t')
   if c[i].startswith('f84r'):continue
   out.append(dict(zip(h,c)))
 return out
def folio(page):
 m=re.match(r'(f\d+)',page);return m.group(1) if m else page
def q(s):return None if s.startswith('q') else 'q'+s
def ds(s):return 's'+s[1:] if len(s)>1 and s.startswith('d') else None
def oot(s):return 'ot'+s[1:] if len(s)>1 and s.startswith('o') and not s.startswith('ot') else None
def repl(s,a,b):return s[:-len(a)]+b if s.endswith(a) else None
OPS={'PREPEND_Q':q,'INITIAL_D_TO_S':ds,'INITIAL_O_TO_OT':oot,'APPEND_DY':lambda s:s+'dy','APPEND_DAL':lambda s:s+'dal','APPEND_DAR':lambda s:s+'dar','FINAL_DAL_TO_DAR':lambda s:repl(s,'dal','dar'),'FINAL_DAL_TO_DY':lambda s:repl(s,'dal','dy'),'FINAL_DAR_TO_DY':lambda s:repl(s,'dar','dy')}

res=json.loads((R/'gdt003_results.json').read_text())
check('status',res['status']=='NOT DISTINGUISHABLE FROM STRING STATISTICS')
check('ceiling',all(s in res['claim_ceiling'] for s in ('No morpheme','translation')))
check('f84_flag',res['holdout']['f84r_formal_retained_or_scored'] is False)
for rel,h in {**res['inputs'],**res['documents'],**res['outputs']}.items():check('hash_'+rel,sha(R/rel)==h)
for name in res['outputs']:check('no_f84r_'+name,'f84r' not in (R/name).read_text())

sep=guarded(S/'source_separator_transcription.tsv');meta={x['source_group_id']:x for x in sep};aln=guarded(S/'source_sta_group_alignment.tsv');g=defaultdict(dict)
for x in aln:g[x['locus'],int(x['source_group_index'])][x['edition']]={**x,'surface':x['nearest_basic_eva_primary'].lower(),'page':meta[x['source_group_id']]['page'],'section':meta[x['source_group_id']]['section']}
records=[];amb=0
for key,em in g.items():
 if len(em)==3 and len({x['surface'] for x in em.values()})==1 and len({x['source_group_count'] for x in em.values()})==1:records.append(next(iter(em.values())))
 else:amb+=1
forms={x['surface'] for x in records}
check('corpus_counts',(len(records),len(forms),amb)==(18760,4394,20704))
check('result_corpus_counts',res['corpus']['stable_physical_groups']==len(records) and res['corpus']['stable_form_types']==len(forms) and res['corpus']['ambiguous_or_topology_disagreement_keys_excluded']==amb)

trows=rows(R/'gdt003_transformations.tsv');td={x['transformation']:x for x in trows};expected={'PREPEND_Q':290,'INITIAL_D_TO_S':72,'INITIAL_O_TO_OT':39,'APPEND_DY':197,'APPEND_DAL':36,'APPEND_DAR':33,'FINAL_DAL_TO_DAR':34,'FINAL_DAL_TO_DY':61,'FINAL_DAR_TO_DY':76}
check('transformation_names',set(td)==set(OPS))
for name,fn in OPS.items():
 n=sum(fn(s) is not None and fn(s) in forms for s in forms);check('edges_'+name,n==expected[name]==int(td[name]['exact_pair_types']))
check('attachment_recovery',Counter(x['inferred_attachment_class'] for x in trows)==Counter({'RIGHT_EDGE':6,'LEFT_EDGE':2,'EDGE_MIXED':1}))

rrows=rows(R/'gdt003_paradigm_rectangles.tsv');states=Counter(x['structure_state'] for x in rrows)
check('rectangle_counts',states==Counter({'PARTIAL_2':2673,'PARTIAL_3':232,'COMPLETE_4':44}) and len(rrows)==2949)
rect_ok=True
for x in rrows:
 a,b=OPS[x['operation_A']],OPS[x['operation_B']];base=x['base_X'];ax=a(base);bx=b(base);ab=a(bx) if bx is not None else None;ba=b(ax) if ax is not None else None
 rect_ok&=x['A_X']==ax and x['B_X']==bx and x['A_of_B_X']==(ab or 'NOT_APPLICABLE') and x['B_of_A_X']==(ba or 'NOT_APPLICABLE')
check('all_rectangle_formulas',rect_ok)

irows=rows(R/'gdt003_transformation_interactions.tsv');ic=Counter(x['interaction_class'] for x in irows)
check('interaction_counts',ic==Counter({'ORDER_DEPENDENT':15,'INSUFFICIENT_DATA':11,'CONDITIONALLY_COMPATIBLE':8,'INDEPENDENT':2}))
ind={(x['operation_A'],x['operation_B']) for x in irows if x['interaction_class']=='INDEPENDENT'}
check('independent_pairs',ind=={('PREPEND_Q','APPEND_DY'),('INITIAL_D_TO_S','APPEND_DY')})
qdy=next(x for x in irows if x['operation_A']=='PREPEND_Q' and x['operation_B']=='APPEND_DY')
check('qdy_counts',(int(qdy['complete_rectangles']),int(qdy['three_cell_rectangles']),int(qdy['two_cell_rectangles']))==(17,20,398))
edition_forms={e:{x['surface'] for em in g.values() if e in em for x in [em[e]]} for e in EDS}
for x in irows:
 for ed,u in edition_forms.items():
  fa,fb=OPS[x['operation_A']],OPS[x['operation_B']];n=0
  for base in u:
   ax=fa(base);bx=fb(base)
   if ax is None or bx is None:continue
   ab=fa(bx);ba=fb(ax);n+=int(ab is not None and ab==ba and all(v in u for v in (base,ax,bx,ab)))
  check('edition_rectangles_'+ed+'_'+x['operation_A']+'_'+x['operation_B'],n==int(x[ed+'_complete_rectangles']))

pred=rows(R/'gdt003_holdout_predictions.tsv');pc=Counter((x['evaluation'],int(x['target_present'])) for x in pred)
check('prediction_counts',pc==Counter({('HOST_CELL_HOLDOUT',1):37,('HOST_CELL_HOLDOUT',0):35,('FOLIO_HELD_NOVEL_FORM',1):9,('FOLIO_HELD_NOVEL_FORM',0):3518,('SECTION_HELD_NOVEL_FORM',1):8,('SECTION_HELD_NOVEL_FORM',0):232}))
byfolio=defaultdict(set);bysection=defaultdict(set)
for x in records:byfolio[folio(x['page'])].add(x['surface']);bysection[x['section']].add(x['surface'])
allfolios=set(byfolio);allsections=set(bysection)
folio_ok=section_ok=True
for x in pred:
 if x['evaluation']=='FOLIO_HELD_NOVEL_FORM':
  held=byfolio[x['fold_id']];train=set().union(*(byfolio[v] for v in allfolios-{x['fold_id']}));folio_ok&=all(v in train for v in (x['base_X'],x['observed_A_X'],x['observed_B_X'])) and x['predicted_fourth'] not in train and int(x['target_present'])==int(x['predicted_fourth'] in held)
 if x['evaluation']=='SECTION_HELD_NOVEL_FORM':
  held=bysection[x['fold_id']];train=set().union(*(bysection[v] for v in allsections-{x['fold_id']}));section_ok&=all(v in train for v in (x['base_X'],x['observed_A_X'],x['observed_B_X'])) and x['predicted_fourth'] not in train and int(x['target_present'])==int(x['predicted_fourth'] in held)
check('all_folio_fold_exclusions_and_targets',folio_ok)
check('all_section_fold_exclusions_and_targets',section_ok)

expected_novel={('f114','qoeeody'),('f34','qoldar'),('f37','qotoldy'),('f43','qotydy'),('f58','sydy'),('f81','qoldy'),('f82','qokoldy'),('f83','qotaldy'),('f93','qokchody')}
got_novel={(x['fold_id'],x['predicted_fourth']) for x in pred if x['evaluation']=='FOLIO_HELD_NOVEL_FORM' and x['target_present']=='1'}
check('nine_specific_novel_targets',got_novel==expected_novel)

b=rows(R/'gdt003_baseline_comparison.tsv');bd={(x['evaluation'],x['baseline']):x for x in b}
pf=bd['FOLIO_HELD_NOVEL_FORM','PARADIGM_COMPLETION_RATE'];ng=bd['FOLIO_HELD_NOVEL_FORM','CHARACTER_ORDER4_KT'];wf=bd['FOLIO_HELD_NOVEL_FORM','VISIBLE_WHOLE_GROUP_FREQUENCY']
check('folio_precision',math.isclose(float(pf['precision']),9/3527) and int(pf['top1_hits'])==1 and int(pf['top5_hits'])==2)
check('folio_baseline_loss',float(pf['average_precision'])<float(ng['average_precision'])<float(wf['average_precision']))
check('folio_coverage',math.isclose(float(pf['recall']),9/2945))
hc=bd['HOST_CELL_HOLDOUT','PARADIGM_COMPLETION_RATE'];hcng=bd['HOST_CELL_HOLDOUT','CHARACTER_ORDER4_KT']
check('host_baseline_loss',float(hc['average_precision'])<float(hcng['average_precision']))
check('result_advantages_negative',res['prediction_metrics']['folio_AP_advantage_over_best_string_baseline']<0 and res['prediction_metrics']['host_AP_advantage_over_best_string_baseline']<0)
check('split_join_not_better',res['split_join']['supported_correct']/res['split_join']['supported_host_tasks'] < res['split_join']['substring_only_correct']/res['split_join']['substring_only_tasks'])
ledger=rows(R/'GDT002_YOLO_LEDGER.tsv');check('ledger_ckpt',sum(x['checkpoint_id']=='GDT003_CKPT001' for x in ledger)==1)

validation={'artifact':'GDT003_PARADIGM_PREDICTION_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(R/'gdt003_results.json'),'validator_sha256':sha(R/'validate_gdt003_paradigm_prediction.py'),'scope':'Independent reconstruction of stable corpus, transformation edges, every rectangle formula, interaction classifications/counts, fold exclusion and target presence for every prediction, exact novel targets, baseline ordering, hashes, and f84r exclusion. It does not infer linguistic morphology or semantics.'}
(R/'gdt003_validation.json').write_text(json.dumps(validation,sort_keys=True,indent=2)+'\n')
print('PASS',len(checks))
