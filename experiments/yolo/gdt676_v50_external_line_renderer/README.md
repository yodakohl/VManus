# GDT676 — V50 external 51-line renderer

Status: `PASS_51_LINE_READER__479_TOKENS__136_OPEN__1_DCHEY_OVERRIDE__ZERO_HARD_GENERIC`

GDT676 turns the 51 external positions touched by GDT675 into a
token-preserving working edition of their 51 complete source lines. It covers
479 positions on 36 already admitted pages and opens no new page. The result is
**not 51 complete translations**: 136 positions remain explicit
`⟦surface:?⟧` gaps, so 49/51 lines are still incomplete.

The working layer contains 343/479 assigned positions (71.6075%); “assigned”
does not mean independently known. The narrow screen finds 105 positions/106
matches in the literal token overlay and 113/114 in the fluent working reader.
Under the wider substance/grade/measure sensitivity screen, 311/343 assigned
literal values match class-level vocabulary (`0.906706`) rather than supplying
a concrete referent by themselves. This is the main next rendering gap. No
banned generic work-item/work-cycle filler occurs in either layer.
Fifty of the 51 GDT675 applications survive the full-line reading. At f26r.2,
initial `dchey` is corrected from an imperative to the nominal measured result
“abgemessene Trockendroge der Mittelstufe, abgeschlossen” before `aiin`
“Menge III”.

The full edition is in
`artifacts/GDT676_V50_EXTERNAL_WORKING_READER.md`; the compact findings and
limits are in `REPORT.md`, and `METHOD.md` describes the reproducible build.

Run from the repository root:

```bash
python3 experiments/yolo/gdt676_v50_external_line_renderer/src/run.py
python3 experiments/yolo/gdt676_v50_external_line_renderer/src/validate.py
```

Both f84 and f84r remain forbidden.
