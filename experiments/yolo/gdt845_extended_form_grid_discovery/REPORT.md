# GDT845 — the ee+d gap does not recur under every prefix

**Descriptive discovery: the extended qo arm has attested ee+d combinations,
and its direction differs from the bare/o arms. No confirmatory test.**

The fixed72-cell raw-source inventory contains847 ZL3b occurrences and61occupied
cells. IT2a has60occupied cells, RF1b59. All48old e0/1cells occur separately in
each reading. Among the24e2cells, ZL3b occupies13, IT2a12 and RF1b11. In57of72
cells, all three readings have the same whole form at at least one common locus.

| Prefix | ZL3b ee+d observed / expected | IT2a | RF1b |
|---|---:|---:|---:|
| empty |1 /5.889 |1 /6.628 |1 /4.818 |
| o |1 /3.891 |1 /4.615 |0 /2.122 |
| qo |6 /4.020 |6 /3.475 |4 /2.517 |

Expected counts assume e-length and d-state independence within each fixed
prefix×k/t×ch/sh stratum, then sum the four strata. These are descriptive
marginal expectations, not predictions from a validated language model or
significance tests. They do not adjust for section, hand, folio, line position
or occurrence dependence. The three readings describe one manuscript and must
not be pooled as three replications.

## Concrete source anchors

Four qo-arm loci preserve an exact ee+d whole in all three readings, at the
same group index and with definite spaces on both sides in the saved source:

| Whole | Locus | Group index | Physical folio |
|---|---|---:|---|
| qokcheedy | f104r.33 |2 |f104 |
| qotcheedy | f104v.20 |6 |f104 |
| qotcheedy | f114v.9 |6 |f114 |
| qotcheedy | f115r.10 |9 |f115 |

These are four loci on three physical folios, not four independent folios.
No native image adjudication was performed here. All eight ZL3b ee+d hits
across the three prefixes are in section S. Six have hand3 metadata, two have
unknown-hand marker @. Thus prefix licensing, section/style and sparse
sampling remain competing explanations. We do not infer that adding qo
causes the difference.

All exceptions and reader variants stay visible in HITS.json and CELLS.json.
The bare kcheedy at f107r.20 is ZL3b/IT2a kcheedy versus RF1b tcheedy;
the o-arm otcheedy at f105v.35 is absent from RF1b's exact-word cell.
The qo-arm has additional non-shared qokcheedy/qoksheedy attestations. IT2a
also has qotcheedy on f41r.1. No variant is silently corrected or discarded.

## What changed and what did not

GDT624 already established48e0/1cells, and GDT646 documented bare-arm e2gaps.
This pass adds their complete common72-cell inventory and the fixed conditional
exposure comparison over all three prefixes. The bare/o gap cannot be exported
as an across-prefix ee+d exclusion: the qo arm supplies concrete retained
counterexamples. A general independent Cartesian codebook is not established,
and the differences are too sparse/confounded for a confirmed prefix rule.

The old GDT624 total829 is not replicated as an occurrence count: this
source-native census gives816 ZL3b e0/1hits. It uses exact whole raw groups,
all source kinds and179selectors, while the historical report uses its older
counting/cleaning contract. The13-count difference has not been reconciled;
we claim replication of48-cell occupancy only, not byte-equivalent counts.
All current observed/expected quantities use only this pass's raw-source data.

Next useful decision: inspect the registered full table for whether sufficient
within-section/hand contrasts exist before assigning any effect to the prefix.
That requires a separately declared comparison; no subgroup retuning or new
ending was applied here. Preserve the four exact source anchors and the full
negative-cell inventory. No automatic decoder, numeric interpretation, heat/
moisture/stage wording or confirmed lexeme follows.

## Reproduction and limits

Protocol committed as33b2c1fa before the new guarded source query.179selectors,
96,184selected raw rows,2,398matching rows across the alternate readings.
No new selector/image; f84/f84r rejected by the selector-first source guard.
HITS retains complete matched raw rows and native separators; CELLS includes all
72cells, per-reading counts, physical-folio sets and common-locus multiplicities.
The latter are explicitly NOT general cross-reader token alignment; the four
named anchors were separately checked at their exact source indices.

Run src/run.py for acquisition/counting; src/validate.py independently aggregates
through a regex and checks every cell count, folio set and conditional summary.
Validation passes for source inventory and arithmetic; not vision or semantics.
Binding and staged privacy/scope checks pass separately. The full repository
check retains the known unrelated GDT600/index debt.
