#!/usr/bin/env python3
"""Apply two independently supported cardless complete wholes after ``ol``.

The row selector is deliberately pure: the parent row must still be a generic
GDT779 fallback, the complete right token must be reader-exact, and its whole
surface must be one of the two frozen cards. Occurrence identifiers, pages,
loci, neighbours, frequency, edit distance and semantic values never select a
row.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
SPECS_PATH = SRC / "TWO_WHOLE_SPECS.tsv"
PARENT = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts"
PARENT_RENDERER = PARENT / "GDT779_376_RENDERER.tsv"
PARENT_RESULT = PARENT / "RESULT.json"
PARENT_RESIDUAL = PARENT / "GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv"
G758_PATH = ROOT / "experiments/yolo/gdt758_ychor_follower_global_content_census/artifacts/ORDERED_VALUE_FOLLOWER_COMPARATOR.tsv"
G745_PATH = ROOT / "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/CROSS_PAGE_ROLE_CARDS.tsv"
G746_PATH = ROOT / "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/CANDIDATE_17_DISTRIBUTION_CENSUS.tsv"
G747_PATH = ROOT / "experiments/yolo/gdt747_supported_whole_passage_application/artifacts/CANDIDATE_12_PASSAGE_CENSUS.tsv"
G747_OCC_PATH = ROOT / "experiments/yolo/gdt747_supported_whole_passage_application/artifacts/OCCURRENCE_64_LOCAL_SUPPORT.tsv"
G748_PATH = ROOT / "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/COLLAPSED_POSITION_EVIDENCE.tsv"
G769_CONTEXT_PATH = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/TARGET_526_EXACT_CONTEXT_ATLAS.tsv"

FROZEN_SURFACES = frozenset({"eees", "sheeol"})
SELECTION_RULE = "GDT779_RENDERER_CONTEXTUAL_0_AND_RIGHT_READER_EXACT_1_AND_COMPLETE_RIGHT_SURFACE_IN_EEES_SHEEOL"
STATUS = "PASS__2_EXACT_CARDLESS_WHOLES__2_FORMS__2_LOCI__247_CONTEXTUAL__129_FALLBACKS__207_CONSUMED__NO_COMPONENT_EXPORT"
VERIFIED_POSITIVE = {
    "eees": "GDT758 gelockt:7 reader-exakte Vorkommen;4 exakte Rechtskontexte;3mal aiin;Rate .75;Baseline .021613;Lift 34.702083;GDT769-Zielzeile entfernt:2 aiin in 3 Kontexten",
    "sheeol": "GDT745 gelockt:10 Cache/9 exakte Vorkommen;GDT746 gelockt:END_STAGE Form-Verteilungskern;GDT747 gelockt:4 lokale END-Kontakte auf 3 Seiten;Ziel G747-O060 ist exact L0 mit 0 Supports",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def serialise(value: object) -> object:
    return int(value) if isinstance(value, bool) else value


def write_tsv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    material = list(rows)
    assert material, path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in material:
            writer.writerow({field: serialise(row.get(field, "")) for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_locks() -> int:
    rows = read_tsv(SRC / "SOURCE_LOCK.tsv")
    assert len(rows) == 11
    seen: set[str] = set()
    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert str(relative) not in seen, relative
        seen.add(str(relative))
        source = ROOT / relative
        assert source.is_file(), source
        assert sha256(source) == row["expected_sha256"], f"source changed: {relative}"
    assert str(PARENT_RENDERER.relative_to(ROOT)) in seen
    assert str(PARENT_RESULT.relative_to(ROOT)) in seen
    assert str(PARENT_RESIDUAL.relative_to(ROOT)) in seen
    assert str(G747_OCC_PATH.relative_to(ROOT)) in seen
    assert str(G769_CONTEXT_PATH.relative_to(ROOT)) in seen
    return len(rows)


def one_by(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for source in rows:
        value = source[key]
        assert value not in output, (key, value)
        output[value] = dict(source)
    return output


def validate_specs(rows: Sequence[Mapping[str, str]]) -> dict[str, dict[str, str]]:
    required = {
        "surface", "default_de", "alternate_1_de", "alternate_2_de", "confidence",
        "functional_axis", "positive_evidence", "counterevidence", "source_evidence",
        "card_class", "renderer_scope", "literal_identity", "confirmed_lexeme",
        "component_export_credit", "numeric_identity_confirmed", "specific_substance_confirmed",
    }
    assert len(rows) == 2 and required <= set(rows[0])
    specs = one_by(rows, "surface")
    assert set(specs) == FROZEN_SURFACES
    assert specs["eees"]["default_de"] == "Mengenfeld"
    assert specs["eees"]["functional_axis"] == "AMOUNT_OR_VALUE_FIELD"
    assert specs["sheeol"]["default_de"] == "Endzustand"
    assert specs["sheeol"]["functional_axis"] == "END_STAGE"
    for surface, row in specs.items():
        assert surface and " " not in surface
        assert row["confidence"] == "C1_ROLE_C0_IDENTITY"
        assert row["card_class"] == "INDEPENDENT_COMPLETE_WHOLE_ROLE_BRIDGE"
        assert row["renderer_scope"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY"
        assert row["literal_identity"] == "OPEN"
        assert all(row[key] == "0" for key in (
            "confirmed_lexeme", "component_export_credit", "numeric_identity_confirmed",
            "specific_substance_confirmed",
        ))
        values = (row["default_de"], row["alternate_1_de"], row["alternate_2_de"])
        assert all(values) and len(set(values)) == 3
    return specs


def select_gdt780_row(gdt779_renderer_contextual: str, right_surface: str,
                      right_reader_exact: str, fixed_complete_surfaces: frozenset[str]) -> bool:
    """Occurrence-free selector over exactly three declared row properties."""
    return (
        gdt779_renderer_contextual == "0"
        and right_reader_exact == "1"
        and right_surface in fixed_complete_surfaces
    )


def inherited_owner_map(base: Sequence[Mapping[str, str]]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for row in base:
        value = row["gdt779_consumed_token_ids"]
        count = int(row["gdt779_consumed_token_count"])
        token_ids = [] if value == "NONE" else value.split("|")
        assert len(token_ids) == count
        for token_id in token_ids:
            assert token_id not in owners, token_id
            owners[token_id] = row["target_occurrence_id"]
    assert len(owners) == 205
    return owners


def build_intake(base: Sequence[Mapping[str, str]], parent_residual: Sequence[Mapping[str, str]],
                 specs: Mapping[str, Mapping[str, str]]) -> list[dict[str, object]]:
    fallback_ids = {row["target_occurrence_id"] for row in base if row["gdt779_renderer_contextual"] == "0"}
    assert len(fallback_ids) == 131 and len(parent_residual) == 131
    assert {row["target_occurrence_id"] for row in parent_residual} == fallback_ids
    residual_by_target = one_by(parent_residual, "target_occurrence_id")

    # GDT779 already consumed every reader-exact right token that had a V99R7
    # card. Its remaining exact, non-final right rows therefore reconstruct the
    # complete cardless intake directly from the parent renderer.
    exact_cardless = [
        row for row in base
        if row["gdt779_renderer_contextual"] == "0"
        and row["right_reader_exact"] == "1"
        and row["right_surface"] != "NONE"
        and int(row["right_ordinal"]) > 0
    ]
    expected_ids = {
        row["target_occurrence_id"] for row in parent_residual
        if row["residual_reason"] == "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT"
    }
    assert len(exact_cardless) == 25
    assert {row["target_occurrence_id"] for row in exact_cardless} == expected_ids

    output: list[dict[str, object]] = []
    for number, row in enumerate(exact_cardless, 1):
        residual = residual_by_target[row["target_occurrence_id"]]
        selected = select_gdt780_row(
            row["gdt779_renderer_contextual"], row["right_surface"],
            row["right_reader_exact"], FROZEN_SURFACES,
        )
        output.append({
            "intake_id": f"G780-I{number:03d}", "parent_residual_id": residual["residual_id"],
            "target_occurrence_id": row["target_occurrence_id"],
            "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
            "section": row["section"], "language": row["language"], "hand": row["hand"],
            "ol_ordinal": int(row["ordinal"]), "right_ordinal": int(row["right_ordinal"]),
            "right_surface": row["right_surface"], "right_reader_exact": int(row["right_reader_exact"]),
            "parent_residual_reason": residual["residual_reason"],
            "parent_gdt779_default_de": row["gdt779_default_de"],
            "frozen_two_whole_deck_member": int(row["right_surface"] in specs),
            "selected_by_pure_rule": int(selected), "selection_rule": SELECTION_RULE,
            "selection_uses_occurrence_id": 0, "selection_uses_page_or_locus": 0,
            "selection_uses_neighbor_or_frequency": 0, "selection_uses_substring": 0,
            "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    assert sum(int(row["selected_by_pure_rule"]) for row in output) == 2
    assert {row["right_surface"] for row in output if int(row["selected_by_pure_rule"])} == FROZEN_SURFACES
    assert len({row["right_surface"] for row in output}) == 25
    return output


def build_target_independence(base: Sequence[Mapping[str, str]]) -> list[dict[str, object]]:
    """Reconstruct both target-removal controls from locked rowwise sources."""
    g758 = one_by(read_tsv(G758_PATH), "surface")["eees"]
    g747_summary = one_by(read_tsv(G747_PATH), "candidate_surface")["sheeol"]
    g747_occurrences = read_tsv(G747_OCC_PATH)
    g769_context = one_by(read_tsv(G769_CONTEXT_PATH), "target_occurrence_id")

    eees_parent_rows = [row for row in base if row["right_surface"] == "eees"]
    assert len(eees_parent_rows) == 1
    eees_parent = eees_parent_rows[0]
    eees_target = g769_context[eees_parent["target_occurrence_id"]]
    assert eees_target["surface"] == "ol"
    assert eees_target["page"] == eees_parent["page"] == "f43v"
    assert eees_target["physical_folio"] == eees_parent["physical_folio"] == "f43"
    assert eees_target["locus"] == eees_parent["locus"] == "f43v.16"
    assert eees_target["ordinal"] == eees_parent["ordinal"] == "1"
    assert eees_target["reader_exact"] == "1" and eees_parent["right_reader_exact"] == "1"
    assert eees_target["written_line_eva"] == eees_parent["written_line_eva"]
    assert eees_target["written_line_eva"] == "ol eees aiin oloaiin oteos qoky chey"
    views = json.loads(eees_target["context_views"])
    r2_donors = {int(row["ordinal"]): row for row in views["R2"]["eligible_donors"]}
    assert set(r2_donors) == {2, 3}
    right, follower = r2_donors[2], r2_donors[3]
    assert right["surface"] == "eees" and follower["surface"] == "aiin"
    for donor in (right, follower):
        assert donor["current_clean"] == 1
        assert donor["gate_status"] == "ELIGIBLE"
        assert donor["per_current_target_gate_status"] == "ELIGIBLE"
    before_contexts = int(g758["exact_right_contexts"])
    before_hits = int(g758["ordered_value_follower_hits"])
    after_contexts, after_hits = before_contexts - 1, before_hits - 1
    assert (before_contexts, before_hits, after_contexts, after_hits) == (4, 3, 3, 2)

    sheeol_parent_rows = [row for row in base if row["right_surface"] == "sheeol"]
    assert len(sheeol_parent_rows) == 1
    sheeol_parent = sheeol_parent_rows[0]
    sheeol_details = [
        row for row in g747_occurrences
        if row["candidate_surface"] == "sheeol"
        and row["locus"] == sheeol_parent["locus"]
        and row["token_ordinal"] == sheeol_parent["right_ordinal"]
    ]
    assert len(sheeol_details) == 1
    sheeol_target = sheeol_details[0]
    assert sheeol_target["gdt747_occurrence_id"] == "G747-O060"
    assert sheeol_target["page"] == sheeol_parent["page"] == "f88r"
    assert sheeol_target["physical_folio"] == sheeol_parent["physical_folio"] == "f88"
    assert sheeol_target["locus"] == sheeol_parent["locus"] == "f88r.21"
    assert sheeol_target["token_ordinal"] == sheeol_parent["right_ordinal"] == "7"
    assert sheeol_target["reader_exact"] == sheeol_parent["right_reader_exact"] == "1"
    assert sheeol_target["passage_core_axes"] == "END_STAGE"
    assert sheeol_target["local_support_tier"] == "L0_NO_LOCAL_W23_SUPPORT"
    assert sheeol_target["supporting_whole_count"] == "0"
    assert sheeol_target["supporting_whole_surfaces"] == "NONE"
    assert sheeol_target["locally_supported_core_axes"] == "NONE"
    assert sheeol_target["locally_supported_core_fraction"] == "0.000"
    global_supports = int(g747_summary["locally_supported_occurrences"])
    global_support_pages = int(g747_summary["local_support_pages"])
    assert (global_supports, global_support_pages) == (4, 3)

    rows: list[dict[str, object]] = [
        {
            "audit_id": "G780-A001", "surface": "eees",
            "target_occurrence_id": eees_parent["target_occurrence_id"],
            "detail_source_record_id": eees_target["raw_occurrence_id"],
            "detail_source": str(G769_CONTEXT_PATH.relative_to(ROOT)),
            "page": eees_parent["page"], "physical_folio": eees_parent["physical_folio"],
            "locus": eees_parent["locus"], "target_ordinal": int(eees_parent["right_ordinal"]),
            "target_reader_exact": int(eees_parent["right_reader_exact"]),
            "target_written_line_eva": eees_parent["written_line_eva"],
            "detail_source_target_surface": eees_target["surface"],
            "detail_source_target_ordinal": int(eees_target["ordinal"]),
            "detail_source_target_reader_exact": int(eees_target["reader_exact"]),
            "parent_right_reader_exact": int(eees_parent["right_reader_exact"]),
            "target_current_clean": int(right["current_clean"]),
            "target_gate_status": right["gate_status"],
            "target_following_surface": follower["surface"],
            "target_following_ordinal": int(follower["ordinal"]),
            "target_following_current_clean": int(follower["current_clean"]),
            "target_following_gate_status": follower["gate_status"],
            "aggregate_evidence_before_target_removal": "3_aiin_hits_in_4_exact_right_contexts",
            "target_evidence_contribution": "1_aiin_hit_in_1_exact_right_context",
            "evidence_after_target_removal": "2_aiin_hits_in_3_exact_right_contexts",
            "target_independence_calculation": "4-1=3_contexts;3-1=2_aiin_hits",
            "target_local_support_tier": "NA", "target_local_support_count": "NA",
            "global_local_support_count": "NA", "global_local_support_pages": "NA",
            "target_removed_local_support_count": "NA",
            "independence_status": "PASS__TARGET_REMOVAL_RETAINS_2_OF_3_AIIN_FOLLOWERS",
            "selection_uses_target_evidence": 0, "default_is_translation": 0,
            "confirmed_lexeme": 0, "component_export_credit": 0,
        },
        {
            "audit_id": "G780-A002", "surface": "sheeol",
            "target_occurrence_id": sheeol_parent["target_occurrence_id"],
            "detail_source_record_id": sheeol_target["gdt747_occurrence_id"],
            "detail_source": str(G747_OCC_PATH.relative_to(ROOT)),
            "page": sheeol_parent["page"], "physical_folio": sheeol_parent["physical_folio"],
            "locus": sheeol_parent["locus"], "target_ordinal": int(sheeol_parent["right_ordinal"]),
            "target_reader_exact": int(sheeol_target["reader_exact"]),
            "target_written_line_eva": sheeol_parent["written_line_eva"],
            "detail_source_target_surface": sheeol_target["candidate_surface"],
            "detail_source_target_ordinal": int(sheeol_target["token_ordinal"]),
            "detail_source_target_reader_exact": int(sheeol_target["reader_exact"]),
            "parent_right_reader_exact": int(sheeol_parent["right_reader_exact"]),
            "target_current_clean": "NA", "target_gate_status": "NA",
            "target_following_surface": "NA", "target_following_ordinal": "NA",
            "target_following_current_clean": "NA", "target_following_gate_status": "NA",
            "aggregate_evidence_before_target_removal": "4_local_END_supports_on_3_pages",
            "target_evidence_contribution": "0_local_END_supports",
            "evidence_after_target_removal": "4_local_END_supports_on_3_pages",
            "target_independence_calculation": "4-0=4_local_END_supports",
            "target_local_support_tier": sheeol_target["local_support_tier"],
            "target_local_support_count": int(sheeol_target["supporting_whole_count"]),
            "global_local_support_count": global_supports,
            "global_local_support_pages": global_support_pages,
            "target_removed_local_support_count": global_supports,
            "independence_status": "PASS__TARGET_IS_EXACT_L0_AND_CONTRIBUTES_ZERO_END_SUPPORTS",
            "selection_uses_target_evidence": 0, "default_is_translation": 0,
            "confirmed_lexeme": 0, "component_export_credit": 0,
        },
    ]
    assert {row["surface"] for row in rows} == FROZEN_SURFACES
    return rows


def build_evidence(specs: Mapping[str, Mapping[str, str]], base: Sequence[Mapping[str, str]],
                   independence: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    independence_by_surface = {str(row["surface"]): row for row in independence}
    assert set(independence_by_surface) == FROZEN_SURFACES
    g758 = one_by(read_tsv(G758_PATH), "surface")
    g745 = one_by(read_tsv(G745_PATH), "candidate_surface")
    g746 = one_by(read_tsv(G746_PATH), "candidate_surface")
    g747 = one_by(read_tsv(G747_PATH), "candidate_surface")
    g748_sheeol = [row for row in read_tsv(G748_PATH) if row["target_surface"] == "sheeol"]

    eees = g758["eees"]
    assert eees["reader_exact_occurrences"] == "7"
    assert eees["exact_right_contexts"] == "4"
    assert eees["ordered_value_follower_hits"] == "3"
    assert eees["ordered_value_follower_counts"] == "aiin:3"
    assert eees["ordered_value_conditional_rate"] == "0.750000"
    assert eees["ordered_value_baseline_rate"] == "0.021613"
    assert eees["ordered_value_descriptive_lift"] == "34.702083"
    assert eees["aiin_follower_hits"] == "3"

    s745, s746, s747 = g745["sheeol"], g746["sheeol"], g747["sheeol"]
    assert (s745["cache_occurrences"], s745["cache_pages"]) == ("10", "8")
    assert (s745["reader_exact_occurrences"], s745["reader_exact_pages"]) == ("9", "7")
    assert s745["analogy_consensus_axes"] == "MATERIAL|END_STAGE"
    assert s745["analogy_rival_axes"] == "DRY|MOIST|PREPARATION"
    assert s746["reader_exact_occurrences"] == "9"
    assert s746["distribution_status"] == "S2_DISTRIBUTION_SUPPORTED"
    assert s746["form_and_top5_axis_agreement"] == "END_STAGE"
    assert s746["top5_distribution_consensus_axes"] == "END_STAGE"
    assert s747["passage_core_axes"] == "END_STAGE"
    assert (s747["locally_supported_occurrences"], s747["local_support_pages"]) == ("4", "3")
    assert s747["passage_status"] == "P1_LOCAL_PASSAGE_SUPPORT"
    assert len(g748_sheeol) == 1
    cold = g748_sheeol[0]
    assert cold["best_predicted_axes"] == "COLD"
    assert cold["whole_form_bridge_tier"] == "B0_NO_WHOLE_FORM_BRIDGE"
    assert cold["gdt747_prior_axes"] == "END_STAGE"
    assert cold["gdt747_prior_comparison"] == "GDT747_PRIOR_CONFLICT"

    output: list[dict[str, object]] = []
    for surface in sorted(specs):
        spec = specs[surface]
        selected_count = sum(
            row["right_surface"] == surface and select_gdt780_row(
                row["gdt779_renderer_contextual"], row["right_surface"],
                row["right_reader_exact"], FROZEN_SURFACES,
            )
            for row in base
        )
        common: dict[str, object] = {
            "entry": surface, "preferred_gdt780_default_de": spec["default_de"],
            "alternate_1_de": spec["alternate_1_de"], "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "functional_axis": spec["functional_axis"],
            "card_class": spec["card_class"], "source_evidence": spec["source_evidence"],
            "selected_exact_fallback_contexts": selected_count,
            "source_cache_occurrences": 0, "source_cache_pages": 0,
            "source_reader_exact_occurrences": 0, "source_reader_exact_pages": 0,
            "exact_right_contexts": 0, "ordered_value_follower_hits": 0,
            "ordered_value_conditional_rate": "NA", "ordered_value_baseline_rate": "NA",
            "ordered_value_descriptive_lift": "NA", "leave_target_out_right_contexts": "NA",
            "leave_target_out_value_hits": "NA", "leave_target_out_conditional_rate": "NA",
            "gdt745_consensus_axes": "NA",
            "gdt745_rival_axes": "NA", "gdt746_distribution_status": "NA",
            "gdt746_form_and_top5_axis_agreement": "NA", "gdt747_local_support_occurrences": 0,
            "gdt747_local_support_pages": 0, "gdt748_counterframe_axes": "NA",
            "gdt748_counterframe_bridge_tier": "NA",
            "target_independence_audit_id": independence_by_surface[surface]["audit_id"],
            "target_independence_status": independence_by_surface[surface]["independence_status"],
            "target_local_support_tier": independence_by_surface[surface]["target_local_support_tier"],
            "target_local_support_count": independence_by_surface[surface]["target_local_support_count"],
            "positive_evidence": VERIFIED_POSITIVE[surface], "counterevidence": spec["counterevidence"],
            "scope": "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY__NO_SUBSTRING_EXPORT",
            "replaceable": 1, "literal_identity": "OPEN", "numeric_identity_confirmed": 0,
            "specific_substance_confirmed": 0, "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        }
        if surface == "eees":
            common.update({
                "source_cache_occurrences": "NA",
                "source_cache_pages": "NA",
                "source_reader_exact_occurrences": int(eees["reader_exact_occurrences"]),
                "source_reader_exact_pages": "NA",
                "exact_right_contexts": int(eees["exact_right_contexts"]),
                "ordered_value_follower_hits": int(eees["ordered_value_follower_hits"]),
                "ordered_value_conditional_rate": eees["ordered_value_conditional_rate"],
                "ordered_value_baseline_rate": eees["ordered_value_baseline_rate"],
                "ordered_value_descriptive_lift": eees["ordered_value_descriptive_lift"],
                "leave_target_out_right_contexts": 3,
                "leave_target_out_value_hits": 2,
                "leave_target_out_conditional_rate": "0.666667",
            })
        else:
            common.update({
                "source_cache_occurrences": int(s745["cache_occurrences"]),
                "source_cache_pages": int(s745["cache_pages"]),
                "source_reader_exact_occurrences": int(s745["reader_exact_occurrences"]),
                "source_reader_exact_pages": int(s745["reader_exact_pages"]),
                "gdt745_consensus_axes": s745["analogy_consensus_axes"],
                "gdt745_rival_axes": s745["analogy_rival_axes"],
                "gdt746_distribution_status": s746["distribution_status"],
                "gdt746_form_and_top5_axis_agreement": s746["form_and_top5_axis_agreement"],
                "gdt747_local_support_occurrences": int(s747["locally_supported_occurrences"]),
                "gdt747_local_support_pages": int(s747["local_support_pages"]),
                "gdt748_counterframe_axes": cold["best_predicted_axes"],
                "gdt748_counterframe_bridge_tier": cold["whole_form_bridge_tier"],
            })
        output.append(common)
    assert len(output) == 2
    assert sum(int(row["selected_exact_fallback_contexts"]) for row in output) == 2
    return output


def build_spans(base: Sequence[Mapping[str, str]], specs: Mapping[str, Mapping[str, str]]) -> list[dict[str, object]]:
    matches = [
        row for row in base
        if select_gdt780_row(
            row["gdt779_renderer_contextual"], row["right_surface"],
            row["right_reader_exact"], FROZEN_SURFACES,
        )
    ]
    all_deck_matches = [row for row in base if row["right_surface"] in FROZEN_SURFACES]
    assert matches == all_deck_matches and len(matches) == 2
    assert {row["right_surface"] for row in matches} == FROZEN_SURFACES
    assert all(row["gdt779_renderer_contextual"] == "0" for row in matches)
    assert all(row["right_reader_exact"] == "1" for row in matches)

    inherited_owners = inherited_owner_map(base)
    spans: list[dict[str, object]] = []
    for number, source in enumerate(matches, 1):
        surface, spec = source["right_surface"], specs[source["right_surface"]]
        ol_ordinal, right_ordinal = int(source["ordinal"]), int(source["right_ordinal"])
        tokens = source["written_line_eva"].split()
        assert right_ordinal == ol_ordinal + 1
        assert tokens[ol_ordinal - 1] == "ol" and tokens[right_ordinal - 1] == surface
        assert source["gdt779_default_de"] == "Ansatz-/Zubereitungsposten"
        assert source["gdt779_consumed_token_count"] == "0"
        assert source["gdt779_consumed_token_ids"] == "NONE"
        token_id = f"{source['locus']}@{right_ordinal}"
        assert token_id not in inherited_owners
        spans.append({
            "span_id": f"G780-S{number:03d}", "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "register_id": f"{source['section']}|{source['language']}|{source['hand']}",
            "ol_ordinal": ol_ordinal, "right_ordinal": right_ordinal, "line_token_count": len(tokens),
            "right_surface": surface, "written_span_eva": f"ol {surface}",
            "written_line_eva": source["written_line_eva"], "right_reader_exact": 1,
            "old_gdt779_branch": source["gdt779_branch"],
            "old_gdt779_default_de": source["gdt779_default_de"],
            "old_gdt779_contextual": int(source["gdt779_renderer_contextual"]),
            "selected_whole_default_de": spec["default_de"],
            "new_gdt780_default_de": spec["default_de"],
            "alternate_1_de": spec["alternate_1_de"], "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "functional_axis": spec["functional_axis"],
            "card_class": spec["card_class"], "source_evidence": spec["source_evidence"],
            "positive_evidence": VERIFIED_POSITIVE[surface], "counterevidence": spec["counterevidence"],
            "scope_status": spec["renderer_scope"], "semantic_change_class": "FALLBACK_REPLACEMENT",
            "fallback_replacement": 1, "display_changed": 1,
            "inherited_consumed_token_ids": source["gdt779_consumed_token_ids"],
            "gdt780_consumed_token_id": token_id, "same_row_inherited_consumption_takeover": 0,
            "new_unique_consumption": 1, "cross_row_consumption_collision": 0,
            "selection_rule": SELECTION_RULE, "selection_uses_occurrence_id": 0,
            "selection_uses_page_or_locus": 0, "selection_uses_neighbor_or_frequency": 0,
            "selection_uses_substring": 0, "exact_complete_whole_only": 1,
            "default_is_translation": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len({row["locus"] for row in spans}) == 2
    assert len({row["page"] for row in spans}) == 2
    assert len({row["physical_folio"] for row in spans}) == 2
    return spans


def build_renderer(base: Sequence[Mapping[str, str]], spans: Sequence[Mapping[str, object]]) -> tuple[
    list[dict[str, object]], dict[str, str]
]:
    by_target = {str(row["target_occurrence_id"]): row for row in spans}
    assert len(by_target) == 2
    output: list[dict[str, object]] = []
    for source in base:
        row: dict[str, object] = dict(source)
        row.update({
            "gdt780_branch": "INHERITED_GDT779", "gdt780_default_de": source["gdt779_default_de"],
            "gdt780_renderer_contextual": int(source["gdt779_renderer_contextual"]),
            "gdt780_span_id": source["gdt779_span_id"], "gdt780_exact_whole": source["gdt779_exact_whole"],
            "gdt780_confidence": source["gdt779_confidence"],
            "gdt780_consumed_token_count": int(source["gdt779_consumed_token_count"]),
            "gdt780_consumed_token_ids": source["gdt779_consumed_token_ids"],
            "gdt780_fallback_replacement": 0, "gdt780_display_changed": 0,
            "gdt780_new_unique_consumption": 0, "gdt780_positive_evidence": "INHERITED_GDT779",
            "gdt780_counterevidence": "INHERITED_GDT779", "gdt780_dispatch_rule": "INHERITED_GDT779",
            "gdt780_scope_status": "INHERITED_GDT779", "gdt780_card_class": "INHERITED_GDT779",
            "gdt780_functional_axis": "INHERITED_GDT779", "gdt780_default_is_translation": 0,
            "gdt780_confirmed_lexeme": 0, "gdt780_confirmed_plaintext": 0,
            "gdt780_component_export_credit": 0,
        })
        span = by_target.get(source["target_occurrence_id"])
        if span is not None:
            row.update({
                "gdt780_branch": "GDT780_EXACT_OL_PLUS_CARDLESS_SUPPORTED_WHOLE",
                "gdt780_default_de": span["new_gdt780_default_de"], "gdt780_renderer_contextual": 1,
                "gdt780_span_id": span["span_id"], "gdt780_exact_whole": span["right_surface"],
                "gdt780_confidence": span["confidence"], "gdt780_consumed_token_count": 1,
                "gdt780_consumed_token_ids": span["gdt780_consumed_token_id"],
                "gdt780_fallback_replacement": 1, "gdt780_display_changed": 1,
                "gdt780_new_unique_consumption": 1, "gdt780_positive_evidence": span["positive_evidence"],
                "gdt780_counterevidence": span["counterevidence"], "gdt780_dispatch_rule": SELECTION_RULE,
                "gdt780_scope_status": span["scope_status"], "gdt780_card_class": span["card_class"],
                "gdt780_functional_axis": span["functional_axis"],
            })
        output.append(row)

    owners: dict[str, str] = {}
    for row in output:
        value, count = str(row["gdt780_consumed_token_ids"]), int(row["gdt780_consumed_token_count"])
        token_ids = [] if value == "NONE" else value.split("|")
        assert len(token_ids) == count
        for token_id in token_ids:
            assert token_id not in owners, (token_id, owners.get(token_id), row["target_occurrence_id"])
            owners[token_id] = str(row["target_occurrence_id"])
    assert len(output) == 376
    assert sum(int(row["gdt780_renderer_contextual"]) for row in output) == 247
    assert sum(1 - int(row["gdt780_renderer_contextual"]) for row in output) == 129
    assert sum(int(row["gdt780_fallback_replacement"]) for row in output) == 2
    assert sum(int(row["gdt780_display_changed"]) for row in output) == 2
    assert sum(int(row["gdt780_new_unique_consumption"]) for row in output) == 2
    assert len(owners) == 207

    for source, row in zip(base, output):
        selected = source["target_occurrence_id"] in by_target
        assert all(str(row[field]) == source[field] for field in source)
        if not selected:
            assert row["gdt780_default_de"] == source["gdt779_default_de"]
            assert int(row["gdt780_renderer_contextual"]) == int(source["gdt779_renderer_contextual"])
            assert row["gdt780_span_id"] == source["gdt779_span_id"]
            assert row["gdt780_exact_whole"] == source["gdt779_exact_whole"]
            assert row["gdt780_confidence"] == source["gdt779_confidence"]
            assert int(row["gdt780_consumed_token_count"]) == int(source["gdt779_consumed_token_count"])
            assert row["gdt780_consumed_token_ids"] == source["gdt779_consumed_token_ids"]
    return output, owners


def build_precedence(base: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, object]],
                     spans: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    old_by_target = one_by(base, "target_occurrence_id")
    new_by_target = {str(row["target_occurrence_id"]): row for row in renderer}
    output: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        target = str(span["target_occurrence_id"])
        old, new = old_by_target[target], new_by_target[target]
        assert old["gdt779_renderer_contextual"] == "0" and old["right_reader_exact"] == "1"
        output.append({
            "precedence_id": f"G780-H{number:03d}", "target_occurrence_id": target,
            "page": old["page"], "physical_folio": old["physical_folio"], "locus": old["locus"],
            "ol_ordinal": int(old["ordinal"]), "right_ordinal": int(old["right_ordinal"]),
            "right_surface": old["right_surface"], "right_reader_exact": int(old["right_reader_exact"]),
            "parent_gdt779_fallback": 1, "parent_gdt779_contextual": 0,
            "frozen_two_whole_deck_member": 1, "precedence_disposition": "SELECTED_GDT780_FALLBACK",
            "old_gdt779_branch": old["gdt779_branch"], "old_gdt779_default_de": old["gdt779_default_de"],
            "old_gdt779_consumed_token_count": int(old["gdt779_consumed_token_count"]),
            "old_gdt779_consumed_token_ids": old["gdt779_consumed_token_ids"],
            "new_gdt780_branch": new["gdt780_branch"], "new_gdt780_default_de": new["gdt780_default_de"],
            "new_gdt780_contextual": int(new["gdt780_renderer_contextual"]),
            "new_gdt780_consumed_token_count": int(new["gdt780_consumed_token_count"]),
            "new_gdt780_consumed_token_ids": new["gdt780_consumed_token_ids"],
            "fallback_replacement": int(new["gdt780_fallback_replacement"]),
            "same_row_inherited_consumption_takeover": 0, "cross_row_consumption_collision": 0,
            "selection_rule": SELECTION_RULE, "selection_uses_occurrence_id": 0,
            "component_export_credit": 0,
        })
    assert len(output) == 2
    return output


def render_line(locus: str, written_line: str,
                renderer_by_position: Mapping[tuple[str, int], Mapping[str, object]], generation: str) -> str:
    assert generation in {"gdt779", "gdt780"}
    tokens, rendered, consumed = written_line.split(), [], set()
    for ordinal, token in enumerate(tokens, 1):
        if ordinal in consumed:
            continue
        dispatch = renderer_by_position.get((locus, ordinal))
        if dispatch is None:
            rendered.append(token)
            continue
        if int(dispatch[f"{generation}_renderer_contextual"]):
            rendered.append(f"⟦{dispatch[f'{generation}_default_de']}⟧")
            count = int(dispatch[f"{generation}_consumed_token_count"])
            consumed.update(range(ordinal + 1, ordinal + count + 1))
        else:
            rendered.append(token)
    return " ".join(rendered)


def build_passages(base: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, object]],
                   spans: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    old_by_pos = {(row["locus"], int(row["ordinal"])): row for row in base}
    new_by_pos = {(str(row["locus"]), int(row["ordinal"])): row for row in renderer}
    output: list[dict[str, object]] = []
    for number, span in enumerate(sorted(spans, key=lambda row: str(row["locus"])), 1):
        locus, written = str(span["locus"]), str(span["written_line_eva"])
        old_patch = render_line(locus, written, old_by_pos, "gdt779")
        new_patch = render_line(locus, written, new_by_pos, "gdt780")
        assert old_patch != new_patch
        output.append({
            "passage_patch_id": f"G780-P{number:03d}", "span_id": span["span_id"],
            "target_occurrence_id": span["target_occurrence_id"],
            "page": span["page"], "physical_folio": span["physical_folio"], "locus": locus,
            "ol_ordinal": span["ol_ordinal"], "right_ordinal": span["right_ordinal"],
            "right_surface": span["right_surface"], "right_token_id": span["gdt780_consumed_token_id"],
            "selected_whole_default_de": span["selected_whole_default_de"],
            "written_line_eva": written, "inherited_gdt779_patch_de": old_patch,
            "gdt780_practical_patch_de": new_patch,
            "patch_legend": "double brackets are replaceable exact-span defaults; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(output) == 2
    return output


def normalize_residual_reason(parent_reason: str) -> str:
    if parent_reason in {"V99_CARD_NONEXACT_FINAL44", "V99_CARD_NONEXACT_RAW_ONLY"}:
        return "V99_CARD_NONEXACT"
    return parent_reason


def build_residual(renderer: Sequence[Mapping[str, object]],
                   parent_residual: Sequence[Mapping[str, str]]) -> list[dict[str, object]]:
    residual_by_target = one_by(parent_residual, "target_occurrence_id")
    remaining = [row for row in renderer if int(row["gdt780_renderer_contextual"]) == 0]
    output: list[dict[str, object]] = []
    for number, row in enumerate(remaining, 1):
        source = residual_by_target[str(row["target_occurrence_id"])]
        reason = normalize_residual_reason(source["residual_reason"])
        output.append({
            "residual_id": f"G780-R{number:03d}", "parent_gdt779_residual_id": source["residual_id"],
            "target_occurrence_id": row["target_occurrence_id"],
            "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
            "ol_ordinal": int(row["ordinal"]), "right_ordinal": int(row["right_ordinal"]),
            "right_surface": row["right_surface"], "right_reader_exact": int(row["right_reader_exact"]),
            "parent_residual_reason": source["residual_reason"], "residual_reason": reason,
            "gdt780_default_de": row["gdt780_default_de"],
            "frozen_two_whole_deck_member": int(str(row["right_surface"]) in FROZEN_SURFACES),
            "component_export_credit": 0,
        })
    assert len(output) == 129
    assert Counter(row["residual_reason"] for row in output) == Counter({
        "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT": 23, "V99_CARD_NONEXACT": 49,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20, "LINE_FINAL_NO_RIGHT": 37,
    })
    assert not any(int(row["frozen_two_whole_deck_member"]) for row in output)
    return output


def make_packet(spans: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        edge_id = f"G780-E{number:03d}"
        packet.append({
            "edge_id": edge_id, "batch_id": "GDT780_TWO_CARDLESS_COMPLETE_WHOLES",
            "page": span["page"], "physical_folio": span["physical_folio"],
            "diagram_unit_id": f"LINE:{span['locus']}",
            "pivot_visual_id": f"TOKEN:{span['locus']}:{span['ol_ordinal']}",
            "pivot_locus": f"{span['locus']}@{span['ol_ordinal']}",
            "target_visual_id": f"TOKEN:{span['locus']}:{span['right_ordinal']}",
            "target_locus": f"{span['locus']}@{span['right_ordinal']}",
            "relation_type": "NEXT_TOKEN", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT779", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT780_RUNNER",
            "relation_reviewer": "GDT780_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNREVIEWED_TEXT_RELATION", "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        crosswalk.append({
            "edge_id": edge_id, "batch_id": "GDT780_TWO_CARDLESS_COMPLETE_WHOLES",
            "span_id": span["span_id"], "target_occurrence_id": span["target_occurrence_id"],
            "page": span["page"], "physical_folio": span["physical_folio"], "locus": span["locus"],
            "ol_ordinal": span["ol_ordinal"], "right_ordinal": span["right_ordinal"],
            "right_surface": span["right_surface"], "written_span_eva": span["written_span_eva"],
            "selection_rule": SELECTION_RULE, "score_eligible": 0, "component_export_credit": 0,
        })
    assert len(packet) == len(crosswalk) == 2
    return packet, crosswalk


def build_report(result: Mapping[str, object], passages: Sequence[Mapping[str, object]]) -> str:
    examples = "\n".join(
        f"- `{row['locus']}`: `{row['written_line_eva']}` → {row['gdt780_practical_patch_de']}"
        for row in passages
    )
    relation = result["relation_packet"]
    assert isinstance(relation, Mapping)
    return f"""# GDT780 — zwei belegte kartenlose Ganzwörter nach `ol`

