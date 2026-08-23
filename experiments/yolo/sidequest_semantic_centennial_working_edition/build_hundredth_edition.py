#!/usr/bin/env python3
"""Build the centennial ten-page working edition from the selected creative layers."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_173_LITERAL_PARSE.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_230_SURFACE_PARSE.tsv"
RENDERERS = ROOT / "experiments/yolo/sidequest_semantic_renderer_inventory_ninety_ninth_edition/NINETY_NINTH_173_RENDERER_FAMILIES.tsv"
SURFACE_RENDERERS = ROOT / "experiments/yolo/sidequest_semantic_renderer_inventory_ninety_ninth_edition/NINETY_NINTH_230_SURFACE_COVERAGE.tsv"
ECONOMY = ROOT / "experiments/yolo/sidequest_semantic_paradigm_economy_ninety_seventh_edition/NINETY_SEVENTH_15_FAMILY_ECONOMY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_continuous_translation_eighty_ninth_edition/EIGHTY_NINTH_381_EVENT_STATEMENT_BINDING.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_continuous_translation_eighty_ninth_edition/EIGHTY_NINTH_116_CONTINUOUS_STATEMENT_TRANSLATION.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_apprentice_ninety_fourth_edition/NINETY_FOURTH_395_GROUP_COPY_TRACE.tsv"
INSTRUMENTS = ROOT / "experiments/yolo/sidequest_semantic_astro_apprentice_ninety_fourth_edition/NINETY_FOURTH_3_INSTRUMENT_ROUNDTRIP.tsv"
SOURCE_WORDS = ROOT / "experiments/yolo/sidequest_semantic_compact_codebook_ninety_fifth_edition/NINETY_FIFTH_44_SOURCE_WORDS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def astro_default(namespace: str) -> str:
    if namespace.startswith("A1_"):
        return "örtliches Himmels-, Kalender- oder Wahlzeichen"
    if namespace.startswith("A2_"):
        return "örtliches Sternort- oder Feldzeichen"
    if namespace == "A3_LEFT_WHEEL_ONLY":
        return "örtliches Kalenderzeichen"
    if namespace == "A3_MIDDLE_WHEEL_ONLY":
        return "örtliches Wetterzeichen"
    if namespace == "A3_RIGHT_WHEEL_ONLY":
        return "örtliches Licht-, Zeit- oder Eigenschaftszeichen"
    return "örtliches Instrumentzeichen"


def main() -> None:
    cards = read_tsv(CARDS)
    surfaces = read_tsv(SURFACES)
    renderer_by_id = {row["master_card_id"]: row for row in read_tsv(RENDERERS)}
    renderer_by_surface = {row["visible_surface"]: row for row in read_tsv(SURFACE_RENDERERS)}
    tier_by_head = {row["head"]: row for row in read_tsv(ECONOMY)}
    card_by_id = {row["master_card_id"]: row for row in cards}
    card_by_surface = {row["visible_surface"]: card_by_id[row["master_card_id"]] for row in surfaces}

    dictionary: list[dict[str, object]] = []
    for order, card in enumerate(cards, 1):
        renderer = renderer_by_id[card["master_card_id"]]
        leading = card["corrected_semantic_atoms"].split("+")[0]
        tier = tier_by_head.get(leading, {}).get("productivity_tier", "LEARNED_WHOLE_CARD")
        if card["parse_class"] in {"MEMORIZED_WHOLE", "WHOLE_CARD_ONLY"}:
            tier = "LEARNED_WHOLE_CARD"
        if tier == "BROAD_PRODUCTIVE_PARADIGM":
            policy = "COMPOSE_LISTED_ATOMS_FREELY__LONGEST_CARD_WINS"
        elif tier == "BOUNDED_PRODUCTIVE_PARADIGM":
            policy = "COMPOSE_ONLY_ATTESTED_TAIL_CLASSES"
        elif tier == "NARROW_RECURRENT_PATTERN":
            policy = "LEARN_MINI_PARADIGM"
        else:
            policy = "MEMORIZE_EXACT_CARD_OR_ALLOGRAPH_SET"
        dictionary.append({
            "dictionary_order": order,
            "master_card_id": card["master_card_id"],
            "master_form": card["master_head_form"],
            "registered_surface_family": card["registered_surface_family"],
            "stable_surface_host": renderer["stable_surface_host"],
            "entry_gestures": renderer["entry_gestures"],
            "renderer_family_class": renderer["family_class"],
            "semantic_atoms": card["corrected_semantic_atoms"],
            "short_default_de": card["short_default_de"],
            "imperative_de": card["imperative_de"],
            "prose_events": card["prose_events"],
            "leading_head": leading,
            "productivity_tier": tier,
            "composition_policy": policy,
        })

    event_source = read_tsv(EVENTS)
    interlinear: list[dict[str, object]] = []
    for event in event_source:
        surface = event["visible_identity"]
        card = card_by_surface[surface]
        renderer = renderer_by_surface[surface]
        interlinear.append({
            "event_serial": event["event_serial"],
            "statement_id": event["statement_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "local_address": event["local_address"],
            "visible_surface": surface,
            "master_card_id": card["master_card_id"],
            "semantic_atoms": card["corrected_semantic_atoms"],
            "stable_surface_host": renderer["stable_surface_host"],
            "renderer_gesture": renderer["renderer_gesture"],
            "short_default_de": card["short_default_de"],
            "card_near_reading_de": event["short_form_reading"],
            "statement_translation_de": event["statement_translation_de"],
            "line_crossing_statement": event["line_crossing_statement"],
        })

    statement_source = read_tsv(STATEMENTS)
    statement_rows: list[dict[str, object]] = []
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in interlinear:
        events_by_statement[str(row["statement_id"])].append(row)
    for statement in statement_source:
        bound = events_by_statement[statement["statement_id"]]
        statement_rows.append({
            "statement_order": statement["statement_order"],
            "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "physical_loci": statement["physical_loci"],
            "line_crossing": statement["line_crossing"],
            "event_count": statement["event_count"],
            "visible_surface_sequence": statement["visible_surface_sequence"],
            "master_card_sequence": " ".join(str(row["master_card_id"]) for row in bound),
            "semantic_atom_program": " | ".join(str(row["semantic_atoms"]) for row in bound),
            "card_near_workshop_reading_de": statement["card_near_workshop_reading_de"],
            "concrete_source_expansion_de": statement["concrete_source_expansion_de"],
            "record_program_de": statement["record_program_de"],
            "sentence_boundary_rule": statement["sentence_boundary_rule"],
        })

    instrument_by_unit = {row["unit_id"]: row for row in read_tsv(INSTRUMENTS)}
    astro_rows: list[dict[str, object]] = []
    for group in read_tsv(ASTRO):
        instrument = instrument_by_unit[group["unit_id"]]
        astro_rows.append({
            "group_serial": group["group_serial"],
            "unit_id": group["unit_id"],
            "page": group["page"],
            "locus": group["locus"],
            "event_index": group["event_index"],
            "opaque_local_id": group["opaque_local_id"],
            "local_owner": group["local_owner"],
            "local_namespace": group["local_namespace"],
            "default_local_meaning_de": astro_default(group["local_namespace"]),
            "copy_instruction_de": group["copy_instruction_de"],
            "instrument_reading_de": instrument["complete_instrument_reading_de"],
            "orientation": "NONE",
            "crosspage_key": "NONE",
        })

    unified: list[dict[str, object]] = []
    for row in interlinear:
        unified.append({
            "unified_serial": len(unified) + 1,
            "compiler_mode": "COMBINATORIAL_PROSE",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "local_address": row["local_address"],
            "visible_or_opaque_identity": row["visible_surface"],
            "registered_identity": row["master_card_id"],
            "default_meaning_de": row["short_default_de"],
            "continuous_reading_de": row["statement_translation_de"],
            "owner_or_namespace": row["record_unit_id"],
        })
    for row in astro_rows:
        unified.append({
            "unified_serial": len(unified) + 1,
            "compiler_mode": "LOCAL_ASTRO_NOMENCLATOR",
            "page": row["page"],
            "unit_id": row["unit_id"],
            "local_address": f"{row['locus']}:{row['event_index']}",
            "visible_or_opaque_identity": row["opaque_local_id"],
            "registered_identity": row["opaque_local_id"],
            "default_meaning_de": row["default_local_meaning_de"],
            "continuous_reading_de": row["instrument_reading_de"],
            "owner_or_namespace": row["local_namespace"],
        })

    source_words = read_tsv(SOURCE_WORDS)
    write_tsv(OUT / "HUNDREDTH_CORRECTED_173_CARD_DICTIONARY.tsv", list(dictionary[0]), dictionary)
    write_tsv(OUT / "HUNDREDTH_381_PROSE_INTERLINEAR.tsv", list(interlinear[0]), interlinear)
    write_tsv(OUT / "HUNDREDTH_116_STATEMENT_TRANSLATION.tsv", list(statement_rows[0]), statement_rows)
    write_tsv(OUT / "HUNDREDTH_395_ASTRO_GROUPS.tsv", list(astro_rows[0]), astro_rows)
    write_tsv(OUT / "HUNDREDTH_776_TOTAL_LEDGER.tsv", list(unified[0]), unified)
    write_tsv(OUT / "HUNDREDTH_44_SOURCE_WORDS.tsv", list(source_words[0]), source_words)

    manual_rows = [
        (1, "SET_OWNER", "Read the pictured plant, bath station or diagram locus as silent owner."),
        (2, "CHOOSE_MODE", "Use combinatorial prose for Herbal/Bio; local nomenclator copying for Astro."),
        (3, "SELECT_CARD", "Choose a registered exact card with the required short default."),
        (4, "COMPOSE_BROAD", "OK and OT may take listed quantity, direction, grade and endpoint tails."),
        (5, "COMPOSE_BOUNDED", "OL, L, CHD, CTH and HO take only their listed tail classes."),
        (6, "LEARN_MINI_FAMILY", "CKH, CHK, SHED, SOLK, KCH and SH are memorized as small paradigms."),
        (7, "LEARN_WHOLE", "CHEO, TY and longer exceptional bodies remain exact learned cards."),
        (8, "LONGEST_CARD", "A registered longer body defeats a tempting shorter stem parse."),
        (9, "CHOOSE_RENDERER", "Choose only a q/sh/s/ch/d/t/zero entry licensed for that card."),
        (10, "KEEP_MEANING", "Renderer entry never changes the card value."),
        (11, "WRITE_STATEMENT", "Order owner, selection, quantity/source/target, operation, grade and optional close."),
        (12, "WRAP_LINE", "Break for available drawing space; a physical line is not a sentence boundary."),
        (13, "RESET_OWNER", "At a visibly new bath station or diagram namespace, reset the silent owner."),
        (14, "COPY_ASTRO", "Copy every local Astro group under its owner key; infer no orientation or crosspage join."),
    ]
    manual = [
        {"rule_order": n, "rule_id": rid, "apprentice_instruction": text}
        for n, rid, text in manual_rows
    ]
    write_tsv(OUT / "HUNDREDTH_14_RULE_APPRENTICE_MANUAL.tsv", list(manual[0]), manual)

    questions = [
        ("Q01", "Which exact plant species owns H1-H5?", "Keep the pictured plant as owner; do not force species names."),
        ("Q02", "Which extraction liquids are water, wine, oil or another carrier?", "Use extraction liquid or carrier unless the picture/context supplies more."),
        ("Q03", "Which complaints or body parts motivate the applications?", "Use local body/work site; no disease name is yet tied to a card."),
        ("Q04", "Does each q/sh/s entry correlate with an actual manuscript hand?", "The renderer is executable but historical hand assignment remains open."),
        ("Q05", "Why does the Y card need six whole allographs?", "Learn the set chey/chy/dy/shy/sy/y until a better internal rule appears."),
        ("Q06", "Do the 23 forward paradigm gaps occur elsewhere?", "Retain their short predicted meanings; do not search outside the fixed pages yet."),
        ("Q07", "Are B1-B4 therapeutic baths or practical washing scenes?", "Keep treatment as lead and washing/service as live local rival."),
        ("Q08", "What are B5 and B6 for?", "Read them as figureless service stations, not body treatment."),
        ("Q09", "What do individual A1 signs name?", "Treat each as a local wheel key for celestial/calendar/election content."),
        ("Q10", "What is the order of the 28 A2 and A3-left places?", "No order is visible; preserve local address only."),
        ("Q11", "Are the A3 middle/right labels weather, light, time or properties?", "Keep those short local class defaults and do not merge the wheels."),
        ("Q12", "Is the whole book medical?", "Practitioner compendium is the lead; illustrated natural-artificial modelbook remains the strongest rival."),
    ]
    question_rows = [
        {"question_id": qid, "remaining_question": question, "current_working_default": default}
        for qid, question, default in questions
    ]
    write_tsv(OUT / "HUNDREDTH_12_OPEN_WORKING_QUESTIONS.tsv", list(question_rows[0]), question_rows)

    records: dict[str, dict[str, str]] = {}
    for row in statement_source:
        records.setdefault(row["record_unit_id"], {"page": row["page"], "program": row["record_program_de"]})
    readable = ["# Hundertste Ausgabe: vollständige Lesung der zehn Seiten", ""]
    for unit in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        readable.extend([f"## {unit} — {records[unit]['page']}", "", f"**Gesamtlesung:** {records[unit]['program']}", ""])
        for row in [item for item in statement_rows if item["record_unit_id"] == unit]:
            readable.append(f"- `{row['visible_surface_sequence']}` — {row['concrete_source_expansion_de']}")
        readable.append("")
    for unit in ["A1", "A2", "A3"]:
        instrument = instrument_by_unit[unit]
        readable.extend([f"## {unit} — {instrument['page']}", "", instrument["complete_instrument_reading_de"], ""])
    (OUT / "HUNDREDTH_TEN_PAGE_READABLE_TRANSLATION.md").write_text("\n".join(readable), encoding="utf-8")

    theory = [
        "# Hundertste Werkstattausgabe: beste Arbeitstheorie", "",
        "## Was für ein System ist es?", "",
        "Die bisher beste Theorie ist ein **bildadressiertes praktisches Werkstattregister**.",
        "Es notiert nicht einfach Buchstaben einer laufenden Sprache. Der Schreiber wählt",
        "gelernte Karten für Besitzer, Teil, Maß, Quelle, Ziel, Arbeitsgang, Grad und Schluss.",
        "Ein kleiner produktiver Kern wird komponiert; der große Fachschwanz wird als",
        "Ganzkarte oder lokaler Nomenklator gelernt. Das Bild liefert oft das ausgelassene",
        "Subjekt. Zeilen folgen dem freien Raum nach der Zeichnung, nicht Satzgrenzen.", "",
        "## Was steht auf den zehn Seiten?", "",
        "Die vier Herbal-Seiten lesen sich als fünf illustrierte Pflanzenartikel mit",
        "Ausziehen, Portionieren, Trennen, Sammeln, äußerlicher Anwendung und Verwahrung.",
        "Die drei Biological-Seiten lesen sich als vier figurenbesetzte Bade-/Anwendungs-",
        "records plus zwei figurenlose Dienststationen für Zulauf, Halten, Durchlass und",
        "Ablauf. Die drei Astro-Seiten sind getrennte lokale Nachschlageinstrumente: zwei",
        "Wahlräder, eine mehrteilige Sterntafel und drei unverbundene Rosetten für lokale",
        "Kalender-, Wetter-, Licht-, Zeit- oder Eigenschaftszeichen.", "",
        "## Wie lernen mehrere Schreiber das?", "",
        "Sie teilen 173 Kartenwerte. 139 Karten haben nur eine sichtbare Form. 33 weitere",
        "Familien besitzen einen stabilen freien oder gebundenen Körper; eine Hand wählt",
        "nur eine zugelassene q/sh/s/ch/d/t/Null-Eintrittsgeste. Nur die Karte",
        "`chey/chy/dy/shy/sy/y` wird als kompletter Sechser-Allographensatz gelernt.",
        "OK und OT sind breit produktiv; OL, L, CHD, CTH und HO begrenzt; die übrigen",
        "kleinen Reihen und Ganzkarten werden aus dem Werkstattexemplar gelernt.", "",
        "## Konkreter Wörterbuchkern", "",
        "`AIIN` Sollmaß; `AIN` Anteil; `IIN` Stufe; `AL` Ziel; `AR` Quelle; `AIR` Lauf;",
        "`OK` ansetzen; `OL` weiter; `OT` danach; `OR` Ansatz; `Y` dieser Posten;",
        "`E/EE/EEE` kurz/länger/vollständig; `CHD` umsetzen; `CTH` bereit;",
        "`CKH/CKHE` Durchlass/trennen; `CHK` wärmen; `SHED` absetzen; `SOLK` sammeln;",
        "`HO` Zutat; `CHEO` Auszug; `KCH` bearbeiten; `TY` Teil; `SH` halten.", "",
        "Diese Werte sind kurze Werkstattdefaults, keine behauptete Lautung. Die vollständige",
        "Kartenliste, jede Prosastelle und jede lokale Astrogruppe liegen daneben tabellarisch.", "",
        "## Buchzweck", "",
        "Als gegenwärtiger kreativer Lead ist das Buch ein illustriertes Kompendium für",
        "Pflanzenzubereitung, Bad-/Waschpraxis und himmelsbezogene Wahl- oder Wetterhilfe.",
        "Ein Natur–Kunst–Himmel-Musterbuch bleibt beinahe gleich stark; deshalb werden",
        "medizinische Einzelglossen nie aus der bloßen Kartenform erzwungen.", "",
        "Dies ist bewusst eine kreative Arbeitstheorie für die zehn freigegebenen Seiten,",
        "keine behauptete Entzifferung. f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDREDTH_BEST_WORKING_THEORY.md").write_text("\n".join(theory) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "dictionary_cards": len(dictionary), "surface_forms": len(surfaces),
        "prose_events": len(interlinear), "prose_statements": len(statement_rows),
        "astro_groups": len(astro_rows), "total_groups": len(unified), "source_words": len(source_words),
        "records": len(records), "astro_instruments": len(instrument_by_unit), "manual_rules": len(manual),
        "open_questions": len(question_rows), "productivity_tiers": dict(Counter(row["productivity_tier"] for row in dictionary)),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
