# GDT470 — future address intake worksheet

GDT470 replays the 89 label-derived unseen-core forms through the supported
GDT469 reader, summarizes the result by owner class and visible channel shape,
and publishes four still-unreleased future-page slots plus an empty item
template.

Build and validate:

```bash
python3 experiments/yolo/gdt470_future_address_intake_worksheet/src/run.py
python3 experiments/yolo/gdt470_future_address_intake_worksheet/src/validate.py
```

Prepare one supplied surface as a complete worksheet row:

```bash
python3 experiments/yolo/gdt470_future_address_intake_worksheet/src/prepare_future_address.py \
  otxainy STAR_BEARING_RING_POSITION --page-slot PAGE_SLOT_1 --item-slot ITEM_001
```

The four page slots remain unopened. The command reads a supplied form; it
does not generate a manuscript spelling or identify an individual object.
