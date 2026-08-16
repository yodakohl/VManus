# GDT164 — parser-independent substitution report

Decision: **PARSER_INDEPENDENT_SUBSTITUTION_NOT_SUPPORTED**.

## Voynich external-context transfer

The firewall-retained source has 15,364 rows and 660
eligible section×hand cells.  The target has 104 dimensions built
only from neighboring source-group identities/classes and mechanical unit
coordinates.

| split | model | predictions | fractional MSE gain | cosine | positive-dot |
| --- | --- | ---: | ---: | ---: | ---: |
| `HELD_BASE` | `OP_SUBSTITUTION` | 322 | -0.057989 | +0.245180 | 0.776 |
| `HELD_BASE` | `POSITION_ONLY` | 660 | -0.028097 | +0.003600 | 0.479 |
| `HELD_BASE` | `EXACT_PAIR_OTHER_STRATA` | 493 | -0.236192 | +0.237803 | 0.787 |
| `HELD_BASE_AND_SECTION` | `OP_SUBSTITUTION` | 261 | -0.127586 | +0.199895 | 0.751 |
| `HELD_BASE_AND_SECTION` | `POSITION_ONLY` | 660 | -0.038352 | -0.005665 | 0.481 |
| `HELD_BASE_AND_SECTION` | `EXACT_PAIR_OTHER_STRATA` | 491 | -0.245396 | +0.241368 | 0.778 |
| `HELD_BASE_AND_HAND` | `OP_SUBSTITUTION` | 252 | -0.152876 | +0.189786 | 0.738 |
| `HELD_BASE_AND_HAND` | `POSITION_ONLY` | 660 | -0.036152 | -0.008509 | 0.477 |
| `HELD_BASE_AND_HAND` | `EXACT_PAIR_OTHER_STRATA` | 485 | -0.278117 | +0.233782 | 0.779 |


Aggregate position-preserving p is 0.132683;
best-operation maxT p is 0.024390.

## Strongest directed relations

| operation | cells/bases | sections/hands | base gain | held-section | held-hand | maxT p | dominant external deltas | label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `L3:P1:l>p` | 5/3 | 2/2 | +0.3389 | +0.0000 | +0.0000 | 0.0244 | `from_start=0:+0.4897/+0.4333|unit_quartile=Q0:+0.4746/+0.4079|prev_freq=MISSING:+0.4382/+0.3891|prev_len=MISSING:+0.4382/+0.3891|from_start=3P:-0.4358/-0.3700` | `WEAK` |
| `L3:P2:k>r` | 5/3 | 4/3 | +0.1735 | +0.0563 | -0.1298 | 0.0702 | `prev_len=L2:+0.3249/+0.0887|to_end=3P:-0.2855/-0.0805|next_freq=R16P:-0.2750/-0.2937|to_end=0:+0.1970/+0.2118|from_start=2:+0.1861/-0.0573` | `WEAK` |
| `L3:P1:k>p` | 5/3 | 3/3 | +0.1707 | +0.1045 | +0.1045 | 0.0722 | `unit_span=8P:+0.3050/+0.0655|from_start=0:+0.2900/+0.4589|prev_freq=MISSING:+0.2715/+0.4313|prev_freq=R16P:-0.2715/-0.3476|prev_len=MISSING:+0.2715/+0.4313` | `WEAK` |
| `L3:P3:o>y` | 17/9 | 4/3 | +0.1508 | +0.0740 | +0.0856 | 0.0820 | `unit_quartile=Q0:-0.2012/-0.1972|from_start=0:-0.1507/-0.1472|from_start=3P:+0.1307/+0.1297|prev_freq=MISSING:-0.1203/-0.1175|prev_len=MISSING:-0.1203/-0.1175` | `WEAK` |
| `L3:P1:l>o` | 5/3 | 2/2 | +0.1145 | +0.0000 | +0.0000 | 0.1044 | `next_freq=R16P:+0.2557/+0.2614|unit_quartile=Q2:+0.2468/+0.2546|to_end=3P:+0.1985/+0.1915|prev_freq=R16P:+0.1518/+0.1655|unit_quartile=Q3:-0.1304/-0.1305` | `WEAK` |
| `L3:P1:c>s` | 8/3 | 4/5 | +0.0932 | +0.0000 | +0.0000 | 0.1200 | `from_start=3P:-0.1620/-0.0671|unit_span=3:+0.1176/+0.0301|prev_freq=R16P:-0.1134/-0.0660|unit_quartile=Q2:-0.1012/-0.0575|unit_quartile=Q1:+0.1001/-0.0026` | `WEAK` |
| `L3:P1:e>l` | 10/4 | 4/4 | +0.0903 | +0.0088 | -0.0061 | 0.1249 | `to_end=0:+0.2634/+0.2304|to_end=3P:-0.2579/-0.2453|next_freq=R16P:-0.2434/-0.2209|next_freq=MISSING:+0.2391/+0.2100|next_len=MISSING:+0.2391/+0.2100` | `WEAK` |
| `L3:P3:e>y` | 17/7 | 4/4 | +0.0764 | +0.0037 | -0.0211 | 0.1424 | `unit_quartile=Q3:+0.1833/+0.1514|to_end=3P:-0.1583/-0.1312|to_end=0:+0.1488/+0.1309|next_freq=MISSING:+0.1374/+0.1215|next_len=MISSING:+0.1374/+0.1215` | `WEAK` |
| `L3:P1:e>k` | 13/6 | 4/3 | +0.0608 | -0.0411 | -0.0461 | 0.1541 | `to_end=3P:-0.2109/-0.2040|unit_quartile=Q3:+0.1730/+0.1715|next_freq=R16P:-0.1686/-0.1601|from_start=1:-0.1562/-0.1531|from_start=3P:+0.1390/+0.1344` | `WEAK` |
| `L2:P2:l>r` | 18/3 | 6/5 | +0.0511 | -0.0737 | -0.0828 | 0.1629 | `unit_quartile=Q0:+0.1559/+0.1665|from_start=3P:-0.1287/-0.1061|from_start=0:+0.1025/+0.0890|prev_freq=MISSING:+0.0995/+0.0867|prev_len=MISSING:+0.0995/+0.0867` | `WEAK` |
| `L2:P1:l>o` | 8/4 | 3/2 | +0.0267 | +0.1727 | +0.1523 | 0.1893 | `prev_freq=R16P:+0.2030/+0.2229|to_end=3P:+0.1550/+0.2246|next_freq=R16P:+0.1441/+0.2138|unit_quartile=Q3:-0.1186/-0.1166|to_end=1:-0.1164/-0.0713` | `WEAK` |
| `L2:P1:o>y` | 15/4 | 5/3 | +0.0248 | -0.0788 | -0.1627 | 0.1922 | `prev_freq=R16P:-0.1598/-0.1620|next_freq=R16P:-0.1466/-0.1488|from_start=3P:-0.1263/-0.1213|unit_span=8P:-0.1020/-0.1039|prev_freq=R5_15:+0.0687/+0.0746` | `WEAK` |


