# IDEA000588: complete manual ZL candidate, review pending

**All156 ZL groups are assigned to the following nine manual derivations.** The complete source paragraph and all fourteen duties are represented. This is an author-supplied working hypothesis, not a confirmed reading or a semantic validator result. All473 original rows are retained; IT/RF full derivations remain unprovided and their literal conflicts/gaps are explicit.

Actual start2026-09-27 09:15:18UTC; author ceiling10:19UTC. The JSON is the full exact definition of values, interfaces, scopes, revisions, all occurrences and reader consequences. No cut or component law is retained.

## Conditional whole account

### C01 — [1, 1] through [1, 11]

`odeedy otedy opaees ar chcthy otchdy otody otar chepaiin otodar otodaiin`

Thunder is first among the double-vapour impressions, and is generated in watery cloud substance.

```text
(CLASSIFY odeedy (otedy (opaees ar (chcthy otchdy))) (otody (otar (chepaiin (otodar otodaiin)))))
FirstAmong(T0, ImpressionsFrom(DoubleVapour)) AND GenericGeneratedIn(T0, Watery(SubstanceOf(C0)))
```

Result: Proposition. Rules: G01, G02, G03, G04, G05, G37.
odeedy introduces generic T0; otodaiin introduces C0. No two-component recipe or dated event is supplied.

### C02 — [1, 12] through [1, 26]

`opaiin otaiin qopchas otchedy olkaiin odar aloees otchedy qotedaiin odar octhody shedaiin olaiin olfor daiin`

Hot, dry vapour moves and shakes back and forth, fleeing its unspecified contrary while constrained on all sides. It strikes into itself and thereby ignites into flame.

```text
(SUBJECT_CHAIN (opaiin (otaiin qopchas)) (otchedy (olkaiin (odar aloees))) (otchedy (qotedaiin (odar octhody))) (ROLE_APPLY shedaiin olaiin) (olfor daiin))
Let x=v:HotDryVapour. BackAndForthMove(v) AND Shake(v) AND Flee(v,ContraryOf(v)) AND Constrained(v,AllSides(v)) AND Strike(s,v,v) AND IgniteFlame(i,v) AND Because(s,i)
```

Result: OpenSubjectAccount[V], completed by C03. Rules: G02, G06, G07, G08, G09, G12.
Vapour x introduced at .1 G012; this subject scope continues through C03. olaiin stays EventKind STRIKE, applied to explicit subject and reflexive patient. olfor takes the preceding strike, not an arbitrary prior clause.

### C03 — [1, 27] through [1, 35]

`ol lkech[ch:?] os aiin oteedy dar otees opaiin chcphdar`

At the end it quenches itself in that cloud, after ignition; the account is attributed to Aristotle.

```text
(CITATION (QUENCH (ol lkech[ch:?]) os aiin oteedy dar) otees (opaiin chcphdar))
AtFinalTime(q,Sequence(v)); SelfQuench(q,v,In(C0)); Later(q,i); AttributedTo(Aristotle, VapourAccount(C02,q))
```

Result: AttributedClaimSequence. Rules: G06, G09, G10, G11.
aiin is still v. C0 is read from C01. The authority introduction is a nested nominal scope, not a retroactive replacement of v. The vapor/fire antecedent is modeled as ignited v and remains a disclosed choice.

### C04 — [2, 1] through [3, 5]

`sain or or aiin opchdy qotor sheedy shodaiin olfar ary`

When a strong whirling storm/wind enters a cloud, increases and seeks a passage, the following cloud-breaking consequences obtain.

```text
(sain (or (or (PRED aiin opchdy qotor) (PRED sheedy shodaiin)) (PRED olfar ary)) CONSEQUENT_C05)
In conditional case W: Let w=StrongWhirlingStormWind, Cw=Cloud. GuardW := Enter(w,Cw) AND Increase(w) AND Seek(w,Passage). WHEN GuardW, C05.
```

Result: ConditionalHeader with explicit Guard and C05 consequent. Rules: G06, G12, G13.
sain introduces w and subject x=w; qotor introduces Cw. sheedy/olfar are paid x aliases. The seek predicate does not assert achieved emergence. C04 requires C05 to complete its conditional.

### C05 — [4, 1] through [7, 5]

`dair sheo oraiin chol daiin ockhdar olkar shoral roseer pchedeey olkey qokedy sheos fcheey`

The wind cleaves/breaks its entered cloud, emerges forcefully, and breaks its parts. The dreadful auditory consequence reaches human and animal ears.

```text
(CONSEQUENT (dair (sheo (oraiin chol daiin))) (MODIFY ockhdar olkar) (shoral roseer) (PRED pchedeey olkey (qokedy sheos fcheey)))
GuardW -> [CleaveBreak(w,Cw) AND ForcefulEmerge(w,Cw) AND BreakParts(r,w,PartsOf(Cw)) AND Dreadful(nW) AND NoiseOf(nW,r) AND Reach(nW,Ears(Humans)) AND Reach(nW,Ears(Animals))]
```

Result: ConditionalConsequent and captured W.noiseClaim. Rules: G07, G13, G14, G15.
No new cloud is silently selected: entered-cloud projection uses C04. r is introduced by shoral; pchedeey reads that r. The first three pieces receive written W.subject; the final noise sentence has explicit pchedeey subject. The noise, not a transported storm, reaches ears.

### C06 — [8, 1] through [11, 4]

`otchedy chotey qocthey oteey ol oloqorain daiin qotaiin tchedy otedy qotchdy chckhey ytchedy qodar qotedar qokar qotchd qotom soiis aiin shedaiin chok{co}m`

The cloud noise is unsurprising in light of a bladder example: even a light bladder makes loud noise if first strongly inflated and afterward violently broken. Its guarded noise is compared with cloud rupture noise; its lightness is explicitly retained as a concession.

