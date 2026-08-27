# GDT526 method

## Question

Can the exact old card `cha=CH+A_ADDR` behave as a productive learned stem,
accepting independently licensed right suffixes on new forms, without a target
whole-form exception and without disturbing old or already correct current
decisions?

## Inputs

- GDT407's 1,558 invariant old surface recipes and four rotating folds;
- GDT516's inherited 159-form current benchmark and current contexts;
- GDT517's finite parser and exact-event/surface-role dictionaries;
- GDT525's complete selected score and its explicit `kcheody` working repair.

No new page is admitted.

## Stem construction

The training deck must contain the exact invariant base:

```text
cha = CH+A_ADDR
```

For a target beginning with visible `cha`, remove that prefix. The remainder
must be a one-to-three-character right suffix. A candidate is eligible only
when removing exactly one right atom block gives `CH+A_ADDR`, and the resulting
visible-suffix-to-atom signature already has a positive GDT522 right/right
license in the old training fold.

The selected feature is:

```text
1 + GDT522_license_bonus
```

at weight `0.80`, applied after the complete GDT525 score. The model ladder
also retains bonus-only, binary, and ten weights from `0.25` through `1.25`.

## Conflict policy

The stem is a default, not a greedy segmentation rule. If the old deck already
contains the exact extended surface with another recipe, that observed recipe
blocks the stem candidate. Thus old forms such as `chaiin`, `chair`, `chal`,
`cham`, and `char` are not forced through `CH+A_ADDR`, while old
`chas=CH+A_ADDR+S` is compatible evidence.

Exact event cards, finite known surface-role options, and explicit working
revisions retain reader precedence. The productive rule is used only below
those layers.

## Decision and claim ceiling

The route passes when it improves at least one current decision, loses no
current correct decision, and leaves the complete four-fold old scorecard no
worse. GDT526 passes with two corrections and exact old-score parity.

This is an exploratory learned-stem and suffix-composition model. `CH`,
`A_ADDR`, `DY`, and `P` are structural atoms. The experiment confirms no
Voynich word meaning, plaintext, language, historical codebook, or unread-page
prediction.
