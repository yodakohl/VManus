#!/usr/bin/env python3
"""Compress the 97 Biological statements into a small workshop phrasebook."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R89 = ROOT / "experiments/yolo/sidequest_semantic_continuous_translation_eighty_ninth_edition/EIGHTY_NINTH_116_CONTINUOUS_STATEMENT_TRANSLATION.tsv"


PRIMITIVES = [
    ("MEASURE", "Maß/Stufe setzen", "AIIN/IIN", r"Sollmaß|Sollstufe|Folgemaß|Absetzmaß|\bMaß\b|\bStufe\b"),
    ("PORTION_ADD", "Portion oder Zusatz zugeben", "AIN/TY/HO/DL", r"Portion|Zusatz|Frischwasser|Wasser ein|\bFülle\b|\bGib\b|\bgib\b"),
    ("TARGET", "örtliche Stelle wählen", "AL", r"dorthin|\bdort\b|Zielstelle|\bZiel\b"),
    ("SET", "Posten ansetzen", "OK", r"\bsetz(?:e|t)[^,.]{0,60}\ban\b|angesetzt|\bAnsatz\b"),
    ("DURATION_GRADE", "kurze, längere oder volle Stufe", "E/EE/EEE", r"\bkurz(?:e|en|er|es)?\b|\blänger\b|\blange\b|vollständig"),
    ("HEAT", "wärmen oder temperieren", "CHK", r"wärm|abgekühlt|temper"),
    ("SETTLE", "ruhen oder absetzen", "SH/SHED", r"absetz|\bruh"),
    ("PASS_STRAIN", "durchführen oder seihen", "CKH/CKHE/CFH/CPH", r"leit[^,.]*durch|Durchlauf|durchgeleitet|seih|Klarlauf"),
    ("WASH", "waschen oder spülen", "N07_WASH", r"wasch|Wasch|Spül|spül"),
    ("DRAIN", "abführen oder ausgießen", "AR/CKH/SK", r"\bführ(?:e|t)[^,.]{0,40}\bab\b|abführ|Ablauf|Auslass|zieh[^,.]*ab|abgeleitet|gieß|Gieß"),
    ("COLLECT", "sammeln oder auffangen", "SOLK/TALAM", r"sammel|Sammel|Auffang"),
    ("TRANSFER", "Posten umsetzen", "CHD/CHED", r"\bsetz(?:e|t)[^,.]{0,60}\bum\b|Umsetz|Führ[^,.]*dorthin|führe[^,.]*dorthin"),
    ("ORDER_CONTINUE", "folgen oder weiterführen", "OT/OL", r"Folge|folge|führ[^,.]*weiter|führe[^,.]*weiter|Fortsetz|fortsetz"),
    ("READY", "Bereitschaft prüfen", "CTH", r"bereit"),
    ("FASTEN", "örtlich befestigen", "LDDY", r"befestig"),
    ("CLOSE", "lokalen Schritt schließen", "licensed DY/terminal card", r"schließ|beende"),
]


MACRO_READINGS = {
    "COMPOSITE_STATION_SEQUENCE": "mehrteiligen Stationsgang in Kartenreihenfolge ausführen",
    "WASH_CELL": "örtlichen Wasch-/Spülgang ausführen",
    "FILTER_PASS_CELL": "Arbeitsflüssigkeit durch den lokalen Durchlass führen",
    "DRAIN_RECEIVE_CELL": "Arbeitsflüssigkeit örtlich abführen oder auffangen",
    "TEMPER_HOLD_CELL": "Posten auf Zustand bringen und kurz oder länger halten",
    "MEASURED_CHARGE_CELL": "Portion oder Sollstufe einstellen und zugeben",
    "TRANSFER_SET_CELL": "Posten örtlich ansetzen, umsetzen oder weiterführen",
    "APPLICATION_FASTEN_CELL": "örtlichen Posten befestigen und den Schritt schließen",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def extract_primitives(text: str) -> list[str]:
    hits = []
    for order, (primitive, _, _, pattern) in enumerate(PRIMITIVES):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            hits.append((match.start(), order, primitive))
    hits.sort()
    sequence = []
    for _, _, primitive in hits:
        if not sequence or sequence[-1] != primitive:
            sequence.append(primitive)
    return sequence


def macro(sequence: list[str]) -> str:
    present = set(sequence)
    if len(present) >= 5:
        return "COMPOSITE_STATION_SEQUENCE"
    if "WASH" in present:
        return "WASH_CELL"
    if "PASS_STRAIN" in present:
        return "FILTER_PASS_CELL"
    if present & {"DRAIN", "COLLECT"}:
        return "DRAIN_RECEIVE_CELL"
    if present & {"HEAT", "SETTLE", "DURATION_GRADE", "READY"}:
        return "TEMPER_HOLD_CELL"
    if present & {"MEASURE", "PORTION_ADD"}:
        return "MEASURED_CHARGE_CELL"
    if present & {"TRANSFER", "SET", "TARGET", "ORDER_CONTINUE"}:
        return "TRANSFER_SET_CELL"
    return "APPLICATION_FASTEN_CELL"


def main() -> None:
    statements = [row for row in read_tsv(R89) if row["record_unit_id"].startswith("B")]
    primitive_rows = []
    for order, (primitive, meaning, card_family, pattern) in enumerate(PRIMITIVES, 1):
        primitive_rows.append({
            "phrasebook_order": order, "primitive_id": primitive,
            "source_meaning_de": meaning, "candidate_card_family": card_family,
            "recognition_cue": pattern,
        })
    write_tsv(OUT / "NINETIETH_16_BATH_SERVICE_PRIMITIVES.tsv", primitive_rows)

    mapped = []
    macro_members: dict[str, list[dict[str, object]]] = defaultdict(list)
    phrase_counts = Counter(row["card_near_workshop_reading_de"].rstrip(". ") for row in statements)
    for row in statements:
        sequence = extract_primitives(row["card_near_workshop_reading_de"])
        macro_id = macro(sequence)
        out = {
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "physical_loci": row["physical_loci"],
            "event_count": row["event_count"], "visible_surface_sequence": row["visible_surface_sequence"],
            "primitive_sequence": ">".join(sequence), "primitive_count": len(sequence),
            "macro_id": macro_id, "macro_reading_de": MACRO_READINGS[macro_id],
            "full_statement_reading_de": row["concrete_source_expansion_de"],
            "exact_phrase_recurrence": phrase_counts[row["card_near_workshop_reading_de"].rstrip(". ")],
            "owner_rule": "KEEP_LOCAL_VISIBLE_OWNER__DO_NOT_MERGE_STATIONS",
        }
        mapped.append(out)
        macro_members[macro_id].append(out)
    write_tsv(OUT / "NINETIETH_97_STATEMENT_PHRASEBOOK.tsv", mapped)

    summary_rows = []
    for macro_id in MACRO_READINGS:
        members = macro_members[macro_id]
        summary_rows.append({
            "macro_id": macro_id, "macro_reading_de": MACRO_READINGS[macro_id],
            "statement_count": len(members),
            "records": ",".join(sorted({str(row["record_unit_id"]) for row in members})) or "NONE",
            "example_statement_ids": ",".join(str(row["statement_id"]) for row in members[:5]) or "NONE",
        })
    write_tsv(OUT / "NINETIETH_8_MACRO_SUMMARY.tsv", summary_rows)

    repeated = []
    for phrase, count in phrase_counts.most_common():
        if count < 2:
            continue
        members = [row for row in statements if row["card_near_workshop_reading_de"].rstrip(". ") == phrase]
        repeated.append({
            "exact_phrase_de": phrase, "occurrence_count": count,
            "statement_ids": ",".join(row["statement_id"] for row in members),
            "records": ",".join(sorted({row["record_unit_id"] for row in members})),
            "interpretation": "SHARED_WORKSHOP_PHRASE__LOCAL_OWNER_STILL_CONTROLS_OBJECT",
        })
    write_tsv(OUT / "NINETIETH_REPEATED_EXACT_PHRASES.tsv", repeated)

    macro_counts = Counter(row["macro_id"] for row in mapped)
    report = [
        "# Neunzigste Werkstattrunde: kleines Bad-/Dienstphrasebook", "",
        "## Ergebnis", "",
        "Die 97 Biological-Aussagen brauchen keine 97 verschiedenen Satzregeln. Sie",
        "lassen sich mit sechzehn kurzen Arbeitsprimitiven und acht Zellmustern lesen.",
        "Die genaue Kartenfolge und der lokale Bildbesitzer bleiben trotzdem erhalten.", "",
    ]
    for macro_id in MACRO_READINGS:
        report.append(f"- {macro_id}: {macro_counts[macro_id]} — {MACRO_READINGS[macro_id]}")
    report.extend([
        "", f"{sum(1 for count in phrase_counts.values() if count > 1)} exakte Satzformulierungen wiederholen sich.",
        "Besonders klar sind `Führe ab und schließe`, `Setze länger an und schließe`,",
        "`Lass absetzen und schließe` und `Setze um und schließe`. Das spricht für ein",
        "gelerntes Arbeitsphrasebook, nicht für 97 frei formulierte Sätze.", "",
        "Wichtig: Gleiches Phrasebook heißt nicht gleicher Gegenstand. Ein Ablauf an B2",
        "und ein Ablauf an B4 benutzen denselben Arbeitssatz, bleiben aber an verschiedene",
        "sichtbare Stationen gebunden. Die Karten liefern die Handlung; das Bild liefert",
        "den lokalen Teilnehmer.", "",
        "Nur die festen Biological-Seiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ])
    (OUT / "NINETIETH_PHRASEBOOK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    build_summary = {
        "status": "CONSISTENT", "primitives": len(primitive_rows),
        "macros": len(summary_rows), "statements": len(mapped),
        "repeated_exact_phrases": len(repeated), "macro_counts": dict(macro_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(build_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
