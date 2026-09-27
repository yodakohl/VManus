# GDT1057 method — complete-source temperament direction

## Question and predecessors

Does GDT623's working `ch=DRY` direction survive a whole-work historical
frequency comparator? GDT623 compared 192 strict Voynich forms with 27
manually selected Clm 667 entries (19 hot/dry, 3 hot/moist, 5 cold/dry,
0 cold/moist) and explicitly said this was not an unbiased census. GDT626–628
add a provisional degree/quantity reading; this run does not score it.
The separate decision note is `research_registry/proposals/laufenberg_f85r2_20260926/QUALITY_FULL_SOURCE_DECISION.md`.

## Inputs and extraction

Use exactly UCC CELT `https://celt.ucc.ie/published/G600005.html`, complete
Part IV editorial English translation of Tadhg Ó Cuinn's 1415 work. Identify
the third exact `<h2>An Irish Materia Medica</h2>` as Part IV start; take
every following `<p> N.` numbered opening through end of document. Keep every
detected entry and its original number, source line, SHA256 of the first
320 visible characters after HTML stripping/entity decoding, and qualification
reason. Do not republish the source's 320-character opening snippets.
The raw downloaded HTML remains a disposable runtime file; its SHA256 and
URL are output. The extract covers one source work, not independent witnesses.

An automatic row qualifies only if its first 320 visible characters contain
exactly one whole-word HOT/COLD and exactly one whole-word DRY/MOIST/WET;
MOIST and WET are one pole. All such rows undergo native text audit before
the result is interpreted. A treatment/patient/environment mention is not a
drug complexion and must be excluded with its reason; nothing is silently
repaired by lengthening the window. Ambiguous or missing entries stay in the
denominator and table.

Read GDT623's published `ORIENTATION_FREQUENCY_COMPARISON.tsv`, exact
`ALL_SAFE_NO_F1R`/`EXACT_Y_EY` rows. These are 192 source tokens, not 192
independent plants; only one transcription is used. Keep all eight published
assignments and four category counts; recompute one full-source smoothed TV
for every unchanged assignment. Use add-0.5 smoothing to four categories on
both sides, matching GDT623's `smoothed()` function. No image identification,
new Voynich selector, new word key, decoder or held-page access.

## Decision and ceiling

If audited whole-source dry is not a majority or another orientation outranks
the inherited `ch=DRY` assignment, remove this frequency rationale for the
working direction. If `ch=DRY` remains first, retain it as a historically
compatible orientation only. If automatic classification is unreliable or
source coverage poor, report an invalid control. This is descriptive and
cannot identify a Voynich word, person, plant, grade, language or plaintext.
