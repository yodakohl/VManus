# GDT698 — exact action surfaces do not transfer a participant frame

Status: `PASS_V71_6_SURFACES_10_OCCURRENCES__9_EXISTING_MATCHES_1_UNBOUND_HELD__0_CROSS_REPLAYS__ZERO_WORD_DELTA`

## Result

The six action surfaces from GDT697 occur only ten times in the complete
479-token scope:

| surface | occurrences | already bound | unbound | admitted frame templates |
|---|---:|---:|---:|---:|
| `qokamdy` | 1 | 1 | 0 | 1 |
| `ykaiin` | 2 | 2 | 0 | 2 |
| `yteeeor` | 1 | 1 | 0 | 1 |
| `qey` | 1 | 1 | 0 | 1 |
| `qol` | 4 | 3 | 1 | 3 |
| `qodar` | 1 | 1 | 0 | 1 |

All nine exact template matches occur at the template's own already bound
source. There is no cross-occurrence replay and therefore no new relation or
microrecord.

## Why the last `qol` remains open

At f77r.38#6 the immediately preceding `chcphey` is the written object:

> Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum
> zugeben.

At #9 the local text is instead:

> Holz, kalt auf Stufe III; mittlere Feuchtstufe erreicht.
> **[Teilnehmerbindung offen:]** Drogenstoff zugeben.

This does not reproduce C005 because the immediate predecessor is the state
`shedy`, not `chcphey`. It does not reproduce C004 because the written `Hierzu`
and hot wood-preparation share are absent. It does not reproduce C008 because
the two `qol` are separated by `ltaiin shedy` and a new nominal clause rather
than sharing the exact `olkar y qol qol` frame.

Calling the last sentence “add drug material to the cold wood” would be a new
nearest-noun binding. V71 does not make it.

## What the repeated surfaces do show

`ykaiin` keeps the heat instruction at both occurrences but accepts two
different admitted sources: a written wood powder and the output of a measuring
action. `qol` keeps the addition instruction across four occurrences but its
three bound cases use three different frames: immediate written object,
written destination plus reference, and repeated destination carry.

Thus the action surface can stabilize the operation while failing to determine
the participant binding. The missing information is one level above the exact
string: a participant-class and geometry signature, not a larger word gloss.

## Freeze and next route

- 6 surfaces, 10 occurrences, 9 source-only matches, 0 cross-replays.
- 1 unbound action held; 0 new edges or microrecords.
- 479 token glosses, 51 line translations and 3 bound spans unchanged.
- 0 new meanings, pages or f84/f84r access.

The broad all-83 participant-class pass is already substantially covered by
GDT595--GDT597 and is therefore not the next route.  The next useful pass is a
five-case audit of the already identified backward-referential HEAT actions:
two admitted prototypes and three open occurrences.  It asks only whether an
objectless heat action can inherit one immediately preceding complete nominal
block or an admitted action output under the same exact geometry.  It may not
fall back to a generic object, nearest noun, block splitting or an invented
result.
