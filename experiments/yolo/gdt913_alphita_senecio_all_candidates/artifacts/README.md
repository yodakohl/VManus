# Reproduction and exact scope

PREDICTIONS.json/.tsv and PREDICTION_GROUPS.md were published before body access.
SELECTION.json and its separate lock were published before confirmation access.
The phase input files preserve complete original IT2a groups for the six bound
paragraphs only. Every unrequested cache body and alternative reading is skipped
as a byte span, not parsed into a paragraph object. f84 selectors are rejected
before any reading payload. The full source cache is unchanged and hash-bound.

From repository root (Python3 standard library):

```sh
python3 experiments/yolo/gdt913_alphita_senecio_all_candidates/src/run.py predict
python3 experiments/yolo/gdt913_alphita_senecio_all_candidates/src/run.py selection
python3 experiments/yolo/gdt913_alphita_senecio_all_candidates/src/run.py confirmation
python3 experiments/yolo/gdt913_alphita_senecio_all_candidates/src/validate.py --phase confirmation
python3 experiments/yolo/gdt913_alphita_senecio_all_candidates/src/render.py
```

Existing prediction and phase files must reproduce byte-for-byte; no overwrite
is permitted on a difference. No GDT888 fitter, decoder or changed compiler is
invoked. Candidate identities are K01–K18 in the original lexicons list order.
All count vectors use C,B,D,L,M,S. The original complete cache is the previously
guarded GDT887 SELECTED.json; mixed raw/sealed TSVs are never loaded here.

Independent validation checks metadata/source and phase-count parity on the
published phase projections. Its default `--phase prediction` opens no body.
`--phase selection` opens no confirmation. Actual source projection is performed
by the separately reviewed bounded intake code, not independently reacquired.

The full-worktree audit retains the pre-existing GDT600 binding and global-index
debt; it is not a global PASS. Exact staged privacy/scope checks are separate.
No null calibration, significance, translation or semantic validation is claimed.
