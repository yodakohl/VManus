# Reproduce GDT835

Python 3 standard library suffices. No GPU, model training or API is used.
All primary inputs are committed GDT834 artifacts. From the repository root:

```sh
python3 experiments/yolo/gdt835_wholeword_precedence_audit/src/test_precedence.py
python3 experiments/yolo/gdt835_wholeword_precedence_audit/src/run.py --gate --check
python3 experiments/yolo/gdt835_wholeword_precedence_audit/src/run.py --evaluate --check
python3 experiments/yolo/gdt835_wholeword_precedence_audit/src/validate.py --check
```

For first execution from the public registration commit, omit --check and run
--gate before --evaluate. The gate refuses to overwrite an existing lock.
Neither stage creates or selects a key or changes GDT834. The independent
validator can use --gate-only before confirmation artifacts exist.

The separate exploratory source-context script additionally requires the pinned
UDante checkout used in GDT834; its --help documents the source-directory option.
It is not imported by the primary gate or confirmation. Its raw corpus stays
outside published experiment artifacts, and its report commits source hashes.
