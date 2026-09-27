# RAW568 recipient-restriction whole ZL draft

A complete proposed ZL account, with manual typing and scope claims for independent review. No confirmed meanings, all-reader completion, outside reading or clinical truth is claimed. All source and target content is already owned.

## Exact lexical inventory

| Form | Value | Denoted value or syntax type | Status |
|---|---|---|---|
| ar | SPLEEN | AnatomicalRole | fixed atom |
| aiin | GALL_BLADDER | AnatomicalRole | fixed atom |
| ain | KIDNEYS | AnatomicalRole | fixed atom |
| dar | A_c(SPLEEN) | Pred[c] | computed |
| daiin | A_c(GALL_BLADDER) | Pred[c] | computed |
| qodar | B_c(A_c(SPLEEN)) | Mod[c] | computed |
| qodaiin | B_c(A_c(GALL_BLADDER)) | Mod[c] | computed |
| qodain | B_c(A_c(KIDNEYS)) | Mod[c] | computed |
| sain | GENERIC_BODY_CONTEXT | ContextBinderSyntax[c] | new |
| or | PAIR | PairConstructor | new |
| opchdy | LIVER | AnatomicalRole | new |
| qotor | VEINS | AnatomicalRole | new |
| sheedy | ARTERIES | AnatomicalRole | new |
| shodaiin | HEART | AnatomicalRole | new |
| olfar | ORGANS_UNDER_NUTRITIONAL_CONSIDERATION | RoleClass[c] | new |
| ary | MEMBERSHIP_DECLARATION | MembershipDeclarationSyntax[Omega] | new |
| dair | GENERIC_MATERIAL_CASE | MaterialBinderSyntax[n] | new |
| sheo | FOR_ORGAN | OrganScopeMarker[b] | new |
| oraiin | GALL_BLADDER | AnatomicalRole | new |
| chol | IS | PredicationOperator | new |
| ockhdar | MATERIAL_n | Ref[n:Material[c]] | new |
| olkar | THEN_HAS_CAPABILITY | CapabilityConsequentMarker | new |
| shoral | ATTRACT | FacultyKind | new |
| roseer | ORGAN_b | Ref[b:AnatomicalRole] | new |
| pchedeey | THEREFORE | ConcludingMarker | new |
| olkey | NO_FURTHER_DOUBT | AssuranceOperator | new |
| qokedy | EVERY_RELEVANT_ORGAN | RoleBinderSyntax[b] | new |
| sheos | THE_NATURAL_FACULTY_SET | FacultySetBinderSyntax[F] | new |
| fcheey | PROPER_FOR | MaterialRoleRelation[c] | new |
| otchedy | REJECT | FacultyKind | new |
| chotey | FOREIGN_TO | MaterialRoleRelation[c] | new |
| qocthey | ALTER | FacultyKind | new |
| oteey | ATTRACT | FacultyKind | new |
| ol | DEFINITE_MENTION | MentionOperator | new |
| oloqorain | RETAIN | FacultyKind | new |
| qotaiin | GENERIC_MATERIAL_CASE | MaterialBinderSyntax[e] | new |
| tchedy | ATTRACT | FacultyKind | new |
| otedy | GALL_BLADDER | AnatomicalRole | new |
| qotchdy | INSTANCE_OF | MembershipRelation | new |
| chckhey | THE_RELEVANT_ORGAN_CLASS | Ref[Omega:RoleClass[c]] | new |
| ytchedy | QUALIFIED_EXAMPLE | DescriptionDeclarationSyntax[D0] | new |
| qotedar | RESIDUE_FROM | AnatomicalRole->Pred[c] | new |
| qokar | LIVER | AnatomicalRole | new |
| qotchd | SOME_QUALIFIED_MATERIAL | QualifiedBinderSyntax[u:Pred[c],x:Material[c]] | new |
| qotom | MATERIAL_x | Ref[x:Material[c]] | new |
| soiis | ANALOGY_FRAME | AnalogyBinderSyntax[a] | new |
| shedaiin | PROPER_FOR | MaterialRoleRelation[c] | new |
| chok{co}m | HIGHLY_PLEASING_TO | MaterialRecipientRelation[c] | new |
| otchs | RESIDUAL_ORIGIN | OriginAssertionOperator | new |
| shedor | LIVER | AnatomicalRole | new |
| chey | MATERIAL_x | Ref[x:Material[c]] | new |
| sorain | INFERRED | ProjectionMarker | new |
| shedy | LIVER | AnatomicalRole | new |
| tedy | THE_RELEVANT_ORGAN_CLASS | Ref[Omega:RoleClass[c]] | new |
| sodaiiin | FOUR | Cardinal | new |
| chy | NECESSARY_FOR_NUTRITION | NutritionNecessityOperator | new |
| ytedar | AS_IN_THE_ANALOGY | AnalogyCompletionMarker | new |
| chz[s:r] | HUMAN_FAECES | Pred[c] | new |
| arody | DOGS | AnimalKind | new |
| ypshedy | GENERIC_CAPABILITY_CASE | MaterialBinderSyntax[k] | new |
| chedy | MATERIAL_k | Ref[k:Material[c]] | new |
| am | SPLEEN | AnatomicalRole | new |
| odain | THE_BASE_DESCRIPTION | Ref[D0:Pred[c]] | new |
| an | OTHER_QUALIFIED_MATERIAL | QualifiedBinderSyntax[g:Pred[c],x:Material[c]] | new |
| orar | OTHER_RECIPIENT | TopicDeclarationMarker | new |
| oldar | THE_BASE_DESCRIPTION | Ref[D0:Pred[c]] | new |
| okees | ANALOGY_SOURCE | SourceSideBinderSyntax[s] | new |
| olaiin | HUMAN_FAECES | Pred[c] | new |
| qokal | ANALOGY | AnalogyRelation | new |
| chdy | DOGS | AnimalKind | new |
| sary | HIGHLY_PLEASING_TO | MaterialRecipientRelation[c] | new |
| qokshedy | OTHERS | ContrastMarker | new |
| chckhy | THE_BASE_DESCRIPTION | Ref[D0:Pred[c]] | new |
| ykeedy | QUALIFIED_MATERIAL | QualifiedBinderSyntax[v:Pred[c],k:Material[c]] | new |
| ckhed[a:y] | G_QUALIFIED_DESCRIPTION | Ref[g:Pred[c]] | new |
| olchey | K_QUALIFIED_DESCRIPTION | Ref[v:Pred[c]] | new |
| qokeody | PROJECT_BASE | ProjectionAssertionOperator | new |
| qoekedy | MATERIAL_x | Ref[x:Material[c]] | new |
| dody | RESIDUE_FROM | AnatomicalRole->Pred[c] | new |
| los | THE_BASE_DESCRIPTION | Ref[D0:Pred[c]] | new |
| qokshey | SHOWN_BEFORE | PriorProofOperator | new |
| qose?y | THE_NECESSITY_ASSERTION | Ref[Pi:Proposition] | new |
| og | KIDNEYS | AnatomicalRole | new |
| lcheol | THE_FOUR_FACULTIES | Ref[F:FacultySet] | new |
| sheoly | CALLED_HANDMAIDS_OF_NUTRITION | FacultySet->Proposition | new |

