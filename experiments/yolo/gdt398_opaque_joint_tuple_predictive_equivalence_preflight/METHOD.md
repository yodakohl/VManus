# GDT398 method — opaque joint-tuple predictive equivalence preflight

Date frozen: 2026-08-21

Status: `PREREGISTERED_BEFORE_OUTER_SCORE`

## Question

Can the 1,676 existing exact GDT327 joint-tuple types be replaced by fewer
anonymous `LATENT_FORM_ID` classes because independently learned classes
predict structural behavior on unseen physical folios better than exact tuple
identity after partition and selector costs?

This is formal compression, not semantic induction. The optimum is permitted
to be the complete exact inventory with no merge.

## Prerequisite and overlap audit

GDT397 is complete, committed, pushed, and validation-clean at commit
`416f9339a3049395bada230ecbb0eeec86c7cc76`. The route screen and primary
reports show no exact duplicate:

- GDT003 learned predefined surface edge additions/replacements and paradigm
  rectangles. It did not cluster GDT327 atomic states from arbitrary context.
- GDT025 described Currier-conditioned closure realizations already selected
  by formal families. It did not learn free equivalence among opaque tuples.
- GDT161 clustered LEFT/RIGHT operations from host-support/compatibility
  profiles; it never clustered complete GDT327 joint tuples.
- GDT299--302 begin from PAGE_HOST and whole-form positional alternants.
- GDT324--325 test predefined host/compiler coordinate cells and fallback.
- GDT338 marginalizes two supported renderer selectors while preserving every
  exact joint tuple; it explicitly does not merge different tuple sequences.

Those routes propose equivalence from edits, operation support, PAGE_HOST,
renderer coordinates, cells, or placement. GDT398 instead gives the candidate
algorithm only opaque IDs (`T0001...T1676` internally relabelled by sorted
hash), their training-folio occurrences, and structural behavior. Equivalence
is admitted only through unseen-folio predictive interchangeability.

## Inputs and seal

Primary input is the already published, f84-free
`gdt327_joint_tuple_interlinear.tsv` (8,448 events, 91 physical folios, 1,676
types). The bound `inputs/gdt398_safe_source_view.tsv.gz` contains exactly the
corresponding 8,448 ZL3b separator/raw-surface rows. It was produced through
`./vmanus-exp query-tsv`, with the exact GDT327 locus allow-list and
`--forbid-prefix f84`, before non-selector columns were materialized. The final
scorer reads only this f84-free view. Those fields supply boundary outcomes and
a named string baseline only.

The candidate model never receives PAGE_HOST, coordinate ID, frame, inner-D,
right family, DY, B3, wrapper, raw spelling, edit features, renderer labels,
semantic/visual annotations, or known transformations. PAGE_HOST and raw form
are isolated comparison baselines. f84 and f84r are forbidden.

## Fixed outer and inner splits

The 91 physical folios are sorted by decreasing event count and assigned
greedily to the currently smallest of 11 folds, ties by fold number. For outer
fold `j`, folds `(j+1) mod 11` and `(j+2) mod 11` form one inner validation
block; the remaining eight folds form inner training. No held-folio event
enters signatures, cluster assignments, smoothing, or selection.

## Observation-side signatures

For each recurrent training tuple, construct six view-balanced hashed vectors:

1. predecessor/successor exact tuple distributions;
2. distance-two predecessor/successor distributions at half weight;
3. physical line role/quartile, paragraph opening, field position/ordinal, and
   record ordinal;
4. guarded left/right source-separator categories;
5. same-record opaque co-occurrence, multiplicity, and record ordinal;
6. section/register/Currier/hand occurrence profiles.

Each view is L1-normalized before deterministic signed hashing to 256
dimensions; the combined vector is L2-normalized. Tuple identity may label a
context dimension but its characters and internal coordinates are unavailable.

## One bounded clustering path

Use deterministic agglomerative predictive clustering. Initial candidate
edges are the 24 nearest structural-signature neighbours under cosine
distance. At each step merge the active pair with the smallest centroid cosine
distance, update its occurrence-weighted centroid, and reconsider only the
union of the two sparse neighbour sets. Deterministic nearest bridges connect
components only if the graph exhausts before a requested cut.

One dendrogram is cut at exactly six retained-type fractions:

`1.00, 0.90, 0.75, 0.60, 0.45, 0.30`.

The `1.00` setting is no merge. The inner validation block selects one cut by
total predictive codelength, ties preferring more classes. No other distance,
linkage, embedding, K range, or smoothing family is tried.

## Held prediction

For every held event score five fixed outcomes:

- previous exact tuple or physical-line start;
- next exact tuple or physical-line end;
- physical placement (`SINGLE/START/MIDDLE/END`);
- guarded source boundary before;
- guarded source boundary after.

