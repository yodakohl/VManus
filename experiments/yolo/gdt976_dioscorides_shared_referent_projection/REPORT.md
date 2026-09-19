# GDT976: shared name-code projection leaves many concrete partial bindings

**Primary decision: PARTIAL_SHARED_REFERENT_BINDINGS_REMAIN.** The unchanged GDT963 source model admits 8,990 partial IRIS/XIPHION code-and-page-pair bindings under the new necessary projection. They use 1,320 distinct ordered code-value pairs. No code pair or plant name is selected; the complete model remains unresolved.

Registration 5721dc288 was publicly pushed before target execution, confirmed 15:37:19 UTC on 15 September 2026. The primary run completed in 2.09 seconds. Source and target exposure predates the test; this is not independent confirmation. No decoder, source atom, alias, target boundary or code-length rule was changed.

## All page pairs and all surviving predictions

| IT2a I.1 / IV.20 page-pair outcome | Count |
|---|---:|
| Different physical leaves, no shared-name projection | 1,111 |
| At least one shared-name projection and eligible Acorus/Meum completion | 2,124 |
| Same physical leaf, excluded by the fixed contract | 65 |
| All ordered candidate page pairs | 3,300 |

[PAGE_PAIRS.tsv](artifacts/PAGE_PAIRS.tsv) lists all 3,300 outcomes. [CANDIDATE_PREDICTIONS.tsv](artifacts/CANDIDATE_PREDICTIONS.tsv) lists every one of the 8,990 surviving partial bindings, both exact code strings, their positions in both linked descriptions, every supported Acorus page and the factored number of Meum completions. No row is retained only because its proposed name looks attractive. [CODE_CLASSES.tsv](artifacts/CODE_CLASSES.tsv) groups identical code-value pairs; grouping does not prefer a meaning.

| Source name under the unchanged hypothesis | Different possible code strings | Length range in EVA transcription characters | Every shortest alternative |
|---|---:|---|---|
| IRIS | 52 | 1–6 | c, k, o, p, t |
| XIPHION | 138 | 1–8 | c, f, k, o, p, t |

Not every cross-product of these two lists is allowed: the 1,320 surviving pairs retain prefix-incomparability, source-position obligations and common supporting pages. Nor are these presumed spoken names or identified Voynich words. A code can cross written group boundaries under the old GDT963 contract.

The factored candidate set contains 520,683 code/Iris-page/Xiphion-page/Acorus-page combinations and 49,581,858 extensions by a distinct Meum page. These counts include distinct code pairs on the same page assignments. They are **not** that many new experiments, distinct translations, independent observations or uniquely distinct four-page tuples. Full text and physical-leaf metadata remain in DOMAINS.json; ACORUS_SUPPORT.json.gz preserves both required occurrences for every cached value. Given one candidate, all allowed Meum pages are exactly its I.3 domain excluding its three already used leaves.

## Concrete consequence and retained limits

The frozen source requires the SAME IRIS value at the beginning of I.1, after 6 omitted atoms and again after 92 intervening omitted atoms in I.2, and inside IV.20. XIPHION likewise begins IV.20 and occurs within I.1. All minimum intervening/trailing lengths follow from the complete source streams. A merely nearby matching substring is insufficient. The independent matching proof uses complete strings and nonempty omitted occurrences; no favorable fragment is cut out.

This fixes only **six source-atom occurrences out of 613** across the four complete records, all conditionally on the unchanged copied-content hypothesis. The other 607 occurrences still require a common nonempty prefix-free code in the full model. Their equality and prefix constraints were relaxed here; a partial binding can fail them. Additional occurrences of a selected string inside omitted codewords are permitted, so absence/count-equality was not silently assumed. No whole paragraph or complete source code has been read by this projection.

GDT963 had 33/101/101/100 locally non-excluded IT2a pages for I.1/I.2/I.3/IV.20 across 58 physical leaves. The new test retains those initial domains. All 357 older frames are accounted for: 103 literal, 254 source-unknown. ZL3b has no literal pages; RF1b has two and no surviving I.1 domain. Their lack of a four-leaf reading is capacity, not semantic evidence against them. Source-unknown frames are not refuted. Alternate transcriptions remain readings of one manuscript.

