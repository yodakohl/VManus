# GDT006 blinded within-group cut review

Status before review: **FROZEN REVIEW RUBRIC; SOURCE-AWARE LOCALIZATION IN
PROGRESS; REVIEWER UNASSIGNED**.

GDT006 refines GDT005's coarse matched control without changing its 17 target
and 17 control cuts. It asks whether the proposed target cuts differ from
mechanically selected same-line pseudo-cuts in a fresh crop-only review.

## Role separation

1. A source-aware localizer sees the registered loci, surfaces, and cut
   offsets. The localizer marks the intended physical inter-ink-unit position
   and records `LOCALIZED` or `LOCALIZATION_UNRESOLVED`. The localizer makes no
   spacing or stroke judgment.
2. A fresh reviewer is created with `fork_turns=none`. The reviewer receives
   only randomly named marked crops, opaque IDs, and the rubric below: no
   folio, locus, transcription, cut offset, target/control identity, operation,
   hypothesis, GDT artifact, or private join.
3. Only after all review calls are frozen are opaque IDs joined to the
   target/control identities.

The workflow is role-blind rather than cryptographically person-blind: all
agents share a workspace, so reviewer nonaccess to the private join remains a
recorded workflow constraint. Exact delivered crop hashes and the opaque
worklist are retained.

## Review rubric

The red vertical marker identifies one registered cut. Ignore the marker ink
itself and classify the underlying manuscript geometry:

- `INK_TOUCH_OR_CROSSING`: manuscript ink visibly touches/crosses the marked
  inter-unit position;
- `NARROW_VISIBLE_GAP`: a small but visible parchment gap;
- `ORDINARY_VISIBLE_GAP`: an unexceptional local inter-unit gap;
- `WIDE_VISIBLE_GAP`: conspicuously wider than ordinary inter-unit spacing in
  the crop but not a source-group separator;
- `UNRESOLVED`: marker placement, fading, damage, crop, or unit mapping does
  not support a stable call.

The reviewer also records confidence and one neutral sentence. No OCR,
transcription inference, glyph naming, or semantic interpretation is allowed.

## Exploratory score

Map resolved calls to the ordered spacing score `0,1,2,3`. Report target and
control distributions, mean difference, median difference, and paired signed
differences where both arms of a pair/cut role resolve. An exact within-pair
swap distribution is diagnostic, not confirmatory. `UNRESOLVED` remains
missing and all localization/review attrition is reported.

GDT006 is exploratory and postselected. It does not modify GDT003, GDT004, or
GDT005. A target-control difference may nominate a frozen human-replication
test; it cannot establish grapheme boundaries, morphemes, linguistic slots,
language, meaning, or translation. f84r remains sealed.
