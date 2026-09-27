# IDEA000589 author packet: independent literal and accounting review B

Reviewed 2026-09-27, before the 09:15 UTC freeze deadline. This is a mechanical review of the frozen author packet, not an independent source or meaning test. The manuscript, source hypothesis, and project are already exposed to this reviewer. Root retains semantic, source, and grammar assessment.

The author freeze is intact. All four hashes and byte lengths in `AUTUMN_SYNOPSIS_AUTHOR_FREEZE_RECEIPT.json` match the files on disk. The stipulated GDT1042 `native_groups.tsv` SHA-256 also matches `e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c`.

The original source table has 473 rows and 12 fields. The consequence TSV and the JSON `all473_consequences` list each preserve those same twelve fields, in the same row order, exactly. All 473 `source_group_id` values are unique. Every added consequence field also agrees between JSON and TSV after normalizing the JSON list of argument obligations to the TSV's ` | ` separator. Stored previous/next literals match adjacent groups in flattened reading order within each reader, including across line boundaries.

The reader accounting reconciles exactly:

| Reader | All groups | Local derivation | Clause span with literal gap | Assigned, unparsed | Unassigned, unparsed | Fixed-value occurrences |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b | 156 | 33 | 0 | 31 | 92 | 64 |
| IT2a | 157 | 14 | 19 | 33 | 91 | 64 |
| RF1b | 160 | 14 | 19 | 30 | 97 | 58 |
| **Total** | **473** | **61** | **38** | **94** | **280** | **186** |

The 37 dictionary forms list 186 unique source IDs. Each listed ID exists in the source, has exactly the listed literal, and the consequence TSV gives it the dictionary's declared value and type. No listed occurrence is duplicated; no fixed row is missing from the dictionary. The five declared derived forms concatenate exactly from their cuts, and each cut accounts for every raw occurrence of its form: `dar` 6, `daiin` 9, `qodar` 2, `qodaiin` 5, `qodain` 3. Thus the five derived forms comprise 25 of the 186 fixed occurrences. No broader segmentation rule is asserted by this check.

Each clause's numeric locus/start/end spans reconstruct its listed ZL IDs and surface string exactly:

| Clause | Fixed span | Groups | ZL / IT / RF result |
|---|---|---:|---|
| C1 | .2 G001–G005; .3 G001–G005 | 10 | exact literal sequence in all three readers |
| C2 | .7 G001–G005; .8 G001–G006 | 11 | ZL exact; IT/RF fixed spans retained as incomplete |
| C3 | .9 G001–G006; .10 G001–G002 | 8 | ZL exact; IT/RF fixed spans retained as incomplete |
| C4 | .10 G003–G006 | 4 | exact literal sequence in all three readers |

The C2/C3 gaps match the underlying rows and are marked as whole incomplete spans in both alternate readings. IT has unassigned `oloeorain` in C2 and `qtchedy` in C3. RF has `qoke@152;y`, `{ch'}eos`, and `otche@152;y` in C2, then `ote@152;y` and `qo@152;ar` in C3. C1 and C4 each account for 14 complete local groups in IT and RF; C2/C3 account for 19 incomplete-span groups per reader. These figures support the report's distinction between an incomplete literal span and a completed derivation.

The declared earliest unresolved ZL row is indeed `ZL3b|f85r2.1|G001` (`odeedy`); no local clause includes it. The adjacent rows are G002 `otedy`, G003 `opaees`, G004 `ar`, consistent with the cited first-annulus gap description. The four hand-written AST strings have balanced parentheses and correspond to the exact clause token spans. No literal, row-identity, occurrence-list, count, or span reconstruction error was found.

The report's total of 186 fixed occurrences (64/64/58 by reader) and 61 rows in complete local derivations are correct. Its 38 lexical-payload lower bound is obtained by adding the two one-payload component operators to the 36 independently paid whole-binding payloads; this decomposition is implicit rather than separately stated. The accompanying cost object lists the same total of 38.

This review does not validate the historical meanings, typed composition, source-duty equivalence, the declared boundary interpretation, or plausibility of unparsed rows. It does not convert the 61 local derivation rows into a complete reading. The author packet remains correctly labeled partial, with no whole-page claim.
