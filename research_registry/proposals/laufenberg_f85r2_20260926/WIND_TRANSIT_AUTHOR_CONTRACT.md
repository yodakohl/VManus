# IDEA000582 exploratory first contract

This freezes a complete local candidate for the entire west argument, not a whole-page reading or a translation claim. The source roster was frozen before these assignments. Actual start: 2026-09-27 07:20:26 UTC. First deadline: 07:39:42 UTC. No old lexicon or grammar is imported.

Complete ZL .18-.23 is the local first argument. Chosen during exploratory work for actual repeated aiin applications, not because W depicts west. No other image/block assignment. Full473 target and all22 source duties retained.

Only the local .18-.23 order is here owned. Cross-block page reading order is not established and is not used to certify earlier/later global reference availability. Whole continuation must declare and pay an explicit page-order assumption before parsing outside this local unit; it cannot change any register or value. This is an acknowledged remaining input, not a claim that all global references are in scope.

## Written local account

**W1 — f85r2.18:1-5.** Let w be the third, west wind, from the direction of sunset.
`INTRODUCE_WIND(PAIR_INFIX(WEST_THIRD,SETTING_DIRECTION(SUN)))`

**W2 — f85r2.19:1-2.** That wind has two companions.
`HAS_TWO_COMPANIONS(WIND_REF)`

**W3 — f85r2.19:3-5.** It is cold and moist by nature.
`NATURAL_QUALITIES(WIND_REF,COLD_AND_MOIST)`

**W4 — f85r2.20:1-3.** Introduce land l and explicitly state its warmth; commit this property as witness WL in D_l.
`ASSERT_MARK(WARM(INTRODUCE_LAND_HOLDER))`

**W5 — f85r2.20:4-8.** The wind traverses that explicitly warm land. The traversal contains l and the same WL assertion.
`ASSERT_MARK(TRAVERSES_PAIR(PAIR_INFIX(WIND_REF,LAND_DESCRIPTION_REF)))`

**W6 — f85r2.21:1-5, f85r2.22:1-8.** Its traversal of that warm land explains that the same wind is always warm here among us. Only the qualified local warmth is the result.
`EXPLAINS(TRAVERSES_TWO_ARGUMENTS(WIND_REF,LAND_DESCRIPTION_REF),FOR_PASSAGE(PAIR_PREFIX(WIND_REF,LAND_DESCRIPTION_REF),ALWAYS_LOCAL(HERE_AMONG_US(ASSERT_MARK(WARM(WIND_HOLDER_REF))))))`

**W7 — f85r2.23:1-5.** That wind does not harm the explicitly introduced local human group. This is a separate statement.
`DOES_NOT_HARM(RESOLVE_ENTITY_REF(WIND_REF),RESOLVE_ENTITY_REF(US_REF))`

The sequence consumes every one of the 36 ZL groups in .18–23. W6 deliberately crosses the .21/.22 line boundary. No line end supplies a causal, anaphoric or propositional operator. The sun-setting direction and third designation are explicitly paid name/origin contents. The two-companion expression contains three paid lexical payloads, not three separately observed target parts.

## Interfaces, binding and scope

Explicit allocation/replacement only at okees, ckhed[a:y], qose?y; never at a line/paragraph boundary. Reference terminals do not introduce or repair owners.

Wind and land are separate typed roles. No identity or disequality is asserted between traversed land and local place. No physical episode is introduced by a WindKind generic assertion.

A HolderRef is a different declared interface from EntityRef. `og` reads the holder reference explicitly written by the wind introduction; `ckhed[a:y]` introduces and returns a land holder. The same `aiin` predicate accepts both. There is no arbitrary EntityRef-to-HolderRef coercion. `ol` explicitly dereferences the two EntityRef operands of no-harm.

The descriptive-land reference carries the exact previously asserted warmth witness. On the first land introduction its description is empty; only the complete W4 assertion populates it. Both traversal constructors snapshot that same descriptor. EXPLAINS checks the supplied wind/land pair against its causal antecedent. No inferred land warmth, default referent, inverse predicate, extra event or physics is supplied. This description-store convention is an additional grammar cost.

`or` is a pure assertion marker while nested. Commit happens only when the outermost statement has been fully composed. Thus W6 does not separately assert unqualified wind warmth before HERE_AMONG_US and ALWAYS_LOCAL have applied. Natural cold/moist and local general warmth remain differently qualified. HERE_AMONG_US explicitly introduces the human group and local place; its combined deixis/ownership/qualification payload is counted. No-harm consumes that same group in the next independent statement.

