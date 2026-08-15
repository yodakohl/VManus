# GDT158 source audit — structured medieval controls

## Augsburg municipal accounts

- Dataset: Dieter Voigt, *Die Augsburger Baumeisterbücher von 1402 bis 1440
  [elektronischer Anhang]*, Universität Augsburg research data (2022).
- Landing page: <https://opus.bibliothek.uni-augsburg.de/opus4/frontdoor/index/index/docId/98153>
- Frozen workbook URL: <https://opus.bibliothek.uni-augsburg.de/opus4/files/98153/Augsburger_Baumeisterb%C3%BCcher_1320_1440.xlsx>
- Source description: the workbook covers the surviving Augsburg financial
  books through 1440 and exposes a `Gesamt_Übersicht` with the original entry,
  year, folio, date and accounting metadata.
- Frozen SHA-256: `bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1`.
- GDT158 scope: every nonempty `Originaltext` row dated 1402–1425, without
  selecting an account, topic, spelling, or outcome. Capacity is 22,071 entries,
  18 represented years, 1,817 year+folio parents and 281,557 whitespace groups.
- Boundary caveat: the workbook row is an editorial account-entry unit. It is
  strong record structure, but it is not asserted to reproduce an original
  physical line break or every manuscript abbreviation mark.
- Redistribution: the workbook is fetched from its public institutional
  landing page and hash-verified; it is not copied into this repository.

The source type and structured-entry character of the edition are also
documented by the scholarly digital-edition project and its review: the
accounts cover Augsburg income/expenditure, and the online edition assigns
stable entry and line identifiers. Those descriptions establish provenance;
they do not supply a positive target statistic.

## Nuremberg council letterbooks

GDT158 reuses the exact GDT155 frozen export, not the source archive directly.
The public dataset is Mayr et al., *Nuremberg Letterbooks: A
Multi-Transcriptional Dataset of Early 15th Century Manuscripts for Document
Analysis*, v1, council letterbooks 2–5 (1408–1423), DOI
<https://doi.org/10.5281/zenodo.13881575>, CC BY 4.0. GDT155 independently
reconstructed 3,176 outgoing-letter/register records and 48,337 physical text
lines. PAGE-XML TextLine order and document divisions are retained.

Nuremberg is included to anchor the already-calibrated abbreviation effect and
to test authentic letter/register boundaries. GDT158 does not relearn or tune
the GDT157 expansion-to-diplomatic channel.

## Ste1 technical recipes

GDT158 reuses the exact GDT155 frozen export of CoReMA object `o:corema.ste1`,
*Sterzing, Stadtarchiv, Miszellaneen-Handschrift Ste1*, dated 1400–1425 in its
TEI manuscript description, Bavarian German, CC BY 4.0 text:
<https://gams.uni-graz.at/o:corema.ste1>. The two admitted TEI segments are
technical/culinary procedures with 10 retained line rows and 33 abbreviation
sites and 111 diplomatic whitespace groups. They provide genre relevance but too little data for a powered
operation-algebra conclusion.

## Freeze decision

All three controls are admitted before residual scoring. Augsburg is the new
powered accounting transfer; Nuremberg is the powered structured-register and
abbreviation anchor; Ste1 is a low-capacity technical-recipe sensitivity. No
other corpus will be added after viewing scores. No Voynich source or f84r
payload is used.
