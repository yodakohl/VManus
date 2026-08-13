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
    lines+=['','## Result','','The current winner is an explicit nonsemantic source model. It uses a separately coded rare-event channel for the seven total occurrences of `j`, `u`, and `z`, a shared second-order line-reset character process, and 41 explicitly paid exceptional contexts. Each exception chooses either a third history symbol or one known metadata axis. The selected predictors are 20 Currier, 5 layout-kind, 5 grammar-scope, 4 hand, 4 section, and 3 longer-history contexts. It scores **2.989391 bits/source symbol**, about 11,130 bits better than the previous rare-sign null.','', 'This is a stronger null, not a decipherment. A frozen counterfactual refit found the gain unchanged under a global identity permutation and substantially larger in the Timm copy/modify synthetic manuscript. The mechanism therefore describes formal source heterogeneity and local construction history; it is not specific evidence for language, cipher, or meaning.','', 'The strongest language-side effect maps the 512 most frequent complete groups to 27 latent characters under a fourth-order medieval-Czech corpus model. After allowing both language and null families to select their paid scale, it gains **5,881.0 bits** over the best group-code null and only **576.1 bits** over an optimized anonymous 27-state bottleneck. All destructive controls lose while a global symbol renaming is invariant. But the three K=512 restart partitions disagree severely (pairwise adjusted Rand 0.136–0.182), and the best total remains 61,749 bits above the global source winner. This is a real-specific group-compression effect, not a stable Czech decoder.','', 'Direct character, positional, context-conditioned, Currier-specific, boundary-rule, periodic, fixed-block, learned-multigraph, whole-group character/expansion, whole-word nomenclator, null-symbol, STA-family/member, morphology, slot, differential-record, carrier/payload, scaffold-core language, and reading-order systems were tested. A new construction-root character model also crossed its own weak matched null but lost badly to the whole-group code and global source baseline. No mapping is retained as a reading.','', 'No candidate met the freeze requirements. **No translation has been obtained.** No confirmation branch is recommended.','', 'All results are exploratory and branch-local.']
    (ROOT/'GDT001_CURRENT_SUMMARY.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'runs':len(rows),'leader':valid[0]['run_id'],'bits_per_symbol':float(valid[0]['bits_per_symbol']),'decision':payload['decision']}))


if __name__=='__main__':main()
