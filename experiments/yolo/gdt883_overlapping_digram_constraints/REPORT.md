# GDT883 — overlapping blocks force extensive homophony

The fixed injective overlapping-block model fails at both preregistered unit
scales. In the exact STA member panel, 25 of 33 written symbol codes are forced
to denote one identical underlying block. The result applies to every fixed
block length k>=2 with advance 1 and overlap k-1; it is not a key-search failure.
A homophonic version remains mathematically possible, with a sharply limited
underlying channel. No meaning is identified.

| Fixed unit scale | Symbol types | Equality components | Symbols forced to one identical pair | Maximum distinct underlying group strings |
|---|---:|---:|---:|---:|
| Literal EVA character | 19 | 4 | 16 | 32 |
| Exact official STA member code | 33 | 9 | 25 | 38 |

Both panels contain the same 1,617 groups, 749 distinct raw forms, 270 loci and
42 physical leaves. Three complete raw-group arrays agree exactly; both outside
boundaries of every retained group are definite or line ends. All retained STA
member sequences also agree exactly, without marked alternatives. The scope is
an admitted subset of GDT882's odd-leaf source, not a new manuscript sample.
142 source loci have differing group arrays; another 111 groups have an uncertain
outer boundary. They supply no constraints. No even-leaf source was queried.

Every observed gh imposes R_g=L_h. The two panels supply 131 and 196 different
adjacencies, respectively, with 6,728 and 4,936 occurrences. Their complete
solution is the endpoint equality graph. The published source-witness forests
have 34 and 57 edges. Any assignment into any underlying alphabet must respect
these equalities. Different component labels may be merged but cannot be split.

In the STA panel the forced identical-pair class is:
`A1 A2 A3 B1 B2 C1 C2 E1 F1 F2 F3 G1 J1 K1 K2 L1 M1 N1 P1 P2 Q1 Q2 T1 U1 U2`.
The corresponding EVA class is:
`a c d e f h i k l n o p r s t y`.
These are transcription codes, not established linguistic units.

The homophonic pair model has a particularly simple maximal reconstruction.
Every actually observed internal boundary has the same latent value, component 0.
Only the first/last value and group length can distinguish the reconstructed
strings. Thus the 749 raw forms yield at most 38 different STA-based strings
(32 EVA-based strings). In the STA panel, for example, `daiin`, `chckhy`, and
`shol` at f103r.23 must all decode to the same four identical latent symbols.
Other models are not required to equate these forms.

The same bound holds for any one fixed block length k>=2 at advance 1: each
symbol has at least one endpoint in component 0, so overlapping coordinate
constraints leave only the first coordinate of an initial-only symbol or last
coordinate of a terminal-only symbol free. Increasing k adds identical core
values to the reconstruction; it cannot recover lost distinctions. This is a
mathematical corollary of the observed graph, not a second tuned experiment.

Independent validation reconstructs all source selections and exclusions through
the guarded STA query, computes graph closure with BFS independently of the
producer's union-find, and verifies every witness and every adjacency: PASS.
Three source-free algebra fixtures also pass. The preregistration and source
were published as commit 83c9f5d4 before extraction/scoring.

This closes the injective fixed-block hypothesis at these two fixed unit scales.
It constrains the homophonic version without claiming that a 38-string message
alphabet is logically impossible. Different segmentation, variable block lengths,
other advances, stateful encoders, errors and ordinary abbreviation remain
outside the test. No automatic exception or segmentation search follows.
