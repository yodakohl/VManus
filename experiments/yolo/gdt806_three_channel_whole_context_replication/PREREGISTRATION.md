# GDT806 transparent exploratory design record

Date: 2026-09-04. This experiment follows the published GDT805 result. It is
an exploratory rival-discrimination pass, not a blind lexical confirmation.

## Transparency timing

The initial design was registered before the official builder existed, but
independent read-only reconstructions exposed approximate target deltas and
K12 ranks while the base-rate, provenance and robustness rules were still
being corrected. The corrections below are therefore a transparent post-data
adversarial correction, not an outcome-blind preregistration. The preview left
only `okal` above the conditional centered-margin screen and left no target
through the K12-rank plus all-opportunity gates. The rules are frozen here
before the official builder and validator are implemented; GDT806 may report
descriptive diagnostics, not confirmatory p-values or a confirmed role.

## Fixed question

Do equally wide, direction-specific macro-role signatures for six complete
GDT805 wholes choose the same practical rival in a narrow GDT739-derived
context deck and a disjoint broader GDT734 sensitivity deck? Do sparse exact
local cells agree, and how do the seven already enumerated repeated frames look
when the resulting rival order is displayed without decision credit?

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
- `GDT734_GLOBAL652_SENSITIVITY`: a non-independent overlay that retags all 652
  surfaces directly from their GDT734 strings. It recombines coverage, not the
  C1/C2 local tags, and is never called a fourth channel.

For the six duel targets together, the expected raw L/R capacities are C1
1/4, C2 77/84, C3 376/374 and full 454/462; pair-stable capacities are 1/3,
56/57, 263/244 and 320/304. The wider eleven-target atlas totals are 1/5,
91/87, 427/421 and 519/513 raw, and 1/4, 65/60, 300/277 and 366/341 stable.
They are not used as duel denominators. Both levels are asserted separately so
`chal/chedal/qotal` cannot enter the six-target score silently.

The fail-closed global deck begins with GDT734's 1,606 confidence rows/1,602
surfaces. It keeps W2/W3 rows with zero GDT734 composition credit, zero
component export, unconditional global export, no literal
`pulver|samen|saat|wurzel|holz`, and at least one GDT739 axis-regex match.
Identical duplicate surfaces may collapse only when all gate fields and derived
tags agree; any conflict aborts the build rather than dropping a row. All GDT754 surfaces,
all GDT738 manual HOLD surfaces and all eleven GDT805 targets are removed.
Expected row/surface stages are 1,606/1,602→990/989→984/983→777/776→
769/768→726/726→659/659→657/657→652/652.
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
`0.5 × (p_L + p_R)`, and signed uncentered delta is candidate A minus candidate B.
Missing bilateral capacity yields `NA`, never zero.

## Post-data adversarial freeze correction

An adversarial calculation found that equal signature width does not equalize
macro prevalence. QUALITY and CARRIER are much more common than PROCESS, so the
first absolute-delta rule would reproduce deck composition even for an
uninformative target. It is therefore retained only as a necessary
compatibility check, never as sufficient target evidence.

For each target, channel, side and view, the twelve already fixed GDT804
`PRIMARY_K12` complete surfaces form a target-specific baseline. Each control
is mapped and scored separately with identical channel and macro code. The K12
baseline is the median of the twelve individual control deltas, and
`centered_delta = target_uncentered_delta - median(K12_control_deltas)`.
No missing control may be replaced. All twelve must be bilaterally scoreable;
in the stable view at least ten must have at least two mapped contacts on at
least two physical folios on each side.

A direction can be selected only when both the target uncentered delta and the
centered delta point to the same rival in raw and stable views. The centered
margin must also be at least the exact rational `1/20` (0.05). This prevents a target from being called
GENERAL_CARRIER, PROCESS_FIELD, QUALITY_STATE or OPAQUE_RECORD merely because
that duel has the same built-in direction for almost every deck surface.

For twelve sorted exact-rational control deltas, the median is the arithmetic
mean of positions six and seven. Any missing/undefined control makes that view
fail. The twelve controls also supply a specificity rank. Let
`s = sign(centered_target_delta)`, then
`oriented_x = s * uncentered_delta_x` for target and each control, with no
absolute-value transform. Compute
`rank = 1 + count(oriented_control >= oriented_target)` using exact-rational
equality; ties count against the target. C2 and C3 must each place the target at
rank at most 3/13 in raw and stable views. Median separation without this rank
cannot select a preference.

Controls are reconstructed from the safe GDT800/GDT802 artifacts. Their pair
stability is recomputed from the mixed cross-reader TSV only through
`./vmanus-exp query-tsv`, with explicit columns, the inherited allow-list and
f84/f84r rejected before materialization. No full raw row is read directly.

