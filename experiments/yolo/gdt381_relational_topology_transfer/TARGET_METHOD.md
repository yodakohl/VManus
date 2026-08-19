# GDT381 — frozen anonymous Voynich topology mapping

## Authorized signature

Only `CMP_TOPOLOGY_04` is authorized. Its readable-comparator provenance is not
a Voynich label. Target artifacts call it `CMP_TOPOLOGY_04` and keep semantic
state `UNASSIGNED`.

The comparator final model is fitted to all four available readable domains
using the already frozen full relational-topology vector. A single rank
threshold is selected from `.50`, `.65`, `.80`, and `.90` using macro balanced
accuracy of leave-one-domain-out comparator predictions. Both coefficients and
the winning quantile are frozen before target scoring.

## Target observation boundary

The sole target source is the already f84-free
`gdt327_joint_tuple_interlinear.tsv`. A target observation contains only atomic
tuple equality, physical page/folio and record order, field/order position,
line reset, DY/B3 closure, register/section/Currier/hand, and recurrence.
PAGE_HOST, host/coordinate factorization, substring, glyph, surface, and exact
tuple/group identity as a predictor are forbidden.

Within each register, exact atomic tuple IDs index form-blind occurrence
profiles but are never classifier inputs. The comparator clustering algorithm
and K rule are reused independently in each register. Register-local class IDs
are arbitrary and not aligned.

Target boundary mapping is frozen as:

- `boundary_before = line_first OR prev_dy`;
- `boundary_after = dy_closure OR b3 OR physical-line-final-group`;
- record = `(page, record_ordinal)`;
- collection = physical folio.

The complete frozen comparator topology vector assigns each event a score.
Within each register, membership in anonymous `CMP04_BEHAVIOR_CLASS_A` is the
frozen comparator-selected score quantile. This definition uses pre/post class
topology but no Voynich identity, meaning, or semantic label.

## Prospective held-folio consequence

Class recurrence is tested by predicting held-folio membership from source-side
information available at or before the pivot:

- nuisance: section, register, Currier, hand, record length, record/line/field
  position, closure, exact-tuple recurrence count, and current latent-class
  size;
- trivial source motif: predecessor/current class change, predecessor graph
  degree, current class frequency, prior return, and left-window class diversity;
- full source topology: predecessor branch degree, number of alternative paths
  entering the pivot class, pre-pivot class-run/persistence, left horizons
  1/2/4/8, and boundary opportunity.

No post-pivot class, target score, target class identity, exact tuple, wrapper,
PAGE_HOST, or renderer coordinate is a predictor. The primary is held
codelength gain of full source topology over both nuisance and trivial source
motif. Secondary measures are AUC and top-quintile lift.

Every physical folio is held out. Feature scales and coefficients are learned
without it. A 4,096-world conditional held-score null permutes behavior-class
membership within section × register × Currier × hand × record-length ×
record/line/field-position × closure × recurrence × latent-class-size strata.
Membership must be mobile; deterministic strata are descriptive only.

Promotion requires all of:

- positive total held gain over nuisance and trivial baselines;
- positive gain over both baselines in at least 60% of powered folios;
- positive gain over both in at least three powered registers;
- held AUC at least .60;
- inclusive maxT `p <= .05` charging both baselines, four horizons, class-size
  choices, register deletions, and all reported source-topology components;
- at least 256 mobile target events, 20 powered folios, and three registers.

Only after all gates pass may exact formal realizations be inventoried. A
failure publishes no realization identity.

## Claim ceiling and seal

At most this can establish a transferable anonymous relation-topology class in
the frozen formal grammar. It cannot establish coordination, AND, OR, NOT,
UNTIL, POS, meaning, language, plaintext, or translation. f84 remains sealed.
