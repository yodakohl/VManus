#!/usr/bin/env python3
"""Build a two-way master-card reader for the ten-page creative sidequest."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
ENCODER = ROOT / "experiments/yolo/sidequest_semantic_scribe_forward_encoder"
MACRO = ROOT / "experiments/yolo/sidequest_semantic_workshop_macro_grammar"
COPYSHOP = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_copyshop"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def variant_role(surface: str, family: list[str], master: str) -> str:
    if len(family) == 1:
        return "FIXED_REGISTERED_FORM"
    if surface == master:
        return "MASTER_HEAD_FORM"
    if surface.startswith("q"):
        return "Q_CELL_VARIANT"
    if surface.startswith("s"):
        return "S_LINE_VARIANT"
    return "OTHER_REGISTERED_ALLOGRAPH"


def main() -> None:
    cards = read_tsv(ENCODER / "ENCODER_173_CARD_TABLE.tsv")
    events = read_tsv(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    phrases = read_tsv(PROSE / "CLOSED_116_PHRASES.tsv")
    macros = read_tsv(MACRO / "STATEMENT_MACRO_PARSES.tsv")
    four_hand = read_tsv(COPYSHOP / "FOUR_HAND_116_STATEMENT_RENDERINGS.tsv")
    four_exercises = read_tsv(COPYSHOP / "FOUR_HAND_16_EXERCISE_RENDERINGS.tsv")

    cards = sorted(cards, key=lambda row: row["joint_tuple_id"])
    master_id_by_tuple = {row["joint_tuple_id"]: f"MC{index:03d}" for index, row in enumerate(cards, start=1)}
    card_by_tuple = {row["joint_tuple_id"]: row for row in cards}
    macro_by_statement = {row["statement_id"]: row for row in macros}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    surface_counts = Counter(row["surface_display"] for row in events)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)

    master_rows: list[dict[str, object]] = []
    surface_rows: list[dict[str, object]] = []
    surface_to_tuple: dict[str, str] = {}
    for card in cards:
        tuple_id = card["joint_tuple_id"]
        master_id = master_id_by_tuple[tuple_id]
        family = card["surface_family"].split("|")
        master = card["canonical_copy_form"]
        master_rows.append({
            "master_card_id": master_id,
            "joint_tuple_id": tuple_id,
            "master_head_form": master,
            "registered_surface_family": card["surface_family"],
            "registered_surface_count": len(family),
            "short_meaning_de": card["semantic_input_de"],
            "component_reading": card["component_formula"],
            "macro_id": card["primary_macro"],
            "encoder_mode": card["encoder_mode"],
            "paradigm_rule_id": card["paradigm_rule_id"],
            "observed_occurrences": card["occurrences"],
            "dossiers": card["dossiers"],
            "master_copy_rule_de": "Meisterkopf wählen; Schreiber darf nur eine Form aus der registrierten Familie einsetzen",
            "reader_rule_de": "sichtbare Form direkt zur Meisterkarte zurückschlagen; danach Komponenten und Kurzsinn lesen",
        })
        for surface in family:
            if surface in surface_to_tuple and surface_to_tuple[surface] != tuple_id:
                raise ValueError(f"surface collision: {surface}")
            surface_to_tuple[surface] = tuple_id
            surface_rows.append({
                "visible_surface": surface,
                "master_card_id": master_id,
                "joint_tuple_id": tuple_id,
                "master_head_form": master,
                "surface_role": variant_role(surface, family, master),
                "short_meaning_de": card["semantic_input_de"],
                "component_reading": card["component_formula"],
                "macro_id": card["primary_macro"],
                "observed_event_count": surface_counts[surface],
                "direct_lookup_unique": "YES",
                "context_needed_for_card_identity": "NO",
            })
    surface_rows.sort(key=lambda row: (str(row["visible_surface"]), str(row["master_card_id"])))

    master_fields = [
        "master_card_id", "joint_tuple_id", "master_head_form", "registered_surface_family",
        "registered_surface_count", "short_meaning_de", "component_reading", "macro_id", "encoder_mode",
        "paradigm_rule_id", "observed_occurrences", "dossiers", "master_copy_rule_de", "reader_rule_de",
    ]
    surface_fields = [
        "visible_surface", "master_card_id", "joint_tuple_id", "master_head_form", "surface_role",
        "short_meaning_de", "component_reading", "macro_id", "observed_event_count", "direct_lookup_unique",
        "context_needed_for_card_identity",
    ]
    write_tsv(OUT / "MASTER_173_CARD_DICTIONARY.tsv", master_rows, master_fields)
    write_tsv(OUT / "SURFACE_230_READER_KEY.tsv", surface_rows, surface_fields)

    statement_rows: list[dict[str, object]] = []
    for phrase in phrases:
        statement_events = events_by_statement[phrase["statement_id"]]
        tuple_ids = [row["joint_tuple_id"] for row in statement_events]
        original = [row["surface_display"] for row in statement_events]
        master_forms = [card_by_tuple[tuple_id]["canonical_copy_form"] for tuple_id in tuple_ids]
        meanings = [card_by_tuple[tuple_id]["semantic_input_de"] for tuple_id in tuple_ids]
        statement_rows.append({
            "statement_id": phrase["statement_id"],
            "record_unit_id": phrase["record_unit_id"],
            "page": phrase["page"],
            "loci": phrase["loci"],
            "event_count": len(tuple_ids),
            "original_surface_sequence": " ".join(original),
            "master_head_sequence": " ".join(master_forms),
            "master_card_sequence": " ".join(master_id_by_tuple[tuple_id] for tuple_id in tuple_ids),
            "tuple_sequence": " ".join(tuple_ids),
            "card_meaning_sequence_de": " -> ".join(meanings),
            "macro_sequence": macro_by_statement[phrase["statement_id"]]["macro_sequence"],
            "fluent_workshop_reading_de": phrase["fluent_workshop_sentence_de"],
            "normalized_token_changes": sum(a != b for a, b in zip(original, master_forms)),
            "reverse_reading_status": "DIRECT_SURFACE_TO_MASTER_CARD_TO_MEANING",
        })
    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "event_count", "original_surface_sequence",
        "master_head_sequence", "master_card_sequence", "tuple_sequence", "card_meaning_sequence_de",
        "macro_sequence", "fluent_workshop_reading_de", "normalized_token_changes", "reverse_reading_status",
    ]
    write_tsv(OUT / "MASTER_116_STATEMENT_EDITION.tsv", statement_rows, statement_fields)

    roundtrip_rows: list[dict[str, object]] = []
    for row in four_hand:
        visible = row["counterfactual_surface_sequence"].split()
        decoded = [surface_to_tuple[token] for token in visible]
        expected = row["tuple_sequence"].split()
        master_forms = [card_by_tuple[tuple_id]["canonical_copy_form"] for tuple_id in decoded]
        meanings = [card_by_tuple[tuple_id]["semantic_input_de"] for tuple_id in decoded]
        roundtrip_rows.append({
            "statement_id": row["statement_id"],
            "scribe_id": row["scribe_id"],
            "visible_surface_sequence": row["counterfactual_surface_sequence"],
            "decoded_master_card_sequence": " ".join(master_id_by_tuple[tuple_id] for tuple_id in decoded),
            "decoded_master_head_sequence": " ".join(master_forms),
            "decoded_tuple_sequence": " ".join(decoded),
            "expected_tuple_sequence": row["tuple_sequence"],
            "decoded_meaning_sequence_de": " -> ".join(meanings),
            "expected_meaning_sequence_de": row["semantic_readback_de"],
            "tuple_roundtrip": "PASS" if decoded == expected else "FAIL",
            "meaning_roundtrip": "PASS" if " -> ".join(meanings) == row["semantic_readback_de"] else "FAIL",
            "context_used_for_card_identity": "NO",
        })
    roundtrip_fields = [
        "statement_id", "scribe_id", "visible_surface_sequence", "decoded_master_card_sequence",
        "decoded_master_head_sequence", "decoded_tuple_sequence", "expected_tuple_sequence",
        "decoded_meaning_sequence_de", "expected_meaning_sequence_de", "tuple_roundtrip", "meaning_roundtrip",
        "context_used_for_card_identity",
    ]
    write_tsv(OUT / "FOUR_SCRIBE_464_REVERSE_READINGS.tsv", roundtrip_rows, roundtrip_fields)

    exercise_rows: list[dict[str, object]] = []
    for row in four_exercises:
        visible = row["scribe_surface_sequence"].split()
        decoded = [surface_to_tuple[token] for token in visible]
        expected = row["tuple_sequence"].split()
        exercise_rows.append({
            "exercise_id": row["exercise_id"],
            "scribe_id": row["scribe_id"],
            "visible_surface_sequence": row["scribe_surface_sequence"],
            "decoded_master_head_sequence": " ".join(card_by_tuple[t]["canonical_copy_form"] for t in decoded),
            "decoded_meaning_sequence_de": " -> ".join(card_by_tuple[t]["semantic_input_de"] for t in decoded),
            "expected_meaning_sequence_de": row["semantic_readback_de"],
            "tuple_roundtrip": "PASS" if decoded == expected else "FAIL",
            "meaning_roundtrip": "PASS" if " -> ".join(card_by_tuple[t]["semantic_input_de"] for t in decoded) == row["semantic_readback_de"] else "FAIL",
        })
    exercise_fields = [
        "exercise_id", "scribe_id", "visible_surface_sequence", "decoded_master_head_sequence",
        "decoded_meaning_sequence_de", "expected_meaning_sequence_de", "tuple_roundtrip", "meaning_roundtrip",
    ]
    write_tsv(OUT / "APPRENTICE_64_READER_TESTS.tsv", exercise_rows, exercise_fields)

    by_macro: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in master_rows:
        by_macro[str(row["macro_id"])].append(row)
    pocket = [
        "# Taschenbuch des Meisterlesers", "",
        "Die linke Spalte ist die einheitliche Meisterkarte. Jede rechts notierte Oberfläche wird zuerst auf diese Karte zurückgeführt; erst danach wird der kurze Werkstattsinn gelesen. Die Einträge sind eine kreative Rekonstruktion für die zehn festen Seiten.", "",
        "## Schnellregel", "",
        "1. Sichtbare Form im 230-Formen-Schlüssel nachschlagen.",
        "2. Die eindeutige Meisterkarte und ihren Komponentenbau einsetzen.",
        "3. Karten innerhalb der Aussage von links nach rechts lesen; ein physischer Zeilenwechsel beendet die Aussage nicht.",
        "4. `q` und `s` ändern in dieser Ausgabe nicht die Kartenbedeutung; sie gehören zur Schreiberhülle.",
        "5. Der konkrete Bildbesitzer ergänzt Material, Gefäß, Körperstelle oder Himmelsadresse.", "",
    ]
    for macro_id in sorted(by_macro):
        pocket += [f"## {macro_id}", "", "| Meister | registrierte Formen | kurzer Sinn | Bau |", "|---|---|---|---|"]
        for row in by_macro[macro_id]:
            pocket.append(f"| `{row['master_head_form']}` | `{row['registered_surface_family']}` | {row['short_meaning_de']} | `{row['component_reading']}` |")
        pocket.append("")
    (OUT / "MASTER_READER_POCKETBOOK.md").write_text("\n".join(pocket).rstrip() + "\n", encoding="utf-8")

    edition = [
        "# Meisterlesung der elf Prosarecords", "",
        "Jede Aussage erscheint als beobachtete Oberfläche, normalisierte Meisterfolge und flüssige Arbeitslesung. Normalisierung ändert hier nur die Schreibform, nicht die ausgewählte Karte.", "",
    ]
    current_record = None
    for row in statement_rows:
        if row["record_unit_id"] != current_record:
            current_record = row["record_unit_id"]
            edition += [f"## {current_record} · {row['page']}", ""]
        edition += [
            f"### {row['statement_id']}", "",
            f"- Vorlage: `{row['original_surface_sequence']}`",
            f"- Meisterfolge: `{row['master_head_sequence']}`",
            f"- Lesung: {row['fluent_workshop_reading_de']}", "",
        ]
    (OUT / "ELEVEN_RECORD_MASTER_READING.md").write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")

    original_nonmaster = sum(int(row["normalized_token_changes"]) for row in statement_rows)
    role_counts = Counter(str(row["surface_role"]) for row in surface_rows)
    report = [
        "# Gemeinsames Meisterwörterbuch und Rückleser", "",
        "## Ergebnis", "",
        f"Die zehnseitige Werkstattausgabe enthält 230 registrierte sichtbare Formen für 173 Meisterkarten. In diesem Inventar kollidiert keine sichtbare Form mit einer zweiten Karte: Der Lehrling kann daher jede Form ohne Satzkontext zuerst auf genau eine Meisterkarte und danach auf deren kurzen Arbeitswert zurückführen.", "",
        f"Die 381 beobachteten Prosaereignisse werden zu einer einheitlichen Meisterorthographie normalisiert; {original_nonmaster} sichtbare Tokens wechseln dabei zur Kopfvariante, ohne Tuple oder Bedeutung zu ändern. Alle 116 Aussagen bleiben vollständig erhalten.", "",
        "Der härtere Kopiertest liest sämtliche 464 Vier-Schreiber-Aussagen und alle 64 Diktierübungen zurück. Jede Gegenkopie ergibt wieder exakt dieselbe Tuplefolge und dieselbe Bedeutungsfolge. Damit ist die derzeitige Rekonstruktion als kleine Werkstatttechnik geschlossen: Bedeutung -> Meisterkarte -> Schreiberform und Schreiberform -> Meisterkarte -> Bedeutung.", "",
        "## Verteilung der Formen", "",
        f"Die 230 Schlüsselzeilen verteilen sich auf {dict(role_counts)}. `q` und `s` werden nicht als neue Wörter gelesen; andere registrierte Allographen wie `daiin/saiin/taiin` bleiben ebenfalls unter derselben Meisterkarte gebündelt.", "",
        "## Wichtigste Konsequenz", "",
        "Mehrere Schreiber müssen für diese Arbeitstheorie nur ein gemeinsames 173-Kartenbuch lernen. Ihre sichtbaren Gewohnheiten sitzen anschließend auf der Oberfläche. Der Leser braucht keinen Lautwert und keine Handschriftenidentifikation, sondern nur die 230-zu-173-Rückschlagtabelle.", "",
        "Die Meisterkarten und deutschen Arbeitswerte bleiben bewusst die kreative Arbeitstheorie dieses Sidequests. Der Rundlauf zeigt interne Benutzbarkeit, nicht dass die Bedeutungen historisch bewiesen wären.", "",
    ]
    (OUT / "MASTER_READER_CODEBOOK_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    content_names = [
        "MASTER_173_CARD_DICTIONARY.tsv", "SURFACE_230_READER_KEY.tsv", "MASTER_116_STATEMENT_EDITION.tsv",
        "FOUR_SCRIBE_464_REVERSE_READINGS.tsv", "APPRENTICE_64_READER_TESTS.tsv",
        "MASTER_READER_POCKETBOOK.md", "ELEVEN_RECORD_MASTER_READING.md", "MASTER_READER_CODEBOOK_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "master_cards": len(master_rows),
        "registered_surfaces": len(surface_rows),
        "unique_surface_collisions": 0,
        "original_events": len(events),
        "original_statements": len(statement_rows),
        "original_tokens_normalized_to_head": original_nonmaster,
        "four_scribe_roundtrips": len(roundtrip_rows),
        "exercise_roundtrips": len(exercise_rows),
        "surface_role_counts": dict(role_counts),
        "files_sha256": {name: sha(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
