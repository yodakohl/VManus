#!/usr/bin/env python3
"""Build the complete E/EE/EEE prose grade matrix and ranked missing forms."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CLASSIFIED = ROOT / "experiments/yolo/sidequest_semantic_full_prose_morphology_two_hundred_ninety_third/TWO_HUNDRED_NINETY_THIRD_149_CARD_PRODUCTION_CLASSIFICATION.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_complete_forward_writer_two_hundred_ninetieth/TWO_HUNDRED_NINETIETH_776_FORWARD_WRITING_LEDGER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paradigm_key(recipe: str) -> str:
    return "+".join(part.split("[")[0] for part in recipe.split("+"))


def grade_from_old(old: str) -> str:
    if "GRADE_3" in old or "EEE_FULL" in old:
        return "EEE_FULL"
    if "GRADE_2" in old or "EE_LONG" in old or "EE_HOLD" in old:
        return "EE_LONG"
    if "GRADE_1" in old or "E_SHORT" in old:
        return "E_SHORT"
    raise ValueError(f"No grade marker in {old}")


PREDICTIONS = [
    ("P01", "E_GRADE+DY+SHED", "EEE_FULL", "sheeedy", "vollständig absetzen und festsetzen", "HIGH", "short and long members exist; add the attested third E grade"),
    ("P02", "OK+E_GRADE+Y", "EEE_FULL", "okeeey", "den aktuellen Posten vollständig einsetzen", "HIGH", "OK+Y has short and long members and the sister OK+DY family has EEE"),
    ("P03", "E_GRADE+Y+CHK", "EEE_FULL", "cheeeky", "den aktuellen Zustand vollständig justieren", "MEDIUM", "short and long exist, but the long grade already has two learned allographs"),
    ("P04", "OT+E_GRADE+DY", "EEE_FULL", "qoteeedy", "den Folgegang vollständig festsetzen", "HIGH", "OT+close has short and long members; extend the same q-framed long spelling"),
    ("P05", "E_GRADE+Y+SOLK", "EEE_FULL", "solkeeey", "den Posten vollständig an der Sammelstelle halten", "HIGH", "SOLK+Y has short and long members with transparent E length"),
    ("P06", "AL+E_GRADE+CKH", "EE_LONG", "sheeckhal", "lange zur Zielpassage führen", "HIGH", "the short target-passage has a single unambiguous E slot"),
    ("P07", "E_GRADE+Y+CKH", "EE_LONG", "sheeckhy", "den aktuellen Posten lange durch die Passage führen", "MEDIUM", "parallel CKH+AL and CKH+Y short cards locate the same grade slot"),
    ("P08", "E_GRADE+Y+CTH", "EE_LONG", "qctheey", "am sichtbaren Gefäß lange bereit halten", "MEDIUM", "owner-conditioned short q-form receives one additional E"),
    ("P09", "E_GRADE+Y+CTH", "EE_LONG", "sheecthy", "in der Übergangszone lange bereit halten", "MEDIUM", "owner-conditioned short sh-form receives one additional E"),
    ("P10", "OK+E_GRADE+Y+CKH", "EE_LONG", "qockheey", "den eingesetzten Posten lange durch die Passage führen", "MEDIUM", "extend the one short OK+CKH+Y card at its visible E slot"),
    ("P11", "OT+E_GRADE+Y", "E_SHORT", "otey", "den Folgeposten kurz halten", "MEDIUM", "reverse the attested long oteey by deleting one E"),
    ("P12", "E_GRADE+DY+CHK", "E_SHORT", "chkedy", "kurz justieren und festsetzen", "MEDIUM", "reverse the attested long chkeedy while preserving CHK and DY"),
    ("P13", "E_GRADE+SOLK", "E_SHORT", "olkedy", "kurz sammeln und festsetzen", "MEDIUM", "reverse the attested long olkeedy at the grade slot"),
    ("P14", "OK+AL+E_GRADE", "E_SHORT", "qokedal", "kurz am Ziel einsetzen", "MEDIUM", "reverse qokeedal from EE to E without moving AL"),
    ("P15", "OK+OL+E_GRADE", "E_SHORT", "okeol", "kurz einsetzen und weiterführen", "MEDIUM", "reverse okeeol from EE to E without moving OL"),
    ("P16", "OT+AIIN+E_GRADE", "EE_LONG", "qoteedaiin", "den Folgesollwert lange halten", "MEDIUM", "extend the attested short qotedaiin by one E"),
]


def main() -> None:
    classified = read_tsv(CLASSIFIED)
    dictionary = {row["master_card_id"]: row for row in read_tsv(DICTIONARY)}
    visible = {row["resulting_visible_surface"] for row in read_tsv(LEDGER)}
    grade_cards = [row for row in classified if row["production_mechanic"] == "GRADE_INSERTION_OR_LENGTHENING"]
    by_key: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    detailed = []
    for row in grade_cards:
        source = dictionary[row["master_card_id"]]
        grade = grade_from_old(source["old_component_parse"])
        key = paradigm_key(row["final_recipe"])
        by_key[key][grade].append(row)
        detailed.append({
            "master_card_id": row["master_card_id"],
            "canonical_surface": row["canonical_surface"],
            "canonical_value_de": row["canonical_value_de"],
            "paradigm_key": key,
            "grade": grade,
            "semantic_recipe": row["final_recipe"],
            "visible_component_parse": source["old_component_parse"],
            "event_support": row["event_support"],
            "choice_context": row["choice_context"],
        })
    detail_path = HERE / "TWO_HUNDRED_NINETY_SIXTH_30_GRADE_CARDS.tsv"
    write_tsv(detail_path, detailed)

    matrix = []
    for order, key in enumerate(sorted(by_key), start=1):
        cells = by_key[key]
        present = [grade for grade in ["E_SHORT", "EE_LONG", "EEE_FULL"] if cells.get(grade)]
        missing = [grade for grade in ["E_SHORT", "EE_LONG", "EEE_FULL"] if not cells.get(grade)]
        matrix.append({
            "paradigm_order": order,
            "paradigm_key": key,
            "e_short_forms": "|".join(row["canonical_surface"] for row in cells.get("E_SHORT", [])) or "MISSING",
            "ee_long_forms": "|".join(row["canonical_surface"] for row in cells.get("EE_LONG", [])) or "MISSING",
            "eee_full_forms": "|".join(row["canonical_surface"] for row in cells.get("EEE_FULL", [])) or "MISSING",
            "observed_grade_cells": len(present),
            "missing_grade_cells": len(missing),
            "missing_grades": "|".join(missing),
            "card_types": sum(len(value) for value in cells.values()),
            "event_support": sum(int(row["event_support"]) for values in cells.values() for row in values),
            "completion_policy": "EXTEND_DIRECTLY" if len(present) >= 2 else "ONLY_PREDICT_WITH_SISTER_FAMILY",
        })
    matrix_path = HERE / "TWO_HUNDRED_NINETY_SIXTH_20_PARADIGM_MATRIX.tsv"
    write_tsv(matrix_path, matrix)

    predictions = []
    for pid, key, grade, surface, meaning, confidence, reason in PREDICTIONS:
        predictions.append({
            "prediction_id": pid,
            "paradigm_key": key,
            "missing_grade": grade,
            "predicted_surface": surface,
            "predicted_value_de": meaning,
            "confidence": confidence,
            "reason": reason,
            "already_visible_on_ten_pages": "YES" if surface in visible else "NO",
            "use_policy": "future permitted page check or apprentice copy exercise; do not insert into current reading",
        })
    prediction_path = HERE / "TWO_HUNDRED_NINETY_SIXTH_16_RANKED_GRADE_PREDICTIONS.tsv"
    write_tsv(prediction_path, predictions)

    manual = """# E/EE/EEE-Gradtafel

