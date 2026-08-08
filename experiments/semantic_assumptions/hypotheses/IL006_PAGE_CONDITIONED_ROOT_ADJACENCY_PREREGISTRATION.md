# IL006 — page-conditioned cross-root adjacency

Registered: 2026-08-06, after IL005's final result and after a training-only
crossfit/power audit, but before any bucket-1 or bucket-0 adjacency score.

## Question and new invariant

IL002/IL005 now describe an order-free exact-root inventory at page scale. Are
roots nevertheless assembled nonrandomly into adjacent positions inside
physical lines?

A pure page-palette process predicts that root labels are exchangeable after
page inventory, exact root-free form, position, entry state, and D/C position
membership are fixed. A structured utterance, procedure, or record predicts
stable cross-root adjacency beyond that conditional null.

This is not IL004's page-level D-set to C-set retrieval. It reuses the same
fixed smoothing constants but learns only immediately adjacent cross-partition
edges and tests them against within-page label permutations.

## Inputs, partitions, and split

- Manual ZL3b is primary; IT2a/RF1b are sensitivity readings only.
- Physical prose-line order and manual metadata come from the locked parser and
  `transcription/voynich_zl3b_lines.tsv`. No OCR, image evidence, embedding,
  dictionary, plaintext, or proposed gloss is permitted.
- Root eligibility, training-line IDF, and D/C assignment are exactly IL003's:
  at least five ZL training-line occurrences and the low SHA256 bit under
  `IL003-ROOT|`. The IDF map binds the eligible inventory and provenance; the
  edge/page score itself is unweighted exactly as specified below.
- Buckets 2--4 train the frozen table. Bucket 1 validates the instrument; fixed
  bucket 0 decides once. Prior aggregate exposure of bucket 0 did not score
  this adjacency invariant.

The disclosed training-only crossfit trained on buckets 3--4 and evaluated
bucket 2. On 23 eligible pages, observed adjacency exceeded the conditional
null by +0.0391 bit/edge with 78.3% positive pages. A 10%-swap greedy plant
added +0.1052 bit/edge with 100% positive pages. These values set no manuscript
outcome and cannot be substituted for validation or final scores.

## Frozen orientation-aware count table

Only visibly adjacent parsed tokens on one physical line enter. An edge is
eligible when one root is in D and the other is in C. Both physical
orientations are retained:

- `DC`: D root on the left, C root on the right;
- `CD`: C root on the left, D root on the right.

For orientation `o`, let `g_o(c)` be the add-0.5 normalized training-edge
distribution over all eligible C roots. For each D root `d`:

`p_o(c|d) = (edges(o,d,c) + 8*g_o(c)) / (sum_c edges(o,d,c) + 8)`.

The edge distribution is `q_o(c|d) = 0.5*g_o(c) + 0.5*p_o(c|d)`, and its score
is `log2(q_o(c|d)/g_o(c))`. A page score is the unweighted mean over its
eligible edges. No parameter or pair subset is tuned.

## Page-conditioned root-label null

Within each physical page, D and C labels are permuted separately among token
positions sharing:

`(D/C partition, exact Currier/section/hand stratum, exact complete root-free
form shell, five-bin horizontal position, paragraph-opening status)`.

Thus every page keeps its complete D and C inventories, every position keeps
its partition membership and exact root-free form, and all eligible adjacency
locations/orientations remain fixed. Only which already-observed root occupies
a compatible position changes.

One deterministic draw is reserved as a negative pseudo-observation; the next
2,048 estimate each page's null mean. The page residual is observed score minus
null mean. Report the mean residual in bits/edge, positive-page fraction, page
sign-flip p, joint conditional-randomization p, their conservative maximum,
and a page bootstrap interval.

An evaluable page has at least ten eligible cross-partition edges and at least
six movable D positions and six movable C positions in variable cells.

## Validation gates

On bucket 1, all must pass before bucket 0 is scored:

1. at least 20 evaluated pages and at least 70% coverage among pages with ten
   eligible edges;
2. finite normalized orientation/global/conditional distributions,
   deterministic repeated results, unchanged cell margins, and unchanged
   root-free sequences;
3. a plant greedily taking the score-maximizing within-cell swap, with physical
   position ties, for at most `ceil(0.10 * movable_positions / 2)` swaps,
   increases mean score by at least 0.05 bit/edge, improves at least 80% of
   pages, and has one-sided page sign-flip `p <= 0.01`;
4. the reserved null pseudo-observation does not simultaneously reach residual
   >= 0.02 bit/edge, 60% positive pages, and conservative `p <= 0.01`.

Gate failure stops before bucket 0 and closes only this instrument.

## Held rule and interpretation

The ZL final result is material only if mean residual >= 0.02 bit/edge, at
least 60% of pages are positive, conservative `p <= 0.05`, primary coverage is
at least 70%, and IT2a/RF1b reuse at least 70% of the frozen ZL pages with the
same positive mean direction. Their p-values are not combined.

- Pass: adjacent root identities are non-exchangeable beyond page vocabulary,
  exact form, position, entry state, and stratum. This establishes structured
  line assembly and rejects a pure page-bag mechanism at this resolution.
- Fail: the frozen adjacency table does not reject page-palette exchangeability.

Neither outcome proves ordinary language, notation, generation, syntax labels,
POS, word meaning, cipher, pronunciation, or plaintext.

## Stop rule

One validation and one final evaluation are allowed. Rerunning requires new
permitted data or a genuinely different invariant, not a new orientation,
window, smoothing value, cell collapse, root partition, split, pair subset, or
threshold.
