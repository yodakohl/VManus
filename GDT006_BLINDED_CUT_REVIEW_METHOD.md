# GDT006 blinded within-group cut review

Final status: **STOP_LOCALIZATION_CAPACITY_3_OF_34_NO_BLIND_REVIEW**.

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

GDT006 is exploratory and postselected. A target-control difference could
have nominated a frozen human-replication test; it could not establish
grapheme boundaries, morphemes, linguistic slots, language, meaning, or
translation. f84r remains sealed.

## Capacity outcome

The source-aware localizer audited all 34 registered probes. Three target cuts
were securely localized, 31 probes were unresolved, and no control cut was
securely localized. Five control display offsets fall inside a single STA sign
and therefore do not define the source-sign boundary that the physical test
requires. The audit also proved that two earlier GDT004 target boxes were on
the wrong physical content.

Every row in `gdt006_cut_localizations.tsv` is an
`AI_DIRECT_VISUAL_OBSERVATION`; localization is visible geometry, not a
transcription, spacing class, or interpretation.

A fresh `fork_turns=none` reviewer had been instantiated, but the provisional
packet was withdrawn as soon as the localization defects were found. The
reviewer produced zero calls and never received a valid final matched packet.
No score was computed. This capacity stop corrects GDT004/GDT005 provenance;
it is not evidence for or against fine spacing at the proposed cuts.
