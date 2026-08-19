# GDT349 method — complete zodiac facing-orientation acquisition

Date: 2026-08-19

Status: `FROZEN_BEFORE_NEW_IMAGE_REVIEW`

## Question

Can a complete, text-blind native review of the 235 strict public zodiac
figure/label positions supply a reusable geometric contrast that is not
determined by page or ring?

The candidate contrast is head/torso facing orientation.  It was selected from
the pre-existing public attribute-capacity audit, where `FACING_LEFT` had ten
explicit records on two physical folios and `FACING_RIGHT` only one record on
one folio.  No Voynich surface, family, tuple, PAGE_HOST, or formal score is
used to select the contrast.

## Frozen panel

The panel is every one of the 235 rows in
`results/zodiac_label_cycle_capacity.tsv`: 21 complete strict rings on eleven
pages and four physical folios.  The upstream panel already excluded four
incomplete/non-primary rings and non-ring positions before this experiment;
GDT349 makes no further row selection.  No retained row may be removed because
its figure is difficult, damaged, unusual, or formally inconvenient.  The
existing Grove ordinal and ring assignment localize the visible figure/label
position; they are not treated as proof that the nearby inscription names the
figure or its pose.

Every slot receives exactly one native visual state:

- `PROFILE_LEFT`: the visible head/torso profile faces toward image-left;
- `PROFILE_RIGHT`: the visible head/torso profile faces toward image-right;
- `FRONTAL_OR_NON_DIRECTIONAL`: no stable left/right profile is visible;
- `UNCERTAIN`: damage, occlusion, scale, or conflicting head/torso cues prevent
  a reliable call.

The observation layer must record source image/canvas, reviewer provenance,
confidence, and a neutral note.  New calls are
`AI_DIRECT_VISUAL_OBSERVATION`; they are never relabeled as human annotation.
No OCR, automated recognition, CV classification, embeddings, or image
similarity are allowed.  Cropping for direct inspection is permitted.

## Capacity gates

The acquisition is capable of supporting a later *exploratory* formal test
only if all of the following hold after the complete census:

1. at least 12 `PROFILE_LEFT` and 12 `PROFILE_RIGHT` rows are retained;
2. each directional state occurs on at least two physical folios;
3. at least three page-by-ring strata contain both directional states;
4. those mixed strata span at least two physical folios;
5. at least 80% of all 235 rows are directional or
   `FRONTAL_OR_NON_DIRECTIONAL`, rather than `UNCERTAIN`;
6. all 235 rows remain present and every image is provenance-bound.

One-sided pages and uncertain rows remain observations.  They do not kill
other strata and are not forced into either direction.

If the gates fail, stop before reading any Voynich formal payload.  If they
pass, freeze a later within-page/ring, folio-held formal comparison before
opening target formal values.  Passing the acquisition gate still does not
create authorial label ownership; it only creates an ordinally aligned visual
endpoint with explicit provenance.

## Seal and claim ceiling

All `f84*` pages are forbidden.  The freeze producer reads only the already
published zodiac structural panel, which contains f70--f73.  No f84 image,
description, transcription, or formal row may be retained, displayed, joined,
or scored.

This experiment may establish only whether the complete zodiac panel contains
a transferable left/right visual contrast suitable for a later anonymous
formal association test.  It cannot establish that a label names direction,
pose, a figure, a sign, or any other object; it cannot supply a word, sound,
language, plaintext, meaning, or translation.
