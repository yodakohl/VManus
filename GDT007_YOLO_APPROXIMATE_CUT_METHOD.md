# GDT007 YOLO approximate physical-cut discovery

Status: **REGISTERED_EXPLORATORY; LOCALIZATION MAY BE APPROXIMATE**.

GDT007 deliberately relaxes GDT006's confirmation-grade localization gate.
It asks whether source-aware AI localization plus independent crop-only AI
review produces any interesting target/control spacing pattern worth later
human confirmation. It is discovery evidence only.

## Frozen source scope

- Reuse the nine non-f84 GDT005 target/control group pairs.
- Reuse all 17 target cuts.
- Retain every control cut that is already an internal STA-sign boundary.
- If a display-coordinate control cut falls inside one STA sign, replace it
  with the nearest internal STA-sign boundary in the same control group; ties
  choose the earlier boundary. Preserve both the original and replacement.
- Do not select or reject a cut from its visual spacing.

## Permissive localization

Two source-aware AI localizers independently inspect exact provenance-bound
native images, the registered physical line, source-group order, and STA
sequence. Each returns a best-effort marker with `HIGH`, `MEDIUM`, or `LOW`
confidence, or `UNRESOLVED`. Approximate markers are allowed. Disagreement is
retained rather than used as an automatic stop.

The reconciled marker is chosen mechanically: agreement first; otherwise use
the higher-confidence localization; equal-confidence disagreement retains both
as a localization-sensitivity pair. Every localization is
`AI_DIRECT_VISUAL_OBSERVATION`, never human annotation or OCR.

## Opaque review

After reconciliation, randomly named crops contain only a marker and local
manuscript geometry. Fresh `fork_turns=none` reviewers receive no locus,
transcription, cut offset, target/control identity, operation, or join. They
classify `INK_TOUCH_OR_CROSSING`, `NARROW_VISIBLE_GAP`,
`ORDINARY_VISIBLE_GAP`, `WIDE_VISIBLE_GAP`, or `UNRESOLVED`, with confidence
and a neutral note.

## Exploratory analysis

All available calls remain data. Report target/control distributions and an
ordered 0--3 gap score, stratified by localizer confidence and reviewer. Show
the full result, HIGH/MEDIUM-only sensitivity, agreement-only sensitivity,
pair contributions, and exact paired swaps where defined. These controls rank
the lead; they are not discovery kill gates.

## Ceiling

Even a target/control difference is a postselected AI-visual lead only. It is
not confirmed handwriting segmentation, a grapheme boundary, morpheme,
linguistic slot, language, meaning, semantic role, plaintext, or translation.
GDT003 remains `NOT DISTINGUISHABLE FROM STRING STATISTICS`. The f84r image and
formal payload remain sealed.
