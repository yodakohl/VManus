# Sidequest V6 — L/O as an associative-link card

Date: 2026-08-21

Status: speculative working theory, not a GDT result or translation. The audit
uses only the ten fixed pages and a guarded f84-free GDT327 slice. f84 and f84r
were not accessed.

## Question

Can exact L/O be expanded more concretely than V5's generic
`RELATION_OR_CLASS_EDGE`?

## Complete occurrence ecology

The exact card occurs 19 times:

- f10r: 3;
- f81v: 9;
- f83r: 7;
- MIDDLE: 14;
- FIRST: 3;
- ONLY: 1;
- LAST: 1.

Twelve occurrences lie in fields that eventually commit; seven lie in open
fields. It participates in repeated internal frames such as:

```text
f10r.8   ... X — L/O — X — L/O — AIIN — X
f81v.2   ... X — L/O — X ... X — L/O — X ...
f81v.18      Y — L/O — X — L/O — X — COMMIT
```

but also occurs as:

```text
f81v.7   L/O                         [one-card open field]
f83r.20  L/O — X — X — COMMIT       [field first]
f83r.37  L/O — X — COMMIT           [field first]
f83r.52  X — X — X — L/O            [field last/open]
```

Therefore L/O cannot require two overt textual operands.

## Competing source functions

### A. Narrow conjunction or preposition

```text
L/O = AND / WITH / IN / OF / TO
```

This works well for the 14 medial cases but badly for the field-first,
field-only and field-final cases unless extensive ellipsis is added. No one
English preposition fits all environments.

### B. Portion or component label

```text
L/O = PART / PORTION / INGREDIENT SLOT
```

Repetition inside ingredient-like lists is attractive. But the standalone and
field-edge cases remain ambiguous, and nothing independently associates the
card with amount, material or a pictured part.

### C. Pure class/checklist edge

```text
L/O = RELATION EDGE / CROSS-REFERENCE SLOT
```

This fits every position formally and matches the indexed-form model. It is
less informative as a source expansion.

### D. Associative link with inherited operands

```text
L/O = ASSOCIATE WITH ACTIVE ITEM / SAME RELATION / LINKED ENTRY
```

This is the selected model. Its nearest source-like realizations are broad:

```text
cum / with
ad / to
de / of-from
similiter / likewise
idem relatione / associated as above
```

The form slot determines the fluent preposition. The stable card function is
`ASSOCIATE(active_node, local_or_inherited_node)`.

When both operands are explicit, L/O appears medially. At field start the
active operand is inherited from the previous cell. At field end the target is
left open. In a one-card field both operands are supplied by record state and
the card means approximately “same association as above.”

## Selected miniature grammar

```text
ITEM_HEAD := qokaiin                 # ITEM / ALSO / NEXT ENTRY
NODE      := Y or local exact card
VALUE     := AIIN or local exact card
STATE     := CTHY or local exact card
LINK      := L/O

LINK_FRAME := NODE? LINK NODE?
ENTRY      := ITEM_HEAD? (NODE | VALUE | STATE | LINK_FRAME)* COMMIT?
```

The optional operands are not arbitrary deletion. They inherit from the active
paragraph/field frame. A physical line break does not clear that frame; a new
paragraph normally does.

## Concrete V6 readings

### f10r.5

```text
X — X — L/O — CTHY
```

> For the pictured simple, record the local item associated with its stated
> condition.

Water or habitat may occupy one opaque X, but L/O itself is not WATER.

### f10r.8

```text
X — X — X — L/O — X — L/O — AIIN — X
```

> Record the local specification; associate it with the following item, then
> associate that item with the stated parameter or reference and its final
> local value.

### f81v.18, field 2

```text
Y — L/O — X — L/O — X — COMMIT
```

> Take the marked node, associate it with the first local value and likewise
> with the second; validate the completed cell.

Conditional medical rendering:

> Apply the indicated part with the first preparation and with the second;
> confirm the resulting entry.

The verbs *apply* and *preparation* are supplied by the medical content fork,
not by L/O.

### f81v.7, standalone L/O field

```text
L/O
```

> Associate this cell as above / retain the current relation.

This is the decisive reason to prefer an inherited associative link over a
narrow spoken preposition.

### f83r.37

```text
L/O — X — COMMIT
```

> For the associated entry, supply the local value and validate it.

### f83r.52

```text
X — X — X — L/O
```

> Record the local values and leave their association open for the following
> continuation.

## Updated source-like idiom

The itemized formulary can now be rendered as:

> Item: activate the next entry. Mark its node, associate it with the stated
> value or condition, and validate the local cell. A bare association inherits
> its participants from the current record; an association at the end remains
> open into the continuation.

This accounts for both list-like and sentence-like appearances without making
the physical line a sentence.

## What remains weak

- The inherited operands are reconstructed from form continuity, not observed
  referents.
- `ASSOCIATE` could still be a purely notational cross-reference.
- The varying English prepositions are contextual paraphrases, not multiple
  proven senses.
- The standalone occurrence could be an arbitrary one-card value rather than
  ellipsis.
- No pair of explicit pictured operands owns a particular L/O occurrence.
- A medical reading remains conditional; the same grammar can encode an index,
  catalogue, apparatus configuration or teaching form.

## Strongest rival

The pure checklist model treats L/O as a cross-reference edge with no spoken
counterpart. It wins if L/O placement tracks fixed form coordinates rather than
the presence of compatible left/right nodes. The associative model wins if
L/O consistently links comparable explicit or inherited roles and its bare
field reuses a relation established immediately before it.

## V6 conclusion

The best current source-class expansion is:

```text
L/O ≈ ASSOCIATED WITH / IN THE SAME RELATION / LINK AS ABOVE
```

not one fixed AND, WITH, OF, IN, TO, PART, or WATER word. This is more concrete
than `RELATION_EDGE` while still explaining every field position with one
function.
