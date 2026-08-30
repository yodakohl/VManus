# GDT645 — ranked five-surface V22 completion

Status: `PASS_5_RANKED_SURFACES__115_POSITIONS__6_NEW_COMPLETE_LINES`

Five exact whole-surface cards render 115 positions and close six passages:
`oky`, `otchor`, `ychair`, `cheaiin`, and `cthom`. The public working edition
is V22 with 303 dictionary rows, 256 exact glosses and 10,345 concretely read
token positions.

Start with [REPORT.md](REPORT.md). Reproduce with:

```bash
python3 experiments/yolo/gdt645_ranked_five_surface_completion/src/run.py
python3 experiments/yolo/gdt645_ranked_five_surface_completion/src/validate.py
```

See [METHOD.md](METHOD.md), `experiment.json`, and `artifacts/README.md` for the
frozen procedure and artifact map.
