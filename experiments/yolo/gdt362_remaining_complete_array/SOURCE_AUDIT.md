# GDT362 source-only array census

The exact human atlas contains the following non-f84 units with at least four
plant-label loci after excluding already used f89/f99/f100/f102 folios:

| folio | unit | mapped loci | source capacity | disposition |
|---|---|---:|---|---|
| f88r | L1 | 5 | source says 6 labels/5 plants; first inscription is editorially C1 | exclude boundary-uncertain |
| f88r | L2 | 5 | source says 6 labels; first inscription is editorially C2 | exclude boundary-uncertain |
| f88v | L1 | 4 | source says 5 labels/4 plants; first inscription is editorially C1 | exclude boundary-uncertain |
| f101v2 | L1 | 8 | source says 9 plants/9 labels | exclude incomplete locus set |
| f101v2 | L2 | 9 | source says 9 plants/9 labels | retain complete array |

The retained loci are `.10`–`.18` in their source order. Provenance is
`transcription/sources/Stolfi_text25e1-52.evt` through
`existing_human_exact_locus_annotations.tsv`. These are source descriptions,
not independent witnesses and not ownership assertions.

The freeze producer loads only the human annotation table under a raw selector
guard. It does not load a transcription, family, surface, GDT360 join, or f84
row.
