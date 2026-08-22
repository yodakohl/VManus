#!/usr/bin/env python3
"""Validate the bounded V73 R3 Herbal third edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    event_path = OUT / "V73_R3_100_EVENT_INTERLINEAR.tsv"
    field_path = OUT / "V73_R3_20_FIELD_EDITION.tsv"
    statement_path = OUT / "V73_R3_19_STATEMENT_REVISIONS.tsv"
    article_path = OUT / "V73_R3_FIVE_ARTICLES.tsv"
    report_path = OUT / "V73_R3_TECHNICAL_REPORT.md"
    build_path = OUT / "V73_R3_BUILD_SUMMARY.json"
    required = [event_path, field_path, statement_path, article_path, report_path, build_path]
    check("required_outputs_exist", all(path.is_file() for path in required), [path.name for path in required])

    events = read_tsv(event_path)
    fields = read_tsv(field_path)
    statements = read_tsv(statement_path)
    articles = read_tsv(article_path)
    source_events = {
        int(row["event_serial"]): row
        for row in read_tsv(V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv")
        if 1 <= int(row["event_serial"]) <= 100
    }
    source_fields = {
        row["field_id"]: row
        for row in read_tsv(V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv")
        if row["record_unit_id"] in {"H1", "H2", "H3", "H4", "H5"}
    }
    selected_owners = {
        row["unit_id"]: row
        for row in read_tsv(V71 / "V71_SELECTED_OWNER_LEDGER.tsv")
        if row["unit_kind"] == "PROSE_FIELD" and row["record_or_diagram"] in {"H1", "H2", "H3", "H4", "H5"}
    }
    selected_statements = {
        row["statement_id"]: row
        for row in read_tsv(V72 / "V72_SELECTED_116_STATEMENTS.tsv")
        if row["record_unit_id"] in {"H1", "H2", "H3", "H4", "H5"}
    }

    check("exact_100_events", len(events) == 100, len(events))
    check("event_serials_1_through_100_once", sorted(int(row["event_serial"]) for row in events) == list(range(1, 101)), "1..100")
    check("exact_20_fields", len(fields) == 20, len(fields))
    check("field_ids_F001_through_F020_once", [row["field_id"] for row in fields] == [f"F{i:03d}" for i in range(1, 21)], [row["field_id"] for row in fields])
    check("exact_19_statements", len(statements) == 19, len(statements))
    check("statement_ids_match_frozen_selection", {row["statement_id"] for row in statements} == set(selected_statements), sorted(row["statement_id"] for row in statements))
    check("exact_five_articles", len(articles) == 5, len(articles))
    check("record_ids_H1_through_H5", [row["record_unit_id"] for row in articles] == ["H1", "H2", "H3", "H4", "H5"], [row["record_unit_id"] for row in articles])

    allowed_pages = {"f10r", "f11r", "f55v", "f56r"}
    check("only_fixed_herbal_pages", {row["page"] for row in events} == allowed_pages, sorted({row["page"] for row in events}))
    check("all_event_cells_nonblank", all(all(value.strip() for value in row.values()) for row in events), "all columns populated")
    check("all_field_cells_nonblank", all(all(value.strip() for value in row.values()) for row in fields), "all columns populated")
    check("all_statement_cells_nonblank", all(all(value.strip() for value in row.values()) for row in statements), "all columns populated")
    check("all_article_cells_nonblank", all(all(value.strip() for value in row.values()) for row in articles), "all columns populated")

    immutable_columns = [
        "page", "locus", "record_unit_id", "field_id", "statement_id", "joint_tuple_id",
        "surface_display_only", "formal_formula_opaque", "terminal_status", "parse_status",
        "selected_exact_mnemonic", "strict_formal_prompt", "event_template",
    ]
    immutable_ok = True
    for row in events:
        source = source_events[int(row["event_serial"])]
        immutable_ok &= all(row[column] == source[column] for column in immutable_columns)
    check("frozen_event_identity_and_control_columns_exact", immutable_ok, immutable_columns)

    field_identity_ok = True
    for row in fields:
        source = source_fields[row["field_id"]]
        for column in ["record_unit_id", "page", "locus", "statement_id", "event_count", "event_serials"]:
            field_identity_ok &= row[column] == source[column]
    check("frozen_field_membership_exact", field_identity_ok, "record/page/locus/statement/count/serials")

    expected_owners = {
        "H1": "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB",
        "H2": "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB",
        "H3": "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT",
        "H4": "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT",
        "H5": "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB",
    }
    owner_ok = all(
        row["whole_plant_owner"] == expected_owners[row["record_unit_id"]]
        and row["whole_plant_owner"] == selected_owners[row["field_id"]]["selected_visible_owner"]
        and row["owner_status"] == "PAGE_OWNER_ONLY"
        for row in events
    )
    check("whole_plant_owner_exact_and_never_part_owner", owner_ok, expected_owners)

    literal_ok = True
    for row in events:
        required_fragments = [
            f"E{row['event_serial']}:[TUPLE:{row['joint_tuple_id']}",
            f"SURFACE_DISPLAY_ONLY:{row['surface_display_only']}",
            f"FORMULA:{row['formal_formula_opaque']}",
            f"CARD:{row['selected_exact_mnemonic']}",
            f"PROMPT:{row['strict_formal_prompt']}",
            f"TEMPLATE:{row['event_template']}",
            "FROZEN_V72_SEGMENT:",
            f"TERMINAL:{row['terminal_status']}",
        ]
        literal_ok &= all(fragment in row["literal_exact_card_formal_exemplar_layer"] for fragment in required_fragments)
    check("every_event_has_complete_literal_exact_card_formal_exemplar_layer", literal_ok, "8 required literal fragments")

    parse_counts = Counter(row["parse_status"] for row in events)
    exemplar_count = parse_counts["UNPARSED_EXEMPLAR"]
    recognized_count = len(events) - exemplar_count
    check("frozen_71_exemplar_29_recognized_split", exemplar_count == 71 and recognized_count == 29, {"exemplar": exemplar_count, "recognized": recognized_count})
    layer_ok = all(
        row["default_layer"] == (
            "CREATIVE_OCCURRENCE_EXEMPLAR_FILL"
            if row["parse_status"] == "UNPARSED_EXEMPLAR"
            else "FROZEN_CONTROL_CLASS_PLUS_CREATIVE_SOURCE_ARGUMENT"
        )
        for row in events
    )
    check("creative_fill_layer_explicit", layer_ok, Counter(row["default_layer"] for row in events))

    confidence_ok = all(0.0 < float(row["technical_default_confidence"]) < 0.50 for row in events)
    check("all_concrete_defaults_low_confidence", confidence_ok, sorted({row["technical_default_confidence"] for row in events}))
    check("every_event_has_medical_rival", all(row["strongest_medical_rival"].startswith("MEDICAL_RIVAL:") for row in events), "100 prefixed rivals")
    check("every_event_has_contradiction", all(len(row["contradiction"]) >= 80 for row in events), min(len(row["contradiction"]) for row in events))
    check("every_event_has_concrete_nonempty_instruction", all(row["concrete_technical_default"].endswith(".") and len(row["concrete_technical_default"]) >= 20 for row in events), min(len(row["concrete_technical_default"]) for row in events))

    terminal_rows = [row for row in events if row["terminal_status"] == "TERMINAL"]
    check("five_frozen_terminal_events", len(terminal_rows) == 5, [row["event_serial"] for row in terminal_rows])
    check("terminal_only_closes_local_field", all("CLOSE_LOCAL_FIELD_ONLY" in row["register_effect_in_creative_template"] for row in terminal_rows), [row["event_serial"] for row in terminal_rows])
    check("previous_is_record_local", all("WITHIN_CURRENT_RECORD" in row["register_effect_in_creative_template"] for row in events if row["event_template"] == "SELECT_PREVIOUS"), [row["event_serial"] for row in events if row["event_template"] == "SELECT_PREVIOUS"])

    events_per_record = Counter(row["record_unit_id"] for row in events)
    expected_record_counts = {"H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27}
    check("record_event_counts_exact", dict(events_per_record) == expected_record_counts, dict(events_per_record))
    article_counts_ok = all(int(row["event_count"]) == expected_record_counts[row["record_unit_id"]] for row in articles)
    check("article_event_counts_exact", article_counts_ok, {row["record_unit_id"]: row["event_count"] for row in articles})

    events_by_field: dict[str, list[int]] = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(int(row["event_serial"]))
    field_sequence_ok = all(
        "|".join(str(value) for value in events_by_field[row["field_id"]]) == row["event_serials"]
        and len(events_by_field[row["field_id"]]) == int(row["event_count"])
        for row in fields
    )
    check("field_event_sequences_roundtrip", field_sequence_ok, "20/20")

    statement_event_total = sum(int(row["event_count"]) for row in statements)
    check("statement_event_total_100", statement_event_total == 100, statement_event_total)
    h5_span = next(row for row in statements if row["statement_id"] == "H5-S001")
    check("H5_S001_cross_field_continuation_retained", h5_span["constituent_fields"] == "F014|F015" and int(h5_span["event_count"]) == 9, h5_span["constituent_fields"])

    joined_defaults = " ".join(row["concrete_technical_default"].lower() for row in events)
    process_coverage = {
        "sampling": any(term in joined_defaults for term in ["probe", "los"]),
        "preparation": any(term in joined_defaults for term in ["schneide", "zerkleinere", "zerdrück"]),
        "extraction": any(term in joined_defaults for term in ["auszug", "presse", "gefilterte"]),
        "storage": any(term in joined_defaults for term in ["lager", "bewahre", "trocknen"]),
        "comparison": any(term in joined_defaults for term in ["vergleich", "daneben", "beiden"]),
        "wet_process": "wasser" in joined_defaults,
    }
    check("required_plant_material_process_families_present", all(process_coverage.values()), process_coverage)

    species_terms = [
        "veilchen", "allium", "wegerich", "sonnentau", "teufelsabbiss", "skabiose",
        "plantago", "drosera", "mandragora", "alraune",
    ]
    all_text = "\n".join(path.read_text(encoding="utf-8").lower() for path in [event_path, field_path, statement_path, article_path, report_path])
    found_species = [term for term in species_terms if term in all_text]
    check("no_species_identification", not found_species, found_species)
    check("semantic_ceiling_on_every_row", all("NOT_TRANSLATION" in row["semantic_ceiling"] for row in events), "100/100")

    report = report_path.read_text(encoding="utf-8")
    required_report_phrases = [
        "100 Herbal-Ereignisse", "20 Felder", "19 Aussagen", "5 Records",
        "71 Ereignisse", "29", "Ausführbare Quellenregel", "Die fünf vollständigen Artikel",
        "nicht abgebildet", "keine Entzifferung oder Übersetzung", "f84 und f84r",
    ]
    check("report_contains_required_scope_and_ceiling", all(phrase in report for phrase in required_report_phrases), required_report_phrases)

    build = json.loads(build_path.read_text(encoding="utf-8"))
    check("build_summary_counts_exact", build["counts"] == {
        "events": 100,
        "fields": 20,
        "statements": 19,
        "records": 5,
        "recognized_events": 29,
        "exemplar_only_events": 71,
    }, build["counts"])
    check("f84_and_f84r_declared_sealed", build["sealed"] == ["f84", "f84r"], build["sealed"])

    failed = [item for item in checks if not item["pass"]]
    result = {
        "experiment": "V73_R3_NONMEDICAL_HERBAL_THIRD_EDITION",
        "status": "PASS" if not failed else "FAIL",
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": [item["name"] for item in failed],
        "dimensions": {
            "events": len(events),
            "fields": len(fields),
            "statements": len(statements),
            "records": len(articles),
        },
        "checks": checks,
        "sealed": ["f84", "f84r"],
    }
    (OUT / "V73_R3_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if failed:
        for item in failed:
            print(f"FAIL {item['name']}: {item['detail']}")
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
