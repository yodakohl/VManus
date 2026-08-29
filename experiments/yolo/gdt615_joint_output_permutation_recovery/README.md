# GDT615 — joint primitive/output binding recovery

Status: `MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE`

GDT614 failed because a post-hoc deck was bound arbitrarily to primitive IDs:
45/64 raw merge renders then lacked common carrier support, and their minimum
paid-subtree cover was 18 rather than eight. GDT615 keeps the deck, roles,
grammar, macro licenses, partitions, and eight-card budget fixed, but chooses
the output-to-primitive bijection jointly with the complete 64-merge bound on
train only and freezes that mapping plus its canonical minimum-cover
certificate. All three complete train worlds then choose their actual eight
paid locations and are committed before held is opened once.

Two independent exact implementations now agree on the complete canonical
mapping: 55/64 raw train-supported merges and an exact relaxed cover minimum
of four. The immutable mapping commit is published. Stage 1 then fails before
paid-card assignment: rank-14 `Ey` must be paid to cover its absent raw render,
but its mandatory unoverridden child composition `E+y → ho+i → hoi` is absent
from train and therefore forbids that same paid location. Three independent
implementations certify the contradiction. No W0/W1/W2 world was built and no
held, LM-confirm, oracle, recovery, Voynich target, f84, or f84r input was
opened.

See `METHOD.md`, `PREREGISTRATION.md`, and
`REPORT.md`. The public Stage-0 certificate begins at
`artifacts/stage0/STAGE0_MAPPING_COMMIT.json`; the terminal result is
`artifacts/stage1/STAGE1_RESULT.json`.
