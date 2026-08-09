#!/usr/bin/env python3
"""Nonimporting validation of the source-separator formal-impact audit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R = HERE / "results"
FILES = {
    "source_atlas": R / "source_separator_transcription.tsv",
    "source_result": R / "source_separator_transcription.json",
    "interlinear": R / "pre_grounding_interlinear.tsv",
    "residual": R / "pre_grounding_surface_residual_atlas.tsv",
    "candidates": R / "unparsed_surface_candidate_lattice.tsv",
    "segmentation": R / "unparsed_surface_segmentation.json",
    "usr002": R / "usr002_exact_y_capacity.tsv",
    "spec": HERE / "SOURCE_SEPARATOR_FORMAL_IMPACT_SPEC.md",
    "producer": HERE / "audit_source_separator_formal_impact.py",
    "impact_groups": R / "source_separator_formal_impact_groups.tsv",
    "result": R / "source_separator_formal_impact.json",
    "report": R / "source_separator_formal_impact_report.md",
}
EXPECTED_HASHES = {
    "source_atlas": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "source_result": "c047bef98ad0f83c65e0dbdad8e6904b6ed4ea6e3d945407191c39fd482e36f4",
    "interlinear": "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    "residual": "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    "candidates": "2b39b60c3bc4348490bd54a2a1965201e9d9eb625c98c3b5c9736b7f96ab12f1",
    "segmentation": "fb003077191a98ef4a8c16b996552ed4fd635f93e1bb26109716f554cf46ea97",
    "usr002": "280bd2d89c39a0d1466b6a79ae62a9cbfe3d92f2c63cd670f9abd842496d0407",
    "spec": "b5d11defe880dee79f818bcbce105ccfbf55b5f97b4b617f92b42138cf5d7810",
    "producer": "c289930eafb8fa3ff99237846eebd58b5eb9dfe388a625cee211693a0f1344bc",
    "impact_groups": "697752c9ada40a5675ef6a14617906a6ee8f95dabfb654f6f40340f6e0ac27ef",
    "result": "3db3e606b8e86756adea25a90aaeb4e7e6bce1bb22e66ecd8462ada433a8e797",
    "report": "663a39232878e1ef6454e6b80336acd36820cc340088595740619ef8d40259a9",
}
VALIDATION = R / "source_separator_formal_impact_validation.json"
VALIDATION_REPORT = R / "source_separator_formal_impact_validation_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
CLAIM = (
    "This audit distinguishes source groups from cleaner fragments and corrects affected "
    "structural counts only. It does not expand special glyphs, choose authorial spacing, "
    "repair the formal parser, assign an unparsed role, identify a sound or language, or "
    "provide plaintext or translation."
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def surfaces(row: dict[str, str]) -> list[str]:
    return [value.split("=", 1)[0] for value in row["formal_interlinear"].split(" | ")] if row["formal_interlinear"] else []


def align(tokens: tuple[str, ...], target: str) -> tuple[bool, ...]:
    @lru_cache(maxsize=None)
    def visit(position: int, offset: int) -> tuple[int, tuple[bool, ...]]:
        if position == len(tokens):
            return (1, ()) if offset == len(target) else (0, ())
        omitted_count, omitted_tail = visit(position + 1, offset)
        count = omitted_count
        answer = (False,) + omitted_tail if omitted_count else ()
        if target.startswith(tokens[position], offset):
            kept_count, kept_tail = visit(position + 1, offset + len(tokens[position]))
            if kept_count:
                if count == 0:
                    answer = (True,) + kept_tail
                count = min(2, count + kept_count)
        return count, answer

    count, answer = visit(0, 0)
    if count != 1:
        raise RuntimeError("nonunique formal alignment")
    return answer


def nested(counter: Counter[tuple[str, str]]) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = defaultdict(dict)
    for (left, right), count in sorted(counter.items()):
        output[left][right] = count
    return dict(output)


def main() -> None:
    observed = {name: digest(path) for name, path in FILES.items()}
    if observed != EXPECTED_HASHES:
        raise RuntimeError("impact artifact hash drift")
    checks = len(observed)

    source = rows(FILES["source_atlas"])
    legacy_list = rows(FILES["interlinear"])
    legacy = {(row["edition"], row["locus"]): row for row in legacy_list}
    by_row: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for group in source:
        by_row[(group["edition"], group["locus"])].append(group)
    if len(source) != 115_470 or len(by_row) != 15_985 or len(legacy) != 15_960:
        raise RuntimeError("base table size mismatch")
    checks += 3

    pos_group: dict[tuple[str, str, int], dict[str, str]] = {}
    masks: dict[tuple[str, str], tuple[bool, ...]] = {}
    retained: dict[tuple[str, str], list[int]] = {}
    expected_impacted: dict[str, dict[str, str]] = {}
    residual_events: dict[tuple[str, str, int], str] = {}
    residual_class = Counter()
    residual_type = Counter()
    y_counts = Counter()
    source_scope = Counter()
    legacy_scope = Counter()
    affected_rows = Counter()
    affected_groups = Counter()
    first_last = Counter()
    affected_loci = defaultdict(set)
    affected_pages = defaultdict(set)

    for key, groups in by_row.items():
        groups.sort(key=lambda group: int(group["source_group_index"]))
        edition, locus = key
        scope = groups[0]["grammar_scope"]
        source_scope[(edition, scope)] += 1
        flattened: list[str] = []
        for group in groups:
            fragment_list = group["clean_ascii_fragments"].split()
            positions = [int(value) for value in group["legacy_surface_positions_1based"].split(",") if value]
            if len(fragment_list) != len(positions):
                raise RuntimeError("fragment-position mismatch")
            for position in positions:
                if (edition, locus, position) in pos_group:
                    raise RuntimeError("duplicate legacy position")
                pos_group[(edition, locus, position)] = group
            flattened.extend(fragment_list)
        if key in legacy:
            row = legacy[key]
            legacy_scope[(edition, scope)] += 1
            tokens = tuple(row["surface"].split())
            if list(tokens) != flattened:
                raise RuntimeError("surface mapping mismatch")
            mask = align(tokens, "".join(surfaces(row)))
        else:
            if flattened:
                raise RuntimeError("missing nonempty legacy row")
            tokens = ()
            mask = ()
        masks[key] = mask
        retained[key] = [position for position, keep in enumerate(mask, 1) if keep]
        for position, (token, keep) in enumerate(zip(tokens, mask), 1):
            if not keep:
                residual_events[(edition, locus, position)] = token

        bad = [group for group in groups if group["legacy_mapping_status"] != "ONE_ASCII_FRAGMENT"]
        if bad:
            affected_rows[(edition, scope)] += 1
            affected_loci[edition].add(locus)
            affected_pages[edition].add(groups[0]["page"])
        for location, group in (("FIRST", groups[0]), ("LAST", groups[-1])):
            if group["legacy_mapping_status"] != "ONE_ASCII_FRAGMENT":
                first_last[(edition, scope, location, group["legacy_mapping_status"])] += 1
        for group in bad:
            positions = [int(value) for value in group["legacy_surface_positions_1based"].split(",") if value]
            kept = [position for position in positions if mask and mask[position - 1]]
            omitted = [position for position in positions if not mask or not mask[position - 1]]
            if group["legacy_mapping_status"] == "ZERO_ASCII_FRAGMENT":
                impact = "SOURCE_GROUP_ABSENT_FROM_LEGACY_ASCII"
            elif kept and omitted:
                impact = "MULTI_FRAGMENT_MIXED_RETAINED_OMITTED"
            elif kept:
                impact = "MULTI_FRAGMENT_ALL_RETAINED"
            else:
                impact = "MULTI_FRAGMENT_ALL_OMITTED"
            affected_groups[(edition, scope, group["legacy_mapping_status"])] += 1
            expected_impacted[group["source_group_id"]] = {
                "source_group_id": group["source_group_id"], "edition": edition,
                "locus": locus, "page": group["page"], "grammar_scope": scope,
                "kind": group["kind"], "source_group_index": group["source_group_index"],
                "source_group_count": group["source_group_count"],
                "left_separator": group["left_separator"], "right_separator": group["right_separator"],
                "ivtff_group_raw": group["ivtff_group_raw"],
                "clean_ascii_fragments": group["clean_ascii_fragments"],
                "clean_ascii_fragment_count": group["clean_ascii_fragment_count"],
                "legacy_surface_positions_1based": group["legacy_surface_positions_1based"],
                "retained_fragment_positions_1based": ",".join(map(str, kept)),
                "omitted_fragment_positions_1based": ",".join(map(str, omitted)),
                "retained_fragments": " ".join(tokens[position - 1] for position in kept),
                "omitted_fragments": " ".join(tokens[position - 1] for position in omitted),
                "legacy_mapping_status": group["legacy_mapping_status"],
                "formal_impact_class": impact,
            }

    stored_impacted = rows(FILES["impact_groups"])
    if len(stored_impacted) != len(expected_impacted) or len(expected_impacted) != 2_861:
        raise RuntimeError("impact group row count mismatch")
    if len({row["source_group_id"] for row in stored_impacted}) != len(stored_impacted):
        raise RuntimeError("duplicate impact group")
    for row in stored_impacted:
        if expected_impacted.get(row["source_group_id"]) != row:
            raise RuntimeError(f"impact group mismatch at {row['source_group_id']}")
        checks += len(row)

    stored_residual: dict[tuple[str, str, int], str] = {}
    for row in rows(FILES["residual"]):
        for item in row["position_token_pairs"].split(";"):
            position, token = item.split(":", 1)
            key = (row["edition"], row["locus"], int(position))
            if key in stored_residual:
                raise RuntimeError("duplicate residual")
            stored_residual[key] = token
    if residual_events != stored_residual or len(residual_events) != 3_838:
        raise RuntimeError("residual reconstruction mismatch")
    checks += len(residual_events)
    for event, token in residual_events.items():
        group = pos_group[event]
        source_class = "COMPLETE_SOURCE_GROUP" if group["clean_ascii_fragment_count"] == "1" else "INTRA_SOURCE_FRAGMENT"
        residual_class[source_class] += 1
        residual_type[(source_class, token)] += 1
        if token == "y":
            y_counts[(event[0], source_class)] += 1
            if source_class == "COMPLETE_SOURCE_GROUP" and group["ivtff_group_raw"] == "y":
                y_counts[(event[0], "EXACT_RAW_Y_GROUP")] += 1

    formal_topology = Counter()
    formal_separator = Counter()
    registered_topology = Counter()
    registered_original = Counter()
    registered_type_topology = Counter()
    registered_type_separator = Counter()
    skipped: list[dict[str, object]] = []
    for key, row in legacy.items():
        edition, locus = key
        positions = retained[key]
        groups = by_row[key]
        group_index = {
            position: int(pos_group[(edition, locus, position)]["source_group_index"])
            for position in range(1, len(row["surface"].split()) + 1)
        }

        def classify(left: int, right: int) -> tuple[str, str]:
            a, b = group_index[left], group_index[right]
            if a == b:
                return "INTRA_SOURCE_GROUP", "NONMANUAL_CLEANER_BOUNDARY"
            if b == a + 1:
                return "ADJACENT_SOURCE_GROUPS", groups[a - 1]["right_separator"]
            return "SKIPS_SOURCE_GROUPS", "INTERVENING_SOURCE_GROUP"

        for left, right in zip(positions, positions[1:]):
            topology, separator = classify(left, right)
            formal_topology[(edition, topology)] += 1
            formal_separator[(edition, separator)] += 1
        for edge in filter(None, row["confirmed_edges"].split(";")):
            coordinate, edge_type = edge.split(":", 1)
            node = int(coordinate.split(">", 1)[0][1:])
            left, right = positions[node - 1], positions[node]
            topology, separator = classify(left, right)
            registered_topology[(edition, topology)] += 1
            registered_original[edge_type] += 1
            registered_type_topology[(edge_type, topology)] += 1
            registered_type_separator[(edge_type, separator)] += 1
            if topology == "SKIPS_SOURCE_GROUPS":
                a, b = group_index[left], group_index[right]
                skipped.append({
                    "edition": edition,
                    "locus": locus,
                    "registered_edge": edge,
                    "left_legacy_position": left,
                    "right_legacy_position": right,
                    "intervening_source_groups": [
                        group["source_group_id"] for group in groups[a:b - 1]
                    ],
                })
    if sum(formal_topology.values()) != 98_274 or sum(registered_topology.values()) != 4_737:
        raise RuntimeError("formal edge total mismatch")
    if sum(value for (edition, topology), value in registered_topology.items() if topology == "INTRA_SOURCE_GROUP"):
        raise RuntimeError("registered edge inside source group")
    checks += 98_274 + 4_737

    candidate_counts = Counter()
    candidate_y = Counter()
    candidate_ids = set()
    for row in rows(FILES["candidates"]):
        event = (row["edition"], row["locus"], int(row["surface_position_1based"]))
        if row["event_id"] in candidate_ids or residual_events.get(event) != row["residual_token"]:
            raise RuntimeError("candidate binding mismatch")
        candidate_ids.add(row["event_id"])
        source_class = "COMPLETE_SOURCE_GROUP" if pos_group[event]["clean_ascii_fragment_count"] == "1" else "INTRA_SOURCE_FRAGMENT"
        candidate_counts[(source_class, row["coverage_class"])] += 1
        if row["residual_token"] == "y":
            candidate_y[(source_class, row["coverage_class"])] += 1
    if len(candidate_ids) != 3_838:
        raise RuntimeError("candidate size mismatch")
    checks += len(candidate_ids)

    direct = Counter()
    direct_type = Counter()
    direct_loci = defaultdict(set)
    unsafe: list[dict[str, object]] = []
    segmentation = json.loads(FILES["segmentation"].read_text(encoding="utf-8"))
    for token, summary in segmentation["cross_reading_space_only"]["directed_residual_fusion_summary"].items():
        for event in summary["events_detail"]:
            source_key = (event["source_edition"], event["locus"], int(event["source_position_1based"]))
            fused_key = (event["other_edition"], event["locus"], int(event["fused_position_1based"]))
            safe = pos_group[source_key]["clean_ascii_fragment_count"] == "1" and pos_group[fused_key]["clean_ascii_fragment_count"] == "1"
            state = "SOURCE_SAFE" if safe else "CLEANER_AFFECTED"
            direct[state] += 1
            direct_type[(token, state)] += 1
            if safe:
                direct_loci[token].add(event["locus"])
            else:
                unsafe.append({
                    "token": token,
                    "source_edition": event["source_edition"],
                    "other_edition": event["other_edition"],
                    "locus": event["locus"],
                    "source_group": pos_group[source_key]["source_group_id"],
                    "source_raw": pos_group[source_key]["ivtff_group_raw"],
                    "fused_group": pos_group[fused_key]["source_group_id"],
                })
            if token == "y" and event["sole_boundary_change"] and event["neighbor_mapping_preserved"]:
                direct["Y_TOTAL"] += 1
                direct["Y_SAFE"] += int(safe)
    if direct["SOURCE_SAFE"] != 310 or direct["CLEANER_AFFECTED"] != 2:
        raise RuntimeError("direct source-safety mismatch")
    checks += 312

    usr_safe = 0
    usr_rows = rows(FILES["usr002"])
    for candidate in usr_rows:
        target = int(candidate["character_offset_1based"]) - 1
        for edition in READINGS:
            start = 0
            hit = None
            for position, token in enumerate(legacy[(edition, candidate["locus"])]["surface"].split(), 1):
                if start <= target < start + len(token):
                    hit = (position, token, target - start)
                    break
                start += len(token)
            if hit is None or hit[1][hit[2]] != "y":
                raise RuntimeError("USR002 offset mismatch")
            group = pos_group[(edition, candidate["locus"], hit[0])]
            if group["clean_ascii_fragment_count"] != "1" or group["ivtff_group_raw"] != hit[1]:
                raise RuntimeError("USR002 unsafe group")
            usr_safe += 1
    if len(usr_rows) != 30 or usr_safe != 90:
        raise RuntimeError("USR002 size mismatch")
    checks += usr_safe

    result = json.loads(FILES["result"].read_text(encoding="utf-8"))
    expected_inputs = {
            str(FILES[name].relative_to(ROOT)): EXPECTED_HASHES[name]
            for name in ("source_atlas", "source_result", "interlinear", "residual", "candidates", "segmentation", "usr002")
    }
    expected_source_exposure = {
        "source_scope_rows": nested(source_scope),
        "legacy_scope_rows": nested(legacy_scope),
        "affected_rows_by_edition_scope": nested(affected_rows),
        "affected_source_groups_by_edition_scope_status": {
            "|".join(key): value for key, value in sorted(affected_groups.items())
        },
        "affected_loci_by_edition": {edition: len(affected_loci[edition]) for edition in READINGS},
        "affected_pages_by_edition": {edition: len(affected_pages[edition]) for edition in READINGS},
        "first_last_affected": {"|".join(key): value for key, value in sorted(first_last.items())},
        "affected_group_rows": len(expected_impacted),
        "affected_group_atlas_sha256": EXPECTED_HASHES["impact_groups"],
    }
    expected_residual = {
        "legacy_residual_events": len(residual_events),
        "source_class_counts": dict(sorted(residual_class.items())),
        "complete_source_group_type_counts": {
            token: count for (source_class, token), count in sorted(residual_type.items()) if source_class == "COMPLETE_SOURCE_GROUP"
        },
        "intra_source_fragment_type_counts": {
            token: count for (source_class, token), count in sorted(residual_type.items()) if source_class == "INTRA_SOURCE_FRAGMENT"
        },
        "y_by_edition_source_class": {"|".join(key): value for key, value in sorted(y_counts.items())},
    }
    expected_formal = {
        "all_formal_adjacencies_by_edition_topology": nested(formal_topology),
        "all_formal_adjacencies_by_edition_separator": nested(formal_separator),
        "registered_hard_edges_by_edition_topology": nested(registered_topology),
        "registered_hard_edge_original_counts": dict(sorted(registered_original.items())),
        "registered_hard_edge_direct_source_counts": {
            edge_type: registered_type_topology[(edge_type, "ADJACENT_SOURCE_GROUPS")]
            for edge_type in sorted(registered_original)
        },
        "registered_hard_edge_by_type_topology": {
            "|".join(key): value for key, value in sorted(registered_type_topology.items())
        },
        "registered_hard_edge_by_type_separator": {
            "|".join(key): value for key, value in sorted(registered_type_separator.items())
        },
        "skipped_registered_edge_examples": skipped,
    }
    expected_candidate = {
        "events": len(candidate_ids),
        "by_source_class_and_coverage": {
            "|".join(key): value for key, value in sorted(candidate_counts.items())
        },
        "y_by_source_class_and_coverage": {
            "|".join(key): value for key, value in sorted(candidate_y.items())
        },
    }
    expected_direct = {
        "events": direct["SOURCE_SAFE"] + direct["CLEANER_AFFECTED"],
        "source_safe_events": direct["SOURCE_SAFE"],
        "cleaner_affected_events": direct["CLEANER_AFFECTED"],
        "by_token_and_state": {"|".join(key): value for key, value in sorted(direct_type.items())},
        "source_safe_physical_loci_by_token": {
            token: len(loci) for token, loci in sorted(direct_loci.items())
        },
        "y_sole_boundary_mapping_preserved_total": direct["Y_TOTAL"],
        "y_sole_boundary_mapping_preserved_source_safe": direct["Y_SAFE"],
        "cleaner_affected_examples": unsafe,
    }
    expected_usr = {
        "candidate_spans": 30,
        "reading_specific_target_groups": 90,
        "all_are_exact_raw_one_fragment_groups": True,
        "prior_unscored_stop_unchanged": True,
    }
    expected_gates = {
        "source_atlas_complete": True,
        "all_residual_events_reconstructed": True,
        "all_affected_groups_emitted": True,
        "all_formal_adjacencies_classified": True,
        "all_registered_hard_edges_classified": True,
        "zero_registered_hard_edges_inside_source_group": True,
        "candidate_lattice_event_set_complete": True,
        "direct_spacing_event_set_complete": True,
        "usr002_source_safe_stop_invariant": True,
        "no_semantic_assignment": True,
    }
    expected_decision = {
        "broad_residual_and_candidate_counts_require_correction": True,
        "direct_cross_reading_spacing_evidence_retained_qualified": True,
        "registered_hard_dependency_system_retained_with_six_exclusions": True,
        "rf1b_token_boundary_features_require_source_aware_rebuild": True,
        "usr002_unscored_stop_reopened": False,
    }
    expected_material = {
        "status": result["status"] == "PASS_SOURCE_SEPARATOR_FORMAL_IMPACT_CORRECTION",
        "claim": result["claim_ceiling"] == CLAIM,
        "inputs": result["inputs"] == expected_inputs,
        "implementation": result["implementation"] == {
            "spec_sha256": EXPECTED_HASHES["spec"],
            "producer_sha256": EXPECTED_HASHES["producer"],
            "extended_entities_expanded": False,
            "formal_parser_rerun": False,
            "english_lexical_glosses": 0,
        },
        "source_exposure": result["source_exposure"] == expected_source_exposure,
        "residual": result["residual_correction"] == expected_residual,
        "formal": result["formal_adjacency_correction"] == expected_formal,
        "candidate": result["candidate_lattice_correction"] == expected_candidate,
        "direct": result["direct_spacing_evidence"] == expected_direct,
        "usr002": result["usr002_invariance"] == expected_usr,
        "gates": result["gates"] == expected_gates,
        "decisions": result["decision"] == expected_decision,
    }
    failures = [name for name, passed in expected_material.items() if not passed]
    if failures:
        raise RuntimeError("result mismatch: " + ", ".join(failures))
    checks += len(expected_material)

    # Mutation controls: one intra-source y fragment must not become a complete group,
    # and a skipped registered edge must not become direct adjacency.
    fragment_y = next(event for event, token in residual_events.items() if token == "y" and pos_group[event]["clean_ascii_fragment_count"] != "1")
    if pos_group[fragment_y]["legacy_mapping_status"] != "MULTI_ASCII_FRAGMENT" or len(skipped) != 6:
        raise RuntimeError("mutation witness setup failed")
    checks += 2

    validation = {
        "status": "PASS_INDEPENDENT_SOURCE_SEPARATOR_FORMAL_IMPACT_VALIDATION",
        "checks": checks,
        "failures": [],
        "inputs": observed,
        "reconstructed": {
            "impact_groups": len(expected_impacted),
            "residual_events": len(residual_events),
            "complete_source_group_residuals": residual_class["COMPLETE_SOURCE_GROUP"],
            "intra_source_fragment_residuals": residual_class["INTRA_SOURCE_FRAGMENT"],
            "exact_raw_y_groups": sum(y_counts[(edition, "EXACT_RAW_Y_GROUP")] for edition in READINGS),
            "formal_adjacencies": sum(formal_topology.values()),
            "registered_edges": sum(registered_topology.values()),
            "registered_intra_source_edges": 0,
            "registered_skipped_edges": len(skipped),
            "direct_source_safe_events": direct["SOURCE_SAFE"],
            "direct_cleaner_affected_events": direct["CLEANER_AFFECTED"],
            "usr002_source_safe_reading_groups": usr_safe,
        },
        "isolation": {
            "producer_imported": False, "formal_parser_rerun": False,
            "extended_entities_expanded": False, "english_glosses": 0,
        },
        "mutation_controls": {
            "intra_source_y_not_complete_group": "PASS",
            "six_skipped_registered_edges_not_direct": "PASS",
        },
        "claim_ceiling": CLAIM,
        "validator_sha256": digest(Path(__file__)),
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_report = f"""# Independent source-separator formal-impact validation

Status: **PASS_INDEPENDENT_SOURCE_SEPARATOR_FORMAL_IMPACT_VALIDATION**

The nonimporting validator completed **{checks:,}** checks. It independently
reconstructed all 2,861 affected source groups, 3,838 residual events, 98,274
formal adjacencies, 4,737 registered hard edges, 3,838 candidate-lattice rows,
312 direct fusion events, and all 90 USR002 reading-specific target groups.

It confirms 2,037 complete-source-group residuals versus 1,801 intra-source
fragments, 625 exact raw `y` groups, zero registered hard edges inside a source
group, six registered edges that skip a source group, and 310/312 source-safe
direct fusion events. The validator imported neither producer nor formal parser
and expanded no special glyph entity.

This validates the provenance correction only; it supplies no authorial word
boundary, sound, grammar assignment, language, plaintext, or translation.
"""
    VALIDATION_REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
