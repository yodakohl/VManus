# GDT1334 — exact capacity of a canonical two-port allograph writer

Registered11October2026 before native frame/run enumeration. Inclusive budget
08:04–09:04UTC for preparation, proofs, implementation, independent validation
and publication. At deadline stop expansion and report incomplete work honestly.
A source-free reduction BEFORE registration replaces a proposed general SMT/CEGIS
search with exact finite run constraints and2SAT; no native result drove this.

## Decision note and predecessors
1001constructs a whole-word minimum-join-cost writer in an invented49-form
teaching alphabet, with physical22-unit binding missing.1295's old literal
conflicts remain necessary by local replacement, but its source-neighbor function
and1310's additional merger conflicts do not all apply to global planning.
928has a different fixed-entry/reset contract; its failures remain.1333finds no
retained positive word/site increment beyond immediate expanded flanks, without
identifying a physical mechanism. It motivates taking a compact neighbor-cost
rule seriously, not altering the failed optional-choice model.

Unknown: can ANY nontrivial global alias interpretation of the22working units
satisfy the precise two-port rule below on all unchanged strict groups? This is
an existence/capacity question over all bindings, not a test confirming chosen
physical ports. If none exists, no independent binding can rescue this exact
family under these data premises. If some exist, supply actual compact finite
writer witnesses and their coverage/activity; distinguish this from arbitrary
context lookups and from meaning. Do not select a native body identification,
fit a language, add ports, costs, exceptions, page styles or another unit split.

The fixed family is a generous structural GENERALIZATION of1001's teaching table,
not a fit of its49literal allographs or source A-Z. Each observed glyph has one
fixed entry and exit bit,0or1. Unknown body classes partition all22glyphs; within
a class at most one glyph has each of the four port pairs. Each source body emits
one glyph from its class. Preserve word order, units and word boundaries. Any
word is writable, paying one cost for each unequal exit/next-entry pair. Both
outer word edges are free. Minimize total cost over the WHOLE word, then choose
the lexicographically smallest sequence of portcodes2*entry+exit. No other
body cost, hidden state, word lookup, position/page/hand term or random choice.

## Exact single-pair reduction
Any valid nontrivial partition contains an observed pair x/y in one body class.
Refine all classes to singletons except that pair. The allowed rendering set
shrinks but keeps every observed word. Cost and lexical preference are unchanged,
so the old canonical optimum remains canonical in the restricted set. Thus
existence of ANY nontrivial family member implies existence for at least one of
231single pairs, with one shared body and20other singleton bodies. Different
ports for x/y give all12ordered choices. No LOW/HIGH-complement quotient: ties
change under that operation. Singleton bodies may freely share port pairs.

All231pairs per reader are retained; ZL/IT/RF separate, no pooling. Passing pairs
need not compose; each positive is only one complete21-body writer. Negative
pairs remain forbidden in any coarser valid partition by refinement. Identity
with22singleton bodies is possible trivially and explicitly outside the question.
A conditional21-body writer is not a source alphabet or a decoded text.

## Fixed exact algorithm
1. Collect every actual immediate visible neighbor pair around each unit,
including distinct BOS/EOS boundaries, across unchanged1233strict Pgroups.
Unlike1295, match across page/length/index as the compact cost rule has none.
If x and y share any identical visible-neighbor context, they cannot be aliases:
replacing only the center would improve cost or its canonical tie order in at
least one occurrence. Retain lex-first context and lowest-ID/index witnesses.
This proof rejects all12port assignments for that pair. Never export1310's extra
SOURCE-neighbor edges automatically.
2. For each remaining pair collect maximal contiguous x/y runs from whole words,
with their actual singleton neighbors or FREEword edges. Fix each of the12ordered
port assignments to x/y. All other glyphs have40unknown port bits.
3. For each run length and each of nine possible outside contexts(0/1/FREE at
both sides), compute its canonical minimum-cost x/y rendering by dynamic
programming. FREE removes that boundary edge, not a third Boolean port value.
The observed run permits exactly those outside bit combinations yielding it.
4. An internal forbidden boundary combination(L=a,R=b) gives the2CNF clause
(L!=a OR R!=b). A single FREE edge leaves one literal; two FREE edges may yield
an empty contradiction. Lmeans exit of the actual left singleton; Rmeans entry
of the actual right singleton. Different occurrences share all global glyph bits.
Conjoin every constraint; fix x/y bits to their enumerated values.
5. Solve2SAT by implication SCC. For SAT retain lexicographically smallest44bit
assignment in sorted-unit entry/exit order, by successive satisfiability checks
preferring0. Store all per-pair/per-port decisions, canonicalized clauses and
witness ports. For each SAT model, check every unique FULL word with canonical
word DP, not just separate center costs. No fitted corpus counts choose a key.

Why step3is sufficient: all singleton/singleton costs are fixed. Each maximal
alias run contributes its internal and at most two incident boundary costs;
these edge sets are disjoint. Given the global bit assignment the minimization
separates over runs, even when two runs share a separating singleton. Its entry
and exit bits are separately retained and globally shared in theCNF. Every run
must reach its own minimum; global lexical tie order chooses its canonical run
independently. These conditions are necessary AND sufficient, unlike merely
being stable against single-center replacements.

Source-free counterexample to the local-only shortcut: x=LL,y=HH,h=HH as a
singleton body. hxxh is stable under either single-center replacement with the
fixed tie order, yet hyyh has lower total cost. Full runs therefore cannot be
replaced by a local-center SAT test.

## Outputs, scope and decisions
Use1233groups,631allowlist and915original joins. Exact raw22unit parser; readers
remain alternatives, historically exposed panel. No new raw TSV, images, source
language, reserved page, f84/f84r,f116v,f1rbody or327/336body. No semantic packet.
All full-group occurrences/rare forms remain; no error allowance is introduced.
1332's robustness warning applies: an exact contradiction is not an error-rate
estimate or a universal ban on human writing. Do not infer native body identity
from an unconstrained fitted existence witness.

Save all pair decisions, old-context counterexamples and all surviving-pair12port
results including clauses/models. For each pair report groups containing x,
groups containing y, their union and intersection; also min(Nx,Ny)/N as a
DESCRIPTIVE minority-spelling mass, not the fraction of translated/explained text.
If all pairs are contradicted, NONTRIVIAL_TWO_PORT_ALIAS_FAMILY_EXCLUDED. Otherwise
EXACT_PAIR_WRITER_WITNESSES, with all compatible pairs and first port witness.
No significance, favorable pair selection, source vocabulary or decoder claim.
The source word distribution is preserved by each deterministic injective writer;
old fixed-source frequency exclusions are not repaired by port planning.

## Validation
Before native enumeration exhaust toy run lengths1..6, all12pair port assignments,
and all9outside contexts against explicit2^nrendering enumeration. Compare the
SCC solver with brute truth tables on bounded small CNFs, including empty/unit
clauses and canonical-bit selection. Check the hxxh/hyyh counterexample.
Independent validator imports no runner: original915joins and raw unit reparse,
per-pair set-intersection context proofs, maximal-run reconstruction, backward
run DP, independently derived forbidden-boundary clauses. Z3plainSolver verifies
all SAT/UNSAT port decisions, with direct clause truth checks and lex-witness
minimality. Full-word backward DP checks all positive writers against all distinct
observed words. Native output may not be scored until these checks agree.
SCC and Z3 are independent computational methods; no independent palaeography
or actual pen trajectories are claimed. Pure proof reviewer sees no new1334data.
