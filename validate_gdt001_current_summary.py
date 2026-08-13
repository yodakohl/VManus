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
    ok(summary['status']=='EXPLORATORY_NOT_CONFIRMED_TRANSLATION','status');ok(summary['run_count']==len(ledger),'run_count');ok(summary['converged_run_count']==len(valid),'converged_count');ok(summary['leaderboard']==valid[:50],'leaderboard_exact');ok(summary['decision']=='NO_DECIPHERMENT_CANDIDATE_FREEZE','decision');ok(valid[0]['run_id']=='variablecontext_o2','leader_id');ok(abs(float(valid[0]['bits_per_symbol'])-2.989390710)<1e-12,'leader_score')
    source=json.load(open(ROOT/'gdt001_source_selected_null_results.json'));ok(source['selected_source_null']['null_symbols']=='juz','source_null_identity');source_row=next(r for r in valid if r['run_id']=='sourcenull_juz');ok(abs(source['selected_source_null']['total_bits']-float(source_row['total_bits']))<1e-5,'source_null_total');ok(source['best_language']['total_bits']>source['selected_source_null']['total_bits'],'source_language_loses')
    classes=json.load(open(ROOT/'gdt001_source_class_results.json'));ok(classes['selected_source_classes']['total_bits']>source['selected_source_null']['total_bits'],'class_runner_up');ok(classes['best_language']['total_bits']>classes['selected_source_classes']['total_bits'],'class_language_loses')
    context=json.load(open(ROOT/'gdt001_context_axis_source_results.json'));context_row=next(r for r in valid if r['run_id']=='contextaxis_o2');ok(context['best']['decoder_hash']==context_row['decoder_hash'],'context_decoder');ok(abs(context['best']['total_bits']-float(context_row['total_bits']))<1e-5,'context_total');ok(context['best']['selected_contexts']==40,'context_count');ok(context['best']['axis_counts']=='{"CURRIER":21,"GRAMMAR_SCOPE":5,"HAND":4,"KIND":6,"SECTION":4}','context_axes')
    controls=json.load(open(ROOT/'gdt001_context_axis_control_results.json'));ok(controls['decision']=='STOP_CONTROL_MATCHES_REAL','control_decision');ok(max(x['gain_vs_matched_global_bits'] for x in controls['controls'])>controls['real']['gain_vs_matched_global_bits'],'control_exceeds_real')
    variable=json.load(open(ROOT/'gdt001_variable_context_source_results.json'));ok(abs(variable['best']['total_bits']-float(valid[0]['total_bits']))<1e-5,'variable_total');ok(variable['best']['selected_contexts']==41,'variable_contexts');ok(variable['best']['predictor_counts']=='{"CURRIER":20,"GRAMMAR_SCOPE":5,"HAND":4,"HISTORY3":3,"KIND":5,"SECTION":4}','variable_predictors')
    variable_controls=json.load(open(ROOT/'gdt001_variable_context_control_results.json'));ok(variable_controls['decision']=='STOP_CONTROL_MATCHES_VARIABLE_CONTEXT','variable_control_stop')
    for name in ('gdt001_scaffold_language_results.json','gdt001_group_expansion_results.json'):
        d=json.load(open(ROOT/name));ok(d['decision'].startswith('STOP'),f'stop:{name}')
    partitions=json.load(open(ROOT/'gdt001_partition_stability.json'));ok(partitions['decision']=='STOP_LANGUAGE_PARTITIONS_UNSTABLE_AFTER_TARGET_LABEL_INVARIANCE','partition_instability')
    for name in ('gdt001_group_character_code_results.json','gdt001_prose_language_hybrid_results.json','gdt001_edge_carrier_language_results.json','gdt001_word_exact_audit_results.json','gdt001_differentiable_key_results.json'):
        d=json.load(open(ROOT/name));ok(d['status']=='EXPLORATORY_NOT_CONFIRMED_TRANSLATION',f'exploratory:{name}');ok(d['decision'].startswith('STOP'),f'stop:{name}')
    report=(ROOT/'GDT001_CURRENT_SUMMARY.md').read_text();ok('No translation has been obtained' in report,'report_ceiling');ok('No confirmation branch' in report,'no_confirmation')
    output={'schema':'GDT001_CURRENT_SUMMARY_VALIDATION_V1','status':'PASS_EXPANDED_EXPLORATORY_LEDGER_AND_LEADER','check_count':len(checks),'checks':checks,'run_count':len(ledger),'leader':valid[0]['run_id'],'leader_bits_per_symbol':float(valid[0]['bits_per_symbol']),'claim_ceiling':'Record/score validation only; no language, cipher, plaintext, meaning, or translation.'};(ROOT/'gdt001_current_summary_validation.json').write_text(json.dumps(output,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps({'status':output['status'],'checks':len(checks),'runs':len(ledger)}))


if __name__=='__main__':main()
