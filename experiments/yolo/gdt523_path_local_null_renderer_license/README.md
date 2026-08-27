# GDT523 — path-local null renderer license

Status: `PASS_PATH_LOCAL_DOMINANT_NULL_LICENSE`

GDT523 applies GDT522's visible-but-null edit inventory directly to renderer
alignment paths. A target no longer needs to leave another known whole surface
after the visible insertion is removed.

The selected light setting preserves all current GDT522 decisions. In the old
four-fold rehearsal it keeps 1,096 rank-one hits, raises top-three from 1,386
to 1,387 and lowers rank sum from 2,113 to 2,111. A deliberately retained
trade-off atlas shows why a stronger `qef` correction is not the default.

```bash
python3 experiments/yolo/gdt523_path_local_null_renderer_license/src/run.py
python3 experiments/yolo/gdt523_path_local_null_renderer_license/src/validate.py
python3 experiments/yolo/gdt523_path_local_null_renderer_license/src/align_surface.py \
  --surface NEUE_FORM --domain PROSE_STREAM --top 5
```
