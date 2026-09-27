# Independent RAW566 literal and local-type replay

## Replay result

The independent script reconstructs the frozen scope from only the owned GDT1042 `guarded_projection.tsv` and the frozen author draft. It does not import the author’s runner, parse full source files, or implement a semantic executor. Run it from the repository root with:

```sh
python research_registry/proposals/laufenberg_f85r2_20260926/MEDIATED_COLD_REPLAY_B.py
```

The script filters S.12–17 and W.18–23 from the safe projection, then reconstructs each physical line by the source’s `LINE_START`/`LINE_END` separators. All 186 IDs, source columns, complete line strings, within-line positions, and exact assignment flags match the frozen draft. The outside list independently replays as the exact 28 projection rows outside those selected loci whose raw whole form is in the draft’s fixed lexicon; all IDs, source fields, line strings and assignment flags match.

| Reader | Selected groups | Assigned exact whole forms | Unassigned rows | Outside assigned rows |
|---|---:|---:|---:|---:|
| ZL3b | 62 | 21 | 41 | 9 |
| IT2a | 61 | 20 | 41 | 10 |
| RF1b | 63 | 20 | 43 | 9 |
| **Total** | **186** | **61** | **125** | **28** |

The outside rows are retained extension obligations, not contextually completed cases. The machine-readable result includes each exact qod/bare-root occurrence and its full literal line.

## Independent spelling and type audit

Across all 473 rows in the owned projection, exact whole-form counting gives `aiin` 16, `ain` 6, `qodaiin` 5, and `qodain` 3. The complete qod-initial census is `qodaiin` 5, `qodain` 3, and `qodar` 2. Only the first two have licensed cuts in this candidate; the two E.10 `qodar` rows remain opaque and unassigned. The marked RF form `qo@152;ain` is not equated with `qodain`; IT’s `aiinog` is not split into `aiin` plus `og`. Every exact qod/bare-root occurrence remains represented literally in the result JSON.

The three ZL qod applications replay their proposed ordered signatures:

- S.16 G002–G004: `qodaiin odain an`. Under the authored cut, `aiin` contributes a `ResourceAspect` argument, followed by a `Condition`; the whole reference types fit those slots, but neither prior typed referent nor a written Case/owner/time frame has been supplied.
- W.19 G002–G005: `qodain chckhy ykeedy chedy`. The candidate argument order is `Location, Carrier, Condition`; the three whole-reference types fit, but all referents and the Case remain unresolved.
- W.21 G005 through W.22 G002: `qodaiin los ar`. The line boundary is crossed inside W, which the draft permits. The ordered `ResourceAspect, Condition` types fit; no referents or Case are completed, and C4 cannot import the S nutrient aspect across the selected paragraph boundary.

The complete IT S.16 run after the compound is `qodain odain an chey`. Since `qodain` inherits two `ain` arguments and adds its Condition argument, the expected order is `Location, Carrier, Condition`. The first actual argument `odain` is fixed `Reference(ResourceAspect)`, not `Location`; the second `an` is `Reference(Condition)`, not `Carrier`; and third `chey` is unassigned rather than a resolved Condition reference. The first mismatch is already sufficient to reject this exact application; the second is a separate fixed-slot mismatch in the same one application, not an independent counterexample. No aspect-to-location cast is licensed. This rejects that exact candidate under IT; it does not reject all mediated interpretations. RF W.19’s marked `qo@152;ain` stays unassigned and does not receive the ZL/IT compound analysis.

The five selected bare-root occurrences also match the draft’s stated open obligations. S.14 `aiin` has unknown possible adjacent argument forms on both sides. S.17 terminal `ain` has no right-side arguments, leaving only unassigned `orar oldar` as a possible postfix pair. At W.20, `aiin` may take unknown `ckhed[a:y]` on the right, but the fixed `or:ConditionKind` cannot serve as its `ResourceAspect` on the left; `ain` may take unknown `olchey qokal` on its right, while postfix would take `or:ConditionKind` where `Carrier` is required. W.22 `aiin` may take unknown `og` on its right, while the preceding `or` again conflicts with its required aspect type. These are unsatisfied or unresolved arguments, not contradictions, because the neighboring whole forms remain unassigned.

## Case ownership, guards, and content limit

No written Case constructor, case owner/time, Condition instance from `or:COLD_KIND`, or ResourceAspect owner appears in this partial. The `an`, `chedy`, and `ar` hypotheses are typed backward references to a prior Condition; no explicit Condition instance has been provided in a complete Case. Likewise, `odain` and `los` are typed prior ResourceAspect references, not themselves the aspect or its bearer. This leaves K1–K3 as open typed applications, not complete propositions.

The draft does not silently convert its cold kind to a Condition, a Carrier to a ResourceAspect, or a reference type to an instantiated entity. Nor does it claim that `INHIBITS` has succeeded or that a downstream operation follows. The nutrient aspect’s owner/heat-dissolution link, support for retention and due-alteration condition remain missing. For wind, its relation to the available aspect, escape depletion, support for expulsion, thickening, and strong-wind guard remain missing. Accordingly, no PATH is derived and no completed source case or block is claimed.

## Verdict and reproducibility

Literal bookkeeping and complete line-context replay pass. The partial imposes the advertised reusable qod argument-order constraint; it also has the declared IT S.16 type failure. Unresolved antecedents, cases, owners, aspect relations and guards are missing definitions/input, not newly discovered contradictions. The partial remains incomplete exactly as reported. No meanings, rules, aliases, source claims, images, or extra corpus rows were added.

The script and JSON bind the current projection and frozen draft hashes directly. The source paths are `experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/guarded_projection.tsv` and `research_registry/proposals/laufenberg_f85r2_20260926/MEDIATED_COLD_AUTHOR_DRAFT.json`; the JSON records their hashes and the exact row-level replay.
