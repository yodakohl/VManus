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
    cards = read("THREE_HUNDRED_SEVENTY_SEVENTH_14_CARD_CROSSWALK.tsv")
    visible = read("THREE_HUNDRED_SEVENTY_SEVENTH_15_SECOND_COPY_FORMS.tsv")
    regions = read("THREE_HUNDRED_SEVENTY_SEVENTH_REGION_RESCALE.tsv")
    cross = read("THREE_HUNDRED_SEVENTY_SEVENTH_FOUR_PAGE_CROSSREADS.tsv")
    checks = {
        "14_cards": len(cards) == 14,
        "all_second_surfaces_registered": all(r["second_surface_registered"] == "YES" for r in cards),
        "eight_changed_six_same": sum(r["surface_changed"] == "YES" for r in cards) == 8 and sum(r["surface_changed"] == "NO" for r in cards) == 6,
        "all_layers_preserved": all(r["identity_preserved"] == r["value_preserved"] == r["owner_preserved"] == "YES" for r in cards),
        "15_visible_14_source": len(visible) == 15 and sum(int(r["source_contribution"]) for r in visible) == 14,
        "one_carry": sum(r["visibility_role"] == "MARKED_ANTICIPATION" for r in visible) == 1,
        "two_images_rescaled": sum(r["region_type"] == "IMAGE" and r["change"] != "SAME" for r in regions) == 2,
        "four_crossreads": len(cross) == 4 and all(r["full_crossread"] == "YES" for r in cross),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_SEVENTH_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
