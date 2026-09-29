# GDT1090 — `schor` visual search multiplicity

Registered 2026-09-29 before this experiment's text–image join. This is a
**retrospective search audit**, not a prospective semantic test.

GDT765 proposed the complete word `schor` ≈ *Blütenstand* at C1 and listed
its three exact loci. The later GDT1089 word-blind, two-reader image inventory
marks the narrow union `MULTI_UNIT_SPIKE OR SPINY_ROUND_HEAD` on all three
folios. Root chose this union after seeing the image codes and already knew
f22r; the 38 images were selected for GDT1089's other question. GDT1080's
flower/fruit direction test failed. Thus the genuinely unknown fact here is
how many other complete words obtain the same 3/3 image match in this selected
dataset. A crowded deck would lower priority for `schor` as a distinct
reproductive organ word; a sparse deck would keep it a lead, still without
word-to-organ ownership. Neither outcome confirms a translation.

## Frozen scope and comparison

Use the exact 38 physical folios in GDT1089 `BLIND_IMAGE_LIST.tsv`, unchanged
`BLIND_A.tsv` and `BLIND_B.tsv`, and all 179 admitted text page selectors in
GDT631 `PAGE_ALLOWLIST.tsv`. Access the mixed transcription **only** through
`vmanus-exp query-tsv` with selector `page`, repeated explicit allow-values,
columns `edition,page,locus,kind,source_group_index,left_separator,
right_separator,ivtff_group_raw`, and `--forbid-prefix f84`. Count only
`kind=P` ZL3b complete words with left boundary `LINE_START`,
`DEFINITE_SPACE`, or `DRAWING_INTERRUPTION` and right boundary
`DEFINITE_SPACE`, `LINE_END`, or `DRAWING_INTERRUPTION`; exclude uncertain
and unaligned drawing boundaries and all non-prose groups. Do not normalize forms or
change transcription rules. Distinct physical folios are the unit; multiple
occurrences on one folio count once. Check IT2a/RF1b only as a reported
sensitivity, never as independent replications.

For every complete word with at least three distinct GDT1089 image folios,
report its total distinct admitted folios, number of image folios, number
having the fixed union YES in **both** image inventories, and whether **all**
of its image folios match. The primary like-for-like deck is words occurring
on exactly three distinct admitted folios, all three in the image roster.
Count every member of that deck, its 3/3 hits, and each word's folios. The
secondary image-only deck is all words on exactly three image folios, with
their 3/3 hits even if they occur elsewhere in the admitted text. A positional
sensitivity reports how many primary-deck 3/3 hits have a definite
line-initial occurrence on at least two image folios, as `schor` does.

If any of the 38 images lack admitted text, report them and evaluate only the
intersection without silently substituting pages. No new images, target
folios, feature unions, synonyms, thresholds, decoder or source names. Report
the full eligible deck, not hand-picked matches. No probability or
significance claim because the union, word and image roster were selected
after exploration and the search history has no suitable global control.

Decision: if another word in the primary deck also has 3/3, the visual
match is demonstrably nonunique within the fair deck; if none does, `schor`
is rare there but still unowned. A word with more than three imaged folios
all positive is separately salient, not evidence that it has the same
meaning. Flower versus fruit, generic item and image co-presence remain live
alternatives. Known counterexample: the `-shor` radiate-head extension fails
on f13r `torshor`; no substring export is tested here.

Correction log, before any scored output: the first execution aborted at the
assertion that `schor` belongs to the eligible deck. A selector-guarded
inspection of its three already known loci showed f22r.4 has left separator
`DRAWING_INTERRUPTION`; the first draft's boundary list accidentally omitted
this explicit separator. The first run produced no score or artifacts. The
fixed rule above includes **all** aligned drawing interruptions on either
side for **every** word; the six unaligned cases remain excluded. No word or
visual outcome was selected to make this change, but the correction is
post-query and bars a strict prospective label for this experiment.

Budget: 50 minutes total: 10 preparation and registration, 15 guarded query
and join, 10 validation/interpretation, 15 publication. At limit stop scope
expansion and report incomplete work. Dependencies: GDT765 C1 hypothesis,
GDT1089 blind coding, GDT1080 failed directional test, selected 38-image
roster, admitted 179-page transcription. f84/f84r and reserves stay closed.
