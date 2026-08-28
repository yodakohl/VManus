# GDT605 method

## Input and split

The page allow-list is taken from GDT327. ZL3b rows are materialized only by
`./vmanus-exp query-tsv` with all 180 page values explicit,
`--forbid-prefix f84`, and the columns
`page,locus,line_number,section,language,hand,eva_clean,ivtff_raw`.
The guarded export has 4,165 rows and SHA-256
`d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9`.
The unchanged GDT604 physical-folio split supplies 68 training and 23 held
folios. f84 and f84r are absent.

## Source separators

IVTFF `.` is called certain, `,` uncertain, and `<->`/`<~>` a drawing
interruption. Editorial markup is normalized and a row is retained only when
its resulting token sequence equals guarded `eva_clean` exactly. This resolves
4,151/4,165 rows; fourteen marked rows remain outside the separator analysis.

For the first diagnostic, all observed intra-line spaces are erased. The
training lines receive the nine composite collapses used by the 2026 unit
analysis (`cth`, `ckh`, `cph`, `cfh`, `ch`, `sh`, `iin`, `in`, `ee`) and 64
deterministic byte-pair merges. Frozen rules are applied to held lines. An
observed source separator is crossed when it falls inside, rather than between,
the learned units.

The production inventory then joins only uncertain separators. Certain spaces
and drawing interruptions become hard chunk boundaries. The same 64 merges are
learned on training chunks and applied unchanged to held chunks.

## Narrow letter attack

As a deliberately restrictive check, each of the 98 production units is mapped
to exactly one plaintext letter with the GDT602 capacity-constrained homophone
solver. Latin and Old Italian each use a real four-gram model and a matched
within-chunk order-destroyed model. Seeds 11, 29 and 47 are trained on the 68
folios; all typicality and agreement values are read on the 23 held folios.

This attack can reject only one-unit-to-one-letter substitution. The open model
allows variable outputs: letters/homophones, double letters, two- or
three-letter syllables, nulls and a small whole-word nomenclator.

## Historical scale

Domnina's reconstruction of an early Tranchedini nomenclator reports an
approximately 1453 inventory of 81 signs: 36 letter signs, four double-letter
signs, one null, thirty syllable signs and eleven word signs. The later system
expanded substantially. This is a category-and-capacity analogue, not a claim
that Tranchedini's key is the Voynich key. Source:
<https://ep.liu.se/ecp/149/007/ecp18149007.pdf>.
