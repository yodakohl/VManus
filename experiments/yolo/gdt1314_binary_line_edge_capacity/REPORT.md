# GDT1314: line-edge words eliminate the m signal key

**READER_SPECIFIC_EDGE_CAPACITY.** Adding all eligible line-edge groups to the
unchanged strict interior panel eliminates the previously common m-partition
under the fixed32-entry codebook. It now requires37/40/40entries. The singleton
cfh-partition alone remains capacity-feasible separately in all three readings.
This does not identify a native signal alphabet or decoded source character.

| Signal1 (all other working units0) | ZL3b strict → union | IT2a strict → union | RF1b strict → union |
|---|---:|---:|---:|
|n|29 →40|31 →37|already excluded|
|m|22 →37|22 →40|22 →40|
|n,m|30 →49|already excluded|already excluded|
|cph|31 →32|32 →32|32 →33|
|cfh|26 →27|26 →27|27 →28|
|cph,cfh|31 →33|32 →33|already excluded|

Every reader-specific survivor was checked:6/5/3key cases, not a selection of
only the three common keys. The added groups cannot reduce the number of distinct
codewords, so none of the previously excluded keys can return. This exhausts the
same global two-class/32-entry family on the expanded panel. Reader-specific
survivors are cph and cfh for ZL/IT, cfh for RF. Different readings describe one
manuscript; separate capacity is not one joint decoder fitting all readings.

## Why this is a useful change of test

1312used only words with definite spaces on BOTH sides. That excluded initial
and final words. The earlier801/802work already showed a physical line-edge
preference for terminal m, with learned family effects. It therefore matters
whether the interior-only m-key also covers clear edge words. This tests that
omitted population using the same alphabet, key family and table budget, without
assigning any meaning or changing a failed model to obtain a fit.

The fixed extension adds6232/7293/6301groups (2639/2952/2681surface types).
All are prose, have definite interior gaps and/or explicit LINE_START/LINE_END,
contain only literal characters, and parse uniquely into the unchanged22units.
Strict groups remain19332/22528/19321; union sizes25564/29821/25622.
No uncertain or drawing gaps were bridged, no strings corrected or shortened.
The maximum unit lengths in the unions are13/12/13.

For example, the retained edge form `mol` produces100 under the m-key; it was a
new codeword relative to the strict panel. `damo` produces0010; `qokomo` produces
000010. Different positions of m and different full lengths consume different
rows. Full per-code witnesses and counts are retained, including all15/18/18new
m-key codewords. These are transcription-based formal consequences, not new
manual confirmations of the rare forms or their atomic divisions.

## Boundary assumption and retained positives

This test assumes physical line edges delimit COMPLETE visible codewords. If a
single codeword is instead allowed to wrap unmarked across lines, these edge
pieces cannot automatically be treated as wholes. That different construction
is not refuted here and has not been adopted. Unlike1313's run interpretation,
this union-capacity argument requires no continuous source record: different
records still use the same fixed global key and table.

1312's original strict-panel capacity result remains true;1313's conditional
six-character/three-letter run obligations remain true for its original panel.
There is no general rejection of binary ciphers, a32-character plaintext alphabet,
or any language. The surviving cfh-partition still allows arbitrary within-class
glyph choices and provides no explanation of the rich native form distribution.
Capacity is not a complete successful writer or a translation. No automatic
larger table, source-key fitting, glyph regrouping or record repair follows.

## Verification and scope

A source-free review checked monotonicity and edge assumptions before counting.
The contract, programs and source hashes were locked before the native run.
The independent same-author verifier uses iterative parsing and length/integer
codes instead of memoized parsing and bitstrings. It independently reselected
19826edge groups, rejoined all61181strict groups to915source records and checked
all14key cases, code counts, added-code identities and source witnesses. PASS
establishes reproduction of the conditional count, not palaeographic truth.

No new corpus, image, rawTSV, reserved material, f84/f84r/f116v/f1rbody or old327/336
body was accessed. All inputs are previously exposed guarded caches. Zero word
meanings assigned. Inclusive budget07:12–07:47UTC10October2026 includes publication.