Status: `{result['status']}`.

## Ergebnis

Der eingefrorene, occurrence-ID-freie Selektor trifft genau zwei der 25
reader-exakten kartenlosen GDT779-Restzeilen: `ol eees` und `ol sheeol`, je
einmal auf zwei loci, zwei Seitenlabels und zwei physischen Folios. Es existiert
kein weiteres exaktes, nicht-exaktes oder bereits kontextuelles Elternmatch
dieser beiden vollständigen Oberflächen.

Beide Treffer ersetzen den generischen Ansatz-/Zubereitungsfallback. Die
kontextuelle Abdeckung steigt **245→247**, die Restmenge fällt **131→129** und
der kollisionsfreie Verbrauch rechter Tokens steigt **205→207**. Alle anderen
374 Rendererzeilen bleiben in Bedeutung, Precedence und Verbrauch unverändert.

## Unabhängige Brücken

- **`eees` → Mengenfeld:** Der gelockte GDT758-Komparator zählt sieben
  reader-exakte Vorkommen, vier exakte Rechtskontexte und drei `aiin`-Folger
  (Rate .75 gegenüber .021613, Lift 34.702083). GDT769s gelockte Detailzeile
  rekonstruiert die Zielstelle als reader-exaktes `ol`, gefolgt von den beiden
  sauberen, zulässigen Tokens `eees aiin`; ihre Entfernung ergibt ausführbar
  **drei Kontexte und zwei `aiin`-Treffer**. Das trägt ein Mengen-/Wertfeld,
  aber weder Zahl noch Einheit.
