# GDT584 — statement-wide collocation polish

## Outcome

GDT584 succeeds at the intended grammar polish without reopening the whole
working dictionary. The decisive change is compositional: the reader now joins
every written packet to its exact statement-wide GDT581 governor instead of
rendering each event in isolation.

That one change removes the largest artificial defect in GDT583:

| issue | before | after |
|---|---:|---:|
| detached `beim …` host fragments | 1,149 in 327 statements | 0 |
| lowercase sentence starts | 1,761 in 424 statements | 0 |
| remote fine arguments separated from their verb | 62 | 0 |
| embedded `Temperiere auf den Grad: auf Grad …` | 32 events | 0 |
| repeated Ringposition inside action plus argument | 43 action clauses / 23 statements | 0 |

All 12,707 written slots in the 591 affected statements remain present in the
exact trace and in exactly one of 6,289 statement-wide governor groups. There
are 845 multi-packet governors; these are now readable without hiding which
event packet supplied each remote argument.

## What changed semantically

The independent direction and material readings found fifty bounded changes
among 1,921 target occurrences. Everything else remains live.

- One relation-only `SH→T` case, `G407-E3488`, changes from unsupported cooling
  to regulation from the outlet basin.
- `G407-E4570` changes from drying before CHD to tempering an explicitly liquid
  extract before broad processing. The two actual dry→grind cases at
  `G407-E4476` and `G407-E4490` remain.
- Three sieve readings immediately after a wet step become straining. One
  `sain` occurrence with direct AIN and only remote AIIN becomes sieving. One
  stage-only S occurrence returns to broad separation.
- Five formerly dry grind readings become wet trituration/maceration. Five
  broad AIIN+Y processing cases receive the same wet-process voice.
- Sixteen remaining `CHD_HP_DRY_GRIND` cases are renamed to the more honest
  material-comminution reading; absence of AIIN supports physical
  fragmentation but does not prove dryness.
- Eight broad SH occurrences immediately before straining become standing or
  settling, two broad S occurrences after wet work become taking off, and five
  OR-only soak readings become holding the material unit.

This yields 1,653 retained slots, 218 wording-only rephrasings, 34 narrowed
readings, fifteen upgrades from broad fallbacks and one return to a broad
fallback. The broad T/SH/CHD/S roots are unchanged.

## Why the remote-host repair matters

GDT583 rendered `G407-E0360` as an isolated “Seihe ab”, followed later by two
fragments containing its inherited AIIN and Y arguments. GDT584 composes the
three written packets under their common key `ACTION:G407-E0360@1:S`:

> Seihe den Auszug der Pflanzencharge ab.

The host artifact still lists the three exact slots separately:
`G407-E0360@1=S`, `G407-E0361@1=AIIN`, and `G407-E0362@2=Y`. The prose is
smoother; the evidence is not collapsed.

The same repair makes the directional examples usable:

- `G407-E0366`: “Erwärme die Pflanzen- oder Arbeitseinheit. Halte die
  Pflanzen- oder Arbeitseinheit warm.”
- `G407-E3488`: “Halte im Bad auf Grad I. Reguliere anschließend von der
  Ausgangsstation oder aus dem Ausgangsbecken.”
- `G407-E4476`: “Trockne die Pflanzencharge … Zerreibe die Pflanzencharge.”
- `G407-E4570`: “Temperiere den Auszug. Bearbeite den Pflanzenauszug …”
- `G515-E0243`: “Sondere die Pflanzen- oder Arbeitseinheit auf der
  Verarbeitungsstufe aus.”

## Remaining roughness

This is the best complete machine reader for the current action experiment,
not a literary translation. The inherited statement units are sometimes very
long: 106 of 591 exceed 100 words and 35 still exceed 200 after rendering.
OT/DY paragraphing makes them navigable but does not invent smaller manuscript
sentences. Broad fallbacks such as “Halte den Zustand” remain intentionally
visible where no object or process direction is available.

Independent validation passes 40/40 checks, including source hashes, exact
slot projection, statement-wide host partition, all remote-argument stitches,
named rule changes, passage identity, output hashes and sealed-page exclusion.

## New working basis

Use GDT584 as the reader layer above GDT583 and the unchanged GDT582 portable
dictionary. The next useful closed-page step is no longer another T/SH/CHD/S
grammar pass. It is a contextual audit of the eighty learned class×name types
across their 109 owner-bound name slots: consolidate repeated substance and
plant-part readings, inspect possible compounds, and improve inconsistent
whole-name defaults while keeping every function shell and owner boundary
fixed. No new page is needed for that step.
