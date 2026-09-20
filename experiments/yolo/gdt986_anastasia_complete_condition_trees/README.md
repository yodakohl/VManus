# GDT986 — complete Anastasia condition trees

Exploratory full-content hypothesis, frozen before target fitting. Nine source
assertions cover all twelve lines of the complete historical entry. Two fixed
writers preserve every semantic atom and every original target word boundary.

Read [METHOD](METHOD.md), [decision](DECISION.md) and
[preregistration](PREREGISTRATION.md). [REPORT](REPORT.md) records the actual
result; a registered or code-compatible model is not a translated word.

In a Python environment with `cvc5==1.3.4`:

```bash
python3 experiments/yolo/gdt986_anastasia_complete_condition_trees/src/run.py --fixtures
python3 experiments/yolo/gdt986_anastasia_complete_condition_trees/src/run.py
python3 experiments/yolo/gdt986_anastasia_complete_condition_trees/src/validate.py
```

The source-only compiler can reproduce `src/SOURCE.json`; the validator's
`--source-only` option checks it without opening target data. Main execution
requires the unchanged preregistration lock. No new image, sealed folio,
reserve, outside contact or old-source modification.
