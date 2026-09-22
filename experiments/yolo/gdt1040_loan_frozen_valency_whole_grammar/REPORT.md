# GDT1040 — the fixed six-production loan grammar fails

Decision: **REFUTED_FIXED_PREFIX_VALENCY**. No global exact-form category
assignment parses any of the three complete registered source units. This
closes the specified syntax, before assigning the47 missing whole-form meanings.
It neither translates the paragraph nor refutes every possible loan account.

The seven inherited guesses remain unchanged: shedy=assetA, qokaiin=titleholderB,
lchedy=borrowerC (nouns); chedy=permission to useA, qokedy=duty to returnA,
qoteedy=title remainsB (zero-argument statements); qokeedy=custody deliveryAtoC
(one noun argument). Unknown forms may only be noun, unary head or binary head,
consistently across every occurrence. Six prefix productions permit complete
clauses and their concatenation; no free nouns, implicit arguments, new P0s,
aliases, skipped groups or line resets are available. Argument sorts and
referent identity were relaxed, making this a necessary syntax test only.

| Complete source | Groups | Recurrent assignments checked | Full parses | Longest complete prefix |
|---|---:|---:|---:|---:|
| Old projected ZL |72|81|0|25|
| Diplomatic ZL3b |72|81|0|25|
| Diplomatic IT2a |71|81|0|25|

The joint model is also UNSAT. Every one of243 category-assignment rows is in
[ALL_ASSIGNMENTS.json](artifacts/ALL_ASSIGNMENTS.json). The
[candidate table](artifacts/CANDIDATE_TABLE.tsv) and
[complete group table](artifacts/ALL_GROUPS.tsv) retain all215 source positions,
including all140 positions outside the displayed partial prefixes. Partial
prefixes are not readings. The independently written Z3 validator checked all
assignment counts, all prefix lengths and exact tie-breaking, the joint model,
and source identity: PASS. This is implementation independence, not independent
manuscript or meaning evidence.

## Concrete obstruction

Positions22–26, f83r.3 groups4–8, are identical in all three sources:

`chey daiin chey lchedy qokaiin`

The last two groups are fixed nouns. To consume position26, its head must be
position25 with one argument or position24 with two. Position25 is already a
noun, so chey24 must be a binary head. Exact-form consistency then also makes
chey22 binary. Its two arguments would include chey24, which would have to be a
noun: contradiction. No meaning for chey or daiin is needed. The post-result
[early-core explanation](artifacts/VALIDATION_EARLY_CORE.json) independently
rechecks this obstruction and retains self-contained SMT-LIB subsets; inclusion
minimality is not a minimum-cardinality claim or a new preregistered test.

The preregistered qoky forecast is retained: its first occurrence after the
fixed qokeedy+lchedy clause must start a new clause, while its later occurrence
before fixed P0 chedy cannot supply the required noun arguments. The registered
reviewer also forecast the terminal chedy/chary failure. The full enumeration
finds the earlier obstruction above; these are related failures of one model,
not separate confirmations. No convenient substring was substituted for the
whole paragraph.

## Literal alternatives and limits

ZL3b preserves op{ch'}edy, d{ch'}eey and che[g:d] where the old projection has
opedy, deey and cheg. IT2a has opcsedy, sches, dsheey, merges o+qol to oqol, and
at f83r.5G9 has qokeedy (inherited unary delivery) instead of qoteedy (inherited
title statement). No variant was aliased away. The early five-group obstruction
survives all these differences. RF has no qualifying whole-reader paragraph in
this registered source contract; no RF result is invented.

Preregistration commit d8e885987580ae9b9a199bdc65e590d17136210d was public
before execution; the public receipt and frozen-file hashes are retained. The
target was already project-exposed and the manual forecasts were disclosed.
The separately disclosed producer f84r legacy-row incident supplied no payload
to root or validator and no input to this test. It does not create a holdout.

There is no semantic execution, new assigned meaning, significance claim,
independent meaning-confirmation capacity or confirmed translated word. The
old RAW372 account and other grammars remain unselected. Stop this exact
six-production route; a genuinely new, independently motivated construction
would require a separate offer preserving this failure, not an automatic
post-hoc grammar repair.
