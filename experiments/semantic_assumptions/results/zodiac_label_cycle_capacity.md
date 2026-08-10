# Zodiac label cycle capacity

Status: **PASS_TEXT_BLIND_21_RING_235_SLOT_PUBLIC_ORDINAL_PANEL**.

This grouping is public catalogue data, not a user-supplied page or label assignment. The [Stolfi/Grove label catalogue](https://www.ic.unicamp.br/en/~stolfi/EXPORT/00-EXPORT/98-02-01-lotsa-labels/) supplies the zodiac page, ring description, and Grove number; Grove numbers count positions clockwise within a ring. The already validated current-locus crosswalk maps those public records to the manual ZL3b/IT2a/RF1b transcription without image recognition or OCR.

The raw catalogue contains 300 zodiac records on 12 pages. A strict panel keeps only complete INNER/MIDDLE/OUTER rings whose ordinals are exactly 1..N and whose every record has an explicit human Grove key, a primary one-to-one current-locus mapping, and all three manual readings. It retains **21 rings, 235 label slots, 11 pages, and 4 physical folios**. Every retained mapping uses `HUMAN_GROVE_SCOPE_NUMBER`; no label text, STA identity, adjacency similarity, or manuscript outcome was inspected.

Four rings are excluded before any text score: f70v1 INNER and OUTER use string-cluster mapping rather than the explicit human-position crosswalk; f72r2 OUTER contains the public missing label; and f72v1 OUTER contains one catalogue ordinal written as `6 (or possibly the queen)` rather than an explicit `#6`. CENTRAL and OUTSIDE records are not cyclic-ring members.

The panel is therefore sufficient for a new rotation/reflection-invariant test of whether adjacent zodiac labels share transferable partial construction structure more than within-ring permutations. Such a test must preserve whole labels, ring membership, length opportunity, alternate-reading linkage, and physical-folio concentration. It is distinct from the failed C-to-L echo, duplicate-sign, opposition, and universal 30-position phase routes. No object ownership is assumed: the only geometry used is public clockwise ring order.

Claim ceiling: capacity and public cyclic order only. No serial code, number, degree, sign name, word, meaning, plaintext, or translation follows.

## Dropped rings

- `f70v1:INNER` (5 slots): NOT_ALL_EXPLICIT_HUMAN_POSITION_MAPPINGS, MISSING_OR_NONPRIMARY_CURRENT_LOCUS
- `f70v1:OUTER` (10 slots): NOT_ALL_EXPLICIT_HUMAN_POSITION_MAPPINGS, MISSING_OR_NONPRIMARY_CURRENT_LOCUS
- `f72r2:OUTER` (16 slots): NOT_ALL_EXPLICIT_HUMAN_POSITION_MAPPINGS, MISSING_OR_NONPRIMARY_CURRENT_LOCUS, NOT_ALL_THREE_MANUAL_READINGS_PRESENT, CURRENT_LOCUS_NOT_ONE_TO_ONE
- `f72v1:OUTER` (20 slots): NONEXPLICIT_OR_MISSING_GROVE_ORDINAL, NOT_ALL_EXPLICIT_HUMAN_POSITION_MAPPINGS
