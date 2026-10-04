# GDT1173 — scope of an edge-versus-identity statistic

## Decision note before computation

Question: can larger shuffle-subtracted edge mutual information than
shuffle-subtracted whole-form mutual information, by itself, locate information
outside whole-form identity or rule out words? This is a source-method question,
not another Voynich suffix-to-prefix model or a decipherment candidate.

New input: Rozanova and Temerev, arXiv2608.17096v1, sections2.2/3.2/A.8.
Their descriptive comparison must distinguish mutual information from a
difference of estimators. The authors explicitly say low adjacent information
is not a test of meaning, report vocabulary-cap sensitivity and retain
alternative writing mechanisms. No unconditional meaninglessness claim is
attributed to them. Inspected code is pinned in artifacts/SOURCE_METADATA.json.

Positive predecessors: GDT608 directed exterior-component backoff and whole-form
residuals; GDT915 known-phrase co-variation. GDT916 fails the different new-pair
extension. The source_cross_boundary_increment_public_prior_audit already stops
another suffix-to-prefix predictor. These decisions remain unchanged.

Unknown: the logical force of the newly encountered cross-scale comparison.
An exact counterexample would forbid using that comparison alone to discard
whole-form models or identify the true linguistic unit. Otherwise report failure
of this construction, without tuning it or declaring the inference proved.
Neither outcome selects a language, word meaning or Voynich decoder.

Smallest adequate check: one eight-token artificial line, all identities
distinct, with repeated edge classes; all8!=40320 within-line permutations.
No new corpus, target query, image or external code execution. Total local
checkpoint:25minutes from18:44 UTC, including protocol, implementation,
validation, interpretation and publication. Earlier literature selection is
prior preparation, not a timed or blind result. The former global45-minute
limit was removed by the user; this is a local expansion checkpoint.

## Fixed contract

Tokens: axa ayb bzb bwa ava aub bvb bxa. They are invented, have no assigned
linguistic meanings and are not Voynich. Use whole-token identity and last glyph
of the left token versus first glyph of the next. All seven adjacent positions
remain. Vocabulary cap2000 is inactive; no OTHER bin is created.

For each representation compute unsmoothed empirical mutual information I from
its seven adjacent pairs. Delta is observed I minus the exact mean over all
40320 equiprobable permutations of the eight distinct identities. Report raw I,
shuffle mean, Delta and Delta divided by destination-feature entropy across all
eight tokens. The denominator follows the inspected implementation, rather than
using only the seven destination positions. No significance test is claimed.

The anticipated algebra is not blind: under EVERY permutation there are seven
distinct left identities, seven distinct right identities and seven distinct
joint cells. Each empirical entropy is log2(7), hence identity I=log2(7) and
identity Delta=0. In the declared order, last glyph equals next first glyph,
with counts3/4. Compute the edge-shuffle average and check edge Delta>identity
Delta. No construction changes, extra examples or favorable subset afterward.

Independent validator enumerates2520 distinct orders of four edge classes with
two copies each. Each represents16 whole-identity permutations. It calculates
MI directly from the2x2 joint table without importing the runner, reconstructing
the complete joint-table histogram, weighted mean, observed value, singleton
identity proof, normalization, enumeration sizes, result and protocol hashes.

## Assumptions, scope and stopping rule

This tests the universal interpretation of a statistic, not the size or cause
of bias in the manuscript. Synthetic hapax fraction is100%; no matched natural
language or Voynich control is claimed. Exact enumeration replaces Monte Carlo
noise without changing the permutation null.

Uncapped whole identity contains its deterministic edge features. Data processing
gives I(edge-left;edge-right)<=I(identity-left;identity-right). Subtracting
different null means need not preserve this inequality. Identity capping adds
another loss, but this example does not depend on it. Different entropy
normalizers also preclude interpreting percentages as the same information pool.

Small identity Delta identifies neither grammar nor absence of content, and is
not the performance of an out-of-sample predictor. No external manuscript data
are downloaded or scored. Metadata distinguishes the inspected source revision
from the paper's stated revision;404 at an attempted path does not prove the
revision absent. The checked functions are independently reimplemented, not run.

Keep the paper's qualified empirical profile, GDT608/915 positives, GDT916
nonconfirmation and the prior cross-boundary stop. No new generic model series.
This is an anticipated fixed arithmetic demonstration, not a blind discovery,
new manuscript finding or independent numerical replication of the paper.
