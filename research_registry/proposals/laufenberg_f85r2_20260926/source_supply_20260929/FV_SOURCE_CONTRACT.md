# FV independent source and scope contract

Status: **frozen preauthor contract; comparison not executed**. Owner: fs_sun_moon_binding. Prepared 2026-10-01, from [FV_DECISION.md](FV_DECISION.md), the live route and preparer metadata. No current discovery source body, additional-unit body, new pixels, author or peer draft was opened during preparation. Source-file hashes are metadata, not body admission. Actual row/group/chunk/error counts remain unset until explicit root GO and an independent guarded source query.

## Fixed input and partition

Discovery is exactly f83r.9–17 and f83v.21–33, with ZL3b, IT2a and RF1b retained. This is 22 requested loci and 66 requested reader/locus cells, **not 66 observed rows or independent samples**. The direct query will account for each cell and determine actual rows, groups, unresolved forms, chunks and errors; no presumed 101-group count is admitted.

The native canonical source is `experiments/semantic_assumptions/results/source_separator_transcription.tsv`, SHA256 `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`. Its selector is `locus`, with each of the 22 loci individually supplied via repeated `--allow`, and `--forbid-prefix f84` and `--forbid-prefix f84r`. The mixed TSV must never be parsed in full and then filtered. All three actual readers are obtained from those selected loci, without substituting a preferred reading. The 18 canonical columns and full selector list are fixed in the companion JSON.

Additional f75v.43–49 and f104v.22–26 bodies are withheld from the author until grammar, dictionary, defaults and complete predictions freeze. These are 12 requested loci, 36 requested reader/locus cells, with observed counts still unset. They require a separate root authorization for this auditor to compare their actual content. RF absence of the exact pair at f75v and IT absence at f104v are not licenses to invent an alias, silently remove a reader or declare an automatic semantic contradiction.

Both sides of f83 are physical leaf83 and joint discovery/training. Additional physical leaves75 and104 provide selected paragraph windows, not complete folio/leaf readings. These are previously exposed manuscript data. A new independent observer, separate recto/verso windows and three transcription alternatives do not create an independent manuscript confirmation. Independent confirmation remains **0**.

## Literal comparison fixed before authorship

**S01 — Independent canonical acquisition.** After explicit root GO, directly invoke query-tsv with selector locus and exactly the 22 listed discovery allows; forbid f84 and f84r before materialization. Do not read the mixed TSV with an ordinary parser and filter afterward. Preserve query argv and output hash. No additional-partition content or pixels.

**S02 — Actual source-cell receipt.** Observe rows per exact edition/locus. Report every requested cell, including absent cells; do not infer a row or a pair from another reader. Record actual editions, source rows, groups, chunks, unresolved groups and errors. The 66 requested cells are not observations or independent samples. Counts are null until direct comparison.

**S03 — Exact source-field conservation.** One-to-one compare all 19 selected canonical fields for every group, including raw field UTF-8 spelling, source_group_id, native row/group indexes, declared group_count, code, flags and separators. No aliasing, trimming, normalization, entity deletion, guessed correction, reader substitution or omission. Distinguish exact canonical field conservation from a diplomatic original full-line-byte claim; no raw-line counterpart is presently promised.

**S04 — Independent ordering and boundary accounting.** Check source_group_id uniqueness, native (edition,locus,source_row_index,source_group_index) identity, contiguous indexes where canonical source requires them, counts and line termination. Compare missing/extra/duplicate/conflicting packet groups as errors. Preserve native definite and uncertain-small-space seams, line breaks, marked entities and explicit gaps; flag malformed seams without repairing them.

**S05 — Native versus imposed paragraph scope.** Compare ZL/IT paragraph_start and paragraph_end literally to the canonical source. RF source-empty paragraph flags must remain empty: external complete-line window/unit grouping is an imposed comparison scope, never a native RF paragraph boundary. No packet-created paragraph fact.

**S06 — Frozen formal replay.** Independently replay the unchanged hash-pinned GDT1051 parse_group/make_chunks using the unchanged GDT012 strip_layers, GDT062 preparse and 64 ordered GDT605 merge rules. Each original group persists. Only lowercase a-z groups are eligible. UNCERTAIN_SMALL_SPACE alone joins groups within a locus for a hard chunk; definite spaces/line ends stop it. Marked chunks remain unresolved. Compare exact joined spelling, collapse, ordered units, recursive tree and wrapper/host fields. Joining BPE units conserves collapsed spelling, not proof of raw spelling conservation.

**S07 — No inferred new parser license.** GDT062 local frame stays NOT_FROZEN_FOR_NEW_INPUT. No new O/OT host licensing, fit, merge order, deterministic context wrapper, stem equivalence, morpheme or semantic role is introduced. GDT605 units and 012/062 formal outputs are alternatives/structure, not confirmed word meanings.

