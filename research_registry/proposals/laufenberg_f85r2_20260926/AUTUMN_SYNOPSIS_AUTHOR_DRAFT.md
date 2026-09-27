# IDEA000589: partial whole-authoring candidate

**This is not a complete f85r2 reading.** Four manually written source-clause islands account for33ZL groups, with all473 literal consequences retained. The first annulus and the rest of the page remain incomplete. No frozen rule was repaired after a result; tentative revisions before this first freeze are disclosed below.

Actual start08:06:56UTC; author ceiling08:58UTC. Numeric .1–.24 order is a paid assumption. ZL is the display channel, not a canonical transcription. Original586,582 and583 remain unchanged.

## Concrete conditional reading

**C1:** `sain or or aiin opchdy qotor sheedy shodaiin olfar ary`
The melancholic profile and autumn match in the written cold/dry respects. Autumn is explicitly modified as cold and dry; the comparison ascribes these respects to both supplied owners.
`sain(or(or(aiin,opchdy),qotor), sheedy, shodaiin(olfar,ary))`
Formula: `CompareIn(M, ApplyDry(ApplyCold(A)), {COLD,DRY})`

**C2:** `pchedeey olkey qokedy sheos fcheey otchedy chotey qocthey oteey ol oloqorain`
Autumn coldness is explained by the sun’s course away from us into winter signs at autumn-time. The generic course/tendency is not a completed winter event.
`pchedeey(olkey(qokedy), COURSE(sheos,fcheey,otchedy(chotey),qocthey(oteey),ol(oloqorain)))`
Formula: `Because(Course(Sun,awayFrom(US),into(WINTER_SIGNS),at(TimeOf(A))), Cold(A))`

**C3:** `daiin qotaiin tchedy otedy qotchdy chckhey ytchedy qodar`
Autumn dryness is explained by dryness of summer in a time preceding that autumn-time. The earlier qualifier belongs to the summer ground, and the result still belongs to A.
`daiin qotaiin tchedy(otedy(qotchdy(chckhey)),ytchedy(qodar))`
Formula: `Because(At(Before(TimeOf(A)),Dry(S)),Dry(A))`

**C4:** `qotedar qokar qotchd qotom`
The summer time precedes the autumn time. This repeats the temporal relation explicitly; it supplies no measured duration.
`qotedar(qokar,qotchd(qotom))`
Formula: `Precedes(TimeOf(S),TimeOf(A))`

The source says summer **dryness**, not heat. C1 precedes C2/C3. The course is away from an explicitly supplied us, into winter signs, at autumn-time; it is not a completed winter event. The same A supplies the results in both explanations, while S owns the earlier dryness. All of this is hypothetical target authorship, not an independently recovered translation.

## Actual part construction

`ar = S`, `aiin = A`, `ain = M`; `d` attaches DRY without changing owner; `qo` quotes the resulting condition as reason material. The five declared cuts are `d|ar`, `d|aiin`, `qo|d|ar`, `qo|d|aiin`, `qo|d|ain`. No other character occurrence is automatically segmented.

C3 actually computes d on A in literal daiin and d on S inside literal qodar. The reason wrapper preserves S; separate written words supply assertion status and the earlier-time frame. This is actual differently owned use of one dry operation. The third compound qodain is fully assigned but has no completed clause use. Neither literal dar outside these clauses nor either outside qodaiin occurrence is excused. No claim of broad morphology or portable confirmation follows.

## Finite dictionary

|Literal|Fixed value/type|Payload cost|
|---|---|---:|
|`ar`|SUMMER: EntityDescription[Season]|1|
|`aiin`|AUTUMN: EntityDescription[Season]|1|
|`ain`|MELANCHOLIC_PROFILE: EntityDescription[Profile]|1|
|`dar`|DRY_DESCRIPTION(S): EntityDescription[Season]|0|
|`daiin`|DRY_DESCRIPTION(A): EntityDescription[Season]|0|
|`qodar`|QUOTED_GROUND(DRY_DESCRIPTION(S)): QuotedGround|0|
|`qodaiin`|QUOTED_GROUND(DRY_DESCRIPTION(A)): QuotedGround|0|
|`qodain`|QUOTED_GROUND(DRY_DESCRIPTION(M)): QuotedGround|0|
|`sain`|COMPARE_IN_RESPECTS: Proposition|3|
|`or`|APPLY_NAMED_MODIFIER: Descriptor[T]|1|
|`opchdy`|COLD_MODIFIER: NamedModifier[EntityDescription -> EntityDescription]|1|
|`qotor`|DRY_MODIFIER: NamedModifier[EntityDescription -> EntityDescription]|1|
|`sheedy`|MELANCHOLIC_PROFILE: EntityDescription[Profile]|1|
|`shodaiin`|RESPECT_PAIR: RespectSet|1|
|`olfar`|COLD: QualityKind|1|
|`ary`|DRY: QualityKind|1|
|`pchedeey`|EXPLAINS_RESULT_FIRST: Proposition|1|
|`olkey`|COLD_PREFIX: EntityDescription|1|
|`qokedy`|AUTUMN: EntityDescription[Season]|1|
|`sheos`|SUN: EntityDescription[Celestial]|1|
|`fcheey`|COURSE: CourseCondition|1|
|`otchedy`|AWAY_FROM: FromQualifier|1|
|`chotey`|US: HumanGroup|1|
|`qocthey`|INTO_SIGNS: IntoQualifier|2|
|`oteey`|WINTER_SIGN_MODIFIER: NamedModifier[SignDescription -> SignDescription]|1|
|`ol`|DEFINITE_NOMINAL: Nominal[T]|1|
|`oloqorain`|AUTUMN_TIME: TimeNominal|2|
|`qotaiin`|EXPLAINED_BY: Proposition|1|
|`tchedy`|IN_TEMPORAL_FRAME: FactualScopedGround|1|
|`otedy`|BEFORE_TIME: TemporalFrame|1|
|`qotchdy`|TIME_OF: TimeNominal|1|
|`chckhey`|AUTUMN: EntityDescription[Season]|1|
|`ytchedy`|FACTUAL_GROUND: FactualGround|1|
|`qotedar`|PRECEDES_TIME: Proposition|1|
|`qokar`|SUMMER: EntityDescription[Season]|1|
|`qotchd`|TIME_OF: TimeNominal|1|
|`qotom`|AUTUMN: EntityDescription[Season]|1|

