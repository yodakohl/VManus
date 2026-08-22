#!/usr/bin/env python3
"""Build the deterministic V59 R3 final sidequest release from selected ledgers."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"

PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}
ALLOWED_PAGES = PROSE_PAGES | ASTRO_PAGES

INPUTS = {
    "v22_ledger": YOLO / "sidequest_theory_candidates_v22" / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv",
    "v49_cards": YOLO / "sidequest_theory_candidates_v49" / "V49_SELECTED_173_CARD_DICTIONARY.tsv",
    "v49_events": YOLO / "sidequest_theory_candidates_v49" / "V49_SELECTED_381_EVENT_INTERLINEAR.tsv",
    "v49_fields": YOLO / "sidequest_theory_candidates_v49" / "V49_SELECTED_135_FIELD_TRANSLATION.tsv",
    "v50_hosts": YOLO / "sidequest_theory_candidates_v50" / "V50_SELECTED_HOST_GLOSSES.tsv",
    "v51_cards": YOLO / "sidequest_theory_candidates_v51" / "V51_SELECTED_WHOLE_CARD_GLOSSES.tsv",
    "v52_grammar": YOLO / "sidequest_theory_candidates_v52" / "V52_SELECTED_FIELD_GRAMMAR.tsv",
    "v53_articles": YOLO / "sidequest_theory_candidates_v53" / "V53_SELECTED_FIVE_ARTICLES.tsv",
    "v54_bio": YOLO / "sidequest_theory_candidates_v54" / "V54_SELECTED_SIX_BIO_RECORDS.tsv",
    "v55_diagrams": YOLO / "sidequest_theory_candidates_v55" / "V55_SELECTED_THREE_DIAGRAMS.tsv",
    "v56_phrasebook": YOLO / "sidequest_theory_candidates_v56" / "V56_SELECTED_SHARED_PHRASEBOOK.tsv",
    "v57_manual": YOLO / "sidequest_theory_candidates_v57" / "V57_SELECTED_TEACHING_MANUAL.tsv",
    "v58_comparison": YOLO / "sidequest_theory_candidates_v58" / "V58_SELECTED_MODEL_COMPARISON.tsv",
    "v58_selection": YOLO / "sidequest_theory_candidates_v58" / "V58_FOUR_ROLE_SELECTION.md",
}

OUTPUTS = {
    "cards": HERE / "V59_R3_FINAL_173_CARD_DICTIONARY.tsv",
    "events": HERE / "V59_R3_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv",
    "fields": HERE / "V59_R3_FINAL_135_FIELD_EDITION.tsv",
    "astro": HERE / "V59_R3_FINAL_395_ASTRO_GROUPS.tsv",
    "ledger": HERE / "V59_R3_FINAL_776_EVENT_LEDGER.tsv",
    "units": HERE / "V59_R3_FINAL_14_RECORD_DIAGRAM_READINGS.tsv",
}

# Exact one-sentence rival defaults selected in V58_FOUR_ROLE_SELECTION.md.
NONMEDICAL_RIVAL = {
    "H1": "Wurzelstoff wässern, als Standardzusatz ansetzen, Rest lagern.",
    "H2": "Obere Teile ausziehen, mit Träger verbinden, zweite Charge buchen.",
    "H3": "Blüten-/Krautanteil ausziehen, filtrieren und getrennt verwahren.",
    "H4": "Blattflotte und weichen Rest als zwei Arbeitsfraktionen führen.",
    "H5": "Seltenes klebriges Feuchtlandmaterial klein dosieren und trocknen.",
    "B1": "Hauptkreislauf temperieren, absetzen, klären und weitergeben.",
    "B2": "Einzelbecken füllen, bewegen, filtern, ablassen und nachfüllen.",
    "B3": "Wiederholten Mehrbecken-/Stationszyklus betreiben.",
    "B4": "Bezeichneten Lauf warm reinigen, filtern und neu ansetzen.",
    "B5": "Restbestand erwärmen, halten und an nächste Station übergeben.",
    "B6": "Kalten Vorlauf filtern und zum sichtbaren Ziel bringen.",
    "A1": "7×12-Zeit-/Sektorkonfiguration mit lokaler Bedingung wählen.",
    "A2": "Zentrum plus 28 räumliche Stern-/Kalenderstationen nachschlagen.",
    "A3": "28 lokale Arbeits-, Ruhe-, Beschaffungs- oder Sperrregeln konsultieren.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def question(value: str) -> str:
    value = value.strip()
    return value if value.endswith("?") else value + "?"


def surface_tokens(card: dict[str, str]) -> set[str]:
    return {token.strip().lower() for token in card["surface_examples"].split("|") if token.strip()}


def build_units(
    articles: list[dict[str, str]],
    bio: list[dict[str, str]],
    diagrams: list[dict[str, str]],
    comparison_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    units: list[dict[str, str]] = []
    prose_key_to_unit: dict[str, dict[str, str]] = {}
    page_to_astro_unit: dict[str, dict[str, str]] = {}
    comparison = {row["axis"]: row for row in comparison_rows}
    require(comparison["architecture"]["selection"] == "DOMAIN_NEUTRAL_ARCHITECTURE", "V58 architecture selection changed")
    require(comparison["overall"]["selection"] == "MEDICAL_NARROW_LEAD", "V58 overall selection changed")

    for row in articles:
        unit_id = row["article_id"]
        folio_record = row["folio_record"]
        page = folio_record.split("_R", 1)[0]
        unit = {
            "unit_id": unit_id,
            "unit_kind": "HERBAL_RECORD",
            "folio_record_or_diagram": folio_record,
            "page": page,
            "container_count": row["field_count"],
            "container_unit": "FIELD",
            "event_count": row["event_count"],
            "event_unit": "PROSE_CARD_EVENT",
            "visible_owner_or_formal_role": row["pictured_owner_default"],
            "selected_iatromedical_default_German": row["selected_complete_working_translation_German"],
            "selected_nonmedical_rival_German": NONMEDICAL_RIVAL[unit_id],
            "selected_content_decision": comparison["herbal"]["selection"],
            "confidence": row["confidence"],
            "strongest_contradiction": row["main_contradiction"],
            "text_status": "COMPLETE_RECORD_DEFAULT_NOT_CARD_MEANING",
            "direct_f68_f69_join": "NONE",
            "source_artifact": "V53_SELECTED_FIVE_ARTICLES.tsv;V58_FOUR_ROLE_SELECTION.md",
        }
        units.append(unit)
        prose_key_to_unit[folio_record] = unit

    bio_ordinals: dict[str, int] = defaultdict(int)
    for row in bio:
        unit_id = row["record_id"]
        page = row["folio"]
        bio_ordinals[page] += 1
        folio_record = f"{page}_R{bio_ordinals[page]}"
        unit = {
            "unit_id": unit_id,
            "unit_kind": "BIOLOGICAL_RECORD",
            "folio_record_or_diagram": folio_record,
            "page": page,
            "container_count": row["field_count"],
            "container_unit": "FIELD",
            "event_count": row["event_count"],
            "event_unit": "PROSE_CARD_EVENT",
            "visible_owner_or_formal_role": row["selected_working_role"],
            "selected_iatromedical_default_German": row["complete_working_translation_German"],
            "selected_nonmedical_rival_German": NONMEDICAL_RIVAL[unit_id],
            "selected_content_decision": comparison["biological"]["selection"],
            "confidence": row["confidence"],
            "strongest_contradiction": row["main_contradiction"],
            "text_status": "COMPLETE_RECORD_DEFAULT_NOT_CARD_MEANING",
            "direct_f68_f69_join": "NONE",
            "source_artifact": "V54_SELECTED_SIX_BIO_RECORDS.tsv;V58_FOUR_ROLE_SELECTION.md",
        }
        units.append(unit)
        prose_key_to_unit[folio_record] = unit

    for row in diagrams:
        unit_id = row["diagram_id"]
        page = row["folio"]
        unit = {
            "unit_id": unit_id,
            "unit_kind": "ASTRO_DIAGRAM",
            "folio_record_or_diagram": page,
            "page": page,
            "container_count": row["locus_count"],
            "container_unit": "LOCUS",
            "event_count": row["group_count"],
            "event_unit": "ASTRO_VISIBLE_GROUP",
            "visible_owner_or_formal_role": row["selected_formal_role"],
            "selected_iatromedical_default_German": row["complete_working_translation_German"],
            "selected_nonmedical_rival_German": NONMEDICAL_RIVAL[unit_id],
            "selected_content_decision": comparison["astro"]["selection"],
            "confidence": row["confidence"],
            "strongest_contradiction": row["main_contradiction"],
            "text_status": "COMPLETE_DIAGRAM_DEFAULT_ASTRO_LOCAL_ONLY",
            "direct_f68_f69_join": "NONE",
            "source_artifact": "V55_SELECTED_THREE_DIAGRAMS.tsv;V58_FOUR_ROLE_SELECTION.md",
        }
        units.append(unit)
        page_to_astro_unit[page] = unit

    require([u["unit_id"] for u in units] == [f"H{i}" for i in range(1, 6)] + [f"B{i}" for i in range(1, 7)] + [f"A{i}" for i in range(1, 4)], "unexpected selected unit order")
    return units, prose_key_to_unit, page_to_astro_unit


def build_card_layer(
    source_cards: list[dict[str, str]],
    host_rows: list[dict[str, str]],
    whole_rows: list[dict[str, str]],
    phrase_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, dict[str, str]], dict[str, tuple[str, str]], dict[str, tuple[str, str]]]:
    require(len(source_cards) == 173, "V49 card source must contain 173 rows")
    cards = {row["joint_tuple_id"]: dict(row) for row in source_cards}
    require(len(cards) == 173, "V49 card IDs must be unique")

    mnemonic: dict[str, str] = {}
    licenses: dict[str, list[str]] = defaultdict(list)
    caveats: dict[str, list[str]] = defaultdict(list)

    def add_mnemonic(card_id: str, value: str, license_name: str, caveat: str) -> None:
        value = question(value)
        if card_id in mnemonic:
            require(mnemonic[card_id] == value, f"conflicting global mnemonic for {card_id}: {mnemonic[card_id]} versus {value}")
        else:
            mnemonic[card_id] = value
        if license_name not in licenses[card_id]:
            licenses[card_id].append(license_name)
        if caveat and caveat not in caveats[card_id]:
            caveats[card_id].append(caveat)

    formal_host_ops: dict[str, str] = {}
    for row in host_rows:
        host = row["host"].upper()
        status = row["status"]
        if status == "FORMAL_OPERATOR":
            formal_host_ops[host] = row["v50_selected_value"]
        elif status.startswith("WEAK_"):
            for card_id, card in cards.items():
                if card["page_host"].upper() == host:
                    add_mnemonic(card_id, row["v50_selected_value"], f"V50_HOST_{host}", status)

    for row in whole_rows:
        if row["v51_selected_value"] == "UNBEKANNT" or row["status"].startswith("WITHDRAWN"):
            continue
        matches = [card_id for card_id, card in cards.items() if card["page_host"].upper() == row["card"].upper()]
        require(len(matches) == 1, f"V51 whole card {row['card']} must resolve to one exact ID")
        add_mnemonic(matches[0], row["v51_selected_value"], f"V51_CARD_{row['card']}", row["status"])

    surface_prompt: dict[str, tuple[str, str]] = {}
    formula_prompt: dict[str, tuple[str, str]] = {}
    for row in phrase_rows:
        basis = row["formal_or_exact_basis"]
        if row["tier"] == "A":
            if basis.startswith("exact_surface_"):
                surface = basis.removeprefix("exact_surface_").lower()
                surface_prompt[surface] = (row["minimal_invariant_German"], row["phrase_id"])
            else:
                formula_prompt[basis] = (row["minimal_invariant_German"], row["phrase_id"])
        elif row["tier"] == "B" and row["status"] == "EXPLORATORY_SHARED_MNEMONIC":
            target = basis.removeprefix("exact_joint_tuple_").lower()
            matches = [card_id for card_id, card in cards.items() if target in surface_tokens(card)]
            if not matches:
                matches = [card_id for card_id, card in cards.items() if card["page_host"].lower() == target]
            require(len(matches) == 1, f"V56 exact basis {basis} must resolve to one exact ID")
            add_mnemonic(matches[0], row["minimal_invariant_German"], f"V56_{row['phrase_id']}", row["status"])

    output: list[dict[str, str]] = []
    metadata: dict[str, dict[str, str]] = {}
    for source in source_cards:
        card_id = source["joint_tuple_id"]
        host = source["page_host"].upper()
        formula = source["formal_formula"]
        base_operation = formal_host_ops.get(host, "")
        if formula in formula_prompt:
            operation = formula_prompt[formula][0]
        else:
            operation = base_operation or "NONE_SELECTED"
        if formula.startswith("CLOSE"):
            operation = "FELDABSCHLUSS" if operation == "NONE_SELECTED" else operation + " + FELDABSCHLUSS"

        global_mnemonic = mnemonic.get(card_id, "UNKNOWN_EXEMPLAR")
        if base_operation:
            atomic_value = base_operation
            atomic_status = "FORMAL_OPERATION"
            atomic_license = f"V50_HOST_{host}"
        elif global_mnemonic != "UNKNOWN_EXEMPLAR":
            atomic_value = global_mnemonic
            atomic_status = "WEAK_MNEMONIC"
            atomic_license = ";".join(licenses[card_id])
        else:
            atomic_value = "UNKNOWN_EXEMPLAR"
            atomic_status = "UNKNOWN_EXEMPLAR"
            atomic_license = "NONE"

        prompt_rules: list[str] = []
        for surface in sorted(surface_tokens(source)):
            if surface in surface_prompt:
                prompt_rules.append(f"surface={surface}=>{surface_prompt[surface][0]}")
        if formula in formula_prompt:
            prompt_rules.append(f"formula={formula}=>{formula_prompt[formula][0]}")

        row = {
            "joint_tuple_id": card_id,
            "surface_examples": source["surface_examples"],
            "page_host_coordinate": source["page_host"],
            "formal_formula": formula,
            "opaque_id_status": "OPAQUE_EXACT_JOINT_TUPLE_NOT_WORD",
            "formal_operation_German": operation,
            "selected_atomic_value_German": atomic_value,
            "selected_atomic_status": atomic_status,
            "selected_atomic_license": atomic_license,
            "global_default_mnemonic_German": global_mnemonic,
            "mnemonic_license": ";".join(licenses[card_id]) if card_id in licenses else "NONE",
            "mnemonic_caveat": ";".join(caveats[card_id]) if card_id in caveats else "NO_SELECTED_V50_V51_V56_MNEMONIC",
            "licensed_context_prompt_rule": ";".join(prompt_rules) if prompt_rules else "NONE",
            "creative_local_exemplar_default_German_V49": source["complete_default_German"],
            "creative_default_status": "LOCAL_CREATIVE_EXPANSION_NOT_CARD_MEANING",
            "component_inheritance": "NO_WHOLE_CARD_MEANING_INHERITANCE",
            "mnemonic_globality": "ONE_DEFAULT_PER_EXACT_ID",
            "source_artifact": "V49_SELECTED_173_CARD_DICTIONARY.tsv;V50;V51;V56 selected overrides",
        }
        output.append(row)
        metadata[card_id] = row

    return output, metadata, surface_prompt, formula_prompt


def build_prose(
    source_events: list[dict[str, str]],
    source_fields: list[dict[str, str]],
    card_meta: dict[str, dict[str, str]],
    surface_prompt: dict[str, tuple[str, str]],
    formula_prompt: dict[str, tuple[str, str]],
    prose_key_to_unit: dict[str, dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require(len(source_events) == 381, "V49 event source must contain 381 rows")
    require(len(source_fields) == 135, "V49 field source must contain 135 rows")
    events: list[dict[str, str]] = []

    for serial, source in enumerate(source_events, 1):
        page = source["page"]
        require(page in PROSE_PAGES, f"unlicensed prose page {page}")
        folio_record = f"{page}_R{source['record']}"
        require(folio_record in prose_key_to_unit, f"no selected unit for {folio_record}")
        unit = prose_key_to_unit[folio_record]
        card = card_meta[source["joint_tuple_id"]]
        prompts: list[str] = []
        prompt_licenses: list[str] = []
        if source["surface"].lower() in surface_prompt:
            value, license_name = surface_prompt[source["surface"].lower()]
            prompts.append(value)
            prompt_licenses.append(license_name)
        if source["formal_formula"] in formula_prompt:
            value, license_name = formula_prompt[source["formal_formula"]]
            prompts.append(value)
            prompt_licenses.append(license_name)
        close = source["formal_formula"].startswith("CLOSE")
        events.append(
            {
                "prose_event_id": f"P{serial:04d}",
                "page": page,
                "physical_line": source["locus"],
                "record_number": source["record"],
                "unit_id": unit["unit_id"],
                "field_id": "",
                "field_ordinal": "",
                "event_index_on_line": source["event_index"],
                "event_index_in_field": "",
                "field_position": "",
                "surface": source["surface"],
                "exact_opaque_id": source["joint_tuple_id"],
                "page_host_coordinate": source["page_host"],
                "formal_formula": source["formal_formula"],
                "formal_operation_German": card["formal_operation_German"],
                "selected_atomic_value_German": card["selected_atomic_value_German"],
                "selected_atomic_status": card["selected_atomic_status"],
                "global_default_mnemonic_German": card["global_default_mnemonic_German"],
                "mnemonic_license": card["mnemonic_license"],
                "licensed_context_prompt_German": ";".join(prompts) if prompts else "NONE",
                "context_prompt_license": ";".join(prompt_licenses) if prompt_licenses else "NONE",
                "closure_status": "ATTACHED_FIELD_FINAL_CLOSE" if close else "NONCLOSE",
                "creative_local_event_expansion_German_V49": source["complete_default_German"],
                "unit_reading_ref": unit["unit_id"],
                "line_is_sentence": "NO",
                "semantic_contract": "ATOMIC_OR_UNKNOWN_PLUS_LOCAL_CREATIVE_EXPANSION",
                "source_artifact": "V49_SELECTED_381_EVENT_INTERLINEAR.tsv",
            }
        )

    by_line: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_line[(event["page"], event["record_number"], event["physical_line"])].append(event)
    offsets: dict[tuple[str, str, str], int] = defaultdict(int)
    fields: list[dict[str, str]] = []

    for serial, source in enumerate(source_fields, 1):
        key = (source["page"], source["record"], source["locus"])
        count = int(source["event_count"])
        start = offsets[key]
        members = by_line[key][start : start + count]
        require(len(members) == count, f"field slice mismatch at {key} ordinal {source['field_ordinal']}")
        require(" ".join(event["surface"] for event in members) == source["surface_sequence"], f"surface sequence mismatch at {key} ordinal {source['field_ordinal']}")
        offsets[key] += count
        field_id = f"F{serial:04d}"
        close_flags = [event["closure_status"] != "NONCLOSE" for event in members]
        require(not any(close_flags[:-1]), f"nonfinal close in {field_id}")
        closure_status = "CLOSED" if close_flags[-1] else "OPEN"
        for index, event in enumerate(members, 1):
            if count == 1:
                position = "ONLY"
            elif index == 1:
                position = "FIRST"
            elif index == count:
                position = "LAST"
            else:
                position = "MIDDLE"
            event["field_id"] = field_id
            event["field_ordinal"] = source["field_ordinal"]
            event["event_index_in_field"] = str(index)
            event["field_position"] = position

        unit = prose_key_to_unit[f"{source['page']}_R{source['record']}"]
        fields.append(
            {
                "field_id": field_id,
                "page": source["page"],
                "physical_line": source["locus"],
                "record_number": source["record"],
                "unit_id": unit["unit_id"],
                "field_ordinal": source["field_ordinal"],
                "event_count": source["event_count"],
                "surface_sequence": source["surface_sequence"],
                "exact_opaque_id_sequence": " | ".join(event["exact_opaque_id"] for event in members),
                "formal_sequence": " | ".join(event["formal_formula"] for event in members),
                "formal_operation_sequence_German": " | ".join(event["formal_operation_German"] for event in members),
                "global_mnemonic_sequence_German": " | ".join(event["global_default_mnemonic_German"] for event in members),
                "licensed_context_prompt_sequence_German": " | ".join(event["licensed_context_prompt_German"] for event in members),
                "closure_status": closure_status,
                "creative_local_field_expansion_German_V49": source["complete_creative_translation_German"],
                "unit_reading_ref": unit["unit_id"],
                "line_is_sentence": "NO",
                "field_grammar": "NONCLOSE* TERMINAL?",
                "text_completion_contract": "LOCAL_FIELD_EXPANSION_PLUS_COMPLETE_UNIT_DEFAULT",
                "source_artifact": "V49_SELECTED_135_FIELD_TRANSLATION.tsv",
            }
        )

    for key, line_events in by_line.items():
        require(offsets[key] == len(line_events), f"unassigned prose events remain at {key}")
    require(all(event["field_id"] for event in events), "every prose event must belong to one field")
    return events, fields


def crosscheck_v22_prose(v22_rows: list[dict[str, str]], events: list[dict[str, str]]) -> None:
    v22_prose = [row for row in v22_rows if row["ledger_scope"] == "GDT327_PROSE"]
    require(len(v22_prose) == 381, "V22 selected ledger must contain 381 prose rows")
    keyed = {
        (row["page"], row["locus"], row["record"], row["event_index"]): (row["surface"], row["exact_tuple_id"])
        for row in v22_prose
    }
    require(len(keyed) == 381, "V22 prose keys must be unique")
    for event in events:
        key = (event["page"], event["physical_line"], event["record_number"], event["event_index_on_line"])
        require(key in keyed, f"V22/V49 prose key mismatch: {key}")
        require(keyed[key] == (event["surface"], event["exact_opaque_id"]), f"V22/V49 prose identity mismatch: {key}")


def build_astro(
    v22_rows: list[dict[str, str]],
    page_to_unit: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    source = [row for row in v22_rows if row["ledger_scope"] == "ZL3B_ASTRO_VISIBLE_TOKEN"]
    require(len(source) == 395, "V22 selected ledger must contain 395 Astro rows")
    output: list[dict[str, str]] = []
    for serial, row in enumerate(source, 1):
        page = row["page"]
        require(page in ASTRO_PAGES, f"unlicensed Astro page {page}")
        unit = page_to_unit[page]
        output.append(
            {
                "astro_group_id": f"A{serial:04d}",
                "page": page,
                "unit_id": unit["unit_id"],
                "locus": row["locus"],
                "record": row["record"],
                "physical_line": row["line"],
                "event_index": row["event_index"],
                "slot_address": f"{page}:{row['locus']}:{row['event_index']}",
                "surface": row["surface"],
                "exact_opaque_id": row["exact_tuple_id"],
                "opaque_id_status": "OPAQUE_ASTRO_LOCAL_OCCURRENCE_ID",
                "diagram_formal_role": unit["visible_owner_or_formal_role"],
                "formal_operation": "PAGE_LOCAL_LOOKUP",
                "global_default_mnemonic_German": "UNKNOWN_EXEMPLAR",
                "mnemonic_license": "ASTRO_LOCAL_ONLY_NO_PROSE_IMPORT",
                "local_slot_default_English_V22": row["default_English"],
                "local_slot_status": "LOCAL_ASTRO_MNEMONIC_NOT_WORD_OR_CROSSPAGE_VALUE",
                "unit_reading_ref": unit["unit_id"],
                "line_is_sentence": "NO",
                "direct_f68_f69_join": "NONE",
                "source_event_serial": row["source_event_serial"],
                "source_artifact": "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv routed by V55 selection",
            }
        )
    return output


def build_combined(events: list[dict[str, str]], astro: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for event in events:
        output.append(
            {
                "ledger_row_id": "",
                "domain": "PROSE",
                "page": event["page"],
                "unit_id": event["unit_id"],
                "physical_line_or_locus": event["physical_line"],
                "field_or_slot_id": event["field_id"],
                "event_index": event["event_index_on_line"],
                "surface": event["surface"],
                "exact_opaque_id": event["exact_opaque_id"],
                "opaque_id_status": "OPAQUE_EXACT_JOINT_TUPLE_NOT_WORD",
                "formal_coordinates_or_diagram_role": event["formal_formula"],
                "formal_operation_German": event["formal_operation_German"],
                "selected_atomic_value_German": event["selected_atomic_value_German"],
                "selected_atomic_status": event["selected_atomic_status"],
                "global_default_mnemonic_German": event["global_default_mnemonic_German"],
                "mnemonic_license": event["mnemonic_license"],
                "licensed_context_prompt_German": event["licensed_context_prompt_German"],
                "local_event_or_slot_expansion": event["creative_local_event_expansion_German_V49"],
                "unit_reading_ref": event["unit_reading_ref"],
                "closure_status": event["closure_status"],
                "line_is_sentence": "NO",
                "direct_f68_f69_join": "NONE",
                "semantic_contract": "PROSE_EXACT_FORMAL_MNEMONIC_OR_UNKNOWN_PLUS_LOCAL_UNIT_EXPANSION",
                "source_artifact": event["source_artifact"],
            }
        )
    for row in astro:
        output.append(
            {
                "ledger_row_id": "",
                "domain": "ASTRO",
                "page": row["page"],
                "unit_id": row["unit_id"],
                "physical_line_or_locus": row["locus"],
                "field_or_slot_id": row["slot_address"],
                "event_index": row["event_index"],
                "surface": row["surface"],
                "exact_opaque_id": row["exact_opaque_id"],
                "opaque_id_status": row["opaque_id_status"],
                "formal_coordinates_or_diagram_role": row["diagram_formal_role"],
                "formal_operation_German": row["formal_operation"],
                "selected_atomic_value_German": "UNKNOWN_EXEMPLAR",
                "selected_atomic_status": "ASTRO_LOCAL_ONLY",
                "global_default_mnemonic_German": "UNKNOWN_EXEMPLAR",
                "mnemonic_license": row["mnemonic_license"],
                "licensed_context_prompt_German": "NONE",
                "local_event_or_slot_expansion": row["local_slot_default_English_V22"],
                "unit_reading_ref": row["unit_reading_ref"],
                "closure_status": "NOT_APPLICABLE",
                "line_is_sentence": "NO",
                "direct_f68_f69_join": "NONE",
                "semantic_contract": "ASTRO_LOCAL_ONLY_NO_PROSE_CARD_IMPORT",
                "source_artifact": row["source_artifact"],
            }
        )
    for serial, row in enumerate(output, 1):
        row["ledger_row_id"] = f"L{serial:04d}"
    return output


def main() -> None:
    for name, path in INPUTS.items():
        require(path.is_file(), f"missing selected input {name}: {path}")

    v22_rows = read_tsv(INPUTS["v22_ledger"])
    require(len(v22_rows) == 776, "selected V22 ledger must contain 776 rows")
    require({row["page"] for row in v22_rows} == ALLOWED_PAGES, "selected V22 page scope mismatch")

    grammar_rows = read_tsv(INPUTS["v52_grammar"])
    require(sum(int(row["fields"]) for row in grammar_rows) == 135, "V52 grammar field total changed")
    require(sum(int(row["events"]) for row in grammar_rows) == 381, "V52 grammar event total changed")
    require(sum(int(row["closed_fields"]) for row in grammar_rows) == 90, "V52 grammar close total changed")
    manual_rows = read_tsv(INPUTS["v57_manual"])
    require([row["lesson_id"] for row in manual_rows] == [f"L{i}" for i in range(1, 9)], "V57 teaching curriculum changed")
    comparison_rows = read_tsv(INPUTS["v58_comparison"])

    units, prose_key_to_unit, page_to_unit = build_units(
        read_tsv(INPUTS["v53_articles"]),
        read_tsv(INPUTS["v54_bio"]),
        read_tsv(INPUTS["v55_diagrams"]),
        comparison_rows,
    )
    cards, card_meta, surface_prompt, formula_prompt = build_card_layer(
        read_tsv(INPUTS["v49_cards"]),
        read_tsv(INPUTS["v50_hosts"]),
        read_tsv(INPUTS["v51_cards"]),
        read_tsv(INPUTS["v56_phrasebook"]),
    )
    events, fields = build_prose(
        read_tsv(INPUTS["v49_events"]),
        read_tsv(INPUTS["v49_fields"]),
        card_meta,
        surface_prompt,
        formula_prompt,
        prose_key_to_unit,
    )
    crosscheck_v22_prose(v22_rows, events)
    astro = build_astro(v22_rows, page_to_unit)
    ledger = build_combined(events, astro)

    write_tsv(OUTPUTS["cards"], cards, list(cards[0]))
    write_tsv(OUTPUTS["events"], events, list(events[0]))
    write_tsv(OUTPUTS["fields"], fields, list(fields[0]))
    write_tsv(OUTPUTS["astro"], astro, list(astro[0]))
    write_tsv(OUTPUTS["ledger"], ledger, list(ledger[0]))
    write_tsv(OUTPUTS["units"], units, list(units[0]))

    print("PASS build")
    print(f"cards={len(cards)} prose_events={len(events)} fields={len(fields)} astro_groups={len(astro)} ledger={len(ledger)} units={len(units)}")


if __name__ == "__main__":
    main()
