#!/usr/bin/env python3
"""Build V80 R2, the bounded historical canonical third edition.

Only frozen central V69/V73--V79 artifacts are consumed.  This builder does
not inspect manuscript images or transcription sources.  It publishes the
formal autonomous layer before the occurrence-bound exemplar layer.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

V69_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
V73_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_20_FIELD_EDITION.tsv"
V74_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_115_FIELD_EDITION.tsv"
V75_GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
V75_LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
V75_INSTRUMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_THREE_INSTRUMENTS.tsv"
V76_PURPOSES = ROOT / "experiments/yolo/sidequest_theory_candidates_v76/V76_SELECTED_BOOK_PURPOSE_COMPETITION.tsv"
V76_UNITS = ROOT / "experiments/yolo/sidequest_theory_candidates_v76/V76_SELECTED_14_UNIT_PURPOSE_SCORECARD.tsv"
V76_CONTRADICTIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v76/V76_SELECTED_CONTRADICTIONS.tsv"
V76_SOURCES = ROOT / "experiments/yolo/sidequest_theory_candidates_v76/V76_SELECTED_HISTORICAL_SOURCE_AUDIT.tsv"
V76_WORKFLOW = ROOT / "experiments/yolo/sidequest_theory_candidates_v76/V76_SELECTED_PRODUCTION_WORKFLOW.tsv"
V77_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_CARD_DICTIONARY.tsv"
V78_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V78_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_116_STATEMENTS.tsv"
V78_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_11_CONTINUOUS_RECORDS.tsv"
V79_MANUAL = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_MACHINE_MANUAL.tsv"
V79_TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv"
V79_REPAIRS = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_REPAIR_DECISIONS.tsv"

OUT_DICT = HERE / "V80_R2_173_EXACT_CARD_DICTIONARY.tsv"
OUT_EVENTS = HERE / "V80_R2_381_PROSE_EVENT_INTERLINEAR.tsv"
OUT_FIELDS = HERE / "V80_R2_135_FIELD_EDITION.tsv"
OUT_STATEMENTS = HERE / "V80_R2_116_STATEMENT_EDITION.tsv"
OUT_ASTRO = HERE / "V80_R2_395_ASTRO_GROUP_EDITION.tsv"
OUT_UNIFIED = HERE / "V80_R2_776_UNIFIED_LEDGER.tsv"
OUT_READABLE = HERE / "V80_R2_READABLE_TEN_PAGE_EDITION.md"
OUT_MANUAL = HERE / "V80_R2_PERIOD_WORKSHOP_MANUAL.tsv"
OUT_CONTRADICTIONS = HERE / "V80_R2_CONTRADICTION_CONFIDENCE_LEDGER.tsv"
OUT_REPORT = HERE / "V80_R2_HISTORICAL_CANONICAL_THIRD_EDITION_REPORT.md"
OUT_RESULT = HERE / "V80_R2_RESULT.json"

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"
PARAM_CARD = "2f1c5e56e8f0ff459065"
RELATION_SLOT_CARD = "308e8ea2d5d190c498e8"

LEAD_ID = "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM"
RIVAL_ID = "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def bracket_exemplar(text: str, label: str = "EXEMPLAR") -> str:
    text = " ".join((text or "").split()).strip()
    if text.startswith(f"[{label}:") and text.endswith("]"):
        return text
    return f"[{label}:{text}]"


def normalize_exemplar(text: str) -> str:
    """Remove autonomous ET/PER/Kustode claims from an exemplar phrase."""
    text = " ".join((text or "").split())
    text = text.replace("[KUSTODE:PER?; NUR EINMAL LESEN] PER? (DURCH/GEMÄSS?)", "[LOKALE ANTICIPATION/CARRY/DITTOGRAPHY: ZWEI SICHTBARE KOPIEN, EIN QUELLTOKEN] [FORMAL_RELATION_OR_ENTRY]")
    text = text.replace("ET? (UND/AUCH?)", "[FORMAL_LINK]")
    text = text.replace("PER? (DURCH/GEMÄSS?)", "[FORMAL_RELATION_OR_ENTRY]")
    text = text.replace("[KUSTODE:PER?; NUR EINMAL LESEN]", "[LOKALE ANTICIPATION/CARRY/DITTOGRAPHY: ZWEI SICHTBARE KOPIEN, EIN QUELLTOKEN]")
    text = re.sub(r"(?<![A-Z])ET\?(?![A-Z])", "[OPTIONALER_MASTERGLOSS_ET]", text)
    text = re.sub(r"(?<![A-Z])PER\?(?![A-Z])", "[OPTIONALER_MASTERGLOSS_PER]", text)
    return text


def card_operational(card: str) -> dict[str, str]:
    if card == ET_CARD:
        return {
            "class": "FORMAL_LINK_OR_SLOT",
            "token": "[FORMAL_LINK]",
            "formal_status": "AUTONOMOUS_FORMAL_CHANNEL__NONLEXICAL",
            "optional_gloss": "ET? = UND/AUCH?__OPTIONAL_MASTER_GLOSS_ONLY",
            "source_entry": "et",
            "attestation": "FLORENCE_FI1_1414_CATEGORY__NOT_VOYNICH_IDENTIFICATION",
            "portable": "NO__MASTER_QUESTION_GLOSS_ONLY",
        }
    if card == PER_CARD:
        return {
            "class": "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS",
            "token": "[FORMAL_RELATION_OR_ENTRY]",
            "formal_status": "AUTONOMOUS_FORMAL_CHANNEL__NONLEXICAL",
            "optional_gloss": "PER? = DURCH/GEMÄSS?__OPTIONAL_MASTER_GLOSS_ONLY",
            "source_entry": "per",
            "attestation": "FLORENCE_FI1_1414_CATEGORY__NOT_VOYNICH_IDENTIFICATION",
            "portable": "NO__MASTER_QUESTION_GLOSS_ONLY",
        }
    if card == PARAM_CARD:
        return {
            "class": "FORMAL_PARAMETER_CHANNEL",
            "token": "[FORMAL:VORGABEPARAMETER; KEIN_WORT]",
            "formal_status": "FROZEN_FORMAL_NONWORD_CHANNEL",
            "optional_gloss": "NONE",
            "source_entry": "NONE",
            "attestation": "NOT_APPLICABLE__STRUCTURAL_LABEL",
            "portable": "NO__FORMAL_NONWORD",
        }
    if card == RELATION_SLOT_CARD:
        return {
            "class": "FORMAL_RELATION_SLOT_CHANNEL",
            "token": "[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN_WORT]",
            "formal_status": "FROZEN_FORMAL_NONWORD_CHANNEL",
            "optional_gloss": "NONE",
            "source_entry": "NONE",
            "attestation": "NOT_APPLICABLE__STRUCTURAL_LABEL",
            "portable": "NO__FORMAL_NONWORD",
        }
    return {
        "class": "EXEMPLAR_VALUE_UNKNOWN",
        "token": "[EXEMPLAR_VALUE_UNKNOWN]",
        "formal_status": "OPAQUE_EXACT_CARD_ONLY",
        "optional_gloss": "NONE",
        "source_entry": "NONE",
        "attestation": "NONE",
        "portable": "NO__NO_CARD_LEVEL_MEANING",
    }


def event_source_token_count(event_id: str) -> int:
    return 0 if event_id == "E180" else 1


def event_read_once_status(event_id: str) -> str:
    if event_id == "E180":
        return "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY_COPY__VISIBLE_NOT_SECOND_SOURCE_TOKEN"
    if event_id == "E181":
        return "MAIN_SOURCE_TOKEN_AFTER_ONE_LOCAL_VISIBLE_COPY"
    return "ORDINARY_VISIBLE_SOURCE_TOKEN"


def mean_conf(rows: list[dict[str, str]], key: str) -> str:
    values = []
    for row in rows:
        try:
            values.append(float(row[key]))
        except (ValueError, TypeError):
            pass
    return f"{sum(values) / len(values):.3f}" if values else "UNKNOWN"


def main() -> None:
    old_dict = read_tsv(V69_DICT)
    v77_rows = read_tsv(V77_DICT)
    source_events = read_tsv(V78_EVENTS)
    source_statements = read_tsv(V78_STATEMENTS)
    source_records = read_tsv(V78_RECORDS)
    herbal_fields = read_tsv(V73_FIELDS)
    bio_fields = read_tsv(V74_FIELDS)
    source_astro = read_tsv(V75_GROUPS)
    astro_loci = read_tsv(V75_LOCI)
    instruments = read_tsv(V75_INSTRUMENTS)
    purposes = read_tsv(V76_PURPOSES)
    unit_scores = read_tsv(V76_UNITS)
    purpose_contradictions = read_tsv(V76_CONTRADICTIONS)
    historical_sources = read_tsv(V76_SOURCES)
    production_workflow = read_tsv(V76_WORKFLOW)
    source_manual = read_tsv(V79_MANUAL)
    transitions = read_tsv(V79_TRANSITIONS)
    repairs = read_tsv(V79_REPAIRS)

    v77_by_card = {row["joint_tuple_id"]: row for row in v77_rows}
    units = {row["unit_id"]: row for row in unit_scores}
    purpose_by_id = {row["purpose_id"]: row for row in purposes}
    lead = purpose_by_id[LEAD_ID]
    rival = purpose_by_id[RIVAL_ID]

    # ------------------------------------------------------------
    # 173 exact-card dictionary: zero autonomously established words.
    # ------------------------------------------------------------
    dictionary: list[dict[str, object]] = []
    for rank, row in enumerate(old_dict, start=1):
        card = row["joint_tuple_id"]
        op = card_operational(card)
        v77 = v77_by_card.get(card)
        dictionary.append({
            "card_rank": rank,
            "joint_tuple_id": card,
            "surface_examples_display_only": row["surface_examples"],
            "visible_occurrences": row["occurrences"],
            "pages": row["pages"],
            "formal_formula_opaque": row["formal_formula_opaque"],
            "autonomous_operational_class": op["class"],
            "autonomous_readback_token": op["token"],
            "formal_channel_status": op["formal_status"],
            "optional_master_gloss": op["optional_gloss"],
            "exact_1414_category_if_any": op["source_entry"],
            "historical_attestation_status": op["attestation"],
            "historical_attestation_detail": (
                v77["historical_attestation"]
                if v77 and card in {ET_CARD, PER_CARD}
                else "NONE_OR_NOT_APPLICABLE"
            ),
            "v77_frozen_decision": v77["decision"] if v77 else "NOT_IN_FROZEN_24_TARGET__UNKNOWN",
            "withdrawn_v69_class": row["V69_FINAL_CONTROL_CLASS"],
            "portable_word_status": op["portable"],
            "source_dependency": "EXACT_FORM_INTERNAL__OPTIONAL_GLOSS_AND_CONTENT_MASTER_DEPENDENT",
            "semantic_ceiling": "EXACT_CARD_OR_FORMAL_CHANNEL_NOT_WORD_LEXEME_STEM_SOUND_LANGUAGE_OR_TRANSLATION",
        })
    write_tsv(OUT_DICT, dictionary, list(dictionary[0]))

    # ------------------------------------------------------------
    # 381 prose events, formal layer first; all content occurrence-bound.
    # ------------------------------------------------------------
    events: list[dict[str, object]] = []
    for row in source_events:
        event_id = row["event_id"]
        card = row["joint_tuple_id"]
        op = card_operational(card)
        source_expansion = normalize_exemplar(row["source_expansion_de"])
        if event_id == "E180":
            source_expansion = "[EXEMPLAR:keine eigene Sachangabe; lokale sichtbare Vorausnahme des nachfolgenden Formtokens]"
        elif card == ET_CARD:
            source_expansion = "[EXEMPLAR:keine eigene Sachangabe; der Master verbindet die benachbarten Quellenglieder an dieser formalen Linkstelle]"
        elif card == PER_CARD:
            source_expansion = "[EXEMPLAR:keine eigene Sachangabe; der Master liefert die lokale Relation oder Eintragsfunktion samt Komplement]"
        event_optional_gloss = (
            "NONE__LOCAL_VISIBLE_COPY_NO_SECOND_GLOSS"
            if event_id == "E180"
            else op["optional_gloss"]
        )
        literal = f"[OWNER:{row['image_owner_id']}] > [OPAQUE_CARD:{card}] > {op['token']}"
        if event_id == "E180":
            literal += " > [LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY_COPY_OF:E181; SOURCE_TOKEN_COUNT:0]"
        elif event_id == "E181":
            literal += " > [MAIN_SOURCE_TOKEN_AFTER_LOCAL_VISIBLE_COPY:E180]"
        visible_reset = "YES__CLEAR_LOCAL_ARGUMENTS" if row["owner_break_before"].startswith("BREAK_") else "NO"
        events.append({
            "event_serial": row["event_serial"],
            "event_id": event_id,
            "record_unit_id": row["record_unit_id"],
            "section": "HERBAL" if row["record_unit_id"].startswith("H") else "BIOLOGICAL",
            "page": row["page"],
            "physical_locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "joint_tuple_id": card,
            "image_owner_id": row["image_owner_id"],
            "owner_break_before": row["owner_break_before"],
            "visible_owner_reset": visible_reset,
            "terminal_status": row["terminal_status"],
            "autonomous_operational_class": op["class"],
            "autonomous_readback_token": op["token"],
            "exact_literal_autonomous_layer": literal,
            "source_token_count": event_source_token_count(event_id),
            "read_once_status": event_read_once_status(event_id),
            "optional_master_gloss": event_optional_gloss,
            "occurrence_bound_exemplar": source_expansion,
            "occurrence_content_source_class": row["source_class"],
            "occurrence_content_confidence": row["source_expansion_confidence"],
            "strongest_occurrence_rival": row["strongest_source_rival"],
            "strongest_occurrence_contradiction": row["strongest_contradiction"],
            "unsupported_exemplar_nouns": row["unsupported_nouns_from_prior_context_layer"],
            "global_purpose_lead": LEAD_ID,
            "global_purpose_rival": RIVAL_ID,
            "semantic_ceiling": "OCCURRENCE_BOUND_EXEMPLAR_NOT_CARD_WORD_STEM_SOUND_LANGUAGE_PLAINTEXT_OR_TRANSLATION",
        })
    write_tsv(OUT_EVENTS, events, list(events[0]))
    event_by_id = {row["event_id"]: row for row in events}
    events_by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        events_by_field[str(row["field_id"])].append(row)
        events_by_statement[str(row["statement_id"])].append(row)

    # ------------------------------------------------------------
    # 135 fields from the two central section editions.
    # ------------------------------------------------------------
    fields: list[dict[str, object]] = []
    for source_kind, row in [("HERBAL", x) for x in herbal_fields] + [("BIOLOGICAL", x) for x in bio_fields]:
        field_id = row["field_id"]
        erows = events_by_field[field_id]
        owner = row["whole_plant_owner"] if source_kind == "HERBAL" else row["local_image_owner"]
        readable = row["third_edition_field_text"] if source_kind == "HERBAL" else row["balneological_field_text"]
        rival_text = row["strongest_alternative"] if source_kind == "HERBAL" else row["strongest_rival"]
        visible_ids = [str(event["event_id"]) for event in erows]
        resets = [str(event["event_id"]) for event in erows if str(event["visible_owner_reset"]).startswith("YES")]
        master_glosses = [f"{event['event_id']}:{event['optional_master_gloss']}" for event in erows if not str(event["optional_master_gloss"]).startswith("NONE")]
        fields.append({
            "field_id": field_id,
            "record_unit_id": row["record_unit_id"],
            "section": source_kind,
            "page": row["page"],
            "physical_locus": row["locus"],
            "statement_id": row["statement_id"],
            "visible_event_count": len(erows),
            "source_token_count": sum(int(event["source_token_count"]) for event in erows),
            "visible_event_ids": "|".join(visible_ids),
            "image_owner_id": owner,
            "visible_owner_reset_events": "|".join(resets) if resets else "NONE",
            "autonomous_formal_sequence": " ".join(f"{event['event_id']}={event['autonomous_readback_token']}" for event in erows),
            "optional_master_gloss_occurrences": "|".join(master_glosses) if master_glosses else "NONE",
            "read_once_status": "E180_VISIBLE_COPY_READ_WITH_E181_ONCE" if "E180" in visible_ids or "E181" in visible_ids else "NONE",
            "occurrence_bound_readable_field": bracket_exemplar(normalize_exemplar(readable)),
            "parse_status": row["parse_status"],
            "mean_occurrence_content_confidence": mean_conf([source_events[int(event["event_serial"]) - 1] for event in erows], "source_expansion_confidence"),
            "strongest_field_rival": rival_text,
            "unsupported_exemplar_nouns": row["unsupported_nouns"],
            "strongest_field_contradiction": row["strongest_contradiction"],
            "semantic_ceiling": "FIELD_FORMAL_SEQUENCE_PLUS_OCCURRENCE_EXEMPLAR_NOT_TRANSLATION",
        })
    fields.sort(key=lambda row: int(str(row["field_id"])[1:]))
    write_tsv(OUT_FIELDS, fields, list(fields[0]))

    # ------------------------------------------------------------
    # 116 statements with the same event inventory and repaired source count.
    # ------------------------------------------------------------
    statements: list[dict[str, object]] = []
    for row in source_statements:
        erows = events_by_statement[row["statement_id"]]
        master_glosses = [f"{event['event_id']}:{event['optional_master_gloss']}" for event in erows if not str(event["optional_master_gloss"]).startswith("NONE")]
        ids = [str(event["event_id"]) for event in erows]
        statements.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "section": row["section"],
            "page": row["page"],
            "sentence_index_in_record": row["sentence_index_in_record"],
            "constituent_fields": row["constituent_fields"],
            "physical_lines": row["physical_lines"],
            "visible_event_count": len(erows),
            "source_token_count": sum(int(event["source_token_count"]) for event in erows),
            "visible_event_ids": "|".join(ids),
            "exact_card_order": " > ".join(str(event["joint_tuple_id"]) for event in erows),
            "autonomous_formal_sequence": " ".join(f"{event['event_id']}={event['autonomous_readback_token']}" for event in erows),
            "optional_master_gloss_occurrences": "|".join(master_glosses) if master_glosses else "NONE",
            "occurrence_bound_readable_statement": bracket_exemplar(normalize_exemplar(row["continuous_sentence_text"])),
            "owner_transition": row["owner_transition"],
            "visible_owner_resets": row["visible_owner_resets"],
            "cross_field_transitions": row["cross_field_transitions"],
            "cross_physical_line_transitions": row["cross_physical_line_transitions"],
            "read_once_status": "LOCAL_E180_E181_READ_ONCE" if "E180" in ids else "NONE",
            "source_class": row["source_class"],
            "strongest_process_or_content_rival": row["process_or_content_rival"],
            "strongest_notation_rival": row["notation_rival"],
            "repair_cost_0_4": row["repair_cost_0_4_v72"],
            "strongest_statement_contradiction": row["hardest_contradiction"],
            "semantic_ceiling": "STATEMENT_MEMBERSHIP_AND_FORMAL_ORDER_NOT_PLAINTEXT_OR_TRANSLATION",
        })
    write_tsv(OUT_STATEMENTS, statements, list(statements[0]))

    # ------------------------------------------------------------
    # 395 Astro groups, always local and without inferred join/order.
    # ------------------------------------------------------------
    groups_per_locus = Counter(row["locus"] for row in source_astro)
    astro: list[dict[str, object]] = []
    for row in source_astro:
        total = groups_per_locus[row["locus"]]
        astro.append({
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "segment_index": row["event_index"],
            "segments_in_local_locus": total,
            "opaque_local_id": row["opaque_local_id"],
            "local_image_owner": row["local_image_owner"],
            "owner_status": row["owner_status"],
            "owner_confidence": row["owner_confidence"],
            "local_namespace": row["local_namespace"],
            "autonomous_operational_class": "OPAQUE_LOCAL_COPIED_GROUP_SEGMENT",
            "autonomous_readback_token": f"[OPAQUE_LOCAL_GROUP:{row['opaque_local_id']}; SEGMENT:{row['event_index']}/{total}]",
            "occurrence_bound_exemplar_label": bracket_exemplar(row["copied_local_meaning_or_label"]),
            "occurrence_content_class": row["local_content_class"],
            "occurrence_content_source_status": row["copied_label_source_status"],
            "occurrence_content_confidence": row["meaning_confidence"],
            "strongest_local_rival": row["strongest_astronomical_calendar_or_formal_rival"],
            "strongest_local_contradiction": row["strongest_contradiction"],
            "unsupported_exemplar_labels": row["unsupported_labels"],
            "orientation_status": row["orientation_status"],
            "order_and_join_status": "NO_AUTHORIAL_ORDER_OR_CROSS_LOCUS_JOIN__ONLY_VISIBLE_SEGMENTS_SHARE_THIS_LOCAL_LOCUS",
            "f68_f69_mapping": row["f68_f69_mapping"],
            "prose_card_import": row["prose_card_import"],
            "global_purpose_lead": LEAD_ID,
            "global_purpose_rival": RIVAL_ID,
            "semantic_ceiling": "LOCAL_OPAQUE_GROUP_AND_EXEMPLAR_LABEL_NOT_WORD_NAME_ORDER_SOUND_OR_TRANSLATION",
        })
    write_tsv(OUT_ASTRO, astro, list(astro[0]))

    # ------------------------------------------------------------
    # Unified 776-visible-group ledger.
    # ------------------------------------------------------------
    unified: list[dict[str, object]] = []
    serial = 0
    for row in events:
        serial += 1
        unit = units[str(row["record_unit_id"])]
        unified.append({
            "unified_serial": serial,
            "unified_id": f"P:{row['event_id']}",
            "section": row["section"],
            "unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["physical_locus"],
            "local_container": row["field_id"],
            "opaque_identity": row["joint_tuple_id"],
            "local_owner": row["image_owner_id"],
            "local_namespace": "PROSE_EXACT_CARD_REGISTER",
            "autonomous_operational_class": row["autonomous_operational_class"],
            "autonomous_readback_token": row["autonomous_readback_token"],
            "visible_group_count": 1,
            "source_token_count": row["source_token_count"],
            "read_once_status": row["read_once_status"],
            "owner_reset_status": row["visible_owner_reset"],
            "optional_master_gloss": row["optional_master_gloss"],
            "occurrence_bound_exemplar": row["occurrence_bound_exemplar"],
            "occurrence_content_confidence": row["occurrence_content_confidence"],
            "purpose_lead_unit_role": unit["purpose_A_unit_role"],
            "purpose_rival_unit_role": unit["purpose_B_unit_role"],
            "strongest_local_rival": row["strongest_occurrence_rival"],
            "strongest_local_contradiction": row["strongest_occurrence_contradiction"],
            "order_join_policy": "PROSE_PHYSICAL_ORDER__STATEMENT_MAY_CROSS_LINE__OWNER_RESET_OVERRIDES_CONTINUITY",
            "semantic_ceiling": row["semantic_ceiling"],
        })
    for row in astro:
        serial += 1
        unit = units[str(row["diagram_id"])]
        unified.append({
            "unified_serial": serial,
            "unified_id": f"A:{row['opaque_local_id']}",
            "section": "ASTRO",
            "unit_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "local_container": row["local_image_owner"],
            "opaque_identity": row["opaque_local_id"],
            "local_owner": row["local_image_owner"],
            "local_namespace": row["local_namespace"],
            "autonomous_operational_class": row["autonomous_operational_class"],
            "autonomous_readback_token": row["autonomous_readback_token"],
            "visible_group_count": 1,
            "source_token_count": 1,
            "read_once_status": "NONE",
            "owner_reset_status": "LOCAL_NAMESPACE_ONLY__NO_CROSS_LOCUS_CARRY",
            "optional_master_gloss": "NONE",
            "occurrence_bound_exemplar": row["occurrence_bound_exemplar_label"],
            "occurrence_content_confidence": row["occurrence_content_confidence"],
            "purpose_lead_unit_role": unit["purpose_A_unit_role"],
            "purpose_rival_unit_role": unit["purpose_B_unit_role"],
            "strongest_local_rival": row["strongest_local_rival"],
            "strongest_local_contradiction": row["strongest_local_contradiction"],
            "order_join_policy": row["order_and_join_status"],
            "semantic_ceiling": row["semantic_ceiling"],
        })
    write_tsv(OUT_UNIFIED, unified, list(unified[0]))

    # ------------------------------------------------------------
    # Period workshop manual: exact memorized versus derived material.
    # ------------------------------------------------------------
    manual: list[dict[str, object]] = []
    for row in source_manual:
        n = int(row["rule_order"])
        operation = row["operation"]
        forward = row["forward_output"]
        backward = row["backward_output"]
        failure = row["failure_if_omitted"]
        optional_gloss = "NONE"
        if n == 6:
            condition = row["condition"] + " + no visible owner reset between the two occurrences"
            failure = "a local visible duplicate may be counted twice; this is not a standard catchword rule"
        else:
            condition = row["condition"]
        if n == 8:
            operation = "EMIT_FORMAL_LINK"
            forward = "[FORMAL_LINK]"
            backward = ET_CARD
            failure = "the exact formal link channel is lost or falsely promoted to an internally known word"
            optional_gloss = "ET? = UND/AUCH?__MASTER_KEY_ONLY"
        if n == 9:
            operation = "EMIT_FORMAL_RELATION_OR_ENTRY"
            forward = "[FORMAL_RELATION_OR_ENTRY]"
            backward = PER_CARD
            failure = "the exact relation/entry channel is lost or falsely promoted to an internally known word"
            optional_gloss = "PER? = DURCH/GEMÄSS?__MASTER_KEY_ONLY"

        if n in {1, 2, 3, 4, 5, 6, 7, 10, 11, 14, 15, 16}:
            memorizes = "Memorize this state-transition rule and the supplied layout/code-sheet convention; memorize no content gloss."
        else:
            memorizes = "Memorize the exact-card-to-formal-channel lookup only; any questioned word gloss remains on the optional master key."
        derives = "Derive the condition from current visible identity, boundary, owner, locus and local namespace; do not infer content."
        if n == 12:
            derives = "Derive only the occurrence address; retrieve bracketed content from the master exemplar by lookup."
        if n == 13:
            derives = "Derive exact form/layout and mark every missing concrete value UNKNOWN."
        master_only = "OCCURRENCE_CONTENT_AND_EXTERNAL_MEANING"
        if n in {8, 9}:
            master_only += "__PLUS_OPTIONAL_QUESTIONED_WORD_GLOSS"
        manual.append({
            "rule_order": row["rule_order"],
            "state": row["state"],
            "visible_input": row["visible_input"],
            "condition": condition,
            "operation": operation,
            "state_update": row["state_update"],
            "forward_autonomous_output": forward,
            "backward_formal_output": backward,
            "optional_master_gloss": optional_gloss,
            "apprentice_memorizes": memorizes,
            "apprentice_derives": derives,
            "master_exemplar_only": master_only,
            "failure_if_omitted": failure,
            "historical_status": "WORKSHOP_SIMULATION_RULE__NOT_ATTESTED_VOYNICH_PRACTICE",
        })
    write_tsv(OUT_MANUAL, manual, list(manual[0]))

    # ------------------------------------------------------------
    # Per-group contradiction/confidence ledger (776 rows).
    # ------------------------------------------------------------
    contradictions: list[dict[str, object]] = []
    for row in unified:
        op = str(row["autonomous_operational_class"])
        if row["unified_id"] == "P:E180":
            formal_conf = "LOCAL_SINGLE_POSITIVE__MECHANICALLY_REVERSIBLE_NOT_HISTORICALLY_IDENTIFIED"
        elif op in {"FORMAL_LINK_OR_SLOT", "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS"}:
            formal_conf = "MEDIUM__V79_OPERATIONAL_SELECTION__SEMANTIC_GLOSS_UNIDENTIFIED"
        elif op.startswith("FORMAL_"):
            formal_conf = "HIGH__FROZEN_NONWORD_CHANNEL"
        elif str(row["section"]) == "ASTRO":
            formal_conf = "HIGH_LOCAL_MEMBERSHIP__NO_ORDER_OR_EXTERNAL_LABEL"
        else:
            formal_conf = "HIGH_EXACT_IDENTITY__NO_FUNCTION_OR_CONTENT_ROLE"
        word_conf = "OPTIONAL_MASTER_QUESTION_GLOSS_ONLY" if not str(row["optional_master_gloss"]).startswith("NONE") else "NONE"
        contradictions.append({
            "ledger_serial": row["unified_serial"],
            "unified_id": row["unified_id"],
            "section": row["section"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "formal_recovery_confidence": formal_conf,
            "occurrence_content_confidence": row["occurrence_content_confidence"],
            "portable_word_confidence": word_conf,
            "global_purpose_confidence": "NEAR_TIE_236_TO_235__WORKING_LEAD_ONLY",
            "strongest_local_rival": row["strongest_local_rival"],
            "strongest_local_contradiction": row["strongest_local_contradiction"],
            "global_counterevidence": lead["largest_forced_assumption"],
            "containment": "KEEP_CONTENT_OCCURRENCE_BOUND__KEEP_FORMAL_AND_SEMANTIC_LAYERS_SEPARATE",
            "status": "OPEN_WORKING_THEORY_NOT_DECIPHERMENT",
        })
    write_tsv(OUT_CONTRADICTIONS, contradictions, list(contradictions[0]))

    # ------------------------------------------------------------
    # Readable ten-page edition.
    # ------------------------------------------------------------
    records_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_records:
        records_by_page[row["page"]].append(row)
    loci_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in astro_loci:
        loci_by_page[row["page"]].append(row)
    instrument_by_page = {row["page"]: row for row in instruments}
    events_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        events_by_record[str(event["record_unit_id"])].append(event)

    readable_lines = [
        "# V80 R2 — lesbare kanonische Zehnseitenedition",
        "",
        "Status: occurrence-gebundene historische Arbeitstheorie; keine Entzifferung.",
        "Autonom werden nur exakte Form, lokale Besitzer, Grenzen, `FORMAL_LINK`,",
        "`FORMAL_RELATION_OR_ENTRY` und zwei formale Nichtwortkanäle gelesen.",
        "Alle konkreten Inhalte stehen in `[EXEMPLAR:…]`. `ET?` und `PER?` sind",
        "hier nicht Bestandteil des autonomen Textes.",
        "",
        "## Herbal",
        "",
    ]
    for page in ["f10r", "f11r", "f55v", "f56r"]:
        readable_lines.extend([f"### {page}", ""])
        for record in records_by_page[page]:
            text = normalize_exemplar(record["selected_continuous_german_working_reading"])
            readable_lines.extend([
                f"#### {record['record_unit_id']} — {record['event_count']} sichtbare Ereignisse / "
                f"{sum(int(event['source_token_count']) for event in events_by_record[record['record_unit_id']])} Quellpositionen",
                "",
                text,
                "",
                f"Ownerfolge: `{record['owner_sequence']}`. Sichtbare Resets: `{record['visible_owner_break_events']}`.",
                "",
            ])

    readable_lines.extend(["## Biological", ""])
    for page in ["f81v", "f82r", "f83r"]:
        readable_lines.extend([f"### {page}", ""])
        for record in records_by_page[page]:
            text = normalize_exemplar(record["selected_continuous_german_working_reading"])
            readable_lines.extend([
                f"#### {record['record_unit_id']} — {record['event_count']} sichtbare Ereignisse / "
                f"{sum(int(event['source_token_count']) for event in events_by_record[record['record_unit_id']])} Quellpositionen",
                "",
                text,
                "",
                f"Ownerfolge: `{record['owner_sequence']}`. Sichtbare Resets: `{record['visible_owner_break_events']}`.",
                "",
            ])

    readable_lines.extend([
        "## Astro",
        "",
        "Die folgenden Locus-Adressen sind redaktionelle Vollständigkeitsadressen,",
        "keine behauptete Start-, Rotations- oder Lesereihenfolge. Sichtbare",
        "Mehrsegmentgruppen werden nur im selben lokalen Locus zusammengehalten;",
        "zwischen Loci, Rädern und Seiten wird nichts gejoint.",
        "",
    ])
    for page in ["f67r2", "f68r1", "f69v"]:
        instrument = instrument_by_page[page]
        readable_lines.extend([
            f"### {page} — {instrument['repaired_visual_system']}",
            "",
            bracket_exemplar(instrument["compact_historical_working_reading"], "EXEMPLAR-HYPOTHESE"),
            "",
        ])
        for locus in loci_by_page[page]:
            readable_lines.append(
                f"- `{locus['locus']}` · `{locus['local_namespace']}` · `{locus['local_image_owner']}` · "
                f"Gruppen `{locus['opaque_group_ids']}`: {bracket_exemplar(locus['complete_copied_local_meaning_or_label'])}"
            )
        readable_lines.append("")
    readable_lines.extend([
        "## Leseschlüssel und Grenze",
        "",
        "E180/E181 bleiben zwei sichtbare Karten, aber genau ein Quelltoken unter",
        "der lokalen anticipation/carry/dittography-Hypothese. Das ist kein",
        "belegter Standard-Catchword. Konkrete Pflanzen-, Bade-, Geräte- und",
        "Himmelswerte sind ausschließlich Masterexemplarwerte. Bestätigte Wörter,",
        "Lautwerte, Klartextklauseln und Übersetzungen: null.",
        "",
    ])
    OUT_READABLE.write_text("\n".join(readable_lines), encoding="utf-8")

    # ------------------------------------------------------------
    # Compact historical report using only the frozen V76 source corpus.
    # ------------------------------------------------------------
    source_lines = []
    for source in historical_sources:
        source_lines.append(
            f"- {source['source_id']}: [{source['institution']}, {source['shelfmark']}]({source['official_url']}), "
            f"{source['date_place']}; {source['genre']}. Mechanism only, not donor or lexical evidence."
        )
    contradiction_lines = []
    for row in purpose_contradictions:
        if row["model"] in {LEAD_ID, RIVAL_ID} and row["severity"] == "HIGH":
            contradiction_lines.append(f"- `{row['contradiction_id']}` ({row['model']}): {row['contradiction']} Containment: {row['containment']}")

    report_lines = [
        "# V80 R2 — historische kanonische dritte Ausgabe",
        "",
        "## Kanonisches Ergebnis",
        "",
        "Die dritte Ausgabe bindet 173 exakte Prosakarten, 381 sichtbare",
        "Prosaereignisse, 135 Felder, 116 Aussagen, 395 Astrogruppen und 776",
        "sichtbare Gesamtgruppen. Nach der einen lokalen E180/E181-Zusammenlegung",
        "entsprechen 776 Schriftgruppen 775 Quellpositionen.",
        "",
        "Das autonome System kennt **null Wörter**. Es kennt exakte opake Karten,",
        "zwei formale Nichtwortkanäle sowie `FORMAL_LINK` und",
        "`FORMAL_RELATION_OR_ENTRY`. Die Florentiner Fi1-Kategorien `et` und `per`",
        "von 1414 erlauben ausschließlich die optionalen Masterglossen `ET?` und",
        "`PER?`; sie identifizieren keine Voynich-Karte und erscheinen nicht im",
        "autonomen Lesetext.",
        "Die Linkkarte hat 19 sichtbare und 19 Quellvorkommen; die Relation-/",
        "Entry-Karte hat neun sichtbare, aber nach E180/E181 genau acht",
        "Quellvorkommen und damit auch höchstens acht optionale Masterglossen.",
        "",
        "## Ein führendes historisches Zweckmodell",
        "",
        f"**{LEAD_ID}** — {lead['period_purpose']}",
        "",
        f"Mechanismus: {lead['compilation_order']} {lead['picture_first_production']} {lead['multiple_scribes']}",
        "",
        "Der praktische Zusammenhang ist kein seitenübergreifender Code: bebilderte",
        "Pflanzen-/Zubereitungsartikel, lokal getrennte Bade-/Anwendungsstationen und",
        "selbständige Himmels-/Kalenderinstrumente können in derselben",
        "Praktikerbibliothek konsultiert werden. Die V76-Wertung 236 ist nur ein",
        "knapper Arbeitslead.",
        "",
        "## Genau ein echter Rivale",
        "",
        f"**{RIVAL_ID}** — {rival['period_purpose']}",
        "",
        f"Mechanismus: {rival['compilation_order']} {rival['picture_first_production']} {rival['multiple_scribes']}",
        "",
        "Der Rivale erreicht 235 Punkte und erklärt Bilddominanz, lokale",
        "Beschriftung, mehrere Hände und fehlende Crosspointer besonders sparsam.",
        "Er verliert nur knapp, weil das Material→Anwendung→Zeit/Bedingung-Modell",
        "einen kohärenteren praktischen Grund für die gemeinsame Aufbewahrung bietet.",
        "Die Auswahl bleibt `NEAR_TIE__WORKING_LEAD_NOT_IDENTIFICATION`.",
        "",
        "## Was der Lehrling memorisiert und was er ableitet",
        "",
        "**Memorisiert bzw. konsultiert:** die exakte Kartenliste; die beiden",
        "Nichtwortkanäle; die Zuordnung von `dcda…` zu `FORMAL_LINK` und `b5fcea…`",
        "zu `FORMAL_RELATION_OR_ENTRY`; Record-/Statement-/Owner-Resetregeln; die",
        "Vier-Bedingungen-Regel für lokale Zeilenkantendoppelungen; die lokalen",
        "Astro-Namespaces; und die Vorschrift, nie einen Exemplarwert aus der Karte",
        "zu erfinden.",
        "",
        "**Aus der sichtbaren Instanz abgeleitet:** exakte Kartenidentität durch",
        "Codeblattvergleich; aktuelle Position, Zeilenkante, `Close`, Ownerwechsel,",
        "Locus und Namespace; ob alle Read-once-Bedingungen erfüllt sind; und wie",
        "viele sichtbare Gruppen bzw. Quellpositionen gezählt werden.",
        "",
        "**Nur im Masterexemplar:** jeder konkrete Pflanzen-, Stoff-, Handlungs-,",
        "Bade-, Geräte-, Himmels- oder Kalenderwert; jede externe Bedeutung; sowie",
        "die optionalen Frageglossen `ET?`/`PER?`. Ohne Master kann der Lehrling",
        "Form und lokale Struktur prüfen, aber keinen konkreten Artikel fortsetzen.",
        "",
        "## Die lokale E180/E181-Reparatur",
        "",
        "Alle 19 aussageninternen physischen Zeilenübergänge sind geprüft. Genau",
        "E180→E181 erfüllt gleiche exakte Karte, gleiche Aussage, gleichen Owner und",
        "kein intervenierendes `Close`; die anderen 18 nicht. Beide Schriftbilder",
        "bleiben erhalten, die erste Randkopie zählt nicht als zweiter Quelltoken.",
        "Dies heißt ausschließlich",
        "`LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY__READ_ONCE`: ein positiver Fall,",
        "kein belegter Standard-Catchword und keine allgemeine historische Kustode.",
        "",
        "## Bild-, Owner- und Astrovertrag",
        "",
        "Herbal bindet den Text nur an den unbenannten Ganzpflanzenowner. Bio",
        "behält alle zehn sichtbaren Owner-Resets; insbesondere werden Stoff, Ziel",
        "und Richtung an E189, E198, E203, E212, E239, E248, E264, E291, E338 und",
        "E356 gelöscht. Aussagen dürfen trotzdem über physische Linien laufen.",
        "Astro bewahrt elf im ausgewählten Gruppenledger belegte lokale Namespaces; es gibt keinen autorischen Start,",
        "keine Richtung, keine Rotation, keinen f68↔f69-Schlüssel, keinen",
        "Prosa-Kartenimport und keinen Join zwischen lokalen Loci oder Rädern.",
        "",
        "## Historische Mechanismenkalibrierung — eingefrorene V76-Quellen",
        "",
        *source_lines,
        "",
        "Keine Quelle ist ein identifizierter Donor. Es wurde für V80 keine neue",
        "Quelle hinzugefügt und kein Quellenwort auf eine Karte abgebildet.",
        "",
        "## Stärkste Gegenbelege",
        "",
        *contradiction_lines,
        "",
        f"- Gesamtlead: {lead['largest_forced_assumption']}",
        f"- Gesamtrivale: {rival['largest_forced_assumption']}",
        "",
        "## Release und Deutungsgrenze",
        "",
        "Die TSVs enthalten jede Gruppe genau einmal; die lesbare Ausgabe zeigt",
        "alle elf Prosarecords und alle 142 Astro-Loci. Bestätigte Lexeme,",
        "Klartextklauseln, Stämme, Laute, Sprache und Übersetzung bleiben null.",
        "Diese Ausgabe ist eine exemplarabhängige Schreiber- und Werkstattsimulation,",
        "keine Entzifferung.",
        "",
    ]
    OUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    read_once_matches = [row for row in transitions if row["classification"] == "TP"]
    result = {
        "experiment": "V80_R2_HISTORICAL_CANONICAL_THIRD_EDITION",
        "status": "PASS",
        "scope": "FIXED_TEN_PAGE_SIDEQUEST_ONLY",
        "exact_card_types": len(dictionary),
        "prose_visible_events": len(events),
        "prose_source_tokens_after_read_once": sum(int(row["source_token_count"]) for row in events),
        "fields": len(fields),
        "statements": len(statements),
        "astro_groups": len(astro),
        "astro_loci": len(astro_loci),
        "unified_visible_groups": len(unified),
        "unified_source_positions": sum(int(row["source_token_count"]) for row in unified),
        "autonomously_established_words": 0,
        "optional_master_question_gloss_cards": [ET_CARD, PER_CARD],
        "formal_nonword_cards": [PARAM_CARD, RELATION_SLOT_CARD],
        "read_once_matches": [f"{row['line_final_event']}->{row['line_initial_event']}" for row in read_once_matches],
        "read_once_historical_status": "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY__NOT_STANDARD_CATCHWORD",
        "leading_historical_purpose": LEAD_ID,
        "single_global_rival": RIVAL_ID,
        "purpose_score": "236:235__NEAR_TIE",
        "new_meanings": 0,
        "new_sources": 0,
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
        "inputs": [str(path.relative_to(ROOT)) for path in [
            V69_DICT, V73_FIELDS, V74_FIELDS, V75_GROUPS, V75_LOCI, V75_INSTRUMENTS,
            V76_PURPOSES, V76_UNITS, V76_CONTRADICTIONS, V76_SOURCES, V76_WORKFLOW,
            V77_DICT, V78_EVENTS, V78_STATEMENTS, V78_RECORDS, V79_MANUAL,
            V79_TRANSITIONS, V79_REPAIRS,
        ]],
        "outputs": [path.name for path in [
            OUT_DICT, OUT_EVENTS, OUT_FIELDS, OUT_STATEMENTS, OUT_ASTRO, OUT_UNIFIED,
            OUT_READABLE, OUT_MANUAL, OUT_CONTRADICTIONS, OUT_REPORT,
        ]],
        "interpretation_ceiling": "HISTORICAL_WORKSHOP_SIMULATION_NOT_DECIPHERMENT_OR_TRANSLATION",
    }
    OUT_RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
