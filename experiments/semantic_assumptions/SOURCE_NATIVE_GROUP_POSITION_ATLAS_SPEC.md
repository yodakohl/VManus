# Source-native exact-group position atlas

## Purpose

Decompose the already confirmed source-native opening/core/closing architecture
at the level of complete STA-family group forms.  The atlas asks which recurring
forms are stably associated with the first versus last group of a multi-group
physical locus, and which are associated with either edge versus the interior.

This is a descriptive decomposition, not a new confirmatory target.  It uses no
legacy cleaner token, unavailable parser root or role, member-code spelling,
image/OCR output, semantic label, or English gloss.

## Frozen inputs and scope

- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`;
- `results/source_native_edge_grammar.json`, SHA-256
  `2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88`;
- `results/source_native_edge_grammar_validation.json`, SHA-256
  `0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712`.

Keep only `strict_zero_alternative=1` and
`grammar_scope=CONFIRMED_PROSE`.  Physical folio is the leading `f` plus
digits, so recto, verso, and panel suffixes remain one held unit.  A group in a
multi-group locus is factually `FIRST`, `LAST`, or `CORE`; a one-group locus is
`SINGLE` and is excluded from both fitted contrasts.

## Fixed contrasts

For complete family surface `x`, compare it with every other surface using a
Jeffreys-smoothed two-by-two log odds ratio:

```text
log((n_x,pos + .5)/(n_x,neg + .5))
- log((n_other,pos + .5)/(n_other,neg + .5)).
```

The two contrasts are:

1. `FIRST_LAST`: `FIRST` versus `LAST`, excluding `CORE` and `SINGLE`;
2. `EDGE_CORE`: `FIRST+LAST` versus `CORE`, excluding `SINGLE`.

Recompute each coefficient after deleting every one of the 94 physical folios.
A form is eligible only with at least 20 total strict-prose occurrences, at
least ten physical folios, and at least 20 observations in that contrast.  It
is associated with the positive or negative state only when the full absolute
log odds ratio is at least 1.0 and at least 90/94 deletion coefficients retain
that direction.  Otherwise it is `UNRESOLVED`; ineligible forms are
`INSUFFICIENT`.

Effective folio and section counts are `exp(Shannon entropy)` over the observed
occurrence distribution.  They are diagnostics, not classification inputs.

## Claim ceiling

The output is a complete descriptive inventory of exact source-native
STA-family group forms under a model family already confirmed on unseen forms.
`FIRST_ASSOCIATED`, `LAST_ASSOCIATED`, `EDGE_ASSOCIATED`, and
`CORE_ASSOCIATED` are relative physical-position tendencies.  They are not
exclusive positions and do not establish START/STOP words, function/content
parts of speech, sounds, morphemes, lexemes, plaintext, language, cipher, or
translation.
