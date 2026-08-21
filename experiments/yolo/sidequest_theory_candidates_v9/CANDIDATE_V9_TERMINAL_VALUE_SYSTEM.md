# V9 candidate — attached terminals as committed values

Status: **independent speculative sidequest analysis, not a GDT result and not
a translation**.

## Decision

The four most frequent attached-terminal families are best modelled, within
this speculative sidequest, as four reusable **value cards carried in one
common COMMIT realization**, not as four punctuation marks:

```text
OPEN CELL     := optional local qualifiers / operands
COMMITTED CELL:= optional local qualifiers / operands
                 + EXACT VALUE CARD
                 + COMMIT(DY)

singleton cell:= inherited question or slot + EXACT VALUE CARD + COMMIT(DY)
```

The strongest claim is architectural, not lexical.  GDT326 still forbids
general factorization of PAGE_HOST from compiler coordinates: each exact joint
tuple remains the licensed atomic card.  The split below is therefore a local
interpretive hypothesis about four already observed tuples, not a renderer
license or a manuscript-wide semantic decomposition.  I call the values `V-S`,
`V-QE`, `V-Q`, and `V-L`; these are deliberately opaque.  They may eventually
expand as a state, operation, result, route, preparation type, quantity, or
other controlled response.  No English word is assigned.

This is the key decomposition exposed by the four families:

| value label | exact joint tuple | host-side formal string | attached coordinate | events | visible realizations |
|---|---|---|---|---:|---|
| `V-S` | `bc4f1f5c006c74a4d26d` | `e` | `b13789bf2874739e46f6` | 12 | `shedy` 10, `cheedy` 1, `tedy` 1 |
| `V-QE` | `7d25241b0e56c836372a` | `okee` | same | 10 | `qokeedy` 10 |
| `V-Q` | `7db18b2f0fb7ed0fcfd3` | `oke` | same | 8 | `qokedy` 8 |
| `V-L` | `de7321bface5628e35d6` | `lche` | same | 8 | `lchedy` 8 |

All 38 events have `DY=1, B3=0`.  Thus their closure coordinate is literally
identical while their host-side formal strings remain different.  This is the
clearest internal reason to test them locally as `VALUE + COMMIT`.  The variation
`shedy/cheedy/tedy` additionally shows why visible spelling is weaker than
exact card identity.

The generic-punctuation component is already represented by the shared DY
coordinate.  Collapsing the four entire cards to punctuation would discard the
only part that systematically distinguishes them.

## Scope and reproducibility

I read only the current route, the compact sidequest state, the GDT327 primary
report, and guarded slices of the fixed prose pages.  The three circle pages
have no GDT327 events and do not enter this terminal audit.  No `f84` or `f84r`
row was opened or materialized.

The event slice was obtained with the repository guard, using selector `page`,
explicit allow-values `f10r,f11r,f55v,f56r,f81v,f82r,f83r`, forbidden prefix
`f84`, and explicit output columns.  It contains 381 events.  Surface displays
were joined by `(locus, group_index)` from an identically guarded GDT276 slice.
Terminal means `DY=1 or B3=1`; this gives the previously reported 90 events,
38 exact types, and leading frequencies 12/10/8/8.

## Complete occurrence audit

Notation: `|` separates fields, `len` counts exact cards in the field, `next`
is the first visible group of the next field, and `NL/NR` means next line or
next record/page rather than the same physical line.  Every occurrence is
listed.

### `V-S` — 12 occurrences

| locus, field | len | complete field surface | immediate predecessor | next |
|---|---:|---|---|---|
| f81v.17 F2 | 3 | `chedy ol shedy` | `ol` (L/O) | `qolchedy` |
| f81v.18 F2 | 5 | `chey ol cheky ol shedy` | `ol` (L/O) | `qokedy` |
| f81v.24 F2 | 4 | `qokal okeey qol cheedy` | `qol` (L/O) | `sal` |
| f81v.27 F2 | 1 | `tedy` | none | `cheky` |
| f82r.7 F2 | 3 | `sotaiin qokar shedy` | `qokar` | `solshedy` |
| f83r.11 F1 | 2 | `sor shedy` | `sor` | `qokaiin` |
| f83r.14 F3 | 1 | `shedy` | none | `qokshedy` |
| f83r.24 F1 | 6 | `soiiin checthy chety otaiin olsaly shedy` | `olsaly` | `qokeedy` (NR) |
| f83r.26 F1 | 5 | `otchey qokeey qoky tol shedy` | `tol` (L/O) | `qokylddy` |
| f83r.28 F2 | 1 | `shedy` | none | `oldy` |
| f83r.37 F3 | 2 | `qokol shedy` | `qokol` | `or` (NL) |
| f83r.44 F1 | 2 | `skar shedy` | `skar` | `otchdy` (NR) |

