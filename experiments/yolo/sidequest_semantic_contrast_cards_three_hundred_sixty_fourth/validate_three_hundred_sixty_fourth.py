#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("THREE_HUNDRED_SIXTY_FOURTH_65_CONTRAST_CARDS.tsv")
    panels = read("THREE_HUNDRED_SIXTY_FOURTH_22_CONTRAST_PANELS.tsv")
    events = read("THREE_HUNDRED_SIXTY_FOURTH_380_FINAL_SETTING_ROUTES.tsv")
    checks = {
        "65_cards": len(cards) == 65 and len({r["target_controlled_phrase"] for r in cards}) == 65,
        "22_panels": len(panels) == 22 and all(r["all_unique_after_contrast"] == "YES" for r in panels),
        "all_cards_in_panels": sum(int(r["card_count"]) for r in panels) == 65,
        "allowed_kinds": {r["contrast_kind"] for r in cards} == {"REPEATED_SEMANTIC_CUE", "GRAMMATICAL_ASPECT", "OWNER_VISIBLE", "NOMENCLATOR_MNEMONIC"},
        "mnemonics_not_composed": all((r["contrast_kind"] == "NOMENCLATOR_MNEMONIC") == (r["teaching_rule"] == "MEMORIZE_WHOLE_CARD") for r in cards),
        "380_events": len(events) == 380 and len({r["source_position_id"] for r in events}) == 380,
        "all_events_exact": all(r["exact_selection"] == "YES" for r in events),
        "three_routes": {r["final_setting_route"] for r in events} == {"DIRECT_COMPOSITION", "CONTRAST_COMPOSITION", "WHOLE_CARD_MNEMONIC"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