```text
(ADJOIN otchedy (chotey qocthey (oteey (BLADDER_ARGUMENT (ol oloqorain) (NOISE_CLAIM daiin qotaiin (tchedy (SEQUENCE otedy qotchdy chckhey ytchedy))) (qodar (qotedar qokar (qotchd qotom))) (soiis (APPOSITIVE_PROPERTY aiin shedaiin chok{co}m))))))
Let B=LightBladder. GuardB := StrongInflate(b1,B) AND ViolentBreak(b2,B) AND Before(b1,b2). GuardB -> Loud(nB) AND NoiseOf(nB,B). Concession(Light(B),LoudUnderGuard(B)); Analogy(NoiseClaimB,NoiseClaimW); NoWonder(NoiseClaimW,explainedBy=Analogy).
```

Result: ExplanatoryAnalogyArgument. Rules: G03, G04, G06, G08, G12, G16, G17, G18.
oloqorain binds x=B. This is conditional, not an observed trial. qodar consumes the preceding guarded nB claim and the explicit following nW description. W.r/Cw remain captured references outside the B scope. This is not a sensory-order replication.

### C07 — [12, 1] through [17, 3]

`otchs shedor chey sorain or shedy tedy sodaiiin chy ytedar chz[s:r] aiin arody ypshedy dar chedy or am oteey qodaiin odain an chey orar oldar ain`

Lightning accompanies thunder. It is seen sooner because it is clear and bright; thunder is heard later, with the comparative subtlety of sight over hearing offered as the reason. Our community owns the two access relations and its ears are the auditory recipients.

```text
(WEATHER (otchs shedor chey sorain) (or (VISUAL shedy tedy sodaiiin (chy (PROPERTIES ytedar chz[s:r] aiin arody))) (AUDITORY (ypshedy dar chedy) (or (am (oteey (FACULTY_COMPARE qodaiin odain an chey))) (orar oldar ain)))))
Accompany(L,T0). Let O=OurCommunity, aV=See(O,L), aA=Hear(O,T0). Before(aV,aA). Because(Clear(L) AND Bright(L),Earlier(aV,aA)); Because(Subtler(Sight(O),Hearing(O)),Later(aA,aV)).
```

Result: CompletedWeatherCase C with access pair, observer and reasons. Rules: G12, G19, G20, G21, G22.
The visual x=L and auditory x=T0 are separate lexical branches. orar oldar ain is the actual observer-binding phrase; no owner is filled from the source or from another reader. All references to C.O remain provisional until this phrase completes the case. Accompaniment does not establish an identical production instant.

### C08 — [18, 1] through [23, 5]

`okees olaiin qokal chdy sary qokshedy qodain chckhy ykeedy chedy or aiin ckhed[a:y] or ain olchey qokal shedy qokeody qoekedy dody shedy qodaiin los ar shedy qokshey qose?y or aiin og ol lcheol chol ol sheoly`

A person sees a stroke before hearing the noise of that same stroke. The stroke belongs to the explicitly described person hewing a tree. The observer remains a separate role. The passage reiterates the stroke and ear ownership, then explicitly maps its seeing and hearing to the lightning/thunder pair.

```text
(okees olaiin (EARLIER_PAIR qokal chdy sary qokshedy qodain chckhy ykeedy chedy) (or (OCCURRENCE aiin ckhed[a:y]) (or (ORGANS ain olchey) (EARLIER_REDESCRIPTION qokal shedy (qokeody (HEW_ACTION qoekedy dody shedy)) qodaiin))) (PAIR_ANALOGY ((los ar shedy) qokshey qose?y) or (aiin og ((ol lcheol) chol (ol sheoly)))))
Introduce generic strike E and observer O_K. Introduce h locally in the relative clause; Hew(h,tree), Agent(E,h), StrokeIn(E,Hew(h,tree)). nE=NoiseOf(E). Before(See(O_K,E),Hear(O_K,nE)). No equality O_K=h is asserted. Repeat Occurs(E), HasOrgan(O_K,Ears), EarlierSeeingOf(E) with its written h/tree action. Map both access members to C and thereby compare the two Before relations.
```

Result: CompletedWoodCase K and analogy of its order with C. Rules: G02, G03, G06, G12, G23, G24, G25, G26, G27, G28, G29, G34.
okees olaiin introduces E, not a second blow. sary binds O_K; ykeedy returns that observer. qodain binds its noise to E. qokeody opens only a local h scope for tree/hewing; outer x remains E afterward. qokal second use repeats the existing K order. qodaiin supplies Sight(O_K), not the hewer's sight. Later noise-of-thunder matches T0 ONLY through paid G34.

### C09 — [24, 1] through [24, 13]

`okees ochar oted[o:a]r ochedy otody olchedy oteedo ar or airol otees ar aram`

Returning to the weather case, distinguish the thunder-generation account from the order of visual and auditory access. The access terms are represented as informational witnesses. This is a newly hypothesized closing summary, not an explicit sentence of the source.

```text
(okees ochar (DISTINCTION (GENERATION_DESCRIPTION oted[o:a]r ochedy otody) olchedy (oteedo ar (or airol (otees ar aram)))))
In existing C: Distinguish(GenerationDescription(T0,Cloud), Ordering(InfoWitness(C.aV),InfoWitness(C.aA))). Ordering is inherited from C.aV/C.aA, not new utterance/report times.
```

Result: AddedMetaStatement. Rules: G02, G03, G12, G23, G30, G31, G32, G37.
ochar explicitly reopens C. oted[o:a]r reads C.T; it is not normalized to another spelling. otees uses the separate paid sensory-information interface here. G31 retains the original access records. No new observer, new weather event, exact generation-time equation or auditory/visual object identity is introduced.

## Every whole meaning

