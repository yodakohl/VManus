# GDT338 method — renderer-invariant formal equivalence

Date: 2026-08-18

Status: `FROZEN_BEFORE_HELD_SCORE`

## Question

After applying only the experimentally supported GDT321–336 renderer and
placement model, do distinct rendered field surfaces on unseen physical folios
behave as observations of the same opaque normalized formal object?

This is not a search for a new parser, grammar feature, PAGE_HOST relation,
substring, phase, semantic role, or external referent. It tests the smallest
equivalence already licensed by the executable grammar.

## Frozen admissible normalization

The source is the f84-free GDT327 joint-tuple interlinear. For a complete field,
ordered by physical source-group order, define:

```text
RENDERED_SURFACE = ((observed_wrapper, exact_joint_tuple_id), ...)
NORMALIZED_OBJECT = (exact_joint_tuple_id, ...)
```

The normalized object removes only:

- the observed wrapper realization;
- physical line entry;
- preceding-DY state;
- within-field position and physical-line quartile;
- page, folio, locus, register, hand, Currier, and record coordinates.

It preserves the exact opaque joint tuple, including PAGE_HOST and all five
compiler coordinates `(frame, inner-D, right-family, DY, B3)`, as well as the
ordered field boundary. This is essential: GDT325 rejected coordinate backoff
and GDT326 rejected independent PAGE_HOST×coordinate recombination. No two
different exact joint-tuple sequences are declared equivalent in advance.

The only renderer coefficients are the exact frozen GDT322 values:

```text
beta_s_line_first = 1.0021314958853849
beta_q_prev_dy    = 0.8920380870887143
```

The only placement coordinates are those supported by GDT335 and used by
GDT336: physical line entry, within-field position, and physical line
quartile. Field ordinal is excluded because its held contribution was negative
in every register.

## Prospective outer panel

Every physical folio is held out inside its fixed register. A held field enters
the primary panel only when all of the following are true using the remaining
folios:

1. every group belongs to the pre-existing GDT322
   `EXECUTABLE_POWERED_CELL` layer;
2. the exact normalized object occurs on at least two training folios;
3. those training occurrences exhibit at least two distinct rendered surfaces;
4. the held rendered surface is absent from training.

This yields a mechanically frozen capacity panel of 25 held fields, 32 group
events, 17 held folios, nine normalized objects, ten register-conditioned
object cells and three registers. One object occurs in two registers; it is one
formal object and two evaluation strata, not two objects. Eighteen fields have
one group and seven have two groups. One-group and multi-group results must be
reported separately. The selection rule is deliberately hard: for one-group
fields the held wrapper realization was not previously observed with that
exact tuple in training.

## Test 1 — unseen-surface renderer transfer

Train wrapper counts only on non-held folios, using symmetric Dirichlet-1/2
smoothing over the fixed classes
`NONE,ch,che,d,q,s,sh,t`. Compare six fixed models:

1. `REGISTER_TWO_RULE`: register-level counts plus the two frozen offsets;
2. `COORDINATE_TWO_RULE`: exact coordinate counts within register plus offsets;
3. `COORDINATE_CONTEXT_TABLE`: exact
   coordinate×line-entry×previous-DY counts, backing off to coordinate;
4. `REGISTER_MARKOV_TWO_RULE`: register×previous-wrapper counts plus offsets,
   backing off to register at field entry;
5. `JOINT_NO_RULE`: exact joint-tuple counts without offsets;
6. `JOINT_TWO_RULE`: exact joint-tuple counts plus the frozen offsets.

`JOINT_TWO_RULE` is the candidate. Score held wrapper log loss, group top-1,
and exact whole-field wrapper-sequence top-1. The exact rendered-surface lookup
coverage is zero by panel definition and is reported rather than given a
fallback. Charge the candidate by `log2(6)` bits against the shortest of the
other five models.

## Test 2 — normalized-object recovery from placement

Hide exact joint-tuple identity from the predictor while retaining its exact
compiler coordinate. Recompute the unchanged GDT336 coordinate and
placement-shrunk probabilities from non-held folios. Use the GDT336 alpha
already selected by its inner training-folio loop for the same
`(register, held_folio)` fold; do not select a new alpha on GDT338.

Compare:

- `COORDINATE`: exact tuple frequency within compiler coordinate;
- `PLACEMENT`: the same distribution updated by line entry, within-field
  position, and line quartile with the frozen alpha.

Score exact tuple log loss, group top-1, and exact normalized whole-field
sequence top-1. Charge the placement model by one bit for the two-model family.

## Controls and sensitivity

- Report every register and physical-folio fold separately.
- Report one-group and two-group fields separately.
- Report coordinate-only compression as an adversarial over-normalization
  baseline, not as a licensed equivalence.
- Use 8,192 deterministic fixed-prediction diagnostic worlds. Wrapper outcomes
  are permuted inside
  `held-folio×register×coordinate×line-entry×previous-DY` strata. Tuple
  outcomes are permuted inside `held-folio×register×coordinate` strata. Report mobile-event
  capacity; these are diagnostics, not refitted exact conditional tests.
- ZL3b, IT2a and RF1b are not independent samples. GDT327 supplies one frozen
  source-native event stream.
- No surface glyph, raw word, separately addressed PAGE_HOST identity or
  feature, substring, neighbor feature, phase, semantic annotation, image, or
  external source enters a model. PAGE_HOST remains opaque inside the exact
  joint-tuple ID.

## Decision rule

Call `RENDERER_INVARIANT_FORMAL_EQUIVALENCE_SUPPORTED` only if all gates pass:

1. at least 20 held fields, 15 physical folios, nine normalized objects, ten
   register-conditioned object cells, and three registers;
2. `JOINT_TWO_RULE` is the shortest wrapper model after the `log2(6)` charge;
3. its gain over every baseline is positive in at least two represented
   registers and at least 10/17 held-folio folds;
4. `PLACEMENT` has positive one-bit-paid gain over `COORDINATE`, is positive in
   at least two represented registers and at least 10/17 held-folio folds, and
   does not reduce exact whole-field top-1;
5. both fixed-prediction max-two diagnostic p-values are at most .05.

If only exact-tuple wrapper normalization transfers but placement cannot recover
the object, call `EXACT_JOINT_RENDERER_NORMALIZATION_ONLY`. Otherwise call
`NO_STABLE_RENDERER_INVARIANT_EQUIVALENCE`. No alternative normalization,
class merge, threshold, renderer, placement variable, or subgroup may be added
after scoring.

## Claim ceiling

At most GDT338 may establish that multiple opaque rendered observations are
predictively exchangeable under one exact joint-tuple field sequence. It may
not collapse different exact tuple sequences unless a future experiment
licenses that operation. It assigns no word, morpheme, PAGE_HOST function,
semantic role, meaning, sound, language, plaintext, translation, diagram phase,
or external correspondence. f84 is forbidden and must not be opened, parsed,
retained, joined, or scored.
