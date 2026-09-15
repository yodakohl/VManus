# Independent Geniza source-model preflight

Reviewed 2026-09-15, before target fitting. Scope: exact source forms and offsets,
complete clauses, finite generation, morphology, references and condition/outcome
bindings. No target text, target solver or reserve was inspected.

## Final specification verdict

**SOURCE_MODEL_PREFLIGHT_PASS — ready to freeze as the stated restricted
constructive hypothesis.** This verdict binds
[`GENIZA_CONSTRUCTIVE_SPEC.json`](GENIZA_CONSTRUCTIVE_SPEC.json), SHA-256
`15cecdcd70307bad9e386581e72c06ddd769a1d29187b95f3a0fbaab40a1fe17`.
Its source packet hash is
`8e2246879c5b2dd1e8f00600fda7f8110c997c0cdaed4f56cb07ff003f23ed36`.

The separate background file `GENIZA_FINITE_CLAUSE_GRAMMAR.json` does not
control this specification. The final specification explicitly supersedes
the background's no-cross-fruit policy. Source-derived words and constructions
may therefore form new propositions; these are not attributed to the source
as historical medical statements.

## Independent mechanical reconstruction

The reviewer independently checked the source packet hash, rebuilt its
157-form vocabulary and 32-unit NFD grapheme inventory, checked every listed
slot-word occurrence against all three source records, and checked all five
extension strings against their exact contiguous source-word intervals.
No letters, marks, final forms or unattested words were substituted.

| Extension | Exact source interval, 1-based inclusive | Words | Completeness and binding |
| --- | --- | ---: | --- |
| SOUR | POMEGRANATE 3–12 | 10 | Complete conditional with the strong-cold and balanced-moisture/dryness predicates; its initial pronoun obtains the named fruit from BASE. |
| SWEET | QUINCE 48–57 | 10 | Complete conditional with a balanced-temperament predicate; ends before the subsequent comparison. |
| UNRIPE | QUINCE 21–35 | 15 | Complete conditional retaining digestion, stomach-departure and binding complements. |
| JUICE_BODY | QUINCE 66–75 | 10 | Paired comparison of the named fruit's juice/water and bulk/flesh. This lexical rendering is a declared working interpretation of text omitted from the public English translation. |
| BEFORE_AFTER | QUINCE 7–18 | 12 | The first participial predicate continues BASE's named subject; the following finite clause retains that subject. The first half is not represented as an autonomous clause. |

Independent enumeration of all choices reproduces **81 distinct paragraphs**:
9 SOUR, 9 SWEET, 9 UNRIPE, 27 JUICE_BODY and 27 BEFORE_AFTER. All are inside
the declared 12–24-word source scope; their actual lengths are 12–18 words.

| Words | Products |
| ---: | ---: |
| 12 | 9 |
| 13 | 24 |
| 14 | 15 |
| 15 | 12 |
| 16 | 12 |
| 17 | 3 |
| 18 | 6 |

The generated language uses **48 source word forms and 28 source units**.
`דֹֹֹ`, `טֹ`, `ף`, and `צ` never occur in any generated product. Their code
values remain unobserved; the declared full 32-unit codebook-completion check
is therefore necessary even if every product were represented. It must use
the fixed global target alphabet, not an alphabet inferred from one paragraph.

## Grammar and discourse assessment

The three heads take the explicitly assumed compatible masculine
singular/collective analyses. The two possible modifiers retain definite
marking, and the bare property predicates retain their unprefixed forms.
These are linked finite analyses, not permission to generate new inflections.
The marked pomegranate head remains its literal edition-level spelling.

Every generated paragraph names exactly one fruit before using its anaphoric
forms. Juice and bulk refer to that same fruit. Physiological effects refer to
the generic eater; no particular woman or other absent patient is silently
introduced. The conditional extensions restrict a variant or circumstance;
their predicates override the generic BASE description within that circumstance
under the explicitly stated discourse hypothesis. No conditional outcome is
reported as an observed event.

The compatibility rule excludes the 54 raw products that would combine an
explicit sweet/sour nominal modifier with one of the SOUR, SWEET or UNRIPE
conditional extensions. Each extension's condition and outcome remain an
inseparable token sequence. Swapping before/after effects, exchanging juice
and bulk effects, deleting the initial subject, introducing an unlicensed
feminine ending, or adding another fruit is outside this finite product rule.
These are consequences of the declared restricted language, not general
judgments that every excluded sentence is impossible Arabic.