## Whole selected sequence

### N1

`sain or or aiin opchdy qotor sheedy shodaiin olfar ary`

Declare generic bodily c; Omega is the organs under nutritional consideration; GALL_BLADDER, LIVER, VEINS, ARTERIES and HEART are members. The paired groupings introduce no fourth-organ or picture map.

Source duties: O04; explicit gall-bladder membership.

Groups: ZL3b|f85r2.2|G001, ZL3b|f85r2.2|G002, ZL3b|f85r2.2|G003, ZL3b|f85r2.2|G004, ZL3b|f85r2.2|G005, ZL3b|f85r2.3|G001, ZL3b|f85r2.3|G002, ZL3b|f85r2.3|G003, ZL3b|f85r2.3|G004, ZL3b|f85r2.3|G005.

### N2

`dair sheo oraiin chol daiin ockhdar olkar shoral roseer`

For generic n:Material[c], b=GALL_BLADDER: A_c(GALL_BLADDER)(n) => NaturalCapability(b,ATTRACT,n,c). IS explicitly applies the bare predicate to Ref[n]; no liver-origin restriction.

Source duties: O02; extra explicit general-organ instantiation.

Groups: ZL3b|f85r2.4|G001, ZL3b|f85r2.4|G002, ZL3b|f85r2.4|G003, ZL3b|f85r2.4|G004, ZL3b|f85r2.4|G005, ZL3b|f85r2.5|G001, ZL3b|f85r2.5|G002, ZL3b|f85r2.5|G003, ZL3b|f85r2.6|G001.

### E1

`pchedeey olkey qokedy sheos fcheey otchedy chotey qocthey oteey ol oloqorain`

Concluding assurance: for every b in Omega, proper material is generically attracted, foreign material generically rejected; what b attracts is subject to its natural ALTER and RETAIN powers. Bind F={REJECT,ALTER,ATTRACT,RETAIN}.

Source duties: O01;O02;O03;O04.

Groups: ZL3b|f85r2.7|G001, ZL3b|f85r2.7|G002, ZL3b|f85r2.7|G003, ZL3b|f85r2.7|G004, ZL3b|f85r2.7|G005, ZL3b|f85r2.8|G001, ZL3b|f85r2.8|G002, ZL3b|f85r2.8|G003, ZL3b|f85r2.8|G004, ZL3b|f85r2.8|G005, ZL3b|f85r2.8|G006.

### E2

`daiin qotaiin tchedy otedy qotchdy chckhey`

For generic e:Material[c], A_c(GALL_BLADDER)(e) => NaturalCapability(GALL_BLADDER,ATTRACT,e,c); assert GALL_BLADDER in Omega. Binder syntax is not passed to the predicate.

Source duties: O02; repeated explicit instantiation.

Groups: ZL3b|f85r2.9|G001, ZL3b|f85r2.9|G002, ZL3b|f85r2.9|G003, ZL3b|f85r2.9|G004, ZL3b|f85r2.9|G005, ZL3b|f85r2.9|G006.

### E3

`ytchedy qodar qotedar qokar qotchd qotom`

Let D0=RESIDUE_FROM(LIVER,c). Bind u=B_c(A_c(SPLEEN))(D0), and some x:Material[c] with u(x). Ref[x] denotes that same x. The existential continuation extends through the remaining selected synopsis.

Source duties: O08 spleen; written modifier application.

Groups: ZL3b|f85r2.10|G001, ZL3b|f85r2.10|G002, ZL3b|f85r2.10|G003, ZL3b|f85r2.10|G004, ZL3b|f85r2.10|G005, ZL3b|f85r2.10|G006.

### E4

`soiis aiin shedaiin chok{co}m`

Bind analogy record a with target recipient GALL_BLADDER, target relation PROPER_FOR, and source relation HIGHLY_PLEASING_TO; its common target origin description is the already declared D0.

Source duties: O07 analogy setup.

Groups: ZL3b|f85r2.11|G001, ZL3b|f85r2.11|G002, ZL3b|f85r2.11|G003, ZL3b|f85r2.11|G004.

### S1

`otchs shedor chey sorain`

Infer RESIDUE_FROM(LIVER,c)(Ref[x]) for the SAME spleen-qualified x introduced in E3. This is projection of u(x), not a new existential.

Source duties: additional downstream origin assertion.

Groups: ZL3b|f85r2.12|G001, ZL3b|f85r2.12|G002, ZL3b|f85r2.12|G003, ZL3b|f85r2.12|G004.

### S2

`or shedy tedy sodaiiin chy`

For the explicit pair LIVER/Omega, assert |F|=4 and Pi: every part b under nutritional consideration requires all faculties F if b is to be nourished. This is necessity, not sufficiency or actual nutrition.

Source duties: O05.

Groups: ZL3b|f85r2.13|G001, ZL3b|f85r2.13|G002, ZL3b|f85r2.13|G003, ZL3b|f85r2.13|G004, ZL3b|f85r2.13|G005.

### S3

`ytedar chz[s:r] aiin arody`

Complete a: human faeces are highly pleasing to DOGS; compare that recipient-relative evaluation to D0 being proper for the stated GALL_BLADDER recipient. aiin agrees with a.target; PLEASING and PROPER remain distinct.

Source duties: O07.

Groups: ZL3b|f85r2.14|G001, ZL3b|f85r2.14|G002, ZL3b|f85r2.14|G003, ZL3b|f85r2.14|G004.

### S4

`ypshedy dar chedy or am oteey`

For generic k:Material[c], A_c(SPLEEN)(Ref[k]) => NaturalCapability(SPLEEN,ATTRACT,k,c). Pair(am,oteey) supplies the independently written organ and faculty arguments.

Source duties: O02; second bare component input.

