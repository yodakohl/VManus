#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_portable_dictionary_entries_two_hundred_nineteenth/TWO_HUNDRED_NINETEENTH_ELEVEN_PORTABLE_DICTIONARY_ENTRIES.tsv"

EXCEPTIONS = {
    "MC017": ("EXISTING_SPECIALIST_COMPOSITION", "OK + AIN", "Anteil zugeben"),
    "MC023": ("EXISTING_SPECIALIST_COMPOSITION", "K + AIR", "Beckenlauf"),
    "MC033": ("EXISTING_SPECIALIST_COMPOSITION", "IIN", "Arbeitsstufe"),
    "MC045": ("EXISTING_SPECIALIST_COMPOSITION", "OL + K + EE + DY", "lange sammeln; Schluss"),
    "MC066": ("EXISTING_SPECIALIST_COMPOSITION", "L + RESULT", "Klarabzug"),
    "MC105": ("EXISTING_SPECIALIST_COMPOSITION", "AIN", "Portion"),
    "MC130": ("EXISTING_SPECIALIST_COMPOSITION", "LSH", "Waschgang"),
    "MC133": ("EXISTING_SPECIALIST_COMPOSITION", "L + CKH + E + DY", "Trennabzug; Schluss"),
    "MC141": ("EXISTING_SPECIALIST_COMPOSITION", "T + RESULT", "Folgeklarlauf"),
    "MC143": ("EXISTING_SPECIALIST_COMPOSITION", "SH + CKH + E + DY", "durchlassen; Schluss"),
    "MC061": ("PARTIAL_SPECIALIST_COMPOSITION", "CHD + DY visible; SSHK hull unresolved", "Haltetransfer; Schluss"),
    "MC109": ("PARTIAL_SPECIALIST_COMPOSITION", "Y + E visible; T hull unresolved", "Kurzteil"),
    "MC012": ("LEARNED_LOCAL_WHOLE_CARD", "DL", "Zusatz"),
    "MC065": ("LEARNED_LOCAL_WHOLE_CARD", "LS", "Auslass"),
    "MC118": ("LEARNED_LOCAL_WHOLE_CARD", "LY", "Auffanggefäß"),
    "MC152": ("LEARNED_LOCAL_WHOLE_CARD", "CHES", "teilen"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    entries = read(DICTIONARY)
    base_axes: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        for card_id in entry["normalized_card_ids"].split("|"):
            base_axes[card_id].append(entry["entry_key"])
    events = [row for row in read(EVENTS) if row["page"] in {"f81v", "f82r"}]
    statement_source = {row["statement_id"]: row for row in read(STATEMENTS)}

    event_rows: list[dict[str, object]] = []
    for row in events:
        if row["master_card_id"] in base_axes:
            status = "BASE_TWENTY_RULE_CURRICULUM"
            analysis = "+".join(base_axes[row["master_card_id"]])
        else:
            status, analysis, _ = EXCEPTIONS[row["master_card_id"]]
        event_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "field_id": row["field_id"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "portable_value_de": row["portable_value_de"],
            "visible_owner": row["visible_owner"],
            "curriculum_status": status,
            "component_or_whole_analysis": analysis,
        })
    write(OUT / "TWO_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_TWENTY_EIGHT_EVENTS.tsv", event_rows)

    statement_rows: list[dict[str, object]] = []
    for statement_id in dict.fromkeys(row["statement_id"] for row in events):
        rows = [row for row in event_rows if row["statement_id"] == statement_id]
        statuses = {row["curriculum_status"] for row in rows}
        if statuses == {"BASE_TWENTY_RULE_CURRICULUM"}:
            statement_status = "FULLY_BASE_RULED"
        elif "LEARNED_LOCAL_WHOLE_CARD" in statuses or "PARTIAL_SPECIALIST_COMPOSITION" in statuses:
            statement_status = "BASE_PLUS_EXEMPLAR_CARD"
        else:
            statement_status = "BASE_PLUS_EXISTING_SPECIALIST_COMPOSITION"
        source = statement_source[statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record_unit_id": rows[0]["record_unit_id"],
            "visible_owner": source["visible_owner"],
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "event_count": len(rows),
            "curriculum_status": statement_status,
            "master_dictation_de": source["r221_owner_expansion_de"],
            "apprentice_response": source["visible_sequence"],
            "nonbase_cards": "|".join(str(row["visible_surface"]) for row in rows if row["curriculum_status"] != "BASE_TWENTY_RULE_CURRICULUM") or "NONE",
        })
    write(OUT / "TWO_HUNDRED_THIRTY_SIXTH_FORTY_THREE_DICTATION_TRACES.tsv", statement_rows)

    card_rows: list[dict[str, object]] = []
    for card_id, (status, analysis, value) in EXCEPTIONS.items():
        rows = [row for row in event_rows if row["master_card_id"] == card_id]
        if not rows:
            continue
        card_rows.append({
            "master_card_id": card_id,
            "visible_surfaces": "|".join(sorted({str(row["visible_surface"]) for row in rows})),
            "event_count": len(rows),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "current_value_de": value,
            "analysis_status": status,
            "component_analysis": analysis,
            "curriculum_action": "ADD_EXISTING_SPECIALIST_COMPONENT_TO_NEXT_LESSON" if status == "EXISTING_SPECIALIST_COMPOSITION" else ("KEEP_PARTIAL_AND_TEACH_AS_CARD" if status == "PARTIAL_SPECIALIST_COMPOSITION" else "MEMORIZE_LOCAL_WHOLE_CARD"),
        })
    card_rows.sort(key=lambda row: int(str(row["event_ids"]).split("|")[0][1:]))
    write(OUT / "TWO_HUNDRED_THIRTY_SIXTH_SIXTEEN_NONBASE_CARDS.tsv", card_rows)

    readable = [
        "# Derselbe Lehrplan auf f81v und f82r",
        "",
        "Der f83r-Grundkurs liest 108 von 128 Karten direkt. 29 der 43 Aussagen können vollständig aus den Grundregeln diktiert werden; 14 brauchen mindestens eine Fach- oder Exemplarkarte.",
        "",
        "## Bereits bekannte Fachkompositionen",
        "",
        "Dreizehn weitere Ereignisse sind nicht wirklich neu: `AIN = Portion`, `AIR = Laufmedium`, `IIN = Stufe`, `CKH = Durchlass`, `LSH = Waschgang` und die gelernte Ergebniskarte erklären zehn Typen. Nimmt der Lehrling diese sechs Zusatzkarten in Lektion 2 auf, sind 121 von 128 Karten konstruktiv lesbar.",
        "",
        "## Der echte kleine Rest",
        "",
        "- `sshkchdy` — Haltetransfer; Schluss: Transfer und Schluss sichtbar, Hülle noch nicht verstanden.",
        "- `ytey` — Kurzteil: Referent und Kurzgrad sichtbar, T-Hülle noch nicht verstanden.",
        "- `dl` — Zusatz: zweimalige lokale Ganzkarte.",
        "- `ls` — Auslass: lokale Ganzkarte.",
        "- `ly` — Auffanggefäß: lokale Ganzkarte.",
        "- `ches` — teilen: lokale Ganzkarte.",
        "",
        "Das ist ein brauchbarer Lehrbetrieb: sechs bekannte Fachkomponenten ergänzen, zwei Formen als halb zerlegt markieren und vier Gegenstände/Handlungen als ganze Karten auswendig lernen.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_SIXTH_READABLE_CURRICULUM_TRANSFER.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 236 — f83r-Lehrplan auf f81v/f82r übertragen",
        "",
        "Ohne neue Bedeutungen deckt der 20-Regel-Grundkurs 108/128 Ereignisse und 29/43 Aussagen vollständig. Der Rest besteht aus 13 Ereignissen mit bereits vorhandenen Fachkomponenten, zwei partiellen Kompositionen und fünf Vorkommen von vier lokalen Ganzkarten.",
        "",
        "Die nächste Verbesserung ist daher klein: eine zweite Lehrstunde mit AIN, AIR, IIN, CKH, LSH und RESULT. Danach bleiben nur sieben exemplarabhängige Ereignisse, und wir können entscheiden, ob deren vier Ganzkarten ein gemeinsames kleines Geräte-/Materiallexikon bilden.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_SIXTH_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "dictionary_source_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "base_rule_events": sum(row["curriculum_status"] == "BASE_TWENTY_RULE_CURRICULUM" for row in event_rows),
        "existing_specialist_events": sum(row["curriculum_status"] == "EXISTING_SPECIALIST_COMPOSITION" for row in event_rows),
        "partial_events": sum(row["curriculum_status"] == "PARTIAL_SPECIALIST_COMPOSITION" for row in event_rows),
        "local_whole_events": sum(row["curriculum_status"] == "LEARNED_LOCAL_WHOLE_CARD" for row in event_rows),
        "fully_base_ruled_statements": sum(row["curriculum_status"] == "FULLY_BASE_RULED" for row in statement_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