Distribution: pages f81v/f82r/f83r = 4/1/7; field lengths
`1:3, 2:3, 3:2, 4:1, 5:2, 6:1`; field ordinals `1:4, 2:6, 3:2`.
Nine are LAST and three are singleton ONLY.  Four non-singletons immediately
follow the exact L/O card, but five have other predecessors.  Three are
physical-line final.

### `V-QE` — 10 occurrences

| locus, field | len | complete field surface | immediate predecessor | next |
|---|---:|---|---|---|
| f82r.2 F3 | 3 | `qokain dy qokeedy` | `dy` (Y) | `qokal` |
| f82r.19 F1 | 4 | `okain char okain qokeedy` | `okain` | `lchy` |
| f82r.26 F1 | 2 | `tshey qokeedy` | `tshey` | `cheal` |
| f82r.27 F3 | 1 | `qokeedy` | none | `rshedy` |
| f82r.27 F6 | 1 | `qokeedy` | none | `lochedy` |
| f83r.6 F3 | 3 | `qokaiin chedy qokeedy` | `chedy` | `lchedy` |
| f83r.14 F2 | 1 | `qokeedy` | none | `shedy` |
| f83r.22 F2 | 1 | `qokeedy` | none | `chedain` |
| f83r.25 F1 | 1 | `qokeedy` | none | `qolchey` |
| f83r.27 F1 | 3 | `dain chedy qokeedy` | `chedy` | `shckhedy` |

Distribution: pages f82r/f83r = 5/5; lengths `1:5, 2:1, 3:3, 4:1`;
field ordinals `1:4, 2:2, 3:3, 6:1`.  Five are LAST and five ONLY.  All ten
have a following field on the same line; none is line-final.  The two copies on
f82r.27 select the same value in two nonadjacent cells of one seven-field line.

### `V-Q` — 8 occurrences

| locus, field | len | complete field surface | immediate predecessor | next |
|---|---:|---|---|---|
| f81v.2 F1 | 1 | `qokedy` | none | `okaiin` |
| f81v.18 F3 | 1 | `qokedy` | none | `qokedy` |
| f81v.18 F4 | 1 | `qokedy` | none | `chckhy` |
| f83r.11 F2 | 4 | `qokaiin chkain shcthey qokedy` | `shcthey` | `okair` |
| f83r.20 F3 | 2 | `qokeey qokedy` | `qokeey` | `sol` (L/O) |
| f83r.20 F4 | 3 | `sol cheeety qokedy` | `cheeety` | `qoky` |
| f83r.25 F2 | 3 | `qolchey qokeey qokedy` | `qokeey` | `chedy` |
| f83r.28 F1 | 4 | `saiin cheeky sheey qokedy` | `sheey` | `shedy` |

Distribution: pages f81v/f83r = 3/5; lengths `1:3, 2:1, 3:2, 4:2`;
field ordinals are evenly `1:2, 2:2, 3:2, 4:2`.  Five are LAST and three ONLY.
All eight have a following field on the same line.  f81v.18 and f83r.20 each
select `V-Q` in two immediately adjacent fields.  This is strong evidence that
an exact terminal identity can be deliberately repeated; it does not by itself
say whether the repeated value means a state, operation, route, or amount.

### `V-L` — 8 occurrences

| locus, field | len | complete field surface | immediate predecessor | next |
|---|---:|---|---|---|
| f82r.23 F2 | 1 | `lchedy` | none | `lar` |
| f83r.3 F3 | 4 | `chey daiin chey lchedy` | `chey` (Y) | `qokaiin` |
| f83r.6 F4 | 1 | `lchedy` | none | `qoky` |
| f83r.11 F4 | 1 | `lchedy` | none | `lo` |
| f83r.14 F5 | 2 | `dal lchedy` | `dal` | `qokaiin` |
| f83r.15 F3 | 1 | `lchedy` | none | `tchedy` (NL) |
| f83r.37 F2 | 1 | `lchedy` | none | `qokol` |
| f83r.41 F1 | 2 | `solkey lchedy` | `solkey` | `qolkain` |

