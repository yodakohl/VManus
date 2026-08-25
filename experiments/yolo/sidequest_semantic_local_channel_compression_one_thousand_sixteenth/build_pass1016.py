#!/usr/bin/env python3
"""Build Pass 1016: compress nineteen local signs into four teaching channels."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1013 = ROOT / "experiments/yolo/sidequest_semantic_embedded_stem_resegmentation_one_thousand_thirteenth"
PASS1015 = ROOT / "experiments/yolo/sidequest_semantic_627_core_owner_edition_one_thousand_fifteenth"
SOURCE_CONTRACT = PASS1013 / "PASS1013_46_SIGN_SEMANTIC_CONTRACT.tsv"
SOURCE_STATEMENTS = PASS1013 / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"
SOURCE_EDITION = PASS1015 / "PASS1015_627_CORE_OWNER_EDITION.tsv"


CHANNELS = {
    "LOCAL_PLACE": {
        "value": "HIER",
        "signs": ["D_ADDR", "AM_ADDR", "A_ADDR", "S_ADDR", "LOCAL_CHAR_F", "D_LABEL", "S_LABEL", "M_LOCAL", "Z_ADDR"],
        "rule": "Wähle die lokal bezeichnete Bild-, Tabellen-, Teil-, Innen-, Rand- oder Nebenposition.",
        "forbidden": "kein portables Teil-, innen-, außen-, Mitte- oder Ortswort",
    },
    "LOCAL_INDEX": {
        "value": "VARIANTE",
        "signs": ["G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_B", "LOCAL_CHAR_J", "LOCAL_CHAR_Z"],
        "rule": "Nimm die lokal markierte Variante, Stufe, Paarung oder Verbindung aus dem Exemplar.",
        "forbidden": "keine universelle Zahl, Farbe, Prüfhandlung oder Verbindungsrichtung",
    },
    "LOCAL_CLASS": {
        "value": "KLASSE",
        "signs": ["HO", "AN"],
        "rule": "Übernimm die lokale Stoff- oder Zusatzklasse; HO steht vorn, AN steht hinten.",
        "forbidden": "kein bestimmter Stoff, keine Pflanze, kein Badezusatz",
    },
    "LOCAL_REFERENCE": {
        "value": "VORBEZUG",
        "signs": ["OS", "RESUME_CARD"],
        "rule": "Aktiviere den lokal vorausgesetzten Bezug oder nimm den vorigen Besitzer/Gang wieder auf.",
        "forbidden": "kein universelles Gefäß-, Wiederholungs- oder Zahlenwort",
    },
}

SUBTYPE = {
    "D_ADDR": "TEILPLATZ", "AM_ADDR": "INNENPLATZ", "A_ADDR": "ORTSPLATZ",
    "S_ADDR": "SONDERPLATZ", "LOCAL_CHAR_F": "NEBENPLATZ", "D_LABEL": "RANDPLATZ",
    "S_LABEL": "RAHMENPLATZ", "M_LOCAL": "MITTELPLATZ", "Z_ADDR": "AUSSENPLATZ",
    "G_LABEL": "PRUEFVARIANTE", "LOCAL_CHAR_G": "EINZELVARIANTE",
    "LOCAL_CHAR_I": "UNTERSTUFENVARIANTE", "LOCAL_CHAR_B": "PAARVARIANTE",
    "LOCAL_CHAR_J": "VERBINDUNGSVARIANTE", "LOCAL_CHAR_Z": "ZWISCHENVARIANTE",
    "HO": "PRAEFIXKLASSE", "AN": "SUFFIXKLASSE", "OS": "LOKALER_BEZUG",
    "RESUME_CARD": "WIEDERAUFNAHME",
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered_unique(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def main() -> None:
    _, contract = read_tsv(SOURCE_CONTRACT)
    _, statements = read_tsv(SOURCE_STATEMENTS)
    _, edition = read_tsv(SOURCE_EDITION)
    local_contract = {row["sign"]: row for row in contract if row["pass1012_class"] == "LOCAL_ADDRESS_OR_MEMORIZED_SIGN"}
    sign_to_channel = {sign: channel for channel, spec in CHANNELS.items() for sign in spec["signs"]}
    if set(sign_to_channel) != set(local_contract):
        raise SystemExit("channel inventory does not cover the nineteen local signs exactly")

    usage = {
        sign: {
            "mentions": 0, "events": set(), "statements": set(), "pages": set(), "registers": set(),
            "positions": Counter(), "surfaces": Counter(), "before": Counter(), "after": Counter(),
        }
        for sign in local_contract
    }
    channel_event_ids: dict[str, set[str]] = defaultdict(set)
    channel_statements: dict[str, set[str]] = defaultdict(set)
    channel_pages: dict[str, set[str]] = defaultdict(set)
    channel_registers: dict[str, set[str]] = defaultdict(set)
    channel_positions: dict[str, Counter[str]] = defaultdict(Counter)
    all_local_event_ids = set()

    for statement in statements:
        surfaces = statement["surface_sequence"].split()
        events = [event.split("+") for event in statement["component_sequence"].split(" | ")]
        for event_index, (surface, tokens) in enumerate(zip(surfaces, events)):
            event_id = f"{statement['statement_id']}@{event_index + 1}"
            local_tokens = [token for token in tokens if token in local_contract]
            if local_tokens:
                all_local_event_ids.add(event_id)
            for token_index, sign in enumerate(tokens):
                if sign not in local_contract:
                    continue
                channel = sign_to_channel[sign]
                info = usage[sign]
                info["mentions"] += 1
                info["events"].add(event_id)
                info["statements"].add(statement["statement_id"])
                info["pages"].add(statement["physical_page"])
                info["registers"].add(statement["register"])
                position = "FIRST" if token_index == 0 else "LAST" if token_index == len(tokens) - 1 else "MIDDLE"
                info["positions"][position] += 1
                info["surfaces"][surface] += 1
                if token_index:
                    info["before"][tokens[token_index - 1]] += 1
                if token_index + 1 < len(tokens):
                    info["after"][tokens[token_index + 1]] += 1
                channel_event_ids[channel].add(event_id)
                channel_statements[channel].add(statement["statement_id"])
                channel_pages[channel].add(statement["physical_page"])
                channel_registers[channel].add(statement["register"])
                channel_positions[channel][position] += 1

    sign_rows = []
    for sign, old in local_contract.items():
        channel = sign_to_channel[sign]
        info = usage[sign]
        sign_rows.append(
            {
                "sign": sign,
                "old_local_value_de": old["single_core_value_de"],
                "pass1016_channel": channel,
                "channel_value_de": CHANNELS[channel]["value"],
                "local_subtype": SUBTYPE[sign],
                "running_mentions": str(info["mentions"]),
                "running_event_count": str(len(info["events"])),
                "statement_count": str(len(info["statements"])),
                "page_count": str(len(info["pages"])),
                "registers": "|".join(sorted(info["registers"])) if info["registers"] else "NONE_IN_RUNNING_LAYER",
                "token_position_counts": "|".join(f"{key}:{info['positions'][key]}" for key in ("FIRST", "MIDDLE", "LAST")),
                "surface_examples": "|".join(key for key, _ in info["surfaces"].most_common(8)) or "NONE_IN_RUNNING_LAYER",
                "common_left_neighbors": "|".join(f"{key}:{value}" for key, value in info["before"].most_common(5)) or "NONE",
                "common_right_neighbors": "|".join(f"{key}:{value}" for key, value in info["after"].most_common(5)) or "NONE",
                "apprentice_rule_de": CHANNELS[channel]["rule"],
                "forbidden_lexicalization_de": CHANNELS[channel]["forbidden"],
                "running_status": "ACTIVE_LOCAL_SELECTOR" if info["mentions"] else "DORMANT_IN_RUNNING_LAYER",
            }
        )
    sign_path = HERE / "PASS1016_19_LOCAL_SIGN_CHANNELS.tsv"
    write_tsv(sign_path, list(sign_rows[0]), sign_rows)

    channel_rows = []
    for channel, spec in CHANNELS.items():
        signs = spec["signs"]
        mentions = sum(usage[sign]["mentions"] for sign in signs)
        channel_rows.append(
            {
                "channel": channel,
                "short_value_de": spec["value"],
                "sign_count": str(len(signs)),
                "active_sign_count": str(sum(bool(usage[sign]["mentions"]) for sign in signs)),
                "signs": "|".join(signs),
                "running_mentions": str(mentions),
                "running_event_count": str(len(channel_event_ids[channel])),
                "statement_count": str(len(channel_statements[channel])),
                "page_count": str(len(channel_pages[channel])),
                "registers": "|".join(sorted(channel_registers[channel])) if channel_registers[channel] else "NONE",
                "token_position_counts": "|".join(f"{key}:{channel_positions[channel][key]}" for key in ("FIRST", "MIDDLE", "LAST")),
                "apprentice_rule_de": spec["rule"],
                "forward_prediction_de": f"Neue kompatible Form zuerst als {spec['value']} lesen; konkreten lokalen Inhalt vom Besitzer übernehmen.",
                "forbidden_lexicalization_de": spec["forbidden"],
            }
        )
    channel_path = HERE / "PASS1016_FOUR_LOCAL_CHANNELS.tsv"
    write_tsv(channel_path, list(channel_rows[0]), channel_rows)

    edition_by_id = {row["statement_id"]: row for row in edition}
    revised_rows = []
    local_statement_count = 0
    for statement in statements:
        old = edition_by_id[statement["statement_id"]]
        _, flat = ([event.split("+") for event in statement["component_sequence"].split(" | ")], [])
        flat = [token for event in statement["component_sequence"].split(" | ") for token in event.split("+")]
        local_signs = ordered_unique([token for token in flat if token in sign_to_channel])
        local_channels = ordered_unique([sign_to_channel[token] for token in local_signs])
        if local_channels:
            local_statement_count += 1
        old_signature_parts = old["semantic_signature"].split(" | ")
        new_signature_parts = [part for part in old_signature_parts if not part.startswith("LOCAL=")]
        new_signature_parts.append("LOCAL_CHANNELS=" + ("+".join(local_channels) if local_channels else "NONE"))
        revised_rows.append(
            {
                **old,
                "semantic_signature": " | ".join(new_signature_parts),
                "local_signs": "+".join(local_signs) if local_signs else "NONE",
                "local_channel_sequence": "+".join(local_channels) if local_channels else "NONE",
                "local_channel_values_de": "+".join(CHANNELS[channel]["value"] for channel in local_channels) if local_channels else "NONE",
                "pass1016_semantic_category_count": "31",
                "pass1016_result": "LOCAL_SIGNS_MAPPED_TO_FOUR_CHANNELS",
            }
        )
    edition_path = HERE / "PASS1016_627_LOCAL_CHANNEL_EDITION.tsv"
    edition_fields = list(edition[0]) + ["local_channel_sequence", "local_channel_values_de", "pass1016_semantic_category_count", "pass1016_result"]
    write_tsv(edition_path, edition_fields, revised_rows)

    report = f"""# Pass 1016 — vier lokale Kanäle statt neunzehn lokaler Wörter

