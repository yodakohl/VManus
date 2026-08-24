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
    melodies = read("FIVE_HUNDRED_SIXTY_FIRST_NINE_RECORD_MELODIES.tsv")
    slots = read("FIVE_HUNDRED_SIXTY_FIRST_TWENTY_TWO_MELODY_SLOTS.tsv")
    executions = read("FIVE_HUNDRED_SIXTY_FIRST_TWENTY_SEVEN_MELODY_EXECUTIONS.tsv")
    renderer = read("FIVE_HUNDRED_SIXTY_FIRST_THREE_HUNDRED_EIGHTY_ONE_FINAL_RENDERER.tsv")
    counts = Counter(row["renderer_source"] for row in renderer)
    checks = {
        "nine_melodies": len(melodies) == 9 and len({row["melody_id"] for row in melodies}) == 9,
        "twenty_two_slots": len(slots) == 22 and len({(row["melody_id"], row["slot"]) for row in slots}) == 22,
        "twenty_seven_executions": len(executions) == 27 and len({row["event_id"] for row in executions}) == 27,
        "slot_event_sum": sum(int(row["events_at_slot"]) for row in slots) == 27,
        "all_melody_refs": {row["melody_id"] for row in slots + executions} <= {row["melody_id"] for row in melodies},
        "renderer381": len(renderer) == 381 and len({row["event_id"] for row in renderer}) == 381,
        "source_counts": counts == Counter({"GLOBAL_RULE_RENDERER": 314, "FORMULA_CADENCE_RULE": 32, "RECORD_WRAPPER_MELODY": 27, "AUTOMATIC_CONTEXT_RULE": 8}),
        "roundtrip381": all(row["surface_roundtrip"] == "YES" for row in renderer),
        "no_locus_table": all(row["local_locus_table"] == "NO" for row in renderer + executions),
        "no_free_choice": all(row["free_choice"] == "NO" for row in renderer + executions + melodies),
        "fixed_pages": {row["page"] for row in renderer} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in renderer),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
