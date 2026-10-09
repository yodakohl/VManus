# GDT1268 — word-column differences are reversible but too unpredictable

**FIXED_WORD_COLUMN_SCREEN_EXCLUDED_ALL_READINGS.** The single fixed writer
recovers every one of6288projected source words in71sections exactly. It needs
no whole-word dictionary, but its within-word conditional sign entropy is
4.360984909bits. Even the greatest cached native allowance is only2.621689042.
All three readers have zero joint matches under the predeclared necessary screen.
No ring order, alignment, reset, source or glyph assignment was changed afterward.

This rejects the particular source/writer/screen conjunction, not every differential
notation, Hebrew, a historical language or all possible uses of word memory.
It is a new artificial source-control result, not a manuscript translation.

## A complete small writer
Keep the previous DECODED word. Number the fixed22base source letters on a ring.
For every letter in the new word, write its clockwise displacement from the
letter in the same position of the previous word; missing previous positions
use reference0. The output has the new word's exact length. After the whole word
is finished, replace the entire previous-word buffer, discarding any old tail.
Each source section resets to an empty buffer. Source spaces/section boundaries
remain visible; there is no hidden word-length message or wordbook lookup.

The reader adds each written displacement to that same previous-word coordinate.
Induction on words proves exact recovery for any finite sequence over the fixed
source alphabet, not only words already in the source vocabulary. Ring addition
works modulo22 without a prime-modulus premise. The state stores a whole word,
not one previous letter; temporary current-word storage is also required.

A hand example over A/B/C/D/E numbered0..4:

| Source word | Previous word | Written residues |
|---|---|---|
|ABC|empty|012|
|AC|ABC|01|
|ACDE|AC|0034|
|ACDE|ACDE|0000|

The third row demonstrates that the third letter of the earlier ABC is not
silently retained after the shorter AC. A zero-only output has the predecessor's letters only where its new
length overlaps; at new positions it decodes to rank0. Only equal lengths make
zero-only output mean an exact repeated source word. Repeated nonzero outputs
are permitted and produce coordinatewise arithmetic progressions of source words.
Thus the old927mandatory-prefix idempotence contradiction does not apply.

Residues0..21 may be bijectively represented by the existing22working signs;
src/run.py declares their display order. No native mapping is fitted or identified.
All three scored quantities are invariant under such a global sign renaming.
Different working-sign labels therefore cannot repair this result. The cipher
packet stores explicit residue arrays, avoiding confusion between an EVA label's
ASCII length and the number of working units.

## Fixed source and outcome
Input is exactly1228's complete bare Deot digital-edition projection,6288words
and24668base letters. Its points, editorial bracket distinctions and punctuation
were already removed by that old projection and are not recovered by this writer.
It is an exposed source control, not an identified Voynich original or a universal
representative of Hebrew. Logical source-letter order and section resets were
fixed before encoding; no reverse-word alternative was tested.

| Metric | Fixed output |
|---|---:|
|Mean group length|3.923027990|
|Population length SD|1.337506126|
|Within-word conditional sign entropy|4.360984909bits|
|Distinct groups /6288|4920 /6288|
|Top10group occurrences|127 (2.0197%)|

Word diversity and top10share are declared diagnostics, not extra decision gates.
They must not be compared to unmatched sample sizes and promoted into another
statistical rejection. The entropy condition alone fails every eligible sample.
The original source's logical H2was3.683285bits; this particular transform raises
local unpredictability despite preserving all projected source content. A change
in first-order conditional entropy is not information loss or translation quality.

| Reading | Cached comparisons | Mean-length passes | SD passes | H2 passes | Joint passes |
|---|---:|---:|---:|---:|---:|
|IT2a|1024|1019|1024|0|0|
|RF1b|1024|1024|1024|0|0|
|ZL3b|1024|787|1024|0|0|

Each comparison contains6288eligible native groups. These are the unchanged1228
samples,128page-order seeds in each of eight scoreable cells per reader, including
pooled and single-metadata strata. All18insufficient-capacity cells remain untested.
Readers are alternate transcriptions; cells and samples overlap.3072checks are
not3072independent trials or a significance estimate. Mean±20%,SD±25%,H2±.30were
unchanged. ANY actual jointly matching sample would have prevented that reader's
exclusion; no marginal extrema were mixed into an imaginary target sample.

## Why this is not another execution of the earlier failures
001's old STOP_DIFFERENTIAL_RECORDS is a cost-based literal versus KEEP/SUB/DEL/INS
code over native groups with line/page scope.927copies a capped initial substring
of the prior sourceword.941transposes shrinking vertical word columns and pays
row endings.1180and1230use previous-letter state;1217's one-ring writer references
the immediately preceding decoded unit. Here every position references the same
position of a whole prior word. These are different output laws; their original
failures remain unchanged. No prior code was patched or source substituted to
rescue its result.237's native differential message proposal is not selected.

The motive was to test whether one explicit previous-word buffer could vary
spellings without1193's2130-entry learned table. It can, but the declared source
output does not have the required within-word predictability. The unbounded
previous-word memory is a real cost; no medieval attestation, writing speed or
paper-table usability is claimed. No blanket minimum-memory theorem follows.

## Reproduction and verification
The protocol and both programs were hash-locked before the single source run.
Original1228source-projection, target-result and validation hashes match their
published manifest. No native sample was regenerated.60879smallalphabet variable-
length word sequences passed source-free roundtrips, including the hand fixture.

The independent validator imports no primary functions. It walks the source ring
to recover each forward displacement, adds to decode each word, verifies whole-
buffer replacement and all71source/encoded section hashes, then reconstructs
length moments, the full18380within-word pair count table, joint-minus-context
entropy and every cached gate. All checks PASS. That is numerical/source fidelity,
not independent historical or semantic confirmation. The producer's conceptual
inverse review was delivered before the source run without target/source counting;
root's later PROOF_REVIEW_RECEIPT preserves those messages. No earlier formal
idea-card registration is claimed.

RESULT.json contains exact pair counts, frequency diagnostics, all cell decisions
and section hashes. CIPHER.json.gz contains the71complete encoded sections;
REGISTRATION_LOCK.json binds the code and immutable inputs. Run src/run.py then
src/validate.py in an isolated copy. No new rawTSVquery, image, native selector,
f84/f84r/f116v or reserve. Confirmed native meanings remain0.

The allocated19:55–20:35UTCwindow includes earlier route selection, implementation,
validation and local closure;19:55is a conservative allocation start, not a measured
exact task-start timestamp. Local4Octoberexception: no commit/push. Stop this fixed
writer after the failed screen. No automatic reverse alignment, weighted ring,
added padding, new corpus or extra state table follows from its reversibility.