## Finite dictionary

| Literal whole form | Fixed typed value | Payload cost |
|---|---|---:|
| `okees` | INTRODUCE_WIND: NameOriginSpec -> Declaration | 4 |
| `olaiin` | WEST_THIRD: NameDesignation | 2 |
| `qokal` | PAIR_INFIX: A B -> Pair[A,B] | 1 |
| `chdy` | SETTING_DIRECTION: Sun -> Direction | 1 |
| `sary` | SUN: Sun | 1 |
| `qokshedy` | WIND_REF: EntityRef[WindKind] | 1 |
| `qodain` | HAS_TWO_COMPANIONS: EntityRef[WindKind] -> Proposition | 3 |
| `chckhy` | NATURAL_QUALITIES: EntityRef[WindKind] QualityBundle -> Proposition | 2 |
| `ykeedy` | WIND_REF: EntityRef[WindKind] | 1 |
| `chedy` | COLD_AND_MOIST: QualityBundle | 2 |
| `or` | ASSERT_MARK: Assertable -> same sort | 1 |
| `aiin` | WARM: HolderRef -> PropertyClause | 1 |
| `ckhed[a:y]` | INTRODUCE_LAND_HOLDER: HolderRef | 4 |
| `ain` | TRAVERSES_PAIR: Pair[EntityRef[WindKind],DescriptionRef[LandRegion]] -> TraversalClause | 1 |
| `olchey` | WIND_REF: EntityRef[WindKind] | 1 |
| `shedy` | LAND_DESCRIPTION_REF: DescriptionRef[LandRegion] | 1 |
| `qokeody` | EXPLAINS: TraversalClause PassageFramedPropertyClause -> Proposition | 3 |
| `qoekedy` | TRAVERSES_TWO_ARGUMENTS: EntityRef[WindKind] DescriptionRef[LandRegion] -> TraversalClause | 1 |
| `dody` | WIND_REF: EntityRef[WindKind] | 1 |
| `qodaiin` | FOR_PASSAGE: Pair[EntityRef[WindKind],DescriptionRef[LandRegion]] PropertyClause -> PassageFramedPropertyClause | 1 |
| `los` | PAIR_PREFIX: A B -> Pair[A,B] | 1 |
| `ar` | WIND_REF: EntityRef[WindKind] | 1 |
| `qokshey` | ALWAYS_LOCAL: LocalPropertyClause -> PropertyClause | 1 |
| `qose?y` | HERE_AMONG_US: PropertyClause -> LocalPropertyClause | 5 |
| `og` | WIND_HOLDER_REF: HolderRef | 1 |
| `ol` | RESOLVE_ENTITY_REF: EntityRef[T] -> T | 1 |
| `lcheol` | WIND_REF: EntityRef[WindKind] | 1 |
| `chol` | DOES_NOT_HARM: WindKind HumanGroup -> Proposition | 2 |
| `sheoly` | US_REF: EntityRef[HumanGroup] | 1 |

Every entry definition and every occurrence ID appears in the JSON. All 473 original rows retain all original fields. A literal binding is distinct from a completed parse. Marked forms, reader spacing and unknown forms are unchanged.

## Finite constructions

**G01: `Program ::= Statement+`.** Statement is Declaration or Assertable; Assertable is Proposition, PropertyClause or TraversalClause, each with its explicit proposition projection. Statements are contiguous complete typed expressions. Completion closes a statement; no token is skipped or converted to punctuation. A line end is not a boundary.

**G02: `okees NameOriginSpec`.** NameOriginSpec must be Pair[NameDesignation,Direction]. IntroduceWind asserts WindKind(w), designated name/ordinal and FromDirection(w,d). It writes W/H_w only after consuming both written fields.

**G03: `chdy Sun`.** DirectionOfSetting(suppliedSun).

**G04: `A qokal B`.** Typed product, with its two contiguous operands. It binds before the enclosing constructor consumes its expected Pair argument.

**G05: `EntityRef qodain`.** Postfix HasTwoCompanions of that exact reference.

**G06: `chckhy EntityRef QualityBundle`.** NaturalRespect(qualities,resolvedOwner); no unqualified warmth/cold slot and no inheritance to companions.

**G07: `or X`.** X must be Assertable (Proposition, PropertyClause or TraversalClause). Typed assertion marking preserves that sort. Pure while nested; top-level completed assertion commits the explicit proposition projection of X. Nested or remains redundant marking of the same proposition and does not create a new referent.

