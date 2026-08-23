#!/usr/bin/env python3
"""Consistency checker for the speakable Astro edition."""

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
    loci = read("THIRTY_SIXTH_142_SPOKEN_LOCI.tsv")
    modules = read("THIRTY_SIXTH_13_INSTRUMENT_MODULES.tsv")
    counts = Counter(row["page"] for row in loci)
    groups = Counter()
    for row in loci:
        groups[row["page"]] += int(row["group_count"])
    checks = {
        "loci_142": len(loci) == 142,
        "groups_395": sum(int(r["group_count"]) for r in loci) == 395,
        "pages_exact": counts == Counter({"f67r2": 74, "f68r1": 37, "f69v": 31}),
        "groups_exact": groups == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
        "namespaces_13": len(modules) == 13,
        "loci_unique": len({r["locus"] for r in loci}) == 142,
        "all_spoken": all(r["spoken_instruction_de"] and r["portable_card_reading_de"] for r in loci),
        "no_orientation": all(r["orientation_rule"] == "DIREKTE_SICHTADRESSE__KEINE_ERFUNDENE_REIHENFOLGE" for r in loci),
        "no_f68_f69_key": all(r["crosspage_rule"].startswith("KEIN_F68_F69_SCHLUESSEL") for r in loci),
        "three_instruments": (OUT / "THIRTY_SIXTH_THREE_SPOKEN_INSTRUMENTS.md").exists(),
        "manual": (OUT / "THIRTY_SIXTH_ASTRO_APPRENTICE_MANUAL.md").exists(),
        "report": (OUT / "THIRTY_SIXTH_EDITION_REPORT.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
