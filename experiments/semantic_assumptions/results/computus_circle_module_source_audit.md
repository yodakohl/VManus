# Computus/cosmography circle-module source audit

Date: 2026-08-10

## Question

Does a newly located historical manuscript provide a labelled one-to-one donor
for the special circular diagrams on f67--f73, rather than another generic
resemblance?

## Public sources

- New York Public Library, MA 069 / MssCol 2557, *Computus, Text 3*, Paris,
  1240--1260: <https://digitalcollections.nypl.org/items/1fbe4680-28ab-013b-27fe-0242ac110002>
- The public-domain NYPL scans used for direct human quality control are
  individually catalogued on Wikimedia Commons under the exact file titles
  containing NYPL image IDs 426175, 426177, 426178, 426179, 1261811, and
  426181.
- Wellcome Collection MS.202, a computistical miscellany copied in a German
  semi-gothic hand and dated by its colophon to 1443:
  <https://wellcomecollection.org/works/aeb73uat>
- Wellcome IIIF manifest for the complete 58-image item:
  <https://iiif.wellcomecollection.org/presentation/v2/b19145068>
- Oxford, St John's College MS 17, official Digital Bodleian facsimile:
  <https://digital.bodleian.ox.ac.uk/objects/cca30c56-0751-4f52-a952-bbffcb7b64e9/>
- Loredana Teresi, “An Illustration to Ælfric's *De temporibus anni* in
  Ælfwine's Prayerbook,” *Anglia* (2020),
  <https://doi.org/10.1515/ang-2020-0021>.

No OCR, automated image recognition, image similarity model, or machine-created
caption was used. Public catalogue prose fixed the source contents; direct
human inspection was used only to reject false one-to-one topology.

## Result

NYPL MA 069 is a strong independent witness for the **module stock** behind the
Voynich circle section. One codex contains:

- a month/zodiac wheel;
- a circular letter-and-number cycle;
- a direction/wind/element/season/temperament/quality wheel;
- a Sun--Moon phase diagram;
- an Earth--Moon--Sun--zodiac diagram; and
- a nineteen-year epact cycle.

This is unusually close to the combined subjects represented by f57 and
f67--f73. It strengthens a computus/cosmography teaching-compendium prior for
the circle block.

It is **not** a source identification or label key. Direct inspection rejects
all six diagrams as one-to-one donors: their cardinalities, ring partitions,
and ownership structures differ from the Voynich panels. The 1443 Wellcome
witness is chronologically closer and confirms that a German-hand computus
could combine tables with a coloured fourfold astrological and Sun--Moon
diagram, but it likewise supplies no matching Voynich slot map.

The often-proposed reading of f68r1's 29 labelled stars between Sun and Moon as
a lunar system remains historically plausible. The manual f68r1 catalogue is
more specific than the page total: exactly one labelled star is described as
being at the centre of the diagram, leaving **28 noncentral labelled stars**.
That is compatible with the 28 lunar mansions, while the total 29 is compatible
with a lunar-month count.

A source correction prevents overclaiming this observation. Teresi documents
standard medieval tidal rotae with 30 sectors, sometimes 29; their moon-age
numbers run clockwise in an explicit ordered ring. Direct inspection of the
official St John's MS 17 facsimile confirms the wedge-and-concentric-ring
topology. This is a genuine historical count analogue, so “no historical
29-slot homologue” is too strong. It is still not a Voynich key: f68r1's stars
are scattered rather than placed in 29 ordered wedges, and its later
alphabetically arranged label catalogue is not an authorial sequence. MA 069
likewise displays eight Moon phases, not an ordered f68r1 roster.

## Decision and ceiling

Status: `COMPUTUS_COSMOGRAPHY_MODULE_PRIOR_STRENGTHENED_NO_LABEL_DONOR`.

Retain computus/cosmography as a strengthened system-family prior for the
special circle diagrams. Do not call MA 069 or MS.202 a Voynich exemplar, do
not map their Latin words or numerals onto Voynich strings, and do not infer a
day, month, degree, planet, direction, language, plaintext, or translation.

Retain f68r1 `28 noncentral + 1 central` only as a provisional lunar-system
candidate. It does not distinguish lunar mansions from a lunar-month or
another 28/29-part system, and it supplies no order, number, name, or word.

Reopen exact transfer only for a historical witness with an author-readable
ordered coordinate and one-to-one topology for a complete Voynich panel.
