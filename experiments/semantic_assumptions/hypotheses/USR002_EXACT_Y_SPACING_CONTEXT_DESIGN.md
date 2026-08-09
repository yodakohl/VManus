# USR002 — exact-y spacing context design

Status: **STOPPED UNSCORED — EXPLICIT TRANSCRIPTION CONFIDENCE EXPLAINS THE
TARGET**.

The parser-free capacity audit found 30 internal exact-character `y` spans on
29 physical loci where all three manual readings have the same non-space
characters but disagree on whether `y` is isolated.  Conservative exclusion of
manual drawing-interruption lines and diagnostic nonprose left 21 spans on 17
folios, with only seven two-reading cases on six folios.  No context score was
computed.

Before a context model was registered, the raw manual ZL3b source was restored
to the audit.  IVTFF preserves four separator states that the normalized
pre-grounding `surface` had flattened: confident apparent space `.`, uncertain
small apparent space `,`, drawing interruption `<->`, and unaligned drawing
interruption `<~>`.  ZL3b isolates `y` at 28 of the 30 disagreement spans.
Every one of those 28 already has an explicit uncertain-small-space or drawing
boundary; zero has two confident spaces.  All 19 ZL-isolated cases in the
proposed context scope remain explicitly uncertain.

Thus a classifier would model a human transcription-confidence flag already
present in the source rather than discover an independent manuscript boundary.
USR002 stops before implementation, calibration, or target scoring.  The stop
does not establish which spacing is authorial and does not assign `y` a
separator, suffix, sound, word, number, plaintext, or meaning.

Primary evidence:

- `results/usr002_exact_y_capacity_report.md`
- `results/zl3b_separator_certainty_report.md`
