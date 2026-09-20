# R392-C1: a complete source-content notation, not a manuscript writer

**RAW_UNREVIEWED elaboration of IDEA000392; no new idea card or target experiment.** Source-only work2026-09-20, bounded03:54:41–04:24:41UTC. Earlier392source/proposal bytes remain frozen. The only additional primary read was the source-only ALLOY_FINITE_GRAMMAR.md; no target experiment files were read.

## Result and decision

C1 explicitly represents all29frozen Cap.XII content positions, including element theory, purposes, explanations, uncertain identities, alternative scope and authorial opening/closure. It provides a finite syntax, a closed atom lexicon and fully written symbolic text. It is **not compact enough to supply a persuasive small shared writing system**: the present source uses20syntactic heads,67predicate heads and58constant types. Of the predicate heads,43occur only once;31constant types also occur once. The fixed family adds OR and SAME_STOCK for comparison, giving21syntactic heads and68predicate heads in total. Counts are source-notation costs, never target-word counts.

No head means an entire arbitrary source sentence, and no TEXT/COMMENT/UNKNOWN_SENTENCE escape exists. Nevertheless, many ordinary meanings occur once in this source: revealing, praising, hearing, calcining, rectifying, stronger heat, a particular furnace and so on. Assigning unknown manuscript strings independently to all these atoms would leave substantial semantic freedom. Finite syntax alone does not remove that debt. The source-return relation is concrete; the proposed full writing theory remains unbound. This is an elaboration of392, so no extra RAW card was added.

[Machine-readable grammar, every predicate signature, every constant explanation, program,48binding records and reference occurrence ledger](RUPESCISSA_CONTENT_LANGUAGE_C1_20260920.json). The final JSON is the normative atom/grammar inventory. The readable complete symbolic text is also reproduced below.

## Source, notation and interpretation are separate

Historical source: [the frozen392inventory](RUPESCISSA_XII_RETURN_CONTENT_20260920.json), SHA256 `8d43fa3d5a9fbe0694f5c36142da15cbe9324dbb3b6813396219bda4d8591337`, with the complete1561Cap.XII and the native1443return clause. Its29numbered items are editorial coverage divisions, not sentence, word or glyph boundaries. The original print conflict, English omission and medieval variants remain unchanged.

C1 is our modern S-expression notation. No claim is made that Rupescissa used registers, prefix syntax or encoded aliquots this way. Semantic labels are human-readable symbols with fixed meanings. They are **not** EVA letters, confirmed word translations, freely chosen names for target groups, or an assumed historical Latin order.

The notation is a content description, not a laboratory execution. A source assertion may be uncertain, false or internally conflicting. `A` records it instead of proving it. Typed external calls retain what the source refers to without inventing their bodies. Initial `pro modico`, final deictic reason and the scope of `vel ... vnum` are explicitly interpreted/uncertain, not silently settled.

## Fixed syntax and typing

A document is a sequence of statements. Parentheses delimit every application. A head has exactly its declared signature; AND and SET permit2–8 and1–8arguments respectively. No unlisted predicate or constant is allowed. Integers are0–31, expression depth at most12 and document statements at most256. These bounds merely make this source-side proposal finite; they were not selected from manuscript lengths. References are restricted to32stock,32aliquot,32vessel/apparatus and32event slots,8set slots,8reason slots, plus the single nonnested bound variable x.

The statement frames are `DECLARE`, `ALLOC`, `A`, `D`, `G`, `BECAUSE`, `PURPOSE`, and `ALTERNATIVE`. Formula structure uses `AND`, `NOT`, `OR`, `FORALL`, `FOR_ONE`; terms use `SET`, `CHOICE`, `Q`, `UP`, `LOW`, `MIX`, `IN`, `BOTTOM`. The JSON lists exact signatures. Temporal/operational relations such as AFTER, BEFORE, UNTIL, DISTIL and COMBINE are separately listed fixed predicates; they are not arbitrary syntax macros.

`DECLARE` introduces a typed discourse handle, not necessarily a physically new object. `ALLOC` introduces a use-site aliquot binding. `A`, `D`, `G` respectively record source assertion, instruction and announced goal. BECAUSE and PURPOSE preserve explanatory content as content; neither silently converts it into an observed physical result. ALTERNATIVE contrasts complete statement branches; OR supports a different distributive scope under a quantifier.

