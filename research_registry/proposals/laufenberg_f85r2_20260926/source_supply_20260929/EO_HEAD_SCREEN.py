"""Reproduce an exposed preimplementation necessary-condition audit; no decoder."""
from pathlib import Path
import json, hashlib, collections
import csv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def main():
    rules = json.loads((HERE / "EO_HEAD_SCREEN_RULES.json").read_text())
    for name in ("source", "parent_model", "author"):
        p = ROOT / rules[name]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == rules[name + "_sha256"]
    source = json.loads((ROOT / rules["source"]).read_text())
    model = json.loads((ROOT / rules["parent_model"]).read_text())
    fixed = model["models"]["G"]["dictionary"]
    nominal = set(rules["nominal_wholes_under_candidate"])
    units, cases = [], []
    for unit in source["units"]:
        # Selector checked before inspecting contents; no new manuscript admission.
        page = unit["page"]
        if page not in rules["declared_native_regions"]:
            continue
        if unit["id"] not in rules["declared_native_regions"][page]:
            continue
        assert not page.startswith("f84") and page != "f116v"
        units.append(unit)
        flat = [(sid, word) for line in unit["lines"] for sid, word in zip(line["source_ids"], line["words"])]
        def side(j):
            if j < 0 or j >= len(flat):
                return {"id": None, "raw": None, "role": "NO_WRITTEN_GROUP"}
            sid, word = flat[j]
            role = "NOMINAL" if word in nominal else "INELIGIBLE_FIXED" if word in fixed else "UNKNOWN"
            return {"id": sid, "raw": word, "role": role}
        for i, (sid, word) in enumerate(flat):
            if word not in rules["target_exact_whole_values"]:
                continue
            left, right = side(i - 1), side(i + 1)
            chosen = left if left["role"] == "NOMINAL" else right if right["role"] == "NOMINAL" else None
            if chosen:
                status = "TYPE_CAPACITY_ONLY_NOT_MEANING_PASS"
            elif left["role"] != "UNKNOWN" and right["role"] != "UNKNOWN":
                status = "KNOWN_SIDE_CONTRADICTION"
            else:
                status = "UNBOUND_HEAD_ROLE"
            cases.append({"edition": unit["edition"], "paragraph_id": unit["id"], "source_id": sid, "raw": word, "left": left, "right": right, "chosen_head": chosen, "status": status})
    result = {"phase": rules["phase"], "source_units": units, "cases": cases,
              "native_units": len(units), "raw_groups": sum(u["groups"] for u in units),
              "counts": dict(collections.Counter(c["status"] for c in cases)),
              "decision": "DECLINE_FINITE_GENITIVE_HEAD_GRAMMAR" if any(c["status"] == "KNOWN_SIDE_CONTRADICTION" for c in cases) else "UNSELECTED",
              "countercase_known_before_screen": True, "semantic_validation": False,
              "confirmed_words": 0, "independent_meaning_capacity": 0}
    (HERE / "EO_HEAD_SCREEN_RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    with (HERE / "EO_HEAD_CASES.tsv").open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["edition", "paragraph_id", "source_id", "raw", "left", "left_role", "right", "right_role", "status"])
        for c in cases:
            writer.writerow([c["edition"], c["paragraph_id"], c["source_id"], c["raw"], c["left"]["raw"], c["left"]["role"], c["right"]["raw"], c["right"]["role"], c["status"]])
    print({k: result[k] for k in ("native_units", "raw_groups", "counts", "decision")})

if __name__ == "__main__":
    main()
