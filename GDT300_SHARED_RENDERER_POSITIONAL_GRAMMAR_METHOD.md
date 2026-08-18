# GDT300 — shared renderer positional grammar

## Question

GDT299 showed that an opaque complete-form identity predicts physical
`FIRST/MIDDLE/LAST` group position beyond its opaque `PAGE_HOST` on held
folios.  GDT300 asks whether that increment is explained by a compact renderer
grammar shared across different hosts, or requires exact host-by-renderer
memory.

No source string, glyph identity, PAGE_HOST substring, or semantic annotation
is inspected.  The renderer is the already frozen GDT297 tuple
`wrapper|local_frame|inner_d|right_family|dy_closure|b3`.

## Frozen population and outcome

Reuse the exact GDT299 panel and eligibility rule: physical lines with at least
two groups, with both opaque host and complete-form hash represented outside
the held physical folio.  The outcome remains mechanical physical group
position: `FIRST`, `MIDDLE`, or `LAST`.  The held-folio split, layout context,
Dirichlet-1/2 smoothing, prior mass 11, and prior-5/prior-22 Voynich
sensitivities are unchanged.

## Models

For each held-folio fold estimate `LAYOUT` and `PAGE_HOST` exactly as GDT299.
For each of six renderer components and the complete renderer tuple, construct
a fixed shared-component predictor.  Let `p_h`, `p_c`, and `p_l` be the
smoothed host, component, and layout probabilities.  The shared prediction is

`p(y | host, component) proportional to p_h(y) * p_c(y) / p_l(y)`.

This is a fixed conditional-independence combination with no fitted mixture
weight.  It asks whether a component has the same positional direction across
opaque hosts.  The exact `HOST_X_RENDERER` predictor uses counts for the exact
host+complete-renderer pair backed off to `PAGE_HOST`; on Voynich it must
reproduce GDT299 `WHOLE_FORM`, because GDT297 established a bijection between
that pair and the complete source form within every audited host.

Report:

- each shared component's held-folio gain over `PAGE_HOST`;
- the complete shared-renderer gain;
- the exact host×renderer gain;
- the fraction of the positive exact-pair gain explained by the shared tuple;
- positive folios and fixed prior sensitivities;
- a descriptive renderer-value position atlas.

## Null and decision

In 64 deterministic worlds, permute complete renderer tuples within exact
panel × physical folio × section × Currier × hand × group count × host strata.
Component fields move together.  This preserves every host, layout
opportunity, renderer tuple's per-folio count, and outcome, while breaking the
renderer-to-position alignment where mobility exists.  Use inclusive local
tails and a max-seven statistic over the six component predictors plus the
complete shared renderer, standardized by each panel/model null mean and
population SD.  Exact host×renderer is reported but is not added as an eighth
selected shared rule.

Call `SHARED_RENDERER_POSITIONAL_GRAMMAR_SUPPORTED` only if the Voynich shared
tuple gain is positive, at least 60 of 91 folios are positive, both prior
sensitivities are positive, max-seven `p <= .05`, and the shared tuple explains
at least half of the positive exact-pair gain.  If the exact-pair signal
reproduces GDT299 but those shared gates fail, call
`POSITION_SIGNAL_HOST_SPECIFIC`.  Otherwise call
`WHOLE_FORM_POSITION_SIGNAL_NOT_REPRODUCED`.

## Claim ceiling

At most this identifies a source-form renderer tuple or component with a
shared physical line-position function across opaque hosts.  It establishes no
word, morpheme, linguistic function, semantic role, code value, sound,
language, meaning, plaintext, or translation.  No f84 row may be opened,
parsed, retained, joined, or scored.
