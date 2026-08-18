# GDT286 — opaque host-to-wrapper transfer

## Question

GDT282--285 show that wrapper identity predicts host character form, while the
terminal penalty depends on recurrent exact-host training support.  GDT286
reverses the prediction: does an exact opaque PAGE_HOST carry a stable wrapper
class across held folios, or does wrapper choice vary with field position?

This is a formal association test.  PAGE_HOST is not treated as a lexeme, and
no host substring, meaning, morphology, or new parser is introduced.

## Frozen panels and outcome

Use the eight wrapper-powered 8,448-event native panels from GDT284: Voynich,
three Latin diplomatic controls, Augsburg accounts, lexical codebook A,
factorial notation B, and human-grown distributed notation B2.  Predict the
frozen wrapper-class label.  Wrapper alphabets are parser outputs and are fixed
per panel; alternate readings are not replications.

## Frozen hierarchical predictors

Use held-physical-folio outer folds.  Every probability is a Dirichlet-1/2
global distribution followed by fixed 11-event hierarchical prior steps:

1. past wrapper counts on the target page;
2. `SHAPE_CONTEXT` training counts keyed by section, Currier, hand, register,
   within-field position, host length, first host character, and last host
   character;
3. `EXACT_HOST` training counts keyed by the opaque exact PAGE_HOST identity;
4. `EXACT_HOST_X_POSITION` training counts keyed by PAGE_HOST identity and
   within-field position.

Report held log-loss, top-1 accuracy, exact-host coverage, and incremental
bits/event for `EXACT_HOST - SHAPE_CONTEXT` and
`EXACT_HOST_X_POSITION - EXACT_HOST`.  No target outcome from a future event is
used; past target-page wrappers are available equally to all models.

For Voynich, repeat the first two models with whole section and whole hand held
out.  These are transfer sensitivities; cells with no training occurrence of a
host remain scored by the same hierarchical backoff.

## Frozen null

For 64 worlds, independently within each physical folio and exact
`section × Currier × hand × register × within-field position × host length ×
first character × last character` stratum, permute opaque host IDs.  This
preserves wrapper outcomes, host frequency within each folio, fixed host shape,
position and all nuisance coordinates while destroying cross-folio identity
alignment.  Seed family: `GDT286_WITHIN_FOLIO_SHAPE_HOST_ID|panel|world`.

Compare the observed held-folio exact-host gain with inclusive one-sided local
and shared-world max-eight p-values.  Position interaction is descriptive and
predeclared, not a second searched endpoint.

## Frozen decision

- `WRAPPER_PRIMARILY_STABLE_HOST_CLASS` if Voynich exact-host gain is positive,
  max-eight `p <= .05`, position interaction is nonpositive, and at least one
  of held-section or held-hand exact-host gains is positive;
- `WRAPPER_CONTEXT_CONDITIONED_HOST_VARIANT` if exact-host gain and max-eight
  gate pass but position interaction is positive;
- otherwise `WRAPPER_HOST_ASSOCIATION_NOT_TRANSFERABLE`.

## Claim ceiling and seal

At most this distinguishes stable opaque host-class association from a
position-conditioned wrapper association.  It cannot establish a lexical
class, morphology, abbreviation, sound, language, meaning, plaintext, or
translation.  Only the published f84-free native inventory is read.  No f84
row may be opened, parsed, retained, joined, or scored.
