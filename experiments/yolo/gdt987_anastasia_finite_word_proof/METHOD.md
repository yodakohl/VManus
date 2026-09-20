# Finite whole-word-constrained proof of the unchanged986equations

This is a new proof procedure, not a changed writing model. Every source line,
clause, atom, tree order, paragraph, character and word seam remains the frozen
GDT986 input. Read its METHOD.md and SOURCE.json for the content assumptions.
No source code can cross a written word. One nonempty injective prefix-free
code is shared by all occurrences of each of47atoms within a complete case.
Cases do not share a learned key or claim three transcriptions as replications.

## Finite completeness and necessary bounds

Traverse the full111atom stream and the target from left to right. A previously
assigned atom must match its exact code at the current target position, ending
no later than the current word. An unassigned atom must take one of the nonempty
prefixes ending inside that same word. Enumerate all such values in ascending
length. The complete sequence and entire paragraph must finish together. Thus
every permitted complete code determines a branch of this tree; no boundary,
source assertion or unknown semantic singleton is removed.

Every code is a within-word substring. If its source frequency is k, at least
k nonoverlapping occurrences must be available inside target words, and its
length is at most floor((target_characters-(111-k))/k), also bounded by the
longest word. Prefix comparability with any assigned value is forbidden.

A further necessary consequence is **forced word starts**: if an assigned code
v prefixes a written word, that word must start with the corresponding atom.
Any shorter alternative code would prefix v; any longer alternative would
have v as its prefix. Both violate the unchanged prefix rule. Therefore the
number of target words starting with v cannot exceed that atom's total source
frequency. This is a derived constraint, not a spelling or meaning change.

At each branch, the sum of remaining assigned lengths and unassigned minimum/
maximum domain lengths must bracket the remaining target length. The remaining
number of words cannot exceed the number of remaining atoms. A repeated assigned
value must have enough nonoverlapping, within-word occurrences in the unconsumed
suffix. For a fixed string, greedily taking the earliest available occurrence
maximizes this count; the implementation precomputes suffix capacities. These
are necessary pruning conditions, never sufficient readings.

## Fixed limits and full accounting

Every one of148literal GDT986cases is checked, including its39contradictions;
all166source-unknown cases stay in the table. Per main case:500000nodes and
10seconds, time checked at128node intervals. Sixteen workers and a45second
external case ceiling include possible projections. No interrupted enumeration
is called exhausted. For each repeated atom in a SAT case, a separate query
forbids its first value with50000nodes/1second. A full alternative code is
saved if found. Exhaustion implies only conditional fixedness in that one case;
timeout leaves that atom's ambiguity open. Singleton values receive no name
identification credit. There is no uniqueness claim from one first witness.

The runner reuses986's frozen ground-witness checker; no cvc5call or larger
solver budget is used. It reports full codes/alignments, primary finite
exhaustions, bounded unknowns and errors separately. Original986status is a
column, never overwritten. A contradiction here can settle a previously unknown
conjunction without altering the historical result of its original computation.

## Separate validation and engineering controls

Before target fitting, a Cartesian-product brute oracle checks all5100small
source/word-partition cases over two symbols and two characters. Both the
forward procedure and the separately written reverse checker must agree with
that oracle. Each fixed111atom source order also has an unpinned known full-code
positive control; ground witnesses must satisfy all seams and prefix conditions.
A one-character-alphabet collision control must fail. These are engineering
controls, not controls of the historical meaning search.

The separate validator imports neither runner nor finite.py. It reconstructs
both streams from the source trees, verifies every inherited case/input, and
checks every full or alternative witness directly. It replays every primary
finite exhaustion from right to left using suffix candidates from independent
substring domains, prefix incomparability and a remaining-length interval. Each
replay has1000000nodes/20seconds, with16workers. Reverse exhaustion independently
corroborates the equation's contradiction. A replay timeout is explicitly an
unverified primary exhaustion; a replay witness conflicts and fails validation.
Projection exhaustions are not independently replayed. All checks are by the
same author; no human-independent review or meaning test is implied by PASS.

## Exposure and stopping

All previous986targets and results have been seen; there is no new blindness,
new data intake, reserve opening or independent confirmation leaf. f84/f84r,
f116v and all reserves remain closed. Source tree interpretation, minimal
writing assumptions and known whole-form/context residuals remain unresolved.
No suitable full-search null exists; no significance or confirmed word follows.
At the inclusive02:35UTC checkpoint, or earlier once complete, close this attempt.
Without a full candidate, stop computation on this source rather than start a
third algorithm, wider code rule or repaired semantic tree.
