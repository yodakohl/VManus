"""Small existing-record audit; no search, target cache, images or experiment."""
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent

def read_tsv(path):
    with (ROOT / path).open() as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

sources = {
    "graft": "experiments/yolo/gdt1021_graft_complete_scoped_instructions/artifacts/ALL_POSITIONS.tsv",
    "clock": "experiments/yolo/gdt1030_clock_whole_reference_consequences/artifacts/ALL_POSITIONS.tsv",
    "unweaving": "experiments/yolo/gdt1020_unweaving_complete_assertion_graph/artifacts/ALL_POSITIONS.tsv",
    "rota": "experiments/yolo/gdt1026_rota_crossleaf_frozen_meanings/artifacts/ALL_POSITIONS.tsv",
    "transport": "research_registry/work_batches/ten_hours_20260915/TRANSPORT_RAW377_COMPLETE_EXPLORATORY_READING_20260920.json",
}
rows = []
for key in ("graft", "clock", "unweaving", "rota"):
    for row in read_tsv(sources[key]):
        if key == "graft" and row["candidate"] != "GROUPED":
            continue
        if key == "unweaving" and row["candidate"] != "DIRECT":
            continue
        if key == "rota" and not row["locus"].startswith("f76v."):
            continue
        rows.append({
            "candidate": key,
            "locus": row["locus"],
            "position": row.get("position", row.get("index", row.get("group"))),
            "raw": row.get("raw", row.get("form", row.get("word"))),
            "hypothetical_type": row.get("value", row.get("lexical_type", row.get("tag"))),
            "hypothetical_meaning": row.get("proposed_value", row.get("denotation", row.get("hypothetical_value", row.get("meaning")))),
            "clause": row["clause"],
            "confirmed": False,
        })
transport = json.loads((ROOT / sources["transport"]).read_text())
for row in transport["all_63_positions"]:
    rows.append({"candidate": "transport", "locus": row["locus"], "position": row["group"], "raw": row["raw"], "hypothetical_type": row["symbol"], "hypothetical_meaning": row["meaning"], "clause": row["clause"], "confirmed": False})
assert len(rows) == 214
expected = {"graft": (23, 23), "clock": (40, 33), "transport": (63, 47), "unweaving": (33, 24), "rota": (55, 38)}
for key, (n, types) in expected.items():
    subset = [r for r in rows if r["candidate"] == key]
    assert len(subset) == n, (key, len(subset))
    assert len({r["raw"] for r in subset}) == types, key
    assert all(not r["locus"].startswith(("f84", "f116v")) for r in subset)
with (OUT / "J_EXISTING_WHOLE_ASSIGNMENTS.tsv").open("w") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

# This exact complete paragraph was already printed in GDT813, not newly chosen.
source = "experiments/yolo/gdt813_f17_content_word_transfer/REPORT.md"
text = (ROOT / source).read_text()
paragraph = re.search(r"The complete ZL3b paragraph remains:\s*```text\n(.*?)\n```", text, re.S).group(1)
groups = paragraph.split()
old = {r["raw"] for r in rows if r["candidate"] == "graft"}
role = {"shol", "cthy", "qor", "chor", "shor", "cho", "cheteg", "som"}
guard = {"tsho", "qof", "qokcheor", "cphor", "cphaldy", "cthey", "dair", "qody"}
capacity = {
    "status": "EXISTING_REPORT_INVENTORY_AUDIT_NOT_NEW_EXPERIMENT",
    "predecessor": "IDEA000526",
    "paragraph": "ZL3b f17r.7-12 as completely printed by GDT813",
    "source": source,
    "source_sha256": hashlib.sha256((ROOT / source).read_bytes()).hexdigest(),
    "groups": len(groups), "types": len(set(groups)),
    "old_inventory_count": len(old),
    "all_old_matches": [x for x in groups if x in old],
    "participant_reference_matches": sorted(set(groups) & role),
    "method_guard_matches": sorted(set(groups) & guard),
    "required": "At least two distinct role/reference forms plus one method/season/guard form; new-value cap 14.",
    "decision": "The printed ZL unit cannot satisfy IDEA526's unchanged reuse gate; not an execution or an all-reader result.",
    "unknown_types_under_old_23": sorted(set(groups) - old),
}
assert len(groups) == 29 and len(set(groups)) == 28
assert not capacity["all_old_matches"]
(OUT / "J_GRAFT526_EXISTING_CAPACITY.json").write_text(json.dumps(capacity, ensure_ascii=False, indent=2) + "\n")
receipts = [{"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()} for path in list(sources.values()) + [source]]
(OUT / "J_ASSIGNMENT_INPUT_RECEIPTS.json").write_text(json.dumps(receipts, indent=2) + "\n")
print("PASS: 214 already-owned assigned positions; five complete working units; zero confirmed meanings; IDEA526 ZL has 0/23 old exact forms.")
