# GDT471 — empirical address shell phrasebook

GDT471 replaces only the learned spans of GDT470's 89 label-derived source
forms with ordered `{NAME_n}` slots. It publishes concrete surface templates,
component templates, slot topologies and a separate owner-family sensitivity
deck, then adds empirical familiarity to the GDT470 worksheet row.

Build and validate:

```bash
python3 experiments/yolo/gdt471_empirical_address_shell_phrasebook/src/run.py
python3 experiments/yolo/gdt471_empirical_address_shell_phrasebook/src/validate.py
```

Prepare a ranked row:

```bash
python3 experiments/yolo/gdt471_empirical_address_shell_phrasebook/src/prepare_ranked_future_address.py \
  otexeeon PICTURED_PLANT --page-slot PAGE_SLOT_1 --item-slot ITEM_001
```

The command ranks an already supplied form. It does not generate a surface or
identify the learned name inside a slot.
