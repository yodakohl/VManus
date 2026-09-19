# Whole-record recurrent code, with singleton spans only

For the unchanged four SOURCE atom arrays, count each type globally. Retain
exactly every type occurring more than once: 78 types, 358 occurrences. Replace
only maximal consecutive runs of globally singleton occurrences with one named
span each: 150 spans, 255 source occurrences. Retain every recurrent atom and
its order, including 208 directly adjacent recurrent pairs without free gaps.

Any GDT963 full code restricts to a nonempty pairwise prefix-free assignment for
these 78 variables. Each singleton run concatenates at least as many characters
as source atoms, since original atom values were nonempty. Therefore that full
code gives a witness for this model. Conversely a free span may begin with,
contain or equal a recurrent value, and may lack any prefix-free split into its
original singletons. SAT of this relaxation cannot certify the original code.
There were no cross-occurrence singleton equalities to learn; their injectivity,
prefix conditions and internal boundaries are precisely the relaxed obligations.

The search uses exact string concatenation, not greedy matching. All recurrent
values and permitted page selectors are solved together. Each term has a
nonempty lower length bound; each upper bound comes from maximum whole-page
length minus the other mandatory minimum atom lengths. No fitted length cap.
Four page-choice disjunctions include exact strings and physical-leaf IDs; a
single DISTINCT condition requires four leaves. Partitioning fixes only the
I.1 page. The old necessary name-code/IV.20-page rows form an additional OR,
including every GDT977 surviving base row in that partition. The old saved
LEAF/BROAD witnesses and their earliest positions are not constraints.

Source-only controls include: a legal recurrent projection whose singleton
span collides with a recurrent code (showing the strict claim ceiling), a
forbidden zero-length singleton span, a forbidden shared leaf, and a forbidden
insertion between adjacent recurrent values. Solver results are not all called
meaning evidence or mathematical proofs. Each SAT is checked by a ground
validator using exact concatenation, minimum span lengths, full code inventory,
prefix collisions, full page identity and the complete inherited name catalog.
UNSAT_SOLVER is a solver answer, not an independently checked proof. Time or
process limits remain UNKNOWN. Errors remain errors.

One SAT witness per partition is an existential certificate. It leaves other
base rows inside that partition unclassified; they are not silently all called
SAT or UNSAT. Each of all 8,990 original rows retains either its four inherited
contradictions or its new partition/witness status. Exact source-index/character
alignments for any witnesses are supplied without inventing boundaries inside
singleton spans. No complete word reading, significance or independent meaning
binding follows, and reserves remain closed.
