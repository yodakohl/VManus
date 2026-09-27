# Independent replay of frozen RAW572 whole-content partial

27 September 2026. This review used the current route, frozen root decision,
unchanged first contract, and the released draft, readable draft and author
report. It did not read root's independent review while forming this result.
For target-side bookkeeping I used only the owned GDT1042
`artifacts/native_groups.tsv` projection. The replay script reads that
projection directly; it does not import the author's checker or runner.

## Reproducible literal replay

Run from the repository root:

```sh
python research_registry/proposals/laufenberg_f85r2_20260926/PLANET_CHILD_REPLAY_B.py
```

The script verifies the expected hashes of the source projection, first
contract, frozen JSON, readable draft and author report. The current hashes
match. It independently derives selected/outside scope from the fixed
f85r2.2–23 line ranges; verifies that all473 draft occurrence rows exactly
match the projection's12 native columns, with no missing, added, or changed
IDs/fields; recomputes exact-form inventories; checks clause partitions and
literal strings; and reconstructs the Respect register from standalone
`ar`/`aiin`/`ain` rows, leaving internal compound components out of that
register. It confirms:

- 324 selected reader rows (ZL108, IT107, RF109) and all149 outside rows are
  retained byte-for-field against the safe projection;
- the selected primary has104 assigned and4 unassigned groups; IT has94/13;
  RF has88/21. Outside assigned counts are14/18/15, totaling47;
- all85 exact selected-ZL forms appear in the lexicon;81 are assigned and4
  (`los`, `qokshey`, `qose?y`, `og`) are unassigned. Every assigned exact
  row's meaning/type matches its exact-form lexicon entry, and each entry's
  occurrence list equals all exact occurrences of that form in the retained
  473-row set;
- the19 clause rows partition all108 primary ZL groups exactly once.100
  groups have authored constructions; all eight groups of W.22 are explicitly
  unresolved. The readable clause text matches the joined source groups;
- all outside assignments resolve to exact forms and the declared reader
  counts. No result claims an outside sentence or discourse interpretation.

These are literal/accounting checks, not successful parsing or semantic
confirmation. The machine result is in `PLANET_CHILD_REPLAY_B.json`.

## Actual component operations and `ain`

The fixed derived forms do appear with the declared component outputs:
`dar`→`d(POWER)` (6 rows), `daiin`→`d(RECEIVED_PROPERTIES)` (9),
`qodar`→`qo(d(POWER))` (2), `qodaiin`→`qo(d(RECEIVED_PROPERTIES))` (5),
and `qodain`→`qo(d(LAST_RESPECT))` (3). The primary authored spans contain
actual applications: N2 supplies `daiin` with its F_R/contributor/degree
arguments; E3 also applies the receipt graded template to the initial donor;
S4 uses `dar` in the rare-active-power count; E4 uses `qodar` on the explicit
power frame and candidate, along with separate east-rise/great-power guards;
S5 and W2 use receipt greatest comparisons; W4 repeats that comparison for
the same named donor at birth. Thus both fixed operations are used on POWER
and RECEIVED_PROPERTIES in written frames; the repeated W4 and qodain uses
do not create extra distinct Respect values.

Independent register replay finds every standalone `ain` and every unmarked
`qodain` resolving to RECEIVED_PROPERTIES under the frozen last-standalone
rule. Primary ZL W2 qodain inherits REC after S17 `ain`, which itself repeats
the S14 standalone aiin. IT qodain at S16 inherits S14 aiin; IT W19 inherits
the S17 standalone ain. IT/RF W20's standalone ar is immediately followed by
aiin, so later W20 ain remains REC. RF has no unmarked qodain in the selected
surface. Internal `ar`/`aiin` inside compounds do not change the register.
These are deterministic consequences of the stipulated rule, not independent
evidence for the rule or meanings.

## Type-review limits and a local interface gap

The contract's first-review sparse-frame problem is addressed by new draft
G04/A03, which requires exactly one observation per declared domain member.
That is explicitly an additional input premise; no observations, degree
values or rankings are supplied. The earlier contract remains unchanged.
Accordingly the draft can define a global greatest operation under its
stronger assumed input interface without claiming to compute a historical
maximum.

One local typed-interface gap remains visible in the written productions.
G03's closed frame-builder signature consumes `HolderTag(p)` and
`ProfileTag(H)` to build a receipt frame, whereas the corresponding lexical
entries label `opchdy` `HolderBinder` and `qotor` `ProfileBinder`. The power
signature consumes `PartialPowerSeed`, while `am` is typed
`PartialFrame[POWER]`. No subtype, alias, or explicit binder-to-tag/seed
conversion appears in the frozen grammar. These pairs may be intended as
syntactic-binder versus denoted-value distinctions, but the draft does not
define that bridge. Under a strict reading of the declared closed signatures
and the no-undeclared-cast rule, these constructor applications are not yet
fully type-checkable. This is a local interface underspecification, not a
contradiction between the proposed meanings or an UNSAT result.

There is a related explicit reference/value boundary: G16/G19/G21 request a
`CompleteReceiptFrame`/`ReceiptFrame`, while `odain`, `shedy` and `chckhy` are
typed `FrameRef[REC]`. A named reference to a previously constructed complete
F_R could make these uses valid, and the prose repeatedly says references
read their named preceding binder; however, the exact denotation/dereference
typing is not set out as a signature. Treat this as a narrowly scoped
formalization obligation, not evidence that the receipt comparison has the
wrong holder or donor.

I do not find a contradiction in the actual respect calculation at the
authored d/qo applications. The report correctly charges frame totality and
functionality, the bottom/active-power interpretation, conditional field
ordering, generalized contributor-strength dependence, degree/bundle
identity, scope selectors, and the unsupplied first C06→C07 causal link as
additional costs or missing source obligations. The two later source links
and claims do not imply that the missing first causal edge has been written.

## Exact partial result

The frozen status is accurately **partial, not UNSAT and not complete**.
The earliest local target gap is all eight literal groups in ZL W.22; its
unknown entries still do not express the missing same-planet birth-day OR
birth-hour clause or the final `etc.`. Independently, source obligation C17
is partial: the mixed-receipt consequence is connected to N2, but the
earlier rarity→graded-giving causal link is absent. C15/C16 are missing.
Those gaps reject completion of this frozen writer only; they do not prove
that every possible compositional extension fails.

The reported inventory costs replay: 3 fixed atoms,5 computed whole types,
73 new opaque assigned whole values and4 unassigned types; 5 cuts/8
boundaries;24 labelled rule/stop bundles with the stated count qualification;
14 added assumption bundles;147 listed semantic payload occurrences,50
multi-feature new values and65 distinct new meaning labels. These costs
make clear why the actual d/qo applications are concrete compositional
content but do not amount to a mostly compositional lexicon or description-
length win. There are zero independently confirmed meanings.

Artifacts and hashes:

- `PLANET_CHILD_REPLAY_B.py`: `33c1186dba939e5fdc3f5b9854520c5af7c4bfccfa97a0d01d4bfafaee02ed6b`
- `PLANET_CHILD_REPLAY_B.json`: `dc885582ed0aab14e3feab675654e8ebf8f2ebce5df4242006fe55f0232ab89e`

