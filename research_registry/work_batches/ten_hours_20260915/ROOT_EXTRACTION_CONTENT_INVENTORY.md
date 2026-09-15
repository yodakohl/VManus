# Fibonacci integer-root content inventory

2026-09-15. **Source-only, raw and unreviewed; no target test or codec.** This audit preserves the original IDEA000347 proposal and its evidence file unchanged. The separate [GDT909 correction](ROOT_EXTRACTION_PREDECESSOR_CORRECTION.md) is binding for subsequent predecessor descriptions: GDT909 partitions each whole paragraph into at least three equal-width steps, rather than requiring three equal-width paragraphs.

The source supplies a deterministic arithmetic dependency structure beyond endpoint triples. It does not yet supply a uniquely frozen full-content compiler. A generated computational reading is a legitimate explicit hypothesis to consider; its field and instruction serialization must be declared before target fitting. Variable Latin exposition is not, by itself, a reason to reject that hypothesis.

## What was inventoried

The accompanying [JSON inventory](ROOT_EXTRACTION_CONTENT_INVENTORY.json) covers the continuous initial integer-root sequence in Boncompagni's *Practica geometriae* edition, printed pp. 19–23: eleven worked examples, the intervening general rules, the immediately preceding three-digit rule, and the transition to fractional roots. It contains 78 source clauses and 206 annotated actions, placements, assertions, explanations and scope statements. These are editorial inventory counts; the annotation categories are **not an opcode alphabet** or a proposed number of written groups.

Each unit preserves normalized continuous Latin wording and its quote boundaries. Each clause has its source quotation, an ordered English content inventory, literal Arabic numeral occurrences, and explicitly marked inferred values where needed. Per-record table entries are retained as raw digit rows; they are not converted into a fabricated chronological trace. Lexical numerals such as *unum*, *binarium*, *zefiro* and *nihil* remain visible in the quotation and are identified in the content annotations where relevant. They are not falsely presented as literal Arabic number fields.

All five primary printed pages were actually inspected through `view_image`. The cached chapter text layer was navigation only: its OCR confuses several numerals. Native manuscript ff. 11v–14r were also inspected over the source-supply and audit tasks, with new native checks of 13r, 13v and 14r in this audit. The inventory witness remains the **printed prose plus its owned printed table**, with conflicts preserved. Manuscript readings are separately attributed comparisons. This is a single-producer normalized source reading, not an independently validated diplomatic transcription.

