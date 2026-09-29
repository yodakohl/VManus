# GDT1089 method

`src/freeze_pairs.py` deterministically regenerates the fixed one-edit and
control tables from GDT1070 and the GDT1087/GDT1088 image-page inventories.
The prerequisite image admissions are in the dated scope note. Capture the
exact official Yale image URL, canvas ID, byte count and SHA-256 for every one
of the 38 folios; do not publish image binaries. The two annotators
independently view those images without access to `FIXED_EDIT1_PAIRS.tsv`,
`FIXED_CONTROLS.tsv` or text-head strings. Their YES/NO/UNKNOWN visual codebook
and pair rule are defined in `PREREGISTRATION.md`.

After both tables are frozen and hashed, join every one of the 25 one-edit
pairs and its 25 preselected same-anchor controls using the same deterministic
pair rule. Report the 14 newly covered targets separately from the 11 already
covered targets. Keep all page/feature unknowns, disagreements and old known
counterexamples. The validator must replay the fixed roster, page set, exact
source hashes, both annotation tables, pair/control coverage and result counts.
Any post-freeze root visual review is a separate sensitivity artifact. A
complete, supported result must include the run source, validator, source
provenance, all decisions, and the claim ceiling.
