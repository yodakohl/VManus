# RAW572 partial whole-content draft

Exploratory C0 authoring. The first contract is unchanged. This is a concrete partial, not a translation, not UNSAT, and not a complete source equivalence. All meanings here are guesses.

## Exact word inventory

| Literal whole form | Proposed value | Type | Status |
|---|---|---|---|
| ar | POWER | Respect | fixed atom |
| aiin | RECEIVED_PROPERTIES | Respect | fixed atom |
| ain | LAST_RESPECT | RespectRef | fixed atom |
| dar | d(POWER) | GradedTemplate[POWER] | computed |
| daiin | d(RECEIVED_PROPERTIES) | GradedTemplate[REC] | computed |
| qodar | qo(d(POWER)) | TopTemplate[POWER] | computed |
| qodaiin | qo(d(RECEIVED_PROPERTIES)) | TopTemplate[REC] | computed |
| qodain | qo(d(LAST_RESPECT)) | TopTemplate[resolved Respect] | computed |
| sain | BRIEF_RECAP | SummaryMarker | new |
| or | ASSEMBLE_FRAME | FrameBuilder | new |
| opchdy | GENERIC_HUMAN_HOLDER | HolderBinder | new |
| qotor | GENERIC_RECEIPT_PROFILE | ProfileBinder | new |
| sheedy | PLANET_COLLECTIVE | CollectiveBinder | new |
| shodaiin | SEVEN | Cardinal | new |
| olfar | NATURES | SummaryTopic | new |
| ary | CHILDREN | SummaryTopic | new |
| dair | FOR_EACH_CONTRIBUTOR | ContributorBinder | new |
| sheo | DONOR_STRENGTH | StrengthExpression | new |
| oraiin | A_RECEIPT_DEGREE | DegreeBinder[REC] | new |
| chol | ACCORDS_WITH | DependenceRelation | new |
| ockhdar | THAT_DEGREE | DegreeRef[REC] | new |
| olkar | LITTLE | DegreePredicate[REC] | new |
| shoral | OR | Disjunction | new |
| roseer | MUCH | DegreePredicate[REC] | new |
| pchedeey | EVENT_CASE | CaseOpener | new |
| olkey | BIRTH | EventKind | new |
| qokedy | OR | Disjunction | new |
| sheos | CONCEPTION | EventKind | new |
| fcheey | MOTHER_OF_THIS_PERSON | MotherRef | new |
| otchedy | GIVES | GiftFieldMarker | new |
| chotey | PROPERTY_BUNDLE | BundleBinder | new |
| qocthey | THIS_PERSON | PersonRef | new |
| oteey | THIS_INITIAL_EVENT | EventRef | new |
| ol | OF_INITIAL_CANDIDATE | AttributeOwner | new |
| oloqorain | NATURE | AttributeKey[Nature] | new |
| qotaiin | THIS_RECEIPT_FRAME | FrameRef[REC] | new |
| tchedy | INITIAL_CANDIDATE | PlanetRef | new |
| otedy | GIFT_RECEIPT_DEGREE | DegreeBinder[REC] | new |
| qotchdy | OF_GIFT | GiftDegreeLink | new |
| chckhey | THIS_PROPERTY_BUNDLE | BundleRef | new |
| ytchedy | RISES_EAST | CasePredicate | new |
| qotedar | THIS_POWER_FRAME | FrameRef[POWER] | new |
| qokar | INITIAL_CANDIDATE | PlanetBinder | new |
| qotchd | GREAT_POWER | CasePredicate | new |
| qotom | THEN | CaseConsequentMarker | new |
| soiis | CLAIMS_CHILD | ChildRelation | new |
| shedaiin | RECEIPT_OF | ReceiptQualification | new |
| chok{co}m | END_CASE | CaseCloser | new |
| otchs | THEREFORE | QuantityConsequenceMarker | new |
| shedor | THIS_RECEIPT_PROFILE | ProfileRef | new |
| chey | ASSERT | AssertionOperator | new |
| sorain | MULTIPLE_DONORS | ProfilePredicate | new |
| shedy | THIS_RECEIPT_FRAME | FrameRef[REC] | new |
| tedy | THIS_HUMAN_HOLDER | HolderTagRef | new |
| sodaiiin | SOME_FOR_EACH_COUNT | ExampleCountOperator | new |
| chy | TWO_AND_THREE | FiniteCardinalList | new |
| ytedar | SOME | ExampleBinder | new |
| chz[s:r] | ALL_SEVEN_PLANETS | CollectiveRef | new |
| arody | RECEIVES_FROM_EACH | ReceiptSupportRelation | new |
| ypshedy | VERY_RARE | RarityOperator | new |
| chedy | ONE | Cardinal | new |
| am | POWER_FRAME_SEED | PartialFrame[POWER] | new |
| odain | THIS_RECEIPT_FRAME | FrameRef[REC] | new |
| an | NAMING_CANDIDATE | NamingCandidateBinder | new |
| orar | NAME_FROM | NamingRelation | new |
| oldar | WITH_RESPECT_TO | RespectQualification | new |
| okees | NEVERTHELESS | AdversativeMarker | new |
| olaiin | THIS_NAMING_FACT | NamingFactRef | new |
| qokal | SAME_HOLDER | OwnerAgreementRelation | new |
| chdy | THIS_PERSON | PersonRef | new |
| sary | THIS_NAMING_CASE | NamingCaseRef | new |
| qokshedy | SELECT_NAMING_WITNESSES | NamingSelectionOperator | new |
| chckhy | THIS_RECEIPT_FRAME | FrameRef[REC] | new |
| ykeedy | THIS_PERSON | PersonRef | new |
| ckhed[a:y] | THIS_RECEIPT_CONTEXT | ReceiptContextTag | new |
| olchey | THIS_NAMING_CONTEXT | ReceiptContextTag | new |
| qokeody | THIS_PERSONS_BIRTH | BirthBinder | new |
| qoekedy | BORN_UNDER | NatalRelation | new |
| dody | NAMING_CANDIDATE | PlanetRef | new |
| lcheol | GIVEN_DEGREE | AttributeKey[DegreeREC] | new |
| sheoly | STRENGTH | AttributeKey[Strength] | new |
| los | UNASSIGNED | UNASSIGNED | unassigned |
| qokshey | UNASSIGNED | UNASSIGNED | unassigned |
| qose?y | UNASSIGNED | UNASSIGNED | unassigned |
| og | UNASSIGNED | UNASSIGNED | unassigned |

