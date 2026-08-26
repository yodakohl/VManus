# GDT436 — the reader can carry its own context

## Result

The GDT435 safety repair no longer needs hand-entered state.

Starting only from the ordered GDT415 event stream—page, register, visible
owner and component recipe—the driver reconstructs all 4,576 inherited-state
decisions, all 4,576 event clauses and all 715 full statements exactly. No
event ID or inherited-state column is used as input.

## The whole memory

There are 57 owner banks. Each stores only:

- the last explicit action;
- the last explicit argument.

A new owner starts empty. Returning to an earlier owner restores that owner's
bank. A physical statement boundary does not by itself erase the state, and a
pure closing card does not invent an inheritance. Unknown atoms and unlicensed
recipes stop before they can alter either slot.

This is enough to reproduce the current 1,598 inherited-action events and
2,096 inherited-argument events exactly.

## What it says about the 49 future cards

The main deck is not a collection of 49 standalone sentences:

- 21 cards explicitly contain both action and argument;
- fourteen contain an argument but need the active action;
- thirteen contain an action but need the active argument;
- `AIR+OL` needs both.

Every card now has an empty-state and a state-supplied reading in all five
registers. The 21 self-contained cards ignore the seed state as they should;
all 28 context-dependent cards change when the missing state is supplied.

## Practical use

`stream_read.py` is the interface to use on a later admitted page after its
visible forms have been segmented into the frozen components. It decides the
intake tier, carries the correct owner bank, renders the clause, and stops on an
unlicensed recipe. This closes the operational gap between “we have a card
reading” and “we can read it in a running passage.”

All 33 checks pass. No component meaning, surface prediction, or page was
added. The exact roundtrip shows that the implementation matches the current
working theory; it is not independent confirmation of that theory.
