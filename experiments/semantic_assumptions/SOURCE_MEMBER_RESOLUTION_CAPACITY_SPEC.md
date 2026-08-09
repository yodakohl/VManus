# Source-native STA member-resolution capacity audit

## Purpose

Determine, without fitting or scoring a target, whether the confirmed
STA-family endpoint grammar has enough source-agreed fine-code variation for a
genuinely new incremental test.  The future question would be whether exact
STA member codes add held-folio first-versus-last information after their
coarse STA-family shells are fixed.

This is not a revival of the closed minimal-pair/allography route.  That route
tested selected substitutions, including the single-folio f57v `f/p` relation,
for export to matched prose.  The present audit uses every strict source-native
multi-group locus, requires exact ZL/IT/RF member-code agreement, and only asks
whether a manuscript-wide conditional-resolution test has capacity.  No
member code is interpreted as a physical glyph, allograph, sound, plaintext
symbol, or meaning.

## Frozen inputs

- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`
- `results/source_native_edge_grammar.json`, SHA-256
  `2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88`
- `results/source_native_edge_grammar_validation.json`, SHA-256
  `0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712`
- `CLOSED_ROUTE_FAMILIES.tsv`, SHA-256
  `4076d73acb6bde55e67cd1192cc85cfb4545444a6b57da784af15d2fdda0298b`

## Score-blind panel

Use the first and last synchronized group from each strict, zero-alternative
locus containing at least two groups.  A fine endpoint is eligible only when
`zl_sta_codes`, `it_sta_codes`, and `rf_sta_codes` are exactly equal.  The held
unit is the physical folio, joining recto, verso, and panels.

For each held folio, count a complete family surface or complete member-code
surface as seen only if it occurs at an endpoint outside that folio.  The
prospective productive target must satisfy all of the following before any
edge statistic is fitted:

1. both endpoint member-code sequences agree exactly in all three readings;
2. both complete family surfaces are seen outside the held folio;
3. at least one complete member-code surface is unseen outside the held folio;
4. every fine `P1`, `P2`, `S1`, and `S2` value on both endpoints occurs outside
   the held folio in both FIRST and LAST roles.

Here a fine value includes its namespace and exact STA code or code pair; its
coarse family shell is always retained.  Condition 4 prevents a later score
from succeeding only because a member feature is role-exclusive in training.

## Capacity gates

- exactly 2,873 strict multi-group loci and 5,746 endpoints;
- at least 2,000 loci with exact member codes at both endpoints;
- at least 300 loci on 80 physical folios where both family shells are seen
  but at least one complete fine surface is unseen;
- at least 250 loci on 75 physical folios after the both-role fine-feature
  support rule;
- at least 200 family shells have two or more exact member realizations across
  at least three folios;
- every prospective target identifier is unique and no target score, fitted
  coefficient, edge contrast, English gloss, legacy root, or legacy role is
  produced.

## Decision and claim ceiling

A pass authorizes only a separately preregistered incremental held-folio test
against the already frozen family-only edge baseline.  It does not establish
that the fine codes are physical glyphs, allographs, sounds, morphemes, words,
an alphabet, a cipher alphabet, meanings, plaintext, a language, or a
translation.  A failure closes this route at score-blind capacity.
