# GDT1141 Stage 1 — distinct finite core candidate 02

Status: candidate only; not frozen or accepted. This is the one authorized alternative to CORE proposal01. It keeps BB's lexical nouns unchanged and attempts a reusable observation/condition grammar in two actual places in the written prose. All values below are new C0 hypotheses, not meanings established by the source. No Stage2 extension is authorized by this file.

## Core lexicon

Inherited BB values remain untouched: `ok=MOON`, `oko=SUN`, exact `okaiin=LIGHT_OF(MOON)`, exact `okoaiin=LIGHT_OF(SUN)`. `LIGHT_OF(B)` is an externally manifest light noun attributed to B, zero semantic operands after composition, and does not claim intrinsic lunar emission.

Eight added whole-form values are paid:

| Form | Proposed C0 value | Type and restrictions |
|---|---|---|
| `ykchol` | same-Moon frame | Modifier on a reference record; no general `yk` value. |
| `qockhy` | greater Sun–Moon separation | Condition modifier on a reference record. Whole form only. |
| `okalda` | exposed lunar portion | Quantity/extent modifier on a Moon-light reference. IT2a form only; no alias to ZL `okaldy` or RF `okal@152;y`. |
| `otal` | Earth-facing amount of the exposed lunar portion | Scalar amount modifier on a reference record. No general `al` or `tal` meaning. |
| `chodar` | approach of Moon toward Sun | Condition argument to `dal`; no modern orbital/rate claim. |
| `chdy` | decreasing-light state | A scalar state that may serve as the state of a varying quantity and as a condition for a following state. Paid polyfunctional type, not a ch/dy rule. |
| `dalg` | compare a named reference-light report with a current light noun of the same body | Binary relation/predicate; no `dal|g` derivation or universal G. |
| `dal` | “varies with” | Binary typed relation, with the ordinary complete left constituent as its first argument and the following condition/state as second. See frozen uniform application rule below. |

`qokaiin` is not a new lexical synonym for `okaiin`: a finite grammatical wrapper constructs a reference observation from the inherited noun. There is no new value for plain `okaiin`; it remains the BB `LIGHT_OF(MOON)` noun in every occurrence.

## Four finite rules

1. **Reference wrapper.** In this candidate only, exact `qokaiin = q(okaiin)`; `q` has arity 1 and type `LIGHT_OF(B) -> ReferenceLight(B)`. The output retains the same inherited light noun as its content; it adds only discourse status “reference”. No q value exports to `qockhy`, `qokol`, `qokool`, or any other q-form.
2. **Typed field adjuncts.** A whole modifier attaches to a preceding compatible `ReferenceLight` by written left-to-right syntax, producing a richer record without changing its light noun. In the `.16` chain `ykchol`, `qockhy`, `okalda`, and `otal` each add the field named in the lexicon. This is a reusable typed adjunct rule, not a locus-specific permission. No `okaiin` noun is rewritten as an event or record.
3. **`dal(X,Y)` = “X varies with Y”.** Arity 2. X is a scalar property/state or a complete constituent containing one; Y is a condition/state. The result is a dependency proposition, not an asserted numerical direction. It binds the complete left constituent in the current written clause and the next complete condition to the right; it does not jump over words or delete either argument. The identical rule is used for every standalone IT2a `dal` in the packet. Where a neighbor lacks a value/type, the application remains visibly unresolved.
4. **`dalg(reference,current)`.** Arity 2; the left argument is the nearest compatible earlier q-marked light reference in the same written local unit; the right argument is the immediately preceding exact `LIGHT_OF(B)` nominal. It is well-typed only when the two body identities match. It returns a comparison slot whose direction/value can remain UNKNOWN if no current quantity is given. This is ordinary typed anaphora tied to q-marking and local order, not a folio/line identifier.

These are authored grammar rules, not inferred from GDT1051 decomposition. They charge reference marking, field attachment, relation arity, argument order, locality and same-body identity. They do not impose sentence boundaries at line ends or ring starts.

