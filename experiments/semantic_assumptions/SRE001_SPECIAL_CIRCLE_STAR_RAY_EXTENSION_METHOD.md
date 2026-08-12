# SRE001 special-circle star-ray ownership extension

## Question

Can the stopped direct star-label ray-count route acquire genuinely new
author-visible ownership data on a second physical folio?

The previous preflight retained 47 strong ray-counted star-label attachments
on f68, but no qualifying ownership device on f70. Its explicit reopen
condition is new source-bound singularly owned, ray-countable star labels on a
second physical folio. SRE001 is a complete visual-capacity census for that
condition. It is not a label-surface, morphology, or meaning test.

## Filler-blind selection

Read only `results/existing_human_exact_locus_annotations.tsv`. Retain a row
iff all of the following hold:

1. its page belongs to physical folio f67, f69, f71, f72, or f73 (the special
   circle folios outside the already resolved f68 and f70 cases);
2. `object_tags` contains both `STAR_OR_SKY` and `LABEL`; and
3. the union of `local_relation_tags` and `unit_relation_tags` contains
   `REL_EXPLICIT_ATTACHMENT`.

Preserve source row order, then inspect targets in SHA-256 order of
`SRE001|<page>|<locus>`. Do not read or serialize any Voynich transcription,
surface, source group, STA member/family, parser root/role, or English gloss.

The frozen source panel contains 24 rows: six f69r/K1, five f72r1/S2, five
f72r2/S0, four f73r/S0, and four f73v/S0. They occupy three physical folios and
four official Yale canvases. Prior exposure to all four full canvases is
disclosed; the target-specific ownership/ray judgments remain prospective.

## Native-visual rubric

Inspect only the source-bound official Yale image. For each target record:

- `SINGULAR_STAR_OWNED_RAY_COUNTABLE`: the inscription is securely localized;
  exactly one drawn star is assigned by an author-visible attachment, bounded
  cell, leader, or unambiguous reserved slot; no equal competing star shares
  the slot; and the complete ray/point count can be read directly.
- `SINGULAR_STAR_OWNED_RAY_UNCOUNTABLE`: singular ownership passes but damage,
  overlap, or resolution prevents a reliable complete ray count.
- `SLOT_OR_GROUP_ONLY`: the inscription belongs only to a sector, annulus,
  star/figure pair, or group with no unique star owner.
- `NON_STAR_OBJECT`: the author-visible owner is a sector, arm, figure, or
  other object rather than one star.
- `LOCALIZATION_UNRESOLVED`: the target inscription cannot be localized
  reliably.

For a countable row, record the integer ray count only after all singular-owner
gates pass. A nearby star selected by distance is not an owner. Human
`star/nymph` wording is a candidate locator, not a positive judgment.

## Capacity gate

The stopped f68 ray-count route may be reopened for a separately registered
association only if one new physical folio satisfies all of:

1. at least eight `SINGULAR_STAR_OWNED_RAY_COUNTABLE` rows;
2. at least two different ray counts;
3. each of at least two ray counts occurs at least three times; and
4. no one logical page supplies more than 75% of its qualifying rows.

Otherwise stop before every Voynich label identity and formal feature. The
three manual readings are alternate readings of one manuscript, never
replications.

## Claim ceiling

Passing this census establishes visual capacity only. It does not establish
that any label encodes ray count, a number, a star name, sound, language,
cipher, plaintext, meaning, or translation.
