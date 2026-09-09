# GDT889 — Whole-form one-edit correction capacity

## Decision, predecessors and budget

IDEA000114 asks whether similar written groups could be redundant encodings
that guarantee recovery of their message after one insertion, deletion or
substitution. GDT338 tests predictive equivalence of opaque normalized fields;
GDT883 tests overlapping latent blocks. Neither supplies this error-ball bound.
The missing quantity is the maximum number of distinct messages compatible with
all fixed valid forms, without guessing any message or assigning a language.
If the bound is one, the model carries no distinctions among these forms. If it
is greater, retain the exact forced classes and their finite capacity; reject
only injectivity if a class contains distinct forms. A noninjective model is not
refuted without an independently justified message-count requirement.
Smallest adequate test: one fixed published cache, exact one-edit balls and an
independent all-pairs dynamic-programming check. Total wall budget25minutes from
17:50 to18:15UTC includes preparation, execution, validation and publication.
No contextual decoder, error-radius change, extra corpus or semantic scoring.

## Frozen observations and model

Use all1,617 GDT883 SELECTED_GROUPS entries and their749 distinct raw strings,
unchanged. They already have definite outside boundaries, literal raw equality
and exact STA agreement in all three readings. This is the old odd-leaf subset,
not new evidence or three independent manuscripts. No raw TSV, image or even
leaf access. f84 and f84r remain explicitly sealed.
Only literal raw characters are units here; alphabet is their fixed observed
union. Spaces/boundaries are externally supplied and not edited. A transposition
is not a single edit. Every observed whole form is assumed to be a valid intended
codeword, not an already corrupted spelling. A deterministic context-free decoder
must give the same message throughout its entire radius-one Levenshtein ball.
Several valid codewords may carry one message. No claim about actual meanings.

## Exact theorem and algorithm

Two unit-edit balls intersect if and only if their centres have Levenshtein
distance at most two. The forward implication is the triangle inequality; the
reverse follows by taking a midpoint of a shortest path. Such a path needs no
letters outside the observed alphabet. Therefore connected centres must carry
one message, even when a component's endpoints are much farther apart.

The number of connected components is an exact maximum for this finite set,
not merely a loose upper bound: give each component a different message and map
the union of its edit balls to that message. Different components' ball unions
are disjoint. Arbitrary other received strings can be declared invalid. Additional
unobserved valid codewords could merge these classes but cannot split them.

The producer explicitly constructs all balls and a shared-received-string
spanning forest. Every forest edge retains the two centres and an intersecting
received string. The independent validator uses full Levenshtein dynamic
programming for every distinct pair and BFS components; it imports no producer
algorithm. It checks all retained witnesses, exact source identities and counts,
maximum capacity, and source-free positive, disconnected and transitive fixtures.
Completeness concerns this fixed set of valid forms and this fixed error model.
No capacity count is a recovered lexeme or a general rejection of redundancy.
