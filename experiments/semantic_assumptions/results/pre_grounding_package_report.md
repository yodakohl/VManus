# Pre-grounding structural information package

> **Correction, 2026-08-09:** this package is complete for manual-transcription
> loci and literal `surface`, but the root/role/formal columns are a partial
> formal parse. They omit 3,838 complete surface groups on 2,833
> reading-specific rows. See
> `pre_grounding_surface_coverage_correction_report.md` and
> `pre_grounding_surface_residual_atlas.tsv`. The original generated text below
> is retained for provenance; “complete interlinear” must not be read as
> complete formal coverage.

Decision: **PRE_GROUNDING_INFORMATION_PACKAGE_COMPLETE**.

This clean package contains every available manual-transcription locus and no
English lexical gloss.  Confirmed prose grammar is kept separate from
diagnostic projections on labels and other non-prose text.  ZL3b, IT2a, and
RF1b remain alternate readings of the same physical loci.

| artifact | rows | purpose |
|---|---:|---|
| `pre_grounding_interlinear.tsv` | 15960 | complete reading-specific surface; partial retained-node root/role interlinear |
| `pre_grounding_locus_atlas.tsv` | 5380 | physical-locus agreement and uncertainty across readings |
| `pre_grounding_root_atlas.tsv` | 636 | root occurrence, role, boundary, neighbor and tuple-partner profiles |
| `pre_grounding_tuple_atlas.tsv` | 2835 | exact root-tuple inventory and hybrid-coverage state |
| `pre_grounding_relation_atlas.tsv` | 13559 | all prose adjacent-tuple counts and role-edge profiles |

Grammar scopes: {'DIAGNOSTIC_NONPROSE': 3868, 'CONFIRMED_PROSE': 12092}.  Reading agreement states:
{'EXACT_SURFACE': 1305, 'EXACT_ROOT_SEQUENCE': 466, 'READING_DISAGREEMENT': 3044, 'ROLE_SEQUENCE_ONLY': 389, 'MISSING_READING': 176}.

The hybrid 95% layer contains **21 candidate component atoms**
and **95 exact exceptions**.  `COMP`, `EXACT`, and `OPEN` in
the interlinear are acquisition states, not morphemes, words, or meanings.

Pair counts and non-prose role projections are diagnostic inventories.  Only
the six role transitions listed in the manifest inherit confirmed status, and
the aggregate adjacency relation—not each listed lexical pair—is confirmed.

The package plus its corrected literal residual atlas is the input boundary for
any later manually authored image/grammar hypothesis: a proposed meaning must
survive all surface occurrences, parsed formal roles, readings, sections, and
counterexamples shown here. No OCR,
automated image recognition, dictionary, contextual overlay, or proposed
English gloss was loaded.
