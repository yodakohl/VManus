# GDT339 method — comparator-first semantic incidence invariants

Date: 2026-08-18

Status: `COMPARATOR_DESIGN_FROZEN_BEFORE_SCORING`

## Question

Can a semantic class remain recoverable when every lexical form is replaced by
an opaque exact ID and only unordered record incidence is retained? If a fixed
incidence instrument transfers across readable held collections, does the same
instrument induce stable anonymous classes for exact GDT327 joint tuples on
held Voynich folios?

This does not reopen phase, PAGE_HOST, substring, visual-role, external-gloss,
or tuple-merging routes. A joint tuple remains an indivisible opaque ID.

## Comparator-first chronology

Stage A uses no Voynich target row or outcome. It scores two readable,
provenance-frozen comparator tasks:

1. six CoReMA recipe collections, with the five explicit editor roles already
   frozen by GDT176;
2. four Nuremberg letter books, with token occurrences assigned only to the
   source's regularized `addressee`, `content`, or other-section divisions
   already exported by GDT155.

All comparator word forms are Unicode-normalized, lowercased, replaced with
SHA-256-derived IDs, and then discarded. CoReMA uses the already-published
opaque IDs. The two corpora have separate classifiers and class vocabularies;
the tested invariant is the shared structural feature family, not a forced
cross-corpus role dictionary. Ste1 has only two records and no powered role
contrast, so it is provenance evidence but not a scoring fold.

The selected feature family, CoReMA coefficient matrix, normalization, class
order, and decision gates must be written to a hash-bound invariant freeze and
published before Stage B reads GDT327.

## Permitted observation

Each occurrence supplies only:

- opaque exact type ID;
- unordered record membership;
- collection/book membership for held-collection splitting;
- grammar/editor-derived unit boundary;
- recurrence of that type across records and collections;
- unordered co-occurrence/hypergraph relations.

Forbidden predictors are token characters, token length or shape, language,
raw position, unit ordinal, relative position, previous/next token, local
sequence, editor English label, concept string, Voynich wrapper, PAGE_HOST,
compiler coordinate, and every semantic/visual annotation on the Voynich side.

## Frozen feature family

All features are computed from the training collections only. Record partners
are summarized into 64 fixed SHA-256 bins, preventing lexical identity or a
corpus-specific partner vocabulary from entering the transferred feature
dimension.

Three predeclared transferable models are compared:

1. `FREQUENCY_DEGREE`: occurrence count, record frequency, within-record
   multiplicity, and mean record hyperedge degree;
2. `TOPOLOGY_ONLY`: repeated-record fraction, record-degree dispersion,
   partner-bin occupancy/entropy/concentration, mean partner document
   frequency, and collection dispersion;
3. `FULL_INCIDENCE`: the union of the first two.

`UNIFORM_PRIOR` is the no-information baseline. `OPAQUE_ID_LOOKUP` is a strong
training-role lookup ceiling but cannot transfer to a new ID namespace and is
therefore ineligible for selection. Models are class-balanced multinomial
ridge classifiers with fixed optimizer, smoothing, and deterministic
per-collection/class cap. Each outer fold holds one entire CoReMA collection or
Nuremberg book. No hyperparameter is selected on a held collection.

Stage A selects the transferable model with the smallest summed balanced held
log loss, with lexical tie-break by model name. Charge `log2(3)` bits to that
choice. Use 2,048 fixed-prediction, within-held-collection label permutations
and a max-three statistic. The invariant is comparator-supported only if it:

- beats `UNIFORM_PRIOR` in both comparator tasks;
- beats `FREQUENCY_DEGREE` in both tasks unless it is itself that baseline;
- is positive against uniform in at least 8/10 held collections/books;
- retains positive selector-paid aggregate gain;
- has max-three diagnostic p <= .05.

## Stage B — unchanged Voynich application

Only after the invariant freeze is public, load the f84-free GDT327
interlinear with `GuardedTSV`. Treat `joint_tuple_id` as the opaque type,
`(page, record_ordinal)` as the unordered record hyperedge, and GDT327 field
membership only as an audit boundary. Do not use any other GDT327 column as a
predictor.

Hold out each physical folio. For every exact tuple occurring in at least two
training folios and at least two records in the held folio:

1. compute its frozen feature vector from non-held folios only and assign the
   frozen CoReMA class probabilities, exported only as `C0..C4`;
2. define its unordered held partner set as the other exact tuple IDs sharing
   any held record hyperedge;
3. score how many held partners were already partners of that tuple in the
   non-held folios.

This is a prospective cross-folio partner-incidence test, not semantic
accuracy. Within each outer fold, training-folio pseudo-holdouts estimate a
Jeffreys-smoothed `REGISTER_FREQUENCY` partner-recurrence probability. The
candidate adds only the frozen anonymous comparator class, shrunk by eight
baseline pseudo-trials. `EXACT_TUPLE` adds the exact tuple ID with the same
shrinkage and is the strong namespace-specific ceiling. Frequency bins are
fixed at 2--3, 4--7, 8--15 and 16+ non-held occurrences.

Report coverage, held partner trials/hits, binomial codelength, folio/register
breakdown, and 8,192 fixed-prediction class-probability permutations within
register×training-frequency bin. Require at least 100 tuple-fold tests, 20
folios, three registers, candidate gain above `REGISTER_FREQUENCY` in at least
60% of folio folds, positive one-bit-paid total gain, and max-family p <= .05.
Otherwise stop. Because comparator failure would invalidate the semantic
instrument regardless of the Voynich diagnostic, the final support decision
is conjunctive with the Stage A comparator gates.

## Claim ceiling

At most GDT339 may establish that one comparator-calibrated anonymous incidence
class is stable for exact opaque joint tuples across held folios. It may not
merge tuple IDs or assign a comparator role, Voynich role, word, morpheme,
meaning, sound, language, plaintext, translation, diagram identity, or
external referent. f84 is forbidden and must not be opened, parsed, retained,
joined, or scored.
