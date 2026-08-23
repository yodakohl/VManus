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
    audited = read("TWO_HUNDRED_SEVENTY_THIRD_107_FINAL_Y_AUDIT.tsv")
    forms = read("TWO_HUNDRED_SEVENTY_THIRD_98_FINAL_Y_FORMS.tsv")
    classes = read("TWO_HUNDRED_SEVENTY_THIRD_SIX_BOUNDARY_CLASSES.tsv")
    channel = read("TWO_HUNDRED_SEVENTY_THIRD_CROSS_REGISTER_Y_CHANNEL.tsv")
    revised = read("TWO_HUNDRED_SEVENTY_THIRD_REVISED_395_ASTRO_GROUPS.tsv")
    counts = Counter(r["final_y_class"] for r in audited)
    expected = {"DY_FIXED": 40, "E_GRADE_Y": 23, "OPERATION_Y": 12, "RELATION_Y": 15, "EXPLICIT_CURRENT_Y": 6, "LOCAL_WHOLE_Y": 11}
    channel_counts = {r["scope"]: int(r["use_count"]) for r in channel}
    checks = {
        "107_audited": len(audited) == 107,
        "98_forms": len(forms) == 98,
        "six_classes": len(classes) == 6,
        "class_counts": counts == expected,
        "all_end_y": all(r["visible_surface"].endswith("y") for r in audited),
        "dy_never_y": all(r["portable_y_licensed"] == "NO" for r in audited if r["final_y_class"] == "DY_FIXED"),
        "secure_local_33": sum(r["portable_y_licensed"] == "YES" for r in audited) == 33,
        "graded_23": sum(r["portable_y_licensed"] == "CANDIDATE" for r in audited) == 23,
        "not_y_51": sum(r["portable_y_licensed"] == "NO" for r in audited) == 51,
        "channel_177_200": channel_counts["PORTABLE_Y_SECURE_TOTAL"] == 177 and channel_counts["PORTABLE_Y_WITH_GRADED_CANDIDATES"] == 200,
        "395_revised": len(revised) == 395,
        "107_revision_flags": sum(r["revision_273"] != "UNCHANGED" for r in revised) == 107,
        "prior_ot_flags_preserved": sum(r["revision_272"] == "OT_FOLLOWING_POST" for r in revised) == 26,
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in revised),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
