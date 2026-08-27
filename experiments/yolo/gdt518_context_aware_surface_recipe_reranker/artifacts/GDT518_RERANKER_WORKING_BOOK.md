# GDT518 compact reranker working book

## Live result

- old-base targets: 159/159 current recipes generated;
- GDT517 order: 117 top-1, 157 top-5, rank sum 281, deepest rank 56;
- visible-form ridge + old rank: 133 top-1, 158 top-5, rank sum 213;
- selected form + neighbor model: 134 top-1, 158 top-5, rank sum 212,
  deepest rank 14;
- changes: 22 errors corrected, 5 correct defaults lost, 4 wrong defaults
  changed but remain wrong, 16 old errors unchanged;
- exact known event/surface recipes always retain precedence.

## Selected score

Input surface features are length and visible character uni-/bi-/trigram
counts. Target recipe features are atom counts and ordered adjacent atom-pair
counts. Ridge alpha is 10. Candidate `i` has:

`SSE(predicted recipe signature, candidate signature) + log(1+i)`

Add `0.05 * mean(add-10 bigram NLL, add-10 trigram NLL)` over ngrams touching
the candidate card. Fourteen non-prose target surfaces have zero context cost.

## What now looks stable

1. Whole-form and residual chunks are both needed to generate the candidate
   space.
2. Visible internal composition is much more informative than generic
   executability and more informative than thematic/register priors tried in
   the exploratory sweep.
3. Neighbor context is a tie-breaker, not a license to invent a new meaning.
4. Remaining errors cluster around `dy`, `ol/O+L`, swallowed `a/d/q`,
   `CH/SH/CHD`, and local-character anchors.
5. Structural recipes remain distinct from German working glosses.

## Next route

Build a monotone visible-anchor transducer. Give each structural atom a visible
anchor learned or inherited from its stem (`CH~ch`, `A_ADDR~a`, `D_ADDR~d`,
etc.), allow known shell letters to remain outside a portable core, and combine
its alignment cost with GDT518. Rehearse the weighting on old compositional
forms before making it the current thirty-page future compiler. Do not open a
new manuscript page for this step.
