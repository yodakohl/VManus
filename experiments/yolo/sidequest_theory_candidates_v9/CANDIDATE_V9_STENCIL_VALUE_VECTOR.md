# Candidate V9 — latent stencil and categorical value vector

Status: **speculative sidequest candidate, not a GDT result and not a
translation**.

Scope is fixed to `f10r`, `f11r`, `f55v`, `f56r`, `f81v`, `f82r`, `f83r`,
`f67r2`, `f68r1`, and `f69v`. This pass uses the full formal records on the
three Biological pages and the Herbal-B bridge `f55v`. Neither `f84` nor
`f84r` was accessed. ZL3b/IT2a/RF1b are alternate readings of one manuscript,
not independent witnesses. Exact card identities below are anonymous formal
objects.

## Decision

The best model is a **slot-conditioned categorical status/value vector**:

```text
PICTURE/PARAGRAPH OWNER
  -> latent register stencil S1 ... Sn
  -> one compact answer packet per active slot
  -> exact value/status card + attached COMMIT
```

This is narrower than saying that every terminal card is an action or result,
but broader than a binary YES/NO checklist. The frequent terminal identities
behave as reusable categorical values which can fill several inherited slots.
The evidence does not identify what any category means. Some identities may
still be lexical operation/result abbreviations, and the entire effect could
ultimately reduce to a formal closing inventory.

The selected source-class paraphrase is therefore:

> For the pictured record, instantiate the applicable configuration slots;
> enter the selected status or value in each slot, commit it, and repeat an
> earlier value where the same exact card recurs.

`status`, `value`, `slot`, and `commit` are analytical classes, not confirmed
English lexemes.

## Frozen sequences before semantics

The sequences were frozen as exact identities and field lengths before the
candidate meanings were compared. `C` means that the field ends in an attached
DY/B3-bearing close; `O` means open. Six-hex labels are only readable handles
for the 20-hex exact IDs.

The four recurrent terminal families are:

| handle | exact terminal ID | events | pages | singleton fields | field lengths | field ordinals |
|---|---|---:|---|---:|---|---|
| T12 | `bc4f1f5c006c74a4d26d` | 12 | f81v 4; f82r 1; f83r 7 | 3 | 1–6 | F1 4; F2 6; F3 2 |
| T10 | `7d25241b0e56c836372a` | 10 | f82r 5; f83r 5 | 5 | 1–4 | F1 4; F2 2; F3 3; F6 1 |
| T8a | `de7321bface5628e35d6` | 8 | f82r 1; f83r 7 | 5 | 1–4 | F1 1; F2 2; F3 2; F4 2; F5 1 |
| T8b | `7db18b2f0fb7ed0fcfd3` | 8 | f81v 3; f83r 5 | 3 | 1–4 | F1–F4 twice each |

None of these four occurs on `f55v`. This matters: they are not demonstrated
Herbal/Biological names for a common material or quality. They are a local
Biological deck, even though the B register itself crosses the Herbal/Bio
boundary.

The two repeated stencil pairs are especially diagnostic:

```text
f81v.17  1C | 3C | 1C | 4O    54e32e | T12 | 28ffbc | OPEN
f82r.7   1C | 3C | 1C | 4O    cbb42a | T12 | daa134 | OPEN

f82r.3   2C | 4O               c1db6b | OPEN
f83r.8   2C | 4O               c45eba | OPEN
```

In the first pair eight of nine cards vary, but the three-card second field
ends in the same exact T12. This is positive evidence for a reusable slot or
construction. The second pair holds the shape fixed while changing its closed
terminal, proving that field shape alone does not determine the value. With
only these two cross-record stencil pairs, neither observation licenses a
semantic dictionary.

## The f82r.27 vector

The full frozen line is:

```text
surface:  pchedy | rsheal daldy | qokeedy | rshedy | qoteedy | qokeedy | lochedy
shape:    1C     | 2C           | 1C      | 1C     | 1C      | 1C      | 1C
IDs:      65df3c | 98bdc4 78b3b3| T10     | 7f68f6 | ff1783  | T10     | f2af63
slot:     S1     | S2           | S3      | S4     | S5      | S6      | S7
```

This is the strongest complete vector because six of seven cells are
terminal-only and S3 and S6 repeat the same exact value T10. The first cell is
also a one-card committed field; S2 alone contains a two-card packet.

A concrete working translation is:

> Pictured configuration: slot 1 = status A; slot 2 = qualified status B;
> slot 3 = setting C; slot 4 = setting D; slot 5 = setting E; slot 6 = the
> same setting C; slot 7 = status F. Commit every entry.

An equally explicit ledger rendering is:

```text
S1=A; S2=(B, qualifier b); S3=C; S4=D; S5=E; S6=C; S7=F.
```

The repeated `qokeedy` licenses only equality of the anonymous card at S3/S6.
It does not prove equal dose, repeated treatment, identical liquid, or a ditto
sign. The fluent words `configuration`, `status`, and `setting` are supplied by
the selected model.

### Image ownership

On the permitted f82r image, this short run lies at the lower boundary of a
large text block immediately above the crowded lower pool/apparatus scene. The
page as a whole contains several figures, containers, conduits and pools, so a
configuration record is visually plausible. But no line visibly points to a
particular figure or pipe, and the inferred fields have no drawn boxes or
column rules. Ownership could be the lower scene, the preceding paragraph, or
a transition between them. All object/station assignments remain uncertain.

