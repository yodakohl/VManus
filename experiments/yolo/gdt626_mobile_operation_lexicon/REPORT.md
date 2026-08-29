# GDT626 report — a four-cell value reader replaces the generic operation

## Result

The search for the word that meant “take,” “process,” or “pass onward” failed
for a productive reason. Its strongest apparent candidate, `daiin`, is not an
atomic instruction. It belongs to this exact family:

| head `da` | occurrences | stable in all three readings | working parse |
|---|---:|---:|---|
| `dan` | 17 | 14 | `d + I` |
| `dain` | 193 | 149 | `d + II` |
| `daiin` | 721 | 602 | `d + III` |
| `daiiin` | 17 | 12 | `d + IV` |

The same architecture is manuscript-wide. The regex `^(.*a)(i*)n$` returns
5,176 tokens under 545 heads. The internal minim count stops absolutely after
three: 102 value-I, 1,565 value-II, 3,404 value-III, and 105 value-IV tokens;
there is no fifth cell. Twenty-eight heads have I/II/III and fifteen have all
four values.

This is not free handwriting noise. There are 136 physical lines on which two
or more values of exactly the same head coexist; 96 survive all three readings.
The two lines with three values are exceptionally clear:

```text
f42v.2  ... dan dain otol daiin
         ... d-I d-II ... d-III

f38v.6  ... daiin daiiin dain dain
         ... d-III d-IV d-II d-II
```

The second line is completely identical in ZL3b, IT2a, and RF1b. These are
alternate readings, but their agreement removes a simple transcription-error
explanation.

## Why I/II/III/IV is the best practical default

Fifteenth-century medical recipes write Roman quantities with a terminal
`j`: `j`, `ij`, `iij`, `iiij`. If Voynich terminal `n` performs the same final
stroke function, the exact surface mapping is:

```text
-an    I       -ain   II       -aiin   III       -aiiin   IV
```

The comparison is unusually close, but still analogical. EVA deliberately
exposes visible minim strings that earlier transcription alphabets sometimes
treated as the single units N and M. Nothing in EVA itself supplies a number.

The strongest countermodel is therefore not random spelling but a four-grade
inflectional or abbreviation slot. Its distributions really are conditioned:
value III among II+III is 0.821 in Herbal but 0.455 in Biological material,
and 0.840 for Hand 1 versus 0.608 for Hand 2. Value I is also line-final in
38/102 cases, compared with 368/3,404 value-III cases. GDT626 keeps that rival
alive. Yet conditioning does not contradict a numerical code: medieval
quantities and degrees also vary by content and scribe. The new reader is a
working default because it predicts concrete compounds that the pure
inflection account does not yet interpret.

## Concrete quality readings

The inherited `k/t × ch/sh` layer supplies hot/cold × dry/moist. Forty-seven
safe tokens on 33 pages combine one of those quality cores with the new value
tail; 37 are stable across all three readings. The direct registered forms
include:

| surface | composition | practical reading |
|---|---|---|
| `kchan`, `kchain`, `kchaiin` | `k+ch+I/II/III` | hot-dry, degree I/II/III |
| `okchan`, `okchain`, `okchaiin` | `o+k+ch+I/II/III` | hot-dry degree I/II/III in o-scope |
| `qokchain`, `qokchaiin` | `qo+k+ch+II/III` | hot-dry, degree II/III |
| `qotchain`, `qotchaiin` | `qo+t+ch+II/III` | cold-dry, degree II/III |
| `otshaiin` | `o+t+sh+III` | cold-moist, degree III |

Four direct line readings now say something specific:

```text
f35r.13 qokchaiin   hot-dry, degree III
f44v.2  qokchain    hot-dry, degree II
f25r.4  qotchain    cold-dry, degree II
f28r.3  qotchaiin   cold-dry, degree III
```

This mirrors real early-fifteenth-century materia-medica phrasing. Wellcome
MS.542 describes aloes as hot and dry in the second degree and white hellebore
root as hot and dry in the third degree. Pal.lat.1234 organizes drugs under
hot-degree rubrics from first through fourth. The manuscripts do not decode
Voynich, but they demonstrate that the exact semantic architecture existed.

## Concrete plant-part readings

Twenty-eight tokens combine one inherited plant-part head with the same value
tail; 22 occur in Herbal. Most useful is the cth series:

| surface | occurrences | practical reading |
|---|---:|---|
| `cthan` | 2 | leaf/above-ground drug material, value I |
| `cthain` | 4 | leaf/above-ground drug material, value II |
| `cthaiin` | 11 | leaf/above-ground drug material, value III |

The image and layout pass supports the composition but not an absolute unit:

```text
f18r.5  tchor shor cthaiin cthol chlol chom
                    ^^^^^^^
          leaf/above-ground drug material, value III
```

`cthaiin` is embedded in one uninterrupted, list-like sequence of reproductive
and cth-family part forms. On the same page a different construction reads:

```text
f18r.12 ... qokchy cthy
             hot-dry leaf material
```

Thus the reader predicts two independent compound orders: quality + part and
part + value. It does not yet decide whether the part value is a dose, amount,
Galenic degree, or a technical class. The drawing has many leaves and does not
license “three leaves,” “three drachms,” or any other absolute measure.

## What `daiin` now says

On f45v.2 the old generic rendering is replaced:

```text
chor | daiin | cthy
Blüten-/Pflanzenteil | d-Wert III | Blattgut
```

This is not yet a polished sentence, because the `d` head and attachment
direction are unknown. But it contains real, falsifiable information: the
middle form occupies cell III of a four-cell `d` paradigm. It is no longer
permitted to hide the uncertainty behind “perform the work step,” nor to call
the whole word “and,” “item,” or “take.” A learned local list-linking use of the
very frequent surface remains possible in addition to its composition.

## Working dictionary update

The compact V3 dictionary now contains the four value endings, their quality
compounds, the cth and chor part-value compounds, and the open `d` head. This is
the first current sidequest layer that predicts new whole-form meanings by
combining already used stems with an independently recurrent suffix.

The next route is narrow: identify what kind of value each head selects. Quality
heads predict degree; part/material heads predict dose or quantity; grammatical
heads predict inflection. The fastest discriminator is a repeated head under a
fixed local frame with an independently countable image, ingredient unit, or
degree referent. Until then the structural four-cell slot is firm, while its
numeric semantics remains the best practical theory rather than a solved
plaintext fact.
