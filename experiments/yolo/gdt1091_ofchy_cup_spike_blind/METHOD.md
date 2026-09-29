# GDT1091 method

The scope, fixed image roster, four-code rubric and decision rule are in
`PREREGISTRATION.md`; five new image admissions are in the dated scope note.
Before download, bind the blind map hash and source metadata. Download official
Yale images to nonpublished temporary filenames `B01`–`B09`, without folio
names. Give each independent reader the same blind files and rubric, without
the mapping or text. Freeze the two tab-separated image-only tables and hash
them before the map is moved into `src/BLIND_MAP.tsv`.

`src/run.py` verifies the map commitment, complete reader tables, source
provenance and four fixed code cells on all nine images, then writes a complete
folio join and one decision. `src/validate.py` replays those checks and result
bytes. The registered primary endpoint is strict cup compatibility; the wider
cup/spike codes are nonselecting sensitivities. Shape-to-word ownership is
still unproved even under the strongest positive result.
