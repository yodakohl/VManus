# GDT611 formal-frame lexical-slot stress test

Frozen before computing any new carrier, frame, section, or paragraph result.
This is an exploratory falsifier of concrete lexical defaults, not a
decipherment preregistration.

## Scope and inputs

- Read only the published, already guarded, f84/f84r-free GDT605/GDT606 stream
  and published GDT608 formal-role artifacts.  Open no page or image and issue
  no new transcription query.
- Preserve the inherited 68-train/23-held physical-folio split.
- `section` remains an opaque catalogue code in all scores.  Conventional
  image-family names may be mentioned only as conditional compatibility
  glosses; they do not own a text carrier.
- Use GDT608 `q`-left-entry, `y/dy/aN`-right-closure, and `k`-right-nonterminal
  tendencies only as syntax-shaped features.  They receive no meaning.
- Exclude all workshop/sidequest values and all generated Latin, Italian, or
  German outputs.

Pinned byte inputs:

- `guarded_rows.tsv`:
  `d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9`
- `unit_sequences.json`:
  `3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf`
- GDT608 `stable_stem_role_summary.tsv` and `merge_tree.tsv`, with hashes
  recorded by the run manifest.

The route-check query is:

```text
GDT608 lexical slot water wine oil salt root leaf flower seed rub grind boil
heat dry soak vessel bath disease woman healing local frame substitution
paradigm section image type paragraph mini dictionary q y k syntax template
carrier repetition counterexample identifiability permutation
```

It returned a closed `LEXICAL_GLOSSES_FROM_FORMAL_ROLES` family and several
noncanonical workshop reports.  Only the closed-family warning is admissible;
workshop meanings are not inputs.

## Observation layer

An exact **carrier** is one complete hard-chunk sequence of final GDT605 units,
written with `+` between units.  Candidate selection is train-only.  A carrier
is eligible if it has at least 12 train events, 6 held events, occurs on at
least 4 train and 2 held physical folios, and is not a singleton-unit chunk
consisting solely of `q`, `y`, or `k`.

For each occurrence retain only:

- exact internal one-unit masked frames (`u1+*+u3`);
- exact preceding/following hard-chunk carriers on the same physical line,
  separately and as a two-sided frame;
- chunk ordinal, line edge, paragraph edge, section code, physical folio;
- formal shape flags: entry-family at the left edge, closure-family at the
  right edge, and internal/nonterminal `k` family.

Paragraphs are reconstructed exactly by GDT608's published rule: a marker
`<%>` within the first 32 IVTFF characters opens a paragraph; `<$>` closes it;
otherwise the page's active paragraph continues.

## Train-only exchange paradigms

Build a carrier graph.  Two carriers are joined by each exact internal masked
frame they share and by exact one- or two-sided line frames in which both are
observed.  Edge weight is the sum of `log(1+min(count_a,count_b))`, with
internal, left, right, and two-sided channels reported separately.  Retain an
edge only when at least two distinct train frames are shared; then retain the
union of each carrier's five highest-weight neighbours (ties by carrier) and
take connected components.  Connected components and nearest neighbours are
frozen from train, then evaluated unchanged on held folios.  Report held frame
coverage, distinct held folios, and whether the same pair shares any held
frame.  Do not add a held-only carrier or edge.

Frequency-matched controls pair each selected carrier to the nearest eligible
carrier in train log frequency having the same sequence length and the same
three formal shape flags.  Compare held exact-frame reuse and section-profile
drift.

Section enrichment uses a Jeffreys-smoothed carrier-versus-rest log odds in
train and held.  Its null permutes complete section labels among physical
folios within split and within terciles of folio event count for 1,000 fixed
seed replicates.  A section tendency is stable only when train and held signs
agree and the held carrier occurs on at least two physical folios in that
section; the one-held-folio `B` stratum can therefore never establish a robust
`B` lexeme by itself.

