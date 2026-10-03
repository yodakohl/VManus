# GDT1162 — nominal source-domain priority

Status: NO_ROBUST_SOURCE_PRIORITY. See REPORT.md and CANDIDATE_TABLE.md for the completed four-work comparison. WATER/AIR dominates the manufactured pair, but neither overall candidate receives priority after the fixed natural-object comparison. No target concept scores or translation.

Read METHOD.md, ANNOTATION_GUIDE.md and SPEC.json. Raw and extracted full texts remain external. Use an external cache directory:

```sh
python3 experiments/yolo/gdt1162_nominal_source_domain_prior/src/extract.py --cache "$VMANUS_SOURCE_CACHE/gdt1162_sources" --fetch
python3 experiments/yolo/gdt1162_nominal_source_domain_prior/src/make_windows.py --cache "$VMANUS_SOURCE_CACHE/gdt1162_sources"
python3 experiments/yolo/gdt1162_nominal_source_domain_prior/src/run.py
python3 experiments/yolo/gdt1162_nominal_source_domain_prior/src/validate.py --cache "$VMANUS_SOURCE_CACHE/gdt1162_sources"
```

The executable accounts for explicit reading packets; it cannot reproduce comprehension automatically. Preserve source hash failures and uncertainty rather than substituting changed editions. Same-window co-occurrence is not a sentence relation. Source priority cannot reject GDT827's local reading or translate qokain/qokaiin.
