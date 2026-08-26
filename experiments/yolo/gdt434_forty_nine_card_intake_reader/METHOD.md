# GDT434 method

## Question

Can the 1,268 observed recipes, the 47 first-ring future cards, the two
second-ring cards, and the 246 narrow candidates be combined into one exact
matcher that never turns a similar German phrase into a false recipe match?

## Inputs

- GDT416: 1,268 observed recipes and their owner-local imperative clauses.
- GDT430: the complete 293-card prediction deck and rank boundaries.
- GDT431: 47 fixed future phrases and 235 register readings.
- GDT433: two Amber-II cards and ten register readings.
- GDT413: the unchanged 46-component working dictionary.

## Method

1. Index every observed or predicted recipe by its exact `+`-joined component
   sequence.
2. Apply the fixed priority order T0 observed, T1 high, T2 strong, T3
   second-ring amber, T4 narrow lookup, T5 no licensed recipe.
3. Put only T1–T3 in the 49-card main deck. Keep all T4 recipes in a separate
   exact-key appendix.
4. For an observed recipe, prefer a real clause in the requested register. If
   that recipe is not observed there, label the local wording as a
   counterfactual register expansion.
5. For an unseen composition of known atoms, show its literal atom trace but
   stop instead of declaring it a card. For an unseen atom, stop earlier.
6. Run eight end-to-end tests spanning every tier, including both stop modes.

## Decision rule and claim ceiling

The recipe key, not the German phrase, decides the match. Four pairs in the
narrow appendix deliberately share a short natural phrase; they remain
distinct because their component order differs. The reader consumes an
already segmented component recipe. It does not segment a new Voynich surface,
predict a spelling, add a page, or establish any working value as plaintext.
