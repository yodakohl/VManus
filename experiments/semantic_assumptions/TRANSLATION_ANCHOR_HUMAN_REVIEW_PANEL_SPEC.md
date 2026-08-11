# Translation-anchor human-review panel

## Purpose

Build one compact, source-native review packet for the four unresolved
manuscript locations where a new human observation could create a semantic
anchor.  This is an acquisition aid, not a translation experiment.

The panel must preserve the ZL3b, IT2a, and RF1b readings as alternate
descriptions of one physical manuscript.  It must not combine their readings
as replications, choose a preferred reading, or infer a word value.

## Fixed scope

The panel contains exactly 38 physical loci:

- `f2r.15`, the only documented Voynich-script note under green paint;
- `f57v.6` through `f57v.13`, the four figure-near labels and four radial
  titles in the four-person wheel;
- `f68r2.31`, the complete circular sequence around the bottom Sun medallion;
- the 28 radial labels on f69v in the author-visible cyclic order
  `f69v.7` through `f69v.31`, then `f69v.4` through `f69v.6`.

For each locus, copy the complete raw row content from each available native
manual (`ZL3b-n`, `IT2a-n`, `RF1b-e`).  An absent row is the literal value
`ABSENT`; it is not imputed.  Preserve IVTFF editorial markup verbatim.

Bind the current human exact-locus annotation where one exists.  The four
page-level witness links are recovered from the cached human-curated
Voynich.nu catalogue and must resolve to the exact Yale catalogue links:

- f2r: `https://collections.library.yale.edu/catalog/2002046?child_oid=1006078`
- f57v: `https://collections.library.yale.edu/catalog/2002046?child_oid=1006187`
- f68r2: `https://collections.library.yale.edu/catalog/2002046?child_oid=1006196`
- f69v: `https://collections.library.yale.edu/catalog/2002046?child_oid=1006199`

No image, crop, OCR result, automated visual label, parser root/role, English
gloss, decoder output, or external-claim score enters the panel.

## Descriptive role fields

The role fields are frozen routing descriptions, not lexical readings:

- `COL001_UNDERPAINT`: `f2r.15`; relation grade `DIRECT_ENCLOSURE_UNDER_PAINT`.
- `F57_FIGURE_NEAR`: `f57v.6`--`.9`; relation grade `PROXIMITY_ONLY`.
  The structural homologue positions are recorded as `HOT_POSITION`,
  `MOIST_POSITION`, `COLD_POSITION`, and `DRY_POSITION`.  The `_POSITION`
  suffix is mandatory: these are diagram-role analogies, not translations.
- `F57_RADIAL_TITLE`: `f57v.10`--`.13`; relation grade
  `BETWEEN_FIGURES_PROXIMITY_ONLY`; role value `UNKNOWN`.
- `F68_SUN_RING`: `f68r2.31`; relation grade `DIRECT_CIRCULAR_REGISTER`.
- `F69_ORDERED_28`: the fixed 28 slots; relation grade
  `DIRECT_RADIAL_SLOT`, with only anonymous values `X1.1`--`X1.28`.

## Acquisition questions

Each family receives exactly one request:

- COL001: a second provenance-clean Voynich-script note physically under
  paint with an independently readable colour, or the same complete phrase
  under another green-painted part on a new folio.
- F57: a complete readable homologue preserving the four-person/two-register
  topology, orientation, and explicit slot ownership, or an independent
  Voynich folio repeating the same owned mapping.
- F68: a qualified full diplomatic and palaeographic reading of the complete
  ring, including script identity and uncertainty for the ending, made
  independently of a proposed Sun gloss.
- F69: a second independently fixed 28-item roster or an authorial readable
  slot legend that fixes start, direction, and all values without post-hoc
  spelling selection.

## Output and ceiling

Write one TSV, one canonical JSON summary, and one short report.  The summary
must report 38 physical loci, 113 present reading rows, one absent IT2a row,
four anchor families, and four official witness URLs.

The only permitted conclusion is:

> A compact human-review packet now exposes the exact unresolved physical
> records and the observation needed to reopen each route.

It supplies no word, morpheme, sound, language, cipher operation, plaintext,
meaning, or translation.