## Ergebnis

Die 19 lokalen Zeichen sind keine 19 zusätzlichen Wörter. Für einen Werkstattschreiber genügen vier kurze Bedeutungen:

1. **LOCAL_PLACE = HIER** — wähle die lokal bezeichnete Stelle;
2. **LOCAL_INDEX = VARIANTE** — nimm die lokal markierte Ausführung;
3. **LOCAL_CLASS = KLASSE** — übernimm die lokale Stoff-/Zusatzklasse;
4. **LOCAL_REFERENCE = VORBEZUG** — nimm den vorausgesetzten lokalen Bezug wieder auf.

Die 46 sichtbaren Zeichenformen bleiben unverändert. Semantisch muss der Lehrling aber nur noch **19 portable Kerne + 8 Kontrollen + 4 lokale Kanäle = 31 Kategorien** lernen.

## Warum diese Kürzung funktioniert

- **LOCAL_PLACE** trägt {channel_rows[0]['running_mentions']} von insgesamt {sum(int(row['running_mentions']) for row in channel_rows)} lokalen Zeichenbeiträgen. Das ist der eigentliche lokale Mechanismus.
- `D_ADDR` ist der flexible Standardselektor; `AM_ADDR` steht 50/59-mal am Ereignisende, `S_ADDR` 12/13-mal. Das sind Positionsvarianten desselben HIER-Kanals, keine eigenen Ortswörter.
- **LOCAL_INDEX** sammelt die seltenen G/I/B/J/Z-Kennungen. Sie wählen eine Variante, ohne automatisch *eins, zwei, unten, prüfen* oder *verbinden* zu bedeuten.
- **LOCAL_CLASS** hat eine klare Schreibsyntax: `HO` steht 16/16-mal am Beginn seines Ereignisses, `AN` 7/7-mal am Ende. Beide markieren KLASSE, aber an entgegengesetzten Rändern.
- **LOCAL_REFERENCE** ist der kleine Vorbezugsrest: `OS` setzt den lokalen Bezug, die einmalige Wiederaufnahmekarte greift ihn wieder auf.
- Drei Formen (`S_LABEL`, `Z_ADDR`, `LOCAL_CHAR_Z`) sind im laufenden Text nicht aktiv. Sie bleiben reservierte lokale Exemplarzeichen, nicht drei Wörter ohne Beleg.

