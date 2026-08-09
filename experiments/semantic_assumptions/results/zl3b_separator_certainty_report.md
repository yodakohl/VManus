# ZL3b manual separator-certainty audit

Decision: **STOP USR002 BEFORE A CONTEXT SCORE**.

The manual ZL3b source explicitly distinguishes confident spaces (`.`),
uncertain small spaces (`,`), and drawing interruptions (`<->`/`<~>`).  The
definitions are in section 6.7 of the
[IVTFF format specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf).
The
derived ZL table matches all 5,385 raw source rows exactly, and
the pre-grounding surface matches all 5,376 shared clean
rows.  Separator order is directly recoverable on
5,323/5,385 rows and on every exact-y
candidate.

Of the 30 parser-free split/fused `y` spans, ZL3b isolates `y` in 28 and fuses
it in two.  All 28 isolated cases already carry at least one explicit uncertain
small-space or drawing-interruption boundary:

| ZL left boundary | ZL right boundary | spans |
|---|---|---:|
| definite | uncertain | 15 |
| uncertain | definite | 8 |
| uncertain | uncertain | 3 |
| drawing interruption | uncertain | 2 |
| definite | definite | 0 |

After the earlier drawing-line and confirmed-prose exclusions, all
19 ZL-isolated cases remain explicitly uncertain.  A
context classifier would therefore model a confidence flag already supplied by
the human transcription, not discover an independent manuscript boundary.

This stop does not make literal `y` meaningless.  Across all 341 ZL residual
`y` events, 318 have recoverable
separator metadata and some are bounded by two confident spaces.  It closes
only the proposed exact-y disagreement route.  No authorial spacing, suffix,
separator, sound, plaintext, or English meaning follows.