- **`sheeol` → Endzustand:** GDT745–GDT747 liefern zehn Cache-/neun exakte
  Vorkommen, einen gemeinsamen Form-Verteilungskern `END_STAGE` und vier lokale
  Endkontakte auf drei Seiten. Die gelockte Detailzeile G747-O060 weist die
  Zielstelle selbst als reader-exakt, `L0` und mit null lokalen Supports aus;
  alle vier Endkontakte liegen damit außerhalb des Ziels. Der sichtbare
  GDT748-Kälterahmen hat ausdrücklich keine Ganzwortbrücke; Feuchte und Kälte
  bleiben Rivalen, nicht Identitäten.

## Zwei vollständige Passagen

{examples}

Die Doppelklammern markieren ersetzbare exakte Spannenwerte. Ungeklammerte
EVA-Formen bleiben ungelöst.

## Restschuld und Grenze

Die 129 Fallbacks zerfallen in 23 reader-exakte kartenlose Rechte, 49
nicht-exakte Rechte mit V99R7-Karte, 20 nicht-exakte Rechte ohne Karte und 37
Zeilenenden ohne rechtes Token. Keine andere Form wird über Nachbarn,
Editdistanz oder Teilstrings mitgezogen.

`Mengenfeld` und `Endzustand` sind praktische Rollenlabels ganzer Spannen, keine
Übersetzungen. GDT780 bestätigt kein EVA-Zeichen, keinen Wortteil, kein Lexem,
keine Zahl, Einheit, Flüssigkeit, Substanz oder Klartextklausel. Es wurden keine
neuen Seiten, Bilder, OCR oder Transkriptionen geöffnet; `f84` und `f84r`
blieben gesperrt. Das GDT388-Paket bleibt `{relation['status']}`.
"""


def build_artifact_readme() -> str:
    return """# GDT780 artifacts

