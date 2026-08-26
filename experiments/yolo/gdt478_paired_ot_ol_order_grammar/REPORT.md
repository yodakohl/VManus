# GDT478 — paired OT/OL order grammar

## Result

The local order system reduces to two distinct state operations:

| root | unchanged value | state operation | observed directional forms |
|---|---|---|---|
| OT | DANACH | start the next sibling unit | 40 forward, 1 bridge, 0 backward |
| OL | FORTSETZEN | keep the current unit active | 9 forward, 10 bridges, 9 backward |

All 69 slots in sixty events now have a positional phrase and a state
operation. OT has a right-hand successor in 41/41 cases and never merely holds
the left carrier. OL is the flexible continuation operator described by
GDT477.

## The one OT bridge

Forty OT slots have the familiar `OT · X` form: “danach X”. The only medial
case is f77r.8 `dotedy`:

`[BADSTATIONSNAME:d] · DANACH · [BADSTATIONSNAME:edy]`

Its literal working reading is consequently “nach Badstation d folgt
Badstation edy”. This is not an exception to next-sibling scope. It is the one
case where both the previous and next sibling names are written inside the same
event. GDT461 independently preserves its internal `ot` channel: 55/56 running
internal extension types, 150 events and nineteen pages.

The normal prefix channel is even cleaner: `ot-` matches 66/66 running
extension types, 211 events and 24 pages.

## The seven OT+OL events

Seven events carry both roots:

| forms | root sequence | count | state reading |
|---|---|---:|---|
| `otolam`, `otol`, `otolaiin`, `otokol`, `otoldy`, `otold` | OT → OL | 6 | start next unit, then keep it active |
| `otolarol` | OT → OL → OL | 1 | start next unit, bridge it to the output, keep that output active |

OT precedes every OL in 7/7. This gives `otol` a simple compositional reading:
“next unit; continue that unit.” It need not be stored as a separate complex
word, and `otolarol` merely repeats the OL operation after `AR=AUSGANG`.

## Name placement

Among the 41 OT slots, 25 are name-free, fifteen precede a learned name and one
lies between two names. None follows the last name and none is terminal. OT is
therefore consistently right-projecting even when the old function-only recipe
made an internal name bridge look bundle-leading.

## Complete paired renderer

The final observed rule set has five cells:

- `OT · X` → next carrier X;
- `X · OT · Y` → after X follows Y;
- `OL · X` → continue with X;
- `X · OL · Y` → carry X into Y;
- `X · OL` → keep X active.

No `X · OT` cell is observed. The missing cell is meaningful for the working
grammar: DANACH always points to something new on its right, whereas
FORTSETZEN may close by retaining what is already on its left.

## Next route

Compile one definitive six-page local microrecord edition over all 183 events
and 135 GDT475 records. It should combine GDT476's selected grammatical model
with this paired order renderer, replacing vague “danach/weiter” wording with
the exact directional scope while preserving every alternative reading in the
machine table. This integrates new information and does not reopen the older
edition route or any new page.

## Validation and ceiling

The validator passes 83/83 checks: exact 69-slot replay, 41/28 root counts,
40+1+0 OT direction, 41/41 right successors, GDT477's complete OL replay,
sixty events, seven joint events with 7/7 OT-before-OL, five rules, both OT
carrier channels, all six pages and a byte-identical rebuild.

This remains an exploratory order renderer. No root meaning, learned name,
surface, recipe, selected model, event, page, object identity, plaintext,
language, confirmed syntax or lexeme changes.
