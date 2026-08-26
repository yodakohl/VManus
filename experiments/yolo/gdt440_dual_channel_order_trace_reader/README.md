# GDT440 — dual-channel order-trace reader

Status: `ORDER_COLLISIONS_RESOLVED__CO_VALUED_LOCAL_CHANNELS_RETAINED`

The prospective reader now emits both the exact ordered meaning trace and the
fluent state-aware clause.

```bash
python3 experiments/yolo/gdt440_dual_channel_order_trace_reader/src/dual_channel_stream_read.py \
  --input INPUT.tsv --output READINGS.tsv
```

See [REPORT.md](REPORT.md) and [METHOD.md](METHOD.md).
