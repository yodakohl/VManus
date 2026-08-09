# `cho/che` paragraph-scope capacity audit

## Purpose

Determine, without scoring `o` versus `e`, whether the source-native manual
transcriptions contain enough repeated exact-template events to test whether
the confirmed formal page regime transfers across ZL-editor-marked paragraph
boundaries or varies locally inside those paragraphs.

This is distinct from the published folio-ratio and template inventories. It
does not re-estimate page states, compare outcome rates, or inspect paragraph
effects.

## Frozen inputs

- `results/source_separator_transcription.tsv`, SHA-256
  `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`
- `results/source_separator_transcription_validation.json`, SHA-256
  `8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb`
- `results/source_sta_group_alignment.tsv`, SHA-256
  `f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840`
- `results/source_sta_group_alignment_validation.json`, SHA-256
  `cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd`
- `results/parisel_cho_che_source_audit_validation.json`, SHA-256
  `17009e151704d91f795216eed0913cfece447a396d08234df9af46624f286f3b`

## Score-blind event construction

Use only ZL `P` lines in `CONFIRMED_PROSE` as the paragraph scaffold. Start a
new paragraph at the first line of each panel and every line carrying the
existing `paragraph_start=1` editorial flag. Apply those physical-locus spans
unchanged to IT and RF. The markers are editorial layout judgments, not
authorial semantics.

Collapse numbered panels to their common page side exactly as the external
folio analysis does, while retaining panel and paragraph IDs. Within each
collapsed side, assign each ZL scaffold line to one of four deterministic
line-order quartiles.

For each reading, retain a source group only if:

- its source-aligned primary STA path has zero alternative sites;
- its nearest basic-EVA projection is lowercase `a-z` only;
- it lies on a scaffold locus;
- it contains exactly one `ch/sh` immediately followed by `o/e` site.

Immediately replace that site's `o/e` with `X`. Store no outcome value or
unmasked surface. A primary query is eligible only if its exact
`collapsed-page + masked-template + line-quartile` stratum contains at least
one other source group in the same marked paragraph and at least one source
group in another marked paragraph. Training counts are group counts, so a
query never trains on itself.

Also report the same capacity without a position stratum and with page halves,
but freeze quartiles as the only primary panel. Define a common query key as
the exact `(locus, source-group index, masked template)` present in every
reading's primary panel. Readings remain alternate descriptions, not
replications.

## Gates

- exactly 197 ZL panel records before the compound `fRos` exclusion, then 196
  numeric panel records, 709 marked paragraphs, and 4,024 scaffold lines;
- at least 450 primary queries, 30 physical folios, and 100 marked paragraphs
  per reading;
- at least 300 common all-reading primary query keys on at least 25 physical
  folios;
- every stored query has nonzero same-paragraph and other-paragraph exact-
  template support inside its page and quartile;
- zero `o/e` outcomes and zero unmasked surfaces in outputs;
- no page state, paragraph effect, model score, p-value, or English gloss;
- independent nonimporting reconstruction of the panel and every count.

## Claim ceiling

Passing capacity authorizes preregistering a conditional exact-template
same-paragraph-versus-other-paragraph predictive test with page/template/
position-preserving inference. It does not establish that marked paragraphs
are authorial, that the regime changes or persists at any boundary, or any
sound, word, language, cipher operation, meaning, plaintext, or translation.
