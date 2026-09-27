# RAW569: complete ZL celestial synopsis candidate, with known alternate-reader failures

Authoring began 2026-09-27 00:51:44 UTC. The decision was frozen before assigning
meanings, SHA256 `8e802768003b916a713154fa76aa32a69a4604a310f476a102bfd8ccfe4954a5`.
The fixed 01:35 UTC ceiling includes documentation. This report and the JSON are
an exploratory authoring packet, not a confirmed translation or a passed test.

**Result:** all 108 primary ZL groups have one written assignment and belong to
23 explicit clauses. The 85 whole forms keep the same values throughout the
owned projection. All eight selected source obligations occur in formulas.
This is a complete **authored ZL candidate**, pending independent replay; it is
not a complete compatible reading of all three transcriptions. In IT, the
already assigned `qodain` is an observer binder where the fixed S4 derivation
requires a report predicate. Eleven IT and eighteen RF groups also have literal
unassigned variants. Nothing is normalized to repair them.

The detailed [draft](CELESTIAL_AUTHOR_DRAFT.json) owns the complete lexicon,
32 numbered grammar entries, every primary group and source ID, every alternate
row, all assigned-form occurrences outside the four blocks, formulas, source
coverage, departures and counts. No semantic executor or automatic search was
written. A temporary serialization script only assembled the manually written
entries and checked literal IDs/counts; it is not an authored decoder.

## The complete proposed reading

The following spans are exact ZL strings. A clause may continue across an
inscribed line; G01 declares N–E–S–W presentation and this continuation before
any semantic test. There is no correspondence between these four blocks and
four figures or four mandatory astronomical themes.

| Clause | Complete literal span | Proposed content |
|---|---|---|
| N1 | `sain or or aiin opchdy qotor sheedy shodaiin` | One lunar eclipse: the report here is at the first night-hour; the report of that same eclipse eastward is at about the third. |
| N2 | `olfar ary` | Sunset is earlier there. |
| N3 | `dair sheo` | Night begins earlier there. |
| N4 | `oraiin chol daiin` | That earlier night beginning explains the difference between the reports. |
| N5 | `ockhdar olkar shoral roseer` | Earth curvature is the sole ultimate cause attributed to this comparison. |
| E1 | `pchedeey olkey qokedy` | Consider stars and signs. |
| E2 | `sheos fcheey otchedy chotey qocthey oteey` | Their applicable risings and settings occur earlier at the eastern station than at the base station. |
| E3 | `ol oloqorain daiin qotaiin` | Earth curvature causes this difference. |
| E4 | `tchedy otedy qotchdy chckhey ytchedy qodar qotedar qokar` | If Earth were flat east to west, rising would occur as soon westward as eastward. |
| E5 | `qotchd qotom` | That equality of rising is false. |
| E6 | `soiis aiin shedaiin chok{co}m` | Thus the observed behavior of these bodies indicates Earth’s roundness. |
| S1 | `otchs shedor chey sorain` | For a northern observer, introduce a class near the Arctic pole and another near the opposite pole. |
| S2 | `or shedy tedy sodaiiin chy` | The primary, visible class remains visible throughout the cycle at that northern station. |
| S3 | `ytedar chz[s:r] aiin arody` | The other class is never visible in the same northern regime. |
| S4 | `ypshedy dar chedy or am oteey qodaiin` | If that observer travels sufficiently far south, the former primary class tends toward setting there. |
| S5 | `odain an chey orar oldar ain` | With further southward travel, its tendency toward setting is greater. |
| W1 | `okees olaiin qokal chdy sary` | For that same traveller, the other, formerly hidden class can be visible at the southern destination. |
| W2 | `qokshedy qodain chckhy ykeedy chedy` | Conversely, another person travels south to north in the corresponding reversed case. |
| W3 | `or aiin ckhed[a:y] or ain olchey qokal shedy` | That class is hidden at the reversed destination, whereas it is visible at the southern starting station. |
| W4 | `qokeody qoekedy` | Earth curvature is the ultimate cause attributed to these polar and travel reports. |
| W5 | `dody shedy qodaiin` | In the earlier forward destination case, the initially visible class tends toward setting. |
| W6 | `los ar shedy qokshey qose?y or aiin og` | If Earth were flat north to south, the always-visible class would remain visible wherever the observer travelled; that unrestricted constancy is false. |
| W7 | `ol lcheol chol ol sheoly` | Earth’s great size causes its appearance of flatness. |

This is a reordered synopsis of the complete accepted *Quod terra sit rotunda*
unit, not a claim that the manuscript copies Sacrobosco. The event report stays
a report about an extended eclipse: no contact, instant or exact two-modern-hour
offset is introduced. The travel claims stay prospective and conditional.
“Tends toward setting” is not silently converted to “has set.” Class variables
are genuinely plural-compatible classes, not one physical star relabeled to
stand for all objects. Earth and human apparent flatness have a separate type;
W7 is not a stellar visibility report.

## Actual reused constructions and their restrictions

**FRAME, written `or`.** Its visible operands are always referent/view first,
station second. The open, written case binder supplies the observation scope.
For an existing view, it replaces the station while preserving referent and
scope. For an ordinary world referent it creates a view. Earth is excluded from
this world-referent sort.