|Literal|Value/type|Paid payload units|
|---|---|---:|
|odeedy|THUNDER / IntroducingPhenomenonReference[AuditoryPhenomenon]|1|
|otedy|FIRST / OrdinalSpecifier|1|
|opaees|IMPRESSION_FROM / RelationalKindDescription|1|
|ar|GENITIVE / RelationApplicationMarker|1|
|chcthy|DOUBLE / KindModifier|1|
|otchdy|VAPOUR / KindDescription|1|
|otody|GENERATED / EventPredicateKind|1|
|otar|IN / LocationConstructor|1|
|chepaiin|WATERY / SubstanceModifier|1|
|otodar|SUBSTANCE_OF / RelationalNominal|1|
|otodaiin|CLOUD / IntroducingCloudReference|1|
|opaiin|INTRODUCE_SUBJECT / Binder|1|
|otaiin|HOT_AND_DRY / VapourModifier|2|
|qopchas|VAPOUR / KindDescription|1|
|otchedy|ADDITIVE / AdditiveMarker|1|
|olkaiin|MOVING_SHAKING_FLEEING / CompoundPredicateKind|4|
|odar|ITS / PossessorReference|1|
|aloees|CONTRARY / RelationalNominal|1|
|qotedaiin|CONSTRAINED_ACROSS / PredicateKind|1|
|octhody|ALL_SIDES / RelationalNominal|2|
|shedaiin|SELF / ParametricSelfReference[Ref[T] with same-witness constraint]|1|
|olaiin|STRIKE / EventKind|1|
|olfor|THEREBY_IGNITE / CausalPredicateConstructor|3|
|daiin|SELF / ParametricSelfReference[Ref[T] with same-witness constraint]|1|
|ol|DEFINITE_NOMINAL / NominalDeterminer|1|
|lkech[ch:?]|FINAL_TIME / TemporalNominal|1|
|os|SELF_QUENCH / ReflexivePredicateKind|2|
|aiin|SUBJECT_REFERENCE / ParametricReferenceLookup[Ref[T] from nearest explicit x:T]|1|
|oteedy|IN_INITIAL_CLOUD / LocationModifier|2|
|dar|LATER / TemporalComparisonModifier|1|
|otees|REPORT / RelationalInformationWitnessKind[typed Source interface]|1|
|chcphdar|ARISTOTLE / AuthorityDescription|1|
|sain|WHEN_STRONG_STORM / ConditionalCaseBinder|6|
|or|COORDINATE / PolymorphicCoordinationMarker|1|
|opchdy|ENTER / EventPredicateKind|1|
|qotor|CLOUD / IntroducingCloudReference|1|
|sheedy|SUBJECT_REFERENCE / ParametricReferenceLookup[Ref[T] from nearest explicit x:T]|1|
|shodaiin|INCREASE / PredicateKind|1|
|olfar|SUBJECT_REFERENCE / ParametricReferenceLookup[Ref[T] from nearest explicit x:T]|1|
|ary|SEEK_PASSAGE / GoalPredicateKind|2|
|dair|BREAK / PredicateKind|2|
|sheo|DEFINITE_NOMINAL / NominalDeterminer|1|
|oraiin|ENTERED_CLOUD_OF / RelationalNominal|2|
|chol|GENITIVE / RelationApplicationMarker|1|
|ockhdar|EMERGE / PredicateKind|1|
|olkar|FORCEFULLY / EventModifier|1|
|shoral|BREAK_PARTS_OF / CompoundPredicateKind|2|
|roseer|WIND_CLOUD_REFERENCE / CloudReference|1|
|pchedeey|DREADFUL_RESULTING_NOISE / IntroducingNoiseReference|3|
|olkey|REACH / PredicateKind|1|
|qokedy|EARS_OF_BOTH / RecipientConstructor|2|
|sheos|HUMANS / RecipientKind|1|
|fcheey|ANIMALS / RecipientKind|1|
|chotey|NO_WONDER / ExplanatoryConclusion|1|
|qocthey|CLOUD_NOISE_CLAIM / PropositionReference|1|
|oteey|CONSIDER / ArgumentIntroducer|1|
|oloqorain|LIGHT_BLADDER / IntroducingEntityReference[Bladder]|3|
|qotaiin|RESOUND_LOUDLY / NoisePredicateKind|2|
|tchedy|IF / ConditionalModifier|1|
|qotchdy|STRONGLY_INFLATED / ConditionalEventPredicate|2|
|chckhey|AFTERWARD / SequenceConstructor|1|
|ytchedy|VIOLENTLY_BROKEN / ConditionalEventPredicate|2|
|qodar|LIKE / NoiseAnalogyConstructor|1|
|qotedar|NOISE / RelationalNominal|1|
|qokar|GENITIVE / RelationApplicationMarker|1|
|qotchd|RUPTURE / RelationalNominal|1|
|qotom|WIND_CLOUD_REFERENCE / CloudReference|1|
|soiis|ALTHOUGH / ConcessiveModifier|1|
|chok{co}m|LIGHT / PropertyPredicate|1|
|otchs|WITH / WeatherCaseConstructor|1|
|shedor|THUNDER / PhenomenonReference[AuditoryPhenomenon]|1|
|chey|IS / Copula|1|
|sorain|LIGHTNING / IntroducingPhenomenonReference[Lightning]|2|
|shedy|SUBJECT_REFERENCE / ParametricReferenceLookup[Ref[T] from nearest explicit x:T]|1|
|tedy|SEEN / AccessPredicateKind|1|
|sodaiiin|SOONER / TemporalComparisonModifier|1|
|chy|BECAUSE / ReasonModifier|1|
|ytedar|CLEAR / PropertyPredicate|1|
|chz[s:r]|BRIGHT / PropertyPredicate|1|
|arody|IS / Copula|1|
|ypshedy|THUNDER / SubjectScopeBinder[AuditoryPhenomenonReference]|2|
|chedy|HEARD / AccessPredicateKind|1|
|am|BECAUSE / ReasonModifier|1|
|qodaiin|SIGHT_OF_OBSERVER / FacultyDescription|2|
|odain|SUBTLER_THAN / ComparativePredicate|1|
|an|HEARING / FacultyKind|1|
|orar|TO_OBSERVER_EARS / RecipientBinderConstructor|2|
|oldar|OUR_COMMUNITY / ObserverDescription|1|
|ain|EARS / OrganKind|1|
|okees|CONSIDER_CASE / CaseScopeIntroducer|1|
|qokal|SOONER / TemporalComparisonModifier|1|
|chdy|SEEN_BY / AccessConstructor|1|
|sary|A_PERSON / IntroducingObserverReference[Person]|2|
|qokshedy|THAN / ComparativePairCompletion|1|
|qodain|NOISE_OF_THIS_STROKE / NoiseProjectionReference|2|
|chckhy|BY / ObserverRoleMarker|1|
|ykeedy|OBSERVER_REFERENCE / ObserverReference|1|
|ckhed[a:y]|OCCURS / EventPredicate|1|
|olchey|ARE_HIS_ORGANS / OrganPredicate|2|
|qokeody|BY_A_PERSON / AgentRelativeBinder|4|
|qoekedy|TREE / IntroducingObjectReference[Tree]|2|
|dody|HEW / PredicateKind|1|
|los|VISUAL_ACCESS_TO / RelationalAccessNominal|2|
|qokshey|PARALLELS_WEATHER_VISUAL_ACCESS / AnalogyMapConstructor|2|
|qose?y|WEATHER_LIGHTNING_REFERENCE / PhenomenonReference|1|
|og|PARALLELS_WEATHER_AUDITORY_ACCESS / AnalogyMapConstructor|3|
|lcheol|NOISE / RelationalNominal|1|
|sheoly|WEATHER_THUNDER_REFERENCE / PhenomenonReference|1|
|ochar|WEATHER_CASE_REFERENCE / ExistingCaseDesignator|1|
|oted[o:a]r|WEATHER_THUNDER_REFERENCE / PhenomenonReference|1|
|ochedy|IN_CLOUD / LocationModifier|2|
|olchedy|DISTINGUISH_FROM / ComparisonConstructor|1|
|oteedo|ORDERING_OF / RelationalNominal|1|
|airol|REPORT_OF_WEATHER_VISUAL_ACCESS / SensoryInformationWitness|2|
|aram|WEATHER_HEARING_ACCESS / AccessReference|1|

