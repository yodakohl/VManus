#!/usr/bin/env python3
"""Validate and byte-replay GDT767 without widening its source scope."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt767_ofch_historical_identity_cofield_tournament"
DEFAULT_ARTIFACTS = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"

EXPECTED_OUTPUTS = (
    "COFIELD_224_OCCURRENCE_ATLAS.tsv",
    "COFIELD_28_FORM_MATRIX.tsv",
    "OFCH_43_AGGREGATE_FEATURE_SUMMARY.tsv",
    "CHOR_CTHY_15_PARALLEL_ATLAS.tsv",
    "SHADOW_REPRODUCTIVE_4_AUDIT.tsv",
    "HISTORICAL_504_CANDIDATE_TOURNAMENT.tsv",
    "HISTORICAL_IDENTITY_SEPARABILITY.tsv",
    "GDT767_28_WORKING_DICTIONARY.tsv",
    "FIVE_LINE_REVISED_READER.tsv",
    "HISTORICAL_REGISTER_READER.md",
    "RESULT.json",
)

DONOR_PATTERN = re.compile(
    r"(?P<surface>[^|@\[\]]+)@(?P<ordinal>[1-9][0-9]*):"
    r"d(?P<distance>[1-9][0-9]*)\[(?P<features>[A-Z0-9_|]+)\]"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_run():
    return load_module("gdt767_run_for_validation", RUN_PATH)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def pipe_set(text: object) -> set[str]:
    return {
        item for item in str(text).split("|")
        if item and item not in {"NONE", "OPEN"}
    }


def parse_donors(text: str) -> list[dict[str, object]]:
    """Parse the unambiguous donor packet emitted by ``run.donors_text``."""

    if text == "NONE":
        return []
    output: list[dict[str, object]] = []
    cursor = 0
    while cursor < len(text):
        match = DONOR_PATTERN.match(text, cursor)
        if match is None:
            raise AssertionError(f"malformed donor packet at byte {cursor}: {text}")
        output.append({
            "surface": match.group("surface"),
            "ordinal": int(match.group("ordinal")),
            "distance": int(match.group("distance")),
            "features": tuple(match.group("features").split("|")),
        })
        cursor = match.end()
        if cursor == len(text):
            break
        if text[cursor] != "|":
            raise AssertionError(f"malformed donor delimiter at byte {cursor}: {text}")
        cursor += 1
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="run every check but do not write VALIDATION.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    art = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    run = load_run()
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    check(tuple(run.OUTPUT_NAMES) == EXPECTED_OUTPUTS, "declared generated-output set")
    check(len(run.OUTPUT_NAMES) == 11, "eleven builder outputs")
    for name in EXPECTED_OUTPUTS:
        check((art / name).is_file(), f"declared output exists: {name}")

    atlas = read_tsv(art / EXPECTED_OUTPUTS[0])
    matrix = read_tsv(art / EXPECTED_OUTPUTS[1])
    aggregate = read_tsv(art / EXPECTED_OUTPUTS[2])
    parallels = read_tsv(art / EXPECTED_OUTPUTS[3])
    shadows = read_tsv(art / EXPECTED_OUTPUTS[4])
    tournament = read_tsv(art / EXPECTED_OUTPUTS[5])
    separability = read_tsv(art / EXPECTED_OUTPUTS[6])
    dictionary = read_tsv(art / EXPECTED_OUTPUTS[7])
    reader = read_tsv(art / EXPECTED_OUTPUTS[8])
    historical_reader = (art / EXPECTED_OUTPUTS[9]).read_text(encoding="utf-8")
    result = json.loads((art / EXPECTED_OUTPUTS[10]).read_text(encoding="utf-8"))

    candidate_deck = read_tsv(run.CANDIDATE_DECK)
    sources = read_tsv(run.SOURCE_REGISTRY)
    passage_specs = read_tsv(run.PASSAGE_SPECS)
    inherited_shadows = read_tsv(run.SHADOW_BRIDGES)
    cthy_prior = next(
        row for row in read_tsv(run.CTHY_CENSUS) if row["surface"] == "cthy"
    )

    # Reconstruct the admitted environment. Targets are rebound to its exact
    # reader, while every recorded donor is rebound to both reader_exact and
    # clean before any feature or candidate check is accepted.
    cofield = run.cofield
    g764 = load_module(
        "gdt764_for_gdt767_validation", ROOT / cofield.G764_RUN_REL
    )
    environment = g764.semantic_environment()
    context = environment["context"]
    expected_targets = cofield.load_target_occurrences(environment)
    target_surfaces = {str(row["surface"]) for row in expected_targets}
    blocked_surfaces, gdt754_surfaces = cofield.load_blocked_donor_surfaces(
        target_surfaces, ROOT
    )

    check(len(target_surfaces) == 28, "28 exact target forms")
    check(len(expected_targets) == 224, "224 exact target occurrences")
    check(len(blocked_surfaces) == 200, "200 blocked donor surfaces")
    check(len(gdt754_surfaces) == 172, "172 GDT754 blocked donor surfaces")
    check(target_surfaces <= blocked_surfaces, "all targets blocked as donors")
    check("pchor" in blocked_surfaces, "pchor separately blocked as donor")
    check(
        blocked_surfaces == target_surfaces | {"pchor"} | set(gdt754_surfaces),
        "blocked donor set has exactly the three declared sources",
    )
    guard = {key: int(value) for key, value in dict(environment["guard"]).items()}
    check(guard.get("selected") == 4137, "guard selected 4137")
    check(guard.get("skipped_forbidden") == 98, "guard skipped forbidden 98")
    check(guard.get("skipped_not_allowed") == 1150, "guard skipped not allowed 1150")
    check(
        cofield.FORBIDDEN_PAGE_PREFIXES == ("f84",),
        "cofield seals the f84 page prefix",
    )

    def exact_token(locus: str, ordinal: int, surface: str, label: str) -> dict[str, object]:
        check(locus in context.by_line, f"known reader locus {label}")
        line = context.by_line[locus]
        check(1 <= ordinal <= len(line), f"reader ordinal in range {label}")
        token = line[ordinal - 1]
        check(str(token["eva"]) == surface, f"surface rebound {label}")
        check(
            bool(context.exact[(locus, int(token["token_index"]))]),
            f"reader-exact gate {label}",
        )
        return token

    # Complete 224-occurrence census and target-excluding donor replay.
    check(len(atlas) == 224, "224 cofield occurrence rows")
    check(len({row["source_occurrence_id"] for row in atlas}) == 224, "unique occurrence ids")
    check(
        len({(row["locus"], row["ordinal"]) for row in atlas}) == 224,
        "unique target positions",
    )
    expected_target_by_id = {
        str(row["source_occurrence_id"]): row for row in expected_targets
    }
    check(
        {row["source_occurrence_id"] for row in atlas} == set(expected_target_by_id),
        "atlas covers independently rebuilt target ids",
    )
    check(
        Counter(row["target_family"] for row in atlas)
        == Counter({"OFCH_CONTAINING": 43, "CHOR_SCHOR_LCHOR": 181}),
        "43 OFCH plus 181 chor-family target occurrences",
    )
    check(
        Counter(row["surface"] for row in atlas if row["target_family"] == "CHOR_SCHOR_LCHOR")
        == Counter({"chor": 176, "schor": 3, "lchor": 2}),
        "176/3/2 chor target census",
    )
    check(
        len({row["surface"] for row in atlas if row["target_family"] == "OFCH_CONTAINING"}) == 25,
        "25 OFCH-containing complete target forms",
    )

    atlas_by_surface: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    total_recorded_donors = 0
    for row in atlas:
        label = row["source_occurrence_id"]
        expected = expected_target_by_id[label]
        check(
            tuple(row[key] for key in ("target_family", "surface", "page", "locus"))
            == tuple(str(expected[key]) for key in ("target_family", "surface", "page", "locus")),
            f"target metadata {label}",
        )
        check(int(row["ordinal"]) == int(expected["ordinal"]), f"target ordinal {label}")
        token = exact_token(row["locus"], int(row["ordinal"]), row["surface"], label)
        line = context.by_line[row["locus"]]
        check(row["page"] == str(token["page"]), f"target page rebound {label}")
        check(int(row["line_token_count"]) == len(line), f"line length {label}")
        check(
            row["written_line_eva"] == " ".join(str(item["eva"]) for item in line),
            f"written line rebound {label}",
        )
        check(row["all_target_surfaces_blocked_as_donors"] == "1", f"target block flag {label}")
        check(row["all_donors_reader_exact_and_clean"] == "1", f"donor gate flag {label}")
        check(row["component_credit"] == "0", f"zero component credit {label}")
        check(not row["page"].lower().startswith("f84"), f"sealed target page {label}")

        parsed_by_scope: dict[str, list[dict[str, object]]] = {}
        for scope, distance_gate in (("d1", 1), ("r3", 3), ("line", None)):
            parsed = parse_donors(row[f"{scope}_donors"])
            parsed_by_scope[scope] = parsed
            total_recorded_donors += len(parsed)
            union: set[str] = set()
            expected_donors: list[dict[str, object]] = []
            for donor_ordinal in range(1, len(line) + 1):
                if donor_ordinal == int(row["ordinal"]):
                    continue
                features, donor = cofield.donor_features(
                    environment,
                    g764,
                    row["locus"],
                    donor_ordinal,
                    blocked_surfaces,
                )
                if not features or donor is None:
                    continue
                distance = abs(donor_ordinal - int(row["ordinal"]))
                if distance_gate is not None and distance > distance_gate:
                    continue
                expected_donors.append({**donor, "distance": distance})
            check(
                row[f"{scope}_donors"] == run.donors_text(expected_donors),
                f"independent donor replay {label} {scope}",
            )
            for donor in parsed:
                donor_ordinal = int(donor["ordinal"])
                donor_surface = str(donor["surface"])
                distance = abs(donor_ordinal - int(row["ordinal"]))
                check(distance == int(donor["distance"]), f"donor distance {label} {scope}")
                if distance_gate is not None:
                    check(distance <= distance_gate, f"donor inside {scope} {label}")
                donor_token = exact_token(
                    row["locus"], donor_ordinal, donor_surface,
                    f"{label}/{scope}/{donor_ordinal}",
                )
                slot = g764.slot(environment, row["locus"], donor_ordinal)
                check(int(slot["reader_exact"]) == 1, f"donor exact slot {label} {scope}")
                check(int(slot["clean"]) == 1, f"donor clean slot {label} {scope}")
                check(str(slot["surface"]) == donor_surface, f"donor slot surface {label} {scope}")
                check(str(donor_token["eva"]) == donor_surface, f"donor token surface {label} {scope}")
                check(donor_surface not in blocked_surfaces, f"blocked donor excluded {label} {scope}")
                classified, classified_row = cofield.donor_features(
                    environment, g764, row["locus"], donor_ordinal, blocked_surfaces
                )
                check(classified_row is not None, f"donor classifier admitted {label} {scope}")
                check(
                    tuple(donor["features"])
                    == tuple(feature for feature in cofield.FEATURES if feature in classified),
                    f"donor feature rebound {label} {scope}",
                )
                union.update(str(feature) for feature in donor["features"])
            check(
                row[f"{scope}_features"] == run.joined(union),
                f"feature union {label} {scope}",
            )
        donor_key = lambda item: (
            str(item["surface"]), int(item["ordinal"]), int(item["distance"]),
            tuple(item["features"]),
        )
        d1 = {donor_key(item) for item in parsed_by_scope["d1"]}
        r3 = {donor_key(item) for item in parsed_by_scope["r3"]}
        line_donors = {donor_key(item) for item in parsed_by_scope["line"]}
        check(d1 <= r3 <= line_donors, f"nested donor scopes {label}")
        atlas_by_surface[row["surface"]].append(row)
    check(total_recorded_donors > 0, "nonempty admitted donor census")

    # Form matrix is an independent aggregation of the occurrence atlas.
    check(len(matrix) == 28, "28 cofield form rows")
    check(len({row["surface"] for row in matrix}) == 28, "unique matrix surfaces")
    check(set(atlas_by_surface) == {row["surface"] for row in matrix}, "matrix covers targets")
    check(sum(int(row["reader_exact_occurrences"]) for row in matrix) == 224, "matrix sums to 224")
    matrix_by_surface = {row["surface"]: row for row in matrix}
    for row in matrix:
        occurrences = atlas_by_surface[row["surface"]]
        check(int(row["reader_exact_occurrences"]) == len(occurrences), f"matrix n {row['surface']}")
        check(
            {item["target_family"] for item in occurrences} == {row["target_family"]},
            f"matrix family {row['surface']}",
        )
        for feature in cofield.FEATURES:
            stem = feature.lower()
            counts = {
                scope: sum(
                    feature in pipe_set(item[f"{scope}_features"])
                    for item in occurrences
                )
                for scope in ("d1", "r3", "line")
            }
            check(
                0 <= counts["d1"] <= counts["r3"] <= counts["line"] <= len(occurrences),
                f"nested feature counts {row['surface']} {feature}",
            )
            for scope in ("d1", "r3", "line"):
                check(
                    int(row[f"{stem}_{scope}"]) == counts[scope],
                    f"matrix feature count {row['surface']} {feature} {scope}",
                )
            check(
                row[f"{stem}_d1_r3_line"]
                == f"{counts['d1']}/{counts['r3']}/{counts['line']}",
                f"matrix feature triple {row['surface']} {feature}",
            )
        check(row["specific_substance_identity_from_cofields"] == "OPEN", f"identity open {row['surface']}")
        check(row["component_credit"] == "0", f"matrix component zero {row['surface']}")

    # OFCH-only feature summary, including both exact identity-anchor zeros.
    ofch_rows = [row for row in atlas if row["target_family"] == "OFCH_CONTAINING"]
    check(len(ofch_rows) == 43, "43 OFCH target rows")
    check(len(aggregate) == len(cofield.FEATURES) == 12, "twelve OFCH feature rows")
    check({row["feature"] for row in aggregate} == set(cofield.FEATURES), "aggregate feature coverage")
    aggregate_by_feature = {row["feature"]: row for row in aggregate}
    for feature in cofield.FEATURES:
        row = aggregate_by_feature[feature]
        check(int(row["ofch_exact_occurrences"]) == 43, f"aggregate denominator {feature}")
        for scope in ("d1", "r3", "line"):
            count = sum(feature in pipe_set(item[f"{scope}_features"]) for item in ofch_rows)
            check(int(row[f"{scope}_occurrences"]) == count, f"aggregate count {feature} {scope}")
            check(row[f"{scope}_rate"] == f"{count / 43:.6f}", f"aggregate rate {feature} {scope}")
        check(row["identity_credit"] == "0", f"aggregate identity credit {feature}")
    for feature in ("CTHY_LEAF", "CHOR_REPRO"):
        row = aggregate_by_feature[feature]
        check(
            tuple(int(row[f"{scope}_occurrences"]) for scope in ("d1", "r3", "line"))
            == (0, 0, 0),
            f"OFCH {feature} is exactly 0/0/0",
        )

    # The independent chor/cthy parallel packet is separate from OFCH identity
    # scoring and is rebound directly to the guarded reader.
    check(len(parallels) == 15, "15 chor/cthy parallel positions")
    check(len({row["pair_id"] for row in parallels}) == 15, "unique parallel ids")
    check(len({row["locus"] for row in parallels}) == 14, "14 chor/cthy loci")
    check(sum(int(row["direct_pair"]) for row in parallels) == 5, "five direct chor/cthy pairs")
    check(cthy_prior["reader_exact_occurrences"] == "85", "cthy prior has 85 exact occurrences")
    check(cthy_prior["herbal_occurrences"] == "83", "cthy prior has 83 herbal occurrences")
    check(cthy_prior["gdt758_primary_candidate_de"] == "Blattgut / Blattdroge", "cthy prior leaf-drug lead")
    expected_parallel_positions: set[tuple[str, int, int]] = set()
    for target in atlas:
        if target["surface"] != "chor":
            continue
        line = context.by_line[target["locus"]]
        for donor_ordinal in range(1, len(line) + 1):
            if str(line[donor_ordinal - 1]["eva"]) != "cthy":
                continue
            features, donor = cofield.donor_features(
                environment, g764, target["locus"], donor_ordinal, blocked_surfaces
            )
            if donor is not None and "CTHY_LEAF" in features:
                expected_parallel_positions.add(
                    (target["locus"], int(target["ordinal"]), donor_ordinal)
                )
    check(
        {(row["locus"], int(row["chor_ordinal"]), int(row["cthy_ordinal"])) for row in parallels}
        == expected_parallel_positions,
        "complete independent chor/cthy parallel census",
    )
    for row in parallels:
        label = row["pair_id"]
        chor_ordinal = int(row["chor_ordinal"])
        cthy_ordinal = int(row["cthy_ordinal"])
        exact_token(row["locus"], chor_ordinal, "chor", f"{label}/chor")
        exact_token(row["locus"], cthy_ordinal, "cthy", f"{label}/cthy")
        cthy_slot = g764.slot(environment, row["locus"], cthy_ordinal)
        check(int(cthy_slot["clean"]) == 1, f"clean cthy parallel {label}")
        distance = abs(chor_ordinal - cthy_ordinal)
        direction = "LEFT" if cthy_ordinal < chor_ordinal else "RIGHT"
        check(int(row["distance"]) == distance, f"parallel distance {label}")
        check(row["cthy_direction_from_chor"] == direction, f"parallel direction {label}")
        check(int(row["direct_pair"]) == int(distance == 1), f"parallel direct flag {label}")
        check(
            row["written_order"] == ("CTHY_CHOR" if direction == "LEFT" else "CHOR_CTHY"),
            f"parallel written order {label}",
        )
        check(
            row["written_line_eva"]
            == " ".join(str(token["eva"]) for token in context.by_line[row["locus"]]),
            f"parallel written line {label}",
        )
        check(row["same_identity_reading"] == "DISFAVORED_BY_REPEATED_PARALLELISM", f"parallel interpretation {label}")
        check(row["cthy_working_whole"] == cthy_prior["gdt758_primary_candidate_de"], f"cthy prior whole {label}")
        check(row["cthy_prior_confidence"] == cthy_prior["working_confidence"], f"cthy prior confidence {label}")
        check(row["cthy_global_exact_occurrences"] == "85", f"cthy exact count {label}")
        check(row["cthy_global_herbal_occurrences"] == "83", f"cthy herbal count {label}")
        check(row["specific_flower_vs_seed_credit"] == "0", f"parallel identity ceiling {label}")
        check(row["component_credit"] == "0", f"parallel component ceiling {label}")

    # Four inherited reproductive contacts stay shadow evidence only.
    check(len(shadows) == len(inherited_shadows) == 4, "four shadow reproductive contacts")
    inherited_by_id = {row["bridge_id"]: row for row in inherited_shadows}
    check({row["bridge_id"] for row in shadows} == set(inherited_by_id), "shadow id coverage")
    for row in shadows:
        label = row["bridge_id"]
        prior = inherited_by_id[label]
        for field, value in prior.items():
            check(row[field] == value, f"shadow inherited field {label} {field}")
        exact_token(row["locus"], int(row["ofch_ordinal"]), row["ofch_surface"], f"{label}/ofch")
        exact_token(
            row["locus"], int(row["reproductive_ordinal"]),
            row["reproductive_surface"], f"{label}/reproductive",
        )
        check(row["reproductive_surface"] != "chor", f"shadow is not exact chor {label}")
        check(row["strict_exact_chor_anchor"] == "0", f"shadow exact-anchor zero {label}")
        check(row["gdt767_identity_credit"] == "0", f"shadow identity zero {label}")
        check(row["score_ready_relation_credit"] == "0", f"shadow relation zero {label}")
        check(row["global_component_export"] == "0", f"shadow component zero {label}")
        check(
            row["gdt767_disposition"] == "RETAIN_AS_C0_FLOWER_OR_SEED_SHADOW_LEAD",
            f"shadow disposition {label}",
        )

    # Historical deck and source registry are finite, whole-form-only inputs.
    check(len(candidate_deck) == 18, "18 historical candidates")
    check(len({row["candidate_id"] for row in candidate_deck}) == 18, "unique candidate ids")
    check(
        Counter(row["candidate_layer"] for row in candidate_deck)
        == Counter({"SUBSTANCE": 8, "FORM": 10}),
        "eight substance plus ten form candidates",
    )
    check(len(sources) == 6, "six historical sources")
    check(len({row["source_id"] for row in sources}) == 6, "unique source ids")
    source_ids = {row["source_id"] for row in sources}
    for row in candidate_deck:
        check(pipe_set(row["source_ids"]) <= source_ids, f"candidate source ids {row['candidate_id']}")
        check(row["component_credit"] == "0", f"candidate component zero {row['candidate_id']}")
        check(bool(row["historical_expression"]), f"candidate historical expression {row['candidate_id']}")
        check(bool(row["working_noun_de"]), f"candidate working noun {row['candidate_id']}")
        check(bool(row["attested_forms"]), f"candidate attested forms {row['candidate_id']}")
    for row in sources:
        check(row["primary_url"].startswith("https://"), f"direct source URL {row['source_id']}")
        check(bool(row["register_evidence"]), f"source evidence {row['source_id']}")
        check(bool(row["caveat"]), f"source caveat {row['source_id']}")

    # Recompute all 28 x 18 candidate gates, scores and within-layer ranks.
    check(len(tournament) == 504, "504 candidate tournament rows")
    check(len({(row["surface"], row["candidate_id"]) for row in tournament}) == 504, "unique tournament cells")
    candidate_by_id = {row["candidate_id"]: row for row in candidate_deck}
    info = run.target_info()
    check(len(info) == 28 and set(info) == set(atlas_by_surface), "28 target-info rows")
    tournament_by_surface: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tournament:
        tournament_by_surface[row["surface"]].append(row)
    check(set(tournament_by_surface) == set(atlas_by_surface), "tournament target coverage")
    for surface, rows in tournament_by_surface.items():
        check(len(rows) == 18, f"18 candidates for {surface}")
        check({row["candidate_id"] for row in rows} == set(candidate_by_id), f"candidate coverage {surface}")
        occurrences = atlas_by_surface[surface]
        target = info[surface]
        for row in rows:
            candidate = candidate_by_id[row["candidate_id"]]
            label = f"{surface}/{row['candidate_id']}"
            for field in (
                "candidate_layer", "historical_expression", "working_noun_de",
                "gate_all_r3", "gate_any_r3", "forbid_line", "repeat_required",
                "identity_specificity", "source_ids", "attested_forms", "attestation_scope",
            ):
                check(row[field] == candidate[field], f"candidate field {label} {field}")
            check(row["target_family"] == target["target_family"], f"target family {label}")
            check(int(row["reader_exact_occurrences"]) == len(occurrences), f"target n {label}")
            check(row["predicted_channel_from_gdt766"] == target["predicted_channel"], f"channel {label}")
            preferred = pipe_set(candidate["preferred_channels"])
            role_fit = int(str(target["predicted_channel"]) in preferred)
            check(int(row["role_fit"]) == role_fit, f"role fit {label}")
            scope_hits: dict[str, int] = {}
            for scope in ("d1", "r3", "line"):
                scope_hits[scope] = sum(
                    run.candidate_hit(
                        candidate,
                        pipe_set(item[f"{scope}_features"]),
                        pipe_set(item["line_features"]),
                    )
                    for item in occurrences
                )
                check(int(row[f"{scope}_gate_hits"]) == scope_hits[scope], f"gate hits {label} {scope}")
            check(row["r3_gate_rate"] == f"{scope_hits['r3'] / len(occurrences):.6f}", f"gate rate {label}")
            redundancy = int(
                surface == "chor"
                and candidate["candidate_id"] == "S04"
                and scope_hits["line"] >= 2
            )
            check(int(row["semantic_redundancy_penalty"]) == redundancy, f"redundancy {label}")
            repeat_required = candidate["repeat_required"] == "1"
            if redundancy:
                level, evidence_label = 0, "REPEATED_PARALLELISM_COUNTEREVIDENCE"
            elif repeat_required and scope_hits["r3"] < 2:
                level, evidence_label = 0, "REPEAT_REQUIREMENT_NOT_MET"
            elif scope_hits["r3"] >= 2 and role_fit:
                level, evidence_label = 4, "REPEATED_GATE_AND_ROLE"
            elif scope_hits["r3"] >= 2:
                level, evidence_label = 3, "REPEATED_GATE"
            elif scope_hits["r3"] == 1 and role_fit:
                level, evidence_label = 2, "ONE_GATE_AND_ROLE"
            elif scope_hits["r3"] == 1:
                level, evidence_label = 1, "ONE_OCCURRENCE_GATE"
            else:
                level, evidence_label = 0, "NO_TARGET_FREE_GATE_HIT"
            check(int(row["evidence_level_0_4"]) == level, f"evidence level {label}")
            check(row["evidence_label"] == evidence_label, f"evidence label {label}")
            legacy = int(
                candidate["candidate_id"] == "S01"
                and candidate["legacy_tiebreak_allowed"] == "1"
                and "Blüten" in str(target["prior_bold_default_de"])
            )
            check(int(row["legacy_flower_tiebreak"]) == legacy, f"legacy tie break {label}")
            evidence_score = 20 * level + 10 * scope_hits["r3"] / len(occurrences) + min(9, scope_hits["r3"])
            exploratory_score = evidence_score + 2 * role_fit + legacy
            check(row["evidence_score"] == f"{evidence_score:.6f}", f"evidence score {label}")
            check(row["exploratory_score"] == f"{exploratory_score:.6f}", f"exploratory score {label}")
            required_hits = 2 if candidate["repeat_required"] == "1" else 1
            check(
                int(row["repeat_requirement_met"]) == int(scope_hits["r3"] >= required_hits),
                f"repeat requirement {label}",
            )
            if repeat_required and scope_hits["r3"] < 2:
                check(level == 0, f"unmet repeat forces level zero {label}")
                check(
                    evidence_label == "REPEAT_REQUIREMENT_NOT_MET",
                    f"unmet repeat receives explicit label {label}",
                )
            check(row["literal_identity_confirmed"] == "0", f"literal identity zero {label}")
            check(row["component_credit"] == "0", f"component zero {label}")
        for layer, expected_count in (("SUBSTANCE", 8), ("FORM", 10)):
            layer_rows = [row for row in rows if row["candidate_layer"] == layer]
            check(len(layer_rows) == expected_count, f"layer size {surface} {layer}")
            evidence_order = sorted(
                layer_rows,
                key=lambda row: (
                    -int(row["evidence_level_0_4"]),
                    -float(row["evidence_score"]),
                    row["candidate_id"],
                ),
            )
            exploratory_order = sorted(
                layer_rows,
                key=lambda row: (-float(row["exploratory_score"]), row["candidate_id"]),
            )
            check(
                [int(row["evidence_rank"]) for row in evidence_order]
                == list(range(1, expected_count + 1)),
                f"evidence ranks {surface} {layer}",
            )
            check(
                [int(row["exploratory_rank"]) for row in exploratory_order]
                == list(range(1, expected_count + 1)),
                f"exploratory ranks {surface} {layer}",
            )

    # Separability is recomputed from the complete tournament support vectors.
    by_candidate: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tournament:
        by_candidate[row["candidate_id"]].append(row)
    vector_groups: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    for candidate_id, rows in by_candidate.items():
        ordered = sorted(rows, key=lambda row: row["surface"])
        vector = "|".join(
            f"{row['surface']}:{row['d1_gate_hits']}/{row['r3_gate_hits']}/{row['line_gate_hits']}"
            for row in ordered
        )
        digest = hashlib.sha256(vector.encode("utf-8")).hexdigest()[:12]
        vector_groups[(rows[0]["candidate_layer"], digest)].append(candidate_id)
    check(len(separability) == len(vector_groups) == 8, "eight observed support groups")
    separability_by_id = {row["observed_support_group"]: row for row in separability}
    check(len(separability_by_id) == 8, "unique separability ids")
    for group_no, ((layer, digest), candidate_ids) in enumerate(sorted(vector_groups.items()), 1):
        row = separability_by_id[f"G767-SEP{group_no:02d}"]
        ids = sorted(candidate_ids)
        check(row["candidate_layer"] == layer, f"separability layer {group_no}")
        check(row["candidate_ids"] == "|".join(ids), f"separability candidates {group_no}")
        check(int(row["candidate_count"]) == len(ids), f"separability count {group_no}")
        check(row["support_vector_sha256_12"] == digest, f"separability digest {group_no}")
        expected_hits = "|".join(
            f"{candidate_id}:{sum(int(item['r3_gate_hits']) for item in by_candidate[candidate_id])}"
            for candidate_id in ids
        )
        check(row["total_r3_hits_by_candidate"] == expected_hits, f"separability totals {group_no}")
        check(
            int(row["observationally_separable_in_current_cofields"]) == int(len(ids) == 1),
            f"separability flag {group_no}",
        )
        check(row["literal_identity_confirmed"] == "0", f"separability identity zero {group_no}")
    tied_groups = sorted(row["candidate_ids"] for row in separability if int(row["candidate_count"]) > 1)
    check(
        tied_groups
        == sorted(["F00|F06|F07|F08|F09", "S00|S01|S02|S03|S05|S06|S07"]),
        "specific liquids and most substances remain tied",
    )

    # Every dictionary whole must retain a concrete default, two rivals,
    # explicit confidence, positive evidence and counterevidence.
    check(len(dictionary) == 28, "28 dictionary rows")
    check(len({row["surface"] for row in dictionary}) == 28, "unique dictionary wholes")
    check({row["surface"] for row in dictionary} == set(matrix_by_surface), "dictionary target coverage")
    check(sum(int(row["reader_exact_occurrences"]) for row in dictionary) == 224, "dictionary sums to 224")
    dictionary_by_surface = {row["surface"]: row for row in dictionary}
    required_nonempty = (
        "portable_working_class_de", "forced_concrete_default_de",
        "forced_concrete_identity_confidence", "form_confidence", "evidence",
        "counterevidence", "primary_rival_de", "secondary_rival_de",
        "selected_target_free_substance_candidate", "selected_target_free_substance_de",
        "selected_target_free_form_candidate", "selected_target_free_form_de",
    )
    for row in dictionary:
        surface = row["surface"]
        stats = matrix_by_surface[surface]
        for field in required_nonempty:
            check(bool(row[field].strip()), f"dictionary nonempty {surface} {field}")
            check(row[field] != "NONE", f"dictionary substantive {surface} {field}")
        check(
            row["forced_concrete_identity_confidence"] == "C0_REPLACEABLE_DEFAULT",
            f"replaceable identity confidence {surface}",
        )
        check(row["form_confidence"].startswith("C"), f"form confidence {surface}")
        check(row["target_family"] == stats["target_family"], f"dictionary family {surface}")
        check(int(row["reader_exact_occurrences"]) == int(stats["reader_exact_occurrences"]), f"dictionary n {surface}")
        substance_rows = [
            item for item in tournament_by_surface[surface]
            if item["candidate_layer"] == "SUBSTANCE"
            and item["candidate_id"] == row["selected_target_free_substance_candidate"]
        ]
        form_rows = [
            item for item in tournament_by_surface[surface]
            if item["candidate_layer"] == "FORM"
            and item["candidate_id"] == row["selected_target_free_form_candidate"]
        ]
        check(len(substance_rows) == len(form_rows) == 1, f"dictionary selected candidates {surface}")
        expected_substance = run.selected_candidate(
            tournament_by_surface[surface], "SUBSTANCE", "S00"
        )
        expected_form = run.selected_candidate(
            tournament_by_surface[surface], "FORM", "F00"
        )
        # The builder deliberately refuses to collapse chor's mutually
        # incompatible repeated state fields into one permanent form.
        if surface == "chor":
            expected_form = next(
                item for item in tournament_by_surface[surface]
                if item["candidate_layer"] == "FORM"
                and item["candidate_id"] == "F00"
            )
        check(
            row["selected_target_free_substance_candidate"]
            == expected_substance["candidate_id"],
            f"dictionary substance selection replay {surface}",
        )
        check(
            row["selected_target_free_form_candidate"] == expected_form["candidate_id"],
            f"dictionary form selection replay {surface}",
        )
        if surface == "chor":
            check(
                row["selected_target_free_form_candidate"] == "F00",
                "chor form remains deliberately unselected",
            )
        for selected, layer in ((substance_rows[0], "substance"), (form_rows[0], "form")):
            if int(selected["evidence_level_0_4"]) >= 2:
                check(
                    int(selected["repeat_requirement_met"]) == 1,
                    f"selected supported {layer} satisfies repeat rule {surface}",
                )
        check(row["selected_target_free_substance_de"] == substance_rows[0]["working_noun_de"], f"substance noun {surface}")
        check(row["selected_target_free_form_de"] == form_rows[0]["working_noun_de"], f"form noun {surface}")
        check(int(row["substance_evidence_level_0_4"]) == int(substance_rows[0]["evidence_level_0_4"]), f"substance evidence {surface}")
        check(int(row["form_evidence_level_0_4"]) == int(form_rows[0]["evidence_level_0_4"]), f"form evidence {surface}")
        for feature in (
            "dry", "moist", "value_amount", "prep", "process_close",
            "cthy_leaf", "chor_repro",
        ):
            check(row[f"{feature}_d1_r3_line"] == stats[f"{feature}_d1_r3_line"], f"dictionary feature {surface} {feature}")
        zero_features = all(
            int(stats[f"{feature.lower()}_line"]) == 0 for feature in cofield.FEATURES
        )
        check(int(row["zero_admitted_target_free_features"]) == int(zero_features), f"zero-feature flag {surface}")
        check(row["specific_identity_replaceable"] == "1", f"specific identity replaceable {surface}")
        check(row["confirmed_lexeme"] == "0", f"confirmed lexeme zero {surface}")
        check(row["component_credit"] == "0", f"dictionary component zero {surface}")
        check(row["unseen_form_export"] == "0", f"unseen export zero {surface}")

    downgraded = {
        row["surface"] for row in dictionary
        if row["gdt767_default_disposition"]
        != "legacy concrete default retained until contradicted or replaced"
    }
    check(downgraded == {"ofcheol", "qofcheol"}, "exact two extract downgrades")
    for surface in ("ofcheol", "qofcheol"):
        row = dictionary_by_surface[surface]
        check(row["predicted_channel"] == "EXTRACT", f"extract channel {surface}")
        check(row["forced_concrete_default_de"] == "Blütenzubereitung", f"downgraded default {surface}")
        check(
            row["gdt767_default_disposition"]
            == "Auszug, Oel, Wasser, Wein oder Essig bleiben C0-Rivalen",
            f"downgrade rival set {surface}",
        )
        check(row["selected_target_free_form_candidate"] == "F00", f"no liquid form selected {surface}")
    check(
        Counter(row["selected_target_free_form_candidate"] for row in dictionary)
        == Counter({"F00": 14, "F01": 5, "F02": 5, "F04": 4}),
        "selected form candidate census",
    )

    # Five complete lines and all 46 exact tokens replay their token defaults
    # in written order, without claiming attachment or plaintext.
    expected_line_lengths = {
        "f22r.4": 9,
        "f22v.1": 8,
        "f41v.2": 9,
        "f93r.2": 11,
        "f107r.38": 9,
    }
    check(len(passage_specs) == 46, "46 inherited passage specs")
    check(len(reader) == 46, "46 revised reader tokens")
    check(Counter(row["locus"] for row in reader) == Counter(expected_line_lengths), "five complete line lengths")
    check(len({row["locus"] for row in reader}) == 5, "five revised reader lines")
    for index, (row, source) in enumerate(zip(reader, passage_specs, strict=True), 1):
        label = row["reader_token_id"]
        check(label == f"G767-R{index:02d}", f"reader id {index}")
        check(
            (row["locus"], row["ordinal"], row["surface"])
            == (source["locus"], source["ordinal"], source["surface"]),
            f"reader source position {label}",
        )
        exact_token(row["locus"], int(row["ordinal"]), row["surface"], label)
        update = dictionary_by_surface.get(row["surface"])
        expected_default = update["forced_concrete_default_de"] if update else source["local_default_de"]
        expected_confidence = update["forced_concrete_identity_confidence"] if update else source["confidence"]
        check(row["gdt766_local_default_de"] == source["local_default_de"], f"reader inherited default {label}")
        check(row["gdt767_local_default_de"] == expected_default, f"reader revised default {label}")
        check(row["gdt767_confidence"] == expected_confidence, f"reader confidence {label}")
        check(int(row["updated_target"]) == int(update is not None), f"reader update flag {label}")
        check(row["renderer_boundary"] == "TOKEN_DEFAULTS_IN_WRITTEN_ORDER_SEMICOLONS_ASSERT_NO_ATTACHMENT", f"reader boundary {label}")
        check(row["confirmed_plaintext"] == "0", f"reader plaintext zero {label}")
        check(row["component_credit"] == "0", f"reader component zero {label}")
        check(bool(row["gdt767_local_default_de"]), f"reader default nonempty {label}")
        check(bool(row["gdt767_confidence"]), f"reader confidence nonempty {label}")
    for locus, length in expected_line_lengths.items():
        rows = sorted(
            (row for row in reader if row["locus"] == locus),
            key=lambda row: int(row["ordinal"]),
        )
        check([int(row["ordinal"]) for row in rows] == list(range(1, length + 1)), f"complete ordinals {locus}")
        written = " ".join(row["surface"] for row in rows)
        rendered = "; ".join(row["gdt767_local_default_de"] for row in rows) + "."
        check({row["written_line_eva"] for row in rows} == {written}, f"single written line {locus}")
        check({row["gdt767_revised_line_de"] for row in rows} == {rendered}, f"single revised line {locus}")

    # Human-readable historical reader contains the complete dictionary and
    # direct URLs, while explicitly retaining the no-spelling/no-plaintext ceiling.
    check(historical_reader.startswith("# GDT767 historical identity and co-field reader\n"), "historical reader title")
    for row in dictionary:
        check(f"| `{row['surface']}` |" in historical_reader, f"dictionary whole in historical reader {row['surface']}")
    for source in sources:
        check(source["primary_url"] in historical_reader, f"source URL in historical reader {source['source_id']}")
    check(
        "No EVA character, initial or substring receives a Latin value." in historical_reader,
        "historical reader denies EVA substring values",
    )
    check("none is confirmed plaintext" in historical_reader, "historical reader plaintext ceiling")

    # Result payload fixes every requested invariant and the claim ceiling.
    expected_scope = {
        "target_forms": 28,
        "target_occurrences": 224,
        "ofch_forms": 25,
        "ofch_occurrences": 43,
        "chor_occurrences": 176,
        "schor_occurrences": 3,
        "lchor_occurrences": 2,
        "gdt754_blocked_surfaces": 172,
        "blocked_donor_surfaces": 200,
        "guard_selected": 4137,
        "guard_skipped_forbidden": 98,
        "guard_skipped_not_allowed": 1150,
        "historical_sources": 6,
        "historical_candidates": 18,
        "candidate_tournament_rows": 504,
        "chor_cthy_parallel_positions": 15,
        "chor_cthy_parallel_loci": 14,
        "chor_cthy_direct_pairs": 5,
        "shadow_reproductive_contacts": 4,
        "working_dictionary_rows": 28,
        "complete_reader_tokens": 46,
        "complete_reader_lines": 5,
        "cthy_prior_exact_occurrences": 85,
        "cthy_prior_herbal_occurrences": 83,
    }
    check(result["schema"] == "GDT767_RESULT_V1", "result schema")
    check(result["status"] == run.STATUS, "result status")
    check(result["scope"] == expected_scope, "result fixed scope")
    check(
        result["ofch_target_excluding_features"]
        == {
            row["feature"]: {
                "d1": int(row["d1_occurrences"]),
                "r3": int(row["r3_occurrences"]),
                "line": int(row["line_occurrences"]),
            }
            for row in aggregate
        },
        "result feature summary",
    )
    check(
        result["ofch_target_excluding_features"]["CTHY_LEAF"] == {"d1": 0, "r3": 0, "line": 0},
        "result OFCH leaf anchor zero",
    )
    check(
        result["ofch_target_excluding_features"]["CHOR_REPRO"] == {"d1": 0, "r3": 0, "line": 0},
        "result OFCH reproductive anchor zero",
    )
    selected_forms = Counter(row["selected_target_free_form_candidate"] for row in dictionary)
    check(result["selected_target_free_form_candidates"] == dict(sorted(selected_forms.items())), "result selected forms")
    zero_feature_forms = [row["surface"] for row in dictionary if int(row["zero_admitted_target_free_features"])]
    check(result["zero_target_free_feature_forms"] == zero_feature_forms, "result zero-feature forms")
    check(result["concrete_default_downgrades"] == ["ofcheol", "qofcheol"], "result downgrade list")
    check(result["observationally_tied_candidate_groups"] == [
        row["candidate_ids"] for row in separability if int(row["candidate_count"]) > 1
    ], "result tied groups")
    check(result["interpretation"]["specific_ofch_substance"] == "OPEN", "specific substance open")
    check(
        result["interpretation"]["oil_water_wine_vinegar"]
        == "OBSERVATIONALLY_UNSEPARATED_AND_UNSUPPORTED_FOR_OFCH_EOL",
        "liquid identities unseparated",
    )
    check(result["claim_boundary"] == {
        "forced_concrete_replaceable_defaults": 28,
        "confirmed_lexemes": 0,
        "confirmed_substances": 0,
        "plaintext_clauses": 0,
        "component_credit": 0,
        "new_pages": 0,
        "new_images": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
    }, "result claim boundary")

    # Every zero/export field is checked row by row; generated products may not
    # contain a sealed page selector anywhere, including embedded lines.
    tables: tuple[Iterable[Mapping[str, str]], ...] = (
        atlas, matrix, aggregate, parallels, shadows, tournament,
        separability, dictionary, reader,
    )
    zero_fields = {
        "component_credit", "identity_credit", "specific_flower_vs_seed_credit",
        "score_ready_relation_credit", "global_component_export",
        "gdt767_identity_credit", "literal_identity_confirmed",
        "confirmed_lexeme", "unseen_form_export", "confirmed_plaintext",
    }
    for rows in tables:
        for row in rows:
            for field in zero_fields & row.keys():
                check(row[field] == "0", f"zero claim/export field {field}")
            for field in ("page", "physical_folio", "locus"):
                check(not row.get(field, "").lower().startswith("f84"), f"sealed f84 absent from {field}")
    # RESULT.json deliberately records ``f84_accessed: false`` and
    # ``f84r_accessed: false``.  Those negative audit keys are not selectors;
    # scan every other generated product literally and verify the result flags
    # structurally above.
    for name in EXPECTED_OUTPUTS[:-1]:
        check(b"f84" not in (art / name).read_bytes().lower(), f"sealed f84 absent from output {name}")

    # Rebuild in isolation and compare every one of the eleven declared output
    # artifacts byte for byte. VALIDATION.json is deliberately not a builder output.
    with tempfile.TemporaryDirectory(prefix=".gdt767_replay_", dir=EXP) as temp_name:
        replay = Path(temp_name)
        replay_result = run.build(replay)
        check(replay_result == result, "builder replay result payload")
        check(
            {path.name for path in replay.iterdir() if path.is_file()} == set(EXPECTED_OUTPUTS),
            "replay emits exactly eleven outputs",
        )
        for name in EXPECTED_OUTPUTS:
            check(
                (art / name).read_bytes() == (replay / name).read_bytes(),
                f"byte-identical replay {name}",
            )

    validation = {
        "schema": "GDT767_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "declared_outputs_byte_identical": len(EXPECTED_OUTPUTS),
        "target_forms": len(matrix),
        "target_occurrences": len(atlas),
        "ofch_occurrences": len(ofch_rows),
        "candidate_tournament_rows": len(tournament),
        "chor_cthy_parallel_positions": len(parallels),
        "chor_cthy_parallel_loci": len({row["locus"] for row in parallels}),
        "chor_cthy_direct_pairs": sum(int(row["direct_pair"]) for row in parallels),
        "shadow_reproductive_contacts": len(shadows),
        "working_dictionary_rows": len(dictionary),
        "complete_reader_tokens": len(reader),
        "complete_reader_lines": len({row["locus"] for row in reader}),
        "blocked_donor_surfaces": len(blocked_surfaces),
        "gdt754_blocked_surfaces": len(gdt754_surfaces),
        "historical_candidates": len(candidate_deck),
        "historical_sources": len(sources),
        "ofch_cthy_leaf_d1_r3_line": "0/0/0",
        "ofch_chor_repro_d1_r3_line": "0/0/0",
        "downgraded_extract_wholes": ["ofcheol", "qofcheol"],
        "confirmed_lexemes": 0,
        "component_exports": 0,
        "sealed_f84": "FORBIDDEN_NOT_ACCESSED",
        "sealed_f84r": "FORBIDDEN_NOT_ACCESSED",
        "new_pages": 0,
    }
    if not args.check_only:
        art.mkdir(parents=True, exist_ok=True)
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
