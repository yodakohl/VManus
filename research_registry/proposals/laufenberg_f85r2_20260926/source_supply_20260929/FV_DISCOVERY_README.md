# FV discovery packet: source preservation and unchanged formal views

Prepared under the root-delegated FV scope after reading the current route and [FV_DECISION.md](FV_DECISION.md). This is source preparation, not a new decoder, candidate grammar, semantic experiment or meaning result. The packet contains **discovery only**: f83r.9–17 and f83v.21–33 in ZL3b, IT2a and RF1b. The two page faces are one physical leaf and joint discovery. No additional application body or pixel was opened; their release remains root-controlled after author freeze.

## Files and frozen hashes

- [FV_DISCOVERY_PACKET.json](FV_DISCOVERY_PACKET.json): SHA256 `10f3b0f904ef0cb421f4eebcfff7069128d587ef0e5688e2ff501a812046b4d6`.
- [FV_DISCOVERY_GROUPS.tsv](FV_DISCOVERY_GROUPS.tsv): SHA256 `3f4d440c2472ba2adc30216d925e6403598cecefc8de3f283e76e8a869cff190`.
- [FV_PREPARE_DISCOVERY.py](FV_PREPARE_DISCOVERY.py): SHA256 `f1a8e3b9902f151e74f1cc61386132e3e53e20c561fa2c4dca183d53496b1b25`.

The packet embeds source/model/cache/preparer hashes and the exact selector-first command and guard receipt. Reproduction from repository root:

```sh
python3 research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/FV_PREPARE_DISCOVERY.py
```

It refuses changed source, formal code, merges, admission allowlist or prior cache. It writes only the packet and native TSV. It does not build or refresh a cache or run a legacy experiment main. The README is an explanatory artifact; its hash can be recorded in the root's final input freeze.

## Native source accounting

The source is `experiments/semantic_assumptions/results/source_separator_transcription.tsv`, SHA256 `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`. Its mixed payload goes through `./vmanus-exp query-tsv --selector locus` with exactly 22 explicit allow-values and both `f84`/`f84r` forbidden prefixes **before** any source row is decoded. No whole mixed TSV is parsed then filtered.

Projected columns are `source_group_id,edition,locus,page,section,currier,hand,code,kind,grammar_scope,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw`. The TSV is the exact guarded stdout byte projection. Source field values, raw editorial entities/unknowns, native indices, order and separator labels are unchanged. No clean fragments, preferred alternate, wrapper-stripped spelling or normalized word substitutes for a source group.

Guard receipt: 503 selected groups, 2,122 forbidden rows skipped, 112,845 other-selector rows skipped. These skip counts describe the guard's operation, not findings about excluded content.

| Complete fixed scope | ZL3b groups | IT2a groups | RF1b groups |
|---|---:|---:|---:|
| f83r.9–17 | 84 | 83 | 83 |
| f83v.21–33 | 84 | 85 | 84 |
| Total per reader | 168 | 168 | 167 |

All 503 IDs are unique and all 66 requested reader/locus cells are present, with complete consecutive within-line group indices and original group counts. Native ZL/IT paragraph starts/ends are .9/.17 and .21/.33 respectively. RF has no native paragraph flags: the packet retains its literal source flag values, marks native flag availability false, and supplies only the externally fixed same-locus scope. No RF paragraph boundary is borrowed from ZL/IT.

The canonical source's group/separator fields are preserved. This is **not** a claim of independent diplomatic full-line preservation: no native raw-line counterpart was needed or queried, and no reconstructed normalized line is substituted for an original raw line.

## Two unchanged formal views

Read GDT1051's runner, report and imported functions before import. Their top levels define constants/functions; source inventory reads and legacy writes occur inside functions or guarded main blocks. This preparer imports the unchanged GDT1051 module and calls only `load_merges`, `parse_group` and `make_chunks`. It does not call `group_rows`, the GDT012/062 inventory/fit routines or any legacy main.

GDT012 `strip_layers` followed by GDT062 `preparse` yields each eligible raw group's wrapper, residual host, DY flag, host before local O/OT framing, B3 flag, right family and internal D flag. The frozen GDT1051 rule leaves local frames at `NOT_FROZEN_FOR_NEW_INPUT`; no new source-dependent O/OT licensing or prefix rule is added. These are formal labels, not English translations or a global DY meaning.

GDT605 uses the unchanged collapse function and the existing **64** ranked merges through GDT1051's hard-chunk construction. Only native `UNCERTAIN_SMALL_SPACE` seams are joined within a line; all other seams terminate a chunk. Every chunk retains source edition/locus/group indices, literal raw joined value, collapsed view, learned units and their unchanged merge trees. Every source group points to exactly one chunk. No merge is learned here, and the two formal views are not combined into a universal morph tree.

The runner's exact `[a-z]+` eligibility rule is retained: **482** raw groups receive formal replay; **21** marked/nonlowercase groups remain `MARKED_OR_NONLOWERCASE_UNRESOLVED`, with no wrapper/host guessed. There are **488** hard chunks, **467** eligible and **21** unresolved. Marked group content and all unassigned whole/host residuals remain in the packet. Successful formal execution does not establish correct segmentation, parts of speech or meanings.

The exact runner/model/merge pins are in `input_hashes`: GDT1051 runner; GDT012 and GDT062 scripts; GDT605 `separator_crossing.py` and `gdt605_bpe_merges.tsv`. Source code is byte-unchanged.

## Exact whole-form priors without outside text

The packet supplies aggregate profiles for every **132 distinct unmarked raw whole forms** present in discovery, separately for each reader. Marked spellings are preserved as source groups but not cleaned into an inferred unmarked form for a prior.

All priors come solely from the existing read-only `experiments/semantic_assumptions/cache/word_profiles.sqlite`, SHA256 `7a3d21719f43bba7388dc90efd559cedcde5325d7d5a8916ac2bd0e9716e6664`. Its saved receipt binds the same canonical source, `tools/word_profiles.py` and the fixed 179-selector allowlist (SHA256 `f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483`). Cache admission receipt: 96,184 groups selected, 2,122 forbidden and 17,164 other-selector rows skipped. These prior data were previously exposed exploration, not independent confirmation.

The SQL returns only exact whole counts, selector dispersion, source-locus start/middle/end/single counts and aggregate section/Currier/hand/kind metadata. It does not call `profile()`/`occurrences()`, read neighbors/examples, return outside occurrence rows or expose outside bodies. Global counts include all admitted source kinds and positions; they are not a prose-only census. Selector count means text selectors, not independent physical leaves. Locus-edge positions are not sentence boundaries. Readers are alternate readings of one manuscript, never pooled.

## Preparation checks and limit

The preparer checks every frozen input, exact guarded projection schema/receipt, source-ID uniqueness, all requested cells, consecutive native indices/counts, within-line flag consistency, unchanged merge inventory and one chunk membership per group. After execution, a source-only comparison checked every packet native field/order against the saved guarded TSV, all prior position totals and global frequency lower bounds against discovery occurrences, projection hash and RF boundary nonimputation. These are accounting checks, not an independent scientific validator or semantic PASS. The independent auditor received metadata/pins only before root GO.

No candidate-specific selection, guessed glossary, application content, new admission, sealed/reserved access, registry mutation or Git action occurred. Confirmed words: **0**. Packet author access and subsequent application access remain subject to root's FV freeze/GO sequence.
