# GDT002 contact/gap acquisition

Status: **REGISTERED BEFORE TARGET IMAGE ACCESS**.

## New observable

This acquisition records only whether a frozen short inscription and a nearby
drawn non-writing contour visibly meet. It does not classify the drawn object
or interpret the contact.

States:

- `CONTACT`: at least one target writing stroke visibly touches or overlaps a
  drawn non-writing contour.
- `CLEAR_GAP`: visible background separates every target writing stroke from
  the nearby drawn contour.
- `UNCERTAIN`: localization, fading, overlap, damage, or geometry prevents a
  secure binary judgment.

The complete panel is frozen from three human-described local arrays before
image access: f89r2.32–34, f99v.15/.17/.18/.20, and f100r.7–11. These are 12
loci on three physical folios. The source comments nominate the arrays but do
not supply the new state: every target is re-localized and re-graded against
the exact official image.

## Separation

The source-aware localizer receives page, locus, array order, and full image.
They create a context crop and a marked target box but make no CONTACT/GAP
judgment. A separate reviewer receives only randomized crop IDs, marked crop
images, and this three-state rubric. They receive no folio, locus, source
comment, transcription, formal family, object name, or discovery/holdout flag.

No OCR, automated vision, segmentation, embedding, or image classifier is
used. All visual calls are `AI_DIRECT_VISUAL_OBSERVATION` and are kept
separate from the human nomination source.

## Capacity gate

f89 and f99 are discovery; f100 is procedural transfer. The visual acquisition
passes only if each physical folio has at least one `CONTACT` and at least two
`CLEAR_GAP` calls, with all required calls securely localized. Otherwise stop
before formal comparison.

If the gate passes, a later frozen joint solver may compare primitive formal
constructions with these two physical relation states. It must preserve array,
folio, and transcription uncertainty in its controls. Exact strings may not be
used as object names. No state, role, word, POS, sound, language, plaintext,
meaning, or translation follows from this acquisition alone.
