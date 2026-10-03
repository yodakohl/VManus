#!/usr/bin/env python3
"""Frozen-core diagnostics over all35 already-exposed GDT1146 occurrences.
No lexical extension, gloss selection, argument completion or new source access.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
POLICIES=['FORWARD_ORIGIN','INVERTED_ORIGIN','INVERTED_DESTINATION']
STATUSES=['compatible','contradiction','unknown','not_applicable']

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def construction(groups,index,core):
    head=groups[index];out={'producer_id':head['source_group_id'],'producer_raw':head['ivtff_group_raw'],
        'argument_ids':[],'raw_arguments':[],'seams':[],'bindings':None}
    if head['ivtff_group_raw']!='qokedy':
        return dict(out,status='not_applicable',reason='not_exact_qokedy')
    if index==0 or index+1==len(groups):
        return dict(out,status='not_applicable',reason='missing_written_side_no_implicit_argument')
    left,right=groups[index-1],groups[index+1]
    out['argument_ids']=[left['source_group_id'],right['source_group_id']]
    out['raw_arguments']=[left['ivtff_group_raw'],right['ivtff_group_raw']]
    out['seams']=[left['right_separator'],head['left_separator'],head['right_separator'],right['left_separator']]
    if int(head['source_group_index'])-int(left['source_group_index'])!=1 or int(right['source_group_index'])-int(head['source_group_index'])!=1:
        return dict(out,status='unknown',reason='noncontiguous_native_indices')
    if set(out['seams'])!={'DEFINITE_SPACE'}:
        return dict(out,status='unknown',reason='uncertain_or_nondefinite_seam')
    licenses=core['whole_word_licenses']
    meanings=[licenses.get(g['ivtff_group_raw']) for g in [left,right]]
    if any(m is None or 'role' not in m or 'root' not in m for m in meanings):
        return dict(out,status='not_applicable',reason='unlicensed_nominal_side_no_wholeform_or_affix_default')
    roles=[m['role'] for m in meanings]
    if sorted(roles)!=['ACTIVE','RECEPTIVE']:
        return dict(out,status='contradiction',reason='fully_licensed_roles_not_one_active_one_receptive',licensed_roles=roles)
    a=roles.index('ACTIVE');r=roles.index('RECEPTIVE');roots=[m['root'] for m in meanings]
    if roots[a]=='LOCAL_PRINCIPLE_VARIABLE':
        if roots[r]=='LOCAL_PRINCIPLE_VARIABLE':
            return dict(out,status='unknown',reason='no_written_rooted_receptive_for_variable')
        roots[a]=roots[r]
    if roots[a]!=roots[r]:
        return dict(out,status='contradiction',reason='fully_licensed_principle_conflict',licensed_roots=roots)
    nominal=[left,right]
    binding={'root':roots[a], 'active':{'source_group_id':nominal[a]['source_group_id'],'whole_form':nominal[a]['ivtff_group_raw'],'role':'ACTIVE','root':roots[a]},
        'receptive':{'source_group_id':nominal[r]['source_group_id'],'whole_form':nominal[r]['ivtff_group_raw'],'role':'RECEPTIVE','root':roots[r]},
        'cataphoric_unification':meanings[a]['root']=='LOCAL_PRINCIPLE_VARIABLE'}
    return dict(out,status='compatible',reason='closed_same_principle_active_receptive_triple',bindings=binding)

def edge(local,policy):
    if local['status']!='compatible':return None
    b=local['bindings'];origin,destination=(b['active'],b['receptive']) if policy=='FORWARD_ORIGIN' else (b['receptive'],b['active'])
    return {'producer_id':local['producer_id'],'root':b['root'],'origin':origin,'destination':destination,
        'qody_endpoint':'DESTINATION' if policy=='INVERTED_DESTINATION' else 'ORIGIN',
        'scope':'CONDITIONAL_LOCAL_CONSTRUCTION_NOT_WHOLE_LINE_ASSERTION'}

def diagnostics(core,source_path):
    source=read(source_path);assert len(source)==35
    rows=[]
    for case in source:
        groups=case['complete_line_groups'];focal=case['left']['source_group_id']
        assert len(groups)==int(case['metadata']['source_group_count'])
        assert [int(g['source_group_index']) for g in groups]==list(range(1,len(groups)+1))
        assert all(g['source_group_id'].startswith(case['edition']+'|'+case['locus']+'|') for g in groups)
        focal_index=next(i for i,g in enumerate(groups) if g['source_group_id']==focal)
        assert groups[focal_index]==case['left'] and groups[focal_index+1]==case['right']
        local=construction(groups,focal_index,core)
        constructions=[construction(groups,i,core) for i,g in enumerate(groups) if g['ivtff_group_raw']=='qokedy']
        unknown_ids=[g['source_group_id'] for g in groups if g['ivtff_group_raw'] not in core['whole_word_licenses']]
        # Exact standalone acts/nominals are licensed values, not a complete statement grammar.
        consumed={x for c in constructions if c['status']=='compatible' for x in [c['producer_id']]+c['argument_ids']}
        remaining=[g['source_group_id'] for g in groups if g['source_group_id'] not in consumed]
        refs=[]
        for i,g in enumerate(groups):
            if g['ivtff_group_raw']=='solchedy':
                available=[c for c in constructions if c['status']=='compatible' and c['bindings']['root']=='UNDERSTAND' and next(j for j,k in enumerate(groups) if k['source_group_id']==c['producer_id'])<i]
                refs.append({'reference_id':g['source_group_id'],'conditional_selected_producer':available[-1]['producer_id'] if available else None,
                    'status':'conditional_local_reference' if available else 'unknown',
                    'reason':'nearest_earlier_core_producer_inside_available_line' if available else 'no_licensed_earlier_producer_in_available_line_prior_chain_not_supplied'})
        # This panel contains no QODY: do not claim an endpoint test from edge order alone.
        assert not any(g['ivtff_group_raw']=='qody' for g in groups)
        whole={'status':'unknown' if remaining else 'compatible',
            'unknown_group_ids':unknown_ids,'unconsumed_or_scope_unresolved_group_ids':remaining,
            'conditional_local_conflict_ids':[c['producer_id'] for c in constructions if c['status']=='contradiction'],
            'reference_obligations':refs,'endpoint_consumers':[],
            'reason':'unassigned_surrounding_scope_or_unconsumed_licensed_material_prevents_whole_assertion' if remaining else 'all_available_line_consumed_under_core',
            'prior_complete_chain_available':False,'old1147_chain_not_repaired':True}
        rows.append({'case_id':focal,'edition':case['edition'],'prior_phase':case['phase'],'page':case['page'],'leaf':case['leaf'],'locus':case['locus'],
            'metadata':case['metadata'],'complete_line_groups':groups,'native_raw_groups_in_order':[g['ivtff_group_raw'] for g in groups],
            'predecessor':{'experiment':'GDT1146','classification':case['classification'],'outcome':case['outcome'],'old_recipe_and_product_semantics_imported':False},
            'focal_producer_id':focal,'local':local,'whole_context':whole,'all_qokedy_constructions_in_line':constructions,
            'policy_results':{p:{'local_status':local['status'],'conditional_local_edge':edge(local,p),'whole_status':whole['status'],
                'endpoint_assertion_tested':False} for p in POLICIES},
            'exposure':'PREVIOUSLY_EXPOSED_COUNTEREXAMPLE_PANEL_NOT_HOLDOUT'})
    assert len({r['case_id'] for r in rows})==35
    assert len({r['locus'] for r in rows})==13 and len({r['leaf'] for r in rows})==8
    totals=lambda subset:{'cases':len(subset),'local':{s:sum(r['local']['status']==s for r in subset) for s in STATUSES},'whole_context':{s:sum(r['whole_context']['status']==s for r in subset) for s in STATUSES}}
    return {'experiment':'GDT1163','schema':'CORE_DIAGNOSTICS_V1','core_sha256':sha(EXP/'src/CORE_FREEZE.json'),'input_sha256':sha(source_path),
        'scope':{'cases':35,'distinct_loci':13,'physical_leaves':8,'readers_are_alternatives':True,'complete_native_lines_retained':True,'new_access':False},
        'policies':POLICIES,'rows':rows,'totals':totals(rows),'by_reader':{o:totals([r for r in rows if r['edition']==o]) for o in sorted({r['edition'] for r in rows})},
        'by_policy':{p:totals(rows) for p in POLICIES},
        'retained_ambiguity':['FORWARD_ORIGIN and INVERTED_DESTINATION paired-reversal symmetry','No QODY consumer in this diagnostic panel; edge directions alone select no policy','Anonymous renaming of UNDERSTAND/LOVE preserves all formal outcomes','No whole-line reading from a locally compatible triple','Alternate readers do not create independent witnesses'],
        'confirmed_words':0,'independent_meaning_confirmation_capacity':0}

def integrate_author(core,diagnostic):
    lockpath=EXP/'artifacts/AUTHOR_LOCK.json'
    assert sha(lockpath)=='993147a54c2cde15d8c8c2ea05ff1103abe4e2d872c1c944f56b2ea6d2333208'
    lock=read(lockpath)
    for path,pin in lock['files'].items():assert sha(ROOT/path)==pin, path
    assert lock['core_sha256']==sha(EXP/'src/CORE_FREEZE.json')
    assert sha(ROOT/core['input']['native_packet'])==core['input']['native_packet_sha256']
    assert sha(ROOT/core['word_prior_source'])==core['word_prior_sha256']
    author=read(EXP/'artifacts/AUTHOR_ACCOUNT.json')
    assert author['source_receipt']['core_sha256']==lock['core_sha256']
    assert author['source_receipt']['native_packet_sha256']==core['input']['native_packet_sha256']
    contributions=author['contributions']
    expected=[(f'IT2a|f83r.{line}|G{i:03d}',raw) for line,groups in core['input']['groups'].items() for i,raw in enumerate(groups,1)]
    assert [(r['source_group_id'],r['raw']) for r in contributions]==expected and len(expected)==32
    counts=Counter(r['lexical_status'] for r in contributions)
    unknown=[r['source_group_id'] for r in contributions if r['lexical_status']=='UNKNOWN']
    unbound=[r['source_group_id'] for r in contributions if r['scope_status']=='UNBOUND_PARAMETER']
    assert counts=={'CORE_C0':12,'EXTENSION_C0':7,'UNKNOWN':13}
    assert unbound==author['lexical_coverage']['unbound_core_parameters']
    assert author['lexical_coverage']==lock['accounting']
    caps={k:{'count':author['cap_ledger'][k]['count'],'limit':limit,'within_cap':author['cap_ledger'][k]['count']<=limit}
          for k,limit in [('additional_content_roots',3),('additional_functional_heads',4),('constructions_total',6),('exceptional_whole_form_entries',8)]}
    policies=[]
    assert [p['policy'] for p in author['policy_executions']]==POLICIES
    for execution in author['policy_executions']:
        assert execution['status']==execution['conditional_core_result']==lock['policy_results'][execution['policy']]
        policies.append({'policy':execution['policy'],'conditional_core_result':execution['conditional_core_result'],
            'whole_execution':execution['whole_execution'],'returned_relation':execution['returned_relation'],
            'consumer':execution['consumer'],'not_executed_tail':execution['not_executed_tail']})
    complete=not unknown and not unbound and all(p['whole_execution']['status']!='BLOCKED_UNKNOWN_SCOPE' for p in policies)
    status='AUTHORING_CONTRACT_FAIL' if not all(c['within_cap'] for c in caps.values()) else 'FULL_C0_RELATIONAL_ACCOUNT' if complete else 'PARTIAL_NO_COMPLETE_READING'
    assert status==author['status']==lock['status']
    result={'experiment':'GDT1163','status':status,'author_lock_sha256':sha(lockpath),
        'author_account_sha256':sha(EXP/'artifacts/AUTHOR_ACCOUNT.json'),'core_sha256':lock['core_sha256'],
        'diagnostics_sha256':sha(EXP/'artifacts/DIAGNOSTICS.json'),
        'source_bindings':{'native_packet':core['input']['native_packet_sha256'],'word_priors':core['word_prior_sha256'],'diagnostic_cases':core['diagnostic_scope']['sha256']},
        'accounting':author['lexical_coverage'],'unknown_position_ids':unknown,'unbound_core_parameter_ids':unbound,
        'cap_checks':caps,'policy_results':policies,'whole_context_blocked':not complete,
        'diagnostic_totals':diagnostic['totals'],'diagnostic_by_reader':diagnostic['by_reader'],
        'retained_symmetries':diagnostic['retained_ambiguity'],
        'decision':author['decision'],'new_target_access':0,'confirmed_words':0,'independent_meaning_confirmation_capacity':0,
        'claim_ceiling':'Frozen exploratory authoring account and conditional core only; whole reading incomplete, no root meaning or orientation selected. Independent validator executes dependencies separately.'}
    write(EXP/'artifacts/RESULT.json',result)
    def esc(value):return str(value).replace('&','&amp;').replace('|','&#124;').replace('\n','<br>')
    lines=['# GDT1163 complete candidate/account table','','Display of the single [locked author account](artifacts/AUTHOR_ACCOUNT.json). No lexical alterations. All English meanings remain C0 hypotheses; UNKNOWN and unbound scope prevent a complete reading.','',
        '|Position|Exact source ID|Raw group|Lexical status|C0 meaning / unknown|Attachment|Attachment debt|Scope|',
        '|---:|---|---|---|---|---|---|---|']
    for i,row in enumerate(contributions,1):
        values=[i,row['source_group_id'],row['raw'],row['lexical_status'],row['meaning'],row['attachment'],row['attachment_debt'],row['scope_status']]
        lines.append('|'+'|'.join(esc(v) for v in values)+'|')
    lines+=['','## All three policies','','|Policy|Conditional core|Whole execution|Returned producer|Consumed endpoint kind|', '|---|---|---|---|---|']
    for p in policies:
        endpoint=p['consumer']['consumed_endpoint']
        lines.append('|'+'|'.join(esc(v) for v in [p['policy'],p['conditional_core_result'],p['whole_execution']['status'],p['returned_relation']['producer'],endpoint['role']+':'+endpoint['root']])+'|')
    lines+=['',f'Registered authoring result: **{status}**.','',
        'FORWARD_ORIGIN and INVERTED_DESTINATION retain the paired-reversal symmetry. PASS concerns only conditional core execution; all three whole-context executions remain blocked. The old35-case panel uses the frozen core only; [all diagnostics](artifacts/DIAGNOSTICS.json) retain complete native contexts. No alternate transcript is an independent witness.','',
        'Confirmed meanings: **0**. Independent meaning-confirmation capacity added: **0**.','']
    (EXP/'CANDIDATE_TABLE.md').write_text('\n'.join(lines))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--diagnostics-only',action='store_true');args=ap.parse_args()
    ack=read(EXP/'artifacts/ROOT_CORE_ACK.json');assert sha(EXP/'src/CORE_FREEZE.json')==ack['core_sha256']
    core=read(EXP/'src/CORE_FREEZE.json');source_path=ROOT/core['diagnostic_scope']['input']
    assert sha(source_path)==core['diagnostic_scope']['sha256']
    result=diagnostics(core,source_path);write(EXP/'artifacts/DIAGNOSTICS.json',result)
    with (EXP/'artifacts/DIAGNOSTICS.tsv').open('w',newline='') as f:
        writer=csv.writer(f,delimiter='\t');writer.writerow(['case_id','reader','page','leaf','locus','local_status','local_reason','whole_context_status','unknown_ids','complete_raw_groups_json','complete_native_groups_json','policies_json'])
        for r in result['rows']:
            writer.writerow([r['case_id'],r['edition'],r['page'],r['leaf'],r['locus'],r['local']['status'],r['local']['reason'],r['whole_context']['status'],json.dumps(r['whole_context']['unknown_group_ids']),json.dumps(r['native_raw_groups_in_order'],ensure_ascii=False),json.dumps(r['complete_line_groups'],ensure_ascii=False),json.dumps(r['policy_results'],ensure_ascii=False)])
    print(json.dumps(result['totals']))
    if not args.diagnostics_only:
        final=integrate_author(core,result)
        print(final['status'])
if __name__=='__main__':main()