Groups: ZL3b|f85r2.15|G001, ZL3b|f85r2.15|G002, ZL3b|f85r2.15|G003, ZL3b|f85r2.15|G004, ZL3b|f85r2.15|G005, ZL3b|f85r2.16|G001.

### S5

`qodaiin odain an chey`

Bind g=B_c(A_c(GALL_BLADDER))(D0), and other x:Material[c] with g(x). This new x shadows E3 x in the continuation; it is not asserted equal or unequal to the earlier witness. chey evaluates to this new x.

Source duties: O08 gall-bladder; O09.

Groups: ZL3b|f85r2.16|G002, ZL3b|f85r2.16|G003, ZL3b|f85r2.16|G004, ZL3b|f85r2.16|G005.

### S6

`orar oldar ain`

Announce another recipient topic: same D0 description, recipient KIDNEYS. This is a topic declaration; its existence/suitability assertion follows in W2.

Source duties: O08 kidneys topic; O09.

Groups: ZL3b|f85r2.17|G001, ZL3b|f85r2.17|G002, ZL3b|f85r2.17|G003.

### W1

`okees olaiin qokal chdy sary`

Bind source-side s=(HUMAN_FAECES,DOGS,HIGHLY_PLEASING_TO) for the ANALOGY relation; retain its generic pleasingness claim. This explicitly restates the first side of the comparison.

Source duties: O07.

Groups: ZL3b|f85r2.18|G001, ZL3b|f85r2.18|G002, ZL3b|f85r2.18|G003, ZL3b|f85r2.18|G004, ZL3b|f85r2.18|G005.

### W2

`qokshedy qodain chckhy ykeedy chedy`

Bind v=B_c(A_c(KIDNEYS))(D0), and other k:Material[c] with v(k). chedy denotes that very k; no new recipient-specific modifier law.

Source duties: O08 kidneys; O09.

Groups: ZL3b|f85r2.19|G001, ZL3b|f85r2.19|G002, ZL3b|f85r2.19|G003, ZL3b|f85r2.19|G004, ZL3b|f85r2.19|G005.

### W3

`or aiin ckhed[a:y] or ain olchey qokal shedy`

Compare source-side s with the two target pairs (GALL_BLADDER,g) and (KIDNEYS,v), whose qualified materials preserve residual origin LIVER and the corresponding PROPER relation. This is an analogy, not a claim that those residues please organs.

Source duties: O07; O08 repeat; same source.

Groups: ZL3b|f85r2.20|G001, ZL3b|f85r2.20|G002, ZL3b|f85r2.20|G003, ZL3b|f85r2.20|G004, ZL3b|f85r2.20|G005, ZL3b|f85r2.20|G006, ZL3b|f85r2.20|G007, ZL3b|f85r2.20|G008.

### W4

`qokeody qoekedy dody shedy qodaiin los`

Project RESIDUE_FROM(LIVER,c)(Ref[x]) from the written [qodaiin los] qualified description applied to that SAME x. Ref[x] remains the gall-bladder witness from S5 because W2 binds k, not x.

Source duties: second downstream origin application.

Groups: ZL3b|f85r2.21|G001, ZL3b|f85r2.21|G002, ZL3b|f85r2.21|G003, ZL3b|f85r2.21|G004, ZL3b|f85r2.21|G005, ZL3b|f85r2.22|G001.

### W5

`ar shedy qokshey qose?y or aiin og`

The prior demonstration applies to Pi, including the explicitly listed SPLEEN, LIVER, GALL_BLADDER and KIDNEYS. No new proof is reconstructed; membership of those organs in the relevant class is stated as the scope premise.

Source duties: O06 prior proof.

Groups: ZL3b|f85r2.22|G002, ZL3b|f85r2.22|G003, ZL3b|f85r2.22|G004, ZL3b|f85r2.22|G005, ZL3b|f85r2.22|G006, ZL3b|f85r2.22|G007, ZL3b|f85r2.22|G008.

### W6

`ol lcheol chol ol sheoly`

The denoted faculty set F IS [CALLED_HANDMAIDS_OF_NUTRITION](F). Definite mention leaves the cited values unchanged. This is a naming metaphor, not literal servants or sufficient nutrition.

Source duties: O06 service metaphor.

Groups: ZL3b|f85r2.23|G001, ZL3b|f85r2.23|G002, ZL3b|f85r2.23|G003, ZL3b|f85r2.23|G004, ZL3b|f85r2.23|G005.

## Written grammar and type interfaces

**G00 Context and scope.** sain is ContextBinderSyntax, not a Context value in an argument slot. Its continuation is all following selected N,E,S,W clauses to the unit end. Evaluate the body as a generic assertion in c. Outside rows receive no automatic c. Omega,F,Pi,D0 and analogy records are bound only by the explicit constructions below. Local generic material/organ binders close at their declared clause end; qualified existentials use the written continuing-declaration construction. No actual episode is introduced. c is a generic historical-physiology setting, not one identified patient or one physical body. Material[c] admits the source liver-residue and human-faeces kinds; this shared domain does not identify them.

**G01 Fixed components.** The first-contract A/B laws and five exact cuts are unchanged. ar/aiin/ain evaluate to fixed role constants. A consumes that value and current c; B consumes the resulting Pred[c]. A Pred is not a faculty; a Mod is not an assertion.

**G02 Typed pairing.** or always constructs an ordered semantic pair from two complete expressions. Product types are exact: Pair[Role,Role], Pair[Pair[Role,Role],Role], Pair[Role,RoleClass], Pair[Role,FacultyKind], Pair[Role,Pred]. Prefix syntax supplies two complete operands. Product consumers below explicitly project first/second components; no pair is silently coerced to a role, predicate or faculty.

**G03 Organ-class declaration.** ContextBinder Pair[Pair[Role,Role],Role] Role Role RoleClass MembershipDeclaration => bind Omega to the written class and assert membership of the five explicit role values. The nested pair is projected by its known product type; the two subsequent roles are separate members. Omega means organs under nutritional consideration, not already successfully nourished parts.

**G04 Generic predication/capability clause.** MaterialBinder[n] FOR_ORGAN Role IS Pred Ref[n] THEN_HAS_CAPABILITY FacultyKind Ref[b] => bind local b to that written Role and local n:Material[c]; evaluate Ref[n] and Ref[b]; assert forall n: ApplyPred(P,n) => NaturalCapability(b,K,n,c). Ref[b] must equal the written role. The IS operator receives evaluated P and n, never the binder node. In N2 b is explicitly gall-bladder and P is A(gall-bladder).

