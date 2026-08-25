#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EDITION = ROOT / "sidequest_semantic_fifth_hand_normalized_edition_eight_hundred_eightieth"
PHRASES = ROOT / "sidequest_semantic_recurrent_phrasebook_eight_hundred_eighty_first"
MARKS = EDITION / "EIGHT_HUNDRED_EIGHTIETH_438_MARK_FIFTH_HAND_EDITION.tsv"
OCCURRENCES = PHRASES / "EIGHT_HUNDRED_EIGHTY_FIRST_22_PHRASE_OCCURRENCES.tsv"
PHRASEBOOK = PHRASES / "EIGHT_HUNDRED_EIGHTY_FIRST_10_RECURRENT_PHRASES.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_SECOND"

LOCAL_COMPACT = {
    "PROC118": "DEN POSTEN LAENGER LEITEN",
    "PROC119": "DEN GANZEN POSTEN ANSETZEN UND SCHLIESSEN",
    "PROC071": "ABKUEHLEN UND WEITERARBEITEN",
    "PROC167": "VON DORT WEITERLEITEN",
    "PROC159": "KURZ WEITERLEITEN UND SCHLIESSEN",
    "PROC115": "WEITERARBEITEN",
    "PROC065": "DANACH DIESEN POSTEN",
    "PROC007": "DANACH DIESEN POSTEN BEARBEITEN, ENTNEHMEN UND WEITERFUEHREN",
    "PROC010": "DEN POSTEN KURZ WEITERBEARBEITEN",
    "PROC150": "DAS WASSER UMSETZEN",
    "PROC165": "AUS DER QUELLE ZUGEBEN",
    "PROC161": "DEN POSTEN KURZ DURCH DEN DURCHLASS FUEHREN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def atoms(recipe: str) -> set[str]:
    return set() if recipe.startswith("WHOLE[") else set(recipe.split("+"))


def slot(recipe: str) -> str:
    values = atoms(recipe)
    if "DY" in values:
        return "RESULT_OR_CLOSE"
    if values & {"AIN", "AIIN", "IIN"}:
        return "QUANTITY_OR_STAGE"
    if "AL" in values:
        return "TARGET"
    if "AR" in values:
        return "SOURCE"
    if values & {"OR", "AIR", "HO"}:
        return "MATERIAL_OR_MEDIUM"
    if values & {"OK", "CHD", "CHK", "CKH", "K", "L", "T", "SHED", "SH", "SOLK"}:
        return "OPERATION_OR_STATE"
    if values & {"OT", "OL"}:
        return "ORDER_OR_CONTINUATION"
    if "Y" in values:
        return "ACTIVE_ITEM"
    return "LOCAL_CONTENT"


def main() -> None:
    all_marks = read(MARKS)
    occurrences = read(OCCURRENCES)
    phrasebook = read(PHRASEBOOK)
    physical: dict[str, dict[str, str]] = {}
    for row in all_marks:
        if not row["stage"].startswith("CONDITION"):
            physical.setdefault(row["source_id"], row)
    ordered = sorted(physical.values(), key=lambda row: int(row["source_id"][1:]))
    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ordered:
        by_unit[row["unit"]].append(row)

    window_rows = []
    boundary_events: dict[str, dict[str, object]] = {}
    frame_acc: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"left": set(), "right": set(), "units": set(), "pages": set()})
    for occurrence in occurrences:
        sequence = by_unit[occurrence["unit"]]
        ids = [row["source_id"] for row in sequence]
        start = ids.index(occurrence["start_source_id"])
        end = ids.index(occurrence["end_source_id"])
        left = sequence[start - 1] if start > 0 else None
        right = sequence[end + 1] if end + 1 < len(sequence) else None
        left_slot = "STATEMENT_START" if left is None else slot(left["component_recipe"])
        right_slot = "STATEMENT_END" if right is None else slot(right["component_recipe"])
        frame_acc[occurrence["phrase_id"]]["left"].add(left_slot)
        frame_acc[occurrence["phrase_id"]]["right"].add(right_slot)
        frame_acc[occurrence["phrase_id"]]["units"].add(occurrence["unit"])
        frame_acc[occurrence["phrase_id"]]["pages"].add(occurrence["page"])
        window_rows.append(
            {
                "phrase_id": occurrence["phrase_id"],
                "unit": occurrence["unit"],
                "page": occurrence["page"],
                "left_source_id": left["source_id"] if left else "NONE",
                "left_surface": left["fifth_hand_surface"] if left else "NONE",
                "left_identity": left["identity"] if left else "NONE",
                "left_slot": left_slot,
                "left_reading_de": left["concrete_default_de"] if left else "AUSSAGEANFANG",
                "phrase_surface": occurrence["surface_sequence"],
                "phrase_reading_de": occurrence["working_phrase_de"],
                "right_source_id": right["source_id"] if right else "NONE",
                "right_surface": right["fifth_hand_surface"] if right else "NONE",
                "right_identity": right["identity"] if right else "NONE",
                "right_slot": right_slot,
                "right_reading_de": right["concrete_default_de"] if right else "AUSSAGEENDE",
            }
        )
        for side, neighbour in [("LEFT", left), ("RIGHT", right)]:
            if neighbour is None:
                continue
            entry = boundary_events.setdefault(
                neighbour["source_id"],
                {
                    "source_id": neighbour["source_id"],
                    "page": neighbour["page"],
                    "unit": neighbour["unit"],
                    "surface": neighbour["fifth_hand_surface"],
                    "identity": neighbour["identity"],
                    "card_class": neighbour["card_class"],
                    "component_recipe": neighbour["component_recipe"],
                    "global_default_de": neighbour["concrete_default_de"],
                    "slot": slot(neighbour["component_recipe"]),
                    "boundary_sides": set(),
                    "phrase_ids": set(),
                },
            )
            entry["boundary_sides"].add(side)
            entry["phrase_ids"].add(occurrence["phrase_id"])

    boundary_rows = []
    local_rows = []
    for source_id, entry in sorted(boundary_events.items(), key=lambda pair: int(pair[0][1:])):
        identity = str(entry["identity"])
        compact = LOCAL_COMPACT.get(identity, str(entry["global_default_de"]))
        row = {
            **{key: value for key, value in entry.items() if key not in {"boundary_sides", "phrase_ids"}},
            "boundary_sides": ",".join(sorted(entry["boundary_sides"])),
            "phrase_ids": ",".join(sorted(entry["phrase_ids"])),
            "phrase_ready_reading_de": compact,
            "semantic_atoms_changed": "NO",
        }
        boundary_rows.append(row)
        if entry["card_class"] == "LOCAL_MODEL":
            local_rows.append(
                {
                    "identity": identity,
                    "surface": entry["surface"],
                    "source_id": source_id,
                    "page": entry["page"],
                    "unit": entry["unit"],
                    "slot": entry["slot"],
                    "old_cardwise_default_de": entry["global_default_de"],
                    "compact_phrase_boundary_de": compact,
                    "phrase_ids": ",".join(sorted(entry["phrase_ids"])),
                    "revision_kind": "WORD_ORDER_AND_ELLIPSIS_ONLY",
                    "new_stem_meaning": "NO",
                }
            )

    frame_rows = []
    phrase_by_id = {row["phrase_id"]: row for row in phrasebook}
    for phrase_id in sorted(frame_acc):
        phrase = phrase_by_id[phrase_id]
        data = frame_acc[phrase_id]
        frame_rows.append(
            {
                "phrase_id": phrase_id,
                "working_phrase_de": phrase["working_phrase_de"],
                "left_slots": ",".join(sorted(data["left"])),
                "right_slots": ",".join(sorted(data["right"])),
                "occurrences": phrase["occurrences"],
                "pages": ",".join(sorted(data["pages"])),
                "teaching_frame_de": f"[{','.join(sorted(data['left']))}] → {phrase['working_phrase_de']} → [{','.join(sorted(data['right']))}]",
            }
        )

    write(f"{PREFIX}_22_ANCHORED_PHRASE_WINDOWS.tsv", window_rows, ["phrase_id", "unit", "page", "left_source_id", "left_surface", "left_identity", "left_slot", "left_reading_de", "phrase_surface", "phrase_reading_de", "right_source_id", "right_surface", "right_identity", "right_slot", "right_reading_de"])
    write(f"{PREFIX}_31_UNIQUE_BOUNDARY_EVENTS.tsv", boundary_rows, ["source_id", "page", "unit", "surface", "identity", "card_class", "component_recipe", "global_default_de", "slot", "boundary_sides", "phrase_ids", "phrase_ready_reading_de", "semantic_atoms_changed"])
    write(f"{PREFIX}_12_LOCAL_BOUNDARY_REFINEMENTS.tsv", local_rows, ["identity", "surface", "source_id", "page", "unit", "slot", "old_cardwise_default_de", "compact_phrase_boundary_de", "phrase_ids", "revision_kind", "new_stem_meaning"])
    write(f"{PREFIX}_10_PHRASE_SLOT_FRAMES.tsv", frame_rows, ["phrase_id", "working_phrase_de", "left_slots", "right_slots", "occurrences", "pages", "teaching_frame_de"])

    lines = ["# Phrasenränder und lokale Karten", ""]
    for row in local_rows:
        lines.extend(
            [
                f"- `{row['surface']}` ({row['identity']}, {row['unit']}): **{row['compact_phrase_boundary_de']}**",
                f"  Slot: {row['slot']}; Anker: {row['phrase_ids']}. Der Komponentenwert bleibt unverändert.",
            ]
        )
    lines.extend(
        [
            "",
            "Die zwölf Änderungen sind keine neuen Wörter. Sie machen aus gestapelten Kartenwerten",
            "eine sprechbare Werkstattanweisung: Quelle steht im Deutschen vor ZUGEBEN, ein bereits",
            "gesetztes POSTEN wird nicht mechanisch wiederholt, und SCHLUSS wird als Verb ausgeführt.",
        ]
    )
    (HERE / f"{PREFIX}_BOUNDARY_LEXICON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "PHRASE_BOUNDARIES_REFINE_TWELVE_LOCAL_CARDS_WITHOUT_CHANGING_STEMS",
        "phrase_types": len(frame_rows),
        "phrase_windows": len(window_rows),
        "unique_boundary_events": len(boundary_rows),
        "portable_boundary_events": sum(row["card_class"] == "PORTABLE_CORE" for row in boundary_rows),
        "local_boundary_events": len(local_rows),
        "local_identities_refined": len({row["identity"] for row in local_rows}),
        "left_statement_boundaries": sum(row["left_source_id"] == "NONE" for row in window_rows),
        "right_statement_boundaries": sum(row["right_source_id"] == "NONE" for row in window_rows),
        "semantic_atom_changes": 0,
        "new_stem_meanings": 0,
        "fixed_pages": sorted({row["page"] for row in boundary_rows}),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 882: phrase-boundary lexicon\n\n"
        "The 22 phrase windows have 31 distinct neighbouring events: 19 portable core and 12\n"
        "local-model cards. Their positions resolve into quantity/stage, source, target, material,\n"
        "operation/state, order/continuation and result/close slots.\n\n"
        "Twelve local cards now receive compact phrase-ready readings such as DEN GANZEN POSTEN\n"
        "ANSETZEN UND SCHLIESSEN, VON DORT WEITERLEITEN and AUS DER QUELLE ZUGEBEN. These are\n"
        "word-order and ellipsis repairs only: no component or stem meaning changes.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
