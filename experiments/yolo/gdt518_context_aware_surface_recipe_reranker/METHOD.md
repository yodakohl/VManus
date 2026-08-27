# GDT518 method

## Question

Can visible surface structure and the immediately surrounding recipe cards
rerank the finite GDT517 candidate set more usefully than its evidence ordering
alone, without changing any already known thirty-page recipe?

## Inputs

- GDT407's 4,576 running events on the older twenty-six pages supply 1,558
  invariant surface/recipe types and 715 recipe statements.
- GDT516 supplies the 159 surfaces genuinely new to that base, their current
  recipes, and the selected prose statements in which they occur.
- GDT517 supplies the residual-closure compiler and its finite candidates.

No additional manuscript page is opened. `f84` and `f84r` remain forbidden.

## Method

### Visible-form decoder

Each old surface type receives one input vector containing visible length and
character unigram, bigram and trigram counts. Its output vector contains recipe
atom counts and ordered adjacent-atom-pair counts. A deterministic ridge model
with alpha 10 predicts the output signature of a new surface. Candidate cost is
the squared distance between predicted and candidate signatures.

GDT517's original order remains a prior rather than being discarded. Candidate
index `i`, counted from zero, contributes `log(1+i)`. The benchmark reranks the
first 100 finite candidates; every current target recipe lies within the first
56 before reranking.

### Neighbor correction

Old statements are rendered as atom tokens with `<S>`, `<C>` and `<E>` for
statement start, card boundary and statement end. Add-10 bigram and trigram
models score only windows touching the candidate card. When a surface has more
than one selected prose occurrence, costs are averaged. Non-prose surfaces
receive zero neighbor cost.

The selected score is:

`surface squared cost + log(1+i) + 0.05 * mean(bigram NLL, trigram NLL)`.

The parameter ladder is an exploratory workshop comparison on these same 159
surfaces; it is not presented as an unseen-page estimate. The executable CLI
rebuilds the analogous future model from all currently admitted thirty-page
running forms and accepts explicit left/right recipes.

## Decision rule and claim ceiling

Pass if all 159 current recipes remain in the finite candidate set and the
selected ordering improves both top-1 count and total rank relative to GDT517.
An exact event card or unique known surface/domain option always outranks the
reranker. The result is an exploratory structural working compiler only: it
does not confirm a lexeme, English meaning, plaintext, language, historical
codebook, or reading of an unopened page.
