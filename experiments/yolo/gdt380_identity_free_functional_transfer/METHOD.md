# GDT380 — identity-free functional-operator transfer

## Question and chronology

GDT379 closes `F1` for semantic interpretation. Its only surviving status is
the exposed formal recurrence anomaly `F1 X F1`; GDT380 neither uses F1 nor
tests it as AND, OR, NOT, UNTIL, a function word, or any other function.

GDT380 asks whether the four cross-corpus signatures frozen by GDT378 can be
expressed as **surface-identity-free local behavioral transformations**, then
transfer to f84-free Voynich records without nominating a recurring tuple.
The experiment has two publication stages:

1. freeze and score the comparator behavioral instrument without reading a
   Voynich target;
2. only if a comparator family passes its frozen cross-domain gate, freeze a
   Voynich mapping and null before reading target outcomes.

Readable comparator labels are available only to the comparator evaluator.
Voynich-facing artifacts use `CMP_FUNCTION_01`–`04` and `UNASSIGNED` only.

## Comparator observation and identity-free representation

The frozen GDT378 observation layer supplies record membership, order,
boundaries, lengths, opaque equality identity, recurrence, and collection
metadata. Words, translations, concepts, POS, parses, roles, parents, and
function labels are absent. Exact `opaque_form_id` values are never model
features. They are used only inside equality predicates and aggregate
recurrence/diversity calculations.

For every element, the common nuisance panel is frozen as record-length bin,
relative-position spline, boundary-before/after, source length, direct-token
count, within-record recurrence count, and collection/domain intercepts. Four
behavior blocks are fixed before scoring:

- `CMP_FUNCTION_01 / GATE_TRANSITION`: pre/post window diversity and entropy,
  forward return horizon, novelty after the pivot, continuation-length change,
  and termination at record/line boundaries;
- `CMP_FUNCTION_02 / BRANCH_RECONVERGENCE`: left/right local-bag similarity,
  predecessor-equals-successor reconvergence, two-sided return, neighbor
  mutual exclusion, and alternative-path convergence within horizons 2/4/8;
- `CMP_FUNCTION_03 / MARKED_INVERSE_DELTA`: asymmetry and signed change between
  pre/post recurrence, diversity, novelty, return and continuation state,
  including whether deleting the pivot joins a recurrent transition;
- `CMP_FUNCTION_04 / CLOSED_CLASS_BOTTLENECK`: grammar-placement stability,
  high neighbor diversity, broad record recurrence, low local identity
  concentration, short return profile, and weak association with one local
  content neighborhood.

All windows 1, 2, 4, and 8 are predeclared. These blocks are behavioral
proxies, not definitions of the readable labels and not meanings.

## Comparator folds, null, and gate

Each family is evaluated in leave-one-domain-out folds over CoReMA, PCEEC2,
Curious Cures, Harleian Cookery, and Quinte Essence where its hidden endpoint
exists. A regularized logistic model compares nuisance alone with nuisance plus
the fixed behavior block. Standardization and coefficients are learned in the
training domains only.

The primary statistics are macro held-domain AUC, held codelength gain over
nuisance, and a conservative transfer floor: the third-best held-domain AUC.
One shared 1,024-world label permutation preserves domain, collection,
record-length bin, position quintile, boundary state, and recurrence bin. The
max statistic charges all four families and all reported horizons/components.

A family becomes eligible for Voynich mapping only if all of the following
hold without retuning:

- transfer-floor AUC at least 0.60;
- positive behavior-over-nuisance held gain in at least three domains;
- AUC at least 0.60 and positive gain in PCEEC2;
- AUC at least 0.60 and positive gain in at least one medical/procedural
  domain (`CURIOUS_CURES`, `HARLEIAN_COOKERY`, or `QUINTE_ESSENCE`);
- inclusive four-family maxT `p <= 0.05`;
- the effect remains positive when all features based on recurrence of the
  pivot itself are removed.

Failure stops that family before Voynich. This gate does not alter GDT378 or
retroactively validate any prior lead.

## Frozen Voynich mapping, if authorized

The target stage may use only the f84-free GDT327 exact joint-tuple
interlinear. Joint tuples remain atomic. Stable tuple, group, PAGE_HOST,
substring, glyph, or surface identity is prohibited as an input.

The same common behavior representation is evaluated at four charged
resolutions: atomic event context, complete source-group context, field-local
transition, and recurring behavior-defined construction/slot. Candidate
classes are defined from cross-fitted behavior scores or training-folio
centroids, never exact tuple identity or an exactly conditioned slot.

Whole physical folios are held out. A class must improve prediction of its
predeclared downstream structural consequence over nuisance in held folios,
retain its direction in at least 60% of powered folios and three registers,
and pass one maxT family charging four signatures × four resolutions × four
horizons plus every reported behavior family. The target null preserves
section, register, Currier, hand, line/field position, closure, record length,
tuple frequency, recurrence, and transition opportunity while leaving class
membership mobile. Deterministic membership after conditioning is
`UNIDENTIFIABLE`, excluded from the max statistic, while its attempted search
remains charged.

Only after a class passes may formal realizations be inventoried. Such a class
is named anonymously, for example `CMP02_BEHAVIOR_CLASS_A`. Realization
inspection cannot promote the class or change its gate.

## Claim ceiling and seal

The ceiling is a transferable anonymous structural-behavior class. GDT380 may
not establish AND, OR, NOT, UNTIL, function word, POS, morpheme, sound,
language, plaintext, meaning, or translation. No f84 file, row, image, text,
or formal payload may be opened, parsed, retained, or scored.
