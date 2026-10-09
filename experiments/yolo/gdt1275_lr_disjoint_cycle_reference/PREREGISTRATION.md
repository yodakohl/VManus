# GDT1275: fixed disjoint-cycle reference (exploratory)

## Decision before calculation
915's known r/l families covary on even physical leaves;916's new stem-pair
transfer failed.1260 has score mobility after preserving line and old
leaf/stem/position counts.1261's full-fibre exact counter hit its state cap,
with zero reference worlds. Its global conditional question stays open.
Unknown here: does the fixed915 score exceed an exactly computable, much narrower
reference with both margin systems, across at least five score-variable leaves?
A positive robust residual warrants retaining a local family-specific dependence
beyond these line totals within this orbit. A nonpositive/fragile residual gives
no such support; low capacity parks this reference. None selects grammar or
meaning, rejects all line-state mechanisms, or reclassifies1261 as successful.
Smallest test: one fixed undirected cycle packing of the old validated population;
analytical exact expectation and variance, no global sampler or fitted decoder.
Inclusive outer budget: previous completed checkpoint13:04UTC to14:14UTC on
2026-10-08, including predecessor review, proof consultation, implementation,
validation and local closure. This is a conservative allowance, not a measured
70minutes of active experiment work. Stop expansion at the deadline.

## Fixed population and packing
Inputs are1260 TOKENS/PAIRS and915 CANDIDATES; all readers separate, ZL3b primary.
All eligible1260 tokens retained, including non-pair tokens. The22old nominees
remain fixed. No new selection, images, source admission, reserve or meanings.
One edge per distinct token connects its source line (page,locus) to its old
cell (physical leaf,exact stem,physical position). Ignore ending/mobile fields
when choosing cycles. Distinct parallel edges remain distinct.
Anchor order: old nominated-pair endpoints first, then others; within each,
lexicographic source_id order (integer token index breaks ties). Adjacency edges
use this same stable source_id order, without the endpoint priority.
For each unused anchor(u,v), BFS from u to v in remaining undirected graph,
excluding the anchor, chooses the lexicographically first shortest edge path.
If found, select [anchor]+reverse(path) and remove its edges; otherwise skip.
No edge in two cycles; sharing vertices allowed. No cycle-length cutoff,
repacking, label-dependent optimization or alternative reference tried.
After this packing is fixed, a cycle is active iff r/l labels strictly alternate
around it. Independently flip every active cycle with a fair bit. Everything
else stays fixed. Activity is invariant under all flips; this is exactly uniform
on that restricted orbit, NOT on all assignments with the two margin systems.
1260's directed, label-dependent witness cycles are not reused.

## Score and fixed decisions
For every physical leaf having any eligible pair, the score is nominated
same-minus-mixed pairs divided by ALL eligible pairs on that leaf. Average
equally over these leaves, including zeros. Evaluate all22families together.
Use signs r=-1,l=+1 and one independent Rademacher variable per active cycle.
A pair contributes a constant, one variable or the product of two variables.
Combine coefficients of identical monomials BEFORE summing squares for variance.
This yields exact rational mean/variance, without Monte Carlo or world enumeration.
A score-variable leaf has strictly positive exact variance; five are required.
Capacity decision precedes effect interpretation. If below five: CAPACITY_STOP.
Otherwise ROBUST_POSITIVE_RESIDUAL only if observed-minus-mean>0 and remains>0
after deleting each eligible leaf in turn; otherwise NONCONFIRMING_OR_FRAGILE.
These are descriptive decisions, no p-value, significance or fresh holdout.
IT2a/RF1b are sensitivity readings of the SAME manuscript, not replications.
Report eligible/nominated counts, cycles/active cycles, score-variable leaves,
observed, exact mean/variance, residual and minimum leave-one-leaf-out residual.
No fitted parameter or post-result threshold adjustment.

## Assumptions and checks
Inherited tokenization, paragraph-text admission, definite-pair filter, stems,
line positions and nominees are1260/915 conventions, not proven linguistic units.
Previously exposed even leaves and discovery-based nominees are not blinded.
Validate independently selected paths by reverse-distance greedy reconstruction,
cycles/disjointness/alternation, margins, full pair scores and exact moments.
Small artificial graphs exhaustively enumerate assignments and orbit states,
including parallel edges, vertex sharing and cancelling coefficients. Native
input/protocol/program hashes locked before calculation. NoGDT388 semantic edge.
