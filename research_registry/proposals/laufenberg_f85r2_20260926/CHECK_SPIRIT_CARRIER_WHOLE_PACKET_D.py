#!/usr/bin/env python3
"""Literal604 validator: hashes/tuples/inventories/manual spans and R1 scope census.
No semantic executor, normalization, decoder or historical-meaning test.
Run from repository root; reads only named author packets and safe1042 projection.
"""
import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
B=Path('research_registry/proposals/laufenberg_f85r2_20260926')
N=Path('experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv')
F=['edition','block','locus','source_group_id','source_group_index','source_group_count','within_line_position','paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
j=lambda p:json.loads(p.read_text())
def tab(p):
 with p.open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
checks=[]
def ck(name,ok,detail=None):checks.append({'check':name,'pass':bool(ok),'detail':detail})
f=j(B/'SPIRIT_CARRIER_AUTHOR_FIRST.json');w=j(B/'SPIRIT_CARRIER_AUTHOR_WHOLE.json')
fr=j(B/'SPIRIT_CARRIER_AUTHOR_FIRST_FREEZE_RECEIPT.json');wr=j(B/'SPIRIT_CARRIER_AUTHOR_WHOLE_FREEZE_RECEIPT.json')
for stage,receipt in [('first',fr),('whole',wr)]:
 for x in receipt['files']:
  p=Path(x['path']);ck(stage+'_hash:'+p.name,sha(p)==x['sha256'] and p.stat().st_size==x['bytes'])
# Hash original source and first receipt without opening reviewer claims.
ck('source_hash',sha(Path(f['source']['path']))==f['source']['sha256']==w['source']['sha256'])
ck('native_hash',sha(N)==f['scope']['sha256']==w['scope']['sha256'])
for x in w['first_contract_preservation']['first_input_hashes']:
 if '/SPIRIT_CARRIER_AUTHOR_FIRST' in x['path']:ck('first_input_hash:'+Path(x['path']).name,sha(Path(x['path']))==x['sha256'])
r=tab(N);ft=tab(B/'SPIRIT_CARRIER_AUTHOR_FIRST_473_CONSEQUENCES.tsv');wt=tab(B/'SPIRIT_CARRIER_AUTHOR_WHOLE_473_CONSEQUENCES.tsv')
ck('473rows',len(r)==len(ft)==len(wt)==473)
for name,rows in [('first',ft),('whole',wt)]:
 ck(name+'_12original_column_order',list(rows[0])[:12]==F)
 ck(name+'_473x12_ordered_tuples',[[x[k] for k in F] for x in rows]==[[x[k] for k in F] for x in r])
for key in ['source','scope','types','binder_contract']:
 ck('first_'+key+'_exact',w[key]==f[key])
ck('first_six_rules_exact',w['rules'][:len(f['rules'])]==f['rules'])
ck('first_five_trees_exact',w['clauses'][:len(f['clauses'])]==f['clauses'])
ck('first11values_exact',len(f['lexicon'])==11 and all(w['lexicon'].get(k)==v for k,v in f['lexicon'].items()))
variant_schema_changes=[]
for old,newv in zip(f['variants'],w['variants']):
 ck('first_variant_shared_fields:'+old['clause']+':'+old['edition'],all(newv.get(k)==v for k,v in old.items() if k!='mismatches'))
 expected=next(c['raw'] for c in f['clauses'] if c['id']==old['clause'])
 rebuilt=[{'id':sid,'actual':actual,'required':required} for sid,actual,required in zip(old['source_ids'],old['actual'],expected) if actual!=required]
 ck('first_variant_mismatches_reconstructed:'+old['clause']+':'+old['edition'],old['mismatches']==rebuilt and newv['expected']==expected)
 variant_schema_changes.append({'clause':old['clause'],'edition':old['edition'],'removed_fields':sorted(set(old)-set(newv)),'added_fields':sorted(set(newv)-set(old))})
ck('nine_duty_texts_and_first_status_exact',[{k:v for k,v in x.items() if k!='whole_status'} for x in w['whole_source_duties']]==f['whole_source_duties'])
lex=w['lexicon'];new=set(lex)-set(f['lexicon'])
ck('34whole23new',len(lex)==34 and len(new)==23)
ck('no_internal_cuts',all(v['cut'] is None for v in lex.values()))
ck('42_declared_payload_entries',sum(len(v['payloads']) for v in lex.values())==42==w['costs']['semantic_payload_entries'])
ck('14_rule_headings',len(w['rules'])==14 and len({x['id'] for x in w['rules']})==14)
ids={x['source_group_id']:x for x in r};lines=defaultdict(list);occ=defaultdict(list);counts={}
for x in r:lines[x['edition'],x['locus']].append(x);occ[x['ivtff_group_raw']].append(x['source_group_id'])
for ed in ['ZL3b','IT2a','RF1b']:
 xs=[x for x in r if x['edition']==ed];n=sum(x['ivtff_group_raw'] in lex for x in xs);counts[ed]={'rows':len(xs),'assigned':n,'unknown':len(xs)-n}
ck('whole_counts',counts==w['counts']['by_reader'] and sum(x['assigned'] for x in counts.values())==185 and sum(x['unknown'] for x in counts.values())==288)
for name,d,rows in [('first',f,ft),('whole',w,wt)]:
 ck(name+'_all_occurrence_lists',d['all_assigned_occurrences']=={word:occ[word] for word in d['lexicon']})
 errs=[]
 for x in rows:
  v=d['lexicon'].get(x['ivtff_group_raw']);expected_type=v['type'] if v else 'UNKNOWN';actual=json.loads(x['fixed_value']) if x['fixed_value'] else None
  if x['fixed_type']!=expected_type or actual!=(v['value'] if v else None) or x['exact_cut']!='' or x[name+'_status']!=('whole_lookup' if v else 'unknown'):errs.append(x['source_group_id'])
 ck(name+'_all_row_values_types_cuts_status',not errs,errs)
ck('first_assignment_preservation_flags',all(x['first_assignment_preserved']==('yes' if x['ivtff_group_raw'] in f['lexicon'] else 'not_first_assigned') for x in wt))
# Complete census of ALL GenericBinder literals and each within-line next group.
# This checks fixed R1 introductions and last-binder identity, not any predicate truth.
def census(d):
 result=[];complete=[]
 for (ed,lo),xs in lines.items():
  for i,x in enumerate(xs):
   if d['lexicon'].get(x['ivtff_group_raw'],{}).get('type')!='GenericBinder':continue
   nx=xs[i+1] if i+1<len(xs) else None;nt=d['lexicon'].get(nx['ivtff_group_raw'],{}).get('type','UNKNOWN') if nx else 'LINE_BOUNDARY';ok=nt=='CarrierKind'
   row={'id':x['source_group_id'],'raw':x['ivtff_group_raw'],'next_id':nx['source_group_id'] if nx else None,'next_raw':nx['ivtff_group_raw'] if nx else None,'next_type':nt,'complete_R1':ok}
   result.append(row)
   if ok:complete.append([x['source_group_id'],nx['source_group_id']])
 return result,complete
fc,fi=census(f);wc,wi=census(w)
ck('every_GEN_accounted',len(wc)==sum(len(occ[a]) for a,v in lex.items() if v['type']=='GenericBinder'))
ck('R1_first_and_whole_same_exact_three_introductions',fi==wi==[[ed+'|f85r2.1|G004',ed+'|f85r2.1|G005'] for ed in ['ZL3b','IT2a','RF1b']])
ck('only_first_CarrierKind_and_GenericBinder_lexical_values',[(a,v) for a,v in lex.items() if v['type'] in ['CarrierKind','GenericBinder']]==[(a,v) for a,v in f['lexicon'].items() if v['type'] in ['CarrierKind','GenericBinder']])
reference_types={'CarrierReference','CarrierIdentityReference','CarrierPartitiveReference','QuantifiedPartitiveReference'}
bindings=[];binding_map={}
for ed in counts:
 xs=sorted([x for x in r if x['edition']==ed],key=lambda x:(int(x['locus'].split('.')[-1]),int(x['source_group_index'])))
 completed={pair[1]:pair for pair in wi if pair[0].startswith(ed+'|')};active=None
 for x in xs:
  if x['source_group_id'] in completed:active=completed[x['source_group_id']]
  ty=lex.get(x['ivtff_group_raw'],{}).get('type')
  if ty in reference_types:
   bindings.append({'id':x['source_group_id'],'raw':x['ivtff_group_raw'],'type':ty,'latest_complete_R1':active});binding_map[x['source_group_id']]=active
ck('every_typed_reference_has_unchanged_first_binder',all(x['latest_complete_R1']==[x['id'].split('|')[0]+'|f85r2.1|G004',x['id'].split('|')[0]+'|f85r2.1|G005'] for x in bindings))
ck('every_TSV_reference_binding',all(x['reference_binding']==('c from unchanged .1G004-G005 generic binder' if x['source_group_id'] in binding_map else '') for x in wt))
# Reader-specific raw spans inspected directly before coding; .22 is not index-aligned.
SPECS=[('BINDER',1,4,5,'ar chcthy'),('HEART_REFINEMENT',1,15,17,'otchedy olkaiin odar'),('BRAIN_REFINEMENT',1,19,21,'otchedy qotedaiin odar'),('REFINEMENT_CONJUNCTION',1,15,21,'otchedy olkaiin odar aloees otchedy qotedaiin odar'),('BEAR_AND_DEPOSIT',8,1,5,'otchedy chotey qocthey oteey ol'),('HEAT_BLOOD_LIVER',3,1,5,'qotor sheedy shodaiin olfar ary'),('SERVICE_NECESSITY',13,1,5,'or shedy tedy sodaiiin chy'),('SOUL_NOT_CARRIER',15,1,4,'ypshedy dar chedy or'),('CARRIER_INSTRUMENT',22,6,8,'or aiin og'),('PORTION_RETAINED',18,1,5,'okees olaiin qokal chdy sary'),('PORTION_DISTRIBUTED',21,1,3,'qokeody qoekedy dody')]
DIFF={('RF1b','HEART_REFINEMENT'):{0:'otche@152;y'},('RF1b','REFINEMENT_CONJUNCTION'):{0:'otche@152;y'},('RF1b','BEAR_AND_DEPOSIT'):{0:'otche@152;y'},('RF1b','SERVICE_NECESSITY'):{1:"{ch'}edy"},('RF1b','SOUL_NOT_CARRIER'):{0:'yfshe@152;y'},('RF1b','PORTION_RETAINED'):{1:'@221;laiin'}}
clauses={x['id']:x for x in w['clauses']};variants={(x['edition'],x['clause']):x for x in w['variants']};members=defaultdict(list);span_reports=[];complete_counts=Counter();complete_lines=defaultdict(set)
for cid,line,start,end,expected_string in SPECS:
 clause=clauses[cid];expected=expected_string.split(' ')
 ck('author_zl_clause_spec:'+cid,clause['locus']=='f85r2.'+str(line) and clause['indices']==list(range(start,end+1)) and clause['raw']==expected)
 for ed in counts:
  a,z=start,end;wanted=list(expected)
  for i,value in DIFF.get((ed,cid),{}).items():wanted[i]=value
  if cid=='CARRIER_INSTRUMENT' and ed=='IT2a':a,z=6,7;wanted=['or','aiinog']
  if cid=='CARRIER_INSTRUMENT' and ed=='RF1b':a,z=7,9
  xs=[x for x in lines[ed,'f85r2.'+str(line)] if a<=int(x['source_group_index'])<=z];raw=[x['ivtff_group_raw'] for x in xs];sids=[x['source_group_id'] for x in xs];match=raw==expected
  ck('independent_span:'+ed+':'+cid,raw==wanted)
  av=variants[ed,cid];ck('author_variant_inventory:'+ed+':'+cid,av['source_ids']==sids and av['actual']==raw and av['expected']==expected and av['literal_match']==match and av['status']==('manual complete local construction' if match else 'incomplete literal interface'))
  complete_counts[ed]+=match
  if match and len(xs)==len(lines[ed,'f85r2.'+str(line)]):complete_lines[ed].add('f85r2.'+str(line))
  for x in xs:members[x['source_group_id']].append(cid+':'+(clause['rule'] if match else 'INCOMPLETE'))
  span_reports.append({'clause':cid,'edition':ed,'ids':sids,'raw':raw,'literal_match':match,'unknown':[x for x in raw if x not in lex],'fixed_values':[lex.get(x) for x in raw]})
ck('all_local_membership_fields',all(x['local_construction_membership']==';'.join(members[x['source_group_id']]) for x in wt))
ck('manual_complete_counts_including_overlap',dict(complete_counts)==w['counts']['manual_complete_items_including_binder_and_overlapping_conjunction'])
ck('ZL_full_line_constructions_only3_13_18',complete_lines['ZL3b']=={'f85r2.3','f85r2.13','f85r2.18'})
# Literal type signatures only, no rule execution or search for paraphrases.
signatures={x['id']:x['input'] for x in w['rules'] if isinstance(x['input'],list) and x['id'] not in ['R4','R8b']}
sig_occ={}
for rid,types in signatures.items():
 found=[]
 for key,xs in lines.items():
  for i in range(len(xs)-len(types)+1):
   sub=xs[i:i+len(types)]
   if [lex.get(x['ivtff_group_raw'],{}).get('type','UNKNOWN') for x in sub]==types:found.append([x['source_group_id'] for x in sub])
 sig_occ[rid]=found
ck('all_declared_simple_type_signature_inventories',sig_occ==w['whole_validation']['finite_type_signature_occurrences'])
# Fixed manual tree fields linked to actual literal values; no proposition evaluator.
V=lambda word:lex[word]['value']
for c in w['clauses'][5:]:
 t=c['tree'];word=c['raw'];rid=t['rule'];ok=True
 if rid=='R9':ok=[t[k] for k in ['cause','predicate','material','locative','site']]==list(map(V,word))
 elif rid=='R6':ok=t['carrier']['literal']==word[0] and t['carrier']['antecedent']=='BINDER' and [t[k] for k in ['resource_noun','necessity','activity_kind','quantifier']]==list(map(V,word[1:]))
 elif rid=='R8b':ok=t['soul_kind']['rule']=='R8a' and [t['soul_kind']['modifier'],t['soul_kind']['base'],t['predicate']]==list(map(V,word[:3])) and t['soul_kind']['result']==V('og') and t['carrier']['literal']==word[3] and t['carrier']['antecedent']=='BINDER'
 elif rid=='R7':ok=t['carrier']['literal']==word[0] and t['carrier']['antecedent']=='BINDER' and [t['predicate'],t['soul_kind']]==list(map(V,word[1:]))
 elif rid=='R10':ok=t['quantifier']==V(word[0]) and t['partitive']==V(word[1])+'(c)' and [t[k] for k in ['predicate','locative','region']]==list(map(V,word[2:])) and t['bound_portion']=='u'
 elif rid=='R11':ok=t['subject']==V(word[0])+'(c)' and [t['predicate'],t['destination']]==list(map(V,word[1:])) and t['bound_portion']=='v'
 ck('new_manual_tree_literal_fields:'+c['id'],ok)
for entry in w['ZL_all24_line_inventory']:
 xs=lines['ZL3b',entry['locus']];unk=[{'id':x['source_group_id'],'raw':x['ivtff_group_raw']} for x in xs if x['ivtff_group_raw'] not in lex]
 ck('ZL_line_inventory:'+entry['locus'],entry['groups']==len(xs) and entry['assigned']==len(xs)-len(unk) and entry['unknown']==unk and entry['full_line_construction']==(entry['locus'] in complete_lines['ZL3b']))
ck('24ZLlines',len(w['ZL_all24_line_inventory'])==24)
coverage=Counter()
for x in r:coverage[('assigned' if x['ivtff_group_raw'] in lex else 'unknown')+('_in_manual_span' if members[x['source_group_id']] else '_outside_manual_span')]+=1
prose=[{'location':'AUTHOR_WHOLE.md R11 paragraph after all-three-reader G001–003 assertion','claim_limit':'The following G004 SERVICE wording is true for ZL/RF, not IT. IT.21G004 is csedy and UNKNOWN; no alias is licensed. JSON/TSV preserve it correctly.','native_rows':[{k:ids[ed+'|f85r2.21|G004'][k] for k in ['source_group_id','ivtff_group_raw']} for ed in counts]}]
inputs=[N,B/'SPIRIT_CARRIER_WHOLE_REVIEW_CONTRACT.md',Path(f['source']['path'])]+[B/('SPIRIT_CARRIER_AUTHOR_'+stage+suffix) for stage in ['FIRST','WHOLE'] for suffix in ['.md','.json','_473_CONSEQUENCES.tsv','_FREEZE_RECEIPT.json']]
result={'status':'PASS_LITERAL_INVENTORIES_WITH_PROSE_CAVEAT' if all(x['pass'] for x in checks) else 'LITERAL_DISCREPANCIES','start_observed_utc':'2026-09-27 12:51:16 UTC','completed_utc':datetime.now(timezone.utc).isoformat(),'deadline_utc':'2026-09-27 13:01:00 UTC','checks':checks,'failed_checks':[x for x in checks if not x['pass']],'counts':counts,'assigned_total':sum(x['assigned'] for x in counts.values()),'unknown_total':sum(x['unknown'] for x in counts.values()),'coverage':dict(coverage),'all_GEN_next_group_census':wc,'first_complete_R1':fi,'whole_complete_R1':wi,'all_typed_reference_bindings':bindings,'reference_limit':'Only fixed known lexicon/R1 scope was checked. No future unknown meaning assumed empty; no general semantic executor. No new complete binder or reset is introduced by the current extension.','manual_spans':span_reports,'complete_manual_item_counts_including_overlap':dict(complete_counts),'simple_type_signature_inventory':sig_occ,'source_duty_flags':w['whole_source_duties'],'prose_findings':prose,'variant_schema_changes':variant_schema_changes,'variant_schema_limit':'First15variant raw strings, source IDs, match/status fields unchanged. Whole serialization replaces mismatches with expected; original mismatch contents were independently reconstructed exactly. No claim that entire variant objects are byte-for-value unchanged.','limits':'Literal scope, integrity and manual-tree-field checks only. No full parse, source meaning confirmation, portion identity execution, historical truth or independent reader evidence.','inputs':[{'path':str(p),'sha256':sha(p)} for p in inputs],'checker_sha256':sha(Path(__file__))}
(B/'SPIRIT_CARRIER_WHOLE_LITERAL_D.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'check_count':len(checks),'failed':result['failed_checks'],'counts':counts,'GEN_count':len(wc),'R1_count':len(wi),'reference_count':len(bindings),'coverage':dict(coverage),'completed_utc':result['completed_utc']},indent=2))
