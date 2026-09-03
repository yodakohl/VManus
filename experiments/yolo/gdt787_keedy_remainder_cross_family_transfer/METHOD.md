# GDT787 method

## Question

Does the independently useful complete word `keedy` carry a reusable semantic
remainder into observed complete `Xkeedy` forms, or are those longer surfaces
better handled as learned wholes despite their strong written paradigm?

The candidate inherited from the GDT646/GDT647 quality architecture is
`HOT + END`, with `CLOSED` tested separately because GDT689 already showed
that visible `d` can be silent when the sister is intrinsically terminal.

## Inputs and boundary

The experiment reconstructs the existing 179-page admitted cache through
GDT782's guarded `query-tsv` loader.  The loader rejects `f84*` before a row is
materialized.  ZL3b, IT2a and RF1b are treated as alternate readings of one
manuscript; their agreement licenses an exact written surface but does not
count as three independent witnesses.  Stolfi is a boundary sensitivity only.

Current whole cards come from the GDT734 dictionary.  GDT647 supplies the
three original quality-family anchors; GDT689 controls the silent terminal
`d`; GDT737 and GDT754 identify retired p/s/r/l patient identities and
source-composed prose; GDT786 supplies the form-specific `salkeedy` card.
Every input is path/hash locked.

## Census and formal paradigm

All raw complete words ending exactly in `keedy` are inventoried.  Exact
occurrences require the occurrence rank of that surface to fit the minimum
surface capacity in ZL3b/IT2a/RF1b on the same line.  The principal formal deck
is ten equally weighted rows (bare plus nine left contexts) by five tails:

```text
Xky  Xkey  Xkeey  Xkedy  Xkeedy
```

The nine prefixed rows are `che, cho, l, o, ol, qo, qol, sol, y`.  Separate
same-X comparisons isolate candidate content:

```text
HOT:    Xkeedy versus Xteedy       (six prefixed X)
END:    Xkeedy versus Xkedy        (nine prefixed X)
CLOSE:  Xkeedy versus Xkeey        (sixteen prefixed X)
```

Each X receives one vote regardless of token count.  This prevents the 201
exact `qokeedy` tokens from dominating the family.

## Target-masked semantic prediction

Every exact `*keedy` target and every GDT754 source-composed surface is masked
as semantic evidence.  The remaining positive whole-card axes and structural
placement features are aggregated first within physical folio and then within
complete surface.  Shared absent binary fields earn no similarity.  The score
is Jensen-Shannon profile similarity on 0--1, not a probability.

For each of the nine complete prefixed squares the additive prediction is:

```text
profile(Xkeedy) = profile(Xkeey) + profile(Xkedy) - profile(Xkey)
```

Negative predicted cells are clipped to zero.  It is compared with (a) the
profile of standalone X, (b) a clean learned whole chosen only by complete-form
length/frequency geometry, and (c) a deliberately strong best-profile
sensitivity chosen after seeing the target.  Structure-only and register-free
feature subsets are reported separately.

An additional, stricter positive-axis audit removes cards descended from the
old GDT647/652/661/663/664/665 family prose.  It measures folio-balanced R1
and R3 HOT-vs-COLD, END-vs-MIDDLE and CLOSE contrasts without rewarding
shared zeroes.  Missing positive information is `NA`, never a perfect match.

## Boundary and split sensitivity

All raw and exact adjacent `X keedy` spans are inventoried.  Five X values
occur both fused and separated: `al`, `cheol`, `chol`, `ol`, `sol`.  The split
inventory is a boundary sensitivity only; it is not fed into the semantic
profile score.  The relevant fused rows can instead be read against the same
nine-row tournament.  A separate guarded Stolfi audit asks only whether a
current-reader fused target is fused, split or otherwise read at the same
locus.  Neither test independently names a meaning.

## Decision and renderer rule

`PORTABLE_KEEDY` would require the additive model to defeat both primary nulls
in at least six of nine X rows and coherent HOT, END and CLOSE directions.
`SHELL_BOUND` requires a non-post-hoc block of at least three related X rows
whose partners also hold.  Otherwise the result is `WHOLE_ONLY`.

The executed result is `WHOLE_ONLY`: only three rows defeat both nulls, and
they do not form a coherent shell.  Existing form-specific HOT+END cards can
survive on their own evidence.  `CLOSED` is not appended automatically.  To
keep every observed form nonempty, all 38 concrete German displays use an
explicit common HOT+END **C0 family prior**.  That is one exploratory display
policy, not 38 independent semantic findings and not a component export.
GDT787 grants zero new renderer licences; inherited scopes remain unchanged.

The 0--100 display confidence is an editorial evidence weight over recurrence,
reader exactness, older whole-card lineage and counterevidence.  It is neither
the Jensen--Shannon score nor a calibrated probability.
Each card keeps two pairwise-distinct concrete semantic rivals and, separately,
a learned-whole, analogy or composition mechanism alternative.

Ceiling: C2 observed current-reader complete-word boundaries; C1 formal
`*keedy` family and at most form-specific whole roles; C0 concrete displays
and cross-family semantic hypotheses.  Zero plaintext, language, phonetics,
specific substance, EVA character value, free substring/component, unseen
form, new page, image, OCR, transcription, `f84` or `f84r`.
