#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"
R123 = ROOT / "experiments/yolo/sidequest_semantic_two_register_source_grammar_hundred_twenty_third"
R124 = ROOT / "experiments/yolo/sidequest_semantic_four_hand_source_roundtrip_hundred_twenty_fourth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    deck = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_17_SHARED_CARDS.tsv")
    templates = read_tsv(R123 / "HUNDRED_TWENTY_THIRD_EIGHT_SOURCE_TEMPLATES.tsv")
    exercises = read_tsv(R123 / "HUNDRED_TWENTY_THIRD_TWELVE_SOURCE_TO_CARD_EXERCISES.tsv")
    copies = read_tsv(R124 / "HUNDRED_TWENTY_FOURTH_48_FOUR_HAND_COPIES.tsv")

    role_by_form = {
        "oldy": "SCHLUSS", "choky": "HANDLUNG+POSTEN", "cheeky": "HANDLUNG+ZUSTAND",
        "aiin": "MASS", "okal": "HANDLUNG+ZIEL", "char": "QUELLE", "chdy": "HANDLUNG+POSTEN",
        "chor": "ANSATZ", "chety": "HANDLUNG+TEIL", "cheey": "ERGEBNIS", "okaiin": "HANDLUNG+MASS",
        "chey": "POSTEN", "cheol": "FORTSETZUNG", "al": "ZIEL", "cholor": "VORIGER_ANSATZ",
        "checthy": "ZUSTAND+POSTEN", "otchey": "FOLGE+POSTEN",
    }
    card_rows = []
    for row in deck:
        card_rows.append({
            "lesson_order": row["deck_order"],
            "master_card": row["master_form"],
            "workshop_role": role_by_form[row["master_form"]],
            "short_reading_de": row["short_default_de"],
            "registered_surfaces": row["registered_surfaces"],
            "memory_hook": f"{role_by_form[row['master_form']]} -> {row['short_default_de']}",
            "copy_rule": "meaning selects card; hand selects one listed surface",
        })
    write_tsv("HUNDRED_TWENTY_FIFTH_SEVENTEEN_CARD_TEACHING_SHEET.tsv", card_rows)

    hand_by_card = defaultdict(dict)
    for row in copies:
        source_cards = row["source_master_cards"].split()
        surfaces = row["visible_copy"].split()
        for card, surface in zip(source_cards, surfaces):
            hand_by_card[card][row["renderer_id"]] = surface
    hand_rows = []
    for row in deck:
        form = row["master_form"]
        hand_rows.append({
            "master_card": form,
            "Vorlagenhand_R_A": hand_by_card[form].get("R-A", form),
            "q_Eintrittshand_R_B": hand_by_card[form].get("R-B", form),
            "s_Flusshand_R_C": hand_by_card[form].get("R-C", form),
            "Kurzhand_R_D": hand_by_card[form].get("R-D", form),
            "reverse_key": form,
        })
    write_tsv("HUNDRED_TWENTY_FIFTH_FOUR_HAND_CARD_TABLE.tsv", hand_rows)

    write_tsv("HUNDRED_TWENTY_FIFTH_EIGHT_TEMPLATE_SHEET.tsv", templates)

    copies_by_exercise = defaultdict(list)
    for row in copies:
        copies_by_exercise[row["exercise_id"]].append(row)
    answer_rows = []
    for row in exercises:
        variants = sorted({copy["visible_copy"] for copy in copies_by_exercise[row["exercise_id"]]})
        answer_rows.append({
            "exercise_id": row["exercise_id"],
            "dictated_command_de": row["ordinary_source_command_de"],
            "answer_master_cards": row["compiled_master_cards"],
            "visible_answers": " || ".join(variants),
            "observed_or_new": row["manuscript_status"],
        })
    write_tsv("HUNDRED_TWENTY_FIFTH_TWELVE_EXERCISES_AND_ANSWERS.tsv", answer_rows)

    lessons = [
        ("D1", "BILD_BESITZER", "Zuerst auf Bild, Becken, Station oder Radstelle zeigen; der Besitzer liefert das konkrete Ding."),
        ("D2", "SIEBZEHN_KARTEN_I", "Die neun häufigsten gemeinsamen Karten als ganze Lehrwerte lernen."),
        ("D3", "SIEBZEHN_KARTEN_II", "Die übrigen acht gemeinsamen Karten und ihre registrierten Oberflächen lernen."),
        ("D4", "ZWEI_REGISTER", "Herbal als Artikelkette, Biological als kurze Arbeitszelle setzen."),
        ("D5", "ZWEI_KLAMMERN", "Y-AIIN-Y und OL-(OL+OR)-OL als unteilbare Formeln kopieren."),
        ("D6", "HANDGEWOHNHEIT", "Nur die eigene Oberflächengewohnheit anwenden; Kartenwert nicht ändern."),
        ("D7", "ZEILE_UND_SCHLUSS", "Zeilenende ist Platzumbruch; nur lizenzierte Schlusskarte beendet die Zelle."),
        ("D8", "KOPIE_UND_KORREKTUR", "Zwölf Diktate schreiben, rücklesen und gegen die Vorlagenhand korrigieren."),
    ]
    lesson_rows = [{"day": day, "lesson": lesson, "master_instruction": instruction} for day, lesson, instruction in lessons]
    write_tsv("HUNDRED_TWENTY_FIFTH_EIGHT_DAY_CURRICULUM.tsv", lesson_rows)

    md = [
        "# Kleines Meisterheft der gemeinsamen Werkstattkarten", "",
        "## Seite 1: zuerst zeigen, dann schreiben", "",
        "Das Bild oder die sichtbare Station nennt den Besitzer. Die Karte nennt nur die kurze Arbeit daran.",
        "Eine Zeile ist Platz, kein Satz. Eine neue Bildstation kann den Besitzer wechseln; sonst bleibt er aktiv.", "",
        "## Seite 2: die siebzehn gemeinsamen Karten", "",
        "| Karte | Kurzer Lehrwert | Zulässige Formen |", "|---|---|---|",
    ]
    for row in card_rows:
        md.append(f"| `{row['master_card']}` | {row['short_reading_de']} | `{row['registered_surfaces']}` |")
    md += ["", "## Seite 3: zwei Arten, dieselben Karten zu ordnen", "",
           "Herbal: Handlung/Zustand -> Material -> Fortsetzung/Quelle -> Maß -> Ziel.",
           "Biological: Handlung -> Quelle/Ziel -> Fortsetzung/Zustand -> Maß -> Posten.",
           "Quelle, Maß oder Ziel dürfen als übernommene Feldrubrik vor der Handlung stehen.", "",
           "## Seite 4: zwei feste Klammern", "",
           "`chey aiin chey`: zwei Posten unter dasselbe Sollmaß stellen.",
           "`cheol cholor cheol`: den vorigen Ansatz in der Fortsetzung mitführen.", "",
           "## Seite 5: vier Hände", "",
           "Die Vorlagenhand schreibt den Kopf. Die q-Hand bevorzugt q-Eintritt, die s-Hand sh/s-Fluss,",
           "die Kurzhand die kürzeste registrierte Form. Beim Lesen wird immer zuerst zur Masterkarte zurückgekehrt.", "",
           "## Seite 6: Meisterregel", "",
           "Gemeinsame Karte aus dem Sinn wählen -> Registerfolge setzen -> Klammer prüfen -> Besitzer ergänzen ->",
           "eigene Oberfläche schreiben -> Schlusskarte nur am wirklichen Zellende -> gegen Vorlage rücklesen.", "",
           "Seltene Herbal- und Biological-Fachkarten werden nicht erraten. Sie werden aus dem Seitenexemplar kopiert.",
    ]
    (OUT / "HUNDRED_TWENTY_FIFTH_APPRENTICE_MASTER_CODEBOOK.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    report = [
        "# Hundertfünfundzwanzigste Runde: ein tatsächlich lehrbares Meisterheft", "",
        "R116-R124 sind auf acht Lektionen und sechs kurze Lehrseiten reduziert. Ein Lehrling muss nicht",
        "173 Bedeutungen produktiv zerlegen. Er lernt siebzehn gemeinsame Karten, zwei Registerfolgen, zwei",
        "Klammern, Besitzervererbung, Zellschluss und die eigene Oberflächengewohnheit. Sektionskarten werden",
        "aus dem Exemplar kopiert.", "",
        "Damit ist das Modell einfach genug für mehrere Hände: gemeinsame Semantik im kleinen Deck, lokale",
        "Fachwerte im Musterbuch und sichtbare Variation erst beim Schreiben. Das nächste kreative Problem ist",
        "inhaltlich: Welche der siebzehn deutschen Kurzwerte sind wirklich die beste Wahl, wenn man alle ihre",
        "Vorkommen als zusammenhängende Befehle liest?",
    ]
    (OUT / "HUNDRED_TWENTY_FIFTH_MASTER_CODEBOOK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "shared_cards": len(card_rows), "templates": len(templates), "hands": len(hand_rows[0]) - 2, "exercises": len(answer_rows), "lessons": len(lesson_rows), "manual_pages": 6}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
