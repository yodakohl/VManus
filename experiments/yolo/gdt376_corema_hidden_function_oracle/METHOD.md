# GDT376 — CoReMA hidden functional oracle

## Question

Can form-blind structural detectors rediscover functional annotations in real
medieval recipes when an entire source collection is unseen?

## Frozen observation boundary

Six previously audited CoReMA collections are used. The public detector layer
contains only collection/record order, element order, record length, direct
token count, and a salted opaque equality ID for each direct source form. It
contains no source string, editor label, concept ID, TEI role, annotation flag,
or parent link. Empty direct surfaces are excluded from scoring.

The hidden oracle contains `ALTERNATIVE`, `TIME`, `REF`, `CLOSER`, exclusion,
analogy, comparison, and `parent_instruction_ordinal`. Predicate-head and
valency endpoints are derived only during evaluation.

## Held evaluation

Each fold holds one complete collection. Fixed models are prevalence,
position/length nuisance, training-only opaque-ID rate, form-blind structural
features, and structure plus opaque-ID rate. Structural features use equality
and recurrence only: before/after repetition, return distance, anonymous
neighbor diversity, previous/next-record overlap, chain/reconvergence flags,
scope horizon, and training-only anonymous-form context diversity.

Promotion requires positive structural gain over nuisance, positive combined
gain over opaque identity, positive gain in at least four collections, pooled
AUC >= .65, average-precision lift >= 1.5, and max-family p <= .05. The
1,024-world held-label null preserves collection, record-length bucket,
position decile, and direct-token-count bucket. The null is a fixed-prediction
conditional diagnostic, not a retraining null.

Only promoted endpoint signatures may be transferred unchanged to Voynich.
No Voynich row is read in this experiment; f84 is not accessed.