## Complete selected sequence with proposed clauses

### N1 — authored

`sain or or aiin opchdy qotor sheedy shodaiin olfar ary`

Recap(RECEIVED_PROPERTIES, U, Cardinal(U)=7, NATURES(U), CHILDREN(U)); introduce generic p, H(p), F_R=ReceiptFrame(p,H).

Source obligations: C01.

Groups: ZL3b|f85r2.2|G001, ZL3b|f85r2.2|G002, ZL3b|f85r2.2|G003, ZL3b|f85r2.2|G004, ZL3b|f85r2.2|G005, ZL3b|f85r2.3|G001, ZL3b|f85r2.3|G002, ZL3b|f85r2.3|G003, ZL3b|f85r2.3|G004, ZL3b|f85r2.3|G005.

### N2 — authored with source extension

`dair sheo oraiin chol daiin ockhdar olkar shoral roseer`

For each q in F_R.domain, some v: G_REC(F_R,q,v) AND Accords(v,Strength_H(q)) AND (Little(v) OR Much(v)).

Source obligations: C07-generalized;C12.

Groups: ZL3b|f85r2.4|G001, ZL3b|f85r2.4|G002, ZL3b|f85r2.4|G003, ZL3b|f85r2.4|G004, ZL3b|f85r2.4|G005, ZL3b|f85r2.5|G001, ZL3b|f85r2.5|G002, ZL3b|f85r2.5|G003, ZL3b|f85r2.6|G001.

### E1 — field of whole E case

`pchedeey olkey qokedy sheos fcheey`

Bind e: EventOf(e,p), Kind(e)=BIRTH OR Kind(e)=CONCEPTION; the latter has MotherOf(p).

Source obligations: C02.

Groups: ZL3b|f85r2.7|G001, ZL3b|f85r2.7|G002, ZL3b|f85r2.7|G003, ZL3b|f85r2.7|G004, ZL3b|f85r2.7|G005.

### E2 — field of whole E case

`otchedy chotey qocthey oteey ol oloqorain`

Gift outcome: Gives(q,p,B,e) AND NatureQualified(B,Nature(q)).

Source obligations: C05.

Groups: ZL3b|f85r2.8|G001, ZL3b|f85r2.8|G002, ZL3b|f85r2.8|G003, ZL3b|f85r2.8|G004, ZL3b|f85r2.8|G005, ZL3b|f85r2.8|G006.

### E3 — field of whole E case

`daiin qotaiin tchedy otedy qotchdy chckhey`

Gift outcome: G_REC(F_R,q,v) AND DegreeOf(B,v) AND IncludedGift(H,B).

Source obligations: C05; explicit H bridge.

Groups: ZL3b|f85r2.9|G001, ZL3b|f85r2.9|G002, ZL3b|f85r2.9|G003, ZL3b|f85r2.9|G004, ZL3b|f85r2.9|G005, ZL3b|f85r2.9|G006.

### E4 — field of whole E case

`ytchedy qodar qotedar qokar qotchd qotom`

Guard: RisesEast(q,e) AND T_POWER(F_P,q) AND GreatPower(q,e); THEN. F_P=PowerFrame(p,e,U).

Source obligations: C03;C04 guard.

Groups: ZL3b|f85r2.10|G001, ZL3b|f85r2.10|G002, ZL3b|f85r2.10|G003, ZL3b|f85r2.10|G004, ZL3b|f85r2.10|G005, ZL3b|f85r2.10|G006.

### E5 — closes whole E case

`soiis aiin shedaiin chok{co}m`

Guard implies ChildOf(p,q), plus E2 and E3; RECEIVED_PROPERTIES qualifies the gift receipt.

Source obligations: C04;C05.

Groups: ZL3b|f85r2.11|G001, ZL3b|f85r2.11|G002, ZL3b|f85r2.11|G003, ZL3b|f85r2.11|G004.

### S1 — authored with discourse premise

