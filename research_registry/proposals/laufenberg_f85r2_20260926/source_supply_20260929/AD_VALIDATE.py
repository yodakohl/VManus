"""Validate AD documentary copying/accounting only; no meaning test or query."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[4]
checks = []


def check(name, value):
    checks.append({"name": name, "pass": bool(value)})


inputs = json.loads((HERE / "AD_INPUTS.json").read_text())
for item in inputs["inputs"]:
    check("input_hash:" + item["path"], hashlib.sha256(
        (REPO / item["path"]).read_bytes()).hexdigest() == item["sha256"])

source_path = REPO / "experiments/yolo/gdt1020_unweaving_complete_assertion_graph/src/SOURCE.json"
check("complete_source_byte_copy", (HERE / "AD_COMPLETE_SOURCE.json").read_bytes() == source_path.read_bytes())
source = json.loads(source_path.read_text())
account = json.loads((HERE / "AD_ACCOUNT.json").read_text())
parent = json.loads((REPO / "experiments/yolo/gdt1025_unweaving_two_paragraph_identity/src/SOURCE.json").read_text())["frozen_parent"]
check("unchanged_24_hypothetical_values", account["old_whole_values"] == parent["all_24_meanings_exact"])
check("unchanged_eight_clauses", account["old_clauses"] == parent["all_eight_clauses"])
expected = []
for projected, diplomatic in zip(source["projected_lines"], source["diplomatic_record"]["lines"]):
    for group, (word, raw) in enumerate(zip(projected["raw"].split(), diplomatic["words"]), 1):
        expected.append({"position": len(expected) + 1, "locus": projected["locus"],
                         "group": group, "projection": word, "raw": raw,
                         "hypothetical_meaning": parent["all_24_meanings_exact"][word],
                         "raw_meaning_bound": word == raw})
check("all_33_positions_exact", account["rows"] == expected and len(expected) == 33)
check("six_full_lines", len(source["projected_lines"]) == 6)
check("two_raw_forms_unbound", [(r["locus"], r["raw"]) for r in expected if not r["raw_meaning_bound"]] == [("f83r.29", "salche'dy"), ("f83r.30", "saii@208;")])
counts = account["counts"]
check("all_family_positions", counts["family_counts"] == {"qoky": 2, "qokey": 0, "qokeey": 2, "qokedy": 2, "qokeedy": 3} and counts["family_positions"] == 9)
check("24_projection_types", len({r["projection"] for r in expected}) == counts["projection_types"] == 24)
check("no_new_card_or_test", account["new_card"] is False and account["new_target_test"] is False)
rendered = (HERE / "AD_COMPLETE_ACCOUNT.md").read_text()
for row in expected:
    check("rendered_position:" + str(row["position"]),
          f'| {row["position"]} | {row["locus"]} | {row["group"]} | `{row["projection"]}` | `{row["raw"]}` |' in rendered)
result = {"status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
          "claim_ceiling": "Documentary source hashes, whole-unit copying and counts only. No semantic, morphological or hypothesis test.",
          "checks_passed": sum(c["pass"] for c in checks), "checks_total": len(checks),
          "checks": checks}
(HERE / "AD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["status", "checks_passed", "checks_total", "claim_ceiling"]}))
raise SystemExit(0 if result["status"] == "PASS" else 1)
