# IL002 — matched line-pair root topology

Registered: 2026-08-06, after IL001 failed validation and before IL002 overlap
scores were computed on validation or held data.

## Question and genuinely different invariant

Do literal root inventories cluster (a) in immediately adjacent physical lines
beyond nonadjacent lines on the same page, or (b) in nonadjacent lines on the
same page beyond matched lines on other pages?

IL001's accumulating probability cache is retired. IL002 instead uses
pair-local, form-matched root-set overlap; it has no smoothing parameter and no
growing history. It assigns no meaning or manuscript-system identity.

## Inputs and split

- Manual ZL3b is primary; manual IT2a/RF1b are directional sensitivity only.
- The locked confirmed parser and conservative canonicalization are reused.
- Eligible rows are physical prose lines with Currier A/B and at least two
  parsed tokens.
- No OCR, image, visual model, embedding, AI label, dictionary, or proposed
  Voynich gloss may be loaded.
- Reuse IL001's untouched page split: SHA256 salt `IL001-2026-08-06|`, bucket
  0 final, bucket 1 validation, buckets 2–4 training. IL001 never scored bucket
  0.

## Frozen line representations

For each visible token, the target is its ordered normalized literal-root
tuple; its control is the ordered tuple of non-root form fields. Root types are
eligible only when they occur in at least five training lines. Each line is a
binary set of eligible root types and a binary set of exact form-shell types.

Root weights and form weights are fixed from training line document frequency:
`log((N_train_lines + 1) / (df + 1))`. Pair similarity is weighted Jaccard.
Lines with fewer than two eligible root types are excluded before pair making.

## Registered contrasts

### A — immediate adjacency

Targets are consecutive same-stratum lines on one page. Candidate controls are
line pairs at distance at least two on that same page and in the same
Currier/section/hand stratum. For every target pair choose the control pair
nearest in the frozen vector:

`(form-shell Jaccard, total token count, absolute token-count difference)`.

Distance is Euclidean after scaling count coordinates by training standard
deviations. Controls may be reused. The outcome is target root Jaccard minus
matched-control root Jaccard, averaged first within page and then over pages.

### B — remote same-page coherence

Targets are same-stratum line pairs at distance at least two on one page.
Candidate controls are pairs of lines from different pages but the same
Currier/section/hand stratum. Match with the identical frozen vector and
distance. Cross-page controls may be reused. The outcome is same-page root
Jaccard minus matched cross-page root Jaccard, again aggregated by page.

Matching reads forms and lengths only, never roots. Nearest-neighbor tie breaks
use stable lexical `(page, locus)` order.

## Gates and inference

Validation must pass before final scoring:

1. all splits and both contrasts contain eligible pages and pairs;
2. at least 80% of target pairs receive a control;
3. median absolute form-Jaccard mismatch is at most 0.05 and median total-length
   mismatch is at most two tokens;
4. replacing 10% of eligible validation roots with deterministic copies from
   the registered source (previous line for A; a nonadjacent same-page line for
   B) makes the intended contrast at least +0.005 Jaccard, at least 5% above
   its matched-control mean, and one-sided page sign-flip `p <= 0.01`;
5. shuffling validation line order within pages removes the planted A advantage.

Final raw p-values are one-sided sign flips of complete-page mean differences;
Holm correction covers A and B. A held effect is material only if its difference
is at least +0.005 Jaccard, at least 5% of the matched-control mean, adjusted
`p <= 0.05`, and IT2a/RF1b have the same sign. Report page bootstrap intervals.

- A material: exact roots carry adjacency-specific sequential information.
- B material without A: exact roots carry page-level topic/catalogue/mnemonic
  information without detected immediate sequencing.
- Both material: mixed sequential and page-level information.
- Neither material: these exact-root overlap invariants are uninformative; this
  does not establish generated text or close natural language, records, or
  mnemonics.

No result licenses English words, POS, sentences, language family, cipher, or a
claim that root similarity is semantic rather than another authorial register.

## Stop rule

One frozen final evaluation is allowed. Failure closes only these exact
form-matched weighted-Jaccard contrasts. Rerunning requires new permitted data
or a different invariant, not another weight, frequency cutoff, similarity,
matching tolerance, split, subset, or threshold.