`otchs shedor chey sorain`

SourceConsequently(N2.QuantityDependence, Generic[MultipleDonors(H(p))]).

Source obligations: C08;C17 second link.

Groups: ZL3b|f85r2.12|G001, ZL3b|f85r2.12|G002, ZL3b|f85r2.12|G003, ZL3b|f85r2.12|G004.

### S2 — authored

`or shedy tedy sodaiiin chy`

For each n in [2,3], some human x with profile H(x) has Cardinal(Contributors(H(x)))=n. The checked frame is the generic profile schema, not reuse of p as both examples.

Source obligations: C09;C10.

Groups: ZL3b|f85r2.13|G001, ZL3b|f85r2.13|G002, ZL3b|f85r2.13|G003, ZL3b|f85r2.13|G004, ZL3b|f85r2.13|G005.

### S3 — authored

`ytedar chz[s:r] aiin arody`

Some human x receives properties from each q in U in H(x).

Source obligations: C11.

Groups: ZL3b|f85r2.14|G001, ZL3b|f85r2.14|G002, ZL3b|f85r2.14|G003, ZL3b|f85r2.14|G004.

### S4 — authored with added input premise

`ypshedy dar chedy or am oteey`

VeryRare(Cardinal({q in F_P.domain : some v G_POWER(F_P,q,v) AND ActivePower(v)})=1).

Source obligations: C06.

Groups: ZL3b|f85r2.15|G001, ZL3b|f85r2.15|G002, ZL3b|f85r2.15|G003, ZL3b|f85r2.15|G004, ZL3b|f85r2.15|G005, ZL3b|f85r2.16|G001.

### S5 — authored

`qodaiin odain an chey`

Bind naming candidate r and naming case n(p,H,r); assert T_REC(F_R,r).

Source obligations: C13 greatest-share condition.

Groups: ZL3b|f85r2.16|G002, ZL3b|f85r2.16|G003, ZL3b|f85r2.16|G004, ZL3b|f85r2.16|G005.

### S6 — authored

`orar oldar ain`

NameFrom(p,r), qualified by Respect=REC, matching n.frame.respect.

Source obligations: C13.

Groups: ZL3b|f85r2.17|G001, ZL3b|f85r2.17|G002, ZL3b|f85r2.17|G003.

### W1 — authored with discourse premise

`okees olaiin qokal chdy sary`

Nevertheless(GenericMultiple(H), NameFrom(p,r)); holder of named fact, explicit p, and naming case n agree.

Source obligations: C18.

Groups: ZL3b|f85r2.18|G001, ZL3b|f85r2.18|G002, ZL3b|f85r2.18|G003, ZL3b|f85r2.18|G004, ZL3b|f85r2.18|G005.

### W2 — authored

`qokshedy qodain chckhy ykeedy chedy`

Use one naming witness r for p satisfying T_REC(F_R,r). Cardinality concerns the one selected role in n, not all greatest candidates or all possible names.

Source obligations: C13; extra selected-role representation.

Groups: ZL3b|f85r2.19|G001, ZL3b|f85r2.19|G002, ZL3b|f85r2.19|G003, ZL3b|f85r2.19|G004, ZL3b|f85r2.19|G005.

### W3 — authored

`or aiin ckhed[a:y] or ain olchey qokal shedy`

Holders of F_R assembled from REC+receipt context, F_R assembled from LAST_RESPECT+naming context, and referenced F_R all equal p.

Source obligations: same-owner bookkeeping.

Groups: ZL3b|f85r2.20|G001, ZL3b|f85r2.20|G002, ZL3b|f85r2.20|G003, ZL3b|f85r2.20|G004, ZL3b|f85r2.20|G005, ZL3b|f85r2.20|G006, ZL3b|f85r2.20|G007, ZL3b|f85r2.20|G008.

### W4 — authored

`qokeody qoekedy dody shedy qodaiin`

Bind b=BirthOf(p); BornUnder(p,r,b) AND T_REC(F_R,r). If Kind(e)=BIRTH, b=e; otherwise b!=e.

Source obligations: C14.

Groups: ZL3b|f85r2.21|G001, ZL3b|f85r2.21|G002, ZL3b|f85r2.21|G003, ZL3b|f85r2.21|G004, ZL3b|f85r2.21|G005.

### W5 — UNRESOLVED

`los ar shedy qokshey qose?y or aiin og`

No clause production. Literal typed residue: ? POWER FrameRefREC ? ? ASSEMBLE_FRAME REC ?. Calendar disjunction and final etc. are not written.

Source obligations: C15;C16 missing.

Groups: ZL3b|f85r2.22|G001, ZL3b|f85r2.22|G002, ZL3b|f85r2.22|G003, ZL3b|f85r2.22|G004, ZL3b|f85r2.22|G005, ZL3b|f85r2.22|G006, ZL3b|f85r2.22|G007, ZL3b|f85r2.22|G008.

### W6 — authored

`ol lcheol chol ol sheoly`

Accords(GivenDegree(q,p,H), Strength(q,e)); q is initial qualifying candidate, not silently r.

Source obligations: C07.

