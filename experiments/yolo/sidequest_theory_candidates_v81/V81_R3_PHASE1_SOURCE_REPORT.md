# V81 R3 Phase 1 — Sienese Si1 source freeze

Status: `FROZEN_BEFORE_V81_TARGET_MANIFEST`

## Outcome

R3 froze one previously unused, in-period Sienese key: **Si1, “Di m.
Antonio Petruccio 1433.”** Its printed nomenclator contains three exact
source-language entries paired with five exact graphic signs. All five signs
are admitted; none is guessed into Unicode. The exact graphics are bound by
official IIIF regions, a hash of the full documentary page image, and a raw
RGB24 pixel hash for each crop.

The frozen rows are:

| Entry | Exact sign alternatives | Inventory rows |
|---|---:|---|
| `Niccolo Fortibraccio` | 1 | `SI1_001` |
| `Duca di Milano` | 1 | `SI1_002` |
| `Serenissimus` | 3 | `SI1_003A`–`SI1_003C` |

This is historical vocabulary granularity only. It does not bind any entry or
sign to a Voynich card, form, sound, role, or meaning.

## Documentary provenance

Meister describes the Siena archive packet as a collection of original cipher
keys and identifies its oldest dated key as the one used by Antonio Petruccio
in 1433. The key is printed under the heading `Di m. Antonio Petruccio 1433.`
on p. 51, with the archive locator printed in the footnote as `Siena St.-Arch.
Lettere in cifra Nr. III. 1. Cifrari N. 1.` The normalized shelfmark used here
is Archivio di Stato di Siena, *Lettere in cifra*, no. III, fasc. 1 *Cifrari*,
no. 1.

- Documentary edition: Aloys Meister, *Die Anfänge der modernen
  diplomatischen Geheimschrift: Beiträge zur Geschichte der italienischen
  Kryptographie des XV. Jahrhunderts* (Paderborn: Schöningh, 1902), pp.
  50–51. [Persistent ULB object](https://nbn-resolving.org/urn:nbn:de:hbz:6:1-143638)
- Exact table: printed p. 51, ULB PDF page 64,
  [IIIF canvas 3076057](https://sammlungen.ulb.uni-muenster.de/i3f/v20/3075984/canvas/3076057).
- Independent catalogue check: Judit W. Somogyi, “Caratteristiche strutturali
  di cifrari monoalfabetici italiani nei secoli XV e XVI,” *Verbum* 17.1–2
  (2016), pp. 195–217. Page 205 identifies Si1 and its date; p. 207 reports 30
  signs as 25 alphabet signs plus five nomenclator signs.

The date 1433 is inside the required 1370–1450 window, and the key is Sienese.
Unlike Florence Fi1 (1414), Pisa Pi1 (1442), and the other V77 source keys,
Si1 was not present in any of the five historical-source-only V77 tables used
for the duplicate screen.

## Exact sign preservation

The opaque signs are not safely representable as ordinary text. Consequently,
`GRAPHIC_RASTER__…` is an identifier, not a transcription. Each inventory row
supplies:

1. the complete hashed IIIF page image (`2340x3063` pixels);
2. a zero-based, top-left, half-open `x,y,w,h` rectangle;
3. a stable IIIF region URL;
4. SHA-256 of the returned region JPEG; and
5. SHA-256 of the unscaled row-major RGB24 bytes cropped from the hashed full
   page image.

The prose descriptions such as “four quadrant dots” are navigation aids only.
They cannot substitute for the exact raster-bound sign.

## Executable documentary rule

The frozen list supports only this narrow encoder/decoder:

```text
ENCODE_EXACT_ENTRY("Niccolo Fortibraccio") -> SI1_001
ENCODE_EXACT_ENTRY("Duca di Milano")       -> SI1_002
ENCODE_EXACT_ENTRY("Serenissimus")         -> one of SI1_003A/B/C
ENCODE_EXACT_ENTRY(anything else)           -> OUTSIDE_FROZEN_VOCABULARY

DECODE_EXACT_SIGN(SI1_001)                  -> "Niccolo Fortibraccio"
DECODE_EXACT_SIGN(SI1_002)                  -> "Duca di Milano"
DECODE_EXACT_SIGN(SI1_003A/B/C)             -> "Serenissimus"
```

The source does not state how a scribe chose among the three `Serenissimus`
homophones, so no cycling, randomization, or context rule is invented.

Example valid bookings are exact round trips through the rows above. Invalid
bookings include `Milano` alone, generic `Duca`, an inflected or translated
variant, or a merely similar-looking graphic. None has an exact row in this
freeze.

## Duplicate screen

Only the source-labeled V77 tables were intended for this check. They exclude
the already used/control families:

- Lavinde 1379 keys 13 and 26;
- Mantua 1395, 1401, and the unavailable-entry 1404 nomenclator;
- the after-1412 Pisan–papal key;
- Florence Fi1 (1414), including the prior `et`/`per` controls; and
- Pisa Pi1 (1442).

Si1 is distinct from all of them. The five screened file hashes are recorded
in the freeze JSON.

## Blind-boundary incident

An initial broad repository `rg`, issued to locate V77 source artifacts,
accidentally displayed lines from `V77_R3_DECISION_TABLE.tsv` along with the
intended historical tables. No V80 file, V81 target/card manifest, V81 sibling
output, manuscript page/image/transcription, `f84`, or `f84r` was opened. The
search was immediately narrowed to the five source-only V77 tables, and none
of the old V77 target-side material was joined to or used to select Si1.

This incident cannot be silently undone. The source inventory remains an exact
documentary freeze, but strict role-blindness is marked
`REQUIRES_CENTRAL_ADJUDICATION` before R3 may enter Phase 2.

## Frozen artifacts and seals

- `V81_R3_SOURCE_INVENTORY.tsv`
  - rows: 5 (three entries, five exact signs; maximum allowed: 60)
  - SHA-256: `6ac100560aa5d0ebba24494cb513972e02a63b809e9d7fd0e2f251c2ae356ac2`
- `V81_R3_SOURCE_FREEZE.json`
  - `target_manifest_opened=false`
  - SHA-256: `89faaeb866ced5ac12da4c4e1b214470f81fa7bff5076faa16bf077f3c2376ff`
- Meister 1902 ULB PDF source object
  - SHA-256: `8cc91d4ed9ba4c7bf0ca6be46f2cc2d30e9a217366ff34d7d4ab02bfeb688cd6`
- ULB full IIIF page image 3076057
  - SHA-256: `49876ab54472fd94981f938e84ca68434f7be8ae0db2e683f0fe28868311061f`

## Stop

R3 Phase 1 is complete. Do not open the V81 target manifest or begin an
occurrence audit until the central Phase-2 gate explicitly adjudicates the
recorded incident and releases R3.
