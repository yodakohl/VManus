# GDT1326 — a reset prefix-only formatter cannot generate the fixed ol/oldy pair

**RESET_PREFIX_GAP_RULE_EXCLUDED_ALL_READINGS**, conditional on the declared22working units, strict group boundaries and continuing source stream within each witness line. The preselected short/long pair is present on the same page in every reading. These are alternate transcriptions of one manuscript, not independent replications.

| Witness | Exact location in all three readings | Complete group | Original next group |
|---|---|---|---|
| Short, nonterminal | f75r.12 G006 |ol|cheey (G007)|
| Proper extension | f75r.43 G003 |oldy|qokain (G004)|

Both groups and their followers belong to the unchanged strict panel and have definite outer spaces. Their literal working-unit sequences are(o,l)and(o,l,d,y). No image was newly inspected, no physical glyph identity was independently established, and no word or letter meaning is assigned.

## The exact writing family

A shared one-to-one22symbol alphabet writes every source symbol, including a designated source-space symbol if present, as a drawing. A separate deterministic formatter considers only the glyph prefix written since the last inserted gap. It inserts a gap immediately when that prefix satisfies its stopping rule, then resets to the SAMEstate. The stopping rule may vary by page and may remember arbitrarily much of the current prefix. It cannot use the next symbol, earlier groups, intended word endings, line position/width, running counts, randomness or a separately varying state.

The reader concatenates the drawing groups and reverses the alphabet map. This supplies a complete content-preserving hypothetical family in which visible gaps need not equal source word gaps. A finite message may flush its last incomplete group; line wrapping itself may not split groups. There are no hidden source-message ends between the witness groups on a physical prose line. These are model premises, not historical claims.

## Why no larger prefix table can fix it

On f75r, emitting the short olgroup before its following group requires the formatter to stop after the prefix(o,l). When producing oldyon that same page, the formatter starts in the same state and reaches exactly the same prefix after its first two units. It must therefore stop again, splitting the proposed longer group. The required stop/no-stop decisions conflict.

Only the short occurrence needs a continuation witness: otherwise olcould be a permitted final flush under a rule that normally waits for oldy. Here the actual same-line following group rules out that escape under the declared continuous-message premise. Even making oldya final flush would not avoid the earlier mandatory cut. Renaming every source/drawing symbol bijectively preserves the prefix relation.

This is the ordinary prefix-freedom argument for OUTERautomatic groups, applied to a specified formatting mechanism. It is not a new coding theorem or a discovery that these word forms exist. GDT1234/1248concern prefix-free INNERletter codes concatenated into words; their whole words may be prefixes of other whole words. They remain valid. GDT1196and1203supply source-word/vowel-run or shifted source-boundary information that this formatter explicitly lacks.

## Fixed extraction and verification

Only olandoldywere nominated from existing exact-form profiles before extraction. The procedure required an original-index-consecutive strict follower and a shared exact page, then chose the first page and first IDs lexicographically. No post-result replacement pair or whole-corpus prefix search was used.

| Reading | Eligible ol / oldy occurrences | Pages containing both eligible forms |
|---|---:|---|
| ZL3b |202 /3|f75r|
| IT2a |321 /5|f75r, f75v, f88r|
| RF1b |254 /3|f75r|

These are the explicitly filtered nominated occurrences, not the broader word-profile totals. Counts are descriptive; one verified contradiction suffices for this deterministic model. The independent validator reconstructs all eligible events from original915adjacent source windows, checks1576occurrence/follower joins, the selected witnesses and the exact prefix relation. Validation PASS. Sixteen exhaustive source-free stop assignments confirm the obstruction on a tiny analogous case; separate fixtures preserve the final-flush exception and show that lookahead is genuinely outside the result.

## Decision and limits

Do not implement or enlarge a deterministic prefix-only gap rule that resets identically after every visible group. More memory of the SAMEprefix cannot resolve this counterpair. Retain the original transcription/unit assumptions and the no-hidden-message-end premise.

The finding does NOT prove that gaps have semantic meaning, that written groups are natural-language words, that spacing needs a complex machine, or that all automatic segmentation fails. An ordinary writer's knowledge of the intended word, lookahead, geometry, carried state or another justified unit/group binding can change the inputs. None is fitted as an automatic repair. A source-free lookahead escape in the fixtures demonstrates the narrow scope rather than supplying a Voynich explanation.

Only existing guarded text caches were reused. No raw mixed TSV, new image, f84/f84r/f116v/f1rbody,327/336body, reserve or semantic relation packet was opened. Protocol, programs and input hashes were locked before extraction. Manifest commands reproduce the source-bound certificate and validation.
