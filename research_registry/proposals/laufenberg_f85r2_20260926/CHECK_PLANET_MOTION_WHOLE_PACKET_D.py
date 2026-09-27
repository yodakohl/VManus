#!/usr/bin/env python3
"""Independent literal bookkeeping for frozen602 whole. No parser/semantic executor.
Only explicitly owned safe1042 projection and frozen author inputs are read.
Run from repository root; writes only WHOLE_LITERAL_D.json in the same dossier.
"""
import csv, hashlib, json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
BASE=Path('research_registry/proposals/laufenberg_f85r2_20260926')
NATIVE=Path('experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv')
FIELDS=['edition','block','locus','source_group_id','source_group_index','source_group_count','within_line_position','paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
readj=lambda p:json.loads(p.read_text())
def tsv(p):
    with p.open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
checks=[]
def check(name,good,detail=None):
    checks.append({'check':name,'pass':bool(good),'detail':detail})
first=readj(BASE/'PLANET_MOTION_AUTHOR_FIRST.json')
whole=readj(BASE/'PLANET_MOTION_AUTHOR_WHOLE.json')
firstreceipt=readj(BASE/'PLANET_MOTION_AUTHOR_FIRST_FREEZE_RECEIPT.json')
receipt=readj(BASE/'PLANET_MOTION_AUTHOR_WHOLE_FREEZE_RECEIPT.json')
# Hash-only reads do not inspect B/root review contents.
for stage,rc in [('first',firstreceipt),('whole',receipt)]:
    for spec in rc['files']:
        p=Path(spec['path']);check(stage+'_frozen_hash:'+p.name,sha(p)==spec['sha256'] and p.stat().st_size==spec['bytes'])
check('safe_native_hash',sha(NATIVE)==first['scope']['sha256']==whole['scope']['sha256'])
rows=tsv(NATIVE); ft=tsv(BASE/'PLANET_MOTION_AUTHOR_FIRST_473_CONSEQUENCES.tsv'); wt=tsv(BASE/'PLANET_MOTION_AUTHOR_WHOLE_473_CONSEQUENCES.tsv')
check('scope_unchanged',first['scope']==whole['scope'])
check('original12_column_order',all(list(r[0])[:12]==FIELDS for r in [rows,ft,wt]))
check('first_receipt_hash_in_whole_input_receipt',any(s['path']==str(BASE/'PLANET_MOTION_AUTHOR_FIRST_FREEZE_RECEIPT.json') and s['sha256']==sha(BASE/'PLANET_MOTION_AUTHOR_FIRST_FREEZE_RECEIPT.json') for s in receipt['inputs']))
check('exact473_original12tuples_first',len(rows)==len(ft)==473 and [[r[k] for k in FIELDS] for r in rows]==[[r[k] for k in FIELDS] for r in ft])
check('exact473_original12tuples_whole',len(rows)==len(wt)==473 and [[r[k] for k in FIELDS] for r in rows]==[[r[k] for k in FIELDS] for r in wt])
for old,new in [('components','first_components_unchanged'),('derived_wholes','first_derived_wholes_unchanged'),('rules','first_rules_unchanged'),('types','first_types_unchanged'),('roles','first_roles_unchanged')]:
    check('first_'+old+'_exact',first[old]==whole[new])
check('first_costs_exact',first['costs']==whole['costs']['first_costs_unchanged'])
check('first_lexicon_exact',all(whole['lexicon'].get(k)==v for k,v in first['lexicon'].items()))
for old,new in zip(first['clauses'],whole['manual_derivations'][:3]):
    check('first_clause_exact:'+old['id'],all(new.get('manual_tree' if k=='tree' else k)==v for k,v in old.items()))
lex=whole['lexicon']; extra=whole['additional_lexical_assignments']
check('43_new_unique_wholes',len(extra)==len(set(extra))==43 and set(extra)==set(lex)-set(first['lexicon']))
check('no_new_cuts',all('cut' not in lex[w] for w in extra))
check('14_rule_headings',len(whole['first_rules_unchanged'])+len(whole['additional_rules'])==14 and [x['id'] for x in whole['additional_rules']]==['G%02d'%i for i in range(7,15)])
# Derive ONLY the four first exact products; no broad interpreter is involved.
products={a+b:{'quantity':[n,u]} for a,n in [('d',30),('qoted',2)] for b,u in [('ar','YEAR'),('aiin','DAY')]}
check('G01_domain_four_exact_values',set(products)==set(first['derived_wholes']) and all(lex[w]['value']==v and ''.join(lex[w]['cut'])==w for w,v in products.items()))
occ=defaultdict(list);byline=defaultdict(list); ids={};byreader=Counter(); assigned=Counter(); unknown=Counter();derived=Counter()
for r in rows:
    occ[r['ivtff_group_raw']].append(r['source_group_id']);byline[r['edition'],r['locus']].append(r);ids[r['source_group_id']]=r;byreader[r['edition']]+=1
    (assigned if r['ivtff_group_raw'] in lex else unknown)[r['edition']]+=1
    if r['ivtff_group_raw'] in products:derived[r['edition']]+=1
check('all_occurrence_lists_exact',whole['all_assigned_occurrences']=={w:occ[w] for w in lex})
check('first_occurrence_lists_exact',first['all_assigned_occurrences']=={w:occ[w] for w in first['lexicon']})
check('unique_native_ids',len(ids)==473)
row_errors=[]
for r in wt:
    w=r['ivtff_group_raw'];v=lex.get(w); ln=byline[r['edition'],r['locus']];i=next(j for j,x in enumerate(ln) if x['source_group_id']==r['source_group_id'])
    expected={'fixed_type':v['type'] if v else 'UNKNOWN','whole_page_parse':'NOT_COMPLETE','exact_internal_cut':'+'.join(v.get('cut',[])) if v else ''}
    expected['whole_status']='first_derived_G01' if w in products else ('first_whole_G02' if w in first['lexicon'] else ('exploratory_whole_assignment' if v else 'unknown'))
    for side,idx,boundary in [('left',i-1,'LINE_START'),('right',i+1,'LINE_END')]:
        n=ln[idx] if 0<=idx<len(ln) else None
        expected[side+'_raw']=n['ivtff_group_raw'] if n else boundary
        expected[side+'_type']=lex.get(n['ivtff_group_raw'],{}).get('type','UNKNOWN') if n else 'BOUNDARY'
    errors={k:{'actual':r[k],'expected':x} for k,x in expected.items() if r[k]!=x}
    actual=json.loads(r['fixed_value']) if r['fixed_value'] else None
    if actual!=(v['value'] if v else None):errors['fixed_value']={'actual':actual,'expected':v['value'] if v else None}
    if errors:row_errors.append({'id':r['source_group_id'],'errors':errors})
check('whole_row_values_statuses_neighbors_cuts',not row_errors,row_errors)
first_value_errors=[]
for r in ft:
    v=first['lexicon'].get(r['ivtff_group_raw']);a=json.loads(r['fixed_value']) if r['fixed_value'] else None
    if a!=(v['value'] if v else None) or r['fixed_type']!=(v['type'] if v else 'UNKNOWN'):first_value_errors.append(r['source_group_id'])
check('first_row_values_preserved',not first_value_errors,first_value_errors)
counts={'rows':len(rows),'readers':dict(byreader),'assigned':dict(assigned),'unknown':dict(unknown),'assigned_rows':sum(assigned.values()),'unknown_rows':sum(unknown.values()),'assigned_types':len(lex),'zl_types':len({r['ivtff_group_raw'] for r in rows if r['edition']=='ZL3b'}),'derived_G01':dict(derived),'derived_total':sum(derived.values())}
c=whole['counts'];check('declared_counts',c['all_rows']==len(rows) and c['all_zl_groups']==byreader['ZL3b'] and c['all_zl_types']==counts['zl_types'] and c['assigned_whole_types']==len(lex) and c['new_whole_types']==len(extra) and c['assigned_rows']==sum(assigned.values()) and c['assigned_by_reader']==dict(assigned) and c['unknown_by_reader']==dict(unknown) and c['derived_first_occurrences']==sum(derived.values())==21,counts)
syn=defaultdict(list)
for w,v in lex.items():syn[(v['type'],json.dumps(v['value'],sort_keys=True))].append(w)
synonyms=[v for v in syn.values() if len(v)>1]
check('synonym_classes_and17_extra_spellings',sorted(map(sorted,synonyms))==sorted(map(sorted,whole['costs']['exact_synonym_groups'])) and sum(len(v)-1 for v in synonyms)==17)
def payload(v):
    if v['type']=='PeriodRole' and v['value']=='EACH_SIGN_STAY':return 3
    return 2 if v['type'] in ['Quantity','ConjunctionOperator','PlanetQuantifier','MotionSelector','Direction'] else 1
payloads={w:payload(lex[w]) for w in extra}
check('63_new_payloads_by_declared_convention',sum(payloads.values())==63 and all(lex[w]['payload_count']==n for w,n in payloads.items()))
check('78_total_payloads_by_declared_convention',sum(payloads.values())+first['costs']['semantic_payloads_with_aliases']==78)
# Independent reader-specific literal selections, set after inspecting each reader's own safe rows.
# Equal indices below were verified separately, not inferred from an alignment.
SPAN={
'P1':(9,1,6), 'P2':(10,2,4), 'P3':(15,1,3),'P4':(1,3,6),'P5':(22,1,4),'P6':(5,1,3),'P7':(4,1,3),'P8':(11,1,4),'P9':(14,1,4),'P10':(16,1,5),'P11':(19,1,5),'P12':(20,2,8),'P13':(7,1,5),'P14':(8,1,6)}
EXPECTED={
'ZL3b':[
'daiin qotaiin tchedy otedy qotchdy chckhey','qodar qotedar qokar','ypshedy dar chedy','opaees ar chcthy otchdy','los ar shedy qokshey','ockhdar olkar shoral','dair sheo oraiin','soiis aiin shedaiin chok{co}m','ytedar chz[s:r] aiin arody','oteey qodaiin odain an chey','qokshedy qodain chckhy ykeedy chedy','aiin ckhed[a:y] or ain olchey qokal shedy','pchedeey olkey qokedy sheos fcheey','otchedy chotey qocthey oteey ol oloqorain'],
'IT2a':[
'daiin qotaiin tchedy otedy qotchdy chckhey','qodar qotedar qokar','ypshedy dar chedy','opoees ar chcthy otchdy','los ar shedy qokshey','ockhdor olkor shoral','dair sheo oraiin','soiis aiin shedaiin chokcod','ytedar ch?s aiin arody','oteey qodain odain an chey','qokshedy qodain chckhy ykeedy chedy','aiin ckhedy or ain olchey qokal shedy','pchedeey olkey qokedy sheos fcheey','otchedy chotey qocthey oteey ol oloeorain'],
'RF1b':[
'daiin qotaiin tchedy ote@152;y qotchdy chckhey','qo@152;ar qotedar qokar','yfshe@152;y dar chedy','opoees ar chcthy otchdy','los ar she@152;y qokshey','ockhdar ol@176;ar shoral','dair sheo oraiin','soiis aiin shedaiin chot{co}g','ytedar ch@152;s aiin arody','oteey qodaiin odain an chey','qokshedy qo@152;ain chckhy ykeedy chedy',"aiin ckhe@152;y or ain olchey qokal {ch'}edy","pchedeey olkey qoke@152;y {ch'}eos fcheey",'otche@152;y chotey qocthey oteey ol oloqorain']}
manual=[];members=defaultdict(list)
for i,m in enumerate(whole['manual_derivations']):
    rec={'id':m['id'],'readers':{}}
    for ed in EXPECTED:
        if i<14:
            line,start,end=SPAN['P'+str(i+1)];sel=[r for r in byline[ed,'f85r2.'+str(line)] if start<=int(r['source_group_index'])<=end];wanted=EXPECTED[ed][i].split(' ')
        else:
            sel=byline[ed,'f85r2.19']+byline[ed,'f85r2.20'];wanted=EXPECTED[ed][10].split(' ')+(['or'] if ed=='ZL3b' else ['ar'])+EXPECTED[ed][11].split(' ')
        raw=[r['ivtff_group_raw'] for r in sel];sids=[r['source_group_id'] for r in sel]
        check('independent_native_span:'+m['id']+':'+ed,raw==wanted)
        if ed=='ZL3b':
            check('author_zl_span:'+m['id'],sids==m['zl_source_ids'] and raw==m['raw'])
            spanlines={r['locus'] for r in sel};complete=all(set(x['source_group_id'] for x in byline[ed,lo])<=set(sids) for lo in spanlines)
            check('author_zl_whole_line_flag:'+m['id'],complete==m['whole_line_complete'])
        missing=[{'id':r['source_group_id'],'raw':r['ivtff_group_raw']} for r in sel if r['ivtff_group_raw'] not in lex]
        diffs=[{'offset':j,'raw':w,'type':lex[w]['type'],'value':lex[w]['value'],'zl_raw':m['raw'][j]} for j,w in enumerate(raw) if w in lex and j<len(m['raw']) and (lex[w]['type'],lex[w]['value'])!=(lex[m['raw'][j]]['type'],lex[m['raw'][j]]['value'])]
        flag=m['whole_stage_literal_consequences'][ed]
        positive=flag in ['source_entry_present','partialM01_present','particular_instance_not_universalM02','conjunction_present']
        check('literal_support_for_flag:'+m['id']+':'+ed, (not missing and not diffs) if positive else bool(missing or diffs))
        rec['readers'][ed]={'ids':sids,'raw':raw,'unknown':missing,'known_value_differences_from_zl':diffs,'author_flag':m['whole_stage_literal_consequences'][ed],'boundary_markers':[[r['source_group_id'],r['left_separator'],r['right_separator']] for r in sel]}
        for sid in sids:members[sid].append(m['id']+':'+m['whole_stage_literal_consequences'][ed])
    manual.append(rec)
check('all473_manual_membership_fields',all(r['manual_clause_membership']==' || '.join(members[r['source_group_id']]) for r in wt))
# Check new manual-tree leaf coverage and constructor arities, never evaluate meaning.
arity={'G03':2,'G07':2,'G04':3,'G09':3,'G05':3,'G06':3,'G10':3,'G11':5,'G12':6,'G08':3}
treemap={m['id']:m for m in whole['manual_derivations']}
def leaves(t):
    if isinstance(t,str):return [ids[t]['ivtff_group_raw'] if t in ids else t]
    if 'reference_to_existing_tree' in t:return treemap[t['reference_to_existing_tree']]['raw']
    assert len(t)==1
    rule,children=next(iter(t.items()));assert rule in arity and len(children)==arity[rule]
    return [leaf for child in children for leaf in leaves(child)]
for m in whole['manual_derivations'][3:]:
    try:check('new_tree_leaf_coverage_and_arity:'+m['id'],leaves(m['manual_tree'])==m['raw'])
    except (KeyError,AssertionError,TypeError) as e:check('new_tree_leaf_coverage_and_arity:'+m['id'],False,type(e).__name__)
periods=whole['source_periods'];covered=[p for p in periods if p['zl_status']=='local_manual_tree'];missing=[p for p in periods if p['zl_status']=='UNFULFILLED']
check('14_period_flags_12_local_2_missing',len(periods)==14 and len(covered)==12 and {p['entry'] for p in missing}=={'MARS_SIGN_STAY','MOON_SIGN_STAY'})
check('period_tree_reference_integrity',all(any(m['id']==p['tree'] and m['source_entry']==p['entry'] for m in whole['manual_derivations']) for p in covered))
check('M01_to_M12_flags_present',set(whole['source_duties'])=={'M%02d'%i for i in range(1,13)})
localfacts={}
for ed in EXPECTED:
    s=[ids[ed+'|f85r2.2|G%03d'%i]['ivtff_group_raw'] for i in (2,3)]
    check('adjacent_or_or:'+ed,s==['or','or'])
    a=[r for r in byline[ed,'f85r2.24'] if r['ivtff_group_raw']=='ar']
    localfacts[ed]={'or_or_raw':s,'literal_ar_indices_line24':[int(r['source_group_index']) for r in a]}
check('infix_rules_literal_domains',whole['additional_rules'][1]['input']==['Proposition','AND','Proposition'] and whole['additional_rules'][2]['input']==['QuantityExpr','AND','QuantityExpr'] and lex['or']['type']=='ConjunctionOperator' and 'or' not in first['lexicon'])
check('IT16_source_quantity_difference_literal',ids['IT2a|f85r2.16|G002']['ivtff_group_raw']=='qodain' and lex['qodain']['value']=={'quantity':[27,'DAY']} and lex['qodaiin']['value']=={'quantity':[28,'DAY']} and ids['IT2a|f85r2.16|G004']['ivtff_group_raw']=='an' and lex['an']['value']=={'quantity':[6,'HOUR']})
# Classify literal inventory coverage, not interpreted proposition truth or a final parse.
classes=Counter()
for r in rows:
    w=r['ivtff_group_raw'];sid=r['source_group_id']
    classes['unknown_with_manual_span' if members[sid] else 'unknown_outside_manual_span']+=int(w not in lex)
    classes['assigned_with_manual_span' if members[sid] else 'assigned_outside_manual_span']+=int(w in lex)
inputs=[NATIVE,BASE/'PLANET_MOTION_WHOLE_REVIEW_CONTRACT.md',BASE/'PLANET_MOTION_AUTHOR_FIRST.md',BASE/'PLANET_MOTION_AUTHOR_FIRST.json',BASE/'PLANET_MOTION_AUTHOR_FIRST_473_CONSEQUENCES.tsv',BASE/'PLANET_MOTION_AUTHOR_FIRST_FREEZE_RECEIPT.json',BASE/'PLANET_MOTION_AUTHOR_WHOLE.md',BASE/'PLANET_MOTION_AUTHOR_WHOLE.json',BASE/'PLANET_MOTION_AUTHOR_WHOLE_473_CONSEQUENCES.tsv',BASE/'PLANET_MOTION_AUTHOR_WHOLE_FREEZE_RECEIPT.json']
result={'status':'PASS_LITERAL_BOOKKEEPING_ONLY' if all(c['pass'] for c in checks) else 'LITERAL_DISCREPANCIES','checker_start_observed_utc':'2026-09-27 12:28:06 UTC','completed_utc':datetime.now(timezone.utc).isoformat(),'deadline_utc':'2026-09-27 12:40:00 UTC','checks':checks,'failed_checks':[c for c in checks if not c['pass']],'counts':counts,'manual_span_coverage_categories':dict(classes),'synonym_classes':synonyms,'new_payload_inventory':payloads,'manual_reader_spans':manual,'period_flags':periods,'source_duty_flags':whole['source_duties'],'literal_special_cases':localfacts,'source_flag_limit':'Flags and references verified, not historical source truth, full source coverage, semantic execution or a whole parse.12/14local ZL entries remain different from whole completion. G01 has21unchanged literal instances; no prior consumption criticism is revived.','inputs':[{'path':str(p),'sha256':sha(p)} for p in inputs],'checker_sha256':sha(Path(__file__))}
(BASE/'WHOLE_LITERAL_D.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failed_checks':result['failed_checks'],'counts':counts,'coverage':dict(classes),'completed_utc':result['completed_utc']},indent=2))
