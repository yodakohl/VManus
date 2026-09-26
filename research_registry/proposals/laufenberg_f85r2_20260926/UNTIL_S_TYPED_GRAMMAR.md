# IDEA550 descendant: fixed typed grammar for S.12–17

Status: exploratory authoring model, not a translation, execution, fit, or confirmation. This document is a new descendant of the frozen 26-group draft; the original `until_s_draft/DRAFT.json`, report, occurrence TSV, and prior reviews remain unchanged. It uses exactly the existing 24 literal ZL3b sense values: the three IDEA550 values and 21 previously authored whole-form assignments. It adds no lexical entry, alias, segmentation, morphology, target query, image owner, or input. The 52 exact assigned positions outside S remain unparsed transfer obligations; IT2a retains two local unassigned S groups and RF1b retains three. Those gaps are not bridged here.

The group order below is the source order. A semicolon in a derivation is a grouping instruction, not a manuscript punctuation mark or sentence boundary. The chosen typed contract is deliberately costly and conditional on its listed assumptions.

## Sorts, written introductions, and paragraph binders

Base sorts: `Substance`, `Recipient`, `Faculty`, `Event`, `EventPoint`, `State`, `Time`, `Proposition`, `Guard`, and `Relation`. Every event is indexed by a paragraph-cycle identifier `κ`. Times form a finite strict linear order for the manual examples only. This is a model convention, not an observed Voynich calendar or duration.

- S.12 `otchs` is the written introducer of substance `x:Substance` (the assigned hypothesis calls x nutriment); `shedor` is the written introducer of recipient `r:Recipient` (the assigned hypothesis calls r a receiving part). Both binder scopes are exactly this physical paragraph S.12–17.
- Explicit later references carry x/r as specified in the frozen lexicon. Their same-value readings alone do not identify event episodes.
- For this descendant only, one unique nourishment cycle `κ` is assumed for x at r. Its written event introductions are `arody` (presentation event p), `shedy` (adhesion phase h), `sorain` (assimilation-completion point c), `ypshedy` (conditional withdrawal-event kind d), and `qodaiin` (attraction event a). `orar` is not a second presentation: a declared uniqueness rule resolves it to the same p introduced by `arody`. This event identity is an added cycle hypothesis; it does not follow from identical participants.
- Within κ, `shedy` introduces one adhesion-onset event h₀ and its resultant adherence state H. `ytedar` refers to h₀. The first `chey` constrains H; it does not turn h₀ and H into two unrelated adhesion episodes. This event/state phase link is an additional, explicit coercion assumption.

## Frozen lexical inventory and group-by-group derivation

The “fixed contribution” column reproduces the existing assigned sense/type in `DRAFT.json`. The “ordered use” column fixes composition for this descendant without changing those sense values.

