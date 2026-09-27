# IDEA000583 — first author contract, before whole authoring

2026-09-27. Scope: the already owned 156 ZL / 157 IT / 160 RF groups, numeric loci .1–.24. First-contract deadline 06:08 UTC; no whole authoring is authorized by this file. This is an exploratory hypothesis with zero confirmed meanings. The accompanying JSON freezes the literal lexicon, manual trees and all473 input fields. It is a serialization, not a parser or semantic executor.

The unknown is whether one argument-exposure law can remain useful under a whole reading. This contract supplies actual constructions in complete .1 and E.7–11 (62 ZL groups), plus conditional local trees for .13 and .15. It does NOT claim the remaining84 groups are derived. In particular, those two latter local trees do not establish a complete intervening .7–.15 text. A contradictory interface closes this attempt; a coherent interface would permit the separately reviewed whole pass. The result is not an independent meaning test.

## Four frozen kernels and one O

`Context` is a circumstance with `recipient: BodyProfile` and `time: YearPosition`. A BodyProfile has age, health class and bodily nature; those are not inferred from a figure. Binding a Context introduces variables for these fields, not prescribed values. No case is automatically the same patient, dose or time as another case. `InputKind` is the generic thing under discussion, not a physical portion. Temporal and recipient variation must later be written separately; equality of the two axes is not supplied here.

Three thermal values HOT, TEMPERATE and COLD are distinct values of one **predominant bodily thermal disposition**, not statements about containing hot/cold elements. Response values GOOD, NEUTRAL and HARM are distinct values under one fixed selected response respect. Their exclusivity and single-valuedness are paid modeling assumptions. The source's positive good/harm predicates alone do not establish them; this is not a net-health algorithm.

| Base | Concrete kernel | Ordinary arguments | Result |
|---|---|---|---|
| `dar` | THERMAL(c) = record of predominant thermal disposition θ of the recipient at the case's time | none | ThermalAssessment(c,θ(c),THERMAL) |
| `tedy` | RESPONSE(c,x) = record of response ρ of the same InputKind x in c | InputKind x | ResponseAssessment(c,x,ρ(c,x),RESPONSE) |
| `tchedy` | ADJUST(c,a) = prospective plan to adjust conduct for c using assessment a | Assessment a, with a.case = c | ConductPlan(c,a,ADJUST_CONDUCT) |
| `chedy` | JUDGMENT_NEEDED(c,x) = judgment about using x in c is needed | InputKind x | Prop |

Assessment is the tagged union of ThermalAssessment and ResponseAssessment. They are not interchangeable attributes: the tag and input field are retained. ADJUST accepts both as assessment bases but must preserve their type, case and payload. It does not prescribe HOT→COOL, identify a particular treatment, imply actual execution or guarantee benefit. JUDGMENT_NEEDED does not imply GOOD, HARM, or that the input itself must be administered. These are four different content relations, not four free wrapper-output tables.

Each base denotes `ImplicitPackage(kernel)`, retaining the unevaluated kernel. Exactly one law is frozen:

```
O(ImplicitPackage(F)) = ExplicitPackage(F)
bare F(a)             = F(snapshot(default), a)
o-F(c,a)              = F(c,a)
```

An implicit head snapshots the current default when that head is encountered, before evaluation of its ordinary arguments. Explicit forms evaluate their overt Context argument and then their ordinary arguments, left to right. O changes neither default nor reference registers, adds no subject/modality, and retains the same output type. It has no root-specific dispatch or residual meaning.

Only the four proposed ZL/IT cuts are used: o|dar, o|tedy, o|tchedy, o|chedy. The already declared RF literal o|che@152;y relation is retained separately. `che@152;y` receives an **additional, independently paid co-denoting base binding** to JUDGMENT_NEEDED; it is not normalized to chedy. Thus there are four different kernels but five literal base bindings and five derived spellings. No other segmentation is permitted. The JSON preserves all41 exact-form obligations, including RF's two literal chedy occurrences.

## Binding, reference, scope and application interfaces

A binder token is an explicit term constructor with a value result and a state effect; it is not silently treated as an entity. A reference token carries a register name and has the explicit DEREF production below. Each binder invocation creates a fresh variable and writes its designated register. Previously constructed expressions retain their earlier variable values; registers do not retroactively rename them. Repeated binder forms never assert that a new variable is the old one.

