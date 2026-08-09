# Independent ZL3b separator-certainty validation

Decision: **PASS — EXACT CLEAN-ROOM RECONSTRUCTION**.

The standalone validator imports no production experiment module. It binds the
manual ZL3b source, derived line table, complete pre-grounding surface,
parser-free capacity panel, and residual atlas, then independently reconstructs
the complete production JSON and report.

The IVTFF separator definitions are provenance-bound to section 6.7 of the
official format specification, and the new JSON field and report citation both
reconstruct exactly.

- Raw source/table binding: **5,385/5,385** exact rows.
- Interlinear/table clean-surface binding: **5,376/5,376** exact rows.
- Separator extraction: **5,323 resolved / 62 unresolved** rows.
- Exact-y panel: **30 spans; 28 ZL-isolated / 2 ZL-fused**.
- Isolated boundary pairs: **15 / 8 / 3 / 2 / 0** in the frozen report order.
- Confirmed-prose clean scope: **19/19** ZL-isolated cases explicitly uncertain.
- Residual ZL `y`: **341 events; 318 resolved / 23 unresolved**.
- Independent checks passed: **52** with zero discrepancies.

Hashes:

- Validator: `441549706674289ef19c4881d03a3fad727e48f8938b8e59a660516cf760f4bd`
- Producer: `df63db83228827c63c0e57e2a92d8a1f60279083fc25e5f8393339e7728d32cc`
- Production JSON: `6399664f6709e472d32b5728cd491ff82115b812a55a04eee5943981635faa3a`
- Production report: `bf7128565354369ca28c343b301e7fc0ae37861f888ef6a5d1cf2092cd5c81bc`
- Gate object: `a03acb33f9b58db26da35273eccc77bd3d955430f5435db7528c3592f8fc5dfe`
- Claim ceiling: `b330fc20972a9d28552cd0f99f850355d6b9263cc63695ab8b7d5820f211aa0f`

The validated claim remains a route-specific transcription/layout-uncertainty
stop. It assigns no authorial spacing, separator, suffix, sound, word, plaintext,
or meaning.
