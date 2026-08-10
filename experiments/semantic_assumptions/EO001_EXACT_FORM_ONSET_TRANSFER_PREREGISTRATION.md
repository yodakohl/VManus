# EO001 exact-form continuation-transfer preregistration

## Fixed hypothesis

The nine exact STA-family forms selected independently as
`FIRST_ASSOCIATED` may carry form-specific continuation construction
signatures when they occur both at factual line openings and inside a line.
EO001 tests whether the immediate successor of the **same complete trigger
form** is more structurally concordant across those two positions than the
successors of different selected forms within the same physical folio.

This is different from the closed `NONE` versus `DA` operation experiment:
EO001 does not vary or strip a prefix-like operation.  It conditions on the
complete trigger form and uses a new exact-form position atlas.

## Frozen panel and target join

The score-blind capacity artifacts define 1,295 events, nine forms, and 92
physical folios.  An event is strict confirmed prose, its trigger is factual
`FIRST` or `CORE`, and at least two groups remain after the trigger.  Thus the
immediate successor is factual `CORE` in both states.

The eventual one-time target runner may join an anonymous event by recomputing
`EO001-` plus the first 20 hexadecimal characters of
`SHA256("EO001|" + consensus_group_id)`.  It then selects only the same-locus
row at `group_index + 1`.  It must assert exact panel cardinality and metadata
before reading that successor's `family_surface`.  Member codes, basic EVA,
images, OCR, parser roots/roles, and semantic fields are forbidden.

## Frozen continuation fingerprints

Use the fixed 24-family alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ`.  For successor
sequence `w` construct three blocks:

1. `EDGE_48`: one-hot first family followed by one-hot last family;
2. `BAG_24`: family counts divided by `len(w)`;
3. `BIGRAM_576`: adjacent family-pair counts divided by `max(1,len(w)-1)`.

These blocks overlap deliberately but expose different construction
resolutions.  No complete successor identity is a feature.

## Frozen nuisance transform

For each trigger state and held physical folio separately, fit ridge regression
on all other panel folios and predict the held rows.  Response columns are one
fingerprint block.  The label-blind basis is:

- intercept;
- centered/scaled one-hot columns for Currier, section, hand, and source code;
- centered/scaled `log1p(locus_group_count)`, its square and cube;
- centered/scaled successor relative position
  `trigger_group_index / (locus_group_count - 1)`, its square and cube;
- centered/scaled `log1p(remaining_groups_after_trigger)`, its square and cube.

Zero-variance columns are rejected.  Fit the two states independently, using
`(Z'Z + 1e-3 I)^{-1}Z'Y` with the intercept unpenalized.  Every held residual
must be finite.  Full-panel metadata means/scales are allowed because they are
outcome-blind; no held successor value enters a fitted coefficient.

## Same-folio concordance statistic

An informative folio has at least two selected forms represented in both
states.  For each such form/state/folio, average held residual fingerprints
over events.  Within each folio and state, subtract the equal-form mean and
unit-normalize each resulting form vector.  The state-to-state cosine matrix
then compares every FIRST form to every CORE form in that folio.

The observed folio score is the mean diagonal cosine.  A deterministic null
permutes the CORE form identities independently within every folio. Assignment
zero is identity.  For assignments 1 through 32,767, order each folio's form
indices by SHA-256 of
`EO001-PERM|assignment|physical_folio|form`; this supplies 32,767 synchronized
Monte Carlo null assignments.  Average folios equally.  Ties use tolerance
`1e-12`, and `p=(1 + number(null >= observed-1e-12))/32768`.

For each block, subtract the null mean and divide by the population null SD.
The primary combined orbit is the equal mean of the three standardized block
orbits.  Folio and form diagnostics use the correct diagonal minus the mean
wrong pairing, divided by the block null SD and averaged across blocks.

## Frozen target gates

EO001 confirms this narrow continuation-transfer relation only if all hold:

1. exact 1,295-event / 92-folio / nine-form join and exact 38 informative
   folios;
2. combined standardized observed statistic at least 1.5 and permutation
   `p <= .01`;
3. every block has positive raw effect and at least two blocks have
   blockwise `p <= .05`;
4. at least 24/38 informative folios and at least 7/9 forms have positive
   diagnostic contributions;
5. Currier-A and Currier-B informative-folio means are both positive;
6. every delete-one-informative-folio combined mean remains positive;
7. the largest absolute folio contribution is at most 20% of the total
   absolute contribution;
8. all registered target-free controls and independent reconstruction pass.

No threshold, feature block, form, folio, nuisance term, or interpretation may
be changed after target access.

## Required target-free calibration

Before target access, run at least 64 null worlds and eight worlds per positive
or adversarial family.  A valid freeze requires:

- zero of 64 Gaussian and zero of 64 realistic whole-row null worlds pass;
- at least 7/8 distributed portable-form signals pass at a frozen amplitude
  selected from a predeclared grid `.25,.50,.75,1.00,1.50,2.00`;
- at least 7/8 feasible whole-row portable-form signals pass when 60% of rows
  receive a form-specific prototype drawn from the non-target donor pool;
- zero passes for generic, position-only, nuisance-only, one-form, one-folio,
  one-state, one-block, reversed-state, state-remapped, and folio-random form
  signals;
- deterministic assignment, row-order, duplicate/missing ID, state, position,
  nonfinite, feature-dimension, and source-exclusion mutations all reject;
- a nonimporting validator independently reconstructs every world, gate,
  artifact, and hash before a target freeze exists.

The positive amplitude is a synthetic signal-to-noise setting, not a manuscript
effect threshold.  Calibration may fail and stop the route; it may not be
weakened after opening a successor.

All synthetic worlds use NumPy `PCG64` seeded by the little-endian first eight
bytes of SHA-256 over `EO001|family|world|amplitude`. Gaussian blocks draw
independent unit-normal noise and independent unit-normal form signatures in
the fixed block order. `REALISTIC_NULL` samples without replacement from
strict confirmed-prose source groups that are not an EO001 target successor.
`WHOLE_ROW_PORTABLE` first makes that same null assignment, draws one donor
prototype per form, and replaces a PCG64-selected 60% of event rows by their
form's prototype in all three blocks.  All whole-row operations keep the three
blocks coupled.  The generic plant adds one shared signature; position-only
uses successor relative-position cubic terms; nuisance-only uses the frozen
design matrix; one-form, one-folio, one-state, and one-block restrict the
portable plant as named; reversed-state negates CORE; state-remapped cyclically
maps CORE form `i` to `i+1`; folio-random maps CORE through a nonzero cyclic
shift derived separately for each folio.  Each adversarial family has eight
worlds at the selected portable amplitude and must yield zero complete passes.

## Claim ceiling

A pass would establish that selected exact source-native group forms have a
portable same-folio continuation-construction fingerprint from factual line
openings to internal core positions.  It would make embedded-onset or subrecord
behavior a testable structural candidate.  It would not prove an embedded
clause, sentence, word, part of speech, copying mechanism, sound, meaning,
plaintext, language, cipher, or translation.  A failure would reject only this
three-block exact-form transfer mechanism at the frozen resolution.
