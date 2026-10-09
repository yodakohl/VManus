# GDT1274 — immediate doublets bound a strict-saving reference writer

## Decision note
1250 excludes mandatory references with disjoint modes and empty paragraph
resets. It explicitly leaves optional full spelling open. The new question is
narrower than arbitrary optional spelling: what if a writer always chooses a
strictly shorter available reference but otherwise may spell fully? Can the
old retained qokeedy doublet force reference width at least7working units?

Unknown before this scoped application: the consequence of that cost rule,
without mode disjointness or paragraph resets. If the old exact witness passes
source checks, reference maxima0..6 are incompatible with this conjunction.
If fidelity fails, report invalid witness instead of widening targets. A bound
of7 is not existence of a viable cache or proof of the true writing mechanism.
No decoder, source corpus, alphabet optimizer or new transcription is needed.
Inclusive allocation12:30–13:15UTC on8October includes predecessor review and
all closure;12:30is a conservative allocation, not a precisely measured start.

## Fixed conjunction
1. One source word produces one complete written group, with no extra written
   control group, unprinted transition or reset between the two observed groups.
2. Literal spelling L is fixed and globally injective on source word strings.
   It need not be disjoint from reference spellings.
3. After a word is emitted, it is retained through the next source word and has
   a legally available reference of total cost<=r. Being cached without a usable
   reference is not sufficient. All marker/escape costs are included.
4. If a shorter reference is available, the next occurrence of that word must
   use a reference shorter than its literal spelling. Ties are unrestricted;
   literal spelling on a hit is allowed when no strict saving exists.
5. Every emitted reference has total width<=r under the same fixed cost units.

This is mandatory exploitation of a strict saving, NOT all optional abbreviation.
It need not choose the very shortest of multiple references; any reference
strictly shorter than the literal is sufficient for this argument.
Authors who may intentionally spell fully despite a saving lie outside the rule.
There is no assumption about when paragraphs reset or begin with empty memory.
Immediate retention/reference availability IS required between the two tokens.
Context-dependent or noninjective literal spellings also lie outside the claim.

## Proof and bound
Let an exact written doublet be XX with width n>r. Neither X can be a reference,
so both must be literal. Injectivity makes their source words identical. After
the first, that word has a legal reference<=r<n; rule4 forbids the second long
literal X. Contradiction. Therefore n<=r for every exact doublet.
Overlap between literal/reference modes cannot evade the length argument.
Nothing implies equal meanings of repeated native reference forms in general.

## Fixed old witness and checks
Use only qokeedy rows already in1250artifacts/WITNESSES.json, not a new maximum
or corpus scan. It was named in the1250primary before this test. Check each
reader separately, complete saved doublet line, consecutive source indices,
two exact qokeedy groups and definite internal AND outer seams with both flank
groups present. Do NOT consume the saved paragraph-start witness or metadata.
The fixed working-unit representation is q,o,k,e,e,d,y, length7. This is not a
new physical grapheme determination or count of penstrokes. No meaning assigned.

Primary derives only the necessary r>=7 from that fixed witness. Separate
validator locates by saved source index rather than searching the literal pair,
checks old input manifest hashes, all raw rows and the width decision. A bounded
producer independently reviewed the source-free proof and availability caveat
before this extraction. Finite controls illustrate tightness at n=r, a longer
literal repeat when shortening is optional, and failure if references are not
available. They supplement rather than prove the general argument.

No new data/images, f84/f84r/f116v/reserve, relation score or statistical null.
All readers are alternate readings of one manuscript. Old1250 remains unchanged.
Local4October exception: no commit/push. No automatic longer references or cache
repair follows from the bound; any new writer needs a separate motivated contract.
