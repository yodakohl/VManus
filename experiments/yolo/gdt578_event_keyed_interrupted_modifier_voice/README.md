# GDT578 — event-keyed interrupted-modifier voice

Status: `PASS_5_ATTACHMENT_CLASSES__3_PROSE_FRAMES__20_HEAD_VOICES__58_EVENT_CARDS__60_GROUPS__121_REPEAT_SLOTS__173_ORDERED_MODIFIER_FRAGMENTS__61_PARTICLES__5122_EXACT_ROUNDTRIPS__ONE_CONFLICT_UNCHANGED`

GDT578 turns GDT577's attachment atlas into a readable German workshop voice
for all 58 conflict-free target events. Every written repeat slot remains
visible and receives its local action or sequence head; overlapping groups are
rendered once at event level.

Run:

```bash
python3 experiments/yolo/gdt578_event_keyed_interrupted_modifier_voice/src/run.py
python3 experiments/yolo/gdt578_event_keyed_interrupted_modifier_voice/src/validate.py
```

The primary result is [REPORT.md](REPORT.md). The complete thirty-page reading
is in `artifacts/GDT578_ATTACHMENT_VOICE_THIRTY_PAGE_EDITION.md`.
