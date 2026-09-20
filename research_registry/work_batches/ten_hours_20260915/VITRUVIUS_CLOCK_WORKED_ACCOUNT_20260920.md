# Vitruvius IX.8.8–15: source-only worked clock account

Status: **RAW_SOURCE_WORKED, not selected and not target-tested**. This file
expands retained `IDEA000394`; it does not add a proposal, assign a Voynich
meaning, inspect a target row or image, or define a decoder.

## Source boundary and predecessor check

The owned source is the later public-domain Gwilt English translation of
Vitruvius, *De architectura* IX.8.8–15, from “Other kinds of winter-dials”
through the announcement of the next machine book. The cached complete source
is `CONTEXTUAL_FULL_CONTENT_RAW_SOURCES_20260920.json`, source id
`VITRUVIUS_IX8_8_15`, excerpt SHA-256
`56f3089ee2c941cee1e33baaee2eb64fc3387dce38a13dfbb017898690ad8149`.
The source card and edition limits are
`research_registry/proposals/raw_vitruvius_clock_state_reference.json`.
No Latin or medieval-witness collation is silently supplied; the analemma is
an explicit prerequisite outside this excerpt.

The predecessor check retains three limits. GDT214's
`GDT214_HYDRAULIC_COMPONENT_KEY_COMPARATOR_REPORT.md` says that historically
attested hydraulic component prose does not recover a target key or an image
match. GDT885's report excludes its registered three-state character action,
while GDT903's report shows broad reversible endpoint compatibility without a
writing rule or meaning. IDEA000348/Hero Pneumatics 37–38 is a different
source mechanism: its admitted visual review did not securely bind suspended
weights, pulleys, an elastic bag, or moving/reset states
(`WHOLE_CONTENT_SELECTION_20260920.md:443–447`). None of these limits is
repaired here.

## Distinct entities and quantities

The source reuses “tympanum” in more than one role. The first mechanical
coupling has a water-raised **phellos** (also called a tympanum in the
translation) and an equal-weight sand **counterpoise**. The later hydraulic
regulator has a **fixed large tympanum** and a **movable lesser tympanum**.
These are not merged into one physical object.

The finite constructor has these physical arguments:

`CLOCK(analemma, dial_rods, month_circles, zodiac_wheel, axis, brass_chain,
phellos, sand_counterpoise, sun_index, month_day_holes, cistern, water_pipe,
fixed_tympanum, fixed_regulator_points, movable_tympanum, tongue,
regulator_hole, receiving_vase)`.

Its state and output fields are separate:

`STATE(annual_position, calendar_day, month_day_hole, regulator_point,
sun_index_position, tongue_position, wheel_sector,
float_displacement, counterpoise_displacement, flow_rate, fill_time,
day_length, hour_length, hour_class)`.

The constructor does not equate these fields. The source says that the sand
counterpoise has equal **weight** to the phellos; it does not state equal
displacement, equal force at every position, or any numerical motion. It says
that the phellos rises, the counterpoise descends, and the axis and wheel turn.
Those are directional events. Likewise, flow rate, fill time, day length and
hour length remain distinct: the prose relates them qualitatively but gives no
equation or numerical durations.

## Ordered source clauses

The following clauses preserve the order of the complete sections. They are a
finite semantic account of the source passage, not a proposed target grammar.

1. **Dial frame.** Given `analemma`, mark hours with `dial_rods` from the
   centre and draw `month_circles` showing month limits.
2. **Seasonal display.** Place `zodiac_wheel` behind the rods, with the twelve
   signs and their larger or smaller arcs.
3. **Opposed mechanical drive.** Fix `axis` through the wheel, coil the
   `brass_chain` around it, attach `phellos` at one end and the equal-weight
   `sand_counterpoise` at the other. Water raises the phellos; the counterpoise
   descends; the axis and wheel turn. The only asserted motion relation is
   `float_displacement↑`, `counterpoise_displacement↓`, `wheel_motion`.
