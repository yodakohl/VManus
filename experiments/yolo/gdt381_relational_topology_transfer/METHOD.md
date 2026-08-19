# GDT381 — cross-domain relational-topology operator transfer

## Purpose and route separation

GDT381 moves one abstraction level above GDT378–380. It does not search exact
Voynich identities and does not reuse GDT380's corpus-independent local feature
vectors. Instead, every readable corpus independently learns its own latent
context/equivalence classes. Cross-domain transfer uses only graph invariants
of transitions among those local classes; class labels and feature scales are
never aligned.

The experiment is comparator-first. The clustering rule, five topology
families, hidden-oracle endpoints, baselines, null, gates, and possible Voynich
mapping are frozen and published before hidden-oracle evaluation. Voynich is
inaccessible unless a comparator topology passes.

## Corpus-local latent classes

The source is the frozen GDT378 comparator observation layer. Words,
translations, concepts, POS, parses, semantic roles, functional annotations,
and parent links remain hidden. Within each domain, each opaque form type is
summarized only by form-blind structural behavior:

- record-position and record-length histograms;
- boundary-before/after rates;
- within-record recurrence and return rates;
- predecessor/successor diversity and normalized graph degree;
- record and collection coverage;
- local predecessor=successor and repeat geometry.

Exact opaque IDs index these within-domain summaries but are not model
features and never cross domains. Features are standardized inside each
domain. Deterministic k-means uses seed `381001 + domain_ordinal`, 20 restarts,
and candidate K values 4, 6, 8, 12, 16, and 24. K is chosen without oracle
labels as the smallest value recovering at least 80% of the maximum
K=24 reduction in within-cluster sum of squares relative to K=1. Empty/tiny
domains fall back to the largest feasible K. Cluster numbers are arbitrary and
must never be aligned, named, or interpreted.

## Class-label-invariant event topology

Each occurrence is mapped to its corpus-local class, then represented only by
invariants under arbitrary permutation of class labels. The fixed topology
library includes:

- predecessor/successor equality and class change;
- source out-degree, target in-degree, and class-size ranks;
- number of distinct two-edge alternatives between the same endpoints;
- branch at the predecessor followed by reconvergence within 1, 2, 4, or 8
  events;
- pre/post class-set overlap and Jensen-Shannon divergence;
- disappearance of a persistent pre-state and entry into a new post-state;
- current-class return and previous-class resume horizons;
- homogeneous left/right class symmetry and repeated A-C-A-C chains;
- deletion-bridge support for predecessor→successor;
- termination at record/physical-line boundaries.

The `TRIVIAL_MOTIF_BASELINE` includes local equality, class-size/degree ranks,
and one-step class change. The full model must add held predictive information
beyond both placement/recurrence nuisance and this baseline, preventing common
non-operator motifs from qualifying by themselves.

## Five jointly charged comparator families

Readable labels are used only by the evaluator. The exported identifiers and
all prospective Voynich identifiers remain anonymous.

| anonymous topology | hidden comparator endpoint | intended topology test |
|---|---|---|
| `CMP_TOPOLOGY_01` | `UNTIL_STATE_GATE` | persistent state followed by gate/exit |
| `CMP_TOPOLOGY_02` | `ALTERNATIVE_OR` | branch, alternatives, reconvergence |
| `CMP_TOPOLOGY_03` | `POLARITY_EXCLUSION` | marked/unmarked counterpart and inverse downstream change |
| `CMP_TOPOLOGY_04` | `COORDINATOR` | homogeneous-class linking and variable-arity chains |
| `CMP_TOPOLOGY_05` | `NEXT_RESUME` | local reset followed by resume/next state |

These names describe comparator provenance only, not Voynich functions.

## Held-domain evaluation and controls

For each endpoint, a low-capacity L2 logistic model is trained on all available
domains except one and evaluated on the entirely held domain. Domain-local
classes for the held corpus are learned without labels. Model inputs are only
label-invariant topology scalars. Standardization and coefficients are learned
from training domains.

Three nested models are fixed: placement/recurrence `NUISANCE`, nuisance plus
`TRIVIAL_MOTIF_BASELINE`, and nuisance plus the complete relational topology.
Primary statistics are held AUC, full-vs-nuisance codelength gain,
full-vs-trivial-baseline gain, and the third-best held-domain AUC.

A shared 2,048-world null permutes hidden endpoint membership within domain ×
collection × record-length bin × position quintile × boundary state ×
recurrence-opportunity bin × latent-class-size quartile. Class assignments,
record topology, class sizes, and recurrence opportunities remain fixed.
Every family, horizon, and reported topology component enters one maxT family.
An endpoint with deterministic membership after conditioning is
`UNIDENTIFIABLE`, excluded from maxT while remaining charged.

A topology is eligible for Voynich only if, without retuning:

- third-best held-domain AUC is at least 0.62;
- full topology adds positive bits over nuisance in at least three domains;
- full topology adds positive bits over the trivial-motif baseline in at least
  three domains;
- PCEEC2 has AUC at least 0.60 and positive gain over both baselines;
- at least one medical/procedural domain has AUC at least 0.62 and positive
  gain over both baselines;
- inclusive five-family maxT `p <= .05`;
- direction remains positive after deleting all one-step equality motifs.

## Voynich stage if and only if authorized

Only a passing anonymous topology may be frozen for target use. The target
source is the already f84-free GDT327 atomic joint-tuple grammar. Joint tuples
remain atomic; PAGE_HOST, substring, glyph, surface, and exact tuple/group
identity are prohibited as model inputs.

Voynich latent context classes are learned independently within powered
register/section strata from grammar-state, field/record membership, physical
line/reset behavior, recurrence, and equality geometry without semantic
labels. Cross-stratum classes are not aligned. The frozen comparator topology
is applied through the same class-label-invariant graph representation.

Whole physical folios are held out. Promotion requires positive held gain over
placement/recurrence and trivial-motif baselines, direction in at least 60% of
powered folios and three registers, and one target maxT family charging every
authorized topology, resolution, horizon, and construction search. Formal
realizations may be inspected only after an anonymous behavior topology passes.

## Deduplication and claim ceiling

This is not GDT345–347. Those experiments predicted Voynich coordinate deltas
and compatibility operators. GDT381 uses no target coordinates as outcomes and
learns no Voynich operator manifold; its endpoint is a comparator-validated
semantic-function topology over independently learned corpus-local classes.

GDT381 cannot establish AND, OR, NOT, UNTIL, POS, meaning, language, plaintext,
or translation. No f84 file, row, image, text, or formal payload may be opened,
parsed, retained, or scored.
