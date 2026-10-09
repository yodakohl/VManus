# GDT1262: robustness radius of the26-entry prefix exclusion

## Decision and prior evidence
1234excludes complete NONTRIVIAL prefix-free tables of at most26entries on the
fixed whole-group panel.1236shows rare-form dependence but does not find a minimum
number of unexplained token occurrences.1237studies only22-entry single-compound
tables.1248constructs complete27-entry cfh/cph tables. Their already exposed usage
summaries now show one once-used compound entry in each table/reader. This implies
an attainable one-token exception bound, subject to checking the actual whole-group
replay and retained nontrivial use. This is a post-result robustness consequence,
not a blind discovery, new historical alphabet or attempt to fix the native text.
Unknown resolved: the exact minimum whole-token exception cost for ANY prefix-free
code with at most26entries and a longer code actually used on its covered subset.
If construction reaches1, the old zero-exception exclusion is mathematically
sharp but not one-token-error robust. Otherwise retain only a weaker upper bound
and stop; no new head or arbitrary table optimization follows.

## Fixed construction and population
Use unchanged1233GROUPS.json.gz, separately in IT/RF/ZL. Original22working units,
strict-interior literal P-group occurrences and exact boundaries remain. No new
query, image, reserve, normalization or error correction. Check original input
hashes. All old groups stay in denominator, and every failure remains reported.
For EACH of the two old27-entry tables(cfh,cph) and each reader, remove each
compound entry whose occurrence usage is minimal in that old table; retain ALL
ties. The six old inspected minima equal1. Old counts imply the expected result;
the new replay identifies the actual unparsed group and checks every other parse.
Do not examine q-tables or change additional entries after the result.

Cost is number of original token occurrences not completely parseable, not number
of types, individual glyph edits or a probability of error. Table must remain
prefix-free, have at most26entries and use a longer entry on at least one accepted
group. Trivial22-singleton identity is excluded from the optimization because its
cost is0and it does not attempt compound spelling. No source values are attached.

## Certificate and consequence
Removing an entry preserves prefix freedom. Any old group whose unique parse
never used it keeps the same parse. A group using it cannot acquire a different
parse in the subset codebook, since that would also have been a second old parse.
Thus a code used once in the old full stream produces EXACTLY one unparsed token.
More than one old compound-active group guarantees some compound use remains.
1234's bound supplies minimum cost>=1for every nontrivial code<=26; one attained
case perreader supplies <=1. Together they prove minimum1over that entire class,
not just the six tried reductions. The exact full-input failure remains unchanged.
No failed group is called erroneous, repaired or dropped from future evidence.
No claim about21--25entry minima or broad activity with exceptions is made.

## Validation and limits
Primary uses deterministic greedy prefix parsing. A separate validator imports
no runner; it uses explicit dynamic codeword decomposition, checks old and reduced
coverage, re-encoding, all retained activity/counts, exact failure identities and
the inherited lower-bound premise. Both programs plus protocol are hash-locked
before new group replay. Old summary exposure is explicit. Whole-reader agreement
is not independent physical evidence. Source-unit, boundary and rare-form premises
remain, as do fixed-source failures and1248's lack of meaningful source values.
No decoder, picture reading, translation or new native statistical fit.
Inclusive25minute budget16:15--16:40UTC includes preparation and local closure.
Local-only publication under4Octoberinstruction; no commit or push.
