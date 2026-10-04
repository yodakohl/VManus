# GDT1171 — open vocabulary context recovery

Status: `REGISTERED_UNSCORED`

One fixed U/C/S comparison on supplied historical sign rules, not Voynich.
See METHOD.md for source separation, exact search, fixed gates and limitations.

Reproduce in order:

1. `python experiments/yolo/gdt1171_open_vocabulary_context_recovery/src/prepare.py`
2. `python experiments/yolo/gdt1171_open_vocabulary_context_recovery/src/validate.py --fixtures`
3. Publish the fixed preregistration and obtain its full commit ID.
4. `python experiments/yolo/gdt1171_open_vocabulary_context_recovery/src/run.py --release COMMIT`
5. `python experiments/yolo/gdt1171_open_vocabulary_context_recovery/src/score.py`
6. `python experiments/yolo/gdt1171_open_vocabulary_context_recovery/src/validate.py`

The runner refuses to overwrite a locked run. Use a separate checkout of the
preregistration commit for fresh reproduction. Each worker sees its raw held
book and only the other books' expanded reference. Prior analyst exposure is
retained. All source files were already public CoReMA material, CC BY4.0,
University of Graz; source URLs/credits and hashes remain in the pinned XML and
source_rule_package/SUMMARY.json. No new source acquisition or manuscript access.
