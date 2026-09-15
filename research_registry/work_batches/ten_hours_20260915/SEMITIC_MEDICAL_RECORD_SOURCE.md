# T-S 8J29.4: complete Judaeo-Arabic medical prescription source

Source-only collation for the 2026-09-15 bounded Semitic-source branch. This
record is independent of PGP40129 (T-S Ar.43.225). No Voynich text, image,
reserve, decoder, or target match was inspected or selected here.

## Why this record qualifies

The Princeton Geniza Project record [T-S 8J29.4](https://geniza.princeton.edu/en/documents/3775/)
labels the primary language Judaeo-Arabic, describes a medical prescription,
provides one transcription, and exposes the Cambridge image for 1r. The online
record's transcription is S. D. Goitein's unpublished edition (1950–85). The
second suggested candidate, [T-S 6J2.18](https://geniza.princeton.edu/en/documents/9494/),
is also catalogued as Judaeo-Arabic and medical, but the public page exposes no
transcription, so it is retained only as a rejected comparison candidate.

The record is a compact prescription unit on T-S 8J29.4 1r, lines 1–6. Line 1
is an opening invocation (`ב]אללה אלתופיק`); line 6 closes with a benefit/well-
wishing formula (`... נאפע אן שא אלל[ה`). The page has internal physical and
textual losses, represented by Goitein's brackets and dotted lacunae. The
online item also exposes 1v, but its page has no transcription and the public
scan shows no writing; it is not silently treated as missing continuation.
Thus “complete” here means a complete bounded prescription unit as represented
by the public edition (1r:1–6), with lacunae retained, rather than a claim that
every damaged character is recoverable.

## Diplomatic transcription

The following is copied exactly from the Princeton page, preserving Hebrew
script, spaces, punctuation, dotted lacunae, and square-bracket placement.

```text
1. ב]אללה אלתופיק
2. שראב לימון מרמל שתוי אוקיה [
3. וילקא פיה סכר נבאת נצף אוק[יה
4. . . . ] תלתה דראהם כתירא ביצא נצף דר[הם
5. . ] מון אביץ תמן דרהם יוכד ללגמ[
6. אללעוק ויסתעמל נאפע אן שא אלל[ה
```

The page metadata describes the visible content as lemon syrup, sugar candy,
tragacanth/white gum, and measured quantities; those catalogue glosses are
source metadata, not replacements for the diplomatic text. The page supplies
no English translation panel.

## Repeated forms and reversible notes

These are observations over the transcription, not Voynich matches and not
confirmed lexical identifications.

| Visible family | Occurrences | Status and safe handling |
|---|---|---|
| `אוק...יה` | line 2 `אוקיה`; line 3 `אוק[יה` | Strong repeated measure-like frame. Keep the bracketed interruption in line 3; do not expand it. The catalogue's “ounce” description makes the measure reading plausible, but the source does not license a normalized spelling. |
| `דרהם` | line 4 `דראהם`; line 5 `דרהם` | Repeated measure family with an inserted א in line 4. Preserve both spellings as distinct surface forms and retain the line-4 final bracket (`דר[הם`). |
| `ביצא` / `אביץ` | line 4 `כתירא ביצא`; line 5 `מון אביץ` | Possible related “white”/colour form family in the Judaeo-Arabic reading, supported only weakly by the catalogue's “white gum” gloss. Treat as uncertain and do not collapse or transliterate without a separate edition. |
| `לימון` / `] מון` | line 2 `לימון`; line 5 `. ] מון` | Surface suffix overlap only. Line 5 is damaged and must not be restored as a repetition of `לימון`. |

The prescription also has repeated dosage/compound syntax (`פיה`, measured
quantities, `יוכד`, `ויסתעמל`) but no repeated exact verb or ingredient beyond
the families above. Arabic transliteration, root segmentation, gender/number
analysis, and any proposed common graphemic code are deliberately deferred.

## Uncertainty ledger

* `]` and `[`: retain exactly as supplied by Goitein; they mark loss or an
  uncertain edge, not optional punctuation.
* `. . . ]` (line 4) and `. ]` (line 5): preserve dotted lacunae and their
  spacing. No missing ingredient is inferred.
* `אוק[יה`, `דר[הם`, `ללגמ[`, and `אלל[ה`: preserve the visible characters and
  bracket locations. The bracketed readings are not silently completed.
* `ביצא` and `אביץ` remain separate strings in any future machine-readable
  representation; their possible relation is a hypothesis with low confidence.
* The page's catalogue description says “probably” for several quantities and
  “possibly” for the aphrodisiac interpretation. Those qualifiers remain
  attached to the description and are not upgraded by this collation.

## Access and hash receipts

Accessed 2026-09-15 UTC. The Princeton HTML was fetched directly and hashed;
the two Cambridge IIIF JPEGs and their IIIF metadata were fetched directly and
hashed. The image permission statement on the Princeton page says the images
are provided by Cambridge University Library, may be used under fair use/fair
dealing for teaching and research, and requires contacting
`genizah@lib.cam.ac.uk` for publication on the public web. No image file is
copied into this repository.

| Object | URL | SHA-256 |
|---|---|---|
| Princeton record HTML | https://geniza.princeton.edu/en/documents/3775/ | `ffbfe01642cd2c9fcced24692b7661f9a3b10bab9e6420bd018c1daa7ffc4ada` |
| Cambridge IIIF image, 1r (2000 px JPEG fetch) | https://images.lib.cam.ac.uk/iiif/MS-TS-00008-J-00029-00004-000-00001.jp2/full/2000,/0/default.jpg | `165149408c506835fb1e187c81094b88ed256eeb1409226764ea8e6dc7be31d4` |
| Cambridge IIIF image, 1v (1000 px JPEG fetch) | https://images.lib.cam.ac.uk/iiif/MS-TS-00008-J-00029-00004-000-00002.jp2/full/1000,/0/default.jpg | `5c820e5a04f227426846a51d1a333a4524cc85d7aef6e9cf5d064ddcf6a4566a` |
| Cambridge IIIF `info.json`, 1r | https://images.lib.cam.ac.uk/iiif/MS-TS-00008-J-00029-00004-000-00001.jp2/info.json | `4cded07f0a66abcb092f463be2e23e480dcfc2a79b1d6d6ad893ccce2f65d4b2` |
| Cambridge IIIF `info.json`, 1v | https://images.lib.cam.ac.uk/iiif/MS-TS-00008-J-00029-00004-000-00002.jp2/info.json | `7660f62cb3b2a943edeaa94b7943bd3d603e7ad1bf11b9908ece551b7a4e0fbe` |

The Princeton page also links the Cambridge CUDL object and its IIIF canvas;
the CUDL viewer itself returned HTTP 403 during this bounded audit, so the
direct IIIF image and metadata endpoints above are the reproducible public
receipts used here.

## Bounded consequence

T-S 8J29.4 supplies enough recurring written forms and dosage/recipe context to
specify a future source-bound common-channel feasibility test, while preserving
surface spellings and damaged text. It does not by itself establish a language
model, a root analysis, or any Voynich decipherment. If a future test is chosen,
it should freeze this six-line unit, treat the bracketed losses as missing data,
and compare against an explicit rival such as unrelated surface-token reuse.
