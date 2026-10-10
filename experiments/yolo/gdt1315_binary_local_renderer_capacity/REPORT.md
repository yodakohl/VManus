# GDT1315: two-state local shape choice is insufficient for the binary survivors

**LOCAL_TWO_STATE_RENDERER_EXCLUDED.** Every remaining1314key needs at least
three distinct graphical choices in some identical complete input context.
Therefore the specified deterministic renderer, with at most two hidden states,
cannot generate all retained observations. This does NOT exclude the unrestricted
binary channel, prove three states suffice, or identify actual writer states.

The model fixes the previous/current/next decoded characters, page selector,
exact group ordinal and total original group count of the physical output line.
It may use either of two hidden states, with arbitrary history-dependent state
updates. The source character values need not be known:1312's injective codebook
makes equality of their full bitwords equivalent to equality of those values.
For fixed inputs, two states can produce at most two different whole forms.

| Reading | Eligible consecutive triples | Surviving signal1 keys | Primary lower bound for each key | Exact layout contexts with >2forms per key |
|---|---:|---|---:|---:|
|ZL3b|15435|cph; cfh|3;3|4;4|
|IT2a|21281|cph; cfh|3;3|12;12|
|RF1b|14158|cfh|3|3|

All five reader/key cases were tested; no favorable reader or key was selected.
Keys and readers often share the same physical witnesses, not independent trials.
These are sparse exact counterexamples, not a high global error rate.

## A concrete ZL3b witness

On f103v each target is group7of a10group line. Under both surviving keys, the
three complete bitwords are00000 /0000 /00000 in every row:

| Original locus | Left whole | Center whole | Right whole |
|---|---|---|---|
|f103v.27|oteal|lpar|otedy|
|f103v.30|otedy|poly|lchedy|
|f103v.33|cheody|otey|shdpchy|

Thus all named inputs coincide, but the required center outputs are lpar, poly
and otey. Working units ch/sh count as single units; spelling length in Roman
transcription is not the unit count. No value or meaning is assigned to any word.
The groups and definite adjoining seams are read from existing transcription
caches; no image or new atomic/gap judgment was obtained.

The first ITmaximum witness is f105r.4/.14/.17group2of11, with center forms
olkeedy/qoeeedy/okeeddl and code lengths6/7/6. RF's first witness is f24r.14/.16/.17
group4of5, centers char/dam/cthom and code lengths3/3/3. Complete flanks, units,
source IDs and original metadata are retained in EVENTS.json.gz. Every primary
context exceeding two forms is retained in CONFLICTS.json.gz.

## What the supplied layout information changes

For the cfhkey, the maximum number of center forms in one cell is:

| Reading | Same source-character triple only | Also same page | Also exact ordinal and line group count (primary) |
|---|---:|---:|---:|
|ZL3b|134|12|3|
|IT2a|173|12|3|
|RF1b|112|9|3|

The larger first-column numbers are NOT necessary state counts for the richer
layout-dependent model. All comparisons use the same events. The full layout
keys are mostly unique:15170/20821/13978cells for15435/21281/14158events in the
cfhcases. Fitting those unique cells is memorization, not evidence for a rule.
This test uses repeated conflicting cells only to refute the stated≤2capacity.
No significance test, predicted translation or estimated native alphabet follows.

## Scope and decision

Paragraph-role-sensitive rules are outside the test. Before any count, the
source-free reviewer flagged RFparagraph metadata as unscorable under1073.
The initially considered paragraph fields were therefore omitted for ALLreaders
before registration was locked. They remain source metadata only; absent flags
are not treated as physically verifiedFalse. No paragraph control is claimed.

The result assumes the three observed groups represent consecutive source
characters, with faithful22unit parsing and boundaries. A real source-record
boundary inside a triple, unmarked cross-line codeword wrapping, longer source
context, preceding written forms, line-number rules, counters, randomness or
voluntary variation would change the model. None is disproven or installed as
a repair. The bound is necessary only: a coherent three-state automaton may
still be impossible, and no three-state machine was fitted.

1295/1310concern one written unit per source letter and within-word allography;
1276concerns fixedstem-pair ending outputs.1204/1254use full written neighbors
under other specific cells. Their original failures, compatibility and sparse
capacity remain. The new restriction here is graphical whole-form choice for
1312's source-character code, after1314's key elimination.1312/1314capacity and
1313decoded-run obligations are retained, not overwritten by this result.

Stop this particular local two-state completion. The surviving unrestricted
cfhchannel still has no identified plaintext or paid rule for graphical choices.
Do not automatically add a third state, another context field or language-key
search. A different completion needs an independently motivated rule with its
own consequence, not merely enough free entries to absorb these cases.

## Reproduction

Contract, source and programs were hash-locked before native counting. A
source-free proof review preceded the run. Primary dictionary cells use bitstrings;
the independent same-author verifier rebuilds source-line windows, reparses raw
forms by iterative DP and uses length/integer codes with sorted grouping. It
checks81007source joins,50874triples, all5reader/key cases and146586context cells,
including maximum witnesses and all conflicting cells. PASS verifies the count
under shared transcription assumptions, not independent palaeographic truth.

Only the unchanged1233+1314panels and their915guarded sources were used. No rawTSV,
new corpus/image, reserved material, f84/f84r/f116v/f1rbody or old327/336body access.
Zero meanings assigned. Inclusive08:00–08:35UTC10Octoberbudget covers publication.
