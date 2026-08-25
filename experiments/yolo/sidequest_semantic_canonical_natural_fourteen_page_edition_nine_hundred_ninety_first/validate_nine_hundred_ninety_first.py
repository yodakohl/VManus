#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BIO = {"f75r", "f81v", "f82r", "f83r"}


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    codebook = read("PASS991_159_CODEBOOK.tsv")
    events = read("PASS991_2511_EVENT_INTERLINEAR.tsv")
    clauses = read("PASS991_354_NATURAL_CLAUSE_EDITION.tsv")
    addresses = read("PASS991_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read("PASS991_14_PAGE_READABLE_EDITION.tsv")
    clause_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    address_ids = [row["event_id"] for row in addresses]
    nonbio = [row for row in clauses if row["physical_page"] not in BIO]
    checks = {
        "codebook_159": len(codebook) == 159,
        "events_2511": len(events) == 2511 and len({row["event_id"] for row in events}) == 2511,
        "clauses_354": len(clauses) == 354 and len({row["clause_id"] for row in clauses}) == 354,
        "clause_events_2010": len(clause_ids) == len(set(clause_ids)) == 2010,
        "addresses_501": len(address_ids) == len(set(address_ids)) == 501,
        "full_partition": set(clause_ids) | set(address_ids) == {row["event_id"] for row in events}
        and not set(clause_ids) & set(address_ids),
        "bio_318_natural": sum(row["physical_page"] in BIO for row in clauses) == 318,
        "nonbio_36_manual": len(nonbio) == 36
        and all(row["reading_source"] in {"HERBAL_NATURAL_REWRITE", "CELESTIAL_NATURAL_LOOKUP_REWRITE", "F88_BATCH_NATURAL_REWRITE"} for row in nonbio),
        "all_clauses_natural": all(row["complete_working_translation_de"] for row in clauses),
        "no_component_list_in_nonbio": all(" · " not in row["complete_working_translation_de"] for row in nonbio),
        "pages_14": len(pages) == 14 and sum(int(row["events"]) for row in pages) == 2511,
        "short_specialist_headwords": all(" " not in row["spoken_value_de"] for row in codebook if row["layer"] in {"E_LOCAL_SPECIALIST_HEADWORD", "F_IMAGE_OWNED_SPECIALIST_CARD"}),
        "sealed_absent": all("f84" not in row["physical_page"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS991_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