## Two complete actual applications of the shared relation

**Application 1, f89v1.14 IT2a, groups 7–9:** `okoaiin dal chdy`.

Composition: `VARIES_WITH(LIGHT_OF(SUN), DECREASING_LIGHT_STATE)`. This is a complete, typed relation: its two written arguments are adjacent, and the direction/value of the solar-light change is not supplied by the word mapping. The next `dal` at G10 is a separate occurrence and must use the same rule, not be merged into this application.

**Application 2, f89v1.16 IT2a, groups 1–9:**

`qokaiin ykchol qockhy okalda otal dal chodar okaiin dalg`

Composition: `qokaiin` forms a reference to the inherited Moon-light noun. Four compatible whole modifiers supply same-Moon identity, greater Sun separation, exposed portion and Earth-facing amount. `otal dal chodar` states that the quantity varies with approach. The final `dalg` binds the actual earlier reference and the immediate current noun `okaiin`, both Moon-light; it requests a same-body comparison. The current amount/result is UNKNOWN, so the reading does **not** claim that the comparison returns less light. The source's greater-separation/more and approach/less statement makes this a plausible consequence to test, not a lexical key.

This preserves BB's zero-operand nominal contract: `okaiin` is never translated as “current observation”. A reference record is constructed by rule 1 from the noun, while the unmodified noun remains the second `dalg` argument. The six intervening groups are not ignored: they supply frame, condition, exposed portion, amount and the written variation relation.

## Every standalone IT2a DAL in owned prose

| Locus/group | Fixed parse | Status under the one `dal` rule |
|---|---|---|
| `.13 G9` | `cheody dal dy` | `VARIES_WITH(UNKNOWN_PROPERTY(cheody), UNKNOWN_CONDITION(dy))`; written arguments retained, semantic result unknown. |
| `.14 G8` | `okoaiin dal chdy` | Completed typed application above. |
| `.14 G10` | `chdy dal daldy` | `chdy` is the paid decreasing-light state and can be the left scalar; `daldy` stays an unknown condition, so the application is unresolved. It is not silently fused with preceding `dal`. |
| `.16 G6` | `otal dal chodar` | Completed typed application above. |
| `.18 G4` | `qokol dal chol` | `qokol` and `chol` remain unassigned; record a typed argument-slot obligation, not an English gloss. The application/result remains unresolved. |

No standalone `dal` is omitted. Composite forms `daldy`, `daldaldy`, `dalshdy`, `dydchy`, and whole `dalg` remain distinct; no d/dy/g export or productive suffix stripping is introduced.

## Countermodels and debt

The fixed alternative W still reads exact `okoaiin`/`okaiin` as solar/lunar proper-return intervals; generic property/content and renamed observation accounts survive. BB's nominal products do not acquire recipients by this proposal. `okaldy` and ZL/RF alternatives stay separate. Morgan M.721 is historical plausibility only, not proof of source copying; its lunar heaven stays distinct from the opaque body, eclipse remains a separate uncertain condition, and medical/human-disposition stanzas are retained as attributed source content but not imported into these word values.

This proposal has 8 new whole values plus the q reference wrapper output; it has 4 finite rules; all are C0. The wording `decreasing-light state` for `chdy` is a new semantic payment made only to make `.14` one actual application, not independently confirmed. Three DAL applications retain UNKNOWN arguments/outputs. The `dalg` current measure and whether the same condition governs its output remain unknown; consequently `.16` is a coherent reference/condition/comparison construction but not the source's complete “less light” sentence.

Nothing here covers all 97 IT positions or 288 native reader groups. Ring order remains stored accounting order, not proven syntax; upper-ring BB `oko` and the two lower-ring `okoaiin` loci keep BB's original values. All repeated forms remain owed. This is exploratory, nonblind, no confirmed words, no significance, no source-copy or plant claim. If the typed syntax is not acceptable as an ordinary reusable grammar, stop with `MISSING_CORE_DESIGN`; do not generate a third variant or start Stage2.
