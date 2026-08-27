# GDT538 — final 159 phrase consistency edition

Status: `PASS_ALL_159_HAVE_CANONICAL_PHRASES__Y_RESTORED_AS_ARGUMENT`

GDT538 replaces 152 inherited phrase placeholders with a complete neutral
German workshop layer. It keeps a slot-exact ordered reading beside each
fluent phrase and leaves every GDT537 recipe unchanged.

Run and validate:

```bash
python3 experiments/yolo/gdt538_final_159_phrase_consistency_edition/src/run.py
python3 experiments/yolo/gdt538_final_159_phrase_consistency_edition/src/validate.py
```

Lookup:

```bash
python3 experiments/yolo/gdt538_final_159_phrase_consistency_edition/src/phrase_surface.py \
  --surface aiicthy --domain PROSE_STREAM
```