4. **Wheel consequence.** Wheel rotation alternately moves larger or smaller
   zodiac arcs and thereby adjusts the seasonal hour display. This does not
   identify a single scalar called “season.”
5. **Daily display.** Each month has one `month_day_hole` per day. The
   `sun_index` advances from one such hole to the next and completes the
   month; `calendar_day` is the shared date variable, not a regulator point or
   a flow measure.
6. **Calendar relation.** As the sun's sign position lengthens or shortens
   days and hours, the index enters the corresponding points around the wheel.
   The water's equable flow is regulated in the following nested apparatus.
7. **Hydraulic assembly.** A `water_pipe` fills the `cistern`; a hole in its
   bottom sits beside the fixed large `fixed_tympanum`, which has a hole.
   The movable lesser `movable_tympanum` fits inside it through rounded male
   and female joints and turns as a stopple.
8. **Regulator index.** The fixed tympanum has `fixed_regulator_points`, 365
   equally spaced physical points. The `tongue` is fixed to the circumference
   of the movable tympanum and points to a `regulator_point`. A
   `regulator_hole` in the movable body passes water into the tympanum and
   onward to the `receiving_vase`. These points are not the display's
   `month_day_holes`; both can advance under one `calendar_day` without being
   the same physical mark.
9. **Fixed orientation.** On the fixed rim, Cancer is above, Capricornus
   below, Libra to the spectator's right, and Aries to the left; the other
   signs occupy the intervening positions.
10. **Capricornus condition.** At the printed Capricornus sign position, the
    tongue reaches a new `regulator_point` daily and the running water bears great
    weight. `flow_rate` is high; the receiving vase has short `fill_time`; the
    source reports diminished `day_length` and `hour_length`, with
    `hour_class=WINTER`.
11. **Aquarius condition.** As the movable tympanum turns into Aquarius, the
    holes stand perpendicular, `flow_rate` lessens, `fill_time` increases, and
    `hour_length` increases. No change to the fixed/movable identities is
    allowed.
12. **Aries condition.** Through Aquarius and Pisces, reaching the source's
    printed “eighth part of Aries” makes the water gentler and yields
    `hour_class=EQUINOCTIAL`. “Eighth part” is retained as an opaque printed
    position label; it is not converted to one eighth of a sign, an angle, or
    a degree.
13. **Cancer condition.** From Aries through Taurus and Gemini to the upper
    Cancer points, the hole or tympanum touches its printed “eighth division”
    and reaches the summit; the power and `flow_rate` lessen further.
    `fill_time` is longer and `hour_class=SOLSTITIAL`. The eighth-division
    qualification is retained without an inferred numerical angle.
14. **Libra return.** Descending from Cancer through Leo and Virgo to the
    source's printed “eighth part of Libra” shortens the stay and diminishes
    the hours, again yielding `hour_class=EQUINOCTIAL`. The wording does not
    establish an angle or identify this mark with the Aries wording.
15. **Capricornus return.** Through Scorpio and Sagittarius, the hole returns
    to the source's printed “eighth division of Capricornus.” The source again
    attributes fast water and `hour_class=WINTER`, closing the annual cycle
    before the machine book transition. This printed division is not assigned
    a numerical fraction or asserted identical to the initial Capricornus
    sign position.

## Scope conditions and invariants

The source account is valid only under all of these conditions:

- `annual_position` follows one ordered cycle: printed Capricornus sign
  position → Aquarius → the printed “eighth part of Aries” → Cancer → the
  printed “eighth part of Libra” → the printed “eighth division of
  Capricornus,” with Scorpio and Sagittarius on the return path. These are
  source labels, not inferred fractions, angles, or degrees; a writer may not
  select a fresh sign-to-effect value at each occurrence.
- `fixed_tympanum` remains fixed and owns the 365 `fixed_regulator_points`;
  `movable_tympanum` turns inside it and owns `tongue`. Shared “tympanum”
  spelling does not merge these roles.
