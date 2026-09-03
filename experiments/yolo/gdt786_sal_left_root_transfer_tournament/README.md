# GDT786 — sal left root transfer tournament

Status: `PARTIAL__FORMAL_FAMILY_RETAINED__PRODUCTIVE_SEMANTIC_ROOT_INACTIVE__12_CONCRETE_WHOLE_DEFAULTS`

GDT786 tests all twelve observed `sal…` complete-word types against additive,
learned-whole, same-remainder, matched-root, and salt models. The additive
model beats the same-remainder null only 5/10 times (`p=.4443`), while inverse
root recovery strongly favors the non-`sal` controls. The result retains a C1
formal string family but leaves productive semantic `sal-` as an inactive C0
hypothesis.

Every observed whole receives a practical concrete default. Standalone
`sal=Droge` remains unchanged; the longer words do not inherit it mechanically.
The strongest form-specific composite leads are `saldal=abgemessene Rohdroge`,
`salkeedy=erhitzte Fertigdroge`, and `saltar=kalter Drogenanteil I`.

Reproduce with:

```bash
python3 -B experiments/yolo/gdt786_sal_left_root_transfer_tournament/src/run.py
python3 -B experiments/yolo/gdt786_sal_left_root_transfer_tournament/src/validate.py
```

See `REPORT.md`, `METHOD.md`, `PREREGISTRATION.md`, and `experiment.json`.
