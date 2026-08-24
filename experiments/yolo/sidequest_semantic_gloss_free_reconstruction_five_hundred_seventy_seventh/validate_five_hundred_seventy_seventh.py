#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    components = read("FIVE_HUNDRED_SEVENTY_SEVENTH_CORRECTED_THIRTY_EIGHT_COMPONENT_INVENTORY.tsv")
    cards = read("FIVE_HUNDRED_SEVENTY_SEVENTH_ONE_HUNDRED_SEVENTY_THREE_GLOSS_FREE_CARD_RECONSTRUCTIONS.tsv")
    events = read("FIVE_HUNDRED_SEVENTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_GLOSS_FREE_EVENT_RECONSTRUCTIONS.tsv")
    summary = json.loads((HERE / "FIVE_HUNDRED_SEVENTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "components38": len(components) == 38 and len({r["component"] for r in components}) == 38,
        "specialists_inside38": sum(r["learning_class"] == "SINGLE_CARD_SPECIALIST_COMPONENT" for r in components) == 7,
        "semantic_items94": summary["semantic_learning_items_corrected"] == 94,
        "cards173": len(cards) == 173 and len({r["card_no"] for r in cards}) == 173,
        "cards_complete": all(r["structural_reconstruction"] == "COMPLETE" for r in cards),
        "old_gloss_not_input": all(r["old_atomic_gloss_used_as_input"] == "NO" for r in cards),
        "wording162_11": sum(r["natural_wording_status"] == "PORTABLE_WORDING_AVAILABLE" for r in cards) == 162 and sum(r["natural_wording_status"] == "OWNER_OR_SLOT_CONTEXT_REQUIRED" for r in cards) == 11,
        "events381": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "events_complete": all(r["complete"] == "COMPLETE" and r["gloss_free_mechanical_reading_de"] for r in events),
        "fixed_pages": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SEVENTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
