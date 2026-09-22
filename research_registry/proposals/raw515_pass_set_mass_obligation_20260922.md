# IDEA515: pass-set and exact mass-cut obligation

22 September 2026. Short content-development note only. No new RAW card,
experiment, simulator, target census or manuscript outcome. All old words,
reader alternatives, complete readings and decisions remain unchanged.

## Fixed evidence and earlier status

The unchanged IDEA515 source is
`raw370_nested_sieve_cut_consequence_20260922.json`, SHA256
`0702d2db0000bb1129e5a18002ad60d198ddc9d9ca1eba66cb3fb6f32e501289`.
The registry records an unreviewed proposal; its primary explicitly says
RAW_UNREVIEWED_NOT_EXECUTED. A bounded exact-reference search of decisions,
experiment manifests and the material ledger found no subsequent dedicated
IDEA515 execution. This does not turn the already written conditional proof
into a new unperformed scientific discovery: the card already states the
same-cut impossibility and the larger-cut necessary condition.

The complete V2 contract is
`raw370_powder_partition_v2_material_contract_20260922.json`, SHA256
`7676250faf7adabc2fd240635a520852c65c2d7a2f8070fb82717351a8ab6d78`;
its linked MD contains every step and rival continuation. V2 already says
that one unchanged perfect cut cannot yield two positive outputs from the
coarse residue. Its execution_status explicitly records a manual ledger,
no simulator run and no semantic PASS.

The later q offer is
`raw370_q_partition_composition_offer_20260922.json`, SHA256
`57808d1291a9b47839e047112ea5395e76a647f7c22986f62b6807d9818845c1`.
Its closure is `../decisions/powder_q_partition_closure_20260922.md`, SHA256
`71ed38686a9783057eb90c61a23b69ab132cb66ce809dc32f5712e91c442c5d2`.
It adds sieve use to f32v.8, but expressly does not identify that tool's
physical cut with the second separation. Exact q decomposition was not
obtained. This note neither reopens that decision nor treats the extra tool
obligation as independent observation.

Both full old entries are exactly:

| Form | Value | Type | Gloss |
|---|---|---|---|
| otaiin | WITH_SIEVE | ToolAdjunct | mit einem Sieb |
| cfhy | WITH_SIEVE | ToolAdjunct | mit einem Sieb |

Neither says SAME_SIEVE, LARGER_MESH or COARSER_CUT. The different spellings do
not themselves distinguish mesh sizes, and their identical tool-kind value
does not identify physical instruments or settings. qotaiin remains
SEPARATE_BY_GRADE, qotchy SORT; no gloss is narrowed in this note.

## Complete chain and added premises

In the full CARRY reading, f32v.7 introduces root A, crushes, dries and mixes
it into B. At .8 B has plant-solid amount3Q: coarse C=2Q plus fine powder P=Q,
Q>0; separation and lifting select C. At .9 SORT WITH_SIEVE produces disjoint
FIBRES F and GRANULES G, each Q, retaining both. At .10 the untouched P, water
and oil are kneaded into paste T; .11 grinds T with its contained water,
retaining its carrier and fine solid. Later paste work changes neither F
nor G and cannot supply an earlier missing coarse-sorting output.

To ask about a physical pass set, add the explicit IDEA515 refinement:

1. The first separation's fine P is its passing output and C its retained
   output, exhausting the same parent stock M without lost plant solid.
2. The next SORT is precisely one pass/retain separation of that C. F and G
   exhaust its two outputs, with either assignment of their names to sides.
3. Individual particles and their plant-solid mass persist between these
   two events. There is no new supply, particle transformation, agglomeration
   or loss concealed in LIFT_OUT. A deterministic pass predicate describes
   each event. General predicates need not depend on one scalar or share
   physical orientation/tool settings.

Premise2 is stronger than the unchanged word SORT WITH_SIEVE. V2 also permits
other feasible sorting interpretations. Even q's newly explicit sieve use
in the first event does not establish these pass/retain identities by itself.

## General pass sets: exactly half of the retained mass must pass next

