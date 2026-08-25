#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_NINTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_ninth.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    families = read(f"{PREFIX}_29_VARIABLE_RENDERER_FAMILIES.tsv")
    events = read(f"{PREFIX}_168_VARIABLE_PHYSICAL_OCCURRENCES.tsv")
    rules = read(f"{PREFIX}_67_IDENTITY_POSITION_RULES.tsv")
    exceptions = read(f"{PREFIX}_45_POSITION_EXCEPTIONS.tsv")
    wrappers = read(f"{PREFIX}_9_WRAPPER_PROFILES.tsv")
    models = read(f"{PREFIX}_3_RENDERER_MODELS.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "physical_core_230": summary["portable_core_physical_events"] == 230,
        "families_29": len(families) == 29,
        "events_168_unique": len(events) == 168 and len({row["source_id"] for row in events}) == 168,
        "wrappers_9": len(wrappers) == 9 and {row["wrapper"] for row in wrappers} == {"BARE", "c", "ch", "che", "d", "q", "s", "sh", "t"},
        "rules_67": len(rules) == 67,
        "position_matches_123": sum(row["identity_position_match"] == "YES" for row in events) == 123,
        "exceptions_45": len(exceptions) == 45 and all(row["identity_position_match"] == "NO" for row in exceptions),
        "page_position_146": sum(row["page_position_match"] == "YES" for row in events) == 146,
        "models_3": len(models) == 3,
        "q_entry_bias": summary["q_entry_or_only"] == 25 and summary["q_total"] == 40,
        "sh_exit_bias": summary["sh_exit_or_only"] == 12 and summary["sh_total"] == 15,
        "bare_middle_bias": summary["bare_middle"] == 23 and summary["bare_total"] == 36,
        "meaning_safe": all(row["meaning_change_if_house_surface_used"] == "NO" for row in events),
        "dictionary_unchanged": summary["dictionary_changes"] == 0,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
