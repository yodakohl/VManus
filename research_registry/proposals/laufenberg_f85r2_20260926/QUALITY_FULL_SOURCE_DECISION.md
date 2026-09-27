# Decision before full-source temperament comparison

2026-09-28. This is a bounded independent historical **control**, not a
decipherment trial or new Voynich access. GDT623 oriented `ch` as dry from a
manually selected Clm 667 sample of 27 paired entries, 24 of them dry. Its
own method says that sample is not an unbiased materia-medica census. The
unknown is whether the resulting dry-majority rationale persists when *all*
eligible entries of one complete 1415 work are taken without selecting plants
or target words. GDT626–628 supply a separate ordinal/grade hypothesis, but
this test does not score exact grade-number identity.

Source fixed before aggregate extraction: University College Cork CELT,
[Tadhg Ó Cuinn, *An Irish Materia Medica*, G600005](https://celt.ucc.ie/published/G600005.html),
Part IV (editorial English translation), its numbered entries from the
heading at the printed p.444 through the end, not introduction, Irish text,
Latin apparatus or glossary. The complete HTML was acquired for format
preflight before this decision. It contains 286 detected numbered entry starts
with numbers reaching 292; no quality totals were inspected. Keep the complete
source URL, hash, encoding and a row for every detected start.

Smallest adequate extraction: strip HTML tags/entities per entry; inspect only
the first 320 visible characters after its numbered opening. A row qualifies
when it has exactly one whole-word `hot` or `cold` and exactly one whole-word
`dry`, `moist` or `wet` (last two share the moisture pole). Multiple opposing
terms, missing terms, or a context clearly about a treatment rather than the
drug are excluded and reported; every automated hit is manually audited
before interpretation. No entry is selected because it resembles a Voynich
plant. Retain all four paired categories and coverage. Compare the source
distribution descriptively with GDT623's published 192 strict exact
`qo(k|t)(ch|sh)(y|ey)` tokens and its eight published orientations. Do not
pool alternate Voynich transcriptions or call repeated words independent
entries. Include Clm 667's 19/3/5/0 baseline for contrast.

Decision: if the full source is not dry-majority or the `ch=dry` orientation
loses to its dry/moist reverse under the unchanged total-variation criterion,
remove corpus-frequency support for that working direction. If it remains
dry-majority and wins, retain only a historically compatible *direction*,
not a decoded morpheme; source and Voynich selection can still differ. If
qualification coverage or manual audit is poor, mark the control invalid and
make no semantic change. The same outcomes do not select hot versus cold,
species, grade numerals, attachment or a complete sentence.

Wall-time budget: 55 minutes total: 10 preparation/source check, 20 extraction
and implementation, 15 manual/independent validation, 10 report/publication.
Stop expansion at the budget limit. No new decoder, control corpus, or shifted
window after inspecting outcomes. Known counterexample: GDT623's Herbal-only
temperature reversal and the broad quality-grid rivals remain unresolved.
