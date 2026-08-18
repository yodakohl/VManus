# GDT326 — held-folio host×coordinate composition

## Question

Does an opaque PAGE_HOST carry a reusable distribution over the five renderer
coordinate dimensions strongly enough to predict a **new full coordinate
combination** on an unseen physical folio? A positive result would support a
separable payload-plus-compiler architecture. A failure would favor the joint
host×coordinate tuple as the operative code unit.

## Frozen prospective panel

For each leave-one-physical-folio-out fold, retain a target event only when:

- its exact PAGE_HOST occurs in training;
- its exact five-field coordinate occurs somewhere in training;
- the exact PAGE_HOST×coordinate edge does **not** occur in training.

This mechanical criterion yields 315 events on 76 held folios. The target
coordinate and all five target components are withheld from the frozen panel.
PAGE_HOST is an opaque ID; no glyph or substring is used.

## Fixed models

The coordinate universe is the 32 exact coordinates present in training.
Using Dirichlet-1/2 counts learned separately in each held-folio fold, compare:

1. `REGISTER_TABLE`: full-coordinate counts for the target register;
2. `HOST_TABLE`: full-coordinate counts for the target opaque host;
3. `HOST_FACTORIAL`: product of that host's five separately normalized
   component distributions, renormalized over the 32 training coordinates;
4. `HOST_FACTORIAL_REGISTER`: normalized
   `log P(HOST_FACTORIAL)+log P(REGISTER_TABLE)-log P(GLOBAL_TABLE)`.

No rank, embedding, cluster, glyph feature, parameter, or smoothing value is
tuned. Score exact held coordinate log loss and top-1/top-3. Give each of the
76 held folios equal primary weight and report event-weighted sensitivity.
Charge each nonbaseline model by a fixed two-bit selector.

Use 8,192 fixed-prediction worlds that permute complete target coordinates
inside held physical folios, preserving the folio's coordinate multiset and
all target hosts. Max-correct over four models. Singleton folios are immobile
and remain explicit. The diagnostic does not refit models.

Call `OPAQUE_HOST_COORDINATES_COMPOSE` only if
`HOST_FACTORIAL_REGISTER` has positive selector-paid folio-equivalent gain,
beats both `REGISTER_TABLE` and `HOST_TABLE`, improves at least 50/76 powered
folios, and max-four p≤.05. Otherwise call
`HOST_COORDINATE_TUPLE_REMAINS_LEXICALIZED`.

This tests formal factorization only. It does not make PAGE_HOST a word or
assign a morpheme, category, meaning, sound, language, plaintext, or
translation. No f84 row may be opened, parsed, retained, joined, or scored.