## All finite rules and interfaces

**G01 — Generic descriptive mode**

`Document -> GenericAccount`

The whole account is read as generic historical explanation and conditional illustration, not dated observations or an unqualified universal weather law. This is a paid document-mode assumption. Numeric locus/group order is the authored order, not recovered manuscript order.

**G02 — Event kind and full role application**

`EventKind + RoleBundle -> EventDescription; Assert(EventDescription) -> EventClaim`

EventKind is a lexical value, not itself a proposition or a concrete event. A written subject frame plus written reflexive object supplies STRIKE(agent=x,patient=x); an explicit CONSIDER_CASE STRIKE introduces a generic stroke description E whose actor/action roles remain due. Complete event descriptions may be asserted only by the stated clause productions. No inverse from an arbitrary proposition to an owner is licensed.

**G03 — Nominal modifiers and relation application**

`Modifier[T] + T -> T; RelNominal[A,B] + A -> B`

chcthy,chepaiin,otaiin and first-class relational nouns retain their arguments and owners. A genitive marker ar/chol/qokar licenses the same relation application; bare juxtaposition of a relational head and its argument is a second paid surface. No generic genitive selects a hidden relation.

**G04 — Ordinal interfaces**

`FIRST(OrderedClass,member) or FIRST(ExplicitSequence,event)`

otedy retains first rank in two written domains: thunder among double-vapour impressions, and inflation before subsequent breaking. These are two paid typing interfaces for one ordinal value; a first event alone does not assert observed performance.

**G05 — Classification plus generation**

`Nominal FIRST RelKind GEN Location -> Proposition`

C01 states FirstMember(T0,Impressions(DoubleVapour)) and GenericGeneratedIn(T0,Watery(Substance(C0))). Nominal classification is an explicitly licensed copulaless production; the generation predicate takes the same written T0.

**G06 — Introduction and lexical reference**

`INTRODUCE_SUBJECT Description -> IntroducedRef; SubjectChain(IntroducedRef,Predicates) -> Account`

opaiin creates a reference. When that introduction heads a subject chain, x is bound only in that chain. Its use in an authority argument introduces an authority reference without overwriting already captured vapour terms. Every EntityReference reads the nearest declared x; references are captured, not rebound retroactively.

**G07 — Explicit subject sharing**

`SubjectChain(x, PredicateTemplate*) -> ClaimSequence`

Within the scope of the written subject introduction or case binder, predicate templates all receive that same x. A complete independently headed proposition keeps its own subject. The two cases are separate productions, not a cast from arbitrary data to an assertion. Chains and their endpoints are exactly listed in the manual ASTs; the absence of unique surface parsing is a cost.

**G08 — Possessor and self**

`ITS R -> R(x); SELF(x) + STRIKE -> Strike(x,x)`

odar supplies x as possessor. shedaiin/daiin retain the same x as an emphatic/reflexive reference. A reflexive object in the strike role application must equal the explicit chain subject. Co-referential nominal apposition X SELF(X) is separately licensed before LIGHT; no second agent is introduced.

**G09 — Causal result and sequence**

`THEREBY_IGNITE(prior StrikeEvent, resultSubject) -> CausalEventClaim`

olfor consumes the immediately preceding complete strike description in the SAME explicit subject chain and the following supplied result subject. The causal linkage is source content; it does not assert friction. The later quenching belongs to that same headed chain; DAR reads its explicitly preceding ignition as comparison anchor.

**G10 — End-time adjunct and self-quenching**

`Definite(FinalTime) + SELF_QUENCH x + Location + LATER -> EventClaim`

A temporal nominal may be a temporal adjunct in this fixed clause production. It is not an unwritten AT token. os supplies reflexive quenching, aiin supplies x, oteedy supplies C0, dar compares with the already written ignition. Treating ignited vapour as the quenching subject is a disclosed choice within the source's compressed vapour/fire antecedent.

**G11 — Authority report interface**

`ClaimSequence REPORT IntroducedAuthority -> AttributionClaim`

otees as InformationWitnessKind is applied to an AuthoritySource and the complete preceding vapour chain C02-C03. It states attribution to Aristotle, not independent truth. This is one of TWO paid REPORT interfaces; it is not supplied by the sensory interface.

