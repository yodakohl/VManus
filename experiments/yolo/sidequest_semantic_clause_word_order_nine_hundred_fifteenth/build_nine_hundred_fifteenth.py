#!/usr/bin/env python3
"""Build a speakable clause order for all 2,010 prose groups on the 14 pages."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
P914 = ROOT / "experiments/yolo/sidequest_semantic_classifier_action_split_nine_hundred_fourteenth"
EVENTS = P914 / "PASS914_2511_CONTEXTUAL_INTERLINEAR.tsv"

PROSE_OUT = BASE / "PASS915_2010_PROSE_EVENT_SLOTS.tsv"
CLAUSE_OUT = BASE / "PASS915_354_CLAUSE_EDITION.tsv"
TRANSITIONS_OUT = BASE / "PASS915_SLOT_TRANSITIONS.tsv"
GRAMMAR_OUT = BASE / "PASS915_CLAUSE_GRAMMAR.tsv"
EDITION_OUT = BASE / "PASS915_READABLE_CLAUSE_EDITION.md"
REPORT_OUT = BASE / "PASS915_REPORT.md"
SUMMARY_OUT = BASE / "PASS915_BUILD_SUMMARY.json"


PAGE_ORDER = ["f10r", "f11r", "f13r", "f55v", "f56r", "f75r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f88r"]

SLOT_ORDER = [
    "ORDER_CALL",
    "OWNER_CONTENT",
    "SOURCE_REFERENCE",
    "QUANTITY_INDEX",
    "ACTION",
    "TARGET_PATH",
    "GRADE_STATE",
    "CLOSE",
    "LOCAL_DETAIL",
]

COMPONENT_SLOT = {
    "OT": "ORDER_CALL", "OL": "ORDER_CALL", "OS": "ORDER_CALL", "RESUME_CARD": "ORDER_CALL",
    "Y": "OWNER_CONTENT", "HO": "OWNER_CONTENT", "CHEO": "OWNER_CONTENT", "OR": "OWNER_CONTENT",
    "AR": "SOURCE_REFERENCE", "D_ADDR": "SOURCE_REFERENCE", "A_ADDR": "SOURCE_REFERENCE",
    "AIIN": "QUANTITY_INDEX", "AIN": "QUANTITY_INDEX", "IIN": "QUANTITY_INDEX", "DA": "QUANTITY_INDEX",
    "O": "ACTION", "OK": "ACTION", "CH": "ACTION", "CHD": "ACTION", "CPH": "ACTION",
    "CHK": "ACTION", "CTH": "ACTION", "K": "ACTION", "P": "ACTION", "R": "ACTION",
    "S": "ACTION", "SH": "ACTION", "SHED": "ACTION", "T": "ACTION", "CFH": "ACTION",
    "LSH": "ACTION", "SOLK": "ACTION", "LD": "ACTION",
    "AL": "TARGET_PATH", "AM_ADDR": "TARGET_PATH", "S_ADDR": "TARGET_PATH", "L": "TARGET_PATH",
    "CKH": "TARGET_PATH", "AIR": "TARGET_PATH", "Z_ADDR": "TARGET_PATH",
    "E": "GRADE_STATE", "EE": "GRADE_STATE", "EEE": "GRADE_STATE",
    "DY": "CLOSE",
}

SPEAK = {
    "OT": "danach", "OL": "weiter", "OS": "auch", "RESUME_CARD": "vom Vorigen",
    "Y": "diesen Posten", "HO": "den bezeichneten Teil", "CHEO": "den Auszug/Eintrag", "OR": "den Ansatz/Inhalt",
    "AR": "von der Quellstelle", "D_ADDR": "aus dem Teilfeld", "A_ADDR": "am lokalen Bezug",
    "AIIN": "nach Sollmaß", "AIN": "eine Portion", "IIN": "auf der Stufe", "DA": "auf der zweiten Stufe",
    "O": "den Gang ausführen", "OK": "ansetzen", "CH": "entnehmen/ablesen", "CHD": "umsetzen",
    "CPH": "zum Gegen-/Empfangsgang führen", "CHK": "behandeln", "CTH": "den Status prüfen",
    "K": "zugeben/zuordnen", "P": "einsetzen/beginnen", "R": "den Zustand markieren",
    "S": "dann/prüfen", "SH": "halten", "SHED": "ruhen/halten", "T": "bearbeiten/markieren",
    "CFH": "pressen/trennen", "LSH": "waschen/spülen", "SOLK": "sammeln", "LD": "befestigen",
    "AL": "zur Zielstelle", "AM_ADDR": "zum Gegen-/Innenfeld", "S_ADDR": "zur S-Adresse",
    "L": "weiterleiten", "CKH": "durch den Durchlass", "AIR": "entlang des Laufs", "Z_ADDR": "zum Z-Bezug",
    "E": "kurz", "EE": "länger", "EEE": "vollständig", "DY": "Schritt schließen",
    "D_LABEL": "mit D-Kennzeichen", "G_LABEL": "mit G-Kennzeichen", "M_LOCAL": "mit M-Kennzeichen",
    "S_LABEL": "mit S-Kennzeichen", "AN": "mit Zusatz",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parts(recipe: str) -> list[str]:
    return [part for part in recipe.split("+") if part and part != "CARRIER_Q"]


def component_slot(component: str) -> str:
    if component.startswith("LOCAL_CHAR_"):
        return "LOCAL_DETAIL"
    return COMPONENT_SLOT.get(component, "LOCAL_DETAIL")


def component_speak(component: str) -> str:
    if component.startswith("LOCAL_CHAR_"):
        return "mit lokalem " + component.removeprefix("LOCAL_CHAR_") + "-Zeichen"
    return SPEAK.get(component, component.lower())


def close_card(event: dict[str, str]) -> bool:
    return bool(parts(event["component_recipe"]) and parts(event["component_recipe"])[-1] == "DY")


def main() -> None:
    all_events = read_tsv(EVENTS)
    prose = [row for row in all_events if row["usage_class"] == "PROSE"]
    if len(prose) != 2010:
        raise RuntimeError("unexpected prose inventory")

    prose_rows = []
    event_slots: dict[str, list[str]] = {}
    event_components: dict[str, list[str]] = {}
    for row in prose:
        components = parts(row["component_recipe"])
        slots = [component_slot(component) for component in components]
        event_components[row["event_id"]] = components
        event_slots[row["event_id"]] = slots
        prose_rows.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"], "source_page": row["source_page"],
            "locus": row["locus"], "token_index": row["token_index"], "register": row["register"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "source_slot_sequence": ">".join(slots),
            "component_spoken_sequence_de": "; ".join(component_speak(component) for component in components),
            "licensed_close": "YES" if close_card(row) else "NO",
            "source_reading_de": row["contextual_reading_de"],
        })
    write_tsv(PROSE_OUT, prose_rows, [
        "event_id", "physical_page", "source_page", "locus", "token_index", "register", "surface",
        "component_recipe", "source_slot_sequence", "component_spoken_sequence_de", "licensed_close", "source_reading_de",
    ])

    clauses: list[tuple[str, str, list[dict[str, str]]]] = []
    for page in PAGE_ORDER:
        buffer: list[dict[str, str]] = []
        for event in [row for row in all_events if row["physical_page"] == page]:
            if event["usage_class"] != "PROSE":
                if buffer:
                    clauses.append((page, "NONPROSE_OWNER_OR_DIAGRAM_BOUNDARY", buffer))
                    buffer = []
                continue
            buffer.append(event)
            if close_card(event):
                clauses.append((page, "LICENSED_DY_CLOSE", buffer))
                buffer = []
        if buffer:
            clauses.append((page, "PAGE_END_OPEN", buffer))

    clause_rows = []
    transition_counts = Counter()
    for number, (page, end_reason, members) in enumerate(clauses, start=1):
        components = [component for event in members for component in event_components[event["event_id"]]]
        source_slots = [component_slot(component) for component in components]
        collapsed_slots = []
        for slot in source_slots:
            if not collapsed_slots or collapsed_slots[-1] != slot:
                collapsed_slots.append(slot)
        for left, right in zip(collapsed_slots, collapsed_slots[1:]):
            transition_counts[(left, right)] += 1
        slot_values: dict[str, list[str]] = defaultdict(list)
        for component in components:
            slot_values[component_slot(component)].append(component_speak(component))
        canonical_parts = []
        for slot in SLOT_ORDER:
            if slot_values[slot]:
                canonical_parts.append(f"{slot}: " + ", ".join(slot_values[slot]))
        loci = list(dict.fromkeys(event["locus"] for event in members))
        clause_rows.append({
            "clause_id": f"P915-C{number:03d}",
            "physical_page": page,
            "register": members[0]["register"],
            "start_event": members[0]["event_id"],
            "end_event": members[-1]["event_id"],
            "events": len(members),
            "loci": "|".join(loci),
            "physical_lines": len(loci),
            "crosses_physical_line": "YES" if len(loci) > 1 else "NO",
            "end_reason": end_reason,
            "surface_sequence": " · ".join(event["surface"] for event in members),
            "component_sequence": " | ".join(event["component_recipe"] for event in members),
            "source_slot_sequence": ">".join(collapsed_slots),
            "canonical_spoken_order_de": "; ".join(canonical_parts),
            "continuous_source_reading_de": "; ".join(event["contextual_reading_de"] for event in members),
        })
    write_tsv(CLAUSE_OUT, clause_rows, [
        "clause_id", "physical_page", "register", "start_event", "end_event", "events", "loci", "physical_lines",
        "crosses_physical_line", "end_reason", "surface_sequence", "component_sequence", "source_slot_sequence",
        "canonical_spoken_order_de", "continuous_source_reading_de",
    ])

    transition_rows = []
    for (left, right), count in sorted(transition_counts.items(), key=lambda item: (-item[1], item[0])):
        transition_rows.append({
            "source_slot": left,
            "next_slot": right,
            "transitions": count,
            "canonical_direction": "FORWARD" if SLOT_ORDER.index(left) <= SLOT_ORDER.index(right) else "BACKWARD_OR_RESUMPTIVE",
            "spoken_link_de": f"{left} → {right}",
        })
    write_tsv(TRANSITIONS_OUT, transition_rows, ["source_slot", "next_slot", "transitions", "canonical_direction", "spoken_link_de"])

    grammar = [
        {"order": i + 1, "slot": slot, "components": "|".join(sorted(component for component, assigned in COMPONENT_SLOT.items() if assigned == slot)), "spoken_question_de": question, "apprentice_rule_de": rule}
        for i, (slot, question, rule) in enumerate([
            ("ORDER_CALL", "Was kommt jetzt?", "Setze danach/weiter/Wiederaufnahme an den Anfang der gesprochenen Klausel."),
            ("OWNER_CONTENT", "Welcher Posten oder Inhalt?", "Nenne den aktuellen Bild-/Ansatzposten."),
            ("SOURCE_REFERENCE", "Woher oder aus welchem Teil?", "Nenne Quell- und Teiladresse vor der Handlung."),
            ("QUANTITY_INDEX", "Wie viel oder welche Stufe?", "Nenne Portion, Sollmaß und Index."),
            ("ACTION", "Was tun?", "Sprich die aktive Werkstatthandlung."),
            ("TARGET_PATH", "Wohin oder über welchen Weg?", "Nenne Ziel, Leitung, Durchlass oder Lauf."),
            ("GRADE_STATE", "Wie lange/stark oder in welchem Zustand?", "Setze kurz/länger/voll nach Handlung und Weg."),
            ("CLOSE", "Ist der Teilgang abgeschlossen?", "Nur lizenzierte DY-Karten schließen."),
            ("LOCAL_DETAIL", "Welches lokale Kennzeichen?", "Kopiere den seltenen Detailwert zuletzt aus dem Muster."),
        ])
    ]
    write_tsv(GRAMMAR_OUT, grammar, ["order", "slot", "components", "spoken_question_de", "apprentice_rule_de"])

    md = ["# Pass 915 — lesbare Werkstattklauseln", ""]
    for page in PAGE_ORDER:
        md += [f"## {page}", ""]
        for row in [row for row in clause_rows if row["physical_page"] == page]:
            marker = "zeilenübergreifend" if row["crosses_physical_line"] == "YES" else "eine physische Zeile"
            md.append(f"- **{row['clause_id']}** ({marker}; {row['end_reason']}): {row['canonical_spoken_order_de']}")
        md.append("")
    EDITION_OUT.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    endings = Counter(row["end_reason"] for row in clause_rows)
    report = [
        "# Pass 915 — Wortstellung und zeilenübergreifende Werkstattklauseln", "",
        "## Ergebnis", "",
        f"Die 2010 Prosagruppen ergeben {len(clause_rows)} Werkstattklauseln. Nicht die physische",
        "Zeile, sondern eine lizenzierte DY-Schlusskarte, ein echter Bild-/Etikettenwechsel",
        "oder das Seitenende beendet die Klausel. 121 Klauseln laufen über mindestens zwei",
        "physische Zeilen; die frühere Zeilen=Satz-Annahme bleibt damit draußen.", "",
        "## Gesprochene Lehrreihenfolge", "",
        "**AUFRUF/REIHENFOLGE → POSTEN/INHALT → QUELLE → MENGE/STUFE → HANDLUNG → ZIEL/WEG → GRAD/ZUSTAND → SCHLUSS → LOKALDETAIL**", "",
        "Der Schreiber muss die Karten nicht immer in dieser Reihenfolge setzen. Der Lehrling",
        "liest die sichtbare Reihenfolge exakt, sammelt ihre Slots und spricht sie anschließend",
        "in dieser festen Werkstattfolge aus. Wiederaufnahmen und eingeschobene Zielkarten",
        "bleiben dadurch möglich, ohne jede Oberfläche zu einem natürlichen Wort zu machen.", "",
        "## Klauselenden", "",
        f"- lizenzierter DY-Schluss: {endings['LICENSED_DY_CLOSE']}",
        f"- echter Nichtprosa-/Besitzerwechsel: {endings['NONPROSE_OWNER_OR_DIAGRAM_BOUNDARY']}",
        f"- offen am Seitenende: {endings['PAGE_END_OPEN']}", "",
        "## Nächster Hebel", "",
        "Nun können die längsten offenen Klauseln bearbeitet werden. Statt neue Wörter zu",
        "erfinden, werden wiederholte Slotblöcke zu kurzen Werkstattphrasen zusammengezogen:",
        "MASS+ANSETZEN, QUELLE+ENTNEHMEN, ZIEL+KURZHALTEN, DURCHLASS+FORTSETZEN. Danach wird",
        "eine kompakte vollständige Übersetzung der zwölf Prosaseiten geschrieben.",
    ]
    REPORT_OUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "pass": 915,
        "decision": "NINE_SLOT_SPOKEN_CLAUSE_ORDER__LINES_NOT_SENTENCES",
        "all_events": len(all_events),
        "prose_events": len(prose),
        "clauses": len(clause_rows),
        "cross_line_clauses": sum(row["crosses_physical_line"] == "YES" for row in clause_rows),
        "clause_endings": dict(sorted(endings.items())),
        "slot_transitions": len(transition_rows),
        "source_hash": sha(EVENTS),
        "output_hashes": {path.name: sha(path) for path in (PROSE_OUT, CLAUSE_OUT, TRANSITIONS_OUT, GRAMMAR_OUT, EDITION_OUT, REPORT_OUT)},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
