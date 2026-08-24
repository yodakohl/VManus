#!/usr/bin/env python3
"""Assign every Biological card and statement to a compact operating-mode inventory."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_ten_weak_cards_three_hundred_fourth/THREE_HUNDRED_FOURTH_173_REVISED_IMPERATIVE_LEXICON.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_ten_weak_cards_three_hundred_fourth/THREE_HUNDRED_FOURTH_116_REVISED_STATEMENTS.tsv"
VISUAL = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_R3_97_STATEMENT_EDITION.tsv"
BLOCKS = ROOT / "experiments/yolo/sidequest_semantic_visual_block_roles_three_hundred_seventh/THREE_HUNDRED_SEVENTH_18_STATEMENT_VISUAL_BINDINGS.tsv"


MODE_LEXICON = [
    ("CHARGE", "Beschicken", "Material, Anteil oder laufenden Posten in einen Arbeitsgang oder Empfänger einsetzen"),
    ("TREAT", "Behandeln", "einwirken lassen, wärmen, bearbeiten, auftragen oder befestigen"),
    ("SETTLE", "Absetzen/Sammeln", "ruhen, absetzen, sammeln oder bis zu einem Stand halten"),
    ("PASS_FILTER", "Durchlassen/Filtern", "waschen, spülen, seihen, durchleiten oder Klarlauf gewinnen"),
    ("DISCHARGE", "Abführen", "abziehen, entleeren oder den Posten aus dem lokalen Arbeitsbereich führen"),
    ("MEASURE", "Messen/Einstellen", "Maß, Anteil, Stufe oder Dauer setzen"),
    ("LOCAL_CONTROL", "Lokal steuern", "Besitzer, Ziel, Folge, Bereitschaft oder aktuellen Posten verwalten"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mode(event: dict[str, str], lexicon: dict[str, dict[str, str]]) -> tuple[str, str]:
    gloss = lexicon[event["master_card_id"]]["source_short_value_de"].lower()
    family = event["family_parse"]
    if any(k in gloss for k in ["abführ", "abzug", "abzieh", "entleer", "auslass", "trennabzug"]):
        return "DISCHARGE", "Abführ-/Abzugwert der Ganzkarte"
    if any(k in gloss for k in ["wasch", "spül", "seih", "klarlauf", "klarabzug", "auswring", "durchlass", "durchleit", "passage"]):
        return "PASS_FILTER", "Wasch-, Durchlass- oder Trennwert der Ganzkarte"
    if any(k in gloss for k in ["absetz", "sammel", "stehzeit", "verwahr"]):
        return "SETTLE", "Absetz-, Sammel- oder Haltewert der Ganzkarte"
    if any(k in gloss for k in ["einwirk", "wärm", "kalt", "bearbeit", "auftrag", "befestig"]):
        return "TREAT", "Kontakt-, Wärme- oder Behandlungswert der Ganzkarte"
    if any(k in gloss for k in ["zugabe", "zutat", "einsetz", "zuführ", "überführ", "transfer", "portion", "anteil", "ansatz", "auszug", "wurzel", "stängel", "kochgut", "sud"]):
        return "CHARGE", "Material-, Beschickungs- oder Übergabewert der Ganzkarte"
    if any(k in gloss for k in ["maß", "stufe", "bemess"]):
        return "MEASURE", "Maß- oder Einstellwert der Ganzkarte"
    return "LOCAL_CONTROL", "lokaler Besitzer-, Ziel-, Folge-, Zustands- oder Postenwert"


def main() -> None:
    raw = [r for r in read(RAW) if r["record_unit_id"].startswith("B")]
    lexicon = {r["master_card_id"]: r for r in read(LEXICON)}
    statements = {r["statement_id"]: r for r in read(STATEMENTS) if r["record_unit_id"].startswith("B")}
    visual = {r["statement_id"]: r for r in read(VISUAL)}
    block_by_statement = {r["statement_id"]: r for r in read(BLOCKS)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[str]] = defaultdict(list)
    event_rows = []
    for event in raw:
        selected_mode, reason = mode(event, lexicon)
        by_statement[event["statement_id"]].append(event)
        if event["statement_id"] not in by_record[event["record_unit_id"]]:
            by_record[event["record_unit_id"]].append(event["statement_id"])
        event_rows.append({
            "event_id": event["event_id"], "record_unit_id": event["record_unit_id"], "page": event["page"],
            "statement_id": event["statement_id"], "field_id": event["field_id"], "visible_surface": event["visible_surface"],
            "master_card_id": event["master_card_id"], "source_short_value_de": lexicon[event["master_card_id"]]["source_short_value_de"],
            "imperative_clause_de": lexicon[event["master_card_id"]]["imperative_clause_de"],
            "operating_mode": selected_mode, "mode_assignment_reason": reason, "terminal_status": event["terminal_status"],
        })
    event_path = HERE / "THREE_HUNDRED_EIGHTH_281_EVENT_OPERATING_MODES.tsv"
    write(event_path, event_rows)

    event_by_id = {r["event_id"]: r for r in event_rows}
    statement_rows = []
    for statement_id, selected in by_statement.items():
        modes = []
        trace = []
        for event in selected:
            value = event_by_id[event["event_id"]]["operating_mode"]
            trace.append(f"{event['event_id']}:{value}")
            if not modes or modes[-1] != value:
                modes.append(value)
        primary = modes[-1]
        block = block_by_statement.get(statement_id)
        vis = visual[statement_id]
        source = statements[statement_id]
        statement_rows.append({
            "statement_id": statement_id, "record_unit_id": source["record_unit_id"], "page": source["page"],
            "field_path": source["field_path"], "event_count": len(selected), "operating_mode_sequence": ">".join(modes),
            "primary_operating_mode": primary, "event_mode_trace": "|".join(trace),
            "visual_owner_bindings": vis["owner_bindings"], "owner_transition": vis["owner_transition"],
            "procedure_block_id": block["block_id"] if block else "NONE",
            "procedure_block_role": block["selected_station_role"] if block else "NONE",
            "fluent_imperative_de": source["fluent_imperative_de"],
            "mode_reading_de": next(label for key, label, _ in MODE_LEXICON if key == primary),
        })
    statement_path = HERE / "THREE_HUNDRED_EIGHTH_97_STATEMENT_OPERATING_MODES.tsv"
    write(statement_path, statement_rows)

    mode_path = HERE / "THREE_HUNDRED_EIGHTH_SEVEN_MODE_LEXICON.tsv"
    mode_rows = []
    for key, label, definition in MODE_LEXICON:
        mode_rows.append({
            "operating_mode": key, "short_label_de": label, "definition_de": definition,
            "event_count": sum(r["operating_mode"] == key for r in event_rows),
            "primary_statement_count": sum(r["primary_operating_mode"] == key for r in statement_rows),
            "record_units": "|".join(sorted({r["record_unit_id"] for r in statement_rows if r["primary_operating_mode"] == key})),
        })
    write(mode_path, mode_rows)

    record_rows = []
    statement_by_id = {r["statement_id"]: r for r in statement_rows}
    for record_id, statement_ids in by_record.items():
        selected = [statement_by_id[s] for s in statement_ids]
        counts = Counter(r["primary_operating_mode"] for r in selected)
        main_mode = counts.most_common(1)[0][0]
        record_rows.append({
            "record_unit_id": record_id, "page": selected[0]["page"], "statement_count": len(selected),
            "event_count": sum(int(r["event_count"]) for r in selected), "dominant_operating_mode": main_mode,
            "mode_counts": "|".join(f"{key}:{counts[key]}" for key, _, _ in MODE_LEXICON),
            "ordered_primary_modes": ">".join(r["primary_operating_mode"] for r in selected),
            "block_ids": "|".join(dict.fromkeys(r["procedure_block_id"] for r in selected if r["procedure_block_id"] != "NONE")) or "NONE",
        })
    record_path = HERE / "THREE_HUNDRED_EIGHTH_SIX_RECORD_MODE_SUMMARY.tsv"
    write(record_path, record_rows)

    lines = ["# Biological-Betriebsausgabe in sieben Modi", "", "Jede Aussage erhält als Hauptmodus ihre letzte inhaltliche Handlung. Davorstehende Modi bleiben in der Pfeilfolge sichtbar; ein komplexer Satz wird also nicht auf nur ein Etikett reduziert.", ""]
    for record in record_rows:
        lines += [f"## {record['record_unit_id']} — Hauptmodus {record['dominant_operating_mode']}", ""]
        for statement_id in by_record[record["record_unit_id"]]:
            row = statement_by_id[statement_id]
            lines += [f"**{statement_id} [{row['operating_mode_sequence']} → {row['primary_operating_mode']}]:** {row['fluent_imperative_de']}", ""]
    edition_path = HERE / "THREE_HUNDRED_EIGHTH_COMPLETE_BIO_OPERATING_EDITION.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    event_counts = Counter(r["operating_mode"] for r in event_rows)
    statement_counts = Counter(r["primary_operating_mode"] for r in statement_rows)
    dominant = statement_counts.most_common()
    report_path = HERE / "THREE_HUNDRED_EIGHTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 308: sieben Betriebsarten für die ganze Biological-Prosa\n\n"
        "Alle 281 Bio-Ereignisse und 97 Aussagen sind jetzt in ein einziges Betriebsinventar eingehängt: Beschicken, Behandeln, Absetzen/Sammeln, Durchlassen/Filtern, Abführen, Messen/Einstellen und lokale Steuerung. Jede Aussage bewahrt ihre volle Modusfolge; der Hauptmodus ist nur die letzte ausgeführte Handlung.\n\n"
        + "Primäre Aussageverteilung: " + ", ".join(f"{mode} {count}" for mode, count in dominant) + ". Die Verteilung zeigt, dass die Seiten nicht von einem einzigen Wasserverb beherrscht werden. Sie wechseln systematisch zwischen lokaler Steuerung, Beschickung/Behandlung, Transfer, Absetzen und Abschluss.\n\n"
        "Als nächstes kann jede der sieben Betriebsarten auf wiederkehrende Kartenstämme zurückgeführt werden. Dann sehen wir, welche Stämme tatsächlich eine Betriebsart vorhersagen und welche weiterhin gelernte Ganzwörter bleiben.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows), "modes": len(mode_rows),
        "event_mode_counts": dict(event_counts), "primary_statement_mode_counts": dict(statement_counts),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [RAW, LEXICON, STATEMENTS, VISUAL, BLOCKS]},
        "output_hashes": {p.name: sha(p) for p in [event_path, statement_path, mode_path, record_path, edition_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
