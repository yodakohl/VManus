# GDT617 prospective registration

Registered: 2026-08-29

Status: `SOURCE_REGISTERED_UNSCORED`

## Frozen present-stage action

GDT617 presently acquires and validates only six allow-listed official
catalogue/IIIF responses. It opens no Voynich page, transcription, name,
target feature, candidate mapping, target score, or sealed material.

The source registry is
`artifacts/REGISTERED_SOURCE_BINDINGS.json`. Its bytes must be committed before
any source-concordance annotation or target selection begins.

### Pre-publication exposure correction

The six-response registry and source freeze were already byte-fixed and passed
their local checks when a parallel historical search consulted Eva-Maria
Wagner's published Clm 28531/Masson 116/Sloane 4016 concordance before this
directory reached its public commit. Consequently, any source-entry candidates
obtained from that search are developmental rather than prospectively sealed.
The source hashes and no-target acquisition result remain valid, and no Voynich
page, transcription, target pairing, score, or mapping was opened. A later
target panel and its four-discovery/one-held assignment must therefore be
registered separately before any Voynich pairing.

## Frozen external transmission claim

The registration uses only claims made in the holding institutions' own
metadata:

- BnF Latin 6823 is a Latin text-bearing *Liber de herbis et plantis* witness;
- the Masson 116 record says most of its plant iconography is copied from the
  *Tractatus de herbis* in BnF Latin 6823; and
- the Sloane MS 4016 record describes that Italian herbal as a copy of Masson
  116.

These statements nominate a source family. They do not establish any Voynich
correspondence.

## Frozen future gates

The route may proceed only in this order:

1. source acquisition and hash validation;
2. manual three-witness concordance with names/plaintext hidden from the later
   target pairing step;
3. at least five concordances on nonreused physical folios in each witness;
4. a target-facing opaque source-picture packet with no Latin names/text;
5. at least five one-to-one matches on five distinct physical Voynich folios;
6. deterministic four-discovery/one-held assignment;
7. exact fitting of one global primitive-to-0..3-letter Latin transducer on
   the four discovery entries; and
8. one held reveal requiring the exact heading plus twelve content words.

No macro, whole-word key, page/folio/entry key, context key, alternate
segmentation, synonym, spelling repair, word-boundary edit, or held retuning is
admissible.

The canonical Latin normalization and exact target-span representation must be
specified in the source-concordance/target-freeze addendum before target
plaintext is opened. If that addendum is absent, no target run exists.

## Present-stage pass

The current acquisition passes only if all six registered bindings match their
registered identity, type, size and binding hash and all three manifests match
the registered canvas counts. The exact fetched Gallica OAI wrapper is retained
and retrospectively hashed, while its prospectively frozen binding is the
canonical complete OAI record described in `METHOD.md`. A pass also requires a
derived request log containing exactly the six allow-listed metadata requests,
with zero redirect attempts and zero non-allow-listed, canvas, image, or target
requests. Its sole pass label is
`SOURCE_BINDING_PASS__TARGET_UNOPENED`.

## Hard exclusions

- no Voynich page or transcription;
- no f84 or f84r access;
- no canvas or image bytes;
- no OCR, automatic image classifier, embedding retrieval, or caption model;
- no plant-name-to-Voynich pairing; and
- no claim of a decoded glyph, word, language, plaintext, or translation.
