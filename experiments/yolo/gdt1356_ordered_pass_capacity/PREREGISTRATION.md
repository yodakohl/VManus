# GDT1356 — Strict global rank with repeated contiguous passes

## Decision before native capacity calculation

Review1219,1238/1239and contextual-source priors did not justify rerunning their
failed fixed writers. Select IDEA001032: a different structural necessary rule
for a writer that scans one fixed sign order but may restart within a word.
1263requires one weakly ordered whole;1345sorts disjoint sign classes with
arbitrary interleaving;1321allows no class return;1349uses nested/circular fields.
None gives the bounded repeated-contiguous-pass envelope here. Their original
results stand. K=1failure is already known and is not new research progress.

Unknown: how many passes are unavoidably needed under EVERYstrict rank, and
whether one explicitglobalrank matches a lower certificate. NewlowerK>=3would
exclude every writer limited to two passes under this contract; higher bounds
similarly exclude whole capped families. Matching upperrank retains those larger
capacities but identifies no syllable, source letter or historical procedure.
Smallest test: elementary lower certificates plus a tightly bounded feasibility
search for one upperrank; no plaintext, language control or larger optimizer.
Budget35minutes from first recorded11:04:45UTC including subsequent retrieval,
proof, implementation, validation and publication. Initial route reading before
that clock has no invented exact duration. No search expansion at the deadline.

## Exact writer constraint

One global strict total order on all22working signs, shared across a reader's
whole panel. Within a contiguous pass the word is NONDECREASING; equal signs can
repeat. A sign may occur in several passes. For a fixed rankr, minimum passes in
nonemptyw equal1+the number of adjacent strict descents r(w_i)>r(w_(i+1)).
Cut at every descent for an explicit minimal segmentation. Additional boundaries
at non-descents are invisible; this does not recover arbitrary original fields
or supply a complete source inverse. No meaning/syllable/phonetic status assumed.

Use unchanged1233strict internal Pgroups with definite outer spaces. FULL and
GE2wholeforms on>=2physical leaves, readers separate. Equal-letter pairs never
create descents. GE2is sensitivity, not repair or confirmation; all22working
units and supplied whole-group boundaries remain assumptions. No new source,
raw TSV, image, f84/f84r/f116v/f1rbody or reserve. No arbitrary word meanings.

## Certified lower bounds L

1. In each word, find a maximum collection of EDGE-disjoint closed subwalks
   w_i...w_j with w_i=w_j and at least two DISTINCTsigns in the interval.
   Every such walk has>=1descent under any strict totalorder. Shared endpoint
   positions are permitted; shared adjacent edges are not. Dynamic programming
   maximizes number of intervals; tie by lexicographic interval list. Retain the
   word with highest bound1+intervalcount, then lexicographically smallest type.
2. If bothw and reversew occur, their descent counts sum to the numbermofunequal
   adjacent edges. ThusK>=1+ceil(m/2). Retain maximal bound, then smallestword.
   A palindrome may serve twice; this is an inequality, not two independentwords.
3. On the multiset containing each wholeTYPEonce, letN_ab count directed ADJACENT
   edges. Sumdescents overTwords is>=sum_{unordered a,b}min(N_ab,N_ba). Therefore
   K>=1+ceil(that sum/T). Retain all edgecounts for replay. This is not1345's
   nonadjacent precedence graph or a frequency-weighted statistical test.

L is the maximum of these sound certificates and1. It need not be the strongest
possible bound. Preserve the supportcount/physicalleaves/first source row for
word certificates; do not select a reader or drop rare forms after outcomes.

## Upper rank, fixed search limit

Alphabetical unit order always gives a valid fallbackU=max(1+descents). Try
K=L,L+1,L+2 only whenK<currentU. For each attempt, Z3 uses22distinct integer ranks
0..21 and all per-word weighted adjacent-descent constraints<=K-1. Drop only
constraints whose unequal-edge count already<=K-1. timeout10seconds per SATcall,
random_seed0; construction/replay time is inside the overall budget. No extra
starts, deeperKsearch, second optimizer or post-result simplification.

SAT supplies a candidate order only; replay every whole group independently and
use its actual maximum asU. On firstSATstop attempts. UNSAT/UNKNOWN are diagnostics
and NEVERraise certifiedL. If none found, retain alphabeticalfallback. Exact
minimum only whenU=L; otherwise report [L,U], not a guessed optimum. Solver
limits can change a reproduced rank or interval; recorded witnesses remain
independently checkable. Do not claim byte-identical timed-search replay unless
it actually occurs. All ranks are fitted on the full exposed panel, not held
prediction. No actual alphabetic values follow from a compatible order.

Report under the retained rank: token/type pass-count distributions, exact
maximum word witness and a canonical descent segmentation of that witness.
Those distributions are descriptive for that rank, not globally optimized means
or universally fixed boundaries. Reversing everyword ANDtheglobalrank preserves
capacity; no native reading direction is inferred. This rule does not repair
1355null bounds,1354codebook uncertainties or phonetic source exclusions.

## Independent verification and source-free controls

Before native run, exhaustive orders on all short3symbol strings verify the
pass/descents identity and all lowercertificate inequalities; include constant
runs, alternatingwords, sharedendpoints and reversedpairs. Validator imports no
runner: independently reparse source and GE2, rebuild DPbounds, replay every
closedwalk/reverse/all-edge certificate and upperrank/segment/histogram. It does
not accept solverUNSATas proof and need not rerun timedsearch. Source/hash and
arithmetic validation do not establish historical use or linguistic units.