**G05 General four-faculty argument.** THEREFORE NO_FURTHER_DOUBT RoleBinder[b] FacultySetBinder[F] ProperRelation RejectKind ForeignRelation AlterKind AttractKind [DEFINITE_MENTION RetainKind] => bind F to these four kind values and assert an assured generic schema over b in Omega and x:Material[c]: Proper(x,b,c)->GenericAttract(b,x,c); Foreign(x,b,c)->GenericReject(b,x,c); GenericAttract(b,x,c)->NaturalCapability(b,ALTER,x,c) AND NaturalCapability(b,RETAIN,x,c). The input Attract/Reject kinds name those generic relation schemata; this kind-to-generic-behavior interpretation is an explicit additional rule. Neither GenericAttract nor capability asserts an observed event. The source concluding/backward force is retained by the first two markers, not a newly reconstructed proof. The four constant kind expressions are evaluated first to bind F for the remaining unit continuation; only b and the schematic material variable are locally universally bound. F therefore does not escape a b-dependent binder. This evaluation/scope convention is explicit and costs an additional let/quantifier ordering rule. The generic slots are genuinely arguments: for input kinds K_R,K_L,K_A,K_T, use GenericBehavior(K_A,b,x,c), GenericBehavior(K_R,b,x,c), NaturalCapability(b,K_L,x,c) and NaturalCapability(b,K_T,x,c), and F={K_R,K_L,K_A,K_T}. The actual words supply REJECT,ALTER,ATTRACT,RETAIN respectively; the rule does not ignore them in favor of fixed output labels.

**G06 Predicate-first generic instance.** Pred MaterialBinder[e] FacultyKind Role INSTANCE_OF RoleClassRef => bind local e, assert membership of the role in the evaluated class, and forall e: ApplyPred(P,e)->NaturalCapability(role,kind,e,c). The binder is interpreted by this quantifying construction; there is no illegal ApplyPred(P,BinderSyntax). E2 supplies gall-bladder as both predicate recipient and written owner.

**G07 Description declaration and first witness.** QUALIFIED_EXAMPLE Mod [OriginDescriptionConstructor Role] QualifiedBinder[u,x] Ref[x] => evaluate base D0, bind its name D0 for the continuation; evaluate Mod(D0):Pred[c], bind name u to that value; existentially bind x:Material[c]; evaluate Ref[x] under the new binding and assert u(x) in the continuation. The output is an existential Proposition, not x. This construction scopes from its opener through unit end. The two binder names are lexical parameters of the QualifiedBinder syntax node, not denoted semantic values. Conjunction projection may unfold the explicit let-bindings D0 and u by substitution. That logical unfolding is not a semantic source-field inspection.

**G08 Analogy record declaration.** ANALOGY_FRAME Role MaterialRoleRelation MaterialRecipientRelation => bind record a=(targetRole,properRelation,pleasingRelation,D0). D0 is an explicit Ref to the description declared by G07 under the rule, not a new origin. This is a costly implicit descriptor-parameter convention in a written record constructor, disclosed separately. It does not merge the two relation types.

**G09 Written residual projection.** RESIDUAL_ORIGIN Role MaterialRef INFERRED => evaluate role a and x reference, then assert RESIDUE_FROM(a,c)(x). The derivation requires an in-scope assumption B(A(b))(RESIDUE_FROM(a,c))(x), already owned by a qualified-witness construction. Conjunction elimination supplies the conclusion on that x. It cannot use another witness or merely some origin fact. No arbitrary Pred value is inspected to recover a source.

**G10 Necessity clause.** Pair[Role,RoleClass] Cardinal NECESSARY_FOR_NUTRITION => take the explicitly bound F, assert its cardinality equals the written Cardinal, and bind Pi: forall b in the written RoleClass, ToBeNourished(b,c) requires possession of every K in F. The explicit Role is additionally a member/instance of that class. This states a necessary faculty condition, never that possession guarantees nourishment. F is a named reference parameter of this constructor and is not inferred from a numeral alone. More precisely Pi=forall b in Omega: NecessaryFor(AllFaculties(b,F,c),Nourishment(b,c)). This does not assert either actual nourishment or its converse.

**G11 Analogy completion.** AS_IN_THE_ANALOGY MaterialDescription TargetRole AnimalKind => use preceding a; require written TargetRole=a.targetRole; assert generic HighlyPleasing(f,AnimalKind,c) for f satisfying the written faeces description and record Analogy((faeces,AnimalKind,a.pleasingRelation),(D0,TargetRole,a.properRelation)). This does not assert PLEASING=PROPER, or food ingestion, or a measured ranking. The target existence is supplied by the qualified residue clauses, not manufactured by the analogy alone. The analogy target is the SOME-qualified schema on D0, not a claim that every D0 material is proper. The actual nonempty target is owned by S5. Source and target sides are tagged SideSpec values; inserting an AnimalKind into an anatomical-recipient relation is forbidden.

**G12 Second bare generic application.** MaterialBinder[k] Pred Ref[k] Pair[Role,FacultyKind] => bind local k; evaluate material reference under it; assert forall k: P(k)->NaturalCapability(pair.first,pair.second,k,c). No origin condition is added. The actual written case has P=A(SPLEEN) and separate role SPLEEN; no recipient is recovered from an extensional predicate.

**G13 Further qualified witness.** Mod DescriptionRef QualifiedBinder[g,x] Ref[x], or OTHERS Mod DescriptionRef QualifiedBinder[v,k] Ref[k] => evaluate Mod and D; bind the named qualified predicate to Mod(D), bind a new existential material under the specified name, then apply the qualified predicate to the evaluated reference. Scope extends to unit end. These are the same application/binding law; OTHERS and OTHER_QUALIFIED_MATERIAL mark contrasted discourse instances, not token inequality or disjoint classes. The plain binder an carries that OTHER discourse feature itself.

**G14 Next recipient topic.** OTHER_RECIPIENT DescriptionRef Role => declare the target pair (role,D) as a pending discourse topic, without asserting existence, motion or a suitability relation. The following qualified witness supplies the actual kidney claim. The marker adds no fresh physical portion.

**G15 Explicit analogy source.** ANALOGY_SOURCE Description ANALOGY AnimalKind MaterialRecipientRelation => bind source side s=(D,animal,Q), assert its generic pleasingness statement, and hold it as the written source argument for the subsequent analogy use. ANALOGY has the same binary relation meaning as in G16; this constructor explicitly supplies/records its first side before its second side is written. The qokal relation value is recorded along with the source side for later application; mentioning that relation here is not counted as a completed two-sided comparison. Source-side generic truth is separately stated by the construction.

