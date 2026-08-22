#!/usr/bin/env python3
"""Build and validate the selected V80 four-role canonical release."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


selected_map = {
    "V80_R3_173_CARD_DICTIONARY.tsv": "V80_CANONICAL_173_CARD_DICTIONARY.tsv",
    "V80_R3_381_EVENT_INTERLINEAR.tsv": "V80_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv",
    "V80_R3_135_FIELD_EDITION.tsv": "V80_CANONICAL_135_FIELD_EDITION.tsv",
    "V80_R3_116_STATEMENT_EDITION.tsv": "V80_CANONICAL_116_STATEMENT_EDITION.tsv",
    "V80_R3_395_ASTRO_GROUPS.tsv": "V80_CANONICAL_395_ASTRO_GROUP_EDITION.tsv",
    "V80_R3_776_UNIFIED_LEDGER.tsv": "V80_CANONICAL_776_UNIFIED_LEDGER.tsv",
    "V80_R3_TEN_PAGE_READABLE_EDITION.md": "V80_COMPLETE_TEN_PAGE_READABLE_EDITION.md",
    "V80_R3_EXECUTABLE_MANUAL.tsv": "V80_CANONICAL_WORKSHOP_MANUAL.tsv",
    "V80_R3_CONTRADICTION_LEDGER.tsv": "V80_CANONICAL_CONTRADICTION_LEDGER.tsv",
}
for source_name, target_name in selected_map.items():
    shutil.copyfile(HERE / source_name, HERE / target_name)

dictionary = tsv_rows(HERE / "V80_CANONICAL_173_CARD_DICTIONARY.tsv")
events = tsv_rows(HERE / "V80_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv")
fields = tsv_rows(HERE / "V80_CANONICAL_135_FIELD_EDITION.tsv")
statements = tsv_rows(HERE / "V80_CANONICAL_116_STATEMENT_EDITION.tsv")
astro = tsv_rows(HERE / "V80_CANONICAL_395_ASTRO_GROUP_EDITION.tsv")
unified = tsv_rows(HERE / "V80_CANONICAL_776_UNIFIED_LEDGER.tsv")
manual = tsv_rows(HERE / "V80_CANONICAL_WORKSHOP_MANUAL.tsv")
contradictions = tsv_rows(HERE / "V80_CANONICAL_CONTRADICTION_LEDGER.tsv")

role_validations = {
    role: json.loads((HERE / name).read_text(encoding="utf-8"))
    for role, name in {
        "R1": "V80_R1_VALIDATION.json",
        "R2": "V80_R2_VALIDATION.json",
        "R3": "V80_R3_VALIDATION.json",
        "R4": "V80_R4_VALIDATION.json",
    }.items()
}

expected_pages = {
    "f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v",
}
models = {
    "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM",
    "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK",
}
formal_values = {
    row["joint_tuple_id"]: row["operational_value"]
    for row in dictionary
    if row["operational_value_class"] == "DERIVED_FORMAL"
}
class_counts = Counter(row["operational_value_class"] for row in dictionary)

checks = {
    "four_role_validations_pass": all(value.get("status") == "PASS" for value in role_validations.values()),
    "canonical_counts": [len(dictionary), len(events), len(fields), len(statements), len(astro), len(unified)] == [173, 381, 135, 116, 395, 776],
    "fixed_ten_page_scope": {row["page"] for row in events + astro} == expected_pages,
    "sealed_pages_absent": not any(row["page"].startswith("f84") for row in events + astro),
    "dictionary_unique": len({row["joint_tuple_id"] for row in dictionary}) == 173,
    "dictionary_class_counts": class_counts == {"EXEMPLAR_VALUE_UNKNOWN": 169, "DERIVED_FORMAL": 4},
    "formal_values_exact": formal_values == {
        "2f1c5e56e8f0ff459065": "FORMAL_PARAMETER_CHANNEL__NOT_A_WORD",
        "308e8ea2d5d190c498e8": "FORMAL_RELATION_SLOT_CHANNEL__NOT_A_WORD",
        "b5fcea1eaed06b2f2291": "FORMAL_RELATION_OR_ENTRY",
        "dcda95c81a5460feb191": "FORMAL_LINK_OR_SLOT",
    },
    "optional_glosses_exact": {
        row["joint_tuple_id"]: row["optional_questioned_master_gloss"]
        for row in dictionary
        if row["optional_questioned_master_gloss"] != "NONE"
    } == {"b5fcea1eaed06b2f2291": "PER?", "dcda95c81a5460feb191": "ET?"},
    "zero_confirmed_words": all(row["confirmed_word"] == "NO" and row["new_word_contribution"] == "0" for row in dictionary),
    "event_serials_exact": [int(row["event_serial"]) for row in events] == list(range(1, 382)),
    "event_source_positions_380": sum(int(row["source_position_contribution"]) for row in events) == 380,
    "e180_e181_accounting": [(row["event_id"], row["source_position_contribution"]) for row in events if row["event_id"] in {"E180", "E181"}] == [("E180", "0"), ("E181", "1")],
    "cross_line_resets_exact": {
        event_id
        for row in statements
        if row["cross_line_owner_reset_events"] != "NONE"
        for event_id in row["cross_line_owner_reset_events"].split("|")
    } == {"E203", "E264", "E291", "E356"},
    "fields_cover_381": sum(int(row["visible_event_count"]) for row in fields) == 381,
    "statements_cover_381": sum(int(row["visible_event_count"]) for row in statements) == 381,
    "astro_serials_exact": [int(row["group_serial"]) for row in astro] == list(range(1, 396)),
    "astro_local_namespaces_13": len({row["canonical_namespace_id"] for row in astro}) == 13,
    "astro_no_orientation_or_join": all(row["orientation_status"] == "LOCAL_EDITORIAL_ADDRESS_ONLY__NO_AUTHORIAL_START_ROTATION_OR_DIRECTION" and row["f68_f69_mapping"] == "NONE__NO_VISIBLE_KEY" for row in astro),
    "unified_serials_exact": [int(row["global_index"]) for row in unified] == list(range(1, 777)),
    "unified_source_positions_775": sum(int(row["source_position_contribution"]) for row in unified) == 775,
    "unified_form_content_separated": all(row["formal_provenance"] == "DERIVED_FORMAL" and row["content_provenance"] == "MASTER_MEMORIZED" for row in unified),
    "exact_model_pair_only": {row["leading_content_model"] for row in unified} | {row["rival_content_model"] for row in unified} == models,
    "manual_22_rules": len(manual) == 22,
    "contradiction_ledger_23_rows": len(contradictions) == 23,
    "central_report_present": (HERE / "V80_FOUR_ROLE_SELECTION.md").stat().st_size > 5000,
    "one_page_theory_present": (HERE / "V80_ONE_PAGE_FINAL_THEORY.md").stat().st_size > 1500,
}

bound_sources = [
    HERE / "V80_R1_REPORT.md",
    HERE / "V80_R1_VALIDATION.json",
    HERE / "V80_R2_HISTORICAL_CANONICAL_THIRD_EDITION_REPORT.md",
    HERE / "V80_R2_VALIDATION.json",
    HERE / "V80_R3_CANONICAL_THIRD_EDITION_REPORT.md",
    HERE / "V80_R3_VALIDATION.json",
    HERE / "V80_R4_CANONICAL_THIRD_EDITION_REPORT.md",
    HERE / "V80_R4_VALIDATION.json",
] + [HERE / source for source in selected_map]
selected_outputs = [HERE / target for target in selected_map.values()] + [
    HERE / "V80_FOUR_ROLE_SELECTION.md",
    HERE / "V80_ONE_PAGE_FINAL_THEORY.md",
]

result = {
    "schema": "SIDEQUEST_V80_FOUR_ROLE_CANONICAL_THIRD_EDITION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "passed": sum(checks.values()),
    "total": len(checks),
    "counts": {
        "cards": len(dictionary),
        "visible_prose_events": len(events),
        "independent_prose_source_positions": sum(int(row["source_position_contribution"]) for row in events),
        "fields": len(fields),
        "statements": len(statements),
        "astro_groups": len(astro),
        "astro_namespaces": len({row["canonical_namespace_id"] for row in astro}),
        "visible_total_groups": len(unified),
        "independent_total_source_positions": sum(int(row["source_position_contribution"]) for row in unified),
        "unknown_cards": class_counts["EXEMPLAR_VALUE_UNKNOWN"],
        "formal_cards": class_counts["DERIVED_FORMAL"],
        "new_words": 0,
    },
    "selection": {
        "canonical_byte_base": "V80_R3",
        "historical_framing": "V80_R2",
        "compact_explanation": "V80_R4",
        "workshop_summary": "V80_R1",
        "lead": "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM",
        "lead_score": 236,
        "rival": "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK",
        "rival_score": 235,
        "semantic_status": "CONTENT_MASTER_MEMORIZED__NOT_DECIPHERED",
    },
    "source_hashes": {path.name: sha256(path) for path in bound_sources},
    "selected_hashes": {path.name: sha256(path) for path in selected_outputs},
    "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
    "next": "STOP__AUTHORIZED_V71_V80_CYCLE_COMPLETE__NO_V81",
}
(HERE / "V80_VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"{result['status']} {result['passed']}/{result['total']}")
raise SystemExit(0 if result["status"] == "PASS" else 1)
