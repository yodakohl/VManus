# S: vollständiger alter Uhr-Kandidat

Dokumentarische Übernahme von GDT1030; sämtliche Werte sind C0. Keine neue Lesung, kein neuer Zieltest.

## Vollständige historische Vergleichspassage

9. Thus as the phellos ascends by the action of the water, the counterpoise of sand descends and turns the axis, as does that the wheel, whose rotation causes at times the greater part of the circle of the zodiac to be in motion, and at other times the smaller; thus adjusting the hours to the seasons. Moreover in the sign of each month are as many holes as there are days in it, and the index which in dials is generally a representation of the sun, shews the spaces of the hours; and whilst passing from one hole to another, it completes the period of the month.

Ancient work, late first century BCE; owned text is the later public-domain Gwilt English translation hosted by LacusCurtius, not a medieval witness. Exact printed edition/year and Latin variants were not collated in this bounded pass. Anaporica spelling, eighth-division references and the hydraulic explanations remain this translation branch. Physical engineering adequacy is not certified. The prior analemma construction is an explicit prerequisite outside this bounded clock description.

## Ganze vorhandene Manuskriptfassungen

### ZL3b: f111r|f111r.51-f111r.54, 40 Gruppen

- f111r.51: `polkeeo shey cheokeain chl kar r aiin char ?ain al lkeedy qokal okchy` (anchor_eligible=False)
- f111r.52: `dair al qokeey qokaiin sheal qokeain shckhy sain chckhy char aiin alom` (anchor_eligible=False)
- f111r.53: `yshe aiin okshdy shkeey kain chaiin alolshey qokaiin chcthydain` (anchor_eligible=False)
- f111r.54: `tair chckhaiin dair qokal otain okal` (anchor_eligible=True)

### IT2a: f111r|f111r.51-f111r.54, 42 Gruppen

- f111r.51: `polkeeo shey cheokeain chl kar r aiin ihar ?ain al lkeedy qokal okchy` (anchor_eligible=False)
- f111r.52: `dair al qokeey qokaiin sheal qokeain shckhy sain chckhy char aiin alom` (anchor_eligible=True)
- f111r.53: `yshe aiin okshdy shkeey kain chaiin alol shey qokaiin chcthy dain` (anchor_eligible=True)
- f111r.54: `tair chckhaiin dair qokal otain okal` (anchor_eligible=True)

RF1b: kein entsprechender vollständiger Datensatz im alten Paket; keine negative zusätzliche Handschrift.

## Alle33 unveränderten Ganzwerte

| Form | Alter Wert | Typ | Gesamtpositionen |
|---|---|---|---|
| `polkeeo` | WATER | water body/source Wt | 1 |
| `shey` | RAISES | acting source × movable part → upward-motion event | 2 |
| `cheokeain` | FLOAT | physical float F | 3 |
| `chl` | SAND_COUNTERWEIGHT | physical counterweight C | 4 |
| `kar` | DESCENDS | movable part → downward-motion event | 5 |
| `r` | TURNS | driving part × rotatable part → driven rotation | 6 |
| `aiin` | MOTION | participant × motion context → motion-event reference | 7,24,27 |
| `char` | WHEEL | physical display wheel W | 8,23 |
| `?ain` | AXIS | physical axle X | 9 |
| `al` | THIS | active demonstrative reference → same specified entity | 10,15 |
| `lkeedy` | TRANSMITS | driving rotatable part × target-motion event → transmission relation | 11 |
| `qokal` | ZODIAC | physical zodiac circle Z | 12,38 |
| `okchy` | GREATER_OR_SMALLER | season-indexed region extent → nonconstant ordered variation | 13 |
| `dair` | PART | whole × specified part role → part reference | 14,37 |
| `qokeey` | ADJUSTS | display configuration × hour kind × season → adaptation relation | 16 |
| `qokaiin` | HOURS | hour-kind Hh | 17,33 |
| `sheal` | SEASONS | seasonal context s | 18 |
| `qokeain` | MONTH | calendar month m | 19 |
| `shckhy` | HOLES | month-sign region → finite hole collection | 20 |
| `sain` | EQUINUMEROUS | finite collection × finite collection → equal cardinality | 21 |
| `chckhy` | DAYS | calendar month → finite day collection | 22 |
| `alom` | BY | effect/adjustment assertion × motion event → causal attribution | 25 |
| `yshe` | INDEX_USUALLY_SUN | physical index I with usual kind-level depiction | 26 |
| `okshdy` | FROM_HOLE | index-step event × origin hole → source endpoint | 28 |
| `shkeey` | TO_ANOTHER_HOLE | index-step event × distinct hole → destination endpoint | 29 |
| `kain` | WHILE | extended event × proposition → during relation | 30 |
| `chaiin` | SHOWS | indicator × displayed object → display relation | 31 |
| `alolshey` | SPACES | hour kind → display-space collection | 32 |
| `chcthydain` | COMPLETES | progress history × period → completion relation | 34 |
| `tair` | PERIOD | calendar month → temporal period | 35 |
| `chckhaiin` | EACH | declared month domain × predicate → universal quantification | 36 |
| `otain` | MONTH | calendar month m | 39 |
| `okal` | WHOLE | period → whole-period qualifier | 40 |