These are post-ranked exploratory relations.  Character names are frozen HPR2
display characters, not manuscript graphemes or sounds.

## Identical historical endpoint

| corpus | capacity | cells/base predictions | held-base gain | position | exact pair | held-stratum gain | null p | top maxT p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `VOYNICH_PAGE_HOST` | `POWERED` | 660/322 | -0.05799 | -0.02810 | -0.23619 | -0.12759 | 0.1327 | 0.0244 |
| `IFORAL_1395_1411_GRAPHEMATIC` | `LOW_CAPACITY` | 349/28 | -0.22344 | -0.04191 | -0.25070 | -0.16138 | 0.4195 | 0.0722 |
| `LATIN_15C_GRAPHEMATIC` | `LOW_CAPACITY` | 485/13 | -0.58779 | -0.01902 | -0.35003 | -0.64729 | 0.9678 | 0.9698 |
| `LATIN_GERMAN_APOTHECARY_LATE15` | `LOW_CAPACITY` | 27/0 | +0.00000 | -0.08689 | +0.40209 | +0.00000 | 1.0000 | 1.0000 |
| `LATIN_MEDICAL_GRAPHEMATIC` | `LOW_CAPACITY` | 482/0 | +0.00000 | -0.01318 | -0.33605 | +0.00000 | 0.5444 | 0.5600 |
| `LATIN_SCHOLASTIC_GRAPHEMATIC` | `POWERED` | 1401/280 | -0.29495 | -0.00612 | -0.32761 | -0.32783 | 0.4429 | 0.0566 |


The endpoint and null are identical across corpora.  Historical held strata are
source folds; they are provenance partitions, not independent manuscripts.

## Interpretation

This is the direct parser-coupling test.  The target excludes every focal
same-group HPR2 field and contains only external neighbor and unit-position
information.  The aggregate substitution gain is negative, and exact-pair
identity is also negative on this external target.  GDT163's strongest
`L3:P3:a>y` relation falls to
-0.168375
at held base,
-0.581220
with section excluded, and
-0.555184
with hand excluded.  The one maxT-ranked local relation has no section- or
hand-excluded predictions and cannot rescue the non-significant aggregate.

Only the scholastic historical control reaches the fixed 100-prediction power
label after fold stratification; all historical results are otherwise retained
as low-capacity sensitivities.  GDT164 therefore does not support substitution
transfer outside the HPR2 parser coupling.  This narrows GDT163 rather than
proving that no internal operation exists.  See `gdt164_counterexamples.tsv`
for failed relations and limitations.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
