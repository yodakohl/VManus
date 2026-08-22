# V77 R1 — source-first exact-card attestation audit

## Result

No portable exact-card word value survives the source-first gate.

- 22 entries were frozen from two genuine 1379 nomenclators before the exact legacy handles and the V73/V74 occurrence panel were revealed.
- 14 reusable control-card IDs and the 10 most frequent remaining exact cards were then audited across all 381 selected prose events.
- The central `V77_TARGET_FREEZE.tsv` fixes 24 cards and 197 occurrences.
- Zero cards have an exact historical source entry that binds the opaque Voynich card to the proposed value.
- Four cards retain only a restricted formal production role as `FORMAL_LABEL_NOT_WORD`.
- The other 20 cards become `EXEMPLAR_VALUE_UNKNOWN`.

This withdraws portable card-level dictionary values. It does not withdraw the occurrence-specific, explicitly creative readings in the V73/V74 working editions, and it does not deny that period workshops used nomenclators.

## R1 workshop background

1. I train several scribes who must continue the same practical book reliably.
2. I think in demonstrable exemplars, frequent whole cards, simple rules, and checkable copying steps.
3. For every theory I ask how an apprentice learns, executes, corrects, and hands it to a second hand.
4. I prefer no language or meaning, but the smallest practically teachable production procedure.
5. I provide a concrete writing instruction, a reading-back procedure, and the errors a real apprentice would make.

## Source-first freeze

The current route, sidequest theory, V71–V80 protocol, attestation rule, frozen V77 protocol, and the R1 profile were read as required. The exact V69 card rows and V73/V74 occurrences were not opened until the following source inventory was frozen.

The source is Aloys Meister's edition of the Gabriel de Lavinde collection, headed 1379 and identified as `Vat. Arch. Collect. 393 f. 166–181`:

> Aloys Meister, *Die Geheimschrift im Dienste der päpstlichen Kurie von ihren Anfängen bis zum Ende des XVI. Jahrhunderts* (Paderborn, 1906), pp. 171–176.

The public scan used is the Internet Archive PDF, SHA-256 `5d38b02e1dfd75803fbe645dd70e73ba77ec62fee9dc9a0955522732d37d6c90`. The stable scan URL and exact print/PDF page locator are present in every source row.

The frozen inventory is a bounded, non-exhaustive sample of 22 entries whose codes are unambiguously set in ordinary Roman type. It covers two distinct keys:

- key 13, `Zifera [Anonym.]`, a cipher alphabet plus nomenclator, printed p. 173 / PDF p. 189;
- key 26, `Ziffera Guigonis Iarenti de Aquis` with Petrus Raynaldi, a vowel cipher plus nomenclator, printed p. 175 / PDF p. 191.

Examples include `dux Andegaviensis → ml`, `Matrimonium → ln`, and `pax → pR` in key 13, and `Massilia → mm`, `Napoli → mh`, and `Lo cancelier → ph` in key 26. These attest a real late-fourteenth-century practice: whole people, offices, places, and diplomatic concepts can receive short opaque codes. They do not connect any Voynich card to any one entry.

The source inventory itself was frozen at SHA-256 `8f2c6afdcdfb2759a10d83c4a4404fabf3448522c8013f46e7418e06e258bfda`. The builder refuses to run if that file changes.

## Bounded reveal and selection

After the source freeze, the 14 V69 reusable control IDs were revealed. Before counting the remaining cards, the additional budget was fixed as:

`TOP_N_NONCONTROL = 10`, ranked only by frequency in the complete 381-event V73/V74 prose panel, with opaque card ID as the deterministic tie-break. The builder additionally pins the published central target manifest at SHA-256 `2b5659f9d7cd213fc22842c38e38388061096b9407723628bb82bb0a51ce1dd7`.

The resulting extra cards have frequencies 18, 12, 11, 10, 7, 5, 4, 4, 4, and 3. No contextual coherence, desired meaning, spelling, stem, PAGE_HOST, or source resemblance entered membership. The frequency-rank 11 and 12 cards and their six occurrences are outside the frozen target and were not audited or replaced.

## Card decisions