**G16 Two target sides of the analogy.** Pair[Role,Pred] Pair[Role,Pred] ANALOGY Role => evaluate both target pairs and source organ a; use source side s from G15. For each target pair (b,Q), assert Q(x)->RESIDUE_FROM(a,c)(x) AND PROPER_FOR(x,b,c), and Analog(s,(Q,b,PROPER_FOR)). The x here is universally bound within that target-description statement. These assertions have premises from the actual qualified descriptions; the relation never calls an organ a dog or identifies pleasingness with propriety. Pair projections are explicit. ProperSide and PleasingSide are explicit tagged alternatives of SideSpec; Analogy:SideSpec x SideSpec->Proposition. The pairing types in G02 do not silently make a SideSpec; this target-side constructor does that work.

**G17 Written qualified-expression projection.** PROJECT_BASE MaterialRef [OriginDescriptionConstructor Role] [Mod DescriptionRef] => evaluate material x, base D, and displayed modified predicate Q=M(Dref); require Dref=D, and an in-scope Q(x) premise. Conjunction elimination for the explicitly written B/A modifier application yields D(x), same x. This is a proof rule referring to a written lambda-law instance and current assumption, not inspection of an arbitrary function's hidden source field. Repeating the modified expression does not introduce another witness.

**G18 Prior proof and named instances.** Role Role SHOWN_BEFORE PropositionRef Pair[Role,Role] => assert PreviouslyShown(Pi), and explicitly instantiate its relevant-organ scope at those four written roles. This is a backward proof reference, not a new demonstration. The part-membership premise for each role is openly supplied by this construction and charged; other named N1 roles remain in Pi's general scope.

**G19 Definite mention and copular predication.** DEFINITE_MENTION E denotes the same evaluated value as E, for exactly FacultyKind, FacultySet, and FacultySetPredicate. This is an explicit identity-like grammatical operator with no independent world constraint. IS supports the infix order Value IS Predicate as well as G04's prefix IS Predicate Value; both denote Apply(P,value). W6 uses FacultySet and its naming-metaphor predicate, while N2 uses Material and Pred[c]. No faculty/material cast occurs.

**G20 Source relation descriptions.** RESIDUE_FROM takes an evaluated AnatomicalRole and active c to a Pred[c]; HUMAN_FAECES is another primitive Pred[c] retaining human attribution. It is not a second RESIDUE_FROM input. HIGHLY_PLEASING_TO takes material, AnimalKind and c; PROPER_FOR takes material, AnatomicalRole and c. The common material domain is a declared analogy convention; the relation names remain distinct.

**G21 References and scoped bindings.** Literal Ref syntax evaluates the specified environment key. qotom/chey/qoekedy read x; ockhdar reads n; chedy reads k; roseer reads b; description refs read D0,g,v; role-class refs read Omega; lcheol reads F; qose?y reads Pi. No nearest-word search occurs. E3 binds x; S5 shadows x only inside its later existential continuation; W2 binds k and leaves x unchanged. S4's local universal k closes before S5. Binding constructions return Propositions/schemas, never their syntax nodes as values.

**G22 Unit-level existential continuation.** The outer generic body contains ordinary conjunctions and the explicitly extending existentials: exists xS[u(xS) AND prior continuation AND exists xG[g(xG) AND later continuation AND exists k[v(k) AND final continuation]]]. Reusing lexical key x implements ordinary shadowing; xS/xG here are explanatory alpha-renamings, not extra target names. Statements outside a witness's scope cannot cite it. No equality or inequality among xS,xG,k is asserted.

**G23 Boundaries and exclusions.** The exact clause spans in the draft are the chosen finite cuts, including S4 crossing .15/.16 and W4 crossing .21/.22. These cuts and N,E,S,W order are added syntax costs. Outside .1/.24 has no complete grammar or binder scope. Unknown alternate forms receive no values, normalization, or rescue productions.

## Application and projection traces

**BARE_GB_N2.** daiin=A_c(GALL_BLADDER); dair binds n:Material[c]; oraiin denotes GALL_BLADDER; sheo binds b to that role; ockhdar evaluates to n; roseer evaluates to b.

ApplyPred(A_c(GALL_BLADDER),n).

forall n: PROPER_FOR(n,GALL_BLADDER,c) => NaturalCapability(GALL_BLADDER,ATTRACT,n,c). Scope: N2 local; explicit Omega membership from N1; no origin condition.

**BARE_SPLEEN_S4.** dar=A_c(SPLEEN); ypshedy binds local k:Material[c]; chedy evaluates to k; or am oteey evaluates to Pair(SPLEEN,ATTRACT).

ApplyPred(A_c(SPLEEN),k).

forall k: PROPER_FOR(k,SPLEEN,c) => NaturalCapability(SPLEEN,ATTRACT,k,c). Scope: S4 only; not W2 k or a physical feeding episode.

**MOD_SPLEEN_E3.** qodar=B_c(A_c(SPLEEN)); qotedar qokar evaluates to D0=RESIDUE_FROM(LIVER,c); qotchd supplies binder syntax names u,x; qotom evaluates to the newly bound x.

u=B_c(A_c(SPLEEN))(D0); u(x).

exists xS: D0(xS) AND PROPER_FOR(xS,SPLEEN,c) AND remaining_continuation. Scope: E3 through unit end; later shadowing does not equate witnesses.

**MOD_GB_S5.** qodaiin=B_c(A_c(GALL_BLADDER)); odain evaluates to existing D0; an supplies binder syntax names g,x; chey evaluates to newly bound x.

g=B_c(A_c(GALL_BLADDER))(D0); g(x).

exists xG: D0(xG) AND PROPER_FOR(xG,GALL_BLADDER,c) AND remaining_continuation. Scope: S5 through unit end; outer E3 x is shadowed by the explicit new binder.

**MOD_KIDNEYS_W2.** qodain=B_c(A_c(KIDNEYS)); chckhy evaluates to D0; ykeedy supplies binder syntax names v,k; chedy evaluates to newly bound k.

v=B_c(A_c(KIDNEYS))(D0); v(k).

exists k: D0(k) AND PROPER_FOR(k,KIDNEYS,c) AND remaining_continuation. Scope: W2 through unit end; does not overwrite xG.

