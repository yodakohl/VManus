# GDT524 method

## Question

Can two genuinely independent nearest local-edit analogies reinforce one
candidate recipe more safely than GDT522's single nearest analogy?

## Inputs

- GDT407's 1,558 invariant old surface recipes;
- GDT516's 159 current new-surface benchmark and neighboring contexts;
- GDT517's exact-event and known surface-role dictionaries;
- GDT523's complete candidate paths and scores.

No new page is admitted.

## Consensus construction

For each finite candidate recipe, GDT524 reuses GDT522's learned one-edit
relations. An analogy route contains an old base surface, the target-side
visible edit, the corresponding atom edit, its position class, and its
smoothed support bonus.

Two routes can form a consensus only when:

1. both bonuses are positive;
2. the old base surfaces differ; and
3. the normalized visible-to-atom edit channels differ.

The third condition prevents duplicate testimony. For example, two bases that
both merely say `k -> K` are one channel, not two independent clues. The
selected feature sums the two strongest compatible bonuses:

```text
consensus = strongest compatible bonus 1 + strongest compatible bonus 2
GDT524 score = GDT523 score - consensus
```

The model ladder retains maximum, mean and summed alternatives over several
weights. `SUM2_W100` is selected because it produces the best current
rank-one count without an old or current rank-one loss.

## Rehearsal and ceiling

Each SHA-256 fold learns edit relations only from the other three old-form
groups, then rebuilds the full GDT523 path before adding consensus. Exact-event
and known surface-role cards keep precedence in the executable intake path.

This is an exploratory compositional recipe rule. It does not identify a
lexeme, plaintext word, language, object, or unread page.
