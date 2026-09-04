# GDT788 method

## Question

Does the independently useful complete word `dal` carry a reusable semantic
remainder into observed complete `Xdal` forms, or is the visible family better
handled as learned or form-specific wholes?

The inherited practical lead is `dal = Material I, abgemessen`, with the value
axis still open. The experiment tests that lead rather than presupposing that
EVA `d` means “measure” or EVA `al` means “material”.

## Guarded corpus and exactness

The existing 179-page cache is reconstructed through GDT782's guarded
`query-tsv` loader. Forbidden `f84*` selectors are rejected before rows are
materialised. ZL3b, IT2a and RF1b are alternate readings of one manuscript;
agreement licenses a reader-exact written occurrence but never supplies three
independent semantic votes. Stolfi is used only as a boundary sensitivity.

All raw complete surfaces ending in `dal` are inventoried. The primary model
uses ten X rows:

```text
ch  che  o  oke  ol  ote  qo  qoke  sh  she
```

crossed with four complete tails:

```text
Xal  Xdal  Xar  Xdar
```

Every primary cell has at least two exact occurrences on at least two physical
folios. A 16-by-4 lattice adds six low-support rows as an inventory sensitivity
but does not let singleton cells vote in the primary semantic decision.

## Two transfer models

The surface-parallelogram model is fixed as:

```text
SHIFT(Xdal) = normalize(clip(P(Xal) + P(Xdar) - P(Xar)))
```

The stronger direct-remainder rival uses the bare complete words:

```text
CORE(Xdal) = normalize(clip(P(Xal) + P(dal) - P(al)))
```

These are relations among complete-whole profiles, not arithmetic over known
word pieces. Negative cells are clipped to zero and every field is
renormalised. Each occurrence is balanced inside its physical folio and each X
row then receives one vote.

Both candidates are compared with `Xal` and with a learned-whole null chosen
only by length, exact-frequency bin and edit distance. The target's similarity
or meaning is unavailable during donor selection. Full, structural,
register-free and semantic-only views are reported.

Fields absent in the observed `Xdal` target are `NA` for every candidate in
that row. A target-populated field absent from a candidate scores zero. This
common target-defined rule prevents different models from being averaged over
different fields. Scores are Jensen–Shannon similarities, not probabilities.

## Leakage mask

All raw surfaces ending in `al`, `dal`, `ar` or `dar` are masked from semantic
neighbour evidence, whether reader-exact or not. GDT754 provenance forms,
GDT737 quarantined forms and every GDT734 card descended from
GDT653/654/655/711/764 are added. The resulting union contains 996 surfaces.

The same mask removes contaminated learned-whole donors. This corrects the
pilot in which forms such as `chtal`, `cheeal` and `chedar` could falsely act
as independent controls even though their history already belonged to the
tested family. Thirty-two of GDT746's 46 reference wholes remain.

Positive neighbours must additionally be reader-exact, known, W2/W3,
composition-credit zero, component-export zero and free of the retired
powder/seed/root/wood patient prose. `VALUE` is kept as its own axis instead of
being silently dropped.

## Direct semantic-axis test

For AMOUNT, VALUE, MATERIAL, PART, PREPARATION, PROCESS and CLOSE, the model
measures folio-balanced radius-one and radius-three rates around every lattice
cell. It records:

```text
d effect in AL carrier = rate(Xdal) - rate(Xal)
d effect in AR carrier = rate(Xdar) - rate(Xar)
DiD                    = first effect - second effect
shared d effect        = mean(first effect, second effect)
carrier contrast       = mean(AL cells) - mean(AR cells)
```

An all-zero four-cell row is `NA`. Exact sign flips are descriptive checks;
they do not turn an axis label into a word translation.

## Boundary evidence

Every raw adjacent `X dal` sequence is retained. The exact deck requires both
tokens to be reader-exact and the ordered pair to remain present in all three
current readers. Fused-versus-separated families and a guarded Stolfi audit are
reported separately. None enters the semantic profile score.

The 115 exact spans are also encoded in the fixed GDT388 relation schema and
run through `vmanus-exp check-edge-packet`. They are intentionally
nonvisual/ineligible acquisition rows, not score-ready relation evidence.

## Decision and dictionary rule

A portable remainder requires either SHIFT or CORE to defeat both primary
controls in at least seven of ten X rows, with a coherent semantic-axis pattern.
Otherwise the family remains `WHOLE_ONLY`.

The executed result is `WHOLE_ONLY`. Standalone `dal` retains its short
provenance-bound whole reading. Every one of the 107 observed surfaces still
receives a nonempty concrete display: 37 explicit overrides, 46 reader-exact
singleton fallbacks and 24 raw-only fallbacks. The shared
`MATERIAL|MEASURE|LEVEL_I` display prior is one C0 editorial policy, not 107
independent discoveries. No new renderer licence or component export follows.

Confidence values are editorial evidence weights based on recurrence,
reader-exactness, inherited whole-card lineage and counterevidence. They are
not calibrated probabilities or model similarities.

Ceiling: C2 observed current-reader complete-word boundaries; C1 formal DAL
family and the provenance-bound bare whole; C0 concrete German whole displays
and transfer hypotheses. No plaintext, language, phonetic value, EVA character
value, named substance, free substring, unseen form, new page, image, OCR,
transcription, `f84` or `f84r`.