The [bounded chapter PDF](https://www.e-rara.ch/download/pdf/10910692.pdf) contains printed pp. 18–29. The integer-root sequence ends before the explicit *Nam si fractiones* transition on p. 23. The later fractional/unit conversions, geometric root construction and arithmetic on roots are outside this program subset. The earlier elementary square table and definitions are prerequisites outside the bounded block. Editorial marginal collation notes, page headers, printer signatures and ornamental table borders are explicitly outside the medieval computational content being inventoried.

## Source sequence and prerequisite ownership

| Unit | Content | Input | Called prefix root | New root, remainder | Printed pages |
| --- | --- | --- | --- | --- | --- |
| U00 | General three-digit rule; placement, choice condition, residual bound, zero-prefix advice | — | — | — | 19 |
| R01 | Worked extraction | 153 | 1 → 1; zero residual inferred | 12, 9 | 19 |
| R02 | Worked extraction with quotient estimate and judgment | 864 | 8 → 2, residual 4 | 29, 23 | 19 |
| R03 | Worked extraction reaching the equality bound | 960 | 9 → 3; zero residual inferred | 30, 60 | 19–20 |
| U01 | Four-digit recursion rule | — | root of leading two digits | — | 20 |
| R04 | Worked extraction with operation-count explanation | 1234 | 12 → 3, residual 3 | 35, 9 | 20 |
| R05 | Worked extraction using a two-digit doubled prefix | 6142 | 61 → 7, residual 12 | 78, 58 | 20 |
| R06 | Zero next digit, justified by two alternative place arguments | 8172 | 81 → 9; zero residual inferred | 90, 72 | 20–21 |
| U02 | Five-digit recursion and placement rule | — | root of leading three digits | — | 21 |
| R07 | Worked extraction and explicit modular verification | 12345 | 123 → 11, residual 2 | 111, 24 | 21 |
| R08 | Worked extraction with quotient estimate | 98765 | 987 → 31, residual 26 | 314, 169 | 21–22 |
| U03 | Six-digit recursion rule | — | root of leading four digits | — | 22 |
| R09 | Worked extension of an earlier result | 123456 | **R04:** 1234 → 35, residual 9 | 351, 255 | 22 |
| R10 | Worked extraction using a three-digit doubled prefix | 987654 | 9876 → 99, residual 75 | 993, 1605 | 22 |
| U04 | Seven-digit recursion rule | — | root of leading five digits | — | 22 |
| R11 | Worked extension of an earlier result | 9876543 | **R08:** 98765 → 314, residual 169 | 3142, 4379 | 22–23 |
| U05 | Eight-digit/general recursion; parity rule for root digit count | — | root of leading six digits, then generalization | — | 23 |
| U06 | Transition to fractional roots and distinction between geometrical and astronomical units | — | — | — | 23 |

The prefix results are source-written calls or assertions. Their numerical validity can be checked, but their internal calculation is generally **not written out within the corresponding record**. Only two prefix calls directly reuse earlier worked examples in this bounded sequence: R04 → R09 and R08 → R11. Calling them all complete fully unrolled traces would add unwritten content.

The source counts partial products to determine where subtraction begins. With doubled prefix 4, the 864 example has the cross product and the chosen digit's square. With doubled prefix 14, the 6142 example uses products by its separate digits 1 and 4, then the square. With doubled prefix 198, the 987654 example uses products by 1, 9 and 8, then the square. Their alignment is part of the source's stated reasoning. These are ordered dependencies, not merely a collection of arithmetically true numbers.

## Complete 12345 record

R07 is wholly on [printed p. 21](https://www.e-rara.ch/i3f/v20/10608493/full/full/0/default.jpg). It begins *Verbi gratia: uolumus inuenire radicem de 12345* and ends *et secundum hunc modum probabis semper in inuentione radicum*, immediately before the 98765 example. Its full normalized text is in the JSON, divided into ten exhaustive clauses. It has 305 whitespace tokens, including 56 literal Arabic numeral occurrences. This count is a transcription property, not a candidate target length.

The full mathematical and instructional content is:

1. Declare input 12345 and call the prefix result 123 → root 11, residual 2.
2. Place the two root digits beneath input digits 3 and 4. Double 11 to 22, place it below the root, and put residual 2 above input digit 3.
3. Join residual 2 to the remaining input digits, obtaining 245. State that three working digits correspond to three required products.
4. Choose a digit whose products by the first 2, the second 2 and itself can be subtracted in sequence from the respective working places. Explicitly choose 1.
5. Remove 1 times the first 2 from residual 2. Nothing remains; the source writes *nihil*, not Arabic 0.
6. Remove 1 times the next 2 from input digit 4, leaving 2 above it.
7. Join that 2 to units digit 5, obtaining 25; remove 1 squared, explicitly 1, leaving 24. State root 111 and remainder 24.
8. Give a general check: square the check of 111, take its check, add the check of 24, and compare with the check of 12345. The text allows a chosen proof/check procedure before giving its concrete modulus.
9. Work the concrete proof modulo 7: 111 gives residue 6; 6 squared is 36; 36 gives residue 1; 24 gives residue 3; 1 plus 3 gives 4; 12345 also gives residue 4. The source states the 111 division twice, first as the check value and then as its explanation. Both statements remain in the inventory.
10. Close the proof and instruct the reader to use this checking method generally when finding roots.

The source says a matching proof shows the work is right. A single modular congruence is mathematically necessary rather than sufficient for exact correctness; the inventory preserves that source assertion without promoting it to a valid sufficiency theorem. The exact root result also depends on the digit computation and residual bound. The proof's intermediate values are prose-owned; they are absent from the accompanying numerical table.

Under the normalized literal reading, 111 occurs four times, 24 four times, 7 four times, and 12345 five times in this record's prose. These repeated values could impose equality constraints under a later fixed global numeral encoder. A content compiler might instead coalesce repeated explanatory assertions; that would be an explicit compiler policy, and these literal counts would then cease to be its predicted record counts.

## Source conflicts and corrections retained

- **8172:** printed prose and endpoint give 8172, but the owned p. 20 table reads `81.71`. Native Urb. lat. 292 f. 12v has 8172 in prose and table. The JSON retains the printed table string and marks a witness conflict. It does not replace the printed input with the mathematically convenient one.
- **123456 placement:** the printed p. 22 prose instructs that residual 9 be put *sub 4*, while the owned table puts 9 above the input row. Native f. 13v appears to read *super 4* and agrees with the above-input placement. The print's instruction and its table remain distinct in the inventory. This does not alter the numerical endpoint, but it matters for a model that includes all placements.
- **864 anchor correction:** the original source-supply dossier's explanation of *1 super 4* was too loose: the relevant 4 is the earlier residual placed over the leading 8, not the original units digit 4. The source diagram places the 1 over that working position. The new annotation distinguishes these two written 4 objects; the old dossier and its bound evidence hash remain unchanged.
- **960:** its remainder 60 equals twice root 30. A general strict `< 2r` bound is false for the supplied source family. The general integer-root condition is `0 <= s <= 2r`.
- **Table completeness:** R11 instructs the doubled root digits 6, 2 and 8 and subsequently names 628, but its printed and native tables do not retain a doubled-628 row. The other tables also omit some prose intermediates. Complete prose-plus-table ownership is different from every arithmetic intermediate having a drawn row.

## One strongest computational architecture

Retain one architecture for later review: **a root-extension dependency program with named prerequisite calls, ordered partial-product subtractions, chosen-digit constraints, endpoint assertions and a typed modular-check block**. It can be a hypothetical compact reading of computational content. It does not require an assumption that Latin is copied phonetically or that the historical prose used a fixed-width ledger.

The common arithmetic step is deterministic. Let the source-called prefix result satisfy `P = a*a + s`, with `0 <= s <= 2*a`. Let `b` be the next two input digits interpreted numerically, `0 <= b <= 99`. Form:

```text
X = 100*s + b
r = 10*a + q
t = X - q*(20*a + q)
```

Choose the digit `q` from 0 through 9 so that `0 <= t <= 2*r`. For a valid prefix state and input pair this identifies the unique next digit. Increasing `q` by one increases the removed quantity by `2*r + 1`; the residual bound therefore excludes the next digit. This algebra is our modern statement of the source's numerical consequence, not a historical written formula.

The source's successive products by the digits of `2*a` implement the cross product, with the final subtraction of `q*q`. The source-specified place counts determine the order and alignment of those partial products. A generated trace can consequently predict a series of carries/residuals and the final greatest-digit condition, rather than just three terminal numbers.

For 12345 the explicitly called prefix is `123 = 11*11 + 2`. Then `X = 245`, `q = 1`, `r = 111` and `t = 24`. The written partial-product progression and the independently written modulo-7 check are both consequences of those same values. For 864, the same compact algebra uses `X = 464`, although the source writes the staged working values 46 and 104 rather than a literal 464. A generated 464 field would therefore be an **inferred execution value**, not a recovered source-written number occurrence.

The zero next digit in 8172 needs an explicit trace policy: the source proves that zero is required by place arguments and does not write out three zero-product subtraction stages. A full generated trace may introduce those implicit stages if the hypothesis says so in advance. It must not then be described as the literal written source record.

The modular check is similarly separable. R07 instructs that the method be used generally, but later records do not write all its intermediates. A uniformly checked generated algorithm is possible as a declared content model; a claim that all eleven historical records literally contain that same proof block is false.

## What remains underdefined

The arithmetic semantics are sufficiently constrained for a finite conditional model. The complete source-to-code projection is still underdefined. A source inventory can make every clause visible without fixing how many encoded instructions any clause produces.

Before a decoder, one global policy must settle:

1. Whether the model encodes the eleven historical input instances or arbitrary inputs to the same algorithm, with an independently declared finite bound.
2. Whether prerequisite-root calls remain atomic or are expanded recursively. Expanded results are computed content; the historical record generally does not write their internal steps.
3. Whether digit placements, operation-count explanations, alternative proofs, experience advice and repeated assertions are preserved as typed content or explicitly excluded from a narrower mathematical program subset. The full source inventory retains all of them either way.
4. Whether zero-digit cases and checks receive full generated traces, and whether the modular check is part of every record or a fixed checked-record class.
5. How printed prose/table conflicts enter the source contract. A model that demands both inconsistent literals cannot quietly substitute the native reading after a fit fails.
6. The operator and reference vocabulary, numerical notation, serialization, global code and complete target-record ownership. None is chosen here.

Once those policies are frozen, a global numeral/operator encoder yields code-specific consequences: repeated value identity, source-ordered operator and operand reuse, dependent partial-product residuals, exact digit admissibility and proof-value consistency. Before then, the source alone does not predict a particular codeword, target group count or unique ciphertext pattern. This is an unfinished model definition, not a failed target experiment or a reason to reopen the unchanged GDT902/GDT909 models.

Smallest next step: root and the independent critic choose one explicit mathematical-content subset and uniform compiler policy, then decide whether a necessary target-capacity consequence exists before implementation. This source audit does not build that compiler or change the idea's unreviewed status.

## Receipts and validation

Public source links and SHA-256 receipts are inside the JSON. New native comparisons were fetched and actually viewed:

| Native source | Public URL | SHA-256 |
| --- | --- | --- |
| f. 13r, full 12345 calculation and proof | <https://digi.vatlib.it/iiifimage/MSS_Urb.lat.292/Urb.lat.292_0031_fa_0013r.jp2/full/full/0/default.jpg> | `4061ea66b38ff532a80d6c8f6c83dff1f79bdbc17432064e769faa837d7acd8c` |
| f. 13v, 123456 and 987654 | <https://digi.vatlib.it/iiifimage/MSS_Urb.lat.292/Urb.lat.292_0032_fa_0013v.jp2/full/full/0/default.jpg> | `8d845a13ff52bb4d48433c6c5c6b61d328d7115e825daf8efffcf3cf53c895e0` |
| f. 14r, final example and general rules | <https://digi.vatlib.it/iiifimage/MSS_Urb.lat.292/Urb.lat.292_0033_fa_0014r.jp2/full/full/0/default.jpg> | `52d3b910a4ec91451f7e3857236d4aabb66523ee18500de53306dfaa6c952eb1` |

The eleven prose endpoint triples, explicit numerical intermediate calculations and 12345 proof were arithmetically checked separately from transcription. These checks establish consistency of the annotations, not manuscript meaning, source palaeography or a code. The source-specific contradictions remain present. JSON structure, quote reconstruction, local links, old evidence preservation and publication-string checks are performed before handoff.

No target text/image, reserve, contact, decoder, new idea card, route or legacy ledger is part of this audit. Source image files remain outside the published tree.
