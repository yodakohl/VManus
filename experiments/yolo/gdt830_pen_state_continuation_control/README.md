# GDT830 — pen-state continuation control

Status: REGISTERED_UNSCORED.

See PREREGISTRATION.md and src/SPEC.json for the frozen task. This is a
control on unambiguous-looking row strips, not a disputed-block order test.

Fetch/verify only the four registered native images and run:

```sh
python3 experiments/yolo/gdt830_pen_state_continuation_control/src/run.py --fetch
```

The default cache is .cache/gdt830_native; --cache-dir can select another
existing cache. Exact image hashes are checked before measurement. Native
JPEGs are not duplicated in this experiment directory. Use --check for
artifact replay after generation. The validator reconstructs the statistical
accounting from the measured descriptor table, with its coverage explicit.