**PROJECTION_S1.** E3 supplies u(xS); u=B_c(A_c(SPLEEN))(D0), D0=RESIDUE_FROM(LIVER,c); chey evaluates to xS here; S5 binder has not begun; shedor denotes LIVER.

unfold u(xS); eliminate conjunction to D0(xS).

RESIDUE_FROM(LIVER,c)(xS). Scope: same xS, no second existential or recipient-as-source substitution.

**PROJECTION_W4.** S5 supplies g(xG); qoekedy evaluates to xG; W2 introduced k only; dody shedy evaluates to RESIDUE_FROM(LIVER,c)=D0; qodaiin los evaluates to B_c(A_c(GALL_BLADDER))(D0)=g.

the displayed qualified predicate has the in-scope g(xG) premise; eliminate conjunction.

RESIDUE_FROM(LIVER,c)(xG). Scope: same xG, no product; actual repeated modifier application, not new recipient input.

## Scope/source assumptions

**A01.** One generic physiology context c and N,E,S,W synopsis order; common Material[c] includes liver residues and human faeces without identity or a single patient. Cost: one context architecture and one presentation order.

**A02.** Omega is an explicit relevant-organ class; N1 asserts gall-bladder/liver/veins/arteries/heart membership, W5 explicitly includes spleen/kidneys. Cost: generic class plus seven named membership instances, two named-list constructions.

**A03.** NaturalCapability and GenericAttract/GenericReject are distinct primitives. The generic faculty program relates proper/foreign to behaviors and attracted material to two powers. Cost: one kind-to-behavior interpretation schema and one11-token program construction.

**A04.** The complete argument is rearranged. The explicit spleen bare clause occurs S4; dog comparison and prior-proof material are repeated. Cost: free whole-unit narrative allocation; no native paragraph/figure semantics.

**A05.** Qualified binders introduce both a description value and material name in an existential continuation. S5 shadows x; W2 binds k. Cost: three two-name binder instances, one continuation law, one ordinary shadowing convention.

**A06.** D0, F, Pi and the analogy records are named products of explicit constructions. Implicit reference parameters in G08/G10 are written grammar conventions, not extra target words. Cost: two implicit named-parameter conventions plus record/scope rules.

**A07.** Concluding assurance, prior proof and handmaid naming are asserted as source discourse. No proof is reconstructed or modern physiological truth certified. Cost: assurance/consequence, prior-proof and figurative-predication primitives.

**A08.** HIGHLY_PLEASING is retained as one opaque emphatic relation; HUMAN_FAECES retains human attribution. Cost: multifeature values itemized, not a measured ranking or actual ingestion.

**A09.** Some/others marks different recipient-relative discourse cases, without disjointness, exhaustion or forced token equality/inequality. Cost: one non-partitioning contrast convention.

**A10.** Two written origin projections are redundancies added to demonstrate same-witness preservation. The source does not demand their position or wording. Cost: two projection constructions and extra target-content repetition.

**A11.** The three residue descriptions may be extensionally equal or overlapping. The source does not prove distinct suitability sets. Cost: no exclusion table, no unique solution or numerical weights.

**A12.** Definite mention is identity-like over exactly three declared types; IS has two surface orders and two argument sorts. Cost: a low-content grammatical whole value, restricted polymorphism, two predication productions.

## Literal alternate consequences

**IT2a.**

- S.16 qodain is KIDNEYS under the fixed contract, not GALL_BLADDER. Its an binder consequently stores g=B(A(KIDNEYS))(D0) and x satisfying that kidney-qualified description. This is a real changed argument, not an alias.
- W4 later explicitly displays qodaiin los, the gall-bladder modifier on D0. The frozen G17 requires that displayed g_GB(x) premise; S5 in IT supplies only the kidney-qualified premise. The source does not entail kidney-proper => gall-bladder-proper. This is an unavailable premise, not proof the material is unsuitable for gall-bladder.
- The first W3 pair starts ar aiin ckhedy instead of or aiin ckhed[a:y]; ar denotes SPLEEN and cannot serve as PAIR. Unknown ckhedy is not repaired.
- aiinog remains one opaque whole; no split into aiin og.

Unassigned literal occurrences: 11. Types: `aiinog`, `ch?s`, `chokcod`, `ckhedy`, `csedy`, `ockhdor`, `olkor`, `oloeorain`, `qoseey`, `qtchedy`, `sosees`.

**RF1b.**

- qo@152;ar and qo@152;ain remain unassigned marked whole forms, not licensed unmarked compounds.
- W3 begins ar aiin ckhe@152;y; the first PAIR constructor is missing under the frozen grammar.
- qose eey remains two unknown groups, not the qose?y prior-proof reference.

Unassigned literal occurrences: 18. Types: `@221;laiin`, `ch@152;s`, `chot{co}g`, `ckhe@152;y`, `eey`, `ol@176;ar`, `otche@152;y`, `ote@152;y`, `qo@152;ain`, `qo@152;ar`, `qoke@152;y`, `qose`, `she@152;y`, `sosees`, `yfshe@152;y`, `{ch'}edy`, `{ch'}eos`.

**ZL3b.**

- All85 types have assigned values; all108 groups belong to a complete proposed clause/field. This is a manual authoring result, not an independent well-typedness pass.
- Marked literal words remain opaque exact lexical assignments, including chz[s:r], chok{co}m and ckhed[a:y]. No pixel or spelling choice is established.

Unassigned literal occurrences: 0. Types: .

## Every assigned outside occurrence

No complete outside clause is supplied. All149 outside raw rows, including unknown neighbors and separators, remain in the JSON. No selected c or witness scope extends here.

### ZL3b

| Exact source group | Form | Value |
|---|---|---|
| ZL3b\|f85r2.1\|G002 | otedy | GALL_BLADDER |
| ZL3b\|f85r2.1\|G004 | ar | SPLEEN |
| ZL3b\|f85r2.1\|G015 | otchedy | REJECT |
| ZL3b\|f85r2.1\|G019 | otchedy | REJECT |
| ZL3b\|f85r2.1\|G023 | shedaiin | PROPER_FOR |
| ZL3b\|f85r2.1\|G024 | olaiin | HUMAN_FAECES |
| ZL3b\|f85r2.1\|G026 | daiin | A_c(GALL_BLADDER) |
| ZL3b\|f85r2.1\|G027 | ol | DEFINITE_MENTION |
| ZL3b\|f85r2.1\|G030 | aiin | GALL_BLADDER |
| ZL3b\|f85r2.1\|G032 | dar | A_c(SPLEEN) |
| ZL3b\|f85r2.24\|G001 | okees | ANALOGY_SOURCE |
| ZL3b\|f85r2.24\|G008 | ar | SPLEEN |
| ZL3b\|f85r2.24\|G009 | or | PAIR |
| ZL3b\|f85r2.24\|G012 | ar | SPLEEN |

