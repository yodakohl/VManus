#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_readable_layered_ten_pages_two_hundred_seventeenth"
STATEMENTS = SOURCE / "TWO_HUNDRED_SEVENTEENTH_116_LAYERED_STATEMENTS.tsv"

# These are editorial repairs, not new card meanings.  Each replacement keeps
# the order and vocabulary of the bracketed card reading while removing an
# unnecessary owner noun, discourse bridge, or over-specific wet expansion.
REPAIRS = {
    "B3-S021": ("DISCOURSE_SCAFFOLD", "Posten; zweiter Zustand; aktueller Posten", "Bemessen, bereitstellen und dorthin bringen; Sollwert am Ziel absetzen, kurz vorbereiten, dorthin bringen, bereitstellen und ans Ziel übertragen; Schluss."),
    "B2-S012": ("LOCAL_MEDIUM_OVEREXPANSION", "klarer Auszug; aktueller Posten", "Abführgut auf Freigabewert kurz vorbereiten, länger einwirken, klar abziehen, auf Sollwert bringen und vollständig einsetzen; Schluss."),
    "B3-S026": ("COMPOUND_NOUN_INFLATION", "Sollabsetzstand; Bereitschaft prüfen", "Von der Quelle übertragen, auf Sollwert absetzen, überführen, Anteil zugeben, bereitstellen, am Ziel vorbereiten und länger sammeln; Schluss."),
    "B2-S011": ("VISIBLE_OWNER_REPETITION", "mittlere rechte Station; weiterer Anteil nehmen", "Anteil zugeben, davon Anteil zugeben und länger einwirken; Schluss."),
    "H1-S001": ("OWNER_AND_MEDIUM_INSERTION", "Bildpflanze; Flüssigkeit", "Wurzel nehmen, Teil im Aufnahmegefäß vorbereiten, zugießen, Folgeteil einsetzen, auf Sollwert bringen und kleinen Rest belassen."),
    "B6-S001": ("VISIBLE_OWNER_REPETITION", "rechter Endposten; aktueller Posten", "Länger sammeln, kurz bearbeiten, zum Endposten weiterführen, auf Sollwert bringen und die Einlage zum Endziel führen."),
    "B2-S016": ("DISCOURSE_SCAFFOLD", "Quelle als neues Nomen; lange Folge als Objekt", "Dorthin führen, davon abführen, teilen, auf Sollwert bringen, die Folge bemessen, kurz einwirken und zuführen; Schluss."),
    "B2-S005": ("LAYOUT_AS_SEMANTICS", "am Zeilenübergang einmal", "Am Ziel einsetzen, bis zum Soll sammeln, durchleiten, zweimal bemessen, die Fortsetzung vorbereiten, länger wärmen und abziehen; Schluss."),
    "B4-S011": ("VISIBLE_OWNER_REPETITION", "linke Unterlaufstation", "Sollwert kurz wärmen, länger weiterführen, Anteil zugeben, überführen, fortsetzen und kurz abziehen; Schluss."),
    "B5-S003": ("DISCOURSE_SCAFFOLD", "zweiter moderner Teilsatz", "Am Ziel absetzen, dorthin bringen, weiterführen und weiter abziehen; Zieltransfer auf Sollwert bringen, bis zur Endstufe fortsetzen und überführen."),
    "H3-S001": ("LOCAL_RESULT_OVEREXPANSION", "Klarlauf statt portablem Freigabewert", "Kochgut zum Sud ansetzen, auswringen, Stehzeit abwarten, nachseihen, Freigabewert abnehmen und kalt stellen; Schluss."),
    "B3-S034": ("VERBAL_PADDING", "auf bereit stellen; nehmen", "Arbeitsstufe bereitstellen, Teil und Folgemaß am Zwischenziel kurz absetzen; Schluss."),
    "H4-S001": ("UNLICENSED_OBJECT_NOUN", "Ansatz", "Bemessen, auf Sollwert in erste und zweite Portion teilen und abkühlen lassen; Schluss."),
    "H5-S001": ("VERBAL_PADDING", "herstellen; bringen", "Zugabeansatz, weitere Zutat als Zielzugabe auf Sollwert, Folgeansatz weiterbearbeiten, einsetzen und dorthin führen."),
    "B4-S003": ("REFERENT_REPETITION", "nächster Posten", "Überführen, danach das Nächste dorthin bringen, länger einwirken, einsetzen, weiterführen und kurz absetzen; Schluss."),
    "B4-S015": ("LOCAL_RESULT_OVEREXPANSION", "Klarlauf statt portablem Freigabewert", "Anteil zum Freigabewert geben, Portion durch die Zielpassage führen, kurz sammeln und abführen; Schluss."),
    "B3-S032": ("VERBAL_PADDING", "einstellen; dann", "Anteil übertragen, überführen, Kurzsoll und Folgemaß setzen, kurz weiterführen; Schluss."),
    "B2-S004": ("DUPLICATE_PATH_NOUN", "Abführpassage plus abführen", "Am Ziel einsetzen, durchleiten, abführen, länger einwirken und getrennt abziehen; Schluss."),
    "H3-S004": ("REFERENT_REPETITION", "Posten dreimal", "Zum Nächsten wechseln, weiter einsetzen, Bereitschaft prüfen und dies halten."),
    "B4-S016": ("UNLICENSED_SOURCE_NOUN", "Quelle", "Weiteren Anteil dorthin bringen, davon ausgießen und kurz absetzen; Schluss."),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def words(value: str) -> int:
    return len(re.findall(r"[A-Za-zÄÖÜäöüß]+", value))


def main() -> None:
    source = read(STATEMENTS)
    revised: list[dict[str, object]] = []
    debt: list[dict[str, object]] = []
    for row in source:
        old = row["fluent_owner_expansion_de"]
        new = old
        status = "UNCHANGED"
        if row["statement_id"] in REPAIRS:
            category, excess, new = REPAIRS[row["statement_id"]]
            status = "TIGHTENED"
            debt.append({
                "debt_rank": 0,
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "visible_owner": row["visible_owner"],
                "visible_sequence": row["visible_sequence"],
                "layered_card_reading": row["layered_card_reading"],
                "debt_category": category,
                "excess_or_overloaded_words": excess,
                "old_owner_expansion_de": old,
                "tightened_owner_expansion_de": new,
                "old_word_count": words(old),
                "new_word_count": words(new),
                "words_removed": words(old) - words(new),
                "event_count": row["event_count"],
            })
        revised.append({
            **row,
            "r218_editorial_status": status,
            "r218_owner_expansion_de": new,
        })

    debt.sort(key=lambda row: (-int(row["words_removed"]), -int(row["old_word_count"]), str(row["statement_id"])))
    for index, row in enumerate(debt, 1):
        row["debt_rank"] = index
    write(OUT / "TWO_HUNDRED_EIGHTEENTH_TOP20_SEMANTIC_DEBT.tsv", debt)
    write(OUT / "TWO_HUNDRED_EIGHTEENTH_116_TIGHTENED_STATEMENTS.tsv", revised)

    lines = [
        "# Kartennahe Ausgabe nach dem Bedeutungs-Schuldenschnitt",
        "",
        "Nur zwanzig Besitzerlesungen wurden gekürzt. Die Klammerlesung und jede Karte bleiben unverändert.",
        "",
    ]
    order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    for unit in order:
        rows = [row for row in revised if row["record_unit_id"] == unit]
        lines.extend([f"## {unit} — {rows[0]['visible_owner']}", ""])
        for row in rows:
            marker = "GESCHÄRFT" if row["r218_editorial_status"] == "TIGHTENED" else "BEIBEHALTEN"
            lines.extend([
                f"- **{row['statement_id']} · {marker}** `{row['visible_sequence']}`",
                f"  - Karten: {row['layered_card_reading']}",
                f"  - Lesung: {row['r218_owner_expansion_de']}",
            ])
        lines.append("")
    (OUT / "TWO_HUNDRED_EIGHTEENTH_TIGHTENED_PROSE_EDITION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "statements": len(revised),
        "events": sum(int(row["event_count"]) for row in revised),
        "tightened": len(debt),
        "unchanged": sum(row["r218_editorial_status"] == "UNCHANGED" for row in revised),
        "old_words_top20": sum(int(row["old_word_count"]) for row in debt),
        "new_words_top20": sum(int(row["new_word_count"]) for row in debt),
        "words_removed": sum(int(row["words_removed"]) for row in debt),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
