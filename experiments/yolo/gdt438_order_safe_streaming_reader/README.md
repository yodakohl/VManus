# GDT438 — order-safe streaming reader

Status: `ORDER_SAFE_ORACLE_FREE_STREAMING_READER_COMPLETE`

This is the prospective reader to use after a visible surface has been
segmented into the current components. It carries page-owner state and keeps
written relation/argument order.

```bash
python3 experiments/yolo/gdt438_order_safe_streaming_reader/src/order_safe_stream_read.py \
  --input INPUT.tsv --output READINGS.tsv
```

See [REPORT.md](REPORT.md) and [METHOD.md](METHOD.md).
