# GDT1431: arbitrary word-internal permutations, one shared letter function

## Decision note before implementation

The previous goal turn completed public1430, a material scoped negative result.
Current preparation began2026-10-17T12:00:53Z. Inclusive budget ends12:45:53Z
(45minutes: retrieval, preparation, implementation, validation and publication).
Stop expansion at that checkpoint; do not raise caps or change source/units.

Known positive information: directed parts and exact whole forms coexist;
1389 retains bag-conditioned whole-form information without a retained extra
order increment. This is not evidence for anagram writing or an identified source.
The exact2133-form Syriac inventory is an already qualified reference, not a
selected manuscript language.1427/1430 reject one common source-letter function
in FWD/globalREV. Those results do not cover general within-word transposition.
1256 covers an injective Deot rare-word case;1358 covers four fixed8000-token
frequency profiles. Neither is this fixed Syric vocabulary/noninjective shared
function/59-group conjunction. Old failures and all open/STOP decisions stand.

Question: could arbitrary permutations alone ever make the exact shared table
and vocabulary fit these59groups? This is a broad necessary-condition closure,
not a proposed medieval decipherment or another fixed permutation recipe.
UNSAT closes all word-internal transpositions under this exact source contract.
SAT leaves an unassessed multiset witness; it does not show that only order was
wrong, select a practical ordering rule or authorize a permutation decoder.
UNKNOWN leaves the relaxed question open. No outcome authorizes new W, units,
source splitting, source-bigram repair, numerical exceptions or larger engines.
The research consequence is whether to retain or discard the entire transposition
family for this fixed source; the route closes here even if SAT/UNKNOWN.

## Fixed contract and smallest test

Inputs are EXACT1426 SOURCE_PROJECTION, NATIVE_INPUT and CONTROL_INPUT bytes.
W has2133distinct source forms/23sourcecodepoints. Native is original all59IT2a
f75v.38–42groups; working alphabet22units,15used. Each whole group is one word.
A single total function K maps every source codepoint to one working unit;
mergers are allowed, splits/nulls/multichar expansions are forbidden.
For each original group g there exists w inW with
Counter(K(c) for c inw)==Counter(g). No source edges, source occurrence counts,
syntax, group reordering, IR, run collapse, numeric exemptions or English values.
Full list/IDs/raw spellings and working units remain unchanged. Same sourceword
may have any different occurrence-specific permutation. This deliberately grants
more than a practical uniquely readable human cipher. It is only an envelope.

Primary: integer-valued K with a finite OR of weighted-count constraints for
same-length source-word multisets. Distinct source anagrams are equivalent for
satisfiability but retained in SAT preimages. Independent implementation:
Boolean sourceletter/unit matrix, exactly one unit perletter, source-word
selectors and weighted pseudo-Boolean equations. Both use Z3: independently
authored encodings, NOT independent solver backends. Each stops at20seconds
preparation or20seconds solving and returns UNKNOWN; no automatic retry.

Before any native solve, both new actual32-group ANY-key searches must be SAT
and their complete certificates checked directly. Planted identity/uniqueness
is NOT a gate. The old FWDcontrol is also a positive under arbitrary reordering;
it is run afresh by both new encodings. Small exhaustive source-free fixtures
check mergers, changed order, impossible multiplicities and globally conflicting
but individually supported bags. Such developmental fixtures may run before
lock and are disclosed; actual control/native solves start only after public lock.

Every SATkey is checked directly against original sourceword codepoints and
all original positions. Retain ALLW inverse words for eachbag for that returned
key, plus an explicit position permutation; these are unassessed alternatives,
not translations. ANYkey is neither preferred nor unique, and separate keys
are never merged. Two UNSATs under different encodings support the scoped
closure, with their shared solver dependency explicitly retained. A conflicting
SAT/UNSAT invalidates the result. UNKNOWN is not an exclusion.

## Assumptions and dependency list

Unproved: this W is relevant; codepoints are linguistic letters;22working units
are actual output units; each group equals one sourceword; K is globally fixed;
letters emit exactly one unit. No meanings of any Voynich whole or substring
are assigned. No picture resemblance, inherited lexical renderers or language
priority enters.1426provenance remains edited rather than diplomatic; Syriac RTL
layout never required mirror coding.1358frequency results do not transfer to
unconstrained choices from this W.1389does not establish order irrelevance.

Use cached admitted packets only. No rawTSVquery, images, source acquisition,
reserve, f84/f84r, f116v, f1rbody or327/336body. No relation evidence is scored.
