# GDT388 endpoint and failure-message correction

2026-09-06. Read-only primary-method/code review; no new manuscript access,
experiment, changed gate or reopened route. This corrects interpretation of
GDT807 bookkeeping, not its paragraph-classification measurements.

GDT388 METHOD explicitly separates a local text-to-drawing relation from an
ordered inscription-to-inscription edge. The latter requires independently
fixed distinct endpoints, direction, singular ownership, source-blind selection,
capacity on at least five physical folios, whole-folio holdout and mobile nulls.
A local visual observation is a separate endpoint; it cannot impersonate such
an edge. No general ban on new visual evidence from known pages follows.

The phrase no formal identity opened during selection does not assert that
any page ever transcribed is forever unusable. But a new reviewer does not
undo prior selection using identities. Prior exposure and selection history
must remain explicit; known FORMAL_ACCESSED rows cannot be relabelled sealed.
Remaining visual admissions are access permission, not scientific holdout.

The GDT807 registry previously described537rows as failing only unsealed
formal access. Its builder explicitly sets geometry_only_selection FALSE,
paragraph-membership ownership, target-membership direction, fold NONE,
crop hashes NONE and INELIGIBLE_EXPLORATORY_TEXT_RELATION. The GDT388 executable
checks formal access for every row, but checks several other conditions only
inside the ELIGIBLE branch. A single emitted error therefore does not imply
all other scientific gates passed. Correct interpretation:537documented
ineligible text-context relations, not537almost-score-ready authorial edges.

The code also checks fold labels without itself proving that each physical
folio belongs to only one fold. A software PASS cannot replace checking the
frozen whole-folio requirement. No eligible new edge source was identified
by this review, and no speculative page acquisition follows.

Primary evidence:
- `experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/METHOD.md`,
  endpoint distinction and frozen eligibility gates.
- `tools/relation_edge_intake.py`, `_validate_edge_rows` conditional checks.
- `experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/src/run.py`,
  relation packet construction near direction_basis/eligibility_status.

Historical experiment bytes remain unchanged. The active registry is corrected
and an append-only ledger row records this interpretation change.
