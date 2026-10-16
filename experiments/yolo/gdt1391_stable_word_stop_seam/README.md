# GDT1391 — stable word-stop seam

An existing same-line `saino ol` pair excludes the specified stable mandatory
stop rule and its concrete IDEA1065 application. Read [REPORT](REPORT.md) and
[METHOD](METHOD.md) for the exact assumptions and exceptions.

This is post-observation verification, not a blinded manuscript experiment.
All inputs are existing repository artifacts. No new corpus or image is used.

From the repository root:

```sh
python experiments/yolo/gdt1391_stable_word_stop_seam/src/run.py --lock experiments/yolo/gdt1391_stable_word_stop_seam/src/REGISTRATION_LOCK.json
python experiments/yolo/gdt1391_stable_word_stop_seam/src/validate.py --lock experiments/yolo/gdt1391_stable_word_stop_seam/src/REGISTRATION_LOCK.json
```

The primary constructs literal menus; the validator computes transitions by
occupied source positions and arithmetic ranks. General proof, finite checks,
old source fidelity and the inherited endpoint count are kept distinct.
