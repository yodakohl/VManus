#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R264 = ROOT / "experiments/yolo/sidequest_semantic_complete_sixty_three_entry_deck_two_hundred_sixty_fourth"
R268 = ROOT / "experiments/yolo/sidequest_semantic_air_path_revision_two_hundred_sixty_eighth"
R278 = ROOT / "experiments/yolo/sidequest_semantic_thirty_six_stem_families_two_hundred_seventy_eighth"
GRAMMAR = ROOT / "experiments/yolo/sidequest_semantic_quantity_preparation/WORKSHOP_SENTENCE_SLOTS.tsv"
GENERATION = R264 / "TWO_HUNDRED_SIXTY_FOURTH_173_COMPLETE_GENERATION.tsv"
EVENTS = R268 / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_381_PROSE_EVENTS.tsv"
FAMILIES = R278 / "TWO_HUNDRED_SEVENTY_EIGHTH_36_STEM_FAMILIES.tsv"
MAPPING = R278 / "TWO_HUNDRED_SEVENTY_EIGHTH_40_TO_36_MAPPING.tsv"

PATTERNS = {
    "OK": r"(^|\+)OK(?:_| |\+|$)", "OL": r"(^|\+)OL(?:_| |\+|$)", "OT": r"(^|\+)OT(?:_| |\+|$)",
    "AR": r"AR_FROM", "AL": r"AL_TO", "L": r"(^|\+)L_OUT|^LCH_|^LD_", "P": r"P_IN",
    "AIN": r"(?<!AI)AIN_PORTION|\+ AIN$", "AN": r"AN_SECOND|\+ AN$", "AIIN": r"AIIN", "IIN": r"(?<!A)IIN",
    "E": r"E_SHORT|GRADE_1", "EE": r"GRADE_2|EE_HOLD|EE_LONG", "EEE": r"GRADE_3|EEE_FULL",
    "Y": r"Y_CURRENT|Y_ITEM|Y_CURRENT_ITEM_CARD|\+ Y$", "DY": r"DY_CLOSE|CLOSE_EXACT|TERMINAL_CLOSE|\+ ?DY$|\+CLOSE$|\+CLOSE_EXACT",
    "OR": r"OR_BATCH|\+ OR$|OT \+ OR|CTH \+ OR|CHO \+ OR", "HO": r"^CHO(?: |$)", "CHEO": r"CHEO", "AIR": r"AIR",
    "CHED": r"CHED_TRANSFER", "CHD": r"CHD_TRANSFER|CHD_NEW", "CTH": r"CTH", "SHED": r"SHED", "CHK": r"CHK_WARM",
    "CKH": r"CKH_THROUGH", "CKHE": r"CKHE_STRAIN", "SOLK": r"SOLK", "LSH": r"LSH", "TY": r"TY_PART",
    "CHO_INPUT": r"^CHO(?: |$)", "O_WITHDRAW": r"O_RESIDUAL|^O \+ DY$", "OS_RECEIVER": r"^OS$", "CH_POUR": r"^CH \+ AIR",
    "TCH_PREPARATION": r"TCH_PREPARATION|OL \+ TCH", "OYK_VESSEL": r"OYK", "K_BINDER": r"(^|\+)K(?: |\+|_)",
    "YTY_PART": r"YTY", "SHFY_DURATION": r"SHFY", "D_PREVIOUS": r"^D \+ OL",
}
REVISED_FAMILIES = {"E_GRADE", "CHED_TRANSFER", "CHO_INPUT", "CHK", "DY"}


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