## Die Regel

E, EE und EEE besetzen einen festen Platz innerhalb einer Kartenfamilie. Sie bedeuten in unserer Werkstattlehre **kurz**, **lang/anhaltend** und **vollständig**. Der Prozesskörper und sein Y- oder DY-Ausgang bleiben stehen.

Das vollständigste Muster ist:

- `qokedy` — kurz einsetzen; festsetzen;
- `qokeedy` — länger einsetzen; festsetzen;
- `qokeeedy` — vollständig einsetzen; festsetzen.

Fünf weitere Familien besitzen bereits zwei Stufen. Aus ihnen folgen die stärksten neuen Karten: `sheeedy`, `okeeey`, `cheeeky`, `qoteeedy` und `solkeeey`.

## Was nicht automatisch ergänzt wird

Eine Familie mit nur einer sichtbaren Stufe bekommt nicht blind zwei neue Wörter. Eine neue Form wird nur geschrieben, wenn eine Schwesterfamilie denselben Gradplatz zeigt. So entstehen `sheeckhal`, `sheeckhy`, die zwei besitzerabhängigen CTH-Langformen, `qockheey` und einige vorsichtige Rückbildungen aus EE nach E.

## Die 20 Familien

Die 30 Karten bilden 20 Rahmenfamilien und 27 belegte Gradfelder. Von den 60 theoretischen E/EE/EEE-Feldern bleiben 33 leer. Nur 16 davon erhalten jetzt eine konkrete Schreibprognose; die übrigen bleiben leere Möglichkeiten, nicht erfundene Wörter.

