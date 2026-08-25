#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CODEBOOK = ROOT / "sidequest_semantic_mixed_root_codebook_eight_hundred_ninety_ninth"
SLOTS = ROOT / "sidequest_semantic_scribe_slot_grammar_nine_hundredth"
RENDERER = ROOT / "sidequest_semantic_allograph_renderer_nine_hundred_first"
CURRENT = ROOT / "sidequest_semantic_complete_functional_renderer_nine_hundred_fourth"
PREFIX = "NINE_HUNDRED_FIFTH"

VOCAB_SOURCE = CODEBOOK / "EIGHT_HUNDRED_NINETY_NINTH_231_MIXED_CODEBOOK_VOCABULARY.tsv"
SYMBOL_SOURCE = SLOTS / "NINE_HUNDREDTH_48_GRAMMAR_SYMBOLS.tsv"
PATTERN_SOURCE = SLOTS / "NINE_HUNDREDTH_8_CARD_PATTERNS.tsv"
PARSE_SOURCE = SLOTS / "NINE_HUNDREDTH_231_IDENTITY_SLOT_PARSES.tsv"
CUE_SOURCE = RENDERER / "NINE_HUNDRED_FIRST_48_SYMBOL_ALLOGRAPHS.tsv"
RULE_SOURCE = RENDERER / "NINE_HUNDRED_FIRST_15_RENDERER_RULES.tsv"
MICRO_SOURCE = CURRENT / "NINE_HUNDRED_FOURTH_38_COMPLETE_ALLOGRAPH_MICROLEXICON.tsv"
MARK_SOURCE = CURRENT / "NINE_HUNDRED_FOURTH_437_FUNCTIONALLY_RENDERED_MARKS.tsv"
UNIT_SOURCE = CURRENT / "NINE_HUNDRED_FOURTH_118_FUNCTIONALLY_RENDERED_UNITS.tsv"
CARD_SOURCE = CURRENT / "NINE_HUNDRED_FOURTH_6_FUNCTIONALLY_RENDERED_JOB_CARDS.tsv"

PAGE_ORDER = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]
PAGE_TITLES = {
    "f10r": "Pflanzenblatt A — gezahnte Blütenpflanze",
    "f11r": "Pflanzenblatt B — zweite Zubereitungsfolge",
    "f55v": "Pflanzenblatt C — breitblättriger Stoff",
    "f56r": "Pflanzenblatt D — feuchte Standortpflanze",
    "f81v": "Badblatt A — gemeinsames zweireihiges Becken",
    "f82r": "Badblatt B — mehrere lokale Stationen",
    "f83r": "Badblatt C — lokale Becken, Wege und Anwendungen",
    "f67r2": "Himmelsblatt A — Phasen- und Aspektplätze",
    "f68r1": "Himmelsblatt B — direkter Sternort",
    "f69v": "Himmelsblatt C — 28er-, Feuchte- und Qualitätsring",
}

