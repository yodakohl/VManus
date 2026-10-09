# GDT1243

See REPORT.md for the limited local gap observation and PREREGISTRATION.md for its fixed decision rule.

To verify the retained result from repository root:

```bash
python3 experiments/yolo/gdt1243_f45r_mandatory_grapheme_gaps/src/fetch_source.py
python3 experiments/yolo/gdt1243_f45r_mandatory_grapheme_gaps/src/validate.py
```

The validator independently recomputes the decision from the sealed manual observation. run.py is the original one-time reducer and deliberately refuses to overwrite its retained RESULT.json. Reproduction cannot independently regenerate an observer's visual judgment.
