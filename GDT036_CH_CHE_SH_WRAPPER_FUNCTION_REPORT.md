# GDT036 — ch/che/sh matched-host wrapper functions

## Outcome

**HOST_LICENSED_WRAPPERS_WITH_WEAK_SHARED_POSITIONAL_TRANSFER_REGISTER_DOMINANT**

The wrapper choice is strongly host-licensed, but exact host is not the whole explanation. The frozen panel contains **3,104** occurrences of `ch`, `che`, or `sh` over **49** recurring residual hosts and **94** physical folios. An in-sample exact-host majority chooses 63.40% correctly, and the exact-host prior gains 1166.868 held-folio bits over a global wrapper prior.

After that exact-host baseline is fixed, line position adds 40.591 bits in leave-one-folio-out evaluation and 43.468 bits on completely unseen hosts. It remains positive after additionally conditioning the baseline on section–Currier–hand register: 32.713/41.931 LOFO/LOHO bits. Previous-state context retains 20.549/3.945 adjusted bits; next-state context retains 7.532/18.716. The strongest raw predictor is register (`section|Currier|hand`), at 146.712/272.051 bits, but those metadata are historically entangled and cannot identify a single cause.

Therefore `ch`/`che`/`sh` are not well described as arbitrary spelling variants attached independently inside each core. They behave as host-licensed renderers with weaker shared positional and neighbouring-state preferences. However, no non-metadata feature clears the register-adjusted maxT threshold (field position is closest at 0.0512), so a stable universal wrapper function is **not established**. This is an exploratory constructional lead only; the experiment does not identify what any preference does or means.

## Design

- Source: the f84-free, all-reading-agreeing physical/manual group inventory from GDT016.
- Candidate host: remove exactly one observed prefix in {`ch`,`che`,`sh`} and retain the exact residual string.
- Capacity rule fixed before scoring: at least 10 rows, at least 2 wrapper types, and at least 3 physical folios.
- Primary association: conditional mutual information given exact host, tested with 5,000 exact-host-stratified wrapper permutations and maxT across 12 declared feature families.
- Register-adjusted control: each of the eight non-metadata features is also tested by permutation inside exact `host × register` cells, and held prediction is rescored beyond host×register or register-only baselines.
- Transfer: a shared multiplicative feature effect is trained outside one physical folio at a time and scored beyond an exact-host prior; a stricter unseen-host pass holds out every occurrence of one residual host and scores beyond the global wrapper prior.
- Uncertainty: this is exploratory YOLO model selection. The shrinkage constants are fixed (`alpha=0.5`, `lambda=5.0`), but they are a compact diagnostic model, not a globally optimal grammar.

## Feature atlas

| Feature | CMI bits/row | local p | maxT p | LOFO gain bits | LOHO gain bits | Classification |
|---|---:|---:|---:|---:|---:|---|
| section | 0.153087 | 0.000200 | 0.000200 | 152.900 | 249.486 | REGISTER_SIGNAL_CONFOUNDED |
| register | 0.207231 | 0.000200 | 0.000200 | 146.712 | 272.051 | REGISTER_SIGNAL_CONFOUNDED |
| hand | 0.096073 | 0.000200 | 0.000200 | 54.775 | 175.735 | REGISTER_SIGNAL_CONFOUNDED |
| currier | 0.053118 | 0.000200 | 0.000200 | 49.366 | 160.750 | REGISTER_SIGNAL_CONFOUNDED |
| line_position | 0.105168 | 0.000600 | 0.002999 | 40.591 | 43.468 | REGISTER_ADJUSTED_WEAK_TRANSFER |
| previous_state | 0.192158 | 0.003199 | 0.042591 | 25.546 | 11.852 | REGISTER_ADJUSTED_WEAK_TRANSFER |
| field_position | 0.067918 | 0.000400 | 0.000400 | 18.015 | 24.450 | REGISTER_ADJUSTED_WEAK_TRANSFER |
| field_index | 0.048492 | 0.065387 | 0.444111 | 12.426 | 22.296 | FOLIO_TRANSFER_ONLY |
| next_state | 0.169723 | 0.096181 | 0.598280 | 11.048 | 54.941 | REGISTER_ADJUSTED_WEAK_TRANSFER |
| dy_adjacency | 0.050654 | 0.188362 | 0.824835 | -0.253 | 10.492 | UNSEEN_HOST_ONLY |
| own_dy_closure | 0.010884 | 0.000400 | 0.000600 | -0.594 | 12.677 | UNSEEN_HOST_ONLY |
| record_state | 0.010884 | 0.000400 | 0.000600 | -0.800 | -292.698 | NO_TRANSFER_SIGNAL |

