# GDT1205 — f108v: original-image check of the chey/chedy pair

**Decision: SOURCE_AWARE_VISUAL_SUPPORT.** One informed AI inspection of the
registered Yale photograph supports an extra looped body in the middle group
of f108v.52 compared with f108v.35. Both complete immediate neighbour pairs are
compatible at the qualitative glyph-family sequence level, and both target
groups have visible space-like separations on either side. This is bounded
visual support, not an independent palaeographic confirmation or a translation.

## Question and fixed contract

GDT1204 retained the literal ZL3b/IT2a contrast:

| Locus | Left group | Middle group | Right group |
|---|---|---|---|
| f108v.35 | qokeedy | chey | qokeey |
| f108v.52 | qokeedy | chedy | qokeey |

The exact same input consisting of base, page, recorded section/Currier/hand,
INTERNAL position and both complete immediate neighbours cannot deterministically
choose both literal middle spellings. This was conditional on transcription.
RF1b's opaque entities on .52 remain `qokee@152;y che@152;y qokee@222;`; they are
not normalized into the other readers. These are readings of one manuscript.

Before native pixels were acquired, the [preregistration](PREREGISTRATION.md)
fixed two target rows, one whole-page localization view, at most two original
IIIF region views, observation categories and the reduction to a decision.
The [new bounded admission](../../../docs/VOYNICH_DATA_SCOPE_20261005_F108V.md)
covers only this source-image check. It does not inherit image rights from the
179 cached text selectors, admit other folios or reopen any reserve.

## Source and observation

Official Yale canvas **1006265**, label **108v**, from manifest **2002046**;
original photograph **2649 × 3706**. Registration: 2026-10-05 13:51:55 UTC;
source acquired 13:52:15 UTC; observation sealed 13:58:11 UTC. The exact source
URL, bytes, dimensions, timestamps and region rectangles are retained in the
artifact receipts. Native resolution was used without OCR, reconstruction,
enhancement or contrast adjustment. One full-page and two region views were used.

| Assessment | Recorded observation |
|---|---|
| .35, sixth ZL/IT group | No separate closed two-lobed body is apparent between the short curved continuation and the terminal loop/tail. `ABSENT`. |
| .52, fifth ZL/IT group | An additional compact, closed, roughly two-lobed or 8-like body appears before the final loop/tail. `PRESENT`. |
| Complete left neighbours | Compatible qualitative sign order, including tall sign, low curves and looped ending. On .52 the selected immediate neighbour is the second of two preceding similar groups. |
| Complete right neighbours | Compatible qualitative sign order; the terminal stroke varies in shape. RF's entity is retained. |
| Separations | Visible blank intervals on both sides of each whole middle group. `BOTH_SPACE_LIKE` in both rows. |

The phrase “d-like” names a shape conventionally represented by EVA `d`; it
assigns no sound, meaning or morphological boundary. Similar flank sequences
are not pixel identity, a diplomatic collation or proven lexical identity.
Connected strokes, contraction and ligature remain possible sources of ambiguity.
The observer knew the expected transcriptions and selected countercase.

The sealed [observation](artifacts/OBSERVATION.json) preserves actual features,
localization, limitations and rival explanations, not just these categories.
For review: [.35 source region](runtime/row_35.jpg) and
[.52 source region](runtime/row_52.jpg). These are crops from one photograph,
not independent source images.

## Consequence and limits

Retain GDT1204's original **FULL_NEIGHBOUR_RULE_CONTRADICTED** decision and add
this qualified physical support for its selected main countercase. Do not erase
the visible extra body merely to obtain a deterministic rule from the two
immediate neighbours. Conversely, this pair does **not** establish that the
two middle groups mean different things. Same-content spelling variation,
different content, farther context and hidden state remain possible.

The test proves neither a universal `By/Bdy` decomposition nor free variation,
grammar, suffix meaning, a source language or general exclusion of allography.
No native word meaning is assigned. There is **one informed observer and zero
independent confirmation capacity**. GDT1204's sparse repeated complete contexts,
RF limits, GDT1198's dal-family constraints and the prior failed routes remain.

An obligatory alternation between `chey` and `chedy` on successive occurrences,
with no other output or reset, must first account for the already retained
`chedy qokedy chedy` at f76v.41 in GDT1163. That is a prior constraint, not a new
count or an endorsement of that report's historical semantic guesses. No such
alternator was selected or tested here.

Next selection question: can independently established available writing space
provide a testable cause of the short/long choice? IDEA000200 is an existing raw
text-context proposal, not a demonstrated mechanism. Its remaining character
and group counts are not independently available physical space. Before any
new measurement, review its predecessor decisions, available geometry and a
fixed falsifier. This is a selection task only: no new image measurement,
candidate experiment or meaning has been authorized by this result itself.

## Reproduction and validation

```
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1205_f108v_y_dy_native_pair/src/run.py
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1205_f108v_y_dy_native_pair/src/validate.py
```

Both completed; [validation](artifacts/VALIDATION.json) **PASS**. The separate
same-author validator checks registered provenance, image hashes/dimensions,
receipt chronology, region bounds, sealed observation and the fixed decision
reduction. It **cannot validate the palaeographic judgments**. Running the
reducer again reproduces the recorded decision, not an independent visual read.
`src/fetch_source.py` reacquires only the three registered image files if missing
and verifies their pinned bytes. The original files are retained under `runtime/`.

No scored semantic relation packet, new text corpus, held-out confirmation or
reserved folio was used. This is a local source-check checkpoint under the live
route's user exception; no commit, push or public publication is claimed.

## Claim-bearing predecessors

- [GDT1204](../gdt1204_yd_context_rule_countercases/REPORT.md): exact literal countercase and fixed input limits.
- [GDT1199](../gdt1199_daldy_label_seam_view/REPORT.md): precedent for qualified source-aware spacing observation, not evidence for this pair.
- [GDT1163](../gdt1163_correlative_relation_whole_account/REPORT.md): retained same-form repetition countercase only; old role guesses are not lexical facts.

