# GDT155 source audit — readable medieval abbreviation controls

## CoReMA Ste1

- Object: `o:corema.ste1`, *Sterzing, Stadtarchiv,
  Miszellaneen-Handschrift*, no shelfmark.
- Stable object: <https://gams.uni-graz.at/o:corema.ste1>
- TEI datastream: <https://gams.uni-graz.at/o:corema.ste1/TEI_SOURCE>
- Citation supplied by the edition: Astrid Böhm and Helmut W. Klug (2021),
  transcription of Ste1 in *CoReMA — Cooking Recipes of the Middle Ages*,
  GAMS PID `o:corema.ste1`, handle `11471/562.10.4082`.
- Manuscript date: first quarter of the fifteenth century (`1400–1425`) in the
  TEI manuscript description.  Watermark strata cited there include
  `1410–1416`, `1418–1420`, and `1422–1425` ranges.
- Language: Bavarian/German in the TEI manuscript description.
- Text license: CC BY 4.0.  Facsimiles have a separate CC BY-NC-SA 4.0 license;
  GDT155 downloads no facsimiles.
- Frozen source SHA-256: `3db06c80345e584e5b6af7e062af839964312b92bcf1edb8b88aa05110024df6`.
- Relevant capacity: two TEI `seg` records, 33 `abbr` elements, and 33 `ex`
  expansion nodes.  The public transcription describes preceding botanical
  and hide-processing material and exposes two culinary/technical procedures.

The CoReMA interface calls its display “slightly normalized,” while the TEI
edition statement calls the source a hyperdiplomatic base transcription.
GDT155 therefore derives diplomatic and expanded strings from the TEI element
structure and does not claim that the display is an untouched grapheme-level
facsimile.

## Nuremberg Letterbooks

- Dataset: Mayr et al., *Nuremberg Letterbooks: A Multi-Transcriptional
  Dataset of Early 15th Century Manuscripts for Document Analysis*, v1.
- Zenodo record and DOI: <https://doi.org/10.5281/zenodo.13881575>.
- Scholarly article: Mayr et al., *Scientific Data* 12, 811 (2025),
  <https://doi.org/10.1038/s41597-025-05144-z>.
- Supporting diplomatic-HTR methods paper: Mayr et al., *Multimedia Tools and
  Applications* 84 (2025), 39107–39122,
  <https://doi.org/10.1007/s11042-024-20545-9>.
- Holdings/scope: Nuremberg council letterbooks 2–5, 1408–1423.  The scholarly
  description identifies them as registers of outgoing city-council letters.
- License: CC BY 4.0 in the Zenodo API record.
- Frozen `labels.zip`: 262,212,368 bytes; official MD5
  `ce2c6150d9fc45ac4b4ea2a439b7aa8e`; computed SHA-256
  `59e5264acb4546477567e78c8b3d444c472f1a0a5256ee0ee7d0407a70904652`.
- Relevant capacity independently reconstructed from the archive: 3,176
  diplomatic/regularized XML records, 1,673 distinct page-image identifiers,
  48,337 diplomatic lines, 479,879 whitespace-delimited surface groups, and
  119,031 `expan` sites.  Book record counts are 465/1,064/556/1,091 for
  books 2/3/4/5.

Each PAGE-XML record contains diplomatic TextLine Unicode in physical reading
order and a separate regularized document division.  Editorially supplied
characters are children of `ex` inside `expan`.  The methods paper explicitly
distinguishes diplomatic text with and without expanded abbreviations and
reports that book 2 was used as its difficult held test set.  GDT155 does not
use the published HTR predictions or manuscript images; it uses the human-
prepared transcription labels.

## Source decision

Both controls are admitted.  Nuremberg is the powered abbreviation-resolution
and record-retrieval control.  Ste1 is an independently edited, period-matched,
technical-recipe relevance check with low sample capacity.  Neither corpus is
a comparator for language identity, and neither supplies a Voynich lexicon.