The initial period of heating until a first distillate is represented by ONSET_CONDITION. The later no-more-ascent condition is UNTIL. These are deliberately distinct: the distillation is not incorrectly terminated at the first drop.

## Stock provenance is not whole-portion conservation

`UP(E0)` names the collected rising stock produced by the first distillation; `LOW(E0)` names its retained bottom stock. The terms are different provenance roles of the same event. Vessel V0 and the stock remaining at its bottom are different types. V1 is the physical bath; its water P1 is not the process-water stock.

The first return has:

```text
(ALLOC A1 (UP E0) unquantified)
(ALLOC A2 (LOW E0) unquantified)
(D (COMBINE E1 A1 A2 V0 over))
(D (RETURN V0 (IN V1)))
```

A1 and A2 are explicit positive, unquantified input amounts from the indicated source stocks. They are not silently the whole stocks. ALLOC is a semantic operand binding, not an invented extra historical manipulation. Subsequent uses of a stock can allocate another amount if some remains. A repeated aliquot handle denotes that same selected amount; a repeated stock handle denotes the same provenance source, potentially for another amount. Total withdrawals cannot exceed availability in a concrete realization, but the source supplies no masses to calculate that ledger. No lossless separation, complete consumption or equal recovered mass is imposed.

Every introduced local handle is listed in the JSON:48entries, including13explicit aliquots and12generated output stocks from the five distillations and two combinations. Holding events generate no output-stock identity. Output-slot order UP-before-LOW is an editorial ledger convention, not a medieval writing fact. Reference occurrence records include both a derived selector such as UP(E0) and its event component; these are audit records, not two physical creations.

P2, the later4:1water source, remains unresolved among available earlier water stocks and an external origin. Unused amounts of UP(E0) are not ruled out. P3, the water in the final list, is also an unresolved available water stock. DOSE preserves both written quantities4pounds and1pound; the main interpretation treats them as a ratio prescription. A literal4-pound/1-pound batch is a distinct possible interpretation, not an invisible substitution.

The allocations A9–A12 make the inputs to later circulation/rectification explicit. The earth allocation A12 is shared by calcination and its reduction prerequisite. These prospective allocations do not imply that all alternative operations execute. Bodies of earlier procedures and internal intermediate stocks during repeated ascents remain unexpanded. Therefore this notation does **not** certify all global stock-creation counts for a future relative-reference scheme. Those unknown counts cannot silently become zero.

## Fully written symbolic source

The following is the whole C1representation. Source-item headings are coverage labels only; they are not symbols emitted by the language. No item is a single target word by assumption.

### Source inventory 01

```text
(A (WILL author (NOT (OMIT_FOR author small_reason (REVEAL author reader chapter_secret)))))
(G (FORALL x ELEMENTS (THEN (EXTRACT x prior_materials) (SHOW_APART x))))
(G (FORALL x ELEMENTS (AFTER (REDUCE_TO x quintessence) (SHOW_APART x))))
```

### Source inventory 02

```text
(DECLARE P0 stock (AND (SELECTED_FROM P0 prior_materials) (QUAL P0 putrefied) (QUAL P0 liquefied)))
(A (PREVIOUSLY_DESCRIBED (PREPARE P0) previous_preparation))
(A (EXAMPLE human_blood P0))
(ALLOC A0 P0 unquantified)
```

### Source inventory 03

```text
(DECLARE V0 vessel (AND (KIND V0 distillatory) (QUAL V0 glass)))
(D (MOVE A0 (IN V0)))
```

### Source inventory 04

```text
(DECLARE V1 vessel (KIND V1 pot))
(DECLARE P1 stock (AND (KIND P1 water) (ROLE P1 heating_medium)))
(A (AT P1 (IN V1)))
(D (NEST V0 V1))
```

### Source inventory 05

```text
(DECLARE V2 vessel (AND (KIND V2 amphora) (QUAL V2 glass) (QUAL V2 very_clean)))
(DECLARE V3 apparatus (KIND V3 alembic_tube))
(D (DISTIL E0 A0 V0 bath V3))
(D (APPLY_HEAT E0 below))
(D (ONSET_CONDITION E0 (DISTILS E0 water)))
```

### Source inventory 06

```text
(D (RECEIVE (UP E0) V2))
```

### Source inventory 07

