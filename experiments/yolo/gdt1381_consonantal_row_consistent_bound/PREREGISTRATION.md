# GDT1381 — One complete within-row key-consistency certificate

## Decision note and scope

1380 leaves precisely Latin/MiddleFrench inconclusive on NEW_PAGE_HOST IT2a.
It intentionally dropped ordinary-symbol equalities and inequalities between
context and next-event assignments. A real global injection must obey these
within every row. This single bounded extension restores ALLwithin-row injection
requirements, without a new model, input, score, threshold or global search.
1052 already named this possible strengthening; novelty is its execution, not a
new writer or independent manuscript sample. Boundedprior review found no exact
executed certificate;1232additivepackets/1226source-mixing are different problems.

Budget25minutes including proof/priorreview, implementation, validation and
publication. Positive margins close the two remaining fixed comparisons;
nonpositive margins remain inconclusive and this proof branch stops. No pair-row
coupling, branch-and-bound, new corpus, representation or alphabet repair follows.

## Frozen inputs

Reuse EXACT1380CORPUS, MODEL_COUNTS and RESULT, IT2a only, packs latin and
middle_french in that order. No new source query, parser, licensing, training or
word filtering. Old1380fourotherpackcertificates are inherited unchanged, not
rescored as new evidence. ZL/RFempty21-targetinjection results remain unchanged.
This is still the newly scoped lossy ASCII PAGE_HOST projection, not old193full
input and not an actual linguistic alphabet. SourceSPACE/BOS remain typed fixed
values; every ordinary sign maps into the same21consonants.

Use1380's integer2^-32bit lower cost ticks unchanged. Primary may import its
frozen arithmetic helper only; validator uses the separate1380Decimal80helper.
Reuse the exact oldKTupper, keylower and SIX-language selectorlower; selecting
two unresolved cases must not replace log2(6) bylog2(2). Sharedoverhead unchanged.

## Complete within-row minimization and proof

For sourcecontext (u,v), collect DISTINCT ordinary symbols excluding SPACE/BOS.
Enumerate their injective images into the21consonants. Repeated sourcecontext
symbols thus share their image, distinct ones have distinct images. This also
fixes the permitted targetcontext; SPACE/BOSretain their typed values.

Reserve EVERY such targetimage, including images of contextsymbols with zero
next-event count. Next-symbol counts for a contextsymbol pay its fixed image's
cost. SPACEpays its fixedcost. For remaining distinct ordinary next-symbols,
pair positive counts descending with the cheapest distinct UNRESERVED target
costs ascending. Missing zero-count source symbols can occupy remaining targets;
within-row assignment extends because the full admitted active alphabet fits21.

Minimize this sum over all legal contextimages. Save minimizing targetcontext,
old and new rowlowercosts, and increase; ties choose lexicographically smallest
targetcontext. No row needs more than21^2context trials or a generic optimizer.
A repeated contextsymbol is reserved and charged only once per counted event.

Every global injection restricts to a legal assignment here. Across different
rows its binding is still relaxed. Therefore
old1380_row_bound <= new_row_bound <= every_global_key_row_cost.
Summing gives a rigorous stronger global lowerbound. All comparisons use exact
integer ticks, so require new>=old separately for EVERY row before reporting.
The new local minimizing maps need not agree with each other and are not a key.

## Frozen decision

Perpack add unchangedkeylower and selectorlower to sumnewrows, subtract oldKTupper.
Strictly positive margin => CERTIFIED_NO_KEY_BEATS_MATCHED_KT; otherwise
BOUND_INCONCLUSIVE. Combine these two cases with the four oldpositive certificates
only to report ALL_PACKS_CERTIFIED or PARTIAL_CERTIFIED_BOUNDS for the unchanged
IT2a six-pack family. Negative or zero bound is not a fitted plaintext.

All source/reader/genre/representation limits from1380remain. In particular this
is not194homophony, not every possible Latin/French text and not a language or
consonantal-writing ban.193/194old numericalfailures and scoped correction remain.
No native word meaning, phoneme, image, reserve, f84/f84r,f116v orf1rbody use.

## Validation

Before newcertificate execution, exhaustive tiny synthetic global injections
and local rowassignments must verify soundness and monotonicity. Include same
and distinctcontextsymbols, anchored successors, an anchor absent from successor
counts, fixedSPACE/BOS and a strict-improvement example. Positive source-free
controls establish algebra/software behavior, not nativeevidence.

Freeze this protocol, both programs, proofreview, oldarithmetic helpers and all
inputs before nativeevaluation. Independent validator reconstructs the finite
row minima, old-rowcomparison and unchangedcostaccounting without importing the
new primary program. Both mathematical proof and integercertificate are needed;
a displayed rounded margin alone is insufficient. Stop after this one extension.