**G12 — Typed coordination**

`or: Coord[T](T,T); otchedy: AppendToHeadedSequence[T](sequence,T)`

or admits prefix and infix forms for SAME-category operands; permitted categories are Proposition, AccessTemplate, PredicateModifier, SensoryInformationWitness and AnalogyMap. otchedy is a sequence-continuation marker, not a binary operator missing its left argument. In C02 the explicit hot/dry subject description initializes the predicate context; in C06 the preceding completed W proposition is the discourse context. These surface alternatives, type domains and lexical aliases are paid. AccessTemplate is not a Proposition until required observer/pair closure.

**G13 — Conditional storm binder**

`WHEN_STRONG_STORM Condition(w,Cw) Consequent(w,Cw) -> ConditionalClaim`

sain introduces wind w and its scope. qotor introduces Cw in the ENTER condition. The written conjunction also contains INCREASE and SEEK_PASSAGE. All consequences remain under this guard. No equality w=vapour or Cw=C0 is asserted; no inequality is asserted either.

**G14 — Guard-owned cloud projection**

`ENTERED_CLOUD_OF(w,W) -> Cw`

oraiin may project Cw only from W's explicit Enter(w,Cw) premise. This is not a universal unique-location function or a material-origin inverse. The following break/emerge/part-breaking templates receive W.subject through G07; shoral introduces r whose broken parts belong to Cw.

**G15 — Noise from the written rupture**

`DREADFUL_RESULTING_NOISE(W.r) -> nW; REACH(nW,EarsOfBoth(Human,Animal)) -> NoiseClaim`

pchedeey reads the rupture witness actually introduced by shoral, not an arbitrary last event or a storm entity. W.noiseClaim is the guarded auditory consequence. Noise nW, not the whole wind, is the ear recipient argument.

**G16 — Explicit explanatory example**

`NO_WONDER priorClaim CONSIDER argument -> ExplanatoryConclusion`

chotey consumes qocthey's explicit W.noiseClaim reference and the following considered argument. It is not a complete one-word no-wonder sentence. The argument must contain the bladder conditional, concession and qodar analogy; without that body the construction is incomplete.

**G17 — Bladder conditional and order**

`Resound(B) IF [FIRST Inflate(B); AFTERWARD Break(B)] -> GuardedNoiseClaim(nB)`

oloqorain introduces B and its x scope. daiin supplies the subject of qotaiin. qotchdy and ytchedy retain B and their strong/violent modifiers. chckhey orders inflation before breaking. nB is a conditional noise witness, never an observed experiment.

**G18 — Rupture/noise analogy and concession**

`LIKE(GuardedNoiseClaim(nB),Noise(Rupture(Cw))) + ALTHOUGH Light(B) -> AnalogyArgument`

qodar takes the explicitly preceding guarded bladder-noise claim as left argument and the whole following noise-of-rupture-of-cloud phrase as right argument. Both guards/owners are retained. soiis attaches Light(B) as a concession to loudness under the guard. This analogy is separate from access-order comparison.

**G19 — Weather case and deferred observer**

`WITH T IS IntroducingLightning -> WeatherCase C`

otchs opens C and sorain introduces L in its visual branch. The thunder name is a generic co-reference to T0, not a common production instant with L. C has a required observer variable O that MUST be bound by the later literal orar oldar ain inside this same case. No owner is supplied from the source or a different reader.

**G20 — Property reason and branch scope**

`Seen(L) SOONER BECAUSE [Clear Bright x IS] -> VisualAccessTemplate`

sorain binds x=L in the visual branch. ytedar/chz are jointly predicated of that same aiin reference through arody. The clear/bright reason modifies earlier seeing. ypshedy then opens a separate x=T branch; captured L is unchanged.

**G21 — Weather access pair**

`Coord(VisualTemplate[earlier],AuditoryTemplate[later]) + written ObserverRecipient -> AccessOrderClaim`

dar/chedy form later hearing of T. The inner or combines two AccessModifiers: the faculty reason and the explicit recipient phrase. orar takes oldar=our community and ain=Ears, assigning O to BOTH templates. Closing C requires all O references resolved and then yields Before(See(O,L),Hear(O,T)), with the two stated reasons. No propagation speeds or numerical delay are inferred.

**G22 — Faculty comparison**

`CONSIDER [SightOf(O) SUBTLER_THAN Hearing(O) IS] -> PropertyClaim`

oteey adds no owner; qodaiin and an use the observer supplied by the same case. chey completes the comparison. This historical faculty explanation is not a new measured causal law.

**G23 — Case-designator interfaces**

`CONSIDER_CASE New(EventKind) Body or CONSIDER_CASE Existing(CaseRef) Body`

okees has two paid interfaces in a tagged CaseDesignator union. With olaiin=STRIKE it introduces K.E and an x reference to that stroke; actor/action fields are due later in the same K body. With ochar it enters the already completed C and does not introduce a new observation. No generic function quotation or unknown operator-as-data is allowed.

**G24 — Wood access comparison**

`E SOONER SEEN_BY O THAN NoiseOf(E) BY sameO HEARD -> AccessOrderClaim`

K.E is the written event from okees olaiin. sary introduces the observer O_K. qodain supplies nE with owner E; chckhy/ykeedy supply the SAME observer for hearing. qokshedy completes the compared access. Thus Before(See(O_K,E),Hear(O_K,nE)); E is not made into two successive external occurrences.

**G25 — Explicit repeated assertions**

`Coord(Occurs(E),Coord(HasOrgan(O_K,Ears),EarlierReDescription(E))) -> Proposition`

The W20 material is not discarded. ckhed asserts occurrence inside the generic illustration. ain/olchey state ear ownership of the already written observer. The latter is an ADDED redundant explanatory assertion, not quoted source wording and not a woodcutter/observer identity. It is paid as a possessive predicate plus observer reference.

**G26 — Written hewer/action ownership**

`E BY_A_PERSON [Tree HEW local-x] -> AgentActionDescription(E,h,Hew(h,tree))`

