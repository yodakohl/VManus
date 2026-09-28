# GDT1079 — exact inner-ring versus paired luminary texts

Registered before computing the cross-ring intersections on 28 September 2026.
All Voynich text and both images were already exposed in the project. This is
an exploratory, within-manuscript priority check, not independent confirmation.

## Unknown and decision

GDT1043 describes the f85r2 centre as sunlike but does not identify it; the
f85/f68 native comparison finds no distinctive motif identity. GDT1042 gives
all f85r2 groups without a meaning, while the f68r2 paired-ring source and
GDT1051 preserve both whole rings and their incompatible simple one-word
substitution. Unknown: does the **inner** f85r2 text ring `.24`, as one
complete fixed unit, share a rare exact written group specifically with the
f68r2 lower Sun-like ring `.31` and not the upper crescent ring `.6`?
If yes, prioritize a C0 solar-reference candidate for a subsequent whole-text
reading. If no, park this exact lexical bridge; do not infer the centre is not
solar. Either outcome leaves current word meanings unconfirmed.

## Fixed input and scope

- f85r2 `.24` inner annulus: **all** raw groups in ZL3b/IT2a/RF1b from
  GDT1042 `artifacts/native_groups.tsv`; its `.1` outer annulus and four
  sector blocks are nonselected same-page controls, not alternative targets.
- f68r2 `.31` lower Sun-like and `.6` upper crescent-associated ring: **all**
  raw groups from the pre-existing
  `F68R_PAIRED_OPENINGS_SOURCE_20260927.json` guarded group rows. No other
  f68 text is admitted or queried.
- Frequency denominator: the pre-existing `word_profiles.sqlite` cache built
  by `tools/word_profiles.py` through the selector-first guarded 179-selector
  query. Before use, verify cache source and allowlist hashes against the live
  files and its receipt. The cache is disposable, never published as evidence.
- Both target pictures were known before design; f84/f84r and reserves closed.
  Three editions are alternate readings of one manuscript, not samples.

## Frozen method and gates

For each edition and each of the three selected rings, preserve the complete
ordered raw-group list with source indices, including marked/uncertain forms.
An **eligible exact form** contains only lowercase `a`–`z`, has length at
least four, and has definite source boundaries on both sides (line start/end
count as definite). Do not normalize, edit, merge, transliterate, stem, or
convert uncertain forms. Compute the full set intersections for `.24` with
`.31` and `.6` separately in every edition. Report all matches with positions
and corpus counts; also show raw ineligible intersections and all ring sizes.

The predeclared **rare Sun-only lead gate** requires at least one identical
eligible spelling present in `.24` and `.31` in **each** edition, absent from
`.6` in each edition, and occurring no more than ten times in the admitted
179-selector cache in **each** edition. The same spelling must satisfy every
reader; reader counts are a stability check, not replicated evidence. Show
whether any passing form occurs in the f85 `.1` outer ring or any of its four
sector blocks; that recurrence is a qualifier, not a post-hoc exclusion.
No gate is widened if empty. A Moon-only form is a countercomparison, not an
alternative success declared after inspection. No p-value or significance
claim: two already noticed pictures and the full search family are not
controlled.

Known risks: exact forms can reflect form/position rather than referent;
ring text need not name its centre; graphic Sun/Moon labels are interpretations;
f85 `.24` physical group-to-angle indexing is unresolved; manuscript/hand
and all-reader correlations remain. No result licenses `okoaiin=Sun`,
`okeo=circle`, or any other translated word.

Smallest adequate implementation: one bounded source read and set comparison,
one independently coded count/check, full tables and a short decision.
Wall-time budget 30 minutes total, including preparation, code, validation,
ledger, privacy preflight and publication. Stop expansion at budget limit.
