# IGR002 — held-folio image-grounded grapheme atlas

Status before target-image access: **FROZEN OUT-OF-SAMPLE SELECTION**.

## Question

IGR001 found enough physical localization capacity to continue: seven of eight
recurrent reading-disagreement types localized on all three sampled folios and
had a repeated complete neutral shape signature. IGR002 asks whether those
seven signatures predict new physical occurrences on entirely different
folios. Type 6, which had only one resolved IGR001 example, is retained as a
localization diagnostic but cannot contribute to the primary prediction.

## Selection and blinding

Use the same eight ordered `(STA family,ZL,IT,RF)` triplets frozen by IGR001.
Exclude every physical folio opened in IGR001. Within each type rank remaining
strict zero-alternative occurrences by

```text
SHA256("IGR002_ATLAS_V1|" + family + "|" + ZL + "|" + IT + "|" + RF
       + "|" + locus + "|" + symbol_index_1based)
```

and retain the first four distinct physical folios. The blinded inspection TSV
contains opaque ID, source coordinate, symbol/group positions, canvas, and
dimensions, but no type, reading code, expected signature, or IGR001 outcome.
Opaque IDs are keyed with a 256-bit registration nonce that is stored only in
the private selection object. Before scoring, only cryptographic commitments
to the private selection, locator sheet, builder, and validator are published.
The crop-review package exposes neither the nonce nor type-decodable IDs.
Annotation order is the SHA-256 order of the opaque IDs, not type order.

Inspection is split. A source-aware localizer may see a private locator sheet
containing folio/locus/manual position and records a bounded crop plus target
marker, but makes no shape judgment. A fresh reviewer with no earlier IGR turn
history receives only randomly named crop bodies and a target marker, never
folio, locus, transcription, type, reading codes, prototype, selection object,
or IGR001 artifact. Only those crop-only reviews may enter the primary score.

## Inspection and scoring

Use exactly the IGR001 localization states and six-field neutral visible-shape
rubric. Manual transcription may be used only by the localizer to mark the
already frozen position. No OCR, CLIP, embeddings, image classifier, semantic
label, preferred reading, or appearance-based target selection is permitted.

After all 32 annotations are sealed, join type identities and the IGR001 modal
signatures. The primary 28 targets are types 1–5, 7, and 8. Type 6 is diagnostic.
Pass only if:

* at least 24/28 primary targets are localized;
* at least 20/28 primary targets exactly match their frozen six-field signature;
* at least six of seven primary types have at least three exact matches among
  their four new-folio targets.

An unresolved or damaged target is a non-match. No threshold may be changed
after target images are opened.

## Ceiling

A pass may establish only that anonymous visible shape classes recur behind
the frozen manual disagreement types on held physical folios. It cannot choose
the correct transcription, prove allography, name a grapheme, assign sound,
alphabet, word, language, cipher, plaintext, meaning, or translation.
