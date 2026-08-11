# f17r / f116v Voynich-surface recurrence audit

Date: 2026-08-11

This is a bounded descriptive follow-up to the native visual finding that
Voynich-style and plain-script-looking writing share one line on f17r and
f116v. The visual result was opened before this recurrence question, so this
is not a preregistered confirmatory experiment.

## Question

Do the four manually transcribed Voynich-style marginal forms recur as exact
whitespace-delimited surfaces elsewhere in the manuscript?

- f116v.1: `oror sheey`
- f17r.13: `oteeeon oiil`

## Input and unit

The sole input is
`results/pre_grounding_interlinear.tsv`, SHA-256
`8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43`.
It contains 15,960 reading rows. ZL3b, IT2a, and RF1b are alternate readings
of one manuscript; the primary recurrence unit is the physical locus, not the
reading row.

The audit uses only the literal `surface` column and the descriptive
`grammar_scope`, `kind`, and `code` fields. Formal roots, roles, parser
assignments, English labels, and proposed readings of the adjacent plain
script are prohibited.

## Exact operations

1. Split each `surface` on whitespace.
2. Count exact token occurrences, reading rows, physical loci, and pages for
   `oror`, `sheey`, `oteeeon`, and `oiil`.
3. Partition counts by `grammar_scope` and edition.
4. Count the two exact adjacent pairs and unordered same-row co-occurrence.
5. Treat the f17r/f116v target rows as ordinary observations, but report
   separately whether recurrence occurs in `CONFIRMED_PROSE` elsewhere.

No normalization, edit distance, family mapping, root reduction, fuzzy match,
or reading agreement score is permitted.

## Claim ceiling

A positive recurrence establishes only that a marginal surface is also used
in the main manuscript transcription. It cannot establish that the marginal
line quotes, glosses, translates, explains, or deciphers the adjacent plain
script. A unique surface is merely unattested elsewhere in this frozen
interlinear; it is not thereby a foreign word, name, or readable plaintext.
