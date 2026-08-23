#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audit = rows("HUNDRED_TWENTIETH_102_OVERRIDE_AUDIT.tsv")
    hands = rows("HUNDRED_TWENTIETH_FOUR_SECONDARY_HAND_HABITS.tsv")
    trace = rows("HUNDRED_TWENTIETH_381_REVISED_RENDERER_TRACE.tsv")
    models = rows("HUNDRED_TWENTIETH_RENDERER_ECONOMY.tsv")
    checks = {
        "audit_102": len(audit) == 102,
        "hands_4": len(hands) == 4,
        "trace_381": len(trace) == 381,
        "models_5": len(models) == 5,
        "absorbed_27": sum(r["resolved_by_secondary_repertoire"] == "YES" for r in audit) == 27,
        "primary_279": sum(r["revised_renderer_status"] == "PRIMARY_HABIT_MATCH" for r in trace) == 279,
        "secondary_27": sum(r["revised_renderer_status"] == "SECONDARY_REPERTOIRE_MATCH" for r in trace) == 27,
        "remaining_75": sum(r["revised_renderer_status"] == "COPY_MASTER_EXEMPLAR_OVERRIDE" for r in trace) == 75,
        "event_unique": len({r["event_serial"] for r in trace}) == 381,
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in trace),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
