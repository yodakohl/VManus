# GDT1223 — the cross-reading strengthened screen is selection-sensitive

**STRENGTHENED_SCREEN_OPERATIONALLY_UNSTABLE.** Only29of128fixed page-order
runs pass the full conjunction across all nine candidate/reference reading
pairs, below the registered minimum122. In contrast,126of128runs pass the
joint own-reference comparisons. These are distinct prespecified outcomes:
the primary cross-reading test fails; the matched-reading diagnostic is
operationally stable at the same122threshold. No criterion was changed.

| Sample reading | Against IT2a reference | Against RF1b reference | Against ZL3b reference |
|---|---:|---:|---:|
| IT2a |127|92|126|
| RF1b |125|127|119|
| ZL3b |120|38|126|

The16recorded gates contain15distinct statistical quantities because the old
loose edit1condition is retained alongside its stricter replacement. Every
sample has8000eligible groups. There are128page-order choices, three alternate
readings per choice and nine reference comparisons; none of these counts is
an independent replication count or a decipherment measure.

## The main source of rejection is final y

| Reading | Original reference final-y share | Range across128same-reading samples |
|---|---:|---:|
| IT2a |40.2000%|36.8625–46.0750%|
| RF1b |37.0500%|34.6250–42.8250%|
| ZL3b |41.5125%|38.5875–47.5875%|

The fixed±5percentage-point bands share only36.5125–42.0500%. Consequently,
90ZL3b samples fail the RF1b final-y band,36IT2a samples fail it, and9RF1b
samples fail the ZL3b band. Other nonzero final-y counts are3RF→IT and8ZL→IT.
Within the matching reader, only seeds26and120 fail: seed26ZL=.46925;
seed120IT=.46075,RF=.42825,ZL=.475875. These are all own-reference exceptions.

The only other failed quantities are word entropy (2IT→RF and2IT→ZL) and
q-count (1ZL→IT and1ZL→RF). All other recorded conditions pass in every pair
and seed, including both edit1bands, conditional glyph entropy and marginal
glyph entropy. Per-seed values, every failed gate and all ranges remain in
RESULT.json. Failures overlap; the table counts must not be added as if they
were separate rejected samples.

This identifies a fragile cross-reading conjunction under the fixed pooled
selection procedure. It does not isolate transcription disagreement as the
sole cause: readers also differ in eligibility and the point at which8000
eligible groups are reached. Sections, hands, vocabulary and underlying ink
were not separately estimated. There was no new stratum analysis or fitted
explanation of the y difference.

## Consequence and retained decisions

Do not use a single pooled8000-group profile required simultaneously across
all reference readings as the sole hard full-profile filter for future writer
construction. A future comparison needs an explicitly justified observation
and sampling contract before looking at a candidate's outcome. This block
selects neither a preferred reading, a best seed nor a wider tolerance.

GDT1213's128/128own-reference two-frequency result reproduces exactly and
remains valid. The present cross-reading experiment is a stronger comparison,
not evidence that1213was incorrectly executed. Every original failed writer
retains its original registered decision. In particular,1195was not rescored,
and its low edit1rates are not erased by finding sensitivity in another gate.
1193remains a working basic artificial control; its new conditional interior-
alphabet contradiction is a separate exact structural argument and is not
repaired by this statistical audit. No source language or native word follows.

Matching one reader was a diagnostic specified before output, not a post-hoc
replacement success criterion.126/128matched passes cannot rescue the29/128
primary outcome. The operational122threshold estimates no independent error
probability: the samples overlap and all three readings concern one manuscript.
The control establishes neither statistical sufficiency nor historical usability.

## Reconstruction and scope

The first pass reconstructs1174's actual contiguous eligible segments and uses
its byte-frozen metric implementation, with a cached pure glyph parser. A second
implementation uses regex units, original-neighbor edges, weighted type counts,
an alternate variance formula and deletion-based edit distance. It imports
neither the runner nor the old metric module. Every metric agrees within1e-10;
every Boolean gate and status agrees. This is same-author software validation.

Every prior1213sample-ID digest and frequency count agrees. The seed1174anchor
reproduces all24,000saved IDs and every original reference metric; that anchor
also passes all cross-reference gates. No alternative reference was chosen.
Eligible counts remain IT29,821,RF25,622,ZL25,564. Both independent reads used
selector-first query-tsv with the same179explicit allowed selectors and eight
columns. f84/f84r remain sealed;f116v,reserves and images were not accessed.
No word-value or relation packet was introduced.

Run a fresh isolated reproduction with:

```bash
python3 experiments/yolo/gdt1223_strengthened_screen_self_control/src/run.py --out experiments/yolo/gdt1223_strengthened_screen_self_control/runtime/replay
python3 experiments/yolo/gdt1223_strengthened_screen_self_control/src/validate.py
```

The validator independently reconstructs the original results without replacing
them. The first command requires its output directory to contain no old result.

Preparation began03:46:09UTC; selected03:49:34; locked03:53:24 before native
acquisition; calculation ended03:53:26; separate validation ended03:54:13.
Local packaging/registry closure follows within the04:21:09inclusive deadline.
No automatic wider calibration, source/decoder repair or new threshold run.
This is a local construction checkpoint under the4Octoberuser instruction,
not a claimed public release. Confirmed native word meanings remain0.
