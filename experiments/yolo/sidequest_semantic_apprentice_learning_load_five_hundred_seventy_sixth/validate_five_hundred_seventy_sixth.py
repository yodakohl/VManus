#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    layers = read("FIVE_HUNDRED_SEVENTY_SIXTH_LEARNING_LAYERS.tsv")
    cards = read("FIVE_HUNDRED_SEVENTY_SIXTH_ONE_HUNDRED_SEVENTY_THREE_CARD_LEARNING_MAP.tsv")
    events = read("FIVE_HUNDRED_SEVENTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_AUDIT.tsv")
    specialists = read("FIVE_HUNDRED_SEVENTY_SIXTH_SEVEN_SPECIALIST_LESSON.tsv")
    checks = {
        "layers9": len(layers) == 9,
        "semantic101": sum(int(r["items"]) for r in layers if r["domain"] == "SEMANTIC") == 101,
        "cards173": len(cards) == 173 and len({r["card_no"] for r in cards}) == 173,
        "composition166_4_3": sum(r["composition_status"] == "COMPOSITIONAL" for r in cards) == 166 and sum(r["composition_status"] == "PARTIAL_WITH_LEARNED_ATOM" for r in cards) == 4 and sum(r["composition_status"] == "LEARNED_WHOLE_CARD" for r in cards) == 3,
        "semantic_wholes7": sum(r["independent_semantic_whole_to_memorize"] == "YES" for r in cards) == 7,
        "specialists7": len(specialists) == 7 and len({r["card_no"] for r in specialists}) == 7,
        "events381": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "event_complete": all(r["complete"] == "YES" and r["semantic_value_de"] for r in events),
        "roundtrip": all(r["card_roundtrip"] == "YES" and r["surface_roundtrip"] == "YES" for r in events),
        "fixed_pages": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SEVENTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
