# RAW568 descendant: frozen recipient / predicate / modifier contract

Author started2026-09-27 02:42:14UTC. Absolute whole-author ceiling03:17UTC,
including preparation, self-review and freeze. First contract is written before
remaining whole-form assignments. Root decision and complete preselection were
read, together with the full568 card and exact800-byte III.9 HTML paragraph.
The composition topic and bounded ideas/route results were read. No572 value,
reference register, comparison frame or grammar is imported.

## Fixed choice and changed unknown

The choice among six recipient permutations is frozen as follows:

| Literal | Denoted value | Semantic type |
|---|---|---|
|ar|SPLEEN|AnatomicalRole|
|aiin|GALL_BLADDER|AnatomicalRole|
|ain|KIDNEYS|AnatomicalRole|

KIDNEYS retains the source's plural role; it is not a new count of physical
kidneys. These are generic anatomical roles, not newly observed organs. The
role domain can subsequently contain the separately written liver, veins,
arteries, heart and other nourished organs. Source and recipient are argument
positions of relations on these roles; their distinction is not erased merely
because both positions may use AnatomicalRole values.

No meaning is assigned to any other whole form in this first contract.
In particular, no whole-word reference or context-introducer spelling is
presupposed by the interfaces below. Those remain actual authoring obligations.

The unknown is whether a complete written account can apply the same suitability
predicate both bare and as a description modifier, with real arguments, and then
project the preserved origin of the SAME modified witness. A list of organ names,
an internal A call inside B, or an independently asserted liver fact does not
meet the requirement. A partial is admissible; this is not a guarantee of a
complete reading and does not reopen any old dictionary.

## Fixed components and denotations

Only these five cuts are licensed:

```
dar     = d | ar
daiin   = d | aiin
qodar   = qo | d | ar
qodaiin = qo | d | aiin
qodain  = qo | d | ain
```

No independent qod, extra cuts, i-run collapse, marked-form alias or general
prefix deletion is licensed. Missing free dain does not exempt qodain. ain is
always KIDNEYS here; it is not an anaphor.

Let c be an explicitly introduced generic bodily context, with compatible
Material[c] domain. Let Pred[c] = Material[c] -> Proposition. A material
description has exactly this predicate type; descriptive use does not create
a second incompatible semantic sort. Let Mod[c] = Pred[c] -> Pred[c].

```
d = A
A_c(b:AnatomicalRole) : Pred[c]
A_c(b)(x) = PROPER_FOR(x,b,c)

qo = B
B_c(P:Pred[c]) : Mod[c]
B_c(P)(D:Pred[c])(x) = D(x) AND P(x)
```

The common c is captured from an explicitly written context binder. Outside
that binder, A/B application has an unbound-context gap; there is no default
patient, time or bodily world. The bare recipient constants can still denote
roles without an active context. PROPER_FOR is not PLEASING, BENEFICIAL,
FOREIGN, ATTRACTION, NUTRITION or a faculty. FOREIGN remains an independent
recipient-relative predicate; no exhaustive negation law is introduced.

RESIDUE_FROM(liver,c) is a separately written description obligation. The root
and modifier do not supply liver origin. Applying a modifier never changes a
material's identity, owner, source, temporal state or kind. Within its qualified
assertion, the SAME x satisfies D and PROPER_FOR. Witnesses in different recipient
claims are neither forced identical nor forced distinct; some/others is retained
without an exhaustive or disjoint partition.

## Syntax/value/reference interfaces, fixed before allocation

Literal transcription strings are syntax, not typed values. Lexical entries
will specify an expression constructor and its denoted semantic type. All
ordinary recipient constant expressions evaluate to the AnatomicalRole shown
above. Component formation is syntactic, but its evaluated result is the exact
Pred[c] or Mod[c] above, not a record, faculty or material.

The following interfaces are available, with explicit occurrence-level use
required in the subsequent grammar:

1. **Context scope.** A written context-binder syntax node introduces c in a
   finite declared continuation. Evaluation is a generic historical bodily
   assertion in c, not an observed feeding episode. Its surface extent and
   any body-condition premise must be written in the final clause grammar.
2. **Value application.** Given evaluated P:Pred[c] and evaluated x:Material[c],
   ApplyPred(P,x) denotes Proposition. Given M:Mod[c] and D:Pred[c],
   ApplyMod(M,D) denotes Pred[c]. These two applications must be separately
   represented; a Mod is never silently a Pred or an assertion.
