# GDT059 — HPR2 external-information localization

## Outcome

**PAGE_HOST_SPECIFIC_EXTERNAL_INFORMATION_LOCALIZATION_NOT_SUPPORTED**

This exploratory pass compares 560 exact human-annotated loci and
194 catalogue-covered pages under complete physical-folio
holdout. It tests 8 local object/relation codes and
5 page catalogue codes. Archived annotation classes are noisy,
postselected hypothesis-generation outcomes, not semantic confirmation.

The top held representation in the all-local panel is
`RAW_CHAR3` with descriptive summed gain
+111.321 bits across its
correlated axes. PAGE_HOST character trigrams score
+109.063, versus raw
surface character trigrams +111.321,
compiler-only -14.523,
and B3-only -641.014.

On the page-catalogue panel the corresponding gains across all five correlated
tags are PAGE_HOST
+17.878, raw
+17.239, compiler-only
+18.487, and B3-only
+17.268. These totals rank
hypotheses only; axes overlap and must not be added as independent evidence.

Restricting that panel to the three source content tags, PAGE_HOST scores
+18.982 bits,
but ROOT scores +19.164,
raw surface +17.484,
compiler-only +17.353,
RIGHT-family-only +21.876,
and the intended B3 negative control
+22.909. Because the
compiler and B3 controls preserve at least as much page-content signal as the
PAGE_HOST, this pass does **not** localize source-catalogue content to PAGE_HOST.
The likely explanation is residual page/register ecology not removed by the
available low-capacity nuisance scaffold.

At exact annotated loci the weaker useful lead is narrower: PAGE_HOST
character trigrams are positive on five of eight axes and uniquely lead only
`REL_PROXIMITY` at +5.081 bits; that advantage falls to +0.159 bits in the
unhedged subset. Raw character trigrams remain the aggregate leader. This is a
future feature-engineering lead, not evidence for a semantic host layer.

## Renderer preservation and capacity

Cross-wrapper and cross-right-family same-PAGE_HOST predictions are reported
for every local annotation axis. Exact cross-folio O-versus-OT transfer has
0 eligible predictions, so the frozen O/OT content-preservation
hypothesis is UNSCORED_ZERO_CAPACITY; it was not
rescued with same-folio or different-host examples.

The result fails to localize the weak external signal specifically to
PAGE_HOST. It does not establish that PAGE_HOST is lexical, semantic, or
linguistic. Every
representation, negative control, hedged sensitivity, and capacity failure is
retained in the artifacts. No PAGE_HOST receives an English gloss, semantic
role, word, morpheme, POS, sound, language, plaintext, or translation. f84r
was filtered before retention and was not opened, queried, joined, or scored.
