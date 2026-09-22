# RAW370 development V2: material, carrier and grinding contract

**Exploratory revision, not a rescued test or semantic PASS.** V1's65 lexical
entries,15 reader-alias assumptions, all raw lines/annotations,18 surface
production schemas and four rival settings remain unchanged. The three V1
files remain byte-frozen. This document replaces the underspecified material
effect/compatibility layer; it does not pretend that those rules were already
complete. The [V2 binding document](raw370_powder_partition_v2_material_contract_20260922.json)
identifies every inherited block and the unchanged source hashes.

## Explicit changes from V1

1. V1 contract6 universally made CRUSH/GRIND create coarse and powder
   submaterial. V2 **removes that mandatory production claim**. Comminution
   may produce both sizes, but it cannot manufacture a coarse fraction from
   material already entirely fine. Positivity of a named later fraction is a
   later textual requirement, not an automatic effect of grinding.
2. A physical aggregate and its plant-solid, water and oil components are
   different objects/roles. Incorporation removes a component from the free
   stock account; it does not duplicate or annihilate its mass.
3. V2 closes the nominal matching table below. POWDER is restricted to the
   model's fine-powder stock type; coarse grist, fibres, granules and a whole
   paste are excluded. This is an explicit model convention, not a recovered
   universal taxonomy of the historical word.
4. GRIND acts on plant solid inside a carrier. It preserves water/oil
   components and the enclosing preparation carrier. Hence GRIND on paste
   yields ground paste, not a new free dry-solid stock. This applies to every
   eligible mixed input, without a rule naming f32v.11.

The English label GRIND stays fixed, but its operational denotation is now
completed and its previous universal coarse-output condition is weakened.
That is a substantive revision. No target result was executed between V1
and this change.

## Closed finite material matching and access

Each material node has a source ancestry, tracked plant-solid mass, physical
carrier, particle grade, properties, and status `free`, `contained`, or
`consumed-as-a-separate-stock`. A consumed parent remains a provenance record;
its mass is not added to its children's mass. A prospective goal is a
description, never a material node.

| Written nominal role/value | Permitted node class in this finite model |
|---|---|
| ROOT_MATERIAL | initially introduced root stock A |
| PLANT_MATERIAL | a pure plant-stock A/B/C/P/F/G, including its adhering rinse water; not a whole oil/water paste |
| PREPARED_BULK | current prepared particulate aggregate B, before it is spent into separate branches |
| COARSE_GRIST | a standalone coarse-grist form |
| COARSE_PART / COARSE_FRACTION / COARSE selector | coarse branch C of the relevant grade partition |
| RESIDUE | C of that grade partition; no arbitrary later remainder |
| POWDER | a standalone fine-powder form, such as P or a selected/refined output U/V |
| FINE_PART / FINE selector | the fine branch of the relevant partition |
| FIBRES | sorted coarse product F |
| GRANULES | sorted coarse product G |
| PASTE | enclosing kneaded aggregate T |
| WATER / OIL | water/oil components W/O, under the access rules below |

These are closed matching predicates; all other matches are false. A current
prepared bulk may also have an all-coarse or all-fine form, so PREPARED_BULK
is a preparation-role predicate rather than a competing substance. F/G are coarse
with respect to the grade split and are not POWDER subtypes. Paste contains
powder but is not itself a free powder stock. FINE and COARSE are disjoint
particle-grade properties; neither means DRY. CLEAN is a separate property.
An operation that changes a standalone solid's grade also updates its form
class: an all-fine result is a powder stock; a mixed result is bulk. An
enclosing paste retains its carrier class while its solid component changes.

The letters A/B/C/P in the ledgers are record names, not literal lookup keys.
For example, B names the current prepared aggregate even when a possible
comminution outcome has only one nonzero grade; its actual form class is then
coarse grist or powder rather than a mixed bulk. The class is computed from
material/form state, not from a locus. A branch-reference role additionally
requires the appropriate partition-parent relation. No new free object is
created solely to obtain a desired form-class label.

Access is role-specific and exhaustive here:

* Ordinary material reuse, RETRIEVE, KEEP, and kneading inputs require a
  **free** compatible node. A contained component cannot be spent again.
* An inventory immediately before SEPARATE describes the disjoint coarse
  and powder components of B. They need not already be separate free stocks.
* A partition-part reference selects its explicitly associated branch.
  UNTIL selects the designated output of its own operation, not whichever
  later noun happens to look similar.
