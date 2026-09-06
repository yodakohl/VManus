# GDT856 — free unique decodability of a published finite code

This is a property test of GDT605's published98final-unit inventory. The
inventory contains observed final BPE tokens, not automatically all initial
symbols and merge parents. GDT605's fixed ordered merge algorithm already
gives a canonical parse; that is distinct from unique free concatenation of
arbitrary inventory codewords. No BPE learning or language fitting is needed.

Input only the unit column of the frozen aggregate inventory. Preserve exact
case-sensitive collapsed-symbol strings; no expansion into EVA or physical
glyphs, normalization, frequencies or manuscript sequence access. The old
GDT605 scope used180selectors, while current text scope is179. This pass
asserts a property of that published aggregate model, not a finding over the
current179corpus or a new page admission. f84/f84r remain explicitly sealed.
Source hashing before registration is permitted for this aggregate inventory;
no unit-content inspection occurs until public GO.

Require98nonempty distinct units. Missing/invalid unit column, empty entries,
duplicate units or wrong count cause INVALID_INVENTORY_STOP, with no code
conclusion. Ignore all frequency and occurrence columns.

For distinct prefix-comparable codewords u,v, initialize two different
one-codeword sequences. A state (side,residual) records which concatenation
is longer and its unmatched nonempty suffix. Append one codeword to the
shorter sequence. If that codeword equals the residual, the concatenations
collide. If one is a prefix of the other, retain their unmatched suffix and
appropriate longer side; otherwise no transition. Explore breadth-first,
starting with lexicographically ordered unordered codeword pairs and adding
codewords in lexicographic order. Keep one witness path per state.

Every residual is a nonempty proper suffix of an input codeword. There are
at most twice the number of such distinct suffixes oriented states. Exhaust
all reachable states and all possible codeword transitions. A collision
returns two distinct finite codeword sequences and their identical exact
concatenation. No shortest-witness claim. Exhaustion without collision gives
a complete finite certificate: initial states, reachable states, all viable
transitions, suffix universe and checked-state count. Empty initial states
are a valid prefix-free certificate. Non-UD output has a witness and may
have only a partial search graph; it is not called a full exhaustion proof.

An independent validator runs a separate unoriented residual-set closure
and verifies each returned witness or complete certificate. Controls before
inventory loading: {0,01} uniquely decodable despite prefix overlap;
{0,01,10} non-UD (010=0|10=01|0); {0,1} UD; {a,aa} non-UD;
duplicates and empty strings invalid. No synchronization or noise-recovery
study. Controls validate finite-code software only.

NON_UD means the inventory alone does not determine an unrestricted free
segmentation; canonical merge rules or context supply additional constraints.
The collision string need not occur in the manuscript, and neither codeword
sequence need be a canonical BPE output. Collapse preprocessing and source
grammar may impose further legality constraints. Non-UD does not imply
ambiguous authorial writing.
UD means only this exact finite dictionary has unique concatenations. Neither
outcome establishes manuscript segmentation, a natural alphabet, plaintext,
language, meaning or authorial intent. Invalid input stops without repair.

Budget15min total from05:58:40UTC through root publication, ending06:13:40UTC.
Freeze code, controls, source hash and protocol before public registration;
root sends GO before unit loading. No source expansion or decoder successor.
