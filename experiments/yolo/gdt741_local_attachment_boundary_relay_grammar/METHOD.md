# GDT741 method

## Question and scope

Can the thirteen manual GDT740 attachment corrections be reproduced without
looking up their occurrence IDs or loci?

The experiment reuses GDT739's 1,373 cached window rows and 202 dispatches plus
GDT740's 104 typed ring rows, 103 binding contacts, 95 target adjudications, manual
override audit and twenty passages. It opens no page, image or transcription;
`f84` and `f84r` remain forbidden.

## Why the 103-contact table alone is insufficient

The selected-contact table omits two relational facts needed by the proposed
grammar:

- the unselected opposite R1 window at the competing-axis case; and
- the current tags carried by the middle cell of a radius-two frame.

The builder therefore joins only the already published GDT739 window and
dispatch artifacts. IDs and loci remain provenance columns in the output. It
then constructs explicit decision-only records that exclude IDs, loci and all
GDT740 outcome fields before calling the adjudicator.

## Normalized local features

For each contact the builder derives:

- target whole-family, ordered level, favored quality axis, current dimension,
  prior mode and requested broad carrier set;
- host quality, carrier, scalar and boundary sets;
- direct flank and formal direction;
- at radius two, middle known/exact/non-head status, boundary class, quality
  signature and carrier coverage;
- `axis_continuity = EXACT_SINGLE | PARTIAL | CONFLICT | NONE`; and
- `carrier_continuity = FULL_WANTED | PARTIAL | NONE`.

These are relations among current whole-field working tags. They are not EVA
substring meanings or Voynich morphemes.

Middle and opposite fields can participate as relational continuity or vetoes
even when they lacked a positive GDT739 host licence. Their positive-host
eligibility and rejection reason are therefore materialized separately; this
experiment never upgrades them into standalone rendering anchors.

## Ordered dispatcher

The predicates are implemented in `src/run.py`. `src/GRAMMAR_RULES.tsv` is the
human-readable ordered rule registry and confidence ledger, not an interpreted
rule language.

1. A nonbinding conflict cue remains evidence only.
2. A reverse direct CARRIER-only closing field blocks itself and the same-side
   AXIS-only radius-two field behind it.
3. Axis and carrier supplied from opposite direct flanks are not fused.
4. At a state target, an exact opposite direct quality rival reopens the axis.
5. A pure amount field keeps its own value while its broad carrier may bind.
6. A requested composite carrier binds only if one direct host covers it.
7. Radius two is silent by default. Both strict relays require an attested
   reader-exact full frame (count at least one), reader-exact known middle cell, independent middle-cell unit,
   non-head/non-target middle status, one selected role, matching formal
   direction and `middle_barrier=OPEN`. The axis rule additionally requires one
   identical quality signature; the carrier rule requires complete requested-
   carrier coverage in middle and host.
8. An old process-result mode survives only with a retained direct PROCESS
   carrier host.
9. Nothing exports to a component, lexeme, unseen form or plaintext claim.

The direct rules run before result-mode evaluation. This prevents a blocked
host from rescuing an otherwise unsupported result reading.

## Replay versus new candidates

The former manual table is loaded only after all grammar decisions, solely to
measure functional agreement. Exact agreement is therefore a replay result,
not an input to the dispatcher.

A second, non-rendering sensitivity channel relaxes formal direction, the
single-role restriction, exact-single-axis continuity to partial overlap, and
the OPEN barrier to every non-CLOSE class. It retains the exact/known/non-head/
non-target middle-frame gate. One candidate therefore crosses a
`PROCESS_OR_PASS` middle. The channel produces six additional role hypotheses
on five targets. They are written as
`OPEN_COLLISION`; the active patch stays byte-equivalent in meaning to GDT740.

## Relation intake and ceiling

The five unique relaxed geometries are also written in GDT388 packet shape.
The executable intake intentionally rejects the packet: it has no sealed formal
acquisition, capacity set, held-folio allocation or mobile-null evidence.

GDT741 may replace the thirteen manual occurrence lookups with this local
grammar and expose the six collisions. It may not claim transfer to an unseen
page, identify a component or whole as a historical word, or infer plaintext,
language, ingredient, species, unit, disease or cure.
