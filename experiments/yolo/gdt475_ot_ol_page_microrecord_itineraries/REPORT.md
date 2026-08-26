# GDT475 — OT/OL page microrecord itineraries

## Result

`OT=DANACH` and `OL=FORTSETZEN` now have different, concrete jobs in the local
address stream:

| root | occurrences | bundle-leading | later-event-leading | event-internal |
|---|---:|---:|---:|---:|
| `OT` | 41 | 40 | 1 | **0** |
| `OL` | 28 | 11 | 1 | **16** |

OT never sits inside an event. It always opens one: forty times it is the first
atom of the whole locus bundle, and once it opens the second card at the same
locus. OL is genuinely a continuation operator: eleven occurrences continue
the previous locus record, one continues with a later card at the same locus,
and sixteen hold the active relation/action inside a card.

This is exactly the distinction suggested by the older GDT429 running profile
but now made concrete inside the complete address edition: OT opens the next
equal-rank unit; OL keeps the current unit going.

## From 146 bundles to 135 records

The boundary inventory is complete:

| boundary role | bundles |
|---|---:|
| page start | 6 |
| explicit next sibling via leading OT | 39 |
| explicit continuation via leading OL | 11 |
| unmarked new visible locus | 84 |
| unmarked new locus with only internal order control | 6 |

Attaching the eleven OL-led bundles to their predecessors converts 146 locus
bundles into 135 microrecords: 127 single-locus records, five two-locus chains
and three three-locus chains. The eight nontrivial chains contain nineteen
bundles and exactly eleven OL joins.

Examples:

- f72r2.31 → f72r3.2 → f72r3.3: an instruction is followed by an OL-labelled
  star entry and then an OL address continuation;
- f77r.1 → f77r.2: a two-name station record continues with
  `OL + [BADSTATIONSNAME:kchs]`;
- f89r1.1 → f89r1.2 → f89r1.3: an explicit drug-handling instruction continues
  with two OL-qualified drug entries;
- f89r1.11 → f89r1.12: exact-package `ykyd` is followed by an OL continuation
  and an explicit `NEHMEN · GRAD I · WÄHLEN` card.

## Why this helps the translation

Previously `DANACH` and `FORTSETZEN` were broad dictionary values. They now
predict different reading operations:

- leading OT says “start the next sibling microrecord”;
- leading OL says “do not start over; attach this locus to the previous
  microrecord”;
- internal OL says “continue the current card's action or qualifier”.

That is much less ambiguous than translating both as a vague “then/continue”.
It also explains forms such as `otol...`: OT opens the next record while OL
inside that record says the carried operation continues. The two roots are not
synonyms and do not compete for one slot.

## Six page itineraries

The readable artifact prints all 135 records on f17r, f71v, f72r, f77r, f88v
and f89r. Every entry retains its GDT474 address/instruction/catalogue choice;
continuation loci are indented beneath the record they extend. No surface or
name is omitted.

## Next route

Use these boundary roles to revisit the 64 GDT474 grammatical ties. A leading
OL continuation can inherit the previous record's headword or action; a leading
OT sibling must open a fresh one; an internal OL cannot choose the page
boundary. Apply only those three context cues and measure how many
address/catalogue ties become one fluent page reading without retuning a root.

## Validation and ceiling

The validator passes 60/60 checks, including all OT/OL positions, boundary
roles, 135 record memberships, eight continuation chains, six page totals,
both exact-package recipes, unchanged GDT474 model/readings and a byte-identical
rebuild.

The scope interpretation is a creative working grammar, not confirmed syntax
or plaintext. No root meaning, name, model, spelling, event, page, object,
language or lexeme is added.
