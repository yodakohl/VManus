# GDT275 — q13 scaffold-to-content prediction

## Question

GDT274 found that 208/240 q13 physical lines reuse a coarse field-size and
endpoint scaffold found on another folio, although every complete raw,
PAGE_HOST, and compiler line is unique.  Does the recurring scaffold predict
which opaque PAGE_HOSTs fill it, or is it an empty layout shell?

## Exposed exploratory design

This design follows pilot inspection of GDT274 and is exploratory.  It uses all
1,896 source-group events in the f84-free GDT227 q13 interlinear.  Each event
has:

- nuisance context: physical folio, exact field group count, DY/line endpoint,
  exact number of fields on the physical line, first/middle/last/only line
  slot, and record-position quartile;
- candidate context: the complete coarse `S12/L3P + endpoint` line template
  and exact field slot within it;
- target: exact PAGE_HOST identity (primary) or exact raw source group
  (sensitivity).

For each held physical folio, the nuisance model backs off from its exact
context to the training global identity distribution.  The scaffold model
adds the candidate context.  Additive prior masses are fixed at 8 for nuisance
and 512 for scaffold after a logged pilot showed smaller masses overfit; they
are not searched in the published family.

The score is held-folio log2 gain of scaffold over nuisance.  A positive gain
alone is not evidence because smoothing can improve calibration mechanically.
The exact null permutes PAGE_HOST/raw pairs inside physical-folio × exact-
nuisance strata, preserving identity frequency and every listed structural
opportunity while destroying only scaffold-slot association.  There are 2,048
shared worlds and a max-two correction across PAGE_HOST and raw targets.

The exploratory support gate requires PAGE_HOST gain above its null, at least
6/9 positive folios, and max-two p <= .05.  Raw is a sensitivity, never a
second independent sample.

## Ceiling

A pass would show only that a coarse q13 line scaffold constrains opaque host
identity.  A failure would show that the reusable scaffold does not carry a
portable exact-identity code under this model.  Neither outcome assigns a
word, field role, language, meaning, plaintext, or translation.  f84r is not
opened, retained, queried, joined, or scored.