### IT2a

| Exact source group | Form | Value |
|---|---|---|
| IT2a\|f85r2.1\|G002 | otedy | GALL_BLADDER |
| IT2a\|f85r2.1\|G004 | ar | SPLEEN |
| IT2a\|f85r2.1\|G007 | otedy | GALL_BLADDER |
| IT2a\|f85r2.1\|G015 | otchedy | REJECT |
| IT2a\|f85r2.1\|G019 | otchedy | REJECT |
| IT2a\|f85r2.1\|G023 | shedaiin | PROPER_FOR |
| IT2a\|f85r2.1\|G024 | olaiin | HUMAN_FAECES |
| IT2a\|f85r2.1\|G026 | daiin | A_c(GALL_BLADDER) |
| IT2a\|f85r2.1\|G027 | ol | DEFINITE_MENTION |
| IT2a\|f85r2.1\|G030 | aiin | GALL_BLADDER |
| IT2a\|f85r2.1\|G032 | dar | A_c(SPLEEN) |
| IT2a\|f85r2.24\|G001 | okees | ANALOGY_SOURCE |
| IT2a\|f85r2.24\|G008 | ar | SPLEEN |
| IT2a\|f85r2.24\|G009 | or | PAIR |
| IT2a\|f85r2.24\|G011 | ol | DEFINITE_MENTION |
| IT2a\|f85r2.24\|G013 | ar | SPLEEN |
| IT2a\|f85r2.24\|G014 | ar | SPLEEN |
| IT2a\|f85r2.24\|G015 | am | SPLEEN |

### RF1b

| Exact source group | Form | Value |
|---|---|---|
| RF1b\|f85r2.1\|G002 | otedy | GALL_BLADDER |
| RF1b\|f85r2.1\|G004 | ar | SPLEEN |
| RF1b\|f85r2.1\|G019 | otchedy | REJECT |
| RF1b\|f85r2.1\|G023 | shedaiin | PROPER_FOR |
| RF1b\|f85r2.1\|G024 | olaiin | HUMAN_FAECES |
| RF1b\|f85r2.1\|G026 | daiin | A_c(GALL_BLADDER) |
| RF1b\|f85r2.1\|G027 | ol | DEFINITE_MENTION |
| RF1b\|f85r2.1\|G032 | dar | A_c(SPLEEN) |
| RF1b\|f85r2.24\|G001 | okees | ANALOGY_SOURCE |
| RF1b\|f85r2.24\|G009 | ar | SPLEEN |
| RF1b\|f85r2.24\|G010 | or | PAIR |
| RF1b\|f85r2.24\|G012 | ol | DEFINITE_MENTION |
| RF1b\|f85r2.24\|G014 | ar | SPLEEN |
| RF1b\|f85r2.24\|G015 | ar | SPLEEN |
| RF1b\|f85r2.24\|G016 | am | SPLEEN |

## Charged synonyms

- `ar`, `am` = SPLEEN (AnatomicalRole).
- `aiin`, `oraiin`, `otedy` = GALL_BLADDER (AnatomicalRole).
- `ain`, `og` = KIDNEYS (AnatomicalRole).
- `opchdy`, `qokar`, `shedor`, `shedy` = LIVER (AnatomicalRole).
- `shoral`, `oteey`, `tchedy` = ATTRACT (FacultyKind).
- `fcheey`, `shedaiin` = PROPER_FOR (MaterialRoleRelation[c]).
- `chckhey`, `tedy` = THE_RELEVANT_ORGAN_CLASS (Ref[Omega:RoleClass[c]]).
- `qotedar`, `dody` = RESIDUE_FROM (AnatomicalRole->Pred[c]).
- `qotom`, `chey`, `qoekedy` = MATERIAL_x (Ref[x:Material[c]]).
- `chok{co}m`, `sary` = HIGHLY_PLEASING_TO (MaterialRecipientRelation[c]).
- `chz[s:r]`, `olaiin` = HUMAN_FAECES (Pred[c]).
- `arody`, `chdy` = DOGS (AnimalKind).
- `odain`, `oldar`, `chckhy`, `los` = THE_BASE_DESCRIPTION (Ref[D0:Pred[c]]).

Binder keys n/e or local k have different scoping roles; printing GENERIC_MATERIAL_CASE twice does not make their binding declarations one token. Reference and binder words with related names are not substituted for one another.

## Multi-feature whole values

Declared accounting: 139 payload occurrences across77 new opaque whole values; 53 have more than one listed feature. This is not a new target segmentation or minimal semantic alphabet.