| Literal group in source order | Fixed contribution / type | Ordered contribution in this grammar |
|---|---|---|
| `.12 G001 otchs` | the nutriment x / `Substance` | Introduces x into S paragraph binder κ. |
| `.12 G002 shedor` | the receiving bodily part r / `Recipient` | Introduces r into the same binder κ. |
| `.12 G003 chey` | strictly before completion of supplied event, with cessation at that event / `Event → TemporalGuard` | Applies to the next written event-denoting phrase `sorain`, making guard U₁. U₁ is preposed and has forward host scope into `.13 G002 shedy`; that forward attachment is counted below. |
| `.12 G004 sorain` | completion of assimilation of explicitly bound nutrient / `Event` | Introduces c, the point marking completion of assimilation of x at r in κ. Completion-of-a-point is idempotent by explicit endpoint convention. |
| `.13 G001 or` | that same nutriment x / `SubstanceRef` | Supplies x as the theme of the following predicate. |
| `.13 G002 shedy` | adheres/remains attached (of x at r) / `Predicate` | With x and the following location/recipient, introduces h₀ and resultant state H in κ. |
| `.13 G003 tedy` | at/in the recipient / `LocativeRelation` | Builds the ordered location argument `at(x,r)`. |
| `.13 G004 sodaiiin` | that same receiving part r / `RecipientRef` | Fills the location/recipient slot with binder r. |
| `.13 G005 chy` | and; coordinates following explicit clause / `ClauseCoordinator` | Opens a rightward coordination whose next conjunct begins with `.14`; it does not supply a hidden proposition. |
| `.14 G001 ytedar` | earlier than the adhesion event / `TemporalModifier` | Relates the following presentation event p to the explicitly introduced h₀: `time(p) < start(h₀)`. Its antecedent is the local written `.13 shedy` event, not an anonymous graph edge. |
| `.14 G002 chz[s:r]` | that same nutriment x, conditional on uncertain literal / `SubstanceRef` | Supplies x only for exact ZL literal `chz[s:r]`; no IT/RF alternative is an alias. |
| `.14 G003 aiin` | that same receiving part r / `RecipientRef` | Supplies r to the following event predicate. |
| `.14 G004 arody` | was presented (nutriment x to recipient r) / `EventPredicate` | Introduces p in κ with written x/r arguments. The clause asserts presentation at r, temporally before h₀. |
| `.15 G001 ypshedy` | continued withdrawal/flowing away / `EventNoun` | Denotes a kind of sustained withdrawal events, not an actually asserted withdrawal occurrence in the base model. A separately counted generic/conditional clause rule scopes over it. |
| `.15 G002 dar` | of; introduces the departing nutriment / `CaseRelation` | Opens the typed genitive/participant slot for the remainder of the ordered source phrase. |
| `.15 G003 chedy` | away from that same recipient r / `SourceRelation` | Combines with the following x reference and paragraph binder r to form an away-from-r source phrase. |
| `.15 G004 or` | that same nutriment x / `SubstanceRef` | Fills the discontinuous `dar … chedy … or` participant phrase; x is the departing theme, r its source. |
| `.15 G005 am` | prevents adhesion and complete assimilation / `Predicate` | Applies to the withdrawal condition and the same-cycle h₀/c outcomes: if d occurs in the stated generic scope, it prevents h₀ and blocks completion c. Both outcomes remain inside this costly fixed sense. |
| `.16 G001 oteey` | the attractive faculty / `Agent` | Introduces/identifies faculty f as the written agent of attraction to r. It is not an image-derived owner. |
| `.16 G002 qodaiin` | draws/attracts / `Predicate` | Introduces attraction event a in κ, with f, x, and r supplied by adjacent written/referring groups. |
| `.16 G003 odain` | that same nutriment x / `SubstanceRef` | Fills a’s theme with x. |
| `.16 G004 an` | toward that same recipient r / `GoalRelation` | Fills a’s destination with r. |
| `.16 G005 chey` | same fixed guard value as `.12 G003` / `Event → TemporalGuard` | Applies to the immediately preceding qodaiin-attraction event a and takes the following `.17` endpoint phrase as its event argument. |
| `.17 G001 orar` | arrival/presentation of explicitly bound x to explicitly bound r / `Event` | Under the unique-κ rule, denotes the same presentation event p introduced by `.14 arody`; not a second arrival. |
| `.17 G002 oldar` | completion of the arrival/presentation event / `EventModifier` | Maps p to its endpoint event p⁺ at `end(p)`. This is an explicit ordered event-modifier application. |
| `.17 G003 ain` | at that same recipient r / `LocativeRelation` | Constrains p⁺ to be at r; this is a second written location check, not an unmentioned destination. |

### Ordered productions

The following productions are the full S derivation, preserving physical group sequence:

1. **S.12 frame:** `Introduce(x); Introduce(r); GuardEvent(U₁ := chey(sorain(c)))`. The final item is not a complete clause by itself; it is a written fronted guard awaiting its host.
2. **S.13 first conjunct:** `Theme(x) + Adhesion(h₀,H) + At(x,r) + Recipient(r) + AND`. The waiting U₁ attaches forward to H. It requires `start(H) < end(c)` and H holds before that boundary but ceases exactly at it. The later S.14 conjunct does not reset the participant binders.
3. **S.14 coordinated conjunct:** `Before(h₀) + Theme(x) + Recipient(r) + Present(p,x,r)`. Ordered composition asserts `time(p) < start(h₀)`. The leading `ytedar` is a written relation to the previously introduced h₀; the line is not parsed as a separate anonymous event graph.
4. **S.15 coordinated conjunct:** `WithdrawalKind(d) + DAR + Source(CHEDY, x, r) + AM(d,h₀,c)`. Surface discontinuity is retained: `dar` opens the case slot, `chedy` specifies the source r, `or` supplies x, and clause-final `am` applies to the completed phrase. `AM` is a pair of prevention relations: d prevents h₀ and prevents completion c. They are two outcomes already included in the frozen word sense and incur two outcome-link costs here.
5. **S.16–17 coordinated conjunct:** `Agent(f) + Attract(a,f,x,r) + Guard(U₂) + Arrival(p) + End(p⁺) + At(p⁺,r)`. The `.16` `chey` scopes rightward across the physical line break to `orar oldar ain`. U₂ constrains a strictly before p⁺ and requires cessation exactly at p⁺. `orar` resolves to p by the unique-cycle binder, `oldar` creates p⁺, `ain` checks r.
6. **Paragraph result:** three explicit conjuncts after the fronted S.12 topic/guard frame, coordinated by `.13 chy`: presentation before adhesion; conditional departure preventing both outcomes; and attraction up to presentation. The topic frame and first guard are part of this derivation, not a fourth silent sentence. This grouping is a grammatical hypothesis; the six physical lines are not asserted to be six or three manuscript sentences.

