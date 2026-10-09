# GDT1299 — positional source blocks cannot span the observed short/long lengths

**ALL_FIXED_SOURCES_PRIMARY_EXCLUDED.** The fixed ordinary positional writer fails on each of the four existing source projections for every block size, every source/output alphabet ordering, and every source base from22through82. This is a source-conditioned construction exclusion, not a Voynich translation or a rejection of all block ciphers.

## The human rule examined
The writer takes k consecutive source characters, including spaces and recipe line breaks, interprets them as a base-N number, and writes its shortest base22 numeral as one visible group. A shared key supplies k and both alphabet orders. A reserved source END plus right-zero padding pays for the final partial block. The reader restores leading source zeros to k positions, decodes all literal boundaries, and stops at END. No word dictionary, numeral meaning for a native word, or fitted letter values are used. This is a complete artificial text-preserving rule, not claimed historical practice.

## Why short and long groups conflict
A one-digit output has value below22. Since N>=22, all but the final source character of its full block must have the zero value. That is a run of k-1 identical actual source characters, whichever letter the unknown key calls zero. If the source has maximum run R, then k<=R+1. For a two-digit output such as the strict whole ol witness, the weaker bound is k<=R+2.

An output with L digits needs value at least22^(L-1), while any source block is smaller thanN^k. Consequently N^(R+s)>22^(L-1) is necessary, for short tier s=1or2. The bound is deliberately generous: it ignores the actual zero-letter identity, block phase, all other groups and other constraints. A necessary base lower bound is not an attainable minimum code or a fitted key.

| Fixed source | Recipes | Stored words | Characters including declared separators | Character types before END | Longest equal-character run R |
|---|---:|---:|---:|---:|---:|
| b4 |271|19,315|98,952|31|3|
| w1 |263|18,141|92,154|33|3|
| bs1 |268|21,963|114,267|32|3|
| gr1 |252|21,512|108,576|33|3|

All sources fit inside the allowed alphabet budget including END. These are the complete old1177projected recipe texts, with one explicit space between stored words and one newline between recipes. They are neither diplomatic original handwriting nor nominated actual plaintexts. No source was normalized again, added or substituted after the result.

## Native witnesses and the stronger robustness check
The unchanged strict1233cache has252one-unit occurrences in ZL,300inIT and422inRF. These are not pooled. All three retain f82v.12G009 `qoteytyqoky`, eleven working units. The earlier1294 image check supported its local inner seam only; it did not independently establish every sign or an authorial word boundary.

Using that fixed eleven-unit group and any retained interior one-unit group gives k<=4. Even at N=82, the maximum block value is below45,212,176, whereas eleven output units require at least26,559,922,791,424. The optimistic required source base is at least2,271, far beyond the frozen82cap. At N<=82 and k<=4, an output can have at most six units.

The separate prespecified weaker tier ignores all one-unit groups and uses only whole ol:252ZL,371IT,340RFoccurrences. It gives k<=5 and a necessary source base of at least485. Thus the primary contradiction survives that weaker short witness; it does not rest on a rare isolated sign. The length11 premise remains explicit.

The prespecified longest-form sensitivity has Lmax13ZL/12IT/13RF. Its necessary bases are10,649/4,917/10,649 for s=1, and1,667/899/1,667 for s=2. It is not needed for the main exclusion. ZL/RF's joined oteeedyqokeey differs from IT segmentation, so these maxima remain separate, exact-reading-dependent sensitivity evidence, not independent replication.

## What was checked and what remains conditional
The independent validator reconstructs all four source streams with a different assembly/counting method, finds runs by regex rather than groupby, reparses61,181native raw groups, and verifies all48bound rows by enumerating the admissible N/k inequality combinations. It checks10,746integer cases; this is validation work, not10,746decipherment attempts. The runner's artificial5632leading-zero cases and2912message roundtrips preserve an explicit final-padding counterexample: a terminal END/zero block can be short without a long run in the actual source. Therefore the short witnesses must be nonterminal within the SAME continuing code stream. Strict interior placement supplies this only under the declared no-hidden-reset document contract.

The producer reviewed the algebra without empirical counts or native rows. All protocol/code/input hashes were fixed before the new run counts and native maximum selection. The choice of the11-unit example was source-informed and declared in advance, not a blind discovery. Source/tokenization/software PASS is not an independent palaeographic judgment.

Retain the literal22working-unit, one-source-block/one-visible-group, shortest positional numeral, fixedk and exact-source premises. Multi-unit digit spellings, variable blocks, nonterminal padding, arbitrary lookup codes, hidden message resets or changed word boundaries are outside this result and are not selected as repairs. A different source with longer repeated-character runs is not universally excluded by these four controls. No number-word assignment or language exclusion follows.

IDEA930's per-character head/tally failure,001's observed-word segmentation,1269's output-pair table bound and1202's whole-word frequency test remain distinct; no old failure was silently rerun or overwritten. The present result avoids the pooled frequency thresholds already qualified by1223/1225. Decision: do not fit a key or build a larger decoder for this unchanged radix construction on these sources.

No new source, image, reserve, f84/f84r/f116v or semantic relation was opened. Source code, protocol, old-input hashes, source-run witnesses and exact native witness IDs are supplied for replay. Publication must pass the exact staged privacy check.
