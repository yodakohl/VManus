# GDT1166 — fixed natural shared-sign pipeline failed

**Registered decision: FAIL_SOURCE_CANDIDATE_CONTROL.** The variable-omission arm recovered no additional primary truth over the constant arm. This is a historical-source result, not a Voynich translation. No target text, reserve or sealed page was used.

Public preregistration: `0de43e794b8225d2d0482d218c8ecd9d2ed7ec5f`, pushed before FIT_RELEASE. The source projection, split, search, thresholds and scorer remained unchanged throughout the real run. Source whitespace was preserved verbatim; the prepublication source excerpt exposure is disclosed in METHOD.md.

## Complete registered outcome

Original B4 yielded 130 discovery and138 held records on disjoint physical-leaf halves, plus one unused bridge. Every one of10,118 held occurrences /1,980 written types was predicted. The primary set contains198 known novel abbreviated types K and7 unknown abbreviated occurrences U. U is seven zero-credit obligations, not seven asserted lexical types.

| Frozen arm | Top1 credit /205 | Top5 credit /205 | Conservative Top5 | Known-type diagnostic |
|---|---:|---:|---:|---:|
| Literal L |58|58|28.293%|29.293%|
| Constant C |66|66|32.195%|33.333%|
| Variable V |66|66|32.195%|33.333%|

K>=20 passes. V>=50%, V−L>=10points and V−C>=10points all fail: the gains are3.902 and0points. Primary occurrence-weighted diagnostics over261 occurrences are L28.352%, C/V33.716%; these do not replace the registered type-based endpoint.

The [complete205-row table](CANDIDATE_TABLE.md) shows every primary obligation, exact source reference and all three Top5 lists. Machine-readable details are in `artifacts/CANDIDATE_TABLE.tsv`; full candidate rankings for all held types are in `PREDICTIONS.json.gz`, with all held position outcomes in `OCCURRENCE_RESULTS.json.gz`. No favorable individual occurrence was selected for the decision.

All three arms select saved panel15. C/V select atom6; C chooses an empty residual. Each selected score has one winner under the fixed tolerance. That uniqueness is only finite-score selection, not decipherment uniqueness. The common32-state heuristic panel is not an exhaustive alphabet search. Full1,487,637 candidate scores and selection ties are retained.

## Errors and post-lock diagnosis

There are16 primary types with unfit atoms. L/C/V have129/123/121 empty primary candidate lists. The known primary occurrences include123 reference-OOV instances; they remain errors. Seven primary types have different C/V Top5 lists, but every one of198 types has equal C/V truth credit. The variable arm's better training score did not yield added held recovery.

After prediction/scoring locks, the preparation key identifies atom6 as combining diaeresis U+0308. The actual overline U+0305 is atom62 and is fit-supported; all selected keys render it literally as `e`. Thus this run did not select the shared abbreviation overline as its variable missing-letter sign. This is descriptive source-key evidence, not a Voynich sign assignment.

The post-lock reference oracle ceiling is93/205 =45.366%, even with perfect reference-word selection. The fixed50% absolute gate was therefore unreachable with this exact supplied vocabulary. This was not used to select a subset, alter the threshold or rerun the fit. The registered K capacity gate still passes and the full-pipeline failure stands. Crucially, this failure cannot isolate or disprove variable abbreviation as a historical mechanism: reference coverage itself limits the task. The independent comparative observation—no V gain over C—also remains unchanged.

## Validation, limits and next decision

Independent frozen code recomputed all1,487,637 finite objectives (maximum absolute discrepancy4.22e−10), all32 saved surrogate scores, contract domains and selection ties. It checked all5,940 held type/arm rankings, compatibility, cut-off ties,10,118 occurrence rows, K/U partition, table accounting and endpoint arithmetic. Separate posthoc validation confirmed the reference ceiling and C/V comparison. See `FINITE_VALIDATION.json`, `SCORE_VALIDATION.json`, and `DIAGNOSTIC_VALIDATION.json`.

The complete XML projection and optimizer trajectories were not independently replayed; preparation has synthetic fixtures and byte-identical replay. Source exposure and related comparison books prevent analyst-blind or independent-tradition claims. The procedure assumes supplied word boundaries and an expanded reference vocabulary. No whole-search countercontrol supplies significance or calibrated semantic probabilities.

**Decision:** close this fixed source candidate pipeline. Do not promote it to a Voynich decoder or automatically change the optimizer, vocabulary, channel or thresholds. GDT1160's conditional supervised gain, GDT1164's failed ranking and GDT1165's invalid result remain unchanged. A later content consumer needs actual complete candidate readings and a distinct justified constraint; this source-only run supplies no Voynich reading. Confirmed translated Voynich words remain0.

The actual fit took roughly20 seconds; preparation and independent validation account for most work. Completion occurs within the final execution selection's21:10UTC checkpoint. The user's ten-hour work block continues to at least04October03:47:39UTC; this report is not its completion.
