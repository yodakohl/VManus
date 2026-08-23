#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    atoms = rows("HUNDRED_TENTH_44_ATOM_POCKET.tsv")
    cards = rows("HUNDRED_TENTH_173_CARD_POCKET.tsv")
    surfaces = rows("HUNDRED_TENTH_230_SURFACE_INDEX.tsv")
    statements = rows("HUNDRED_TENTH_116_CURRENT_STATEMENTS.tsv")
    checks = {
        "atoms_44": len(atoms) == 44,
        "cards_173": len(cards) == 173,
        "surfaces_230": len(surfaces) == 230,
        "statements_116": len(statements) == 116,
        "unique_atoms": len({r["atom"] for r in atoms}) == 44,
        "unique_cards": len({r["master_card_id"] for r in cards}) == 173,
        "unique_surfaces": len({r["visible_surface"] for r in surfaces}) == 230,
        "unique_statements": len({r["statement_id"] for r in statements}) == 116,
        "surfaces_resolve": {r["master_card_id"] for r in surfaces} == {r["master_card_id"] for r in cards},
        "all_current_readings": all(r["current_reading_de"] for r in statements),
        "bio_hybrid_56": sum(r["selected_content_layer"] in {"ZUBEREITUNG_SERVICE", "KOERPER_BAD_ANWENDUNG"} for r in statements) == 56,
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
