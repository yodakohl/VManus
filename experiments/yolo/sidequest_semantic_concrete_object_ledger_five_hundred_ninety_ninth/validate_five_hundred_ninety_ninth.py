#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    components = read("FIVE_HUNDRED_NINETY_NINTH_38_COMPONENT_OBJECT_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_NINETY_NINTH_381_EVENT_OBJECT_BINDING.tsv")
    statements = read("FIVE_HUNDRED_NINETY_NINTH_116_STATEMENT_OBJECT_LEDGER.tsv")
    owners = read("FIVE_HUNDRED_NINETY_NINTH_21_OWNER_OBJECT_CHAINS.tsv")
    checks = {
        "components38": len(components) == 38 and len({row["component"] for row in components}) == 38,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "owners21": len(owners) == 21 and len({row["owner_id"] for row in owners}) == 21,
        "owner_statement_reconciliation": sum(int(row["statements"]) for row in owners) == 116,
        "all_event_objects": all(row["primary_object_class"] and row["primary_object_de"] and row["local_output_de"] for row in events),
        "all_statement_objects": all(row["concrete_objects_de"] and row["object_before_id"] and row["object_after_id"] for row in statements),
        "no_cross_owner": all(row["object_crosses_visible_owner_reset"] == "NO" for row in statements),
        "fixed_pages": set(row["page"] for row in events) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
