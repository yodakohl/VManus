# GDT808 method

## Question

Do the `Xol→Xeol` and `Xedy→Xeody` changes each transfer across unseen carrier
families after paragraph topic, distant formula, and form/register information
are modelled separately; and do their held contextual directions behave as one
shared expanded-side relation or as two different relations?

## Inputs

The experiment reuses the inherited 179-selector allow-list and the same three
cached transcription views as GDT807.  Mixed line, token, and cross-reader TSVs
are materialised only through `./vmanus-exp query-tsv` with explicit selector
allow-values and requested columns.  The selector is rejected before any
other field is retained.  No new image or page is opened; `f84` and `f84r` are
forbidden.

The strict paragraph builder, physical-folio normalisation, rank-stability,
and exact LCS procedures are replayed from source rather than trusted from a
derived score file.  Historical sources are topology comparators only.

## Method

### Exact four-cell relation

Every observed exact ZL3b surface is parsed once by the first eligible suffix
in the longest-first order `eody`, `eol`, `edy`, `ol`; the remainder must be a
nonempty carrier `X`.  A carrier is complete when all four exact surfaces
exist.  The two axes and side labels are:

| axis | positive expanded side | negative base side |
|---|---|---|
| `L` | `Xeol` | `Xol` |
| `DY` | `Xeody` | `Xedy` |

`ALL28` contains the 28 carriers with at least one rank-stable occurrence in
each cell.  `CORE13` requires at least three rank-stable occurrences on three
physical folios in every cell.  The fixed CORE13 carriers are `ch`, `cth`,
`k`, `kch`, `ok`, `ot`, `pch`, `qok`, `qot`, `sh`, `t`, `tch`, and `yt`.
These are analyst partitions of complete surfaces, not exported morphemes.

### Focal events and Q152

A primary event must lie in one of the 665 strictly closed paragraphs, be
rank-stable in ZL3b/IT2a/RF1b, possess a unique-forced exact LCS position in
both alternate readings, and be the sole occurrence of its own four-surface
family on the focal physical line.  Multiple other carrier families may occur
on that line, but their identities are masked.  The expected CORE13 event
census is 1,777: 641 `ol`, 273 `eol`, 715 `edy`, and 148 `eody` events.

The exact Q152 quarantine is constructed mechanically from 35 raw-complete
four-cell carriers (140 surfaces) plus the eighteen surfaces in nine thin
`Xkol/Xtal` pairs, minus six overlaps.  Quarantine is by complete surface only;
it never exports a substring rule.  An ED1 sensitivity additionally removes
feature surfaces within Levenshtein distance one of Q152, but cannot replace
the primary exact-whole view.

Rank stability is occurrence-based: the occurrence rank of a surface in the
ZL3b line must not exceed the minimum count of that same complete surface in
the ZL3b, IT2a, and RF1b readings.  The own-family singleton rule counts all
raw ZL3b tokens, not only stable ones.  Physical folio is the regex capture
`^(f\d+[rv])`.  For each alternate reading, the exact-token LCS optimum is
recomputed with and without the focal reference position; a position is
unique-forced only when removing it lowers the optimum and exactly one equal
alternate token can participate in an optimum alignment.

### Four disjoint feature decks

All features are namespaced by deck and rebuilt inside each training fold.
No page, locus, carrier, target tail, focal target identity, or feature derived
from the focal spelling is emitted.

1. `TOPIC`: binary exact-whole presence in the other lines of the strict paragraph.
   Lines containing another member of the focal carrier family are removed;
   Q152 tokens are then deleted.
2. `TEMPLATE`: binary exact-whole presence on the focal line outside radius
   two, in the fixed signed bins `L3`, `L4`, `L5PLUS`, `R3`, `R4`, and
   `R5PLUS`.  Q152 is deleted.
3. `FORM_REGIME`: section, language, hand, their joint cell, target-free
   line/paragraph length bins, relative line location, focal-hole
   FIRST/MIDDLE/LAST/SINGLE geometry, forward/reverse index and quartile, and
   target-free word length/end-class histograms.  Q152 counts, anonymous mask
   status, boundary status, and unstable-neighbour status are omitted from
   this primary deck and emitted only in `MASK_STATUS_AUDIT`.
4. `SLOT_HOLE`: only exact stable `L2/L1/R1/R2` neighbour identities and their
   ordered brackets.  Q152 neighbours are omitted completely rather than
   replaced by a relation-density marker.  Boundaries and unstable-neighbour
   status remain audit-only.  A raw-neighbour version is a sensitivity only.

A deck feature enters a training vocabulary only when it occurs on at least
two training carriers and two training physical folios.  Each event supplies
binary feature presence.  Per-deck multinomial naive Bayes uses alpha 0.5,
equal class priors, and equal total weight for every training
`carrier × class` cell.  Its event score is the mean known-feature log
likelihood ratio; an all-OOV event scores zero.

All length bins are `floor(log2(n+1))`.  Paragraph-line and focal-token
quartiles are `min(4, 1 + floor(4*(index-1)/count))`.  Forward and reverse
focal indices use `1`, `2`, `3`, `4`, `5PLUS`; word lengths use `1` through
`6`, `7PLUS`, and every end-character count is bucketed `0`, `1`, `2`,
`3PLUS`.