Zero-cost derived rows have no separately adjustable whole meaning; their component/base choices and cuts are counted. Other rows are independently paid whole assignments. Detailed definitions and all occurrence IDs appear in JSON.

## Grammar and denotation

**G01 — Lexical nominals.** Named season/profile/celestial terms denote A,S,M and Sun; the explicit deictic term denotes an unspecified us. No individual patient, dated year or latitude is introduced. Generic historical predication is not a measured-event claim.

**G02 — Finite lexical composition.** Only the five explicitly declared cuts are derived by d and qo. Other d/o/qo-looking forms remain whole unknowns or separately listed whole values. No universal prefix deletion or full morphological parser is claimed.

**G03 — Named modifier application.** or D F applies a supplied NamedModifier[T -> T] to D:Descriptor[T], for T=EntityDescription or SignDescription. The operator/function is explicitly a lexical value; arbitrary quoted operators, unknown lambda tables and owner-changing coercions are not licensed.

**G04 — Direct cold application.** olkey D applies COLD to that written EntityDescription. The separate opchdy interface supplies the corresponding named modifier as data. These are paid surface choices, not independently confirmed inflections.

**G05 — Respect construction.** shodaiin Q1 Q2 yields the ordered pair/set of the two quality arguments. No quality is inferred from a drawing, name or phrase length.

**G06 — Comparison.** sain Target Source Respects forms CompareIn(Source,Target,Respects), also ascribing each written quality to the two written owners. The first expression provides an explicitly modified target. This is not identity, causation, a patient change or a rule for all members of a biological population.

**G07 — Course clause.** SunTerm fcheey (otchedy Group) (qocthey WinterModifier) TimeNominal forms Course(Sun,awayFrom(Group),into(WinterSigns),at(TimeNominal)). The final temporal nominal is a declared syntactic temporal adjunct; no separate unwritten AT token is alleged. All four roles are written. This constructor introduces no global referent register.

**G08 — Definite nominal.** ol N marks the explicit nominal as definite while preserving its sort and referent. TimeNominal stays temporal, EntityDescription stays an entity description.

**G09 — Prefix reason-giving.** pchedeey ResultDescription Ground asserts ConditionOf(ResultDescription), Ground and Because(Ground,ConditionOf(ResultDescription)). The result description must have at least one written qualification; the explicit G16 interface supplies its condition. The two complete argument expressions supply their own owners and qualifiers. The result is exactly the supplied condition.

**G10 — Before frame and time projection.** otedy Time produces Before(Time). qotchdy Season and qotchd Season produce TimeOf(Season), through two paid whole spellings of the same function.

**G11 — Factual scoped ground.** ytchedy QuotedGround preserves its content and marks it asserted; tchedy Frame FactualGround applies the frame to that ground. The temporal qualifier does not migrate to the result or a subsequent clause.

**G12 — Infix reason-giving.** QualifiedResultDescription qotaiin ScopedGround uses the same Because kernel as G09, preserving the full scoped ground. This is an additional fixed surface/interface, not a per-occurrence gloss change.

**G13 — Earlier relation.** qotedar Season Time states that the time of the written season precedes the written time. In C4 both the summer subject and autumn temporal owner are written.

**G14 — Clause completion and limits.** Complete typed Proposition expressions may form successive statements. No line end is a sentence operator. Bare nominals, modifiers, before-frames and quoted grounds are not by themselves completed statements. No gap skipping, reset, free cast, source-inferred reference or unrestricted higher-order escape is licensed.

**G15 — Permitted unknowns for preflight.** Unknown literal forms have no meaning yet. Sort requirements recorded in the table are obligations, not permission to invent an arbitrary phrase macro. This partial supplies no new global parser or proof that all unknowns can be completed.

