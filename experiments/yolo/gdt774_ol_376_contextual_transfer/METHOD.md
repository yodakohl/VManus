# GDT774 method — contextual transfer, nominal fallback, and structural audit

## Question and scope

How much of GDT773's fifteen-case `ol` renderer can be predicted over all 376
reader-exact cached occurrences from observable context, without using the
case identity? The experiment must give every occurrence a working output,
while distinguishing a context-specific output from the nominal fallback.

No page, image, OCR, or transcription is newly opened. The 376 positions are
the exact `ol` subset of GDT769's fixed 526-target atlas. The 98 page selectors
and 61 physical folios describe that inherited cache, not a claim of new visual
inspection. `f84` and `f84r` remain forbidden.

## Inputs and safe loading

The core inputs are GDT769's exact target and frame atlases, GDT760's amount
span boundaries, GDT762's sixteen amount contacts, GDT763's slot dispatch,
GDT773's fifteen selected outputs, and GDT683's legacy `Grundansatz` crosswalk.
The structural supplement also uses the guarded exact-slot provider inherited
through GDT769/GDT764 and GDT771's strict-left atlas.

`SOURCE_LOCK.tsv` fixes every direct input by path and hash. GDT683 occurrence
and adjacent-pair artifacts, and the GDT771 relation subset, are treated as
mixed sources: the runner requests only explicit columns for the 98 already
selected GDT769 page values through `./vmanus-exp query-tsv`. The selector is
rejected before the remainder of an unapproved row is materialized. Hashing a
locked file does not parse its rows.

## Automatic transfer policy

Rules are applied in the following order. A position is consumed by the first
matching rule.

1. A selected amount expression immediately left of `ol`, provided `ol` is not
   line-final, emits the content-field head `Ansatz:`.
2. `ol` immediately left of a selected amount expression emits the quantity
   head `Menge:`.
3. A direct PROCESS or `oly` anchor to the right emits `und dann`.
4. A direct CLOSE anchor to the left emits the field boundary `;`.
5. A direct CLOSE anchor to the right is an explicit nominal veto: it emits
   `Ansatz-/Zubereitungsposten` and prevents the broader state rule from firing.
6. A GDT769 F15 state-transition bridge that is also an F14 medial two-sided
   locus emits the coordination default `und`.
7. Everything else emits the nominal whole-form fallback
   `Ansatz-/Zubereitungsposten`.

The close-right veto matters. Three F15 positions have CLOSE on the right; one
was already consumed by an amount rule, and the other two reduce the state
branch from 29 to 27. F14 alone, line position alone, PROCESS on the left, and
repetition alone have no contextual licence.

The sixteen amount-contact rows expand to seventeen `ol` edges because
`ol s aiin ol` contributes one edge on each side. Five left-of-amount edges
emit `Menge:`. Twelve right-of-amount edges could emit `Ansatz:`, but two are
line-final and are excluded as dangling field heads. The audit retains the
original phrase licence, the GDT763 slot class, the exclusion, and the
bilateral ambiguity for every edge.

## Automatic versus hybrid renderer

The automatic renderer never copies a GDT773 case output by ID. Its replay over
the fifteen calibration positions is therefore a portability check. It matches
nine outputs and sends six unsupported case-specific field choices back to the
nominal fallback.

The hybrid renderer has a different practical purpose. It first copies all
fifteen fixed GDT773 outputs, including their six nonportable choices, then
uses the automatic policy on the other 361 positions. The automatic result is
the evidence-bearing transfer measurement; the hybrid is the current display
layer. Their counts and rules are published separately at every occurrence.

## Repetition, register, and structural nulls

The companion `structural_audit.py` reconstructs 24,090 reader-exact slots
through GDT769's guarded provider and runs three deterministic 20,000-draw
comparisons:

- N01 fixes each physical folio's `ol` count and samples from that folio's
  exact slots, measuring line position, paragraph boundary, same-line pairs,
  and physical adjacency;
- N02 fixes physical folio and FIRST/MIDDLE/LAST counts, then measures distinct
  left followers, right followers, and complete neighbor frames;
- N03 fixes section, language, and hand counts, then measures same-line and
  adjacent repetition.

Seeds are 776, 778, and 774. Sampling is without replacement inside every
stratum. Quantiles use `sorted[floor(p*(N-1))]`; tail probabilities use the
add-one empirical estimate. The output also contains all 61 leave-one-physical-
folio summaries, section/hand splits, repeated-line records, and exact neighbor
surface counts.

These are exploratory structural controls, not lexical tests. In particular,
the concentrated right follower inventory is compatible both with a nominal
head taking a complement and with a bound field operator.

## Manual contrast audit and legacy comparison

The fixed 24-row contrast table contains amount direction, PROCESS direction,
CLOSE direction, state bridge, repeated `ol`, line-edge, and signalless-medial
examples. It checks that the implementation follows the intended rule and
veto. Since the cases were selected to expose those branches, a 24/24 match is
not independent semantic evidence and receives zero score credit.

All 376 positions crosswalk to GDT683's `Grundansatz`, but all use the same
inherited GDT664 learned-whole evidence type. GDT774 therefore does not count
them as 376 confirmations. It preserves a weaker nominal fallback and replaces
only positions with an explicit contextual rule.

## Output and claim ceiling

`OL_376_TRANSFER_ATLAS.tsv` is the canonical occurrence table. It records raw
direct signatures, every boolean transfer signal, precedence result, automatic
output, hybrid output, calibration status, repetition geometry, legacy source,
confidence, and zero-credit fields. The working dictionary lists each output
with positive evidence, counterevidence, scope, and occurrence count.

GDT774 may select a replaceable complete-whole renderer and say which cached
contexts distinguish its field functions. It may not identify `ol` as a
specific substance, oil, water, wine, unit, operation, part of speech, sound,
glyph value, or historical word. Confirmed lexemes, plaintext clauses, and
component exports remain zero. The independent validator reconstructs the
dispatch and amount edges, checks all summaries and credit fields, and
byte-replays the 24 runner outputs plus report in 28,954 checks.