Distribution: pages f82r/f83r = 1/7; lengths `1:5, 2:2, 4:1`; field ordinals
`1:1, 2:2, 3:2, 4:2, 5:1`.  Three are LAST and five ONLY.  Seven continue to a
new field on the same line and one at the next line.  Two of the three
non-singletons are followed immediately by qokaiin in the next cell.

## Field ecology and transitions

Across all 90 terminal events, 44 fields consist solely of their terminal card.
The four leading families account for 16 of those 44 singleton cells:

| family | singleton / all | mean field length |
|---|---:|---:|
| `V-S` | 3/12 | 2.92 |
| `V-QE` | 5/10 | 2.00 |
| `V-Q` | 3/8 | 2.38 |
| `V-L` | 5/8 | 1.63 |

This is a heterogeneous value ecology.  `V-S` more often terminates a populated
field; `V-L` and `V-QE` more often fill a cell by themselves.  A single generic
punctuation function does not predict that contrast.  Conversely, no family is
restricted to one field ordinal, one predecessor, or one record position, so
the evidence does not support four rigid columns with four fixed questions.

For adjacent fields on the same physical line, the target-to-target transitions
are:

| from | target outgoing / same-line outgoing | target destinations |
|---|---:|---|
| `V-S` | 2/9 | `V-Q` twice |
| `V-QE` | 3/10 | `V-L`, `V-S`, `V-Q` once each |
| `V-Q` | 3/8 | `V-Q` twice, `V-S` once |
| `V-L` | 1/7 | `V-S` once |

There is no deterministic chain or station order.  The most informative local
event is the repeated `V-Q -> V-Q` on f81v.18 and f83r.20.  Repeated selection
is natural for a controlled response system.  A route model would need an
independently owned drawing position to turn these sequences into stations;
none is available here.

Cross-page recurrence is entirely Biological in this sample.  `V-S` crosses
all three fixed Biological pages; the other three each cross two.  None of the
four occurs on the four fixed Herbal pages.  This is compatible with a common
Biological form deck plus page-local choices.  It is evidence against treating
these four as manuscript-wide punctuation marks.

## Forced architecture comparison

| model | fit | decisive evidence and failure |
|---|---:|---|
| generic punctuation | 42/100 | Explains finality, but the shared DY coordinate already supplies it. It throws away four stable payload hosts, unequal singleton rates, exact repetitions, and Biological restriction. |
| categorical answer/status values | **88/100** | Directly predicts exact identity plus a common commitment layer, singleton value cells, reuse across slots/pages, and adjacent same-value repetition. It must remain broad because no slot question is externally identified. |
| lexical action/result words | 72/100 | Historically plausible recipe tails and populated fields fit. High singleton rates and reuse at many ordinals also remain possible as one-word imperatives/results. It lacks the transition order or source-language syntax needed to beat the value analysis. |
| route/station codes | 61/100 | Fits a picture-addressed apparatus register and compact singleton cells. No family is tied to a drawing-owned station, a fixed ordinal, or a deterministic route transition. |
| inherited/ditto values | 68/100 | Adjacent `V-Q` repeats and the two f82r.27 `V-QE` cells show inheritance is possible. But the same cards also occur after many distinct populated fields and across records/pages; the evidence fits repeated payload selection better than a universal DITTO operator. |

The chosen system is therefore a **reusable committed-value vocabulary**.  A
value may be inherited in a particular singleton cell, but inheritance is a
property of that occurrence, not the lexical meaning of all `V-Q`, `V-QE`,
`V-S`, or `V-L` cards.

## Consecutive pseudo-translations

These are deliberately algebraic.  `✓V-X` means “commit exact value X”; it is
not the word *yes*, *done*, or *result*.

```text
f81v.18
[OTHER ✓] |
[Y — ASSOCIATED — cheky — ASSOCIATED — ✓V-S] |
[✓V-Q] | [✓V-Q] |
[chckhy qoky ...]

≈ one qualified cell committed with V-S; then two consecutive slots both
  receive the same exact value V-Q; the line continues open.
```

