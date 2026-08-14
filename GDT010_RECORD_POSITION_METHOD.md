# GDT010 host-matched record-position test

Status: `YOLO_FUNCTIONAL_CONSTRAINT_TEST`

## Purpose

Test whether the provisional GDT009 functions predict where a transformed form
appears inside its physical line.  The unit is an all-reading-exact physical
source group from the already published, non-f84 GDT002 occurrence inventory.

The primary contrasts are fixed before the permutation run:

1. bare host versus `q+host`;
2. `s+host` versus `d+host`;
3. bare host versus `host+DY`;
4. bare host versus `host+SY`;
5. `host+DAL` versus `host+DAR`.

Only hosts observed in both contrasted forms contribute.  Every contrast is
scored at three matching levels: host globally, host within physical folio,
and host within page.  The page-matched result is primary.  The fixed-effect
score weights each stratum by `nA*nB/(nA+nB)` and compares normalized line
position, line-final status, line-initial status, and nonprose status.  A
deterministic 20,000-draw permutation shuffles form labels within the declared
stratum while preserving frequencies and all observed outcomes.  Leave-one-
physical-folio and leave-one-section ranges expose concentration.

This is an exploratory test on a module-selected group universe.  It does not
establish semantic meanings, but a stable host-matched ordering can constrain
the generative record grammar.  f84r remains absent and sealed.