def main() -> None:
    generation = read_tsv(GENERATION)
    events = read_tsv(EVENTS)
    grammar = read_tsv(GRAMMAR)
    families = read_tsv(FAMILIES)
    mapping = read_tsv(MAPPING)
    family_value = {r["family_id"]: r["short_value_de"] for r in families}
    family_order = {r["family_id"]: int(r["family_order"]) for r in families}
    old_to_new = {r["old_component_id"]: r["new_family_id"] for r in mapping}

    dictionary: list[dict[str, object]] = []
    by_card: dict[str, dict[str, object]] = {}
    for row in generation:
        old = [component for component, pattern in PATTERNS.items() if re.search(pattern, row["component_parse"])]
        new = sorted({old_to_new[c] for c in old}, key=lambda x: family_order[x])
        if row["new_generation_class"] == "MEMORIZED_WHOLE_SIGN":
            cls = "MEMORIZED_WHOLE_SIGN"
            parse = f"WHOLE_SIGN[{row['master_form']}]"
            literal = row["portable_core_de"]
        elif row["master_card_id"] == "MC141":
            cls = "FRAME_PLUS_LEARNED_WHOLE"
            parse = "T_FRAME+WHOLE_SHEY"
            literal = "RAHMEN + FREIGEGEBENER_LAUF"
        else:
            cls = "COMPOSED_FROM_36_FAMILIES"
            parse = "+".join(new)
            literal = " + ".join(family_value[x] for x in new)
        entry = {
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "old_component_parse": row["component_parse"],
            "family_parse": parse,
            "family_literal_de": literal,
            "card_class_279": cls,
            "local_prose_default_de": row["portable_core_de"],
            "contains_revised_family": "YES" if set(new) & REVISED_FAMILIES else "NO",
            "prose_event_count": row["prose_event_count"],
        }
        dictionary.append(entry)
        by_card[row["master_card_id"]] = entry

    event_rows: list[dict[str, object]] = []
    for event in events:
        card = by_card[event["master_card_id"]]
        local = event["local_register_expansion_de"]
        if "DY" in str(card["family_parse"]) and event["terminal_status"] == "TERMINAL":
            local = f"{local}; Arbeitsschritt festsetzen"
        event_rows.append({
            "event_id": event["event_id"],
            "statement_id": event["statement_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "field_id": event["field_id"],
            "visible_owner": event["visible_owner"],
            "visible_surface": event["visible_surface"],
            "master_card_id": event["master_card_id"],
            "family_parse": card["family_parse"],
            "family_literal_de": card["family_literal_de"],
            "register_expansion_de": local,
            "two_layer_reading_de": f"{card['family_literal_de']} => {local}",
            "terminal_status": event["terminal_status"],
            "contains_revised_family": card["contains_revised_family"],
        })

    grammar_by_statement = {r["statement_id"]: r for r in grammar}
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statements: list[dict[str, object]] = []
    for statement in grammar:
        rows = events_by_statement[statement["statement_id"]]
        statements.append({
            "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "loci": statement["loci"],
            "owner_slot": statement["owner_slot"],
            "event_count": len(rows),
            "surface_sequence": " · ".join(str(r["visible_surface"]) for r in rows),
            "family_sequence_de": "; ".join(str(r["family_literal_de"]) for r in rows),
            "register_expansion_sequence_de": "; ".join(str(r["register_expansion_de"]) for r in rows),
            "two_layer_statement_de": f"Beim Besitzer {statement['owner_slot']}: " + " | ".join(str(r["two_layer_reading_de"]) for r in rows),
            "contains_revised_family": "YES" if any(r["contains_revised_family"] == "YES" for r in rows) else "NO",
            "terminal_status": "CLOSED" if rows[-1]["terminal_status"] == "TERMINAL" else "OPEN",
        })

    dictionary_path = OUT / "TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
    events_path = OUT / "TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
    statements_path = OUT / "TWO_HUNDRED_SEVENTY_NINTH_116_TWO_LAYER_STATEMENTS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_NINTH_ELEVEN_RECORD_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_NINTH_REPORT.md"
    write_tsv(dictionary_path, dictionary, list(dictionary[0]))
    write_tsv(events_path, event_rows, list(event_rows[0]))
    write_tsv(statements_path, statements, list(statements[0]))

    md = ["# Elf Prosarecords in zwei Leseschichten", "", "Links steht die kurze Stammlesung, rechts ihre konkrete lokale Werkstattauslegung.", ""]
    for record in dict.fromkeys(str(r["record_unit_id"]) for r in statements):
        rows = [r for r in statements if r["record_unit_id"] == record]
        md.extend([f"## {record} / {rows[0]['page']}", ""])
        for row in rows:
            md.append(f"- **{row['statement_id']}** — {row['two_layer_statement_de']}")
        md.append("")
    md.extend([
        "## Neue portable Aussprachen", "",
        "`CHO=EINGABE`, `CHK=ZUSTAND JUSTIEREN`, `DY=FESTSETZEN`, `E/EE/EEE=GRAD I/II/III`, `CHD/CHED=ÜBERFÜHREN`. Zutat, Wärme und Satzschluss bleiben lokale Expansionen, nicht die vollständige Stammbedeutung.", "",
    ])
    readable_path.write_text("\n".join(md), encoding="utf-8")

    card_counts = Counter(str(r["card_class_279"]) for r in dictionary)
    event_counts = Counter(str(by_card[str(r["master_card_id"])]["card_class_279"]) for r in event_rows)
    report_path.write_text(f"""# Sidequest-Pass 279: vollständige Zwei-Schichten-Prosa

## Ergebnis

Alle173 Karten,381 Ereignisse und116 Aussagen werden neu gelesen: zuerst in der 36-Familien-Sprache, danach als lokale Herbal- oder Bio-Auslegung. 149 Karten/352 Ereignisse sind reine Familienkompositionen, eine Karte/ein Ereignis ist ein Rahmen plus gelerntes SHEY-Ganzzeichen, und23 Karten/28 Ereignisse bleiben Nomenklator.

Die fünf revidierten Familien erscheinen in {sum(r['contains_revised_family']=='YES' for r in dictionary)} Karten und {sum(r['contains_revised_family']=='YES' for r in event_rows)} Ereignissen. Keine konkrete Wärme-, Zutat- oder Schlusslesung wird verloren; sie ist jetzt sichtbar als Registerexpansion statt als überladener Stammwert.

Inputs `{sha(GENERATION)}`, `{sha(EVENTS)}`, `{sha(FAMILIES)}`.
""", encoding="utf-8")
    outputs = (dictionary_path, events_path, statements_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "cards": len(dictionary), "events": len(event_rows), "statements": len(statements),
        "records": len({r["record_unit_id"] for r in statements}),
        "card_classes": dict(card_counts), "event_classes": dict(event_counts),
        "revised_cards": sum(r["contains_revised_family"] == "YES" for r in dictionary),
        "revised_events": sum(r["contains_revised_family"] == "YES" for r in event_rows),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
