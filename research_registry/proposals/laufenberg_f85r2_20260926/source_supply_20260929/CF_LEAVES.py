#!/usr/bin/env python3
"""Keep both admitted sides of every leaf selected by fixed direct contacts."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
SOURCE = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
COLS = "source_group_id,edition,page,locus,kind,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw"
contacts = json.loads((BASE / "CF_DIRECT_CONTEXTS.json").read_text())
leaves = {r["page"][:-1] for r in contacts["edges"]}
assert leaves == {"f9", "f50"}
pages = sorted(leaf + side for leaf in leaves for side in ("r", "v"))
cmd = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "page"]
for page in pages:
    cmd += ["--allow", page]
cmd += ["--columns", COLS]
result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
assert {r["page"] for r in rows} == set(pages)
frames = {}
for row in rows:
    frames.setdefault((row["edition"], row["page"], row["locus"]), []).append(row)
lines = [{"edition": key[0], "page": key[1], "locus": key[2], "groups": sorted(rs, key=lambda r: int(r["source_group_index"]))} for key, rs in frames.items()]
packet = {"scope": "Both complete admitted text sides of physical leaves f9 and f50, all alternate readers",
    "exposure": "Already exposed exploratory data; f9r and f9v are not independent leaves",
    "command": cmd, "guard_receipt": result.stderr.strip(),
    "source_sha256": hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(),
    "direct_contexts_sha256": hashlib.sha256((BASE / "CF_DIRECT_CONTEXTS.json").read_bytes()).hexdigest(),
    "rows": rows, "lines": lines}
(BASE / "CF_FULL_LEAVES.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
md = ["# CF — whole f9 and f50 text leaves", "All raw groups and native paragraph flags retained in CF_FULL_LEAVES.json. Readers are alternatives; exposure is not confirmation."]
for x in lines:
    md += ["", f"## {x['edition']} {x['locus']}", "`" + " ".join(r["ivtff_group_raw"] for r in x["groups"]) + "`"]
(BASE / "CF_FULL_CONTEXTS.md").write_text("\n".join(md) + "\n")
print(json.dumps({"pages": pages, "groups": len(rows), "lines": len(lines),
    "contact_lines_all_readers": [x for x in lines if x["locus"] in {r["locus"] for r in contacts["edges"]}]}, indent=2))
