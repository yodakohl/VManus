# GDT1036 — fixed vocabulary capacity for a whole continuation

Phase: exploratory selection, frozen before this census. The complete82-group
two-paragraph offer was fitted after observing both source paragraphs. This is
not a test of its guessed meanings. Its lexical inventory is fixed; no grammar,
quantity or reference rule is evaluated here.

Inputs: the new offer JSON, its exact source packet, and GDT928's hash-bound
PARAGRAPHS.json containing659ZL and690IT complete paragraphs. RF has no complete
paragraph contract in that packet. Historical exposure remains exposure; both
physical leaves21 and32 are excluded from continuation selection. f84/f84r
remain sealed and f116v remains unadmitted. No mixed TSV is parsed.

Inventory: exact65primary keys plus15alternate keys, including raw unresolved
groups. Their offered values are frozen. Compositional alternate keys remain
whole tokens; their fixed constituent values may contribute operation tags but
are not split, normalized, decoded or counted as extra source positions.

Enumerate all1,349paragraph rows, retaining raw groups, exact source IDs, literal
line flags, known/unknown positions, known/unknown exact types, and all failure
reasons. A raw group is known iff an exact inventory key exists. Counts are not
semantic likelihoods. Strict-line flags are reported but not used to discard
rows; source uncertainty remains. Full lexical coverage is reported separately.

A row qualifies for a bounded continuation only if all hold:

* physical leaf is neither21 nor32;
* 25 through100raw groups inclusive;
* at least8distinct known raw forms;
* at most20distinct unknown raw forms;
* at least half its raw positions have frozen values;
* at least2distinct frozen operation values occur.

The operation values are the explicit fixed list in SPEC.json. This is a
minimum process-content/overlap contract, not a significance threshold. No
cutoff will be lowered after results. A paired candidate additionally requires
one complete ZL and one complete IT paragraph with the same page and ordered
full locus list, and both rows qualifying independently. Different boundaries
remain unpaired; no text alignment, cropping or repair makes them match.

Rank qualifying pairs by: ascending maximum unknown-type count across readers;
descending minimum exact known-position fraction (rational comparison);
descending minimum known-type count; natural numerical physical-leaf order;
page string; full ordered locus tuple using natural numeric components; then
reader paragraph IDs. Select exactly the first pair, or none. Publish every
qualifying pair and all unpaired/rejected rows, not just the winner.

Outputs: all-row CSV/JSON with raw known/unknown position bindings; all pair
gates and ranks; full selected paragraphs with frozen values and explicit
UNKNOWNs; summary. The runner does not invent a single new gloss or execute a
semantic parser. Zero qualified pairs => PARK_WITHIN_FROZEN_CAPACITY_LIMITS.
One or more => ONE_COMPLETE_EXTENSION_TARGET, requiring a subsequent full
exploratory reading with unchanged old values before any meaning test.

Independent validator reconstructs inventory, every row, pairing and exact
ranking without importing the runner. Synthetic fixtures check equality at
the thresholds, failure on one-below/above, complete-leaf exclusion, ambiguous
raw keys, and rational ranking. Lock and source hashes must match. All findings
remain developmental: no independent meaning confirmation, no significance,
zero confirmed words. An ordinary unrelated dictionary can also have lexical
coverage; that rival is not distinguished by this census.
