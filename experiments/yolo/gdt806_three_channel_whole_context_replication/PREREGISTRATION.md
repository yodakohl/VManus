# GDT806 transparent exploratory design record

Date: 2026-09-04. This experiment follows the published GDT805 result. It is
an exploratory rival-discrimination pass, not a blind lexical confirmation.

## Fixed question

Do equally wide, direction-specific macro-role signatures for six complete
GDT805 wholes choose the same practical rival in a narrow GDT739-derived
context deck and a disjoint broader GDT734 sensitivity deck? Can the sparse
exact local cells corroborate that choice, and do the seven already enumerated
repeated frames make the winning reading more concrete?

## Fixed targets and rivals

The six targets are exactly `cheol, otal, okal, ol, qokeol, qokol`. Each has
two fixed candidates in `src/RIVAL_SIGNATURE_SPECS.tsv`; every signature has
one L1 and one R1 macro cell:

- `MAT_PREP`: QUALITY on the left, PROCESS on the right;
- `QUALITY_STATE`: CARRIER on the left, SCALAR on the right;
- `OPAQUE_RECORD`: SCALAR on the left, CARRIER on the right;
- `GENERAL_CARRIER`: QUALITY on both sides;
- `SPECIFIC_MEDIUM_LIKE`: PROCESS on the left, SCALAR on the right;
- `PROCESS_FIELD`: CARRIER on the left, QUALITY on the right.

The fixed duels are `MAT_PREP` versus `QUALITY_STATE` for `cheol` and `otal`,
`OPAQUE_RECORD` versus `MAT_PREP` for `okal`, `GENERAL_CARRIER` versus
`SPECIFIC_MEDIUM_LIKE` for `ol`, and `PROCESS_FIELD` versus `MAT_PREP` for
`qokeol` and `qokol`.

## Fixed disjoint channels

- C1 `EXACT_LOCAL`: the six GDT805 flanks whose page, locus, ordinal and
  surface are the identical active GDT739 source cell.
- C2 `GDT739_NARROW_PROJECTED`: non-source occurrences of the 75 GDT805
  projection-eligible surfaces.
- C3 `GDT734_GLOBAL_RESIDUAL`: a fail-closed global deck with the 75 narrow
  surfaces removed.
- `GLOBAL652_FULL`: a sensitivity overlay that recombines C1, C2 and C3; it is
  not an additional independent channel.

For the six duel targets together, the expected raw L/R capacities are C1
1/4, C2 77/84, C3 376/374 and full 454/462; pair-stable capacities are 1/3,
56/57, 263/244 and 320/304. The wider eleven-target atlas totals—1/5, 91/87,
427/421 and 519/513 raw—are not used as duel denominators. Both levels are
asserted separately so `chal/chedal/qotal` cannot enter the six-target score
silently.

The fail-closed global deck begins with GDT734's 1,606 confidence rows/1,602
surfaces. It keeps W2/W3 rows with zero GDT734 composition credit, zero
component export, unconditional global export, no literal
`pulver|samen|saat|wurzel|holz`, and at least one GDT739 axis-regex match.
Surviving duplicate surfaces must agree or be dropped. All GDT754 surfaces,
all GDT738 manual HOLD surfaces and all eleven GDT805 targets are removed.
Expected unique-surface stages are 1,602→989→983→776→768→726→659→657→652.
All 75 narrow surfaces must occur in the 652; C3 therefore has 577 surfaces.

## Macro counting and score

GDT739's fixed `axis_group` map is used unchanged:

- QUALITY = HOT, COLD, DRY, MOIST;
- SCALAR = AMOUNT, VALUE, PASS;
- CARRIER = PART, MATERIAL, PREPARATION;
- PROCESS = PROCESS, CLOSE.

A contact may hit more than one macroclass, but within one contact and
macroclass it counts at most once. For each target, channel, side and view,
`p = macro hits / mapped contacts`. The stable view restricts both numerator
and denominator to GDT805 pair-sequence-stable contacts. A candidate score is
`0.5 × (p_L + p_R)`, and absolute delta is candidate A minus candidate B.
Missing bilateral capacity yields `NA`, never zero.

## Pre-build base-rate and capacity correction

An adversarial calculation found that equal signature width does not equalize
macro prevalence. QUALITY and CARRIER are much more common than PROCESS, so the
first absolute-delta rule would reproduce deck composition even for an
uninformative target. It is therefore retained only as a necessary
compatibility check, never as sufficient target evidence.

For each target, channel, side and view, the twelve already fixed GDT804
`PRIMARY_K12` complete surfaces form a pooled target-specific baseline. They
are mapped with the identical channel and macro code. The same two candidate
scores give a K12 baseline delta, and
`centered_delta = target_absolute_delta - pooled_K12_delta`.

A direction can be selected only when both the target absolute delta and the
centered delta point to the same rival in raw and stable views. The centered
margin must also reach 0.05. This prevents a target from being called
GENERAL_CARRIER, PROCESS_FIELD, QUALITY_STATE or OPAQUE_RECORD merely because
that duel has the same built-in direction for almost every deck surface.

Controls are reconstructed from the safe GDT800/GDT802 artifacts. Their pair
stability is recomputed from the mixed cross-reader TSV only through
`./vmanus-exp query-tsv`, with explicit columns, the inherited allow-list and
f84/f84r rejected before materialization. No full raw row is read directly.

For C2 and C3, remove each mapped target physical folio once from both target
and pooled K12 events and recompute the stable absolute and centered deltas. A
fold retains direction only when both have the same strict selected sign;
zero, unavailable or reversed folds count against. A separate
leave-one-control-surface-out diagnostic recomputes the pooled baseline twelve
times; at least ten folds must retain the centered direction. C1 is descriptive
unless it has at least two stable contacts on each side and four physical
folios.

## Working-rival decision

A practical rival preference requires all of the following in both C2 and C3:

1. at least two stable mapped contacts on each side and four mapped folios;
2. raw and stable absolute deltas and raw and stable K12-centered deltas have
   the same nonzero direction;
3. absolute values of all four deltas are each at least 0.05;
4. at least 80 percent of leave-one-mapped-folio-out folds retain the stable
   direction;
5. at least ten of twelve leave-one-control-surface-out folds retain the
   centered direction;
6. C2 and C3 prefer the same candidate;
7. `GLOBAL652_FULL` does not reverse the absolute or centered direction in
   either view.

If C1 also reaches its capacity and agrees, the status may be
`THREE_CHANNEL_CORROBORATED`; otherwise a replicated preference is explicitly
`EXACT_UNDERPOWERED`. A narrow/residual disagreement, full-overlay reversal or
margin/folio failure remains unresolved. These statuses choose only a concrete
working rival, not a word translation.

## Repeated-frame interpretation

The seven GDT805 real two-sided multi-folio frames are fixed before the new
channel scores. `src/FRAME_RIVAL_SPECS.tsv` records a candidate reading and its
strongest rival for each. A frame may sharpen a replicated role only when its
target's channel decision is compatible. A single frame cannot install a
dictionary value. `cheol` and `qokeol` have no repeated real frame and cannot
gain frame support in this pass.

## Claim boundary

All three axis decks descend from prior German working renderers. Separating
their provenance tests robustness to deck breadth; it does not create
independent historical semantics. No EVA substring is interpreted. Even a
replicated `SPECIFIC_MEDIUM_LIKE` result would mean only measured/treated
medium, never automatically oil, water or wine. No new page, image or raw
transcription is opened; f84 and f84r remain forbidden.