## Vier alte vollständige Produktionen

### C01: Positionen 1,2,3,4,5,6,7,8,9,10,11

`polkeeo shey cheokeain chl kar r aiin char ?ain al lkeedy`

The water raises the float; as the sand counterweight descends, it turns the axle, and that axle transmits rotation to the wheel.

```json
{
  "episode": "e",
  "coupled_claims": [
    "RAISES(Wt,F,e)",
    "DESCENDS(C,e)",
    "TURNS(C,X,e)",
    "TRANSMITS(THIS(X9),MOTION(W8,e))"
  ],
  "part_identity": [
    "F != C",
    "X != W"
  ],
  "supporting_argument_positions": {
    "RAISES2": [
      1,
      3
    ],
    "DESCENDS5": [
      4
    ],
    "TURNS6": [
      4,
      9
    ],
    "MOTION7": [
      8
    ],
    "THIS10": [
      9
    ],
    "TRANSMITS11": [
      10,
      7
    ]
  },
  "position_list_scope": "Lists identify supporting word positions, not a flat interpreter ABI; the written typed formulas above supply argument nesting and scopes."
}
```

### C02: Positionen 12,13,14,15,16,17,18,23,24,25

`qokal okchy dair al qokeey qokaiin sheal char aiin alom`

By the motion of that same wheel, a greater or smaller portion of the zodiac circle is brought into motion at different seasons; this adjusts the hours to the seasons.

```json
{
  "part": "A(s)=PART(Z12, moving_region_for(SEASONS18))",
  "variation": "GREATER_OR_SMALLER13(extent(A(s)),s)",
  "adjustment": "ADJUSTS16(THIS15(A(s)14),HOURS17,s18)",
  "postposed_cause": "BY25([MOTION24(A(s)14,e),variation,adjustment], MOTION24(WHEEL23,e)); one written MOTION24 shared under B19",
  "same_wheel": "WHEEL23=WHEEL8",
  "supporting_argument_positions": {
    "PART14": [
      12,
      18
    ],
    "GREATER_OR_SMALLER13": [
      14,
      18
    ],
    "THIS15": [
      14
    ],
    "ADJUSTS16": [
      15,
      17,
      18
    ],
    "MOTION24": [
      23
    ],
    "BY25": [
      24,
      13,
      16
    ]
  },
  "position_list_scope": "Lists identify supporting word positions, not a flat interpreter ABI; the written typed formulas above supply argument nesting and scopes."
}
```

### C03: Positionen 19,20,21,22,36,37,38

`qokeain shckhy sain chckhy chckhaiin dair qokal`

For each month, the holes in its sign-part of that same zodiac are as many as the days in that month.

```json
{
  "quantifier": "EACH36 m in MONTH19 binds BOTH C03 and C04 through end40, under B20",
  "sign": "S(m)=PART37(ZODIAC38,sign_of(m))",
  "formula": "EQUINUMEROUS21(HOLES20(S(m)),DAYS22(m))",
  "same_zodiac": "ZODIAC38=ZODIAC12",
  "supporting_argument_positions": {
    "EACH36": [
      19,
      21
    ],
    "PART37": [
      38,
      19
    ],
    "HOLES20": [
      37
    ],
    "DAYS22": [
      19
    ],
    "EQUINUMEROUS21": [
      20,
      22
    ]
  },
  "position_list_scope": "Lists identify supporting word positions, not a flat interpreter ABI; the written typed formulas above supply argument nesting and scopes."
}
```

### C04: Positionen 26,27,28,29,30,31,32,33,34,35,39,40

`yshe aiin okshdy shkeey kain chaiin alolshey qokaiin chcthydain tair otain okal`

