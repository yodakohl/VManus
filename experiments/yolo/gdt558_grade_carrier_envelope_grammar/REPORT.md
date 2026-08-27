# GDT558 — Grade carrier envelope grammar

## Result

All 333 grade occurrences in OT/OL-bearing cards now have a short default, and
they require only eight control envelopes. The useful rule is simple:

> `E/EE/EEE` supplies the value Grad I/II/III inside the current carrier;
> OT, OL and DY determine how that carrier opens, continues and closes.

The grade does not need a long lexical gloss and it does not alter the three
state operations.

| envelope | occurrences | default |
|---|---:|---|
| `OT>G<END` | 97 | danach X auf Grad n |
| `START>G<OL` | 91 | X auf Grad n; X weiterführen |
| `OT>G<DY` | 72 | danach X auf Grad n; X abschließen |
| `OL>G<DY` | 29 | X weiterführen auf Grad n; X abschließen |
| `OL>G<END` | 27 | X weiterführen auf Grad n |
| `OT>G<OL` | 9 | danach X auf Grad n; X weiterführen |
| `OL>G<OL` | 7 | X weiterführen auf Grad n; weiter aktiv halten |
| `START>G<DY` | 1 | X auf Grad n; X abschließen |

Together these cover 214 E, 114 EE and five EEE atoms in 326 cards, 222
statements and 22 pages. Seven cards contain two grades; each grade receives
its own nearest-control envelope.

## OT and OL do different work around the grade

OT is perfectly directional here. It is the left boundary of all 178 grade
occurrences in an OT card and the right boundary of none. Thus OT never says
“retain the grade on my left”; it opens the graded carrier on its right.

OL is genuinely two-sided:

- it is the left boundary of 63 graded blocks, so it continues forward into
  the block;
- it is the right boundary of 107 blocks, so it retains the graded block on
  its left;
- seven `OL>G<OL` blocks do both;
- in `OK+EE+DY+OL`, DY separates the grade from OL, so OL begins only after the
  grade-II step has closed.

This exactly extends GDT557's operator grammar into actual carried material.

## Same-envelope action heads are concrete

One hundred fifty-one grades have at least one visible action to their left
inside the same control envelope. The selected host is the single action or,
for a chain, its last ordered action pair. All 151 are already licensed by
GDT420 or GDT421. Examples:

- `SH+E+OL`: halten auf Grad I; weiterführen;
- `OL+K+EE+DY`: weiter mit geben auf Grad II; Schritt schließen;
- `START>[CH+P+EEE+D_ADDR]<OL`: nehmen und einsetzen auf Grad III; an der
  bezeichneten Stelle; weiterführen;
- `OL+T+E+DY`: weiter mit einstellen auf Grad I; Schritt schließen.

The grade therefore attaches cleanly when its action is visible inside the
same block.

## Do not force an old action through the control boundary

The remaining 182 grades have no visible action to their left inside their
block. An older running action is available for 152 of them. Blindly binding
the grade to it looks tempting, but it creates eighteen direct clashes with
the existing head cards:

- ten inherited `CHD` + E;
- five inherited `CHD` + EE;
- two inherited `CH` + EEE;
- one inherited `SH` + EEE.

Sixteen occur after OT and two after OL. Nothing needs resegmentation. The
short default is simply “carrier on grade n” inside the visible control
envelope. The inherited action may remain contextual background, but the
reader does not claim that the grade modifies it across the boundary.

This resolves forms such as:

- `oteedy` after CHD: “afterward, carrier at grade II; close,” not the blocked
  “work at grade II”;
- `oteees` after CH: “afterward, carrier at grade III,” not the blocked “take
  at grade III”;
- `oleeed` after SH: “continue with carrier at grade III,” not the blocked
  “hold at grade III.”

## The rung changes, the envelope does not

Replacing a sole E/EE/EEE by `G` reveals seventeen exact multi-rung recipe
families containing 235 cards. The largest is the complete three-rung family:

```text
OT+E+DY     37 cards
OT+EE+DY    28 cards
OT+EEE+DY    1 card
```

All 66 mean “afterward, carrier at grade n; close.” Sixteen more families have
both E and EE, including `OT+G+Y`, `SH+G+OL`, `OK+G+OL`, `OL+K+G+DY` and
`OL+SH+G+DY`.

The boundary result is decisive for the working reader: all 94 cards in
DY-ending multi-rung families are statement-final, whereas only 2/141 cards in
the same kind of multi-rung families without DY are final. Changing the rung
does not move the boundary; changing the control envelope does.

## Concrete dictionary consequence

Keep the atomic entries short:

```text
E    Grad I
EE   Grad II
EEE  Grad III
OT   nächsten Träger eröffnen / danach
OL   laufenden Träger fortsetzen
DY   laufenden Schritt abschließen
```

Longer meanings belong to composition, not to any one atom. Every one of the
25 observed grade+state projections has a written-order default in the
artifact table, so no observed sequence is left blank.

## Validation and ceiling

The independent validator passes 31/31 checks, including all 333 positions,
eight envelopes, 25 projections, seventeen rung families, 151/151 visible
host licenses, the exact eighteen inheritance hazards and a byte-identical
rebuild.

This is an exploratory working grammar. It changes no root, grade value,
recipe, surface, action state, sentence boundary or page, and it does not claim
historical plaintext, syntax, language, codebook identity or objects.

## Next route

Apply the same carrier-envelope reader to the four common argument values
`Y/AIIN/AIN/OR` (post/item, value, share, unit). Search exact substitution
families inside fixed OT/OL/DY envelopes and give every observed argument-state
sequence a short compositional default without opening a page.
