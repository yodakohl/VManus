# GDT238 — stable label prefix to visible relation mode

## Question

Do the seven prefixes selected in all eight GDT237 training folds carry a
reusable graphical relation mode among independently human-annotated labels?

## Endpoint and model

Use non-f84 exact-locus rows tagged `LABEL` with a nonempty local relation tag
and strict first-family coverage.  Reduce the source tags by fixed precedence:
explicit attachment; enclosure/contact; array/group; proximity.

The primary set contains only rows carrying one of the seven already-frozen
prefixes.  In leave-one-physical-folio-out prediction, map each exact prefix to
its modal training relation class and compare it on identical covered rows to
the held row's training-section modal class.  Exact raw-family lookup is a
secondary counterexample.  No prefix, threshold, or relation class is selected
from the outcome.

The endpoint is visible source annotation geometry, not authorial ownership or
semantics.