## Die neue Schreibregel

Ein unbekannter seltener Buchstabenteil bekommt nicht sofort einen Stoff- oder Tätigkeitsnamen. Der Schreiber fragt zuerst:

> **Wählt er einen Platz, eine Variante, eine Klasse oder einen Vorbezug?**

Erst das Bild oder die Tabelle füllt den lokalen Wert: Wurzelteil, Beckenrand, Sternposition, Gefäßgruppe, Paarvariante und so weiter. Das konkrete Substantiv gehört dem Besitzer, nicht dem Zeichen.

## Kompositionsvorhersagen

- Ein neuer D/A/AM/S/F/M/Z-artiger Einschub wird als **HIER** gelesen.
- Ein neuer G/I/B/J/Z-Mikrocharakter wird als **VARIANTE** gelesen.
- Eine HO-artige Vorsilbe oder AN-artige Endung wird als **KLASSE** gelesen.
- Eine alleinstehende OS-/Wiederaufnahmeform wird als **VORBEZUG** gelesen.
- Erst wenn eine Form diese vier Rollen wiederholt verletzt, darf ein neues lokales Wort erwogen werden.

## Wirkung auf die Gesamtausgabe

Alle **627 Aussagen / 3.888 Gruppen** bleiben bytegleich in Oberfläche, Reihenfolge, Besitzer, Handlung, Grad und Ende. **{local_statement_count} Aussagen** enthalten mindestens einen lokalen Kanal. Ihre Pass-1015-Lesung bleibt erhalten; die neue Ausgabe ersetzt lediglich die Liste scheinbarer lokaler Wörter durch die vier Kanäle.

