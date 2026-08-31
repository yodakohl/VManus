# GDT705 — complete immediate written-result census

Status: `PASS_V78_60_ACTION_NOMINAL_RESULTS__2_NEW_C017_C018__5_NEW_HOLDS__20_OPEN_26_CONTROLS__17_EDGES_12_COMPONENTS__ZERO_WORD_DELTA`

## Result

The first nominal token after all 60 immediate ACTION-to-NOMINAL transitions is now classified. Later entries inside those nominal blocks are not claimed as resolved. Two first-token cases say something substantially more concrete than “continue the work.”

> **C017 / f80r.17 `sheky#3 → shkeol#4`:** Bis zur Mittelstufe einweichen, erhitzen und abschließen. Ergebnis: eingeweichter Drogenstoff, bis Mittelstufe erhitzt.

> **C018 / f7r.2 `dold#5 → dchey#6`:** Drogenstoff abmessen und abschließen. Ergebnis: fertige abgemessene Mittelstufen-Trockenportion.

C017 binds only #3 to #4; `qokar#5` is an unbound later register entry. C018 binds only #5 to #6; #7-9 are unbound later register entries, not proven separate batches.

## Why these two improve the renderer

C017 writes the state created by two operations and the same stage: `einweichen → eingeweicht`, `erhitzen → erhitzt`, and `Mittelstufe → Mittelstufe`; its material identity remains open because #2 `sheckhy` names feuchtes Arzneikompositum. C018 writes `abmessen → abgemessen`, while `abschließen → fertig` is a semantic equivalence rather than an identical lemma; #6 itself has no Drogenstoff head. These are usable local event/result statements, not generic procedural filler.

The strongest unadmitted alternatives retain concrete readings:

| rank | locus | working reading | why still open |
|---:|---|---|---|
| 3 | `f86v3.13#10→11` | Einen gleichen Teil erhitzen; danach Trockengut, heiß auf Stufe II. | Only heating matches; dry material, grade II and the antecedent of “same part” are supplied elsewhere. |
| 4 | `f86v5.2#10→11` | Drogenstoff abkühlen; danach ein Maß kalten Ansatzes. | Cold mirrors cooling, but quantity and material change. |
| 5 | `f76v.10#1→2` | Eine Portion Arzneikompositum abmessen; danach feuchte abgemessene Rohstoffmenge I. | Measurement matches, but material changes and moisture/stage occur only on the right. |
| 6 | `f105r.31#5→6` | In drei Bündel abfüllen und schließen; danach vollständig bereitetes, abgeschlossenes Arzneikompositum. | Completion matches, but packaging and three bundles disappear. |
| 7 | `f56r.6#1-2→3` | Warme Trockenmischung bereiten; danach fertige abgemessene Mittelstufen-Trockenportion. | Measurement, portion and middle stage occur only on the right; warm mixture is not preserved. |

## The two useful contrasts

`sheky` occurs three times in the same line with the same action gloss. Only A057 is followed by the soaked, heated middle-stage drug state. A058 is followed by another action; A060 by hot raw material at the beginning of the grade. C017 therefore cannot become “`sheky` always produces `shkeol`.”

`dchey` is the immediate HIGH target in both A056 and A043. A056 supplies measurement and completion; A043 does not. C018 therefore cannot become “`dchey` is always the result of the preceding action.” The contrast is useful precisely because target identity alone does not decide the binding.

## Complete 60-case accounting

| class | count | cases |
|---|---:|---|
| new local edges | 2 | A057/C017, A056/C018 |
| attractive new holds | 5 | A066, A072, A046, A006, A043 |
| earlier admitted readings replayed | 3 | A007, A026, A033 |
| earlier holds retained | 4 | A005, A009, A024, A053 |
| partial open compatibility | 20 | possible patient, quantity, material or single-state continuations |
| visible conflicts | 26 | material, process, heat/cold, dry/wet or grade breaks |

This corrects the impression that GDT703's seven cases were the whole relevant population. They were only the exact `NOMINAL_FINISHED_RESULT_STATE` gate; A043 and A056 belong to the separate HIGH `NOMINAL_FINISHED_MIDDLE_DRY_PORTION` class, and A057 was outside GDT687's target deck entirely.

## Cumulative graph

C017 and C018 each form a new two-node component. The graph changes from 15 edges/10 components to 17 edges/12 components. Unique edge nodes rise from 28 to 32, endpoint incidences from 33 to 37, and hull/render positions from 30 to 34. Shared nodes remain five. No old edge or component is reinterpreted.

## What remains next

The immediate first-token nominal space is now exhausted. The next useful pass is a separate later-result census for only those actions whose result is still unwritten, beginning with the already ranked delayed candidates. A066, A072, A046, A006 and A043 remain live comparators. No new page and no word reinterpretation is needed for that pass.

## Claim ceiling

These are exploratory local readings within the current working codebook. They are not a recovered plaintext, a portable `sheky`, `dold`, `shkeol` or `dchey` dictionary entry, or a historical decipherment claim.
