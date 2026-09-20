# GDT992 Sunzi source-tree review

2026-09-20, bounded independent source-only review. No target, corpus, writer implementation or experiment output read. Reviewed only current SOURCE.json and the frozen Sunzi source audit, plus the live route. No frozen file changed.

Reviewed SOURCE: `experiments/yolo/gdt992_sunzi_complete_contextual_count/src/SOURCE.json`

SHA256: `5e5bf2da2ad22af0c60aae9ef250e00649c2d6b37454ffbfacde5ee4689e24ef`

Audit: `research_registry/work_batches/ten_hours_20260915/SUNZI_SECTION26_SOURCE_AUDIT_20260920.md`

SHA256: `de96a37458ef0c068122ef949d96716dfb91f8e5a6a4dc0fcd21dfc795730825`

**Finding: no missing Chinese content clause, reversed numerical instruction, or unsupported source theorem found.** This supports source coverage under the declared exploratory meanings; it neither confirms manuscript meaning nor licenses the modern writer historically.

## Coverage and scope

| Source span | Reviewed units | Finding |
|---|---|---|
| Introduction, unknown count | S01–S02 | Both retained; no named knower invented. |
| Three grouping conditions | S03–S05 | Same specific collection, group sizes3/5/7 and remainders2/3/2. No reduplication-as-multiplication error. |
| Question and answer | S06–S07 | Both retained; explicit23 without uniqueness or least qualifier. |
| Method rubric and repeated conditions/placements | S08–S11 | All retained;140/63/30 are PLACE values, not asserted products. WHEN is the declared contextual case interpretation. |
| Combination and result | S12 | All three placed values referenced; explicit233 retained; no intermediate partial arithmetic sum inserted. |
| Specific subtraction and obtaining result | S13 |210 is removed from233; DONE retains即得 without inserting another printed23. |
| General rubric and unit-remainder rules | S14–S17 | Separate generic templates with70/21/15; no dependence on the specific collection being23. |
| Threshold, subtraction, result | S18 | Inclusive106, one105 subtraction, unspecified current numeric parameter; no loop or obligatory23 result. |

REF's declared operator/section dispatch retains the source's changing antecedents. AT_LEAST's implicit current subject is explicitly called a contextual choice. The generic x is not silently identified with the sum of the three generic placements, and no missing general combination instruction is invented.

## Mechanical source checks

An independent recursive walk of the JSON trees, without importing any experiment code, found:

- 18 clauses;27 operator/terminal types; every declared arity matches every occurrence.
- Prefix and postfix serializations exactly match the saved streams,122 atoms each.
- Both declared frequency tables match the independently counted trees.
- DECIMAL_APPEND evaluates the complete numeral subtrees to23,140,63,30,233,210,70,21,15,106,105 in their intended positions.

For clarity, the digits0–7 used in this finite passage do not make this base8: the declared function is10*a+d. Inner positional subtrees such as14 in140 or10 in106 are modern numeral composition, not extra historical arithmetic steps. The old audit's illustrative NUM/END wording does not require those atoms; replacing that example with explicitly modern DECIMAL_APPEND changes no Chinese content claim.

## Three semantic contracts to make explicit

These are clarifications of the written meanings, not requests to alter the trees or to fit a target:

1. **Subtraction argument order:** the first child is the subtrahend and the second is the current value. State `SUBTRACT(a,b)=b−a`. Reading it by a conventional first-minus-second function would reverse both source instructions. The current prose meanings correctly specify the direction.
2. **Repeated OBJECTS:** the leaf in S06 denotes the collection introduced in S01, rather than introducing another collection. GROUP/COUNT:REF is already scoped, but the repeated bare OBJECTS occurrence should share that declared identity.
3. **Initial ignorance:** UNKNOWN in S02 describes the problem's initial epistemic situation. It is not an invariant saying that the answer remains unknown after S07. The source is a question/answer/method discourse, not an unordered conjunction of timeless epistemic claims.

The final generic subtraction may yield128 from233, which still satisfies the same remainders; this does not contradict the separate worked subtraction210→23. The source gives no basis for a forced smallest-solution reading. Decimal digits, zero components, prefix/postfix traversal, injective codes and one common REF spelling are clearly listed as modern writing assumptions, not observations of historical Chinese or Voynich.

## Limit of this review

No finite writer was inspected or tested. A single contextual REF atom and the18 modern tree boundaries are a declared model, not a recovered historical encoding. Full source coverage does not establish that its operators are individually identified meanings or that an inverse reading is unique. Existing IDEA354 and GDT991 decisions are unchanged. No new RAW card or registry operation is needed for this source check.
