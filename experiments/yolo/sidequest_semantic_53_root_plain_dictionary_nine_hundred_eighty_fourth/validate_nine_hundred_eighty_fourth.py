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
    roots = read("PASS984_53_PORTABLE_ROOT_DICTIONARY.tsv")
    signs = read("PASS984_THREE_LOCAL_DIAGRAM_SIGNS.tsv")
    by_id = {r["root_id"]: r for r in roots}
    checks = {
        "portable_roots_53": len(roots) == 53,
        "root_ids_unique": len(by_id) == 53,
        "local_signs_3": len(signs) == 3,
        "local_sign_ids_unique": len({r["sign_id"] for r in signs}) == 3,
        "all_roots_have_content": all(int(r["content_events"]) > 0 for r in roots),
        "all_atomic_meanings_short": all(1 <= len(r["atomic_meaning_de"].split()) <= 2 for r in roots),
        "y_is_posten": by_id["R-Y"]["atomic_meaning_de"] == "POSTEN",
        "or_is_arbeitssatz": by_id["R-OR"]["atomic_meaning_de"] == "ARBEITSSATZ",
        "air_is_lauf": by_id["R-AIR"]["atomic_meaning_de"] == "LAUF",
        "cheo_is_auszug": by_id["R-CHEO"]["atomic_meaning_de"] == "AUSZUG",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS984_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