The implementation reports every deck alone.  The fixed nuisance score is the
sum of `TOPIC`, `TEMPLATE`, and `FORM_REGIME`; the augmented score adds
`SLOT_HOLE`.  This equal-deck stack has no tuned coefficient.  No fitted
stacker or post-score sign flip can rescue the fixed primary result.  A
required `UNION_MNB_SCORER` sensitivity instead pools all namespaced binary
features into one alpha-0.5 model.  If its local gain is nonpositive, a primary
local pass is downgraded to `SCORER_SENSITIVE_LOCAL_LEAD`.

### Component- and folio-held transfer

For each target cell `(carrier X, physical folio F)`, training excludes every
event with `carrier == X` or `physical_folio == F`.  The primary portable-
relation tests are `L_TO_L` and `DY_TO_DY`: train on the same formal change in
other carriers and test it on the held carrier.  The cross-axis `L_TO_DY` and
`DY_TO_L` tests decide whether the two changes share a direction, oppose one
another, or are unrelated.  Predictions are scored as micro AUC,
carrier-macro AUC, balanced accuracy with tied zero votes, log loss, and
within-carrier conditional concordance.  The conditional score compares only
positive/negative event pairs inside the same held
`carrier × section × language × hand × target-free-length-bin` cell, so a
local claim cannot be purchased by Currier/register separation.  Every
paragraph and occurrence remains auditable.

Twenty-four deterministic target-label rotations accompany the primary local
result.  On the already held predictions, complete labels are cyclically
rotated inside fixed `axis × carrier × section × language × hand ×
target-free-line-length-bin` strata after sorting by page, numeric line,
token index, and event id.  Offset `k` is `k mod n`; singleton and
divisor-aligned strata remain unchanged.  Scores, nuisance, SLOT packets,
events, folds, and vocabularies do not move.  This preserves label counts and
cannot import a donor carrier or folio into a fold.  Ties count against the
target and moved/identity labels are printed.

A separate twelve-member portability null reverses source-axis labels for a
cyclic consecutive block of six of the twelve available training carriers,
sorted lexically for each held carrier.  Repetition `r=0..11` begins the block
at `r`; models are rebuilt, while target labels remain real.  The local-gain
rank is `1 + count(rotated_gain >= observed_gain)` among the 24 target-label
rotations.  The nuisance-portability rank is separately
`1 + count(carrier_null_auc >= observed_auc)` among twelve carrier nulls.
Unmoved strata and ties count against the target.  `Xkol/Xtal` and learned-whole
`cheol/otal` tracks are descriptive calibrations, not substitutes for the
four-cell test.

### Historical topology orientation

The held result is compared with six period-attested record roles:
`QUALITY_DEGREE`, `PART_FORM_SCOPE`, `GROUP_DOSE`, `UNIT_VALUE`,
`RELATION_SUBSTITUTE`, and `RECORD_CHANNEL`.  A seventh
`BREVIGRAPH_OR_ORTHOGRAPHY` rival is the historical null.  Observable
signatures—local versus distant gain, multi-head grouping, amount contacts,
position, section transfer, reader stability, and e-run ladders—rank these
rivals.  Historical sources can orient a role topology but never assign a
Voynich spelling.

## Decision rule and claim ceiling

For each primary within-axis relation, `PORTABLE_LOCAL_SLOT_RELATION` requires
CORE13 augmented carrier-macro AUC at least 0.60, at least 0.02 gain over
nuisance, positive fixed-score log-loss gain, neighbour-only AUC above 0.50 on
at least nine of thirteen carriers, conditional augmented-minus-nuisance AUC
gain at least 0.02, and gain rank exactly one of 25 against the 24 target-label
nulls.  Its ALL28 sensitivity must reach macro AUC 0.55 with positive gain,
and the union-MNB local gain must also be positive.  A relation satisfying the
direction and gain gates but ranking second or third, or failing only the
union scorer, is retained as `PROVISIONAL_OR_SCORER_SENSITIVE_LOCAL_LEAD`.
A relation with nuisance carrier-macro AUC at least
0.60, nuisance AUC above 0.50 on at least nine carriers, ALL28 nuisance macro
AUC at least 0.55, and nuisance-portability rank no worse than three of
thirteen but no local increment is
retained as `PORTABLE_RECORD_OR_FORM_RELATION`; it is not discarded or
mislabeled as a local morpheme.

If both within-axis relations transfer and both cross-axis local-neighbour
directions are at least 0.60, the joint topology is
`SHARED_EXPANDED_SIDE_DIRECTION`.  Cross-axis inversion confined to nuisance
features is `OPPOSED_REGISTER_DIRECTIONS__NO_SHARED_SLOT_INFERENCE`, not an
opposite semantic operator.  Only inversion of both neighbour-only directions
at or below 0.40 may be called `OPPOSED_LOCAL_RELATIONS`.  Mixed cross-axis
behavior yields `TWO_DISTINCT_OR_AXIS_BOUND_RELATIONS`.  A single transferable
within-axis relation remains an explicit one-axis lead.  Otherwise the output
is `NO_PORTABLE_RELATION_SIGNAL`.  Failure of a promotion gate does not erase
the ranked working rival; it remains explicit until a better model replaces
it or an observation makes it impossible.

At its ceiling GDT808 may select a reusable formal side relation and a
replaceable historical role-family lead.  It cannot establish a lexeme,
plaintext, language, cipher, sound, glyph value, EVA component meaning,
ingredient, preparation, quality, plant part, disease, cure, patient,
container, unit, number, renderer patch, or translation.
