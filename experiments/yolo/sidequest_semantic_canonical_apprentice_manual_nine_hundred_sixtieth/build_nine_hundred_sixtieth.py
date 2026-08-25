#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CODEBOOK = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_122_ENTRY_CODEBOOK.tsv"
FORMULAS = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_66_TRUE_MULTICOMPONENT_FORMULAS.tsv"
VARIANTS = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_126_FORMULA_SURFACE_VARIANTS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_2511_DEDUPLICATED_THREE_LAYER_EDITION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOT_LESSON = {
    1: {"Y", "CARRIER_Q", "RESUME_CARD", "D_ADDR", "A_ADDR", "AM_ADDR", "S_ADDR", "Z_ADDR", "D_LABEL", "S_LABEL", "M_LOCAL"},
    2: {"OL", "OT", "S", "R", "DA", "LOCAL_CHAR_F", "G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_B", "LOCAL_CHAR_J", "LOCAL_CHAR_Z"},
    3: {"AIIN", "AIN", "AL", "AR", "IIN"},
    4: {"OK", "O", "CH", "CHD", "K", "T", "P", "SH", "CHK", "CTH", "SHED"},
    5: {"E", "EE", "EEE", "DY"},
    6: {"L", "AIR", "CKH", "CHEO", "OR", "SOLK", "LSH", "CPH", "CFH", "HO", "AN", "OS", "LD"},
}


LESSONS = [
    (1, "Bildbesitzer und Adresse", "Zeige erst Pflanze, Becken, Figur, Ring oder Sternort; dann setze DIES, TEIL, ORT, INNEN oder AUSSEN."),
    (2, "Reihe, Auswahl und Fortsetzung", "Lies AUSWÄHLEN, MARKIEREN, FORTSETZEN, DANACH und die kleinen lokalen Klassenzeichen."),
    (3, "Menge, Quelle und Ziel", "Binde SOLLMASS, PORTION, STUFE, QUELLE und ZIEL an den aktiven Posten."),
    (4, "Werkstatthandlungen", "Übe ANSETZEN, AUSFÜHREN, ENTNEHMEN, UMSETZEN, ZUGEBEN, HALTEN, BEHANDELN und ABSETZEN."),
    (5, "Grad und Abschluss", "KURZ, LÄNGER und VOLL verändern den Arbeitsgang; nur die lizenzierte Endkarte SCHLIESSEN beendet ihn."),
    (6, "Stoff- und Wegkarten", "Leite Ansatz und Auszug über Lauf, Durchlass und Ziel; spüle, trenne, fange auf oder befestige."),
    (7, "Häufige Ganzkarten F001–F017", "Lerne die häufigsten Karten als feste Wendungen; zerlege sie nur als Gedächtnishilfe."),
    (8, "Ganzkarten F018–F034", "Lerne Fortsetzungs-, Quellen-, Ziel- und Zustandskarten samt ihrer Rendererformen."),
    (9, "Ganzkarten F035–F050", "Lerne die mittleren Transfer-, Halte-, Spül- und Auffangkarten."),
    (10, "Ganzkarten F051–F066 und lokale Karten", "Lerne die langen Karten; kopiere Bildnamen und Sonderadressen aus dem Meisterexemplar."),
]


def root_lesson(component: str) -> int:
    for number, members in ROOT_LESSON.items():
        if component in members:
            return number
    raise KeyError(component)


def formula_lesson(formula_id: str) -> int:
    number = int(formula_id[1:])
    return 7 if number <= 17 else 8 if number <= 34 else 9 if number <= 50 else 10


