#!/usr/bin/env python3
"""Guarded inventory of two literal adjacent pairs and their immediate lines."""
from collections import defaultdict
from pathlib import Path
import hashlib, json, subprocess

root = Path(__file__).resolve().parents[2]
allowlist = root / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
source = root / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
cmd = ["./vmanus-exp", "query-tsv", str(source.relative_to(root)), "--selector", "page"]
for page in allowlist.read_text().splitlines()[1:]:
    if page.strip(): cmd += ["--allow", page.strip()]
cmd += ["--forbid-prefix", "f84", "--forbid-prefix", "f84r", "--columns",
        "page,locus,edition,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw"]
query = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=True)
text = query.stdout
lines = defaultdict(list)
for line in text.splitlines()[1:]:
    page, locus, edition, index, count, left, right, raw = line.split("\t")
    lines[(edition, locus)].append({"index": int(index), "raw": raw, "left": left, "right": right})

result = {"source": "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
          "allowlist": "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv",
          "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
          "guard_command": cmd, "guard_statistics": query.stderr.strip(), "pairs": {}}
for pair in (("shol", "kaiin"), ("cheor", "chey")):
    key = " ".join(pair); occurrences = []
    for (edition, locus), groups in sorted(lines.items()):
        groups.sort(key=lambda x: x["index"])
        for i in range(len(groups) - 1):
            a, b = groups[i:i+2]
            if (a["raw"], b["raw"]) != pair or b["index"] != a["index"] + 1: continue
            abab = i + 3 < len(groups) and tuple(x["raw"] for x in groups[i:i+4]) == pair + pair
            occurrences.append({"locus": locus, "edition": edition,
                                "groups_1based": [a["index"], b["index"]],
                                "internal_seams": [a["right"], b["left"]],
                                "abab": abab,
                                "line_raw_groups": [x["raw"] for x in groups], "line_groups": groups})
    result["pairs"][key] = occurrences
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
