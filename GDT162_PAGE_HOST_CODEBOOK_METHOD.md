# GDT162 — short PAGE_HOST lexical-address/codebook architecture

Status: `METHOD_AND_ANALYSIS_FAMILY_FROZEN_BEFORE_SCORING`

## Question

GDT160 found unusually broad specific LEFT×RIGHT compatibility, while GDT161
found that the graph does not collapse into a small stable inventory of
operation classes.  GDT162 moves the unit of analysis inward.  It asks whether
the already frozen HPR2 `PAGE_HOST` strings behave like a compact inventory of
short, recurrent lexical addresses or code identities, especially at lengths
two and three, rather than like internally productive morphology.

This is exploratory formal hypothesis testing.  `lexical-address/codebook` is
an architecture label, not a claim that a host is a word, lexeme, number,
meaning, sound, plaintext, or translation.

## Frozen source and host definition

The sole Voynich row source is the published
`gdt062_right_family_inventory.tsv`.  Its `page_host` column is the frozen HPR2
representation generated before this experiment.  GDT162 does not refit the
HPR2 parser or change its licensed O/OT inventory.

All rows whose page or locus begins `f84` are rejected before retention.  In
particular no f84r row is present in the actual input, and no f84r image,
transcription, formal row, or result is opened, queried, retained, joined, or
scored.

The primary candidate inventory contains PAGE_HOST strings of exactly two or
three HPR2 display characters.  All host lengths are reported so that this
choice cannot hide the full distribution.  A “glyph” below means one character
in this frozen HPR2 display representation; it is not a new paleographic or
phonetic segmentation.

Outer material stays separate from the candidate code:

- LEFT/context fields: `wrapper`, `inner_d`, `local_frame`;
- RIGHT/context fields: `right_family`, `dy_closure`, `b3`;
- nuisance fields: section, Currier, hand, host length, and within-line
  position quartile.

No outer field is concatenated into PAGE_HOST, and no raw whole token is
allowed to define a host identity.  Raw source-display tokens are retained only
as an internal, unstripped comparison.

## Frozen descriptive tests

### T1 — length concentration and recurrence

Report token- and type-weighted host-length distributions, Shannon/effective
vocabulary size, the mass at lengths 2–3, recurrent-token coverage, and
cross-folio recurrent-token coverage.  Compare PAGE_HOST with the unstripped
raw group on exactly the same rows and with the frozen GDT159 diplomatic
graphematic controls.  Historical forms are surface controls; HPR2 is not
retrofit to Latin or Portuguese.

### T2 — positional inventory and slot dependence

For length 2 and length 3 separately, report each position's glyph inventory,
entropy, normalized entropy, pairwise mutual information, and total correlation
`sum H(position) - H(whole host)`, both type-weighted and token-weighted.

### T3 — one-glyph-neighbor geometry

Build the equal-length Hamming-distance-one graph over distinct 2–3-character
hosts.  Report edge density, degree, isolates, connected components, largest
component, and substitution-class support `(length, position, a↔b)`.  No edge
is called a morpheme or sound change.

### T4 — identity versus neighbor context transfer

Leave one physical folio out.  For each held occurrence, predict each outer
context component from:

1. a nuisance model using section, Currier, hand, host length, and position;
2. exact PAGE_HOST identity with nuisance backoff;
3. equal-length one-glyph PAGE_HOST neighbors with nuisance backoff.

All counts and smoothing are learned from training folios only.  The primary
summary is total held log-loss across wrapper, inner-D, frame, right-family,
DY, and B3.  Exact-host gain with absent/negative neighbor gain is a
codebook-like lead; positive neighbor gain is evidence for transferable
internal host structure.  Results are also reported by component, section,
and leave-one-section-out sensitivity.  The test concerns formal context, not
external semantics.

### T5 — substitution-class context coherence

For recurrent Hamming-one edges, represent each host by its outer-context
frequency vector.  Compare endpoint similarity with frequency-matched
non-neighbor hosts and compare the direction of context changes among edges
sharing the same substitution class.  Repeated spelling substitutions whose
context deltas do not align are counted against productive internal
morphology; they remain compatible with independent code identities.

## Nulls

Use 1,024 deterministic shared worlds.

1. `LENGTH_UNIGRAM`: keep every host identity, its occurrence frequency, and
   length fixed, but shuffle the complete glyph multiset among type slots.
2. `POSITION_PRESERVING`: keep every host identity/frequency/length and each
   position's glyph multiset fixed, but independently shuffle glyphs among
   type identities at each position.
3. `CONTEXT_IDENTITY`: within exact host length × section × Currier × hand,
   permute host identities among occurrences.  This preserves the declared
   nuisance strata while breaking finer page/line/compiler association.

Generated strings may collide.  Identities remain separate nodes, and the
collision count is reported; this avoids silently conditioning the null on an
injective codebook.  Exact inclusive local p-values and max-family p-values are
reported for the predeclared metric family.  The nulls quantify surprise; in
this YOLO discovery pass they rank evidence rather than impose automatic kill
gates.

## Historical graphematic controls

Use the five already frozen GDT159 surface-only diplomatic corpora without
phoneme maps, expansions, translations, or lemmas.  Apply the same Unicode-NFC
character, length, positional-entropy, recurrence, and Hamming-neighbor
calculations.  The three 12,000/matched-or-near-matched Latin panels are the
primary controls; iForal and the late-fifteenth-century apothecary panel remain
visible low-capacity sensitivities.  Different scripts and transcription
practices are an explicit limitation, so normalized measures and ranks matter
more than raw character identities.

## Interpretation rules

- `SHORT_HOST_CODEBOOK_ARCHITECTURE_INTERESTING` requires concentrated 2–3
  length, recurrent exact identities across folios, exact-host held-context
  gain, and no comparable neighbor-transfer gain.  It is still exploratory.
- `SHORT_HOST_INTERNAL_PRODUCTIVITY_INTERESTING` requires neighbor-transfer
  gain and coherent repeated substitution classes above the position-preserved
  null.
- `MIXED_SHORT_HOST_CODEBOOK_AND_INTERNAL_STRUCTURE` applies if both sets of
  evidence are positive.
- `SHORT_HOST_CODEBOOK_NOT_DISTINGUISHED` applies if neither architecture is
  distinguished from nulls and historical controls.

The existing negative controls remain binding: GDT003 did not beat string
statistics, GDT123 found no globally surviving exact-host visual codeword,
and GDT161 found no small stable operation-class inventory.  GDT162 cannot
override them with an internal formal statistic.

## Claim ceiling

At most GDT162 can identify a short recurrent formal-address architecture and
distinguish exact-identity behavior from one-glyph-neighbor transfer.  It
cannot establish a word boundary, lexical item, morpheme, phoneme, language,
semantic role, meaning, plaintext, or translation.