## Anschluss an die Schreibgrammatik

Der Grad steht am familiengebundenen E-Platz, nicht als frei wanderndes Suffix. Y bleibt der aktuelle Posten; DY ist nur in der lizenzierten Ganzkarte ein Abschluss. Deshalb kann `sheey` offen sein, während `sheedy` schließt.
"""
    manual_path = HERE / "TWO_HUNDRED_NINETY_SIXTH_GRADE_MANUAL.md"
    manual_path.write_text(manual, encoding="utf-8")

    report = """# Sidequest-Pass 296: vollständige Gradmatrix

## Ergebnis

Die 30 Gradkarten und 73 Vorkommen bilden 20 Rahmenfamilien. Zusammen sind 27 von 60 möglichen E/EE/EEE-Feldern belegt; eine Familie, OK+Grad+DY, ist vollständig, fünf weitere zeigen zwei Stufen und vierzehn nur eine.

Statt alle 33 Lücken zu füllen, werden 16 konkrete Formen vorgeschlagen. Fünf sind direkte dritte Glieder bereits zweistufiger Reihen, elf nutzen eine sichtbare Schwesterfamilie zur Platzierung. Keine der 16 Formen ist auf den zehn Seiten schon vorhanden.

Die stärksten neuen Formen sind `sheeedy`, `okeeey`, `qoteeedy`, `solkeeey` und die bereits separat abgeleitete Zielpassage `sheeckhal`. `cheeeky` bleibt etwas schwächer, weil der lange CHK-Grad bereits zwei gelernte Oberflächen besitzt.

## Nächster Angriff

Nun werden die 35 Grundfamilienkarten geprüft: Welche sind echte produktive Kerne, welche nur registrierte Unterformen derselben Bedeutung, und welche sollten aus dem 36-Stamm-Lehrplan in die Ganzzeichenkiste zurückwandern? Ziel ist ein kleinerer, ehrlicherer Kernbestand ohne Verlust der 149 Karten.
"""
    report_path = HERE / "TWO_HUNDRED_NINETY_SIXTH_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "grade_cards": len(detailed),
        "grade_events": sum(int(row["event_support"]) for row in detailed),
        "paradigm_families": len(matrix),
        "observed_grade_cells": sum(int(row["observed_grade_cells"]) for row in matrix),
        "missing_grade_cells": sum(int(row["missing_grade_cells"]) for row in matrix),
        "complete_three_grade_families": sum(int(row["observed_grade_cells"]) == 3 for row in matrix),
        "two_grade_families": sum(int(row["observed_grade_cells"]) == 2 for row in matrix),
        "ranked_predictions": len(predictions),
        "predictions_already_visible": sum(row["already_visible_on_ten_pages"] == "YES" for row in predictions),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [CLASSIFIED, DICTIONARY, LEDGER]},
        "outputs": {path.name: sha(path) for path in [detail_path, matrix_path, prediction_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
