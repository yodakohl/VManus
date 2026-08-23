#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
DICT = BASE / "TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv"
EVENTS = BASE / "TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv"
ASTRO = BASE / "TWO_HUNDRED_THIRTEENTH_395_ASTRO_SURFACE_BRIDGE.tsv"

COMMON = [
    ("OK", "EINSETZEN", ("OK_SET", "OK_ADD"), ("MC026", "MC040"), "Posten in den aktiven Gang setzen", "Diagrammposten oder Wert setzen"),
    ("OL", "WEITER", ("OL_CONTINUE",), ("MC153", "MC157", "MC019"), "laufenden Ansatz oder Weg fortsetzen", "im selben Ring oder Satz fortsetzen"),
    ("OT", "FOLGE", ("OT_FOLLOW", "OT_NEXT"), ("MC171",), "zum folgenden Posten wechseln", "zum folgenden Diagrammplatz wechseln"),
    ("AR", "VON", ("AR_FROM", "AR_SOURCE"), ("MC055",), "von der aktiven Quelle oder Charge", "vom Bezugssektor oder Ausgangswert"),
    ("AL", "ZIEL", ("AL_TO",), ("MC154", "MC040"), "an die Zielstelle", "zum Zielsektor oder Zielfeld"),
    ("AIIN", "SOLLWERT", ("AIIN_MEASURE", "AIIN_TARGET_MEASURE"), ("MC039",), "örtliches Sollmaß", "Parameter- oder Tabellenwert"),
    ("Y", "DIES", ("Y_CURRENT", "Y_ITEM", "CHY_ITEM"), ("MC123",), "aktuell gemeinter Arbeitsposten", "aktueller Diagrammposten"),
    ("DY", "FERTIG", ("DY_CLOSE", "CLOSE_EXACT", "TERMINAL_CLOSE"), ("MC019",), "lizenzierte Zelle schließen", "Eintrag als fertig markieren"),
    ("OR", "ANSATZ", ("OR_BATCH",), ("MC080", "MC157"), "laufende Zubereitung oder Charge", "Bedingungs- oder Tabellensatz"),
    ("CHED~CHD", "ÜBERFÜHREN", ("CHED_TRANSFER", "CHD_TRANSFER", "CHD~CHED_TRANSFER"), ("MC074",), "zwischen Arbeitsplätzen übertragen", "zwischen Diagrammplätzen übertragen"),
]

