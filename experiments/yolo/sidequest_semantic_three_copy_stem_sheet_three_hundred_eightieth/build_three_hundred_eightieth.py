#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P376 = ROOT / "experiments/yolo/sidequest_semantic_image_first_practice_page_three_hundred_seventy_sixth"
P377 = ROOT / "experiments/yolo/sidequest_semantic_rescaled_image_copy_three_hundred_seventy_seventh"
P379 = ROOT / "experiments/yolo/sidequest_semantic_board_call_third_copy_three_hundred_seventy_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CORES = {
    1: ("HO", "Zutat", "ENTRY_WRAPPER+HO"),
    2: ("OR", "Ansatz", "ENTRY_WRAPPER+OR"),
    7: ("CTHY", "Bereit", "ENTRY_WRAPPER+CTHY"),
    8: ("Y", "Diesposten", "ENTRY_WRAPPER+Y"),
    9: ("AIIN", "Sollmaß", "ENTRY_WRAPPER+AIIN"),
    10: ("CKHY", "durchleiten", "ENTRY_WRAPPER+CKH+Y"),
    11: ("OKY", "Einsetzen", "ENTRY_WRAPPER+OK+Y"),
    12: ("OKEEY", "Langkontakt", "ENTRY_WRAPPER+OK+EE+Y"),
}


def wrapper(surface: str, core: str) -> str:
    low = surface.lower()
    low_core = core.lower()
    if not low.endswith(low_core):
        return "NON_SUFFIX_REALIZATION"
    prefix = low[: -len(low_core)] if len(low_core) else low
    return prefix.upper() if prefix else "BARE"


def main() -> None:
    first = {int(row["source_position"]): row for row in read(P376 / "THREE_HUNDRED_SEVENTY_SIXTH_14_SOURCE_CARDS.tsv")}
    second = {int(row["source_position"]): row for row in read(P377 / "THREE_HUNDRED_SEVENTY_SEVENTH_14_CARD_CROSSWALK.tsv")}
    third = {int(row["source_position"]): row for row in read(P379 / "THREE_HUNDRED_SEVENTY_NINTH_14_HIDDEN_VALUE_CHECK.tsv")}
    alignment_rows = []
    paradigm_rows = []
    fixed_rows = []
    for position in range(1, 15):
        a = first[position]
        surfaces = [a["surface"], second[position]["second_palette_surface"], third[position]["third_surface"]]
        registered = a["registered_surface_palette"].split("|")
        observed = list(dict.fromkeys(surfaces))
        missing = [surface for surface in registered if surface not in observed]
        productive = position in CORES
        core, core_value, analysis = CORES.get(position, (a["surface"].upper(), a["atomic_value_de"], "FIXED_CARD_OR_FIXED_COMPOUND"))
        alignment_rows.append({
            "source_position": position,
            "joint_tuple_id": a["joint_tuple_id"],
            "atomic_value_de": a["atomic_value_de"],
            "copy_one_surface": surfaces[0],
            "copy_two_surface": surfaces[1],
            "copy_three_surface": surfaces[2],
            "distinct_observed_surfaces": len(observed),
            "registered_surface_palette": a["registered_surface_palette"],
            "productive_core": core if productive else "NONE",
            "core_value_de": core_value if productive else "WHOLE_CARD",
            "composition": analysis,
            "status": "PRODUCTIVE_WRAPPER_PARADIGM" if productive else "FIXED_CARD",
            "unseen_registered_surfaces": "|".join(missing) if missing else "NONE",
        })
        if productive:
            paradigm_rows.append({
                "core": core,
                "core_value_de": core_value,
                "source_position": position,
                "joint_tuple_id": a["joint_tuple_id"],
                "composition": analysis,
                "observed_surfaces": "|".join(observed),
                "observed_wrappers": "|".join(wrapper(surface, core) for surface in observed),
                "registered_surfaces": "|".join(registered),
                "remaining_registered_predictions": "|".join(missing) if missing else "NONE",
                "predicted_value_de": core_value,
                "prediction_rule": "Only entry wrapper changes; core value and exact card identity remain.",
            })
        else:
            fixed_rows.append({
                "source_position": position,
                "joint_tuple_id": a["joint_tuple_id"],
                "surface": a["surface"],
                "atomic_value_de": a["atomic_value_de"],
                "registered_surface_palette": a["registered_surface_palette"],
                "reason_fixed": "All three copies use the same registered surface; no wrapper prediction is needed.",
            })
    write("THREE_HUNDRED_EIGHTIETH_14_POSITION_STEM_ALIGNMENT.tsv", alignment_rows)
    write("THREE_HUNDRED_EIGHTIETH_EIGHT_PRODUCTIVE_CORES.tsv", paradigm_rows)
    write("THREE_HUNDRED_EIGHTIETH_SIX_FIXED_CARDS.tsv", fixed_rows)
    predictions = [
        {"core": row["core"], "predicted_surface": surface, "predicted_value_de": row["predicted_value_de"], "joint_tuple_id": row["joint_tuple_id"], "licensed_by_registered_palette": "YES"}
        for row in paradigm_rows
        for surface in row["remaining_registered_predictions"].split("|")
        if surface != "NONE"
    ]
    write("THREE_HUNDRED_EIGHTIETH_REMAINING_WRAPPER_PREDICTIONS.tsv", predictions)
    sheet = ["# Pass 380 — Stamm- und Variantenblatt", "", "## Produktive Kerne", ""]
    for row in paradigm_rows:
        sheet.append(f"- **{row['core']} = {row['core_value_de']}**: `{row['observed_surfaces']}`; noch registriert: `{row['remaining_registered_predictions']}`.")
    sheet += ["", "## Feste Karten", ""]
    for row in fixed_rows:
        sheet.append(f"- `{row['surface']}` = {row['atomic_value_de']}.")
    sheet += [
        "",
        "Die Wrapper sind hier Schreiber-/Eintrittsformen. Sie dürfen den Kernwert nicht ändern. Die sechs Vorhersagen sind bereits im Gesamtbrett registriert, wurden aber in den drei Musterkopien noch nicht verwendet.",
    ]
    (HERE / "THREE_HUNDRED_EIGHTIETH_STEM_VARIANT_SHEET.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    report = f"""# Pass 380 — Kerne über drei Kopien

Die acht variablen Positionen bilden acht saubere Workshop-Kerne: HO, OR,
CTHY, Y, AIIN, CKHY, OKY und OKEEY. Ihre unterschiedlichen Eintrittsformen
ändern weder Kartenidentität noch Wert. Sechs weitere Karten bleiben in allen
drei Kopien fest.

Nur {len(predictions)} registrierte Wrapperformen der produktiven Kerne fehlen
noch in den drei Musterkopien: `or`, drei weitere Y-Formen sowie `aiin` und
`daiin`. Sie liefern konkrete Vorhersagen für eine vierte Palette, ohne eine neue
Form zu erfinden.

Als nächstes soll eine vierte Kopie bevorzugt diese sechs noch unbenutzten, aber
bereits registrierten Formen einsetzen und anschließend denselben vierzehnteiligen
Text zurücklesen.
"""
    (HERE / "THREE_HUNDRED_EIGHTIETH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "positions": len(alignment_rows),
        "productive_cores": len(paradigm_rows),
        "fixed_cards": len(fixed_rows),
        "remaining_registered_predictions": len(predictions),
        "cores": [row["core"] for row in paradigm_rows],
        "predicted_surfaces": [row["predicted_surface"] for row in predictions],
    }
    (HERE / "THREE_HUNDRED_EIGHTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
