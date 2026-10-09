# GDT1226 — arbitrary mixtures of fixed source profiles

See REPORT.md for the conditional exclusion, PREREGISTRATION.md for the frozen
question and METHOD.md for the exact two-set certificate.

Python3 with NumPy1.26.4 and SciPy1.14.1 is used by the certificate proposer.
The validator requires only the Python standard library. In an isolated fresh
reproduction checkout with RESULT.json absent and the registration lock present:

```
python3 experiments/yolo/gdt1226_pooled_source_alias_lower_bound/src/run.py
python3 experiments/yolo/gdt1226_pooled_source_alias_lower_bound/src/validate.py
```

The runner refuses to overwrite an existing result. The validator can check
saved certificates directly without installing the optimizer. All source files
are the existing pinned1202/1177artifacts; no extra corpus is needed. CoReMA
attribution, source projection and retained licensing are documented with1177.
This is not a physical writer, native reading or public preregistered experiment.
