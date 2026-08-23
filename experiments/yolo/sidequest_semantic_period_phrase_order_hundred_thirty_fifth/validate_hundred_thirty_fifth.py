#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    sources = rows("HUNDRED_THIRTY_FIFTH_PERIOD_SOURCE_COMPARATORS.tsv")
    cards = rows("HUNDRED_THIRTY_FIFTH_41_ACTIVE_CARD_REVISIONS.tsv")
    jobs = rows("HUNDRED_THIRTY_FIFTH_FOUR_JOB_PERIOD_ORDER.tsv")
    checks = {
        "sources_9": len(sources) == 9,
        "active_cards_41": len(cards) == 41,
        "jobs_4": len(jobs) == 4,
        "card_ids_unique": len({r["master_card_id"] for r in cards}) == 41,
        "all_period_values_short": all(0 < len(r["period_sized_default_de"].split()) <= 4 for r in cards),
        "all_sources_linked": all(r["source_url"].startswith("https://") for r in sources),
        "all_cells_nonempty": all(all(v for v in r.values()) for table in (sources, cards, jobs) for r in table),
        "core_repairs_present": {"fertig", "Anteil", "Klarauszug", "bemessen", "bereit"}.issubset({r["period_sized_default_de"] for r in cards}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
