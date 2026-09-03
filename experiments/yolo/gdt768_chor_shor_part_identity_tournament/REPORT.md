# GDT768 report — concrete reader and chor/shor tournament

## Result

The experiment improves the reader without pretending to have selected a
flower/seed direction. The best-supported statement is:

> `chor` and `shor` are parallel nominal plant-part or content wholes in the
> same technical register. One may be rendered as flower and the other as
> seed/fruit, but the admitted evidence does not say which is which.

M02 and its exact reverse M03 tie at **0.820437**. Their shared two-part family
wins; neither individual direction passes its replacement rule. The concrete
reader therefore keeps `chor=Blütenstand` and `shor=Fruchtstand` as visible,
replaceable defaults while preserving the reverse as an equal rival.

## What the reader now says

The strongest compact example is `f17r.5`:

```text
EVA
ychekchy cthy chor shor cphor cphaldy dair cthey qody

working reader
Ansatzposten: Blattgut; Blütenstand; Fruchtstand; Dosisposten;
fertiger Anteil I; Anteil II; Droge Form I; fertige Zubereitung.
```

The useful information is the record structure: `cthy chor shor` gives three
consecutive nominal content cells, followed by dose/fraction/preparation
fields. This is far more specific than “take the work item and process it”. It
still is a working reconstruction, not a plaintext claim.

The six anchor defaults used by the renderer are:

| complete EVA form | portable reading | displayed concrete default | main rival |
|---|---|---|---|
| `chor` | non-leaf plant-part item; reproductive role possible | Blütenstand | Samen- oder Fruchtstand |
| `shor` | reproductive plant-part item; organ open | Fruchtstand | Blütenstand |
| `cthy` | leaf material or aerial herb drug | Blattgut | oberirdisches Kraut |
| `dair` | measured fraction/portion, level II | Anteil II | local Herbal root-part rival |
| `kooiin` | underground/rootstock drug head | thick or creeping root drug | general Herbal class head |
| `koaiin` | sibling underground/rootstock head | creeping root drug | general Herbal page head |

All twelve complete line readings are reproduced in
`artifacts/HISTORICAL_PART_REGISTER_READER.md`. Their current displayed
readings are:

| locus | class | concrete working reading |
|---|---|---|
| `f17r.5` | inventory | Ansatzposten: Blattgut; Blütenstand; Fruchtstand; Dosisposten; fertiger Anteil I; Anteil II; Droge Form I; fertige Zubereitung. |
| `f3r.19` | ambiguous | Kalt-trockene Portion; Ansatz; Trockenform; Zubereitungsportion; Anteil II; Kaltzubereitung; Dosis III; Blütenstand; Blattgut. |
| `f2r.2` | inventory | Fertige Drogenportion; heiß-trockener Anteil I; zu gleichen Teilen: Fruchtstand und Blattgut. |
| `f28v.4` | local state pair | Kalt-Feuchtzubereitung III; getrockneter Blütenstand; Ansatz; kalt-trocken auf Stufe I; kaltes Gut; eingeweichter Fruchtstand, drei Einheiten; Kältestufe I. |
| `f10r.6` | record role | Zum Schluss: Blattgut; Blütenstand; Drogenposten III; abgeseihte Zubereitung; fertig; leicht getrocknet; Kältegrad III; leicht angefeuchtet. |
| `f9v.3` | record role | Abgeschlossene Wärmestufe; Blütenstand, Wärmegrad III, drei Einheiten; Blattgut, Kältegrad III; erste Wärmestufe; Endstufencharge, drei Einheiten. |
| `f10r.9` | ambiguous | Heiß-trockene Drogenportion: Fruchtstand; Blütenstand; leicht getrocknet; Wärmegrad IV; fertig; Trockenansatz, drei Dosen. |
| `f15r.5` | inventory | Kalt-trocken, Stufe I; Teil: Fruchtstand; Blattgut, drei Einheiten; Blattgut, fertig. |
| `f86v5.10` | local state pair | Erster heißer Anteil; heißer Ansatz aus Rohstoff I; heißer Anteil I; feucht bis zur Mittelstufe, fertig: Fruchtstand; heißer Anteil I: Blütenstand, eine Portion; Grad III; ein Maß Kaltansatz; abgekühlte Dosis. |
| `f15v.10` | inventory | Portionsposten: Blütenstand; Zubereitung Form III; Blattgut; Wärmegrad III. |
| `f6r.12` | inventory | Eine Portion feuchtes Gut; eine Handvoll Zubereitung; Blütenstand; Blattgut. |
| `f6r.2` | record role | Drei Einheiten; trockene Zubereitung Stufe I; Blütenstand; Blütenstand; heißer Anteil I; Blattgut; Drogenportion; fertiges Trockenprodukt. |

These renderings deliberately keep low-confidence fillers concrete. The token
artifact exposes the confidence and rival beside every one of the 94 tokens.

## Corpus and guards

The admitted cache contains **404** exact occurrences of the six anchors on
**135 pages** and **350 loci**:

```text
chor 176 | shor 77 | cthy 85 | dair 63 | kooiin 2 | koaiin 1
```

There are **33 multi-anchor lines on 26 pages**. The reader covers **94 tokens
in 12 complete lines**. No new page, image, or transcription was opened;
`f84` and `f84r` were not accessed.

The global GDT754 quarantine contains 172 source-composed complete surfaces.
It is applied before feature extraction and blocks **54 target-context
exposures** in this atlas. None can support a target through a derived family
echo.

The final validator reports `PASS`: **53,504 checks**, byte replay true, all
twelve declared builder outputs reproduced, and all lexical, plaintext, and
component counters zero.

## Why the dry/moist same-part model lost

The raw D1 state counts initially look promising:

| target | ED0 DRY/MOIST | ED1 | ED2 |
|---|---:|---:|---:|
| `chor` | 45/9 | 28/9 | 12/7 |
| `shor` | 8/12 | 8/5 | 7/2 |

`chor` remains dry-affine, though weakly. `shor`, however, is moist-affine
only at ED0; it reverses to dry-affine after near-family forms are removed.
The direct state opposition therefore survives just one of three radii.

CF04 confirms where the apparent pair came from. The exact complete-form
donor counts are:

| target/radius | expected side | rival side |
|---|---|---|
| `chor` ED0 | `chol=15`, `qokchol=2`, `cheor=2` | `sheor=1` |
| `chor` ED1 | `qokchol=2` | `sheor=1` |
| `chor` ED2 | `qokchol=2` | none |
| `shor` ED0 | `shol=5`, `sheol=2`, `sheor=2` | `qokchol=1` |
| `shor` ED1 | `sheol=2` | `qokchol=1` |
| `shor` ED2 | none | `qokchol=1` |

Thus `chol` and `shol` disappear at ED1, and `sheol` disappears at ED2. At
ED2 the six-form deck retains only `qokchol`, twice beside `chor` and once
beside `shor`. The M01 conjunctive family-persistence score is consequently
**0.000000**: `chor` expected-family retention is 2/19 = 0.105263, but `shor`
retention is 0/9.

The same survivors yield a symmetric target-normalised weighted Jaccard of
**0.875000**. This supports form-conditioned compatibility for two nominal
items, but it contains no direction telling us which item is flower.

## Why a shared two-part family survived

Three independent observations converge on parallel record roles:

- After ED2 removal, the outward non-anchor 12D cosine remains **0.966080** at
  D1, **0.984115** at R3, and **0.990899** over the line.
- `chor` and `shor` occur together on **8 lines / 8 pages**, with **3 direct
  pairs** and both orders (5 versus 3).
- Both parallel the `cthy` control: `chor` on 14 lines/11 pages with 5 direct
  pairs, and `shor` on 8 lines/7 pages with 3 direct pairs.

Their position similarity is **0.969525** and section-profile similarity is
**0.950704**. Both have zero true paragraph-opener events. The profiles are too
similar for M05's unrelated learned roles and do not give M04 the required
general-herb hierarchy.

CF07 is only a `BROAD_VALUE_AMOUNT_PROXY`. It is reported as register ecology,
not a demonstrated bound dose formula and not a seed/fruit discriminator.

## Model result

| rank | model | score | minimum support | disposition |
|---:|---|---:|---:|---|
| 1 | M02 `chor` flower / `shor` seed-fruit | 0.820437 | 0 | tied direction; no replacement |
| 1 | M03 reverse direction | 0.820437 | 0 | tied direction; no replacement |
| 3 | M01 same part, dry/moist | 0.644178 | 0 | live rival; persistence failed |
| 4 | M04 general herb / reproductive | 0.631987 | 0 | live rival; breadth failed |
| 5 | M05 role-distinct learned wholes | 0.132523 | 0 | disfavored; divergence failed |

Every feature-by-model row contains its score, evidence, and counterevidence.
The two leaders have identical weighted sums (9.024812/11) because flower and
seed/fruit identity credit is fixed to zero. Their high tied score supports the
shared two-part architecture; it does not satisfy either directional minimum.

## Historical bridge

The circa-1400 comparators make this structure historically ordinary. One
family of witnesses organizes materia under parallel part rubrics—flower,
seed, fruit, leaf/frond, root, wood, and gum. Another gives learned substance
names followed by part, hot/cold, dry/moist, degree, amount, or recipe fields.
That is the kind of mixed “learned whole plus specialist field” architecture
the Voynich reader is being tested against.

The bridge stops at architecture. Latin forms such as `flos`, `semen`,
`fructus`, `radix`, and `lignum` are attested comparison vocabulary; none is
matched to an EVA spelling or initial. In particular, `p/s/r/l` are not granted
Latin values, and no substring of `chor` or `shor` is exported.

## Bottom line

GDT768 replaces generic process prose with a readable, falsifiable nominal
record model. It does **not** authorize a dictionary replacement: the current
concrete direction remains a renderer choice. Confirmed lexemes, productive
components, and plaintext clauses remain **0**.
