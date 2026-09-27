#!/usr/bin/env python3
"""605 literal checker preparation; no general parser or semantic evaluator.
Default mode reads FIRST and named prospective contracts ONLY.
Whole mode must not run before explicit parent notification of author freeze.
Prepared starting2026-09-27 13:13:26UTC; counts toward12-minute review budget.
"""
import argparse,csv,json,hashlib
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
B=Path('research_registry/proposals/laufenberg_f85r2_20260926')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
j=lambda p:json.loads(p.read_text())
def table(p):
 with p.open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--whole-after-freeze',action='store_true',help='Use only after actual author freeze notification.');args=ap.parse_args()
 f=j(B/'ADAMANT_AUTHOR_FIRST.json');fr=j(B/'ADAMANT_AUTHOR_FIRST_FREEZE_RECEIPT.json')
 contract=B/'ADAMANT_WHOLE_REVIEW_CONTRACT.md';auth=B/'ADAMANT_WHOLE_AUTHORIZATION_RECEIPT.json'
 checks=[]
 def ck(name,ok,detail=None):checks.append({'check':name,'pass':bool(ok),'detail':detail})
 for x in fr['files']:
  p=Path(x['path']);ck('first_hash:'+p.name,sha(p)==x['sha256'] and p.stat().st_size==x['bytes'])
 ck('first_freeze_receipt_exact',sha(B/'ADAMANT_AUTHOR_FIRST_FREEZE_RECEIPT.json')=='b78769dbd838764e0478bad32d3905735d4d7fb049fd3ebec466952157b7c9d3')
 # Read/hash only the prospective authorization itself, never root review contents.
 authorization=j(auth);ck('prospective_contract_hash',any(x['path']==str(contract) and x['sha256']==sha(contract) for x in authorization['files']))
 ck('first15lexicon',len(f['lexicon'])==15)
 ck('firstA0_to_A8', [x['id'] for x in f['rules']]==['A'+str(n) for n in range(9)])
 ck('first17group_frame',next(x for x in f['clauses'] if x['id']=='COMPLETE_FIRST_FRAME')['indices']==list(range(8,25)))
 if not args.whole_after_freeze:
  print(json.dumps({'status':'PREPARATION_ONLY_WHOLE_UNOPENED','checks':checks,'whole_files_read':False,'completed_utc':datetime.now(timezone.utc).isoformat()},indent=2));return
 # Inactive until parent supplies freeze; schema-specific span/scope review will follow.
 w=j(B/'ADAMANT_AUTHOR_WHOLE.json');wr=j(B/'ADAMANT_AUTHOR_WHOLE_FREEZE_RECEIPT.json')
 ck('whole_receipt_notified_hash',sha(B/'ADAMANT_AUTHOR_WHOLE_FREEZE_RECEIPT.json')=='6c66862ecd92145bc9fe93863f9a7ad1218ab2970a39493e9f164a0c20a2ad00')
 for x in wr['files']:
  p=Path(x['path']);ck('whole_hash:'+p.name,sha(p)==x['sha256'] and p.stat().st_size==x['bytes'])
 for key in ['scope','type_interfaces','binding_table','complete_tree']:
  ck('first_'+key+'_preserved',w.get(key)==f[key])
 ck('source_preserved_except_disclosed_count', {k:v for k,v in w['source'].items() if k!='unit'}=={k:v for k,v in f['source'].items() if k!='unit'} and f['source']['unit']=='complete85-word id00097, all6duties' and w['source']['unit']=='complete86-whitespace-word id00097, all6duties')
 ck('source_excerpt_bytes_and_count',sha(Path(w['source']['path']))==w['source']['sha256'] and len(Path(w['source']['path']).read_text().split())==86)
 ck('first_rules_prefix_preserved',w.get('rules',[])[:len(f['rules'])]==f['rules'])
 ck('first_clauses_prefix_preserved',w.get('clauses',[])[:len(f['clauses'])]==f['clauses'])
 ck('first15values_preserved',all(w['lexicon'].get(k)==v for k,v in f['lexicon'].items()))
 native=Path(f['scope']['file']);rows=table(native);firstrows=table(B/'ADAMANT_AUTHOR_FIRST_473_CONSEQUENCES.tsv');wholerows=table(B/'ADAMANT_AUTHOR_WHOLE_473_CONSEQUENCES.tsv');fields=f['scope']['original_fields']
 ck('safe_native_hash',sha(native)==f['scope']['sha256'])
 for name,tab in [('first',firstrows),('whole',wholerows)]:
  ck(name+'_473x12',len(tab)==len(rows)==473 and list(tab[0])[:12]==fields and [[r[k] for k in fields] for r in tab]==[[r[k] for k in fields] for r in rows])
 lex=w['lexicon'];occ=defaultdict(list);lines=defaultdict(list);counts=defaultdict(Counter)
 for r in rows:
  word=r['ivtff_group_raw'];occ[word].append(r['source_group_id']);lines[r['edition'],r['locus']].append(r);counts[r['edition']]['rows']+=1;counts[r['edition']]['assigned' if word in lex else 'unknown']+=1
 ck('all_occurrence_lists',w['all_assigned_occurrences']=={word:occ[word] for word in lex})
 errors=[]
 for r in wholerows:
  v=lex.get(r['ivtff_group_raw']);a=json.loads(r['fixed_value']) if r['fixed_value'] else None
  if r['fixed_type']!=(v['type'] if v else 'UNKNOWN') or a!=(v['value'] if v else None):errors.append(r['source_group_id'])
 ck('all_literal_values_types',not errors,errors)
 # Enumerate every old boundary and old relation signature, not asserted semantics.
 boundary_types={'ConditionalOpen','ConsequentBoundary','ConditionalClose','ExplanatoryConditionalOpen','DispositionOperator','ConcessionOperator'}
 boundary_rows=[{k:r[k] for k in ['edition','locus','source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']} for r in rows if lex.get(r['ivtff_group_raw'],{}).get('type') in boundary_types]
 signatures={x['id']:x['input'] for x in f['rules'] if x['id'] in ['A3','A4','A5']};census={}
 for label,dictlex in [('first',f['lexicon']),('whole',lex)]:
  census[label]={}
  for rule,types in signatures.items():
   matches=[]
   for xs in lines.values():
    for i in range(len(xs)-len(types)+1):
     sub=xs[i:i+len(types)]
     if [dictlex.get(x['ivtff_group_raw'],{}).get('type','UNKNOWN') for x in sub]==types:matches.append([x['source_group_id'] for x in sub])
   census[label][rule]=matches
 # Independent literal coordinates, not author variant IDs or a grammar parser.
 first_specs={
 'PLACEMENT':(list(range(9,12)), 'chepaiin otodar otodaiin'),
 'MAGNET_RELATION':(list(range(15,19)), 'otchedy olkaiin odar aloees'),
 'MAGNET_DISPOSITION':(list(range(14,19)), 'qopchas otchedy olkaiin odar aloees'),
 'ADAMANT_RELATION':(list(range(19,24)), 'otchedy qotedaiin odar octhody shedaiin'),
 'CONCESSION_PAIR':(list(range(13,24)), 'otaiin qopchas otchedy olkaiin odar aloees otchedy qotedaiin odar octhody shedaiin'),
 'COMPLETE_FIRST_FRAME':(list(range(8,25)), 'otar chepaiin otodar otodaiin opaiin otaiin qopchas otchedy olkaiin odar aloees otchedy qotedaiin odar octhody shedaiin olaiin')}
 specs={k:([(1,i) for i in inds],raw.split()) for k,(inds,raw) in first_specs.items()}
 specs.update({
 'PREVENTION_SENTENCE': ([(9,i) for i in range(1,7)],'daiin qotaiin tchedy otedy qotchdy chckhey'.split()),
 'VIOLENCE_MANNER_SENTENCE': ([(12,i) for i in range(1,5)],'otchs shedor chey sorain'.split()),
 'REPORTED_NAMING_SENTENCE': ([(13,i) for i in range(1,6)],'or shedy tedy sodaiiin chy'.split()),
 'HUMAN_COMPLETE_SENTENCE': ([(ln,i) for ln,n in [(14,4),(15,5),(16,5),(17,3),(18,2)] for i in range(1,n+1)],'ytedar chz[s:r] aiin arody ypshedy dar chedy or am oteey qodaiin odain an chey orar oldar ain okees olaiin'.split())})
 byid={r['source_group_id']:r for r in rows};bypos={(r['edition'],int(r['locus'].split('.')[-1]),int(r['source_group_index'])):r for r in rows}
 spans=[]; variant_map={(v['edition'],v['clause']):v for v in w['variants']+w['new_variants']}
 for ed in counts:
  for clause,(poses,expected) in specs.items():
   selected=[bypos[(ed,*pos)] for pos in poses];ids=[r['source_group_id'] for r in selected];actual=[r['ivtff_group_raw'] for r in selected];match=actual==expected
   v=variant_map[ed,clause]
   ck('span:'+ed+':'+clause,v['ids']==ids and v['actual']==actual and v['literal_match']==match)
   key='required' if clause in first_specs else 'expected'
   mm=[{'id':i,'actual':a,key:e} for i,a,e in zip(ids,actual,expected) if a!=e]
   ck('mismatches:'+ed+':'+clause,v['mismatches']==mm)
   locindexes=[rows.index(r) for r in selected];ck('contiguous:'+ed+':'+clause,locindexes==list(range(locindexes[0],locindexes[0]+len(selected))))
   if clause not in first_specs:
    ck('dependency:'+ed+':'+clause,v['prior_completed_A8_available']==(ed=='ZL3b') and v['new_assertion_available']==(match and ed=='ZL3b'))
   spans.append({'edition':ed,'clause':clause,'ids':ids,'actual':actual,'expected':expected,'literal_match':match,'mismatches':mm,'new_assertion_available':match and ed=='ZL3b' if clause not in first_specs else None,'separators':[{'id':r['source_group_id'],'left':r['left_separator'],'right':r['right_separator']} for r in selected]})
 ck('all_30_spans',len(spans)==len(variant_map)==30)
 ck('first18variants_preserved',w['variants']==f['variants'])
 ck('counts_reader',dict(counts)==w['counts']['by_reader'])
 ck('counts_inventory',len(lex)==w['counts']['whole_types']==46 and len(lex)-len(f['lexicon'])==w['counts']['new_whole_types']==31 and sum(x['assigned'] for x in counts.values())==w['counts']['assigned_rows']==212 and sum(x['unknown'] for x in counts.values())==w['counts']['unknown_rows']==261)
 ck('payload_count',sum(len(v['payloads']) for v in lex.values())==w['costs']['payload_entries']==56)
 ck('no_cuts',all(v['cut'] is None and v['status']=='whole_lookup' for v in lex.values()) and all(r['exact_cut']=='' for r in wholerows))
 ck('first_assignments_marked',all(r['first_assignment_preserved']==('yes' if r['ivtff_group_raw'] in f['lexicon'] else 'not_first_assigned') for r in wholerows))
 ck('whole_status_marked',all(r['whole_status']==('whole_lookup' if r['ivtff_group_raw'] in lex else 'unknown') for r in wholerows))
 firstids=set(next(s['ids'] for s in spans if s['edition']=='ZL3b' and s['clause']=='COMPLETE_FIRST_FRAME'))
 newids=set(i for s in spans if s['edition']=='ZL3b' and s['clause'] not in first_specs for i in s['ids'])
 actualscopes=Counter(r['assertion_scope_status'] for r in wholerows)
 scope_errors=[]; memberships=[]
 for r in wholerows:
  rid=r['source_group_id'];expected_scope='unchanged complete A8' if rid in firstids else 'complete new sentence interface' if rid in newids else 'no complete asserted scope supplied'
  if r['assertion_scope_status']!=expected_scope:scope_errors.append({'id':rid,'actual':r['assertion_scope_status'],'expected':expected_scope})
  pieces=[]
  for ss in spans:
   if rid not in ss['ids']:continue
   if ss['clause'] in first_specs:tag='old_exact_subexpression' if ss['literal_match'] else 'old_INCOMPLETE'
   else:tag='complete_new_assertion' if ss['new_assertion_available'] else 'INCOMPLETE_OR_UNBOUND'
   pieces.append(ss['clause']+':'+tag)
  if r['manual_expression_membership']!=';'.join(pieces):memberships.append({'id':rid,'actual':r['manual_expression_membership'],'expected':';'.join(pieces)})
 ck('all473_scope_flags',not scope_errors,scope_errors)
 ck('all473_memberships',not memberships,memberships)
 zlinv=[]
 for (ed,loc),xs in lines.items():
  if ed=='ZL3b':zlinv.append({'locus':loc,'groups':len(xs),'assigned':sum(x['ivtff_group_raw'] in lex for x in xs),'unknown':[{'id':x['source_group_id'],'raw':x['ivtff_group_raw']} for x in xs if x['ivtff_group_raw'] not in lex]})
 ck('24_line_inventory',zlinv==w['ZL_all24_line_inventory'])
 ck('no_new_old_relation_signatures',census['first']==census['whole'])
 rulemap={r['id']:r for r in w['rules']}
 ck('new_rules_list',list(rulemap)[9:]==w['costs']['new_rules'])
 # Flattened terminal types for the four explicitly offered new constructions.
 terminal_types={
 'PREVENTION_SENTENCE':['CompletedCaseGuardReference','SettingActorReference','PreventionPredicate','SettingPatientReference','ApproachPredicate','ConcededActorReference'],
 'VIOLENCE_MANNER_SENTENCE':['CompletedCaseGuardReference','CompletedMainEffectReference','AdjunctIntroducer','MannerValue'],
 'REPORTED_NAMING_SENTENCE':['SettingActorKindReference','ReportedNamingPredicate','NameDescriptor','NameOfPhrase','NameListAppend'],
 'HUMAN_COMPLETE_SENTENCE':['ExplanatoryConditionalOpen','WomanNoun','AwayStatePredicate','SubjectHusbandNoun','ConditionDisjunction','TrespassPredicate','HumanHusbandReference','SettingActorKindReference','ConsequentBoundary','HumanWomanReference','RelativeTimeModifier','ReconciliationPredicate','PurposeHavingOperator','AdjunctIntroducer','VirtueNoun','LocalStoneKindReference','GraceNoun','HusbandPossessive','ConditionalClose']}
 for name,types in terminal_types.items():ck('new_leaf_types:'+name,[lex[x]['type'] for x in specs[name][1]]==types)
 interface_rows=[{k:r[k] for k in ['source_group_id','ivtff_group_raw','fixed_type','fixed_value','assertion_scope_status']} for r in wholerows if ('Reference' in r['fixed_type'] or r['fixed_type'] in boundary_types or r['fixed_type'] in ['SubjectHusbandNoun','HusbandPossessive'])]
 warnings=[{'code':'STALE_FIRST_RESIDUALS','text':w['residuals'][4:6],'assessment':'Unlabelled retained first-stage missing-duty prose conflicts with present local W/H offers; MD explicitly remains target-incomplete.'}, {'code':'UNCERTAIN_H3_BOUNDARY','ids':['ZL3b|f85r2.15|G004','ZL3b|f85r2.15|G005'],'assessment':'or/am are separate source groups but UNCERTAIN_SMALL_SPACE. No normalization; H3 depends on using this uncertain grouping.'}, {'code':'UNCERTAIN_W2_BOUNDARY','ids':['ZL3b|f85r2.12|G003','ZL3b|f85r2.12|G004'],'assessment':'chey/sorain likewise use UNCERTAIN_SMALL_SPACE; retained literally, not independently secure segmentation.'}]
 result={'status':'LITERAL_CHECKS_WITH_EXPLICIT_CAVEATS','review_start_utc':'2026-09-27T13:23:17+00:00','checks':checks,'failed_checks':[x for x in checks if not x['pass']],'counts':dict(counts),'all_conditional_boundary_rows':boundary_rows,'old_relation_type_signature_census':census,'all30_reader_spans':spans,'scope_counts':dict(actualscopes),'all_interface_word_rows':interface_rows,'complete_scope_union':{'first_ZL_rows':len(firstids),'new_ZL_rows':len(newids),'union':len(firstids|newids),'assigned_outside_assertions':212-len(firstids|newids),'unknown_all':261},'warnings':warnings,'scope_limit':'Literal inventory and manual interface review only. No semantic execution, arbitrary grammar parse enumeration, source-to-manuscript proof, or reading confirmation. New W0/W1/W2/W3b/H8 requirements and old A3-A7 limits inspected in their actual frozen prose.','completed_utc':datetime.now(timezone.utc).isoformat()}
 (B/'ADAMANT_WHOLE_LITERAL_D.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'failed_checks':[{'check':x['check'],'first_details':x['detail'][:3] if isinstance(x['detail'],list) else x['detail']} for x in result['failed_checks']],'scope_counts':dict(actualscopes)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
