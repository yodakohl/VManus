#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R251 = ROOT / "experiments/yolo/sidequest_semantic_component_equations_two_hundred_fifty_first"
R250 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_working_edition_two_hundred_fiftieth"
R248 = ROOT / "experiments/yolo/sidequest_semantic_astro_native_card_values_two_hundred_forty_eighth"
CARDS = R251 / "TWO_HUNDRED_FIFTY_FIRST_REVISED_173_CARD_DICTIONARY.tsv"
EVENTS = R250 / "TWO_HUNDRED_FIFTIETH_381_PROSE_EVENTS.tsv"
ASTRO = R248 / "TWO_HUNDRED_FORTY_EIGHTH_REVISED_395_GROUP_MANUAL.tsv"

STEM_VALUE = {
    "AR": ("VON_QUELLE", "von der Quelle oder dem Vorrat her"),
    "AL": ("ZU_ZIEL", "an die bezeichnete Stelle oder zum Ziel"),
    "OL": ("WEITER_GLEICHER_FORTGANG", "im selben Fortgang weiter"),
    "OT": ("DANACH_NAECHSTER", "danach zum nächsten Posten"),
    "OR": ("ANSATZ_AKTIVER_SATZ", "der laufende Ansatz oder Bedingungssatz"),
    "Y": ("DIES_AKTUELLER_POSTEN", "dieser aktuell gemeinte Arbeitsposten"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stems(component_parse: str) -> list[str]:
    f = component_parse.upper()
    found: list[str] = []
    tests = {
        "AR": "AR_FROM" in f or bool(re.search(r"(^|\+)\s*AR($|\s)", f)),
        "AL": "AL_TO" in f or bool(re.search(r"(^|\+)\s*AL($|\s)", f)),
        "OL": "OL_CONTINUE" in f or bool(re.search(r"(^|\+)\s*OL($|\s)", f)),
        "OT": "OT_FOLLOW" in f or "OT_NEXT" in f or f.startswith("OT +"),
        "OR": "OR_BATCH" in f or bool(re.search(r"(^|\+)\s*OR($|\s)", f)),
        "Y": "Y_CURRENT" in f or "Y_ITEM" in f or bool(re.search(r"(^|\+)\s*Y($|\s)", f)),
    }
    for stem in STEM_VALUE:
        if tests[stem]:
            found.append(stem)
    return found


def main() -> None:
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    astro = read_tsv(ASTRO)
    selected_cards = []
    by_id: dict[str, dict[str, object]] = {}
    for row in cards:
        detected = stems(row["component_parse"])
        if not detected:
            continue
        item = {
            **row,
            "relation_stems": "|".join(detected),
            "relation_skeleton_de": " + ".join(STEM_VALUE[s][0] for s in detected),
            "composition_reading_de": row["portable_core_de"],
        }
        selected_cards.append(item)
        by_id[row["master_card_id"]] = item

    prose_rows = []
    for row in events:
        if row["master_card_id"] not in by_id:
            continue
        card = by_id[row["master_card_id"]]
        prose_rows.append({
            "event_id": row["event_id"], "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "field_id": row["field_id"], "field_position": row["field_position"],
            "visible_owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"], "relation_stems": card["relation_stems"],
            "relation_skeleton_de": card["relation_skeleton_de"],
            "portable_core_de": card["portable_core_de"],
            "local_register_expansion_de": row["local_register_expansion_de"],
            "terminal_status": row["terminal_status"],
        })

    astro_rows = []
    for row in astro:
        card_id = row["exact_prose_card_id"]
        if card_id not in by_id:
            continue
        card = by_id[card_id]
        astro_rows.append({
            "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
            "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
            "visible_surface": row["visible_surface"], "master_card_id": card_id,
            "relation_stems": card["relation_stems"],
            "relation_skeleton_de": card["relation_skeleton_de"],
            "portable_prose_value_de": row["portable_prose_value_de"],
            "diagram_local_reading_de": row["concrete_diagram_reading_de"],
        })

    card_counter = Counter()
    prose_counter = Counter()
    astro_counter = Counter()
    for row in selected_cards:
        card_counter.update(str(row["relation_stems"]).split("|"))
    for row in prose_rows:
        prose_counter.update(str(row["relation_stems"]).split("|"))
    for row in astro_rows:
        astro_counter.update(str(row["relation_stems"]).split("|"))
    stem_rows = []
    for stem, (short, gloss) in STEM_VALUE.items():
        stem_rows.append({
            "stem": stem, "short_value_de": short, "teaching_gloss_de": gloss,
            "card_type_count": card_counter[stem], "prose_event_count": prose_counter[stem],
            "astro_group_count": astro_counter[stem],
            "minimal_workshop_rule": f"Wenn {stem} sichtbar als lizenzierter Bestandteil erscheint, füge `{short}` hinzu; der Rest der Karte bestimmt Sache und Handlung.",
        })

    stems_path = OUT / "TWO_HUNDRED_FIFTY_FOURTH_SIX_RELATION_STEMS.tsv"
    cards_path = OUT / "TWO_HUNDRED_FIFTY_FOURTH_102_RELATION_CARDS.tsv"
    prose_path = OUT / "TWO_HUNDRED_FIFTY_FOURTH_219_PROSE_OCCURRENCES.tsv"
    astro_path = OUT / "TWO_HUNDRED_FIFTY_FOURTH_67_ASTRO_OCCURRENCES.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_FOURTH_READABLE_RELATION_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_FOURTH_REPORT.md"
    write_tsv(stems_path, stem_rows, list(stem_rows[0]))
    write_tsv(cards_path, selected_cards, list(selected_cards[0]))
    write_tsv(prose_path, prose_rows, list(prose_rows[0]))
    write_tsv(astro_path, astro_rows, list(astro_rows[0]))

    readable = [
        "# Die sechs Beziehungsstämme", "",
        "Der Schreiber braucht für fast jeden Arbeitsgang dieselben sechs kleinen Richtungsfragen:", "",
        "- `AR`: Woher kommt es? — von Quelle oder Vorrat.",
        "- `AL`: Wohin geht es? — an die bezeichnete Stelle.",
        "- `OL`: Was geschieht weiter? — im selben Fortgang weiter.",
        "- `OT`: Was kommt danach? — der nächste Posten oder Schritt.",
        "- `OR`: Woran wird gearbeitet? — am laufenden Ansatz oder Bedingungssatz.",
        "- `Y`: Was ist gerade gemeint? — dies, der aktuelle Posten.", "",
        "## Werkstattlesung", "",
        "Eine lange Karte ist damit nicht ein langes deutsches Wort. Sie ist eher eine gelernte Grundkarte mit angehängter Adresse. `OK+AL+Y` heißt beispielsweise: den aktuellen Posten am Ziel ansetzen. `OT+OL` heißt: danach im selben Fortgang weiter. `OL+OR` hält den vorigen Ansatz als Bezug aktiv.", "",
        "In den Astrotafeln verlieren dieselben Stämme ihre Bade- oder Rezeptfarbe: `Y` hält den aktuellen Platz, `AL/AR` adressieren Ziel und Ausgangspunkt, `OT/OL` ordnen Nachfolge und Fortsetzung, `OR` hält einen lokalen Bedingungssatz. Das ist genau die Art von portabler Werkstattgrammatik, die mehrere Schreiber lernen können.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 254: AR/AL/OL/OT/OR/Y

## Ergebnis

Die sechs Beziehungsstämme bilden das bisher größte gemeinsame Gerüst: 102 von 173 Karten, 219 von 381 Prosaereignissen und 67 Astrogruppen tragen wenigstens einen davon. Der Inhalt bleibt in der Grundkarte; die sechs Stämme liefern Quelle, Ziel, Fortsetzung, Folge, laufenden Ansatz und aktuellen Referenten.

Das macht die Schrift wesentlich leichter lehrbar. Ein Schreiber muss nicht 102 unabhängige Langwörter lernen. Er lernt sechs Adress- und Fortgangsmarker und dazu die kürzere Liste von Stoff-, Handlungs- und Nomenklatorzeichen.

Die Bedeutungen bleiben kurz: AR=VON, AL=ZU, OL=WEITER, OT=DANACH, OR=ANSATZ, Y=DIES. Lange lokale Übersetzungen entstehen erst aus Bildbesitzer, Grundkarte und diesen kleinen Beiträgen.

Input dictionary `{sha(CARDS)}`; prose `{sha(EVENTS)}`; Astro `{sha(ASTRO)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (stems_path, cards_path, prose_path, astro_path, readable_path, report_path)
    summary = {
        "status": "PASS", "relation_stems": 6, "card_types": len(selected_cards),
        "prose_occurrences": len(prose_rows), "astro_occurrences": len(astro_rows),
        "per_stem_cards": dict(card_counter), "per_stem_prose": dict(prose_counter),
        "per_stem_astro": dict(astro_counter), "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