| Whole | Charged payloads |
|---|---|
| sain | GENERIC, BODY_CONTEXT, BIND_c |
| olfar | ORGANS, NUTRITIONAL_CONSIDERATION |
| ary | MEMBERSHIP_ASSERTION, BIND_Omega |
| dair | GENERIC_CASE, BIND_n |
| sheo | ORGAN_SCOPE, BIND_b |
| ockhdar | REFERENCE, n |
| olkar | CONDITIONAL_CONSEQUENT, NATURAL_CAPABILITY |
| roseer | REFERENCE, b |
| pchedeey | CONCLUDING, THEREFORE |
| olkey | NO_FURTHER, DOUBT |
| qokedy | EVERY_RELEVANT_ORGAN, BIND_b |
| sheos | NATURAL_FACULTIES, SET, BIND_F |
| fcheey | PROPER, RECIPIENT_RELATION |
| chotey | FOREIGN, RECIPIENT_RELATION |
| ol | DEFINITE, MENTION |
| qotaiin | GENERIC_CASE, BIND_e |
| qotchdy | INSTANCE, MEMBERSHIP |
| chckhey | REFERENCE, Omega |
| ytchedy | QUALIFIED_EXAMPLE, BIND_D0 |
| qotedar | RESIDUE, SOURCE_RELATION |
| qotchd | SOME, BIND_u_DESCRIPTION, BIND_x_MATERIAL |
| qotom | REFERENCE, x |
| soiis | ANALOGY, BIND_a |
| shedaiin | PROPER, RECIPIENT_RELATION |
| chok{co}m | HIGH_DEGREE, PLEASING, RECIPIENT_RELATION |
| otchs | RESIDUAL, ORIGIN_ASSERTION |
| chey | REFERENCE, x |
| sorain | INFERENCE, PROJECTION |
| tedy | REFERENCE, Omega |
| chy | NECESSITY, NUTRITION, BIND_Pi |
| ytedar | ANALOGY, COMPLETION |
| chz[s:r] | HUMAN_ATTRIBUTION, FAECES |
| ypshedy | GENERIC_CAPABILITY_CASE, BIND_k |
| chedy | REFERENCE, k |
| odain | REFERENCE, D0 |
| an | OTHERS, BIND_g_DESCRIPTION, BIND_x_MATERIAL |
| orar | OTHER_RECIPIENT, TOPIC_DECLARATION |
| oldar | REFERENCE, D0 |
| okees | ANALOGY_SOURCE, BIND_s |
| olaiin | HUMAN_ATTRIBUTION, FAECES |
| sary | HIGH_DEGREE, PLEASING, RECIPIENT_RELATION |
| chckhy | REFERENCE, D0 |
| ykeedy | QUALIFIED_MATERIAL, BIND_v_DESCRIPTION, BIND_k_MATERIAL |
| ckhed[a:y] | REFERENCE, g |
| olchey | REFERENCE, v |
| qokeody | PROJECTION, BASE_DESCRIPTION |
| qoekedy | REFERENCE, x |
| dody | RESIDUE, SOURCE_RELATION |
| los | REFERENCE, D0 |
| qokshey | SHOWN, BEFORE |
| qose?y | REFERENCE, Pi |
| lcheol | REFERENCE, F |
| sheoly | CALLED, HANDMAIDS, OF_NUTRITION |

## Final author self-review, before freeze

- Every selected ZL group has exactly one clause owner and every ZL type exactly one lexical entry. This is allocation, not an independently replayed semantic pass.
- Both bare inputs have actual evaluated material arguments inside generic conditionals. Explicit gall-bladder class membership is owned; no bare kidney-use claim is made.
- All three modifier applications use the identical A/B law, the same explicit D0, and evaluated witness references. The first-contract recipient assignment and cuts are unchanged.
- S1 projects the E3 spleen witness before shadowing; W4 projects the S5 gall-bladder witness after a distinct k binder. The names and scopes are stated rather than inferred from word proximity.
- G08 and G10 have implicit named parameters D0 and F under explicit written grammar conventions. They remain extra costs; the corresponding words are not pretended present as extra tokens.
- G05 is a large one-off faculty-program construction. Its arguments are genuine input values, but it is not independently supported by repeated target programs.
- The typed analogy SideSpec constructors preserve relation and recipient-sort differences. Their records and repeated source/target clauses are freely authored machinery.
- Only one origin description is actually varied through the source cases. A constant-on-D modifier rival could reproduce the same outputs at this one D0; preservation for arbitrary unseen D is a chosen law, not independently tested.
- The opaque vocabulary, aliases and identity-like definite mention dominate the packet. No whole-reading likelihood, compression, significance or meaning confirmation follows.
- IT/RF and outside contexts remain incomplete. A changed IT kidney predicate alone is not a logical negation of gall-bladder suitability.

## Explicit type and scope table

- **AnatomicalRole**: Generic anatomical role value, not a physical organ token; SPLEEN,GALL_BLADDER,KIDNEYS,LIVER,VEINS,ARTERIES,HEART are distinct named role constants.
- **FacultyKind**: Named kind ATTRACT,REJECT,ALTER,RETAIN; not a predicate or an occurrence/event.
- **FacultySet**: FiniteSet[FacultyKind].
- **RoleClass[c]**: AnatomicalRole -> Proposition in c.
- **Material[c]**: Generic logical material domain in the declared context.
- **Pred[c]**: Material[c] -> Proposition, also the type of material descriptions.
- **Mod[c]**: Pred[c] -> Pred[c].
- **MaterialRoleRelation[c]**: (Material[c],AnatomicalRole) -> Proposition.
- **MaterialRecipientRelation[c]**: (Material[c],AnimalKind) -> Proposition for this packet; no automatic Role/Animal conversion.
- **SideSpec**: Tagged union PleasingSide(description,AnimalKind,pleasingRelation,GENERIC) | ProperSide(description,AnatomicalRole,properRelation,SOME).
- **AnalogyRelation**: (SideSpec,SideSpec) -> Proposition.
- **Ref[k:T]**: Syntax expression whose evaluated value is Gamma[k]:T; the handle itself is not T.
- **BinderSyntax**: A special-form syntax parameter introducing the named type/value variables under an explicit quantifier/declaration rule; no ordinary semantic value when used alone as an argument.
- **QualifiedBinderSyntax[d:Pred,x:Material]**: Two-name syntax parameter; the construction binds d to evaluated M(D0), then existential x under the described continuation.
- **PredicationOperator**: Apply(P:alpha->Proposition,v:alpha), with alpha restricted to Material[c] or FacultySet; two declared surface orders.
- **MentionOperator**: Identity_T for T in {FacultyKind,FacultySet,FacultySet->Proposition}; no predicate/faculty conversion.
- **Projection proof context**: Ordinary scoped assumptions plus explicit let-definitions. Conjunction elimination and substitution operate on written formulas, not a source field obtained from an arbitrary function value.

| Binding | Written introducer | Scope |
|---|---|---|
| c,Omega | N1 sain/ary | N1 through W6 |
| n,b | N2 dair/sheo | N2 only; b=GALL_BLADDER |
| F | E1 sheos and four written kind inputs | E1 through W6; constructed before local forall b |
| b,z | E1 qokedy and generic faculty-program rule | E1 only; z is the rule-bound schematic material |
| e | E2 qotaiin | E2 only |
| D0,u,xS (lexical key x) | E3 ytchedy/qotchd | E3 through W6; x name shadowed beginning S5 |
| a | E4 soiis | E4 through W6 |
| Pi | S2 chy necessity declaration | S2 through W6 |
| kS (lexical key k) | S4 ypshedy | S4 only |
| g,xG (lexical key x) | S5 an | S5 through W6, nested inside E3 |
| s | W1 okees | W1 through W6 |
| v,kW (lexical key k) | W2 ykeedy | W2 through W6, nested inside S5 |

Every selected ZL Ref occurrence also carries its evaluated binding in the JSON. No reference binding is copied into an unparsed alternate or outside construction.
