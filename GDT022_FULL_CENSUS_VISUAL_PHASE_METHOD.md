# GDT022 full-census visual-anchor / record-phase audit

GDT022 corrects a sampling defect in GDT021.  GDT021 treated
`gdt013_prose_anchor_occurrences.tsv` as an inferential population, but that
file is only a display export: GDT013 retained at most the first 40 prose
occurrences of each selected anchor feature.  GDT021's effects, p-values, and
leave-one-folio statements are therefore superseded.

The replacement uses the same 80 post-selected GDT013 anchors but reconstructs
their complete occurrence sets directly in the frozen GDT016 group-state
inventory.  That inventory contains 15,592 strict all-reading-agreed
confirmed-prose groups on 94 physical folios and contains no f84r row.  No
canonical transcription, image, or f84r payload is opened by this experiment.

For each of eight visually derived role labels, four record contexts are
tested: after any earlier DY checkpoint, immediately after DY, within a field
that eventually closes with DY, and line-final.  Tests are repeated for
SOURCE_FAMILY anchors, RESIDUAL_HOST anchors, and their union (96 cells).
Role labels identify the provenance of the annotated examples that nominated
the formal features; they are not meanings assigned to prose occurrences.

Each conditional randomization fixes page, GDT016 state, and normalized
position quartile.  It fixes the number of anchor members and context outcomes
in every stratum, then convolves the stratum hypergeometric distributions.
The reported p-value is the inclusive two-sided conditional tail.  Bonferroni
over all 96 cells is reported.  Leave-one-physical-folio effects measure
concentration without treating alternate readings as replications.

The ten individual FIGURE anchor features are separately audited for the
immediate-post-DY context against the complete 15,592-group inventory.  This
audit is corrected over ten features and distinguishes a broad anchor-set
effect from one or two selected motifs.

This is permissive YOLO hypothesis generation.  Controls rank a lead rather
than automatically killing it.  The claim ceiling is a complete-census
association between visually nominated formal motifs and an anonymous record
phase.  It establishes no semantic role, referent, morpheme, word, syntax,
sound, language, plaintext, meaning, or translation.

