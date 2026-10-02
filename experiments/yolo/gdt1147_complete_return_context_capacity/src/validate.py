#!/usr/bin/env python3
"""Independent metadata-first boundary/candidate check. No run.py import.

Known means only membership in the frozen23-whole-form dictionary. This is
not a paragraph interpreter, and no product is seeded. Only own JSON written.
"""
import ast
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode=True
EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
METHOD='c4be3c3f5b6751296ae86fa29b2ac4ac9273053988d93ec45e020f7bed22486f'
SOURCE='d621aa3e045988858be828b4a1bc509bda7f03ab300c35eec112d62f7b5b2e0a'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

def safe(s):
    p=Path(s)
    if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe receipt path')
    return ROOT/p

def joined(a,b):
    return int(b['source_group_index'])-int(a['source_group_index'])==1 and (a['right_separator'],b['left_separator'])==('DEFINITE_SPACE','DEFINITE_SPACE')

def main():
    checks=[]
    def check(name,ok,evidence=None):
        checks.append({'name':name,'pass':bool(ok),'evidence':evidence})
    source=load(EXP/'src/SOURCE.json'); lock=load(EXP/'src/PREREG_LOCK.json')
    pins={r['path']:sha(safe(r['path'])) for r in source['inputs']}
    rootfiles=['METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/PREREG_LOCK.json','src/run.py',
               'artifacts/SELECTION.json','artifacts/NATIVE_SOURCE.json','artifacts/CASES.json','artifacts/RESULT.json']
    before={s:sha(EXP/s) for s in rootfiles}
    check('registered_contract_and_lock_pins',before['METHOD.md']==METHOD and before['src/SOURCE.json']==SOURCE and all(before[s]==h for s,h in lock['hashes'].items()))
    check('all_eight_source_construction_pins',all(pins[r['path']]==r['sha256'] for r in source['inputs']),pins)
    docs={Path(s).stem:load(safe(s)) for s in pins if '/SOURCE_EVALUATION_' in s}
    spec=load(safe(next(s for s in pins if s.endswith('/SPEC.json'))))
    # Boundary discovery dereferences metadata only; no word-based selection.
    meta={ed:sorted([line['metadata'] for line in docs['SOURCE_EVALUATION_'+ed]['lines']
                       if line['metadata']['page']==source['page']],key=lambda m:int(m['source_row_index']))
          for ed in spec['editions']}
    zl=meta['ZL3b']; anchor=next(i for i,m in enumerate(zl) if m['locus']==source['anchor_locus'])
    starts=[i for i in range(anchor+1) if zl[i]['paragraph_start']=='1']
    ends=[i for i in range(anchor,len(zl)) if zl[i]['paragraph_end']=='1']
    if not starts or not ends:raise ValueError('Missing native paragraph boundary capacity; no body window constructed')
    lower,upper=starts[-1],ends[0]; primary_meta=zl[lower:upper+1]
    loci=[m['locus'] for m in primary_meta]
    selection=load(EXP/'artifacts/SELECTION.json')
    check('independent_ZL_boundary_metadata_and_no_crossed_start',primary_meta[0]['paragraph_start']=='1' and primary_meta[-1]['paragraph_end']=='1'
          and not any(m['paragraph_start']=='1' for m in primary_meta[1:])
          and all(int(b['source_row_index'])==int(a['source_row_index'])+1 for a,b in zip(primary_meta,primary_meta[1:])),
          {'first':loci[0],'last':loci[-1],'lines':len(loci),'kinds':dict(Counter(m['kind'] for m in primary_meta))})
    check('root_selection_exact_metadata_first',selection['loci']==loci and selection['metadata']==primary_meta and selection['first']==loci[0] and selection['last']==loci[-1])
    stamp=lambda s:datetime.fromisoformat(s.replace('Z','+00:00'))
    check('documented_registration_before_boundary_selection',stamp(lock['utc'])<stamp(selection['utc']),
          'Documented local chronology only; no public pre-data timestamp or blindness certificate.')
    expected_native={}
    for ed in spec['editions']:
        snap=docs['SOURCE_EVALUATION_'+ed]
        rows=sorted([line for line in snap['lines'] if line['metadata']['page']==source['page'] and line['metadata']['locus'] in loci],key=lambda line:int(line['metadata']['source_row_index']))
        expected_native[ed]={'group_columns':snap['group_columns'],'lines':rows}
        check(ed+'_exact_aligned_complete_window_and_all_kinds',len(rows)==len(loci) and [r['metadata']['locus'] for r in rows]==loci
             and Counter(r['metadata']['kind'] for r in rows)==Counter(m['kind'] for m in primary_meta)
             and all(int(b['metadata']['source_row_index'])==int(a['metadata']['source_row_index'])+1 for a,b in zip(rows,rows[1:])))
    check('native_source_all_snapshot_fields_exact',expected_native==load(EXP/'artifacts/NATIVE_SOURCE.json'))
    authorpath=safe(next(s for s in pins if s.endswith('/src/author.py')))
    lexicon={}
    for node in ast.parse(authorpath.read_text()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['CORE_WORDS','EXTENSION'] for t in node.targets):
            values=ast.literal_eval(node.value)
            check('nonoverlapping_frozen_dictionary_'+node.targets[0].id,not set(lexicon)&set(values))
            lexicon.update(values)
    check('exact23_existing_whole_licenses',len(lexicon)==23)
    corepath=safe(next(s for s in pins if s.endswith('/src/core.py')))
    module_spec=importlib.util.spec_from_file_location('independent_1137_core',corepath)
    core=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(core)
    recorded=load(EXP/'artifacts/CASES.json'); expected={}; selector_api={}
    for ed,packet in expected_native.items():
        flat=[];byline=[]
        for line in packet['lines']:
            gs=[]
            for raw in line['groups']:
                g=dict(zip(packet['group_columns'],raw))
                g.update(locus=line['metadata']['locus'],kind=line['metadata']['kind'],position=len(flat),known=g['ivtff_group_raw'] in lexicon)
                gs.append(g);flat.append(g)
            byline.append(gs)
        check(ed+'_all_native_groups_unique_preserved_order',len({g['source_group_id'] for g in flat})==len(flat) and
              all([int(g['source_group_index']) for g in gs]==sorted({int(g['source_group_index']) for g in gs}) for gs in byline))
        qcases=[]
        for gs in byline:
            for i,g in enumerate(gs):
                if g['ivtff_group_raw']!='qokedy':continue
                q={'q':g,'status':'RIGHT_OUTSIDE_LICENSES','span':[]}
                right=gs[i+1] if i+1<len(gs) else None
                left=gs[i-1] if i else None
                if right is None:q['status']='LINE_END'
                else:
                    q['right']=right; rw=right['ivtff_group_raw']
                    if rw in core.LICENSES:
                        if not joined(g,right):q['status']='UNCERTAIN_RIGHT_SEAM'
                        elif rw in ['chedy','shedy']:
                            q.update(status='UNARY_PRODUCT',span=[g,right],product=core.qokedy(core.lexical_nominal(rw),g['source_group_id']))
                        elif left is None:q['status']='MISSING_LEFT_DY'
                        else:
                            q['left']=left
                            if left['ivtff_group_raw'] not in ['chedy','shedy']:q['status']='LEFT_OUTSIDE_DY'
                            elif not joined(left,g):q['status']='UNCERTAIN_LEFT_SEAM'
                            else:
                                product=core.qokedy(core.lexical_nominal(left['ivtff_group_raw']),g['source_group_id'])
                                q.update(status='BINARY_PRODUCT',span=[left,g,right],product=product,
                                    assertion=core.source_predicate(product,core.lexical_nominal(rw)))
                qcases.append(q)
        producers=[q for q in qcases if 'product' in q]
        unknown=lambda lo,hi:[g for g in flat if lo<g['position']<hi and not g['known']]
        che=core.lexical_nominal('chedy'); returns=[]; api_records=[]
        for g in flat:
            if g['ivtff_group_raw']!='solchedy':continue
            prior=[p for p in producers if max(x['position'] for x in p['span'])<g['position']]
            later=[p for p in producers if max(x['position'] for x in p['span'])>=g['position']]
            matching=[p for p in prior if (p['product']['material'],p['product']['operations'])==(che['material'],che['operations'])]
            candidates=[p for p in matching if prior.index(p)<len(prior)-1]
            status='EARLIER_TYPED_CANDIDATE' if candidates else 'LATEST_COMPATIBLE_ONLY_IN_KNOWN_PROJECTION' if matching else 'NO_MATCHING_KNOWN_PRODUCER'
            ret={'selector':g,'status':status,'earlier_producers':[p['q']['source_group_id'] for p in prior],
                 'matching_producers':[p['q']['source_group_id'] for p in matching],
                 'earlier_typed_candidates':[p['q']['source_group_id'] for p in candidates],
                 'later_excluded':[p['q']['source_group_id'] for p in later],
                 'unknown_before':unknown(-1,g['position']),
                 'witnesses':[{'producer':p['q']['source_group_id'],'span':p['span'],
                    'unknown_between':unknown(max(x['position'] for x in p['span']),g['position'])} for p in prior]}
            returns.append(ret)
            # Known projection only, never execute unknown intervals or seed types.
            policies={}
            for policy in ['explicit-earlier-type','latest-product-only']:
                try:
                    value=core.sol([p['product'] for p in prior],che,policy)
                except ValueError as error:policies[policy]={'defined':False,'error':str(error)}
                else:policies[policy]={'defined':True,'result':value}
            api_records.append({'selector_id':g['source_group_id'],'projection_only':True,'policies':policies})
        selector_api[ed]=api_records
        consumers=[{'consumer':g,'prior_return_candidates':[{'selector_id':r['selector']['source_group_id'],
                   'status':r['status'],'unknown_between':unknown(r['selector']['position'],g['position'])}
                   for r in returns if r['selector']['position']<g['position']]}
                   for g in flat if g['ivtff_group_raw']=='qody']
        coverage={'total':len(flat),'known':sum(g['known'] for g in flat),'unknown':sum(not g['known'] for g in flat),
                  'known_form_counts':dict(Counter(g['ivtff_group_raw'] for g in flat if g['known']))}
        differences=[{'locus':r['metadata']['locus'],'ZL':[primary_meta[i][k] for k in ['paragraph_start','paragraph_end']],
              ed:[r['metadata'][k] for k in ['paragraph_start','paragraph_end']]}
              for i,r in enumerate(packet['lines']) if any(r['metadata'][k]!=primary_meta[i][k] for k in ['paragraph_start','paragraph_end'])]
        expected[ed]={'groups':flat,'coverage':coverage,'qokedy_cases':qcases,'returns':returns,'consumers':consumers,'boundary_differences':differences}
        check(ed+'_all_coverage_and_unknowns_exact',recorded[ed]['groups']==flat and recorded[ed]['coverage']==coverage)
        check(ed+'_all_H2_producers_status_spans_actual_core_fields',recorded[ed]['qokedy_cases']==qcases)
        check(ed+'_all_SOL_ordering_candidates_unknown_barriers',recorded[ed]['returns']==returns)
        check(ed+'_all_written_QODY_and_actual_prior_returns',recorded[ed]['consumers']==consumers)
        check(ed+'_reader_boundary_differences_exact',recorded[ed]['boundary_differences']==differences)
    result=load(EXP/'artifacts/RESULT.json')
    expected_readers={ed:{'coverage':v['coverage'],'qokedy':len(v['qokedy_cases']),'products':sum('product' in q for q in v['qokedy_cases']),
           'returns':[{'locus':r['selector']['locus'],'id':r['selector']['source_group_id'],'status':r['status'],
              'earlier_typed_candidates':r['earlier_typed_candidates'],'unknown_before':len(r['unknown_before'])} for r in v['returns']],
           'consumers':len(v['consumers']),'boundary_differences':v['boundary_differences']} for ed,v in expected.items()}
    decision='NEW_WRITTEN_REFERENCE_CANDIDATE' if any(r['status']=='EARLIER_TYPED_CANDIDATE' for v in expected.values() for r in v['returns']) else 'FIXED_CONSTRUCTION_CONTEXT_INCOMPLETE'
    check('all_case_objects_exact_no_unlisted_seed_products',recorded==expected)
    check('root_result_counts_scope_and_decision',result['readers']==expected_readers and result['scope']==loci and result['decision']==decision)
    check('no_whole_execution_meaning_confirmation_claim',result['full_execution'] is False and result['confirmed_words']==result['independent_confirmation_capacity']==0)
    check('all_root_artifacts_and_bound_legacy_bytes_unchanged',before=={s:sha(EXP/s) for s in before} and pins=={s:sha(safe(s)) for s in pins})
    output={'experiment':'GDT1147','validator_sha256':sha(Path(__file__)),'accounting_pass':all(c['pass'] for c in checks),
       'checks':checks,'independent_decision':decision,'metadata_scope':{'primary':'ZL3b','first':loci[0],'last':loci[-1],
          'lines':len(loci),'kinds':dict(Counter(m['kind'] for m in primary_meta)),
          'RF_status':'Inherited aligned window; no independent RF paragraph boundary flags.'},
       'reader_summary':expected_readers,'known_projection_selector_API':selector_api,'licensed_whole_inventory':sorted(lexicon),
       'root_pins':before,'source_pins':pins,'interpretation':{
          'fixed_construction':'No earlier H2 product occurs before the sole written SOLCHEDY. The binary SHE and later unary CHE products cannot supply its antecedent.',
          'unknowns':'Unknown-before lists are exact43/42/44 occurrences, not executed no-ops or proof that no other semantic antecedent exists.',
          'consumer':'No exact written QODY in this selected window; no synthetic attachment or full consumer execution.',
          'licensed_coverage':'known is frozen whole-dictionary membership only, not interpreted sentences, valid bindings or confirmed meanings.'},
       'limits':['Conditional known-producer availability only, not whole paragraph translation or general reference impossibility.',
          'L rows are preserved in the metadata-defined window; source row order is the registered projection, not independently recovered reading order.',
          'Original1137/1146 and H2 history remain unchanged; this neither rescues1146 nor confirms H2 or material meanings.',
          'Alternate readers describe one manuscript; RF closure is not independently established.',
          'Local documentary chronology only; all data exposed, no new holdout, significance, scored edge or reserve eligibility.'],
       'confirmed_words':0,'full_execution':False,'reserves':'CLOSED'}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'accounting_pass':output['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],
        'decision':decision,'groups':{ed:v['coverage']['total'] for ed,v in expected.items()}}))
    return 0 if output['accounting_pass'] else 1

if __name__=='__main__':
    raise SystemExit(main())
