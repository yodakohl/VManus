# GDT1368 — Nucleus capacity with bounded source-word fragmentation

## Decision note

IDEA001046 changes the explicit word/group contract rather than repairing old
1042/1363/1364 results. Unknown: do exact consecutive three-group windows force
more than five fixed nucleus-carrier representatives even when a sourceword may
span one or two groups? If yes, exclude the declared B2/K5 conjunction on the
retained windows. If no, that previous whole-group exclusion cannot be extended
by this necessary test; no phonetic support or successful partition follows.
Smallest adequate test: exact minimum hitting size up to5, with full upper and
lower certificates. Budget25minutes including proof, implementation, independent
validation and publication. No language/decoder or automatic larger B afterward.
Data previously exposed; no holdout or prospective discovery claim.

## Contract and proof

Sourcewords partition the stream into blocks of1or2nonempty visible groups.
Groups never combine parts of different sourcewords. Order is preserved; each
sourceword retains at least one nonempty fixed nucleus carrier from an inventory
of at mostKstrings, aligned to RAW_CHAR boundaries. Carriers may cross the newly
inserted fragment gaps; deleting those gaps preserves their rawcharacters.
Choose one rawcharacter from each carrier. A complete sourceword contains one
chosen representative, so the global representative set has size at mostK.

Every2B-1consecutive groups contain a complete sourceword block: otherwise only
two proper edgefragments occur, each of length<=B-1, totaling<=2B-2groups.
ForB2, every consecutive triple must contain a representative. A hitting minimum
above5therefore contradictsK5under this contract. A passing hitset does not show
that full carriers occur or that a consistent sourceword partition exists.
No actual vowels, sounds, meaning or language selected; Kcounts written carriers.
RAW_CHARavoids retokenization ambiguity when a gap splits a working unit likech.
It is still not an identified physical alphabet or universally valid codeunit.

## Frozen eligibility

Reuse unchanged1233GROUPS.json.gz and631allowlist. Independently verify rawparse,
ID/edition/page/locus, Pkind, allowedpages, definiteleft/rightgaps and exclusions.
For each reader group by(page,locus); require distinct integer source_group_index.
Enumerate keys lexicographically; startindices ascending. Keep a window iff rows
at i,i+1,i+2 are ALLpresent in the cache and meet eligibility. No GE2filter, no
joining across a missing index, line, locus or page. No invented line continuation.
The cache is filtered: these are only retained trueconsecutive windows. A FAIL
is still a counterexample; a PASS does not cover missing windows or the manuscript.
Readers remain separate readings of one manuscript, never independent replications.

## Computation and artifacts

Window support is union of individual rawcharacters in its3groups. Alphabet is
sorted FULLcachealphabet for thatreader, not a fitted subset. Enumerate all
subsets of sizes0..5. First size with a set hitting EVERYretainedwindow is tau;
save number of minimum sets and the first lexicographic character-tuple witness.
If none succeeds, record lowerbound6andno upper witness. Do not search largerK.
If anyreaderhaszeroeligiblewindows, stop UNAPPLICABLE, no vacuous pass.

Save WINDOWS.json.gz (mtime0) as reader->ordered list of windows, each with
sources:[threecompleteoldrows], support:sortedcharacters. RESULTpanels reader->
{groups,windows,loci,leaves,alphabet,tau_or_null,lower_bound,minimum_sets,
canonical_hitset,decision,lower_certificate:[{set:list,first_missed_window:int}]}.
For tau>=1, lowercertificate enumerates EVERYset of size tau-1, ordered by
itertools.combinations(sortedalphabet,k), with its first missedwindow index.
If no<=5cover, use allsize5sets. Any smaller set extends to thatsize, so this
proves lowerbound. Upper hitset must cover every savedwindow. Decision is
K5_NOT_EXCLUDED_BY_RETAINED_WINDOWS or K5_EXCLUDED_BY_RETAINED_WINDOWS.
Groups means FULL inputrows; loci/leaves describe eligiblewindows only.

Primary uses subset-sum transform on window support masks. Independent validator
uses per-character window bitsets and direct subset coverage, reconstructing all
sourcewindows, counts and everylowercertificate. Lockproof/protocol/bothprograms/
cache/allowlist/RAWproposal before census. Synthetic controls include missingindex,
wronglocus, overlapping windows, splitunit and hitsetnon-sufficiency. Exactform
frequencyalone assigns no value; there are no word meanings or relation scores.

Prior1257tests whole control words in fourgroupwindows, not character-carriers;
1196tests specific source-vowel segmentation/frequency, not this bound.1364old
RAW_CHARwholegroup minima are not a matchedsample comparison with these windows.
Their original failures, model limits and rarity sensitivities remain unchanged.
No rawTSV,image,sourcecorpus,reserve,f84/f84r,f116v orf1rbody access.
