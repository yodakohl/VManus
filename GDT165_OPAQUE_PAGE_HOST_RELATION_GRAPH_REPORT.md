# GDT165 — opaque PAGE_HOST relation graph report

Decision: **OPAQUE_HOST_RELATIONS_NOT_TRANSFERABLE**.

## Capacity

The parser-firewalled inventory contains 12,467 directed within-line
adjacencies on 92 physical folios,
1,511 source identities, and 1,454 target identities.
The fixed 128-host community panel contains
94.62%
of edges at at least one endpoint.

## Held prediction

| split | events/folds | exact-host gain | bits/event | positive folds | community gain | exact over community | source seen | host top1/top5 | nuisance top1/top5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HELD_FOLIO` | 12467/92 | -8912.517 | -0.71489 | 0/92 | -13522.283 | +4609.766 | 0.923 | 0.0701/0.2621 | 0.0780/0.2832 |
| `HELD_SECTION` | 12467/6 | -8808.239 | -0.70652 | 0/6 | -15514.558 | +6706.319 | 0.904 | 0.0685/0.2318 | 0.0687/0.2533 |
| `HELD_HAND` | 12467/5 | -8573.718 | -0.68771 | 0/5 | -15460.978 | +6887.260 | 0.897 | 0.0610/0.2255 | 0.0443/0.2470 |


The held-folio alignment null gives p=0.000976;
the directed-relation maxT p is 0.000976.
The null has 11,253 swappable and
11,209 target-variable held events.
The total-gain p-value is an upper-tail alignment diagnostic: the observed
-8912.517-bit gain is less negative
than the shuffled mean -10613.567, but it remains
far below zero.  It therefore does not reverse the failed predictive result.

## Community stability

Held-section median coassignment Jaccard is 0.2813 versus median
null q95 0.0781; held-hand is 0.2357 versus
0.0782.  Community prediction is
`NOT_POSITIVE_ALL_SPLITS`.

| axis | held | hosts | Jaccard | null q95 | p | above q95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `HELD_SECTION` | `B` | 128 | 0.2650 | 0.0779 | 0.0010 | 1 |
| `HELD_SECTION` | `C` | 128 | 0.2998 | 0.0770 | 0.0010 | 1 |
| `HELD_SECTION` | `H` | 128 | 0.1440 | 0.0799 | 0.0010 | 1 |
| `HELD_SECTION` | `P` | 128 | 0.2975 | 0.0767 | 0.0010 | 1 |
| `HELD_SECTION` | `S` | 127 | 0.2333 | 0.0802 | 0.0010 | 1 |
| `HELD_SECTION` | `T` | 128 | 0.3612 | 0.0783 | 0.0010 | 1 |
| `HELD_HAND` | `1` | 127 | 0.1687 | 0.0784 | 0.0010 | 1 |
| `HELD_HAND` | `2` | 128 | 0.2357 | 0.0793 | 0.0010 | 1 |
| `HELD_HAND` | `3` | 127 | 0.1476 | 0.0777 | 0.0010 | 1 |
| `HELD_HAND` | `5` | 128 | 0.3952 | 0.0782 | 0.0010 | 1 |
| `HELD_HAND` | `@` | 128 | 0.3275 | 0.0766 | 0.0010 | 1 |


## Strongest eligible directed relations

| source -> target | occurrences/folios | held-folio | held-section | held-hand | maxT p | label |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `H2689367b205c16ce->Ha1fce4363854ff88` | 87/33 | +70.178 | +64.974 | +75.845 | 0.0010 | `STABLE_DIRECTED_RELATION` |
| `H7175517a370b5cd2->H055eebf601617046` | 40/28 | +38.817 | +54.880 | +50.128 | 0.9337 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H174023d6298d8ced->H174023d6298d8ced` | 19/7 | +36.813 | +43.928 | +40.152 | 0.9766 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `Hacac86c0e609ca90->Hacac86c0e609ca90` | 75/39 | +36.427 | +39.934 | +47.110 | 0.9844 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H3f79bb7b435b0532->Hb13c0ea15587743a` | 24/12 | +36.301 | +41.953 | +34.614 | 0.9844 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H3f79bb7b435b0532->H174023d6298d8ced` | 23/9 | +34.711 | +43.307 | +41.351 | 0.9961 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H2689367b205c16ce->H3f79bb7b435b0532` | 49/17 | +33.983 | +40.201 | +48.036 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `Hb13c0ea15587743a->Hb13c0ea15587743a` | 18/7 | +32.847 | +36.568 | +40.405 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `Hacac86c0e609ca90->Ha1fce4363854ff88` | 74/34 | +31.053 | +30.290 | +31.391 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H2689367b205c16ce->Hab5b62081b1d305e` | 34/21 | +30.412 | +27.039 | +32.672 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H2689367b205c16ce->Hfda71671c022a8e5` | 21/14 | +26.630 | +21.357 | +29.984 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `Ha1fce4363854ff88->H2689367b205c16ce` | 64/26 | +26.094 | +26.273 | +37.503 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H0a19b4727d1fbd3a->Ha1fce4363854ff88` | 39/20 | +26.086 | +25.310 | +29.231 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H99fa2a55212dbc31->H99fa2a55212dbc31` | 13/8 | +24.765 | +30.328 | +28.243 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |
| `H0a19b4727d1fbd3a->H0a19b4727d1fbd3a` | 27/12 | +24.716 | +20.917 | +27.557 | 1.0000 | `STABLE_DIRECTION_UNCORRECTED_ONLY` |


Exact display identities are retained in the machine atlas for reproducible
joins, but neither their characters nor apparent similarity entered any model.

## Interpretation

This test concerns opaque exact-identity dependence in physical source-group
order.  It is distinct from GDT060/GDT111's suffix, DY, and edge-state models
and from GDT163/GDT164 substitution tests.  Stable directed relations found here
would remain anonymous distributional dependencies, not words or meanings.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
