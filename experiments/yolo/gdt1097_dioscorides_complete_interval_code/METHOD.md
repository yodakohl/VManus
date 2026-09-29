# GDT1097: complete local equations as suffix intervals

## Contract and selection

The preceding decision is
`research_registry/proposals/laufenberg_f85r2_20260926/DIOSCORIDES_COMPLETE_INTERVAL_DECISION_20260929.md`.
Inclusive block09:47–10:37UTC on29September2026. GDT963 source order, aliases,
positive code lengths, injectivity, prefix freeness, complete target frames,
and permission to cross written groups remain unchanged. This implements the
same complete local equation with integer constraints; no new linguistic decoder.
GDT1096 supplies proved necessary domains, not translated words or full fits.

Test EVERY GDT1096 literal IT2a I.1 case with nonempty final domains:
528/f17v,764/f46r,784/f48v,788/f49r,792/f49v,892/f8r,904/f93r.
These are the seven remaining candidates for one obligatory record, selected
by the same explicit status rule, not by drawing, word identity or solver ease.
All265 source occurrences, including every singleton, are mandatory. The
other1421 old cases remain visible with their inherited status; no new testing
of other source roles is implied. The previous26 literal I.1 contradictions
and original length exclusions are retained. All1016 source-unknown cases,
including any I.1 cases, remain unknown. ZL/RF four-leaf capacity stops remain.

All inputs and pages are previously exposed; there is no new confirmation set.
No raw mixed transcription, images, new source, f84/f84r, f116v or reserves.
Alternate transcriptions are not independent manuscripts. Confirmation capacity0.

## Exact encoding and equivalence argument

For a fixed target string T of length n, sort its n nonempty suffixes, retaining
both starting positions and ranks. A nonempty substring w is a prefix of some
suffix. The suffixes beginning with w form a nonempty contiguous rank interval
I(w). Two words u and v have intersecting intervals if and only if one prefixes
the other: an intersecting suffix starts with both; conversely every suffix
starting with the longer word also starts with its prefix. Equality is included.
Thus distinct source atoms have injective prefix-free codes exactly when their
chosen suffix intervals are pairwise disjoint.

Group substrings that have identical intervals. Such a group is one edge of
the compressed suffix trie: its strings are prefixes of the same suffix and
have every length from a minimum to a maximum. The implementation obtains the
classes without retaining all substring strings, scanning each positive length
and grouping adjacent suffixes whose LCP is at least that length. The class
is (lo,hi,min_length,max_length), with both rank endpoints inclusive.

For each source type a choose one valid class and a positive length l(a) in
its exact range. The upper length bound follows solely from the full equation:
(count(a)-weighted length) plus one character for every other occurrence must
fit n. Class width must cover at least count(a) distinct occurrence starts.
For a recurrent type use only its exact GDT1096 final strings, represented by
(lo,hi,length) tuples. No recurrent value is widened, sampled or selected early.
Singletons retain ALL possible class/length choices within the necessary bound.

For the complete source stream a[0]...a[m-1], set p[0]=0, p[m]=n and
p[i+1]=p[i]+l(a[i]). The suffix rank at p[i] must belong to I(a[i]). All type
intervals must be disjoint, using the integer solver's global NoOverlap. No
condition constrains p[i] to an existing word or line boundary.

Forward: any old nonempty prefix-free local code has substring values; its
intervals, lengths and actual starts satisfy every constraint, and its recurrent
values survived the necessary GDT1096 procedure. Backward: a chosen interval
and length identify one exact prefix shared by every suffix in that interval.
Every source occurrence therefore spells the same code; the cumulative boundaries
cover T exactly and disjoint intervals supply all injectivity/prefix conditions.
This is equality of local feasible sets, NOT equality to the original four-record
joint problem, which additionally requires shared codes and distinct leaves.

## Controls, execution and decisions

Before target execution: exhaustively check126binary substring inventories and
17942interval/prefix pairs; compare882small complete equations with independent
backtracking (400SAT/482UNSAT); plant the entire265-occurrence source shape with
one-character distinct codes; test a variable-length/domain positive and reject
a forged prefix collision. The large planted alphabet checks occurrence accounting,
not practical search capacity on Voynich. The independent tiny oracle and ground
validator do not import the suffix encoding. Same author; no meaning independence.

Freeze methods, source inputs, scripts, dependencies, controls and selection before
one target run, then publish registration. Pin OR-Tools9.15.6755;7processes x4CP-SAT
workers=28. Each case gets30solver seconds and90total seconds; complete run150seconds.
Fixed seed1097. No restart or longer second pass. Resource exhaustion is UNKNOWN;
MODEL_INVALID/process failures are invalid computations, never manuscript exclusions.

A FEASIBLE/OPTIMAL result must retain ALL code values and265position spans, and
pass direct ground checks of concatenation, nonempty values, equality, injectivity,
every prefix pair and inherited domains. It is one COMPLETE LOCAL C0 candidate;
search is not exhaustive over all successful codes, so no uniqueness claim.
No automatic expansion to the other three records. INFEASIBLE is a solver result
on the exact encoded system; no independently replayed UNSAT certificate is
claimed. If all7 are INFEASIBLE, the literal IT conjunction lacks a required
local role under this model. Any UNKNOWN keeps that conjunction unresolved.
Source-unknown frames are outside that literal conclusion.

The validator checks hashes, all1428case identities, the full printed table,
all7statuses and any full witnesses. It checks the saved solver report for
negative statuses but does not turn that report into an independent proof.
Zero confirmed words, no named plant identification, no significance or global
Voynich-language conclusion follows. At the inclusive checkpoint stop expansion
and reassess; preserve old failures and unknowns. No source/alias/code repair.