The nominal BASE plus SOUR/SWEET/UNRIPE or JUICE_BODY is a complete discourse
under those assumptions. BASE plus BEFORE_AFTER supplies a continued
participial predicate and a second finite predicate with contrasting eating
conditions. Nothing in this review requires a confirmed Voynich meaning.
A future exact code witness would still need whole-paragraph reencoding and
its full ambiguity report; the source preflight establishes no target fit.

## Copied material versus actual generation

All five extensions are copied, complete source constituents. The full
paragraphs arise from an explicit finite product over fruit heads, definite
modifiers and linked bare-predicate alternatives, subject to the compatibility
restriction. This is genuine specified recombination, although narrowly
constrained and heavily dependent on five fixed source sequences. It is not
a broad productive Arabic grammar or a free per-word gloss code.

New fruit/property combinations can differ from PGP's statements. The
specification correctly calls them generated propositions and fixes the
underlying word spellings and shared grapheme code. Clinical truth of those
new propositions is not asserted. The independent question is whether this
finite source-derived discourse language has a representation under the
declared writing channel in the separately registered target scope.

## Background inventory review and corrections

The earlier 14-template draft initially contained accidental Arabic letters
inside purportedly exact Hebrew-script strings, an added holam in T07, and
incomplete starts in T02/T03. These were reported directly to the producer.
The later background revision inspected at 09:04 UTC had JSON SHA-256
`1ec8ad5fd0db664cdcb6e2c346862ee948f0cfc79b21a921a4c7b2a5ad15f590`.
Its token strings all matched contiguous source passages, but the following
table records the remaining distinction between exact copying and clause
completeness. The producer may correct this background separately; those
corrections do not alter the final specification reviewed above.

| Template | Source/clause assessment |
| --- | --- |
| T01 | Exact three-word headed nominal property clause; source continues with other predicates. Fixed constituent, no productive slots yet. |
| T02 | The inspected full-line repair PEACH 1–22 ends in dangling `ומא כאן`. A complete intended comparison requires PEACH 6–20, or 1–20 if the head and preceding properties are retained. Not a complete-clause PASS at that hash. |
| T03 | The inspected full-line repair PEACH 15–52 includes previous material and ends in dangling `ומתי אכלה אצחאב`. The intended full contrast is PEACH 21–49. Its corrected working reading concerns peaches whose pits detach or adhere, not digestion of a soft/hard pit. |
| T04 | Complete source instruction with prior peach reference; its three offered follow-ups are an observed disjunction, not yet an encoded substitution rule. |
| T05 | Complete pomegranate head and sour-variant predicate sequence; preserve the coordinated stomach/liver context for the modifier. |
| T06 | Complete seed-of-sour-pomegranate conditional; the predicate/object sequence is not idafa. The r18 boundary name must use the actual unmarked form. |
| T07 | Complete sweet-pomegranate nominal clauses after the spelling correction; the r18 offset must likewise use the unmarked form. |
| T08 | Complete named-type predicate sequence requiring the pomegranate topic for its reference. |
| T09 | Complete 41-word cited case, with an introduced woman. Its public English translation is absent; the working rendering and some antecedents must not be presented as translator-certified. Too long as one atomic constituent for a 12–24-word model. |
| T10 | Complete base and before/after-food block. `אלטביעה` is not a pronoun meaning the quince's own nature; keep the physiological recipient/effect interpretation separate. |
| T11 | Complete unripe conditional requiring a quince topic. |
| T12 | Complete sour-quince degree conditional with all three holam marks retained. |
| T13 | Complete sweet conditional followed by a comparison; whether that comparison is restricted to the sweet subtype or refers more generally to quince remains an interpretive scope issue. The final specification avoids it by stopping SWEET earlier. |
| T14 | Complete displayed comparison, but the earlier comparative-astringency gloss was unsupported. The final specification explicitly adopts juice/water versus bulk/flesh as its working lexical analysis. |

Thus the background inventory is not independently certified as a complete
generative grammar. **The freeze-ready verdict applies to the exact final
constructive specification hash above**, which defines its own five reviewed
extensions, substitutions and reference policy directly from the source packet.
