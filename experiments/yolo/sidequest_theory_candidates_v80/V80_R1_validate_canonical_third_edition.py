#!/usr/bin/env python3
"""Validate the complete independent R1 V80 canonical third edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}
DCDA = "dcda95c81a5460feb191"
B5FCEA = "b5fcea1eaed06b2f2291"
FORMAL_PARAMETER = "2f1c5e56e8f0ff459065"
FORMAL_RELATION_SLOT = "308e8ea2d5d190c498e8"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def source_tsv(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_ids(value: str) -> list[str]:
    return [x for x in value.split("|") if x and x != "NONE"]


def main() -> None:
    checks: dict[str, object] = {}
    failures: list[str] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks[name] = {"pass": bool(condition), "detail": detail}
        if not condition:
            failures.append(name)

    dictionary = read_tsv("V80_R1_173_CARD_DICTIONARY.tsv")
    events = read_tsv("V80_R1_381_PROSE_EVENT_INTERLINEAR.tsv")
    fields = read_tsv("V80_R1_135_FIELD_EDITION.tsv")
    statements = read_tsv("V80_R1_116_STATEMENT_EDITION.tsv")
    astro = read_tsv("V80_R1_395_ASTRO_GROUP_EDITION.tsv")
    unified = read_tsv("V80_R1_776_UNIFIED_LEDGER.tsv")
    manual = read_tsv("V80_R1_COMPACT_WORKSHOP_MANUAL.tsv")
    contradictions = read_tsv("V80_R1_CONTRADICTION_LEDGER.tsv")
    summary = json.loads((OUT / "V80_R1_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    check("required_counts", [len(dictionary), len(events), len(fields), len(statements), len(astro), len(unified)] == [173, 381, 135, 116, 395, 776], {
        "dictionary": len(dictionary), "events": len(events), "fields": len(fields),
        "statements": len(statements), "astro": len(astro), "unified": len(unified),
    })
    check("serials_complete", [int(x["event_serial"]) for x in events] == list(range(1, 382)) and [int(x["group_serial"]) for x in astro] == list(range(1, 396)) and [int(x["unified_serial"]) for x in unified] == list(range(1, 777)), "1..381; 1..395; 1..776")
    check("fixed_page_scope", {x["page"] for x in events} == PROSE_PAGES and {x["page"] for x in astro} == ASTRO_PAGES and {x["page"] for x in unified} == PAGES, sorted({x["page"] for x in unified}))
    check("sealed_pages_absent_from_selectors", not any(x["page"].startswith("f84") for x in events + astro + unified), "no f84/f84r row")

    dict_ids = {x["joint_tuple_id"] for x in dictionary}
    event_ids = {x["joint_tuple_id"] for x in events}
    check("dictionary_exact_event_inventory", dict_ids == event_ids and len(dict_ids) == 173, {"dictionary": len(dict_ids), "events": len(event_ids)})
    classes = Counter(x["dictionary_class"] for x in dictionary)
    check("dictionary_class_counts", classes == Counter({"CONTENT_CARD_UNKNOWN": 169, "FORMAL_LABEL_NOT_WORD": 2, "AUTONOMOUS_FORMAL_ROLE": 2}), dict(classes))
    by_card = {x["joint_tuple_id"]: x for x in dictionary}
    check("dcda_primary_formal", by_card[DCDA]["autonomous_operational_value"] == "FORMAL_LINK_OR_SLOT" and by_card[DCDA]["optional_questioned_master_gloss"] == "ET?=UND/AUCH?__OPTIONAL_QUESTIONED_MASTER_GLOSS_ONLY" and "1414" in by_card[DCDA]["historical_category_attestation"], by_card[DCDA])
    check("b5fcea_primary_formal", by_card[B5FCEA]["autonomous_operational_value"] == "FORMAL_RELATION_OR_ENTRY" and by_card[B5FCEA]["optional_questioned_master_gloss"] == "PER?=DURCH/GEMÄSS?__OPTIONAL_QUESTIONED_MASTER_GLOSS_ONLY" and "1414" in by_card[B5FCEA]["historical_category_attestation"], by_card[B5FCEA])
    check("two_formal_nonwords", {x["joint_tuple_id"] for x in dictionary if x["dictionary_class"] == "FORMAL_LABEL_NOT_WORD"} == {FORMAL_PARAMETER, FORMAL_RELATION_SLOT}, [x["joint_tuple_id"] for x in dictionary if x["dictionary_class"] == "FORMAL_LABEL_NOT_WORD"])
    unknown = [x for x in dictionary if x["dictionary_class"] == "CONTENT_CARD_UNKNOWN"]
    check("all_other_cards_unknown", len(unknown) == 169 and all(x["autonomous_operational_value"] == "EXEMPLAR_VALUE_UNKNOWN" and x["portable_content_value"] == "NONE" and x["memorized_guess_exact"] == "NONE" for x in unknown), len(unknown))

    event_counts = Counter(x["joint_tuple_id"] for x in events)
    check("formal_occurrence_counts", (event_counts[DCDA], event_counts[B5FCEA], event_counts[FORMAL_PARAMETER], event_counts[FORMAL_RELATION_SLOT]) == (19, 9, 20, 6), {k: event_counts[k] for k in (DCDA, B5FCEA, FORMAL_PARAMETER, FORMAL_RELATION_SLOT)})
    check("all_event_exemplars_bracketed", all(x["occurrence_bound_exemplar"].startswith("[EXEMPLAR:") and x["occurrence_bound_exemplar"].endswith("]") for x in events), sum(x["occurrence_bound_exemplar"].startswith("[EXEMPLAR:") for x in events))
    check("no_portable_word_in_primary_tokens", all("ET?" not in x["autonomous_primary_token"] and "PER?" not in x["autonomous_primary_token"] for x in events), "primary tokens are formal/unknown only")
    check("optional_gloss_only_on_two_cards", all((x["optional_questioned_master_gloss"] != "NONE") == (x["joint_tuple_id"] in {DCDA, B5FCEA}) for x in events), "28 questioned-gloss occurrences")

    event_by_id = {x["event_id"]: x for x in events}
    e180, e181 = event_by_id["E180"], event_by_id["E181"]
    check("e180_e181_same_visible_context", e180["joint_tuple_id"] == e181["joint_tuple_id"] == B5FCEA and e180["statement_id"] == e181["statement_id"] == "B2-S005" and e180["image_owner_id"] == e181["image_owner_id"] and e180["locus"] == "f82r.3" and e181["locus"] == "f82r.4", {"E180": e180["locus"], "E181": e181["locus"]})
    check("e180_e181_two_visible_one_source", e180["source_token_count"] == "0" and e181["source_token_count"] == "1" and sum(int(x["source_token_count"]) for x in events if x["joint_tuple_id"] == B5FCEA) == 8, "9 visible b5fcea; 8 source tokens")

    transitions = source_tsv("experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv")
    check("generic_read_once_one_positive", len(transitions) == 19 and Counter(x["classification"] for x in transitions) == Counter({"TN": 18, "TP": 1}) and [x for x in transitions if x["classification"] == "TP"][0]["line_final_event"] == "E180", dict(Counter(x["classification"] for x in transitions)))
    b2_resets = [x["event_id"] for x in events if x["record_unit_id"] == "B2" and x["owner_reset"] != "NO"]
    check("four_b2_owner_resets", b2_resets == ["E189", "E198", "E203", "E212"], b2_resets)

    field_cover = [s for f in fields for s in split_ids(f["event_serials"])]
    statement_cover = [s for st in statements for s in split_ids(st["event_serials"])]
    check("fields_partition_381_events", Counter(field_cover) == Counter(str(i) for i in range(1, 382)), {"references": len(field_cover), "unique": len(set(field_cover))})
    check("statements_partition_381_events", Counter(statement_cover) == Counter(str(i) for i in range(1, 382)), {"references": len(statement_cover), "unique": len(set(statement_cover))})
    check("field_source_expansions_bracketed", all(x["selected_source_field_expansion"].startswith("[EXEMPLAR:") for x in fields), len(fields))
    check("statement_source_expansions_bracketed", all(x["selected_source_sentence"].startswith("[EXEMPLAR:") for x in statements), len(statements))

    source_prose = source_tsv("experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv")
    source_astro = source_tsv("experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv")
    check("prose_forms_unchanged", [(x["event_serial"], x["joint_tuple_id"], x["surface_display_only"]) for x in events] == [(x["event_serial"], x["joint_tuple_id"], x["surface_display_only"]) for x in source_prose], "381 exact identity/surface rows")
    check("astro_forms_unchanged", [(x["group_serial"], x["opaque_local_id"], x["surface_display_only"]) for x in astro] == [(x["group_serial"], x["opaque_local_id"], x["surface_display_only"]) for x in source_astro], "395 exact identity/surface rows")
    check("astro_local_namespaces", all(x["local_namespace"] and x["local_namespace"] != "NONE" for x in astro), dict(Counter(x["local_namespace"] for x in astro)))
    check("astro_no_orientation", all(x["orientation_status"] == "LOCAL_EDITORIAL_ADDRESS_ONLY__NO_AUTHORIAL_START_ROTATION_OR_DIRECTION" for x in astro), "395/395")
    check("astro_no_f68_f69_key", all(x["f68_f69_mapping"] == "NONE__NO_VISIBLE_KEY" for x in astro), "395/395")
    check("astro_no_prose_import", all(x["prose_card_import"] == "NONE" for x in astro), "395/395")
    check("astro_exemplars_bracketed", all(x["occurrence_bound_exemplar"].startswith("[EXEMPLAR:") for x in astro), "395/395")
    page_group_counts = Counter(x["page"] for x in astro)
    check("astro_page_counts", page_group_counts == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}), dict(page_group_counts))

    loci = source_tsv("experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv")
    f69_left_slots = [x for x in loci if x["page"] == "f69v" and 4 <= int(x["locus"].split(".")[1]) <= 31]
    check("f69_left_28_unordered_slots", len(f69_left_slots) == 28 and sum(int(x["group_count"]) for x in f69_left_slots) == 33 and all(x["local_namespace"] == "A3_LEFT_WHEEL_ONLY" and "NO_AUTHORIAL" in x["orientation_status"] for x in f69_left_slots), {"slots": len(f69_left_slots), "groups": sum(int(x["group_count"]) for x in f69_left_slots)})

    check("unified_partition", Counter(x["item_kind"] for x in unified) == Counter({"PROSE_EVENT": 381, "ASTRO_GROUP": 395}), dict(Counter(x["item_kind"] for x in unified)))
    check("unified_source_token_accounting", sum(int(x["source_token_count"]) for x in unified) == 775 and sum(int(x["visible_count"]) for x in unified) == 776, {"visible": 776, "source": 775})
    check("manual_complete", len(manual) == 21 and {x["rule_order"] for x in manual} == {f"{i:02d}" for i in range(1, 17)} | {str(i) for i in range(17, 22)}, len(manual))
    check("contradiction_ledger_complete_layers", len(contradictions) >= 23 and {"BOOK_PURPOSE", "FORMAL_READBACK", "PROSE_OCCURRENCE", "ASTRO_OCCURRENCE"} <= {x["level"] for x in contradictions}, {"rows": len(contradictions), "levels": sorted({x["level"] for x in contradictions})})

    readable = (OUT / "V80_R1_TEN_PAGE_READABLE_EDITION.md").read_text(encoding="utf-8")
    report = (OUT / "V80_R1_REPORT.md").read_text(encoding="utf-8")
    check("readable_has_exact_ten_page_heads", sum(readable.count(f"## {p}\n") for p in PAGES) == 10 and not any(f"## f84{x}" in readable for x in ("", "r")), [p for p in PAGES if f"## {p}\n" in readable])
    check("exactly_one_lead_and_rival_ids", summary["lead_model"] == "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM" and summary["rival_model"] == "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK", {"lead": summary["lead_model"], "rival": summary["rival_model"]})
    check("report_states_memorized_guesses", "## Exakt memorierte Vermutungen" in report and "Alle übrigen 169 Karten" in report and "[EXEMPLAR:…]" in report, "present")
    check("builder_summary_counts", summary["counts"]["dictionary_cards"] == 173 and summary["counts"]["unified_groups"] == 776 and summary["counts"]["pages"] == 10, summary["counts"])

    generated = summary["generated_hashes"]
    check("generated_hashes_current", all((OUT / name).exists() and sha(OUT / name) == digest for name, digest in generated.items()), len(generated))

    result = {
        "status": "PASS" if not failures else "FAIL",
        "candidate": "V80_R1_CANONICAL_THIRD_EDITION",
        "scope": sorted(PAGES),
        "sealed": ["f84", "f84r"],
        "counts": {
            "dictionary": len(dictionary), "prose_events": len(events), "fields": len(fields),
            "statements": len(statements), "astro_groups": len(astro), "unified": len(unified),
            "manual_rules": len(manual), "contradictions": len(contradictions),
        },
        "formal_specials": {
            "dcda_primary": "FORMAL_LINK_OR_SLOT",
            "b5fcea_primary": "FORMAL_RELATION_OR_ENTRY",
            "optional_master_glosses": ["ET?=UND/AUCH?", "PER?=DURCH/GEMÄSS?"],
            "formal_nonword_channels": [FORMAL_PARAMETER, FORMAL_RELATION_SLOT],
            "content_cards_unknown": 169,
        },
        "read_once": {"opportunities": 19, "positive": 1, "visible_events": ["E180", "E181"], "visible_count": 2, "source_count": 1},
        "b2_owner_resets": b2_resets,
        "lead_model": summary["lead_model"],
        "strongest_rival": summary["rival_model"],
        "checks": checks,
        "failures": failures,
    }
    (OUT / "V80_R1_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("FAIL: " + ", ".join(failures))
    print(json.dumps({"status": "PASS", "checks": len(checks), "counts": result["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
