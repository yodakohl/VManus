# GDT625 — State paths expose Blattgut, not yet a drying verb

Status: `CTHY_BLATTGUT_PROMOTED__STATE_PATHS_SPLIT_PART_CONTRAST_FROM_PROCESS`

The strongest new concrete reading is:

```text
cth-  = vegetative plant-part / leaf-drug family
cthy  = Blattgut, Blattdroge (folium)
```

`cthy` occurs 92 times in the safe panel, 90 times in Herbal, and has 85
conservative identical-token witnesses across ZL3b/IT2a/RF1b. It belongs to a
408-token, 69-type `cth-` family. It makes 32 same-line contacts with current
root or reproductive-part candidates and twelve immediate contacts with a
terminal quality form. Eleven of those twelve carry the current dry `ch`
value.

This corrects the first reading of f29v.4:

```text
ysho  otshy okaiin  cthy oltchy  s shot sho okaiin
       cold-moist    leaf-drug cold-dry

[otshy okaiin] [cthy oltchy]
"cold-moist preparation/material; cold-dry leaf drug"
```

The local two-part binding is better than treating the line automatically as
"moist, then dry." A temporal reading remains a secondary possibility.

Across all 1,162 terminal quality-family tokens there are 535 successive local
pairs and 63 moisture-axis flips. Same-line direction is exactly balanced:
17 dry-to-moist and 17 moist-to-dry. Six local three-state paths are all
dry-to-moist-to-dry, but no opened image establishes that all three states
belong to one carrier. Therefore:

- dry -> moist may be rendered "befeuchten/einweichen" only after carrier
  identity is established;
- moist -> dry may be rendered "trocknen" only after carrier identity is
  established;
- no isolated quality word receives an operation meaning;
- `otar` is the first low-confidence separate `then/until/process` candidate.

Rebuild and validate:

```bash
python3 experiments/yolo/gdt625_ordered_quality_state_transitions/src/run.py
python3 experiments/yolo/gdt625_ordered_quality_state_transitions/src/validate.py
```

See `REPORT.md` for the working translations and `artifacts/README.md` for the
compact evidence inventory.