The complete N1 application is:

```
sain : bind e:Event, h:Station, cE:WholeEclipseReportScope
v0 = or(aiin=e, opchdy=h; cE)
v1 = or(v0, qotor=east(h); cE)
PAIR([v0,v1], [sheedy=FirstNightHour, shodaiin=AboutThirdNightHour])
```

The local-phase reports also carry their local-night contexts for the following sunset and night-beginning statements; this is an explicit scope choice. The report-contrast reference is proposition-valued, not a clock difference.

Nested `or or` is accounted for, not dropped as duplication. The two-node
expression retains the inner node for the paired reports; that retention and
inner-before-outer report order are explicit G05 choices. Event identity does
not identify one eclipse contact or prove report simultaneity.

The complete S2 application uses the same operand order and preserves the
source-owned stellar class:

```
otchs / shedor : bind C, observer a, northern station n, cycle cC, primary p
shedy : VISIBLE property
G18 in the required WorldRef slot: NOM_PRIMARY(VISIBLE,C) = p
vP = or(p, tedy=n; cC)
ALWAYS(sodaiiin, VISIBLE(chy,vP))
```

The property-to-primary-class nominalization is a **new rule**, not a hidden
cast. It selects the first explicitly introduced class and presupposes that
property at the episode base station. It cannot choose any convenient earlier
referent. The same `shedy` remains the visibility property in W3's report slot;
its three nominal uses are S2, W5 and W6. This is a substantial authoring cost,
although conventional substantivization makes it a possible construction.

The complete W3 application also reuses G05 with a different report type:

```
u1 = or(aiin=q, ckhed[a:y]=after-journey station; cB)
u0 = or(ain=q, olchey=before-journey station; cB)
PAIR([u1,u0], [qokal=HIDDEN, shedy=VISIBLE])
```

The lexical distinction between `aiin` (Event-or-Class reference) and `ain`
(Class-only reference) is retained. Both refer to q here because W1 explicitly
sets q as topic and the converse preserves it. The new person b comes from
`qodain`; the forward traveller a is retained in W1 by `olaiin`. These are
reference laws with written binders, not an assumption that all paragraphs
concern the same person.

**Earth-aspect owner, written `ol`.** It computes `Aspect(g,k)` from the Earth
introduced by `ockhdar` and an explicit AspectKind operand. Three separate
occurrences take curvature, great size and apparent flatness as different
arguments. The one internal cut `olkar = ol + kar` computes the earlier Earth
curvature expression. `kar` is one new hypothetical bound component; it is not
an independently known root. There is no universal `ol` prefix law:
`olchey` and `olaiin` remain opaque, and `chey=AND` would not be an admissible
AspectKind operand in an attempted `ol+chey` parse. Likewise `oldar` is not
`ol+dar`; `dar` has TravelExtent type. This is only one licensed internal cut,
not a recovered general morphology.

**Causal relation, written `chol`.** The same attributed causal relation takes
the earlier-night proposition and report contrast in N4, and Earth's great
size and apparent flatness in W7. It has declared causal operand sorts, not an
unrestricted function interpolation. A second, expressly purchased postfix
surface order and synonym `qotaiin` occur in E3.

These laws impose genuine typed argument obligations. They do not make the
84 other whole-form assignments independently probable. Most recurring letter
parts—including the apparent `qod`, `ot`, and `aiin` families—remain unexplained.
In particular `oraiin` is an opaque proposition reference, not `or+aiin`, and
`qodain`/`qodaiin` are independently assigned whole forms. That residual freedom
is a serious limitation of this candidate.

## Source coverage and additional interpretation

The accepted source is the complete normalized electronic 1478 subsection,
cache SHA256 `fe33becfd1f4fe44973e0c1840030834e1af61ca3895f49a861e067850e694ad`.
No new source was fetched or image inspected. Its complete body was reread
while reviewing these clauses. The predecessor/source review in the frozen
selection note remains controlling; no older target gloss is inherited.

| Obligation | Written clauses | Retained distinction |
|---|---|---|
| C1 eastern rising/setting and curvature | E1–E3, E6 | Applicable event comparisons, not an assertion that every star rises and sets at every station. |
| C2 one eclipse and local hours | N1–N5 | Same event; approximate eastern third; earlier sunset/night; attributed sole curvature cause. |
| C3 polar visibility classes | S1–S3, W4 | Distinct nonempty classes; fixed cyclic scopes; always versus never. |
| C4 qualified southward travel and stronger tendency | S4–S5, W4–W5 | Sufficiency guard, same traveller, qualitative more, prospective tending toward setting. |
| C5 new visibility and converse | W1–W4 | Forward same a; converse new b; class identity; explicit curvature explanation. |
| C6 flat east–west counterfactual | E4–E6 | Positive counterfactual consequent plus its separate actual falsity. |
| C7 flat north–south counterfactual | W6 | Positive constant-visibility consequence and projected actual-falsity assertion. |
| C8 apparent flatness because of size | W7 | Appearance to generic human perception, not actual flatness. |

