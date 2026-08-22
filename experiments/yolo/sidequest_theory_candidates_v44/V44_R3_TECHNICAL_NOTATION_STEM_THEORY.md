# V44 R3 — adversarial stem theory from a 1420 workshop register

## Perspective and evidence ceiling

I treat the ten-page V43 dictionary as the internal handbook of a small
workshop.  A repeated form is allowed to be a lexical stem, a code carrier, or
an indivisible memorized card.  It counts as a stem only when distinct licensed
formal realizations preserve a nontrivial V43 meaning intersection.

The audit joins the 381 V40 prose events to the f84-free HPR record by exact
`locus + group_index`, and then to the 173 V43 exact-card defaults.  The HPR
rows were selected through `vmanus-exp query-tsv` using only the 54 explicitly
allowed ten-page loci.  The guard rejected 228 `f84*` rows before parsing.  No
f84 or f84r content was retained.  The assigned meanings remain the creative
V42/V43 defaults, not decipherment evidence.

## Result

There is no single clean spoken-word morphology.  The best hand-learnable
system is mixed:

1. a few fairly contentful card cores, especially `aiin` and provisionally
   `or`;
2. relational or state carriers such as `ok`, `ot`, `l`, `y`, `ey`, and `che`;
3. a table of licensed right completions, frames, inner-D states, and closures;
4. entry renderers chosen by writing position without changing the licensed
   card.

In compact workshop notation:

```text
CARD := licensed(ENTRY_RENDERER, LOCAL_FRAME, HOST, INNER_D,
                 RIGHT_FAMILY, DY, B3)

surface := render(CARD, line/field context)
meaning := lookup(CARD), with HOST contributing only where contrasts support it
```

This remains teachable around 1420: an apprentice learns a small core deck,
then the common completion table and positional hands.  It resembles the
learning burden of recipe brevigraphs, notarial formulae, account symbols, or a
workshop tally system more than a perfectly regular invented cipher.  This is
a historical analogy, not identification of a specific notation.

## Ranked families

### 1. `aiin` — strongest content-stem candidate

All 20 local occurrences are one exact card meaning **a prescribed measure**,
while the visible entry can be `aiin`, `chaiin`, `daiin`, `saiin`, or `taiin`.
This is precisely the behavior wanted from a shared core plus positional
renderer.

Working value:

```text
aiin = STANDARD/PRESCRIBED MEASURE
```

The spelling-neighbour `ain` is not its demonstrated inflection: standalone
`dain` is assigned “through a cloth.”  The extra `i` is therefore potentially
identity-bearing, not ornamental.

Decision: **NATURAL_STEM**, provisionally.  It could still be an indivisible
measure card rather than a spoken lexical root.

### 2. `or` — prepared-medium candidate

Seven base-cell occurrences under `NONE/ch/s/sh` renderer all denote the
**prepared working liquid**.  The one `or+ain` cell means “use the finished
liquid fresh.”  Both preserve a prepared/usable-medium intersection.

Working value:

```text
or = PREPARED MEDIUM / READY LIQUID
```

Decision: **NATURAL_STEM**, weaker than `aiin`.  The ten-page interpretation is
strongly liquid-biased; manuscript-wide `or` may be more abstract than water or
decoction.

### 3. `ey` — endpoint card, but not a raw suffix

All four occurrences are the same exact card, rendered as `shey` or `cheey`,
and V43 calls it “until the liquid runs clear.”  The defensible intersection is
only:

```text
ey-cell = REQUIRED/OBSERVABLE ENDPOINT
```

The counterexample is decisive: surface `chey` belongs to PAGE_HOST `y`, not
`ey`, and its V43 default is “this active portion.”  Therefore a reader cannot
strip a visible final `ey` and assign “clear/until.”  `ey` is an HPR card core
inside a licensed cell, not a free surface suffix.

Decision: **CODE_AXIS**.  The completion-gate value belongs to the exact cell;
whether the host contributes “endpoint” is not independently contrasted.

### 4. `ok` — productive carrier, not a measure noun

The 24 occurrences split into five licensed cards:

| completion | events | V43 expansion |
|---|---:|---|
| `ok + aiin` | 9 | begin the next measured item |
| `ok + ain` | 7 | add a measured share |
| `ok + al` | 6 | combine both shares |
| `ok + ar` | 1 | above the locally marked place |
| `ok + air` | 1 | open the upper conduit afterward |

