# Sidequest V7 — AIIN as a stated-reference card

Date: 2026-08-21

Status: speculative working theory, not a GDT result or translation. Only the
ten fixed pages and a guarded f84-free GDT327 slice were used. f84 and f84r
were not accessed.

## Main proposal

The exact AIIN card is better read as a reference to a contextually supplied
standard than as a numeral or amount:

```text
AIIN ≈ IDEM / AS STATED / ACCORDING TO THE ACTIVE VALUE
```

The referenced content may be an amount, degree, duration, stage, index or
setting. AIIN itself need not encode which one.

## Complete positional census

AIIN occurs 20 times across all seven fixed prose pages:

- FIRST: 6;
- MIDDLE: 9;
- LAST: 5;
- immediately followed by an attached close: 0;
- Herbal: 9;
- Biological: 11.

This is awkward for a narrow infix quantity marker. It is natural for a
reference/value card whose scope can open a field, modify an interior node or
remain pending at an open-field edge.

Key contexts include:

```text
f10r.6   Y — AIIN — Y
f83r.3   Y — AIIN — Y — COMMIT
f55v.5   ITEM_HEAD — AIIN — X — X — COMMIT
f55v.5   AIIN — STEP — X/COMMIT
f55v.11  AIIN — SET — X — X — Y — X
f81v.7   X — L/O — X — AIIN — X — AIIN — PROC — X/COMMIT
f83r.54  AIIN — L/O — X — Y — X
```

Five open fields end in AIIN. Six fields begin with it. Thus AIIN does not
require overt material on both sides.

## Competing readings

### A. AMOUNT / NUMBER

This explains recipe plausibility and the central position in `Y–AIIN–Y`.
It struggles with field-first and field-final mobility, repeated AIIN inside
one field, and the absence of any established unit or numerical ordering.

### B. PROCESS / APPLY / MIX

This can turn some Herbal/Bio sequences into fluent instructions. It makes
`Y–AIIN–Y` and five field-final occurrences difficult and lacks a visible
operation owner.

### C. Generic coordinate/index value

This fits the checklist architecture and every position but supplies little
source-like content.

### D. Stated-reference or standard-value card

This is selected:

```text
AIIN = bind current slot to a value/setting supplied by the record,
       previous entry, page template or active parameter frame
```

Nearest historical source-class expansions include *idem*, *ut supra*, “as
before,” “the stated amount,” “at the same degree,” or a ditto-like value mark.
No Latin or vernacular word is identified, and AIIN is not read phonetically
as any of them.

## Updated grammar

```text
ITEM_HEAD := qokaiin                  # ITEM / ALSO / NEXT
LINK      := L/O                      # ASSOCIATE / SAME RELATION
REFVAL    := AIIN                     # AS STATED / ACTIVE STANDARD
NODE      := Y or local card
STATE     := CTHY or local card

ENTRY := ITEM_HEAD?
         (NODE | LINK | REFVAL | STATE | LOCAL_CARD)*
         COMMIT?
```

`REFVAL` receives its value type from the field/register. Herbal can supply a
measure or preparation standard; Biological can supply a stage, route setting
or checklist value. The formal function stays constant.

## Concrete readings

### f55v.5, first field

```text
ITEM — AIIN — X — X — COMMIT
```

> Item: use the same or stated setting for the next two local specifications;
> validate the resulting cell.

Medical-content rendering:

> Item: take the pictured simple in the stated quantity, add the two specified
> details, and confirm the preparation.

“Quantity” is supplied by the recipe fork; the card itself means only that the
active standard is reused or instantiated.

### f55v.5, second field

```text
AIIN — STEP — COMMIT
```

> Under the same stated setting, perform the indicated step and validate its
> local value.

### f10r.6 and f83r.3

```text
Y — AIIN — Y
```

> This marked item and that marked item are bound to the same stated value or
> reference.

This finally gives the symmetrical construction a coherent reading without
claiming equal quantities. The two nodes may share a setting, category,
duration, degree, source entry or measure.

### f81v.7

```text
X — L/O — X — AIIN — X — AIIN — PROC — X/COMMIT
```

> Associate the first local value with the next; apply the stated reference to
> the following value, retain that same reference for the process, and validate
> the cell.

The two AIIN cards can be two explicit ditto/reference bindings rather than
two unrelated numerical amounts.

### Field-initial AIIN

```text
AIIN — ...
```

> As stated above / under the active standard: ...

This is especially natural after an earlier itemized cell.

### Field-final AIIN

```text
... — AIIN
```

> ... under the stated value [continuation remains open].

The lack of COMMIT is predicted: a reference binding can remain open for the
next physical line or field.

## V7 source-like pseudo-translation

> Item: open the next entry. Mark its current node, associate it with the active
> relation, and assign the value or setting already stated for this record.
> Validate the local cell. Where two nodes surround the reference card, bind
> both to that same standard. Continue with the next item.

Conditional medical phrasing:

> Item: take the next part, combine it as indicated, and use the previously
> stated quantity or preparation setting. Confirm the result; apply the same
> setting to the paired part and continue.

## Consequences

1. `Y–AIIN–Y` no longer needs a fragile “equal amount” story; it is a shared-
   reference construction.
2. AIIN's field-edge mobility becomes expected rather than exceptional.
3. The itemized-form and indexed-checklist interpretations converge further:
   both need a ditto/reference mechanism.
4. A workshop trainee can copy rare values while knowing only that AIIN invokes
   the active standard.
5. Surface wrapper variation does not change the reference function.

## Weak points

- No explicit antecedent has been externally identified for any AIIN event.
- “Same” can become unfalsifiably broad unless the active record state is
  specified.
- Some first-position occurrences may be ordinary content entries, not ditto.
- Two AIIN cards in f81v.7 could encode two genuinely different values.
- A generic formal slot/index interpretation explains the same positions with
  fewer semantic commitments.
- Nothing identifies the referenced scale as quantity, time, degree, stage or
  anything else.

## Strongest rival

The strongest rival is `AIIN = GENERIC VALUE/INDEX SLOT` with no equivalence or
reuse semantics. It wins if AIIN occurrences do not show local antecedent
continuity and instead align with fixed form coordinates. The stated-reference
model wins if field-initial and repeated AIIN systematically reuse a value or
setting already active in the same paragraph.

## Conclusion

The best current source-class expansion is:

```text
AIIN ≈ AS STATED / SAME ACTIVE VALUE / REFER TO THE CURRENT STANDARD
```

Amount, degree, duration and index are possible values of the reference, not
the meaning of the card itself.