* WITH_MEDIUM may refer to water directly contained in the active aggregate.
  It neither frees that water nor introduces another supply.
* External input introduction remains limited to the original source/input
  rules and the declared WATER/OIL supplies. The FRESH rival changes only
  the already specified unmarked-input-list rule.
* Tools, manner words, elapsed time and prospective goals introduce no
  plant-solid stock. There is no free stock created merely by a matching noun.

These rules complete the intended P-only lookup at f32v.10. It follows
conditionally from this **new closed table**, not from object inequality
alone or an inferred universal meaning of “powder”.

## Global effects and still-unbound physical parameters

Let plant solid have uncomminuted/coarse/fine size classes. CRUSH eliminates
the uncomminuted class into coarse and/or fine material. GRIND transfers
material only toward equal or smaller particle sizes. Both conserve tracked
plant solid and preserve any enclosing liquid/paste carrier. In a two-grade
bulk this can be written `c' = c − a`, `p' = p + a`, `0 ≤ a ≤ c`.
All-fine input has c=0, hence no new coarse output. The particular amount a
is not determined by the words or a new target observation.

DRY removes retained carrier water, not tracked plant solid or oil. RINSE
adds its written water supply and may remove extraneous dirt, while retaining
the desired plant-solid amount. MIX redistributes the existing bulk. SEPARATE
separates its grade components. SORT partitions the selected input into the
two named disjoint products. KEEP/COVER/STORE alter retention/location,
not material amount. KNEAD incorporates the listed inputs into one T; their
components cease being free. SIEVE produces a selected passing fraction plus
a disjoint remainder, with their combined plant mass equal to its input.
Refinement of already fine powder can leave two fractions that are both
fine relative to the earlier grade threshold. It need not create a coarse
branch; an unnamed zero remainder is represented by no material node.

The global frame rule preserves ancestry, component amounts and properties
except where an operation explicitly changes them. Entry assertions such as
FRESH describe the input at that step, not an obligation that processed
material remain fresh. DRY, FINE and CLEAN remain separate; the idealized
ledger assumes no unmodeled contamination. Water removed by DRY enters an
external vapor register; rinse drainage enters a spent-water register.
Neither register is an available ingredient supply. Thus initial moisture
and rinse water are accounted for without adding plant mass or silently
providing water for later operations. GRIND removes neither water nor oil.

The actual grade threshold, mesh openings, tool identities, grinding extent,
rinse-water amount, oil amount, initial moisture and process efficiency are
not measured. WITH_SIEVE is a tool kind, not a claim that every use has the
same sieve or cut. In particular, sorting the already coarse f32v branch
into two positive products requires an appropriate further discriminator
(for example a different size cut or shape-sensitive sorting). V2 does not
assert that one unchanged perfect binary cut could do this twice. The chosen
SORT outputs must be physically feasible under some such parameter setting;
that feasibility has not been independently established. No tool value is
changed and no favorable mesh parameter is presented as manuscript evidence.

## Hand-checked state ledger: f21r, identical for all four rivals

Q>0. M is the initial tracked plant-solid mass. Water quantities h are
separate. A/B labels below denote successive forms of the same source stock,
not two simultaneously countable masses. `S{…}` lists free stocks. An active
partition frame without a selected physical branch is written `frame`.

| Written operation/binding | Before | After / required condition |
|---|---|---|
| .8 ACQUIRE root FRESH | no material stock | S{A:M}; active A; native moisture h0≥0; source ancestry A |
| .8 DRY | A:M, water h0 | A:M, retained water0; DRY true |
| .8 CRUSH | A:M | S{B:M}; component amounts c0,p0≥0, c0+p0=M; no automatic claim that both are positive |
| .8 FOR_OUTPUT powder Q DRY | B remains available | future goal G=(powder,Q,DRY,source A); **no additional stock** |
| .9 RINSE water UNTIL CLEAN | B:M; written rinse supply w>0 | B:M, retained water 0≤h1≤w, CLEAN; the rest of w is drainage, not plant mass |
| .9 SPREAD thinly/evenly plant material | B:M, CLEAN | same B and amount; spread/thin/even properties; no new plant material |
| .10 DRY in sun | B:M, water h1 | B:M, water0, DRY/CLEAN |
| .10 GRIND coarsely | B(c0,p0) | B(c1,p1), c1=c0−a, p1=p0+a; 0≤a≤c0; later conditions require c1>0 and p1≥Q |
| .10 SEPARATE coarse FROM fine with sieve | B(c1,p1) | S{C:c1,P:p1}; B no longer a free whole; active frame; both dry/clean |
| .11 KEEP fine | C and P free | P stored; active P; S unchanged |
| .11 KEEP coarse | C and P free | C stored; active C; S unchanged |
| .11 COVER with cloth | active C:c1 | same C, covered; cloth adds no plant solid |
| .11 STORE_SEPARATELY residue | C:c1 selected by its grade-partition identity | C separately stored; P:p1 still free; no new “residue” node |
| .12 RETRIEVE powder | S{C:c1,P:p1}; active C | select existing P:p1; C stays stored; the future goal is not a candidate |
| .12 SIEVE UNTIL powder FINE Q CLEAN | P:p1≥Q, dry/clean/fine | S{C:c1,U:Q,V:p1−Q if positive}; P no longer separate; U selected by UNTIL, source A, DRY/FINE/CLEAN |

