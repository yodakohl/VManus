# KW: optional design scope and primary-pointer availability

2026-09-08 02:32 UTC. Engineering budget15minutes including implementation, tests, metadata validation and publication.

Root observed75authored designs but only42usable declared-design fingerprints. The other33 may be searchable lexically but cannot receive a same_declared_design match because the fingerprint requires optional design.scope. The intake schema accepts designs without it. Unknown after inspection: can exact declared-field navigation cover those valid sketches while preserving all existing scoped fingerprints and preventing incomplete/invalid designs from matching? This changes whether duplicate intake can be detected; it is not a semantic equivalence decision.

Smallest fix: require mechanism/unit/contrast/prediction; include scope in the fingerprint if supplied, validating it as before. Omitted scope stays omitted, not filled from a later mutable review scope. Preserve existing hashes for all five-field designs. Retain candidate-only behavior, no automatic merge or scientific novelty claim. Add focused regression checks for omitted-scope duplicate retrieval, existing hash parity, and incomplete/invalid inputs. Existing implementation digest already invalidates the SQLite cache; no new cache framework.

Separately record the independently checked IL019 unavailable local primary pointer without changing the inherited closed-family disposition. Four comparison pointers resolve under the semantic-assumptions directory. No source restoration or wider decoder/control work.
