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
    rel = read("TWO_HUNDRED_SEVENTY_FIRST_25_LOCAL_RELATIONS.tsv")
    forms = read("TWO_HUNDRED_SEVENTY_FIRST_20_RELATION_FORMS.tsv")
    totals = read("TWO_HUNDRED_SEVENTY_FIRST_CROSS_REGISTER_TOTALS.tsv")
    revised = read("TWO_HUNDRED_SEVENTY_FIRST_REVISED_395_ASTRO_GROUPS.tsv")
    counts = Counter(r["relation_suffix"] for r in rel)
    checks = {
        "25_relations": len(rel) == 25,
        "20_forms": len(forms) == 20,
        "17_or_8_ol": counts == {"OR": 17, "OL": 8},
        "all_three_pages": {r["page"] for r in rel} == {"f67r2", "f68r1", "f69v"},
        "suffix_matches_surface": all(r["visible_surface"].endswith(r["relation_suffix"].lower()) for r in rel),
        "two_total_rows": len(totals) == 2,
        "cross_totals": {r["relation_component"]: int(r["cross_register_total"]) for r in totals} == {"OR": 37, "OL": 65},
        "395_revised": len(revised) == 395,
        "25_revision_flags": sum(r["revision_271"] == "OR_OL_RELATION_SUFFIX" for r in revised) == 25,
        "otolor_triple": any(r["visible_surface"] == "otolor" and r["component_parse"] == "OT+OL+OR" for r in rel),
        "prior_address_flags_preserved": sum(r["revision_270"] == "AL_AR_ADDRESS_SUFFIX" for r in revised) == 54,
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in revised),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
