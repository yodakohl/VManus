# GDT211 external source audit — *De balneis Puteolanis*

## Purpose and freeze order

This is the external, readable comparator freeze for GDT211.  It was written
before the q13 formal score was run.  Its purpose is to derive a small record
schema from a known medieval therapeutic-bath text.  It is not a source for
Voynich readings, and no Voynich surface form was consulted when the role
inventory was made.

## Source

The source is the ALIM (Archivio della Latinità Italiana del Medioevo,
Università di Siena) record for Petrus de Ebulo, *De balneis puteolanis*:

- public record: <https://alim.unisi.it/dl/resource/553>
- public text download endpoint: <https://alim-admin.unisi.it/download_txt?id=553>
- ALIM identifier: `553`
- ALIM metadata: author `Petrus de Ebulo`; period `XII`; type `Medicina`;
  2,777 words and 17,991 characters with spaces
- ALIM's stated textual source: M. Hanly, “An edition of Richart Eude’s
  French Translation of Pietro da Eboli’s *De balneis puteolanis*,”
  *Traditio* 51 (1996), 232–254
- retrieved 2026-08-17
- downloaded text SHA-256:
  `397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd`
- downloaded API response SHA-256:
  `a7640d9d3f371a0e59b0fdec7e0702b2c6eccc18c1e1ec5442eae541b29d7828`

The ALIM metadata describes a prologue and 33 numbered compositions.  The
numbered sequence contains 32 bath descriptions and one authorial dedication
(number 31).  The compact inventory therefore retains all 33 numbered items
but excludes the dedication from the bath-record counts.  This distinction is
source-visible and was not selected after looking at q13.

This audit uses the readable Latin only to annotate broad information roles.
It does not claim a new critical edition or copy the source text into the
repository.  The compact paraphrases in the TSV are an audit aid, not a
replacement for the cited edition.

## Frozen role vocabulary

Each numbered composition is marked for the presence of these coarse roles:

- `IDENTITY`: a bath/site name or explicit naming statement;
- `LOCATION_ACCESS`: where the bath is or how it is reached;
- `HYDRAULIC_PHYSICAL`: visible or described water, building, cave, route,
  capacity, heat, or flow organization;
- `INDICATION`: a condition, body region, or claimed therapeutic effect;
- `PROCEDURE_CAUTION`: use, dose, diet, contraindication, preparation, or
  repetition instruction;
- `OUTCOME_TESTIMONY`: narrated case, witness, or explicit reported outcome.

The flags record presence only.  They do not assert that the roles occur in a
fixed order, that every poetic line is a separate field, or that the Voynich
uses the same genre.

## Frozen comparator schema

The source supports the following permissive schema:

```text
BATH_RECORD := IDENTITY
               [LOCATION_ACCESS]
               [HYDRAULIC_PHYSICAL]
               INDICATION
               [PROCEDURE_CAUTION]
               [OUTCOME_TESTIMONY]
```

The square brackets mean optional information, not a textual slot boundary.
The schema deliberately does not encode Latin words, syntax, verse order, or
the meaning of any Voynich unit.

## Pre-target predictions

Only two anonymous q13 predictions are licensed for the next pass:

1. If q13 paragraphs are bath-like records, their first PAGE_HOST is a
   candidate identity/site field and should be less recurrent across physical
   folios than matched continuation-line first PAGE_HOSTs.
2. The remainder of records should draw more heavily on reusable host material
   if it contains shared indication/procedure/physical-description fields.

These are weak architectural predictions.  Paragraph starts are editorial
layout evidence, not translated headings; PAGE_HOST is an opaque formal key,
not a word; and a generic manuscript-wide line-opening effect is a mandatory
alternative explanation.  Failure will reject this proposed record-schema
bridge, not therapeutic balneology as an image-level possibility.

## Claim ceiling

At most, the next pass may say that anonymous q13 record organization is or is
not compatible with a readable medieval bath-entry schema.  It cannot identify
a bath name, disease, body part, procedure, word, morpheme, sound, language,
plaintext, or translation.  No f84 page was used in this source audit.
