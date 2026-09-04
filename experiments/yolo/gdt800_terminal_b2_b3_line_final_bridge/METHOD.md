# GDT800 method

## Inputs and scope

Only three already validated artifacts are materialized:

1. the 4,128-line f84-free V99R7 cache from GDT734;
2. the 101-locus source-native Kluge-A atlas from GDT795;
3. the nine fixed f70/f71/f72 visual transitions from GDT799.

No new page, transcription or image is opened. The two A09 native inspections
reuse the exact Yale canvases already admitted by GDT799. Crop rectangles,
source hashes and derived crop hashes are frozen in
`src/NATIVE_A09_GLYPH_AUDIT.tsv`.

## Surface census

Every whitespace token in the V99R7 ZL3b line is recorded. A token ending in
literal EVA `l` or `m` contributes the complete preceding surface as its
`matched_stem`. A stem is eligible only when it is nonempty and both complete
surfaces `stem+l` and `stem+m` occur. Bare one-sign `l`/`m` tokens remain in
the broad descriptive terminal census but are excluded from every paired-stem
model. Spaces are removed only for the separate circular-label stem
comparison; no source boundary is silently deleted in the running text.

Two line-end definitions are reported:

- any physical line: its last token, including a one-token line;
- multi-token physical line: its last token only when the line contains at
  least two tokens. In the frozen primary population, a singleton line is
  retained but coded `multi_line_final=False`; an explicit sensitivity removes
  singleton-line events altogether. This conservative choice cannot create the
  observed positive boundary effect.

## Conditional tests

For each fixed stratum, the number of `m` endings assigned to final positions
has its exact hypergeometric distribution under fixed ending and position
margins. Stratum distributions are convolved, yielding a deterministic
one-sided conditional probability. Mantel-Haenszel odds ratios are reported
for stem, stem×section×language×hand, and stem×page strata. Section,
language, hand, leave-one-section-out and end-distance gradients are retained
as diagnostics.

## Label bridge and adjudication

The label atlas preserves full ZL3b/IT2a/RF1b member sequences. Coarse family
identity never substitutes for member identity. The complete 156
cross-array same-Kluge-member pairs are enumerated before A09 is identified.
The A09 pair remains the held concrete visual case. Four normalized terminal
stem bases (`oka`, `okala`, `ota`, `otara`) are then compared with the running
text.

Candidates distinguish a boundary-favoured surface field, an obligatory
line-end allograph, a portable semantic suffix, page-level allography,
whole-label clothing status, and indivisible learned wholes. Selection is
formal only. No candidate may turn EVA `l` or `m` into a sound, Latin letter,
word, morpheme or English/German meaning.