```text
(D (UNTIL E0 (NO_MORE_RISE E0 bath)))
(A (AT_STOP E0 (ONLY_COMPONENT (UP E0) water)))
```

### Source inventory 08

```text
(BECAUSE
  (A (COMPONENTS (LOW E0) (SET air fire earth)))
  (AND (CANNOT_RAISE bath air) (CANNOT_RAISE bath fire) (CANNOT_RAISE bath earth)))
(A (REMAINS (LOW E0) (BOTTOM V0)))
```

### Source inventory 09

```text
(ALLOC A1 (UP E0) unquantified)
(ALLOC A2 (LOW E0) unquantified)
(D (COMBINE E1 A1 A2 V0 over))
```

### Source inventory 10

```text
(D (RETURN V0 (IN V1)))
(D (HOLD E2 (MIX E1) V1 (Q 7 day)))
(D (MIX_WELL (MIX E1)))
(D (SEAL V0 (DURING E2 (NOT (DISTILL_ANY V0)))))
```

### Source inventory 11

```text
(ALLOC A3 (MIX E1) unquantified)
(D (AFTER (DISTIL E3 A3 V0 ash unstated_path) E2))
(A (STRONGER ash bath))
```

### Source inventory 12

```text
(A (APPEARANCE (UP E3) (SET water oil bright golden)))
```

### Source inventory 13

```text
(DECLARE V4 vessel (KIND V4 ampulla))
(D (UNTIL E3 (NO_MORE_RISE E3 ash)))
(A (AT_STOP E3 (AND (AT (UP E3) (IN V4)) (COMPONENTS (UP E3) (SET water air)))))
```

### Source inventory 14

```text
(DECLARE V5 vessel (ROLE V5 processing_container))
(ALLOC A4 (UP E3) unquantified)
(PURPOSE
  (D (DISTIL E4 A4 V5 bath unstated_path))
  (SEPARATE water air))
(A (AND (ONLY_COMPONENT (UP E4) water) (QUAL (UP E4) clear)))
(A (AND (ONLY_COMPONENT (LOW E4) air) (APPEARANCE (LOW E4) (SET oil golden)) (REMAINS (LOW E4) (BOTTOM V5))))
```

### Source inventory 15

```text
(D (SET_ASIDE (LOW E4)))
(A (IDENTIFIED_AS (LOW E4) air))
```

### Source inventory 16

```text
(A (AND (STILL_AVAILABLE (LOW E3)) (COMPONENTS (LOW E3) (SET fire earth))))
```

### Source inventory 17

```text
(DECLARE P2 stock (AND (KIND P2 water) (QUAL P2 elemental) (UNRESOLVED_ID P2 (SET (UP E0) (UP E4) external_water))))
(ALLOC A5 P2 unquantified)
(ALLOC A6 (LOW E3) unquantified)
(PURPOSE
  (D (COMBINE E5 A5 A6 V0 over))
  (SEPARATE fire earth))
(D (DOSE A5 (Q 4 pound) A6 (Q 1 pound)))
```

### Source inventory 18

```text
(DECLARE V6 vessel (ROLE V6 water_bath))
(PURPOSE
  (D (HOLD E6 (MIX E5) V6 (CHOICE (Q 7 day) (Q 8 day))))
  (QUAL (MIX E5) well_incorporated))
(A (SAME_METHOD E6 E2))
```

### Source inventory 19

```text
(ALLOC A7 (MIX E5) unquantified)
(D (AFTER (DISTIL E7 A7 V0 strong_flame unstated_path) E6))
```

### Source inventory 20

```text
(A (APPEARANCE (UP E7) (SET water red)))
(D (COLLECT_WHILE (UP E7) (ANY_RISE E7)))
```

### Source inventory 21

```text
(A (AND (REMAINS (LOW E7) (BOTTOM V0)) (WRITTEN_NAME (LOW E7) water) (QUAL (LOW E7) very_black)))
(D (SET_ASIDE (LOW E7)))
```

### Source inventory 22

```text
(ALLOC A8 (UP E7) unquantified)
(A (AND (QUAL (UP E7) very_red) (COMPONENTS (UP E7) (SET water fire))))
```

### Source inventory 23

