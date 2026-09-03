# GDT765-Bericht — von offenen Feldern zu Blütenmaterial

## Outcome

The best working reading is now concrete:

| whole | stable role | concrete default | identity confidence |
|---|---|---|---|
| `ofchy` | named drug/preparation head | **Blütenmasse** | C0 bold family lead, 31/100 |
| `schor` | plant-part item/subentry | **Blütenstand** | C1 reproductive-part lead, 39/100 |

The role decision is substantially stronger than either noun. That is useful,
not a retreat: the renderer always has a practical default, while the evidence
table says exactly which part may later change. Neither result comes from
reading EVA `f` as *flos* or EVA `s` as *semen*.

## Why `ofchy` is a material name

There are four raw `ofchy` strings and three reader-exact positions. The raw
f39v.5 form is excluded because ZL3b reads `ofchy` while IT2a/RF1b read
`opchy`. All admitted positions are in the Herbal register, all are medial,
and each opens a different but compatible nominal specification:

| locus | exact span | concrete working reading |
|---|---|---|
| f22r.4 | `ofchy daiin` | Blütenmasse, drei Einheiten |
| f26v.5 | `ofchy chs ar` | ein Anteil trockener Blütenmasse in Grundform |
| f39v.1 | `ofchy kar or aiin` | drei Portionen der ersten heißen Blütenfraktion |

A quality/index interpretation works only at f22r.4. At the other two loci it
creates a quality stacked on dry form or a redundant value stacked on a hot
material fraction and an amount. An action or unit reading is worse. The
complete content-head hypothesis scores 11 against 0 for quality, 0 for unit,
and -6 for action under the explicit comparison in the scorecard.

The guarded cache contains 25 exact `ofch*` occurrences across thirteen
complete forms and thirteen exact `*fchy` occurrences across eight forms. This
supports a real formal neighborhood but not automatic composition. The only
semantic bridge is deliberately weak: one scoped `ofchedy` card already reads
“fully dried flower mass.” GDT765 uses that as a whole-family analogy to choose
**Blütenmasse** over the close rival **Blütenzubereitung**; it does not create
an `ofch = flower` component.

## Why `schor` is an item and why “Blütenstand” is the useful default

All three raw `schor` occurrences are reader-exact. Two are line-initial item
heads and one is the internal H2 field on f22r.4:

| locus | exact span | concrete working reading |
|---|---|---|
| f22r.4 | `schor daiin` | Blütenstand, drei Einheiten |
| f32r.4 | `schor` | Blütenstandsposten |
| f42v.10 | `schor okchey` | Blütenstand, heiß-trocken auf mittlerem Grad |

The builder preserves the awkward fact that GDT738 rejected a general body
transfer into `schor`. The new reading therefore does not pretend that a
suffix has been decoded. It instead combines three facts at the complete-word
level: `schor` behaves as an H2 item at all three positions; one position bears
an exact value; and the separately observed whole `chor` bridges all four
dry/moist carrier words at five exact spans with a reproductive plant-part
lead. The 67 direct value pairs for nine `chor`-like heads also show that such
wholes routinely occupy nominal value-bearing slots. `Blütenstand` is the
concrete choice; **Samenstand** and a generic plant-part item remain the live
rivals.

## The f22r record now says something

The first two lines of the local paragraph contain four exact value cells:

```text
f22r.4  ofchy daiin  ...  schor daiin
f22r.5  ol daiin     ...  dar daiin
```

Across the entire cache there are twelve exact `H-head X daiin` triples
(H1 five, H2 five, H4 two); f22r.4 alone contains two on one line. That makes a
main-field/subfield inventory much more natural than a sequence of actions.

The deliberately concrete f22r.4 working translation is:

> Haupteintrag, Trockenklasse III: drei Einheiten Blütenmasse; abgemessene
> Drogenportion Form III mit dazugehörigem Trockenmaterial; Unterposten: drei
> Einheiten Blütenstand.

This line covers all nine written tokens. The central `cfhy` now acts locally
as a field transition. It occurs reader-exact six times, five medial and once
line-final, never at paragraph end and never directly before `daiin`; the old
“take,” “wring,” and free cfh/flower readings are not used. `doroiin` and
`ypchol` retain explicit C0 local defaults, so this is a complete working
reading rather than a claim of recovered plaintext.

The amount wording is also a choice. The portable form remains “value III”
because `daiin` can still be class, degree, or amount. The concrete f22 renderer
chooses three units because four neighboring material/preparation heads make
an inventory or recipe quantity list plausible.

## Historical fit

Seven retained comparators show the needed mixed architecture: learned drug
names beside hot/cold, dry/moist, and degree fields; plant-part rubrics such as
*De floribus* and *De seminibus*; and recipe ingredients beside separate part,
unit, and number fields. They support the type of record, not the target
spelling and not the flower identity.

## Result boundary and next route

GDT765 contributes two usable complete-word defaults and six exact-span
renderers. They are replaceable working readings: zero confirmed lexemes,
plaintext clauses, substances, units, or component values are claimed. No new
page, image, or transcription is used; f84/f84r remain inaccessible. The pass
validates 357 checks and fifteen byte-identical builder outputs.

The next useful pass is a prediction test over the already cached family:
assign concrete processing/state meanings to the remaining twelve `ofch*`
wholes and compare `chor`, `pchor`, `schor`, and `lchor` as one plant-part
domain with different record roles. The aim is to see whether “flower mass”
versus “flower head” predicts new readable phrases before any further page is
opened.
