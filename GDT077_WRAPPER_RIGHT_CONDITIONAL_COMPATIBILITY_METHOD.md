# GDT077 — WRAPPER/RIGHT_FAMILY conditional compatibility

Status: **YOLO formal dependency test**

Score the paired HPR2 coordinates `WRAPPER` (8 states) and `RIGHT_FAMILY` (6
states) on all source groups with complete target physical folios held out.
The baseline estimates PAGE_HOST marginals and adapts them to the five-way
register using a fixed pseudocount grid `{1,4,16,64,256}`.  Two directional
models then add a host×register pair table, shrunk to the corresponding adapted
marginal with pseudocount `{1,4,16,64,256}`:

- `RIGHT_GIVEN_WRAPPER`: `P(W|H,register) P(R|H,register,W)`;
- `WRAPPER_GIVEN_RIGHT`: `P(R|H,register) P(W|H,register,R)`.

Report all 5 baseline and 25 directional configurations.  Pay `log2(5)` or
`log2(25)` selector bits when comparing best totals.  A material one-way gain
supports ordered conditional compatibility, not meanings or linguistic
morphology.  f84r is excluded.