```text
(DECLARE V7 vessel (KIND V7 distillatory))
(D (DISTIL E8 A8 V7 bath unstated_path))
(A (AND (ONLY_COMPONENT (UP E8) water) (QUAL (UP E8) clear)))
(A (AND (REMAINS (LOW E8) (BOTTOM V7)) (APPEARANCE (LOW E8) (SET oil red)) (IDENTIFIED_AS (LOW E8) fire)))
```

### Source inventory 24

```text
(DECLARE P3 stock (AND (KIND P3 water) (QUAL P3 elemental) (UNRESOLVED_ID P3 (SET (UP E0) (UP E4) (UP E8) P2))))
(A (OBTAINED_APART (SET (LOW E4) P3 (LOW E8) (LOW E7))))
(A (AND (IDENTIFIED_AS (LOW E4) air) (IDENTIFIED_AS P3 water) (IDENTIFIED_AS (LOW E8) fire) (IDENTIFIED_AS (LOW E7) earth)))
```

### Source inventory 25

```text
(BECAUSE
  (A (PURPOSE_OF (RETURN_KIND water) (EXTRACT_FROM (SET air fire) earth)))
  (FORALL x (SET air fire) (NEEDS_FOR x ascent water)))
```

### Source inventory 26–27

```text
(ALLOC A9 (LOW E4) unquantified)
(ALLOC A10 P3 unquantified)
(ALLOC A11 (LOW E8) unquantified)
(ALLOC A12 (LOW E7) unquantified)
(DECLARE S0 aliquot_set (MEMBERS S0 (SET A9 A10 A11 A12)))
(ALTERNATIVE
  (D (FORALL x S0 (CALL previous_circulation x circulation_vessel quintessence)))
  (D (FOR_ONE x S0 (RECTIFY x (REPEAT 7 (ASCEND x aludel))))))
```

### Source inventory 28

```text
(D (BEFORE
  (CALCINE A12 (Q 21 day) (CHOICE glassmakers_furnace reverberatory_furnace))
  (REDUCE_TO A12 quintessence)))
(A (AND (WRITTEN_NAME (LOW E7) earth) (QUAL (LOW E7) very_black)))
```

### Source inventory 29

```text
(DECLARE R0 reason (UNRESOLVED_REASON R0))
(BECAUSE
  (A (WILL author (NOT (SPEAK_FURTHER author science))))
  (IS_REASON R0))
(BECAUSE
  (D (PRAISE reader God))
  (AND (HEARD reader chapter_content) (TAUGHT author reader chapter_content)))
```

## Same-grammar identity and scope rivals

Both source and rivals are expressible under the same fixed grammar. A rival may be a legal description while failing to describe the historical paragraph; syntax acceptance is not a semantic success.

**Independent external same-type water at first return**

```text
(DECLARE P4 stock (AND (KIND P4 water) (QUAL P4 elemental) (UNRESOLVED_ID P4 (SET external_water)) (NOT (SAME_STOCK P4 (UP E0)))))
(ALLOC A1 P4 unquantified)
```

Return input no longer derives from first collected output. Same component class and later instructions do not repair that written provenance loss.

**Different-stock same-type residue**

```text
(DECLARE P5 stock (AND (COMPONENTS P5 (SET air fire earth)) (NOT (SAME_STOCK P5 (LOW E0)))))
(ALLOC A2 P5 unquantified)
```

Return is no longer over the earlier retained three-element stock.

**Different positive return amounts from the correct source stock**

```text
(ALLOC A1 (UP E0) unquantified)
```

Two concrete realizations may choose distinct positive amounts <=available stock. The source and C1 do not distinguish them. This is not presented as a rejected rival or a different required string.

**Choose known recovered water for the later dose**

```text
(A (SAME_STOCK P2 (UP E4)))
```

An optional in-grammar completion only if enough stock remains. Source does not select it; external_water remains possible.

**Distributive method alternative**

```text
(D (FORALL x S0 (OR (CALL previous_circulation x circulation_vessel quintessence) (RECTIFY x (REPEAT 7 (ASCEND x aludel))))))
```

Each selected elemental product may use either method, unlike outer all-circulation versus one-rectification. A real scope difference in the same grammar, currently unresolved by source collation.

The snippets preserve original stable IDs for comparison. A chosen canonical first-use numbering must rename every affected later reference consistently throughout the full program. No relative-distance notation is selected here. The extra declaration in the fresh-stock rival is visible; no unrecorded new pool is inserted.

