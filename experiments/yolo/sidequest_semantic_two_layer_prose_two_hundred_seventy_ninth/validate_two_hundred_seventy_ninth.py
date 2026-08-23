#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv")
    events = read("TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv")
    statements = read("TWO_HUNDRED_SEVENTY_NINTH_116_TWO_LAYER_STATEMENTS.tsv")
    checks = {
        "173_cards": len(cards) == 173 and len({r["master_card_id"] for r in cards}) == 173,
        "381_events": len(events) == 381 and [r["event_id"] for r in events] == [f"E{i:03d}" for i in range(1, 382)],
        "116_statements": len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116,
        "11_records": len({r["record_unit_id"] for r in statements}) == 11,
        "event_statement_sum": sum(int(r["event_count"]) for r in statements) == 381,
        "card_classes": Counter(r["card_class_279"] for r in cards) == {"COMPOSED_FROM_36_FAMILIES": 149, "MEMORIZED_WHOLE_SIGN": 23, "FRAME_PLUS_LEARNED_WHOLE": 1},
        "event_classes": Counter(next(c["card_class_279"] for c in cards if c["master_card_id"] == e["master_card_id"]) for e in events) == {"COMPOSED_FROM_36_FAMILIES": 352, "MEMORIZED_WHOLE_SIGN": 28, "FRAME_PLUS_LEARNED_WHOLE": 1},
        "all_two_layers_nonempty": all(r["family_literal_de"].strip() and r["register_expansion_de"].strip() for r in events),
        "chk_portable_corrected": all("ZUSTAND_JUSTIEREN" in r["family_literal_de"] for r in cards if "CHK" in r["family_parse"].split("+")),
        "dy_portable_corrected": all("FESTSETZEN" in r["family_literal_de"] for r in cards if "DY" in r["family_parse"].split("+")),
        "cho_portable_corrected": all("EINGABE" in r["family_literal_de"] for r in cards if "CHO_INPUT" in r["family_parse"].split("+")),
        "only_allowed_pages": {r["page"] for r in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in events),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
