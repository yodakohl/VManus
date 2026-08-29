# GDT641 — strict TCH bound-form completion

Status: `PASS_2_STRICT_TCH_EXACT_DEFAULTS__2_NEW_COMPLETE_LINES`

GDT641 promotes the two reader-exact strict holes exposed by GDT640:

- `tcheor = kalt-trockener Drogenteil`
- `chetchy = getrocknete Droge; kalt-trocken, Grundform`

Both are exact-whole working defaults. The seven observed occurrences are
audited; no component, substring, wrapper or absent form is promoted globally.
V18 contains 285 dictionary rows, 238 exact surfaces and 44 complete
multi-token lines, 33 of them strict.

Run:

```bash
python3 experiments/yolo/gdt641_strict_tch_bound_form_completion/src/run.py
python3 experiments/yolo/gdt641_strict_tch_bound_form_completion/src/validate.py
```

See `METHOD.md`, `REPORT.md` and `experiment.json`.
