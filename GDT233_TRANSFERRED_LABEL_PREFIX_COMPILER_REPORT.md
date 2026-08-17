# GDT233 — transferred graphical-label prefix compiler

## Outcome

**`TRANSFERRED_GRAPHICAL_LABEL_PREFIX_LAYER_PARTIAL_CONTENT_RESIDUAL_UNRESOLVED`.**

A source-family prefix model learned without q13 transfers strongly enough to
identify a real graphical-label register layer in q13.  It does not recover
content.

## Held-section result

Training used 3,211 non-q13, non-f84 first-group loci, including 643 editorial
labels.  Fourteen prefixes met the exposed fixed rule.  Applied unchanged to
the 646 q13 loci:

| TP | FP | FN | TN | precision | recall | q13 label prevalence |
|---:|---:|---:|---:|---:|---:|---:|
| 34 | 12 | 64 | 536 | **.739** | .347 | .152 |

The postselected hypergeometric tail is `5.42e-21`.  This is not a semantic
probability; it shows that prefix architecture identifying editorial graphical
labels transfers across section/register boundaries.

The selected set includes broad `AQA-`, `AQAB-`, and `AQAC-` families plus
several less frequent prefixes.  The low recall is important: most q13 labels
do not carry one of these transferred prefixes, so there is no single label
grammar.

## BACA sensitivity

Outside q13, `BACA-` has 14 occurrences and 7 labels.  Its one-sided training
tail is `.01152`, just outside the strict `.01` selection rule; it was not
silently added.  In q13 it marks 5/5 labels, but this is the exposed sensitivity
from GDT231/GDT232.

Removing `BACA-` leaves residuals:

| locus | residual family |
|---|---|
| f75v.21 | `B` |
| f75v.30 | empty |
| f82r.35 | `B` |
| f82r.38 | `CA` |
| f83r.51 | `BCA` |

The f82r pair therefore decomposes naturally as a shared graphical/local-class
layer plus two different residuals, `B` and `CA`.  Nothing yet identifies what
those residuals encode; they could be instance, side, state, local formula, or
unrelated material.

## Consequence for the generative model

The q13 label register now has direct cross-section support for an outer
family-prefix compiler.  A useful abstract parse is:

```text
GRAPHICAL_LABEL := LABEL_REGISTER_PREFIX? RESIDUAL_FAMILY
```

This helps separate rendering from content.  It also makes a naive reading of
`dar-`/`BACA-` as the content word less plausible.  Translation work should
target residual invariance under independently repeated referents, not the
transferred label prefix itself.

The design and scratch performance were exposed before publication, and
editorial `kind=L` is not an authorial semantic category.  No prefix or
residual is a confirmed label marker, object, word, morpheme, sound, language,
plaintext, or translation.  No f84 row was retained, joined, or scored and no
new f84 access occurred.
