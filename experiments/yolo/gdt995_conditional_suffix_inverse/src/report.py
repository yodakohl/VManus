#!/usr/bin/env python3
"""Post-result reporting only; no candidate, score or selection changes."""
import csv,hashlib,importlib.util,json
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];O=E.parent/'gdt837_scg_integrated_wholeword_control'
def read(p):return json.loads(p.read_text())
d=read(E/'artifacts/DISCOVERY.json');r=read(E/'artifacts/RESULT.json');v=read(E/'artifacts/VALIDATION.json');assert v['status']=='PASS'
s=importlib.util.spec_from_file_location('bound_direct_forward',E/'src/validate.py');oracle=importlib.util.module_from_spec(s);s.loader.exec_module(oracle)
checks=[]
for a,b in zip(d['rows'],r['rows']):
 key=read(O/a['fit'])['key'];cipher=oracle.read(O/f'prepared/world_{a["world_id"]}_discovery.json.gz')
 words=Counter(tuple(w) for p in cipher['paragraphs'] for w in p['words'])
 errors=[]
 for group in oracle.orders_by_behavior(key):
  errors.append(sum(n for w,n in words.items() if oracle.forward(''.join(key[c]['output'] for c in w),key,group[0])!=w))
 assert len(set(errors))==1 and errors[0]==sum(a['original_gate']['violations'].values())
 checks.append(dict(fit=a['fit'],direct_forward_wrong_words=errors[0]))
(E/'artifacts/COUNTS_VALIDATION.json').write_text(json.dumps(dict(status='PASS',post_result_reporting_check=True,checks=checks),indent=2)+'\n')
header=['world','arm','start','original_selected','original_inverse_violations','compatible_suffix_maps','selected_suffix_values','active_correct','held_correct','held_total','score_gap_to_second','remaining_global_orders']
rows=[];comp=[];table=[]
for a,b in zip(d['rows'],r['rows']):
 selected=b['selection'];scores=sorted((x['discovery_score'] for x in a['completions']),reverse=True)
 gap=scores[0]-scores[1] if len(scores)>1 else None
 z=[a['world_id'],a['arm'],a['start'],b['was_original_selected'],sum(a['original_gate']['violations'].values()),a['compatible_assignments'],
    '/'.join(selected['suffix_values']) if selected else '-',selected['active_packages']-len(selected['active_mismatch_ids']) if selected else '-',
    selected['held_exact_words'] if selected else '-',selected['held_words'] if selected else '-',f'{gap:.6f}' if gap is not None else '-',len(selected['joint_suffix_orders']) if selected else 0]
 rows.append(z)
 table.append(f"| {z[0]} | {z[1]} | {z[2]}{'*' if z[3] else ''} | {z[4]} | {z[5]} | {z[6]} | {z[7]} | {z[8]} |")
 for c,t in zip(a['completions'],b['completion_truth']):
  assert c['suffix_values']==t['suffix_values']
  comp.append([a['world_id'],a['arm'],a['start'],'/'.join(a['suffix_carriers']),'/'.join(c['suffix_values']),f'{c["discovery_score"]:.9f}',len(c['suffix_orders']),','.join(t['active_mismatch_ids']),c==a['selected']])
for name,head,body in [('CANDIDATES.tsv',header,rows),('COMPLETIONS.tsv',['world','arm','start','suffix_carriers','suffix_values','discovery_score','global_orders','active_mismatch_ids','selected'],comp)]:
 with (E/'artifacts'/name).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(head);w.writerows(body)