**G08: `aiin HolderRef`.** Warm(ResolveHolder(r)) creates a PropertyClause with explicit subject and Plain respect. Resolving HolderRef is part of this one declared interface, not a cast from any other type.

**G09: `ckhed[a:y]`.** Evaluate a written Land introduction and return its HolderRef. Its effect is explicit and only occurs where this literal token is present.

**G10: `ain Pair[WindRef,LandDescriptionRef]`.** Create TraverseWithDescription(w,l,D); D is a snapshot of explicit property witnesses of l.

**G11: `qokeody TraversalClause PassageFramedPropertyClause`.** Check identical owner pair, then form A AND R AND Because(A,R). Because does not include a subsequent top-level proposition. No extrapolation to other routes.

**G12: `qoekedy WindRef LandDescriptionRef`.** The same TraverseWithDescription as G10, through an explicitly paid two-argument interface.

**G13: `qodaiin Pair[WindRef,LandDescriptionRef] PropertyClause`.** Check PropertyClause.subject == pair.wind; retain both pair owners and the supplied property, without adding an event or time.

**G14: `los A B`.** Prefix typed product; a second paid surface license for G04 product.

**G15: `qokshey LocalPropertyClause`.** For all relevant presentations of this supplied wind kind at the supplied place, its supplied property holds there. The source permits this prospective generic interpretation, not empirical verification.

**G16: `qose?y PropertyClause`.** Allocate explicit deictic U/P and qualify the supplied property Local(P). Bindings persist into following statements until another explicit HERE_AMONG_US. No unspoken us/here owner.

**G17: `ol EntityRef`.** Resolve the written reference to its value. Undefined references stay failures, never inferred from source or layout.

**G18: `WindValue chol HumanGroupValue`.** Negative HARM of the two explicitly resolved operands.

**G19: `Reference terminals`.** W/H_w, L/D_l and U/P are separate registers with the binder effects above. Each read captures the current value; later introductions do not rewrite earlier clauses. All references fail if their corresponding register is absent.

**G20: `Commit and description ownership`.** Commit the proposition projection of a completed top-level Assertable only after all written enclosing modifiers. For a PropertyClause, if its subject owns an explicitly introduced description register, append that exact qualified property witness idempotently. Description snapshots contain only these previously committed properties. No inverse of a predicate, inferred property or automatic co-reference is licensed.

**G21: `Generic qualification and causal witness identity`.** Natural, Plain and Local properties retain their qualifier fields. Warm of land and Warm of wind use one predicate but different holders. Clause/witness identities are immutable; passing a description carries the same recorded assertion, not a new material or episode.

**G22: `Application/closure`.** Prefix constructors consume exactly their declared contiguous argument expressions. G04 and G18 are the only infix productions, G05 the only postfix production. No unrestricted unknown higher-order operator may swallow malformed first-contract strings. Additional ordinary terminals may later inhabit these sorts/signatures, but may not introduce new state effects, casts or production rules.

## Cost and limits

29 whole-form assignments; zero component values and zero cuts; 47 semantic payloads as a lower bound; 22 explicit productions/control conventions. The six EntityRef-to-W terminals pay five aliases beyond the first. Product has two surface orders and traversal has paired/two-argument surface interfaces: both are paid alternatives. The separate wind HolderRef is another interface assignment. This is expensive exploratory content construction; it is not a newly found morphological family or proof of compression.

Two actual differently typed holder applications are W4 land warmth and W6 wind warmth. W5/W6 reuse the same explicit wind/land/description inputs. The causal relation occurs once. No portable empirical transit law follows. All non-west source duties, source ambiguities and all global occurrence consequences remain obligations; none is declared satisfied by this local reading. Cross-block order is unresolved and cannot be silently used to hide unbound earlier references.

The strongest faithful rival uses ordinary separately qualified predicates and explicit because, with the same written owners. It can preserve every source claim; no unique architecture follows. A mere source list misses causality, and making no-harm the result changes the complement. Unqualified coexistence of cold/warm is not itself a contradiction without a separately justified exclusivity rule.

Source roster hashes: MD `ae5b630b3835fae0fa765e964955f6592488c0adf902327feba8017407b5c378`; JSON `bd98cd0c2966076760d0536f80313a75f7f78518eec4f05a7de406e31b5fdf4b`. JSON receipts contain unchanged input hashes. First-contract files are frozen together; stop for independent review. The JSON freeze timestamp records the actual final write.
