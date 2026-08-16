# GDT166 — opaque PAGE_HOST distributional context report

Decision: **OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_NOT_TRANSFERABLE**.

## Held unordered-context prediction

| context | split | focal/folds | gain bits | bits/focal | null mean / excess | positive folds | seen | without frozen ok->y | p/max3 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `WINDOW_PM2` | `HELD_FOLIO` | 15203/92 | -8777.144 | -0.57733 | -0.61614 / +0.03881 | 0/92 | 0.920 | -8806.153 | 0.0010/0.0010 |
| `WINDOW_PM2` | `HELD_SECTION` | 15203/6 | -8678.252 | -0.57082 |  | 0/6 | 0.901 | -8705.214 |  |
| `WINDOW_PM2` | `HELD_HAND` | 15203/5 | -8529.861 | -0.56106 |  | 0/5 | 0.897 | -8565.059 |  |
| `WHOLE_LINE` | `HELD_FOLIO` | 15203/92 | -7572.887 | -0.49812 | -0.52768 / +0.02957 | 0/92 | 0.920 | -7586.584 | 0.0010/0.0010 |
| `WHOLE_LINE` | `HELD_SECTION` | 15203/6 | -7253.287 | -0.47710 |  | 0/6 | 0.901 | -7265.205 |  |
| `WHOLE_LINE` | `HELD_HAND` | 15203/5 | -7117.835 | -0.46819 |  | 0/5 | 0.897 | -7136.799 |  |
| `PARAGRAPH_BAG` | `HELD_FOLIO` | 8447/91 | -2912.618 | -0.34481 | -0.34585 / +0.00104 | 0/91 | 0.907 | -2915.540 | 0.1317/0.6741 |
| `PARAGRAPH_BAG` | `HELD_SECTION` | 8447/6 | -2645.328 | -0.31317 |  | 0/6 | 0.878 | -2647.943 |  |
| `PARAGRAPH_BAG` | `HELD_HAND` | 8447/5 | -2546.793 | -0.30150 |  | 0/5 | 0.879 | -2552.425 |  |


Every focal occurrence has total context weight one.  The frozen `ok -> y`
control was neither a feature nor a selection seed; the deletion column removes
only that focal/context mass.

## Whole-line distributional neighbor transfer

| split | predictions/folds | MRR | top1/top5 | null mean / excess | local/max3 p | swappable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HELD_FOLIO` | 446/69 | 0.2765 | 43/199 | 0.2313 / +0.0451 | 0.0010/0.0029 | 418 |
| `HELD_SECTION` | 195/6 | 0.1280 | 7/32 | 0.1071 / +0.0208 | 0.0517/0.1327 | 194 |
| `HELD_HAND` | 158/5 | 0.1167 | 4/22 | 0.1033 / +0.0135 | 0.1727/0.3502 | 158 |


Neighbor identities are exact opaque categories; PPMI profiles use only
unordered whole-line co-occurrence.  Alternate readings are not replications.

## Interpretation

This test asks whether exact PAGE_HOST identity has stable distributional
context without fixed word order.  It neither rescues GDT165's failed immediate
prediction nor assigns a lexical/code/semantic value.  Paragraph grouping is an
editorial-layout sensitivity and correlated bag members are weighted
descriptive events, not independent samples.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
