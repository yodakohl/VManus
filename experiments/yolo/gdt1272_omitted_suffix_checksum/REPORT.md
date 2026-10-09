# GDT1272 — readable checksum abbreviations fail the fixed comparison

**FIXED_CHECKSUM_SCREEN_EXCLUDED_ALL_READINGS.** The fixed omitted-suffix
checksum/escape rule recovers every one of6288 source words, but fails three
of the six inherited necessary conditions in every cached comparison: length
variation, marginal sign entropy and within-word conditional sign entropy.
This stops this particular source/wordbook/carrier. It does not reject all
abbreviation, Hebrew, checksums or meaningful Voynich writing.

## What the writer actually does
Keep the first two source letters; add the omitted length and a weighted
mod19 checksum of the omitted letters. Use this four-sign form only when the
shared fixed dictionary resolves it uniquely. Otherwise print an explicit
escape and the full spelling. The last of22 abstract sign labels is the escape;
short forms starting with that same label also take literal mode. Group spaces
supply boundaries. Source order, marker, modulus and dictionary were not fitted.
No sign has been assigned to a native glyph or word meaning. Any fixed bijective
renaming leaves the six tested statistics unchanged.

The full bare Deot projection and its2411-type wordbook are unchanged from the
previous work. Its one-to-one word frequencies already pass some old necessary
frequency comparisons; the four recipe profiles excluded in1202/1226 were not
silently reused.1229's failed branch-rank writer was not repaired or rescored.
The new mechanism is a fixed checksum of omitted content, rather than934's
shortest prefix or IP014's contradicted checksum of the remaining visible prefix.

## Costs, including the fallbacks

| Quantity | Count |
|---|---:|
| Source words |6288|
| Short-form occurrences |2992|
| Literal occurrences, escape included |3296|
| Original projected source letters |24668|
| Literal-only encoding with an escape per word |30956|
| Actual mixed output signs |25695|
| Shared dictionary entries |2411|
| Source letters stored in that dictionary |11126|
| Indexed checksum buckets |1776|

The mixed writer saves5261 signs against its own escape-only baseline, but
uses1027 signs more than direct one-letter/one-sign spelling: **4.1633% overhead**.
These are distinct comparisons. The dictionary and lookup structure are extra
shared resources, not added anew for every source occurrence. No claim of net
historical economy follows from the first comparison alone.

There are180 nonunique buckets containing393 source types and773 source-token
occurrences. These require literal spelling; the other literal cases include
short words and reserved-prefix cases. The categories overlap and are not summed
as disjoint causes. No ambiguous short record was guessed into a reading.

## Fixed statistical comparison

| Statistic | Writer | Observed cached native range across separate readers |
|---|---:|---:|
| Mean length |4.086355|Mean gate passes all3072 comparisons|
| Population length SD |0.837848|1.482660–1.687016|
| Top10 word share |0.116412|Some individual gates pass|
| Type share |0.383429|Some individual gates pass|
| Marginal sign entropy H1 |4.137637|3.793482–3.900530|
| Within-word conditional entropy H2 |3.865271|1.848707–2.321689|

The displayed range is a compact envelope, not pooled-reader data or an extra
statistical test. Every sample keeps its original reader/cell/seed identity.
The predeclared tolerances were SD relative25%, H1 absolute0.15, H2 absolute0.30
and the other unchanged1229 gates. Even the loosest H2 ceiling is2.621689.
There are zero SD, H1, H2 or six-way passes in each reader's1024 comparisons.
Mean length passes all; whole-word frequency equality is exactly retained.
4509/6288 output groups have length4, explaining the very concentrated lengths.
This is a fixed exposed-source operational mismatch, not a p-value or independent
confirmation across three transcriptions. Eighteen no-capacity cells stay untested.

## Verification and limits
Before the full run, the protocol, programs, inputs and artificial controls were
hash-locked at22:55:45 UTC on7October. Controls exercise checksum collision,
unknown words, short words, reserved-prefix words and eight malformed records.
The planned XXCA/XXAB collision was represented in the executable fixture as
AACA/AAAB because the artificial22-letter alphabet A..V has no X. This prefix
substitution is an explicit fixture deviation: the same omitted CA/AB suffixes
both have weighted sum5. No source rule or scored output changed after results.
The frozen protocol and control bytes are preserved rather than silently amended.

An independently written validator imports no producer code. It calculates the
checksum by reverse cumulative sums, rebuilds every dictionary bucket, decodes
every saved section, checks canonical re-encoding and exact word frequencies,
and recomputes all six metrics and3072 decisions. PASS. It verifies these cached
inputs; it does not reconstruct the old source projection or new manuscript
measurements. Source/input hashes were checked against their original manifests.
Same author; no independent philological or historical usability validation.

The complete wordbook is learned from the entire exposed source, not a blind
key. The digital projection already discarded points, punctuation and final
letter shapes. The test preserves its71 section/group sequences, not original
medieval page layout. No new native text, image, reserve, relation packet, corpus
or word meaning was opened or assigned. The prior whole-word/grouping limitations
and1223/1225 screen fragility remain. Confirmed native meanings remain0.

Decision: stop this fixed978 instantiation. Do not tune the modulus, pick a better
source alphabet order, add alternative spellings or change the dictionary after
the failure. The general incomplete978 proposal is not universally refuted; a
future genuinely different contract needs its own evidence and discriminator.
The new RAW979 ratio-path sketch is retained as incomplete and unreviewed, not
selected as the next successful writer. Local4October exception: no commit/push.
