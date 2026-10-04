# GDT1173 — shuffle excess does not locate information outside whole forms

**Provenance correction,4October:** the paper and identical inspected code were
already reviewed in the project's5September proposal. The claim of new project
input and the resulting external-search selection are withdrawn. The arithmetic
below is unchanged. See [CORRECTION.md](CORRECTION.md) for primary evidence and
the user's previously recorded restriction on public-approach searches.

**Decision: SHUFFLE_EXCESS_ORDERING_IS_NOT_INFORMATION_LOCALIZATION.**
The comparison alone cannot establish that the written groups are not words,
or justify discarding whole-form identity. This is an exact small estimator
counterexample, not a new Voynich finding or a translation.

## What was checked

[Rozanova and Temerev, arXiv2608.17096v1](https://arxiv.org/html/2608.17096v1)
compare adjacent edge-glyph and capped token-identity mutual information after
subtracting within-line shuffle averages. Section3.2 interprets the cross-scale
ordering as localization at edges. The authors also state that low adjacent
information is not a meaning test, disclose vocabulary-cap sensitivity and
retain other encoding mechanisms. Those qualifications and their empirical
profile are not refuted here. The paper motivated this scope check; its
manuscript measurements were not reproduced.

One artificial line was fixed before computation:

```
axa ayb bzb bwa ava aub bvb bxa
```

Every whole form is different. At every boundary the last glyph of the previous
form equals the first of the next. The strings carry no assigned language or
meaning. All40320 permutations of the same eight identities were evaluated,
without a vocabulary cap taking effect or a fitted alternative construction.

| Representation | Observed empirical MI, bits | Exact shuffle mean, bits | Difference, bits |
|---|---:|---:|---:|
| Whole identity → whole identity |2.807354922|2.807354922|0|
| Last glyph → first glyph |0.985228136|0.142091707|0.843136429|

Normalizing by the destination-feature entropy across all eight tokens gives
0% for whole identity and84.3136% for edges. These percentages have different
denominators (3 versus1 bit); they are not shares of a common information pool.

## Why this happens

In every permutation there are seven different left identities, seven different
right identities and seven different identity pairs. All three empirical
entropies are log2(7). Thus empirical identity MI always equals log2(7), and
subtracting its shuffle mean necessarily leaves zero. This is an algebraic
property of the singleton sample, irrespective of its chosen order.

The edge features pool those sparse identity cells into two recurrent classes.
Their measured dependence changes under permutation, leaving a positive excess.
There is no violation of data processing: the raw observed0.985 bits at edges
are below the raw2.807 bits for full identity. Rather, subtracting two different
null expectations need not preserve that ordering. Capping rare identities can
create further loss, but is unnecessary for this counterexample.

The raw identity value is itself an overfit empirical quantity, not demonstrated
predictive information. The example establishes neither successful language
prediction nor meaningful syntax. Its purpose is to prevent interpreting a
shuffle-corrected ranking as an information decomposition or word-boundary test.

## Limits and research decision

The construction has100% singleton identities and only eight tokens. It does
not estimate how much of the actual Voynich contrast results from sparsity,
capping, writing mechanism, corpus differences or real linguistic structure.
In particular, this result does not establish that Voynich groups ARE words,
that ordinary prose fits, or that the paper's numerical findings are wrong.
The authors' weaker claim that words have not been established remains intact.

Retain the whole-form information already supported in
[GDT608](../gdt608_compositional_stem_orientation/REPORT.md), together with its
component backoff. Retain the limited known-phrase transfer in
[GDT915](../gdt915_terminal_lr_phrase_transfer/REPORT.md) and the different
new-pair nonconfirmation in
[GDT916](../gdt916_unseen_lr_stem_pair_transfer/REPORT.md).
Do not turn this paper's ranking into a new reason to abandon whole forms,
select a glyph alphabet or launch a decoder. The existing
[cross-boundary-model stop](../../semantic_assumptions/results/source_cross_boundary_increment_public_prior_audit.md)
also remains. No new suffix-to-prefix predictor, matched-corpus series or
reopening of a failed decoder is selected. A proposed writing rule must still
make a consequence that distinguishes its competing readings; this check does
not supply such a rule. Confirmed meanings remain0.

## Reproduction and provenance

```
python3 experiments/yolo/gdt1173_edge_identity_statistic_scope/src/run.py
python3 experiments/yolo/gdt1173_edge_identity_statistic_scope/src/validate.py
```

The runner enumerates full identity permutations and calculates entropy sums.
The separate validator imports none of it: it enumerates2520 distinct orders
of the four two-member edge classes, expands each with multiplicity16, and
calculates MI directly from joint/marginal frequency ratios. All16 resulting
joint-count tables, their multiplicities, both means and the conclusion agree.
`artifacts/VALIDATION.json` is PASS. This is independent code, not an independent
analyst, manuscript sample or source of semantic evidence.

The local protocol lock preceded execution at18:48 UTC. The identity result was
already anticipated algebraically, and the source paper was already read;
no blind discovery or public-before-execution registration is claimed.
`SOURCE_METADATA.json` pins inspected functions in source revision956a7c4.
The paper identifies revision66f8adaa; the same attempted file path there
returned404. We did not silently equate the revisions. No downloaded source
module was executed and no external manuscript records were fetched. The
analysis depends on the displayed statistic and our bound artificial input.
The one rejected file-writing patch changed no source; no analytical repair
or post-result tuning occurred. Preparation, execution and publication timing
are retained in artifacts/WORK_RECORD.json.
