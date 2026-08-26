# GDT437 — future card state transition order repair

Status: `RELATION_ARGUMENT_ORDER_COLLISION_REPAIRED`

The 49-card reader previously rendered `AIR+Y` and `Y+AIR` identically in
every reachable state. GDT437 preserves their written order and gives all 49
cards distinct transition signatures.

```bash
python3 experiments/yolo/gdt437_future_card_state_transition_order_repair/src/run.py
python3 experiments/yolo/gdt437_future_card_state_transition_order_repair/src/validate.py
```

See [REPORT.md](REPORT.md) and [METHOD.md](METHOD.md).