Groups: ZL3b|f85r2.23|G001, ZL3b|f85r2.23|G002, ZL3b|f85r2.23|G003, ZL3b|f85r2.23|G004, ZL3b|f85r2.23|G005.

## Finite written constructions and scopes

**G00 Discourse and closed reference stores.** Order N,E,S,W. Explicit generic p/H/U bind through the synopsis. References in the lexicon read only their named preceding binder; E case q,e,B have whole-case scope, including fields textually before q. Case q/e references may persist into S/W as a generic case schema, not as an observed successful episode. Local example x never overwrites p. Naming candidate r,n persist from S5 through W. No other omitted arguments are supplied.

**G01 Respect reference.** Exactly the frozen contract LAST_RESPECT rule; evaluated standalone respects update. Internal pieces and PartialFrame do not.

**G02 Component family.** The five exact cuts and d/qo definitions are incorporated unchanged from the frozen contract. No whole-tag dispatch.

**G03 Frame assembly.** or always denotes binary ASSEMBLE_FRAME. Its five closed typed signatures are: (REC,HolderTag(p))->PartialReceipt(R,p); (PartialReceipt(R,p),ProfileTag(H))->ReceiptFrame(p,H); (CompleteReceiptFrame,HolderTag(p))->that checked same frame; (PartialPowerSeed,EventRef(e))->PowerFrame(p,e,U), where e already owns p and U is the explicit N1 collective; (REC,ReceiptContextTag(p,H))->ReceiptFrame(p,H). Prefix application supplies two following complete terms; nested application gives or [or aiin opchdy] qotor. No other pairs are licensed. The power seed has PartialFrame type and does not update LAST_RESPECT.

**G04 Additional frame-input premise.** Every frame admitted by G03 and the E case constructor has exactly one Observe_F(q,v) for each q in its declared domain. This is a NEW total-and-functional input restriction, not entailed by first-contract formulas. No actual values or rankings are supplied. A model can assert T without computing a numerical maximum.

**G05 Summary.** BRIEF_RECAP Frame CollectiveBinder Cardinal NatureTopic ChildTopic => Summary and generic p/H/U declarations. Closed SummaryTopic alternatives are NATURES, CHILDREN; a frame contributes its respect as receipt topic. No arbitrary heterogeneous conjunction cast. All binders in this declaration scope the whole declaration, including earlier fields. H is explicitly a generic Human->Profile assignment as in A01, not a particular observed horoscope.

**G06 Contributor quantity clause.** FOR_EACH_CONTRIBUTOR StrengthExpression DegreeBinder ACCORDS_WITH GradedTemplate, followed THAT_DEGREE DegreePredicate OR DegreePredicate => for each q in the last explicit receipt frame, exists v with G(F,q,v), Accords(v,Strength_H(q)), and disjoined degree predicates. Binder q/v owns the strength and degree reference; G must have REC respect. This construction generalizes C07 to all contributors and is counted as source extension. The local contributor is u, distinct from the later initial candidate q. OR builds Alternative[DegreePredicate]; each predicate applies to that same v.

**G07 Event case.** CASE EventKind OR EventKind MotherRef GiftField GradeField GuardField THEN ChildField END => one generic conditional case. e is one event with the disjunction, not two events. Power frame is constructed from p,e,U with G04. q binder in GuardField scopes all fields. Gift and grade fields before THEN are consequent fields, not unconditional assertions. MotherRef applies to the CONCEPTION disjunct only. This unusual field ordering is an explicit new syntax cost. OR builds Alternative[EventKind]; Kind(e) belongs to that alternative. This is a closed polymorphic alternative constructor for EventKind and DegreePredicate only.

**G08 Gift field.** GIVES BundleBinder PersonRef EventRef [AttributeOwner AttributeKeyNature] => Given(q,p,B,e) and NatureQualified(B,Nature(q)); owner constructor supplies initial q, not human p or r.

**G09 Graded gift field.** G_R FrameRef PlanetRef DegreeBinder OF_GIFT BundleRef => G_R(F,q,v) and DegreeOf(B,v) and IncludedGift(H,B). All arguments are written refs/binders; required respect REC. The inclusion is an explicit law connecting B to H, not equality of power/receipt support. The shared v identifies the bundle degree with the q-share degree represented in H; A13 charges this stronger representative-bundle assumption.

**G10 Guard and Top application.** RISES_EAST T_R FrameRef PlanetBinder GREAT_POWER THEN => RisesEast(q,e) AND T_R(F,q) AND GreatPower(q,e), with F.respect=POWER. Greatest is distinct from both other guards.

**G11 Child outcome.** CLAIMS_CHILD Respect RECEIPT_OF => ChildOf(p,q), and the case gift is typed receipt under that Respect. Only a complete explicit case supplies p/q/B. Respect must REC. Close END_CASE finishes implication of G07.

**G12 Generic profile assertion.** THEREFORE ProfileRef ASSERT ProfilePredicate => Generic(ProfilePredicate(H(p))) plus SourceConsequently(previous quantity-dependence proposition, this generic assertion). Antecedent is explicitly a typed discourse reference to last G06 quantity dependence, not nearest arbitrary sentence. This selector is an added scope rule.

