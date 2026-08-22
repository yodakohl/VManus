#!/usr/bin/env python3
"""Publish the four-role V60 selection from frozen role outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

FINAL = {
    "2f1c5e56e8f0ff459065": ("AIIN", "MASS?", "PARAMETER_NOUN", "R1,R2,R4", "SOLLWERT?"),
    "276a7c2d74d1143446f4": ("OKY", "ANWENDEN?", "ACTION", "R4", "VERWENDEN?|AUSFÜHREN?"),
    "e0b630cb1b5df5e7105b": ("CTHY", "BEREIT?", "STATE", "R1,R2,R4", "FREIGABE?"),
    "7a4bb8136330ee4e6e56": ("OR", "ANSATZ?", "WORKING_MATERIAL_NOUN", "R3,R4", "ZUBEREITUNG?"),
    "dd0ecaf5e27d81befffc": ("AL", "ZIEL?", "RELATION_ARGUMENT", "R3,R4", "DORTHIN?"),
    "b5df9126607030b95175": ("EY", "KLAR?", "STATE", "R1,R2,R4", "ENDZUSTAND?"),
    "dec401773c1f0347793d": ("OLOR", "VORIGES?", "BACK_REFERENCE", "R2,R4", "VOM VORIGEN?|VORLAUF?"),
    "faf321940aed922846a9": ("OTCHEY", "ANTEIL?", "SELECTION_NOUN", "R1,R4", "NIMM?|POSTEN?"),
    "0275fbf14e07935b0a45": ("OKEEY", "TEMPERIEREN?", "ACTION", "R3,R4", "LAUWARM?"),
    "7db18b2f0fb7ed0fcfd3": ("OKE", "SPÜLEN?", "TERMINAL_ACTION", "R1,R2,R3,R4", "SCHRITT_A?"),
    "de7321bface5628e35d6": ("LCHE", "ABLASSEN?", "TERMINAL_ACTION", "R1,R2,R4", "SCHRITT_B?|ABFÜHREN?"),
}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    role_files = [
        HERE / "V60_R1_11_CARD_DECISIONS.tsv",
        HERE / "V60_R2_EXACT_CARD_DECISIONS.tsv",
        HERE / "V60_R3_11_CARD_TECHNICAL_DECISIONS.tsv",
        HERE / "V60_R4_EXACT_CARD_DECISIONS.tsv",
    ]
    source_dict = HERE / "V60_R4_REVISED_173_CARD_DICTIONARY.tsv"
    source_events = HERE / "V60_R4_REVISED_381_EVENT_LEDGER.tsv"
    dictionary = read_tsv(source_dict)
    events = read_tsv(source_events)
    dictionary_by_id = {row["joint_tuple_id"]: row for row in dictionary}

    rows = []
    for joint_id, (card, winner, source_class, support, strongest_rival) in FINAL.items():
        item = dictionary_by_id[joint_id]
        rows.append({
            "card": card,
            "joint_tuple_id": joint_id,
            "surface_examples_display_only": item["surface_examples"],
            "occurrences": item["occurrences"],
            "pages": item["pages"],
            "selected_short_mnemonic": winner,
            "source_class": source_class,
            "direct_role_support": support,
            "strongest_live_rival": strongest_rival,
            "binding": "EXACT_JOINT_TUPLE_ID_ONLY",
            "interpretation_status": "CREATIVE_WORKING_VALUE_NOT_TRANSLATION",
        })

    # R4 already encodes exactly the chosen values.  Assert this before using
    # its full tables as the selected release.
    for row in dictionary:
        if row["joint_tuple_id"] in FINAL:
            assert row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == FINAL[row["joint_tuple_id"]][1]
    for row in events:
        if row["joint_tuple_id"] in FINAL:
            assert row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == FINAL[row["joint_tuple_id"]][1]

    outputs = {
        "decisions": HERE / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv",
        "dictionary": HERE / "V60_SELECTED_173_CARD_DICTIONARY.tsv",
        "events": HERE / "V60_SELECTED_381_EVENT_LEDGER.tsv",
    }
    write_tsv(outputs["decisions"], rows, list(rows[0]))
    shutil.copyfile(source_dict, outputs["dictionary"])
    shutil.copyfile(source_events, outputs["events"])
    checks = {
        "four_independent_role_tables_present": all(path.exists() for path in role_files),
        "eleven_selected_cards": len(rows) == 11,
        "eighty_five_selected_occurrences": sum(int(row["occurrences"]) for row in rows) == 85,
        "dictionary_173": len(dictionary) == 173,
        "events_381": len(events) == 381,
        "all_values_short": all(len(row["selected_short_mnemonic"].rstrip("?").split()) <= 1 for row in rows),
        "no_page_host_binding": all(row["binding"] == "EXACT_JOINT_TUPLE_ID_ONLY" for row in rows),
        "no_f84": all(not row["page"].startswith("f84") for row in events),
    }
    validation = {
        "schema": "SIDEQUEST_V60_FOUR_ROLE_SELECTION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "role_inputs": {str(path.relative_to(ROOT)): sha(path) for path in role_files},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V60_SELECTION_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if validation["status"] != "PASS":
        raise SystemExit("V60 selection validation failed")


if __name__ == "__main__":
    main()
