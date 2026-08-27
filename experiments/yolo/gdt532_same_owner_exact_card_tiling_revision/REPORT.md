# GDT532 — three exact cards expose the hidden `daiir` tail

## Result

`PASS_UNIQUE_SAME_OWNER_EXACT_CARD_TILING_REVISION`.

The best working composition of `dsholdaiir` is now:

```text
d       | shol                | daiir
D_ADDR  | SH+OL               | DA+IIN+R
HIER    | HALTEN · FORTSETZEN | STUFE II · MARKIEREN
```

Short working reading: **“Hier halten und fortsetzen; Stufe II markieren.”**

The three visible cards are not invented for the target:

- `d=D_ADDR` occurs eleven times in the old running deck;
- `shol=SH+OL` occurs eighteen times across four registers;
- `daiir=DA+IIN+R` occurs twice as an old local card on f70v.

The tail then crosses roles intact. `daiir=DA+IIN+R` occurs in current prose on
f31r and f66r. Its f66r occurrence is especially useful: target
`dsholdaiir` sits at f66r.58, while exact `daiir` appears at f66r.62 in the
same prose block and owner. Between them, f66r.60 also contains
`sholdy=SH+OL+D_ADDR+Y`, preserving the middle `SH+OL` package locally.

## Why the former reading changes

The inherited analysis was:

```text
D_ADDR+SH+OL+D_ADDR+IIN+R
HIER · HALTEN · FORTSETZEN · HIER · STUFE · MARKIEREN
```

That recipe is mechanically plausible and was GDT529 rank two. But it requires
the visible tail `daiir` to be split against its exact whole-card value. None of
the twelve finite alternatives except rank six can be tiled completely from
the old exact-card inventory:

| candidate | rank | exact tilings |
|---|---:|---:|
| `D_ADDR+SH+OL+D_ADDR+AIIN+R` | 1 | 0 |
| `D_ADDR+SH+OL+D_ADDR+IIN+R` | 2 | 0 |
| `D_ADDR+SH+OL+DA+IIN+R` | **6** | **4** |
| all other nine candidates | 3–5, 7–12 | 0 |

The four rank-six routes differ only in whether already compositional cards are
split further (`shol` versus `sh|ol`, `daiir` versus `daii|r`). The shortest
route preserves both larger cards and is therefore `d|shol|daiir`.

## Residual-wide comparison

This was not a search only inside the desired word. The same exact-card test
was applied to all five GDT531 residuals. `dairykodas` has twelve routes but
they support both rank one and the inherited rank two, so tiling does not
decide it. `aiicthy`, `dalcheeeky`, and `qef` have no candidate-matching route.
Only `dsholdaiir` has one and only one tileable recipe.

## The rank conflict is real

Adopting the exact composition moves this one working choice from candidate
rank 2 to rank 6. The accumulated heuristic agreement diagnostics change as
follows:

| Working edition | Rank 1 | Top 2 | Top 3 | Top 5 | Rank sum |
|---|---:|---:|---:|---:|---:|
| after GDT531 | 154 | 158 | 158 | 158 | 171 |
| after GDT532 | 154 | 157 | 157 | 157 | 175 |

That cost is accepted because those ranks were trained to reproduce the old
provisional recipe, while this pass supplies a more direct visible whole-card
composition. GDT532 therefore changes the semantic working layer, not GDT529's
candidate generator or scores.

## Next move

Four forms remain genuinely undecided:

```text
aiicthy  dairykodas  dalcheeeky  qef
```

`dairykodas` should be attacked next because exact cards already reduce it to
two complete recipes. The decisive question is whether final `odas` behaves as
the whole package `O+DA+S` or the target instead preserves `kod|as` as
`K+O+D_ADDR | A_ADDR+S`. That can be tested inside the existing f66r block and
old `odas/kod/as` families without opening another page.
