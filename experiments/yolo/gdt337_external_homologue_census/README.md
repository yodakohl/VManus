# GDT337 — blind external homologue census

Status: `NO_VIABLE_FROZEN_ENDPOINT`

GDT337 audits readable medieval astronomical/computistical diagrams before any
Voynich joint-tuple or text scoring. It asks whether an external source fixes a
complete slot order and ownership map that can be transferred through a
geometry-only Voynich correspondence on disjoint physical folios.

It finds **zero currently viable endpoints**. The strongest new external donor,
British Library Add MS 25435, has a numbered I–XXVIII lunar wheel, a movable
pointer, and 28 readable associated records. Current Voynich 28-item targets do
not have both a text-blind phase and independent-folio transfer capacity.

Files:

- `METHOD.md` — frozen eligibility and access rules.
- `SOURCE_AUDIT.md` — source-by-source provenance audit.
- `REPORT.md` — result, near-misses, and acquisition requirements.
- `artifacts/gdt337_external_source_manifest.tsv` — 14 external witnesses or
  source families.
- `artifacts/gdt337_voynich_topology_capacity.tsv` — text-blind target
  inventory only.
- `artifacts/gdt337_candidate_correspondences.tsv` — 11 audited near-matches.
- `artifacts/gdt337_viable_endpoint_freeze.tsv` — header-only because no row
  passes every gate.
- `artifacts/gdt337_result.json` and `gdt337_validation.json` — compact result
  and 45-check independent mechanical validation.

Run:

```bash
python3 experiments/yolo/gdt337_external_homologue_census/src/run.py
python3 experiments/yolo/gdt337_external_homologue_census/src/validate.py
```

No Voynich transcription, tuple identity, PAGE_HOST, source-family value, or
manuscript image is loaded. f84 remains forbidden.
