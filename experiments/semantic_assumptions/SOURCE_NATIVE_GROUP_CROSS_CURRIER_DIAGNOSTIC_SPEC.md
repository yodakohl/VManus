# Source-native exact-group cross-Currier diagnostic

## Purpose and status

Describe whether recurring complete STA-family group forms retain the same
first-versus-last physical-position tendency in Currier A and Currier B.  The
confirmed source-native edge model already transfers at the compositional
family-feature level; this audit asks whether whole-form behavior is likewise
shared or is more register-specific.

This is a post-atlas descriptive audit.  It has no confirmatory p-value and may
not be used to select a favorable threshold or individual form.

## Inputs and scope

Use the frozen strict source-native group table and require the validated exact
group position atlas.  Keep only strict zero-alternative confirmed-prose groups
in Currier A or B and only factual first/last endpoints of multi-group loci.
Physical folio is the leading `f` plus digits.

A family surface enters the fixed common-support panel when, separately in A
and B, it has at least ten endpoint occurrences and spans at least five physical
folios.  These gates use endpoint availability but not first-versus-last
direction.

For surface `x` and register `r`, report the Jeffreys-smoothed log odds ratio
against every other surface in that register:

```text
log((first_x + .5)/(last_x + .5))
- log((first_other + .5)/(last_other + .5)).
```

Report the complete form table, sign cross-tabulation, Pearson and midrank
Spearman correlations, and all leave-one-form Pearson correlations.  Zero is a
separate direction.  No significance threshold or post-hoc subset is defined.

## Claim ceiling

The audit can show only that exact source-native group-form position tendencies
are partly shared or partly register-specific.  Currier A/B are correlated
manuscript registers, not independently sampled languages.  Neither agreement
nor reversal identifies dialect, language, part of speech, sound, morpheme,
word meaning, plaintext, cipher, or translation.