**G13 Example counts.** CompleteReceiptFrame SOME_FOR_EACH_COUNT FiniteCardinalList => independently for every cardinal in list exists human x and own H(x) with that contributor count. Frame serves as schema through an explicit generic p/H abstraction; it is not a concrete frame silently recast. This abstraction rule is an added commitment.

**G14 All-planets example.** SOME CollectiveRef Respect RECEIVES_FROM_EACH => exists x,H(x), for each q in U: Received(x,q,H(x),REC); requires R=REC. No conclusion that every human receives from all seven.

**G15 Rare active count.** VERY_RARE GradedTemplate Cardinal CompletePowerFrame => VeryRare(Count{q: exists v G(F,q,v) AND ActivePower(v)}=Cardinal). Additional degree input law: POWER degrees have distinguished least inactive value bottom; ActivePower(v) iff v>bottom. REC receives no such inactivity cast. This is a NEW representational premise, not entailed by source or first contract. Strictly above bottom means bottom<=v and not v<=bottom in the POWER preorder. GreatPower(q,e) additionally entails ActivePower(v) for the unique power degree observed for q at e; this lexical/input bridge is an extra declared premise. The generic p/e parameters of the written event frame are explicitly abstracted into a CasePredicate over the already introduced human birth-or-conception case schema, per A14. The operator takes that CasePredicate; it is not a truth-functional frequency on one observed event.

**G16 Naming top assertion.** TopTemplate CompleteReceiptFrame NamingCandidateBinder ASSERT => bind r in F.domain and naming record n(owner=F.holder,profile=H,planet=r,frame=F); assert T(F,r). No uniqueness or equality to initial q.

**G17 Naming respect.** NAME_FROM WITH_RESPECT_TO Respect => NameFrom(n.owner,n.planet), requiring R=n.frame.respect. n is the preceding explicitly introduced naming record, not an invented owner.

**G18 Adversative owner agreement.** NEVERTHELESS NamingFactRef SAME_HOLDER PersonRef NamingCaseRef => assert named fact and owner equality, with adversative link to last explicitly Generic profile proposition. This separate typed antecedent selector is an added scope rule. Owner extraction is defined only for PersonRef (identity), NamingFact, NamingCase and constant-holder ReceiptFrame; it is not a free cast for arbitrary semantic types.

**G19 Naming witness count.** SELECT_NAMING_WITNESSES TopTemplate ReceiptFrame PersonRef Cardinal => the current n contributes that many selected naming-role witnesses for this person satisfying T(F,r). Here Cardinal=1 and n has one r. This does not say T has only one solution, choose a tie-break, or rule out another possible name. It is representation bookkeeping beyond the source.

**G20 Three-way owner agreement.** CompleteFrame CompleteFrame SAME_HOLDER CompleteFrame => assert equality of their holder persons. All must be REC frames; no domain/provenance/power-holder equality is inferred.

**G21 Natal clause with criterion.** BirthBinder BORN_UNDER PlanetRef ReceiptFrame TopTemplate => b=BirthOf(p), BornUnder(p,r,b), T(F,r). The postposed T applies to the already written F and PlanetRef. Birth binder also imposes b=e if initial event kind BIRTH, b!=e for CONCEPTION; no calendar condition follows.

**G22 Owner-qualified attributes and dependence.** AttributeOwner AttributeKey ACCORDS_WITH AttributeOwner AttributeKey => Accords(Attribute(q,key1),Attribute(q,key2)); keys GIVEN_DEGREE and STRENGTH take the explicit initial case q plus p/H or e respectively. This is the same primitive Accords relation as G06, with no units, linearity or rank-equivalence axiom. A08 explicitly propagates the stored initial-case guard to the resulting proposition when these case-owned attributes occur outside E.

**G23 No extension production.** There is deliberately no W5 / calendar / etc. production, no outside whole-clause grammar, and no generic higher-order constructor rescue rule. Missing production is incompleteness, not proof that every extension is impossible.

## Additional premises and costs

**A01.** N1 is a generic declaration: U:finite Planet set, |U|=7; H:Human->Profile with Owner(H(x))=x and nonempty Contributors(H(x)) subset U. p is generic Human. All N1 binders scope the whole N1 declaration, including fields textually before U. Cost: generic profile function, simultaneous declaration scope, owner/support restrictions.

**A02.** Receipt frame F_R(p)=ReceiptFrame(p,H(p)). G13 expressly abstracts the generic p/H expression and instantiates it at local x; no concrete observed person is cast to a schema. Local example variables do not update the persistent generic p. Cost: one abstraction/instantiation rule.

**A03.** Every G03/E-frame input is total and single-degree per domain member. This stronger input premise was introduced after the first-contract review; the frozen component law itself remains permissive of sparse/multivalued Observe. Cost: two independent input properties: totality and functionality.

**A04.** Power degree sort has a distinguished least inactive value bottom. ActivePower(v) means strictly greater than bottom. Rarity does not count every total observation as active power. GreatPower(q,e) entails ActivePower of the unique Observe degree for that q/e frame. Cost: one designated constant and one active-degree interpretation and one great-power-to-active bridge.

**A05.** The source uses no numbers or calibrated common metric. Degree preorders may have ties. Neither d nor qo identifies the amount with power, imposes monotonic donor-share ranking, or picks a unique greatest. Cost: no extra rank-equivalence law.

