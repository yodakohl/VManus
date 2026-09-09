# IDEA000107: type invariance does not distinguish the proposed meanings

2026-09-09. Source/design review only; no new manuscript experiment.

## Decision and bounded scope

Question: does GDT559 supply an observable contrast between a stable argument
meaning and context-conditioned homonymy? Budget: 15 minutes including source
inspection, registry validation and publication; no decoder, new data or rerun.
A concrete independent incompatible requirement would justify specifying a
finite test. Coincident predictions require revising the rival contract; missing
requirements leave the semantic hypothesis untested. Stop after the cited source
and implementation checks. This note records the review, not a preregistered
manuscript test.

## Source evidence

GDT559 REPORT and METHOD report 390 argument positions, six envelopes and the
complete OT+ARG and OL+ARG families (88 and 59 cards). These are inherited
formal observations, not new counts in this review. Its source fixes the German
values in `ARGUMENT_VALUES` (src/run.py:51). Its successor decision compares
`next_inherited == last_argument` (src/run.py:466), using the GDT416/GDT539
context fields (src/run.py:193–206).

The input producers explicitly assign `inherited_argument = active_argument`:
GDT416 src/run.py:218–222 and GDT539 src/run.py:294–301. Thus the reported
157/157 is consistency with a constructed context state, not 157 independently
observed cases of preserved meaning. No raw table was opened or rerun.

GDT593 REPORT provides concrete applications, including E1778 as an inherited
AIN application and E3314 as its reset exception. But its portion/unit types
come from inherited roots and owner defaults. It does not provide an independent
observed participant type for the proposed cross-envelope test.

Primary files:
- experiments/yolo/gdt559_argument_carrier_substitution_grammar/REPORT.md
- experiments/yolo/gdt559_argument_carrier_substitution_grammar/METHOD.md
- experiments/yolo/gdt559_argument_carrier_substitution_grammar/src/run.py
- experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/src/run.py
- experiments/yolo/gdt539_four_page_contextual_statement_edition/src/run.py
- experiments/yolo/gdt593_gdt569_bath_candidate_promotion/REPORT.md

## Logical counterexample to the discriminator

The raw proposal says a context-homonym rival predicts a changed role or an
incompatible downstream requirement. That does not follow from homonymy.
Let one written form denote entity a in OT and entity b in OL, where a and b
are distinct but both participants of the same type T. The invariant-meaning
model denotes a in both envelopes. Both models preserve T and fit the same
formal slot pattern. This is a logical example, not a Voynich reading.
Even an independently measured invariant type would not separate those models.
Conversely, a single meaning can participate in different constructional roles;
role change alone is not a general lexical refutation.

Joint inference remains allowed: no already translated word is required.
What is required for selection is a finite observable relation or requirement
with different predictions under the specific rival models. The source examples
reviewed here do not nominate one. Do not rerun GDT559, add a type classifier,
or relabel its defaults as held semantic targets.

## Outcome

IDEA000107 remains semantically not tested; method review records an invalid
rival discriminator and missing independent binding. Preserve its original
proposal bytes and all existing formal results. No lexeme, page admission,
statistical result or general rejection of homonymy follows. The bounded
parallel producer found no concrete new discriminator and added no proposals;
this is not an exhaustive absence claim.