## Explicit assumptions and costs

No listed assumption is a lexical value; each is an additional grammar, binder, event-model, or cross-source commitment.

1. **Paragraph binder:** the written `.12` introductions bind x/r only within S.12–17. Later local references are resolved to these referents; there is no cataphoric binder across paragraphs.
2. **One-cycle uniqueness:** all typed events belong to one κ for x at r; `arody` and `orar` co-refer to one p; `sorain` is c for the same κ; `shedy` provides h₀/H; `qodaiin` provides a. This is not licensed by participant identity alone.
3. **Event/state coercion:** `shedy`’s one adhesion phase has an initiation h₀ and resultant state H; `ytedar` orders the initiation, while `chey` bounds the state. This resolves the distinction between a point/process event and “remains attached.”
4. **Finite interval model:** processes/states occupy intervals; completion is represented by an endpoint event. `end(point)=point`; this explicit idempotence convention resolves `chey(sorain)` without a hidden second completion layer. No observed duration is supplied.
5. **Forward-scope attachment U₁:** `.12 chey sorain` scopes across the line break and topic sequence to `.13 shedy`; no punctuation rule is inferred. U₁ imposes the fixed strict UNTIL/cessation-at-c value.
6. **Presentation-before-adhesion construction:** the preposed `.14 ytedar` takes the verb-final `arody` event as its clause and refers to the written h₀ from `.13`. It asserts p before h₀.
7. **Discontinuous `dar` production:** the `.15` slot opened by `dar` takes the later `chedy + or` phrase, producing “of x away from r.” This is an explicit, nonlocal ordered rule rather than a free English reordering.
8. **Generic conditional departure modality:** `.15 ypshedy` does not existentially assert that x actually departs in κ. The complete `.15` clause is read as a generic conditional law: for any sustained withdrawal d of x away from r in a nourishment cycle, if d occurs, d prevents that cycle’s h₀ and c. No “if” or universal marker has a separate written value; assigning this generic scope to the event-kind construction is a counted assumption. If one insists that .15 asserts an actual departure, the model must be rebuilt and may conflict with the positive adhesion assertion.
9. **Typed `am` outcome application:** `am` is refined as `DepartureCondition × AdhesionEvent × AssimilationCompletion → PropositionPair`. Its two consequence slots resolve to the same-cycle h₀ and c under assumption 2. The semantic burden is explicitly two outcomes, not one zero-argument sentence.
10. **Coordinator:** `.13 chy` coordinates the `.14` presentation conjunct with the subsequent `.15`/`.16–17` conjuncts in the written order. The precise grouping of the last two is fixed in production 6; alternative punctuation is not silently supplied.
11. **Forward-scope attachment U₂:** `.16 chey` scopes across the line break to `.17 orar oldar ain`; it bounds the written qodaiin event a by p⁺. This is the same strict UNTIL/cessation-at-boundary seed, used with a second declared host attachment.
12. **Location endpoint rule:** `ain` predicates location of the boundary event p⁺ at r. It is a written endpoint condition in addition to `orar`’s lexical x/r identification, not a hidden recipient.
13. **No automatic event coreference:** event identity is assigned only by assumptions 2–3 and the named introducers above. Repeated x/r elsewhere does not imply same event. All 52 outside-S positions remain unknown in reference and clause scope; IT/RF unassigned literal strings remain gaps.
14. **Optional source bridge, not a target axiom:** only in the second document’s source-compatibility layer, target p/h₀/c/a are mapped to one Galenic presentation/adhesion/assimilation/attraction sequence. This mapping has a separate cost and is not part of target-only meaning.

The 21 whole-form values, 2 written participant introductions, 2 participant binders, 3 IDEA550 seeds, repeated use of `am`’s two outcomes, forward attachment at each `chey`, event uniqueness, genericity, and source mapping are all reported separately. The broad role label `Predicate` never substitutes for the signatures above. No grammar or relation is free.

## Incompleteness held fixed

The model has no local interpretation for the 52 outside-S exact positions; it does not test their contexts. IT2a’s `.14 ch?s` and `.16 qodain` and RF1b’s `.13 {ch'}edy`, `.14 ch@152;s`, and `.15 yfshe@152;y` remain unmatched alternatives, never aliases. The exact uncertain literal `chz[s:r]` has a value only under ZL3b. Nothing in the grammar propagates across alternate transcriptions or makes 125 positions 125 independent observations. The original550 incomplete decision and all original files remain unchanged.
