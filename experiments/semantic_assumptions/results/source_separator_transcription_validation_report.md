# Independent source-separator transcription validation

Status: **PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION**

The clean-room validator made **2,771,299** successful checks without importing
the producer or legacy parser.  It reconstructed all **15,985**
source rows, **115,470** source groups,
**99,485** explicit separators, and their exact
**118,011**-fragment legacy mapping.

It independently confirms **173**
zero-fragment groups, **2,688**
multi-fragment groups, and **2,714**
cleaner-created nonmanual boundaries.  Exact atlas rows, source/interlinear key
partition, hashes, counts, gates, and claim ceiling all match.  Synthetic
controls reject empty/trailing source groups and exercise all four separator
states plus both cleaner failure modes.

This validates transcription provenance and loss accounting only.  It assigns
no authorial word boundary, sound, grammatical role, lexeme, plaintext,
language, or translation.
