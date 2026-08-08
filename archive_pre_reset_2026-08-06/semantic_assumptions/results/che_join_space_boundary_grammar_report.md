# Exact `che+R` JOIN versus `che R` SPACE grammar

Decision: **CHE_ROOT_CONDITIONED_JOIN_SPACE_GRAMMAR_CONFIRMED_PROBABILISTIC**

Both event types contain the identical canonical `BOUND_E:che` then plain `BARE:R` pair. Only the visible boundary differs. Each null shuffles JOIN/SPACE labels within its own manuscript page, preserving page composition, root counts, and the exact number of each boundary.

The decision requires root/boundary association in all six panels and at least 95% fixed-group boundary accuracy with a page-shuffle pass in every panel outside odd-ZL discovery. Balanced accuracy is retained as a diagnostic, not an absolutist gate.

Odd ZL label-blind support retains 17 roots. Its descriptive thresholds freeze JOIN-preferred roots `ckh`, `cth`, `k`, `o`, `od`, `ok`, `ol`, `or`, `os`, `ot`, `t` and SPACE-preferred roots `ai`, `aii`, `al`, `ar`, `l`.

| panel | events | MI bits | MI null max | MI p | frozen-group accuracy | balanced | prediction p |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b:odd | 445 | 0.3076 | 0.1332 | 1.99996e-05 | 0.970 | 0.852 | 1.99996e-05 |
| ZL3b:even | 455 | 0.2768 | 0.1422 | 1.99996e-05 | 0.973 | 0.833 | 1.99996e-05 |
| IT2a:odd | 447 | 0.2710 | 0.1194 | 1.99996e-05 | 0.968 | 0.833 | 1.99996e-05 |
| IT2a:even | 447 | 0.2759 | 0.1533 | 1.99996e-05 | 0.977 | 0.848 | 1.99996e-05 |
| RF1b:odd | 475 | 0.4363 | 0.1245 | 1.99996e-05 | 0.959 | 0.880 | 1.99996e-05 |
| RF1b:even | 492 | 0.5004 | 0.1524 | 1.99996e-05 | 0.973 | 0.916 | 1.99996e-05 |

## Fixed root inventory

| root | ZL odd J/S | ZL even J/S | IT odd J/S | IT even J/S | RF odd J/S | RF even J/S |
|---|---:|---:|---:|---:|---:|---:|
| `H` | 3/4 | 5/8 | 3/2 | 5/7 | 5/3 | 5/13 |
| `ai` | 0/8 | 0/5 | 0/9 | 0/5 | 0/12 | 0/9 |
| `aii` | 0/6 | 0/10 | 0/7 | 0/9 | 0/15 | 0/24 |
| `al` | 0/7 | 0/5 | 0/7 | 0/5 | 0/12 | 0/13 |
| `ar` | 0/5 | 0/4 | 0/3 | 0/4 | 0/15 | 0/11 |
| `ckh` | 20/0 | 28/0 | 21/0 | 26/0 | 21/0 | 27/0 |
| `cth` | 14/0 | 16/1 | 13/0 | 16/1 | 14/0 | 17/1 |
| `k` | 30/0 | 34/1 | 32/0 | 35/0 | 31/0 | 38/1 |
| `l` | 0/5 | 0/0 | 0/2 | 0/0 | 0/6 | 0/7 |
| `o` | 60/2 | 60/1 | 58/2 | 58/1 | 70/3 | 66/1 |
| `od` | 67/3 | 50/0 | 65/2 | 49/0 | 52/2 | 44/1 |
| `ok` | 9/0 | 5/0 | 9/0 | 6/0 | 7/0 | 5/0 |
| `ol` | 100/4 | 115/5 | 104/5 | 113/4 | 99/8 | 108/4 |
| `or` | 56/3 | 57/3 | 61/3 | 64/3 | 55/5 | 51/4 |
| `os` | 23/0 | 25/0 | 20/1 | 19/0 | 20/0 | 24/0 |
| `ot` | 4/1 | 4/1 | 3/1 | 4/1 | 6/1 | 5/1 |
| `t` | 11/0 | 12/0 | 14/0 | 12/0 | 13/0 | 12/0 |

## Interpretation

The space is grammatical information, not random handwriting noise. After the same exact `che` frame, roots such as `ol` and `od` are overwhelmingly integrated inside the word, whereas `ai`, `aii`, `al`, `ar`, and `l` overwhelmingly begin a separate word. This is compatible with a compact agglutinative, polysynthetic, classifier, or record-slot system; it is not evidence for European SVO order. The 0.833--0.916 held balanced accuracies also show that this is a strong probability, not a rule without exceptions.

For translation, `che+ol` and `che+od` should therefore be treated as bound carrier-value constructions. `che ar` or `che aii` has a different boundary class; a separate test is required before calling that adjacency a selected constituent relation. The English functions remain unknown.

Exported ZL classified events: 880. Runtime: 4.803 seconds with 50,000 page-stratified permutations per panel.
