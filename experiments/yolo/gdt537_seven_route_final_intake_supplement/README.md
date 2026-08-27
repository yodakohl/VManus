# GDT537 — seven-route final intake supplement

Status: `PASS_SEVEN_ROUTE_FINAL_INTAKE_SUPPLEMENT`

This experiment makes GDT536's complete 159-surface prose edition executable
ahead of the older GDT517 compiler and preserves all seven post-intake
revisions with named route cards.

Run and validate:

```bash
python3 experiments/yolo/gdt537_seven_route_final_intake_supplement/src/run.py
python3 experiments/yolo/gdt537_seven_route_final_intake_supplement/src/validate.py
```

Lookup:

```bash
python3 experiments/yolo/gdt537_seven_route_final_intake_supplement/src/intake_surface.py \
  --surface aiicthy --domain PROSE_STREAM
```
