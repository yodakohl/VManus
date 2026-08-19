# GDT360 — existing-annotation joint grounding

GDT360 asks whether the repository's already acquired, provenance-bound visual
annotations contain a reusable visual–formal signal that was missed by the
earlier narrow GDT002 channels. It performs no new image inspection. It
canonicalizes the existing evidence by physical locus, keeps annotation axes
and source lineages separate, joins them to the frozen source-native family
projection, and ranks compact formal signatures by held-folio transfer.

The experiment is exploratory. Its candidates are neutral visual/formal
associations, not semantic roles, lexemes, or translations. See [METHOD.md](METHOD.md)
and [REPORT.md](REPORT.md).

Run:

```bash
python3 experiments/yolo/gdt360_existing_annotation_joint_grounding/src/run.py
python3 experiments/yolo/gdt360_existing_annotation_joint_grounding/src/validate.py
```

The `f84*` selector is rejected before any source row is parsed.
