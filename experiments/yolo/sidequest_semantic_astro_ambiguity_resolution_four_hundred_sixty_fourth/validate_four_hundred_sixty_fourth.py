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
    decisions = read("FOUR_HUNDRED_SIXTY_FOURTH_41_ASTRO_AMBIGUITY_DECISIONS.tsv")
    groups = read("FOUR_HUNDRED_SIXTY_FOURTH_395_ASTRO_GROUP_RESOLVED.tsv")
    loci = read("FOUR_HUNDRED_SIXTY_FOURTH_142_ASTRO_LOCUS_RESOLVED.tsv")
    ledger = read("FOUR_HUNDRED_SIXTY_FOURTH_776_GROUP_RESOLVED_LEDGER.tsv")
    summary = read("FOUR_HUNDRED_SIXTY_FOURTH_THREE_ASTRO_SUMMARY.tsv")
    checks = {
        "decisions_41": len(decisions) == 41,
        "groups_395": len(groups) == 395,
        "loci_142": len(loci) == 142,
        "ledger_776": len(ledger) == 776,
        "summaries_3": len(summary) == 3,
        "all_ambiguities_resolved": all(row["transfer_status"] != "AMBIGUOUS_COMPONENT_SEQUENCE" for row in groups),
        "resolved_41": sum(row["transfer_status"] == "POSITION_RESOLVED_COMPONENT_SEQUENCE" for row in groups) == 41,
        "status_partition_395": sum(int(row[key]) for row in summary for key in ("exact_full_card", "unique_components", "position_resolved_components", "local_labels")) == 395,
        "decision_parses_were_candidates": all(row["selected_parse"] in row["parse_alternatives"].split(" || ") for row in decisions),
        "decision_values_complete": all(row["selected_atomic_value_de"] for row in decisions),
        "group_order": [row["group_serial"] for row in groups] == [str(n) for n in range(1, 396)],
        "locus_groups_once": sorted((serial for row in loci for serial in row["group_serials"].split("|")), key=int) == [str(n) for n in range(1, 396)],
        "ledger_partition": [sum(row["domain"] == domain for row in ledger) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "ledger_defaults_complete": all(row["atomic_default_de"] for row in ledger),
        "astro_pages_exact": {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"},
        "no_cross_join": all(row["cross_instrument_join"] == "NONE" for row in groups + loci),
        "orientation_unspecified": all(row["orientation"] == "UNSPECIFIED" for row in loci),
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
