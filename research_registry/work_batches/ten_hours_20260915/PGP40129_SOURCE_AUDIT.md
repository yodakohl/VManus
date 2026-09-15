# PGP40129 source-only audit

Date: 2026-09-15. Source: T-S Ar.43.225, PGP40129, Avetisyan's 2022 edition.
Scope: source boundaries, transcription units, and limits of the source witness.
No target text, target fitting, decoder, or other manuscript data was inspected.

## Decision

The proposed **three head-bounded records are supported** by the PGP
transcription and the placement of the heads in the two cached manuscript
images. Their exact boundaries are below. They are complete under the declared
rule “include a surviving named head and continue to the next named head.”
This does not certify every editorial reading or establish the date of copying.
Source: [PGP40129 edition and images](https://geniza.princeton.edu/en/documents/40129/).

| Record | Inclusive start | Exclusive stop | Required treatment |
| --- | --- | --- | --- |
| Peach | recto 5, head `אלכוך` | recto 13, before pomegranate head `אלרמֹאן` | Retain the preceding words on recto 13 as peach. |
| Pomegranate | recto 13, at its head | verso 5, before quince head `אלספרגֹל` | Continue across the leaf turn, including the Hippocrates passage. |
| Quince | verso 5, at its head | verso 15, before apple head `אלתֹפאחֹ` | Include all of verso 14; it precedes the next head. |

Apricot has no surviving initial head on this leaf and begins in continuation.
Apple has a surviving head but no following head or complete endpoint here;
the last main-text line continues syntactically. The apple marginal note is
separate and incomplete. Neither provides a fourth complete record by this rule.

The English translation is selective. It omits the intervening peach material
at recto 7–11, the pomegranate continuation at verso 1–5, and the quince text
after the first sentence of verso 13 through verso 14. Its printed “5–13” label
for quince therefore cannot define the complete source span. The PGP catalog
description mentions tamarind, but the selected named entry is quince according
to both the transcription and Avetisyan's translation. Use the actual heads,
not the catalog's illustrative fruit list, to identify these records.

## Independent extraction checks

An independent standard-library `HTMLParser` extraction entered only
`div.transcription.ed-22905` and collected each `h3` with its following ordered
list. It recovered recto 21 lines, verso 21 lines, and verso right margin 4
lines. The complete records were then cut at the heads listed above. No
translation panel text was admitted.

| Record | Whitespace tokens | Hebrew base-letter clusters | U+05B9 code points | Printed punctuation |
| --- | ---: | ---: | ---: | --- |
| Peach | 64 | 285 | 9 | 5 periods, 1 semicolon |
| Pomegranate | 102 | 464 | 9 | 4 periods |
| Quince | 75 | 326 | 14 | 4 periods |

“Base-letter cluster” here means one printed Hebrew base character with all
immediately following combining marks attached. It is an explicitly defined
edition-level unit, not a claim about the manuscript's complete grapheme or
phoneme inventory. Counts include the named heads. The three selected records
contain no Arabic-script letter or bracketed lacuna. Their only combining
character is U+05B9, whose Unicode name is HEBREW POINT HOLAM.

Across the selected records the marked cluster counts are:
`גֹ` 16; `צֹ` 7; `ץֹ` 3; `טֹ` 2; `מֹ` 1; `דֹֹֹ` 1.
These are 30 marked clusters containing 32 combining code points. The
independent totals agree with root's later corrected source extraction.

## Graphemic cautions

The language is cataloged as Judaeo-Arabic and the edition is Hebrew-script.
Hebrew code-point names do not establish Hebrew pronunciation. The same
combining character does several jobs in the published representation:

- In ordinary words it represents dots that distinguish Arabic consonant
  readings. Avetisyan's side-by-side Hebrew-script and Arabic-script excerpts
  provide direct examples involving gimel and tsadi. Removing all combining
  marks as if they were dispensable Hebrew vowel points would discard
  distinctions present in the edition.
- The pomegranate head carries a mark on mem although later occurrences of
  its name are unmarked. The native recto image shows a decorated/dotted head.
  The peach and quince heads also show visible dot clusters that are not
  represented as a complete mark-by-mark diplomatic inventory in the PGP text.
- Verso 11 has `בארדֹֹֹ`, with three consecutive U+05B9 code points. The
  Cambridge article also prints this anomaly. Its function is not resolved
  here; it must not be silently reduced to a vowel, a new consonant, or one
  ordinary dot. The image check does not certify an exact correspondence
  between each encoded mark and each physical dot.
- Final letter shapes and nonfinal shapes occur in the edition. Folding them
  together is a separate normalization decision. It is unnecessary for a
  strict literal model that preserves the printed distinctions.
- Outside the selected records, the apple passage includes an Arabic-script
  word at verso 16, an Arabic question mark at verso 17, and further repeated
  holam marks. The margin contains an explicit lacuna. These demonstrate why
  a whole-page “Hebrew letters only” cleanup would not be a neutral source
  transcription.

Comparison source: [Avetisyan, “Ripe apples with bread?”](https://www.lib.cam.ac.uk/collections/departments/taylor-schechter-genizah-research-unit/fragment-month/fotm-2022/fragment-1).
The direct article fetch returned 403, but its indexed text was available;
the cached PGP HTML and native images supplied the principal boundary evidence.
The [Cambridge repository record](https://www.repository.cam.ac.uk/items/41d7ffb4-00ce-4e30-8a81-1a54acfa6a54)
identifies the archived article and DOI 10.17863/CAM.99637.

## What a conditional code may claim

A fixed literal code may take the three exact PGP record strings, retain
every Hebrew base/final shape and attached mark sequence, and omit only the
explicitly declared printed periods and semicolon. Original strings and line
addresses should remain recoverable alongside that lexical projection.

Such a code tests a model of this edition's printed lexical stream. It does
not demonstrate historical Hebrew phonology, resolve the mixed functions of
dots, or reconstruct omitted vowels. Nor does it establish that modern
punctuation, encoded mark placement, or whitespace exactly reproduce scribal
practice. Any later changed reading or normalization would be a changed input
requiring a separately recorded decision.

## Dating and source identity limits

PGP gives only an inferred **post-10th-century** date, based on cited physicians.
The HTML's machine range is `1000/1700`; it is not evidence of secure copying
before 1420. Mention of an earlier author dates neither this copy nor its
immediate exemplar precisely. This witness therefore cannot, on the evidence
reviewed here, be labeled securely pre-1420. The three records also belong to
one leaf of one textual witness, not three independent historical sources.

## Evidence fingerprints

All paths below are relative to this dossier. Image files were inspected
locally without editing and are not publication artifacts.

| Cached evidence | SHA-256 |
| --- | --- |
| `semitic_cache/PGP40129.html` | `b16ca687bac29041c3873e5d3705012d057055f3b55e260d9ac12cba23816291` |
| `semitic_cache/PGP40129_1.jpg` | `9c08c678962d3b7a4e113fc40683ea1e48dbe6013c9768e74103a518351b6d8d` |
| `semitic_cache/PGP40129_2.jpg` | `4206dfd095ef86b79b0f0353ca7dbcc3221e9640dd152ed5d499446abf29fb6c` |

The first cached `PGP40129_TRANSCRIPTION.json` had an overbroad second `face`
field containing unrelated HTML/translation text. That file was not used as
the audit's source. Root reported correcting its extraction separately; this
audit did not modify source data, global ledgers, route state, or other work.
