#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    family = rows("TWO_HUNDRED_SIXTY_EIGHTH_12_ASTRO_AIR_GROUPS.tsv")
    forms = rows("TWO_HUNDRED_SIXTY_EIGHTH_SEVEN_AIR_FORM_TYPES.tsv")
    astro = rows("TWO_HUNDRED_SIXTY_EIGHTH_REVISED_395_ASTRO_GROUPS.tsv")
    components = rows("TWO_HUNDRED_SIXTY_EIGHTH_REVISED_40_COMPONENTS.tsv")
    cards = rows("TWO_HUNDRED_SIXTY_EIGHTH_REVISED_173_CARD_DICTIONARY.tsv")
    events = rows("TWO_HUNDRED_SIXTY_EIGHTH_REVISED_381_PROSE_EVENTS.tsv")
    statements = rows("TWO_HUNDRED_SIXTY_EIGHTH_REVISED_116_STATEMENTS.tsv")
    status = Counter(r["composition_status"] for r in family)
    checks = {
        "12_groups_seven_forms": len(family) == 12 and len(forms) == 7,
        "11_full_one_partial": status == {"FULL_40_COMPONENT_PARSE": 11, "LOCAL_CORE_PLUS_AIR": 1},
        "pages_f67_f69": {r["page"] for r in family} == {"f67r2", "f69v"},
        "all_air_path": all(r["air_contribution_de"] == "LAUF_ODER_BAHN" for r in family),
        "full_inventory_counts": len(astro) == 395 and len(components) == 40 and len(cards) == 173 and len(events) == 381 and len(statements) == 116,
        "air_component_revised": next(r for r in components if r["component_id"] == "AIR")["short_value_de"] == "LAUF_ODER_BAHN",
        "five_prose_cards": {r["master_card_id"] for r in cards if r["revision_268"] == "AIR_PATH_CORE"} == {"MC014", "MC023", "MC081", "MC091", "MC116"},
        "five_prose_events": sum(r["revision_268"] == "AIR_PATH_CORE" for r in events) == 5,
        "previous_astro_revisions_preserved": sum(r["revision_266"] == "AIIN_COMPOSITION" for r in astro) == 13 and sum(r["revision_267"] == "AIN_AN_COMPOSITION" for r in astro) == 10,
        "12_air_revision_flags": sum(r["revision_268"] == "AIR_PATH_COMPOSITION" for r in astro) == 12,
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in astro + events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
