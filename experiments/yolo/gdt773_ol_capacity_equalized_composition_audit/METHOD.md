# GDT773 method — equal capacity, concrete composition

## Question

Can the same fifteen `ol` contexts distinguish five readings once the inherited
GDT770 binding asymmetry is removed? Which reading is the best invariant
single-word fallback under observed topology, and does one compact contextual
operator produce a better practical default for every occurrence?

## Inputs

- GDT772's fifteen-case `ol` table and complete 22-line cohort;
- the seven-case GDT772 manual recipe audit;
- GDT763's sixteen amount-contact classifications and GDT769's global exact
  `ol` census;
- GDT769's already cached historical relator analogues;
- the authored five-model, fifteen-case and contextual-dispatch specifications
  in `src/`.

Only eleven lines containing the fifteen already admitted `ol` occurrences are
rendered. No raw mixed TSV, new image, OCR or transcription is read.

## Method

### 1. Equal structural capacity

The old score rewarded its relator for a synthetic two-sided `FIELD_EDGE`, but
did not give the nominal rival an equivalent way to consume the same right
modifier. GDT773 removes every candidate-specific binder. At each occurrence,
all five pure readings may consume the same one left and one right typed edge.
The capacity penalty is therefore only the number of absent typed sides and
must be identical for all five candidates case by case, in aggregate and after
leaving out any physical folio. A difference is an implementation failure, not
semantic evidence.

### 2. Formal five-way topology score

The immediate left and right observations are reduced without reading the
target as either amount/value (`A`), content/field/process (`C`), or absent
(`0`). This yields the observed topology inventory `AC=7`, `CA=2`, `CC=2`, and
one each of `A0`, `0A`, `AA`, and `C0`.

The authored topology rules charge `0` for support, `1` for neutral evidence,
and `2` for contradiction. Nominal-head support is bidirectional (`AC|CA`);
partitive `von` supports `AC` but contradicts `CA`; field/sequence supports
`CC`; measure/unit supports `AA|A0|0A` and contradicts content-only frames; and
directional `aus` can receive support only if an independent right-hand
`SOURCE|MATERIAL` role is visible. No such directional case occurs.

The formal whole-deck scores are therefore:

- quantifiable nominal head: **6**;
- partitive `von`: **10**;
- field/sequence marker: **13**;
- measure/unit complement: **15**;
- directional `aus`: **24**.

The nominal head is the unique invariant fallback, remains uniquely lowest in
all ten leave-one-physical-folio-out folds, has nine supports on eight folios,
includes two supports on two folios outside the seven focal acquisitions, and
has no contradiction. The entire four-point margin over `von` comes from the
two reverse `CA` cases; the seven focal `AC` cases contribute a zero nominal
versus-`von` delta.

### 3. Five explicit practical readings

The pure alternatives are:

- partitive `von`;
- directional/source-result `aus`;
- a quantifiable nominal head `Ansatz/Inhaltsstoff`;
- a field boundary or continuation rendered `:`, `;`, `und` or `dann`;
- a measure/unit complement.

Each case receives a fixed four-level workshop-fit cost: `0` natural, `1`
usable, `2` strained, `3` locally contradictory. The source table records all
five costs, a concrete mini-reading, the reason and the evidence reference.
This is an explicit practical model comparison, not a claim that German words
have been cryptographically recovered.

### 4. Contextual record-field model

The sixth model is a single record-field operator with two main branches and
five ordered context rules:

1. amount/value→content opens the associated content field as `Ansatz:` (five
   cases);
2. content→amount opens the associated quantity field as `Menge:` (two cases);
3. before an independent process it continues as `und dann` (two cases);
4. between two content fields it coordinates as `und` (one case);
5. at a field boundary or after an already filled value/content field it emits
   `;`, with the one explicitly authored nested-field display emitted as `:`
   (five cases).

Thus the practical split is exactly seven amount/content associations and
eight field/sequence connections. It does not emit `von` or `aus` as its
selected output.

Ordered rules in `src/DISPATCH_RULE_SPECS.tsv` must cover every one of the
fifteen cases exactly once. The mixed model pays a fixed complexity cost of
two; it cannot win merely by choosing the cheapest word after seeing each case.
Its selected local cost is zero in all fifteen cases, hence adjusted cost
**2**, compared with **6** for the best pure practical model,
field/sequence. Every selected output remains visible in the occurrence ledger
and eleven-line reader.

### 5. Mechanical ledger and manual record display

`GDT773_11_LINE_TOKEN_DEFAULTS.tsv` is the auditable token ledger and
`GDT773_11_LINE_READER.tsv` is its mechanical line rendering. Together they
account for all 93 source tokens as 91 visible practical units; consumed
multi-token amount spans render once.

The separate `GDT773_11_LINE_POLISHED_RECORD_READER.tsv` is a non-scoring
presentation layer authored line by line. It must preserve the locus, source
line, target count, and all fifteen selected `ol` directions. It may add
punctuation, nominalize inherited imperative-like prose, and expose an unclear
process or field, but it may not alter a target assignment or feed back into a
fit score. Across its 78 non-`ol` tokens, 33 have no structural type, 29 carry
only an inherited display default, and three are not reader-exact. Those counts
are visible limitations, not evidence for the `ol` model.

### 6. Independent readings, historical analogues, and global check

Two independently authored practical judgments remain visible rather than
being averaged away. The apothecary reader assigns seven cases to a nominal
head and eight to field/sequence. The specialist-scribe reader assigns five to
`von`, seven to field/sequence, two to measure/unit, and one to a nominal head.
They agree exactly on six primary cases, all field/sequence contexts, and
neither assigns a primary case to `aus`.

Cached near-period analogues keep four constructions distinct: direct or
genitive amount attachment, coordination/sequence, source-to-result `ex`, and
unit/measure fields. In particular, `aus` requires actual direction, and a
fixed unit predicts much denser amount contact than the observed sixteen
contacts among 376 reader-exact `ol` occurrences. These channels constrain the
working interpretation but contribute no EVA-letter or lexical identity.

## Decision rule and claim ceiling

The experiment records two deliberately separate decisions:

1. the formal topology score selects an invariant whole-form fallback only if
   the support, non-acquisition support, margin, contradiction, directional,
   unique-minimum, and folio-holdout gates pass;
2. the practical renderer selects the lowest total of authored local fit plus
   declared model-complexity cost.

Ties remain explicit. The composite operator is accepted only if every case is
covered once, no rule uses target prose or an assumed `ol` identity, and it
improves on every pure practical model after its complexity cost. Accordingly,
`Ansatz-/Zubereitungsposten` is the invariant single-word fallback, while the
5/2/8 contextual operator is the selected running-text renderer.

The result may select a replaceable occurrence-conditioned renderer and state
that `von`, `aus`, nominal head, separator and unit are not interchangeable.
It confirms no Voynich lexeme, word class, plaintext clause, language, cipher,
substance, liquid, operation, EVA character value or productive component.

The independent validator completes 6,507 checks: eight source locks, separate
capacity/topology/dispatch/reader reconstruction, all decision invariants, and
a byte-identical replay of all 20 runner artifacts plus `REPORT.md`.