```text
f83r.11
[sor + ✓V-S] |
[ITEM/NEXT + chkain + shcthey + ✓V-Q] |
[okair + OTHER ✓] |
[✓V-L] |
[lo ...]

≈ commit V-S for one qualified cell; open the next item and commit V-Q after
  two local qualifiers; commit another opaque value; assign V-L in a singleton
  cell; continue.
```

```text
f83r.14
[OTHER ✓] | [✓V-QE] | [✓V-S] | [OTHER ✓] |
[dal + ✓V-L] | [ITEM/NEXT + shcthy + dal + sy ...]

≈ a run of five committed cells selects three of the recurrent values in
  separate slots; the sixth cell reopens an item and remains uncommitted.
```

```text
f83r.3
[OTHER ✓] | [OTHER ✓] |
[Y — SAME/STATED REFERENCE — Y + ✓V-L] |
[ITEM/NEXT + qotal + dar ...]

≈ bind the paired/reference construction to committed value V-L, then open
  the next item.
```

```text
f82r.27
[OTHER ✓] | [OTHER ✓] | [✓V-QE] | [OTHER ✓] |
[OTHER ✓] | [✓V-QE] | [OTHER ✓]

≈ two nonadjacent cells in one seven-cell line select the same value V-QE.
```

These passages are less fluent than an English recipe because the evidence
supports field operations more strongly than clause syntax.  They nevertheless
make a falsifiable prediction: further pages using the same Biological stencil
should reuse these exact hosts as selectable cell values, while another
closure realization may attach to the same payload only if licensed by the
renderer/register.

## Historical calibration

Historical material keeps the lexical-action rival alive but does not overturn
the internal selection:

- The open [Carolingian recipe transcriptions](https://www.ncbi.nlm.nih.gov/books/NBK608569/)
  include recipes laid out with each ingredient on a new line and preserve an
  unresolved abbreviation `ss`.  This shows that list layout, heavy
  abbreviation, and source ambiguity are ordinary in medical transmission; it
  does not identify any Voynich value.
- The study of late-medieval practical books notes precise ingredient measures
  written with apothecaries' shorthand symbols in an English medical
  miscellany ([Cambridge Core](https://www.cambridge.org/core/journals/journal-of-british-studies/article/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12)).
  Thus a compact value can historically be a measure rather than a word.
- Recipe texts can also end in formulaic actions or efficacy statements.  A
  structural study distinguishes title, ingredients, preparation, application,
  and efficacy phrase ([Nordic Journal of English Studies](https://publicera.kb.se/njes/article/view/24373));
  manuscript cataloguing likewise documents abbreviated *probatum est* at a
  recipe tail ([Royal College of Physicians of Edinburgh](https://www.rcpe.ac.uk/heritage/heritage-blog/cataloguing-handwritten-medical-recipes-part-2)).
  This is a real warning that some committed payloads could expand as RESULT or
  VERIFIED rather than as nominal status codes.

These are analogies of document practice only.  They neither establish a donor
nor justify Latin expansions.  Internally, the common closure coordinate plus
distinct recurrent hosts is compatible with both abbreviated words and
notational values; `committed value` is chosen because it is the narrower claim
shared by both possibilities.

## Predictions and falsifiers

The terminal-value architecture predicts:

1. exact host identity should recur across multiple fields while closure
   behavior remains common;
2. singleton fields should disproportionately contain recurrent values because
   the question/slot is inherited from the stencil;
3. repeated exact values should occur in neighboring or parallel cells without
   requiring the card to mean DITTO;
4. the four families should remain Biological/register-local more often than a
   universal punctuation analysis predicts;
5. if external geometry later owns cell roles, value distributions should vary
   by owned role even after controlling field length and page.

The model would be weakened if a larger predeclared sample showed that exact
terminal identities are exchangeable after conditioning only on line/field
length, or if the same four full cards behaved as universal clause stops in
Herbal prose.  A lexical action/result model would overtake it if independent
parallel texts or externally owned slot semantics mapped one family
consistently to an operation or outcome.  A route/station model requires
repeatable independently annotated geometry.  No such semantic endpoint is
claimed here.

## Compact conclusion

The four 12/10/8/8 families expose a two-layer system:

```text
distinct exact-card/host side = candidate opaque selected payload
shared DY coordinate = commit the field
```

`V-S`, `V-QE`, `V-Q`, and `V-L` are therefore best treated as four entries in
a Biological controlled-value deck.  Their English expansions remain unknown.
