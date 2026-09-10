# GDT907 — line-seam joins do not yet identify word continuation

The complete census contains26 identical fragment-pair hits in all three
readings, spread across22 physical leaves and21 joined forms. But recorded
line adjacency produces only a small excess over endpoint reassignment.
This supplies no persuasive aggregate evidence of hyphenation, and does not
rule out individual continuations. No word meaning or translation is recovered.

| Reading | Eligible seams | Actual joins | Reassignment expectation | Excess | Exploratory upper-tail fraction |
|---|---:|---:|---:|---:|---:|
| ZL3b |2709|55|52.919048|2.080952|0.2782|
| IT2a |2957|48|47.528571|0.471429|0.5042|
| RF1b |2711|41|38.251586|2.748414|0.2442|

Each reading covers90 physical leaves; their seam union has3315 locus pairs.
The three readings are alternate transcriptions of one manuscript. Their
counts are not added into independent observations or combined p-values.
The fixed diagnostic requiring both fragments to have at least2 letters gives
25/23.835714 observed/expected in ZL,27/25.278571 in IT and23/19.213707 in RF.
It is not a second success criterion or a replacement for the primary result.

A hit means only that literal A+B occurs as one plain running-text group
on another physical leaf in the same reading. For example, the fragment pair
`qoty` / `shey` at f77v.29–30 agrees in all three readings; ZL supplies an
unbroken `qotyshey` witness at f107v.29. Another all-reading pair is
`dal` / `daiin` at f103v.1–2, with ZL `daldaiin` at f45r.11. Common forms
can concatenate by accident or through ordinary syntax. These examples
are retained observations, not reconstructed words or instructions to join them.

There are27 locus pairs hit in all readings, but only26 have identical A and B;
f75r.24–25 is the difference and is not silently normalized. The artifacts
preserve every eligible seam, all hit witnesses, every reassignment matrix,
exact rational expectations and all9999 null scores per reading. Singleton
strata have observed=expected and provide no sequence-discrimination evidence.
There are557/660/581 exchangeable strata in ZL/IT/RF respectively.

## Scope and interpretation

The source is the unchanged, previously guarded GDT851179-selector cache.
No new TSV query, image, page admission, held data, literal repair or learned
word mapping entered. Public registration4005fed7 preceded seam enumeration.
The new endpoint is cross-line literal concatenation, not GDT853's stopped
same-line neighboring-word predictor; its failed metadata pairs were not loosened.

A source limitation matters: RF has zero paragraph-start/end flags on all3768
P lines; ZL and IT have665 and697 marked starts respectively. The frozen
code/location breaks are still applied, but RF runs are not independent
confirmation of the same paragraph partition. More generally, consecutive
numeric loci and +P0/+P1 codes are metadata evidence for below-line succession,
not fresh native verification of all physical obstacles or intended discourse.
An uninterrupted run may begin in midparagraph. No paragraph boundary or
hyphenation truth is inferred from absence of an annotation.

Within a run and right-fragment length, the null reassigns actual next-line
heads to actual line tails. It preserves endpoint inventories and fragment
lengths, but does not model topic-conditioned syntax, handwriting or the full
writing process. Even a large excess would require a separate distinction
between genuine word continuation and syntactic concatenation. The present
small excess does not select that follow-up. No automatic larger-window,
fragment-normalization or decoder successor is authorized by this result.

## Reproduction and validation

Run `python3 experiments/yolo/gdt907_line_seam_join_discovery/src/run.py`.
Run the separate validator with
`python3 experiments/yolo/gdt907_line_seam_join_discovery/src/validate.py`.

For exact Monte Carlo reproduction, the public registered source serializes
RNG calls with reading outermost, sorted stratum next, replicate innermost,
and a fresh index list on each shuffle, including singleton strata. One
Random(907) instance continues across ZL, IT and RF in SPEC insertion order.
This paragraph clarifies the already frozen implementation after execution;
it does not change any assignment, statistic or comparison.

A separate implementation independently reconstructed source eligibility, runs,
leave-leaf-out witnesses, all matrices and rational expectations, all9999 null
scores per reading, and the cross-reading overlaps: PASS. It did not import the
primary runner. This checks extraction and arithmetic, not native boundaries,
the adequacy of the null as a writing-process model, hyphenation or meanings.

The focused staged privacy/scope/binding check passes. The full repository audit
still reports the existing seven GDT600 binding errors and stale global index
group; those unrelated failures are not fixed or presented as a global PASS.
