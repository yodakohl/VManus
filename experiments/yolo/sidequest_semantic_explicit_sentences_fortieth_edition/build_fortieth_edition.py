#!/usr/bin/env python3
"""Restore the four memory values into every abbreviated prose statement."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MEMORY = ROOT / "experiments/yolo/sidequest_semantic_scribe_memory_thirty_ninth_edition/THIRTY_NINTH_116_MEMORY_TRANSITIONS.tsv"


OWNER_DE = {
    "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB": "der ganzen breitblättrigen gezähnten Bildpflanze",
    "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT": "der ganzen dicht blau bekrönten Bildpflanze",
    "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB": "der ganzen mehrköpfigen stacheligen Bildpflanze",
    "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT": "der ganzen breitblättrigen rispigen Bildpflanze",
    "B1_SHARED_TWO_ROW_POOL": "dem gemeinsamen zweireihigen Becken",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "den oberen Paarbecken mit Zylinder",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "der mittleren linken Vorrichtung mit Zwischenknoten",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "der mittleren rechten Station",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "dem unteren grünen Mehrfigurenbecken",
    "B2_LOWER_POOL_EDGE_STATIONS": "den Randstationen des unteren Beckens",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "der oberen offenen Fächerstation",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "der mittleren runden Gefäßstation",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "der unteren korbförmigen Gefäßstation",
    "B3_MAIN_ARCH_LINKED_PAIR": "dem verbundenen Hauptbogenpaar",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "der Lücke zwischen Randstation und Hauptbogen",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "der linken offenen Randstation",
    "B4_MAIN_ARCH_LINKED_PAIR": "dem verbundenen Hauptbogenpaar",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "der rechten S-förmigen Mehrfachstation",
    "B5_LEFT_OPEN_FRINGE_STATION": "der linken offenen Randstation",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "der rechten S-förmigen Mehrfachstation",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def human_slot(value: str, kind: str) -> str:
    if value in {"LEER", "UNSET"}:
        return ""
    match = re.search(r"([A-Z][0-9]):[ITO](\d+)", value)
    if match:
        record, number = match.groups()
        number = str(int(number))
        nouns = {"active": "Arbeitsposten", "target": "Zielstelle", "previous": "Vorposten"}
        return f"{nouns[kind]} {record}-{number}"
    return value


def owner_phrase(owner: str) -> str:
    parts = owner.split("|")
    spoken = [OWNER_DE.get(part, part.lower().replace("_", " ")) for part in parts]
    if len(spoken) == 1:
        return spoken[0]
    return f"zuerst {spoken[0]}, dann {spoken[-1]}"


def main() -> None:
    memory = read_tsv(MEMORY)
    rows: list[dict[str, object]] = []
    restored_counts: Counter[str] = Counter()
    for row in memory:
        owner = owner_phrase(row["visible_owner_post"])
        active_raw = row["active_pre"] if row["active_pre"] != "LEER" else row["active_post"]
        target_raw = row["target_pre"] if row["target_pre"] != "LEER" else (
            row["target_post"] if row["target_operation"] in {"INTRODUCE", "RESUME"} else "LEER"
        )
        previous_raw = row["previous_pre"] if row["previous_pre"] != "LEER" else (
            row["previous_post"] if row["previous_operation"] in {"INTRODUCE", "RESUME"} else "LEER"
        )
        active = human_slot(active_raw, "active")
        target = human_slot(target_raw, "target")
        previous = human_slot(previous_raw, "previous")
        clauses = [f"Der Text gehört zu {owner}"]
        supplied = ["OWNER"]
        if active:
            clauses.append(f"der laufende Gegenstand ist {active}")
            supplied.append("ACTIVE")
        if target:
            clauses.append(f"die geltende Zieladresse ist {target}")
            supplied.append("TARGET")
        if previous:
            clauses.append(f"‚das Vorige‘ bezeichnet {previous}")
            supplied.append("PREVIOUS")
        for slot in supplied:
            restored_counts[slot] += 1
        memory_preamble = "; ".join(clauses) + "."
        expanded = row["expanded_workshop_reading_de"].strip()
        if expanded and expanded[-1] not in ".!?":
            expanded += "."
        full = f"{memory_preamble} {expanded}"
        rows.append({
            "sequence": row["sequence"],
            "statement_id": row["statement_id"],
            "record_id": row["record_id"],
            "page": row["page"],
            "surface_sequence": row["surface_sequence"],
            "atom_sequence": row["atom_sequence"],
            "literal_visible_reading_de": row["literal_card_reading_de"],
            "memory_values_restored": "|".join(supplied),
            "owner_expansion_de": owner,
            "active_expansion_de": active or "NICHT_BENÖTIGT",
            "target_expansion_de": target or "NICHT_BENÖTIGT",
            "previous_expansion_de": previous or "NICHT_BENÖTIGT",
            "fully_explicit_apprentice_sentence_de": full,
            "fluent_workshop_sentence_de": expanded,
            "macro_program": row["macro_program"],
            "what_remains_learned": "BILDOWNER_UND_LOKALER_GANZKARTENINHALT",
        })
    write_tsv(OUT / "FORTIETH_116_EXPLICIT_SENTENCES.tsv", rows)

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_record[str(row["record_id"])].append(row)
    lines = [
        "# Elf vollständig ausgesprochene Prosa-Records",
        "",
        "Jede Aussage wird zuerst als sichtbare Kartenfolge und dann mit den vier",
        "aus der Merktafel ergänzten Referenten gezeigt. Die Wiederholung der Referenten",
        "ist absichtlich schulmeisterlich; ein geübter Leser darf sie wieder elliptisch sprechen.",
        "",
    ]
    for record_id, record_rows in by_record.items():
        lines.extend([f"## {record_id} — {record_rows[0]['page']}", ""])
        for row in record_rows:
            lines.extend([
                f"### {row['statement_id']}",
                "",
                f"Sichtbar: `{row['surface_sequence']}`",
                "",
                f"Ausgesprochen: {row['fully_explicit_apprentice_sentence_de']}",
                "",
            ])
    (OUT / "FORTIETH_11_EXPLICIT_RECORDS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    guide = [
        "# Vom Kartenfeld zum vollständigen Satz",
        "",
        "Die ausgeschriebene Form entsteht in drei Schritten:",
        "",
        "1. Lies die sichtbaren Karten und Prozessmakros.",
        "2. Setze OWNER, ACTIVE, TARGET und PREVIOUS aus der Vierfach-Merktafel ein, sofern der Satz sie benutzt.",
        "3. Ergänze erst danach die konkrete Bildsache aus dem gelernten Exemplar.",
        "",
        "Damit bleibt etwa `AL` nur Zieladresse, nicht ‚unteres Becken‘; erst der sichtbare Besitzer",
        "macht daraus die konkrete Öffnung oder Schale. Ebenso bleibt `Y` der laufende Posten und",
        "wird erst durch ACTIVE zu einem bestimmten Auszug, Stoffanteil oder Stationswert.",
        "",
        "## Ergänzungsumfang",
        "",
    ]
    for slot in ("OWNER", "ACTIVE", "TARGET", "PREVIOUS"):
        guide.append(f"- {slot}: in {restored_counts[slot]} von 116 Aussagen ausdrücklich eingesetzt.")
    (OUT / "FORTIETH_EXPANSION_GUIDE.md").write_text("\n".join(guide).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "statements": len(rows),
            "records": len(by_record),
            "surface_groups": sum(len(str(row["surface_sequence"]).split()) for row in rows),
            "restored_slot_mentions": dict(restored_counts),
            "fully_explicit_sentences": sum(bool(row["fully_explicit_apprentice_sentence_de"]) for row in rows),
        },
        "source": {str(MEMORY.relative_to(ROOT)): sha256(MEMORY)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
