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
    decisions = read("FOUR_HUNDRED_SIXTY_SEVENTH_11_FINAL_NAME_DECISIONS.tsv")
    cores = read("FOUR_HUNDRED_SIXTY_SEVENTH_TWO_FINAL_ASTRO_CORES.tsv")
    groups = read("FOUR_HUNDRED_SIXTY_SEVENTH_395_ASTRO_GROUP_CLOSED_NOMENCLATOR.tsv")
    loci = read("FOUR_HUNDRED_SIXTY_SEVENTH_142_ASTRO_LOCUS_CLOSED_NOMENCLATOR.tsv")
    ledger = read("FOUR_HUNDRED_SIXTY_SEVENTH_776_GROUP_COMPLETE_APPRENTICE_LEDGER.tsv")
    dictionary = read("FOUR_HUNDRED_SIXTY_SEVENTH_52_UNIT_APPRENTICE_DICTIONARY.tsv")
    aliases = read("FOUR_HUNDRED_SIXTY_SEVENTH_ELEVEN_EXACT_CARD_ALIAS_RULES.tsv")
    whole = read("FOUR_HUNDRED_SIXTY_SEVENTH_ONE_ASTRO_WHOLE_NAME.tsv")
    checks = {
        "decisions_11": len(decisions) == 11,
        "cores_2": len(cores) == 2,
        "groups_395": len(groups) == 395,
        "loci_142": len(loci) == 142,
        "ledger_776": len(ledger) == 776,
        "dictionary_52": len(dictionary) == 52,
        "aliases_11": len(aliases) == 11,
        "whole_name_1": len(whole) == 1 and whole[0]["surface"] == "otaza",
        "astro_compositions_394": sum(row["nomenclator_resolution"] != "MEMORIZED_WHOLE_NAME" for row in groups) == 394,
        "astro_whole_1": sum(row["nomenclator_resolution"] == "MEMORIZED_WHOLE_NAME" for row in groups) == 1,
        "sd_unified": all("S_LABEL" not in row["selected_component_parse"] and "D_LABEL" not in row["selected_component_parse"] for row in groups),
        "all_group_defaults": all(row["atomic_common_root_value_de"] for row in groups),
        "all_ledger_defaults": all(row["atomic_default_de"] for row in ledger),
        "group_order": [row["group_serial"] for row in groups] == [str(n) for n in range(1, 396)],
        "locus_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "ledger_partition": [sum(row["domain"] == domain for row in ledger) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "dictionary_partition": [sum(row["unit_kind"] == kind for row in dictionary) for kind in ("PRODUCTIVE_COMPONENT", "PRODUCTIVE_ADDRESS_COMPONENT", "MEMORIZED_WHOLE_CARD", "MEMORIZED_WHOLE_NAME")] == [35, 10, 6, 1],
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in groups + loci),
        "astro_pages": {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