- `GDT780_25_EXACT_CARDLESS_INTAKE.tsv`: complete reconstructed reader-exact cardless intake.
- `GDT780_2_EXACT_WHOLE_ATLAS.tsv`: both pure-selector matches and their whole-span defaults.
- `GDT780_2_PRECEDENCE_AUDIT.tsv`: parent/new state and consumption for both changes.
- `GDT780_376_RENDERER.tsv`: full compact GDT779 parent plus GDT780 renderer state.
- `GDT780_2_WORKING_DICTIONARY_EVIDENCE.tsv`: both replaceable defaults, rivals and reconstructed source evidence.
- `GDT780_2_TARGET_INDEPENDENCE_AUDIT.tsv`: rowwise target-removal arithmetic and local-support exclusion.
- `GDT780_2_PASSAGE_PATCHES.tsv`: both complete changed line renderings.
- `GDT780_RESIDUAL_129_FALLBACK_CENSUS.tsv`: every remaining fallback and normalized reason.
- `GDT780_GDT388_RELATION_PACKET.tsv`: explicitly ineligible descriptive adjacency packet.
- `GDT780_RELATION_EDGE_CROSSWALK.tsv`: packet-to-span crosswalk.
- `RELATION_PACKET_INTAKE.json`: executable GDT388 intake result.
- `RESULT.json`: compact machine-readable result.

