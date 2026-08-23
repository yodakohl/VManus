#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LAYER = ROOT / "experiments/yolo/sidequest_semantic_776_layered_edition_two_hundred_sixteenth/TWO_HUNDRED_SIXTEENTH_776_LAYERED_LEDGER.tsv"
AXES = ROOT / "experiments/yolo/sidequest_semantic_scoped_apprentice_grammar_two_hundred_fifteenth/TWO_HUNDRED_FIFTEENTH_TEN_COMMON_CORE_AXES.tsv"

ORDER = ["OK", "OL", "OT", "AR", "AL", "AIIN", "Y", "DY", "OR", "CHED~CHD", "RESULT"]
META = {
    "OK": ("EINSETZEN", "Handlungsverb", "setzt den folgenden Posten oder Arbeitsgang aktiv ein", "kein Stoffname und nicht jede sichtbare o/k-Folge"),
    "OL": ("WEITER", "Fortsetzungspartikel", "behält Ansatz, Weg oder Diagrammreihe bei", "lokal auch Teil längerer Ganzkarten"),
    "OT": ("FOLGE", "Reihenfolgepartikel", "wechselt zum folgenden Posten oder Platz", "kein festes Zeitwort wie morgen"),
    "AR": ("VON", "Quellrelation", "nimmt den Bezug vom aktiven Ausgang", "nennt die Quelle nicht selbst"),
    "AL": ("ZIEL", "Zielrelation", "weist den bezeichneten Zielplatz zu", "nennt weder Körperteil noch Gefäß"),
    "AIIN": ("SOLLWERT", "Parameterwort", "ruft einen vorgeschriebenen Wert auf", "in nasser Prosa oft Sollmaß, im Diagramm Grad oder Tabellenwert"),
    "Y": ("DIES", "Referenzwort", "hält den aktuell gemeinten Posten aktiv", "sichtbares y oder dy ist nicht automatisch diese Karte"),
    "DY": ("FERTIG", "Abschlusspartikel", "schließt nur die lizenzierte Karten- oder Zellkonstruktion", "kein global zerlegbares Suffix"),
    "OR": ("ANSATZ", "Arbeitszustandswort", "bezeichnet den laufenden Ansatz oder Bedingungssatz", "nicht automatisch Flüssigkeit oder Sud"),
    "CHED~CHD": ("ÜBERFÜHREN", "Transferverb", "setzt einen Posten zwischen Arbeits- oder Diagrammplätzen um", "Schreibgestalt und Schluss bleiben kartengebunden"),
    "RESULT": ("FREIGABEWERT", "gelernte Resultatkarte", "meldet den ablesbaren oder freigegebenen Endwert", "CHEEY/SHEY ist eine Ganzkarte; EY ist kein freier Stamm"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def compact(counter: Counter[str], limit: int = 8) -> str:
    return " | ".join(f"{value} ({count})" for value, count in counter.most_common(limit))


def main() -> None:
    ledger = read(LAYER)
    axes = {row["axis"]: row for row in read(AXES)}
    portable = [row for row in ledger if row["primary_layer"] in {"COMMON_PORTABLE_CARD", "COMMON_PORTABLE_SURFACE"}]
    prose_all = [row for row in ledger if row["source_kind"] == "PROSE_EVENT"]

    membership_by_card: dict[str, set[str]] = defaultdict(set)
    for row in prose_all:
        if row["portable_core_value_de"] == "Freigabewert":
            membership_by_card[row["normalized_id"]].add("RESULT")
        for axis in row["component_axes"].split("+"):
            if axis in ORDER:
                membership_by_card[row["normalized_id"]].add(axis)

    occurrence_rows: list[dict[str, object]] = []
    grouped_prose: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prose_all:
        memberships = set(membership_by_card.get(row["normalized_id"], set()))
        if row["portable_core_value_de"] == "Freigabewert":
            memberships.add("RESULT")
        for entry in memberships:
            grouped_prose[entry].append(row)

    grouped_astro: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in portable:
        memberships = set(membership_by_card.get(row["normalized_id"], set()))
        if row["portable_core_value_de"] == "Freigabewert":
            memberships.add("RESULT")
        if not memberships:
            raise ValueError(f"portable row without entry: {row['source_id']} {row['normalized_id']}")
        if row["source_kind"] == "ASTRO_GROUP":
            for entry in memberships:
                grouped_astro[entry].append(row)
        occurrence_rows.append({
            "unified_serial": row["unified_serial"],
            "source_kind": row["source_kind"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "locus_or_field": row["locus_or_field"],
            "source_id": row["source_id"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "normalized_id": row["normalized_id"],
            "dictionary_entries": "+".join(sorted(memberships, key=ORDER.index)),
            "portable_core_value_de": row["portable_core_value_de"],
            "local_expansion_de": row["local_expansion_de"],
        })
    write(OUT / "TWO_HUNDRED_NINETEENTH_182_PORTABLE_OCCURRENCES.tsv", occurrence_rows)

    entry_rows: list[dict[str, object]] = []
    for index, key in enumerate(ORDER, 1):
        prose = grouped_prose[key]
        astro = grouped_astro[key]
        rows = prose + astro
        headword, word_class, rule, boundary = META[key]
        local_prose = Counter(row["local_expansion_de"] for row in prose)
        astro_core = Counter(row["portable_core_value_de"] for row in astro)
        entry_rows.append({
            "entry_order": index,
            "entry_key": key,
            "headword_de": headword,
            "word_class": word_class,
            "composition_rule_de": rule,
            "hard_boundary_de": boundary,
            "productive_card_types_registered": axes[key]["productive_card_types"] if key in axes else 1,
            "prose_membership_occurrences": len(prose),
            "whole_portable_prose_occurrences": sum(row["primary_layer"] == "COMMON_PORTABLE_CARD" for row in prose),
            "astro_membership_occurrences": len(astro),
            "normalized_card_ids": "|".join(sorted({row["normalized_id"] for row in rows})),
            "visible_surfaces": "|".join(sorted({row["visible_surface"] for row in rows})),
            "prose_units": "|".join(sorted({row["unit_id"] for row in prose})),
            "astro_units": "|".join(sorted({row["unit_id"] for row in astro})),
            "prose_local_expansions": compact(local_prose),
            "astro_portable_values": compact(astro_core),
            "example_prose": prose[0]["visible_surface"] if prose else "NONE",
            "example_astro": astro[0]["visible_surface"] if astro else "NONE",
        })
    write(OUT / "TWO_HUNDRED_NINETEENTH_ELEVEN_PORTABLE_DICTIONARY_ENTRIES.tsv", entry_rows)

    lines = ["# Kleines portables Wörterbuch", ""]
    for row in entry_rows:
        lines.extend([
            f"## {row['entry_key']} — {row['headword_de']}",
            "",
            f"**Art:** {row['word_class']}.",
            "",
            f"**Lehrregel:** {row['composition_rule_de']}.",
            "",
            f"**Grenze:** {row['hard_boundary_de']}.",
            "",
            f"**Belege in der festen Ausgabe:** {row['prose_membership_occurrences']} Prosa-Mitgliedschaften, {row['astro_membership_occurrences']} Astro-Mitgliedschaften; Karten `{row['normalized_card_ids']}`.",
            "",
            f"**Oberflächen:** `{row['visible_surfaces']}`.",
            "",
            f"**Lokale Prosa-Lesungen:** {row['prose_local_expansions'] or 'keine'}.",
            "",
            f"**Astro-Kernwerte:** {row['astro_portable_values'] or 'keine'}.",
            "",
        ])
    (OUT / "TWO_HUNDRED_NINETEENTH_READABLE_PORTABLE_DICTIONARY.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "layered_source_sha256": hashlib.sha256(LAYER.read_bytes()).hexdigest(),
        "entries": len(entry_rows),
        "portable_occurrences": len(occurrence_rows),
        "prose_occurrences": sum(row["source_kind"] == "PROSE_EVENT" for row in portable),
        "astro_occurrences": sum(row["source_kind"] == "ASTRO_GROUP" for row in portable),
        "prose_axis_membership_links": sum(len(rows) for rows in grouped_prose.values()),
        "astro_axis_membership_links": sum(len(rows) for rows in grouped_astro.values()),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
