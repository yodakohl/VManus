# Sunzi III.26: independent source coverage audit

2026-09-20. Source-only audit of IDEA000354; no target, writer, decoder, result packet or new manuscript access. Existing proposal/source bytes remain unchanged. **No missing Chinese clause found in the old seven-part inventory**, but the distinctions below matter for any complete semantic representation.

## Owned source and boundary

The complete problem, answer, method and concluding general rule were actually viewed again on physical **PDF page74** of the [Peking University Library/CADAL scan](https://archive.org/download/02094034.cn/02094034.cn.pdf). The whole block runs from 今有物 to the final 即得; it is present on that page. The version-A scan has columns and answer/method indentation, not a printed section number26. Its catalogue names Li Chunfeng and others as commentators and does not supply a securely established impression date. No medieval witness date is invented.

The [Conway section26 transcription](https://yawnoc.github.io/sun-tzu/iii/26) follows versionD by default, with modern punctuation/sectioning. Native inspection agrees with all numerical values and the question/answer/method/general-rule sequence. This audit does not certify every graphic variant as a diplomatic transcription of versionA. In particular, the modern Chinese string below is retained as the owned edition's text; no source spelling is changed to fit a model.

| Cached source object | SHA256 |
|---|---|
| Original PDF,1,770,639bytes | `a377aadf78f8e61f4dffbe84fb115913dfee8ff229be8a841491791457976e8e` |
| Owned section26HTML,11,676bytes | `53467207d549a770d50a58403cabd702fb590b3809190024d95e07fc808c4910` |
| Page74 native-inspection raster, not added to repository | `39c3c9d8321cdddcf54288f1b47a8865fd9d6a15193e7d656cf145f9e664c540` |

Complete Chinese, retaining the transcription's punctuation:

> 今有物不知其數。三三數之賸二、五五數之賸三、七七數之賸二。問物幾何。
>
> 答曰、二十三。
>
> 術曰、三三數之賸二、置一百四十、五五數之賸三、置六十三、七七數之賸二、置三十。
>
> 并之、得二百三十三。
>
> 以二百一十減之、即得。
>
> 凡三三數之賸一、則置七十、五五數之賸一、則置二十一、七七數之賸一、則置十五。
>
> 一百六以上、以一百五減之、即得。

## Every content clause and its scope

These rows are an audit division, **not a historical field count or proposed target-group count**.

| Source clause | Complete meaning required | Scope/identity caution |
|---|---|---|
| 今有物 | Introduce a collection of objects in a problem situation. | 今 is the conventional present/supposition opening. It does not name a material, owner or physical location. |
| 不知其數 | The number of those objects is unknown. | 其 refers to the introduced objects; no named knower is supplied. Do not add a separate actor. |
| 三三數之賸二 | Counting/grouping those objects by threes leaves two. | 三三 is distributive grouping, not the product3×3. The same collection persists. |
| 五五數之賸三 | Counting the same objects by fives leaves three. | Not a fresh collection with an independently chosen total. |
| 七七數之賸二 | Counting the same objects by sevens leaves two. | A third constraint on the same unknown count. |
| 問物幾何 | Ask how many objects there are. | The question remains part of the content, not a decorative header. |
| 答曰、二十三 | The answer says23. | A stated answer, not a written uniqueness theorem or explicit least-positive qualification. The count's unit is inherited. |
| 術曰 | Introduce the method. | A discourse/rubric change; no named new human speaker. |
| 三三數之賸二、置一百四十 | Restate the3/remainder2 case and put140. | The condition is repeated in writing. The operation is placing/setting a value; no multiplication is written. |
| 五五數之賸三、置六十三 | Restate the5/remainder3 case and put63. | No implicit new object total. The63 is a computational term, not the count of a second collection. |
| 七七數之賸二、置三十 | Restate the7/remainder2 case and put30. | Again a placed value. Physical rods or a particular board are not named. |
| 并之、得二百三十三 | Combine/add the placed values, obtaining233. | 之 now refers collectively to140,63,30. No intermediate203, association order or register allocation is written. |
| 以二百一十減之、即得 | Subtract210 from that result and obtain the answer. | Subtrahend210 and current result233 have distinct roles; the result23 follows arithmetically and from the answer. No written2×105 multiplication. |
| 凡 | Introduce a general rule. | This changes scope from the one worked example. It must not silently keep every later quantity identified with the special23. |
| 三三數之賸一、則置七十 | In the3/remainder1 case put70. | An explicitly conditional unit-remainder rule. |
| 五五數之賸一、則置二十一 | In the5/remainder1 case put21. | Same instruction kind with changed arguments. |
| 七七數之賸一、則置十五 | In the7/remainder1 case put15. | The text does not explicitly state an arbitrary-remainder scaling rule. |
| 一百六以上 | The applicable quantity is106 or above. | Inclusive threshold. The noun is omitted; construing it as the accumulated computational value is a reasonable contextual interpretation, not an explicit repeated noun. |
| 以一百五減之 | Subtract105 from that quantity. | Exactly one subtraction is explicitly written. No iterate/until command is present. |
| 即得 | Then obtain the result / the procedure yields it. | The result is not numerically restated. Do not identify this generic result with23 in every case. |

## The106/105 sentence does not license an unmarked loop

Literal single-step reading: if the relevant value is at least106, subtract105. Its scope does not specify a maximum input, repeated execution, stopping test, least answer or nonnegative representative convention. A future formal model may add any of these only as an explicit assumption.

Useful exact arithmetic consequences, **calculated here, not extra Chinese claims**:

- The three general unit-remainder placements sum to70+21+15=106; one subtraction gives1, which has remainder1 in all three divisions.
- Applying one105 subtraction to the worked sum233 gives128. That also has remainders2,3,2. Thus the single-step rule is not arithmetically false merely because128 differs from23.
- The actual example separately writes subtraction210, yielding23. Identifying210 with2×105 is valid arithmetic but not a written instruction to perform a two-iteration loop.
- The original remainder conditions permit23+105k, with the admissible integer range depending on the domain convention. For positive counts,23,128,233,... survive. The Chinese question never writes “least”.
- The threshold leaves105 unchanged, whereas a least-nonnegative normalization would send105 to0. Neither0 nor such a normalization appears here. A hypothesized least-positive loop would be compatible with this threshold but remains an extension.

The general rule therefore supplies basis values and one reduction statement. It does not spell out a complete modern arbitrary-modulus Chinese-remainder algorithm. Reading it as shorthand for a familiar larger procedure is historically possible, but must be distinguished from the literal content selected for a fixed test.

## Written numerals versus modern components

| Written spelling | Value | What is absent |
|---|---:|---|
| 二十三 | 23 | No decimal-place glyph0. |
| 一百四十 | 140 | No units-zero glyph. |
| 六十三 | 63 | No arithmetic product sign. |
| 三十 | 30 | No units-zero glyph. |
| 二百三十三 | 233 | No intermediate partial sum. |
| 二百一十 | 210 | No units-zero glyph and no written2×105. |
| 七十 | 70 | No units-zero glyph. |
| 二十一 | 21 | No derivation of the coefficient. |
| 十五 | 15 | No explicit leading一 before十. |
| 一百六 | 106 | No 零 or 〇 between百 and六. |
| 一百五 | 105 | No 零 or 〇 between百 and五. |

The base group sizes/remainders use三、五、七、二、一 in their indicated clauses. Number spellings are lexical Chinese numerals, not positional decimal digit strings. In particular, repeated三三/五五/七七 does not double or square the group size. A modern decimal NUM/END representation can be stipulated as an analyst's semantic serializer, but its0 components and delimiters are then writing assumptions, not written historical signs. No word/group count correspondence follows.

## Reference and lexical ambiguity that must survive

1. 數 is the noun “number” in 其數 and the verb “count” in 數之. The written graph recurs with context-dependent grammatical roles; no common target glyph or phonetic value is thereby established.
2. The six specific grouping mentions refer to one collection/count, while the later remainder1 cases are generic. Copying one global object token into both scopes without a binder would add identity not written by the source.
3. 之 takes different typed antecedents: objects during grouping, placed terms during addition, result/current value during subtraction. One nearest-word reference policy is not sufficient by itself.
4. 置 gives each case its computational value. Neither its physical storage nor an abstract immutable-register system is supplied. Numerical dependency is stronger than an unowned physical-portion analogy.
5. 并之 and both 即得 occurrences must remain represented. It would be incomplete to retain only the three remainder facts and final23 while dropping method, generic cases and result claims.
6. The mathematics permits deriving140=2×70,63=3×21,30=2×15 and105=3×5×7. All four are **inferences**, not additional source-written equations. Likewise quotient witnesses7,4,3 and explicit remainder bounds are modern formal consequences/domain choices, not quoted Chinese clauses.
7. The source supplies no derivation of70/21/15, proof of uniqueness modulo105, or reason for choosing210. Those absent proofs cannot be fabricated as part of a complete source translation.

## Audit decision

The old source inventory is substantially complete and its major caveats stand. A complete conditional meaning model should keep the specific example and generic rule distinct; retain question/answer/method markers, repeated conditional assertions, placement/addition/subtraction/result roles, and unspecified generic reference scope. It should not claim that historical Chinese licenses a decimal renderer, hidden multiplication or normalization loop. No new RAW card is necessary for these clarifications; they audit IDEA000354 rather than introduce a distinct mechanism.
