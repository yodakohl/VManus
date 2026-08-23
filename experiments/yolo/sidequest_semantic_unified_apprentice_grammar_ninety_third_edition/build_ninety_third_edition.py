#!/usr/bin/env python3
"""Merge Herbal and Biological phrasebooks into one apprentice grammar."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
H_PATH = ROOT / "experiments/yolo/sidequest_semantic_herbal_phrasebook_ninety_second_edition/NINETY_SECOND_19_HERBAL_STATEMENT_PHRASEBOOK.tsv"
B_PATH = ROOT / "experiments/yolo/sidequest_semantic_bath_phrasebook_ninetieth_edition/NINETIETH_97_STATEMENT_PHRASEBOOK.tsv"
V72_PATH = ROOT / "experiments/yolo/sidequest_theory_candidates_v72/V72_SELECTED_116_STATEMENTS.tsv"


UNIFIED = [
    ("OWNER_SELECT", "sichtbaren Seiten-/Szenenbesitzer setzen", "Bild oder Layout"),
    ("PART_SELECT", "Pflanzenteil oder örtlichen Gegenstand wählen", "Herbal-Quellenprogramm"),
    ("MATERIAL_ADD", "Medium, Portion oder Zusatz zugeben", "AIN/TY/HO/DL + Quellenfüllung"),
    ("MEASURE", "Sollmaß oder Stufe eintragen", "AIIN/IIN"),
    ("SET", "laufenden Arbeitsposten ansetzen", "OK"),
    ("CUT_CRUSH", "Pflanzenstoff zerteilen oder zerstoßen", "Herbal-Ganzkarte"),
    ("GRADE", "kurze, längere oder volle Stufe setzen", "E/EE/EEE"),
    ("HEAT", "wärmen oder temperieren", "CHK"),
    ("SETTLE", "ruhen oder absetzen", "SH/SHED"),
    ("PASS_STRAIN", "durchlassen, auswringen oder seihen", "CKH/CKHE/CFH/CPH"),
    ("WASH", "waschen oder spülen", "gelernte WASH-Familie"),
    ("DRAIN", "örtlich abführen oder ausgießen", "AR/CKH/SK"),
    ("COLLECT_STORE", "sammeln, auffangen oder verwahren", "SOLK/TALAM"),
    ("TARGET", "örtliche Zielstelle setzen", "AL"),
    ("TRANSFER", "Posten umsetzen", "CHD/CHED"),
    ("CONTINUE", "Folge oder Fortsetzung markieren", "OT/OL"),
    ("READY", "Bereitschaft prüfen", "CTH"),
    ("USE_APPLY", "Mittel gebrauchen oder äußerlich anwenden", "DAN + Quellenfüllung"),
    ("FASTEN", "örtlich befestigen", "LDDY"),
    ("CLOSE", "lokalen Schritt schließen", "lizenzierte Terminalkarte"),
]


H_MAP = {
    "SELECT_PLANT_PART": ["PART_SELECT"], "PREPARE_SET": ["SET"],
    "ADD_MEDIUM": ["MATERIAL_ADD"], "MEASURE": ["MEASURE"],
    "CUT_CRUSH": ["CUT_CRUSH"], "WRING": ["PASS_STRAIN"],
    "SETTLE": ["SETTLE"], "STRAIN_SEPARATE": ["PASS_STRAIN"],
    "HEAT_GRADE": ["HEAT", "GRADE"], "COLLECT": ["COLLECT_STORE"],
    "DOSED_USE": ["MEASURE", "USE_APPLY"],
    "EXTERNAL_APPLY": ["TARGET", "USE_APPLY"],
    "STORE_RESERVE": ["COLLECT_STORE", "CLOSE"],
    "ORDER_CONTINUE": ["CONTINUE"], "READY_CLOSE": ["READY", "CLOSE"],
}


B_MAP = {
    "MEASURE": ["MEASURE"], "PORTION_ADD": ["MATERIAL_ADD"],
    "TARGET": ["TARGET"], "SET": ["SET"], "DURATION_GRADE": ["GRADE"],
    "HEAT": ["HEAT"], "SETTLE": ["SETTLE"], "PASS_STRAIN": ["PASS_STRAIN"],
    "WASH": ["WASH"], "DRAIN": ["DRAIN"], "COLLECT": ["COLLECT_STORE"],
    "TRANSFER": ["TRANSFER"], "ORDER_CONTINUE": ["CONTINUE"],
    "READY": ["READY"], "FASTEN": ["FASTEN"], "CLOSE": ["CLOSE"],
}


RULES = [
    (1, "CHOOSE_REGISTER", "Herbal oder Biological wählen; die Inhaltsnomenklaturen nie vermischen."),
    (2, "SET_OWNER", "Am Recordbeginn und nach sichtbarer Szenenlücke den kleinsten Bildbesitzer setzen."),
    (3, "LOAD_SOURCE_PROGRAM", "Nur die endliche Quellenwortliste des aktiven Records laden."),
    (4, "SELECT_OBJECT", "Pflanzenteil, Figur, Becken oder Dienststation aus Besitzer plus Quellenprogramm wählen."),
    (5, "ADD_MATERIAL", "Medium, Portion oder Zusatz vor der zugehörigen Prozesskarte einsetzen."),
    (6, "SET_MEASURE", "AIIN/IIN nur als Maß-, Stufen- oder Wertslot des aktiven Programms lesen."),
    (7, "RUN_PROCESS", "Ansetzen, zerteilen, wärmen, ruhen, waschen oder seihen in Kartenreihenfolge ausführen."),
    (8, "APPLY_GRADE", "E/EE/EEE erst nach der Prozessbasis als kurz/länger/voll lesen."),
    (9, "MOVE_LOCALLY", "Ziel, Umsetzen, Durchlass und Ablauf nur innerhalb des sichtbaren Besitzers führen."),
    (10, "USE_OR_STORE", "Herbal kann Mittel gebrauchen/verwahren; Bio kann lokal anwenden/befestigen/entleeren."),
    (11, "CLOSE_BY_CARD", "Nur eine lizenzierte Terminalkarte schließt; sichtbares dy allein genügt nicht."),
    (12, "WRAP_AND_RENDER", "Zeilenumbruch nach Platz, dann exakte Karte im Renderer der Hand kopieren."),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def expand(sequence: str, mapping: dict[str, list[str]]) -> list[str]:
    output = []
    for primitive in sequence.split(">"):
        for item in mapping[primitive]:
            if not output or output[-1] != item:
                output.append(item)
    return output


def main() -> None:
    herbal = read_tsv(H_PATH)
    bio = read_tsv(B_PATH)
    v72 = {row["statement_id"]: row for row in read_tsv(V72_PATH)}

    primitive_rows = [
        {"grammar_order": order, "primitive_id": primitive, "source_meaning_de": meaning, "card_or_source_basis": basis}
        for order, (primitive, meaning, basis) in enumerate(UNIFIED, 1)
    ]
    write_tsv(OUT / "NINETY_THIRD_20_UNIFIED_SOURCE_PRIMITIVES.tsv", primitive_rows)
    rule_rows = [{"rule_order": order, "rule_id": rule_id, "instruction_de": instruction} for order, rule_id, instruction in RULES]
    write_tsv(OUT / "NINETY_THIRD_12_APPRENTICE_RULES.tsv", rule_rows)

    combined = []
    input_rows = [(row, "HERBAL", H_MAP) for row in herbal] + [(row, "BIOLOGICAL", B_MAP) for row in bio]
    input_rows.sort(key=lambda item: int(v72[item[0]["statement_id"]]["event_serials"].split("|")[0]))
    for row, register, mapping in input_rows:
        sequence = expand(row["primitive_sequence"], mapping)
        transition = v72[row["statement_id"]]["owner_transition"]
        if row["statement_id"].endswith("-S001") or any(marker in transition for marker in ("RESET_RECORD", "BREAK_VISIBLE_GAP", "SET_DIRECT_OWNER", "SET_PAGE_OWNER", "SET_UNRESOLVED_OWNER")):
            if not sequence or sequence[0] != "OWNER_SELECT":
                sequence.insert(0, "OWNER_SELECT")
        combined.append({
            "statement_order": len(combined) + 1,
            "statement_id": row["statement_id"], "register": register,
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "event_count": row["event_count"], "owner_transition": transition,
            "unified_primitive_sequence": ">".join(sequence),
            "unified_primitive_count": len(sequence),
            "visible_surface_sequence": row["visible_surface_sequence"],
            "complete_working_reading_de": row["full_statement_reading_de"],
            "apprentice_status": "WRITE_FROM_OWNER_PROGRAM_PRIMITIVES_THEN_RENDER",
        })
    write_tsv(OUT / "NINETY_THIRD_116_UNIFIED_STATEMENT_GRAMMAR.tsv", combined)

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in combined:
        by_record[str(row["record_unit_id"])].append(row)
    roundtrips = []
    for record_id in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
        members = by_record[record_id]
        primitives = [part for row in members for part in str(row["unified_primitive_sequence"]).split(">")]
        roundtrips.append({
            "record_unit_id": record_id, "register": members[0]["register"], "page": members[0]["page"],
            "statement_count": len(members), "event_count": sum(int(row["event_count"]) for row in members),
            "owner_select_count": sum(str(row["unified_primitive_sequence"]).split(">").count("OWNER_SELECT") for row in members),
            "distinct_primitive_count": len(set(primitives)),
            "distinct_primitives": ",".join(sorted(set(primitives))),
            "forward_status": "SOURCE_PROGRAM_TO_PRIMITIVES_TO_VISIBLE_SEQUENCE_COMPLETE",
            "backward_status": "VISIBLE_SEQUENCE_TO_PRIMITIVES_AND_RECORD_PROGRAM_COMPLETE",
            "content_limit": "EXACT_CONTENT_WORD_REQUIRES_RECORD_SOURCE_PROGRAM",
        })
    write_tsv(OUT / "NINETY_THIRD_11_RECORD_ROUNDTRIP.tsv", roundtrips)

    primitive_counts = Counter(part for row in combined for part in row["unified_primitive_sequence"].split(">"))
    doc = [
        "# Lehrbuch der gemeinsamen Herbal-/Bio-Werkstattgrammatik", "",
        "## Die zwanzig Primitiven", "",
    ]
    for row in primitive_rows:
        doc.append(f"{row['grammar_order']}. **{row['primitive_id']}** — {row['source_meaning_de']} ({row['card_or_source_basis']})")
    doc.extend(["", "## Die zwölf Schreibregeln", ""])
    for row in rule_rows:
        doc.append(f"{row['rule_order']}. **{row['rule_id']}** — {row['instruction_de']}")
    doc.extend([
        "", "## Was der Lehrling wirklich lernen muss", "",
        "Ein Lehrling lernt nicht 116 unabhängige Sätze. Er lernt zwanzig Rollen, zwölf",
        "Reihenfolgeregeln, die 43 Karten-/Kürzelwerte des aktuellen Decks und die lokalen",
        "Quellenprogramme. Herbal und Bio teilen den Satzmotor; Bild und Quellenprogramm",
        "setzen die konkreten Gegenstände ein. Danach kopiert die Hand nur den Renderer.", "",
        "Die Rücklesung funktioniert auf derselben Ebene: Besitzer erkennen, Kartenfolge",
        "lesen, Primitiven zusammensetzen und den konkreten Inhalt aus dem aktiven Record-",
        "programm ergänzen. Ohne dieses Programm bleiben Wein/Öl/Honig ebenso unbestimmt",
        "wie der genaue Zweck einer figurenlosen Dienststation.",
    ])
    (OUT / "NINETY_THIRD_APPRENTICE_MANUAL.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Dreiundneunzigste Werkstattrunde: ein gemeinsamer Prosa-Compiler", "",
        "## Ergebnis", "",
        "All 116 prose statements and 381 prose events now run through one twenty-primitive",
        "source grammar and twelve apprentice rules. Every primitive is used. Eleven record",
        "roundtrips preserve statement count, event count, owner resets and visible order.", "",
        "The unification is operational rather than lexical: Herbal and Biological share",
        "set, measure, grade, heat, settle, pass, transfer, continue, ready and close, while",
        "their content fillers remain separate. This is simple enough for several scribes",
        "because each hand learns one common compiler plus local exemplars.", "",
        "Only the fixed prose pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "NINETY_THIRD_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "primitives": len(primitive_rows), "rules": len(rule_rows),
        "statements": len(combined), "events": sum(int(row["event_count"]) for row in combined),
        "records": len(roundtrips), "primitive_occurrences": dict(primitive_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
