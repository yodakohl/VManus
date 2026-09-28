# GDT1068 method

The complete frozen contract and prior-exposure disclosure are in
`PREREGISTRATION.md`. This is an exact whole-group/whole-title check, not a
decoder or a wind-name assignment.

`src/run.py` reads the already fixed 12 `raw_title` entries per ZL3b, IT2a
and RF1b from GDT958's `FROZEN_TITLE_VARIANTS.tsv`. It selects f69r from the
mixed cross-transcription TSV only through `./vmanus-exp query-tsv --selector
page --allow f69r`, asking only for locus and the three clean readings. It
checks the expected 49 selected loci before taking f69r.5–20 as outer and
f69r.21–42 as radial items. It splits on written spaces; no edit, variant,
substring, or component transfer is allowed.

For each reading, title and item, it records (a) whether the entire title is a
consecutive sequence in the item and (b) every exact constituent group shared
with the item. Thus all 12×38=456 cells per reading, 1368 total cells, are
accounted for. `src/validate.py` independently rescans the guarded source
and reconstructs all complete and constituent matches. The JSON artifact
retains all six register-by-reading results, including empty matches.

Only a complete literal title match could prioritize a later owner-mapping
test; it would not itself translate the title. Zero matches park this exact
literal bridge. The f69r 12+16 visual wind prior and GDT952/958/1067 decisions
are outside this test.