**S08 — Cached frequency prior provenance.** Validate the supplied exact-whole aggregate map against the existing hash-pinned word_profiles.sqlite using read-only SQL for distinct discovery lowercase whole groups only. Keep editions separate, count/page count/locus-edge/strata fields separate, and native source-locus position distinct from sentence/paragraph position. No profile(), occurrences(), outside occurrence rows, neighboring literals, examples, cache rebuild or new corpus census. Validate the fixed179-selector receipt; its allowlist hash is metadata, not additional access. Mark unavailable receipt or disagreement explicitly.

**S09 — Scope and exposure conclusion.** Discovery f83r and f83v belong to physical leaf83 and joint training, despite recto/verso and differing native paragraph windows. f75v and f104v are additional physical leaves75/104 with selected-paragraph coverage only, previously exposed manuscript data, not whole-leaf readings, untouched holdouts or independent confirmation. Independent reader alternatives and an independent new observer do not make independent manuscript evidence.

**S10 — Failure/no-capacity distinction.** Source mismatch means packet is not safe for authorship/scoring until corrected and source conservation passes; it is not a semantic refutation. Missing native material/marked form/reader pair is explicitly retained and scoped, never filled from a peer or dictionary. An absent exact pair does not automatically contradict the operation or license an alias. A formal replay PASS establishes only faithful input representation. Missing provenance or unsupported claim is NOT_ESTABLISHED rather than invented count or success.

Prepared packet paths were supplied as metadata before freeze: `FV_DISCOVERY_PACKET.json`, `FV_DISCOVERY_GROUPS.tsv`, `FV_DISCOVERY_README.md` and `FV_PREPARE_DISCOVERY.py`, schema `FV-discovery-native-v1`. Their bodies remain unopened.

The principal test is an independent field-by-field source comparison, not agreement with the preparer's summary count. Every canonical raw group and its actual native source ID, row/group indices, separators, marked spellings, metadata and native paragraph flags must survive exactly once. Source spellings are compared without trimming or normalization. The audit claims canonical group/separator conservation; a diplomatic whole original raw-line-byte conservation claim would require a separate admitted raw-line counterpart, which is not presently planned.

RF paragraph flags remain source-empty. Its grouping under the same complete-line comparison windows is imposed scope, not recovered native paragraph structure. ZL/IT paragraph flags are checked directly, without inferring them from the scope label.

## Frozen formal models and priors

Unchanged GDT1051 application pins GDT012 `strip_layers`, GDT062 `preparse`, GDT605 `collapse`/`apply_bpe` and its 64 ordered merges. Pure lowercase groups may be replayed; marked/nonlowercase groups remain unresolved. Only `UNCERTAIN_SMALL_SPACE` joins source groups into a within-locus hard chunk. Original groups persist even when a chunk is collapsed or merged. Definite spaces and line ends remain hard. Ordered BPE units must rejoin the collapsed spelling; this alone does not prove raw-source conservation. GDT062 local-frame output remains `NOT_FROZEN_FOR_NEW_INPUT`.

These formal parts, wrapper/host distinctions and segmentational alternatives have no confirmed semantic roles or morpheme status. No new fit, O/OT license, directed-context gloss, deterministic wrapper-removal rule or decoder is authorized. All model/source hashes are in the companion JSON.

The preparer's prior cache is existing `experiments/semantic_assumptions/cache/word_profiles.sqlite`, SHA256 `7a3d21719f43bba7388dc90efd559cedcde5325d7d5a8916ac2bd0e9716e6664`. The supplied fixed179-selector allowlist hash is `f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483`; its receipt locator is pending. Post-GO validation may use read-only aggregate SQL for distinct discovery lowercase whole groups only, separately by reader. Count, distinct-page count, source-locus start/middle/end/single and section/Currier/hand/kind strata stay distinct. Locus-edge position is not a sentence or paragraph boundary. No outside occurrence rows, neighboring literal context, `profile()`/`occurrences()`, new census or cache rebuild is admitted.

## Outcomes and research decisions

A conservation PASS permits this faithfully represented packet as exploratory FV input; it binds no meaning and changes independent confirmation by zero. A missing/extra/duplicate group, changed native flag, normalization, source-ID or replay mismatch returns the affected packet to its preparer before use; this is a representation failure, not a lexical refutation. Native missing or uncertain material stays explicit and narrows comparison capacity. Unverified prior provenance blocks use of that prior as verified evidence, without erasing conserved source text. Scope/blinding breaches must be recorded as exposure and invalidate an independence claim; root decides whether exploratory authorship remains usable.

Passing requires each requested cell to be accounted for, exact canonical fields and fixed transformations conserved, and zero unexplained representation discrepancies. Missing native cells are reported rather than manufactured. This file fixes the checks; it does not report their result. No body comparison, author repair, decoder, reserves, Git or global ledger/route edits have occurred under this contract.
