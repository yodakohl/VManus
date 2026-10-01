# FW: complete previous/current discovery paragraphs

Prepared after root GO for source preparation under [FW_DECISION.md](FW_DECISION.md), after reading the current route. This is a separate source packet from FV. No FV author/draft was read, and the four frozen FV preparation files were verified byte-unchanged. The earlier resource interruption left no FW preparation files; this single retry completed without another capacity error.

This packet contains discovery only: complete f83r.1–8 previous plus .9–17 current, and f83v.11–20 previous plus .21–33 current. These four units are on the same physical leaf 83 and joint discovery, never independent confirmation. Application bodies/pixels were not opened. Author access waits for root GO and criteria freeze.

## Frozen files and reproduction

- [FW_DISCOVERY_PACKET.json](FW_DISCOVERY_PACKET.json): SHA256 `518d03e887d788e4b3da0ec702d7df95c338cb71f14a40faad9d65be8d2e59e1`.
- [FW_DISCOVERY_GROUPS.tsv](FW_DISCOVERY_GROUPS.tsv): SHA256 `70841c74725458499bb5bd3448076b117045a75c6101a7c18fffac1bfc6b8e8e`.
- [FW_PREPARE_DISCOVERY.py](FW_PREPARE_DISCOVERY.py): SHA256 `ecbad28eea9132eccde157b2c3b7c899a0e49bb7506267ec87b5f605a156b5f1`.

```sh
python3 research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/FW_PREPARE_DISCOVERY.py
```

The preparer reuses the unchanged pure-function and aggregate-prior logic from the earlier preparation, changing only the FW artifact names, fixed scope/unit partition and paragraph-role metadata. It refuses changed source, model, merges, allowlist or prior cache and writes only its two FW outputs. It neither fits a model nor rebuilds the cache.

## Native source coverage

Canonical mixed source: `experiments/semantic_assumptions/results/source_separator_transcription.tsv`, SHA256 `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`. Only a selector-first `./vmanus-exp query-tsv --selector locus` projection with **40 explicit allow-values** (f83r.1–17 and f83v.11–33) and `f84`/`f84r` forbidden prefixes was decoded. No whole mixed row was parsed and then filtered.

The exact 18 output columns are `source_group_id,edition,locus,page,section,currier,hand,code,kind,grammar_scope,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw`. All source fields are copied unchanged into packet groups. The TSV is the guarded stdout byte projection. It retains literal entities, marked unknowns, original separator classes, flags, IDs and order; no cleaned fragment or preferred-reader spelling replaces a group.

Guard receipt: **1,016 selected**, 2,122 forbidden rows skipped, 112,332 other-selector rows skipped. Skip counts describe guard operation, not excluded-content findings.

| Unit ID | Fixed native scope | ZL3b groups | IT2a groups | RF1b groups |
|---|---|---:|---:|---:|
| FW_F83R_PREVIOUS | f83r.1–8 | 72 | 71 | 72 |
| FW_F83R_CURRENT | f83r.9–17 | 84 | 83 | 83 |
| FW_F83V_PREVIOUS | f83v.11–20 | 99 | 98 | 101 |
| FW_F83V_CURRENT | f83v.21–33 | 84 | 85 | 84 |
| Total | 40 physical loci | 339 | 337 | 340 |

All **1,016 source IDs** are unique and all **120 reader/locus cells** are present. Each native line has complete consecutive group indices and its original group count. ZL/IT starts/ends are 1/8, 9/17, 11/20 and 21/33 respectively. RF retains literal `0/0` flags and `native_paragraph_flags_available=false`; its four units are externally fixed same-locus windows, not inferred native paragraphs.

This is canonical group/separator conservation, not an independent diplomatic full-line preservation claim. No separate raw-line counterpart was queried and no normalized reconstructed line substitutes for one.

## Unchanged formal transformations

The GDT1051 module and imported pure functions were inspected before use; their file reads/writes occur in called loaders or guarded main functions. Only its unchanged `load_merges`, `parse_group` and `make_chunks` run here. No legacy inventory loader, fit routine, saved-source reader or main is called.

Every source group receives the unchanged GDT012 `strip_layers`→GDT062 `preparse` view when eligible. It retains wrapper, residual host, DY flag, host before local framing, B3/right-family/internal-D fields, with local frames still `NOT_FROZEN_FOR_NEW_INPUT`. No O/OT licensing, new prefix rule or universal morph tree is introduced; these labels have no English meaning assigned here.

The GDT605 view uses the unchanged collapse function and existing **64** merges through GDT1051's hard chunks. Only native `UNCERTAIN_SMALL_SPACE` seams are joined within a line; other seams terminate chunks. Every source group points to exactly one chunk; chunks retain raw joined text, source indices, collapsed view, units and existing merge trees. Raw source fields remain unchanged.

There are **966 eligible pure groups**, **50 marked/nonlowercase unresolved groups**, **993 hard chunks**, and **943 eligible chunks**. Unresolved marked groups have no guessed wrapper/host or normalized alternate. All source unknowns and formal residuals remain. Formal replay does not prove morphology, grammar or meanings. Exact code/merge pins are embedded in `input_hashes`.

## Existing aggregate whole priors

All **214 distinct unmarked raw whole forms** in discovery receive exact per-reader aggregate priors. Marked forms remain literal source entries and are not repaired for a count.

The only prior source is the existing read-only `experiments/semantic_assumptions/cache/word_profiles.sqlite`, SHA256 `7a3d21719f43bba7388dc90efd559cedcde5325d7d5a8916ac2bd0e9716e6664`. Its receipt binds the canonical source, `tools/word_profiles.py` and the fixed 179-selector allowlist (SHA256 `f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483`). The complete cache provenance is embedded; no rebuild occurred.

Aggregate SQL returns exact frequency, number of selectors containing the form, source-locus start/middle/end/single counts and section/Currier/hand/kind counts. It does not return outside occurrence rows, examples, neighbors or bodies, and does not call `profile()`/`occurrences()`. Counts include all admitted source kinds and positions, not a prose-only corpus. Selector dispersion is not independent-leaf dispersion; locus positions are not sentence boundaries. Readers are alternate readings of one manuscript and are never pooled.

## Accounting checks and limits

The preparer verified input pins, exact query schema/receipt, all requested reader/locus cells, unique IDs, consecutive indices, group totals, native flag consistency, fixed 64-merge inventory and one chunk membership per group. Source-only post-run checks compared every packet native field and row order to the guarded TSV, required exact four-unit/120-cell coverage, literal RF `0/0` flags, global prior counts at least discovery counts, position totals and original FV file hashes. The decision/preparer/projection bindings were also verified.

These checks concern reproducible source preparation only. Confirmed words: 0; semantic validation false. No candidate glossary, Plan semantics, output dependency, source efficacy, independent confirmation, application content, new pixel, decoder, reserve/sealed access, global registry write or Git action was supplied by preparation. Root controls author release and the separate frozen transfer.