qokeody introduces human h in a LOCAL x scope and associates E with the explicitly written hewing action. qoekedy and dody supply tree and hew; shedy supplies h. That complete object-verb-agent clause closes the local x scope. The outer x remains E. The rule states E is a stroke in that hewing action, not merely an unrelated blow by a person who also hews. This extra action-link payload is explicit and paid.

**G27 — Referential earlier description**

`SOONER E AgentActionDescription SightOf(O_K) -> repeated EarlierAccessClaim`

The second qokal uses the SAME completed K order, not another unmentioned comparison or timing case. qodaiin explicitly supplies the faculty with its written owner O_K; the sight-to-visual-access construction is paid. The event E remains the object; the relative hewer h does not replace the observer. There is no implicit global reset.

**G28 — Written pair analogy**

`VisualAccessOf(O_K,E) PARALLELS_WEATHER_VISUAL L; E PARALLELS_WEATHER_AUDITORY Noise(T) -> paired AnalogyMap`

los/ar/shedy supply the first visual access. qokshey maps it to C's already written seeing L. aiin/og plus the complete noise-of-thunder phrase map K's hearing of nE to C's hearing T. og checks that nE is the noise of the SAME E. The infix or joins the two map components. As both owned pairs have Before, this yields the source's comparison of comparisons. It never equates observers or physical objects across cases.

**G29 — Captured references and finite scopes**

`Reference(scope,name) -> previously introduced typed value`

All references and their introductions are tabulated. Authority introductions, the visual and auditory branches, and the hewer relative clause have explicit lexical scopes. Body concatenation does not silently reset x. No reference from another transcription may repair an unbound slot. Only C.O has the declared within-case delayed binding; all other reads require their listed introduction.

**G30 — Sensory report interface**

`REPORT_OF(AccessWitness) -> SensoryInformationWitness`

The second REPORT interface wraps an ALREADY WRITTEN sensory access as informational witness and retains that exact access. It creates no later spoken report or extra sensory event. airol is a paid whole spelling of the visual witness; otees ar aram constructs the auditory witness. This cross-domain report abstraction is an additional, source-unconfirmed interface distinct from G11.

**G31 — Ordering of retained access witnesses**

`ORDERING_OF(Coord(InfoWitness(aV),InfoWitness(aA))) -> AccessOrderingDescription`

The ordering is projected through retained access records and must equal the completed C order. No inequality of utterance/report production times is inferred. Both members are the SAME typed SensoryInformationWitness category; raw Event versus Report is not silently coordinated.

**G32 — Closing distinction**

`GenerationDescription(T0,C0) DISTINGUISH_FROM AccessOrderingDescription -> MetaStatement`

C09 redescribes the initial thunder/cloud generation through the same generated predicate. It distinguishes that account from C's access order. This is an ADDED metalinguistic synopsis conclusion, not an explicit sentence of id88 or a new causal theorem. It does not assert that lightning and thunder are generated simultaneously.

**G33 — Complete statement and scope endpoints**

`Complete typed Assertion/Argument -> DocumentMember`

The authored ASTs determine the paid boundaries. No native line ending is an operator or automatic reset. Bare nominals, unfilled access templates and unknown literal forms do not become statements. The grammar can be ambiguous; no unique parse, deciphered syntax or executable decoder is claimed.

**G34 — Auditory-aspect identity only on auditory phenomena**

`NoiseOf(t:AuditoryPhenomenon)=t; NoiseOf(e:StrikeEvent)=n with Owner(n)=e and n not typed StrikeEvent`

Thunder is assigned AuditoryPhenomenon. The weather HEARD(T) object and the later NOISE OF THUNDER phrase therefore match through this PAID law. No identity NoiseOf(Stroke)=Stroke is allowed. The law is an authoring commitment, not independently confirmed word meaning; without it the later weather analogy has an object mismatch.

**G35 — Introducing nominals versus kinds**

`IntroducingReference -> Ref with description; KindDescription -> Spec; INTRODUCE_SUBJECT(Spec) -> Ref`

The lexicon explicitly marks which words introduce references. Pure vapour/organ/faculty kinds are not silently made into persons or events. Named Aristotle is a proper nominal specification whose introduction retains that named actor. Determiners preserve introducing effects and reference type. With a relational head, a determiner decorates that head while its owner slot remains OPEN until the written genitive argument arrives; it does not assert an unowned noise.

**G36 — Explicit nominal-restriction initialization**

`SubjectIntroduction(HotDryVapour) -> x with [Vapour(x),Hot(x),Dry(x)] predicate context`

The initial additive marker in C02 has this WRITTEN nominal restriction as its antecedent context. It does not invent an empty preceding assertion, owner or omitted clause. This is a paid description-to-subject-qualification interface; it does not invert an arbitrary predicate into a reference.

**G37 — Generation-description surfaces**

`Phenomenon GENERATED Location or Phenomenon Location GENERATED -> GenerationDescription`

C01 and C09 use these two paid linear surfaces for the SAME complete role bundle. A classification/assertion context in C01 asserts generic generation; the distinction context in C09 consumes the description without asserting a new occurrence. The predicate cannot absorb an arbitrary untyped location or owner.

## Type boundaries, scopes and costs

