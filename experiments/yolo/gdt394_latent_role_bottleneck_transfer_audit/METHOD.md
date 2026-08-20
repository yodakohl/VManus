# GDT394 — latent-role bottleneck transfer audit

## Interpretation correction

A learned role score is a deterministic function of the licensed source-side
observation. Therefore it cannot contain information conditional on the
complete source representation. The raw GDT384 `+425` bits, GDT385 `+194`
bits, and GDT387 `+85` bits can only measure useful compression,
regularization, or abstraction relative to finite fitted source models. They
are not information absent from the source.

GDT394 asks the corrected question: does the anonymous role score compress the
source into one dimension that predicts an independently supplied relation
better than equally small generic source summaries?

## Comparator-only sources

The two endpoints are fixed before scoring:

1. CoReMA explicit editor parent links, using the already retained
   `CMP_PARENT_02` cross-collection predictions from GDT385; and
2. PCEEC2 exact parse-derived governor targets and the retained anonymous
   cross-file role coordinate from GDT387.

The GDT382 observation layer supplies only its frozen opaque/composite
representation. No source word, translation, POS, concept name, role name, or
parse label is a predictor. There is no Voynich input.

## Fixed one-dimensional family

Every route produces exactly one scalar coordinate per held observation. No
dimension, hash width, penalty, smoothing parameter, or model family is tuned.

| ID | one-dimensional bottleneck |
|---|---|
| `ROLE_BOTTLENECK` | retained collection/file-held anonymous GDT385/GDT387 role log-odds |
| `LINEAR_ROLE_1D` | ridge projection of the same source features onto the hidden comparator role in training folds |
| `SUPERVISED_RELATION_1D` | ridge projection onto the first training-only multiclass-relation contrast |
| `PCA_SOURCE_1D` | first training-only principal component of the source representation |
| `RANDOM_SOURCE_1D` | one fixed seeded random source projection |
| `GRAMMAR_SUMMARY_1D` | first training-only component of frequency/recurrence/position/boundary/length summaries |
| `EXACT_JOINT_ROLE_1D` | training-fold smoothed role rate for exact composite-joint identity |
| `SHUFFLED_ROLE_1D` | linear role projection after a fixed training-only within-opportunity role shuffle |

The common source vector is a signed 64-bin hash of the frozen opaque host,
rendered group, wrapper, positional state, boundary state, record state,
renderer, composite joint state, previous opaque host, source-equality ID, and
fixed local conjunctions, plus seven numeric grammar channels. Continuous
features are standardized from training folds only. Ridge penalty is `10`.
Random seed is derived from `GDT394_FIXED_RANDOM_PROJECTION_V1`.

## Nested held evaluation

Outer folds are the six complete CoReMA collections and the 84 complete PCEEC2
source files. Each scalar is learned without its held collection/file. The
already retained `ROLE_BOTTLENECK` was produced by the same held-unit regime.
All other projections are refitted independently inside each outer fold.

A common downstream decoder converts each scalar into eight training-fold
quantile bins and estimates the external relation distribution with eight
Dirichlet pseudo-observations backed by the training-fold global relation
prior. Thus every route has one input dimension and the same relation-decoder
capacity. The reference is the training-fold global relation distribution.

The outputs are held codelength gain, relation-class top-1, true-class rank and
MRR, per-fold direction, and largest-fold sensitivity. Relation classes are
`NONE/D1..D13` for CoReMA and the frozen signed governor-distance classes for
PCEEC2. ZL3b/IT2a/RF1b and Voynich text do not enter this experiment.

## Coupling-destruction null

The fixed `512` shared worlds permute each scalar within

`held domain unit × positional state × boundary state × field-index bin ×
within-field-index bin × record-length bin × recurrence/frequency bin`.

The scalar marginal, held fold, source opportunity, and target remain fixed;
only scalar-to-relation coupling is destroyed. Every world refits the common
downstream decoder. The maximum gain across all eight routes is retained. For
each route report raw gain, null mean, and excess above null mean. The primary
inclusive p-value compares observed `ROLE_BOTTLENECK` gain to the worldwise
eight-route maximum.

## Frozen promotion gate

The anonymous role bottleneck passes only if, independently in **both**
domains:

1. its held codelength gain is positive and exceeds every other
   one-dimensional control;
2. its gain is positive in a strict majority of held units (`>=4/6` CoReMA,
   `>=43/84` PCEEC2);
3. its excess above its coupling-null mean is positive and exceeds every
   control's null-centered excess;
4. corrected max-eight `p <= .05`;
5. true-class MRR exceeds the best control by at least `.001`; and
6. top-1 correct classes exceed the best control by at least
   `max(3, ceil(.001 × N))`.

The overall result passes only if both domains pass. No threshold is changed
after scoring. Losing to any equal-budget source bottleneck closes this
semantic-role architecture; a pass freezes only an anonymous transferable
structural bottleneck and authorizes design—not execution—of a separate
GDT395.

## Claim ceiling

At most GDT394 may establish that one deterministic, low-dimensional source
abstraction transports across two readable relation tasks better than matched
one-dimensional alternatives. It cannot establish conditional information
outside the source, a Voynich role, TIME, REF, coordination, parent, syntax,
POS, meaning, language, plaintext, or translation. No Voynich or f84 material
may be opened, parsed, retained, or scored.
