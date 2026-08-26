# GDT435 — context-safe shadow reader

Status: `CONTEXT_SAFE_READER_REQUIRED__49_CARD_DECK_UNCHANGED`

GDT435 shadow-replays all 4,576 known events and corrects one practical flaw in
the first intake command: a component recipe identifies a card, but it does
not always identify the inherited verb and object of the full sentence.

Use the corrected command:

```bash
python3 experiments/yolo/gdt435_observed_recipe_shadow_fallback/src/context_safe_read_recipe.py \
  --recipe AIIN --register HERBAL
```

Add `--inherited-action` and `--inherited-argument` for an exact known-state
reading, or `--event-id` for a replay of a known occurrence.

See [REPORT.md](REPORT.md) and [METHOD.md](METHOD.md).