For target `t` and channel `c`, define `F_stable(t,c)` as exactly the union of
physical folios contributing at least one stable mapped L1 or R1 target flank.
For every `f` in that set, remove all events on `f` from the target and every
K12 control synchronously and recompute capacity, stable uncentered delta and
median-centered delta. Both target sides and the required K12 controls must
remain scoreable after removal, and at least ten controls must still meet the
two-contact/two-folio-per-side stable robustness rule. No smaller or silently
filtered control median is allowed. A fold retains direction only when both deltas
have the same strict selected sign; zero, unavailable or reversed folds count
against. The gate is `successes >= ceil(0.8 * len(F_stable(t,c)))`. A separate
leave-one-control-surface-out diagnostic removes exactly one of the twelve
complete control surfaces, leaves the target unchanged and uses sorted
position six as the median of the remaining eleven. No replacement is allowed.
The selected direction is fixed from the full sample and is never reselected
inside a fold. Success tests only whether the recomputed centered delta has
that strict nonzero sign. This is run separately in raw and stable views, and
at least ten of twelve folds must succeed in each. C1 is descriptive regardless
of capacity.

A mandatory selection-conditioning sensitivity repeats every K12-centered
score with the GDT805 denominator: raw denominator is every occurrence of the
subject on that side, including `NONE`/line-boundary as a non-hit; stable
denominator is every occurrence with the corresponding pair-sequence-stable
flag, regardless of whether its neighbour belongs to the channel deck. If only
the mapped-contact denominator passes, the strongest allowed outcome is
`CONDITIONAL_MAPPED_DECK_PREFERENCE`, not a replicated role. A working-role
preference requires a full corresponding gate. A cross-denominator result
requires all-opportunity raw/stable uncentered and centered deltas to share the
mapped selected direction and have absolute magnitude at least 0.05, all twelve
control deltas to have bilateral raw and stable opportunity denominators, with
at least ten controls contributing two stable opportunities on two folios per
side, oriented target ranks at most 3/13 raw and stable, LOCO retention at least
10/12, and no raw/stable uncentered or centered reversal under
`GDT734_GLOBAL652_SENSITIVITY`. Its stable LOFO universe
is exactly the union of physical folios contributing a stable L1 or R1 target
opportunity, whether or not the neighbour is mapped. Each fold removes the
folio synchronously from target and controls, requires both target sides and
all twelve control deltas to remain scoreable with at least ten still meeting
the robust stable-opportunity capacity, and applies the same strict
`ceil(0.8*N)` rule.

Across the six targets, the all-opportunity raw L1/R1 denominators must be
967/967 and the stable L1/R1 denominators 600/594. These totals are assertions,
not mapped-contact capacities.

## Working-rival decision

A practical rival preference requires all of the following in both C2 and C3:

1. at least two stable mapped contacts on at least two physical folios on each
   side, and at least four distinct stable mapped folios in their union;
2. raw and stable uncentered deltas and raw and stable K12-centered deltas have
   the same nonzero direction;
3. `abs(delta)` for all four signed deltas is at least the exact rational
   `1/20` (0.05);
4. the strict stable mapped-contact LOFO gate above passes;
5. at least ten of twelve leave-one-control-surface-out folds retain the
   centered direction;
6. target specificity rank is at most 3/13 in raw and stable views;
7. C2 and C3 prefer the same candidate;
8. `GDT734_GLOBAL652_SENSITIVITY` does not reverse the uncentered or centered direction in
   either view; strict same sign is required, while zero or unavailable fails;
9. the all-opportunity sensitivity passes the corresponding capacity,
   raw/stable uncentered and K12-centered direction and 0.05-margin tests,
   raw/stable K12 ranks, LOCO, strict stable LOFO and global no-reversal gates
   in both C2 and C3.

If conditions 1–8 pass but condition 9 fails, the result is only a
`CONDITIONAL_MAPPED_DECK_PREFERENCE`. If all conditions pass, the result is
`CROSS_DENOMINATOR_DECK_BREADTH_CONCORDANCE`; sparse exact-cell agreement is
reported separately and never upgrades it to independent confirmation. A
narrow/residual disagreement, global-sensitivity reversal or margin/folio
failure remains unresolved. These statuses order concrete working rivals; they
do not select a dictionary word.

## Repeated-frame interpretation

The seven GDT805 real two-sided multi-folio frames are fixed before the new
channel scores. `src/FRAME_RIVAL_SPECS.tsv` records a candidate display and its
strongest rival for each. The frames are drawn from the same 1,086 events, and
their manual wording already reflects the rivals; every row therefore has
`frame_decision_credit=0`, `frame_score_weight=0` and `renderer_license=0`.
They illustrate what the alternatives say but cannot sharpen, corroborate or
install a role. `cheol` and `qokeol` have no repeated real frame.

## Claim boundary

All three axis decks descend from prior German working renderers. C1/C2 share
GDT739 lineage; C2/C3 can occur on the same target events; and both projected
decks ultimately descend from GDT734 German working strings. Their agreement is
only deck-breadth concordance, never independent replication or confirmation.
No EVA substring is interpreted. Even a
concordant `SPECIFIC_MEDIUM_LIKE` result would mean only measured/treated
medium, never automatically oil, water or wine. No new page, image or raw
transcription is opened; f84 and f84r remain forbidden.
