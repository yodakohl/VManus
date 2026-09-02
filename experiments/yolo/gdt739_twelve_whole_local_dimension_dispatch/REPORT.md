# GDT739 report — host-first local dimension of twelve complete wholes

## Outcome

GDT739 replaces the last unconditional family glosses on GDT738's twelve
licensed wholes with a host-first occurrence renderer. The compact invariant is
now only **field class plus ordered level**. A local quality, amount, counted
process passage, dry/moist orientation, or broad carrier is spoken only when an
eligible host occurs within two cells.

This is a material correction. The former whole cards favored heat, dry,
moist/soaked, or fraction orientations. Those orientations remain useful
candidates, but they do not hold locally often enough to be spoken at every
licensed occurrence.

The experiment covers exactly 202 cached positions of twelve complete forms.
It opens no page and exports no substring or lexeme.

## Local-host footprint

The radius-five audit contains 1,373 neighboring tokens. After alternate-reader
exactness, W2/W3 confidence, zero-composition, known-cell, non-target,
non-opaque-head, retired-patient, and explicit-axis gates, 230 contacts survive.

| Maximum distance | target occurrences with any eligible host |
|---:|---:|
| 1 | 62 |
| 2 | 98 |
| 3 | 121 |
| 5 | 146 |

Only distance one or two is active. Thus 104/202 positions have no eligible
active-radius host at all. Distance three to five remains visible as a useful
candidate deck, but cannot make the renderer sound more certain than the local
record actually is.

## Scalar dispatch: one form family, several factual axes

The 172 `ain/kain/kaiin/kar` occurrences use a nearest-unanimous-ring rule. A
quality root plus grade/value stem selects a quality degree; an amount,
measure, portion, or explicitly numbered fraction selects amount/portion; a
counted or repeated treatment selects a process passage. A bare verb does not.

| complete form | quality degree | amount/portion | process passage | open/conflict | total |
|---|---:|---:|---:|---:|---:|
| `lain` | 2 | 0 | 0 | 2 | 4 |
| `lkaiin` | 8 | 5 | 3 | 26 | 42 |
| `lkain` | 5 | 4 | 1 | 17 | 27 |
| `lkar` | 4 | 2 | 0 | 23 | 29 |
| `rain` | 8 | 0 | 1 | 5 | 14 |
| `sain` | 14 | 4 | 0 | 35 | 53 |
| `skaiin` | 2 | 0 | 0 | 1 | 3 |
| **total** | **43** | **15** | **5** | **109** | **172** |

Of the 63 selected scalar axes, 35 are immediate and 28 are at distance two;
57 use W3 hosts and seven W2 contacts contribute to the selected rings. The
109 open cases comprise 89 without any eligible local host, 17 with eligible
but untyped context, and three direct conflicts.

This is the key semantic result: the same complete-form family occurs under
quality, amount, and process hosts. A global equation such as `ain = amount`,
`kain = hot`, or `kaiin = heating` is therefore worse than the local model.

Representative positive cases include:

- `lain` on `f111v.31`: the immediate dry grade/class host yields **interner
  Trockenheitsgrad II des Materials**;
- `lkaiin` on `f76r.44`: the numbered fraction/material host yields
  **Mengen-/Portionsstufe III des Materials**;
- `rain` on `f116r.36`: the immediate heat-end-grade host yields **Heißgrad II;
  interner Rückbezug**, while `lkain` later on the same line remains open;
- `lkain` on `f78r.32`: an immediate measure/heat field conflicts with an
  immediate heat-grade field, so the renderer keeps the dimension open.

## State versus result: the old result default was too strong

The 30 `cheol/cheedy/sheedy` positions were manually inspected as state versus
result fields. They divide 22/8, not 18/12 or a universal result series.

| form | occurrences | descriptive state | result/end | broad carrier bound | favored dry/moist host |
|---|---:|---:|---:|---:|---:|
| `pcheol` | 10 | 10 | 0 | 5 | 2 |
| `lcheol` | 8 | 8 | 0 | 2 | 3 |
| `lcheedy` | 6 | 2 | 4 | 2 | 0 |
| `lsheedy` | 4 | 1 | 3 | 0 | 0 |
| `rsheedy` | 2 | 1 | 1 | 1 | 1 |
| **total** | **30** | **22** | **8** | **10** | **6** |

Two result assignments have strong local W2/W3 support. Six are explicit
endpoint/closure best fits and remain labeled as such in the source table.
Most importantly, only six of the 30 positions have a clean local host for the
formerly automatic dry or moist orientation. Neither `lcheedy` nor `lsheedy`
has one in the active radius.

The new defaults are therefore:

- `pcheol/lcheol`: **status field**, locally `Trockenstatus` only with a dry
  host;
- `lcheedy`: **state level II** or, at four enumerated loci, **result/end level
  II**; dry remains open unless locally supported;
- `lsheedy/rsheedy`: **state level II** or enumerated **result/end level II**;
  moist/soaking remains open unless locally supported.

The contrast is visible in the reader. `rsheedy` on `f77v.8` has a clean moist
material host and renders **Feucht-/Einweich-Endstufe II des Materials;
interner Rückbezug**. The other `rsheedy` on `f82r.31` sits in a dry-dominated
line without such a host and remains **Zustandsstufe II; Zustandsachse offen**.

## Carrier binding

Seventy-three of 202 positions bind a broad preparation/material/part carrier;
129 remain carrier-open. The binder copies only the broad class, never the
neighbor's proposed substance. This allows compact entries such as
`Trockenstatus des Materials` or `Mengen-/Portionsstufe III der
Zubereitungsfraktion` without reviving `Drogenholz`, powder, seed, root, or a
species name.

The safe twenty-line reader covers all twelve licensed wholes, 23 focal patches,
and eight section/language registers. Unsupported or retired-patient cells are
shown as `[surface:?]` instead of being padded into fluent recipe prose.

## New working basis

Renderer precedence after GDT739 is:

1. exact bound context/span;
2. licensed complete whole at its enumerated position;
3. invariant compact field class and ordered level;
4. nearest unambiguous eligible host at distance one or two supplies local
   dimension and/or broad carrier;
5. conflict or absence leaves that slot explicitly open;
6. otherwise unknown.

The favored heat/dry/moist/fraction orientations survive as candidate priors in
the profile, not as automatically spoken meanings. Distance-three-to-five
contacts remain discovery evidence only. No head, body, EVA substring, unseen
form, literal patient, species, language, or plaintext clause is promoted.

## Reproduction and validation

Run:

```bash
python3 experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/run.py
python3 experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/validate.py
```

The validator passes 46 independent geometry, scope, dispatch, export, artifact,
and replay checks. Builder replay is byte-identical.