The index, usually represented as the sun, shows the spaces of those hours; during its progression from one month-sign hole to another it completes the whole period of that same month.

```json
{
  "index": "I=INDEX_USUALLY_SUN26",
  "history": "Pm=MOTION27(I26,month_progression(m))",
  "steps": "For local step t in Pm: FROM_HOLE28(t,h) and TO_ANOTHER_HOLE29(t,h_prime), with h,h_prime in H(S(m)) and h != h_prime",
  "during": "WHILE30(Pm, [SHOWS31(I,SPACES32(HOURS33)),COMPLETES34(Pm,WHOLE40(PERIOD35(MONTH39)))])",
  "same_month": "MONTH39=MONTH19=m",
  "same_hours": "HOURS33=HOURS17=Hh",
  "actuator": "UNSPECIFIED",
  "supporting_argument_positions": {
    "MOTION27": [
      26,
      39
    ],
    "FROM_HOLE28": [
      27,
      20
    ],
    "TO_ANOTHER_HOLE29": [
      27,
      20
    ],
    "WHILE30": [
      27,
      31,
      34
    ],
    "SHOWS31": [
      26,
      32
    ],
    "SPACES32": [
      33
    ],
    "COMPLETES34": [
      27,
      35,
      40
    ],
    "PERIOD35": [
      39
    ],
    "WHOLE40": [
      35
    ]
  },
  "position_list_scope": "Lists identify supporting word positions, not a flat interpreter ABI; the written typed formulas above supply argument nesting and scopes.",
  "month_scope": "m bound by C03/C04 joint EACH36 scope; not a free escaped variable"
}
```

## Zwanzig alte Bindungsannahmen

**B01 — One apparatus and normal episode.** F,C,X,W,Z,I are persistent apparatus parts. F/C and X/W remain distinct. Z is borne by W under explicit inherited§8 context, not a newly identified image. Statements concern normal operating episode e; broken/disconnected apparatus behavior is not asserted. The episode e is a variable over normal operating cases: each C01/C02 case shares its e, but comparing different seasons allows different e(s). Persistent parts are shared across cases; no one event occurs in multiple seasons simultaneously.

**B02 — Coupled opposed motion.** WATER1 RAISES2 FLOAT3 and C4 DESCENDS5 share e under a fitted coupled-as juxtaposition: water-raised F is accompanied by downward C in this apparatus. No equality of displacement, rate, force or exact delay.

**B03 — Delayed axle argument.** TURNS6 takes C4 as driver and AXIS9 as target, across MOTION7 WHEEL8. THIS10 resumes X9. This delayed argument rule is explicit; TURNS must not silently target W instead.

**B04 — Axle-to-wheel transmission.** MOTION7 WHEEL8 forms mu(W,e). THIS10 TRANSMITS11 binds Transmit(X,mu(W,e)); TURNS(C,X) supplies X rotation. These separate arguments make C→X→W, not one word encoding the chain.

**B05 — Three discontinuous ownership lists.** C01 owns1–11; C02 owns12–18,23–25; C03 owns19–22,36–38; C04 owns26–35,39–40. Every group once. Three productions are discontinuous, not two. Physical word/line boundaries remain, while the interleaving is new fitted grammar.

**B06 — Motion noun with explicit participants.** MOTION7/24 refers to the same W motion/event family; WHEEL23 resumes W8. MOTION27 refers to I26 progression history Pm. Same constructor, separate participant arguments. No participant queue and no calendar drive inferred from W automatically.

**B07 — Two PART role projections.** PART14 with Z12 and SEASONS18 yields moving region A(s). PART37 Z38 under MONTH/EACH yields sign S(m) of the same Z. A and S are role-selected parts, not a single identical region or per-occurrence word meanings. Role selection is a new assumption.

**B08 — Qualitative comparative variation.** GREATER_OR_SMALLER13 asserts varying ordered extents of A(s) at source differing times/seasons. No angles, exact season labels, constant W speed, linear formula or numerical month-season map. The extent projection is an explicitly assumed qualitative ordered attribute of a region, not an independently read measurement word. The draft does not assert that the rest of the rigid wheel remains stationary or select an engineering interpretation of the changing arc.

**B09 — Adjustment and postposed cause.** THIS15 resumes A(s)14. ADJUSTS16(A(s),Hh17,s18); WHEEL23 MOTION24 BY25 causally modifies moving-region variation and hour adaptation. Fitted order and shared causal scope are charged.