Selection stability is measured over 200 fixed-seed train-folio bootstrap
restarts.  A carrier is stable only if it returns to its semantic-family
candidate pool in at least 75% of restarts.

## Concrete candidate families

The requested labels are tested as named competitors, not accepted meanings:

1. liquid/material: `WASSER`, `WEIN`, `OEL`, `SALZ`;
2. plant part: `WURZEL`, `BLATT`, `BLUETE`, `SAMEN`;
3. operation: `REIBEN`, `KOCHEN_ERWAERMEN`, `TROCKNEN`, `EINWEICHEN`;
4. record/entity: `GEFAESS`, `BAD`, `KRANKHEIT`, `FRAU`, `HEILUNG`.

Train-only candidate pools are selected deterministically:

- plant-part pool: highest positive train `H` log odds among members of a
  four-or-more-carrier exchange component (top four);
- liquid/material pool: highest train `P|B` versus other-section log odds in
  a four-or-more-carrier exchange component (top four);
- operation pool: highest sum of the across-carrier z-scores for train
  line-initial rate and entry-family occurrence rate, plus `0.25*log(number of
  train section codes)`, requiring recurrence in at least three section codes
  and a four-or-more-carrier exchange component (top four);
- record/entity pool: best train single-section contrast among `B`, `P`, and
  `T`: select the top three by their maximum positive log odds, then from the
  next seventeen choose the lowest- and highest-line-initial rivals (ties by
  score and carrier).  All stability gates are evaluated only after these
  train-only choices are frozen.

For each pool first choose the exchange component with the highest mean of its
best `k` eligible scores (`k=4,4,4,5` respectively), then take the specified
members from that one component.  Pools are chosen in the fixed order
operation, plant part, liquid/material, record/entity; an already selected
carrier is skipped so the printed 17-entry dictionary has unique keys.
Within-family labels follow descending train frequency and carrier string
after pool selection.

Within each pool, concrete default labels are assigned by a declared
reproducible convention (descending train frequency, then carrier string) only
to make a full candidate dictionary printable.  This convention is not
evidence for which member means which word.

## Identifiability gates

A semantic-family compatibility may be reported if at least three selected
members survive the held sign, exact-frame, folio, `p<=0.05` section-null (when
a section contrast is used), and 75% bootstrap gates; an operation member uses
positive held formal score and at least two held section codes in place of the
section-null gate.  The pool must additionally contain at least two held shared
frame edges.  An exact lexical assignment
is stronger and requires all of:

1. two or more held physical folios carrying the relevant contrast;
2. held reuse of the named exchange frame;
3. an independently owned observable that differs for the named word and every
   listed alternative;
4. the exact assignment scores better than every within-family label
   permutation.

If only carrier distributions are used, any permutation of labels within a
family leaves every score byte-identical.  Such a result is recorded as
`FAMILY_COMPATIBLE__LEXEME_PERMUTATION_UNIDENTIFIABLE`, not as a word.  If even
the family gates fail, use `DEFAULT_ONLY__NO_HELD_FAMILY_SUPPORT`.

The deterministic held paragraph witness is the paragraph with the largest
number of selected dictionary events, then distinct selected carriers, then
lines, ties by paragraph ID.  Print every source line and its exact unit
carriers; annotate only dictionary hits as `[LABEL?]`.  Also print the best
held counterexample for each family: strongest section sign reversal, absent
held frame, or closest alternative carrier, chosen by fixed severity and locus
order.

## Decision

- `CONCRETE_LEXICAL_SLOT_LEAD` requires at least one exact assignment to pass
  all four lexical gates.
- `FORMAL_SLOT_ATLAS__LEXEME_PERMUTATION_UNIDENTIFIABLE` applies when stable
  exchange/section families exist but no exact assignment beats its label
  permutations.
- `NO_STABLE_LEXICAL_OR_FAMILY_SLOT` applies if no family survives held data.

No fluent repair, historical-language fit, semantic postselection, or
paragraph cherry-picking is allowed.
