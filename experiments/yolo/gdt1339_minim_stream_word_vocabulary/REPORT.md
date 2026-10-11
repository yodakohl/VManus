# GDT1339 — encoded source spaces and ambiguous minim runs

## Result and decision

**The fixed reference-vocabulary construction fails in both readings, for all 20 possible source-space signs, even when repeated source spaces are allowed.** Do not build a shared-key decoder for this contract. This is a new test of an ambiguous variable-width stream, not a reversal of the older uniquely-decodable or fixed-pair exclusions.

| Reading | Previously exposed paragraphs | Units | Reference types | Longest reference word | Smallest required maximum over all markers | Surviving S / R markers |
|---|---:|---:|---:|---:|---:|---:|
| IT2a | 23 | 3293 | 5896 | 17 | 29 | 0 / 0 |
| ZL3b | 23 | 3420 | 5896 | 17 | 29 | 0 / 0 |

The readings describe the same manuscript; they are not independent confirmations. Paragraphs are the old GDT1259 rank-selected certificates, not a new holdout. The reference inventory is the fixed union of four old GDT1177 source books after the declared ASCII-only admission and J/I, U/V, W/VV projection. It is neither an identified source language nor a complete inventory of any language.

## Writer and informative counterexample

The proposed writer ignores visible word gaps for plaintext segmentation. One of 20 working signs represents a plaintext space; the remaining signs encode 19 literal letters and ambiguous, variable-width I/N/M/V runs using e or i. This is an invented, content-bearing construction, not a claim about historical scribal practice. See the frozen [preregistration](PREREGISTRATION.md).

For each possible space sign, every segment between its occurrences must belong to one source word. Each non-e/i unit requires one source letter. Each monochromatic e/i run requires at least its length divided by three, rounded up. A clipped outer fragment also cannot contain more source letters than its complete source word. Every possible marker forces some segment above the reference maximum of 17. Thus the length condition alone already excludes all markers, without relying on dictionary equality patterns or a shared substitution key.

The least demanding marker is o, but this does not identify its value. Its maximum-length witness lies in f103v.18–19 in both readings. The IT2a unit sequence is:

`l d a i i n ch e y l k e e y ch a l k a r ch e e e y l ch e a l a i i n`

It has 23 non-minim units and six monochromatic minim runs of lengths 2, 1, 2, 3, 1, 2: at least 23 + 6 = 29 source letters. It extends from IT2a f103v.18 group 10 offset 6 through f103v.19 group 6 offset 8. ZL3b has one final i instead of two and ends in group 7 offset 6; its bound remains 29. Both are complete internal segments, so this particular counterexample does not depend on clipping at the paragraph edge. Exact pointers and all other marker witnesses are in CASES and STREAMS.

The complete local compatibility filter additionally checks all 4509 complete nonempty spans. Its word-specific partial keys are deliberately allowed to differ: retaining a local candidate would not decode the manuscript or establish a globally consistent key. Full candidate IDs, unsupported spans and adjacent-marker witnesses remain available. Rare markers with no complete spans are marked uninformative for dictionary matching, but their clipped length bounds still exclude the fixed inventory.

## Validation and procedural disclosure

Independent validation reconstructed 1418 original groups through the guarded, exact-locus query, checked full group indices and consecutive source rows, reparsed all 6713 units dynamically, and recomputed all 40 marker decisions. Direct source-word alignment independently reproduced every candidate set, without calling the primary signature matcher. All 17688 source-only true-word controls and 15762 clipped-word fixtures passed. A separate agent reviewed the logic of clipping, marker exclusivity and partial-bijection completion and found no false-exclusion bug.

Two validator integration errors were corrected before validation passed: the query requires a separate `--allow` for every locus, and diagnostic lines must not be treated as TSV headers. These errors initially prevented provenance validation; they did not change the primary runner, frozen rules or native results. The registration lock remains unchanged.

The preregistration's final compressed phrase “No ... rawTSV” was too broad: independent validation did reread the original TSV through the required selector-first guard, restricted to the already selected certificate loci. This was provenance recollation, not new data selection or admission. The frozen preregistration is preserved; this report explicitly records the deviation. No sealed, reserve, f116v, f1r-body, GDT327-body or GDT336-body material was opened. No word meaning was assigned.

## Scope, audit and next decision

The [independent prior-closure audit](../../../research_registry/proposals/production_origin_supply_20261003/ROUTE_CLOSURE_ERROR_AUDIT_20261011.md) found no new error or justified reopening in its selected cases. It preserved the already known limitations of GDT1165, GDT1166/1171 and GDT1316/1317. It did not certify all previous work. Its 240 source-free CSP cases are an engineering spot check, not new manuscript evidence.

This result rejects only the declared writer plus fixed reference inventory. It does not reject ambiguous streams generally, all Latin, other languages, different letter inventories, or the unbounded RAW1006 family. The latter must account for required long source words and the full pattern constraints; merely inventing words or adding vocabulary after observing these failures supplies no corroboration. The writer also leaves visible layout unexplained. No automatic corpus expansion, alternate separator role, longer minim code or decoder repair is selected.

Reconsideration requires an independently motivated source/writing contract and a different predeclared discriminating consequence, retaining the old counterexamples. No next manuscript experiment has yet been selected. The inclusive budget was 12:38–13:23 UTC, including verification and publication; no further scientific expansion occurred in this unit.
