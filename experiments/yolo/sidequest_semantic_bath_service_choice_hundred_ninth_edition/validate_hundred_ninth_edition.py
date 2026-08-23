#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    choices = rows("HUNDRED_NINTH_56_BATH_VS_SERVICE_CHOICES.tsv")
    stations = rows("HUNDRED_NINTH_STATION_ROLE_TABLE.tsv")
    records = rows("HUNDRED_NINTH_TWO_SELECTED_HYBRID_RECORDS.tsv")
    checks = {
        "choices_56": len(choices) == 56,
        "stations_11": len(stations) == 11,
        "records_2": len(records) == 2,
        "one_choice_each": all(r["selected_local_role"] in {"ZUBEREITUNG_SERVICE", "KOERPER_BAD_ANWENDUNG"} for r in choices),
        "both_readings_each": all(r["medical_bath_expansion_de"] and r["service_maintenance_expansion_de"] for r in choices),
        "service_35": sum(r["selected_local_role"] == "ZUBEREITUNG_SERVICE" for r in choices) == 35,
        "body_21": sum(r["selected_local_role"] == "KOERPER_BAD_ANWENDUNG" for r in choices) == 21,
        "transition_service": all(r["selected_local_role"] == "ZUBEREITUNG_SERVICE" for r in choices if "B3_LOCAL_TRANSITION_BATCH" in r["owner_sequence"] and r["statement_id"] != "B3-S026"),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in choices),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
