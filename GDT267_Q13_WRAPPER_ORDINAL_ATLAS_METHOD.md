# GDT267 — q13 wrapper/record-ordinal atlas

## Question

GDT265 found a large but search-adjusted-borderline wrapper signal for the
earlier versus later eligible q13 record.  GDT267 identifies which fixed
wrapper categories carry it.  This is a constructional-placement test, not a
semantic interpretation.

## Panel and statistics

Use the unchanged nine-page/eighteen-record GDT227 panel.  For each page and
each of the eight observed wrapper values (`NONE`, `ch`, `che`, `d`, `q`, `s`,
`sh`, `t`), compute wrapper occurrences per source group in the earlier and
later eligible record.  The primary page effect is the unweighted paired rate
difference `EARLIER - LATER`, so record length is normalized before pages are
combined.

For each wrapper report mean difference, positive/negative/tied pages,
leave-one-page range, a page-stratified Mantel–Haenszel odds ratio, correlation
with the log earlier/later group-count ratio, and held-page direction accuracy
where the expected sign is learned from the other eight pages.

The exact null enumerates all `2^9 = 512` page-level sign flips.  A wrapper's
statistic is `abs(sum(diff))/sqrt(sum(diff^2))`; the denominator is invariant
under sign flips.  Local two-sided and max-eight inclusive p-values use the
same worlds.

## Claim ceiling

An association licenses only a q13 record-placement description such as
“q-wrapped rendering is enriched in the earlier eligible record.”  It does not
make `q` a word, phoneme, morpheme, topic, operation, or semantic operator.
The experiment uses only the already published f84-free GDT227 interlinear and
performs no new f84r access.