## Register-adjusted formal-feature transfer

| Feature | adjusted CMI | adjusted local p | adjusted maxT p | adjusted LOFO bits | adjusted LOHO bits |
|---|---:|---:|---:|---:|---:|
| line_position | 0.192805 | 0.081584 | 0.423115 | 32.713 | 41.931 |
| previous_state | 0.319406 | 0.085983 | 0.429714 | 20.549 | 3.945 |
| field_position | 0.123357 | 0.008198 | 0.051190 | 13.831 | 68.953 |
| next_state | 0.303715 | 0.622076 | 0.993401 | 7.532 | 18.716 |
| field_index | 0.107195 | 0.157968 | 0.663467 | 3.648 | -10.179 |
| own_dy_closure | 0.016506 | 0.001000 | 0.002000 | -0.269 | 61.275 |
| record_state | 0.016506 | 0.001000 | 0.002000 | -0.912 | -191.522 |
| dy_adjacency | 0.101463 | 0.474505 | 0.973405 | -4.422 | -4.190 |

## Largest exact-host-adjusted descriptive residuals

| Feature=value | Wrapper | Observed | Host-conditioned expected | Residual |
|---|---|---:|---:|---:|
| section=H | che | 195 | 330.67 | -135.67 |
| section=H | ch | 585 | 478.74 | +106.26 |
| register=H|A|1 | che | 119 | 225.16 | -106.16 |
| section=S | che | 420 | 326.74 | +93.26 |
| hand=1 | che | 178 | 269.56 | -91.56 |
| currier=A | che | 192 | 282.24 | -90.24 |
| currier=B | che | 808 | 720.59 | +87.41 |
| register=S|B|3 | che | 386 | 304.28 | +81.72 |
| register=H|A|1 | ch | 481 | 404.85 | +76.15 |
| hand=1 | ch | 527 | 457.15 | +69.85 |
| currier=A | ch | 543 | 474.53 | +68.47 |
| hand=3 | che | 409 | 342.65 | +66.35 |

## Strongest non-metadata constructional residuals

| Feature=value | Wrapper | Observed | Host-conditioned expected | Residual |
|---|---|---:|---:|---:|
| field_index=1 | che | 578 | 625.32 | -47.32 |
| line_position=MIDDLE | ch | 411 | 369.18 | +41.82 |
| line_position=FIRST | sh | 114 | 73.79 | +40.21 |
| field_position=FIELD_START | ch | 115 | 153.61 | -38.61 |
| previous_state=BOS | sh | 118 | 79.68 | +38.32 |
| field_position=FIELD_START | sh | 158 | 123.16 | +34.84 |
| dy_adjacency=PREV0_NEXT0 | ch | 844 | 814.38 | +29.62 |
| field_index=1 | sh | 789 | 760.23 | +28.77 |
| dy_adjacency=PREV0_NEXT0 | che | 739 | 766.55 | -27.55 |
| line_position=FIRST | ch | 40 | 66.50 | -26.50 |
| field_index=2 | sh | 177 | 203.35 | -26.35 |
| previous_state=BOS | ch | 47 | 72.11 | -25.11 |
| field_index=3 | che | 195 | 170.18 | +24.82 |
| next_state=Q_OUTER_STATE | sh | 176 | 152.72 | +23.28 |
| line_position=EARLY | ch | 285 | 308.23 | -23.23 |


These residuals describe the fitted panel; the held-folio and held-host gains above are the relevant transfer diagnostics. One-sided or rare contexts remain observations rather than automatic failures.

## What this does and does not establish

The reusable signal is principally **where a wrapped host occurs** and **which record state precedes or follows it**. Direct association with the group's own anonymous record state is weak; DY adjacency is also substantially weaker than the positional and register effects. That pattern is compatible with a wrapper layer selecting constructional renderers around already licensed hosts, but it does not distinguish grammar, scribal convention, technical layout, or register-conditioned orthography.

Currier, hand, section, and combined register effects are reported separately. They must not be read as four independent causes, and the all-Herbal hand/Currier coupling remains a known confound. Exact-host preferences remain large, so this result also rejects a freely interchangeable universal prefix slot.

No meanings, morphemes, sounds, parts of speech, languages, plaintext, or translations were inferred. **f84r was not opened, retained, queried, joined, or scored.**
