#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    decode = read_tsv("PASS970_1078_SURFACE_DECODER.tsv")
    encode = read_tsv("PASS970_948_RECIPE_ENCODER.tsv")
    commands = read_tsv("PASS970_12_WORKSHOP_COMMAND_ROUNDTRIPS.tsv")
    decoder = {row["surface"]: row for row in decode}
    checks = {
        "surfaces_1078": len(decode) == 1078 and len(decoder) == 1078,
        "recipes_948": len(encode) == 948 and len({row["component_recipe"] for row in encode}) == 948,
        "commands_12": len(commands) == 12,
        "primary_roundtrip_948": all(decoder[row["default_surface"]]["component_recipe"] == row["component_recipe"] for row in encode),
        "all_variant_roundtrips": all(all(decoder[surface]["component_recipe"] == row["component_recipe"] for surface in row["allowed_observed_surfaces"].split("|")) for row in encode),
        "meaning_roundtrip": all(decoder[row["default_surface"]]["portable_core_de"] == row["portable_core_de"] for row in encode),
        "command_roundtrip": all(decoder[row["default_surface"]]["component_recipe"] == row["component_recipe"] and decoder[row["default_surface"]]["portable_core_de"] == row["readback_de"] for row in commands),
        "no_empty_values": all(row["portable_core_de"] for row in decode + encode + commands),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in decode + encode + commands),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS970_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