The first 22 occurrences suggest allocation or manipulation of bounded
operands.  The `ar/air` exceptions broaden it toward spatial routing.

Working value:

```text
ok = ACTIVATE / ALLOCATE / ROUTE A BOUNDED WORK ITEM
RIGHT_FAMILY = licensed kind of item or relation
```

Decision: **CODE_AXIS**.  Calling `ok` “measure,” “water,” or “take” would be
too narrow.

### 5. `y` — current-state carrier with destructive coordinate contrasts

The base cell occurs 18 times under six renderers and means “this active
portion.”  But the same host under inner-D gives `chedy`, eleven times “stir
until uniform,” while the O-frame singleton `choy` is a wet shaded habitat.

Thus the safe rule is:

```text
base y-cell = CURRENT ACTIVE ITEM
inner-D y-cell = learned MIX/UNIFORM operation
O-frame y-cell = separate learned card
```

Decision: **CODE_AXIS**.  The host-wide intersection is too weak for a natural
stem.

### 6. `ot` — oriented relation carrier

Its completions yield prior duration (`+aiin`), lower-outlet direction (`+al`),
and later use of that outlet (`+ar`).  The only common idea is a prior/later or
directed relation.

Decision: **CODE_AXIS** with working value `RELATION/DIRECTION CARRIER`, not a
concrete “lower,” “time,” or “outlet” word.

### 7. `l` — strongest false-stem warning

The host appears as:

- O-frame `ol/chol/qol/sol/tol`: previous preparation, 19 events;
- O-frame plus DY `oldy`: boil gently and close, 2;
- bare `dl`: prepared oil, 2;
- bare plus DY `ldy`: draw off and close, 2;
- `l+ar`: close lower outlet, 1.

No content intersection survives beyond a vague carried state or continuation.
The productive-looking visible family is largely frame and closure machinery.

Decision: **CODE_AXIS**, not a lexical root.

### 8. `che`, `chy`, `cth`

`che` always occurs with DY in this panel.  The plain frame means wash the
apparatus through and close; OT frame means mix equal parts and close.  Their
shared ending is already explained by DY, leaving no secure `che` content.
Decision: **CODE_AXIS**.

`chy` has only two singleton cells: leaf compress versus pouring warmed water.
They weakly intersect in application/liquid placement but do not establish a
root.  `cth` has one cell, `cth+aiin`, assigned addition of expressed juice.
Decisions: **UNRESOLVED**.

The visible similarity `che/chy/cth` is therefore not presently a semantic
paradigm.

### 9. `ain`, `ol`, `os`, `op`

- Standalone `ain` occurs twice as “through a cloth,” but right-family `ain`
  elsewhere does not carry cloth semantics.  **UNRESOLVED**.
- `ol` occurs once as an OT-framed handful measure. **UNRESOLVED**.
- `os` occurs once as coarse crushing. **UNRESOLVED**.
- `op` has no V43 prose assignment. **UNRESOLVED**.

## The most useful dictionary correction

The consolidated dictionary should expose three levels rather than one:

| level | example | allowed default |
|---|---|---|
| exact card | exact `b5df...`, rendered `shey/cheey` | required endpoint; locally “until clear” |
| host contribution | `ey` | possible endpoint carrier, not independently proven |
| visible substring | final letters `ey` in arbitrary surface | no meaning |

Likewise:

```text
aiin  -> provisional MEASURE core
or    -> provisional PREPARED-MEDIUM core
ok    -> operand/relation carrier; completion determines operation
ot    -> relation/direction carrier
y/l   -> low-content state carriers; exact cell must be looked up
DY    -> local-step closure contribution, not the whole action
wrapper -> positional renderer unless a specific cell says otherwise
```

## Adversarial conclusion

The V43 meanings support **two plausible content stems** (`aiin`, `or`), several
**formal code axes** (`ey`, `ok`, `ot`, `l`, `y`, `che`), and six unresolved
short families.  The system is neither a flat 173-word vocabulary nor a clean
prefix–stem–suffix language.  The most economical 1420 workshop model is a
mixed card algebra: a few reusable content cores, common relational carriers,
and many conventional whole-cell values learned by example.

Any future dictionary line like `ey = clear`, `ok = measure`, `l = liquid`, or
`y = portion` is invalid unless it names the full licensed cell.  The complete
cell can retain a concrete creative expansion; the bare surface substring
cannot inherit it.
