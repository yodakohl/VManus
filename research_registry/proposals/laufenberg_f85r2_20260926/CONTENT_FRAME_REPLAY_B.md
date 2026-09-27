# Independent replay of the frozen ContentFrame partial

## Literal replay

I independently reconstructed the literal packet from the owned safe projection `experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv`. The replay script compares all 473 rows by native ID, checks every available source column, independently recomputes same-locus neighbours, rebuilds the raw-form→occurrence index, checks every occurrence's assigned type/value/status against the type index, and recomputes reader/type/assignment totals. Result: **literal replay PASS**.

| Reader | Groups | Distinct types | Loci | Assigned types | Unassigned types | Assigned occurrences |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b | 156 | 115 | 24 | 47 | 68 | 80 |
| IT2a | 157 | 115 | 24 | 44 | 71 | 78 |
| RF1b | 160 | 123 | 24 | 41 | 82 | 69 |

The ZL count includes all 24 loci, including both annuli. The whole-type inventory contains 162 reader-forms: 47 assigned, 115 unassigned. ZL has 39 exploratory new whole assignments in 59 occurrences (plus the eight frozen-contract whole forms). The 51 newly assigned semantic payload units, 15 productions, five cuts and explicit same-value sets are reproduced as packet bookkeeping; this is not a minimum-description-length score. All 473 IDs and 12 native fields match; no ID, neighbour, lexical-index, or per-occurrence assignment discrepancy was found. The validator does not execute a semantic grammar.

Reproduction: from the repository root run `python research_registry/proposals/laufenberg_f85r2_20260926/CONTENT_FRAME_REPLAY_B.py`. It binds the full safe projection, contract, draft and report hashes in [the machine result](CONTENT_FRAME_REPLAY_B.json).

## Manual derivation audit

I manually checked the four authored derivation records against the unchanged first contract, the occurrence inventory, and the selected owned source intake. The local E1 derivation is well typed under its declared rules: it introduces case `C_E`, an explicit ModelCase guard and ASSERTED mode, binds a four-field FrameArgs record, constructs and postfix-binds a liver frame, then constructs a stomach SupplySpec and uses `SomeSupply` with the written LIVER recipient and bound material reference. `SomeSupply`'s definition supplies existential `Fits` restriction and `SupplyApply` over the same frame. Thus the local conditional gastric-to-liver statement is a concrete typed use. It does not establish that `C_E` is the source's first period; the separately constructed liver frame is unused, and no later derivation carries it forward.

The `S_ARGS` record has all four explicitly typed fields: `C_F`, `ORGAN_BODY`, `UNKNOWN`, and a description conjoining juice with an explicitly written adhesion-or-assimilation description relative to LIVER. It is a valid argument record, not a proposition. Its `UNKNOWN` phase field does not cancel the more specific phase predication inside the material description. No withdrawal exclusion, same-case relation to E, or case order follows from this initializer.

The `S_SCOPE_FAIL` attempt does not produce a proposition: its proposed `aG` reference has no declaration, and the `or` value is PhaseSpec where the fixed `Under` signature takes Mode. Those are failures of this written S layout. They do not prove that every possible scope construction in the frozen contract is impossible. `S_SUPPLY_FAIL` likewise explicitly attempts the direct `SupplyApply` layout; the last value `C_F` is a Case, while the signature requires a Material. This is a local type clash under that attempted application, not a global contradiction.

The additional .1 annulus attempt `daiin ol` has a Builder followed by a PhaseSpec rather than FrameArgs, so the direct `Build` application is unavailable under the frozen grammar. Since its preceding `olfor` remains unassigned, this does not rule out every possible surrounding construction. The JSON correctly keeps it as a concrete obstacle rather than a universal impossibility claim.

## Source coverage and exact limits

The packet lists 27 obligations for the selected complete III.13 P15–22 unit. Reading the owned intake against the status table, its conservatism is warranted: 24 entries are UNWRITTEN, U09 and U11 are PARTIAL, and U19 is DESCRIPTIONS_ONLY. U09's explicit model guard is not the three-period division or temporal ordering; U11's local gastric-to-liver supply lacks the source's first-period identification and setting. U19 has two descriptions in separate unlinked cases, but no stated contrast, exclusion, or same-case relation. No item is marked complete.

Consequently the report's main conclusion is accurately limited: one 26-group local E1 discourse and one 12-group argument-record initializer are achieved, but the source's required two-supplier reuse, same-owner withdrawal contrast, later two-owner phase consequence, spleen possibility, and most remaining P15–22 content are not. No whole reading or full source coverage follows. The 27-item status accounting is a manually authored source mapping; this replay checks the enumeration and reports the manual comparison, not a new translation or independent historical source judgment.

## Exposure and limits

The route, contract, author draft/report, owned safe projection, and owned source intake were read. This was a same-exposure, informed review, not a blinded or independent meaning confirmation. No raw mixed table, other target, target image, sealed/reserve leaf, or new source was accessed. No root review or result was read before this audit was frozen. Confirmed-word and semantic-confirmation capacity remain zero.
