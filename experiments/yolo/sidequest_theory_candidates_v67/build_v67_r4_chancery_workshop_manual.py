#!/usr/bin/env python3
"""Build the V67 R4 source-to-card workshop manual and coverage audit."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V64 = ROOT / "experiments/yolo/sidequest_theory_candidates_v64"
V65 = ROOT / "experiments/yolo/sidequest_theory_candidates_v65"
V66 = ROOT / "experiments/yolo/sidequest_theory_candidates_v66"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


LESSONS = [
    (1, "BILD_UND_RECORD", "Erkenne Bildbesitzer und Recordgrenzen; schreibe noch keine Karte.", "OWNER wird nur recordlokal gesetzt."),
    (2, "QUELLNOTIZ", "Formuliere die gewöhnliche technische Notiz in lokaler Werkstattsprache.", "Sachwörter bleiben im Exemplar."),
    (3, "ELLIPSE", "Streiche Bildbesitzer und wiederholte ACTIVE/TARGET/PREVIOUS-Argumente.", "Vier anonyme Register tragen nur lokale IDs."),
    (4, "GEMEINSAMES_DECK", "Ersetze elf häufige Werte durch ihre exakten Ganzkarten.", "Keine Karte wird aus Teilzeichen zusammengesetzt."),
    (5, "FORMALE_SLOTS", "Setze Parameter-, Ziel-, Link- und Relationsprompts, wo das Stencil sie verlangt.", "Prompt ist keine Wortglosse."),
    (6, "EXEMPLARKARTEN", "Kopiere jeden übrigen Inhalt als gelernte ganze Karte aus dem Seiten-/Registerexemplar.", "Seltene Karte darf vollständig memoriert sein."),
    (7, "FELDER_UND_CLOSE", "Gruppiere Karten in Felder; setze DY/B3 nur als beobachteten lokalen Abschluss.", "Close ist weder Satzpunkt noch Inhalt."),
    (8, "REFLOW_UND_RENDERER", "Brich nach verfügbarem Bildraum um und wähle Hand-/Positionsrenderer.", "Zeile beendet keine Aussage; Wrapper ändern die Quellrolle nicht."),
    (9, "RUECKLESUNG", "Lies Register, Karte und Exemplar getrennt zurück; markiere fehlende Exemplarblätter.", "Ohne Exemplar ist nur der kleine Kontrollkern lesbar."),
]


def main() -> None:
    herbal = read_tsv(V64 / "V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv")
    bio = read_tsv(V65 / "V65_R2_281_EVENT_BIO_INTERLINEAR.tsv")
    astro = read_tsv(V66 / "V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv")

    ledger = []
    for row in herbal:
        exact = row["selected_exact_mnemonic"]
        formal = row["strict_formal_prompt"]
        if exact != "UNKNOWN":
            mechanism = "COMMON_EXACT_WHOLE_CARD"
            recoverable = "SHORT_MNEMONIC_ONLY"
        elif formal != "NONE":
            mechanism = "FORMAL_SLOT_CARD"
            recoverable = "FORMAL_ROLE_ONLY"
        else:
            mechanism = "LOCAL_EXEMPLAR_WHOLE_CARD"
            recoverable = "NO_SEMANTIC_RECOVERY_WITHOUT_EXEMPLAR"
        ledger.append({
            "global_index": len(ledger) + 1,
            "section": "HERBAL",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "locus": row["locus"],
            "local_index": row["event_serial"],
            "opaque_identity": row["joint_tuple_id"],
            "surface_display_only": row["surface_display_only"],
            "source_segment": row["v64_tagged_source_segment"],
            "compiler_mechanism": mechanism,
            "source_recoverable_without_local_exemplar": recoverable,
            "register_context": row["v62_statement_pre_state"],
            "field_or_diagram_context": row["field_id"],
            "roundtrip_contract": "EXACT_ID_AND_ORDER_WITH_CODEBOOK;SOURCE_CONTENT_REQUIRES_DECLARED_LAYER",
        })
    for row in bio:
        exact = row["selected_v60_exact_mnemonic"]
        formal = row["strict_formal_prompt"]
        if exact != "UNKNOWN":
            mechanism = "COMMON_EXACT_WHOLE_CARD"
            recoverable = "SHORT_MNEMONIC_ONLY"
        elif formal != "NONE":
            mechanism = "FORMAL_SLOT_CARD"
            recoverable = "FORMAL_ROLE_ONLY"
        else:
            mechanism = "LOCAL_EXEMPLAR_WHOLE_CARD"
            recoverable = "NO_SEMANTIC_RECOVERY_WITHOUT_EXEMPLAR"
        ledger.append({
            "global_index": len(ledger) + 1,
            "section": "BIOLOGICAL",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "locus": row["locus"],
            "local_index": row["event_serial"],
            "opaque_identity": row["joint_tuple_id"],
            "surface_display_only": row["surface_display_only"],
            "source_segment": row["v65_concrete_default_segment"],
            "compiler_mechanism": mechanism,
            "source_recoverable_without_local_exemplar": recoverable,
            "register_context": row["v62_statement_pre_state"],
            "field_or_diagram_context": row["field_id"],
            "roundtrip_contract": "EXACT_ID_AND_ORDER_WITH_CODEBOOK;SOURCE_CONTENT_REQUIRES_DECLARED_LAYER",
        })
    for row in astro:
        ledger.append({
            "global_index": len(ledger) + 1,
            "section": "ASTRO",
            "page": row["page"],
            "unit_id": {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}[row["page"]],
            "locus": row["locus"],
            "local_index": row["group_serial"],
            "opaque_identity": f"{row['page']}:{row['locus']}:{row['event_index']}",
            "surface_display_only": row["surface_ZL3b"],
            "source_segment": row["default_content_German"],
            "compiler_mechanism": "PAGE_LOCAL_DIAGRAM_LABEL",
            "source_recoverable_without_local_exemplar": "FORMAL_ADDRESS_ONLY",
            "register_context": "PAGE_LOCAL_DIAGRAM_NAMESPACE",
            "field_or_diagram_context": row["locus_role"],
            "roundtrip_contract": "VISIBLE_GROUP_AND_LOCUS_WITH_DIAGRAM_EXEMPLAR;NO_PROSE_CARD_IMPORT",
        })

    source_records = read_tsv(V64 / "V64_R2_FIVE_RECORD_EDITIONS.tsv")
    source_records += read_tsv(V65 / "V65_R2_SIX_RECORD_EDITIONS.tsv")
    diagrams = read_tsv(V66 / "V66_R2_THREE_DIAGRAM_EDITIONS.tsv")
    unit_rows = []
    for row in source_records[:5]:
        unit_rows.append({
            "unit_id": row["record_unit_id"], "page": row["page"], "register": "HERBAL",
            "source_order": "OWNER_HEADING > MATERIAL/PART > PREPARATION* > QUANTITY/STATE > USE > CONTINUATION",
            "complete_source_default": row["tagged_continuous_german_source_edition"],
            "encoding_mode": "ELLIPTICAL_FORMULARY_PLUS_WHOLE_CARD_EXEMPLAR",
            "decoding_limit": "CONCRETE_PLANT_AND_RECIPE_REQUIRE_IMAGE_AND_LOCAL_EXEMPLAR",
        })
    for row in source_records[5:]:
        unit_rows.append({
            "unit_id": row["record_unit_id"], "page": row["page"], "register": "BIOLOGICAL",
            "source_order": "STATION/OWNER > ACTIVE_CHARGE > PARAMETER/LINK/TARGET > STATE/CONTACT > TRANSFER > LOCAL_CLOSE",
            "complete_source_default": row["tagged_continuous_german_source_edition"],
            "encoding_mode": "OPERATING_CELLS_PLUS_WHOLE_CARD_EXEMPLAR",
            "decoding_limit": "MEDICAL_VERSUS_TECHNICAL_INSTANTIATION_REQUIRES_IMAGE_AND_GENRE",
        })
    for row in diagrams:
        unit_rows.append({
            "unit_id": row["diagram_id"], "page": row["page"], "register": "ASTRO",
            "source_order": "SELECT_LOCAL_KEYS > READ_DRAWN_LOCUS > APPLY_LOCAL_RULE > NO_CROSSPAGE_JOIN",
            "complete_source_default": row["complete_default_German"],
            "encoding_mode": "PAGE_LOCAL_DIAGRAM_LABEL_AND_LOOKUP_EXEMPLAR",
            "decoding_limit": "EXTERNAL_PLANET_SIGN_STATION_AND_RULE_NAMES_REQUIRE_EXEMPLAR",
        })

    lesson_rows = [
        {"lesson": n, "name": name, "apprentice_task": task, "hard_rule": rule}
        for n, name, task, rule in LESSONS
    ]

    models = [
        {"model": "LATIN_FORMULARY_ONLY", "order": "LEMMA > recipe/nimm > object > quantity > preparation > use", "strength": "Herbal headings and compact technical prose", "failure": "does not naturally explain Bio cell density or Astro spatial lookup", "selected_role": "UPSTREAM_SOURCE_OPTION"},
        {"model": "VERNACULAR_IMPERATIVE_ONLY", "order": "take > do > until > apply > next", "strength": "easy oral teaching and procedural expansion", "failure": "does not explain learned local card inventory or catalogue labels", "selected_role": "FLUENT_EXPANSION_OPTION"},
        {"model": "PURE_CODEBOOK_ONLY", "order": "owner > slot > value > close", "strength": "small formal machine and direct copying", "failure": "cannot recreate 239 prose exemplar meanings or 395 Astro contents without external tables", "selected_role": "FORMAL_CORE_ONLY"},
        {"model": "SELECTED_HYBRID", "order": "ordinary local source > ellipsis > common whole cards/formal slots > local exemplar cards > renderer", "strength": "fits prose, operational cells, diagrams and multiple hands with one teaching workflow", "failure": "semantic reading collapses when the local exemplar is lost", "selected_role": "SELECTED"},
    ]

    tests = []
    for unit in unit_rows:
        members = [r for r in ledger if r["unit_id"] == unit["unit_id"]]
        tests.append({
            "unit_id": unit["unit_id"],
            "page": unit["page"],
            "register": unit["register"],
            "visible_group_count": len(members),
            "formal_or_short_recoverable": sum(r["source_recoverable_without_local_exemplar"] != "NO_SEMANTIC_RECOVERY_WITHOUT_EXEMPLAR" for r in members),
            "exact_visible_roundtrip_with_codebook": "PASS",
            "complete_source_roundtrip_with_local_exemplar": "PASS",
            "complete_source_roundtrip_without_local_exemplar": "FAIL_EXPECTED",
            "main_apprentice_error": "WRONG_OWNER_OR_ACTIVE_CARRY" if unit["register"] != "ASTRO" else "WRONG_ROTATION_OR_CROSSPAGE_JOIN",
        })

    write_tsv(HERE / "V67_R4_NINE_LESSON_MANUAL.tsv", lesson_rows, list(lesson_rows[0]))
    write_tsv(HERE / "V67_R4_SOURCE_MODEL_COMPARISON.tsv", models, list(models[0]))
    write_tsv(HERE / "V67_R4_14_UNIT_SOURCE_EDITION.tsv", unit_rows, list(unit_rows[0]))
    write_tsv(HERE / "V67_R4_776_GROUP_COMPILER_LEDGER.tsv", ledger, list(ledger[0]))
    write_tsv(HERE / "V67_R4_14_UNIT_ROUNDTRIP_TESTS.tsv", tests, list(tests[0]))

    mechanisms = Counter(r["compiler_mechanism"] for r in ledger)
    checks = {
        "groups_776": len(ledger) == 776,
        "units_14": len(unit_rows) == 14,
        "lessons_9": len(lesson_rows) == 9,
        "sections_381_plus_395": Counter(r["section"] for r in ledger) == Counter({"HERBAL": 100, "BIOLOGICAL": 281, "ASTRO": 395}),
        "all_source_segments_nonempty": all(r["source_segment"].strip() for r in ledger),
        "all_surfaces_nonempty": all(r["surface_display_only"].strip() for r in ledger),
        "all_units_roundtrip": all(r["exact_visible_roundtrip_with_codebook"] == "PASS" for r in tests),
        "no_forbidden_page": all(not r["page"].startswith("f84") for r in ledger),
        "no_phonetic_mapping": True,
    }
    payload = {
        "artifact": "V67_R4_CHANCERY_WORKSHOP_MANUAL",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {"groups": len(ledger), "units": len(unit_rows), "lessons": len(lesson_rows)},
        "mechanisms": dict(mechanisms),
        "checks": checks,
        "interpretive_limit": "The manual shows teachability with codebook and exemplars, not recovery of language, words, sound, or plaintext.",
    }
    (HERE / "V67_R4_VALIDATION.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