```json
{
  "type_interfaces": {
    "reference": "Ref[T] retains its tagged referent sort. READ_X and SELF_X are parametric lookup operations over the explicitly typed binder, not per-occurrence sense changes or Event/Person casts.",
    "nominals": "Pure KindSpec is distinct from Ref[T]. Only marked IntroducingReference lexical constructors or opaiin introduce a witness. Tree, cloud, lightning, observer and bladder introductions are listed. A determiner preserves type/arity.",
    "event_kind": "EventKind STRIKE is data usable only through the declared role-application or case-instantiation constructors; it is not silently asserted or read as a concrete event.",
    "case": "Finite case records W,C,K,B and the vapour subject sequence have exactly the fields listed in the scope/grammar. The literal heads introduce them. No unknown token receives a hidden control effect.",
    "observer": "Observer is a tagged human-community or human-person reference. C.O is explicitly OUR; K.O is explicitly A_PERSON. No equality with hewer h is asserted.",
    "pending": "Only C.O may be bound later within the same C AST. Every other lookup has its listed introduction; all C.O uses must be resolved at case closure.",
    "noise": "AuditoryPhenomenon thunder is already auditory. G34 is an explicit paid fixed point NoiseOf(T)=T only for that sort. A StrikeEvent and its NoiseRef remain differently typed, with written ownership.",
    "reports": "InformationWitnessKind has two paid construction interfaces. A sensory witness retains its access event and has no new speech/report time. Authority attribution does not inherit that timing projection.",
    "event_assertion": "Complete EventDescription is distinct from EventClaim. Only the stated assertion/classification/guard productions assert it. C09 uses a generation description as an object of a metalinguistic distinction.",
    "unknown": "An unassigned alternate literal has no value, binding, reset, coercion or alias. A matching following form cannot borrow a ZL reference."
  },
  "scopes": {
    "V": {
      "intro": "ZL3b|f85r2.1|G012",
      "body": "C02 and quenching in C03",
      "x": "vapour v",
      "closure": "authority suffix in C03; its own authority introduction is nested"
    },
    "Authority": {
      "intro": "ZL3b|f85r2.1|G034",
      "body": "the following Aristotle nominal only",
      "x": "Aristotle",
      "closure": "end C03 argument"
    },
    "W": {
      "intro": "ZL3b|f85r2.2|G001",
      "body": "C04-C05",
      "x": "wind w",
      "additional_bindings": "qotor=Cw; shoral=r; pchedeey=nW and guarded noise claim",
      "closure": "complete noise-recipient clause in C05; W record retained by explicit later references"
    },
    "B": {
      "intro": "ZL3b|f85r2.8|G006",
      "body": "C06",
      "x": "bladder B",
      "closure": "complete concession in E11"
    },
    "C": {
      "intro": "ZL3b|f85r2.12|G001",
      "body": "C07",
      "x_branches": {
        "visual": "sorain gives L",
        "auditory": "ypshedy gives T0"
      },
      "observer": "orar oldar ain binds O=OurCommunity; this is the sole permitted forward within-case owner binding",
      "closure": "complete S17 recipient phrase; captured C later read explicitly"
    },
    "K": {
      "intro": "ZL3b|f85r2.18|G001",
      "body": "C08",
      "x": "stroke E from following olaiin EventKind",
      "observer": "sary binds O_K; ykeedy reads it",
      "noise": "qodain introduces nE owned by E",
      "closure": "complete paired analogy in W23"
    },
    "Hewer": {
      "intro": "ZL3b|f85r2.21|G001",
      "body": "qokeody (qoekedy dody shedy)",
      "x": "human hewer h",
      "closure": "the complete tree/object-hew/verb-h/agent clause; outer K x=E resumes"
    },
    "C_reentry": {
      "intro": "ZL3b|f85r2.24|G001",
      "body": "C09",
      "case_designator": "ochar explicitly names C",
      "closure": "end of .24"
    }
  },
  "costs": {
    "independent_literal_whole_bindings": 115,
    "retained_component_values": 0,
    "retained_cuts": 0,
    "declared_lexical_payload_units": 158,
    "payload_unit_definition": "One named semantic relation/property/reference/binder in the listed entry, counted by the declared convention. Not a minimal description length estimate; unbounded evidence of compression is not claimed. All scope, rule and interface costs are separately listed.",
    "grammar_productions_or_conventions": 38,
    "whole_occurrence_values": {
      "ZL3b": 156,
      "IT2a": 136,
      "RF1b": 128
    },
    "named_scope_records": 8,
    "reader_aliases": 0,
    "state_or_reference_effect_entries": 42,
    "surface_and_interface_costs": [
      "generic account mode",
      "numeric page order",
      "copulaless classification and properties",
      "marked/unmarked genitive application",
      "prefix/infix coordination and additive lexical alternative",
      "event-kind role application versus case instantiation",
      "nominal kind/introduction distinction",
      "subject-sharing with explicit lexical scope",
      "authority report versus sensory information witness",
      "first rank over class versus explicit conditional sequence",
      "earlier/later templates closed by an overt observer phrase",
      "delayed observer binding ONLY in C",
      "postposed authority scope over the vapor account",
      "local hewer/action relative clause and action-event association",
      "second qokal as referential repetition of the same pair",
      "auditory-aspect fixed point ONLY on auditory phenomena",
      "closing generation/access distinction as an added summary",
      "nominal restrictions initialize the explicit vapour predicate context before additive continuation",
      "two word orders for generation role application; assertion versus use as a description remain distinct"
    ],
    "paid_synonym_groups": {
      "reference_to_current_x": [
        "aiin",
        "sheedy",
        "olfar",
        "shedy"
      ],
      "self_reference": [
        "shedaiin",
        "daiin"
      ],
      "vapour_kind": [
        "otchdy",
        "qopchas"
      ],
      "definite_nominal": [
        "ol",
        "sheo"
      ],
      "genitive_markers": [
        "ar",
        "chol",
        "qokar"
      ],
      "copula": [
        "chey",
        "arody"
      ],
      "because": [
        "chy",
        "am"
      ],
      "earlier": [
        "sodaiiin",
        "qokal"
      ],
      "thunder_names_with_different_declared_scope_effects": [
        "odeedy",
        "shedor",
        "ypshedy"
      ],
      "noise_relational_heads": [
        "qotedar",
        "lcheol"
      ]
    },
    "paid_source_extensions": [
      "repeated occurrence and observer-ear ownership in W20",
      "earlier access repeated through the explicit agent/tree relative clause",
      "closing generation-versus-access statement",
      "sensory access represented as an information witness; not a literal quotation"
    ],
    "no_claim": "No MDL advantage, statistical fit, independently meaningful morphology, unique parsing or confirmation. A substantial freely chosen whole dictionary remains."
  },
  "reader_counts": {
    "ZL3b": {
      "all_rows": 156,
      "assigned_literal_rows": 156,
      "unassigned_literal_rows": 0,
      "manual_whole_candidate_rows": 156,
      "complete_reader_claim": "conditional author ZL derivation only"
    },
    "IT2a": {
      "all_rows": 157,
      "assigned_literal_rows": 136,
      "unassigned_literal_rows": 21,
      "manual_whole_candidate_rows": 0,
      "complete_reader_claim": "NO; no alternate full derivation or reference completion asserted"
    },
    "RF1b": {
      "all_rows": 160,
      "assigned_literal_rows": 128,
      "unassigned_literal_rows": 32,
      "manual_whole_candidate_rows": 0,
      "complete_reader_claim": "NO; no alternate full derivation or reference completion asserted"
    }
  }
}
```

