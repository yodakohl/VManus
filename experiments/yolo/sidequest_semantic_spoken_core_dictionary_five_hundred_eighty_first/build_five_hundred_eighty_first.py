#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P554 = YOLO / "sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"
P579 = YOLO / "sidequest_semantic_integrated_composition_parser_five_hundred_seventy_ninth"
P580 = YOLO / "sidequest_semantic_compact_workshop_idiom_five_hundred_eightieth"

SPEECH = {
    "AIIN": ("ADDRESS_OR_CONTENT", "Maß"), "AIN": ("ADDRESS_OR_CONTENT", "Teil"),
    "AIR": ("ADDRESS_OR_CONTENT", "Lauf"), "AL": ("ADDRESS_OR_CONTENT", "dorthin"),
    "AR": ("ADDRESS_OR_CONTENT", "davon"), "CFH": ("ACTION", "wringe aus"),
    "CH": ("ACTION", "ziehe ab"), "CHD": ("ACTION", "setze um"),
    "CHK": ("ACTION", "wärme"), "CKH": ("ADDRESS_OR_CONTENT", "Durchlass"),
    "CTH": ("ADDRESS_OR_CONTENT", "bereit"), "DA": ("GRAMMAR_SIGNAL", "zweiter"),
    "DY": ("GRAMMAR_SIGNAL", "schließe"), "E": ("GRAMMAR_SIGNAL", "kurz"),
    "EE": ("GRAMMAR_SIGNAL", "länger"), "EEE": ("GRAMMAR_SIGNAL", "voll"),
    "HO": ("ADDRESS_OR_CONTENT", "Gabe"), "IIN": ("ADDRESS_OR_CONTENT", "Grad"),
    "K": ("ACTION", "gib zu"), "L": ("ACTION", "führe"),
    "LD": ("ACTION", "binde fest"), "LS": ("GRAMMAR_SIGNAL", "weiter"),
    "LSH": ("ACTION", "wasche"), "O": ("ADDRESS_OR_CONTENT", "Gang"),
    "OK": ("ACTION", "setze an"), "OL": ("GRAMMAR_SIGNAL", "fort"),
    "OR": ("ADDRESS_OR_CONTENT", "Ansatz"), "OS": ("ADDRESS_OR_CONTENT", "Fach"),
    "OT": ("GRAMMAR_SIGNAL", "danach"), "P": ("ACTION", "gib hinein"),
    "R": ("ACTION", "kühle"), "S": ("ACTION", "teile"),
    "SH": ("ACTION", "halte"), "SHED": ("ACTION", "setze ab"),
    "SOLK": ("ACTION", "fange auf"), "T": ("ACTION", "trage ein"),
    "TALAM": ("ACTION", "verwahre"), "Y": ("GRAMMAR_SIGNAL", "dies"),
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    source_components = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    events = read(P579 / "FIVE_HUNDRED_SEVENTY_NINTH_THREE_HUNDRED_EIGHTY_ONE_PARSED_EVENTS.tsv")
    compact = {r["statement_id"]: r for r in read(P580 / "FIVE_HUNDRED_EIGHTIETH_ONE_HUNDRED_SIXTEEN_COMPACT_INSTRUCTIONS.tsv")}
    specialist = {"CFH", "DA", "LD", "LS", "OS", "S", "TALAM"}

    dictionary = []
    for row in source_components:
        cls, spoken = SPEECH[row["component"]]
        dictionary.append({
            "component": row["component"],
            "workshop_class": cls,
            "short_spoken_value_de": spoken,
            "expanded_meaning_de": row["atomic_meaning_de"],
            "grammar_contribution_de": row["grammar_contribution_de"],
            "card_types": row["card_types"],
            "events": row["events"],
            "learning_status": "RARE_SPECIALIST" if row["component"] in specialist else "RECURRENT_CORE",
            "visible_owner_spoken_here": "NO",
        })

    event_rows = []
    observed = Counter()
    for row in events:
        parts = row["component_parse"].split("+")
        for part in parts:
            observed[part] += 1
        event_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "surface": row["observed_surface"],
            "card_no": row["card_no"],
            "component_parse": row["component_parse"],
            "spoken_component_sequence_de": " · ".join(SPEECH[p][1] for p in parts),
            "compact_statement_de": compact[row["statement_id"]]["compact_workshop_instruction_de"],
            "silent_owner_de": row["silent_owner_de"],
            "owner_is_separate_from_spoken_dictionary": "YES",
            "complete": "YES",
        })

    for row in dictionary:
        row["observed_component_tokens_in_381_events"] = observed[row["component"]]
    write("FIVE_HUNDRED_EIGHTY_FIRST_THIRTY_EIGHT_SPOKEN_CORE_DICTIONARY.tsv", dictionary)
    write("FIVE_HUNDRED_EIGHTY_FIRST_THREE_HUNDRED_EIGHTY_ONE_SPOKEN_EVENT_SEQUENCES.tsv", event_rows)
    class_counts = Counter(r["workshop_class"] for r in dictionary)
    class_rows = [{"workshop_class": cls, "components": class_counts[cls], "description_de": {
        "ACTION": "kurze ausführbare Handlungswörter",
        "ADDRESS_OR_CONTENT": "Maß-, Quellen-, Ziel-, Zustands- und Sachadressen",
        "GRAMMAR_SIGNAL": "Grad-, Folge-, Deixis- und Schlusswörter",
    }[cls]} for cls in ["ACTION", "ADDRESS_OR_CONTENT", "GRAMMAR_SIGNAL"]]
    write("FIVE_HUNDRED_EIGHTY_FIRST_SPOKEN_CLASS_SUMMARY.tsv", class_rows)
    summary = {
        "status": "PASS",
        "spoken_core_entries": len(dictionary),
        "actions": class_counts["ACTION"],
        "addresses": class_counts["ADDRESS_OR_CONTENT"],
        "grammar_signals": class_counts["GRAMMAR_SIGNAL"],
        "recurrent_core": sum(r["learning_status"] == "RECURRENT_CORE" for r in dictionary),
        "rare_specialists": sum(r["learning_status"] == "RARE_SPECIALIST" for r in dictionary),
        "events": len(event_rows),
        "owner_words_in_dictionary": sum(r["visible_owner_spoken_here"] == "YES" for r in dictionary),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhunderteinundachtzigste Runde: gesprochenes Kernwörterbuch",
        "",
        "## Ergebnis",
        "",
        "Das Arbeitsregister braucht 38 kurze Sprechwerte: siebzehn Handlungen, zwölf Adress-/Sachwörter und neun Grammatiksignale. Einunddreißig gehören zum wiederkehrenden Kern; sieben sind seltene Fachwerte. Alle 381 Kartenereignisse lassen sich als Folge dieser Wörter expandieren.",
        "",
        "Der Kern lautet unter anderem: Maß, Teil, Lauf, davon, dorthin, Ansatz, Durchlass, Grad; ziehe ab, setze um, wärme, gib zu, führe, binde fest, wasche, setze an, halte, setze ab, fange auf; kurz, länger, voll, danach, fort, dies, schließe.",
        "",
        "Wichtig ist die stille Bildellipse: Pflanzenname, Becken, Figur, Gerät oder Station ist kein zusätzliches Kartenwort. Der sichtbare Besitzer füllt ›dies‹. So kann derselbe kleine Wortschatz einen Pflanzenartikel und eine Bad-/Stationsanweisung tragen.",
        "",
        "## Nächster Schritt",
        "",
        "Nun werden die 38 Werte auf echte Synonymdubletten geprüft. Besonders LS/OL, K/P, CH/CHD, AIIN/IIN und AL/OS könnten in einer Lehrsprache weiter zusammenfallen oder müssen durch feste Minimalpaare getrennt werden.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_FIRST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