* `opaees` introduces a fresh Context and writes case register c1; `otody` introduces a fresh Context and writes c0. Their first values are named c1 and c0 in the manual trees. A later otody occurrence would create a new Context and replace the c0 register, **without changing the default value**.
* `ar` introduces a fresh generic InputKind and writes x. Later ar occurrences are the same binder operation, not x references. All of them remain obligations. `qopchas` introduces a physician role variable d. These binders existentially quantify their fresh variables over the following program continuation. This generic-existential convention is a source-to-synopsis assumption, not a source quantifier discovery.
* ContextRef, InputRef and RoleRef are distinct reference sorts. DEREF resolves them to the matching value sort or fails if unbound. No nearest noun, picture, line or category supplies a referent. Every synonym of a reference is counted in the JSON.
* `otchdy` and `pchedeey` are two openly paid spellings of SET_DEFAULT(Context). They replace the one active default with the resolved Context value. Page entry has none. `aram` is CLEAR_DEFAULT. No other whole value introduced in a later authoring pass may acquire a binding, default-update, close or scope-reset effect under this first contract.
* Updating a reference register by an overt binder and updating the default by SET_DEFAULT are different operations. Only SET_DEFAULT and CLEAR_DEFAULT change the default. There is no push/pop context stack or implicit reset at layout boundaries.
* `olfor` is an explicit reference to the basis assessment of the last ConductPlan in the last fully closed REQUIRE_LIST. It fails if there is no such plan. This costs the list selector, last-plan selector and basis projection. It does not inspect an arbitrary earlier expression or recover a kernel from a truth value. The referenced object remains stored with its actual case and response input if applicable.

The fact context is monotone: asserted propositions remain available; no unassigned word may erase them. Future unassigned whole forms may denote ordinary content objects/functions only. Introducing additional operators for binding, state or scope would change this frozen contract and is not licensed as routine filling.

## Frozen finite productions

P01. Literal lexical lookup, preserving every raw form; unknowns remain unknown. No aliases or uncertainty repair.

P02. BINDER term evaluation creates the fresh typed value, writes its named register, and extends existential scope over the continuation. DEREF is a separate typed production. Each costs a rule; no binders are values of the referenced entity sort before this evaluation.

P03. Prefix typed function application, with exactly the declared arguments, evaluates left to right. First-class functions remain functions when supplied to a higher-order argument. Thus EQUALS can be an argument of RESPECT_RELATION without becoming a proposition. No automatic entity/predicate, proposition/assessment or plan/assessment cast is available.

P04. Implicit and explicit family realization are the two rules displayed above. Bare use with no default fails. ADJUST additionally checks a.case=c; there is no inherited case override. Its ConductPlan stores the exact assessment argument, not a fresh compatible assessment.

P05. `left aiin right` realizes EQUALS on two Scalar values of the same scalar sort. EQUALS is otherwise the first-class binary relation value. `left daiin right` realizes HAS_VALUE on a Valued object and a value of its appropriate sort. Valued is exactly Assessment or ConductPlan; a plan's value means the value of its stored **basis**, not its achieved outcome. This shared projection is an additional declared interface. It cannot turn a ReviewPlan or LawPlan into a Valued object.

P06. `odeedy assessment value` asserts that assessment's value. `ASSERT prop` asserts prop. Scalar equality and HAS_VALUE produce propositions; adjacency of complete propositions at program level conjoins them. This conjunction is paid syntax, not a manuscript boundary observation. ASSERT adds no hidden argument or modality.

P07. CHANGES_WITH takes an AspectClass followed by the literal WITH_ARGUMENT_MARKER and a Cycle. The marker is syntactic; it does not add a causal claim. EXHORT_CONSIDERATION(Cycle,Population) is an overt normative predicate requiring attention to the cycle for that population; its exhortative and consideration payloads are both counted.

P08. REQUIRE_LIST starts with its head and physician-role argument and ends only at END_REQUIRE_LIST. An item is either a fully typed Plan or a fully typed Prop. Its interpretation is explicitly conditional: conjunction of Prop items is the guard, and the Plans are the conduct/judgment requirements for that role. No Prop items means the true guard. Plan items are not silently cast to propositions. This is **one additional unmarked conditional-list construction**, charged here; it is not licensed by a supposed medieval punctuation mark or inherited from581. Its output is Prop and the completed list is stored for the specific olfor reference.

P09. The Plan sum has ConductPlan, ReviewPlan and LawPlan. CONSIDER_COMPARISON(AgePair,Respect,OrderPolicy) forms ReviewPlan. AGE_PAIR takes two literal Age values. NO_DIRECTION_SELECTED explicitly withholds their rank. RESPECT_RELATION accepts a binary relation and creates LawPlan. None of these creates a treatment direction or a changed patient state.

P10. CHECKED_THERMAL_RECORD(Context,value,Respect) returns the corresponding ThermalAssessment **only if** Respect=THERMAL and the current asserted facts already entail θ(Context)=value. Otherwise it is unresolved; the constructor itself cannot assert that condition. This is an extra checked record-construction rule, not a free thermal synonym. The E.8 use has the earlier .1 G024–027 premise.