**A06.** N2 local donor variable u ranges over each contributor of H(p). Strength_H(u) is an added profile-indexed strength expression. Its universal dependence statement extrapolates the source initial donor C07; W6 separately retains the initial q/e case. Cost: one all-contributor generalization and one profile-indexed strength argument; not a source entailment.

**A07.** E binds one event e and candidate q throughout its case fields, including textual backward references. E gives a generic implication Guard(q,e)->Gift/Grade/Child, not an observed episode. Cost: one record field-order convention and forward binder scope.

**A08.** Outside E, the ol owner reference carries the initial case key (q,e,Guard). A proposition built using such initial-candidate attributes retains that guard. W6 thus means Guard(q,e)->Accords(GivenDegree(q,p,H),Strength(q,e)), not an assertion about an unqualified planet. Event-only references such as oteey identify e without carrying q's guard. Cost: one explicit guard-propagation rule for case-owned attributes; no silent event identity.

**A09.** The an binder introduces existential r,n for the generic p. S5 onward conjoins properties of that chosen witness; T(F,r) is not treated as an implication naming every tied greatest. W2 counts one witness role inside this record, not the cardinality of T solutions. Cost: one rightward existential scope and one selected-role record.

**A10.** THEREFORE refers by type to the preceding quantity-dependence assertion N2. NEVERTHELESS refers by type to preceding GenericMultiple S1. These selectors are written extra discourse conventions, not source-discovered morpheme behavior. Cost: two selective reference rules.

**A11.** C07 donor-strength and C12 each-actual-contributor attachment are chosen source readings. Property-strength and the narrower all-planets-class attachment remain rivals. Initial e uses one birth-or-conception variable; H is not pooled e/b; later b is same person's birth. Cost: two source ambiguity choices plus event/profile/birth scope decisions.

**A12.** No established inter-block manuscript reading order or historical sentence punctuation follows from using N,E,S,W. This authored ordering is a premise. Outside .1/.24 do not acquire a discourse position in the selected synopsis. Cost: one selected discourse order; outside scope unresolved.

## All assigned outside occurrences

These are literal extension obligations, not complete outside clauses. The JSON retains every outside raw row and its separators, including unknown neighbors. No binding or scope is supplied merely because a value recurs.

### ZL3b

| Source group | Form | Fixed value |
|---|---|---|
| ZL3b\|f85r2.1\|G002 | otedy | GIFT_RECEIPT_DEGREE |
| ZL3b\|f85r2.1\|G004 | ar | POWER |
| ZL3b\|f85r2.1\|G015 | otchedy | GIVES |
| ZL3b\|f85r2.1\|G019 | otchedy | GIVES |
| ZL3b\|f85r2.1\|G023 | shedaiin | RECEIPT_OF |
| ZL3b\|f85r2.1\|G024 | olaiin | THIS_NAMING_FACT |
| ZL3b\|f85r2.1\|G026 | daiin | d(RECEIVED_PROPERTIES) |
| ZL3b\|f85r2.1\|G027 | ol | OF_INITIAL_CANDIDATE |
| ZL3b\|f85r2.1\|G030 | aiin | RECEIVED_PROPERTIES |
| ZL3b\|f85r2.1\|G032 | dar | d(POWER) |
| ZL3b\|f85r2.24\|G001 | okees | NEVERTHELESS |
| ZL3b\|f85r2.24\|G008 | ar | POWER |
| ZL3b\|f85r2.24\|G009 | or | ASSEMBLE_FRAME |
| ZL3b\|f85r2.24\|G012 | ar | POWER |

### IT2a

| Source group | Form | Fixed value |
|---|---|---|
| IT2a\|f85r2.1\|G002 | otedy | GIFT_RECEIPT_DEGREE |
| IT2a\|f85r2.1\|G004 | ar | POWER |
| IT2a\|f85r2.1\|G007 | otedy | GIFT_RECEIPT_DEGREE |
| IT2a\|f85r2.1\|G015 | otchedy | GIVES |
| IT2a\|f85r2.1\|G019 | otchedy | GIVES |
| IT2a\|f85r2.1\|G023 | shedaiin | RECEIPT_OF |
| IT2a\|f85r2.1\|G024 | olaiin | THIS_NAMING_FACT |
| IT2a\|f85r2.1\|G026 | daiin | d(RECEIVED_PROPERTIES) |
| IT2a\|f85r2.1\|G027 | ol | OF_INITIAL_CANDIDATE |
| IT2a\|f85r2.1\|G030 | aiin | RECEIVED_PROPERTIES |
| IT2a\|f85r2.1\|G032 | dar | d(POWER) |
| IT2a\|f85r2.24\|G001 | okees | NEVERTHELESS |
| IT2a\|f85r2.24\|G008 | ar | POWER |
| IT2a\|f85r2.24\|G009 | or | ASSEMBLE_FRAME |
| IT2a\|f85r2.24\|G011 | ol | OF_INITIAL_CANDIDATE |
| IT2a\|f85r2.24\|G013 | ar | POWER |
| IT2a\|f85r2.24\|G014 | ar | POWER |
| IT2a\|f85r2.24\|G015 | am | POWER_FRAME_SEED |