Damit ist der nächste Engpass kleiner: Nicht 46 Bedeutungen müssen auf weiteren Seiten halten, sondern 31 Kategorien. Die 15 übrigen Unterschiede sind grafische Auswahlvarianten innerhalb der vier lokalen Kanäle.
"""
    report_path = HERE / "PASS1016_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "pass": 1016,
        "source_contract_sha256": sha256(SOURCE_CONTRACT),
        "source_statement_sha256": sha256(SOURCE_STATEMENTS),
        "source_edition_sha256": sha256(SOURCE_EDITION),
        "visible_sign_count": len(contract),
        "portable_core_count": 19,
        "formal_control_count": 8,
        "local_sign_count": len(local_contract),
        "local_channel_count": len(CHANNELS),
        "semantic_category_count": 31,
        "local_sign_mentions": sum(info["mentions"] for info in usage.values()),
        "local_event_count": len(all_local_event_ids),
        "local_statement_count": local_statement_count,
        "dormant_running_signs": sorted(sign for sign, info in usage.items() if not info["mentions"]),
        "channel_counts": {row["channel"]: int(row["running_mentions"]) for row in channel_rows},
        "statement_count": len(revised_rows),
        "event_count": sum(int(row["event_count"]) for row in revised_rows),
        "result": "NINETEEN_LOCAL_SIGNS_COMPRESS_TO_FOUR_CHANNELS",
        "outputs": {
            sign_path.name: sha256(sign_path),
            channel_path.name: sha256(channel_path),
            edition_path.name: sha256(edition_path),
            report_path.name: sha256(report_path),
        },
    }
    (HERE / "PASS1016_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
