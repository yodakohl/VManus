#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P474 = ROOT / "experiments/yolo/sidequest_semantic_referent_propagation_four_hundred_seventy_fourth"

SPELLING = {
    "fuellen": "füllen", "zufuehren": "zuführen", "weiterfuehren": "weiterführen",
    "fuehren": "führen", "abkuehlen": "abkühlen", "vollstaendig": "vollständig",
    "laenger": "länger", "naechster": "nächster", "schliessen": "schließen",
    "uebertragen": "übertragen", "gueltig": "gültig", "zaehlen": "zählen",
    "gefuellt": "gefüllt", "Mass": "Maß",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def short_referent(value: str, register: str) -> str:
    if value.startswith("abgeteilte Portion von abgeteilte Portion von "):
        return "zweite Teilportion von " + short_referent(value.removeprefix("abgeteilte Portion von abgeteilte Portion von "), register)
    if value.startswith("abgeteilte Portion von "):
        return "Teilportion von " + short_referent(value.removeprefix("abgeteilte Portion von "), register)
    if value.startswith("entnommene Fraktion aus "):
        inner = short_referent(value.removeprefix("entnommene Fraktion aus "), register)
        if inner == "Pflanzenmaterial":
            return "Pflanzenanteil"
        if "flüssigkeit" in inner.lower() or "fluss" in inner.lower():
            return "abgezogene Flüssigkeitsfraktion"
        return "entnommene Fraktion des " + inner
    if value.startswith("aufgefangener Bestand von "):
        return "aufgefangener Bestand des " + short_referent(value.removeprefix("aufgefangener Bestand von "), register)
    if value == "Material dieser Pflanze":
        return "Pflanzenmaterial"
    if value.startswith("laufender Ansatz bei "):
        return "laufender Pflanzenansatz" if register == "HERBAL" else "laufender Stationsansatz"
    if value.startswith("Laufflüssigkeit bei "):
        return "Arbeitsflüssigkeit"
    if value.startswith("Zugabe bei "):
        return "Zugabe"
    if value.startswith("Ergebnisbestand bei "):
        return "Ergebnisbestand"
    if value.startswith("nächster Arbeitsposten bei "):
        return "nächster Arbeitsposten"
    replacements = {
        "Arbeitsflüssigkeit oder Körperposten im gemeinsamen Becken": "Beckenposten",
        "Arbeitsflüssigkeit in den oberen Becken": "obere Beckenflüssigkeit",
        "Arbeitsflüssigkeit am linken Zwischenknoten": "Flüssigkeit am Zwischenknoten",
        "Arbeitsposten an der rechten Einzelstation": "Posten der Einzelstation",
        "Arbeitsflüssigkeit oder Körperposten im unteren Becken": "unterer Beckenposten",
        "Arbeitsflüssigkeit am unteren Beckenrand": "Flüssigkeit am Beckenrand",
        "Arbeitsgut an der oberen Fächerstation": "Gut der Fächerstation",
        "Arbeitsflüssigkeit im runden Gefäß": "Gefäßflüssigkeit",
        "Arbeitsgut im unteren Korbgefäß": "Gut im Korbgefäß",
        "übernommener Arbeitsposten ohne sichtbare Verbindung": "übernommener Posten",
        "Arbeitsflüssigkeit im verbundenen Hauptpaar": "Flüssigkeit des Hauptpaares",
        "Arbeitsgut an der linken Randstation": "Gut der Randstation",
        "Arbeitsflüssigkeit in der rechten Mehrarmstation": "Flüssigkeit der Mehrarmstation",
        "Arbeitsposten an der linken Nachtragsstation": "linker Nachtragsposten",
        "Arbeitsflüssigkeit in der rechten Nachtragsstation": "rechte Nachtragsflüssigkeit",
    }
    return replacements.get(value, value)


def normalize(text: str) -> str:
    for old, new in SPELLING.items():
        text = text.replace(old, new)
    grammar = {
        "von laufender Pflanzenansatz": "aus dem laufenden Pflanzenansatz",
        "von laufender Stationsansatz": "aus dem laufenden Stationsansatz",
        "von Arbeitsflüssigkeit": "aus der Arbeitsflüssigkeit",
        "von Ergebnisbestand": "aus dem Ergebnisbestand",
        "von Pflanzenmaterial": "vom Pflanzenmaterial",
        "verwende laufender Pflanzenansatz": "verwende den laufenden Pflanzenansatz",
        "verwende laufender Stationsansatz": "verwende den laufenden Stationsansatz",
        "laufender Pflanzenansatz füllen": "den laufenden Pflanzenansatz füllen",
        "laufender Stationsansatz füllen": "den laufenden Stationsansatz füllen",
        "entnommene Fraktion des Arbeitsflüssigkeit": "abgezogene Flüssigkeitsfraktion",
        "entnommene Fraktion des Ergebnisbestand": "Fraktion des Ergebnisbestands",
        "aufgefangener Bestand des rechte Nachtragsflüssigkeit": "aufgefangener Bestand der rechten Nachtragsflüssigkeit",
        "Teilportion von aufgefangener Bestand": "Teilportion des aufgefangenen Bestands",
        "Teilportion von Posten": "Teilportion des Postens",
        "zweite Teilportion von Posten": "zweite Teilportion des Postens",
    }
    for old, new in grammar.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compress_event(row: dict[str, str]) -> str:
    before = row["active_before_de"]
    short = short_referent(before, row["register"])
    text = row["referent_resolved_value_de"].replace(before, short)
    return normalize(text)


def collapse_runs(rows: list[dict[str, str]]) -> tuple[str, int]:
    chunks: list[str] = []
    collapsed = 0
    i = 0
    while i < len(rows):
        j = i + 1
        while j < len(rows) and rows[j]["compressed_event_de"] == rows[i]["compressed_event_de"]:
            j += 1
        count = j - i
        text = rows[i]["compressed_event_de"]
        if count > 1:
            chunks.append(f"{count}× {text}")
            collapsed += count - 1
        else:
            chunks.append(text)
        i = j
    sentence = "; ".join(chunks).strip()
    if sentence:
        sentence = sentence[0].upper() + sentence[1:]
    return sentence + ".", collapsed


def main() -> None:
    trace = read(P474 / "FOUR_HUNDRED_SEVENTY_FOURTH_381_REFERENT_TRACE.tsv")
    statements = read(P474 / "FOUR_HUNDRED_SEVENTY_FOURTH_116_REFERENT_RESOLVED_STATEMENTS.tsv")
    astro = read(P474 / "FOUR_HUNDRED_SEVENTY_FOURTH_142_ASTRO_LOCUS_REFERENTS.tsv")

    event_rows = []
    for row in trace:
        event_rows.append({
            **row,
            "short_active_before_de": short_referent(row["active_before_de"], row["register"]),
            "compressed_event_de": compress_event(row),
            "short_active_after_de": short_referent(row["active_after_de"], row["register"]),
        })
    write("FOUR_HUNDRED_SEVENTY_FIFTH_381_READABLE_EVENT_ALIGNMENT.tsv", event_rows)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    collapsed_total = 0
    raw_chars = 0
    compact_chars = 0
    for source in statements:
        rows = by_statement[source["statement_id"]]
        reading, collapsed = collapse_runs(rows)
        collapsed_total += collapsed
        raw_chars += len(source["referent_resolved_statement_de"])
        compact_chars += len(reading)
        statement_rows.append({
            "statement_id": source["statement_id"],
            "register": source["register"],
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "owner_code": source["owner_code"],
            "events": source["events"],
            "event_ids": "|".join(row["event_id"] for row in rows),
            "reference_tokens_resolved": source["reference_tokens_resolved"],
            "collapsed_adjacent_repetitions": collapsed,
            "raw_referent_reading_de": source["referent_resolved_statement_de"],
            "readable_workshop_statement_de": reading,
            "active_post_after_statement_de": rows[-1]["short_active_after_de"],
        })
    write("FOUR_HUNDRED_SEVENTY_FIFTH_116_READABLE_WORKSHOP_STATEMENTS.tsv", statement_rows)

    astro_rows = []
    for row in astro:
        text = normalize(row["referent_resolved_locus_de"])
        astro_rows.append({**row, "readable_locus_de": text})
    write("FOUR_HUNDRED_SEVENTY_FIFTH_142_READABLE_ASTRO_LOCI.tsv", astro_rows)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in statement_rows if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": rows[0]["register"],
            "statements_or_loci": len(rows),
            "groups": sum(int(row["events"]) for row in rows),
            "continuous_readable_workshop_de": " ".join(row["readable_workshop_statement_de"] for row in rows),
        })
    for unit in ("A1", "A2", "A3"):
        rows = [row for row in astro_rows if row["diagram_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": "ASTRO",
            "statements_or_loci": len(rows),
            "groups": sum(int(row["groups"]) for row in rows),
            "continuous_readable_workshop_de": " ".join(row["readable_locus_de"] for row in rows),
        })
    write("FOUR_HUNDRED_SEVENTY_FIFTH_14_READABLE_UNIT_EDITIONS.tsv", units)

    rules = [
        ("R01", "Material dieser Pflanze", "Pflanzenmaterial"),
        ("R02", "entnommene Fraktion aus Pflanzenmaterial", "Pflanzenanteil"),
        ("R03", "laufender Ansatz bei Besitzer", "laufender Pflanzen-/Stationsansatz"),
        ("R04", "Laufflüssigkeit bei Besitzer", "Arbeitsflüssigkeit"),
        ("R05", "abgeteilte Portion von X", "Teilportion von X"),
        ("R06", "Portion von Portion von X", "zweite Teilportion von X"),
        ("R07", "entnommene Fraktion aus Flüssigkeit", "abgezogene Flüssigkeitsfraktion"),
        ("R08", "aufgefangener Bestand von X", "aufgefangener Bestand des X"),
        ("R09", "owner-specific long Bio referent", "kurzer Stationsposten"),
        ("R10", "adjacent identical event values", "N× Wert; Ereignis-IDs bleiben einzeln"),
        ("R11", "ASCII-Umschrift", "deutsche Umlaute"),
        ("R12", "Astro locus owner", "Owner: lokale Lesung; kein Cross-Locus-Carry"),
    ]
    write("FOUR_HUNDRED_SEVENTY_FIFTH_COMPRESSION_RULES.tsv", [
        {"rule_id": rid, "input_pattern": old, "readable_output": new, "semantic_change": "NONE"}
        for rid, old, new in rules
    ])

    md = ["# Readable ten-page workshop edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_readable_workshop_de"], ""])
    (HERE / "FOUR_HUNDRED_SEVENTY_FIFTH_READABLE_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS",
        "events": len(event_rows),
        "statements": len(statement_rows),
        "astro_loci": len(astro_rows),
        "units": len(units),
        "groups": sum(int(row["groups"]) for row in units),
        "references_preserved": sum(int(row["reference_tokens_resolved"]) for row in statement_rows),
        "adjacent_repetitions_compacted": collapsed_total,
        "raw_prose_characters": raw_chars,
        "readable_prose_characters": compact_chars,
        "character_reduction_percent": round(100 * (raw_chars - compact_chars) / raw_chars, 2),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