The strongest source-only difference is provenance: replacing UP(E0) by same-kind P4 loses the written extracted-output reference. It does not automatically falsify the rest of the chemistry. Changing only an unquantified aliquot amount from the correct source does not produce a required different string. The reader should not confuse those two cases.

## Exact singleton costs

Predicate heads used only once in the source representation:

`ANY_RISE`, `APPLY_HEAT`, `ASCEND`, `BEFORE`, `CALCINE`, `CALL`, `COLLECT_WHILE`, `DISTILL_ANY`, `DISTILS`, `DOSE`, `DURING`, `EXAMPLE`, `EXTRACT`, `EXTRACT_FROM`, `HEARD`, `IS_REASON`, `MEMBERS`, `MIX_WELL`, `MOVE`, `NEEDS_FOR`, `NEST`, `OBTAINED_APART`, `OMIT_FOR`, `ONSET_CONDITION`, `PRAISE`, `PREPARE`, `PREVIOUSLY_DESCRIBED`, `PURPOSE_OF`, `RECEIVE`, `RECTIFY`, `REPEAT`, `RETURN`, `RETURN_KIND`, `REVEAL`, `SAME_METHOD`, `SEAL`, `SELECTED_FROM`, `SPEAK_FURTHER`, `STILL_AVAILABLE`, `STRONGER`, `TAUGHT`, `THEN`, `UNRESOLVED_REASON`.

Constant types used only once:

`God`, `alembic_tube`, `aliquot_set`, `aludel`, `amphora`, `ampulla`, `apparatus`, `ascent`, `below`, `bright`, `chapter_secret`, `circulation_vessel`, `external_water`, `glassmakers_furnace`, `heating_medium`, `human_blood`, `liquefied`, `pot`, `previous_circulation`, `previous_preparation`, `processing_container`, `putrefied`, `reason`, `reverberatory_furnace`, `science`, `small_reason`, `strong_flame`, `very_clean`, `very_red`, `water_bath`, `well_incorporated`.

The JSON gives every occurrence count and the entire fixed lexicon, including repeated material words, typed quantities, source procedure names and grammatical sort names. Counts include those sort names; they are not a claimed number of independently lexicalized medieval meanings. Whole property constants such as very_clean/very_red/very_black and strong_flame are not compressed by a retrospectively invented degree morphology in this version. That is another transparent cost.

## Preserved limits and decision

- The first return fixes original output provenance and original retained-residue provenance, with unknown actual quantities.
- Later vessel handles may alias; labels do not prove distinct glass objects. Reusing V0 for the later original-residue treatment is a declared contextual interpretation, not a newly observed vessel inscription.
- Black material retains the written name water at47 and earth at48, plus the earth endpoint assertion. Recording these claims does not repair them or prove their joint physical truth.
- Main branch scope is either circulation of each endpoint or rectification of one selected endpoint. The distributive OR rival remains a real, unresolved Latin-scope alternative.
- Initial preparation and final circulation are source calls, not fully expanded instructions. Internal result bindings and repeated-ascent intermediate identities remain unknown.
- No wholly free unknown-word placeholder exists, but finite existential identity choices and undeclared quantitative amounts still leave substantial source-level ambiguity.
- Actual manuscript realization remains missing: alphabet, segmentation, packing into space-delimited groups, code for predicates/constants/references, contextual variants and treatment of whole-form residuals. Nothing in C1 selects these.

The source-only predecessor [ALLOY_FINITE_GRAMMAR.md](ALLOY_FINITE_GRAMMAR.md) explicitly separated immutable recipe values from physical stock and omitted some historical exposition from its generated accounts. C1 keeps the stock/aliquot distinction and explicitly represents exposition; it does not inherit the old renderer, any target outcome or arithmetic success. The other primary stops already preserved in392remain in force; no target-containing successor report was reopened.

Decision: retain this concrete source elaboration, **not a new RAW candidate or a selected target test**. It supplies auditable dependencies and an honest lexical cost. At present it does not show how the complete paragraph can be written with a small, independently constrained global vocabulary. No decoder, process simulator, synthetic control corpus, target data, reserve, contacts, registry refresh or commit.

Static checks: JSON syntax, defined heads/constants, balanced parentheses, all29inventory positions, unique explicit binding IDs, frozen-source hash. No semantic execution or chemical validation was performed.
