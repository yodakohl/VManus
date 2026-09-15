# Geomantic one-substitution class constraint: bounded review

**Date:** 2026-09-15. **Scope:** source and frozen GDT957/GDT959 artefact review only. No new manuscript material, image, key search, or experiment was opened.

The concrete f66r forms differ by transcription. In the complete IT2a list, the only equal-length pair at Hamming distance one is `rary`/`fary` (positions 1 and 8). The ZL3b and RF1b readings instead contain the known pair `saly`/`salf` (positions 6 and 7), but those editions have two other unknown f66r positions and therefore are not complete 15-label lists. IT2a has `syly`/`salf` at those positions, which differs in two positions. This edition distinction must be fixed before treating any pair as a protocol object; silently substituting `saly` for IT2a `syly` would be a transcription repair.

The primary GDT957 report assigns the illustrative names as follows: IT2a f66r.6 `syly` and f66r.7 `salf`; the ZL3b/RF1b forms at the same loci are `saly` and `salf`. The GDT959 source tables are Turner's 1655 late Agrippa-attributed witness, not an early-source certification. Their frozen figure index gives **Puella = 11** and **Albus = 2**, with these elemental classes:

| figure | A sign/course | B preferred planetary/figure | C vulgar |
|---|---|---|---|
| Puella | EARTH | AIR | WATER |
| Albus | AIR | EARTH | WATER |

Therefore the selected GDT959 report case `TOP_DOWN 18557 B` maps f66r.6 `syly` to Puella and f66r.7 `salf` to Albus; under B these are AIR and EARTH, so the proposed same-class condition fails for that concrete case. The source reports `TOP_DOWN 18621 B` as Carcer/Albus for those positions; both are EARTH under B, showing that a passing selected case can occur without yielding a universal constraint. No positive pilot should be claimed.

As an arithmetic cross-check, the frozen GDT957 surviving-calculation table contains 376 rows across the six edition/direction cases. I performed this diagnostic before GDT964 registration, so it is additional prior exposure rather than a blind prediction. The initial pass failed to reverse physical positions for BOTTOM_UP; the corrected mapping is shown below. Comparing the relevant physical positions against the three GDT959 tables gives:

| physical positional pair | A same class | B same class | C same class | same in all A/B/C |
|---|---:|---:|---:|---:|
| positions 1/8 (`rary`/`fary` in complete IT2a) | 46/376 | 58/376 | 74/376 | 3/376 |
| positions 6/7 (`saly`/`salf`, ZL3b/RF1b applicable rows only) | 51/344 | 83/344 | 65/344 | 2/344 |

These corrected counts map a physical top-down position `p` to output position `p` for TOP_DOWN and `16-p` for BOTTOM_UP: physical 1/8 becomes output 15/8 in BOTTOM_UP, and physical 6/7 becomes output 10/9. They are descriptive checks over correlated hypothetical calculations, not independent observations or significance evidence. The second row uses only the 344 ZL3b/RF1b rows where `saly` and `salf` are actually the known forms. The earlier pre-registration review counted output positions 1/8 and 6/7 without this BOTTOM_UP reversal; its earlier figures (67/51/40 and 53/74/64, with 3 and 4 all-table survivors) are invalid as physical-pair pilot results and must be disclosed as a superseded diagnostic, not published as findings.

## Logical distinction from the closed minimal-pair family

The proposed GDT964 predicate is a hypothetical semantic class constraint: for each fixed GDT957 key and each frozen GDT959 table, the figures predicted at two source-label positions must belong to the same named elemental class. It does not state that the two Voynich forms are synonymous, allographic, or one morpheme, but it does hypothesize a same-class relation between their whole-label readings. It is a relation between positions, frozen arithmetic outputs, and a late historical classification.

The archived `MINIMAL_PAIRS_ALLOGRAPHY_AND_SYNONYMS` family is a different claim about recurring Voynich substitutions and semantic identity/root-class collapse. Its closed-route row records “too few disjoint substitutions; H/e position adaptation and root-class collapses fail confirmation,” with reopening only for a new recurring substitution on multiple disjoint page pairs with an untouched holdout. The referenced primary report `semantic_assumptions/results/contrastive_minimal_pair_semantic_bridge_report.md` is absent from this checkout; no stronger historical conclusion is recoverable from that missing file. The new class predicate therefore does not by itself reopen that family or satisfy its reopening condition.

A same-class result could become a predeclared mathematical consequence test if the exact pair set, source table, key set, direction handling, and unknown policy were fixed before evaluating the 376 rows. A surviving result would still be only compatibility with a named class relation. It would not identify a word meaning. A failed result would falsify that narrow class constraint, not the underlying geomantic arithmetic or the old allograph/synonym family.

## Contract risks and source uncertainty

- The 957 report explicitly warns that the 15 distinct IT2a names are renaming-invariant under the arithmetic. Adding external names/classes after seeing the surviving keys breaks that invariance and needs its own public pre-registration.
- `saly`/`syly` is a cross-edition transcription difference at the same locus. The pair universe must not combine forms from different editions without an explicit rule. The same risk occurs for other variants such as `dara`/`dary` and `ykcol`/`ykeol`.
- GDT959 A retains printed `Amitia` unresolved; its possible Amissio class is an explicit upper completion, not a fact. Unknown source classes must remain unknown rather than be assigned by convenience.
- Turner 1655 supplies three competing elemental classifications (A, preferred B, and C). Choosing B because it makes a selected pair agree would be circular; checking all three is a source-uncertainty disclosure, not replication.
- All 376 rows derive from one f66r construction and are correlated across directions and editions. They cannot support a frequency or significance claim. Known and unknown transcription rows must remain separate.
- `Puella`/`Albus` are figure names in the historical table. Their class assignments cannot be promoted to `saly`, `syly`, or `salf` meanings, and the source provides no evidence that one-character variation encodes elemental class.

**Disposition:** GDT964 has now frozen the pair universe, separate edition handling, all 105 per-edition pairs, `UNKNOWN_TARGET` policy, and common source completion before evaluation. The earlier review was exposed before registration and its un-reversed BOTTOM_UP counts are invalid; the corrected diagnostic above is retained only for disclosure. The registered test may proceed as a bounded stress test of the hypothetical same-class relation. Any outcome remains conditional on GDT957/GDT959, carries no confirmed word or elemental morpheme, and does not reopen the closed synonym/allograph family.