Several interpretations are added openly. N4 makes the earlier night an
intermediate explanation of the eclipse-report contrast; the Latin instead
infers earlier night from that contrast. N5's “ultimate” qualification is an
analytical causal hierarchy that permits this intermediate link while retaining
the source's sole curvature cause. G09 applies the same whole-episode causal
scope at W4, preserving the conditional guards rather than asserting that a
journey actually happened.

The secondary class q is a source-selected formerly hidden class capable of
becoming visible, not all stars near the opposite pole. G24 makes the converse
conditional on realizing such a visibility regime before reversing the route.
The source's brief converse statement does not spell out this guard. Both the
witness alignment and guard are additional commitments. W5 is a deliberate
redundant reminder of the earlier forward report; it earns no independent
source support and avoids moving its fixed predicate into the converse case.
The written `dody` retains that earlier observer, frame, scope and guard.

G30 projects an actual-falsity status outside a counterfactual while retaining
its positive consequent. This is an explicit extra scope law. The source
asserts that consequence false; the candidate does not derive its falsity from
mere tendency toward setting. There is no unmentioned geometry simulator.

The source's rhetorical remark that the eclipse illustration is clear from
happenings aloft has no separate ABOVE/ALOFT token here. Source phrasing and
presentation order are condensed. No C1–C8 obligation is dropped, but literal
full-source equivalence is expressly **not** claimed.

## Exact freedom and outstanding obligations

The inventory is 85 ZL whole types: **84 independently assigned whole values,
one derived whole, one additional bound component, and one chosen internal
cut**. There are 32 numbered rule entries and 23 clauses. Some rules contain
multiple stipulations; 32 is an inventory count, not an elementary-parameter or
minimum-description-length claim. The JSON separately lists 27 substantial
scope/typing commitments and 17 opaque multi-feature values. Every binding is
hypothetical. Confirmed meanings remain zero.

There are nine identical-value synonym clusters with **11 extra forms**:
`ary/sheo/otchedy`, `chol/qotaiin`, `shoral/qoekedy`, `olkey/chey`,
`sheos/qokar`, `chotey/qotedar`, `tchedy/ypshedy/los`, `shedy/chy`, and
`ytedar/okees`. Further near-equivalences and alternative encodings are listed
in the JSON, including `arody` versus `qokal`, and `qose?y` versus
`sodaiiin + chy`. These are paid freedoms, not independently demonstrated
synonymy or morphology. Case binders also supply several named fields; their
content is itemized rather than counted as a costless paragraph default.

All 324 selected rows are preserved: 108 ZL, 107 IT, 109 RF. All marked strings,
raw entities, separators and IDs survive. The earliest IT lexical gap is
`f85r2.5 G001 ockhdor`; RF first lacks `f85r2.5 G002 ol@176;ar`. The assigned
IT S4 type mismatch is later, at `f85r2.16 G002 qodain`: after `oteey` completes
the view, the frozen rule requires a ReportPredicate; ANOTHER_PERSON is an
ObserverBinder licensed after CONVERSE_CASE. It cannot serve as the predicate
without changing this packet.

Both alternate W.20 rows start with `ar`, whose value here is FLAT_NORTH_SOUTH,
not FRAME. Thus the fixed first W3 view construction does not transfer. Later
unknown operands prevent a universal no-possible-reading claim. IT `aiinog`
is one unknown whole group; RF `qose eey` is two unknown groups. Neither is
silently replaced by the primary spelling or split. The complete eleven/eighteen
literal gap inventories are in the JSON.

Outside these four blocks, the projection contains 14 ZL, 18 IT and 15 RF
occurrences of assigned forms. All 47 have exact IDs and unchanged values in
the JSON, as do their complete occurrence lists in the lexicon. No outside
syntax or discourse order has been supplied. In ZL these include early `ar`,
`otedy`, `otchedy`, `shedaiin`, `olaiin`, `daiin`, `ol`, `aiin`, `dar`, and
later `okees`, `ar`, `or`, `ar`. They are extension obligations, not validated
uses or an excuse to move Earth/traveller binders invisibly into the ring.

The strongest source-compatible rival keeps every dictionary entry, station,
referent, guard and source assertion, but writes direct
`NIGHT_REPORT(e,f,c,phase)` and `VIS_REPORT(class,f,c,value)` relations.
The written FRAME expressions then assemble their arguments, without an
intermediate View object. This compiles the current candidate without changing
its extensional claims. No target consequence here selects the View ontology
against that rival. The meaningful constraints are the written shared
argument/type laws, not a preference for the name VIEW.

The result therefore supports review of a concrete, fully written ZL content
hypothesis. It does not resolve the literal alternate failures, most morphology,
source-to-target binding, regional transmission, or independent meaning.

## Freeze receipt

Frozen 2026-09-27 01:25:21 UTC after 33.62 minutes from the recorded author start.
No semantic execution or independent validation is included.
Draft SHA256: `6f696bafb5a22f94fd2649558d0292183b1757cc2fdaa01a6dd0b9033416080d`.
The final report hash is handed to root with the packet; the frozen decision is unchanged.