Every physical operation in the complete paragraph is represented. THEN
orders clauses; properties and amounts constrain their named nodes. The final
goal is checked on U. `c1 + Q + (p1−Q) = M`; because c1>0, M>Q. The initial
mass and the two comminution distributions remain free subject to these
constraints. This is a conditional feasible ledger, not a prediction that
arbitrary root stock succeeds. No coarse material is produced by the final
sieving of already fine P.

## Hand-checked state ledger: f32v CARRY+ADD

The initial stock has plant mass N and native moisture h0. Its written later
inventory requires N=3Q in this reading. W:w and O:o are physical input
components with w,o>0; neither quantity is Q merely because the solids are.

| Written operation/binding | Before | After / required condition |
|---|---|---|
| .7 root introduction | no stock | S{A:N}; active A |
| .7 CRUSH | A:N | S{B:N}, coarse c0 and powder p0, c0+p0=N |
| .7 DRY overnight in shade | B:N, native water h0 | B:N, retained water0; DRY; duration does not by itself prove physical completion |
| .7 MIX thoroughly/evenly prepared bulk | B:N | same B, redistributed; no extra ingredient |
| .8 inventory coarse Q Q, powder Q | B:N | require c0=2Q,p0=Q,N=3Q; the inventory adds no material |
| .8 SEPARATE | B=C+P, amounts2Q+Q | S{C:2Q,P:Q}; B ceases to be free; active frame |
| .8 LIFT_OUT the coarse fraction | C:2Q and P:Q free | active C:2Q; P:Q retained untouched; nothing discarded |
| .9 SORT with sieve | C:2Q active | S{F:f,G:g,P:Q}, f,g>0 and f+g=2Q; C no longer free; product types supplied by the whole following product-list construction |
| .9 KEEP fibres Q, granules Q | F:f,G:g,P:Q | require f=g=Q; F/G stored, active G; P still free Q |
| .10 water/oil/powder ingredient list | free F:Q,G:Q,P:Q | select P and introduce W:w,O:o; these are the complete kneading inputs; no extra powder |
| .10 KNEAD TO paste ONE PORTION | selected P,W,O free | S{F:Q,G:Q,T}; T contains P:Q,W:w,O:o; these components are not free separately; active T, one paste batch |
| .11 WITH_MEDIUM water | active T with contained W | select T.W as medium, without adding/freeing water |
| .11 GRIND | T, plant-solid component entirely fine Q; W:w,O:o | same paste carrier T, plant solid Q still fine, W:w,O:o retained; S{F:Q,G:Q,T}; no new coarse or free powder stock |

The decisive .10 lookup does not inspect the live paste, because it occurs
before kneading. It selects P across the intervening work on C. At .11 the
lookup has a different explicit role: access to the contained medium. It
cannot be used as an unrestricted exception allowing later powder reuse.

## Complete rival continuations

The entire f21r table is shared by all rivals: none of their changed
constructions occurs there. On f32v the following tables retain every
operation. Entries mentioning earlier rows inherit exactly their before/after
state, not an omitted new reading.

### FRESH_INPUT_LISTS

