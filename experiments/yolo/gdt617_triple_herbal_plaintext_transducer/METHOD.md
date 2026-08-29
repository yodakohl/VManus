# GDT617 method

## Question

Can a source-only, three-witness herbal concordance provide at least five
independently located exact entry plaintexts, and can one globally fixed
primitive-to-short-Latin transducer learned on four distinct Voynich folios
reproduce an untouched fifth entry's exact heading plus twelve content words?

This registration performs only the source-acquisition step. It does not open
or score a Voynich target.

## Why this route is new

The closed historical-herbal routes tested plant-name order, broad medicinal
properties, or image-model similarity. This route instead requires an
authorial entry/text endpoint. The official source records state a concrete
copy chain: Masson 116 derives most plant iconography from BnF Latin 6823, and
Sloane 4016 is catalogued as a copy of Masson 116. Latin 6823 supplies the
entry text; the two later witnesses supply independently physical captioned
image witnesses for source-only concordance.

The triple does not count as three target replications. It establishes one
external entry identity before a target is considered.

## Inputs

`artifacts/REGISTERED_SOURCE_BINDINGS.json` allow-lists exactly six HTTPS
responses:

- BnF Gallica OAI catalogue metadata and Gallica IIIF manifest for Latin 6823;
- Beaux-Arts Paris Omeka catalogue JSON and IIIF manifest for Masson 116; and
- British Library Search Archives catalogue JSON and IIIF manifest for Sloane
  MS 4016.

The acquisition code rejects every HTTP redirect before a follow-up request and
never follows a canvas or image-service URL. It retains
only the six small metadata/manifest responses (about 1.25 MB in total).
Five responses are bound byte-for-byte. The Gallica OAI wrapper reports a
volatile server search duration; for that one response the registered hash is
over a canonical extraction of the complete OAI record header and Dublin Core
metadata, while the exact fetched wrapper is still retained and separately
hashed in the acquisition report.

## Method

### Source acquisition

Run:

```text
python3 experiments/yolo/gdt617_triple_herbal_plaintext_transducer/src/acquire_sources.py --execute-registered-source-acquisition
```

The command:

1. rejects every URL not present in the registry and blocks redirects before a
   follow-up request can be issued;
2. requires HTTPS, the registered host, response media type, size ceiling,
   exact final URL, identity markers, and registered hash;
3. parses each manifest only to validate its identity and canvas count;
4. writes the six metadata snapshots, compact hash reports, and an exact
   request log whose zero counters are derived from its recorded URLs and
   resource classes; and
5. never requests any URI contained inside a manifest.

`--verify-existing` repeats all checks without network access.

### Prospective source-concordance packet

The next source-only pass must be manual. It may display the three registered
external witnesses, but it may not display Voynich material and may not use
OCR, automatic image classification, embeddings, or generated captions.

An eligible entry must satisfy all of the following:

- one human-confirmed corresponding illustrated entry exists in each of the
  three witnesses;
- its Latin heading is transcribed independently from all available source
  captions and conflicts are resolved before any target is seen;
- the text-bearing Latin 6823 entry supplies a manually transcribed heading
  and at least twelve following content words;
- the three physical folio locators are recorded, and no physical folio in any
  witness is reused by another retained entry;
- the published target-facing packet replaces the entry name and plaintext by
  an opaque salted commitment, retaining only source image locators needed for
  later visual pairing; and
- the plaintext/name table remains unavailable to the later Voynich pairing
  step until that target packet is committed.

Fewer than five eligible concordances stops as
`INSUFFICIENT_TRIPLE_SOURCE_CONCORDANCE`.

### Prospective five-folio panel

A later addendum, committed before any source plaintext is revealed to the
target solver, must freeze exact Voynich paragraph/entry spans and their
primitive segmentation. A human may pair source pictures to target drawings,
but receives neither Latin names nor entry text. The panel must contain at
least five one-to-one pairs on five different physical Voynich folios. Each
pair must also use different physical folios in every external witness.

If more than five pairs survive, select the five smallest values of
`SHA256("GDT617_PANEL_V1" || opaque_pair_id)`. Among those five, the largest
value of `SHA256("GDT617_HELD_V1" || opaque_pair_id)` is held; the other four
are discovery. These rules use opaque IDs, not names, plaintext, transcription
forms, or model fit.

### Global transducer

Let `P` be the frozen primitive alphabet and let

```text
F : P -> {a,...,z}^{0..3}.
```

`F` is shared by every word, line, entry, and folio. The output for a target
word is the concatenation of the outputs of its frozen primitives. Existing
target word boundaries become single plaintext spaces. No boundary may be
inserted, deleted, moved, or emitted by a primitive.

Forbidden model capacity includes:

- macro or whole-word entries;
- context-conditioned outputs;
- page, folio, entry, line, word, position, or section keys;
- alternate primitive segmentations;
- post-hoc spelling aliases or synonym substitutions; and
- any change after the held plaintext is opened.

All four discovery entries must match their registered canonical Latin strings
exactly. Among discovery-perfect maps, choose the one minimizing, in order:

1. total output length `sum_p len(F(p))`;
2. number of nonempty primitive outputs; and
3. the tuple of outputs in frozen primitive order, ordered first by length and
   then ordinary ASCII lexicographic order.

The held folio is then opened once. A pass requires exact equality for the
complete registered heading and the first twelve content words, including the
registered word boundaries. There is no partial-credit score.

## Decision rule and claim ceiling

Registered outcomes are:

- `SOURCE_BINDING_PASS__TARGET_UNOPENED` for the present acquisition;
- `INSUFFICIENT_TRIPLE_SOURCE_CONCORDANCE`;
- `INSUFFICIENT_FIVE_FOLIO_PANEL`;
- `NO_GLOBAL_DISCOVERY_TRANSDUCER`;
- `HELD_EXACT_PLAINTEXT_FAILURE`; or
- `FIVE_FOLIO_EXACT_PLAINTEXT_TRANSFER`.

Even the final pass licenses only the exact registered spans and one candidate
global primitive key. It does not by itself identify the manuscript's
language, translate unregistered text, or validate a botanical species match.
Until a target addendum is separately published, GDT617 licenses no Voynich
value, word, plaintext, or meaning.
