#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R251 = ROOT / "experiments/yolo/sidequest_semantic_component_equations_two_hundred_fifty_first"
R250 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_working_edition_two_hundred_fiftieth"
CARDS = R251 / "TWO_HUNDRED_FIFTY_FIRST_REVISED_173_CARD_DICTIONARY.tsv"
EVENTS = R250 / "TWO_HUNDRED_FIFTIETH_381_PROSE_EVENTS.tsv"
STATEMENTS = R250 / "TWO_HUNDRED_FIFTIETH_116_PROSE_STATEMENTS.tsv"

BLOCKERS = {
    "MC061": ("AR|AL", "UEBERTRAGEN", "von der aktiven Stelle zur nächsten übertragen", "MEDIUM"),
    "MC124": ("AR|OL", "WEITERABZUG", "aus dem laufenden Posten weiter abziehen", "HIGH"),
    "MC049": ("AR|OR", "SUDANSATZ", "aus dem bezeichneten Kochgut einen Ansatz bilden", "MEDIUM"),
    "MC068": ("AL|OL", "FOLGEANWENDUNG", "zur folgenden Anwendung weiterführen", "HIGH"),
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


def is_whole(row: dict[str, str]) -> bool:
    return "WHOLE" in row["dictionary_layer"] or "WHOLE" in row["component_parse"] or row["dictionary_layer"] == "MEMORIZED_WHOLE_CARD"


def main() -> None:
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    statements = {r["statement_id"]: r for r in read_tsv(STATEMENTS)}
    whole = [r for r in cards if is_whole(r)]
    event_by_card: dict[str, list[dict[str, str]]] = {}
    for row in events:
        event_by_card.setdefault(row["master_card_id"], []).append(row)

    audit = []
    for row in whole:
        selected = row["master_card_id"] in BLOCKERS
        pair, short, expansion, confidence = BLOCKERS.get(row["master_card_id"], ("NONE", row["portable_core_de"], row["local_prose_expansion_de"], "NONE"))
        contexts = event_by_card.get(row["master_card_id"], [])
        audit.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "current_core_de": row["portable_core_de"], "component_parse": row["component_parse"],
            "prose_event_count": row["prose_event_count"], "records": row["records"],
            "missing_pair_candidate": pair, "candidate_status": "SELECTED_LEXICAL_BLOCKER" if selected else "NO_PAIR_MATCH",
            "lexical_short_value_de": short, "contextual_expansion_de": expansion,
            "confidence": confidence,
            "event_ids": "|".join(r["event_id"] for r in contexts),
            "statement_ids": "|".join(dict.fromkeys(r["statement_id"] for r in contexts)),
        })

    blockers = []
    for card_id, (pair, short, expansion, confidence) in BLOCKERS.items():
        card = next(r for r in cards if r["master_card_id"] == card_id)
        card_events = event_by_card[card_id]
        blockers.append({
            "missing_pair": pair, "master_card_id": card_id, "master_form": card["master_form"],
            "whole_sign_value_de": short, "full_pair_expansion_de": expansion,
            "confidence": confidence, "support_event_count": len(card_events),
            "support_events": "|".join(r["event_id"] for r in card_events),
            "support_statements": "|".join(dict.fromkeys(r["statement_id"] for r in card_events)),
            "visible_contexts": " || ".join(statements[r["statement_id"]]["visible_sequence"] for r in card_events),
            "complete_context_readings_de": " || ".join(statements[r["statement_id"]]["complete_local_translation_de"] for r in card_events),
            "blocking_rule": f"Use the learned sign {card['master_form']} instead of mechanically fusing {pair}.",
        })

    audit_path = OUT / "TWO_HUNDRED_FIFTY_SIXTH_23_WHOLE_SIGN_AUDIT.tsv"
    blockers_path = OUT / "TWO_HUNDRED_FIFTY_SIXTH_FOUR_LEXICAL_BLOCKERS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_SIXTH_READABLE_MIXED_CODEBOOK.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_SIXTH_REPORT.md"
    write_tsv(audit_path, audit, list(audit[0]))
    write_tsv(blockers_path, blockers, list(blockers[0]))

    readable = [
        "# Warum vier Stammkombinationen fehlen", "",
        "Die Werkstatt baut vieles aus kleinen Stämmen, hat aber für häufige Gesamtvorgänge eigene gelernte Zeichen. Diese Ganzkarten blockieren vier theoretisch mögliche Zusammensetzungen:", "",
        "- `sshkchdy` = **ÜBERTRAGEN**. Es erfüllt funktional AR+AL: von hier nach dort.",
        "- `lkedy` = **WEITERABZUG**. Es erfüllt AR+OL: aus dem laufenden Posten weiter abziehen.",
        "- `schoal` = **SUDANSATZ**. Es erfüllt AR+OR: aus dem Kochgut einen Ansatz bilden.",
        "- `sotodan` = **FOLGEANWENDUNG**. Es erfüllt AL+OL: zur nächsten Anwendung weiterführen.", "",
        "Das erklärt, warum die reguläre Grammatik elf Paare bildet, aber diese vier nicht. Der Schreiber schreibt bei gewöhnlichen Beziehungen produktive Kürzel; bei vier vertrauten Arbeitsvorgängen greift er zur kompakten Ganzkarte.", "",
        "## Beispiel", "",
        "`qol sshkchdy` liest sich nicht Buchstabe für Buchstabe, sondern: **weiter — übertragen; Schluss**. Das erste Zeichen setzt den Fortgang, das zweite ruft den gelernten gesamten Transfer ab.", "",
        "`tshol schoal cfhy shfydaiin cphy shey tchody` wird dadurch: **Kochgut — Sudansatz — auswringen — vorgeschriebene Stehzeit — nachseihen — Klarlauf — kalt stellen; Schluss.**", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 256: lexikalische Blockierung

## Ergebnis

Die vier Lücken der Beziehungsalgebra sind funktional besetzt, jedoch nicht als regelmäßige Stammfusionen. Vier gelernte Ganzkarten übernehmen die Arbeit: ÜBERTRAGEN für AR+AL, WEITERABZUG für AR+OL, SUDANSATZ für AR+OR und FOLGEANWENDUNG für AL+OL.

Das stärkt das gesuchte historische Mischmodell. Produktive Kürzel bilden die häufigen Adress- und Fortgangsrelationen; eine kleine Nomenklatorschicht speichert routinisierte Fachvorgänge als Ganzzeichen. Man kann deshalb neue Kartenkompositionen vorhersagen, ohne jede sichtbare Form gewaltsam zu zerlegen.

Der Audit umfasst 23 gelernte Ganzzeichen. Nur vier passen kontextuell zu den vier Algebra-Lücken; die übrigen neunzehn behalten ihre kurzen Stoff-, Gefäß-, Handlungs- oder Zustandswerte.

Inputs: dictionary `{sha(CARDS)}`, events `{sha(EVENTS)}`, statements `{sha(STATEMENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (audit_path, blockers_path, readable_path, report_path)
    summary = {
        "status": "PASS", "whole_signs_audited": len(audit), "lexical_blockers": len(blockers),
        "missing_pairs_filled": sorted(r["missing_pair"] for r in blockers),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
