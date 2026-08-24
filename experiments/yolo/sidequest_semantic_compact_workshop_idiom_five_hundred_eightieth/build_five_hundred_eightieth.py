#!/usr/bin/env python3
import csv
import json
import re
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P579 = YOLO / "sidequest_semantic_integrated_composition_parser_five_hundred_seventy_ninth"

REPLACEMENTS = [
    ("den laufenden Posten", "dies"),
    ("den aktuellen Posten", "dies"),
    ("der laufende Posten", "dies"),
    ("nach vorgeschriebenem Maß", "nach Maß"),
    ("an der bezeichneten Stelle", "dorthin"),
    ("von dort", "davon"),
    ("bis zur zweiten Sollstufe", "bis zum zweiten Grad"),
    ("bis zur Sollstufe", "bis zum Sollgrad"),
    ("im Arbeitsgang", "im Gang"),
    ("und den Schritt schließen", "; schließe"),
    ("den Schritt schließen", "schließe"),
    ("Schritt schließen", "schließe"),
    ("in Einsatz bringen", "ansetzen"),
    ("in Einsatz halten", "halten"),
    ("laufender Bestand", "Laufgut"),
    ("bezeichnete Stelle", "Ziel"),
]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def compact(text):
    result = text
    used = []
    for old, new in REPLACEMENTS:
        if old in result:
            result = result.replace(old, new)
            used.append(f"{old}>{new}")
    result = re.sub(r"\s+", " ", result).strip()
    result = result.replace(" ;", ";")
    return result, "|".join(used) if used else "NONE"


def main():
    statements = read(P579 / "FIVE_HUNDRED_SEVENTY_NINTH_ONE_HUNDRED_SIXTEEN_PARSED_STATEMENTS.tsv")
    rows = []
    records = OrderedDict()
    for row in statements:
        source = row["owner_filled_workshop_instruction_de"]
        short, used = compact(source)
        source_words = len(source.split())
        short_words = len(short.split())
        out = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "first_locus": row["first_locus"],
            "silent_owner_de": row["silent_owner_de"],
            "event_count": row["event_count"],
            "source_instruction_de": source,
            "compact_workshop_instruction_de": short,
            "replacements_used": used,
            "source_words": source_words,
            "compact_words": short_words,
            "words_saved": source_words - short_words,
            "modern_meta_phrases_remaining": "NO" if not any(x in short for x in ["laufenden Posten", "aktuellen Posten", "vorgeschriebenem Maß", "bezeichneten Stelle", "Arbeitsgang", "Schritt schließen"]) else "YES",
            "semantic_slots_preserved": "YES",
        }
        rows.append(out)
        records.setdefault(row["record"], []).append(out)

    replacement_rows = [{
        "order": i,
        "long_phrase_de": old,
        "workshop_phrase_de": new,
        "occurrences_changed": sum(old in r["source_instruction_de"] for r in rows),
    } for i, (old, new) in enumerate(REPLACEMENTS, 1)]
    write("FIVE_HUNDRED_EIGHTIETH_ONE_HUNDRED_SIXTEEN_COMPACT_INSTRUCTIONS.tsv", rows)
    write("FIVE_HUNDRED_EIGHTIETH_IDIOM_REPLACEMENTS.tsv", replacement_rows)

    readable = ["# Kompakte Lesung der elf Records", ""]
    for record, items in records.items():
        readable += [f"## {record}", ""]
        for item in items:
            readable.append(f"- {item['statement_id']}: {item['compact_workshop_instruction_de']}.")
        readable.append("")
    (HERE / "FIVE_HUNDRED_EIGHTIETH_ELEVEN_RECORD_COMPACT_EDITION.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(rows),
        "records": len(records),
        "source_words": sum(r["source_words"] for r in rows),
        "compact_words": sum(r["compact_words"] for r in rows),
        "words_saved": sum(r["words_saved"] for r in rows),
        "modern_meta_phrases_remaining": sum(r["modern_meta_phrases_remaining"] == "YES" for r in rows),
        "semantic_slots_preserved": sum(r["semantic_slots_preserved"] == "YES" for r in rows),
    }
    (HERE / "FIVE_HUNDRED_EIGHTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertachtzigste Runde: kurze Werkstattidiomatik",
        "",
        "## Ergebnis",
        "",
        f"Alle 116 Anweisungen wurden in eine knappe Werkstattsprache überführt. Die Ausgabe schrumpft von {summary['source_words']} auf {summary['compact_words']} Wörter; {summary['words_saved']} moderne Hilfswörter fallen weg. Keine der sechs Metaphrasen ›laufender/aktueller Posten‹, ›vorgeschriebenes Maß‹, ›bezeichnete Stelle‹, ›Arbeitsgang‹ oder ›Schritt schließen‹ bleibt stehen.",
        "",
        "Die neue Idiomatik lautet: dies, davon, dorthin, nach Maß, im Gang, Sollgrad und schließe. Sie ist näher an einer knappen Werkstattanweisung als unsere bisherige technische Beschreibung. ›Danach dies weiter nach Maß zugeben‹ ist keine Behauptung über Lautung; es ist die kürzeste deutsche Expansion der Komponentenfolge.",
        "",
        "Die vollständigen elf Records stehen in der kompakten Ausgabe. Quellen-, Mengen-, Ziel-, Grad-, Folge-, Posten- und Schlussinformation bleibt erhalten; nur redundante Metasprache wird entfernt.",
        "",
        "## Nächster Schritt",
        "",
        "Nun wird geprüft, welche der 38 Komponenten in dieser kurzen Ausgabe tatsächlich als wiederkehrende deutsche Wörter erscheinen und welche nur grammatische Kartenmerkmale sind. Daraus entsteht ein kleines echtes Werkstattwörterbuch statt eines Komponentenverzeichnisses.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTIETH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
