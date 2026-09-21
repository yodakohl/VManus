# Post-result source-scope correction, 2026-09-21

The locked GDT1015 input is the **normalized P28/RAW379 working copy**, not a
complete diplomatic ZL3b transcription. The independent post-result comparison
against the already owned GDT928 cache finds the same nine-line paragraph and
80 group positions, but two different groups:

| Locus/group | GDT1015 working copy | Diplomatic cache |
|---|---|---|
| f82r.15 / 4 | `qokeedy` | `qok[ee:ch]dy` |
| f82r.16 / 11 | `ra` | `ra{cty}` |

The first commits to one listed alternative; the second does not retain the
braced entity. Their justification was not supplied by GDT1015. Seven lines
match at group-string level, but only three of nine lines are marked
`anchor_eligible` in GDT928. Exact string agreement therefore does not certify
that all remaining source boundaries or signs are unambiguous.

This audit was conducted after result publication `bf5d29983`. It is not blind
verification or a new decoding experiment. The locked SOURCE, MODEL, first
reading, code and arithmetic outputs remain byte-for-byte unchanged. All 357
independent arithmetic checks still concern those declared inputs. The
complete-coverage claim is narrowed to that supplied working copy; complete
diplomatic manuscript coverage is withdrawn. No alternate reading is silently
substituted and no source uncertainty is counted as a successful prediction.

The same scope applies to the subsequent Palladius and Euclid proposal
preflights that copied these 80 groups. Their counting contradictions concern
the supplied normalized target and exact proposed writers. They are not
exhaustions over every diplomatic alternative.

Reproduce with `python3 experiments/yolo/gdt1015_coupled_hour_day_reading/src/audit_source_scope.py`.
The source cache and both differing groups are bound in
`artifacts/SOURCE_SCOPE_AUDIT.json`. This uses an already exposed, f84-free owned
cache; no new page, image, reserve or contact. Confirmed words remain zero.
