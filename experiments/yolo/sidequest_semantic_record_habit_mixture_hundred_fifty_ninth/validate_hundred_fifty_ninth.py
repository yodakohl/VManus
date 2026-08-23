#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_FIFTY_NINTH_251_OBSERVED_PROFILE_FIT.tsv")
    records = rows("HUNDRED_FIFTY_NINTH_11_RECORD_HABIT_MIXTURES.tsv")
    exceptions = rows("HUNDRED_FIFTY_NINTH_10_MICRO_ALLOGRAPHS.tsv")
    checks = {
        "events_251": len(events) == 251,
        "event_serials_unique": len({row["event_serial"] for row in events}) == 251,
        "records_11": len(records) == 11,
        "profile_reproduced_228": sum(row["fit_status"] == "PROFILE_REPRODUCED" for row in events) == 228,
        "micro_allograph_events_23": sum(row["fit_status"] == "REGISTERED_MICRO_ALLOGRAPH_WITHIN_HABIT" for row in events) == 23,
        "micro_allograph_forms_10": len(exceptions) == 10,
        "micro_allograph_cards_8": len({row["master_card_id"] for row in exceptions}) == 8,
        "all_surfaces_registered": all(row["registered_surface"] == "YES" for row in events),
        "all_master_cards_recover": all(row["master_recovery"] == "EXACT" for row in events),
        "no_single_profile_record": all(row["one_stable_extreme_profile"] == "NO" and int(row["best_single_profile_misses"]) > 0 for row in records),
        "records_mix_3_to_5_habits": all(3 <= int(row["observed_habit_count"]) <= 5 for row in records),
        "profile_cover_plus_variants_251": sum(int(row["profile_reproduced_events"]) + int(row["registered_micro_allograph_events"]) for row in records) == 251,
        "no_semantic_change": all(row["new_meaning"] == "NONE" for row in exceptions),
        "no_empty_cells": all(all(value for value in row.values()) for table in (events, records, exceptions) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