### RF1b

| Source group | Form | Fixed value |
|---|---|---|
| RF1b\|f85r2.1\|G002 | otedy | GIFT_RECEIPT_DEGREE |
| RF1b\|f85r2.1\|G004 | ar | POWER |
| RF1b\|f85r2.1\|G019 | otchedy | GIVES |
| RF1b\|f85r2.1\|G023 | shedaiin | RECEIPT_OF |
| RF1b\|f85r2.1\|G024 | olaiin | THIS_NAMING_FACT |
| RF1b\|f85r2.1\|G026 | daiin | d(RECEIVED_PROPERTIES) |
| RF1b\|f85r2.1\|G027 | ol | OF_INITIAL_CANDIDATE |
| RF1b\|f85r2.1\|G032 | dar | d(POWER) |
| RF1b\|f85r2.24\|G001 | okees | NEVERTHELESS |
| RF1b\|f85r2.24\|G009 | ar | POWER |
| RF1b\|f85r2.24\|G010 | or | ASSEMBLE_FRAME |
| RF1b\|f85r2.24\|G012 | ol | OF_INITIAL_CANDIDATE |
| RF1b\|f85r2.24\|G014 | ar | POWER |
| RF1b\|f85r2.24\|G015 | ar | POWER |
| RF1b\|f85r2.24\|G016 | am | POWER_FRAME_SEED |

## Alternate-reading consequences

**IT2a.**

Additional literal unknowns: `aiinog`, `ch?s`, `chokcod`, `ckhedy`, `csedy`, `ockhdor`, `olkor`, `oloeorain`, `qoseey`, `qtchedy`, `sosees`.

- S.16 qodain computes T_REC, since S.14 standalone aiin is the last respect; it is not an exception or normalization to qodaiin.
- W.19 qodain also resolves REC from S.17 ain.
- W.20 begins ar aiin ckhedy: ar is POWER and aiin immediately restores REC; therefore later ain remains REC. The opening FrameBuilder is absent, independently of unknown ckhedy. G20 has no declared construction for a standalone Respect pair in place of its first frame.
- W.22 aiinog remains one opaque unassigned form, not aiin+og. No calendar parse is claimed.

**RF1b.**

Additional literal unknowns: `@221;laiin`, `ch@152;s`, `chot{co}g`, `ckhe@152;y`, `eey`, `ol@176;ar`, `otche@152;y`, `ote@152;y`, `qo@152;ain`, `qo@152;ar`, `qoke@152;y`, `qose`, `she@152;y`, `sosees`, `yfshe@152;y`, `{ch'}edy`, `{ch'}eos`.

- qo@152;ar and qo@152;ain do not receive the compound licenses for qodar and qodain.
- W.20 begins ar aiin ckhe@152;y: the opening FrameBuilder is absent; aiin immediately supersedes ar in the respect register, so later ain is REC.
- W.22 qose eey are two separate unknown groups; their existence does not license splitting ZL qose?y or assigning DAY/OR/HOUR.

**ZL3b.**

- Every selected free ain and qodain resolves REC. W.22 ar is the first selected standalone POWER; W.22 aiin then restores REC.
- All marked words remain literal opaque wholes, including ckhed[a:y], chz[s:r], chok{co}m. Their hypothetical assigned values say nothing about which marked alternative is correct.

## Two reused operations, with actual arguments

**N2.** aiin:REC; d(REC)=G_REC by fixed law; N1 written F_R supplies holder p, donor index u, H(p); dair binds u; oraiin binds v; G06 yields G_REC(F_R,u,v). Result: actual graded receipt application.

**S4.** ar:POWER inside dar does not update register; d(POWER)=G_POWER; or am oteey constructs F_P(p,e,U); G15 binds u,v in its cardinal comprehension and tests G_POWER(F_P,u,v) AND ActivePower(v). Result: actual graded power application; bottom/active premise extra.

**E4.** d(POWER)=G_POWER; qo(G_POWER)=T_POWER; qotedar supplies F_P; qokar binds q; G10 tests T_POWER(F_P,q) together with east/great guards. Result: actual greatest-power application.

**S5.** d(REC)=G_REC; qo(G_REC)=T_REC; odain supplies F_R; an binds r; G16 asserts T_REC(F_R,r). Result: actual greatest-receipt application.

**W2.** last standalone respect is S.14 aiin, repeated by S.17 ain:REC; ain resolves REC inside qodain without switching register; qodain=T_REC; chckhy supplies F_R, ykeedy p, chedy cardinal1; G19 checks current naming witness r against T_REC(F_R,r). Result: all qodain argument roles proposed; no third input or independent contrast.

**W4.** qodaiin=T_REC; shedy supplies F_R; dody supplies r; G21 uses postposed template on F_R,r. Result: repeated same-respect criterion, not new distinct argument evidence.


## Additional self-review qualifications

