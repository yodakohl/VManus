#!/usr/bin/env python3
"""Independent validation for the GDT547 atomic/factor visible reader."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt547_atomic_factor_visible_reader"
OUT = BASE / "artifacts"
G517 = ROOT / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/artifacts"
G535 = ROOT / "experiments/yolo/gdt535_same_statement_q_null_qef_closure/artifacts"
G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
G542 = ROOT / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"

TIER_IN = G542 / "gdt542_145_final_support_tiers.tsv"
CONTEXT_IN = G540 / "gdt540_145_surface_context_contract.tsv"
CURRENT_MAP_IN = G517 / "gdt517_current30_chunk_mapping_lexicon.tsv"
QEF_CERT_IN = G535 / "gdt535_qef_resolution_certificate.tsv"

CARD = OUT / "gdt547_24_atomic_factor_reader_cards.tsv"
COVER = OUT / "gdt547_44_old26_exact_cover_paths.tsv"
SEAM = OUT / "gdt547_52_atomic_pair_interfaces.tsv"
SPECIAL = OUT / "gdt547_3_special_visible_routes.tsv"
AIIS = OUT / "gdt547_4_aiis_prefix_conditioning_cards.tsv"
SUMMARY = OUT / "gdt547_atomic_factor_reader_summary.tsv"
BOOK = OUT / "GDT547_24_ATOMIC_FACTOR_READER.md"
RESULT = OUT / "gdt547_result.json"
VALIDATION = OUT / "gdt547_validation.json"
RUN = BASE / "src/run.py"
CLI = BASE / "src/read_atomic.py"
CERT_CLI = (
    ROOT
    / "experiments/yolo/gdt446_identity_execution_intake_split/src"
    / "intake_certificate_v2.py"
)
STATUS = "PASS_24_ATOM_FACTOR_CARDS_VISIBLE__21_OLD_DECK_COVERS__3_SPECIAL_ROUTES"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field}")
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace_aliases(trace: str) -> list[str]:
    return [part.split("→", 1)[0] for part in trace.split(" | ")]


def trace_recipe(trace: str) -> str:
    atoms = []
    for part in trace.split(" | "):
        right = part.split("→", 1)[1]
        if right == "NULL_Q":
            continue
        atoms.extend(right.split("+"))
    return "+".join(atoms)


def main() -> int:
    tiers = [
        row
        for row in read_tsv(TIER_IN)
        if row["final_support_tier"] == "ATOMS_AND_FACTORS_ONLY"
    ]
    contexts = keyed(read_tsv(CONTEXT_IN), "surface")
    current_map = read_tsv(CURRENT_MAP_IN)
    qef_cert = read_tsv(QEF_CERT_IN)
    cards = read_tsv(CARD)
    covers = read_tsv(COVER)
    seams = read_tsv(SEAM)
    specials = read_tsv(SPECIAL)
    aiis = read_tsv(AIIS)
    summary_rows = read_tsv(SUMMARY)
    book = BOOK.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    tier_map = keyed(tiers, "surface")
    card_map = keyed(cards, "surface")
    special_map = keyed(specials, "surface")
    summary = {row["metric"]: row["value"] for row in summary_rows}
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("source_tier_count", len(tiers) == 24, len(tiers))
    check("reader_card_count", len(cards) == 24 and len(card_map) == 24, [len(cards), len(card_map)])
    check("reader_surface_set_exact", set(card_map) == set(tier_map), sorted(set(card_map) ^ set(tier_map)))
    check("old_cover_path_count", len(covers) == 44, len(covers))
    check("seam_count", len(seams) == 52, len(seams))
    check("special_route_count", len(specials) == 3, len(specials))
    check("aiis_conditioning_count", len(aiis) == 4, len(aiis))

    source_errors = []
    for surface, card in card_map.items():
        tier = tier_map[surface]
        context = contexts[surface]
        comparisons = {
            "final_recipe": tier["final_recipe"],
            "atom_count": tier["final_recipe_atom_count"],
            "observed_requirement_modes": context["observed_requirement_modes"],
            "observed_incoming_action_roots": context["observed_incoming_action_roots"],
            "observed_incoming_argument_roots": context["observed_incoming_argument_roots"],
            "future_action_contract": context["future_action_contract"],
            "future_argument_contract": context["future_argument_contract"],
            "neutral_component_reading_de": context["neutral_surface_phrase_de"],
            "known_contextual_readings_de": context["known_contextual_readings_de"],
        }
        for field, expected in comparisons.items():
            if card[field] != expected:
                source_errors.append([surface, field, card[field], expected])
    check("tier_and_context_fields_exact", not source_errors, source_errors[:10])

    visible_errors = []
    recipe_errors = []
    count_errors = []
    for surface, card in card_map.items():
        reconstructed_surface = "".join(trace_aliases(card["visible_trace"]))
        if reconstructed_surface != surface or card["exact_surface_reconstruction"] != "YES":
            visible_errors.append([surface, reconstructed_surface])
        reconstructed_recipe = trace_recipe(card["visible_trace"])
        if reconstructed_recipe != card["final_recipe"]:
            recipe_errors.append([surface, reconstructed_recipe, card["final_recipe"]])
        if (
            int(card["renderer_segment_count"])
            != int(card["canonical_segment_count"])
            + int(card["learned_or_special_segment_count"])
        ):
            count_errors.append(surface)
    check("all_24_visible_surfaces_reconstruct", not visible_errors, visible_errors)
    check("all_24_visible_traces_reconstruct_recipe", not recipe_errors, recipe_errors)
    check("segment_partition_exact", not count_errors, count_errors)

    route_counts = Counter(row["visible_route_class"] for row in cards)
    expected_routes = {
        "OLD26_ALL_CANONICAL_VISIBLE_ATOMS": 16,
        "OLD26_MIXED_CANONICAL_AND_LEARNED_RENDERERS": 5,
        "CURRENT30_DOMINANT_SHORT_RENDERER": 1,
        "PREFIX_CONDITIONED_CURRENT_AIIS_CHANNEL": 1,
        "GDT535_LOCAL_Q_NULL_PLUS_CANONICAL_ATOMS": 1,
    }
    check("visible_route_distribution", route_counts == Counter(expected_routes), dict(route_counts))
    check(
        "special_route_inventory",
        set(special_map) == {"chedaiir", "faiis", "qef"},
        sorted(special_map),
    )

    selected_covers = [row for row in covers if row["selected_cover"] == "YES"]
    selected_cover_map = keyed(selected_covers, "surface")
    cover_counts = Counter(row["surface"] for row in covers)
    cover_errors = []
    for surface, cover in selected_cover_map.items():
        if cover["visible_trace"] != card_map[surface]["visible_trace"]:
            cover_errors.append([surface, cover["visible_trace"], card_map[surface]["visible_trace"]])
        if "".join(trace_aliases(cover["visible_trace"])) != surface:
            cover_errors.append([surface, "surface"])
        if trace_recipe(cover["visible_trace"]) != card_map[surface]["final_recipe"]:
            cover_errors.append([surface, "recipe"])
        if int(card_map[surface]["old26_exact_cover_path_count"]) != cover_counts[surface]:
            cover_errors.append([surface, "count"])
    check("selected_old_covers_replay", len(selected_cover_map) == 21 and not cover_errors, cover_errors)
    check(
        "old_cover_missing_set",
        set(card_map) - set(selected_cover_map) == {"chedaiir", "faiis", "qef"},
        sorted(set(card_map) - set(selected_cover_map)),
    )

    aiir = [
        row
        for row in current_map
        if row["surface_chunk"] == "aiir" and row["recipe"] == "IIN+R"
    ]
    check(
        "aiir_dominant_mapping_replay",
        len(aiir) == 1
        and aiir[0]["support"] == "17"
        and aiir[0]["total_surface_support"] == "20"
        and aiir[0]["support_share"] == "0.850000"
        and aiir[0]["high_confidence_top_mapping"] == "YES",
        aiir,
    )
    aiis_split = Counter(row["aiis_channel_recipe"] for row in aiis)
    check(
        "aiis_prefix_split_replay",
        aiis_split == Counter({"IIN+S": 2, "A_ADDR+IIN+S": 2})
        and {row["surface"] for row in aiis} == {"qoaiis", "faiis", "saiisol", "saiis"},
        dict(aiis_split),
    )
    qef_layers = {row["evidence_layer"]: row for row in qef_cert}
    check(
        "qef_local_q_null_replay",
        qef_layers["CURRENT_SAME_STATEMENT_NEIGHBOURS"]["support"] == "6"
        and qef_layers["CURRENT_SAME_STATEMENT_NEIGHBOURS"]["total"] == "6"
        and qef_layers["CURRENT_SAME_STATEMENT_NEIGHBOURS"]["value"] == "NONCARRIER_Q"
        and qef_layers["OLD_GLOBAL_VISIBLE_q_NULL"]["support"] == "75"
        and qef_layers["OLD_GLOBAL_VISIBLE_q_NULL"]["total"] == "84",
        special_map["qef"]["support"],
    )

    seams_by_surface: dict[str, list[dict[str, str]]] = {}
    for seam in seams:
        seams_by_surface.setdefault(seam["surface"], []).append(seam)
    seam_errors = []
    for surface, card in card_map.items():
        expected_pairs = list(zip(card["final_recipe"].split("+"), card["final_recipe"].split("+")[1:]))
        observed = sorted(seams_by_surface.get(surface, []), key=lambda row: int(row["pair_ordinal"]))
        observed_pairs = [row["ordered_pair"] for row in observed]
        if observed_pairs != [">".join(pair) for pair in expected_pairs]:
            seam_errors.append([surface, observed_pairs])
        old_count = sum(row["interface_status"] == "OLD26_DIRECT_INTERFACE" for row in observed)
        if int(card["direct_interface_count"]) != len(observed) or int(card["old26_direct_interface_count"]) != old_count:
            seam_errors.append([surface, "count"])
    check("all_atomic_pair_rows_replay", not seam_errors, seam_errors)
    seam_status = Counter(row["interface_status"] for row in seams)
    check(
        "seam_status_distribution",
        seam_status == Counter({"OLD26_DIRECT_INTERFACE": 40, "NEW_DIRECT_INTERFACE": 12}),
        dict(seam_status),
    )
    check(
        "nine_new_seam_targets",
        len({row["surface"] for row in seams if row["interface_status"] == "NEW_DIRECT_INTERFACE"}) == 9,
        sorted({row["surface"] for row in seams if row["interface_status"] == "NEW_DIRECT_INTERFACE"}),
    )

    decision_counts = Counter(row["gdt446_execution_decision"] for row in cards)
    current_counts = Counter(row["current_execution_route"] for row in cards)
    check(
        "gdt446_decision_distribution",
        decision_counts == Counter({"READ": 20, "READ_AMBER": 1, "STOP": 3}),
        dict(decision_counts),
    )
    check(
        "current_execution_overlay_distribution",
        current_counts
        == Counter(
            {
                "READ_FACTOR_GREEN": 20,
                "READ_FACTOR_AMBER_LOCAL_APPENDIX": 1,
                "READ_CURRENT_LOCAL_X_OVERLAY": 2,
                "READ_EXPLICIT_OBSERVED_PAIR_DEFAULT": 1,
            }
        ),
        dict(current_counts),
    )
    check(
        "gdt446_stop_inventory",
        {row["surface"] for row in cards if row["gdt446_execution_decision"] == "STOP"}
        == {"axor", "chxar", "shso"},
        sorted(row["surface"] for row in cards if row["gdt446_execution_decision"] == "STOP"),
    )
    check(
        "amber_inventory",
        {row["surface"] for row in cards if row["gdt446_execution_decision"] == "READ_AMBER"}
        == {"shtchy"},
        [row["surface"] for row in cards if row["gdt446_execution_decision"] == "READ_AMBER"],
    )
    check(
        "all_cards_have_meaning",
        all(row["neutral_component_reading_de"] and row["known_contextual_readings_de"] for row in cards),
        sum(bool(row["neutral_component_reading_de"]) for row in cards),
    )
    check(
        "reader_decision_and_guard",
        {row["reader_decision"] for row in cards} == {"READ_KNOWN_ATOMIC_FACTOR_WORKING_CARD"}
        and {row["guard"] for row in cards}
        == {"EXACT_KNOWN_SURFACE_ONLY__NO_UNKNOWN_SURFACE_OR_NEW_MEANING"},
        [sorted({row["reader_decision"] for row in cards}), sorted({row["guard"] for row in cards})],
    )

    counts = {
        "target_card_count": len(cards),
        "exact_surface_reconstruction_count": sum(row["exact_surface_reconstruction"] == "YES" for row in cards),
        "old26_exact_cover_target_count": len(selected_cover_map),
        "old26_exact_cover_path_count": len(covers),
        "old26_all_canonical_target_count": route_counts["OLD26_ALL_CANONICAL_VISIBLE_ATOMS"],
        "old26_mixed_learned_renderer_target_count": route_counts["OLD26_MIXED_CANONICAL_AND_LEARNED_RENDERERS"],
        "bounded_special_route_count": len(specials),
        "current30_dominant_aiir_route_count": route_counts["CURRENT30_DOMINANT_SHORT_RENDERER"],
        "prefix_conditioned_aiis_route_count": route_counts["PREFIX_CONDITIONED_CURRENT_AIIS_CHANNEL"],
        "local_q_null_route_count": route_counts["GDT535_LOCAL_Q_NULL_PLUS_CANONICAL_ATOMS"],
        "direct_interface_count": len(seams),
        "old26_direct_interface_count": seam_status["OLD26_DIRECT_INTERFACE"],
        "new_direct_interface_count": seam_status["NEW_DIRECT_INTERFACE"],
        "target_with_new_direct_interface_count": len(
            {row["surface"] for row in seams if row["interface_status"] == "NEW_DIRECT_INTERFACE"}
        ),
        "gdt446_factor_green_count": decision_counts["READ"],
        "gdt446_factor_amber_count": decision_counts["READ_AMBER"],
        "gdt446_factor_stop_count": decision_counts["STOP"],
        "current_local_x_overlay_count": current_counts["READ_CURRENT_LOCAL_X_OVERLAY"],
        "current_explicit_pair_default_count": current_counts["READ_EXPLICIT_OBSERVED_PAIR_DEFAULT"],
        "current_readable_card_count": len(cards),
        "self_contained_card_count": sum(row["observed_requirement_modes"] == "SELF_CONTAINED" for row in cards),
        "active_action_card_count": sum(row["observed_requirement_modes"] == "REQUIRES_ACTIVE_ACTION" for row in cards),
        "active_argument_card_count": sum(row["observed_requirement_modes"] == "REQUIRES_ACTIVE_ARGUMENT" for row in cards),
        "active_action_and_argument_card_count": sum(
            row["observed_requirement_modes"] == "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT" for row in cards
        ),
    }
    expected_counts = {
        "target_card_count": 24,
        "exact_surface_reconstruction_count": 24,
        "old26_exact_cover_target_count": 21,
        "old26_exact_cover_path_count": 44,
        "old26_all_canonical_target_count": 16,
        "old26_mixed_learned_renderer_target_count": 5,
        "bounded_special_route_count": 3,
        "current30_dominant_aiir_route_count": 1,
        "prefix_conditioned_aiis_route_count": 1,
        "local_q_null_route_count": 1,
        "direct_interface_count": 52,
        "old26_direct_interface_count": 40,
        "new_direct_interface_count": 12,
        "target_with_new_direct_interface_count": 9,
        "gdt446_factor_green_count": 20,
        "gdt446_factor_amber_count": 1,
        "gdt446_factor_stop_count": 3,
        "current_local_x_overlay_count": 2,
        "current_explicit_pair_default_count": 1,
        "current_readable_card_count": 24,
        "self_contained_card_count": 11,
        "active_action_card_count": 1,
        "active_argument_card_count": 8,
        "active_action_and_argument_card_count": 4,
    }
    check("core_metric_replay", counts == expected_counts, counts)
    check(
        "summary_core_metric_replay",
        all(summary.get(key) == str(value) for key, value in counts.items()),
        {key: summary.get(key) for key in counts},
    )
    expected_result = {
        **counts,
        "status": STATUS,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_exact", result == expected_result, result)

    known_probe = subprocess.run(
        [sys.executable, str(CLI), "--surface", "faiis", "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    known_payload = json.loads(known_probe.stdout) if known_probe.returncode == 0 else {}
    check(
        "known_cli_probe",
        known_probe.returncode == 0
        and known_payload.get("final_recipe") == "LOCAL_CHAR_F+IIN+S"
        and known_payload.get("visible_route_class") == "PREFIX_CONDITIONED_CURRENT_AIIS_CHANNEL",
        {"returncode": known_probe.returncode, "route": known_payload.get("visible_route_class")},
    )
    unknown_probe = subprocess.run(
        [sys.executable, str(CLI), "--surface", "unknown_atomic_card", "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    unknown_payload = json.loads(unknown_probe.stdout) if unknown_probe.stdout else {}
    check(
        "unknown_cli_stops",
        unknown_probe.returncode == 2
        and unknown_payload
        == {
            "status": "STOP_UNKNOWN_ATOMIC_FACTOR_SURFACE",
            "surface": "unknown_atomic_card",
            "known_surface_count": 24,
            "guard": "EXACT_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE",
        },
        {"returncode": unknown_probe.returncode, "payload": unknown_payload},
    )
    list_probe = subprocess.run(
        [sys.executable, str(CLI), "--list-surfaces"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    listed = list_probe.stdout.splitlines()
    check("cli_lists_exact_24", list_probe.returncode == 0 and set(listed) == set(card_map) and len(listed) == 24, len(listed))

    check("book_status", f"Status: `{STATUS}`" in book, STATUS)
    check("book_all_surface_inventory", all(f"`{surface}`" in book for surface in card_map), len(card_map))
    check("book_names_shso_default", "`SH>S`" in book and "`shso`" in book, "SH>S")

    generated = [CARD, COVER, SEAM, SPECIAL, AIIS, SUMMARY, BOOK, RESULT]
    before = {path.name: digest(path) for path in generated}
    rerun = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    after = {path.name: digest(path) for path in generated}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout[-1200:] + rerun.stderr[-1200:])
    check("generator_byte_determinism", before == after, after)

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
