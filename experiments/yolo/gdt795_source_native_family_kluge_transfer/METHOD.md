# GDT795 method

## Question

Can a majority-supported source-family rendering of every one of the 101
already admitted Kluge-A circle labels recover several catalogue positions or
relative spacings across held physical folios, and does it improve on the
visible complete label string enough to seed a concrete contextual codebook?

## Scope and inputs

The manuscript panel is fixed by GDT794: 101 label loci in eleven arrays on
f70, f71 and f72. No new page, image or transcription is opened. The exact
locus list is taken from the GDT794 atlas before the mixed source is queried.

`source_sta_group_alignment.tsv` is mixed and contains f84 material. The
builder may access it only by invoking `./vmanus-exp query-tsv` with
`selector=locus`, the 101 explicit admitted values, and the exact columns in
`src/GUARDED_QUERY_SPECS.tsv`. The selector is rejected before the remaining
fields are materialized. The three editions are alternate readings of one
manuscript, never independent evidence.

For each locus, source groups are ordered by `source_group_index` and their
`primary_sta_families` are joined with `|`. A boundary-bearing sequence is
accepted when two or three editions agree exactly. Its compact companion
removes `|`. The longest prefix selected in GDT233 is then separated from the
majority sequence; the remainder is only a formal residual.

## Comparisons

1. Inventory all majority sequences, reading agreement and group boundaries.
2. Count recurring signatures, distinct visible surfaces, folios and Kluge-A
   positions.
3. Leave one physical folio out. For exact surface, boundary-family, compact-
   family, transferred-prefix and residual keys, record coverage, any training
   position at exact A or within one A, and a single circular-mean prediction.
4. Rank all 99 targets whose A-code exists on another folio by normalized edit
   similarity of the boundary-family, compact-family and visible surface.
5. On the fifteen-member f70v1/f71v/f72r1 template and thirty-member
   f70v2/f72r2 template, scan one rotation/reflection per whole diagram. No
   form receives its own phase. Also inspect the sole unambiguous recurring
   signature pair for relative-distance preservation.
6. Calibrate exact and similarity scores by deterministic within-diagram A-code
   permutations. These are scale checks, not semantic probabilities.

## Meaning rule

A concrete contextual card may survive when the same exact family points to
the same or adjacent T15 member on another physical folio. A family letter,
prefix or residual never becomes a word, sound or freely compositional root.
A calendar/day/degree reading would require several different signatures to
recover several held positions under one shared transformation. Otherwise the
primary model remains learned member designations carried by a broad graphical
label layer.

## Claim ceiling

GDT795 may identify formal family agreement, contextual member-position cards,
weak template texture and a renderer/codebook architecture. It cannot confirm
a word, morpheme, letter value, number, day, degree, planet, star, substance,
action, disease, treatment, language, cipher or plaintext translation.
