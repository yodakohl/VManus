# GDT1271 — chart-independent zero mask and chart-fitting ambiguity

Source-free selection before demonstration construction,2026-10-07UTC. Whole
work allocation22:15–23:00UTC includes prior retrieval/thinking, proof, programs,
validation and local closure.22:15is a conservative allocation start, not a
measured exact turn-start timestamp. No native data or fitted manuscript chart.

## Decision question
1270provides necessary chart-size bounds but no usable chart. Before chart search,
identify a consequence no choice of chart can alter, and check whether merely
fitting a chart to a text can conceal a chosen input message. This changes the
selection criterion for977: compatibility/inverse alone must not count as evidence
for a reading. No automatic chart/state enlargement follows.960graph-word-index
and1229fixed-wordbook decisions remain, as do the 1270registered and later bounds.

## Exact core and theorem
Use unchanged977first-six/first-four distinct-label lists, clockwise starting
ATthe reached pointer. Each list has its current label at rank0 and no other
occurrence of that same label. Consequently an output label equals the previous
output label iff that step's selected rank is0. The first output can be compared
to the public INITIALchart label; an excerpt whose preceding output is unseen
has an unknown first bit. No extra unencoded relocation/reset/null is allowed.

For one source indexv=4a+b, a in0..5,b in0..3, the two zero/nonzero indicators
partition the24values into sizes1,3,5,15:
- a=0,b=0: {0};
- a=0,b>0: {1,2,3};
- a>0,b=0: {4,8,12,16,20};
- a>0,b>0: the remaining15.
This is a conditional source-index class signature, not actual Voynich values,
sounds, word meanings or a complete inverse without the chart and phase.

Conversely, fix any finite requested visible output and any two-step source
index stream with the same rank-zero/equality mask (including a fixed initial
label). Construct a chart from left to right. A zero rank emits the current label
without moving. For a positive rankd, append d−1distinct filler labels, excluding
the current and requested labels, then append the requested label. It is now the
d-th first-occurring distinct label from the current pointer. Each positive step
lands at a new last constructed position. At the end append every alphabet label
not yet present. No requested step wraps, so the final completion cannot alter
any selected rank. With22labels and d<=5there are enough fillers. A bound on
positions is1+sum(positive ranks)+22 (deliberately not claimed tight).

This proves existence of a message-dependent chart for any compatible finite
pair. It does NOT prove that a fixed small chart can encode arbitrary chosen
native/source pairs, nor that a single chart gives two inverses. Enlarging the
chart can simply store the desired path and must be charged.

## Fixed artificial demonstration
No manuscript string is used. The toy source alphabet is A..V (22letters), SPACE
(index22), and #(index23) as an explicit end-of-message source symbol. The two
payloads are exactly HEAT OIL# and HEAT GIN#. This is an artificial finite alphabet
and two invented strings, not English-language coverage or historical instructions.
Their source-digit zero masks must agree; if not, stop without replacing messages.

Use the existing22working-unit LABELS as demonstration drawings only. Initial
label o. On each nonzero source digit, request the next label in the fixed cycle
[e,d,y,a,l,ch,i,n], skipping a label equal to the current one if needed. On a zero
digit, repeat the current label. Both messages use this SAMEsynthetic output.
For fillers use the original fixed working-label order, excluding the two endpoint
labels. Complete each chart with missing labels in that order, then pad the shorter
chart at its unvisited tail to the longer chart's length using the initial label.
This equalizes chart-position cost without changing either demonstrated path.
No ring/native key is selected for later data and no sourceword/glyph value is
exported from the artificial chart into Voynich.

Primary expected result is a verified equal-output/different-message witness
under two DIFFERENTequal-size charts plus the arbitrary-length zero-mask proof.
A demonstration failure invalidates this construction; no replacement message,
chart fitter, source or target is tried. The fixed inverse for each chart must
remain unique and recover its own complete payload including#. A native reading,
full statistical match or new word meaning is never an outcome here.

## Verification and consequences
Before examples, exhaustive short digit streams check the constructor and inverse
on a small fixed output alphabet with at least6labels. Source sequences retain
both row and column widths; resets only at whole-message start. Independent
validator imports no runner: separate chart traversal, digit extraction, integer
assembly, masks, equal output and chart length, all24source-index classes and
constructor-size bounds. Protocol, programs and RAWinput locked before examples.
Store full artificial charts and traces, so costs and all hidden positions are
visible. No native graph, transcription, source corpus, image or reserve is read.

If confirmed, retain the zero mask as a required future source/structure check.
Do not build a large chart solely to replay observed glyphs and call that a
reading. A useful candidate needs an independently specified construction/budget,
source/message contract and predictions beyond chart-fitting. This is consistent
with earlier nonidentifiability warnings, not a general impossibility of decipherment.
Original RAW977is not rewritten or rejected as an entire family. Local checkpoint
only under4Octoberexception; no publication/push; confirmed native meanings0.
