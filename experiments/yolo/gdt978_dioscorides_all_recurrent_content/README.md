# GDT978: all recurrent content jointly

Read PREREGISTRATION.md and METHOD.md. Dependencies retain unchanged SOURCE,
ALIASES, whole-page domain, old name-code cases and GDT977 outcomes. This tests
358 recurrent occurrences with 208 exact adjacencies; only singleton runs have
free span values. It is an explicitly necessary, incomplete content code.

Use Python with `src/requirements.txt` installed (`cvc5==1.3.4`):

```sh
python3 experiments/yolo/gdt978_dioscorides_all_recurrent_content/src/run.py
python3 experiments/yolo/gdt978_dioscorides_all_recurrent_content/src/validate.py
```

The primary run checks its registration lock and requires the public execution
receipt. The validator checks sources, every SAT witness, all partition/base-row
coverage and aggregate counts. It does not run a second solver or certify an
UNSAT proof. Synthetic checks can run with `src/check_controls.py`; they are
source-only engineering controls, not a semantic null.
