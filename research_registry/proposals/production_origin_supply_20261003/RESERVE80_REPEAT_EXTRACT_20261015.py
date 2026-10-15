"""Exact fixed f115r.17 projection and declared local source checks only."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LOCUS = "f115r.17"


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def extract():
    contract_path = HERE / "RESERVE80_REPEAT_CONTRACT_20261015.json"
    contract_blob = contract_path.read_bytes()
    contract = json.loads(contract_blob)
    assert contract["scope"]["locus"] == LOCUS
    rules_entry = next(x for x in contract["source_rule_primaries"] if x["path"].endswith("F45R_RECORD_SYNTHESIS_RULES_20261015.json"))
    rules_blob = (ROOT / rules_entry["path"]).read_bytes()
    assert sha(rules_blob) == rules_entry["sha256"]
    rules = json.loads(rules_blob)
    sources, readers = [], {}
    for edition in contract["scope"]["readers"]:
        records = []
        for phase in ("DISCOVERY", "EVALUATION"):
            path = Path("experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts") / f"SOURCE_{phase}_{edition}.json"
            blob = (ROOT / path).read_bytes()
            data = json.loads(blob)
            sources.append({"path": path.as_posix(), "sha256": sha(blob)})
            for line in data["lines"]:
                if line["metadata"]["locus"] != LOCUS:
                    continue
                assert line["metadata"]["page"] == "f115r"
                assert line["metadata"]["edition"] == edition
                records.append({"source": path.as_posix(), "group_columns": data["group_columns"], "line": line})
        assert len(records) <= 1
        checks = {}
        if records:
            record = records[0]
            line = record["line"]
            rows = [dict(zip(record["group_columns"], group)) for group in line["groups"]]
            by_index = {int(row["source_group_index"]): row for row in rows}
            head, first, second = (by_index.get(i) for i in (3, 4, 5))
            checks["own_kind_P"] = line["metadata"]["kind"] == "P"
            checks["complete_line_group_indices"] = sorted(by_index) == list(range(1, int(line["metadata"]["source_group_count"]) + 1))
            checks["selected_indices_present"] = all(row is not None for row in (head, first, second))
            if checks["selected_indices_present"]:
                checks["G003_whole_nonmarker_nonbound"] = head["ivtff_group_raw"] not in rules["free_markers"] and head["ivtff_group_raw"] not in rules["bound_forms"]
                checks["G004_G005_exact_daiin"] = first["ivtff_group_raw"] == second["ivtff_group_raw"] == "daiin"
                checks["G003_G004_definite"] = head["right_separator"] == first["left_separator"] == "DEFINITE_SPACE"
                checks["G004_G005_definite"] = first["right_separator"] == second["left_separator"] == "DEFINITE_SPACE"
        readers[edition] = {"status": "PRESENT" if records else "MISSING_NO_RESAMPLING", "records": records, "source_conditions": checks, "all_source_conditions_hold": bool(checks) and all(checks.values())}
    return {"schema": "reserve80-repeat-source-v1", "locus": LOCUS, "contract": {"path": contract_path.relative_to(ROOT).as_posix(), "sha256": sha(contract_blob)}, "extractor": {"path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__).read_bytes())}, "rule_source": rules_entry, "sources": sources, "readers": readers, "limits": ["Original line arrays, columns, raw groups, separators and metadata retained unchanged.", "Only the fixed locus selected; no resampling or other source payload output.", "Source-condition checks only: no noun meaning, resource identity, commitment event or semantic result established.", "Alternate readings are not independent confirmation; existing exposed data."]}


if __name__ == "__main__":
    packet = extract()
    output = HERE / "RESERVE80_REPEAT_SOURCE_20261015.json"
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    assert json.loads(output.read_bytes()) == packet
    print(json.dumps({"sha256": sha(output.read_bytes()), "source_checks": {edition: value["all_source_conditions_hold"] for edition, value in packet["readers"].items()}}, indent=2))
    for edition, value in packet["readers"].items():
        for record in value["records"]:
            print(edition, json.dumps(record["line"], ensure_ascii=False))
