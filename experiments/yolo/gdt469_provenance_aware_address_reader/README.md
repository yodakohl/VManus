# GDT469 — provenance-aware address reader

Status: `PROVENANCE_AWARE_ADDRESS_INTAKE_READY`

The executable reader now returns the GDT466 working reading, exact channel
trace and GDT468 recipe-support tier in one JSON object.

```bash
python3 experiments/yolo/gdt469_provenance_aware_address_reader/src/read_supported_address.py \
  otxainy STAR_BEARING_RING_POSITION
```

See `REPORT.md` for the replay result and example output.
