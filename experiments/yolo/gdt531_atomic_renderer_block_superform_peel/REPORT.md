# GDT531 — `saiis` inherits the inside of exact old `saiisol`

## Result

`PASS_ATOMIC_RENDERER_BLOCK_SUPERFORM_PEEL`.

The best current composition is now:

```text
saiis = S+A_ADDR+IIN+S
        WÄHLEN · HIER · STUFE · WÄHLEN
```

Short working reading: **“Wählen; hier die Stufe wählen.”**

The decisive larger pattern is already present in the old deck:

```text
saiisol = S+A_ADDR+IIN+S+OL
saiis   = S+A_ADDR+IIN+S
```

Removing terminal visible `ol` removes terminal recipe atom `OL`, leaving the
current form and recipe unchanged internally. The relation is exact, and the
same right-edge `ol↔OL` removal occurs in 29 of 33 eligible old comparisons.

## What changed

The previous working analysis was:

```text
saiis = S+IIN+S
        WÄHLEN · STUFE · WÄHLEN
```

That lean segmentation remains mechanically possible, but it skips the address
atom preserved by the exact old superform. GDT529 already ranked
`S+A_ADDR+IIN+S` first; the larger form now supplies the missing compositional
reason to adopt it.

There is also a serious runner-up:

```text
saii | s = S+AIIN | S
```

Old `saii=S+AIIN` occurs once, and the same-recipe `saiin` family occurs twenty
times. This makes `S+AIIN+S` a useful alternate reading, but it explains the
target through two independent cards. Exact `saiisol` explains the whole
target as one preserved interior and is therefore the more specific carrier.

## Whole-edition comparison

The block-peel construction was applied to all 159 current forms:

- 29 licensed routes occur across 15 surfaces;
- 28 reconfirm an already rank-one working recipe;
- only `saiis` supports a different rank-one candidate;
- no working selection becomes worse.

| Working edition | Rank 1 | Top 2 | Top 3 | Top 5 | Rank sum |
|---|---:|---:|---:|---:|---:|
| after GDT530 | 153 | 157 | 158 | 158 | 173 |
| after GDT531 | **154** | **158** | 158 | 158 | **171** |

Five discrepancies remain:

```text
aiicthy  dairykodas  dalcheeeky  dsholdaiir  qef
```

## Scope of the result

This is not a license to strip `ol` everywhere. The update requires an exact
old superform, exact preservation of the remainder, a matching recipe-block
removal, and a strong position-matched old signature. Those conditions select
only `saiis` among the unresolved forms.

## Next move

The next high-information target is `dsholdaiir`. Its current disagreements
can be compared against the exact old cards `d`, `shol`, and `daiir`; notably,
`daiir=DA+IIN+R` also occurs later in the same f66r prose block. That permits a
same-owner whole-form composition test without opening another page.