| Exact card ID | Revealed legacy handle or selection | n | Cross-occurrence result | V77 atomic default |
|---|---:|---:|---|---|
| `0275fbf14e07935b0a45` | TEMPERIEREN? | 7 | contextually stable in Bio, unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `276a7c2d74d1143446f4` | ANWENDEN? | 10 | broad application family, arguments vary | `EXEMPLAR_VALUE_UNKNOWN` |
| `2f1c5e56e8f0ff459065` | MASS? + restricted formal prompt | 20 | stable formal prescription channel, no word value | `FORMAL_LABEL_NOT_WORD` |
| `308e8ea2d5d190c498e8` | local relation-slot prompt | 6 | reusable formal placement only | `FORMAL_LABEL_NOT_WORD` |
| `7a4bb8136330ee4e6e56` | ANSATZ? | 7 | active-post family, operation varies | `EXEMPLAR_VALUE_UNKNOWN` |
| `7db18b2f0fb7ed0fcfd3` | SPÜLEN? | 8 | contextually stable in Bio, unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `b5df9126607030b95175` | KLAR? | 4 | clear state versus generic test state | `EXEMPLAR_VALUE_UNKNOWN` |
| `b5fcea1eaed06b2f2291` | standard-slot prompt | 9 | reusable formal placement only | `FORMAL_LABEL_NOT_WORD` |
| `dcda95c81a5460feb191` | active-work-state prompt | 19 | reusable formal linkage only | `FORMAL_LABEL_NOT_WORD` |
| `dd0ecaf5e27d81befffc` | ZIEL? | 10 | context supplies station/target | `EXEMPLAR_VALUE_UNKNOWN` |
| `de7321bface5628e35d6` | ABLASSEN? | 8 | contextually stable in Bio, unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `dec401773c1f0347793d` | VORIGES? | 2 | coherent but under-supported and unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `e0b630cb1b5df5e7105b` | BEREIT? | 7 | flowering/readiness/test-state mixture | `EXEMPLAR_VALUE_UNKNOWN` |
| `faf321940aed922846a9` | ANTEIL? | 2 | coherent but under-supported and unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `b921a237be883a820352` | frequency rank 1 | 18 | fraction/oil/heat/stir/store/use/honey/deixis conflict | `EXEMPLAR_VALUE_UNKNOWN` |
| `bc4f1f5c006c74a4d26d` | frequency rank 2 | 12 | readiness-plus-close family, unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `6f7ff8287eddf4da9fdb` | frequency rank 3 | 11 | Herbal wring/settle versus Bio mix | `EXEMPLAR_VALUE_UNKNOWN` |
| `7d25241b0e56c836372a` | frequency rank 4 | 10 | terminal construction; local operation varies | `EXEMPLAR_VALUE_UNKNOWN` |
| `1645e612504fcef59ced` | frequency rank 5 | 7 | measured-share expansion stable in Bio, unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `4d4559019a961b834aa1` | frequency rank 6 | 5 | same-post linkage/merge/deictic-source family | `EXEMPLAR_VALUE_UNKNOWN` |
| `259b2b3b0bf859882e2c` | frequency rank 7 | 4 | rinse-plus-close stable in Bio, unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `2cc054357a929df85f64` | frequency rank 8 | 4 | collect/crush/dry/add-honey conflict | `EXEMPLAR_VALUE_UNKNOWN` |
| `2cc8bb3c2af19607888f` | frequency rank 9 | 4 | connected-run expansion stable in Bio, unattested | `EXEMPLAR_VALUE_UNKNOWN` |
| `28ffbc88b97772a75f1e` | frequency rank 10 | 3 | set-aside-plus-close stable in Bio, unattested | `EXEMPLAR_VALUE_UNKNOWN` |

The key distinction is between contextual consistency and an invariant atomic value. A later creative edition can repeatedly assign “drain” to one card without supplying the independent codebook row needed to make “drain” a word value. Conversely, cards `b921…`, `6f7…`, and `2cc0…` demonstrate directly that an occurrence paraphrase cannot simply be copied into the dictionary.

## Teachable workshop rule

The smallest rule that can be handed to another scribe is:

1. Copy the exact whole card from the master exemplar. Do not split it into stems or infer a pronunciation.
2. For the four formal cards, learn only a visible production instruction: set or link the appropriate record-local slot. Read them back as “formal mark here,” never as a word.
3. For every other audited card, obtain the concrete noun or action from the pictured exemplar, the local record model, or an oral rubric. The card ledger itself says `EXEMPLAR_VALUE_UNKNOWN`.
4. Never export one occurrence sentence to another page merely because the exact card repeats.
5. Correct a copy by checking whole-card identity, local owner, field order, and closure—not by asking whether a guessed German gloss sounds plausible.

An apprentice can therefore reproduce the pages without learning 22 false words. The master must supply exemplars for content, while four repeatable formal moves can be taught as moves.

## Apprentice failure modes

- **Stable-context overreach:** turning eight Bio drain paraphrases into a historically attested word.
- **Section leakage:** carrying a Bio mixing value into the Herbal wring/settle occurrence of `6f7…`.
- **One-page polysemy fabrication:** forcing collection, crushing, drying, and honey addition into one atomic value for `2cc0…`.
- **Form decomposition:** treating visible spellings or their pieces as stems, prefixes, suffixes, or sounds.
- **Nomenclator analogy as identity:** reasoning that because `pax → pR` existed in 1379, an opaque Voynich card must also name a concept.
- **Formal/lexical collapse:** reading a record-slot prompt as MASS, TARGET, or PREVIOUS instead of retaining it as a nonword production label.

## Historical ceiling

The selected source supports only this period-compatible working proposition:

> A workshop around the manuscript's period could use short opaque whole codes and teach them by a key or exemplar.

It does not supply an exact Voynich codebook entry. It therefore cannot establish word, stem, sound, language, or meaning. The absence of a match in this bounded source sample is not proof that no comparable historical key existed; it is proof that the mandatory attestation fields for these proposed values are presently missing.

## Scope and validation

The audit reads exactly the selected 100 Herbal and 281 Biological events on `f10r`, `f11r`, `f55v`, `f56r`, `f81v`, `f82r`, and `f83r`. The celestial pages contain no V73/V74 prose events and were not used in this card audit. Sealed pages were not accessed.

`V77_R1_VALIDATION.json` is `PASS`: 22 source rows, 24 decision rows, 197 audited occurrences, 14 withdrawal/restriction rows, zero admitted word rows, and no sealed-page occurrence.