- The first contract remains byte-identical. Its unrestricted Observe still permits sparse/multivalued relations; only this draft's openly stronger frame-input premise excludes them.
- 100 is a group-allocation count, not a machine-verified grammar pass. G03, generic profile abstraction, E record ordering, existential naming scope and guard propagation carry substantive new assumptions.
- Both fixed d and qo laws are actually instantiated at the two declared respect inputs; the derived family is not dispatched by whole-word identity. W qodain earns no third input and mostly repeats the naming criterion.
- C15 day/hour, C16 etc., and C17 first consequence link remain absent. The literal W.22 residue is not a contradiction: four values and any suitable connecting construction remain unknown.
- IT/RF W.20 starts ar aiin rather than or aiin. Missing FrameBuilder prevents the frozen G20 structure; aiin does restore REC, so claiming its following ain resolves POWER would be wrong.
- An aligned-order rival remains compatible with the proposed statements. No concrete model values force the two maxima to differ.

Further possible synonyms: oraiin/otedy both bind received degree; ckhed[a:y]/olchey yield the same p/H pair through two reference paths. These are charged separate whole values, not credited as compositional savings.

## Explicit multi-feature whole-value costs

These are 147 semantic payload occurrences across the73 new whole assignments, using the declared accounting below; 50 of those wholes have more than one listed feature. This is not a minimal alphabet or another target segmentation. Features do not generate other forms. Values not listed below carry one opaque meaning-label payload.

| Whole | Charged semantic payloads |
|---|---|
| sain | BRIEF, RECAP |
| opchdy | GENERIC, HUMAN, HOLDER, BIND_p |
| qotor | GENERIC, RECEIPT_PROFILE, BIND_H |
| sheedy | PLANETS, COLLECTIVE, BIND_U |
| dair | FOR_EACH, CONTRIBUTOR, BIND_u |
| sheo | STRENGTH, DONOR_OWNER, PROFILE_INDEX |
| oraiin | EXISTS, BIND_v, REC_DEGREE |
| ockhdar | REFERENCE, RECENT_DEGREE |
| pchedeey | CASE, BIND_e, CONDITIONAL_RECORD |
| fcheey | MOTHER, REFERENCE_p |
| chotey | PROPERTY, BUNDLE, BIND_B |
| ol | REFERENCE_INITIAL_q, ATTRIBUTE_OWNER, CASE_KEY |
| qotaiin | REFERENCE_F_R, REC_FRAME |
| otedy | BIND_v, REC_DEGREE, GIFT_ROLE |
| qotchdy | LINK, GIFT, DEGREE |
| ytchedy | RISE, EAST, CASE_KEY |
| qotedar | REFERENCE_F_P, POWER_FRAME |
| qokar | BIND_q, PLANET |
| qotchd | GREAT, POWER, CASE_KEY |
| soiis | CLAIM, CHILD_RELATION |
| shedaiin | RECEIPT, OF, CASE_KEY |
| chok{co}m | END, CASE |
| otchs | CONSEQUENTLY, QUANTITY_ANTECEDENT |
| shedor | REFERENCE_H, PROFILE |
| sorain | MULTIPLE, DONORS |
| shedy | REFERENCE_F_R, REC_FRAME |
| tedy | REFERENCE_p, HOLDER_TAG |
| sodaiiin | SOME, EACH, COUNT_CONDITION |
| chy | TWO, THREE, LIST |
| ytedar | SOME, LOCAL_HUMAN_BINDER |
| chz[s:r] | ALL, REFERENCE_U |
| arody | RECEIVE, FROM_EACH, SOURCE_INDEX |
| am | POWER, FRAME_SEED |
| odain | REFERENCE_F_R, REC_FRAME |
| an | BIND_r, NAMING_ROLE, BIND_n |
| orar | NAME, FROM, REFERENCE_n |
| okees | NEVERTHELESS, GENERIC_ANTECEDENT |
| olaiin | NAMING_FACT, REFERENCE |
| qokal | SAME, HOLDER |
| sary | NAMING_CASE, REFERENCE |
| qokshedy | SELECT, NAMING_WITNESS |
| chckhy | REFERENCE_F_R, REC_FRAME |
| ckhed[a:y] | CONTEXT_TAG, REFERENCE_p, REFERENCE_H |
| olchey | CONTEXT_TAG, REFERENCE_n, PROJECT_p_H |
| qokeody | BIRTH, BIND_b, REFERENCE_p |
| qoekedy | BORN, UNDER |
| dody | NAMING_PLANET, REFERENCE |
| lcheol | DEGREE, GIVEN, ATTRIBUTE_KEY |
| sheoly | STRENGTH, ATTRIBUTE_KEY |

## Final pre-freeze assumption disclosure

**A13.** E3 equates the gift bundle degree with the q-indexed degree in H. Thus B is the representative complete q-share for this model, not an arbitrary smaller gift merely included in H. This is stronger than inclusion alone and is an added source/model premise. It does not identify other contributors with power holders. Cost: one initial-donor bundle/share identification.

**A14.** The rarity construction explicitly abstracts the generic p/e parameters of the written event reference into a case predicate. Its domain is the already written human birth-or-conception case schema. VERY_RARE is qualitative, with no numerical threshold or sampling claim. Cost: one case-predicate abstraction and the source intensity feature VERY.

The ypshedy value is VERY_RARE and is charged two features, VERY and RARE. The total declared payload accounting is147 occurrences across73 new wholes, with50 multifeature wholes. These disclosures were written before final freeze, not amendments to the first contract.