**B10 — Universal month and owned sign.** EACH36 binds m from MONTH19. PART37 Z38 supplies S(m). That sign owns HOLES20, and DAYS22 belongs to the same m. No number of months or named calendar.

**B11 — Equality without a numeral.** EQUINUMEROUS21 compares H(S(m))20 and D(m)22. Both finite, common size n(m) variable. Formula forall m: |H(S(m))|=|D(m)|. No particular bijection, zero index, length or transition-count algorithm.

**B12 — Same month and local step endpoints.** MONTH39 resumes C03 m; PERIOD35 is T(m). FROM_HOLE28 and TO_ANOTHER_HOLE29 bind each local step of Pm to distinct holes h,h_prime in H(S(m)). No intrinsic numerical adjacency, all-holes-once rule, wrap or reset.

**B13 — Whole history distinct from one step.** MOTION27 creates I-owned progression history Pm with local step constraints. WHILE30 scopes SHOWS31 and COMPLETES34 over Pm. History/step composition is an explicit grammar assumption; one arbitrary step does not mean a whole month.

**B14 — Same hours and usually solar index.** INDEX_USUALLY_SUN26 introduces I and the source’s usual kind-level solar depiction, not a universal shape guarantee. SHOWS31(I,SPACES32(HOURS33)) keeps the hour-kind Hh17. Display-space relation to the season belongs to this apparatus; no numerical reading formula.

**B15 — Whole-period completion as source constraint.** COMPLETES34(Pm,WHOLE40(PERIOD35(MONTH39))) states full month completion. It is not derived from an invented n/n−1-step algorithm and does not fix the actuator. Operator, history, period and month have separate ownership.

**B16 — No selected calendar actuator.** Main leaves mechanical versus manual index advance unresolved. Mechanical daily advance would need an additional coupling/controller and timing law; no once-per-day, start, reset or successful engineering claim is supplied by§9.

**B17 — Synonym and composite costs.** qokeain/otain are separately counted MONTH spellings. Six explicit composite values: SAND_COUNTERWEIGHT,GREATER_OR_SMALLER,INDEX_USUALLY_SUN,FROM_HOLE,TO_ANOTHER_HOLE,EQUINUMEROUS. Each needs external arguments; none holds the entire mechanism/calendar clause. Typed projections and other grammar remain additional costs.

**B18 — Historical and draft scope.** All33 values remain guesses, including the6 tentative498 values. Only whole§9 is target-bound;§8 apparatus context is explicit, while§10–15 regulator/annual-return content is outside. English translation, uncollated Latin, engineering limits and§12 HTML artifact persist. Old498 bytes and unfinished status unchanged.

**B19 — Shared motion predicate within seasonal cause.** C02 uses the one written MOTION24 constructor for both the source wheel-motion reference mu(W23,e) and the causally affected part-motion mu(A(s)14,e). This is an explicit predicate-sharing/ellipsis construction; the two participant arguments are written WHEEL23 and PART14. BY25 relates these, with variation and adjustment. No hidden second motion word is claimed, and PART alone is not allowed to assert physical motion. This extra semantic application of one word is counted as grammar, not a per-occurrence new denotation.

**B20 — Quantifier scope shared with month progression.** EACH36 binds m across both C03’s equality/sign statement and C04’s same-month progression/period statement. The binder closes at the complete month-unit end40, despite physical interleaving. MONTH39 resumes that in-scope m; it is not a free variable leaked from a closed universal statement or a silently selected different month. This joint scope is a fitted construction. The month parameter belongs to the source-described calendar context; no rule across unmentioned calendars or leap-year systems is asserted. I,W and Z are global apparatus identities across this month quantification; EACH does not create a fresh clock or index per month.

## Diplomatische Grenze

{
  "ZL3b": "All40 groups, ?ain, source_ids and boundary/anchor flags preserved. ?ain=AXIS remains a raw uncertain whole-form hypothesis.",
  "IT2a": "Entire42-group counterpart retained. char8→ihar; alolshey32→alol shey; chcthydain34→chcthy dain. IT shey now also appears in the split where ZL has SPACES, while its whole-form value is RAISES elsewhere. ihar,alol,chcthy,dain are unassigned. No new split/alias rules or IT meaning is supplied.",
  "RF1b": "No corresponding record in the owned parent packet.",
  "scope": "ZL full51–54 boundary unchanged; alternate readings of one manuscript, not independent corroboration."
}