Let P1 and P2 be the first and second pass predicates, evaluated on the same
particle universe M. Write C = M \ P1 and let mu be plant-solid mass, not
particle count, volume, wet mass or a probability. The complete reading gives
mu(C)=2Q and mu(F)=mu(G)=Q. Under the added pass/retain contract:

    mu(C intersect P2) = Q
    mu(C minus P2)     = Q

Thus exactly half of the first retained plant-solid mass passes the second
separation, and half remains retained. This strengthens the qualitative
'some previously retained material must pass' into a fixed relative mass
obligation. Which named product passes remains a two-way open choice.

P2 cannot equal P1 on C, nor be a subset of P1 there. This **does not imply
that P1 and P2 are globally incomparable**: P2 may contain P1, or may exclude
some earlier passing material. The second event never applies to the saved P.
Without nesting, mu(P1 intersect P2) is unobserved and can range from0 toQ;
therefore a counterfactual P2 on all M could pass betweenQ and2Q. There is no
general 'coarser sieve' conclusion.

This local equation holds also for FRESH's newly introduced3Q inventory and
for TWO's collective C1+C2. It does not select CARRY over FRESH or identify
F with C1. REITERATED's Q-to-two-Q contradiction remains the older separate
mass contradiction. No new success/failure is assigned to those rivals here.

## Stronger scalar refinement: an exact mass-bisecting threshold must exist

Add one stable scalar grade g per particle and the fixed convention that a
particle passes a threshold t exactly when g<=t. Let the second threshold be
u and retain the old first fine/coarse distinction. Then:

    mu(g<=t) = Q
    mu(t<g<=u) = Q
    mu(g>u) = Q

These equations refer only to the3Q inventory entering the first partition.
They entail u>t and require u to bisect the2Q coarse branch by mass. Relative
to that inventory, the first and second cumulative passing masses are1/3
and2/3. These fractions are algebraic consequences of the guessed quantities,
not readings of a Voynich number, a measured size distribution or probabilities.
F/G remain coarse relative to t even when one passes u; no grade word is
reinterpreted relative to the most recent mesh.

A larger u alone is insufficient. For an adverse example, let all coarse
particles have the same grade a>t and total mass2Q. Any u<a passes0 from C;
any u>=a passes all2Q. No threshold supplies the required Q, although a
larger mesh exists and mass is conserved. Thus the exact mass-bisecting cut
need not exist in a discrete or tied grade distribution. Calling an arbitrary
weighted median a solution would conceal the tie convention and this gap.

A conditional witness instead places coarse massQ at grade a and massQ at
b, with t<a<=u<b, and the earlier fine Q at grades<=t. It meets all three
mass equations. This is a symbolic feasibility witness, not a supplied
particle measurement. Shape-sensitive, orientation-dependent or manual
sorting remains a different feasible rival outside the scalar refinement.

## Required f21r countercase and scientific decision

The complete f21r paragraph first creates/stores coarse C and fine P, then
retrieves P of amount p>=Q and sieves to selected fine U=Q, with an optional
fine remainder V=p-Q. For that second pass set S:

    mu(P intersect S) = Q; mu(P minus S) = p-Q.

The allowed p=Q case has zero remainder and does not require a changed cut.
Only a positive remainder would force a finer scalar cut than the earlier
fine threshold. No text requirement makes that remainder positive. No
identity between the f21r and f32v physical sieve settings is supplied.
Fine, clean and dry properties remain distinct; the earlier dry-state caveat
is not repaired by this calculation.

The exact half-mass requirement and existence of a compatible scalar cut are
more precise conditional obligations than 'a different discriminator is
needed'. They are nevertheless entailed by the existing complete quantities
plus the explicit added pass-set premises. They provide no newly observed
manuscript distinction. Neither the relevant particle distribution nor a
written relation between physical cuts is independently bound. Re-proving
these equations with a simulator would not change the research decision.

Retain this note with IDEA515 as a content diagnosis. Do not add a duplicate
RAW or select a fixed manuscript test from it. A later discriminator would
need a complete retained reading whose already bound material/cut relation
separates these exact alternatives; no unknown word may be assigned a mesh
relation merely to obtain that outcome. Confirmed meanings remain0.
