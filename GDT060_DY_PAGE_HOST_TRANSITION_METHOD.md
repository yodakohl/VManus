# GDT060 — DY-conditioned PAGE_HOST transition transfer

Status: **YOLO exploratory generative test**

## Question

Does an internal DY boundary select the following HPR2 `PAGE_HOST` conditional
on the preceding host, beyond ordinary held-folio character statistics and
beyond the marginal distribution of material after DY?

## Frozen input and decomposition

Use every complete physical line in `gdt016_group_state_inventory.tsv`, with
f84r excluded before retention.  Apply exactly the GDT059 HPR2 exploratory
decomposition: terminal B3, frozen right-family, carrier-conditioned inner D,
and only ladder-licensed O/OT layers are removed to obtain `PAGE_HOST`.

Every adjacent group pair is one boundary.  A boundary is DY when the left
group has the source-native `dy_closure` flag.  The target is the complete
right-hand representation.  Physical source groups remain the units; no
separator is interpreted as a linguistic word break.

## Held prediction

For each complete physical-folio fold, train four fixed order-2 character
models on all other folios:

1. `BASE`: right string only;
2. `BOUNDARY`: right string conditional on DY versus non-DY;
3. `PRE`: right string conditional on the last two characters of the left
   string;
4. `PRE_BOUNDARY`: both previous-host suffix and boundary class.

Conditional models use a fixed four-event shrinkage prior; the joint model
shrinks to the mean of `BOUNDARY` and `PRE`.  Score raw surface, residual-root,
and PAGE_HOST strings separately.  Repeat with the complete target register
class excluded from training as a strong transfer sensitivity.

The primary statistic is the PAGE_HOST `PRE_BOUNDARY` gain over `PRE` on real
DY boundaries.  The sharper interaction statistic compares, for each held
boundary, the DY-versus-non-DY log odds from `PRE_BOUNDARY` with the same log
odds from `BOUNDARY`.  Permute DY locations within physical folio × register ×
line-position quartile × left-length bucket × right-length bucket, preserving
every stratum's DY count.  Report local and maxT-adjusted Monte Carlo p-values
over the three representations and three frozen discrimination statistics.

## Interpretation

Positive transfer would identify a formal record-transition channel, not a
semantic field or linguistic morpheme.  Negative transfer would weaken only
HPR2's claim that DY coordinates content-host transitions.  It would not erase
DY's already established formal boundary behavior.  No English gloss, role,
word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned.
