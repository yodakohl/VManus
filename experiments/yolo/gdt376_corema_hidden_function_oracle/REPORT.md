# GDT376 report — hidden CoReMA functional oracle

## Result

One endpoint passes the complete frozen collection-held gate:
`PREDICATE_HEAD_WITH_DEPENDENTS`. Across 27,349 observable elements, its
form-blind structural model gains **845.705 bits** over position/length
nuisance. Structure plus opaque identity gains **3,409.024 bits** over opaque
identity alone and **2,239.561 bits** over the better aggregate baseline. The
gain is positive in 5/6 held collections; pooled AUC is .9036, average
precision .7525 at prevalence .2675, and the 11-endpoint max-family p is
.000976.

This calibrates only an anonymous **local-head-with-dependents structural
signature**. It does not calibrate the number or type of arguments:
`HIGH_VALENCY_HEAD` fails with 0/6 positive folds, while
`PARENTED_DEPENDENT` loses 708.032 bits to its strongest baseline.

## Non-transfers

No detector for ALTERNATIVE, TIME, REF, CLOSER, exclusion, analogy, comparison,
or a pooled function-word class passes. Several have attractive AUC or a raw
gain against the weak nuisance model, but exact opaque identity or generic
record position explains more. In particular, CLOSER is highly rankable but
its structure-only model loses 1,283.867 bits to nuisance; REF loses to both
baselines; and exclusion/analogy gains vanish against opaque identity.

The ranked roadmap therefore narrows to one admissible Voynich transfer:
`LOCAL_VALENCY_PREDICATE_HEAD`. Every other new family remains registered but
must not be tuned on Voynich candidates.

## Next action

Map the frozen local-head signature once to f84-free GDT327 atomic tuples,
using physical record order and opaque exact tuple equality. Rank candidates
without assigning a predicate, action, POS, or English gloss. The high-valency
and dependent signatures remain negative controls.

No Voynich row was read or scored here, and f84 was not accessed.
