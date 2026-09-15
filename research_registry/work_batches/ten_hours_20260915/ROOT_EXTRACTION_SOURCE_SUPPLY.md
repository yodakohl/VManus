# Complete worked square-root source supply

Source-only dossier, 2026-09-15. Status: **RAW_UNREVIEWED CONTENT PROPOSAL; NOT SELECTED; NO TARGET TEST**. No Voynich text, image, reserve, or contact was accessed for this supply task. Root owns experimental selection and publication.

Fibonacci's complete worked extraction of the integer square root of 864 is a real sustained instruction passage with an owned numerical table and dependent arithmetic end conditions. It supplies a distinct nonastronomical meaning candidate. It does not establish a Voynich numeral system, record boundary, or complete text encoding.

## Primary record and dating

- Leonardo of Pisa, *Practica geometriae*, distinctio II, complete 864 example. The work's rubric gives 1220. The [Jordanus catalogue entry for Urb. lat. 292](https://ptolemaeus.badw.de/jordanus/ms/10331), sourced to Stornajolo's direct manuscript catalogue, records that rubric and dates the **witness to the fifteenth century**. This bounded lookup does not establish a pre-1450 date for this particular copy; composition date and witness date must remain separate.
- The actual record begins in the last two manuscript lines of [Urb. lat. 292, f. 11v](https://digi.vatlib.it/view/MSS_Urb.lat.292/0028), and ends in the upper part of [f. 12r](https://digi.vatlib.it/view/MSS_Urb.lat.292/0029), with the owned red numerical table at the right. Both full native page images were downloaded and actually inspected through `view_image`. No enhanced or reconstructed diagram was substituted.
- The complete passage and its table appear together on printed p. 19 of Boncompagni's 1862 edition, *La practica geometriae di Leonardo Pisano, secondo la lezione del codice urbinate no. 292 della Biblioteca Vaticana*, ETH-Bibliothek Rar 29283: 2. [Catalogue and Public Domain Mark](https://www.e-rara.ch/zut/content/titleinfo/10608466); [persistent volume identifier](https://doi.org/10.3931/e-rara-34353); [direct primary p. 19 image](https://www.e-rara.ch/i3f/v20/10608491/full/full/0/default.jpg). This full page was also inspected through `view_image`.
- The route to the example came from Steihaug's 2024 [original research paper](https://arxiv.org/html/2401.12016v1). That paper was navigation, not the authority for the historical wording: its liberal English translation explicitly uses automated translation. The source below was checked against the printed primary edition and the manuscript. No modern reconstructed table is used as the medieval output.

The manuscript's angular numeral 3 initially looked ambiguous at this display scale. The printed primary edition explicitly reads 23, twice, and also prints 23 in the owned table. This dossier makes **no claim of a manuscript arithmetic error** from that visual ambiguity, and does not silently amend a confirmed alternate reading.

## Complete source content and dependencies

The unit is the entire 864 paragraph **plus its table**. A page turn does not make two independent records. The preceding 153 example and following 960 example have their own inputs and tables. The 864 instruction begins with “Item si uis inuenire radicem de 864”; it ends with “que 23 sunt minus dupla radicis inuencte.” These are source boundaries, not fitted target boundaries.

| Source step | Values and dependency | Written ownership |
| --- | --- | --- |
| Initial root digit | The integer root of 8 is 2; put 2 below 6 in 864. | Prose and root row of table. |
| Initial residual | Removing the square of 2 from 8 leaves 4; put that 4 above 8. | Prose describes the residual; table shows its position. The expression 8 minus 2 squared is our explicit arithmetic expansion. |
| Double the root digit | Double 2 to get 4; put it below 2. | Prose and bottom row of table. |
| Form trial quotient | Combine residual 4 with the second digit 6 to get 46; divide by 4, obtaining 11 as an integer estimate. | Prose. The quotient is an estimate, not the selected root digit. |
| Choose the next digit | Choose 9, less than the estimate 11, to stand below the first-place digit. | Prose explicitly uses judgment, *arbitrio*; table has 9. |
| Subtract the cross product | Multiply 9 by the doubled digit 4 and remove it from 46, leaving 10. Put 0 above 6 and 1 above 4. | Prose and two positioned digits in table. |
| Bring down the last digit | Combine 10 with the original units digit 4 to get 104. | Prose; 104 is not a separate retained table row. |
| Subtract the new digit's square | Remove 9 squared from 104, leaving 23. | Prose and bracketed remainder in table. |
| Certify the result | 23 is less than twice the found root. The table's root digits are 2 and 9, giving 29. | Final prose inequality and owned table. |

Modern arithmetic verification of those declared values is exact:

```text
8 - 2*2 = 4
10*4 + 6 = 46
floor(46/4) = 11
46 - 9*4 = 10
10*10 + 4 = 104
104 - 9*9 = 23
29*29 + 23 = 864
0 <= 23 <= 2*29
29*29 <= 864 < 30*30
```

The last two identities spell out why the calculation certifies the integer root. The source does not spell out the sentence `29*29 + 23 = 864`; that identity is entailed by its dependent steps and numerical table. This is a semantic consequence, not an extra written field we may pretend the source contains.

The table retains the input 864, root 29, doubled first root digit 4, positioned residual digits, and remainder 23. It **does not retain every intermediate object**: 46, 11, and 104 are explicitly explained in the prose but do not each receive their own table row. Thus a historical fixed seven-field ledger, equal-width paragraph chain, or all-intermediates-visible table cannot be inferred from this example.

The immediately following 960 example is an important known boundary case. Its table on the same printed page gives root 30, doubled first digit 6, and remainder 60. Accordingly a general integer-root condition must allow `remainder = 2*root`; the general condition is `0 <= remainder <= 2*root`, while the 864 example happens to meet the stronger strict inequality. This is source-side scope control, not a target-driven repair.

The entire 960 example was read across printed pp. 19–20, with p. 20 also inspected through `view_image`. Its operational inventory is: root of 9 is 3; double 3 to 6; choose next digit 0; multiply 0 by 6 and remove the product from 6, retaining 6; combine that 6 with the units 0, producing 60; remove 0 squared; retain 60 and explicitly identify it as twice the found root 30. The words directly name 960, 9, 3, 6, 0, 60 and 30. The table owns the root 30. Expressions `30*30 + 60 = 960` and `31*31 = 961` are our entailed checks, not additional source-written fields.

## Public-domain transcription of the complete paragraph

Transcribed from the inspected Boncompagni p. 19 scan; line-break hyphenation and numeral-surrounding printer's dots are removed, and the printed ae form is represented as `e` as in ordinary searchable Latin. This is a normalized source reading, not a frozen diplomatic character stream or a translation. The accompanying table is described above rather than republished as pixels.

> Item si uis inuenire radicem de 864, pone 2 sub 6, cum 2 sint integra radix de 8; et 4 que remanent pone super 8: deinde dupla ipsa 2, erunt 4, que pone sub 2; et per ipsa 4 diuide 46, scilicet copulationem superflui tertie figure cum secunda, exibunt 11: ex qua diuisione possumus habere arbitrium sequentis ponende figure, que multiplicanda est per duplum prime figure posite; et postea per se ipsam, erit ipsa figura aut parum minus, aut totidem quantum ex ipsa diuisione euenit; quod cognosces ex usu. Quare ponemus arbitrio 9 sub prima figura, que sunt minus de 11 predictis; et multiplicabis 9 per 4, scilicet per duplum inuenti binarij, et extrahes de 46 predictis, et ex remanentibus 10 pones 0 super 6, et 1 super 4; et copulabis ipsa 10 cum 4 primi gradus, erunt 104; de quibus extracta multiplicatione nouenarij in se ipso, remanent 23; que 23 sunt minus dupla radicis inuencte.

That normalized 864 paragraph has **156 whitespace-separated words and numeral tokens**. Its prose explicitly names 864, 2, 6, 8, 4, 46, 11, 9, 10, 0, 1, 104 and 23. The root 29 is explicitly drawn as two digits in the table. Values 36, 81, 841, 58 and 900 in a fully expanded arithmetic check are inferred computations; they are not five additional literal fields in this paragraph.

Complete 960 paragraph, with the same normalization, checked across the printed page turn:

> Rursus si radicem de 960 inuenire uolueris, pone radicem de 9, scilicet 3 sub 6; et duplica ipsa 3, erunt 6, que pones sub ipso 3; per que 6 oportet quamdam figuram multiplicare, que ponenda est ante 3; et ipsam multiplicationem de 6 superiore extrahere, et remaneat inde figura; que cum fuerit copulata cum 0; et possis extrahere multiplicationem ipsius figure in se ipsam, et non remaneat ultra duplum radicis inuente; eritque illa figura 0: quod 0 cum multiplicatum fuerit per 6, que fuerunt duplum de 3; et ipsa multiplicatio extracta fuerit de 6, remanebunt eadem 6; que cum copulata fuerint cum 0, quod est in primo gradu, faciunt 60; de quibus 60 cum extracta fuerit multiplicatio de 0 in se ipso, remanebunt 60, que sunt duplum de 30, scilicet de radice inuenta.

## Bounded chapter inventory before target selection

The publisher's [Distinctio secunda PDF](https://www.e-rara.ch/download/pdf/10910692.pdf) supplies printed pp. 18–29, including the preceding section's ending on p. 18. The actual section opens there with *Incipit capitulum de inuenctione radicum*. Its initial integer-root worked sequence occupies pp. 19–23; the closing paragraph generalizes to eight-digit and arbitrary-length inputs, then explicitly switches to fractional roots and units at “Nam si fractiones”. The later material includes dimensional/fractional roots, a geometric construction, and arithmetic on roots. It must not be silently bundled into a fixed integer-root codec.

All five printed native pages 19–23 were inspected through `view_image`; the bounded chapter's text layer was also read as navigation, not accepted as an error-free numeric transcription. There are **11 named worked integer-root inputs in this initial sequence**, in the following source order. This inventory defines a bounded source family; it is not an experimental selection or a claim that every prose/table numeral has received diplomatic validation.

| Input | Stated root | Stated remainder | Printed span | Source completeness qualification |
| --- | --- | --- | --- | --- |
| 153 | 12 | 9 | 19 | Worked from the first digit; owns table. |
| 864 | 29 | 23 | 19 | Complete normalized paragraph above; owns table. |
| 960 | 30 | 60 | 19–20 | Complete normalized paragraph above; equality boundary case. |
| 1234 | 35 | 9 | 20 | Worked digit extension; owns table. |
| 6142 | 78 | 58 | 20 | Worked digit extension; owns table. |
| 8172 | 90 | 72 | 20–21 | Zero final digit; printed table has 8171 whereas printed prose and native manuscript prose/table have 8172; see the explicit witness comparison below. |
| 12345 | 111 | 24 | 21 | Takes root of 123 as 11 with remainder 2; then computes the extension and an explicit modulo-7 proof. |
| 98765 | 314 | 169 | 21–22 | Takes root of 987 as 31 with remainder 26; computes extension. |
| 123456 | 351 | 255 | 22 | Takes root of 1234 as the earlier 35 with remainder 9; computes extension. |
| 987654 | 993 | 1605 | 22 | Takes root of 9876 as 99 with remainder 75; computes extension. |
| 9876543 | 3142 | 4379 | 22–23 | Takes root of 98765 as the earlier 314 with remainder 169; computes extension. |

The larger examples really refer to prior root results; their prose is not a fully unrolled trace from the first digit. A source-derived content projection can preserve such named prerequisite calls, but a fully expanded modern trace is a different explicit hypothesis. Neither may quietly replace the source's written content.

**Retained edition countercase:** the 8172 example's printed p. 20 table visibly reads `81.71`, although its prose says 8172. A targeted native check of [Urb. lat. 292, f. 12v](https://digi.vatlib.it/view/MSS_Urb.lat.292/0030), actually inspected through `view_image` together with the full printed page at original detail, shows 8172 in both its prose and red table, with root 90 and remainder 72. The manuscript and print must not be treated as one error-free literal stream. A later source freeze must choose an explicit witness/correction policy before target fit; this dossier preserves the discrepancy and does not amend the printed primary bytes. The eleven prose endpoint triples listed above all satisfy their exact square-plus-remainder identity and non-strict remainder bound by independent arithmetic.

The **12345 record has a particularly useful independent written check**, directly visible on p. 21 after the endpoint 111 with remainder 24. It directs the reader to check the square of the root, add the check of the remainder, and compare with the check of the input; then works the check modulo 7. Explicitly named values are `111 mod 7 = 6`, `6*6 = 36`, `36 mod 7 = 1`, `24 mod 7 = 3`, `1 + 3 = 4`, and `12345 mod 7 = 4`. This is an actual source-written proof sequence, not a modern appended field. Congruence alone is not sufficient to prove the exact square-root result; it is a necessary check combined with the digit computations and residual bound.

The full content of the 12345 example is visible on a single [primary p. 21 image](https://www.e-rara.ch/i3f/v20/10608493/full/full/0/default.jpg), from “Verbi gratia: uolumus inuenire radicem de 12345” through “et secundum hunc modum probabis semper in inuentione radicum”, immediately before the 98765 example. This bounded source gives a longer complete record with explicit dependent verification if the 864 record is insufficient for a later content projection.

## Distinction from predecessors and decision relevance

Current route and `context topic numbers` were read first. Bounded idea searches and duplicate/route screens for square-root extraction, algorism and common-measure chains were navigation checks, not novelty proofs. Additional literal searches for `Fibonacci`, `algorithmus` and `square-root extraction` and a combined duplicate screen were completed before proposal retention; their lexical results do not establish an absence of prior work. The relevant claim-bearing predecessors were then read directly:

- [GDT902 primary report](../../../experiments/yolo/gdt902_treviso_complete_multiplication_register/REPORT.md): its frozen Treviso multiplication table had complete equations under particular global word/numeral encodings. The root candidate has iterative residuals and a nonlinear terminal square identity; it does not reopen that failed table model.
- [GDT909 primary report](../../../experiments/yolo/gdt909_worked_division_chains/REPORT.md): three or more equal-sized consecutive paragraphs with four single-group fields and constant remaining columns were eliminated by a necessary recurrence pattern. Fibonacci's actual prose is not that record template. Unequal prose must not be converted into an exemption to the old model; a genuinely new whole-record contract would have to be supplied before testing.
- [IDEA000126 source proposal](../../proposals/astronomical_arithmetic_register_program.json): related broad architecture of complete executable arithmetic records, but its exact historical canon was absent. The present source provides actual nonastronomical wording, placement instructions and owned outputs. It does not solve the shared problem of deriving a complete written encoding from the source.

Unknowns that a later review must resolve, before code or target access:

1. Whether the complete historical prose and table can specify a finite, independently frozen meaning model for whole manuscript records. A hypothetical compact **content projection** need not copy Latin phonetically, but it must declare what it preserves, what is implicit and how every written group is generated. Merely retaining the nine arithmetic relations and calling them the full historical record is insufficient. No fixed seven- or twelve-field format follows from the source.
2. How the trial-digit judgment is represented. In this example 9 is explicitly given and verified; the general instructions do not give a simple unconditional mapping from the estimate 11 to 9. No modern deterministic replacement is silently inherited.
3. What owns target input, output, paragraph boundaries and numeric roles, and whether a single global numeral/operator/word treatment can cover all written groups. None is supplied by the fact that 29 squared plus 23 equals 864.
4. Whether a sufficiently dated witness and independent next complete example can be frozen without looking at target fit. The work is dated 1220; this inspected witness is catalogued only to the fifteenth century. Adjacent examples are source supply, not held target confirmation.

Smallest adequate next review: a source-only whole-record serialization and ownership audit, bounded to 20 minutes, with no decoder. If it yields no independently fixed complete written contract, retain a raw idea with missing meaning binding. If it yields one, root can decide whether an admitted target has the necessary record capacity before implementation. This bounded source supply itself makes no manuscript finding and no experimental PASS or FAIL.

## Reproducible source receipts

Hashes identify fetched bytes on 2026-09-15, not authenticity certificates. Images stay outside the published tree; these are public URLs and hashes only.

| Resource | Public URL | SHA-256 |
| --- | --- | --- |
| Vatican manifest | <https://digi.vatlib.it/iiif/MSS_Urb.lat.292/manifest.json> | `ceb392b97cff4e405b753caff6a5eb3be078d5ac5fe956e38dab17f05484ff08` |
| Native f. 11v | <https://digi.vatlib.it/iiifimage/MSS_Urb.lat.292/Urb.lat.292_0028_fa_0011v.jp2/full/full/0/default.jpg> | `8dc30562905ffa8892aa85b11db3da9d1823b3ede74772b9edb903ffaf6d5315` |
| Native f. 12r | <https://digi.vatlib.it/iiifimage/MSS_Urb.lat.292/Urb.lat.292_0029_fa_0012r.jp2/full/full/0/default.jpg> | `2e1499d9236163fdc023f3b06a79994a1cba3a3282c126ce18309d2eaaa2fc26` |
| Native f. 12v | <https://digi.vatlib.it/iiifimage/MSS_Urb.lat.292/Urb.lat.292_0030_fa_0012v.jp2/full/full/0/default.jpg> | `c268bfb77d18a837a835a0ee4912b0a349097d374008ec0febec06aab7bf43fc` |
| Boncompagni p. 19 | <https://www.e-rara.ch/i3f/v20/10608491/full/full/0/default.jpg> | `88a6900c8421d7a6610a59fd544e983910004cf910da16b66b52c1c1c82769f6` |
| Boncompagni p. 20 | <https://www.e-rara.ch/i3f/v20/10608492/full/full/0/default.jpg> | `d18da8f3dc0445b123e7d9731437979ffd68f56df3782c074b10b42d77ce6429` |
| Boncompagni p. 21 | <https://www.e-rara.ch/i3f/v20/10608493/full/full/0/default.jpg> | `0f977ce632e5e24b9e789eb2f97be494ad251b1426a6e775e3a96c2d397c7555` |
| Boncompagni p. 22 | <https://www.e-rara.ch/i3f/v20/10608494/full/full/0/default.jpg> | `9ae86bc4ddea4be8a1e3781ad4a4c83ee631545dd5b4b47dc5cf29e4c72ee38f` |
| Boncompagni p. 23 | <https://www.e-rara.ch/i3f/v20/10608495/full/full/0/default.jpg> | `e8a84688ed2185177e86dff507939616e52b1fd0fe3a563662516a6fbaa951a3` |
| Bounded Distinctio II PDF | <https://www.e-rara.ch/download/pdf/10910692.pdf> | `3d6dfd4c2b9de01f603d7d5ace9da28e48aca1d52b0f9f4f401ab21ba803427d` |
| Boncompagni volume II manifest | <https://www.e-rara.ch/i3f/v20/10608466/manifest> | `e3111f9518df3246b24286d83f9d7fdecdce78813444dce6a85091a9bbe0205a` |
| Jordanus manuscript catalogue | <https://ptolemaeus.badw.de/jordanus/ms/10331> | `73346b7b3062e187c6f81fdd05b6ad3837d1610a93ae036fbae995a331999f8e` |

No source pixels, machine paths, target excerpts, new decoder, experimental manifest, ledger entry or route change are part of this source-only artifact.
