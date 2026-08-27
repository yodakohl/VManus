# GDT533 method

## Question

Which of the two complete exact-card recipes for `dairykodas` better preserves
the old card hierarchy: terminal `odas=O+DA+S`, or overlapping `kod|as`?

## Inputs

- GDT407's 4,576 old running events and invariant exact cards;
- GDT522's position-matched old edit signatures;
- GDT516's current target statement;
- GDT529's twelve finite `dairykodas` candidates;
- GDT532's exact-card tiling atlas and complete 159-form working edition.

No page beyond the already admitted thirty is used.

## Method

GDT532 left exactly two tileable candidate recipes:

```text
rank 1: dair | y | k   | odas
        D_ADDR+AIR | Y | K | O+DA+S

rank 2: dair | y | kod       | as
        D_ADDR+AIR | Y | K+O+D_ADDR | A_ADDR+S
```

Both use four exact cards, so card count alone does not decide them. Compare
four more specific properties:

1. whether the route preserves the longest exact terminal card;
2. whether that terminal card has a nested exact-card derivation;
3. support for every adjacent atom pair in the complete candidate recipe; and
4. whether the visible ending supports one unconditional suffix value.

The first route preserves old `odas=O+DA+S`. Its inside is independently old
`das=DA+S`, and the larger form differs by exact initial `o/O`:

```text
das  =   DA+S
odas = O+DA+S
```

The old left-edge `o/O@LEFT/LEFT` signature has 31/37 support,
`p=0.797468354`, and reliability `0.939393939`. Thus `odas` is simultaneously
an exact whole card, a nested `o|das` composition, and the complete visible
suffix of the target.

All adjacent pairs of the selected recipe have at least two old occurrences:

```text
D_ADDR+AIR 16   AIR+Y 2   Y+K 69
K+O 21          O+DA 6    DA+S 2
```

The rival is not nonsense: `kod=K+O+D_ADDR` and `as=A_ADDR+S` are exact old
cards. But their join introduces `D_ADDR+A_ADDR`, seen only once in 4,576 old
events and never followed by `S`. More importantly, it breaks the exact
visible `odas` tail across the `kod|as` boundary.

Visible `...as` is contextual rather than one suffix: six invariant ending
types include `A_ADDR+S`, `DA+S`, `O+DA+S`, and even `OK+EE+Y`. The selection
therefore uses exact whole `odas`, not a global `as` rule.

## Decision rule and claim ceiling

Prefer rank one only because it preserves an exact terminal whole card that
also has a matching nested exact superform relation, while the rival splits
that tail and has the weaker boundary bottleneck. This revises only
`dairykodas`; the remaining 158 choices are inherited unchanged.

The recipe reads:

```text
D_ADDR+AIR = HIER · BAHN
Y          = POSTEN
K          = GEBEN
O          = AUSFÜHRUNG
DA+S       = STUFE II WÄHLEN
```

Compact reading: “Hier entlang der Bahn posten; zur Ausführung geben und Stufe
II wählen.” It is an exploratory functional reconstruction, not confirmed
plaintext or a transferable `odas/as` suffix dictionary.
