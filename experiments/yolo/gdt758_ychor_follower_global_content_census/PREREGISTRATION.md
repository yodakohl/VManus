# GDT758 preregistration

## Target

Audit all admitted reader-exact occurrences of the eleven direct `ychor`
followers and revise the complete-form working dictionary without using EVA
letters as Latin initials.

## Candidate ordering fixed for the pass

| whole | primary candidate | two principal rivals |
|---|---|---|
| `chor` | Pflanzenteil, probably flower/seed head | unspecified plant part; dry/state marker |
| `chshoty` | cold dry preparation | cool and dry; soaked preparation |
| `cthy` | leaf drug | aerial herb; unspecified plant part |
| `oky` | first heat stage | heat first; hot preparation |
| `qokchol` | heated and dried | hot-dry state; heated dry preparation |
| `s` | each / in equal parts | drachm sign; ounce sign |
| `ar` | part / share | portion; amount/ratio term |
| `odol` | measured preparation | one dose; measure the preparation |
| `ols` | strained final product | strain; oil/oily preparation |
| `sheol` | moist / soaked | moist preparation; water/wine preparation |
| `chol` | dry / dried | dry matter; dry as an imperative |

The detailed German forms, positive evidence and counterevidence are fixed in
`src/FOLLOWER_CANDIDATE_PRIORS.tsv`. Eight exact observed span hypotheses are
fixed separately in `src/YCHOR_EXACT_SPAN_RENDER_RULES.tsv`.

## Expected discriminators

- `s` should behave as a quantity introducer if its exact right neighbors are
  strongly enriched for the ordered-value family; it need not be unique.
- `cthy` should retain the earlier leaf-drug lead if its Herbal concentration
  survives the current guarded cache.
- `chol`, `qokchol` and `sheol` should retain dry, hot-dry and moist axes while
  losing unsupported carrier nouns.
- `ar` should retain part/share but lose the unsupported ordinal "first."
- `ols` and `chshoty` are allowed to remain C0 because their sparse evidence
  does not justify removing a still-possible concrete default.

## Output boundary

The output is an exploratory working dictionary and renderer. No candidate is
a confirmed word or translation. Historical expressions provide register and
functional comparators only; target spelling is never matched to Latin.