- `month_day_hole` belongs to the display's month/day ring and is selected by
  `sun_index`; `regulator_point` belongs to the fixed tympanum and is selected
  by `tongue`. They may share `calendar_day` as a date relation, but the
  source does not identify them as one physical point or one index.
- `calendar_day`, `month_day_hole`, and `regulator_point` are not identical to
  `flow_rate`, `fill_time`, `day_length`, or `hour_length`.
- `float_displacement` and `counterpoise_displacement` are opposite signed
  directions. The source's equal-weight statement does not license equal
  displacement or a conservation equation.
- `flow_rate`, `fill_time`, `day_length`, and `hour_length` remain separate
  fields. The source supplies ordered qualitative effects, not measurements.
- The two equinoctial states share `hour_class=EQUINOCTIAL` but need not share
  `annual_position`, `tongue_position`, flow rate, or physical angle.
- The analemma supplies a prerequisite construction; the excerpt does not
  restate its measurements. No exact 365-state numerical writer is inferred.

## Fixed rival and changed observable outcome

The fixed rival `R_FLIP` keeps every physical argument, annual position,
calendar-day progression, the separate month-hole and regulator-point
sequences, and opposed float/counterpoise motion above, but replaces
the source's hydraulic relation with:

`flow_rate↑ → fill_time↑ → hour_length↑`, and
`flow_rate↓ → fill_time↓ → hour_length↓`.

It therefore predicts at Capricornus **high flow, long fill time, and long
winter hours**, whereas the source predicts **high flow, short fill time, and
short winter hours**. At Cancer it predicts the reverse of the source's
slow-flow, long-stay, solstitial result. The rival differs on independently
named observables; it is not a global renaming of components or a collapse of
the state fields.

An additional structural rival, `R_INDEPENDENT`, assigns a new apparatus to
each date. It can copy local names and even the hour labels, but cannot retain
one fixed outer regulator, one movable inner regulator, a daily tongue/point
relation, and the return to the printed Capricornus winter condition. This
rival is useful
as a reference-policy countercase, not as an alternative historical reading
already established by the source.

## What would bind this content, and what remains missing

A target-independent source mechanism could only be bound by independently
owned evidence for the conjunction of: nested fixed/movable regulator bodies;
a tongue or equivalent index selecting discrete marks; a water source, hole and
receiving vessel; opposed lifting and counterweight directions coupled to an
axis or wheel; an ordered annual or cyclic state; and repeated consequences
that distinguish flow rate, fill time and hour class. Component names or a
circle/list alone are insufficient. The earlier Hero 37/38 visual review did
not bind its own weights, pulleys, elastic bag, or moving/reset states, so a
generic apparatus resemblance would fail this requirement as well.

No admitted target drawing, target paragraph, target participant, word value,
or source relationship is claimed here. The principal source uncertainties
remain the translation branch, Latin/edition variation, missing dimensions,
unmodeled flow equations, and the external analemma prerequisite. No new
decoder, experiment, target access, reserve access, ledger, route, refresh,
commit, or publication was performed.

## Correction receipt (2026-09-20)

The cached source wording was rechecked against
`CONTEXTUAL_FULL_CONTENT_RAW_SOURCES_20260920.json`: it says “the eighth part
of Aries,” “the eighth part of Libra,” and “the eighth division of Capricornus.”
The earlier shorthand `Aries(1/8)` and `Libra(1/8)` could be read as an
inferred fraction of a sign, so it has been removed. The worked account now
uses opaque printed-position labels and explicitly declines an angle, degree,
or fraction interpretation. The terminal Capricornus wording is likewise
kept distinct from the initial printed Capricornus sign position.

The same source check confirmed two distinct mark systems: the display has
month-specific holes, one per day, traversed by the sun index; the regulator's
fixed large tympanum has 365 equally spaced points traversed by the movable
body's tongue. They may be coordinated by `calendar_day`, but this account no
longer uses one `day_mark` field or claims that the physical marks coincide.

Root final source check also restored the eighth-division qualification at
Cancer in clause13; the same no-inferred-angle limit applies there.