All models use the same hierarchical multinomial smoothing: a symmetric
Dirichlet-1/2 global distribution and conditional shrinkage mass 8. Models are:

- `GLOBAL_FREQUENCY`;
- `EXACT_TUPLE` (unweakened 1,676-way identity);
- `PAGE_HOST` (comparison only);
- `GDT338_NORMALIZED` (at group level this preserves the exact tuple and must
  reproduce `EXACT_TUPLE`);
- `STRING_SIMILARITY` (training-only connected components of modal raw forms
  at Levenshtein distance at most one; comparison only);
- `PLACEMENT_FREQUENCY` (training frequency bin plus dominant line role);
- `LEARNED_LATENT_CLASS`.

The primary gain is `EXACT_TUPLE bits - LEARNED_LATENT_CLASS bits`, summed over
the five outcomes.

## Complexity and stability accounting

Report raw held codelength, selected K, and two costs. Because the partition is
deterministic given training data and a cut, its conservative description cost
is `log2(number of training tuple types)` per outer fold. Cut selection costs
`log2(6)` per fold. Selector-paid gain subtracts both from raw gain.

Across outer fits report pairwise adjusted Rand stability on common training
types, per-type coassignment-neighbour Jaccard consistency, singleton and giant
cluster counts, and direct-merge coassignment stability. Repeat the gain after
removing the largest held cluster and after removing the training-frequency
top 5% of tuple types.

## Fixed null and anti-triviality controls

Use 64 deterministic worlds. Within each outer fold, permute learned class
assignments among training tuple types inside exact bins of training-frequency
band, dominant physical line role, and dominant register. This preserves tuple
frequency and approximate placement/register opportunity while breaking the
tuple-specific structural-context coupling. Held folio sizes and outcomes are
unchanged. For each world take the most favourable of all six outer-fold cut
scores before applying the same partition/selector costs. Partition-stability
nulls independently apply the same matched shuffles. Inclusive tails are
reported.

Candidate gain is also compared with PAGE_HOST, exact GDT338 normalization,
string similarity, placement/frequency, per-section/register direction,
largest-cluster removal, and frequent-type removal. Stable merges report
PAGE_HOST agreement and edit similarity descriptively only; neither helped
construct the partition.

## Decision rule

`PREDICTIVE_LATENT_TUPLE_EQUIVALENCE_SUPPORTED` requires all ten user-specified
conditions, mechanically instantiated as:

1. median selected retained fraction at most 0.90;
2. selector/partition-paid gain over exact identity is positive;
3. raw aggregate gain is positive;
4. at least 8/11 outer folds are positive;
5. positive raw gain in at least three powered registers and three powered
   sections (at least 100 held events per stratum);
6. mean partition ARI exceeds the 95th percentile matched-null stability;
7. raw gain remains positive after removing each fold's largest class;
8. raw gain remains positive after removing its top 5% frequent tuple types;
9. the paid candidate beats GLOBAL/FREQUENCY, PAGE_HOST, and the
   exact-equivalent GDT338 baseline;
10. it beats `STRING_SIMILARITY`, and at least half of published stable direct
    merges cross that string grouping.

If raw sharing is positive but fails costs/stability/controls, use
`LATENT_SHARING_WEAK_NOT_A_LEXICON_EQUIVALENCE` or
`APPARENT_EQUIVALENCE_EXPLAINED_BY_EXISTING_STRUCTURE` as appropriate. If no
selector-paid gain exists, use
`JOINT_TUPLE_LEXICON_NOT_COMPRESSIBLE_BY_FREE_PREDICTIVE_EQUIVALENCE`.

## Claim ceiling and stop

A pass establishes only a smaller anonymous predictive formal identity. It
does not establish a word, lexeme, morpheme, stem, allomorph, synonym, entity,
POS, language, meaning, sound, plaintext, or translation. A failure closes
this free latent-lexicon/equivalence route. No alternative clustering method,
expanded K range, edit/PAGE_HOST initialization, semantic interpretation, or
automatic follow-on experiment is authorized.

## Post-execution decision-label conformance correction

The public pre-outcome freeze is commit `12d5658e`. Before result publication,
the first deterministic run exposed that condition 9 above had named PAGE_HOST
and GDT338 but accidentally omitted the already mandatory GLOBAL/FREQUENCY
anti-triviality comparator. The correction adds no model, K, endpoint,
threshold, score, or search freedom and can only make promotion harder. It also
routes a raw gain that is dominated by GLOBAL/FREQUENCY, frequent-type removal,
or largest-cluster removal to
`APPARENT_EQUIVALENCE_EXPLAINED_BY_EXISTING_STRUCTURE`, as required by the
registered decision vocabulary. All numerical analysis remains byte-identical.
