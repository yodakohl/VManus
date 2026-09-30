#!/usr/bin/env python3
"""Retain exact exposed occurrence obligations; no word decoder or score."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT))
from tools.word_profiles import ensure_cache, occurrences, receipt

FORMS = ("cthy", "otaiin", "oky")
PAIRS = {frozenset(pair) for pair in (
    ("cthy", "otaiin"), ("otaiin", "oky"), ("cthy", "oky")
)}
conn = ensure_cache(ROOT)
rows = [row for form in FORMS for row in occurrences(conn, form)]
assert len({row["source_group_id"] for row in rows}) == len(rows)
columns = list(rows[0])
with (BASE / "CF_OCCURRENCE_OBLIGATIONS.tsv").open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
edges = []
for row in rows:
    if frozenset((row["ivtff_group_raw"], row["next_literal"])) not in PAIRS:
        continue
    edges.append({
        "edition": row["edition"], "page": row["page"], "locus": row["locus"],
        "left_id": row["source_group_id"], "left_index": row["source_group_index"],
        "left": row["ivtff_group_raw"], "right": row["next_literal"],
        "separator": row["right_separator"],
    })
frames = []
for edition, page, locus in sorted({(r["edition"], r["page"], r["locus"]) for r in edges}):
    raw = [dict(r) for r in conn.execute(
        "SELECT * FROM groups WHERE edition=? AND page=? AND locus=? ORDER BY source_group_index",
        (edition, page, locus),
    )]
    frames.append({"edition": edition, "page": page, "locus": locus, "groups": raw})
packet = {
    "scope": "All admitted exact cthy/otaiin/oky occurrences; all direct contacts in either direction for three fixed pairs",
    "exposure": "Already exposed exploration; no independent confirmation or significance",
    "cache_receipt": receipt(conn),
    "counts": {form: dict(Counter(r["edition"] for r in rows if r["ivtff_group_raw"] == form)) for form in FORMS},
    "obligation_count": len(rows), "edges": edges, "contact_lines": frames,
    "ce_source_sha256": hashlib.sha256((BASE / "CE_SOURCE.json").read_bytes()).hexdigest(),
    "decision_sha256": hashlib.sha256((BASE / "CF_DECISION.md").read_bytes()).hexdigest(),
}
(BASE / "CF_DIRECT_CONTEXTS.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"counts": packet["counts"], "obligations": len(rows), "edges": edges}, indent=2))
