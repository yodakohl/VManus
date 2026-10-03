# GDT1164 — unpaired context word ranking

**NO_SUPPORTED_SOURCE_CONTEXT_RANKING.** See [report](REPORT.md), [complete marked-type table](CANDIDATE_TABLE.md), [fixed method](METHOD.md), and [result](artifacts/RESULT.json).

## Reproduction

Use the pinned Python/NumPy/PyTorch versions in requirements.txt and SPEC.json. Source tables are pinned in src/SOURCE.json. In a separate checkout, regenerate numeric packets using a repository-relative working directory; execution receipts include new timestamps, so preserve the published original receipts for chronology.

```sh
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/prepare.py --runtime runtime/gdt1164 --registered-commit ca1d9ec93
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/validate.py --runtime runtime/gdt1164
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/prepare.py --runtime runtime/gdt1164 --registered-commit ca1d9ec93 --nulls --capacity-validation experiments/yolo/gdt1164_unpaired_context_word_ranking/artifacts/CAPACITY_REPLAY.json
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/validate.py --runtime runtime/gdt1164 --all-worlds
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/run.py --runtime runtime/gdt1164 --stage fit --workers 16
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/run.py --runtime runtime/gdt1164 --stage score --release-gold
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/validate.py --runtime runtime/gdt1164 --fits
python3 experiments/yolo/gdt1164_unpaired_context_word_ranking/src/validate.py --runtime runtime/gdt1164 --scores --release-gold
```

The fitter accepts only six numeric arrays. Score-stage gold access requires the full prediction lock. No manuscript inputs or reserves are used. Complete published gzip predictions permit independent score accounting without retraining; numeric source packets are regenerated for geometry/objective/Adam checks. F is fit once per fold and reused across its19 count-preserving worlds.