**G16 — Written description-to-condition interface.** d, cold attachment and dry attachment produce owner-qualified descriptions. The qo reifier and the two because constructors explicitly use ConditionOf(D) = conjunction of the written qualifications of D applied to its retained owner. This interface requires a nonempty qualification list; it is not a global cast from every noun/reference to a proposition. This additional semantic construction is paid explicitly. No time is inserted by ConditionOf.

## Full-page preparation results

**ar, aiin, ain:** Every exact occurrence is the same named owner descriptor. Bare nouns do not complete a statement; all outside clause ownership remains owed. No extra owner is supplied to make an unparsed adjacency work.

**dar, daiin:** Every literal is a derived dry description of S or A. The local C3 result is daiin. A bare dar occurrence elsewhere has not been supplied a complete sentence merely because embedded d|ar computes inside qodar.

**qodar, qodaiin, qodain:** All exact ground forms are derived by the same d/qo laws, including the third owner M and the IT S.16 qodain reading. Only qodar receives a completed local reason use. qodaiin and qodain outside are quoted grounds, not free clauses or different word senses.

**otedy:** Every occurrence requires a written TimeNominal. Outside C3, .1 G002 requires the following opaees/opoees to participate in a TimeNominal expression. IT .1 G007 also has otedy and requires an actual time expression beginning otar. No default anchor is inserted.

**otchedy:** Every literal requires a HumanGroup argument and yields an AwayFrom qualifier. The two ZL/IT annular occurrences require actual group expressions beginning olkaiin and qotedaiin; their surrounding course syntax has not been completed. RF variant otche@152;y is unassigned.

**or:** Every occurrence is typed modifier application. N.2 has two actual nested applications. S.13 requires a descriptor beginning shedy and a compatible modifier expression; these remain unassigned. S.15 across the next line encounters fixed oteey: a direct completion with am as the first operand would require am:SignDescription, because oteey modifies sign descriptions. W.20/22 applications beginning aiin/ain require owner-preserving EntityDescription modifiers. Outside .24 requires a descriptor and a matching named modifier, not an implicit reference reset. IT aiinog and RF split forms are not normalized.

**ol:** Each occurrence demands a nominal argument and preserves its sort. The local temporal nominal at E.8 is supplied. Annular lkech variants and W.23 lcheol/sheoly are unassigned nominal obligations; a later grammar cannot silently use ol as AT or as a type cast.

**oteey:** Fixed as the winter modifier of sign descriptions in both E.8 and S.16. Its latter placement is an actual constraint on the uncompleted S.15–16 application, not a second freely chosen winter-time noun.

**other listed wholes:** Occurrence IDs, immediate literal neighbors, output types and required input sorts are retained for every row. Single-occurrence assigned constructors also have their explicit children in the local derivations. Unknown sorts are not successful parses.

These checks record requirements, not completed surrounding parses. In particular, an unassigned form is not automatically a convenient modifier, reference, sentence boundary or type adapter. The supplied TSV retains every native field, immediate literal neighbor and fixed argument obligation.

## Unfinished text and revisions

No whole first-annulus clause/constructor has been authored. The next fixed otedy atG002 yields a Before(time) frame and requires a TimeNominal expression beginning opaees atG003; ar atG004 supplies S. Their consuming clause, temporal application and following words are unresolved. This is incomplete authorship, not proof that those words cannot be assigned.

**R0 (rejected before final candidate):** Considered quality roots with predication/causal lifts. No completed whole argument or frozen values resulted; do not report this as a tested failure.

**R1 (retained in partial):** Named owners ar=S, aiin=A, ain=M; d attaches DRY, qo quotes a condition as reason material. This gives actual differently owned d applications in C3, while retaining all three qod forms.

**R2 (rejected before freeze):** An attempted ol=AT reading conflicted with possible nominal uses elsewhere. It was not frozen or counted as a manuscript result. Current ol is definite nominal marking; the written TimeNominal in C2 supplies its own adjunct role.

**R3 (retained in partial):** or is explicit named-modifier application over EntityDescription or SignDescription. The second descriptor class is needed by the repeated winter-sign modifier. This is a paid type/interface choice, not evidence of its meaning.

**R4 (not adopted):** A prospective W.18/W.20 qokal=BECAUSE plus shedy=solar-course reference would make the W.20 result owner M through or ain, unless an extra owner-changing projection or root alias were added. No such qokal/shedy binding, projection or ain=aiin alias is adopted. This was a genuine whole-occurrence warning before freeze, not a contradiction of the retained partial or of all completions.

**R5 (explicit interface before freeze):** Self-review made the result-description versus proposition interface explicit: qo and the because constructors project only nonempty written owner qualifications through G16. No general DescriptionRef-to-assertion cast or predicate-to-owner inversion is introduced.

**stop (partial):** Did not complete the .1 annulus or the remaining page without additional loosely motivated declarations, synonymous owner references and scope/projection operations. The local source accounting is not a complete page reading. No global UNSAT claim.

The general whole candidate was not completed. The retained artifact is useful conditional content and a constrained d/qo family, together with its full literal debts. It is not a successful full-page extension or a global impossibility theorem. A new unrestricted paragraph dictionary, causal-owner projection or synonymous root would change the candidate and is not installed here.
