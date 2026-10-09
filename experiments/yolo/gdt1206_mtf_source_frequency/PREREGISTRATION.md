# GDT1206 — fixed source-forward MTF frequency screen

Preparation began 2026-10-05 14:12:08 UTC with the live space-input question.
Total budget through 14:52 UTC includes selection, implementation, validation
and local closure. Select only the previously unexecuted MTF arm of GDT1197;
that historical deferred report is unchanged and ALT remains unrun.

## Decision note and retained constraints

The contemplated f108v space measurement is not selected. IDEA000200 records
written remaining characters/groups, not independently available writing room.
No intended right boundary is bound for this pair. The earlier primary
`docs/visual_overview/NEXT_STEP.md` already withdrew width as main priority:
positive width does not distinguish meaning from writing convention. No image
is opened or measured here; space-pressure mechanisms are not all refuted.

IDEA000939 defines one content-preserving writer without a word dictionary.
Unknown: do its history-dependent rank words satisfy the necessary frequency
screen under any fixed uniquely decodable unit carrier? GDT1202's at-most-two
whole-word alias bound does not cover the full moving alphabet state. A failure
stops this precise source/reset/fixed-carrier contract before any glyph table;
a pass preserves only eligibility for later selection. No pass could establish
daldy morphology, q-o, final y, a historical writer or a native meaning.

GDT001's failed six-pack, order-2, physical-line-reset native inverse MTF search
remains failed. This uses known source text, 26 ordinary ranks and recipe resets;
no native key search. GDT1196/1180 failures, 1193's dictionary costs and 1194/1195
failures remain. GDT1204/1205 do not favor MTF over content or other mechanisms.
A mere demonstration that MTF reverses would add no new research decision.

## Frozen source and transformation

Input: unchanged GDT1177 artifacts/SOURCE_TEXTS.json, books b4,w1,bs1,gr1.
Every complete stored recipe resets the list to abcdefghijklmnopqrstuvwxyz.
Each exact source word, including a standalone punctuation token, becomes one
output group. Spaces do not update memory. No new source, normalization, native
projection, image or reserve is accessed; f84/f84r sealed and f116v unadmitted.

For an ordinary lowercase letter: emit its zero-based current rank 0..25,
then remove that letter and put it first. The additional-character inventory is
exactly the 56 ordered characters of RAW939; emit 26+j for additional index j
and leave the list unchanged. Any unlisted source character is COVERAGE_FAILURE,
not silent deletion or expansion of the inventory. The decoder obtains state
only from the output it has already decoded. Full exact source words/order and
recipe boundaries must be recovered. Original manuscript spelling and original
source whitespace are not claimed: source is the existing edition projection.

Learning/operation costs: 26 rank units, 56 auxiliary units and a moving list of
26 entries, with up to 26-position search per ordinary character. 26! possible
orders do not require a 26!-entry dictionary, but hand practicality is untested.
No glyph carrier is selected; the raw illustrative palette's q/y defects remain.

## Fixed sample and decision

Encode all complete recipes for reversal. Per book take the first 8000 groups
in stored order, retaining recipe boundaries and a possible final partial recipe.
Calculate distinct whole unit sequences /8000, the ten largest whole-sequence
counts /8000, and equal adjacent whole sequences divided by all within-recipe
sample pairs. Never join across recipes. Record unchanged source-word statistics
descriptively, not as another candidate.

Compare separately with each of the three already exposed GDT1174 RESULT.json
target summaries. Absolute inclusive tolerances remain: .05 for type ratio,
.05 for top10 share, .01 for exact adjacent repetition. Use exact integer counts
and rational comparisons against target counts/rates. All 4 books × 3 readers
× 3 metrics must pass. One failure gives MTF_FREQUENCY_SCREEN_FAIL; otherwise
MTF_FREQUENCY_SCREEN_PASS. Not a significance test or ten-metric PASS. Encoding,
validation and coverage errors are distinguished from frequency failures.

If a fixed unit code is uniquely decodable, different unit strings cannot print
the same glyph string. Thus any such carrier leaves these whole-word frequency/
equality statistics unchanged. This does not preserve glyph lengths, edit
 distances or entropy. A state-dependent or non-uniquely-decodable carrier is
outside this claim and not an automatic repair here.

## Validation and stop

Register source/proposal/contract/runner/validator hashes before encoding/counting.
Store complete rank groups per source recipe, sample-frequency counts, full-source
receipts and all reader comparisons, including failures and compatible values.
Separate same-author validation reconstructs ranks by last-use timestamps,
decodes without plaintext, compares complete words, checks source and code hashes,
and independently recomputes sample counts and decisions. No runner import.

Tiny fixed fixtures: a; aa; abb abb abb; neu xylophon xylophon xylophon; Ä 7 , a a.
Verify reset by separate recipes. For any word repeated three times without a
reset, second and third rank strings must agree; adjacent repeated ordinary
letters use rank0 after the first. Software identities, not new native constraints
or human usability evidence.

No carrier fit, extra reset, relaxed tolerance, other source or automatic ALT
run follows. All native word meanings remain unassigned. Local construction/
selection checkpoint under the current-route user exception; no publication claim.
