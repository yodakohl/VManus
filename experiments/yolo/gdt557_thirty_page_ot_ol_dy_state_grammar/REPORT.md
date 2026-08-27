# GDT557 — Thirty-page OT/OL/DY state grammar

## Result

The old six-page distinction has transferred and become a substantially more
useful working mechanism. Across 5,122 events and 793 statements, the three
roots occupy different operational slots:

| root | unchanged value | occurrences | positional signature | default operation |
|---|---|---:|---|---|
| `OT` | DANACH | 404 | right carrier in 402/404 (99.50%) | open/advance the next carrier |
| `OL` | FORTSETZEN | 761 | 199 initial, 85 bridge, 288 terminal, 189 alone | keep the current carrier active |
| `DY` | ABSCHLIESSEN | 705 | left carrier 705/705; statement-final 702/705 | close the current step |

This is the first version in which the three meanings operate together as a
small reader rather than as isolated German glosses:

`OT = NEXT` → `OL = KEEP ACTIVE` → `DY = CLOSE`.

Every one of the 1,870 observed atoms has a default positional realization. No
sequence is discarded for being unusual.

## DY is the closure switch

The marker-only card sequences make the state behavior unusually concrete:

- 704 cards have DY as their last state operator; 702 are statement-final
  (99.72%);
- 951 marker-bearing cards contain no DY; only twenty are statement-final
  (2.10%);
- `OT+DY` closes 86/86 statements;
- `OL+DY` closes 74/74 statements;
- `OT+OL` closes 0/38 statements.

So OT and OL determine how a carrier enters or remains active, while DY
predicts when that working unit closes. This also explains why OT by itself is
not a boundary marker: only 5/279 pure-OT cards end a statement, whereas all
86 OT+DY cards do.

## The complete nine-sequence inventory

Removing all non-state atoms leaves exactly nine observed sequences in 1,656
marker-bearing cards:

| sequence | cards | working reading | statement-final |
|---|---:|---|---:|
| `OL` | 619 | continue the current carrier | 14 |
| `DY` | 544 | close the current step | 542 |
| `OT` | 279 | open the next carrier | 5 |
| `OT+DY` | 86 | open the next carrier, then close it | 86 |
| `OL+DY` | 74 | continue the carrier, then close it | 74 |
| `OT+OL` | 38 | open the next carrier and keep it active | 0 |
| `OL+OL` | 14 | continue, then continue the new active scope | 1 |
| `DY+OL` | 1 | close the local step, then continue | 0 |
| `OL+OT` | 1 | continue the current carrier, then open the next | 0 |

There is no three-marker card and no `DY+OT`. The inventory is not a proposed
historical phrase list; it is the exhaustive projection of existing recipes
onto the three current control roots.

## Pair order composes

The dominant direction is start → continue → close:

| pair | joint cards | dominant order | reverse |
|---|---:|---:|---:|
| OT / OL | 39 | OT→OL 38 | OL→OT 1 |
| OT / DY | 86 | OT→DY 86 | 0 |
| OL / DY | 75 | OL→DY 74 | DY→OL 1 |

The two reversals make the model better, not worse, because both have a direct
reading in written order:

- f1r `roloty`, `R+OL+OT+Y`: continue the marked carrier; then open the next
  active item;
- f75r `okeedyqol`, `OK+EE+DY+OL`: set at grade II; close that local step; then
  continue.

The second card is independently one of GDT556's three internal DY closures.
Its exceptional order therefore predicts exactly the exceptional scope already
observed there.

## Twelve edge rows all retain defaults

The full atlas exposes only two bare OT cards, five post-DY attachments, three
internal DY closures and the two reverse pair observations. These are twelve
category rows but only eight unique events because the informative DY cases
belong to more than one category.

- bare `qot` and `ot` take the next carrier from their same-statement context;
- two `DY+D_LABEL` and two `DY+L` forms close before a label/linkage tail;
- `DY+OL` closes the local step and explicitly reopens continuation;
- all three internal-DY cards continue with a later card in the same statement.

Nothing remains without a state reading.

## Page transfer

All 28 admitted pages that contain running cards contain all three operators.
The current four-page cohort is especially clean: OT has a right carrier 41/41,
all 66 DY cards are statement-final, and its five OT+OL, eight OT+DY and two
OL+DY pairings all follow the dominant order. The two remaining admitted pages,
f69v and f70v, are local-only pages with no running events and are explicitly
retained as zero rows.

Compared with GDT478, the evidence expands from 69 OT/OL slots in sixty selected
local events to 1,870 OT/OL/DY atoms in 1,656 complete running cards. The old
roles survive; the full corpus adds the closure switch and reveals the two
legible reverse compositions that the six-page selection did not contain.

## Working reader adopted

For the current sidequest edition, use these defaults:

1. `OT · X`: “danach X”; `X · OT · Y`: “nach X folgt Y”; bare OT obtains X
   from the sentence context.
2. `OL · X`: “weiter mit X”; `X · OL · Y`: “X in Y weiterführen”;
   `X · OL`: “X weiterführen”; bare OL retains the active contextual carrier.
3. `X · DY`: close X. If DY is the last card operation, close the statement as
   well; if another atom or card follows, close only the current local step and
   continue in written order.

These three rules are now a better base than treating OT, OL and DY as free
German connective words. They predict direction, compound order and closure.

## Validation and ceiling

The independent validator passes 37/37 checks, including guarded old-source
materialization, exact atom positions, all nine sequences, all pair orders,
page transfer, GDT478 seed values, exact parity with GDT556's 705 DY rows and a
byte-identical rebuild.

This is an exploratory state renderer for existing roots, not decipherment or
confirmed historical syntax. No surface, recipe, segmentation, root value,
statement boundary, page, plaintext, language, object or historical codebook
identity changes.

## Next route

Use the state reader to isolate the material immediately carried by OT and OL,
then ask whether the `E/EE/EEE` grade ladder changes only the carried value or
also changes the operator scope. That can turn the next pass into concrete
compound meanings without reopening pages or retuning these three roots.
