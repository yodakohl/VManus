#!/usr/bin/env python3
"""Independent GDT733 validator; deliberately does not import run.py."""
from __future__ import annotations
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path

def find_root(p):
    for q in (p,*p.parents):
        if (q/'AGENTS.md').is_file() and (q/'.git').exists(): return q
    raise RuntimeError('root')
ROOT=find_root(Path(__file__).resolve()); EXP=ROOT/'experiments/yolo/gdt733_v99r6_integrated_legacy_grade_cache_renderer'; SRC=EXP/'src'; ART=EXP/'artifacts'
G671=ROOT/'experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts'; G696=ROOT/'experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts'; G727=ROOT/'experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts'; G730=ROOT/'experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/artifacts'; G732=ROOT/'experiments/yolo/gdt732_v99r5_grade_frame_spoken_renderer/artifacts'
GRADE=re.compile(r'(?:Grades|Gradanfang|Gradmitte|Gradende)',re.I)
def tsv(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(r,field='token_ordinal'):return r['page'],r['locus'],int(r[field]),r['surface']

def main():
    checks=[]
    def ck(name,cond,detail=''):
        assert cond,f'{name}: {detail}'; checks.append({'name':name,'status':'PASS','detail':detail})
    pages=tsv(G671/'PAGE_ALLOWLIST.tsv'); source=tsv(G671/'ALL_LINE_CONCRETE_COVERAGE_V48.tsv')
    cells=tsv(ART/'V99R6_32339_CELL_REGISTER.tsv'); lines=tsv(ART/'V99R6_4128_INTEGRATED_LINE_READER.tsv')
    contexts=tsv(G727/'V99_479_CONTEXT_REALIZATIONS.tsv'); dictionary=tsv(G730/'V99R4_COMPLETE_WORD_CONFIDENCE.tsv')
    residual=tsv(G732/'V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv'); specs=tsv(SRC/'ALIAS_MERGE_SPECS.tsv')
    punct_specs=tsv(SRC/'STRUCTURAL_PUNCTUATION_SPECS.tsv')
    precedence=tsv(SRC/'INTEGRATION_PRECEDENCE.tsv'); merges=tsv(ART/'V99R6_8_ALIAS_MERGE_AUDIT.tsv'); bound=tsv(ART/'V99R6_8_CURRENT_V99_BOUND_SPAN_AUDIT.tsv'); punct=tsv(ART/'V99R6_4_PUNCTUATION_ATTACHMENT_AUDIT.tsv'); supers=tsv(ART/'V99R6_52_SUPERSEDED_EXACT_V48_AUDIT.tsv'); summaries=tsv(ART/'V99R6_INTEGRATION_CLASS_SUMMARY.tsv'); quality=tsv(ART/'V99R6_RENDER_QUALITY_SUMMARY.tsv'); parity=tsv(ART/'V99R6_INHERITED_ARTIFACT_PARITY.tsv'); result=json.loads((ART/'RESULT.json').read_text())
    pset={r['page'] for r in pages}; ck('179 allowed pages',len(pages)==len(pset)==179); ck('sealed absent',not any(re.match(r'^f84(?:r|v|$)',p) for p in pset))
    ck('source shape',len(source)==4128 and sum(int(r['token_count']) for r in source)==32339)
    skeys=[]; sgloss={}
    for r in source:
        toks=r['zl3b_line'].split(); gl=r['token_glosses_de'].split(' | '); ck('aligned '+r['locus'],len(toks)==len(gl)==int(r['token_count']))
        for n,(s,g) in enumerate(zip(toks,gl),1): k=(r['page'],r['locus'],n,s); skeys.append(k); sgloss[k]=g
    ckeys=[key(r) for r in cells]; ck('32339 unique keys',len(cells)==len(ckeys)==len(set(ckeys))==32339); ck('key order parity',ckeys==skeys); ck('inherited values',all(r['inherited_v48_gloss_de']==sgloss[key(r)] for r in cells)); ck('no new pages',{r['page'] for r in cells}=={r['page'] for r in lines}<=pset)
    expected={r['integration_class']:int(r['expected_cell_count']) for r in precedence}; actual=Counter(r['integration_class'] for r in cells)
    ck('exact class partition',actual==Counter(expected),{'expected':expected,'actual':dict(actual)}); ck('precedence priorities',sorted(int(r['priority']) for r in precedence)==list(range(1,len(precedence)+1))); ck('class summary',len(summaries)==len(expected) and all(int(r['actual_cell_count'])==actual[r['integration_class']]==int(r['expected_cell_count']) for r in summaries))
    ck('7132 spoken grade cells',sum(r['grade_policy_id']!='NONE' for r in cells)==7132); ck('zero audible cell frames',not any(GRADE.search(r['v99r6_spoken_cell_de']) for r in cells)); ck('zero audible line frames',len(lines)==4128 and all(int(r['grade_frame_cells_v99r6'])==0 and not GRADE.search(r['v99r6_practical_render_de']) for r in lines))
    cby={key(r):r for r in contexts}; r52=[r for r in residual if r['residual_class']=='OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL']
    ck('52 exact superseded',len(r52)==len({key(r) for r in r52})==52); ck('52 audit parity',len(supers)==52 and {key(r) for r in supers}=={key(r) for r in r52}); ck('context precedence',all(key(r) in cby and r['current_v99_context_de']==cby[key(r)]['v99_context_realization_de'] for r in supers))
    special=[r for r in supers if int(r['current_v99_grade_frame'])]; ck('unique chockhy special',len(special)==1 and special[0]['locus']=='f104v.2' and special[0]['token_ordinal']=='3' and special[0]['surface']=='chockhy',special); ck('51 clean plus special rendered',sum(int(r['current_v99_grade_frame'])==0 for r in supers)==51 and all(int(r['final_v99r6_grade_frame'])==0 for r in supers))
    ck('eight merge specs/audits',len(specs)==len(merges)==8 and len({r['spec_id'] for r in specs})==8 and {r['spec_id'] for r in specs}=={r['spec_id'] for r in merges})
    by={(r['locus'],int(r['token_ordinal'])):r for r in cells}; occupied=set(); card_cache={}
    for s in specs:
        a,b,z=map(int,(s['span_start_ordinal'],s['span_end_ordinal'],s['anchor_ordinal'])); ck('adjacent '+s['spec_id'],b==a+1 and z in (a,b)); pair={(s['locus'],a),(s['locus'],b)}; ck('nonoverlap '+s['spec_id'],not occupied&pair); occupied|=pair
        first,second=by[(s['locus'],a)],by[(s['locus'],b)]; anchor=by[(s['locus'],z)]; companion=second if z==a else first
        ck('merge surfaces '+s['spec_id'],first['surface']+second['surface']==s['merged_surface'] and anchor['surface']==s['anchor_surface'] and companion['surface']==s['companion_surface'])
        path=ROOT/s['source_artifact']; card_cache.setdefault(path,{r['card_id']:r for r in tsv(path)}); card=card_cache[path][s['source_card_id']]; ck('source card '+s['spec_id'],card['reader_merge_surface']==s['merged_surface'] and card['working_render_de']==s['old_anchor_v48_de'])
    ck('16 legacy cells consumed',len(occupied)==16); ck('legacy merge emits once',all(r['span_positions_consumed']=='2' and r['practical_units_emitted']=='1' and r['component_export_credit']=='0' for r in merges))
    upstream_units=tsv(G727/'V99_471_PRACTICAL_RENDERED_UNITS.tsv'); upstream_bound=[r for r in upstream_units if r['source_kind']=='BOUND_SPAN']
    ck('eight inherited bound spans',len(upstream_bound)==len(bound)==8)
    upstream_by_ref={r['source_ref']:r for r in upstream_bound}; bound_cells=set()
    for r in bound:
        ck('bound source '+r['source_ref'],r['source_ref'] in upstream_by_ref and r['rendered_text_de']==upstream_by_ref[r['source_ref']]['rendered_text_de'] and r['integrated_practical_unit_de']==upstream_by_ref[r['source_ref']]['rendered_text_de'] and r['consumed_position_ids']==upstream_by_ref[r['source_ref']]['consumed_position_ids'])
        ids={r['left_cell_id'],r['right_cell_id']}; ck('bound disjoint '+r['source_ref'],len(ids)==2 and not bound_cells&ids); bound_cells|=ids
        ck('bound emits once '+r['source_ref'],r['span_positions_consumed']=='2' and r['practical_units_emitted']=='1' and r['component_export_credit']=='0' and r['debug_text_in_practical_unit']=='0')
    legacy_cell_ids={r['anchor_cell_id'] for r in merges}|{r['companion_cell_id'] for r in merges}
    ck('16 spans consume 32 disjoint positions',len(bound_cells)==len(legacy_cell_ids)==16 and not bound_cells&legacy_cell_ids)
    ck('four punctuation specs/audits',len(punct_specs)==len(punct)==4 and {r['spec_id'] for r in punct_specs}=={r['spec_id'] for r in punct})
    punct_ids={r['cell_id'] for r in punct}; ck('punctuation positions unique and outside spans',len(punct_ids)==4 and not punct_ids&(bound_cells|legacy_cell_ids))
    ck('punctuation attaches without unit',all(r['independent_practical_unit_emitted']=='0' and r['attachment_applied']=='1' and r['cell_value_retained']=='1' and r['component_export_credit']=='0' for r in punct))
    ck('32319 units',sum(int(r['practical_unit_count']) for r in lines)==32319 and sum(int(r['current_v99_bound_span_unit_count']) for r in lines)==8 and sum(int(r['legacy_alias_merge_unit_count']) for r in lines)==8 and sum(int(r['structural_punctuation_attachment_count']) for r in lines)==4)
    ck('7125 grade-affected practical units',sum(int(r['grade_rendered_practical_unit_count']) for r in lines)==7125)
    ck('no debug labels in practical output',all('keine Einzelausgabe' not in r['v99r6_practical_units_de'] and 'Gesamtspan' not in r['v99r6_practical_units_de'] and 'keine Einzelausgabe' not in r['v99r6_practical_render_de'] and 'Gesamtspan' not in r['v99r6_practical_render_de'] for r in lines))
    ck('zero doubled semicolon separators',all(not re.search(r';\s*;',r['v99r6_practical_render_de']) for r in lines))
    qby={r['metric']:r for r in quality}; separator_metric=qby.get('doubled_semicolon_separators_in_practical_output',{})
    ck('separator quality replay',separator_metric.get('v48_or_pre_before')=='48' and separator_metric.get('v99r6_after')=='0' and separator_metric.get('delta_after_minus_before')=='-48')
    by_id={r['cell_id']:r for r in cells}
    ck('bound render-once cell layer',all(by_id[r['left_cell_id']]['practical_unit_id']==by_id[r['right_cell_id']]['practical_unit_id']==r['source_ref'] and by_id[r['left_cell_id']]['practical_unit_role']=='SPAN_START_EMITS_ONCE' and by_id[r['right_cell_id']]['practical_unit_role']=='SPAN_COMPANION_SUPPRESSED' and by_id[r['left_cell_id']]['practical_render_once_de']==by_id[r['right_cell_id']]['practical_render_once_de']==r['rendered_text_de'] for r in bound))
    dby={r['reading_id']:r for r in dictionary}; ck('1586 dictionary identities',len(dictionary)==len(dby)==1586); auth=[r for r in cells if r['authority_reading_id']!='NONE']
    ck('dictionary authority immutable',all(r['authority_reading_id'] in dby and r['authority_score_0_100_not_probability']==dby[r['authority_reading_id']]['working_model_score_0_100_not_probability'] and r['authority_confidence_level']==dby[r['authority_reading_id']]['working_model_level'] and r['authority_semantic_scope']==dby[r['authority_reading_id']]['semantic_scope'] and r['authority_global_export_scope']==dby[r['authority_reading_id']]['global_export_scope'] for r in auth)); ck('zero component credit',all(r['component_relation_credit']=='0' for r in cells))
    paths=[G696/'V69_51_LINE_RELATION_OVERLAY.tsv',G696/'V69_479_TOKEN_RELATION_OVERLAY.tsv',G696/'GDT696_V69_LOCAL_OBJECT_CARRY_READER.md',G727/'V99_324_ACTIVE_LEXICAL_READINGS.tsv',G727/'V99_479_CONTEXT_REALIZATIONS.tsv',G727/'V99_471_PRACTICAL_RENDERED_UNITS.tsv',G727/'V99_51_PRACTICAL_LINE_READER.tsv',G727/'GDT727_V99_51_LINE_WORKING_READER.md',G730/'V99R4_COMPLETE_WORD_CONFIDENCE.tsv',G732/'V99R5_COMPLETE_SPOKEN_RENDERER.tsv',G732/'V99R5_2431_LICENSED_POSITION_OVERLAY.tsv',G732/'V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv']
    pmap={r['source_artifact']:r for r in parity}; ck('12 parity bindings',len(parity)==len(pmap)==len(paths)==12); ck('parity hashes',all(str(p.relative_to(ROOT)) in pmap and pmap[str(p.relative_to(ROOT))]['sha256']==sha(p) and pmap[str(p.relative_to(ROOT))]['gdt733_rewrite_count']=='0' for p in paths))
    contract={'allowed_pages':179,'cached_lines':4128,'cache_cells':32339,'practical_units':32319,'exact_v99_contexts':479,'superseded_exact_v48_grade_cells':52,'current_v99_bound_spans':8,'current_v99_bound_positions_consumed':16,'legacy_alias_merge_spans':8,'legacy_alias_merge_positions_consumed':16,'all_bound_spans':16,'all_bound_span_positions_consumed':32,'structural_punctuation_tokens_attached':4,'grade_cells_spoken':7132,'grade_affected_practical_units':7125,'audible_grade_frame_cells_after':0,'lines_with_audible_grade_frames_after':0,'component_relation_credit':0,'dictionary_changes':0,'score_changes':0,'confidence_changes':0,'evidence_changes':0,'scope_changes':0,'export_changes':0,'new_pages':0}; ck('RESULT contract',all(result.get(k)==v for k,v in contract.items()),contract)
    ck('RESULT status matches separator gate','NO_DOUBLED_SEPARATORS' in result.get('status','') and 'NO_DEBUG_TEXT_IN_PRACTICAL_OUTPUT' in result.get('status','') and '32319_PRACTICAL_UNITS' in result.get('status',''))
    validation={'experiment_id':'GDT733','status':'PASS','check_count':len(checks),'checks':checks,'output_hashes':{p.name:sha(p) for p in sorted(ART.iterdir()) if p.is_file() and p.name!='VALIDATION.json'}}; out=ART/'VALIDATION.json'; text=json.dumps(validation,ensure_ascii=False,indent=2)+'\n'
    if out.exists(): assert out.read_text(encoding='utf-8')==text,'stale VALIDATION.json'
    else: out.write_text(text,encoding='utf-8')
    print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True)); return 0
if __name__=='__main__':raise SystemExit(main())
