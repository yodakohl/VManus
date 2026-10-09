# GDT1198 — daldy contexts: recurring form, unresolved inner boundaries

Decision: **DESCRIPTIVE_CONTEXTS_NO_SEMANTIC_SELECTION**. The complete exact-form concordance is source-validated. It supports taking the recurring sequence seriously while retaining concrete segmentation disagreements. No morpheme boundary, meaning or grammatical function is selected. This is a targeted review of exposed material, not a new manuscript discovery or an independent confirmation.

## Observations that change the construction question

The admitted profile has 17/16/8 exact standalone `daldy` groups in ZL3b/IT2a/RF1b. Their union contains **19 physical text loci**, inspected in all three readings: 57 complete reader-lines. The readings are alternatives, not 41 independent observations. The larger difference in exact counts is substantially a difference of transcription spelling/annotation and segmentation; it is not evidence that one reader saw the word on nine fewer physical locations.

In the table, `|` denotes DEFINITE_SPACE and `~` UNCERTAIN_SMALL_SPACE. These are transcription flags, not new image judgments.

| Locus | ZL3b | IT2a | RF1b |
|---|---|---|---|
| f103r.1, line end | `daldy` | `dal | dy` | `dal ~ @152;y` |
| f75v.22, entire label locus | `daldy` | `dal | dy` | `daldy` |
| f89v1.13, line end | `daldy` | `dal | dy` | `dal ~ dy` |
| f89v1.14, line end | `daldaldy` | `dal | daldy` | `@152;al ~ daldy` |
| f45r.10, local sequence | `kair | daldy | dalor | cheol | dal` | same literal sequence | same literal sequence |

Thus ZL and IT preserve the same concatenated local letters across three `daldy`/`dal dy` disagreements and one `daldaldy`/`dal daldy` disagreement. RF agrees literally in some cases and uses explicitly different entity spellings in others. `@152;` is retained as written, never converted to `d`. On f89v1.14, the earlier ZL `dal ~ chdy` boundary is also uncertain; it must not be silently rendered as a definite space.

The f45r.10 sequence is reader-stable at the relevant groups and separators. It puts standalone `dal` near `daldy` and `dalor` in the same physical line. That is an actual local structural expectation for a proposed system, but the repeated substring does not itself prove that all three carry one reusable meaning.

The f89v1.13–20 paragraph was already read completely in September: see `research_registry/proposals/laufenberg_f85r2_20260926/F89V1_OKOAIIN_CONTEXT_RESULT_20260927.md`. The current work checks the daldy boundary cases directly; it does not claim fresh exposure or revive the old solar hypothesis. GDT852's image-supported spacing contrast concerns f75v.44, not these labels; GDT1060's unresolved okal-dy image remains unresolved and cannot adjudicate a daldy seam.

## Full reader accounting

Each cell below classifies the relevant span at the same 19 locus-union entries. The category labels are transcription bookkeeping, not physical alignments or normalized word identities.

| Reading | Exact standalone daldy | Literal dal dy | Split with entity | Entity-bearing single group | Correction annotation | Embedded in longer group |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b | 17 | 0 | 0 | 0 | 1 | 1 |
| IT2a | 16 | 3 | 0 | 0 | 0 | 0 |
| RF1b | 8 | 1 | 1 | 9 | 0 | 0 |

The annotation is `daldy<!corr?>` at f85r1.13; the embedded case is `daldaldy` at f89v1.14. All are preserved in [BOUNDARY_REVIEW.json](artifacts/BOUNDARY_REVIEW.json) and the full [CONTEXT_PACKET.json](artifacts/CONTEXT_PACKET.json). These counts do not replace the original exact standalone counts.

## Similar use: what the immediate contexts do and do not show

The predefined exact-neighbour census finds **zero shared complete left-and-right frames** between distinct members of `{daldy,daly,dal}`, separately in each reader. Both outside groups and their literal separators had to match, and physical line edges were excluded. This is sparse exact-context evidence, not rejection of morphology or all contextual similarity.

There are weaker one-sided similarities, visible in the saved neighbour lists: ZL has `qokedy` before both daldy and daly, and `chedy` after both daldy and dal. Other left neighbours overlap with the much more frequent dal. Their frequency and selection history prevent treating such overlap as a discovered grammatical substitution. No relation packet is scored and no significance or calibrated probability is reported.

The new construction should therefore start from stable observable strings and explicitly qualify uncertain boundaries. It may not assume that daly and daldy are known cases, tenses, quantities or different inflections of a translated word. `dal+{empty,y,dy}`, `da+{l,ly,ldy}` and learned whole forms are still alternative formal descriptions. GDT608's directed part structure plus whole-form residual remains the positive baseline, while GDT788's component-transfer limits and GDT916's failed new-pair generalization remain binding.

## Validation and scope

The runner uses the existing guarded, read-only word-profile cache. Before extraction its contract, runner, profile implementation and prior profile artifact were hashed. The separately written validator imports no runner code and queries the original mixed source only through `vmanus-exp query-tsv`, explicitly selecting the admitted target loci before materialization. It rechecks source IDs, raw strings, separators, complete windows/lines, counts, frame absence and three literal join/split comparisons. Completeness is checked against the frozen existing exact-profile totals. The validator was written after exploratory extraction, not presented as a pre-output or blinded test.

Validation PASS covers 1,300 exact occurrences across the five requested forms/readers, 57 daldy reader-lines and 57 boundary bookkeeping entries. This count is not 1,300 independent scientific tests. The guarded query selected 12,738 rows from only those admitted loci and rejected sealed rows before materialization. One bounded assistant independently inspected the five table locations and confirmed the literal/uncertain-boundary distinctions. It knew the question and inspected the same transcription packet; this is not an independent physical witness or human palaeographic validation.

No image, OCR, new source, native word meaning or reserve was used. f84/f84r remain sealed, f116v unadmitted. GDT1197 remains unexecuted;1196 and other earlier failed models remain failed. Reproduce extraction and source validation with the manifest commands. The validator also consumes the explicitly post-extraction manual bookkeeping file. Preparation through validation occupied approximately 10:08–10:18 UTC on 5 October; reporting and local closure are within the 10:38 budget. Local construction checkpoint; no commit or push.

## Next discriminating action

Before treating the f75v.22 split as a writing rule, check the actual internal clearance on the already admitted exact f75v photograph, with the same-spelled f75v.32 label as a fixed comparison. This requires its own declared image question and exact existing scope, not a reinterpretation of the present transcription-only result. A clear difference could constrain spacing practice; unresolved spacing must remain unresolved. Either result alone would still not translate dal or dy. No automatic universal-suffix decoder or random character-state fit follows.