The same caution applies across f81v and f83r. Text is fitted around and above
drawings, but the visual adjacency does not independently name the terminal
values. `f55v` confirms that B-style short committed fields can occur on a
pictured plant page, yet it does not contain any of T12/T10/T8a/T8b.

## Model comparison

### 1. YES/NO/status

**Retain only the broad status/value part; reject binary YES/NO.** Thirty-eight
exact terminal types across 90 terminal events are far too rich for an
unqualified two-answer system. No pair of families alternates cleanly in the
same repeated slot. However, singleton committed cells, adjacent repeated
values (`f81v.18` F3–F4), and the S3=S6 repeat on f82r.27 fit a compact
categorical status inventory.

### 2. Operation/result

**Live runner-up.** A terminal payload after a longer field can naturally be a
result or commanded operation. But every leading family also occurs as a
one-card field, and the four families range across field lengths and ordinals.
That requires inherited operands or elliptical imperatives. It is possible,
but adds more source syntax than the categorical-cell reading.

### 3. Path/station

**Visually attractive, structurally unowned.** Biological pictures contain
plausible stations, routes and endpoints. Yet no exact field-to-drawn-node
mapping is established, f82r.27 has seven cells without seven independently
owned picture targets, and the same terminal identity moves among different
field ordinals. Treat path/station as a possible question axis, not as the
answer-card dictionary.

### 4. Material/quality

**Plausible content expansion, not the selected formal class.** Medieval
medical records can tabulate ingredients, measures, qualities and treatments.
But the four leading families are absent from the Herbal-B bridge f55v, so a
cross-register material or elemental vocabulary is specifically unsupported.
Local bath-medium, temperature, degree or quality values remain possible.

### 5. Purely formal closers

**Strong adversarial alternative, but too lossy as the default.** All four
families necessarily share closing behavior, and no semantic endpoint exists.
Nevertheless there are 38 exact terminal identities rather than one or two
generic terminators; fixed shape can take different terminal identities, and
an exact identity can recur non-adjacently inside one seven-slot vector. The
least lossy representation is therefore `unknown categorical payload +
COMMIT`, while explicitly retaining a future collapse to a formal closer
inventory.

Provisional ranking:

| model | fit / 10 | principal reason |
|---|---:|---|
| categorical status/value vector | **8.5** | preserves exact identities, singleton cells and repeated slot values with minimal syntax |
| operation/result cards | 7.0 | good terminal semantics, but needs pervasive ellipsis for singleton cells |
| purely formal closers | 6.5 | safest semantically, but discards exact within-vector equality and large terminal inventory |
| material/quality values | 5.5 | historically plausible but fails the f55v bridge expectation |
| path/station values | 5.0 | picture-compatible but no owned node-to-cell alignment |
| binary YES/NO | 2.5 | inventory and lack of paired alternation contradict a binary code |

## Historical calibration

Structured medical reference formats are historically real, so a latent value
vector is not anachronistic:

- The US National Library of Medicine describes a ca. 1145 manuscript page as
  a [table of measurements for recipe ingredients](https://www.nlm.nih.gov/hmd/topics/medieval/treatises-96-recto_100886418-sm.html?imgid=2).
- A late-fifteenth-century French medical miscellany contains both a
  [table of ailments and medicines and a table of herbs and ailments](https://find.library.upenn.edu/catalog/9958854883503681), alongside prose recipes.
- Ibn Jazla's *Taqwim al-abdan* supplies an especially strong functional
  comparator: diseases are arranged under twelve recurrent headings including
  prognosis, causes, signs and treatments in a
  [medical tabular form](https://commons.wikimedia.org/wiki/File:Tables_of_the_Body_for_Treatment_WDL9713.pdf).
- The Durham catalogue shows the opposing ordinary-prose baseline: a practical
  miscellany can place a [monthly regimen, bath recipes, wound recipes and
  brief medical notes](https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s19s1616306.xml)
  together without encoding them as a questionnaire.

These sources establish only that lists, tables, recurring headings and bath
recipes belonged to medieval medical book culture. They do not identify the
Voynich language, origin, donor, slot headings, or terminal values. Ibn Jazla's
surviving illustrated comparator cited here is a later copy from a different
scribal tradition, so it supports function, not descent or visual homology.

## Discriminating predictions

1. If categorical slots are real, future repetitions of an exact stencil on
   the fixed pages should preserve some terminal identities by slot more often
   than a field-length/page-frequency baseline predicts.
2. If the cards are operations/results instead, their immediate left-card
   contexts should be more stable than their absolute field ordinals.
3. If they are path/station values, a preregistered visual ownership map should
   predict terminal identity across complete held records; adjacency chosen
   after seeing the strings is inadmissible.
4. If they are material/quality values shared with the Herbal register, an
   expanded but predeclared Herbal-B bridge must recover the families. The
   current fixed f55v bridge supplies zero of the four.
5. If they are purely formal closers, exact family identity should be predicted
   from renderer/field shape as well as from the full left payload, and slot
   identity should add no held-record information.

## Claim ceiling

The result is a working translation of a **form vector**, not plaintext:

```text
f82r.27 = [A, (B,b), C, D, E, C, F] with seven local commitments
```

Confirmed English lexemes: **0**. Confirmed plaintext clauses: **0**. The
selected model changes the most useful reading of the ignored terminal-only
runs from “seven opaque words” to “seven filled categorical cells,” while
leaving every category unnamed.