| Operation/binding | Before → after |
|---|---|
| introduction, CRUSH, DRY, MIX | Same four transitions as CARRY, but N stays unconstrained by the later new inventory; prepared B:N remains free thereafter. |
| .8 measured input list | S{B:N} → S{B:N,E:3Q}; E is newly supplied coarse2Q+powderQ. |
| .8 SEPARATE | E:3Q → C:2Q and P:Q; B:N untouched. |
| .8 LIFT_OUT | C/P/B free → active C:2Q; P:Q and B:N untouched. |
| .9 SORT | C:2Q → F:f,G:g, f+g=2Q; P:Q and B:N untouched. |
| .9 KEEP | f=g=Q required; F/G stored; P:Q and B:N free. |
| .10 input list | Introduce fresh P′:Q,W:w,O:o; do not select old P. |
| .10 KNEAD | P′,W,O → paste T containing those components; old P:Q, B:N and F/G:Q each remain free. |
| .11 WITH_MEDIUM | Select contained T.W; no addition. |
| .11 GRIND | T remains paste with fine solid Q and its same W/O; all other stocks remain. |

Total supplied plant solid is N+4Q; final stocks total
`B:N + old P:Q + F:Q + G:Q + T-solid:Q = N+4Q`.
This rival remains coherent and materially different. No hidden “use
everything” clause is introduced to dismiss its leftovers.

### REITERATED_QUANTITY_ASSERTION

| Operation/binding | Before → after |
|---|---|
| introduction, CRUSH, DRY, MIX | Same transitions as CARRY until the inventory. |
| .8 inventory | c0=Q asserted twice, p0=Q; N=2Q. No two-Q coarse stock. |
| .8 SEPARATE | B:2Q → C:Q,P:Q. |
| .8 LIFT_OUT | Select C:Q; P:Q untouched. |
| .9 SORT | C:Q → proposed F:f,G:g, f+g=Q in the fixed lossless rule. Even relaxing this to f+g≤Q with nonnegative loss will not help. |
| .9 KEEP | Requires f=Q,g=Q, impossible since Q>0. This is the first incompatible postcondition. |
| .10 ingredient list/KNEAD; .11 WITH_MEDIUM/GRIND | All source words and values remain in the full reading, but no reachable state satisfies the already failed prior condition; these operations are not falsely reported as executed. |

Local routing gives Q≥2Q, impossible. The separate global argument needs
exhaustive inventory, no new plant-solid input, and three disjoint still-live
terminal stocks; it gives2Q≥3Q. Neither argument identifies Q. Nonnegative
loss cannot rescue the contradiction. Other assignments of ownership,
overlapping product descriptions, or new supply would be different rivals.

### TWO_EQUAL_PORTIONS

| Operation/binding | Before → after |
|---|---|
| introduction, CRUSH, DRY, MIX | Same transitions and eventual total N=3Q as CARRY. |
| .8 inventory | Coarse stock comprises C1:Q and C2:Q, plus disjoint fine P:Q. |
| .8 SEPARATE | Produces one collective coarse branch C={C1,C2}:2Q and fine P:Q; the two portion identities remain in provenance. |
| .8 LIFT_OUT | Selects the collective C:2Q, not an arbitrarily chosen individual Ci. |
| .9 SORT | C → F/G; F may contain a from C1 and Q−a from C2; G then contains Q−a from C1 and a from C2, 0≤a≤Q. |
| .9 KEEP | F=G=Q; P:Q untouched. No later word fixes a or identifies F with C1. |
| .10 ingredient list/KNEAD | Existing P:Q plus written W/O → T, exactly as CARRY. |
| .11 WITH_MEDIUM/GRIND | Same contained water, preserved paste carrier and fine solid Q as CARRY. |

Its mass equation is identical to ADD. V2 supplies no new distinction between
one coarse portion2Q and two coarse portionsQ+Q.

## What survives and what is withdrawn

The local repeated-assertion contradiction survives without depending on
the final grinding step or on zero loss. The global3Q accounting survives
under its separate exhaustion/disjoint-terminal-stock assumptions. CARRY
versus FRESH still predicts different prerequisite supplies and leftovers;
ADD versus TWO remains unselected. The initial f21r goal is still not stock,
and its final selected powder remains source-bound.

Withdrawn is any claim that V1 already supplied a complete carrier update or
that every grinding action produces two positive grades. V2's closed matching
table is an additional assumption. The complete symbolic ledger is internally
consistent only subject to the stated stock, sorting and successful-process
conditions; no physical sieving experiment, unique parser, new target run,
whole-corpus search, probability or historical meaning confirmation follows.

No new paragraph, image, reserve or source was opened. All lexical values,
reader variants and surface production schemas remain those of V1; this is
the explicitly changed global semantic layer offered for criticism.
