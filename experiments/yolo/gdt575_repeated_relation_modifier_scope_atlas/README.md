# GDT575 — repeated relation/modifier scope atlas

Status: `PASS_4609_RELATION_MODIFIER_SLOTS__96_DUPLICATE_GROUPS_IN_90_EVENTS__3_SAME_ROOT_ADJACENT__62_SAME_ROOT_INTERRUPTED__31_SURFACE_COLLISIONS__17_OUTER_INNER_PAIRS__ZERO_SCOPE_COLLAPSE`

GDT575 inventories every current German relation and modifier phrase in the
complete GDT574 event edition. It distinguishes true raw-adjacent repetition,
interrupted repetition, German surface collisions between different atoms, and
the deliberately different outer/inner scope pair.

Run:

```bash
python3 experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/src/run.py
python3 experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/src/validate.py
```

The primary result is [REPORT.md](REPORT.md). This experiment does not rewrite
the readable edition; GDT574 remains its source.
