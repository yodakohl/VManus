#!/usr/bin/env python3
"""Selector-first recount for QH0 repeated three-group sequences.

The mixed source is materialized only by vmanus-exp query-tsv.  This script
then reads that bounded projection and counts exact adjacent raw groups within
each edition/locus, retaining group indices and separator classes.
"""
from collections import defaultdict
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
allowlist = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
source = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
pages = [line.strip() for line in allowlist.read_text().splitlines()[1:] if line.strip()]
cmd = ["./vmanus-exp", "query-tsv", str(source), "--selector", "page"]
for page in pages:
    cmd += ["--allow", page]
cmd += ["--forbid-prefix", "f84", "--columns",
        "page,locus,edition,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw"]
text = subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.PIPE)

rows = defaultdict(list)
for line in text.splitlines()[1:]:
    page, locus, edition, index, count, left, right, raw = line.split("\t")
    rows[(edition, locus)].append((int(index), raw, left, right))

hits = defaultdict(dict)
for (edition, locus), values in rows.items():
    values.sort()
    for i in range(len(values) - 2):
        tri = values[i:i + 3]
        if [x[0] for x in tri] != list(range(tri[0][0], tri[0][0] + 3)):
            continue
        key = tuple(x[1] for x in tri)
        hits[key].setdefault(locus, []).append({
            "edition": edition,
            "groups_1based": [x[0] for x in tri],
            "internal_right_separators": [x[3] for x in tri[:2]],
        })

for key, loci in sorted(hits.items(), key=lambda item: (-len(item[1]), item[0])):
    if len(loci) >= 2:
        print("\t".join((str(len(loci)), *key)))
        for locus, occurrences in sorted(loci.items()):
            print("\t", locus, occurrences)
