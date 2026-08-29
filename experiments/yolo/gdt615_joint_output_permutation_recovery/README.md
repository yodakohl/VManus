# GDT615 — joint primitive/output binding recovery

Status: `STAGE0_MAPPING_CERTIFICATE_PASS__STAGE1_NOT_RUN`

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
of four. The immutable mapping commit is published; Stage 1 has not yet chosen
actual paid locations or constructed an ordered truth world. Held can only
confirm or terminate the later unchanged three-world bundle; it cannot select
a replacement.

See `METHOD.md`, `PREREGISTRATION.md`, and
`REPORT.md`. The public Stage-0 certificate begins at
`artifacts/stage0/STAGE0_MAPPING_COMMIT.json`.
