# GDT885 — all reversible three-state line machines

Prospective mechanism contract, 2026-09-09; target ranks unopened.

GDT882 excludes fixed additive line sums and constant products in solvable
groups. It explicitly leaves open a weaker question: can every complete line
send one common starting state to one common final state under fixed reversible
character actions? A proper point stabilizer need not be a normal subgroup.
This test answers that remaining question for three states, allowing unused
states but requiring the start orbit to be nontrivial. No language is assumed.

Reuse precisely GDT882/artifacts/SELECTED_LINES.json: 413 complete concordant
literal lines on 43 odd physical leaves, 20 characters, reference f19r.8.
No new TSV projection, image, even-leaf reading or sealed-data access occurs.
The three transcriptions are alternate readings, not replications. Line order
and all literal characters remain unchanged; spaces were already erased by882.

Every permutation of three states is uniquely x -> epsilon*x+b over F3,
epsilon in {1,-1}, b in {0,1,2}. Relabel the common start as0. For each of the
2^20 sign assignments, the endpoint of word w is c_w(epsilon) dot b.
Thus common endpoints are exactly (c_w-c_reference) dot b=0 for every line.
Enumerate every sign mask, bit1 meaning -1 in lexicographic alphabet order,
and compute exact rank over F3. A full rank20 forces b=0, so all letters fix
the starting state. If every mask has rank20, there is no nontrivial reversible
machine on at most three states satisfying this common-endpoint contract.
The arbitrary common endpoint is not set equal to the starting state.

The producer accumulates coefficients by a reverse suffix-sign scan and uses
two bitsets for exact ternary elimination. The independent checker uses forward
coefficient-vector recurrence and array elimination. Compare the complete
one-byte-per-mask rank vectors, not just aggregate counts. Synthetic fixtures
verify all six affine permutations and endpoint expansion; no control decoder
is built. A rank-deficient result requires an explicit nonzero null vector and
direct permutation replay before compatibility is reported. At most100 such
spaces need diagnostic display; the full rank vector preserves exhaustive scope.
No even-leaf source is opened automatically: first freeze a nontrivial candidate
and a separate complete prediction contract. A compatible machine alone is not
a writing rule, historical identification or meaning.

Decision note: full rank throughout closes the three-state endpoint mechanism;
a genuine nontrivial solution nominates an independently held prediction;
timeout/disagreement stops interpretation. This differs from882's group-product
constraint and from old pairwise-preserving statistical line-assembly tests.
No raw term frequency, tuned language score or inherited working gloss is used.

Budget:45 minutes total from03:16UTC including implementation, independent
verification and publication; native runs each stop after1200 seconds and use
at most16 OpenMP workers, at most32 workers combined. Unprocessed masks are255,
never silently full-rank. No automatic larger-state, error-tolerant or alternate
segmentation follow-on. Incorrect authorial transcription/scope remains outside
the conditional exact result. Confirmed meanings remain zero.
