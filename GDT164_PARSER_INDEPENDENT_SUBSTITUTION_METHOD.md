# GDT164 — parser-independent substitution context transfer

Status: `METHOD_AND_ANALYSIS_FAMILY_FROZEN_BEFORE_SCORING`

## Question

GDT163 found that directed one-character changes between short HPR2
`PAGE_HOST` identities predicted held outer HPR2 deltas, but its strongest
effects involved DY and B3 fields parsed from the same source group.  GDT164
asks whether the same held-base relation survives when the target contains
only *external* context.

This is an exploratory surface test.  A directed substitution is not assumed
to be a glyph operation, sound change, morpheme, grammatical category, or
semantic operation.

## Sources and f84 guard

Voynich input is the frozen `gdt062_right_family_inventory.tsv`.  `PAGE_HOST`
is used only to identify the focal short form and define its Hamming-one
substitution.  Every row whose page or locus begins `f84` is rejected before
retention.  No f84r row, image, transcription, or formal payload may be
opened, queried, retained, joined, or scored.

Historical controls are the five frozen surface-only GDT159 corpora.  Their
visible diplomatic `form` occupies the same identity slot as Voynich
`PAGE_HOST`; expansion, lemma, meaning, phonology, and translation remain
hidden.

## Explicit parser firewall

The target representation may not read the focal row's:

- raw token;
- wrapper;
- inner-D;
- local O/OT frame;
- right family;
- DY closure;
- B3 closure;
- or any other value parsed from the same source group.

Only other source groups and mechanical unit coordinates are admissible.
The scorer constructs a new minimal occurrence record containing identity,
unit, integer position, section, hand, and historical fold only; it then
deletes the source row before constructing target features.

## Frozen external-context target

For each focal occurrence, the categorical target blocks are:

1. SHA256 bucket 0--31 of the immediately preceding contiguous identity, or
   `MISSING`;
2. the same for the immediately following identity;
3. preceding and following identity length classes `1`, `2`, `3`, `4+`, or
   `MISSING`;
4. preceding and following corpus-frequency classes `1`, `2--4`, `5--15`,
   `16+`, or `MISSING`;
5. distance from unit start: `0`, `1`, `2`, or `3+`;
6. distance to unit end under the same bins;
7. unit-position quartile;
8. observed unit index-span class `1`, `2`, `3`, `4`, `5--7`, or `8+`.

A neighbor is contiguous only when its integer occurrence index differs by
exactly one.  Gaps in sampled historical material remain `MISSING` and are not
invented record boundaries.  The hash is a fixed compression of external
identity, not a learned semantic class.  All blocks use Jeffreys-smoothed
categorical distributions and are applied identically to Voynich and every
historical corpus.

Voynich cells are `(identity, section, hand)`.  Historical cells are
`(identity, fold_id, ALL)`.  This allows the exact-pair baseline to use other
strata rather than collapsing all occurrences into one corpus-wide cell.

## Directed substitutions and transfer

Use PAGE_HOST/form lengths two and three.  Equal-length identities differing
at exactly one position define an edge.  Direction is Unicode ascending at the
changed position.  The operation key is `(length, position, source, target)`;
the base family masks the changed position with `*`.

Both endpoints must occur at least twice in the exact cell.  Operations need
at least four eligible cells.  Test-cell weight is
`min(20, min(source_count, target_count))`.  A prediction needs at least three
training cells and two training base families.

Primary prediction learns the weighted delta for the same operation while
excluding the complete base family.  Voynich additionally reports:

- `HELD_BASE_AND_SECTION`;
- `HELD_BASE_AND_HAND`.

Historical controls report `HELD_BASE_AND_FOLD`.  Two baselines remain
separate:

- `POSITION_ONLY`: same length/position, different glyph pair, held base;
- `EXACT_PAIR_OTHER_STRATA`: same exact source/target identities in another
  section/hand or historical fold.

Report fractional MSE gain over zero delta, cosine, positive-dot rate,
coverage, per-operation scores, and register-exclusion sensitivity.  Exact
identity never enters the substitution learner.

## Null and cross-corpus comparison

Run 1,024 deterministic position-preserving identity-label worlds per corpus.
Each identity, occurrence, external-context vector, length, and positional
character multiset stays fixed.  Shuffling the characters across identities
destroys which identities are Hamming neighbors and which edges share an
operation.  In every world rerun eligibility, prediction, and the
best-operation search.  Report inclusive aggregate and maxT p-values.

The same external target, minimum counts, prediction rule, position baseline,
exact-pair baseline, and null apply to Voynich and GDT159.  ZL3b/IT2a/RF1b are
not replications; GDT164 uses the already frozen PAGE_HOST display view only.

## Decisions

- `PARSER_INDEPENDENT_SUBSTITUTION_TRANSFER_SUPPORTED` requires positive
  Voynich held-base, held-section, and held-hand gains, aggregate p<=.05, at
  least one operation with maxT p<=.05, and held-base gain above every powered
  historical control.
- `PARSER_INDEPENDENT_TRANSFER_PROVISIONAL` requires all three Voynich gains
  positive but misses a null or historical-comparison gate.
- `PARSER_INDEPENDENT_TRANSFER_LOCAL_ONLY` applies when held-base is positive
  but held-section or held-hand is not.
- `PARSER_INDEPENDENT_SUBSTITUTION_NOT_SUPPORTED` applies when primary
  held-base gain is nonpositive.

These are formal predictive labels, not linguistic morphology claims.

## Claim ceiling

At most GDT164 can show that a repeated one-character relation predicts
external neighboring-form and physical-unit context on unrelated short-form
bases.  It cannot establish a grapheme, phoneme, morpheme, word, POS,
language, semantic role, meaning, plaintext, or translation.
