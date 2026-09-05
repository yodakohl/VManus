# Replaying GDT833

The fitter and evaluator are byte-frozen from prospective commit
`efa4aad80305a599d672d20bae8cf7ebf1ba0e69`. Use that commit for a fresh optimization
replay; the completed checkout refuses to overwrite locked fits.

The complete-result checkout can rebuild the pinned source and runtime models,
then independently verify its stored outcomes:

```sh
python experiments/yolo/gdt833_reference_orthography_intervention/src/prepare.py --source-dir experiments/yolo/gdt833_reference_orthography_intervention/runtime/udante_source --fetch-source
python experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py --reference experiments/yolo/gdt833_reference_orthography_intervention/prepared/reference_native.jsonl --families experiments/yolo/gdt833_reference_orthography_intervention/prepared/families.json --out experiments/yolo/gdt833_reference_orthography_intervention/runtime/reference_native
python experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py --reference experiments/yolo/gdt833_reference_orthography_intervention/prepared/reference_collapsed.jsonl --families experiments/yolo/gdt833_reference_orthography_intervention/prepared/families.json --out experiments/yolo/gdt833_reference_orthography_intervention/runtime/reference_collapsed
python experiments/yolo/gdt833_reference_orthography_intervention/src/run.py --check
python experiments/yolo/gdt833_reference_orthography_intervention/src/validate.py --source-dir experiments/yolo/gdt833_reference_orthography_intervention/runtime/udante_source --model-root experiments/yolo/gdt833_reference_orthography_intervention/runtime --check
```

Source generation is deterministic and must reproduce the committed inputs.
The validator first checks all 48+6 locked fits, then source/truth bindings,
every discovery objective, held metrics and the fixed legal v/z oracle. It does
not fit a key or normalize the control's u/v distinction away.
