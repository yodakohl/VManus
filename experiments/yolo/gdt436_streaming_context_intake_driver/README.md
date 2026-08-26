# GDT436 — streaming context intake driver

Status: `ORACLE_FREE_STREAMING_CONTEXT_DRIVER_COMPLETE`

This is the prospective front end for the recipe reader. It accepts ordered
event rows with page, register, owner and component recipe, maintains two tiny
state values per owner, and emits a full clause or a stop.

```bash
python3 experiments/yolo/gdt436_streaming_context_intake_driver/src/stream_read.py \
  --input INPUT.tsv --output READINGS.tsv
```

The input needs no inherited-action column, inherited-argument column, or known
event ID. See [REPORT.md](REPORT.md) and [METHOD.md](METHOD.md).
