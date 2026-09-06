# Reproduce GDT836

Python3 standard library and a C++17 compiler are sufficient. No GPU, external LLM or API key is used. Runtime files stay
ignored. The source-only capacity replay additionally needs UDante at pinned
commit `e02420457780c6fbb503ba39a7d8798ab6a8645c`, under this experiment's
`runtime/udante_source` or supplied through --source-dir. Source attribution,
license and exact commitments are in sources/.

From the repository root:

```sh
python3 experiments/yolo/gdt836_integrated_wholeword_precedence/src/prepare.py --check
python3 experiments/yolo/gdt836_integrated_wholeword_precedence/src/test_constraint.py
python3 experiments/yolo/gdt836_integrated_wholeword_precedence/src/run.py --build
python3 experiments/yolo/gdt836_integrated_wholeword_precedence/src/validate.py --check
```

The historical guard is deliberately stopped:

```sh
python3 experiments/yolo/gdt836_integrated_wholeword_precedence/src/run.py --fit
```

It reports SOURCE_CAPACITY_STOP and exits2 without generating keys, ciphertext
or fits. Do not change that source split or its support gates to make it run.
The actual reusable engine interface is documented by its usage output and
ENGINE_SPEC.json; only invented test fixtures were run here. It is not a
registered historical fit orchestrator or a fresh recovery result.
