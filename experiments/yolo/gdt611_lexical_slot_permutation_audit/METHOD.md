# GDT611 method

## Question

Can the compositional units and exterior roles established by GDT605/GDT608
select concrete meanings such as water, wine, oil, salt, plant parts,
operations, vessel, bath, disease, woman, and healing on held folios?

## Inputs

Only published f84/f84r-free artifacts are read:

- GDT606 `guarded_rows.tsv` and `unit_sequences.json`;
- GDT608 `stable_stem_role_summary.tsv` and `merge_tree.tsv`.

The inherited split is 68 training and 23 held physical folios. No manuscript
image, new page, workshop gloss, or generated reference plaintext is used.

## Method

The analysis builds complete hard-chunk carriers and exact substitution frames:
one-unit internal masks, same-line left and right neighbors, and two-sided
neighbors. Candidate pools are frozen from training data using section
contrasts and the formal q-entry, y/dy/aN-closure, and k-nonterminal profiles.
The frozen candidates are then checked on held folios with exact frame reuse,
physical-folio section permutations, 200 train-folio bootstrap restarts, and
frequency/shape-matched controls. Within-family label permutations test whether
the observations identify a particular word rather than only a formal slot.

## Decision rule and claim ceiling

A concrete word requires held-folio recurrence, held reuse of its nominated
frame, an independently owned observable that distinguishes the word from all
alternatives, and a better score than every within-family label permutation.
The experiment may retain transferred formal paradigms and reject these 17
specific default assignments. It may not turn section codes or formal roles
into English meanings, reject all possible semantics, or identify a language,
sound system, cipher, plaintext, or manuscript genre.

The exact frozen details and thresholds are in `PREREGISTRATION.md`; guarded
implementation corrections are in `DEVIATIONS.md`.
