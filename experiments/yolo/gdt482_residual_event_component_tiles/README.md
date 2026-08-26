# GDT482 — residual event component tiles

GDT482 opens the 45 single-event tails left by GDT481 and tiles their fixed
GDT479 meanings with recurrent contiguous component fragments. It keeps both a
same-model reading and a broader model-free backoff, while preserving every
surface, learned name, event model, and German default reading.

The result is no longer a tail of 45 opaque events. Thirty-nine are fully made
from components recurrent in the same model, and 42 are fully recurrent when
the same component may be borrowed across models. Two of the remaining three
contain only learned lexical slots. The only unique functional residue is
`sodar`, specifically `ZWEITE STUFE · MARKIEREN`.

See [`REPORT.md`](REPORT.md) for the compact interpretation and
[`artifacts/GDT482_RESIDUAL_EVENT_COMPONENT_TILES.md`](artifacts/GDT482_RESIDUAL_EVENT_COMPONENT_TILES.md)
for all 45 tiled readings.

```bash
python3 experiments/yolo/gdt482_residual_event_component_tiles/src/run.py
python3 experiments/yolo/gdt482_residual_event_component_tiles/src/validate.py
```
