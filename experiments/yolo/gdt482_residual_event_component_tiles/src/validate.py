#!/usr/bin/env python3
"""Validate GDT482's residual-event component atlas and tilings."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G481 = ROOT / "experiments/yolo/gdt481_microrecord_fragment_grammar/artifacts"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
BUNDLES_IN = G479 / "gdt479_146_definitive_local_bundles.tsv"
COVERAGE_IN = G481 / "gdt481_135_record_fragment_coverage.tsv"
SEQUENCES = OUT / "gdt482_183_event_component_sequences.tsv"
CONDITIONED_ATLAS = OUT / "gdt482_model_conditioned_component_fragment_atlas.tsv"
FREE_ATLAS = OUT / "gdt482_model_free_component_fragment_atlas.tsv"
TILES = OUT / "gdt482_45_residual_event_internal_tiles.tsv"
SEGMENTS = OUT / "gdt482_residual_tile_segments.tsv"
SUMMARY = OUT / "gdt482_residual_tile_summary.tsv"
READABLE = OUT / "GDT482_RESIDUAL_EVENT_COMPONENT_TILES.md"
RESULT = OUT / "gdt482_result.json"
VALIDATION = OUT / "gdt482_validation.json"
STATUS = "FORTY_TWO_OF_45_TILE_FROM_RECURRENT_COMPONENTS__TWO_LEARNED_SLOTS__ONE_FUNCTIONAL_OUTLIER"
CLASSES = (
    "FULL_RECURRENT_MULTI_FRAGMENT_TILE",
    "MIXED_RECURRENT_MULTI_PLUS_ATOMS",
    "RECURRENT_ATOMS_ONLY",
    "LOCAL_TOKEN_REMAINS",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_span(tokens: list[str], separators: list[str], start: int, length: int) -> str:
    pieces = [tokens[start]]
    for index in range(start, start + length - 1):
        pieces.extend((" · " if separators[index] == "DOT" else " / ", tokens[index + 1]))
    return "".join(pieces)


def expected_class(token_count: int, covered: int, multi: int) -> str:
    if covered < token_count:
        return "LOCAL_TOKEN_REMAINS"
    if multi == token_count:
        return "FULL_RECURRENT_MULTI_FRAGMENT_TILE"
    if multi:
        return "MIXED_RECURRENT_MULTI_PLUS_ATOMS"
    return "RECURRENT_ATOMS_ONLY"


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [SEQUENCES, CONDITIONED_ATLAS, FREE_ATLAS, TILES, SEGMENTS, SUMMARY, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT482 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    source_events = read_tsv(EVENTS_IN)
    source_bundles = read_tsv(BUNDLES_IN)
    coverage = read_tsv(COVERAGE_IN)
    sequences = read_tsv(SEQUENCES)
    conditioned_atlas = read_tsv(CONDITIONED_ATLAS)
    free_atlas = read_tsv(FREE_ATLAS)
    tiles = read_tsv(TILES)
    segments = read_tsv(SEGMENTS)
    summary = read_tsv(SUMMARY)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    event_map = {row["source_event_id"]: row for row in source_events}
    bundle_map = {row["bundle_id"]: row for row in source_bundles}
    sequence_map = {row["source_event_id"]: row for row in sequences}
    tile_map = {row["source_event_id"]: row for row in tiles}
    residual_records = {
        row["record_id"]
        for row in coverage
        if row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL" and row["event_count"] == "1"
    }
    expected_residual_ids = [
        row["source_event_id"] for row in source_events if row["record_id"] in residual_records
    ]

    check("source_event_count_183", len(source_events) == 183, len(source_events))
    check("source_bundle_count_146", len(source_bundles) == 146, len(source_bundles))
    check("source_coverage_count_135", len(coverage) == 135, len(coverage))
    check("gdt481_residual_record_count_45", len(residual_records) == 45, len(residual_records))
    check("sequence_count_183", len(sequences) == 183, len(sequences))
    check("conditioned_atlas_count_345", len(conditioned_atlas) == 345, len(conditioned_atlas))
    check("free_atlas_count_272", len(free_atlas) == 272, len(free_atlas))
    check("tile_count_45", len(tiles) == 45, len(tiles))
    check("segment_count_207", len(segments) == 207, len(segments))
    check("summary_count_8", len(summary) == 8, len(summary))
    check("sequence_ids_unique", len({row["sequence_id"] for row in sequences}) == 183)
    check("sequence_event_ids_unique", len(sequence_map) == 183)
    check("tile_ids_unique", len({row["tile_id"] for row in tiles}) == 45)
    check("tile_event_ids_unique", len(tile_map) == 45)
    check("segment_ids_unique", len({row["segment_id"] for row in segments}) == 207)
    check("conditioned_fragment_ids_unique", len({row["fragment_id"] for row in conditioned_atlas}) == 345)
    check("free_fragment_ids_unique", len({row["fragment_id"] for row in free_atlas}) == 272)
    check("conditioned_keys_unique", len({(row["active_model"], row["semantic_fragment"]) for row in conditioned_atlas}) == 345)
    check("free_keys_unique", len({row["semantic_fragment"] for row in free_atlas}) == 272)
    check("source_sequence_key_set_exact", set(sequence_map) == set(event_map))
    check("source_sequence_order_exact", [row["source_event_id"] for row in sequences] == [row["source_event_id"] for row in source_events])
    check("residual_tile_key_set_exact", set(tile_map) == set(expected_residual_ids))
    check("residual_tile_order_exact", [row["source_event_id"] for row in tiles] == expected_residual_ids)

    preserved_fields = (
        "record_id", "bundle_id", "physical_page", "register", "surface", "working_recipe",
        "literal_working_reading_de", "definitive_event_reading_de",
    )
    check(
        "sequence_source_fields_preserved",
        all(all(row[field] == event_map[row["source_event_id"]][field] for field in preserved_fields) for row in sequences),
    )
    check(
        "sequence_models_preserved",
        all(row["active_model"] == event_map[row["source_event_id"]]["active_model"] == bundle_map[row["bundle_id"]]["active_model"] for row in sequences),
    )
    check(
        "sequence_residual_flags_exact",
        all((row["is_gdt481_single_event_residual"] == "YES") == (row["source_event_id"] in expected_residual_ids) for row in sequences),
    )
    check("all_normalized_literals_nonempty", all(row["normalized_literal_de"] for row in sequences))
    check("raw_name_labels_removed", all(not re.search(r"\[(?:[A-ZÄÖÜ_]*NAME):", row["normalized_literal_de"]) for row in sequences))
    check("all_sequences_tokenized", all(int(row["token_count"]) == len(row["semantic_tokens"].split("|")) for row in sequences))
    check(
        "separator_counts_exact",
        all((0 if row["semantic_separators"] == "NONE" else len(row["semantic_separators"].split("|"))) == int(row["token_count"]) - 1 for row in sequences),
    )
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in sequences + tiles))

    conditioned_support: dict[tuple[str, str], list[str]] = defaultdict(list)
    free_support: dict[str, list[str]] = defaultdict(list)
    for row in sequences:
        tokens = row["semantic_tokens"].split("|")
        separators = [] if row["semantic_separators"] == "NONE" else row["semantic_separators"].split("|")
        for start in range(len(tokens)):
            for length in range(1, min(3, len(tokens) - start) + 1):
                fragment = semantic_span(tokens, separators, start, length)
                conditioned_support[(row["active_model"], fragment)].append(row["source_event_id"])
                free_support[fragment].append(row["source_event_id"])
    conditioned_rows = {(row["active_model"], row["semantic_fragment"]): row for row in conditioned_atlas}
    free_rows = {row["semantic_fragment"]: row for row in free_atlas}
    check("conditioned_atlas_key_set_exact", set(conditioned_rows) == set(conditioned_support))
    check("free_atlas_key_set_exact", set(free_rows) == set(free_support))

    def atlas_support_exact(row: dict[str, str], event_ids: list[str]) -> bool:
        unique = set(event_ids)
        return (
            int(row["occurrence_count"]) == len(event_ids)
            and int(row["event_count"]) == len(unique)
            and int(row["page_count"]) == len({sequence_map[event_id]["physical_page"] for event_id in unique})
            and int(row["register_count"]) == len({sequence_map[event_id]["register"] for event_id in unique})
            and int(row["model_count"]) == len({sequence_map[event_id]["active_model"] for event_id in unique})
            and int(row["surface_type_count"]) == len({sequence_map[event_id]["surface"] for event_id in unique})
            and set(row["event_ids"].split("|")) == unique
        )

    check("conditioned_atlas_support_exact", all(atlas_support_exact(conditioned_rows[key], ids) for key, ids in conditioned_support.items()))
    check("free_atlas_support_exact", all(atlas_support_exact(free_rows[key], ids) for key, ids in free_support.items()))
    check("conditioned_models_bounded", {row["active_model"] for row in conditioned_atlas} == {"COORDINATE", "INSTRUCTION", "CATALOGUE"})
    check("free_model_is_any", all(row["active_model"] == "ANY" for row in free_atlas))
    check("fragment_lengths_bounded", all(1 <= int(row["component_length"]) <= 3 for row in conditioned_atlas + free_atlas))
    check("atlas_claims_bounded", all(row["claim_status"] == "OBSERVED_COMPONENT_FRAGMENT__NO_NEW_MEANING" for row in conditioned_atlas + free_atlas))
    check("conditioned_recurrent_fragment_count_126", sum(int(row["event_count"]) > 1 for row in conditioned_atlas) == 126)
    check("free_recurrent_fragment_count_114", sum(int(row["event_count"]) > 1 for row in free_atlas) == 114)

    tile_fields = ("record_id", "bundle_id", "physical_page", "register", "active_model", "surface", "working_recipe", "definitive_event_reading_de")
    check("tile_source_fields_preserved", all(all(row[field] == sequence_map[row["source_event_id"]][field] for field in tile_fields) for row in tiles))
    check("all_source_meanings_preserved", all(row["all_source_meanings_preserved"] == "YES" for row in tiles))
    check("tile_token_counts_exact", all(int(row["token_count"]) == int(sequence_map[row["source_event_id"]]["token_count"]) for row in tiles))
    check("tile_name_slot_counts_exact", all(int(row["name_slot_count"]) == sum(token.startswith("{N") for token in sequence_map[row["source_event_id"]]["semantic_tokens"].split("|")) for row in tiles))

    grouped_segments: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in segments:
        grouped_segments[(row["source_event_id"], row["tile_mode"])].append(row)
    check("both_tile_modes_present", set(grouped_segments) == {(event_id, mode) for event_id in expected_residual_ids for mode in ("MODEL_CONDITIONED", "MODEL_FREE_BACKOFF")})
    check("segment_event_ids_resolve", all(row["source_event_id"] in tile_map for row in segments))
    check("segment_modes_bounded", {row["tile_mode"] for row in segments} == {"MODEL_CONDITIONED", "MODEL_FREE_BACKOFF"})
    check("segment_lengths_bounded", all(1 <= int(row["component_length"]) <= 3 for row in segments))
    check("local_segments_are_atoms", all(row["recurrent_in_other_event"] == "YES" or int(row["component_length"]) == 1 for row in segments))
    check("donors_exclude_target", all(row["source_event_id"] not in row["donor_event_ids"].split("|") for row in segments))
    check("all_donors_resolve", all(row["donor_event_ids"] == "NONE" or all(event_id in sequence_map for event_id in row["donor_event_ids"].split("|")) for row in segments))
    check("recurrent_flags_match_donor_counts", all((row["recurrent_in_other_event"] == "YES") == (int(row["donor_event_count"]) > 0) for row in segments))
    check("donor_counts_match_lists", all(int(row["donor_event_count"]) == (0 if row["donor_event_ids"] == "NONE" else len(row["donor_event_ids"].split("|"))) for row in segments))
    check("name_slot_flags_exact", all((row["contains_name_slot"] == "YES") == bool(re.search(r"\{(?:N|F)\d+\}", row["semantic_fragment"])) for row in segments))

    segmentation_ok = True
    donor_support_ok = True
    donor_metadata_ok = True
    row_metrics_ok = True
    for tile in tiles:
        event_id = tile["source_event_id"]
        sequence = sequence_map[event_id]
        tokens = sequence["semantic_tokens"].split("|")
        separators = [] if sequence["semantic_separators"] == "NONE" else sequence["semantic_separators"].split("|")
        for mode, prefix, support_store in (
            ("MODEL_CONDITIONED", "conditioned", conditioned_support),
            ("MODEL_FREE_BACKOFF", "free", free_support),
        ):
            rows = grouped_segments[(event_id, mode)]
            rows.sort(key=lambda row: int(row["segment_ordinal"]))
            position = covered = multi = 0
            local_tokens: list[str] = []
            for ordinal, segment in enumerate(rows, 1):
                length = int(segment["component_length"])
                expected_fragment = semantic_span(tokens, separators, position, length)
                segmentation_ok &= (
                    int(segment["segment_ordinal"]) == ordinal
                    and int(segment["start_component_ordinal"]) == position + 1
                    and segment["semantic_fragment"] == expected_fragment
                )
                key: object = (sequence["active_model"], expected_fragment) if mode == "MODEL_CONDITIONED" else expected_fragment
                expected_donors = sorted(set(support_store[key]) - {event_id})
                actual_donors = [] if segment["donor_event_ids"] == "NONE" else segment["donor_event_ids"].split("|")
                donor_support_ok &= actual_donors == expected_donors
                donor_rows = [sequence_map[donor] for donor in expected_donors]
                donor_metadata_ok &= (
                    int(segment["donor_page_count"]) == len({row["physical_page"] for row in donor_rows})
                    and int(segment["donor_register_count"]) == len({row["register"] for row in donor_rows})
                    and (segment["donor_surface_examples"] == "NONE" if not donor_rows else bool(segment["donor_surface_examples"]))
                )
                if expected_donors:
                    covered += length
                    if length > 1:
                        multi += length
                else:
                    local_tokens.append(expected_fragment)
                position += length
            segmentation_ok &= position == len(tokens)
            expected_local = "|".join(local_tokens) or "NONE"
            row_metrics_ok &= (
                int(tile[f"{prefix}_segment_count"]) == len(rows)
                and int(tile[f"{prefix}_recurrent_token_count"]) == covered
                and int(tile[f"{prefix}_multi_fragment_token_count"]) == multi
                and int(tile[f"{prefix}_local_token_count"]) == len(local_tokens)
                and tile[f"{prefix}_local_tokens"] == expected_local
                and tile[f"{prefix}_tile_class"] == expected_class(len(tokens), covered, multi)
            )
    check("segmentations_are_contiguous_and_exact", segmentation_ok)
    check("segment_donor_support_exact", donor_support_ok)
    check("segment_donor_metadata_exact", donor_metadata_ok)
    check("tile_metrics_reconstructed", row_metrics_ok)
    check("conditioned_donors_same_model", all(row["tile_mode"] != "MODEL_CONDITIONED" or row["donor_event_ids"] == "NONE" or all(sequence_map[event_id]["active_model"] == tile_map[row["source_event_id"]]["active_model"] for event_id in row["donor_event_ids"].split("|")) for row in segments))
    check("free_coverage_never_worse", all(int(row["free_recurrent_token_count"]) >= int(row["conditioned_recurrent_token_count"]) for row in tiles))

    conditioned_classes = Counter(row["conditioned_tile_class"] for row in tiles)
    free_classes = Counter(row["free_tile_class"] for row in tiles)
    interpretations = Counter(row["residual_interpretation"] for row in tiles)
    check("conditioned_class_profile_exact", conditioned_classes == Counter({CLASSES[0]: 14, CLASSES[1]: 21, CLASSES[2]: 4, CLASSES[3]: 6}), conditioned_classes)
    check("free_class_profile_exact", free_classes == Counter({CLASSES[0]: 18, CLASSES[1]: 21, CLASSES[2]: 3, CLASSES[3]: 3}), free_classes)
    check("interpretation_profile_exact", interpretations == Counter({"MODEL_CONDITIONED_RECURRENT": 39, "MODEL_FREE_RECURRENT_BACKOFF": 3, "LEARNED_LEXICAL_SLOT_ONLY": 2, "UNIQUE_FUNCTIONAL_COMPONENT_REMAINS": 1}), interpretations)
    check("conditioned_token_profile_exact", (sum(int(row["token_count"]) for row in tiles), sum(int(row["conditioned_recurrent_token_count"]) for row in tiles), sum(int(row["conditioned_multi_fragment_token_count"]) for row in tiles)) == (160, 152, 95))
    check("free_recurrent_token_count_156", sum(int(row["free_recurrent_token_count"]) for row in tiles) == 156)
    check("conditioned_multi_event_count_36", sum(int(row["conditioned_multi_fragment_token_count"]) > 0 for row in tiles) == 36)
    check("model_free_coverage_upgrades_3", sum(int(row["model_free_coverage_upgrade"]) > 0 for row in tiles) == 3)
    check("model_free_multi_upgrades_10", sum(int(row["model_free_multi_fragment_upgrade"]) > 0 for row in tiles) == 10)
    check("name_slot_event_count_29", sum(int(row["name_slot_count"]) > 0 for row in tiles) == 29)

    conditioned_local_ids = {row["source_event_id"] for row in tiles if row["conditioned_tile_class"] == "LOCAL_TOKEN_REMAINS"}
    free_local_ids = {row["source_event_id"] for row in tiles if row["free_tile_class"] == "LOCAL_TOKEN_REMAINS"}
    learned_ids = {row["source_event_id"] for row in tiles if row["residual_interpretation"] == "LEARNED_LEXICAL_SLOT_ONLY"}
    functional_ids = {row["source_event_id"] for row in tiles if row["residual_interpretation"] == "UNIQUE_FUNCTIONAL_COMPONENT_REMAINS"}
    check("conditioned_local_ids_exact", conditioned_local_ids == {"P1008-E0412", "P1003-E0083", "P1003-E0460", "P1008-E1182", "P1008-E1233", "P1008-E1297"}, sorted(conditioned_local_ids))
    check("free_local_ids_exact", free_local_ids == {"P1003-E0460", "P1008-E1182", "P1008-E1297"}, sorted(free_local_ids))
    check("learned_slot_ids_exact", learned_ids == {"P1003-E0460", "P1008-E1182"}, sorted(learned_ids))
    check("functional_outlier_exact", functional_ids == {"P1008-E1297"} and tile_map["P1008-E1297"]["free_local_tokens"] == "ZWEITE STUFE|MARKIEREN", tile_map["P1008-E1297"])
    check("learned_slots_are_only_name_types", all(all(re.fullmatch(r"(?:\{N\d+\}|\{F\d+\}:NAMENSFAMILIE)", token) for token in row["free_local_tokens"].split("|")) for row in tiles if row["residual_interpretation"] == "LEARNED_LEXICAL_SLOT_ONLY"))

    actual_summary = {(row["tile_mode"], row["tile_class"]): int(row["event_count"]) for row in summary}
    expected_summary = {
        **{("MODEL_CONDITIONED", klass): conditioned_classes[klass] for klass in CLASSES},
        **{("MODEL_FREE_BACKOFF", klass): free_classes[klass] for klass in CLASSES},
    }
    check(
        "summary_counts_exact",
        actual_summary == expected_summary,
        {f"{mode}:{klass}": count for (mode, klass), count in actual_summary.items()},
    )
    summary_ids_ok = True
    for row in summary:
        field = "conditioned_tile_class" if row["tile_mode"] == "MODEL_CONDITIONED" else "free_tile_class"
        expected_ids = {tile["source_event_id"] for tile in tiles if tile[field] == row["tile_class"]}
        actual_ids = set() if row["event_ids"] == "NONE" else set(row["event_ids"].split("|"))
        summary_ids_ok &= actual_ids == expected_ids
    check("summary_event_ids_exact", summary_ids_ok)

    check("readable_contains_all_tiles", all(event_id in readable for event_id in expected_residual_ids))
    check("readable_preserves_default_warning", "nicht bedeutungslos" in readable and "Defaultbedeutungen" in readable)
    check("readable_names_not_identities", "nicht die Identität des Namens" in readable)
    check("readable_reports_core_counts", all(term in readable for term in ("39/45", "42/45", "`sodar`", "`ZWEITE STUFE`", "`MARKIEREN`")))

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_source_counts_exact", (result.get("source_event_count"), result.get("residual_event_count")) == (183, 45))
    check("result_atlas_counts_exact", (result.get("conditioned_fragment_atlas_count"), result.get("free_fragment_atlas_count"), result.get("conditioned_recurrent_fragment_count"), result.get("free_recurrent_fragment_count")) == (345, 272, 126, 114))
    check("result_conditioned_classes_exact", (result.get("conditioned_full_multi_tile_count"), result.get("conditioned_mixed_multi_atom_tile_count"), result.get("conditioned_atom_only_tile_count"), result.get("conditioned_local_token_remains_count"), result.get("conditioned_all_tokens_covered_count")) == (14, 21, 4, 6, 39))
    check("result_free_classes_exact", (result.get("free_full_multi_tile_count"), result.get("free_mixed_multi_atom_tile_count"), result.get("free_atom_only_tile_count"), result.get("free_local_token_remains_count"), result.get("free_all_tokens_covered_count")) == (18, 21, 3, 3, 42))
    check("result_interpretation_exact", (result.get("model_conditioned_recurrent_event_count"), result.get("model_free_recurrent_backoff_event_count"), result.get("learned_lexical_slot_only_count"), result.get("unique_functional_component_event_count")) == (39, 3, 2, 1))
    check("result_local_ids_exact", set(result.get("conditioned_local_token_event_ids", [])) == conditioned_local_ids and set(result.get("free_local_token_event_ids", [])) == free_local_ids)
    check("result_special_ids_exact", set(result.get("learned_slot_only_event_ids", [])) == learned_ids and set(result.get("unique_functional_event_ids", [])) == functional_ids)
    check("result_functional_tokens_exact", result.get("unique_functional_tokens") == ["MARKIEREN", "ZWEITE STUFE"])
    unchanged = ("component_meaning_change_count", "active_model_change_count", "surface_change_count", "recipe_change_count", "event_change_count", "new_page_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "no new meaning" in result.get("claim_ceiling", ""))

    failed = [row for row in checks if not row["pass"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [row["name"] for row in failed],
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