report='''# GDT995 — exact conditional recovery after enforcing the full writing rule

**RETROSPECTIVE_CONDITIONAL_RECOVERY_45_OF_48.** All six originally selected
GDT837 keys, and 39 other saved keys, yield a correct active key under the new
finite conditional audit. Each reads all **192,991 held words and 13,828 held
source sentences exactly**. The three remaining keys have no suffix-only
completion. GDT837 itself remains **STRICT_RECOVERY_FAIL**: this is a separately
registered retrospective result, not a replacement of its selections or outcome.

The positive is precise: with each old role, literal and wholeword map held
fixed, enforcing its declared deterministic encoder removes the known wrong
suffix deck. The unchanged reference objective then selects the correct
assignment among all compatible alternatives. No new restart, letter map,
wholeword value, corpus, normalization or language score was fitted.

## What the writing rule actually determines

The original 45 near-correct maps read an S carrier as `a`, but simultaneously
spell 8,978 discovery words ending in `a` with literal carriers. Under their own
mandatory suffix rule those words require that S carrier. For example, the
first lexicographic witness in world83701 is `turba` written entirely literally.
The gate used all word types and occurrences, not that example. The other three
old maps have 16,144, 14,923 and 16,144 incompatible discovery word occurrences.
The independent direct-forward report check reproduces all48 violation totals.

All48 old maps therefore fail full forward compatibility. Exhausting each
12P4=11,880 suffix assignment accounts for570,240 nominal cases. For the45
completable maps the only possible suffix **set** is `{ae,is,um,us}`: all24
permutations pass the writing rule. Each has24 indistinguishable priority orders
because none of these suffixes overlaps another. The inverse alone therefore
identifies the deck, not the carrier-to-suffix assignment.

The unchanged discovery language score uniquely selects the correct assignment
in all45 cases, with a45,778.825417-nat gap to the next compatible assignment.
Exactly one of each24-map class has every active value correct. Across the whole
panel1,080 compatible completions and all their truth differences are retained.
The selected score is−1,432,617.648124, lower than the old illegal winner by
31,589.171877nats. More search over the old larger space would still prefer the
illegal key. This refines the diagnosis of that comparison; it does not alter
its numerical result or prove every inverse-compatible language optimum correct.

Three fixed non-suffix maps leave only three allowable suffix values for four
injective S slots:83701 STRICT5 has `{ae,em,is}`,83701 STRICT7 has `{am,as,is}`,
and83702 STRICT4 has `{ae,em,is}`. They stop before any conditional selection.
No role/letter/wholeword repair is attempted.

## Complete candidate table

`*` marks the six identities selected in the ORIGINAL GDT837 experiment.
Suffix outputs follow sorted carrier IDs, recorded in COMPLETIONS.tsv.
Active correct is out of34; held correct is out of192,991. A dash means no
conditional completion, not zero successfully translated words in a target.

| World | Arm | Start | Old inverse violations | Compatible maps | Selected S outputs | Active correct | Held correct |
|---|---|---:|---:|---:|---|---:|---:|
'''+ '\n'.join(table)+'''

The machine-readable CANDIDATES.tsv contains all48 rows and score gaps;
COMPLETIONS.tsv contains all1,080 feasible maps, scores, remaining priority
orders and active mismatch identities. DISCOVERY.json preserves excluded
suffix-value witnesses and the accounting of every nominal assignment.
No favorable restart is discarded or substituted into GDT837.

## Scope, validation and decision

Registration `19648e498` was pushed before the audit. Discovery enumeration ran
2026-09-20 13:28:56–13:29:07UTC, then its outputs and selections were hash-locked
before the truth/held evaluator ran. The analyst already knew the old ae-to-a
error and public truth: procedural separation is not fresh blindness.45maps and
three encryption worlds share one source split, not45independent replications.
The fixed old literal/wholeword maps are a major supplied condition; this is not
full-key recovery from arbitrary initialization. Boundaries, role counts and
mandatory abbreviation are properties of this synthetic control, not Voynich.

The separately written direct forward encoder validates all48 inventories,
finite completions, allowed global orders, old sentence scores, selections,
active-map joins and held consequences.11invented fixtures pass. The first
validation invocation occurred before RESULT.json existed and stopped with
FileNotFoundError; the unchanged validator was run after evaluation completed.
A prepublication manifest-only correction removed an unsupported command field;
it is disclosed in PREREG_LOCK.json. No scientific code changed after registration.
The additional post-result report check independently recomputes all old
violation counts using the already bound direct encoder.

Decision: the full writing inverse resolves this particular conditional control
error, whereas W priority alone did not. A fresh blind recovery experiment,
with this constraint active during inference, would still be required to claim
an improved general recovery method. No such experiment is automatically started.
No Voynich target fit, Latin identification, word meaning or significance follows.
GDT616/CDA001, GDT836's source stop, GDT832 and GDT837's original failures remain.
Known non-target debt is retained; the next research choice must be made separately.
'''
(E/'REPORT.md').write_text(report)
print(json.dumps(dict(candidate_rows=len(rows),completion_rows=len(comp),extra_forward_count_checks=len(checks))))
