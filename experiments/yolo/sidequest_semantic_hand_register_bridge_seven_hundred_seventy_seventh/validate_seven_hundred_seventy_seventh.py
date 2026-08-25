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
    signatures = read("SEVEN_HUNDRED_SEVENTY_SEVENTH_7_PAGE_SIGNATURES.tsv")
    pairs = read("SEVEN_HUNDRED_SEVENTY_SEVENTH_21_PAGE_PAIRS.tsv")
    nearest = read("SEVEN_HUNDRED_SEVENTY_SEVENTH_7_NEAREST_PAGE_READINGS.tsv")
    bridge = read("SEVEN_HUNDRED_SEVENTY_SEVENTH_F55V_BRIDGE.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    near = {row["page"]: row for row in nearest}
    bridge_map = {(row["layer"], row["comparison_pool"]): float(row["mean_similarity"]) for row in bridge}
    checks = {
        "counts_7_21_7_4": (len(signatures), len(pairs), len(nearest), len(bridge)) == (7, 21, 7, 4),
        "events381": sum(int(row["events"]) for row in signatures) == 381,
        "f55_exact_nearest_f81": near["f55v"]["nearest_exact_card_page"] == "f81v",
        "f55_component_nearest_f10": near["f55v"]["nearest_component_page"] == "f10r",
        "f55_exact_prefers_hand2_bio": bridge_map[("EXACT_CARD_IDENTITY", "HAND_2_BIO")] > bridge_map[("EXACT_CARD_IDENTITY", "HAND_1_HERBAL")],
        "f55_components_prefer_herbal": bridge_map[("COMPONENT_FREQUENCY", "HERBAL_CONTENT")] > bridge_map[("COMPONENT_FREQUENCY", "BIO_CONTENT")],
        "pair_values_bounded": all(0 <= float(row[key]) <= 1 for row in pairs for key in ("exact_card_jaccard", "component_jaccard", "component_frequency_cosine")),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (signatures, pairs, nearest, bridge) for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
