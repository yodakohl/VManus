# Reproduce GDT837

Python 3 and a C++17 compiler are sufficient. No GPU or external LLM service is
used. Use a Git checkout of the licensed source repository at the pinned commit recorded
in sources/MANIFEST.json; retain its LICENSE.txt. Install it at runtime/ittb_source
or pass --source-dir to preparation/validation. A plain archive is insufficient
because preparation verifies committed bytes with Git. Runtime files are ignored.

The initial public preregistration checkout omits confirmation payloads. On that
checkout, first regenerate them with prepare.py --phase all (without --check).
On the final result checkout they are included. Then, from the repository root:

```sh
python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/prepare.py --phase all --check
python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/test_pipeline.py
python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/validate.py --source-only --check
```

To reproduce the fitting experiment, use the initial public preregistration
checkout, regenerate omitted confirmation files as above,
and run the following in order. Fit refuses to overwrite a completed run.

```sh
python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/run.py --fit --workers 24
python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/run.py --check
python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/evaluate.py
python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/validate.py
```

On the final result checkout, rebuild reference tables and discovery projections
without a search using run.py --prepare-verification, then run the fit-lock check,
evaluator check and independent validator. The validator checks published results
without modifying them. All keys share one fixed content split; do not interpret
three successful keys as three independent text corpora.
