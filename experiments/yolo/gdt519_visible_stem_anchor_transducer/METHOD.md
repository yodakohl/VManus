# GDT519 method

## Question

Can a monotone visible-stem transducer distinguish GDT518's remaining finite
recipe candidates by requiring their structural atoms to explain the written
surface, while retaining learned short whole renderers?

## Inputs

- GDT407: 4,576 older running events and 1,558 invariant surface/recipe types.
- GDT516: the current 159 forms new to that older base, their recipes and prose
  contexts.
- GDT517: finite residual-closure compiler candidates and mapping evidence.
- GDT518: visible-form ridge and neighboring-card base score.

No additional manuscript page is opened; `f84` and `f84r` stay forbidden.

## Visible anchors and learned renderers

Each structural atom receives a short visible spelling handle. Ordinary tags
use their lowercase stem (`CH~ch`, `OL~ol`, `Y~y`). Structural tags use an
explicit handle (`A_ADDR~a`, `D_ADDR~d`, `LOCAL_CHAR_F~f`, `CARRIER_Q~q`).
`CHD~ched` follows its dominant direct old mapping. These handles are surface
anchors, not English translations.

The old compiler mapping deck also contributes renderer aliases of one to
three atoms. A one-atom alias needs at least ten contacts and 70% mapping
share; a two-/three-atom renderer needs ten contacts and 60%. At most five
aliases survive per atom sequence, and no alias may exceed its canonical
spelling by more than two characters. Thus the model can retain short learned
whole renderers such as `chek~CH+K` rather than forcing every visible character
to become a separate atom.

Alias penalty is `0.25 * weighted_edit(alias, canonical) - 0.10*log(share)`.
The weighted edit treats an unexplained visible surface character as cost 1,
a claimed but missing anchor character as cost 2, and a substitution as cost
1. Dynamic programming partitions the complete surface monotonically across
one-, two- or three-atom renderer transitions. The resulting alignment cost
is added to GDT518 with weight 1.0.

## Older compositional rehearsal

The 1,558 older surface types are assigned deterministically to four rotating
folds by SHA-256. For each fold, its surface types are removed from the
compiler and form-decoder training deck, then parsed from the other three
folds. This is a workshop rehearsal of compositional behavior, not a claim of
language decipherment. It isolates surface/form ordering; the current 159-form
comparison additionally retains GDT518's neighboring-card term.

## Decision rule and ceiling

Pass if the stem-aligned order improves top-1, top-5 and rank sum over the
form-decoder in the older rehearsal, and improves top-1 and rank sum over
GDT518 on the current 159 forms. Exact events and unique known surface/domain
recipes always keep precedence.

The experiment can support only an exploratory structural renderer. Atom
anchors remain distinct from German working values. No confirmed word,
plaintext, language, historical codebook, object identity or unopened-page
reading follows.
