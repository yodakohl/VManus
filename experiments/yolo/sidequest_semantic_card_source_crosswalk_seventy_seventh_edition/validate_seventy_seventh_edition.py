#!/usr/bin/env python3
"""Validate the bounded card-to-source crosswalk."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    crosswalk = read_tsv("SEVENTY_SEVENTH_43_CARD_TO_SOURCE_LICENSES.tsv")
    audits = read_tsv("SEVENTY_SEVENTH_381_EVENT_LICENSE_AUDIT.tsv")
    checks = {
        "forty_three_entries": len(crosswalk) == 43 and len({row["entry_id"] for row in crosswalk}) == 43,
        "every_entry_decided": all(row["licensed_source_slots"] and row["license_class"] for row in crosswalk),
        "no_direct_rich_noun": all(row["direct_rich_noun_license"] == "NO" for row in crosswalk),
        "381_events": len(audits) == 381 and len({row["source_group_id"] for row in audits}) == 381,
        "all_events_classified": all(row["license_status"] in {"CONTENT_SLOT_LICENSED", "OPERATION_OR_REFERENCE_ONLY"} for row in audits),
        "no_event_invents_noun": all(row["rich_noun_may_be_invented"] == "NO" for row in audits),
        "all_atoms_accounted": all(row["crosswalk_entry_ids"] != "NONE" or row["structural_or_local_atoms"] != "NONE" for row in audits),
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in crosswalk + audits),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