## Prefreeze revisions

- R0 (unfrozen planning): Prospective source allocation: initial annulus classification/vapour; N and E7 wind; remaining E bladder; S weather access; W wood access/analogy; final annulus summary. No figure labels or source-defined fourfold map.
- R1 (rejected before retention): Explored d/qo as sound/owned-aspect operations over named or changing owners and possible ar/aiin/ain reference roots. First annular references and the later ear/faculty uses did not supply one fixed typed interface. No cut or component value was retained.
- R2 (rejected before retention): Under the actual whole candidate, qod|aiin would have to yield observer sight from a changing subject reference, while qod|ain would have to yield stroke noise from EAR-kind. A common operator cannot be obtained from these two outputs without additional input-specific lookup or context repair. qodar also remains LIKE. These are opaque paid wholes, not a claimed qod family.
- R3 (paid construction): olaiin kept one STRIKE EventKind value. Explicit role application for the vapour and explicit case instantiation for the wood example replace an unannounced noun/verb cast.
- R4 (paid scopes): Current-subject references became lexical-scope references with explicit introductions, captures and endpoints. No implicit global subject switching remains authorized. The hewer local x closes after TREE HEW x and restores the outer stroke reference by lexical scope, not a new reset word.
- R5 (paid interfaces): FIRST has classification and conditional-sequence interfaces; coordinate has prefix/infix surfaces; nominal relation application has marked and unmarked surfaces. These are syntax costs, not manuscript discoveries.
- R6 (paid repeated-order reference): The second qokal re-describes the SAME completed K comparison. It is not an independent sensory case and cannot use an unbound comparison partner.
- R7 (paid REPORT interfaces): Authority attribution and sensory information witnesses are separately specified. The final summary is not read as two spoken reports made at different times.
- R8 (prefreeze type correction): The tail initially mixed a raw visual access with an auditory information witness. airol is now explicitly a paid whole visual information witness so the pair has one type; G31 projects its retained access ordering. No silent Event/Report cast remains claimed.
- R9 (prefreeze additional law): The later NOISE OF THUNDER phrase otherwise differed from the earlier HEARD(THUNDER) object. G34 explicitly makes NOISE_OF the identity on an already auditory phenomenon, while keeping a stroke distinct from its noise. This is a new authoring assumption, not source-confirmed morphology.
- R10 (source extensions retained and marked): The W ear-ownership repetition and closing generation/access distinction are not literal source sentences. They are added synopsis assertions. The authority/sensory-report abstraction, ear predicate and closure are the weakest motivated additions.
- R11 (prefreeze type clarification): All introducing nominal references were distinguished from pure kind specifications. Tree introduction, lightning/thunder branch binding, and relation-head determiners are explicit; no new literal aliases were added for other readers.
- R12 (prefreeze domain/valency clarification): Explicitly included AccessTemplate in the finite coordination domains, distinguished additive sequence continuation from binary coordinate, and paid initialization of the first vapour predicate context from the written hot/dry nominal. Parametric reference lookups preserve referent sorts rather than casting Events into Persons.
- R13 (prefreeze final interface clarification): The two generation surfaces were explicitly licensed and REPORT was typed as a relational witness kind with exactly the two already paid construction interfaces. These clarifications are included in the first freeze, not retrospective repairs.

## Literal alternate consequences

- IT2a f85r2.1 G007 otedy where ZL has otody: In the SAME C01 template, FIRST:OrdinalSpecifier occupies the GENERATED:EventPredicateKind position. It cannot be silently read as GENERATED. This is a fixed-template conflict, not a theorem excluding a wholly different IT parse.
- IT2a/RF1b f85r2.20 initial ar where ZL has or: The frozen C08 continuation expects COORDINATE; GENITIVE is a different fixed operator. No r/o alias or reader switch is permitted.
- IT2a/RF1b f85r2.24 final ar ar am rather than ZL ar aram: The ZL auditory-access reference aram is not derived from ar+am. am remains BECAUSE and ar remains GENITIVE. The same C09 tail therefore does not have its required access-reference argument.
- all alternatives all24 21 IT /32 RF unassigned occurrences: These remain literal gaps. Unknown words cannot supply unstated bindings or rescue known conflicts. No full alternate derivation is claimed.

## Limits

The early source/vapour report and the final sensory-report representation require different paid interfaces. The closing generation/access statement and W ear-ownership repetition are source-inspired additions, not quoted source sentences. All source duties remain, but exact source equivalence is not claimed. A large independently paid whole dictionary remains; this does not establish a productive word-part model.

## Final prefreeze scope clarification

C02 is an OPEN subject-account fragment completed by C03, not a standalone closed binder. C04 is an OPEN conditional header completed by C05. The actual lexical binders are opaiin and sain, not the presentation wrappers ScopeV/ConditionalW. The nested complete AST carries these scopes; native line endings never close them. The selected body boundaries are paid parse choices, not claimed unique or source-independent punctuation.

`DOCUMENT(C01, SUBJECT_SCOPE_OPENED_BY_C02_OPAIIN(C02,C03), CONDITIONAL_OPENED_BY_C04_SAIN(C04,C05), C06, C07, C08, C09)`

Final grammar/convention count:38. C02 has type OpenSubjectAccount[V], completed by C03. C04 is completed by C05. These are display fragments of one whole scoped AST, not independent closed binders.
