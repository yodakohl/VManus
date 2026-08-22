#!/usr/bin/env python3
"""Build the V80 R4 canonical third edition from frozen selected artifacts.

This is the last fixed-ten-page creative sidequest release.  No manuscript
source is read here; all inputs are already published f84/f84r-free tables.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent

SOURCES = {
    "cards": YOLO / "sidequest_theory_candidates_v69" / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv",
    "herbal_fields": YOLO / "sidequest_theory_candidates_v73" / "V73_SELECTED_20_FIELD_EDITION.tsv",
    "bio_fields": YOLO / "sidequest_theory_candidates_v74" / "V74_SELECTED_115_FIELD_EDITION.tsv",
    "events": YOLO / "sidequest_theory_candidates_v78" / "V78_SELECTED_381_EVENT_INTERLINEAR.tsv",
    "statements": YOLO / "sidequest_theory_candidates_v78" / "V78_SELECTED_116_STATEMENTS.tsv",
    "records": YOLO / "sidequest_theory_candidates_v78" / "V78_SELECTED_11_CONTINUOUS_RECORDS.tsv",
    "astro_groups": YOLO / "sidequest_theory_candidates_v75" / "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv",
    "astro_loci": YOLO / "sidequest_theory_candidates_v75" / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv",
    "astro_instruments": YOLO / "sidequest_theory_candidates_v75" / "V75_SELECTED_THREE_INSTRUMENTS.tsv",
    "manual": YOLO / "sidequest_theory_candidates_v79" / "V79_SELECTED_MACHINE_MANUAL.tsv",
    "repairs": YOLO / "sidequest_theory_candidates_v79" / "V79_SELECTED_REPAIR_DECISIONS.tsv",
}

ET_ID = "dcda95c81a5460feb191"
PER_ID = "b5fcea1eaed06b2f2291"
PARAM_ID = "2f1c5e56e8f0ff459065"
REL_ID = "308e8ea2d5d190c498e8"

LEADING_MODEL = "ILLUSTRATED_PRACTITIONER_BATH_AND_CELESTIAL_LOOKUP_COMPENDIUM"
RIVAL_MODEL = "NATURALIA_COSMOGRAPHIA_WORKSHOP_MODEL_AND_MEMORY_BOOK"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_card_value(card_id: str) -> tuple[str, str, str, str, str]:
    if card_id == ET_ID:
        return (
            "FORMAL_LINK_OR_SLOT",
            "formale Verbindung oder Fortsetzung; kein selbständiger Sachwert",
            "ET?__UND_ODER_AUCH?",
            "FI1_1414_WHOLE_WORD_CATEGORY_ET__OPTIONAL_MASTER_GLOSS_ONLY",
            "OPTIONAL_HISTORICALLY_ATTESTED_CATEGORY__VOYNICH_MAPPING_UNCONFIRMED",
        )
    if card_id == PER_ID:
        return (
            "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS",
            "formale Relation oder Eintragsöffnung; kein selbständiger Sachwert",
            "PER?__DURCH_ODER_GEMAESS?",
            "FI1_1414_WHOLE_WORD_CATEGORY_PER__OPTIONAL_MASTER_GLOSS_ONLY",
            "OPTIONAL_HISTORICALLY_ATTESTED_CATEGORY__VOYNICH_MAPPING_UNCONFIRMED",
        )
    if card_id == PARAM_ID:
        return (
            "FORMAL_NONWORD_CHANNEL",
            "VORGABEPARAMETER_CHANNEL",
            "NONE",
            "NOT_A_WORD",
            "FORMAL_LABEL_NOT_WORD",
        )
    if card_id == REL_ID:
        return (
            "FORMAL_NONWORD_CHANNEL",
            "RELATIONSSLOT_CHANNEL",
            "NONE",
            "NOT_A_WORD",
            "FORMAL_LABEL_NOT_WORD",
        )
    return (
        "OPAQUE_EXEMPLAR_CARD",
        "EXEMPLAR_VALUE_UNKNOWN",
        "NONE",
        "NO_ATTESTED_PORTABLE_WORD_MAPPING",
        "EXEMPLAR_VALUE_UNKNOWN",
    )


cards_source = read_tsv(SOURCES["cards"])
event_source = read_tsv(SOURCES["events"])
statement_source = read_tsv(SOURCES["statements"])
record_source = read_tsv(SOURCES["records"])
herbal_fields = read_tsv(SOURCES["herbal_fields"])
bio_fields = read_tsv(SOURCES["bio_fields"])
astro_groups_source = read_tsv(SOURCES["astro_groups"])
astro_loci = read_tsv(SOURCES["astro_loci"])
astro_instruments = read_tsv(SOURCES["astro_instruments"])
manual_source = read_tsv(SOURCES["manual"])

assert len(cards_source) == 173
assert len(event_source) == 381
assert len(herbal_fields) + len(bio_fields) == 135
assert len(statement_source) == 116
assert len(astro_groups_source) == 395
assert len(astro_loci) == 142
assert {row["page"] for row in event_source + astro_groups_source} == {
    "f10r", "f11r", "f55v", "f56r", "f67r2", "f68r1", "f69v", "f81v", "f82r", "f83r"
}


# 173 exact cards: no productive component or sound claim survives.
cards: list[dict[str, object]] = []
for source in cards_source:
    operational_class, value, optional_word, attestation, word_status = canonical_card_value(source["joint_tuple_id"])
    cards.append(
        {
            "joint_tuple_id": source["joint_tuple_id"],
            "surface_examples_display_only": source["surface_examples"],
            "occurrences": source["occurrences"],
            "pages": source["pages"],
            "opaque_formula_display_only": source["formal_formula_opaque"],
            "operational_class": operational_class,
            "operational_value_de": value,
            "optional_historical_master_word": optional_word,
            "codebook_attestation_status": attestation,
            "portable_word_status": word_status,
            "master_exemplar_content": "OCCURRENCE_BOUND_ONLY__SEE_EVENT_LEDGER",
            "productive_component_claim": "NONE",
            "sound_language_pos_morphology_claim": "NONE",
            "legacy_mnemonic_disposition": "WITHDRAWN_AS_PORTABLE_WORD",
            "semantic_ceiling": "FORMAL_OR_EXEMPLAR_CARD__NOT_CONFIRMED_LEXEME",
        }
    )
card_fields = list(cards[0])
write_tsv(HERE / "V80_R4_CANONICAL_173_CARD_DICTIONARY.tsv", card_fields, cards)
card_map = {row["joint_tuple_id"]: row for row in cards}


# 381 prose events with autonomous operational layer separated from exemplar prose.
events: list[dict[str, object]] = []
for source in event_source:
    card = card_map[source["joint_tuple_id"]]
    event_id = source["event_id"]
    if event_id == "E180":
        source_count = 0
        edge = "ANTICIPATORY_EDGE_COPY_OF_E181__PRESERVE_VISIBLE_COPY"
    elif event_id == "E181":
        source_count = 1
        edge = "MAIN_SOURCE_POSITION_AFTER_EDGE_COPY__READ_ONCE"
    else:
        source_count = 1
        edge = "ORDINARY_VISIBLE_EVENT"
    events.append(
        {
            "event_serial": source["event_serial"],
            "event_id": event_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "locus": source["locus"],
            "field_id": source["field_id"],
            "statement_id": source["statement_id"],
            "joint_tuple_id": source["joint_tuple_id"],
            "image_owner_id": source["image_owner_id"],
            "owner_break_before": source["owner_break_before"],
            "terminal_status": source["terminal_status"],
            "operational_class": card["operational_class"],
            "operational_value_de": card["operational_value_de"],
            "optional_historical_master_word": card["optional_historical_master_word"],
            "source_token_count": source_count,
            "edge_copy_status": edge,
            "master_exemplar_content_de": source["source_expansion_de"],
            "selected_readable_event": source["selected_continuous_event_token"],
            "strongest_content_rival": source["strongest_source_rival"],
            "unsupported_nouns": source["unsupported_nouns_from_prior_context_layer"],
            "content_status": "OCCURRENCE_BOUND_MASTER_EXEMPLAR__NOT_CARD_MEANING",
            "leading_book_model": LEADING_MODEL,
            "rival_book_model": RIVAL_MODEL,
            "semantic_ceiling": "VISIBLE_FORM_PLUS_CREATIVE_EXEMPLAR_LAYER__NOT_PLAINTEXT",
        }
    )
event_fields = list(events[0])
write_tsv(HERE / "V80_R4_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv", event_fields, events)
events_by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
for row in events:
    events_by_field[str(row["field_id"])].append(row)
    events_by_statement[str(row["statement_id"])].append(row)


def operation_sequence(rows: list[dict[str, object]]) -> str:
    return " > ".join(f"{row['event_id']}:{row['operational_class']}" for row in rows)


# 135 fields from the current Herbal and Biological selected editions.
fields: list[dict[str, object]] = []
for source in herbal_fields:
    rows = events_by_field[source["field_id"]]
    fields.append(
        {
            "field_id": source["field_id"],
            "section": "HERBAL",
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "locus": source["locus"],
            "statement_id": source["statement_id"],
            "event_serials": source["event_serials"],
            "image_owner_id": source["whole_plant_owner"],
            "operational_sequence": operation_sequence(rows),
            "master_exemplar_field_text": source["third_edition_field_text"],
            "strongest_content_rival": source["strongest_alternative"],
            "parse_status": source["parse_status"],
            "unsupported_nouns": source["unsupported_nouns"],
            "content_status": "OCCURRENCE_BOUND_HERBAL_EXEMPLAR",
            "semantic_ceiling": "FIELD_FORM_AND_OWNER_VISIBLE__CONTENT_NOT_DECODED",
        }
    )
for source in bio_fields:
    rows = events_by_field[source["field_id"]]
    fields.append(
        {
            "field_id": source["field_id"],
            "section": "BIOLOGICAL",
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "locus": source["locus"],
            "statement_id": source["statement_id"],
            "event_serials": source["event_serials"],
            "image_owner_id": source["local_image_owner"],
            "operational_sequence": operation_sequence(rows),
            "master_exemplar_field_text": source["balneological_field_text"],
            "strongest_content_rival": source["strongest_rival"],
            "parse_status": source["parse_status"],
            "unsupported_nouns": source["unsupported_nouns"],
            "content_status": "OCCURRENCE_BOUND_BATH_OR_STATION_EXEMPLAR",
            "semantic_ceiling": "LOCAL_STATION_FORM_VISIBLE__CONTENT_NOT_DECODED",
        }
    )
fields.sort(key=lambda row: int(str(row["field_id"])[1:]))
write_tsv(HERE / "V80_R4_CANONICAL_135_FIELD_EDITION.tsv", list(fields[0]), fields)


# 116 statements retain V78 continuity, but the dictionary phrase is rebuilt.
statements: list[dict[str, object]] = []
for source in statement_source:
    rows = events_by_statement[source["statement_id"]]
    statements.append(
        {
            "statement_id": source["statement_id"],
            "record_unit_id": source["record_unit_id"],
            "section": source["section"],
            "page": source["page"],
            "constituent_fields": source["constituent_fields"],
            "physical_lines": source["physical_lines"],
            "event_serials": source["event_serials"],
            "event_count": source["event_count"],
            "operational_sequence": operation_sequence(rows),
            "master_exemplar_statement_text": source["continuous_sentence_text"],
            "owner_transition": source["owner_transition"],
            "visible_owner_resets": source["visible_owner_resets"],
            "cross_physical_line_transitions": source["cross_physical_line_transitions"],
            "strongest_content_rival": source["process_or_content_rival"],
            "notation_rival": source["notation_rival"],
            "strongest_contradiction": source["hardest_contradiction"],
            "content_status": "MASTER_EXEMPLAR_LOOKUP_NOT_CARD_TRANSLATION",
            "semantic_ceiling": "CONTINUOUS_FORMAL_STATEMENT_PLUS_CREATIVE_SOURCE_EXPANSION",
        }
    )
write_tsv(HERE / "V80_R4_CANONICAL_116_STATEMENT_EDITION.tsv", list(statements[0]), statements)


# 395 Astro groups: entirely local copied labels, no prose dictionary import.
astro_groups: list[dict[str, object]] = []
for source in astro_groups_source:
    astro_groups.append(
        {
            "group_serial": source["group_serial"],
            "diagram_id": source["diagram_id"],
            "page": source["page"],
            "locus": source["locus"],
            "event_index": source["event_index"],
            "opaque_local_id": source["opaque_local_id"],
            "local_image_owner": source["local_image_owner"],
            "local_namespace": source["local_namespace"],
            "operational_class": "LOCAL_OPAQUE_CELESTIAL_LABEL",
            "operational_value": "COPY_ONLY_WITHIN_LOCAL_NAMESPACE",
            "optional_historical_master_word": "NONE",
            "master_exemplar_label": source["copied_local_meaning_or_label"],
            "strongest_content_rival": source["strongest_astronomical_calendar_or_formal_rival"],
            "orientation_status": source["orientation_status"],
            "f68_f69_mapping": source["f68_f69_mapping"],
            "content_status": "LOCAL_MASTER_EXEMPLAR_LABEL__NOT_WORD_OR_TRANSLATION",
            "semantic_ceiling": "LOCAL_CELESTIAL_NAMESPACE_ONLY",
        }
    )
write_tsv(HERE / "V80_R4_CANONICAL_395_ASTRO_GROUP_EDITION.tsv", list(astro_groups[0]), astro_groups)


# Unified 776-row ledger.
unified: list[dict[str, object]] = []
for row in events:
    unified.append(
        {
            "unified_serial": len(unified) + 1,
            "section": "HERBAL" if str(row["record_unit_id"]).startswith("H") else "BIOLOGICAL",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "local_id": row["event_id"],
            "visible_identity": row["joint_tuple_id"],
            "owner_or_namespace": row["image_owner_id"],
            "operational_formal_value": row["operational_class"],
            "optional_master_word_gloss": row["optional_historical_master_word"],
            "source_token_count": row["source_token_count"],
            "master_exemplar_content": row["master_exemplar_content_de"],
            "strongest_local_rival": row["strongest_content_rival"],
            "leading_book_model": LEADING_MODEL,
            "rival_book_model": RIVAL_MODEL,
            "content_status": row["content_status"],
            "source_artifact": "V80_R4_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv",
        }
    )
for row in astro_groups:
    unified.append(
        {
            "unified_serial": len(unified) + 1,
            "section": "ASTRO",
            "page": row["page"],
            "unit_id": row["diagram_id"],
            "local_id": f"{row['diagram_id']}:{row['opaque_local_id']}",
            "visible_identity": row["opaque_local_id"],
            "owner_or_namespace": row["local_namespace"],
            "operational_formal_value": row["operational_class"],
            "optional_master_word_gloss": "NONE",
            "source_token_count": 1,
            "master_exemplar_content": row["master_exemplar_label"],
            "strongest_local_rival": row["strongest_content_rival"],
            "leading_book_model": LEADING_MODEL,
            "rival_book_model": RIVAL_MODEL,
            "content_status": row["content_status"],
            "source_artifact": "V80_R4_CANONICAL_395_ASTRO_GROUP_EDITION.tsv",
        }
    )
write_tsv(HERE / "V80_R4_CANONICAL_776_UNIFIED_LEDGER.tsv", list(unified[0]), unified)


# Selected workshop manual with autonomous formal values first.
manual: list[dict[str, object]] = []
for source in manual_source:
    row = dict(source)
    if source["operation"] == "EMIT_ET_QUESTIONED":
        row["operation"] = "EMIT_FORMAL_LINK_OR_OPTIONAL_ET"
        row["forward_output"] = "FORMAL_LINK_OR_SLOT; optional master gloss ET?"
        row["failure_if_omitted"] = "historically admissible optional gloss becomes an internally proved word"
    elif source["operation"] == "EMIT_PER_QUESTIONED":
        row["operation"] = "EMIT_FORMAL_RELATION_OR_OPTIONAL_PER"
        row["forward_output"] = "FORMAL_RELATION_OR_ENTRY; optional master gloss PER?"
        row["failure_if_omitted"] = "historically admissible optional gloss becomes an internally proved word"
    row["v80_status"] = "CANONICAL_OPERATIONAL_RULE"
    manual.append(row)
write_tsv(HERE / "V80_R4_CANONICAL_WORKSHOP_MANUAL.tsv", list(manual[0]), manual)


# Complete readable ten-page edition: all 11 prose records and all 142 Astro loci.
def operationalize(text: str) -> str:
    # Protect the full PER phrase before replacing any remaining bare PER token
    # (notably the explicitly bracketed E180 edge-copy annotation).
    protected = text.replace("PER? (DURCH/GEMÄSS?)", "__V80_PER_OPTIONAL__")
    return (
        protected.replace("ET? (UND/AUCH?)", "[FORMAL_LINK_OR_SLOT; optional ET?]")
        .replace("PER?", "[FORMAL_RELATION_OR_ENTRY; optional PER?]")
        .replace("__V80_PER_OPTIONAL__", "[FORMAL_RELATION_OR_ENTRY; optional PER?]")
    )


records_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in record_source:
    records_by_page[row["page"]].append(row)
loci_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in astro_loci:
    loci_by_page[row["page"]].append(row)
instrument_by_page = {row["page"]: row for row in astro_instruments}
page_order = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]
readable = [
    "# V80 R4 — vollständige lesbare Zehnseitenfassung",
    "",
    "Diese Ausgabe ist eine kreative Masterexemplar-Lesung, kein Klartext. Operationaler Formalwert steht vor optionaler Wortglosse; jeder konkrete Inhalt bleibt exemplarisch.",
    "",
]
for page in page_order:
    readable.extend([f"## {page}", ""])
    if page in records_by_page:
        for record in records_by_page[page]:
            readable.extend(
                [
                    f"### Record {record['record_unit_id']}",
                    "",
                    operationalize(record["selected_continuous_german_working_reading"]),
                    "",
                    f"**Stärkster Rivale:** {record['strongest_global_rival']}",
                    "",
                    f"**Decke:** {record['semantic_ceiling']}",
                    "",
                ]
            )
    else:
        instrument = instrument_by_page[page]
        readable.extend(
            [
                f"**Sichtbares System:** {instrument['repaired_visual_system']}",
                "",
                f"**Arbeitslesung:** {instrument['compact_historical_working_reading']}",
                "",
                f"**Rivale:** {instrument['strongest_competing_instrument']}",
                "",
                "### Vollständige lokale Loci",
                "",
            ]
        )
        for locus in loci_by_page[page]:
            readable.append(
                f"- `{locus['locus']}` · `{locus['local_namespace']}` · {locus['complete_copied_local_meaning_or_label']}"
            )
        readable.append("")
readable.extend(
    [
        "## Buchzweck",
        "",
        f"**Redaktionell führend:** `{LEADING_MODEL}`.",
        "",
        f"**Gleichwertig lebender Rivale:** `{RIVAL_MODEL}`.",
        "",
        "Die Reihenfolge ist eine Arbeitsentscheidung, kein entschlüsselter Titel oder Inhaltsnachweis.",
    ]
)
(HERE / "V80_R4_COMPLETE_TEN_PAGE_READABLE_EDITION.md").write_text("\n".join(readable) + "\n", encoding="utf-8")


contradiction_data = [
    ("C01", "CONCRETE_CONTENT_WITHOUT_MASTER", "0/103 prose and 0/28 tested Astro values", "HARD", "Keep every concrete value occurrence-bound."),
    ("C02", "ET_VS_FORMAL_LINK", "Both cover 19/19 visible positions", "UNRESOLVED", "Operational LINK first; ET only optional master gloss."),
    ("C03", "PER_VS_FORMAL_ENTRY", "Read-once repairs form but ENTRY is simpler or tied", "UNRESOLVED", "Operational RELATION/ENTRY first; PER only optional master gloss."),
    ("C04", "EDGE_COPY_HISTORY", "One positive E180/E181 case", "UNRESOLVED", "Use local read-once; do not claim standard catchword."),
    ("C05", "PHYSICAL_LINE_EQUALS_SENTENCE", "19 statement-internal crossings", "REJECTED", "Statement state crosses the line."),
    ("C06", "OWNER_CONTINUITY", "Four cross-line owner resets plus further local scene resets", "REJECTED", "Reset substance, target and direction at each visible break."),
    ("C07", "GLOBAL_BIO_FLOW", "Local contacts exist, global directed circuit absent", "REJECTED", "Use local station readings only."),
    ("C08", "PLANT_SPECIES", "Whole-plant owners visible; species anchors absent", "UNRESOLVED", "Keep every plant unnamed."),
    ("C09", "WATER_MEDIUM_AND_THERAPY", "Coherent in leading model but mostly unpictured", "EXEMPLAR_ONLY", "Retain as creative source prose, never card meaning."),
    ("C10", "ASTRO_START_DIRECTION", "No selected authorial start or rotation", "REJECTED", "Use unordered local namespaces."),
    ("C11", "F68_F69_KEY", "No visible or textual key", "REJECTED", "Keep instruments independent."),
    ("C12", "PRODUCTIVE_STEMS", "Exact-card and renderer history do not license shared meaning", "REJECTED", "No stem, morphology, sound or PAGE_HOST semantics."),
    ("C13", "BOOK_PURPOSE", "Practitioner compendium and model/memory book remain near-tied", "UNRESOLVED", "Show one editorial lead and one live rival."),
    ("C14", "MULTIPLE_SCRIBES", "Shared formal deck fits, but content teaching is not directly observed", "WORKSHOP_HYPOTHESIS", "Treat master/apprentice workflow as plausible generator only."),
    ("C15", "COMPLETE_GERMAN_COVERAGE", "776/776 can be narrated under several content worlds", "NOT_EVIDENCE_OF_TRUTH", "Coverage tests consistency, not historical correctness."),
]
contradictions = [
    {"contradiction_id": cid, "issue": issue, "evidence": evidence, "status": status, "canonical_resolution": resolution}
    for cid, issue, evidence, status, resolution in contradiction_data
]
write_tsv(HERE / "V80_R4_CANONICAL_CONTRADICTION_LEDGER.tsv", list(contradictions[0]), contradictions)


outputs = [
    HERE / "V80_R4_ONE_PAGE_FINAL_THEORY.md",
    HERE / "V80_R4_CANONICAL_THIRD_EDITION_REPORT.md",
    HERE / "V80_R4_CANONICAL_173_CARD_DICTIONARY.tsv",
    HERE / "V80_R4_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv",
    HERE / "V80_R4_CANONICAL_135_FIELD_EDITION.tsv",
    HERE / "V80_R4_CANONICAL_116_STATEMENT_EDITION.tsv",
    HERE / "V80_R4_CANONICAL_395_ASTRO_GROUP_EDITION.tsv",
    HERE / "V80_R4_CANONICAL_776_UNIFIED_LEDGER.tsv",
    HERE / "V80_R4_COMPLETE_TEN_PAGE_READABLE_EDITION.md",
    HERE / "V80_R4_CANONICAL_WORKSHOP_MANUAL.tsv",
    HERE / "V80_R4_CANONICAL_CONTRADICTION_LEDGER.tsv",
]
summary = {
    "schema": "SIDEQUEST_V80_R4_BUILD_V1",
    "status": "PASS",
    "counts": {
        "cards": len(cards),
        "prose_events": len(events),
        "fields": len(fields),
        "statements": len(statements),
        "astro_groups": len(astro_groups),
        "unified_groups": len(unified),
        "pages": len(page_order),
        "records": len(record_source),
        "astro_loci": len(astro_loci),
        "manual_rules": len(manual),
        "contradictions": len(contradictions),
        "formal_link_cards": sum(row["operational_class"] == "FORMAL_LINK_OR_SLOT" for row in cards),
        "formal_relation_entry_cards": sum(row["operational_class"] == "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS" for row in cards),
        "formal_nonword_cards": sum(row["operational_class"] == "FORMAL_NONWORD_CHANNEL" for row in cards),
        "unknown_exemplar_cards": sum(row["operational_class"] == "OPAQUE_EXEMPLAR_CARD" for row in cards),
        "new_words": 0,
        "edge_copy_visible_events": 2,
        "edge_copy_source_tokens": 1,
    },
    "models": {"leading_editorial": LEADING_MODEL, "rival_live": RIVAL_MODEL},
    "source_hashes": {key: sha256(path) for key, path in SOURCES.items()},
    "output_hashes": {path.name: sha256(path) for path in outputs},
    "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
    "ceiling": "COMPLETE_CREATIVE_EXEMPLAR_EDITION__NO_CONFIRMED_WORD_SOUND_LANGUAGE_OR_PLAINTEXT",
}
(HERE / "V80_R4_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