PROSE = [
    ("L", "AB", ("L_OUT", "LCH_WITHDRAW"), "aus dem aktiven Posten herausführen"),
    ("P", "ZU", ("P_IN",), "in einen lokalen Empfänger zuführen"),
    ("AIN", "PORTION", ("AIN_PORTION",), "abgegrenzte Teilmenge"),
    ("IIN", "STUFE", ("IIN_TARGET_STAGE", "IIN_PORT_GRADE"), "Arbeits- oder Bearbeitungsstufe"),
    ("E", "KURZ", ("GRADE_1", "E_SHORT"), "kurz oder unmittelbar"),
    ("EE", "LANG", ("GRADE_2", "EE_LONG", "EE_HOLD"), "länger halten oder fortsetzen"),
    ("EEE", "VOLL", ("GRADE_3", "EEE_FULL"), "bis zur vollen Stufe"),
    ("HO", "ZUTAT", ("HO_INGREDIENT",), "weiterer Materialposten"),
    ("CHEO", "AUSZUG", ("CHEO_EXTRACT",), "gewonnener Auszug"),
    ("AIR", "LAUFFLÜSSIGKEIT", ("AIR_WATER",), "Flüssigkeit im lokalen Lauf"),
    ("CTH", "BEREIT", ("CTH_READY",), "Posten als vorbereitet setzen"),
    ("SHED", "ABSETZEN", ("SHED_SETTLE",), "stehen und sich absetzen lassen"),
    ("CHK", "WÄRMEN", ("CHK_WARM",), "erwärmen oder warm halten"),
    ("CKH", "DURCHLASS", ("CKH_THROUGH",), "durch eine lokale Passage führen"),
    ("CKHE", "SEIHEN", ("CKHE_STRAIN",), "durch einen trennenden Durchlass führen"),
    ("SOLK", "SAMMELN", ("SOLK_COLLECT",), "an einer Auffangstelle halten"),
    ("LSH", "WASCHEN", ("LSH_WASH",), "Wasch- oder Spülgang"),
    ("TY", "TEIL", ("TY_PART",), "Materialteil oder Rest"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def matches(formula: str, keys: tuple[str, ...]) -> bool:
    return any(key in formula for key in keys)


def main() -> None:
    dictionary = read(DICT)
    events = read(EVENTS)
    astro = read(ASTRO)
    event_counts = Counter(row["master_card_id"] for row in events)
    astro_counts = Counter(row["exact_prose_card_id"] for row in astro if row["is_herbal_bio_bridge_card"] == "YES")

    common_rows: list[dict[str, object]] = []
    for order, (axis, value, keys, anchors, prose_expansion, astro_expansion) in enumerate(COMMON, 1):
        cards = [row for row in dictionary if matches(row["component_formula"], keys)]
        common_rows.append({
            "teaching_order": order,
            "axis": axis,
            "portable_value_de": value,
            "prose_local_expansion_de": prose_expansion,
            "astro_local_expansion_de": astro_expansion,
            "productive_card_types": len(cards),
            "prose_events": sum(event_counts[row["master_card_id"]] for row in cards),
            "astro_anchor_card_ids": "|".join(anchors),
            "astro_exact_groups": sum(astro_counts[card_id] for card_id in anchors),
            "example_prose_cards": "|".join(row["master_card_id"] for row in cards[:4]),
            "scope": "COMMON_THREE_REGISTER_CORE",
        })
    write(OUT / "TWO_HUNDRED_FIFTEENTH_TEN_COMMON_CORE_AXES.tsv", common_rows)

    prose_rows: list[dict[str, object]] = []
    for order, (axis, value, keys, reading) in enumerate(PROSE, 1):
        cards = [row for row in dictionary if matches(row["component_formula"], keys)]
        prose_rows.append({
            "teaching_order": order,
            "axis": axis,
            "portable_prose_value_de": value,
            "prose_reading_de": reading,
            "productive_card_types": len(cards),
            "prose_events": sum(event_counts[row["master_card_id"]] for row in cards),
            "example_cards": "|".join(row["master_card_id"] for row in cards[:4]),
            "astro_rule": "keine portable Astro-Bedeutung; gleiche Zeichenfolge dort lokal lesen",
            "scope": "HERBAL_BIO_PROSE_ONLY",
        })
    write(OUT / "TWO_HUNDRED_FIFTEENTH_EIGHTEEN_PROSE_AXES.tsv", prose_rows)

    whole_rows: list[dict[str, object]] = []
    for row in dictionary:
        if row["component_class"] != "MEMORIZED_WHOLE_CARD":
            continue
        if row["master_card_id"] == "MC119":
            scope = "COMMON_THREE_REGISTER_RESULT_CARD"
            herbal = "Klarlauf oder geklärter Pflanzenauszug"
            bio = "klarer Stationsablauf"
            astro_expansion = "abgelesener oder freigegebener Diagrammwert"
        else:
            scope = "PROSE_LOCAL_WHOLE_CARD"
            herbal = row["current_value_de"] if "H" in row["records"] else "NOT_USED"
            bio = row["current_value_de"] if "B" in row["records"] else "NOT_USED"
            astro_expansion = "kein portabler Ganzkartenwert"
        whole_rows.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "portable_value_de": row["current_value_de"],
            "scope": scope,
            "herbal_expansion_de": herbal,
            "bio_expansion_de": bio,
            "astro_expansion_de": astro_expansion,
            "prose_occurrences": row["event_count"],
        })
    write(OUT / "TWO_HUNDRED_FIFTEENTH_22_SCOPED_WHOLE_CARDS.tsv", whole_rows)

    scoped_rows: list[dict[str, object]] = []
    for row in dictionary:
        formula = row["component_formula"]
        common_axes = [axis for axis, _, keys, _, _, _ in COMMON if matches(formula, keys)]
        prose_axes = [axis for axis, _, keys, _ in PROSE if matches(formula, keys)]
        if row["component_class"] == "MEMORIZED_WHOLE_CARD":
            scope = "COMMON_RESULT_WHOLE_CARD" if row["master_card_id"] == "MC119" else "LOCAL_WHOLE_CARD"
        elif common_axes:
            scope = "HAS_COMMON_CORE_AXIS"
        elif prose_axes:
            scope = "PROSE_COMPONENT_CARD"
        else:
            scope = "LOCAL_PRODUCTIVE_CARD_CORE"
        scoped_rows.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "current_value_de": row["current_value_de"],
            "semantic_scope": scope,
            "common_axes": "+".join(common_axes) if common_axes else "NONE",
            "prose_only_axes": "+".join(prose_axes) if prose_axes else "NONE",
            "component_formula": formula,
            "event_count": row["event_count"],
            "records": row["records"],
        })
    write(OUT / "TWO_HUNDRED_FIFTEENTH_173_CARD_SCOPED_DICTIONARY.tsv", scoped_rows)

    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "astro_source_sha256": hashlib.sha256(ASTRO.read_bytes()).hexdigest(),
        "common_axes": len(common_rows),
        "prose_axes": len(prose_rows),
        "whole_cards": len(whole_rows),
        "common_whole_cards": sum(row["scope"] == "COMMON_THREE_REGISTER_RESULT_CARD" for row in whole_rows),
        "cards": len(scoped_rows),
        "scope_counts": dict(Counter(row["semantic_scope"] for row in scoped_rows)),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
