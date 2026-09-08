#!/usr/bin/env python3
"""Find exact repeated contiguous raw-group sequences of lengths 4--6."""
from collections import defaultdict
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
allow = root / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
source = root / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
cmd = ["./vmanus-exp", "query-tsv", str(source), "--selector", "page"]
for page in allow.read_text().splitlines()[1:]:
    if page.strip(): cmd += ["--allow", page.strip()]
cmd += ["--forbid-prefix", "f84", "--columns", "page,locus,edition,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw"]
rows = defaultdict(list)
for line in subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.PIPE).splitlines()[1:]:
    page, locus, edition, index, count, left, right, raw = line.split("\t")
    rows[(edition, locus)].append((int(index), raw, right))
hits = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
for (edition, locus), values in rows.items():
    values.sort()
    for n in range(4, 7):
        for i in range(len(values) - n + 1):
            window = values[i:i+n]
            if [x[0] for x in window] == list(range(window[0][0], window[0][0] + n)):
                hits[n][tuple(x[1] for x in window)][locus][edition] = {
                    "groups_1based": [x[0] for x in window],
                    "internal_right_separators": [x[2] for x in window[:-1]],
                }
for n in range(6, 3, -1):
    for sequence, loci in hits[n].items():
        if len(loci) >= 2:
            print(n, sequence, dict(loci))
