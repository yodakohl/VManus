#!/usr/bin/env python3
"""Document integrity of copied owned contexts; no parser or semantic test."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
checks = []


def check(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


def read(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


source_base = ROOT / "experiments/yolo/gdt943_solkain_second_leaf_complete_clause/artifacts"
for authored, original in [
    ("AB_CONTEXT_SOURCE_LINES.json", "CONTEXT_SOURCE_LINES.json"),
    ("AB_CONTEXT_PARAGRAPHS.json", "CONTEXT_PARAGRAPHS.json"),
    ("AB_INHERITED_LEXICONS.json", "LEXICONS.json"),
]:
    check("byte-identical owned copy " + authored,
          (BASE / authored).read_bytes() == (source_base / original).read_bytes())

lines = read("AB_CONTEXT_SOURCE_LINES.json")
summary = read("AB_ACCOUNT_SUMMARY.json")
lexicons = read("AB_INHERITED_LEXICONS.json")
new_words = set(summary["new_values"])
check("five new exact forms", new_words == {"keey", "qoty", "dalched", "qokair", "dalom"})
check("eight unchanged 41-value branches", len(lexicons) == 8 and all(len(v) == 41 for v in lexicons.values()))
flat = []
expected_occurrences = []
per_unit = {}
for block in lines:
    groups = [dict(zip(block["columns"], row)) for row in block["groups"]]
    flat.extend(groups)
    key = block["edition"] + " " + groups[0]["page"]
    counts = per_unit.setdefault(key, Counter())
    for i, group in enumerate(groups):
        word = group["ivtff_group_raw"]
        status = "new" if word in new_words else "inherited" if word in next(iter(lexicons.values())) else "unassigned"
        counts[status] += 1
        counts["total"] += 1
        if word in new_words:
            expected_occurrences.append({
                "edition": block["edition"], "locus": block["locus"],
                "group_id": group["source_group_id"], "word": word,
                "previous": groups[i-1]["ivtff_group_raw"] if i else "",
                "next": groups[i+1]["ivtff_group_raw"] if i+1 < len(groups) else "",
                "left_separator": group["left_separator"], "right_separator": group["right_separator"],
                "paragraph_start": group["paragraph_start"], "paragraph_end": group["paragraph_end"],
                "full_raw_line": " ".join(x["ivtff_group_raw"] for x in groups),
            })
with (BASE / "AB_FIVE_WORD_OCCURRENCES.tsv").open(encoding="utf-8", newline="") as handle:
    saved_occurrences = list(csv.DictReader(handle, delimiter="\t"))
check("all 17 exact occurrences with complete owned lines", expected_occurrences == saved_occurrences and len(saved_occurrences) == 17)
check("all140 lines and1553 groups", len(lines) == 140 and len(flat) == 1553)
check("all per-unit lexical account counts", per_unit == summary["per_edition_page"])
totals = Counter()
for counts in per_unit.values():
    totals.update(counts)
check("394 old 17 new 1142 unknown", totals == {"total": 1553, "inherited": 394, "new": 17, "unassigned": 1142})
check("no acquired IT f80r20", not any(b["edition"] == "IT2a" and b["locus"] == "f80r.20" for b in lines))
check("all four exact keey targets", sum(g["ivtff_group_raw"] == "keey" for g in flat) == 4)

# Confirm the four manually authored source positions, not the truth of reference.
choices = read("AB_REFERENCE_CHOICES.json")["choices"]
intervals = []
for choice in choices:
    target_id = choice["edition"] + "|" + choice["target"] + "|G" + str(choice["target_group"]).zfill(3)
    source_id = choice["edition"] + "|" + choice["source"] + "|G" + str(choice["source_group"]).zfill(3)
    target = next(g for g in flat if g["source_group_id"] == target_id)
    unit = [g for g in flat if g["edition"] == choice["edition"] and g["page"] == target["page"]]
    target_index = next(i for i, g in enumerate(unit) if g["source_group_id"] == target_id)
    previous = [(i, g) for i, g in enumerate(unit[:target_index]) if g["ivtff_group_raw"] == "qokeedy"]
    check("authored exact source position " + target_id, bool(previous) and previous[-1][1]["source_group_id"] == source_id)
    check("authored exact target " + target_id, target["ivtff_group_raw"] == "keey")
    interval = unit[previous[-1][0]+1:target_index]
    intervals.append({"source_id": source_id, "target_id": target_id, "status": choice["status"],
                      "intervening_groups": interval, "group_count": len(interval),
                      "unassigned_count": sum(g["ivtff_group_raw"] not in new_words and g["ivtff_group_raw"] not in next(iter(lexicons.values())) for g in interval)})
(BASE / "AB_REFERENCE_INTERVALS.json").write_text(json.dumps({"kind": "AUTHORED_LINK_SOURCE_ACCOUNT_NOT_SEMANTIC_TEST", "intervals": intervals}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

card = read("AB_01_FLOW_EVENT_ASSERTION.json")
check("raw unreviewed only", card["status"] == "RAW_UNREVIEWED_NOT_SELECTED_NOT_TESTED")
check("one783 receipt", read("AB_ADD_RECEIPT.json")["id"] == "IDEA000783")
for receipt in read("AB_INPUTS.json")["inputs"]:
    check("source hash " + receipt["path"], hashlib.sha256((ROOT / receipt["path"]).read_bytes()).hexdigest() == receipt["sha256"])

result = {"status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
          "kind": "DOCUMENT_INTEGRITY_ONLY_NO_SEMANTIC_TEST", "check_count": len(checks), "checks": checks}
(BASE / "AB_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "check_count": result["check_count"], "kind": result["kind"]}))
raise SystemExit(0 if result["status"] == "PASS" else 1)