P11. POSSIBLY is an ordinary unary modal operation on Prop. qokedy is prefix; am is postfix. These are two paid spellings and two fixed placement licenses. No actual event follows from possibility. UNDER_ASSESSMENT(a,p) produces the implication Truth(a)→p; Truth(a) is the corresponding explicit value statement about a's stored case/input. This reflection and conditional are separately charged payloads, not a cast of an Assessment to Prop.

P12. `input shedy response value` asserts that the response's stored input is that same input and its value is the written value. This is a frozen infix ternary production, not a second evaluation kernel. No response is recomputed or assigned a new context by this construction.

P13. END_ASSERTION is a terminator only. It does not clear default, references, facts or requirement history. SET_DEFAULT and CLEAR_DEFAULT are the only default-state instructions. Fully saturated terms/propositions determine phrase closure; native line numbers do not occur in any grammar rule.

There are 13 numbered production families, containing separately charged operations: binder, dereference, ordinary application, two family realizations, two infix realizations, scalar/value projections, explicit assertion/value assertion, conjunctive continuation, marked CHANGES_WITH, exhortation, conditional typed list, list storage/reference, three Plan constructors, checked record construction, two modal placements, assessment-truth reflection/conditional, ternary response assertion, terminator and two default controls. Grouping these under13 headings does not turn them into13 cost-free rules. No general executor is supplied.

## Complete actual units owned now

The JSON gives every token of each tree. These are complete ZL units, not collections of favorable anchors.

**.1, all35 groups:** the first five groups bind c1 and x and assert RESPONSE(c1,x)=HARM. The next two bind c0 and set it as default. Groups8–12 assert bodily natures change with the year. Groups13–23 require adjustment plans for c0 using THERMAL(c0) and c1 using THERMAL(c1). Groups24–27 use the written last-list/basis reference and assert θ(c1)=COLD. Groups28–32 assert HOT=THERMAL_VALUE(dar), where bare dar uses c0. Groups33–35 exhort attention to the year for humans.

The thermal contrast is an openly added hypothetical instance of the source's undirected cold/heat variation. Neither context has been labeled old/young or sick/healthy here. Three thermal values are disjoint by contract, so θ(c0)=HOT and θ(c1)=COLD require distinct cases. This is not a source claim that young is hot or that sick benefits. Combining these thermal cases with the response discussion is another paid synopsis linkage.

**E.7–11, all27 groups:** .7's first two groups explicitly set default to REF c0. The remaining25 form POSSIBLY(REQUIRE_LIST(d,...)) plus END_ASSERTION. The first item is the written HAS_VALUE check on an explicit ADJUST(c1,checked record(c1,COLD,THERMAL)) plan. This guard concerns its basis, not whether adjustment succeeds. The second item is bare tchedy applied to explicit otedy(c0,x), giving ADJUST(c0,RESPONSE(c0,x)). The third is a plan to consider the OLD/YOUNG pair under thermal respect without ordering it. The fourth is a plan to respect EQUALS as a relation. The source does not literally command respect for an abstract equality relation: this is a charged explanatory addition preserving the chosen same-input reasoning.

The two units have independent overt default setup; no unparsed N passage is crossed to obtain E's default. The checked thermal record and role/input/context references retain the earlier explicit declarations/assertions. No unparsed word is permitted to redefine those earlier values, delete the fact, or alter scope. This still does not parse N. A later whole failure would remain a failure even if these local trees survive.

**Conditional local trees only:** .13's five groups assert GOOD for a RESPONSE of the same input reference under the current default. .15's five groups say, possibly, that under the bare thermal assessment, judgment about that same input is needed. They are fully token-accounted locally, but .12/.14 remain unparsed. They are not evidence of complete intervening prose. All bare and explicit chedy/ochedy occurrences, repeated ar binders, and final CLEAR_DEFAULT must still survive whole authoring and alternate readings.

## Reuse, discriminating consequence and rivals

DAR has actual explicit uses at .1 G017/G021 and bare use G032. TCHEDY has explicit uses in .1 and .8 and a bare use at .9 G003. The ordinary argument of TCHEDY is a **retained assessment**, first thermal, later response; ownership is checked in both cases. These are two kernels under the same O law, not new values for each prefixed word. The other two family laws are frozen simultaneously, not exemptions to be filled differently later.

