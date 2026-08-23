#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_expanded_hand_profile_hundred_ninety_first/HUNDRED_NINETY_FIRST_381_EVENT_EXPANDED_PROFILE.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


PAGE_PROFILE = {
    "f10r": "HAND_A_EARLY_HERBAL",
    "f11r": "HAND_A_EARLY_HERBAL",
    "f55v": "HAND_B_LATE_HERBAL",
    "f56r": "HAND_B_LATE_HERBAL",
    "f81v": "HAND_C_EARLY_BIO",
    "f82r": "HAND_C_EARLY_BIO",
    "f83r": "HAND_D_LATE_BIO",
}


CORRECTIONS = {
    ("f10r", "MC153", "MEDIAL"): ("A1", "chol", "Hand A keeps the ch-L frame on f10r.", True),
    ("f10r", "MC161", "MEDIAL"): ("A2", "cthy", "Hand A drops the che-frame on the CTH card.", True),
    ("f11r", "MC161", "MEDIAL"): ("A2", "cthy", "Hand A drops the che-frame on the CTH card.", True),
    ("f56r", "MC026", "MEDIAL"): ("B1", "choky", "Hand B keeps the ch-frame on the active current-item card.", True),
    ("f81v", "MC153", "MEDIAL"): ("C1", "qol", "Rejected: f81v uses qol only in a late local block, not page-wide.", False),
    ("f82r", "MC040", "MEDIAL"): ("C2", "qokal", "Hand C retains q on the medial OK-target card.", True),
    ("f83r", "MC161", "MEDIAL"): ("D1", "shcthy", "Rejected: f83r splits shcthy and checthy by local block.", False),
    ("f83r", "MC040", "MEDIAL"): ("D2", "qokal", "Hand D retains q on the medial OK-target card.", True),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    fieldnames = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def frame(surface: str) -> str:
    for prefix, name in (("q", "Q"), ("sh", "SH"), ("ch", "CH"), ("s", "S"), ("d", "D"), ("t", "T"), ("o", "O"), ("k", "K"), ("l", "L")):
        if surface.startswith(prefix):
            return name
    return "BARE_OR_OTHER"


def main() -> None:
    base = read(BASE)
    dictionary = {row["master_card_id"]: row for row in read(DICTIONARY)}
    rows: list[dict[str, object]] = []
    for row in base:
        key = (row["page"], row["master_card_id"], row["position_class"])
        if key in CORRECTIONS and CORRECTIONS[key][3]:
            rule, surface, explanation, _selected = CORRECTIONS[key]
        else:
            rule, surface, explanation = "PROFILE_DEFAULT", row["expanded_profile_surface"], "Use the expanded shared profile."
        rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "page_hand_profile": PAGE_PROFILE[row["page"]],
                "field_id": row["field_id"],
                "position_class": row["position_class"],
                "master_card_id": row["master_card_id"],
                "portable_value_de": row["portable_value_de"],
                "observed_surface": row["observed_surface"],
                "shared_profile_surface": row["expanded_profile_surface"],
                "hand_rule": rule,
                "hand_rule_de": explanation,
                "page_hand_surface": surface,
                "shared_match": row["expanded_match"],
                "page_hand_match": "YES" if surface == row["observed_surface"] else "NO",
                "surface_registered": "YES" if surface in dictionary[row["master_card_id"]]["registered_surfaces"].split("|") else "NO",
            }
        )
    write(OUT / "HUNDRED_NINETY_SECOND_381_EVENT_PAGE_HAND_PROFILE.tsv", rows)

    correction_rows: list[dict[str, object]] = []
    for key, (rule, surface, explanation, selected_for_profile) in CORRECTIONS.items():
        page, card_id, position = key
        selected = [row for row in rows if row["page"] == page and row["master_card_id"] == card_id and row["position_class"] == position]
        correction_rows.append(
            {
                "page_hand_profile": PAGE_PROFILE[page],
                "rule_id": rule,
                "page": page,
                "master_card_id": card_id,
                "position_class": position,
                "shared_surface": selected[0]["shared_profile_surface"],
                "page_hand_surface": surface,
                "rule_de": explanation,
                "selected_for_profile": "YES" if selected_for_profile else "NO",
                "events": len(selected),
                "shared_exact": sum(row["shared_match"] == "YES" for row in selected),
                "page_hand_exact": sum(row["page_hand_match"] == "YES" for row in selected),
                "net_gain": sum(row["page_hand_match"] == "YES" for row in selected) - sum(row["shared_match"] == "YES" for row in selected),
            }
        )
    write(OUT / "HUNDRED_NINETY_SECOND_8_PAGE_HAND_CORRECTIONS.tsv", correction_rows)

    fingerprint_rows: list[dict[str, object]] = []
    for page in PAGE_PROFILE:
        selected = [row for row in rows if row["page"] == page]
        multi = [row for row in selected if "|" in dictionary[str(row["master_card_id"])]["registered_surfaces"]]
        counts = Counter(frame(str(row["observed_surface"])) for row in multi)
        fingerprint_rows.append(
            {
                "page": page,
                "page_hand_profile": PAGE_PROFILE[page],
                "events": len(selected),
                "multi_surface_card_events": len(multi),
                "q_frame": counts["Q"],
                "sh_frame": counts["SH"],
                "ch_frame": counts["CH"],
                "s_frame": counts["S"],
                "d_frame": counts["D"],
                "o_frame": counts["O"],
                "other_frame": len(multi) - sum(counts[key] for key in {"Q", "SH", "CH", "S", "D", "O"}),
                "shared_exact": sum(row["shared_match"] == "YES" for row in selected),
                "page_hand_exact": sum(row["page_hand_match"] == "YES" for row in selected),
                "residual_events": sum(row["page_hand_match"] == "NO" for row in selected),
            }
        )
    write(OUT / "HUNDRED_NINETY_SECOND_7_PAGE_RENDERER_FINGERPRINTS.tsv", fingerprint_rows)

    residual_by_profile: list[dict[str, object]] = []
    for profile in sorted(set(PAGE_PROFILE.values())):
        selected = [row for row in rows if row["page_hand_profile"] == profile]
        residual = [row for row in selected if row["page_hand_match"] == "NO"]
        transforms = Counter(f"{row['page_hand_surface']}>{row['observed_surface']}@{row['position_class']}" for row in residual)
        residual_by_profile.append(
            {
                "page_hand_profile": profile,
                "pages": "|".join(page for page, value in PAGE_PROFILE.items() if value == profile),
                "events": len(selected),
                "exact": len(selected) - len(residual),
                "residual": len(residual),
                "top_residuals": "|".join(f"{key}:{value}" for key, value in transforms.most_common(8)) or "NONE",
            }
        )
    write(OUT / "HUNDRED_NINETY_SECOND_4_HAND_PROFILE_SUMMARY.tsv", residual_by_profile)

    shared_exact = sum(row["shared_match"] == "YES" for row in rows)
    page_exact = sum(row["page_hand_match"] == "YES" for row in rows)
    summary = {
        "shared_profile_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "events": len(rows),
        "pages": len(PAGE_PROFILE),
        "page_hand_profiles": len(set(PAGE_PROFILE.values())),
        "page_hand_candidates": len(CORRECTIONS),
        "selected_page_hand_corrections": sum(value[3] for value in CORRECTIONS.values()),
        "correction_triggers": sum(row["hand_rule"] != "PROFILE_DEFAULT" for row in rows),
        "shared_exact": shared_exact,
        "page_hand_exact": page_exact,
        "net_gain": page_exact - shared_exact,
        "page_hand_accuracy": round(page_exact / len(rows), 6),
        "remaining_residual_events": len(rows) - page_exact,
        "all_surfaces_registered": all(row["surface_registered"] == "YES" for row in rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
