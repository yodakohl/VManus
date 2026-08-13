#!/usr/bin/env python3
"""Independent compact validation of the expanded GDT001 branch leaderboard."""

import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def main():
    checks=[]
    def ok(x,n):
        if not x:raise AssertionError(n)
        checks.append(n)
    with (ROOT/'GDT001_YOLO_LEDGER.tsv').open(newline='',encoding='utf-8') as h:ledger=list(csv.DictReader(h,delimiter='\t'))
    summary=json.load(open(ROOT/'gdt001_current_summary.json'));valid=[r for r in ledger if r['convergence_status']=='CONVERGED' and float(r['total_bits'])<1e100];valid.sort(key=lambda r:(float(r['total_bits']),r['run_id']))
    ok(len({r['run_id'] for r in ledger})==len(ledger),'unique_run_ids');ok(summary['status']=='EXPLORATORY_NOT_CONFIRMED_TRANSLATION','status');ok(summary['run_count']==len(ledger),'run_count');ok(summary['converged_run_count']==len(valid),'converged_count');ok(summary['leaderboard']==valid[:50],'leaderboard_exact');ok(summary['decision']=='NO_DECIPHERMENT_CANDIDATE_FREEZE','decision');ok(valid[0]['run_id']=='contextmixer_s0_015625','leader_id');ok(abs(float(valid[0]['bits_per_symbol'])-2.960465267)<1e-12,'leader_score')
    source=json.load(open(ROOT/'gdt001_source_selected_null_results.json'));ok(source['selected_source_null']['null_symbols']=='juz','source_null_identity');source_row=next(r for r in valid if r['run_id']=='sourcenull_juz');ok(abs(source['selected_source_null']['total_bits']-float(source_row['total_bits']))<1e-5,'source_null_total');ok(source['best_language']['total_bits']>source['selected_source_null']['total_bits'],'source_language_loses')
    classes=json.load(open(ROOT/'gdt001_source_class_results.json'));ok(classes['selected_source_classes']['total_bits']>source['selected_source_null']['total_bits'],'class_runner_up');ok(classes['best_language']['total_bits']>classes['selected_source_classes']['total_bits'],'class_language_loses')
    context=json.load(open(ROOT/'gdt001_context_axis_source_results.json'));context_row=next(r for r in valid if r['run_id']=='contextaxis_o2');ok(context['best']['decoder_hash']==context_row['decoder_hash'],'context_decoder');ok(abs(context['best']['total_bits']-float(context_row['total_bits']))<1e-5,'context_total');ok(context['best']['selected_contexts']==40,'context_count');ok(context['best']['axis_counts']=='{"CURRIER":21,"GRAMMAR_SCOPE":5,"HAND":4,"KIND":6,"SECTION":4}','context_axes')
    controls=json.load(open(ROOT/'gdt001_context_axis_control_results.json'));ok(controls['decision']=='STOP_CONTROL_MATCHES_REAL','control_decision');ok(max(x['gain_vs_matched_global_bits'] for x in controls['controls'])>controls['real']['gain_vs_matched_global_bits'],'control_exceeds_real')
    variable=json.load(open(ROOT/'gdt001_variable_context_source_results.json'));variable_row=next(r for r in valid if r['run_id']=='variablecontext_o2');ok(abs(variable['best']['total_bits']-float(variable_row['total_bits']))<1e-5,'variable_total');ok(variable['best']['selected_contexts']==41,'variable_contexts');ok(variable['best']['predictor_counts']=='{"CURRIER":20,"GRAMMAR_SCOPE":5,"HAND":4,"HISTORY3":3,"KIND":5,"SECTION":4}','variable_predictors')
    variable_controls=json.load(open(ROOT/'gdt001_variable_context_control_results.json'));ok(variable_controls['decision']=='STOP_CONTROL_MATCHES_VARIABLE_CONTEXT','variable_control_stop')
    mixer=json.load(open(ROOT/'gdt001_online_context_mixer_results.json'));ok(abs(mixer['best']['total_bits']-float(valid[0]['total_bits']))<1e-5,'mixer_total');ok(mixer['best']['share']==1/64,'mixer_share');mv=json.load(open(ROOT/'gdt001_online_context_mixer_validation.json'));ok(mv['status']=='PASS_CPU_EXACT_RECONSTRUCTION_CONTROL_NOT_SPECIFIC','mixer_validation');ok(abs(mv['total_bits']-mixer['best']['total_bits'])<1e-6,'mixer_rebuild');mc=json.load(open(ROOT/'gdt001_online_context_mixer_control_results.json'));ok(mc['decision']=='STOP_CONTROL_MATCHES_CONTEXT_MIXER','mixer_control_stop')
    for name in ('gdt001_scaffold_language_results.json','gdt001_group_expansion_results.json','gdt001_context_tree_source_results.json','gdt001_latin_scholastic_results.json','gdt001_residual_payload_language_results.json','gdt001_rank_nomenclator_results.json'):
        d=json.load(open(ROOT/name));ok(d['decision'].startswith('STOP'),f'stop:{name}')
    high=json.load(open(ROOT/'gdt001_group_code_high_order_results.json'));ok(high['decision']=='STOP_GROUP_CODE_HIGH_ORDER_UNSTABLE','high_order_stop');ok(high['best']['gap_vs_matched_null_bits']>0,'high_order_no_crossover')
    refined=json.load(open(ROOT/'gdt001_group_code_order4_refine_results.json'));ok(refined['decision']=='CONTINUE_ORDER4_REFINED_UNSTABLE','refined_status');ok(refined['best']['gap_vs_matched_null_bits']<0,'refined_crossover');ok(refined['best']['gap_vs_variable_context_bits']>0,'refined_loses_global');ok(len({r['decoder_hash'] for r in refined['rows']})==3,'refined_unstable')
    for r in refined['rows']:ok(abs(r['total_bits']-(r['key_bits']+r['payload_bits']+r['fixed_bits']))<1e-6,f"refined_sum:{r['seed']}");ok(r['cpu_exact'] is True,f"refined_cpu:{r['seed']}")
    gc=json.load(open(ROOT/'gdt001_group_code_order4_control_results.json'));ok(gc['decision']=='STOP_CONTROLS_MATCH_GROUP_LANGUAGE','group_control_stop');ok(abs(gc['real']['gain_vs_matched_null_bits']-next(r['gain_vs_matched_null_bits'] for r in gc['controls'] if r['manuscript']=='BOUNDARY_PRESERVING_IDENTITY_PERMUTATION'))<1e-6,'group_identity_invariant');ok(all(r['gain_vs_matched_null_bits']<0 for r in gc['controls'] if r['manuscript']!='BOUNDARY_PRESERVING_IDENTITY_PERMUTATION'),'group_destructive_controls_lose')
    scale=json.load(open(ROOT/'gdt001_group_code_scale_results.json'));ok([r['k'] for r in scale['rows']]==[256,512,1024],'scale_sizes');ok(all(r['gain_vs_matched_null_bits']>0 for r in scale['rows']),'scale_conditional_gains')
    sv=json.load(open(ROOT/'gdt001_group_code_scale_validation.json'));ok(sv['status']=='PASS_EXPLORATORY_SCALE_ARITHMETIC_AND_STABILITY_STOP','scale_validation');ok(abs(sv['selection_correct_family_gain_bits']-5880.960600502905)<1e-6,'scale_selection_gain');ok(max(sv['restart_pair_ari'])<.2,'scale_partition_unstable')
    anon=json.load(open(ROOT/'gdt001_group_code_anonymous_null_results.json'));ok(anon['decision']=='CONTINUE_CZECH_BEATS_ANONYMOUS_NULL','czech_small_margin');ok(anon['best']['gap_vs_best_czech_bits']<1000,'czech_margin_under_1k')
    ssv=json.load(open(ROOT/'gdt001_symbol_state_markov_validation.json'));ok(ssv['status']=='PASS_EXACT_ARTIFACT_ARITHMETIC_STOP','symbol_state_stop');ok(ssv['best_total_bits']>float(valid[0]['total_bits']),'symbol_state_loses')
    lsv=json.load(open(ROOT/'gdt001_latent_space_homophonic_validation.json'));ok(lsv['status']=='PASS_EXACT_ARTIFACT_ARITHMETIC_DECISIVE_SCREEN_STOP','latent_space_stop');ok(lsv['best_total_bits']>900000,'latent_space_loses')
    sk=json.load(open(ROOT/'gdt001_consonantal_skeleton_validation.json'));ok(sk['status']=='PASS_INDEPENDENT_PYTHON_PROJECTED_KEY_DIAGNOSTIC','skeleton_projected_key');ok(sk['best_total_bits']>1200000,'skeleton_projected_key_loses')
    li=json.load(open(ROOT/'gdt001_line_initial_channel_validation.json'));ok(li['status']=='PASS_INDEPENDENT_CPU_EXACT_STOP','line_initial_stop');ok(li['best_total_bits']>580000,'line_initial_loses')
    partitions=json.load(open(ROOT/'gdt001_partition_stability.json'));ok(partitions['decision']=='STOP_LANGUAGE_PARTITIONS_UNSTABLE_AFTER_TARGET_LABEL_INVARIANCE','partition_instability')
    for name in ('gdt001_group_character_code_results.json','gdt001_prose_language_hybrid_results.json','gdt001_edge_carrier_language_results.json','gdt001_word_exact_audit_results.json','gdt001_differentiable_key_results.json'):
        d=json.load(open(ROOT/name));ok(d['status']=='EXPLORATORY_NOT_CONFIRMED_TRANSLATION',f'exploratory:{name}');ok(d['decision'].startswith('STOP'),f'stop:{name}')
    report=(ROOT/'GDT001_CURRENT_SUMMARY.md').read_text();ok('No translation has been obtained' in report,'report_ceiling');ok('No confirmation branch' in report,'no_confirmation')
    output={'schema':'GDT001_CURRENT_SUMMARY_VALIDATION_V1','status':'PASS_EXPANDED_EXPLORATORY_LEDGER_AND_LEADER','check_count':len(checks),'checks':checks,'run_count':len(ledger),'leader':valid[0]['run_id'],'leader_bits_per_symbol':float(valid[0]['bits_per_symbol']),'claim_ceiling':'Record/score validation only; no language, cipher, plaintext, meaning, or translation.'};(ROOT/'gdt001_current_summary_validation.json').write_text(json.dumps(output,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps({'status':output['status'],'checks':len(checks),'runs':len(ledger)}))


if __name__=='__main__':main()