All German values are replaceable complete-whole role defaults, not translations.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()

    lock_count = verify_locks()
    specs = validate_specs(read_tsv(SPECS_PATH))
    base = read_tsv(PARENT_RENDERER)
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    parent_residual = read_tsv(PARENT_RESIDUAL)
    assert len(base) == 376
    assert sum(int(row["gdt779_renderer_contextual"]) for row in base) == 245
    assert sum(1 - int(row["gdt779_renderer_contextual"]) for row in base) == 131
    assert parent_result["renderer"]["gdt779_contextual"] == 245
    assert parent_result["renderer"]["gdt779_fallbacks"] == 131
    assert parent_result["consumption"]["total_unique_right_tokens"] == 205

    intake = build_intake(base, parent_residual, specs)
    independence = build_target_independence(base)
    evidence = build_evidence(specs, base, independence)
    spans = build_spans(base, specs)
    renderer, owners = build_renderer(base, spans)
    precedence = build_precedence(base, renderer, spans)
    passages = build_passages(base, renderer, spans)
    residual = build_residual(renderer, parent_residual)
    packet, crosswalk = make_packet(spans)

    outputs = [
        ("GDT780_25_EXACT_CARDLESS_INTAKE.tsv", intake),
        ("GDT780_2_EXACT_WHOLE_ATLAS.tsv", spans),
        ("GDT780_2_PRECEDENCE_AUDIT.tsv", precedence),
        ("GDT780_376_RENDERER.tsv", renderer),
        ("GDT780_2_WORKING_DICTIONARY_EVIDENCE.tsv", evidence),
        ("GDT780_2_TARGET_INDEPENDENCE_AUDIT.tsv", independence),
        ("GDT780_2_PASSAGE_PATCHES.tsv", passages),
        ("GDT780_RESIDUAL_129_FALLBACK_CENSUS.tsv", residual),
        ("GDT780_GDT388_RELATION_PACKET.tsv", packet),
        ("GDT780_RELATION_EDGE_CROSSWALK.tsv", crosswalk),
    ]
    for name, rows in outputs:
        write_tsv(artifacts / name, rows, list(rows[0]))

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.relation_edge_intake import validate_relation_edge_packet

    packet_intake = validate_relation_edge_packet(artifacts / "GDT780_GDT388_RELATION_PACKET.tsv")
    assert packet_intake == {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 2, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", packet_intake)

    result: dict[str, object] = {
        "experiment_id": "GDT780", "status": STATUS, "source_locks": lock_count,
        "inherited_guard": parent_result["inherited_guard"],
        "cohort": {
            "renderer_rows": 376, "reader_exact_cardless_intake": len(intake),
            "selected_spans": len(spans), "selected_forms": len(specs),
            "loci": len({row["locus"] for row in spans}),
            "page_labels": len({row["page"] for row in spans}),
            "physical_folios": len({row["physical_folio"] for row in spans}),
        },
        "precedence": {
            "full_parent_deck_matches": 2, "reader_exact_parent_deck_matches": 2,
            "nonexact_parent_deck_matches": 0, "parent_fallback_deck_matches": 2,
            "protected_contextual_deck_matches": 0, "selected_fallback_matches": 2,
            "nonselected_parent_rows_unchanged": 374,
        },
        "changes": {
            "fallback_replacements": 2, "actual_display_changes": 2,
            "contextual_sharpenings": 0, "contextual_confirmations": 0,
            "passage_patches": len(passages),
        },
        "renderer": {
            "gdt779_contextual": 245, "gdt780_contextual": 247,
            "gdt779_fallbacks": 131, "gdt780_fallbacks": 129,
        },
        "consumption": {
            "gdt779_unique_right_tokens": 205, "gdt780_selected_right_tokens": 2,
            "same_row_inherited_takeovers": 0, "new_unique_right_tokens": 2,
            "total_unique_right_tokens": len(owners), "cross_row_collisions": 0,
        },
        "evidence": {
            "dictionary_evidence_rows": len(evidence),
            "target_independence_audit_rows": len(independence),
            "eees_reader_exact_occurrences": 7,
            "eees_exact_right_contexts": 4, "eees_ordered_value_follower_hits": 3,
            "eees_leave_target_out_right_contexts": 3,
            "eees_leave_target_out_value_hits": 2,
            "eees_leave_target_out_claim_runner_reconstructed": True,
            "sheeol_local_end_contacts": 4, "sheeol_local_end_contact_pages": 3,
            "sheeol_target_local_support_tier": "L0_NO_LOCAL_W23_SUPPORT",
            "sheeol_target_local_support_count": 0,
            "sheeol_target_independence_runner_reconstructed": True,
            "sheeol_cold_counterframe_has_whole_bridge": False,
        },
        "residual_fallback_rows": len(residual),
        "residual_partition": {
            "no_card_reader_exact": 23, "v99_card_nonexact": 49,
            "no_card_reader_nonexact": 20, "line_final_no_right": 37,
        },
        "relation_packet": packet_intake, "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0, "numeric_identities": 0,
        "specific_substances": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0,
        "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": "Two replaceable exact ol plus complete-whole role defaults only; no EVA component, lexeme, number, unit, language, plaintext, liquid, substance, disease, or treatment.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result, passages), encoding="utf-8")
    (artifacts / "README.md").write_text(build_artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
