#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    components = read("FIVE_HUNDRED_FORTY_FIRST_COMPONENT_TEACHING_DECK.tsv")
    manual = read("FIVE_HUNDRED_FORTY_FIRST_EIGHTEEN_RULE_APPRENTICE_MANUAL.tsv")
    samples = read("FIVE_HUNDRED_FORTY_FIRST_TWELVE_NEW_WORKSHOP_INSTRUCTIONS.tsv")
    traces = read("FIVE_HUNDRED_FORTY_FIRST_SAMPLE_CARD_TRACES.tsv")
    whole = read("FIVE_HUNDRED_FORTY_FIRST_THREE_WHOLE_CARD_MINIDECK.tsv")
    checks = {
        "manual18": len(manual) == 18 and [row["rule_no"] for row in manual] == [f"M{i:02d}" for i in range(1, 19)],
        "components_nonempty": len(components) >= 30 and all(row["workshop_value_de"] for row in components),
        "three_whole_cards": [row["card_no"] for row in whole] == ["PROC005", "PROC043", "PROC115"],
        "samples12": len(samples) == 12 and [row["sample_id"] for row in samples] == [f"X{i:02d}" for i in range(1, 13)],
        "samples6_6": Counter(row["uses_predicted_card"] for row in samples) == Counter({"NO": 6, "YES": 6}),
        "trace_partition": Counter(row["sample_id"] for row in traces) == Counter({row["sample_id"]: len(row["component_program"].split("|")) for row in samples}),
        "all_roundtrip": all(row["roundtrip"] == "PASS" for row in traces) and all(row["forward_roundtrip"] == "PASS" and row["backward_roundtrip"] == "PASS" for row in samples),
        "all_surface_sequences": all(row["written_surface_sequence"] for row in samples),
        "no_unknown_values": all(row["card_value_de"] for row in traces),
        "no_sealed_tokens": all("f84" not in "\t".join(row.values()).lower() for row in [*components, *manual, *samples, *traces, *whole]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
