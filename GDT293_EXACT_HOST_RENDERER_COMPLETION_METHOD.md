# GDT293 — exact-host renderer completion

## Question

GDT288 predicted that recurrence of an exact opaque `PAGE_HOST` should help
complete its own source group even though exact-host `NEXT_HOST` transfer has
already failed.  GDT293 tests the still-unscored half of that statement: does
the same host, learned only on other physical folios, predict the complete
same-group renderer tuple beyond record/layout opportunity?

This is a parser-dependent formal completion test.  It does not test a word,
lexical meaning, or sequential host relation, and it does not rerun GDT165.

## Frozen population and endpoint

Use the same eight f84-free native panels as GDT286--292.  In each held-folio
fold, score only events whose exact host occurs on at least one training folio.
The primary outcome is the exact joint tuple:

`wrapper | local frame | inner-D | right family | DY | B3`.

The six coordinate-wise held codelength gains are fixed diagnostics.  They do
not replace the joint primary endpoint.

## Frozen models

Both models use Dirichlet-1/2 global smoothing and an 11-event hierarchical
prior.

1. `LAYOUT_CONTEXT`: section, Currier, hand, register, within-field position,
   record-ordinal bucket, field-ordinal bucket, physical group position, and
   host length;
2. `EXACT_HOST`: add the exact opaque PAGE_HOST identity learned only outside
   the held physical folio.

No host glyph similarity, substring, preceding host, following host, or
same-folio target history is used.  Repeat prior masses 5 and 22, and hold out
whole sections and hands, as fixed Voynich sensitivities.

## Frozen null and decision

After held-folio probability vectors are frozen, permute the joint renderer
tuples within exact `physical folio × layout context` strata.  This preserves
folio, every layout opportunity, and the joint outcome inventory while
destroying exact-host alignment.  Use 64 shared worlds and a standardized
max-eight statistic over panels with positive null variance.  Zero-variance
panels retain descriptive results and `NA` p-values.

Call `EXACT_HOST_RENDERER_COMPLETION_SUPPORTED` only if:

- the Voynich joint gain is positive;
- at least four of six coordinate gains are positive;
- at least 60/91 held folios have positive joint gain;
- held-section and held-hand joint gains are positive;
- max-family `p <= .05`.

Otherwise call `EXACT_HOST_RENDERER_COMPLETION_WEAK_OR_LOCAL`.

## Claim ceiling and seal

At most, support would establish cross-folio completion of a parser-defined
renderer tuple by an opaque host identity.  It cannot establish that the host
is lexical, a word, code value, morpheme, sound, language, meaning, plaintext,
or translation.  Only the published f84-free native inventory is read.  No
f84 row may be opened, parsed, retained, joined, or scored.
