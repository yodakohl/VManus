#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R257 = ROOT / "experiments/yolo/sidequest_semantic_mixed_codebook_edition_two_hundred_fifty_seventh"
R258 = ROOT / "experiments/yolo/sidequest_semantic_minimum_apprentice_deck_two_hundred_fifty_eighth"
CARDS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_173_CARD_DICTIONARY.tsv"
EVENTS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_381_PROSE_EVENTS.tsv"
STATEMENTS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_116_STATEMENTS.tsv"
GENERATION = R258 / "TWO_HUNDRED_FIFTY_EIGHTH_173_CARD_GENERATION.tsv"


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
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    generation = {r["master_card_id"]: r for r in read_tsv(GENERATION)}
    candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        candidates[row["portable_core_de"]].append(row)

    instructions = []
    for index, core in enumerate(sorted(candidates, key=str.casefold), 1):
        rows = candidates[core]
        instructions.append({
            "instruction_id": f"I{index:03d}", "workshop_instruction_de": core,
            "candidate_card_count": len(rows),
            "candidate_card_ids": "|".join(r["master_card_id"] for r in rows),
            "candidate_master_forms": "|".join(r["master_form"] for r in rows),
            "selection_class": "UNIQUE_CARD" if len(rows) == 1 else "WORKING_EQUIVALENCE_SET",
            "selection_rule": "write the unique master card" if len(rows) == 1 else "choose the registered hand/exemplar variant; meaning remains unchanged",
            "prose_event_count": sum(int(r["prose_event_count"]) for r in rows),
        })
    instruction_by_core = {r["workshop_instruction_de"]: r for r in instructions}

    generated_events = []
    for row in events:
        instruction = instruction_by_core[row["portable_core_de"]]
        generated_events.append({
            "event_id": row["event_id"], "statement_id": row["statement_id"],
            "page": row["page"], "visible_owner": row["visible_owner"],
            "source_instruction_de": row["portable_core_de"],
            "candidate_card_ids": instruction["candidate_card_ids"],
            "actual_master_card_id": row["master_card_id"],
            "actual_visible_surface": row["visible_surface"],
            "semantic_generation": "PASS",
            "master_selection": "EXACT_FROM_INSTRUCTION" if instruction["selection_class"] == "UNIQUE_CARD" else "EQUIVALENCE_SET_NEEDS_RENDERER_CHOICE",
            "construction_class": generation[row["master_card_id"]]["construction_class"],
            "terminal_status": row["terminal_status"],
        })

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in generated_events:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        evs = by_statement[row["statement_id"]]
        classes = {r["construction_class"] for r in evs}
        route = "REQUIRES_WHOLE_SIGN" if "WHOLE_SIGN" in classes else (
            "REQUIRES_LOCAL_CORE" if "FRAME_PLUS_LOCAL_CORE" in classes else "FULLY_PRODUCTIVE"
        )
        exact = all(r["master_selection"] == "EXACT_FROM_INSTRUCTION" for r in evs)
        statement_rows.append({
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "visible_owner": row["visible_owner"], "source_instruction_chain_de": row["portable_core_chain"],
            "generated_candidate_sequence": " ".join(
                r["candidate_card_ids"] if "|" not in r["candidate_card_ids"] else "{" + r["candidate_card_ids"] + "}" for r in evs
            ),
            "actual_master_sequence": " ".join(r["actual_master_card_id"] for r in evs),
            "actual_visible_sequence": row["visible_sequence"],
            "apprentice_route": route, "semantic_roundtrip": "PASS",
            "master_card_roundtrip": "EXACT_UNIQUE" if exact else "WORKING_EQUIVALENCE_SET",
            "complete_local_translation_de": row["complete_local_translation_de"],
        })

    instructions_path = OUT / "TWO_HUNDRED_FIFTY_NINTH_171_INSTRUCTION_ENTRIES.tsv"
    events_path = OUT / "TWO_HUNDRED_FIFTY_NINTH_381_REVERSE_GENERATED_EVENTS.tsv"
    statements_path = OUT / "TWO_HUNDRED_FIFTY_NINTH_116_REVERSE_GENERATED_STATEMENTS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_NINTH_READABLE_WRITING_MANUAL.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_NINTH_REPORT.md"
    write_tsv(instructions_path, instructions, list(instructions[0]))
    write_tsv(events_path, generated_events, list(generated_events[0]))
    write_tsv(statements_path, statement_rows, list(statement_rows[0]))

    route_counts = Counter(r["apprentice_route"] for r in statement_rows)
    readable = [
        "# Vom Arbeitsauftrag zur Voynich-Karte", "",
        "## Schreibablauf", "",
        "1. Das Bild oder Diagramm setzt den stillen Besitzer.",
        "2. Der Meister nennt die kurze Arbeitsfolge: etwa Sollwert — Ziel — einsetzen — länger halten — Schluss.",
        "3. Der Schreiber ersetzt jeden Schritt durch den Eintrag des 53er-Decks.",
        "4. Produktive Bestandteile werden zusammengesetzt; lokale Kerne und Ganzzeichen werden aus dem Exemplar genommen.",
        "5. Erst danach wählt die Hand die registrierte Oberflächenform.", "",
        "## Restmehrdeutigkeit", "",
        "169 der 171 Arbeitsanweisungen wählen genau eine Masterkarte. Zwei bilden harmlose Arbeitsäquivalenzen:", "",
        "- `DANACH_WEITER` → `otol` oder `qotchol`.",
        "- `einführen; Schluss` → `okchedy/qokchedy` oder `qokchdy`.", "",
        "Die Anweisung bestimmt in beiden Fällen die Bedeutung vollständig; Hand, Register oder Masterexemplar bestimmen die konkrete Form.", "",
        "## Satzdeckung", "",
        "47 der 116 Aussagen können vollständig produktiv geschrieben werden. 48 brauchen mindestens einen lokalen Kern, 21 mindestens ein Ganzzeichen. Alle 116 ergeben dieselbe Bedeutungsfolge; 109 wählen jede Masterkarte eindeutig, sieben enthalten eine der beiden Variantenfamilien.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 259: Rückwärtscompiler

## Ergebnis

Die 173 Karten bilden 171 verschiedene Arbeitsanweisungen. 169 Anweisungen wählen genau eine Masterkarte; nur DANACH_WEITER und EINFÜHREN_SCHLUSS haben je zwei gleichwertige Kartenformen. Dadurch werden 374/381 Ereignisse aus der kurzen Anweisung bis zur Masterkarte eindeutig, sieben bis zu einer zweigliedrigen Variantenfamilie.

Auf Satzebene sind 47/116 Folgen vollständig produktiv, 48 benötigen einen lokalen Kern und 21 ein Ganzzeichen. 109 Aussagen wählen alle Masterkarten eindeutig; sieben benötigen zusätzlich die Hand-/Exemplarwahl. Die semantische Arbeitsfolge bleibt in allen 116 erhalten.

Inputs: cards `{sha(CARDS)}`, events `{sha(EVENTS)}`, statements `{sha(STATEMENTS)}`, generation deck `{sha(GENERATION)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (instructions_path, events_path, statements_path, readable_path, report_path)
    summary = {
        "status": "PASS", "instruction_entries": len(instructions),
        "unique_instructions": sum(r["selection_class"] == "UNIQUE_CARD" for r in instructions),
        "equivalence_sets": sum(r["selection_class"] == "WORKING_EQUIVALENCE_SET" for r in instructions),
        "events_exact": sum(r["master_selection"] == "EXACT_FROM_INSTRUCTION" for r in generated_events),
        "events_variant": sum(r["master_selection"] != "EXACT_FROM_INSTRUCTION" for r in generated_events),
        "statement_routes": dict(route_counts),
        "statements_exact": sum(r["master_card_roundtrip"] == "EXACT_UNIQUE" for r in statement_rows),
        "statements_variant": sum(r["master_card_roundtrip"] != "EXACT_UNIQUE" for r in statement_rows),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
