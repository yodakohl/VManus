# GDT1310: exact single-pair allograph compatibility

**EXACT_SINGLE_MERGE_COMPATIBILITY.** Fully checking each proposed pair merger
adds two contradictions in ZL3b, one in IT2a and none in RF1b to1295's necessary
literal-neighbor graph. Every old inequality remains. The remaining individual
mergers have explicit finite lookup witnesses, not identified native letters.

| Reading | Unordered pairs | Old literal conflicts | Complete single-merge conflicts | Additional | Compatible single merges |
|---|---:|---:|---:|---:|---:|
| ZL3b |231|171|173|2|58|
| IT2a |231|177|178|1|53|
| RF1b |231|178|178|0|53|

There are48pairs that pass separately in all three readings. Their lookup
functions may differ; readers are alternate transcriptions of one manuscript,
not independent replications or a pooled corpus. A compatible pair is not
necessarily a plausible graphical equivalence. No source sound or meaning is
assigned, and the old<=11alphabet exclusion remains unchanged.

## The exact rule and why a missing edge was insufficient

Use1295's unchanged model: one visible working unit per source letter, unchanged
word boundaries/order and one global inverse psi. The deterministic forward
form may depend on exact page selector, word unit-length, index, and immediate
left/current/right SOURCEletters. It has no whole-word identity, longer memory,
random choice, line geometry or different unit segmentation.

For each pair x/y, merge ONLY those two inverse values. Now their occurrences
in neighboring slots also merge. All observations having the same resulting
source context must still produce the same written center.1295checked only
contexts with already identical VISIBLEneighbors; it explicitly warned that
neighbor merging could introduce additional collisions.1310tests that omitted
step exhaustively for each individual pair, without a color search or cap increase.

A contradiction persists under every coarser partition containing x=y: more
merging cannot separate two already identical source inputs, while the actual
written outputs remain different. Thus each failed pair is forbidden in every
coarser inverse UNDER THIS LOCAL RULE. Compatible pairs need not work together.

## New retained counterexamples

| Reading/pair | Conflicting contexts | Physical leaves | First saved same-page case |
|---|---:|---:|---|
| ZL d/i |1|1| f105v: ckhddl versus aiil, target index2 |
| ZL i/o |2|2| f106v: aiiin versus looin, target index2 |
| IT e/i |64|25| f102v2: oeees versus aiiin, target index2 |

Indices are zero-based. Every full witness retains exact source IDs, original
flanks, written centers, word forms and mapped context. All negative and
compatible pair rows remain in PAIR_RESULTS.json, not just these examples.

The IT e/i example is especially transparent. oeees and aiiin each have five
working units. At index2 their local written triples are e/e/e and i/i/i.
If e and i decode to one source value E, both inputs become E/E/E on the SAME
page, at the SAME length/index, yet one output is e and the other i. That
contradicts deterministic local selection. Farther word endpoints o/s versus
a/n differ, but the stipulated function does not receive them. This is not a
claim that a longer-context, optional or differently segmented system is impossible.

ZL's d/i addition rests on one physical leaf; this fragility is retained rather
than discarded. ZL i/o has two-leaf support. IT's e/i addition spans25leaves.
In ZL/RF, e/i were already excluded by literal-neighbor cases, so the ITresult
supplies the previously missing same-model contradiction rather than three new
independent discoveries. No new image reading or transcription correction was made.

## What compatibility really buys

If a pair has no conflict, store each observed merged-center source context's
written output; unseen contexts emit the lexicographically smaller pair member.
Every other source letter emits its sole visible representative. This is a
complete finite writer with a fixed inverse for arbitrary input source words,
and reproduces the observed groups at their given pages. It is deliberately
an existence witness with paid context lookup, not a recovered human rule.

Two post-result examples show the cost:

| Compatible pair | Reading | Observed merged-center contexts | Nondefault lookup entries |
|---|---|---:|---:|
| a/q |ZL|4576|722|
| a/q |IT|5094|749|
| a/q |RF|4673|732|
| cfh/f |ZL|223|187|
| cfh/f |IT|264|225|
| cfh/f |RF|226|189|

Default is the fixed lexicographically smaller visible member, not an optimized
human spelling convention. Digests bind all observed context/output rows.
No claim that a/q or cfh/f ARE allographs follows from these tables. The lack
of a conflict can reflect restricted/sparse occurrence contexts and the generous
page/length/index inputs. No held-word or held-page generalization is measured.

For comparison, cph/p is contradicted on f20r in all readings: qocphy and chopy
share length4, index2 and literal o/y flanks but differ cph versus p. Their
more-distant first units differ and remain outside the model. This was already
an old edge, not a new discovery. Similarly k/t, ch/sh, l/r and m/n retain old
contradictions. No actual phoneme inventory can be read off those conditional edges.

Single-pair compatibility does not compose freely. In the source-free example
axb/cyb on one page, merging x/y alone works and merging a/c alone works, but
merging both makes identical source words require different written outputs.
Therefore48common individual possibilities are not a48-choice alphabet recipe.
No joint partition, chromatic number or minimum native alphabet was computed.

## Proof, source and verification

Only the unchanged1233strict Pcache,179-selector allowlist and1295saved edge
metadata were used. The693maps cover278564positions in61181groups. No new raw
TSV, image, plaintext corpus, reserve or old327/336body was opened; f84/f84r,
f116v and f1rbody remain excluded. Textual f106v evidence is within the existing
text allowlist; it is not new image access.

Protocol/code/input hashes were sealed before the pair run. The bounded producer
checked the monotonic-obstruction and complete-default-writer proofs source-free
before execution, including the joint-merger counterexample. The independent
root-authored validator imports no runner: integer source maps, sort/group full
contexts and dynamic raw segmentation reproduce all693decisions,529conflict
witnesses,164compatible lookup digests and4875distinct raw parses. Source-free
fixtures cover literal and newly collapsed neighbor conflicts, page separation,
62valid contextual-writer words and the monotonicity/joint-merger distinction.
PASS concerns finite consistency and source fidelity, not palaeography or meaning.

## Decision

Retain the stronger pair-specific restrictions before proposing graphical variants.
Do not call an absent literal edge a compatible merger without this full context
check, or call a compatible merger an economical human writing rule. The old15/13
lower bounds and<=11failure are not reopened; no larger-alphabet fit is selected.
Remaining questions concern a motivated compact rule or independently supported
physical unit binding, not automatic table compression or added context fields.
No translation was obtained. The45minute inclusive budget ends15:37:36UTC.
