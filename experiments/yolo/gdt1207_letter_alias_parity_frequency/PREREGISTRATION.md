# GDT1207 — fixed letter aliases, parity and necessary frequencies

Preparation2026-10-05 14:37:25UTC; total budget30minutes through15:07:25UTC,
including predecessor/parity review, implementation, source validation and local
closure. Only the previously unexecuted ALT arm of1197 is selected.1197's old
deferred report and1206's failed MTF decision remain unchanged.

## Decision note and assumptions

Positive construction: each of two aliases always names the same ordinary
source letter; no native value is assigned. Unlike moving MTF ranks, a complete
unit-aligned repeated code part therefore has one fixed underlying letter string.
But identical glyph substrings are not automatically unit-aligned parts.

Known counterconstraint: GDT1200 has exact whole ol and olol. Under the proposed
single fixed non-erasing uniquely decodable letter-unit carrier, one source word
per written group, both whole strings must be concatenations of full code units.
Then the olol parse must equal the ol unit parse twice. Valid strict alias
alternation requires each ordinary source letter in that decoded ol block to
occur evenly. This is an obligation, not a contradiction or a proposed reading.
It can be satisfied by an even-parity block. No native unit, letter, sound,
lexeme, synonymy or morphological cut is thereby selected. Similar reasoning
for B Bdy or BBdy additionally needs B AND dy to be valid complete code strings;
do not assume this from a free interior substring.1201's multiple transparent
chunking/one message distinction and known spacing disagreements remain.

Unknown: do the fixed26independent ticks produce the necessary whole-word
frequency distribution while preserving all source contents?1202's at-most-two
WHOLE-word variants does not cover per-letter ticks: different entry states can
produce more than two variants of a whole word.1206's MTF failure does not answer
this different fixed-value rule.1196/1180/931/928failed bindings remain. The raw
illustrative glyph palette's q-o/final-y defects are not solved or selected.

Smallest adequate test: complete ALT encoding/recovery on the same four sources,
plus the same three fixed equality-frequency metrics as1197/1206. Failure stops
this source/reset/fixed-carrier rule before any glyph table; success retains only
necessary frequency compatibility and does not establish native word structure.
No glyph fitting, alternate reset, arbitrary state filters, new source, threshold
repair or control cascade follows. The finite fixtures check the parity argument,
not historical handwriting or meaning. Local construction checkpoint only.

## Fixed writer

Input exactly1177 artifacts/SOURCE_TEXTS.json: b4,w1,bs1,gr1, all complete stored
recipes and exact word tokens/order. Reset all26ticks to0 at each recipe; preserve
one output group per source token including punctuation. Spaces do not update.
No source normalization/new acquisition, native extraction, image or reserve.
f84/f84r sealed;f116v unadmitted.

For lowercase ordinary letter index i (a=0,...,z=25), emit 2*i+tick[i] and flip
only that tick. These52aliases each have the fixed inverse letter floor(unit/2).
The56additional characters are exactly ordered RAW938 input_contract inventory;
emit52+j and update no tick. Unlisted characters are COVERAGE_FAILURE, never
silently deleted or added to the table. The canonical decoder checks each
alias against its own recovered-letter state and rejects wrong parity. Plain
letter recovery can ignore ticks, but canonical validity cannot.

Cost:52ordinary units,56auxiliary units and26writer ticks (2^26possible global
states, not two states and not a huge learned table). Canonical checking also
tracks ticks. No actual native glyph lengths or hand-writing speed is established.
Any fixed uniquely decodable carrier preserves the full unit-word equality
partition and the three tested statistics. Stateful/ambiguous/erasing carriers
are outside the claim. No native edit-distance or entropy score on abstract units.

## Fixed sample and numerical decision

Encode all recipes for full recovery. For each book take first8000whole groups
in original order, preserving recipe boundaries and any final partial recipe.
Count distinct whole unit sequences/8000, top-ten sequence counts/8000, and exact
adjacent whole equality divided by within-recipe sample pairs. No cross-recipe
join. Original source-word metrics remain descriptive only.

Compare separately with unchanged1174 RESULT.json target summaries: absolute
inclusive tolerances .05types, .05top10 and .01exact-repeat. Use integer counts
and rational comparisons. All4books×3readers×3metrics must pass. One failure gives
ALT_FREQUENCY_SCREEN_FAIL, else ALT_FREQUENCY_SCREEN_PASS. Coverage/encoding/
validation failure is a different status. No statistical significance claim or
complete ten-metric writer pass is possible here.

## Validation

Lock source/proposal/contract/runner/validator hashes before encoding/counting.
Runner uses a26-bit integer and bit flips. Separate same-author validator uses
independent per-letter occurrence counts/parity, decodes from output without
plaintext assistance, compares all source words and independently reconstructs
frequencies/decisions. No runner import. Retain complete source-ID rank books,
frequency partitions, receipts, all36conditions, including failures and positives.

Fixed fixtures: a; aa; abb abb abb; abba abba abba; neu xylophon xylophon xylophon;
Ä 7 , a a; aÄa aÄa aÄa. First/third forms of any directly triple-repeated word
must match. First/second forms match iff every ordinary source letter appears
an even number of times; auxiliary symbols do not affect parity. Different
source words cannot share a whole emitted unit sequence because unit values
are fixed. Deliberately invalid [a-alias0,a-alias0] must be rejected. Reset is
checked by encoding separate recipes with the same source sequence.

The native ol/olol obligation is a conditional proof from existing whole forms,
not a new manuscript census or inverse key search. All word meanings stay
unassigned. No scored semantic relation packet or independent confirmation.
