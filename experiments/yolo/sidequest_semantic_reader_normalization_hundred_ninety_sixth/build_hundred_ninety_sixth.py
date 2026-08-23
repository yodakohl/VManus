#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
HARMONIZED = ROOT / "experiments/yolo/sidequest_semantic_forward_frame_mode_hundred_ninety_fourth/HUNDRED_NINETY_FOURTH_25_TOKEN_MODE_INSTRUCTION.tsv"
MIXED = ROOT / "experiments/yolo/sidequest_semantic_mixed_second_renderer_hundred_ninety_fifth/HUNDRED_NINETY_FIFTH_25_TOKEN_MIXED_RENDERING.tsv"


RULES = {
    "R1_Q_ACTIVE": "Ein registriertes q vor einer O/OT/OL-Karte ändert die Kartenidentität nicht.",
    "R2_AIIN_MEASURE": "AIIN, CHAIIN, DAIIN, SAIIN und TAIIN lesen als dieselbe Sollmaßkarte.",
    "R3_AL_TARGET": "AL, CHAL, CHEAL, DAL, SAL und TAL lesen als dieselbe Zielkarte.",
    "R4_Y_REFERENT": "CHEY, CHY, DY, SHY, SY und Y lesen als dieselbe Dies-Karte.",
    "R5_OL_CONTINUE": "CHEOL, CHOL, OL, QOL, SOL und TOL lesen als dieselbe Weiter-Karte.",
    "R6_OR_PREPARATION": "CHOR, OR, SHOR und SOR lesen als dieselbe Ansatzkarte.",
    "R7_AR_SOURCE": "CHAR, DAR und SAR lesen als dieselbe Davon-Karte.",
    "R8_CTH_STATE": "CHECTHY, CTHY und SHCTHY lesen als dieselbe Bereit-Karte.",
    "R9_CHEDY_CLOSE": "Die registrierten D/S/T-CHEDY-Schlussflächen bleiben ihre jeweilige genaue Schlusskarte.",
    "R10_PAIRED_ALLOGRAPH": "Die übrigen 14 kleinen Aliasformen werden als gelehrte Allographen gelesen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def alias_rule(card_id: str, master: str, alias: str) -> str:
    if alias.startswith("q") and not master.startswith("q"):
        return "R1_Q_ACTIVE"
    if card_id == "MC039":
        return "R2_AIIN_MEASURE"
    if card_id == "MC154":
        return "R3_AL_TARGET"
    if card_id == "MC123":
        return "R4_Y_REFERENT"
    if card_id == "MC153":
        return "R5_OL_CONTINUE"
    if card_id == "MC080":
        return "R6_OR_PREPARATION"
    if card_id == "MC055":
        return "R7_AR_SOURCE"
    if card_id == "MC161":
        return "R8_CTH_STATE"
    if card_id in {"MC025", "MC128"}:
        return "R9_CHEDY_CLOSE"
    return "R10_PAIRED_ALLOGRAPH"


def main() -> None:
    dictionary_rows = read(DICTIONARY)
    dictionary = {row["master_card_id"]: row for row in dictionary_rows}
    surface_index: dict[str, str] = {}
    surface_rows: list[dict[str, object]] = []
    alias_rows: list[dict[str, object]] = []
    for row in dictionary_rows:
        surfaces = row["registered_surfaces"].split("|")
        for surface in surfaces:
            if surface in surface_index:
                raise ValueError(f"ambiguous registered surface: {surface}")
            surface_index[surface] = row["master_card_id"]
            is_master = surface == row["master_form"]
            rule = "MASTER_FORM" if is_master else alias_rule(row["master_card_id"], row["master_form"], surface)
            surface_row = {
                "surface": surface,
                "master_card_id": row["master_card_id"],
                "master_form": row["master_form"],
                "portable_value_de": row["portable_card_value_de"],
                "is_master_form": "YES" if is_master else "NO",
                "normalization_rule": rule,
                "normalizes_to": row["master_form"],
            }
            surface_rows.append(surface_row)
            if not is_master:
                alias_rows.append(surface_row)
    write(OUT / "HUNDRED_NINETY_SIXTH_230_SURFACE_NORMALIZATION.tsv", surface_rows)
    write(OUT / "HUNDRED_NINETY_SIXTH_57_ALIAS_NORMALIZATION.tsv", alias_rows)

    rule_rows: list[dict[str, object]] = []
    for rule_id, rule_de in RULES.items():
        selected = [row for row in alias_rows if row["normalization_rule"] == rule_id]
        rule_rows.append(
            {
                "rule_id": rule_id,
                "reader_rule_de": rule_de,
                "alias_surfaces": len(selected),
                "cards": len({row["master_card_id"] for row in selected}),
                "examples": "|".join(f"{row['surface']}→{row['master_form']}" for row in selected[:8]),
            }
        )
    write(OUT / "HUNDRED_NINETY_SIXTH_10_READER_RULES.tsv", rule_rows)

    observed_rows: list[dict[str, object]] = []
    for row in read(EVENTS):
        decoded = surface_index[row["surface"]]
        observed_rows.append(
            {
                "event_id": row["event_id"],
                "surface": row["surface"],
                "decoded_card_id": decoded,
                "source_card_id": row["master_card_id"],
                "exact_readback": "YES" if decoded == row["master_card_id"] else "NO",
                "normalized_master_form": dictionary[decoded]["master_form"],
                "portable_value_de": dictionary[decoded]["portable_card_value_de"],
            }
        )
    write(OUT / "HUNDRED_NINETY_SIXTH_381_EVENT_READER_AUDIT.tsv", observed_rows)

    h_rows = read(HARMONIZED)
    m_rows = read(MIXED)
    parallel_rows: list[dict[str, object]] = []
    for harmonized, mixed in zip(h_rows, m_rows, strict=True):
        h_card = surface_index[harmonized["surface"]]
        m_card = surface_index[mixed["mixed_hand_surface"]]
        parallel_rows.append(
            {
                "token_order": harmonized["token_order"],
                "harmonized_surface": harmonized["surface"],
                "mixed_surface": mixed["mixed_hand_surface"],
                "harmonized_card": h_card,
                "mixed_card": m_card,
                "intended_card": harmonized["master_card_id"],
                "same_card_readback": "YES" if h_card == m_card == harmonized["master_card_id"] else "NO",
                "normalized_form": dictionary[h_card]["master_form"],
                "portable_value_de": dictionary[h_card]["portable_card_value_de"],
            }
        )
    write(OUT / "HUNDRED_NINETY_SIXTH_25_TOKEN_TWO_HAND_NORMALIZATION.tsv", parallel_rows)

    summary = {
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "cards": len(dictionary_rows),
        "registered_surfaces": len(surface_rows),
        "master_forms": sum(row["is_master_form"] == "YES" for row in surface_rows),
        "aliases": len(alias_rows),
        "ambiguous_registered_surfaces": 0,
        "reader_rules": len(rule_rows),
        "rule_alias_distribution": dict(Counter(str(row["normalization_rule"]) for row in alias_rows)),
        "observed_event_readback": sum(row["exact_readback"] == "YES" for row in observed_rows),
        "two_hand_parallel_readback": sum(row["same_card_readback"] == "YES" for row in parallel_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
