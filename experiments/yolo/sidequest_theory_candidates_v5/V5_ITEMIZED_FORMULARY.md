# Sidequest V5 — itemized formulary reconstruction

Date: 2026-08-21

Status: aggressive working theory, not a GDT result or confirmed translation.
Only the ten fixed pages and the f84-free GDT327 interlinear were used. f84 and
f84r were not accessed.

## Main advance

V4's anonymous `ADDRESS/ACTIVATE_CURRENT_SLOT` is given a historically ordinary
source expansion:

```text
exact qokaiin ≈ ITEM / DEINDE / NEXT ENTRY
```

This is a function class, not a phonetic reading. Late-medieval recipes,
inventories and working lists commonly restart successive entries with an
equivalent of “item/also/next.” Such a card can occur at field entry, inside a
long compressed entry, or as a catchword copied at a margin without naming the
object that follows.

The resulting genre is an **itemized pictured formulary**:

```text
PICTURED OWNER
  + descriptive/list entries in open A mode
  + ITEM-headed checked entries in B mode
  + relation, parameter, pointer and state cards
  + exact value/product card carrying COMMIT
```

This unifies the practical-register and indexed-checklist models. The index is
the form of writing; medical/herbal/application material remains the leading
content interpretation.

## Exact qokaiin accounting

The exact card occurs nine times on the fixed prose pages:

- seven field-initial;
- five of those immediately follow a committed field;
- two are physical-line initial;
- one is medial inside a long open field;
- one is field-final and is repeated exactly at the next physical-line start;
- all nine following cards differ when the boundary copy is retained.

This ecology is compatible with:

```text
ITEM: introduce another entry or subentry
DEINDE: continue with the next operation/setting
R./TAKE: a more specifically recipe-like contextual expansion
```

It is less compatible with one recurring substance or liquid because the
followers do not form a stable object frame and no liquid owner is independently
identified.

## V5 compact source lexicon

| exact card/construction | anonymous role | V5 source-class expansion |
|---|---|---|
| qokaiin | address/reactivate entry | ITEM / ALSO / NEXT; sometimes TAKE NEXT |
| L/O | relation or class edge | WITH / OF / TO / IN, selected by form slot |
| AIIN | parameter/index/reference | STATED VALUE / MEASURE / DEGREE / TABLE ENTRY |
| Y | node/pointer | THIS ITEM / PART / ENDPOINT / SAME REFERENT |
| CTHY | status/state | IN THE STATED OR PREPARED CONDITION |
| terminal card | opaque payload + commit | exact local value/product; CELL FILLED |
| Y–AIIN–Y | two pointers under one parameter | EACH/PAIR UNDER THE SAME SETTING |

The table is intentionally asymmetric. qokaiin receives a more concrete
function because its distribution is strongly entry-like. L/O, AIIN, Y and
CTHY remain context-filled register cards rather than single spoken words.

## Source grammar

```text
RECORD := PICTURED_OWNER + ITEMIZED_ENTRY+

ITEMIZED_ENTRY := ITEM_HEAD?
                  + NODE_OR_LOCAL_PAYLOAD*
                  + RELATION_OR_CLASS*
                  + PARAMETER_OR_STATE*
                  + TERMINAL_VALUE_COMMIT?

OPEN_A_ENTRY := accumulated description or specification without checkbox
CLOSED_B_ENTRY := short local value terminated by a committed exact card
```

Physical lines pack entries around a pre-existing drawing. A paragraph owns the
larger record. An entry may cross a line, and a line may contain several
committed entries.

## Continuous V5 excerpts

### f55v.5

Abstract:

```text
ITEM — PARAMETER — local — local — VALUE/COMMIT
PARAMETER — STEP — VALUE/COMMIT
```

Conditional medical expansion:

> Item: for the pictured simple, take or register the stated quantity and its
> two local specifications; confirm that preparation. Enter the following
> measure or setting, perform the indicated step, and confirm its result.

Safer indexed expansion:

> Next entry: assign the stated parameter and two local values, then validate
> the cell. Assign the following parameter and step value, then validate it.

### f82r.3–4

Abstract:

```text
[prior value/commit]
[local relation — parameter — configuration — ITEM(catchword)]
line break
ITEM(executable copy) — [local — state — value/commit]
[following setting remains open]
```

Conditional medical expansion:

> Continue with the next preparation and its configuration—ITEM [written at
> the margin]. Item: take up that same entry on the new line, apply its stated
> condition, and confirm it. Leave the following setting open.

The duplicated “item” is not elegant spoken prose; that is precisely why the
first copy is treated as a scribal catchword and the second as the logical
entry head.

### f83r.3

Abstract:

```text
[value/commit] | [value/commit]
| POINTER — PARAMETER — POINTER — VALUE/COMMIT
| ITEM — local — local
```

Conditional medical expansion:

> Confirm the first two local values. Give or register the two indicated parts
> under one shared setting and confirm that entry. Item: continue with the next
> local specification.

Safer form expansion:

> Validate two cells. Bind two marked nodes to the same reference and validate
> the exact value. Next entry: record the following two specifications.

### f83r record-level paraphrase

> Validate the initial cells. Item: open the next setting and fill its dependent
> values. Confirm the linked cell. Item: open the following state, attach its
> parameter and marked members, and validate it. Continue through the related
> entries, leaving incomplete specifications open until their committed value
> is supplied.

## What became more concrete

1. qokaiin is no longer merely a machine-like ADDRESS tag. Its best source
   expansion is the ordinary itemizing function `ITEM/ALSO/NEXT`.
2. The practical form and indexed checklist cease to be rival genres. A
   formulary is itself an indexed working list.
3. Currier A and B need not represent different syntax. A supplies open dossier
   entries; B supplies explicitly checked subentries.
4. The repeated f82r card has a familiar scribal explanation: anticipatory
   catchword plus executable restart.
5. The source need not repeatedly name the pictured plant, body, vessel or
   diagram slot.

## What remains unresolved

- `ITEM/ALSO/NEXT` is a functional translation, not an identified source word.
- L/O still cannot be narrowed to AND, WITH, OF, IN or TO.
- AIIN may be a value, index, degree, quantity or reference.
- Y may be a pointer, member tag or pure checklist node.
- CTHY may be a state flag with no spoken expansion.
- exact terminal identities remain untranslated local values.
- the internal architecture does not decide whether the content is medical,
  alchemical, mnemonic, classificatory or pedagogical.
- Astro uses the same possible itemizing pedagogy but no shared prose-card
  dictionary.

## Strongest rival

The strongest rival is a content-light workshop checklist with:

```text
qokaiin = MODE/RECORD KEY
L/O      = cross-reference edge
AIIN     = coordinate/value slot
Y        = labelled node
CTHY     = status flag
```

V5 differs mainly by giving qokaiin an upstream itemizing expansion and by
treating the checklist as a practical document rather than a semantic-null
exercise. The rival wins if the same cards track fixed checklist coordinates
without any relation to page-owned practical content.

## V5 stopping point

The best compact pseudo-translation now is:

> For the pictured dossier, enter the next item; attach its marked nodes to the
> stated value, relation or condition; validate the local cell; then proceed to
> the next item, repeating the entry head at a physical restart when necessary.

This is the first source-like function assigned more narrowly than V4's formal
algebra. It still establishes no phonetics, language or confirmed plaintext.
