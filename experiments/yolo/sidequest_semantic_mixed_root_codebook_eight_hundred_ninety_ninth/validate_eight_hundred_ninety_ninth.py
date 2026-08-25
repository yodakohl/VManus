#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_cross_register_stem_unification_eight_hundred_ninety_eighth"
PREFIX = "EIGHT_HUNDRED_NINETY_NINTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    source_marks = read(SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_437_UNIFIED_MARK_DECK.tsv")
    source_vocab = read(SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_231_UNIFIED_WORKSHOP_VOCABULARY.tsv")
    source_units = read(SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_118_UNIFIED_UNIT_EDITION.tsv")
    source_surfaces = read(SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_8_EXACT_SURFACE_BRIDGES.tsv")
    roots = read(HERE / f"{PREFIX}_36_MIXED_ROOT_CODEBOOK.tsv")
    decomposition = read(HERE / f"{PREFIX}_105_TAUGHT_CARD_DECOMPOSITIONS.tsv")
    conditions = read(HERE / f"{PREFIX}_73_MIXED_CODEBOOK_CONDITIONS.tsv")
    vocabulary = read(HERE / f"{PREFIX}_231_MIXED_CODEBOOK_VOCABULARY.tsv")
    marks = read(HERE / f"{PREFIX}_437_MIXED_CODEBOOK_MARK_DECK.tsv")
    units = read(HERE / f"{PREFIX}_118_MIXED_CODEBOOK_UNITS.tsv")
    cards = read(HERE / f"{PREFIX}_6_MIXED_CODEBOOK_JOB_CARDS.tsv")

    check("root_count", len(roots) == 36, len(roots))
    check("root_unique", len({row["root"] for row in roots}) == 36, len({row["root"] for row in roots}))
    check("root_class_split", Counter(row["root_class"] for row in roots) == Counter({"CROSS_REGISTER_ABBREVIATION": 22, "LEARNED_WORKSHOP_ROOT": 14}), Counter(row["root_class"] for row in roots))
    root_by_name = {row["root"]: row for row in roots}
    check("R_is_cool", root_by_name["R"]["atomic_value_de"] == "KUEHL", root_by_name["R"]["atomic_value_de"])
    check("core_values", {name: root_by_name[name]["atomic_value_de"] for name in ["AIIN", "AIR", "AL", "AR", "CH", "K", "L", "OK", "OL", "OR", "OT", "Y"]} == {
        "AIIN": "MASS", "AIR": "LAUF", "AL": "ZIELSTELLE", "AR": "QUELLE", "CH": "ENTNEHMEN", "K": "ZUGEBEN", "L": "LEITEN", "OK": "ANSETZEN", "OL": "FORTSETZEN", "OR": "ANSATZ", "OT": "DANACH", "Y": "POSTEN"
    }, "12/12")

    check("decomposition_identity_count", len(decomposition) == 105, len(decomposition))
    check("decomposition_identity_unique", len({row["identity"] for row in decomposition}) == 105, len({row["identity"] for row in decomposition}))
    check("decomposition_mark_total", sum(int(row["marks"]) for row in decomposition) == 113, sum(int(row["marks"]) for row in decomposition))
    check("decomposition_status_split", Counter(row["composition_status"] for row in decomposition) == Counter({"PREDICTED_ROOT_COMPOSITION": 100, "FUSED_CROSS_REGISTER_WHOLE_FORM": 4, "LEARNED_WHOLE_ROOT": 1}), Counter(row["composition_status"] for row in decomposition))
    check("decomposition_action_split", Counter(row["apprentice_action"] for row in decomposition) == Counter({"READ_ROOT_COMPOSITION": 100, "READ_FUSED_WHOLE_WORD": 4, "READ_LEARNED_WHOLE_ROOT": 1}), Counter(row["apprentice_action"] for row in decomposition))
    check("root_compositions_literal", all(row["selected_short_value_de"] == row["root_sequence_de"] for row in decomposition if row["composition_status"] == "PREDICTED_ROOT_COMPOSITION"), "100/100")
    check("whole_root_is_talam", [row["surface"] for row in decomposition if row["composition_status"] == "LEARNED_WHOLE_ROOT"] == ["talam"], [row["surface"] for row in decomposition if row["composition_status"] == "LEARNED_WHOLE_ROOT"])
    fused_expected = {"ody", "cho", "oteey", "sheey"}
    check("fused_surface_set", {row["surface"] for row in decomposition if row["composition_status"] == "FUSED_CROSS_REGISTER_WHOLE_FORM"} == fused_expected, sorted(row["surface"] for row in decomposition if row["composition_status"] == "FUSED_CROSS_REGISTER_WHOLE_FORM"))
    check("local_fluent_expansions_retained", all(row["local_fluent_expansion_de"].strip() for row in decomposition), "105/105")

    check("condition_count", len(conditions) == 73, len(conditions))
    check("condition_unique", len({row["opaque_local_id"] for row in conditions}) == 73, len({row["opaque_local_id"] for row in conditions}))
    check("condition_R_repairs", sum(row["root_revision"] == "R=KUEHL" for row in conditions) == 2, sum(row["root_revision"] == "R=KUEHL" for row in conditions))
    check("condition_R_final_has_cool", all("KUEHL" in row["mixed_codebook_reading_de"] for row in conditions if row["root_revision"] == "R=KUEHL"), [row["mixed_codebook_reading_de"] for row in conditions if row["root_revision"] == "R=KUEHL"])
    check("condition_R_final_no_generic_reference", all("BEZUG" not in row["mixed_codebook_reading_de"].split(" · ") for row in conditions if row["root_revision"] == "R=KUEHL"), "2/2")

    check("vocabulary_count", len(vocabulary) == 231, len(vocabulary))
    check("vocabulary_unique", len({row["identity"] for row in vocabulary}) == 231, len({row["identity"] for row in vocabulary}))
    check("mark_count", len(marks) == 437, len(marks))
    check("mark_unique", len({row["order_mark_id"] for row in marks}) == 437, len({row["order_mark_id"] for row in marks}))
    check("unit_count", len(units) == 118, len(units))
    check("unit_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    check("job_card_count", len(cards) == 6, len(cards))

    action_expected = Counter({"READ_SHARED_CORE": 251, "READ_ROOT_COMPOSITION": 106, "READ_LOCAL_CONDITION_WORD": 73, "READ_FUSED_WHOLE_WORD": 6, "READ_LEARNED_WHOLE_ROOT": 1})
    check("mark_action_split", Counter(row["apprentice_action"] for row in marks) == action_expected, Counter(row["apprentice_action"] for row in marks))
    check("no_old_taught_action", not any(row["apprentice_action"] == "READ_TAUGHT_WHOLE_WORD" for row in marks), "0")
    check("no_model_copy", not any(row["apprentice_action"] == "COPY_LOCAL_MODEL" for row in marks), "0")
    check("reanalyzed_mark_count", sum(row["tenth_lesson"] == "TAUGHT_CARD_REANALYSED" for row in marks) == 113, sum(row["tenth_lesson"] == "TAUGHT_CARD_REANALYSED" for row in marks))

    source_mark_by_id = {row["order_mark_id"]: row for row in source_marks}
    check("mark_order_preserved", [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks], "437/437")
    check("formal_columns_preserved", all(
        row["surface"] == source_mark_by_id[row["order_mark_id"]]["surface"]
        and row["identity"] == source_mark_by_id[row["order_mark_id"]]["identity"]
        and row["component_recipe"] == source_mark_by_id[row["order_mark_id"]]["component_recipe"]
        and row["page"] == source_mark_by_id[row["order_mark_id"]]["page"]
        for row in marks
    ), "437/437")
    identity_values: dict[str, set[str]] = defaultdict(set)
    identity_actions: dict[str, set[str]] = defaultdict(set)
    for row in marks:
        identity_values[row["identity"]].add(row["concrete_default_de"])
        identity_actions[row["identity"]].add(row["apprentice_action"])
    check("identity_value_invariance", all(len(values) == 1 for values in identity_values.values()), {key: sorted(values) for key, values in identity_values.items() if len(values) > 1})
    check("identity_action_invariance", all(len(values) == 1 for values in identity_actions.values()), {key: sorted(values) for key, values in identity_actions.items() if len(values) > 1})
    vocab_by_id = {row["identity"]: row for row in vocabulary}
    check("vocabulary_mark_value_alignment", all(vocab_by_id[row["identity"]]["short_value_de"] == row["concrete_default_de"] for row in marks), "437/437")
    check("vocabulary_mark_action_alignment", all(vocab_by_id[row["identity"]]["apprentice_action"] == row["apprentice_action"] for row in marks), "437/437")
    check("vocabulary_id_set_preserved", {row["identity"] for row in vocabulary} == {row["identity"] for row in source_vocab}, "231/231")

    surface_roots = {row["surface"]: row["portable_root_de"] for row in source_surfaces}
    check("exact_surface_bridges_preserved", all({row["concrete_default_de"] for row in marks if row["surface"] == surface} == {value} for surface, value in surface_roots.items()), "8/8")
    condition_by_id = {row["opaque_local_id"]: row for row in conditions}
    condition_marks = [row for row in marks if row["master_section"] == "WHEN"]
    check("condition_mark_values_exact", all(row["concrete_default_de"] == condition_by_id[row["source_id"]]["mixed_codebook_reading_de"] for row in condition_marks), "73/73")

    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_unit[source_unit_lookup[(row["order_id"], row["stage"], row["unit"])]["master_unit_id"]].append(row)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("unit_literals_exact", all(row["literal_sequence_de"] == "; ".join(mark["concrete_default_de"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("condition_sequences_exact", all(row["speakable_condition_sequence_de"] == " -> ".join(mark["concrete_default_de"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units if row["section"] == "WHEN"), "6/6")
    check("all_units_zero_model", all(int(row["model_marks"]) == 0 for row in units), "118/118")
    check("all_cards_readable", all(row["mixed_codebook_readable"] == "YES" for row in cards), "6/6")

    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    observed_pages = {row["page"] for row in marks}
    check("fixed_page_allowlist", observed_pages <= allowed_pages, sorted(observed_pages))
    check("sealed_pages_absent_from_data", not any(page.lower().startswith("f84") for page in observed_pages), "0")

    passed = all(item["passed"] for item in checks)
    result = {"status": "PASS" if passed else "FAIL", "checks": len(checks), "passed": sum(bool(item["passed"]) for item in checks), "failed": [item for item in checks if not item["passed"]], "details": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(json.dumps(result["failed"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
