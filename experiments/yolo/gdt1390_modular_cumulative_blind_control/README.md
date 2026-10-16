# GDT1390 — full-scale cumulative-writer control

**The fixed search fails: 0/12 complete positive messages recovered.** All true
keys score above their wrong returned candidates. This is a limitation of the
search, not a rejection of the writer or a native decipherment.

Read the [report](REPORT.md), frozen [preregistration](PREREGISTRATION.md) and
[method](METHOD.md). `artifacts/RESULT.json` contains primary accounting;
`artifacts/VALIDATION.json` independently verifies generation and scores.

## Reproduce

Run from the repository root. Python with NumPy and a C++17 compiler are needed.
Use the recorded compiler/runtime for exact stochastic-search replay. No raw
language-pack copy is included. The existing GDT001 preparation script and
pinned manifest supply the six public source inputs; their provenance and
licenses are retained in `artifacts/SOURCE_ATTRIBUTIONS.json`.

Rebuild the models only when the six original cached packs are available:

```sh
python experiments/yolo/gdt1390_modular_cumulative_blind_control/src/prepare.py
```

The original driver contains the original dated wall-time stop. For a later
exact replay, use the separate post-result wrapper with a fresh destination:

```sh
python experiments/yolo/gdt1390_modular_cumulative_blind_control/src/reproduce.py --output experiments/yolo/gdt1390_modular_cumulative_blind_control/runtime/replay --seconds 600 --workers 32
```

This repeats exactly the old 576 starts, compares their scientific fields,
and leaves all frozen outputs unchanged. It does not read the released truth
or constitute a new blind experiment. The caller's budget is required; the
original experiment's stop remains historical evidence.

The independent validator can verify the released controls and all final
scores without rerunning optimization. It needs the original source packs to
reconstruct training and control offsets:

```sh
python experiments/yolo/gdt1390_modular_cumulative_blind_control/src/validate.py --models experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts/MODELS.json --cases experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts/CASES.json --unblind experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts/TRUTH.json --recovery experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts/RECOVERY.json --recovery-lock experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts/RECOVERY_LOCK.json
```

`generate.py --replay-truth ... --output-dir ... --lock ...` also replays the
released seed into a fresh directory. The independent validator reconstructs
the same draws without importing that generator.

No manuscript image, sealed folio, native word meaning or native key is tested.

Publication rehearsal reproduced all 576 starts and every winning result in a
clean working tree. See `artifacts/REPLAY_VALIDATION.json`.