GDT963's original BOUNDED_SEARCH_UNRESOLVED result is unchanged. The new projection supplies actual necessary exclusions and explicit candidate sets; it neither rescues a failed code nor establishes a full GDT963 witness. It does not identify a plant drawing, the comparative axis, a translation language, or a word meaning. All pages were already exposed. Independent confirmation capacity 0; f84/f84r and reserves remain closed. No significance or scored relation packet.

## Research decision

Retain all 1,320 code-value classes and 8,990 code/page rows as **partial hypotheses only**. Repeated-name consistency alone leaves too much freedom to choose one. Do not rank by restart agreement, occurrence count or familiar-looking syllables; do not start another complete solver run merely because this relaxation has solutions.

A distinct possible next consequence is to add the unchanged source's shared LEAF and comparative BROAD atoms across the same complete records, with all existing name bindings retained. That requires a separate bounded declaration and must keep every current candidate and every source unknown. It could test common content beyond the repeated names without inventing a new paragraph header or adopting old plant glosses. IDEA357's proposed jointly learned constituent grammar itself remains unexecuted, and the paired-root/scale/ownership counterexamples remain intact.

The inclusive work unit began 15:16 UTC with source/primary review and targeted duplicate checks; its checkpoint is 15:46 UTC. The 30-minute inclusive budget was exceeded during validator correction and closure; no further scientific search or scope expansion followed the checkpoint. Publication is required closure, not claimed additional manuscript progress. Confirmed translated words remain 0.

## Validation correction and reproduction

The registered `src/validate.py` remains byte-for-byte intact. Its full run was interrupted after inspection identified incorrect aggregation of same-leaf pairs, pre-completion pair counts and output field names, as well as an impractical unpruned traversal. The interruption is retained in [VALIDATION_INITIAL.json](artifacts/VALIDATION_INITIAL.json). This is a validator defect, not a failed target prediction or permission to alter the hypothesis.

The separate candidate engine in `src/validate_projection.py` enumerates substring occurrence caps and explicit qualifying positions. Before the output-format corrections it already reproduced all 8,990 candidate rows and 1,320 code classes exactly. Root subsequently corrected only the validator's output comparisons: pair counts after all leaf/completion conditions, the actual result schema, and the cache's successful-support view. This last cache contains only tested prefixes with complete two-occurrence witnesses; the independent diagnostic support table also includes empty-position failures and more prefixes. The comparison verifies every saved entry and coverage of every surviving candidate value. Both intervening FAIL receipts are retained in `VALIDATION_CORRECTIVE_FIRST.json` and `VALIDATION_CORRECTIVE_SECOND.json`; the final cache correction has a before/after code hash receipt. No primary runner, source, preregistration, prediction table or target result was repaired.

The corrected validator is post-registration engineering and is disclosed as such. Its independently implemented enumeration is a calculation cross-check, not blinded scientific replication or independent meaning evidence. The final validation receipt is [VALIDATION.json](artifacts/VALIDATION.json). Reproduce the unchanged primary calculation and the disclosed check with:

```sh
python3 experiments/yolo/gdt976_dioscorides_shared_referent_projection/src/run.py
python3 experiments/yolo/gdt976_dioscorides_shared_referent_projection/src/validate_projection.py --full
```

`src/finalize.py` preserves the original registered binder and selects the corrected validator in the final manifest. The original README and registered validation source are not silently rewritten.

Final corrected validation: **PASS** for all nine artifact/domain checks, source projection, fixture and all 19 registration hashes. Every primary candidate, prediction-table cell, page-pair outcome and code-class count is reproduced. Validation completed on 15 September; publication closure resumed on 19 September 2026 after an interruption. The intervening calendar time is not reported as active research time.

Closure checks: `ideas check` and `context check` PASS. The repository-wide `vmanus-exp check --all` still reports exactly eight pre-existing failures: seven unbound GDT600 files and one GDT953 large-artifact justification. No GDT976 failure is reported; this is not a global repository PASS.

Source-only next-step check on 19 September: unchanged SOURCE.json places LEAF at zero-based atom positions I.1:2, I.2:3, I.3:15, IV.20:11, and BROAD at I.1:11, I.2:8, IV.20:21. Adding those two fixed shared values would add seven source occurrences, for thirteen of 613 total, and link the previously name-free I.3 record. This is a proposed necessary constraint, not an executed follow-up or evidence that leaf/breadth meanings occur in Voynich. Even a severe candidate reduction would not itself establish meaning; a useful survivor must support further shared content without repairs and ultimately a coherent complete reading.