def main() -> None:
    codebook = read_tsv(CODEBOOK)
    formulas = read_tsv(FORMULAS)
    variants = read_tsv(VARIANTS)
    events = read_tsv(EVENTS)
    formula_by_id = {row["formula_card_id"]: row for row in formulas}

    entries: list[dict[str, object]] = []
    for row in codebook:
        is_root = row["entry_type"] == "PRODUCTIVE_ROOT"
        lesson = root_lesson(row["recognition_form"]) if is_root else formula_lesson(row["codebook_entry_id"])
        entries.append({
            "entry_id": row["codebook_entry_id"],
            "lesson": lesson,
            "entry_type": row["entry_type"],
            "recognition_form": row["recognition_form"],
            "spoken_value_de": row["short_value_de"],
            "surface_variants": row["surface_variants"],
            "uses": row["events_or_uses"],
            "production_rule_de": "Mit Nachbarkürzeln zusammensetzen." if is_root else "Als ganze Karte aus dem Formeldeck wählen.",
            "reading_rule_de": "Kurzen Stammwert einsetzen." if is_root else "Ganze Wendung sprechen; Komponenten nur zur Wiedererkennung nutzen.",
        })
    write_tsv(OUT / "PASS960_122_ENTRY_MASTER_TABLE.tsv", entries)

    drill_rows: list[dict[str, object]] = []
    for formula_id in sorted(formula_by_id):
        family = formula_by_id[formula_id]
        members = [row for row in variants if row["formula_card_id"] == formula_id]
        members.sort(key=lambda row: (-int(row["events"]), row["surface"]))
        for rank, row in enumerate(members, 1):
            drill_rows.append({
                "formula_card_id": formula_id,
                "lesson": formula_lesson(formula_id),
                "variant_rank": rank,
                "is_primary_training_form": "YES" if rank == 1 else "NO",
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "spoken_value_de": family["workshop_formula_de"],
                "events": row["events"],
                "renderer_or_context": row["surface_role"],
                "apprentice_prompt_de": f"Erkenne {row['surface']} als {formula_id}; sprich: {family['workshop_formula_de']}.",
            })
    write_tsv(OUT / "PASS960_126_VARIANT_RECOGNITION_DRILL.tsv", drill_rows)

    lesson_rows: list[dict[str, object]] = []
    for number, title, instruction in LESSONS:
        members = [row for row in entries if int(row["lesson"]) == number]
        exercise = (
            "Meister zeigt drei Besitzer; Lehrling setzt je zwei neue Stammkombinationen und liest sie rückwärts."
            if number <= 6 else
            "Meister zeigt fünf Rendererformen; Lehrling nennt Karten-ID und kurze Wendung ohne Buchstabieren."
        )
        lesson_rows.append({
            "lesson": number,
            "title_de": title,
            "entries": len(members),
            "entry_ids": "|".join(str(row["entry_id"]) for row in members),
            "instruction_de": instruction,
            "exercise_de": exercise,
            "pass_condition_de": "Fünf fehlerfreie Hin- und Rücklesungen nacheinander.",
        })
    write_tsv(OUT / "PASS960_10_LESSON_PLAN.tsv", lesson_rows)

    counts = Counter(row["codebook_layer"] for row in events)
    manual = [
        "# Meistertafel für das 122-Einträge-System",
        "",
        "## Die Regel in sechs Sätzen",
        "",
        "1. Das Bild nennt den Stoff, Körperteil, Behälter oder Himmelsplatz.",
        "2. Der erste Kartenblock wählt Besitzer, Quelle, Menge oder Ziel.",
        "3. Der zweite Block nennt Handlung, Grad und laufenden Posten.",
        "4. Passt eine der 66 Formelkarten, wird sie als ganze Wendung gelesen.",
        "5. Sonst werden die 56 kurzen Stämme in sichtbarer Reihenfolge zusammengesetzt.",
        "6. Nur eine lizenzierte Endkarte schließt den Teilgang; der Zeilenrand tut es nicht.",
        "",
        "## Unterricht",
        "",
    ]
    for row in lesson_rows:
        manual.extend([
            f"### Lektion {row['lesson']}: {row['title_de']} ({row['entries']} Einträge)",
            "",
            str(row["instruction_de"]),
            "",
            f"Übung: {row['exercise_de']}",
            "",
        ])
    manual.extend([
        "## Was der Lehrling danach beherrscht",
        "",
        f"Er liest {counts['LEARNED_FORMULA_CARD']} Ereignisse direkt über Formelkarten, setzt {counts['PRODUCTIVE_ABBREVIATION_COMPOSITION']} Ereignisse aus Stämmen zusammen und übernimmt {counts['LOCAL_NOMENCLATOR_OR_ADDRESS']} lokale Namen oder Adressen aus Bild und Meisterexemplar.",
        "",
        "Die 126 sichtbaren Formelvarianten sind keine 126 zusätzlichen Wörter: 66 Hauptkarten besitzen zusammen 60 weitere Renderer- oder Stellungsformen.",
    ])
    (OUT / "PASS960_COMPLETE_APPRENTICE_MANUAL.md").write_text("\n".join(manual) + "\n", encoding="utf-8")

    report = f"""# Pass 960 — die bereinigte Lehrfassung

Das aktuelle System lässt sich einem Werkstattschreiber in zehn Lektionen
beibringen: **56 produktive Stämme + 66 echte Formelkarten = 122 Einträge**.
Die 66 Karten erscheinen in 126 Oberflächenformen; die übrigen 60 Formen sind
Renderer- oder Stellungsvarianten und werden nicht als zusätzliche Wörter
gezählt.

Der Lehrling beginnt immer beim Bildbesitzer, liest Adress- und Mengenblock,
erkennt danach entweder eine gelernte Ganzkarte oder setzt kurze Stämme
zusammen. Lokale Pflanzennamen, Stationsnamen und Sternadressen kopiert er aus
dem Exemplar. Das ist klein genug für mehrere Schreiber und komplex genug, um
die drei aktuellen Ereignisschichten {dict(counts)} zu erzeugen.
"""
    (OUT / "PASS960_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS960_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "entries": len(entries), "roots": 56, "formulas": 66,
        "formula_variants": len(drill_rows), "lessons": len(lesson_rows),
        "layer_counts": counts, "outputs": outputs,
    }
    (OUT / "PASS960_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
