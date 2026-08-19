# GDT383 — repaired multi-resolution local-role transfer with disjoint prediction

## Constraint inherited from GDT382

GDT382 is a methodology constraint.  GDT383 therefore does not privilege exact
composite joint identity, does not demand universal cross-domain coefficients,
and does not automatically remove frequency, recurrence, position, boundary,
or context as nuisance.  The GDT381 numeric target result, memberships,
threshold, realizations, and scores are not inputs to this design.

## Stage A only until authorization

Stage A reuses the frozen oracle-blind GDT382 observation layer and the
hash-bound readable oracle.  No Voynich table is an input.  Stage B is
unauthorized unless the complete Stage A gate passes; a passing Stage A result
must be published before a separate f84-free target method is frozen.

## Hierarchical local-role model

For each of six hidden positive-control roles, every outer fold learns separate
domain-local realizations and prevalence.  Five resolutions contribute without
a globally privileged unit:

1. local opaque/host identity;
2. complete rendered group;
3. wrapper/boundary/position construction;
4. exact composite joint state; and
5. a short field-local construction span.

Each resolution produces a fold-local log-odds score.  Nonnegative weights are
learned only from inner training blocks using rank performance and are
normalized separately in every domain/fold.  The resulting score represents a
local realization of an otherwise shared anonymous role.  Exact-joint-only and
strict held-domain universal models remain explicit controls.

Frequency, recurrence, record/field position, boundary/closure, previous state,
and record length are each evaluated in three modes: evidence available to the
role model; conditioned nuisance baseline; and omitted.  The primary hierarchy
allows them as grammar evidence.  No channel is removed merely because it is
predictive.

## Strict source/outcome separation

The pivot is element `j`.  `X` contains only the pivot and events at or before
`j`: local identities, renderer/construction state, frequency/recurrence,
position, boundary at the pivot, record shape, and preceding context.  No
event after `j` enters role membership.

Candidate outcomes `Y` are computed only from events `j+1..j+3` within the same
record.  The frozen family is:

* `POST_RETURN_ABC_A` — downstream state 1 equals state 3 but differs from 2;
* `POST_PERSIST_THEN_EXIT` — downstream states 1 and 2 agree, then 3 differs;
* `POST_HOMOGENEOUS_3` — all three downstream host states agree;
* `POST_LOW_DIVERSITY_3` — at most two downstream host states;
* `POST_ANY_BOUNDARY_3` — a downstream physical/field boundary occurs;
* `POST_WRAPPER_CHANGE_3` — wrapper changes within the downstream triple;
* `POST_RENDERER_STABLE_3` — renderer is constant across the downstream triple;
* `POST_TERMINUS_3` — a downstream event reaches record END.

Equality outcomes use only the three downstream host identities.  Construction
outcomes use only downstream construction coordinates.  No pivot identity,
role label, or source-side score defines `Y`.

For every outcome, a source-only model is fitted and evaluated out of fold.
An outcome is ineligible if the best source-only macro AUC exceeds the frozen
leakage ceiling `0.65`.  There is no post-target repair.  Among eligible
outcomes, each role chooses one outcome and one channel treatment solely on the
fixed development domains CoReMA, PCEEC2, and Curious Cures.  It is then tested
unchanged on Harleian and Quinte Essence.  The post-pivot model compares
source-only prediction with source plus the cross-fitted local-role score.

## Positive controls and gates

Roles: `FUNCTION_WORD`, `ALTERNATIVE_OR`, `POLARITY_EXCLUSION`,
`UNTIL_STATE_GATE`, `COORDINATOR`, and `REF_ANAPHORA`.

The seven GDT382 oracle-driven realization ceilings are retained: free token,
prefix, suffix, wrapper, boundary, positional, and zero/suppletive.  They are
diagnostic encodings, not corpus discoveries.

Stage A authorizes a target freeze only if all conditions hold:

1. all six local-role models have macro AUC at least `0.80`, positive held
   codelength gain, at least three positive domains, and joint max-family
   `p <= .05`;
2. for every role, the hierarchy exceeds exact-joint-only AUC by `0.02` and
   strict-universal AUC by `0.10`;
3. all 42 role×realization ceilings have AUC at least `0.90` and positive gain;
4. each selected post-pivot outcome passes source-overlap AUC `<= .65`;
5. at least four of six selected roles, including `COORDINATOR`, add positive
   held codelength on both untouched confirmation domains; and
6. the jointly charged 512-world fixed-prediction max-family diagnostic is
   `<= .05` for every promoted role and selected downstream test.

If any gate fails, Stage A stops and no Voynich source is read.

## Conditional Stage B contract

Only after Stage A passes will a separate target freeze bind the f84-free
GDT327 corpus.  It will learn register-/section-local realizations, keep all
five resolutions and grammar channels, infer membership on training folios,
and predict a strictly post-pivot held-folio transformation.  It must beat
placement/frequency baselines, be direction-stable across folios and at least
three registers, and pass one mobile maxT family over roles, horizons,
resolutions, and channels.

The priority lineage is comparator `COORDINATOR`, renamed anonymously.  It may
seed `LATENT_ROLE_A` only after Stage A.  No GDT381 target membership, threshold,
realization, or score may be reused or inspected.  Exact joint identity is one
channel, never the transfer unit.

## Ceiling and exclusions

A success can establish only `anonymous latent role + reproducible downstream
transformation`.  It cannot establish AND, OR, NOT, UNTIL, a function word,
POS, language, plaintext, or translation.  F1, AQ/contact, PAGE_HOST substring
mining, exact-tuple operator routes, and GDT345–347 remain closed.  No f84 file,
row, image, text, or formal payload may be opened, parsed, retained, or scored.