The .1 no-update consequence is actual: after setting default c0, the last explicit family uses c1. If exposure updated the default to that context, the later bare dar would return θ(c1)=COLD. The written later assertion demands HOT, while the written reference assertion demands COLD for c1. Disjoint thermal values therefore reject that **one stipulated update rival under these hypothetical meanings**. No unknown word intervenes in this35-group derivation. This is stronger than merely copying a Context tag, but the meanings and thermal instance are authored assumptions.

At E.9 the actual tree is ADJUST(c0,RESPONSE(c0,x)). Under an update rival the preceding explicit c1 use would matter; the declared head-snapshot rule and case check prevent repairing it by silently delaying default capture. The .1 consequence already supplies a complete no-update test without depending on this additional evaluation-order comparison.

A constant context-ignoring RESPONSE is inconsistent with the chosen GOOD/HARM assertions only when the conditional .13 tree is incorporated under c0 and the exclusive-respect assumption is retained. Do not count this as an already complete source/target derivation. Likewise, a constant THERMAL value conflicts with the authored .1 contrast, not with independent target meaning evidence. The strongest historical rivals remain ordinary explicit external argument syntax with unrelated/spelling-related wholes, and independently named qualified relations. A lookup dictionary can reproduce this authored content; the family law limits that freedom but does not prove the segmentation or meaning.

## Cost, source coverage and remaining obligations

The JSON has66 literal bound types:61 independent bindings and5 derived o-forms, with a69-item elementary lexical payload tally. Four different family kernels plus O are the conceptual family core; RF's additional base is paid separately. The remaining56 independent bindings include context and input references, controls, predicates, modal/delimiter words, and constructors. The numeric tally is a declared accounting convention, not an MDL score.

There are four core cuts and the separately retained RF literal cut. No more cuts. Multiple words co-denote SET_DEFAULT, ASSERT, REQUIRE_LIST, c0/c1 references, input references, COLD, thermal respect and POSSIBILITY. They remain separately paid entries; no source-irrelevant tag makes them cheaper or artificially different. Binding versus reference does make a real typed distinction and is not counted as a synonym merely because the first resulting referent matches.

This first contract already spends substantial whole-word freedom to own the two units. At most three lexical choices are saved by the four-family law against eight unrelated family wholes before the extra grammar/package costs. It does not establish materially smaller whole-page authorship. The whole continuation is permitted to fail on that practical criterion as well as on literal/type consistency.

Source O1 is expressed by the year/body-nature statement; O2 remains the prospectively selected modal same-input temporal interpretation and still needs actual time-field variation; O3 still needs actual different recipient/health-class ownership of the same input, without polarity assignment; O4 has an undirected age comparison and actual plans for adjusted conduct, with the additional semantic assumptions disclosed above. Merely possessing Context fields does not discharge O2/O3. All four remain whole-synopsis obligations and no four-block map is assumed.

The prior omissions remain exactly prospective: divine origin, animal/cloak examples, full hazards, stars/elements, spirits/sin, divine protective arts and closing body/soul exhortation. This is not a translation of all64 verses, an attribution to a direct exemplar, or a repair of581/577/558/532. The wind comparator is not a second meaning pool. No581 gloss, grammar or review is imported.

All473 raw fields are copied literally into the JSON with assigned binding or null. Nulls are not wildcards that may acquire scope effects. ZL is an openly chosen display reading. IT's additional otedy and RF's distinct encoded forms are simultaneous obligations, not independent corroboration. The current manual derivations have not certified them; known-side failures may close the whole attempt. Every assigned occurrence outside the62 complete ZL groups remains owed, even where a conditional local tree is provided.

Stop here for root review. Do not start whole authoring or adjust this contract after review without a separately selected new hypothesis.

## Input receipts and freeze

- `DEFAULT_CONTEXT_ROOT_DECISION.md`: `e172754e65b65f908a8c9d6f06fd111fb1634dca02565416b2a935253a9422c4`
- `DEFAULT_CONTEXT_FAMILY_PRESELECTION.md`: `8efd0977089057a1396be528777d38c7770c5eb31e1adbe0e12f05da51978000`
- `ideas/context_argument_exposure_family.json`: `36aa9870afb8a7415696a93dd7f174da43567d4af028183d7d732d34a5821304`
- `REGIMEN_CONTEXT_SOURCE_RESULT.md`: `9f31a79bb38f16b5528716b2b44c52214ecc41d636e8aec6dd03b49c3b37b9b4`
- Safe1042 projection: `e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c`.
- Companion JSON: `b254870d081812cdb3d3afec63856f382eaaef251ab9a7f5b73d1ecbc4545e6f`.

Freeze 2026-09-27 06:07:04 UTC. Actual first tool/read time05:52:29; corrected root budget starts05:53. No registry/Git/state/old packet writes, new images, sources, reserves or contacts.
