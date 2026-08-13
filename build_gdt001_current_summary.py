#!/usr/bin/env python3
"""Rebuild the branch-local follow-up leaderboard from the append-only ledger."""

import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def main():
    with (ROOT/'GDT001_YOLO_LEDGER.tsv').open(newline='',encoding='utf-8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
    valid=[r for r in rows if r['convergence_status']=='CONVERGED' and float(r['total_bits'])<1e100];valid.sort(key=lambda r:(float(r['total_bits']),r['run_id']))
    best_class={}
    for r in valid:best_class.setdefault(r['model_class'],r)
    payload={'schema':'GDT001_CURRENT_SUMMARY_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','run_count':len(rows),'converged_run_count':len(valid),'leaderboard':valid[:50],'best_by_class':best_class,'decision':'NO_DECIPHERMENT_CANDIDATE_FREEZE','claim_ceiling':'Exploratory whole-manuscript tournament only; no confirmed language, cipher, plaintext, meaning, or translation.'}
    (ROOT/'gdt001_current_summary.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    lines=['# GDT001 current exploratory summary','',f"Runs retained: **{len(rows):,}**; converged: **{len(valid):,}**.",'','## Current leaders','','| rank | run | class | system | bits/source symbol | total bits |','|---:|---|---|---|---:|---:|']
    for i,r in enumerate(valid[:20],1):lines.append(f"| {i} | `{r['run_id']}` | {r['model_class']} | {r['language_or_system']} | {float(r['bits_per_symbol']):.6f} | {float(r['total_bits']):,.1f} |")
    lines+=['','## Result','','The current winner is an explicit nonsemantic source model. It treats the seven total occurrences of `j`, `u`, and `z` as a separately coded rare-event/deletion channel and uses the same second-order line-reset source model for the remaining symbols. It scores **3.046666 bits/source symbol**, 1,343 bits better than the original character null. A separately learned contextual-class model independently selected a 20-class alphabet and achieved nearly the same improvement, showing that the gain is rare-sign handling rather than semantic decoding.','', 'Every language/cipher/notation candidate remains worse than an appropriate source-only baseline. Direct character, positional, context-conditioned, Currier-specific, periodic, fixed-block, learned-multigraph, whole-group character, whole-word nomenclator, null-symbol, STA-family/member, morphology, slot, differential-record, carrier/payload, and reading-order systems were tested. A stable 8-word Middle High German mapping was frequency-plausible but lost its exact matched source null; it is not retained as a reading.','', 'No candidate met the freeze requirements. **No translation has been obtained.** No confirmation branch is recommended.','', 'All results are exploratory and branch-local.']
    (ROOT/'GDT001_CURRENT_SUMMARY.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'runs':len(rows),'leader':valid[0]['run_id'],'bits_per_symbol':float(valid[0]['bits_per_symbol']),'decision':payload['decision']}))


if __name__=='__main__':main()