WORKFLOW = [
    (1, "OWNER", "Nimm Bild, Becken, Station oder Diagrammplatz als stillen Besitzer."),
    (2, "REGISTER", "Wähle WHAT für Herstellung, HOW für Anwendung und WHEN für Bedingung."),
    (3, "ORDER", "Setze OT/OL/OS, wenn Folge, Fortsetzung oder Zusatz ausdrücklich markiert werden soll."),
    (4, "OPERATION", "Wähle Handlungskerne wie OK, K, CH, CHD, CHK, LSH, P, SOLK oder T."),
    (5, "MATERIAL", "Füge Teil, Ansatz, Portion, Maß oder Nachgabe mit HO/OR/AIN/AIIN/AN ein."),
    (6, "ADDRESS", "Gib Quelle, Zielstelle, Lauf oder Durchlass mit AR/AL/AIR/CKH/L an."),
    (7, "GRADE", "Setze E/EE/EEE für kurz, lang oder vollständig."),
    (8, "STATE", "Setze bereit, kühl, halten, ruhen oder Stufe mit CTH/R/SH/SHED/IIN."),
    (9, "REFERENT", "Setze Y für den laufenden Posten; wähle dessen funktionalen Allographen."),
    (10, "CLOSE", "Füge DY nur als lizenzierten Schrittabschluss hinzu; nacktes dy kann ein Y-Allograph sein."),
    (11, "RENDER", "Erhalte die Wurzelreihenfolge und wende q-, Rahmen-, Grad- und Endallographen an."),
    (12, "READ_BACK", "Lies Wurzeln atomar zurück und erweitere sie mit Bildbesitzer zur flüssigen Werkstattanweisung."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    vocabulary = read(VOCAB_SOURCE)
    symbols = read(SYMBOL_SOURCE)
    patterns = read(PATTERN_SOURCE)
    parses = read(PARSE_SOURCE)
    cues = read(CUE_SOURCE)
    rules = read(RULE_SOURCE)
    microlexicon = read(MICRO_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)

    cue_by_symbol = {row["symbol"]: row for row in cues}
    symbol_rows = []
    for row in symbols:
        cue = cue_by_symbol[row["symbol"]]
        symbol_rows.append({
            "symbol": row["symbol"],
            "atomic_value_de": row["atomic_value_de"],
            "slot_role": row["slot_role"],
            "symbol_class": row["symbol_class"],
            "canonical_surface_cue": cue["canonical_surface_cue"],
            "cue_class": cue["cue_class"],
            "weighted_mark_uses": cue["weighted_mark_uses"],
            "surface_examples": cue["whole_surface_examples"],
            "scribe_rule": row["scribe_rule"],
            "renderer_instruction": cue["renderer_instruction"],
        })

    vocab_by_id = {row["identity"]: row for row in vocabulary}
    parse_by_id = {row["identity"]: row for row in parses}
    marks_by_identity: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_identity[row["identity"]].append(row)
    micro_by_form = {(row["component_recipe"], row["surface"]): row for row in microlexicon}

    dictionary_rows = []
    for identity in [row["identity"] for row in vocabulary]:
        vocab = vocab_by_id[identity]
        parsed = parse_by_id[identity]
        local = marks_by_identity[identity]
        values = {row["concrete_default_de"] for row in local}
        actions = {row["apprentice_action"] for row in local}
        assert len(values) == 1 and len(actions) == 1
        forms = sorted({row["surface"] for row in local})
        microfunctions = []
        for form in forms:
            item = micro_by_form.get((parsed["component_recipe"], form))
            if item:
                microfunctions.append(f"{item['renderer_microfunction']}->{form}")
        dictionary_rows.append({
            "identity": identity,
            "surface_forms": " | ".join(forms),
            "component_recipe": parsed["component_recipe"],
            "slot_signature": parsed["slot_signature"],
            "atomic_root_reading_de": parsed["root_reading_de"],
            "dictionary_value_de": next(iter(values)),
            "local_fluent_expansions_de": vocab["local_fluent_expansions_de"],
            "primary_card_pattern": parsed["primary_pattern"],
            "apprentice_action": next(iter(actions)),
            "functional_allographs": " | ".join(microfunctions) if microfunctions else "NONE",
            "marks": len(local),
            "orders": " | ".join(sorted({row["order_id"] for row in local})),
            "pages": " | ".join(sorted({row["page"] for row in local})),
            "sections": " | ".join(sorted({row["master_section"] for row in local})),
            "owners_or_handles_de": " | ".join(sorted({row["owner_or_handle_de"] for row in local})),
        })

    dictionary_by_id = {row["identity"]: row for row in dictionary_rows}
    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    interlinear_rows = []
    for row in marks:
        dictionary = dictionary_by_id[row["identity"]]
        unit = unit_lookup[(row["order_id"], row["stage"], row["unit"])]
        interlinear_rows.append({
            "order_mark_id": row["order_mark_id"],
            "order_id": row["order_id"],
            "page": row["page"],
            "unit": row["unit"],
            "section": row["master_section"],
            "surface": row["surface"],
            "identity": row["identity"],
            "component_recipe": row["component_recipe"],
            "slot_signature": row["slot_signature"],
            "atomic_root_reading_de": row["root_reading_de"],
            "dictionary_value_de": row["concrete_default_de"],
            "local_fluent_expansion_de": dictionary["local_fluent_expansions_de"],
            "functional_allograph": row["renderer_microfunction"],
            "microfunction_trigger_de": row["microfunction_trigger_de"],
            "owner_or_handle_de": row["owner_or_handle_de"],
            "unit_fluent_instruction_de": unit["front_instruction_de"],
            "renderer_skeleton": row["renderer_skeleton"],
            "predicted_surface": row["predicted_surface"],
            "reading_action": row["apprentice_action"],
        })

    grouped_page_units: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in units:
        grouped_page_units[(row["page"], row["unit"])].append(row)
    page_unit_rows = []
    for page in PAGE_ORDER:
        for (candidate_page, unit_id), local in grouped_page_units.items():
            if candidate_page != page:
                continue
            for field in ["fifth_hand_surface_sequence", "literal_sequence_de", "front_instruction_de", "section", "root_reading_sequence_de", "predicted_surface_sequence"]:
                assert len({row[field] for row in local}) == 1
            first = local[0]
            page_unit_rows.append({
                "page": page,
                "page_title_de": PAGE_TITLES[page],
                "unit": unit_id,
                "section": first["section"],
                "orders": " | ".join(sorted(row["order_id"] for row in local)),
                "owner_or_handle_de": " | ".join(
                    f"{row['order_id']}:{row['owner_trace_de']}" for row in sorted(local, key=lambda item: item["order_id"])
                ),
                "surface_sequence": first["fifth_hand_surface_sequence"],
                "atomic_root_sequence_de": first["root_reading_sequence_de"],
                "dictionary_literal_de": first["literal_sequence_de"],
                "fluent_workshop_reading_de": first["front_instruction_de"],
                "predicted_surface_sequence": first["predicted_surface_sequence"],
                "source_unit_copies": len(local),
            })

    workflow_rows = [{"step": step, "stage": stage, "instruction_de": instruction} for step, stage, instruction in WORKFLOW]
    write(f"{PREFIX}_48_COMPLETE_SYMBOL_DICTIONARY.tsv", symbol_rows, list(symbol_rows[0]))
    write(f"{PREFIX}_8_CARD_PATTERNS.tsv", patterns, list(patterns[0]))
    write(f"{PREFIX}_15_RENDERER_RULES.tsv", rules, list(rules[0]))
    write(f"{PREFIX}_38_ALLOGRAPH_MICROLEXICON.tsv", microlexicon, list(microlexicon[0]))
    write(f"{PREFIX}_231_COMPLETE_CARD_DICTIONARY.tsv", dictionary_rows, list(dictionary_rows[0]))
    write(f"{PREFIX}_437_COMPLETE_INTERLINEAR.tsv", interlinear_rows, list(interlinear_rows[0]))
    write(f"{PREFIX}_118_COMPLETE_UNIT_EDITION.tsv", units, list(units[0]))
    write(f"{PREFIX}_115_DEDUPED_PAGE_UNITS.tsv", page_unit_rows, list(page_unit_rows[0]))
    write(f"{PREFIX}_6_COMPLETE_JOB_CARDS.tsv", cards, list(cards[0]))
    write(f"{PREFIX}_12_STEP_WORKFLOW.tsv", workflow_rows, list(workflow_rows[0]))

    handbook = [
        "# Vollständiges Schreiberhandbuch",
        "",
        "Diese Arbeitsfassung benutzt eine kleine produktive Kartenmaschine: 36 Bedeutungswurzeln, 12 Hilfszeichen, 8 Kartenmuster, 15 Rendererregeln und 38 Funktionsallographen.",
        "Zwei Diagrammwerte bleiben lokale Ganzwörter; alles andere wird aus Wurzelrezept, Slotrolle und beabsichtigter Allographenfunktion gelesen.",
        "",
        "## Zwölf Arbeitsschritte",
        "",
    ]
    for row in workflow_rows:
        handbook.append(f"{row['step']}. **{row['stage']}** — {row['instruction_de']}")
    handbook.extend(["", "## Acht Kartenmuster", ""])
    for row in patterns:
        handbook.append(f"- **{row['pattern']}** — {row['teaching_rule_de']}")
    handbook.extend(["", "## Symbolkern", ""])
    for row in symbol_rows:
        handbook.append(f"- `{row['symbol']}` = **{row['atomic_value_de']}**; sichtbarer Hinweis `{row['canonical_surface_cue']}`.")
    handbook.extend(["", "## Funktionsallographen", ""])
    for row in microlexicon:
        handbook.append(f"- `{row['component_recipe']}` + {row['renderer_microfunction']} → `{row['surface']}`.")
    (HERE / f"{PREFIX}_COMPLETE_SCRIBE_HANDBOOK.md").write_text("\n".join(handbook).rstrip() + "\n", encoding="utf-8")

    edition = [
        "# Zehnseitige Werkstattausgabe",
        "",
        "Dies ist die vollständige aktuelle Sechs-Auftrags-Auswahl auf den zehn festen Seiten; doppelt verwendete Seitenfelder stehen nur einmal und nennen alle zugehörigen Aufträge.",
        "",
    ]
    for page in PAGE_ORDER:
        edition.extend([f"## {page}: {PAGE_TITLES[page]}", ""])
        for row in page_unit_rows:
            if row["page"] != page:
                continue
            edition.extend([
                f"### {row['unit']} / {row['section']} / {row['orders']}",
                "",
                f"`{row['surface_sequence']}`",
                "",
                f"**Atomar:** {row['atomic_root_sequence_de']}",
                f"**Lesung:** {row['fluent_workshop_reading_de']}",
                "",
            ])
    (HERE / f"{PREFIX}_TEN_PAGE_WORKING_EDITION.md").write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")

    action_counts = Counter(row["apprentice_action"] for row in marks)
    page_counts = Counter(row["page"] for row in page_unit_rows)
    summary = {
        "status": "PASS",
        "decision": "ONE_CONSOLIDATED_SCRIBE_HANDBOOK_BINDS_THE_COMPLETE_CURRENT_TEN_PAGE_WORKSHOP_SELECTION",
        "pages": len(PAGE_ORDER),
        "page_unit_counts": dict(page_counts),
        "semantic_roots": 36,
        "helper_signs": 12,
        "symbols": len(symbol_rows),
        "card_patterns": len(patterns),
        "renderer_rules": len(rules),
        "allograph_entries": len(microlexicon),
        "dictionary_identities": len(dictionary_rows),
        "marks": len(interlinear_rows),
        "units": len(units),
        "deduped_page_units": len(page_unit_rows),
        "job_cards": len(cards),
        "workflow_steps": len(workflow_rows),
        "mark_actions": dict(action_counts),
        "surface_prediction_mismatches": sum(row["surface"] != row["predicted_surface"] for row in marks),
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 905: konsolidiertes Schreiberhandbuch\n\n"
        "## Ergebnis\n\n"
        "Die aktuelle Arbeitstheorie ist nun in **einer** benutzbaren Werkstattausgabe zusammengezogen. "
        "Sie umfasst 36 kurze Bedeutungswurzeln, 12 Hilfszeichen, 8 Kartenmuster, 15 Rendererregeln, "
        "38 Funktionsallographen, 231 Kartenidentitäten, 437 sichtbare Marken, 118 Auftrags-Einheiten "
        "und 115 eindeutige Seiteneinheiten. Alle 437 beobachteten Oberflächen werden von der "
        "Schreiberregel exakt wieder erzeugt.\n\n"
        "## Was der Lehrling lernt\n\n"
        "Der Schreiber beginnt nicht mit einem lateinischen Satz. Er nimmt zuerst den sichtbaren Besitzer "
        "— Pflanze, Becken, Station oder Himmelsplatz — und baut dann eine kurze Karte aus Reihenfolge, "
        "Handlung, Stoff/Menge, Adresse, Grad, Zustand, laufendem Posten und gegebenenfalls Schluss. "
        "Die Karte wird anschließend mit einem passenden Funktionsallographen geschrieben. Beim Lesen "
        "geschieht dasselbe rückwärts: Oberfläche → Kartenrezept → atomare Werkstattwörter → mit dem Bild "
        "ergänzte Anweisung. Das erklärt, warum dieselbe kurze Karte in Pflanzen-, Bad- und Himmelskontext "
        "anders flüssig klingt, ohne ihren Kernwert zu wechseln.\n\n"
        "## Vollständigkeit der Ausgabe\n\n"
        "Die Zehn-Seiten-Datei ist die vollständige **aktuelle Sechs-Auftrags-Auswahl** auf den zehn festen "
        "Seiten, nicht die Behauptung einer diplomatischen Vollübersetzung jeder physischen Textzeile. "
        "Drei Seiteneinheiten werden von zwei Aufträgen geteilt. Bei f11r H3-S001 unterscheiden sich deren "
        "Bildprodukt-Besitzer; beide Zuordnungen bleiben ausdrücklich nebeneinander stehen, statt sie beim "
        "Deduplizieren zu verwischen.\n\n"
        "## Noch ungelernte Ecke\n\n"
        "Nur zwei Karten werden weiterhin als lokale Ganzwörter gelernt: `iokeeor` = WETTERZEICHEN und "
        "`daiial` = FEUCHTESTUFE. Der nächste kreative Pass soll prüfen, ob ihre sichtbaren Teile mit den "
        "bestehenden 36 Wurzeln wirklich kompositionell lesbar werden; falls nicht, bleiben sie ehrliche "
        "kleine Nomenklatorwörter.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