3. **Binder syntax.** A MaterialBinder node is NOT a Material[c] value. A written
   existential construction has semantics `exists x:Material[c] [D(x) AND
   Body(x)]`; a written generic construction binds x in an explicit conditional
   or capability schema. The binder's type and scope must be specified by that
   construction. Passing the binder node itself to P is not allowed.
4. **References.** A Ref[k:T] expression evaluates to the value of a written,
   in-scope binding k:T. A reference handle and its denoted value are different
   layers. Only the evaluated value enters a typed semantic application. Missing
   binding is a gap. There is no automatic nearest-token, last-organ, arbitrary
   antecedent or register fallback. Any later reference-selection convention
   is a new named and costed grammar rule.
5. **Generic binders return assertions.** A binder construction's output is a
   Proposition/schema, not its newly bound witness. A later occurrence can refer
   to that witness only inside a declared continuing scope or through an
   explicitly written continuation construction. No escaping existential is
   licensed merely because a later word means “this”.
6. **No semantic inversion.** A bare Pred[c] does not expose a recoverable
   recipient field. Two recipients could have extensionally equal predicates.
   Attraction or faculty-owner claims must therefore obtain their organ argument
   from separately written role expressions or explicit bound references, not
   from an unlicensed `recipientOf(P)` operation. Modifiers likewise do not
   yield a recoverable source field as a value by themselves.
7. **Origin projection.** Within a written witness scope satisfying
   B_c(A_c(b))(RESIDUE_FROM(liver,c))(x), ordinary conjunction elimination
   licenses RESIDUE_FROM(liver,c)(x). A subsequent written assertion must apply
   that description/relation to a reference which evaluates to this SAME x.
   It may not introduce another existential, substitute b for liver, or inspect
   an arbitrary extensional predicate and guess its historical construction.

The final grammar may openly choose finite surface orders and additional whole
operators, but must give their syntax-node inputs, evaluated argument types,
output type, scope and actual uses. The above interfaces cannot be repaired by
silent binder/value casts or predicate-to-faculty promotion.

## Required actual uses and source scope

Bare dar and daiin must supply actual PROPER_FOR applications in owned generic
attraction/capability assertions for spleen and gall-bladder respectively.
The gall-bladder's inclusion among the relevant nourished organs must be
explicitly stated as a membership/instantiation premise; merely citing “other
organs” does not count as its already written target owner. qodar and qodaiin
must actually modify the written liver-residue description and qualify written
material witnesses. qodain must use the unchanged law for kidneys. The third
recipient receives no independent whole-word exception. At least one later
written claim must use origin projected from a modified witness under the
scope rule above. This does not require two different source-origin arguments.

The fixed full III.9 paragraph is102400-byte cache SHA256
1d0f8547ae087a7c97d36f7600cee05dbb1b3321beb973b3065bba2ea8b0ad24;
its selected800-byte HTML unit has SHA256
79c952e0b031eef6253f5766fee7916b3355b53842938240335646611c0b4e2e.
It includes concluding assurance, proper-attraction, foreign-rejection,
retention/alteration of attracted material, liver/veins/arteries/heart/other
organs, four faculties necessary for nutrition, prior proof and handmaid
metaphor, human faeces highly pleasing to dogs, and all three liver-residue
recipient claims. Pleasingness remains distinct from propriety. Powers do not
become actual episodes; necessity does not become sufficiency.

N/E/S/W in that declared presentation are the whole selected synopsis scope:
108ZL/107IT/109RF groups. This order is an authoring assumption, not a native
figure-to-organ map. All149 outside groups and assigned-form occurrences remain
extension obligations. Alternate readings remain literal; ZL is only the
bookkeeping scaffold. No automatic outside context is created.

## Costs, rival and stopping

First-contract costs: three free role assignments (one of six permutations),
two bound function values, five computed whole types, five cut licenses, eight
internal boundaries, one selected generic context architecture, seven explicit
syntax/value interfaces, and the additional written downstream-projection
requirement. No source-proven word or numerical compression is claimed.

The strongest rival names separate recipient-qualified material descriptions
and states origin and propriety in ordinary clauses on the same witness. It can
satisfy every source truth. Rejecting two unrelated existential witnesses does
not reject that serious rival. Extensional equivalence is not a decipherment
result. At03:17UTC or an earlier substantive stopping point, freeze the exact
partial and complete remaining literal obligations rather than change these
values, create a recipient-specific rule, or pad the source with sentence macros.
