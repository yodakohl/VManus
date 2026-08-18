# GDT335 — tuple placement component decomposition

Status: **TUPLE_GAIN_IS_LINE_PLACEMENT_NOT_RECORD_FIELD_ORDINAL**.

The frozen GDT334 gain decomposes as follows:

- physical line entry: +281.830 bits;
- within-field position: +289.929 bits;
- physical line quartile: +167.126 bits;
- field ordinal: -42.360 bits.

Field ordinal is negative in all five registers. Line entry is positive in all five; within-field position and line quartile are positive in four.  GDT334 therefore supports register-conditioned *line-placement signatures* of exact joint tuples, not stable numbered record fields.  The within-field component remains a formal boundary-position effect, not a semantic role.

No tuple meaning, semantic role, word, POS, sound, language, plaintext, or translation follows. No f84 row was opened, retained, joined, or scored.
