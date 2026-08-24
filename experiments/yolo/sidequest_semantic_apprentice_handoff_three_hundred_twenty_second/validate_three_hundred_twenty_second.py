#!/usr/bin/env python3
"""Validate Pass 322 apprentice handoff dialogues."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dialogues = read("THREE_HUNDRED_TWENTY_SECOND_FIVE_APPRENTICE_DIALOGUES.tsv")
    channels = read("THREE_HUNDRED_TWENTY_SECOND_25_INFORMATION_CHANNELS.tsv")
    counts = Counter(x["information_channel"] for x in channels)
    checks = {
        "five_lessons": len(dialogues) == 5,
        "five_records": {x["herbal_record"] for x in dialogues} == {"H1", "H2", "H3", "H4", "H5"},
        "every_handoff_has_exact_word": all(x["exact_handshake_words"] for x in dialogues),
        "twenty_five_channels": len(channels) == 25,
        "five_each_channel": set(counts.values()) == {5} and len(counts) == 5,
        "picture_channels_ten": counts["MATERIAL_OWNER"] + counts["STATION_OWNER"] == 10,
        "no_direct_pointer": all(x["direct_cross_page_pointer"] == "NONE" for x in dialogues),
        "all_actions_concrete": all(x["apprentice_action"] and x["spoken_handoff"] for x in dialogues),
        "no_sealed_page": all("f84" not in "\t".join(x.values()).lower() for rows in [dialogues, channels] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
