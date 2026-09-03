# GDT768 artifacts

The twelve result files are generated from the already admitted guarded cache
by the first command; the validator writes its compact audit with the second:

```bash
python3 experiments/yolo/gdt768_chor_shor_part_identity_tournament/src/run.py
python3 experiments/yolo/gdt768_chor_shor_part_identity_tournament/src/validate.py
```

The tables retain audit detail because the central result depends on knowing
which complete donor forms disappear under ED0/ED1/ED2 family ablation. No
artifact contains a confirmed translation or productive component value.

| artifact | rows | purpose |
|---|---:|---|
| `ANCHOR_404_OCCURRENCE_ATLAS.tsv` | 404 | every exact `chor`, `shor`, `cthy`, `dair`, `kooiin`, and `koaiin` occurrence, with line geometry and donor views for three scopes × three radii |
| `MULTI_ANCHOR_33_LINE_ATLAS.tsv` | 33 | complete lines containing at least two distinct anchors; 26 pages represented |
| `ANCHOR_15_PAIR_SUMMARY.tsv` | 15 | all unordered anchor-pair line, page, order, and direct-adjacency counts |
| `ANCHOR_6X3X3_FAMILY_ABLATION.tsv` | 54 | six anchors × three radii × three scopes, including feature and exact donor-surface counts |
| `ANCHOR_6_ROLE_GEOMETRY.tsv` | 6 | line/paragraph position, section, language, hand, and multi-anchor geometry per complete whole |
| `MODEL_OBSERVED_METRICS.tsv` | 63 | transparent CF01–CF13 observations; includes eight donor-derived CF04 rows and labels CF07 as `BROAD_VALUE_AMOUNT_PROXY` |
| `MODEL_5_FEATURE_EVIDENCE.tsv` | 65 | every one of 13 features against each model, including weights, bounded match, evidence, and counterevidence |
| `MODEL_5_SCOREBOARD.tsv` | 5 | final ranking, minimum-support result, replacement rule, and decision for M01–M05 |
| `GDT768_6_WORKING_DICTIONARY.tsv` | 6 | portable and concrete defaults, rivals, confidence, evidence, and replacement guard for each anchor |
| `TWELVE_COMPLETE_LINE_READER.tsv` | 94 | one row per token across twelve complete lines; full line and rendered sequence repeated for auditability |
| `HISTORICAL_PART_REGISTER_READER.md` | — | human-readable scoreboard, six-word dictionary, and all twelve complete working readings |
| `RESULT.json` | — | compact machine-readable scope, count, guard, model, reader, and claim-ceiling summary |
| `VALIDATION.json` | — | 53,504-check PASS with byte replay of all twelve declared builder outputs |

Key invariants:

- 404 occurrences / 135 pages / 350 loci;
- 33 multi-anchor lines / 26 pages;
- 94 tokens / 12 complete lines;
- 54 GDT754 source-composed target-context exposures blocked;
- M02 = M03 = 0.820437 and both directional minimum flags are zero;
- M01 = 0.644178, M04 = 0.631987, M05 = 0.132523;
- every identity-credit, confirmed-lexeme, and component-export field is zero;
- no new page or image, and no `f84`/`f84r` access.

The corresponding input schemas and declared priors are in `../src/*.tsv`.
`../src/model_scoring.py` is read-only; artifact serialization belongs solely
to `../src/run.py`.
