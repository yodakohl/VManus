# GDT459 — local nomenclator content atlas

## Result

The old `LOCAL_ADDRESS` bucket was too coarse. The 183 events split cleanly
enough to support the mixed system we have been looking for:

| reading tier | events | interpretation |
|---|---:|---|
| exact running formula | 61 | identical surface has one invariant recipe in running text |
| attested recipe under a new surface | 7 | minimal segmentation reproduces an observed recipe |
| short/repeated provisional composition | 8 | bounded new composition; factor reader does not stop |
| learned whole nomenclator label | 107 | owner-bound object/station/name card |

Thus 76 events (55 surfaces) carry address formulae, while 107 events (107
surfaces) are learned whole labels. All retained whole labels are singletons in
this address set. That singleton tail is not a failure of the compositional
model: it is exactly the learned nomenclator layer expected beside a compact
technical code.

## What the whole labels denote

The image owner supplies a concrete class, but not the missing individual
identity:

- 64 stellar-position labels on `f71v`/`f72r` → `STERNSTELLENNAME`;
- 35 drug or ingredient labels on `f88v`/`f89r` → `DROGENNAME`;
- 6 bath/outlet-station labels on `f77r` → `BADSTATIONSNAME`;
- 2 labels beside the pictured flowering plant on `f17r` → `PFLANZENNAME`.

These are short defaults for what kind of learned entry the card is, not claims
that a particular star, drug, station, or species has been deciphered.

## Portable formula evidence

The strongest evidence is cross-context exact identity. Sixty-one local events
use a surface already present in running text, and every such surface has one
invariant running recipe. Examples include `aiin → WERT`, `ar/char → AUSGANG`,
`okal → SETZEN · ZIELORT`, `otaiin → DANACH · WERT`, and
`okaldy → SETZEN · ZIELORT · SCHLUSS`. These do not behave like 61 unrelated
object names.

Seven further events form an already attested recipe under another rendering,
including `ary → AR+Y`, `otalshy/otalsy → OT+AL+Y`, and
`okchshy → OK+CH+Y`. Eight bounded creative reads remain provisional:
`Y+S`, `AIN+AM_ADDR`, `OT+AIR`, `AIR+AL`, `AR+AL`, and the repeated
`OT+AR+AL+Y` family.

## Why the remaining 107 were not force-parsed

The same minimal-form segmenter was tested on 761 known running surfaces. It
recovered the true recipe only 442 times (58.08%). Restricting attention to a
predicted recipe that also has another surface raises this to 185/253 (73.12%),
but that is still not a license to decompose every long string. The tier rules
therefore keep the large unique tail as memorized whole labels.

## Page distribution

| page | address events | A | B | C | learned whole |
|---|---:|---:|---:|---:|---:|
| f17r | 2 | 0 | 0 | 0 | 2 |
| f71v | 22 | 10 | 0 | 0 | 12 |
| f72r | 96 | 32 | 5 | 7 | 52 |
| f77r | 11 | 5 | 0 | 0 | 6 |
| f88v | 14 | 2 | 0 | 0 | 12 |
| f89r | 38 | 12 | 2 | 1 | 23 |

The formula/whole-label mixture occurs independently in celestial, biological,
and pharmaceutical layouts. The Herbal sample is only two labels and supplies
no formula evidence by itself.

## Working architecture

The best current practical description is now more specific:

> a productive nineteen-core workshop/address layer embedded in a larger
> learned nomenclator whose individual entries are supplied by the visible
> owner and a master exemplar.

That architecture can predict how a new visible item should be handled without
pretending to know every item name: exact old formula first; attested recipe
under a bounded new rendering second; short/repeated composition provisionally;
otherwise memorize one whole owner-bound label.

## Validation and ceiling

The validator passes 36/36 checks, including exact source order, all tier and
content counts, image hashes, invariant surface decisions, source-recipe tests,
sealed-page exclusion, and a byte-identical rebuild.

No core meaning, page inventory, surface prediction, or confirmed lexeme was
added. The result is a better complete working dictionary, not a decipherment.
