# GDT802 method

## Inputs

- GDT800's 4,137 paired-terminal occurrence atlas supplies target identities,
  line positions and outcomes.
- GDT801's 542-event exact boundary join defines the 388-event local lead.
- GDT734's 4,128-line V99R7 reader supplies only the cached ZL3b line token
  sequence needed to recover immediate neighbours.
- `src/SOURCE_LOCK.tsv` binds every predecessor byte-for-byte.  The builder
  rejects any materialized value beginning with sealed `f84`.

## Exact join and masking

Each GDT800 event joins the line reader by `(page,locus)` and its one-based
`token_index`; the joined token must equal the recorded target surface.  Left
and right context never crosses a physical line.  Empty line edges are stored
as `NONE` and do not become features.  The scored target display is
`<stem>{l|m}` so the outcome is never leaked through the full target surface.

The physical-folio alias removes only a terminal panel numeral after the
recto/verso marker: for example `f95v1` and `f95v2` become `f95v`.  It is a
blocking alias, not a semantic page identity.

## Deterministic predictor

For a training set, let the global probability be

`p0=(m+1)/(n+2)`.

For distance cell `d`, the fixed physical baseline is

`P_d=(m_d+16*p0)/(n_d+16)`.

Its logit is an offset.  Each eligible sparse coefficient is independently
optimized by Newton iteration for the penalized logistic objective

`sum_i[y_i*eta_i-log(1+exp(eta_i))] - (4/2)*sum_j beta_j^2`.

The implementation has no learned intercept beyond the physical offset.  Each
coefficient begins at zero, stops when its update is below `1e-12` or after 50
steps, and probabilities are clipped only for numerical scoring.  Left and
right coefficients are fit separately against the physical offset and summed.
For `SC`, the stem coefficient is fit first and the two context coefficients
are fit against the stem-adjusted offset.  Every event has at most one stem,
one left and one right feature.

The builder emits event, fold, score, capacity, `daiin`, sensitivity,
adjudication and structural-card artifacts.  `src/validate.py` independently
checks schemas, joins, cardinalities, fold exclusion, score arithmetic, claim
ceilings and two byte-identical builder replays.

The transparent audit uses `SINGLE/FINAL/PENULTIMATE/EARLIER`, holds out one
complete stem or physical folio at a time, and estimates
`(m[p,c]+20*q[p])/(n[p,c]+20)`. Left and right are scored separately and by the
arithmetic mean when available. Conditional AUC is computed within exact
target-stem x physical-position strata. The outcome-blind rarity control is
`-n[p,c]`; unseen neighbours therefore receive the highest rarity score.

## Interpretation

The comparison asks which information channel predicts a formal terminal
choice on unseen folios and stems.  It does not turn a predictive feature into
a medieval word meaning.  In particular, a useful whole neighbour remains an
opaque contextual address unless another experiment supplies semantic
grounding.
