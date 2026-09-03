#!/usr/bin/env python3
"""Independent reconstruction, safety, renderer, and replay checks for GDT775."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.util
import io
import json
import math
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test"
SRC, ART = EXP / "src", EXP / "artifacts"
RUN, REPORT, VALIDATION = SRC / "run.py", EXP / "REPORT.md", ART / "VALIDATION.json"
G774 = ROOT / "experiments/yolo/gdt774_ol_376_contextual_transfer/artifacts/OL_376_TRANSFER_ATLAS.tsv"
G734 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G762_STATES = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/src/STATE_PAIR_PRIORS.tsv"
G737_CANDIDATES = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
G757_CONTROLS = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_11_WHOLE_ROLE_ATLAS.tsv"
G768_CONTROLS = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
G769_CORE = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py"
CROSS = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
FALLBACK = "Ansatz-/Zubereitungsposten"
FAMILY = frozenset({"chy", "chey", "cheey", "chdy", "chedy", "sheey", "shedy",
                    "aiin", "daiin", "kaiin", "okaiin", "oiin", "olaiin"})
BOUNDARY = frozenset({"cheey", "kaiin", "oiin"})
EXPECTED_FAMILY = {"aiin": 9, "chedy": 7, "sheey": 7, "chey": 6, "cheey": 6,
                   "daiin": 5, "kaiin": 5, "shedy": 5, "okaiin": 4, "olaiin": 4,
                   "oiin": 3, "chdy": 3, "chy": 2}
EXPECTED_ANCHORS = {"chor": 141, "shor": 63, "cthy": 49, "dair": 39, "ofchy": 3,
                    "schor": 2, "pol": 9, "polaiin": 7, "ychor": 13, "ycheol": 7,
                    "ychol": 8, "dcheol": 4, "qokchor": 5, "ycheor": 5,
                    "pchor": 9, "tshol": 5}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if page.startswith("fRos"):
        return "fRos"
    assert match is not None
    return match.group(1)


def load_core() -> object:
    spec = importlib.util.spec_from_file_location("gdt769_for_gdt775_validator", G769_CORE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outputs_from_ast() -> tuple[str, ...]:
    tree = ast.parse(RUN.read_text(encoding="utf-8"))
    nodes = [node for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == "OUTPUT_NAMES" for target in node.targets)]
    assert len(nodes) == 1
    value = ast.literal_eval(nodes[0].value)
    assert isinstance(value, list) and all(isinstance(item, str) for item in value)
    return tuple(value)


def neighbor(row: Mapping[str, str], context: object, offset: int) -> tuple[str, bool]:
    line = context.by_line[row["locus"]]
    index = int(row["ordinal"]) - 1 + offset
    if not 0 <= index < len(line):
        return "NONE", False
    token = line[index]
    return str(token["eva"]), bool(context.exact[(row["locus"], int(token["token_index"]))])


def cosine(first: Counter[str], second: Counter[str]) -> float:
    keys = set(first) | set(second)
    numerator = sum(first[key] * second[key] for key in keys)
    denominator = math.sqrt(sum(value * value for value in first.values())) * math.sqrt(sum(value * value for value in second.values()))
    return numerator / denominator if denominator else 0.0


def mean_surface_vector(edges: Sequence[Mapping[str, object]], surfaces: Sequence[str]) -> Counter[str]:
    totals = Counter(str(row["predecessor_surface"]) for row in edges)
    output: Counter[str] = Counter()
    for surface in surfaces:
        assert totals[surface]
        for row in edges:
            if row["predecessor_surface"] == surface:
                output[str(row["right_surface"])] += 1 / totals[surface] / len(surfaces)
    return output


def boundary_mode(text: str, right: str) -> str:
    tokens = text.split()
    separated = sum(tokens[i] == "ol" and tokens[i + 1] == right for i in range(len(tokens) - 1))
    fused = sum(token == "ol" + right for token in tokens)
    if separated == 1 and fused == 0:
        return "SEPARATED_EXACT"
    if separated == 0 and fused == 1:
        return "FUSED_EXACT"
    if separated == 0 and fused == 0:
        return "NO_EXACT_PAIR_FORM"
    return "AMBIGUOUS_MULTIPLE_FORMS"


def guarded_cross(pages: Sequence[str]) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS.relative_to(ROOT)),
               "--selector", "page", "--columns", "page,locus,all_three_present,zl3b_clean,it2a_clean,rf1b_clean"]
    for page in sorted(set(pages)):
        command.extend(["--allow", page])
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    assert "GUARD_STATS" in done.stderr
    return list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--validation-path", type=Path, default=VALIDATION)
    args = parser.parse_args()
    artifacts = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    validation_path = args.validation_path if args.validation_path.is_absolute() else ROOT / args.validation_path
    checks = 0
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    outputs = outputs_from_ast()
    check(len(outputs) == 20 and len(set(outputs)) == 20, "runner output contract differs")
    for name in outputs:
        check((artifacts / name).is_file(), f"missing artifact {name}")
    check(REPORT.is_file(), "missing report")

    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    check(len(locks) == 14, "source lock count differs")
    for row in locks:
        path = Path(row["path"])
        check(not path.is_absolute() and ".." not in path.parts, f"unsafe lock path {path}")
        full = ROOT / path
        check(full.is_file(), f"missing locked source {path}")
        if full.is_file():
            check(sha256(full) == row["expected_sha256"], f"source hash differs {path}")

    family_specs = read_tsv(SRC / "RIGHT_COMPLEMENT_SPECS.tsv")
    extension_specs = read_tsv(SRC / "SLOT_ONLY_EXTENSION_SPECS.tsv")
    anchors = read_tsv(SRC / "PREDECESSOR_CONTROL_SPECS.tsv")
    family_by = {row["surface"]: row for row in family_specs}
    extension_by = {row["surface"]: row for row in extension_specs}
    check(len(family_specs) == 13 and {row["surface"] for row in family_specs} == FAMILY, "family spec differs")
    check(len(extension_specs) == 4 and {row["surface"] for row in extension_specs} == {"al", "dain", "or", "chol"}, "extension spec differs")
    check(len(anchors) == 16 and len({row["surface"] for row in anchors}) == 16, "anchor deck differs")
    check(all(row["component_export_credit"] == "0" for row in family_specs + extension_specs + anchors), "authored component credit found")
    card_rows = read_tsv(G734)
    cards: dict[str, dict[str, str]] = {}
    for authored in family_specs + extension_specs:
        matches = [row for row in card_rows if row["surface"] == authored["surface"]
                   and row["v99r7_spoken_default_de"] == authored["expected_whole_default_de"]
                   and row["working_model_level"] == authored["expected_whole_level"]]
        check(len(matches) == 1, f"GDT734 whole-card binding differs for {authored['surface']}")
        if len(matches) == 1:
            cards[authored["surface"]] = matches[0]
    state_by_surface: dict[str, dict[str, str]] = {}
    for prior in read_tsv(G762_STATES):
        for side in ("dry", "moist"):
            state_by_surface[prior[f"{side}_surface"]] = {
                "state_pair_id": prior["pair_id"], "state_pair_role": prior["pair_role"],
                "state_prior_candidate_de": prior[f"{side}_working_candidate_de"],
                "state_prior_confidence": prior["working_confidence"],
                "state_prior_counterevidence": prior["counterevidence"],
            }
    check({surface: state_by_surface[surface]["state_pair_id"] for surface in
           ("chy", "chey", "cheey", "chdy", "chedy", "sheey", "shedy")} == {
               "chy": "SP02", "chey": "SP03", "cheey": "SP04", "chdy": "SP05",
               "chedy": "SP06", "sheey": "SP04", "shedy": "SP06",
           }, "GDT762 state-pair bindings differ")
    later_olaiin_rows = [row for row in read_tsv(G737_CANDIDATES) if row["body"] == "olaiin"]
    check(len(later_olaiin_rows) == 1, "GDT737 olaiin rival row differs")
    later_olaiin = later_olaiin_rows[0]
    check(later_olaiin["concrete_body_role_de"] == "Materialträger: Wert III"
          and "OLD_ABSOLUTE_NUMBER_UNSUPPORTED" in later_olaiin["counterevidence"],
          "GDT737 olaiin rival content differs")
    upstream_757 = {row["surface"]: row for row in read_tsv(G757_CONTROLS)}
    upstream_768 = {row["surface"]: row for row in read_tsv(G768_CONTROLS)}
    check(upstream_768["dair"]["anchor_class"] == "MEASURED_FRACTION_CONTROL_WITH_OLD_ROOT_RIVAL",
          "dair upstream mixed-control role differs")
    check(upstream_757["pol"]["primary_role_id"] == "ENTRY_HEADING"
          and upstream_757["polaiin"]["primary_role_id"] == "ENTRY_HEADING"
          and "no noun is identified" in upstream_757["polaiin"]["counterevidence"],
          "pol/polaiin upstream heading caveat differs")
    for path in (SRC / "RIGHT_COMPLEMENT_SPECS.tsv", SRC / "SLOT_ONLY_EXTENSION_SPECS.tsv", SRC / "PREDECESSOR_CONTROL_SPECS.tsv"):
        text = path.read_text(encoding="utf-8")
        check(not re.search(r"\bf(?:\d+|Ros)[rv]?\d*\.", text), f"occurrence locator leaked into policy {path.name}")
        check("G769-T" not in text and "G772-OL" not in text, f"occurrence id leaked into policy {path.name}")

    ol_rows = read_tsv(G774)
    check(len(ol_rows) == 376 and len({row["target_occurrence_id"] for row in ol_rows}) == 376, "ol universe differs")
    check(not any(row["page"].startswith("f84") for row in ol_rows), "forbidden page in target universe")
    fallback = [row for row in ol_rows if row["automatic_contextual"] == "0"]
    no_signature = [row for row in fallback if row["any_direct_signature"] == "0"]
    clean = [row for row in no_signature if row["hybrid_contextual"] == "0"]
    alternate_clean = [row for row in no_signature if row["calibration_case_id"] == "NONE"]
    check((len(fallback), len(no_signature), len(clean)) == (327, 311, 305), "327/311/305 chain differs")
    check({row["target_occurrence_id"] for row in clean} == {row["target_occurrence_id"] for row in alternate_clean}, "clean selectors are not equivalent")

    module = load_core()
    _g764, environment = module.load_guarded_environment(ROOT)
    check(dict(environment["guard"]) == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard counts differ")
    context = environment["context"]
    clean_ids = {row["target_occurrence_id"] for row in clean}
    target_all: list[dict[str, object]] = []
    target_clean: list[dict[str, object]] = []
    family_counts: Counter[str] = Counter()
    family_pages: dict[str, set[str]] = {surface: set() for surface in FAMILY}
    family_folios: dict[str, set[str]] = {surface: set() for surface in FAMILY}
    family_registers: dict[str, set[tuple[str, str, str]]] = {surface: set() for surface in FAMILY}
    left_written = right_written = left_exact = right_exact = 0
    for row in ol_rows:
        left, le = neighbor(row, context, -1)
        right, right_is_exact = neighbor(row, context, 1)
        left_written += int(left in FAMILY)
        right_written += int(right in FAMILY)
        left_exact += int(left in FAMILY and le)
        right_exact += int(right in FAMILY and right_is_exact)
        if row["automatic_contextual"] == "0" and right_is_exact:
            edge = {"page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
                    "section": row["section"], "language": row["language"], "hand": row["hand"],
                    "right_surface": right, "target_occurrence_id": row["target_occurrence_id"],
                    "predecessor_ordinal": int(row["ordinal"]), "right_ordinal": int(row["ordinal"]) + 1,
                    "predecessor_surface": "ol", "predecessor_line_position": row["line_position"]}
            target_all.append(edge)
            if row["target_occurrence_id"] in clean_ids:
                target_clean.append(edge)
                if right in FAMILY:
                    family_counts[right] += 1
                    family_pages[right].add(row["page"])
                    family_folios[right].add(row["physical_folio"])
                    family_registers[right].add((row["section"], row["language"], row["hand"]))
    check((len(target_all), len(target_clean)) == (221, 203), "exact-right target counts differ")
    check(dict(family_counts) == EXPECTED_FAMILY, "13-family count vector differs")
    check((left_written, right_written, left_exact, right_exact) == (36, 94, 27, 77), "family orientation differs")
    expected_primary = {"aiin", "chedy", "chey", "cheey", "daiin", "kaiin", "shedy", "okaiin", "olaiin", "oiin", "chdy"}
    check({row["surface"] for row in family_specs if row["family_tier"] == "PRIMARY"} == expected_primary, "primary surfaces differ")
    check(sum(family_counts[surface] for surface in expected_primary) == 57, "primary occurrence total differs")
    check(sum(family_counts[surface] for surface in FAMILY - expected_primary) == 9, "extension occurrence total differs")

    bigrams: list[dict[str, object]] = []
    for locus in sorted(context.by_line):
        line = context.by_line[locus]
        for index in range(len(line) - 1):
            left, right = line[index], line[index + 1]
            if not context.exact[(locus, int(left["token_index"]))] or not context.exact[(locus, int(right["token_index"]))]:
                continue
            page = str(left["page"])
            bigrams.append({"page": page, "physical_folio": physical_folio(page), "locus": locus,
                            "predecessor_ordinal": index + 1, "right_ordinal": index + 2,
                            "predecessor_surface": str(left["eva"]), "right_surface": str(right["eva"]),
                            "predecessor_line_position": "FIRST" if index == 0 else "MIDDLE"})
    check(len(bigrams) == 16657, "bigram count differs")
    check(len({(row["predecessor_surface"], row["right_surface"]) for row in bigrams}) == 14395, "pair-type count differs")
    check(len({row["predecessor_surface"] for row in bigrams}) == 3488, "predecessor surface count differs")
    check(len({row["right_surface"] for row in bigrams}) == 3393, "right surface count differs")
    check(len({row["locus"] for row in bigrams}) == 3584 and len({row["physical_folio"] for row in bigrams}) == 90, "bigram locus/folio count differs")
    anchor_edges = [row for row in bigrams if row["predecessor_surface"] in EXPECTED_ANCHORS]
    anchor_counts = Counter(str(row["predecessor_surface"]) for row in anchor_edges)
    check(dict(anchor_counts) == EXPECTED_ANCHORS, "anchor outgoing counts differ")

    classes = {
        "CORE_6_PLUS_6": {
            "NOMINAL_HEAD": ("chor", "shor", "cthy", "dair", "ofchy", "schor"),
            "FIELD_OPERATOR": ("ychor", "ycheol", "ychol", "dcheol", "qokchor", "ycheor"),
        },
        "EXPANDED_8_PLUS_8": {
            "NOMINAL_HEAD": ("chor", "shor", "cthy", "dair", "ofchy", "schor", "pol", "polaiin"),
            "FIELD_OPERATOR": ("ychor", "ycheol", "ychol", "dcheol", "qokchor", "ycheor", "pchor", "tshol"),
        },
    }

    fallback_right_counts = Counter(str(row["right_surface"]) for row in target_all)

    def slot_evidence(surface: str) -> tuple[str, str]:
        mass: dict[tuple[str, str], float] = {}
        support_surfaces: dict[tuple[str, str], int] = {}
        support_folios: dict[tuple[str, str], int] = {}
        for deck, deck_classes in classes.items():
            for anchor_class, surfaces in deck_classes.items():
                selected = [row for row in anchor_edges if row["predecessor_surface"] in surfaces
                            and row["right_surface"] == surface]
                key = (deck, anchor_class)
                mass[key] = sum(
                    sum(1 for row in selected if row["predecessor_surface"] == anchor) /
                    anchor_counts[anchor] / len(surfaces) for anchor in surfaces
                )
                support_surfaces[key] = len({row["predecessor_surface"] for row in selected})
                support_folios[key] = len({row["physical_folio"] for row in selected})
        deltas = [mass[(deck, "NOMINAL_HEAD")] - mass[(deck, "FIELD_OPERATOR")] for deck in classes]
        direction = "NOMINAL_HEAD" if all(value > 0 for value in deltas) else \
                    "FIELD_OPERATOR" if all(value < 0 for value in deltas) else \
                    "DECK_FLIP" if deltas[0] * deltas[1] < 0 else "UNINFORMATIVE"
        strong = direction in {"NOMINAL_HEAD", "FIELD_OPERATOR"} and fallback_right_counts[surface] >= 2
        if strong:
            loser = "FIELD_OPERATOR" if direction == "NOMINAL_HEAD" else "NOMINAL_HEAD"
            for deck in classes:
                win, lose = mass[(deck, direction)], mass[(deck, loser)]
                ratio = math.inf if win > 0 and lose == 0 else win / lose if lose else 0.0
                strong = strong and ratio >= 2.0
                strong = strong and support_surfaces[(deck, direction)] >= 2
                strong = strong and support_folios[(deck, direction)] >= 2
        tier = "TIER_A_STABLE" if strong else "LEAD_ONLY" if direction in {"NOMINAL_HEAD", "FIELD_OPERATOR"} else direction
        return direction, tier

    target_vector = Counter(str(row["right_surface"]) for row in target_clean)
    observed_vectors = {(row["target_cohort"], row["deck"]): row for row in read_tsv(artifacts / "PREDECESSOR_VECTOR_COMPARISON.tsv")}
    target_positions = Counter(str(row["predecessor_line_position"]) for row in target_clean)
    check(target_positions == {"FIRST": 20, "MIDDLE": 183}, "target position vector differs")
    for deck, deck_classes in classes.items():
        values: dict[str, float] = {}
        equalized: dict[str, float] = {}
        positions: dict[str, Counter[str]] = {}
        capacities: dict[str, int] = {}
        for anchor_class, surfaces in deck_classes.items():
            selected = [row for row in anchor_edges if row["predecessor_surface"] in surfaces]
            capacities[anchor_class] = len(selected)
            positions[anchor_class] = Counter(str(row["predecessor_line_position"]) for row in selected)
            vector = Counter(str(row["right_surface"]) for row in selected)
            values[anchor_class] = cosine(target_vector, vector)
            averaged = mean_surface_vector(anchor_edges, surfaces)
            equalized[anchor_class] = cosine(target_vector, averaged)
        artifact_row = observed_vectors[("NOVEL_203", deck)]
        check(abs(float(artifact_row["nominal_raw_cosine"]) - values["NOMINAL_HEAD"]) <= 5e-9, f"{deck} nominal cosine differs")
        check(abs(float(artifact_row["operator_raw_cosine"]) - values["FIELD_OPERATOR"]) <= 5e-9, f"{deck} operator cosine differs")
        check(abs(float(artifact_row["nominal_surface_equalized_cosine"]) - equalized["NOMINAL_HEAD"]) <= 5e-9, f"{deck} equalized nominal differs")
        check(abs(float(artifact_row["operator_surface_equalized_cosine"]) - equalized["FIELD_OPERATOR"]) <= 5e-9, f"{deck} equalized operator differs")
        check(values["NOMINAL_HEAD"] > values["FIELD_OPERATOR"] and equalized["NOMINAL_HEAD"] > equalized["FIELD_OPERATOR"], f"{deck} winner differs")
        check(int(artifact_row["target_first_edges"]) == target_positions["FIRST"]
              and int(artifact_row["target_middle_edges"]) == target_positions["MIDDLE"], f"{deck} target position fields differ")
        check(int(artifact_row["nominal_edges"]) == capacities["NOMINAL_HEAD"]
              and int(artifact_row["operator_edges"]) == capacities["FIELD_OPERATOR"], f"{deck} control capacities differ")
        check(int(artifact_row["nominal_first_edges"]) == positions["NOMINAL_HEAD"]["FIRST"]
              and int(artifact_row["nominal_middle_edges"]) == positions["NOMINAL_HEAD"]["MIDDLE"]
              and int(artifact_row["operator_first_edges"]) == positions["FIELD_OPERATOR"]["FIRST"]
              and int(artifact_row["operator_middle_edges"]) == positions["FIELD_OPERATOR"]["MIDDLE"], f"{deck} control positions differ")
        check(artifact_row["position_confound_status"] == "SEVERE_FIRST_MIDDLE_CLASS_IMBALANCE", f"{deck} confound label differs")

    frame_counts = {"FALLBACK_327": Counter(), "NOVEL_305": Counter()}
    for row in fallback:
        left, le = neighbor(row, context, -1)
        right, right_is_exact = neighbor(row, context, 1)
        if le and right_is_exact:
            frame_counts["FALLBACK_327"][f"{left}|ol|{right}"] += 1
            if row["target_occurrence_id"] in clean_ids:
                frame_counts["NOVEL_305"][f"{left}|ol|{right}"] += 1
    check((sum(frame_counts["FALLBACK_327"].values()), len(frame_counts["FALLBACK_327"])) == (167, 166), "fallback frame counts differ")
    check((sum(frame_counts["NOVEL_305"].values()), len(frame_counts["NOVEL_305"])) == (151, 150), "novel frame counts differ")
    check({key: n for key, n in frame_counts["NOVEL_305"].items() if n > 1} == {"chey|ol|aiin": 2}, "repeated frame differs")

    cross = {row["locus"]: row for row in guarded_cross([row["page"] for row in ol_rows])}
    audited = variants = all_separated = exact_audited = selected_audited = selected_fusions = 0
    for row in ol_rows:
        right, right_is_exact = neighbor(row, context, 1)
        if right not in BOUNDARY:
            continue
        audited += 1
        exact_audited += int(right_is_exact)
        selected = right_is_exact and row["target_occurrence_id"] in clean_ids
        selected_audited += int(selected)
        source = cross[row["locus"]]
        modes = [boundary_mode(source[name], right) for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        variant = int(modes[0] == "SEPARATED_EXACT" and sorted(modes[1:]) == ["FUSED_EXACT", "SEPARATED_EXACT"])
        variants += variant
        selected_fusions += int(selected and variant)
        all_separated += int(set(modes) == {"SEPARATED_EXACT"})
    check((audited, variants, all_separated) == (19, 3, 16), "boundary audit differs")
    check((exact_audited, selected_audited, selected_fusions) == (16, 14, 0), "selected boundary scope differs")

    atlas = read_tsv(artifacts / "OL_327_RIGHT_COMPLEMENT_ATLAS.tsv")
    renderer = read_tsv(artifacts / "GDT775_376_RENDERER.tsv")
    roles = read_tsv(artifacts / "RIGHT_COMPLEMENT_13_ROLE_REGISTRY.tsv")
    slot = read_tsv(artifacts / "SLOT_ONLY_EXTENSION_AUDIT.tsv")
    dictionary = read_tsv(artifacts / "GDT775_WORKING_DICTIONARY.tsv")
    holdouts = read_tsv(artifacts / "PREDECESSOR_FOLIO_HOLDOUT.tsv")
    drop_audit = read_tsv(artifacts / "PREDECESSOR_TARGET_DROP_AUDIT.tsv")
    boundary_artifact = read_tsv(artifacts / "CROSS_READER_BOUNDARY_AUDIT.tsv")
    crosswalk = read_tsv(artifacts / "GDT775_RELATION_EDGE_CROSSWALK.tsv")
    check(len(atlas) == 327 and len({row["target_occurrence_id"] for row in atlas}) == 327, "fallback atlas rows differ")
    check(Counter(row["dispatch_branch"] for row in atlas) == {"GENERIC_NOMINAL_FALLBACK": 253, "RIGHT_COMPLETE_13_FAMILY": 66, "SLOT_ONLY_WHOLE_EXTENSION": 8}, "fallback dispatch differs")
    atlas_by_id = {row["target_occurrence_id"]: row for row in atlas}
    check(set(atlas_by_id) == {row["target_occurrence_id"] for row in fallback}, "atlas target set differs")
    for source in fallback:
        actual = atlas_by_id[source["target_occurrence_id"]]
        left, left_is_exact = neighbor(source, context, -1)
        right, right_is_exact = neighbor(source, context, 1)
        novel = source["target_occurrence_id"] in clean_ids
        selected_family = family_by.get(right) if novel and right_is_exact else None
        selected_slot = extension_by.get(right) if novel and right_is_exact else None
        branch = "RIGHT_COMPLETE_13_FAMILY" if selected_family else \
                 "SLOT_ONLY_WHOLE_EXTENSION" if selected_slot else "GENERIC_NOMINAL_FALLBACK"
        selected = selected_family or selected_slot
        expected = {
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "ordinal": source["ordinal"], "left_surface": left, "left_reader_exact": str(int(left_is_exact)),
            "right_surface": right, "right_ordinal": str(int(source["ordinal"]) + 1 if right != "NONE" else 0),
            "right_reader_exact": str(int(right_is_exact)), "automatic_contextual": source["automatic_contextual"],
            "any_direct_signature": source["any_direct_signature"], "calibration_case_id": source["calibration_case_id"],
            "hybrid_contextual": source["hybrid_contextual"], "no_direct_signature": str(int(source["any_direct_signature"] == "0")),
            "not_calibration_case": str(int(source["calibration_case_id"] == "NONE")), "novel_305_member": str(int(novel)),
            "dispatch_branch": branch, "register_id": f"{source['section']}|{source['language']}|{source['hand']}",
            "family_tier": selected_family["family_tier"] if selected_family else "NONE",
            "semantic_class": selected["semantic_class"] if selected else "NONE",
            "portable_span_de": selected["portable_span_de"] if selected else FALLBACK,
            "fluent_span_de": selected["fluent_span_de"] if selected else FALLBACK,
            "construction_confidence": selected["construction_confidence"] if selected else "C0_CONTEXT_UNRESOLVED",
            "scope_status": selected["scope_status"] if selected else "NONE",
            "specific_counterevidence_de": selected["specific_counterevidence_de"] if selected else "NONE",
            "adjacent_left_ol_collision": str(int(left == "ol")),
        }
        for field, value in expected.items():
            check(actual[field] == value, f"atlas dispatch differs {source['target_occurrence_id']}:{field}")

    check(len(renderer) == 376 and len({row["target_occurrence_id"] for row in renderer}) == 376, "renderer rows differ")
    check(sum(row["family_renderer_contextual"] == "1" for row in renderer) == 115, "family renderer count differs")
    check(sum(row["throughput_renderer_contextual"] == "1" for row in renderer) == 123, "throughput renderer count differs")
    check(sum(row["hybrid_throughput_contextual"] == "1" for row in renderer) == 129, "hybrid renderer count differs")
    renderer_by_id = {row["target_occurrence_id"]: row for row in renderer}
    check(set(renderer_by_id) == {row["target_occurrence_id"] for row in ol_rows}, "renderer target set differs")
    consumed_token_ids: set[str] = set()
    for source in ol_rows:
        actual = renderer_by_id[source["target_occurrence_id"]]
        right, right_is_exact = neighbor(source, context, 1)
        left, _left_is_exact = neighbor(source, context, -1)
        novel = source["target_occurrence_id"] in clean_ids
        family = source["automatic_contextual"] == "0" and novel and right_is_exact and right in family_by
        extension = source["automatic_contextual"] == "0" and novel and right_is_exact and right in extension_by
        selected = family_by[right] if family else extension_by[right] if extension else None
        consumes = family or extension
        right_ordinal = int(source["ordinal"]) + 1 if right != "NONE" else 0
        expected_confidence = (
            "C0_ADJACENT_OL_COLLISION__FAMILY_RETAINED" if family and left == "ol"
            else selected["construction_confidence"] if selected else source["automatic_confidence"]
        )
        expected = {
            "right_surface": right, "right_ordinal": str(right_ordinal), "right_reader_exact": str(int(right_is_exact)),
            "gdt774_automatic_branch": source["automatic_branch"],
            "gdt774_automatic_default_de": source["automatic_default_de"],
            "family_branch": "RIGHT_COMPLETE_13_FAMILY" if family else "INHERITED_GDT774",
            "family_renderer_default_de": selected["fluent_span_de"] if family else source["automatic_default_de"],
            "family_renderer_contextual": str(int(source["automatic_contextual"] == "1" or family)),
            "throughput_branch": "SLOT_ONLY_WHOLE_EXTENSION" if extension else "RIGHT_COMPLETE_13_FAMILY" if family else "INHERITED_GDT774",
            "throughput_renderer_default_de": selected["fluent_span_de"] if consumes else source["automatic_default_de"],
            "throughput_renderer_contextual": str(int(source["automatic_contextual"] == "1" or consumes)),
            "hybrid_throughput_default_de": selected["fluent_span_de"] if consumes else source["hybrid_default_de"],
            "hybrid_throughput_contextual": str(int(source["hybrid_contextual"] == "1" or consumes)),
            "family_span_consumes_right_token": str(int(family)),
            "throughput_span_consumes_right_token": str(int(consumes)),
            "hybrid_throughput_span_consumes_right_token": str(int(consumes)),
            "family_span_id": f"G775-FAMILY-SPAN:{source['target_occurrence_id']}" if family else "NONE",
            "throughput_span_id": f"G775-THROUGHPUT-SPAN:{source['target_occurrence_id']}" if consumes else "NONE",
            "throughput_right_token_id": f"{source['locus']}@{right_ordinal}" if consumes else "NONE",
            "construction_confidence": expected_confidence,
        }
        for field, value in expected.items():
            check(actual[field] == value, f"renderer dispatch differs {source['target_occurrence_id']}:{field}")
        if consumes:
            check(actual["throughput_right_token_id"] not in consumed_token_ids,
                  f"right token consumed twice {actual['throughput_right_token_id']}")
            consumed_token_ids.add(actual["throughput_right_token_id"])
    check(len(consumed_token_ids) == 74, "consumed right-token count differs")
    check(len(roles) == 13 and sum(int(row["selected_occurrences"]) for row in roles) == 66, "role registry differs")
    role_by_surface = {row["surface"]: row for row in roles}
    for surface, spec in family_by.items():
        actual = role_by_surface[surface]
        selected_rows = [row for row in atlas if row["dispatch_branch"] == "RIGHT_COMPLETE_13_FAMILY"
                         and row["right_surface"] == surface]
        registers = {(row["section"], row["language"], row["hand"]) for row in selected_rows}
        card = cards[surface]
        threshold = (card["working_model_level"].startswith(("W2_", "W3_"))
                     and len(selected_rows) >= 3
                     and len({row["physical_folio"] for row in selected_rows}) >= 3
                     and len(registers) >= 2)
        direction, tier = slot_evidence(surface)
        expected = {
            "semantic_class": spec["semantic_class"], "portable_span_de": spec["portable_span_de"],
            "fluent_span_de": spec["fluent_span_de"], "strongest_rival_de": spec["strongest_rival_de"],
            "family_tier": "PRIMARY" if threshold else "EXTENSION",
            "construction_confidence": spec["construction_confidence"], "scope_status": spec["scope_status"],
            "specific_counterevidence_de": spec["specific_counterevidence_de"],
            "whole_default_de": card["v99r7_spoken_default_de"], "whole_level": card["working_model_level"],
            "tier_threshold_pass": str(int(threshold)),
            "tier_basis": "WHOLE_W2_OR_W3__TOKENS_GE3__FOLIOS_GE3__REGISTERS_GE2",
            "selected_occurrences": str(len(selected_rows)),
            "pages": str(len({row["page"] for row in selected_rows})),
            "physical_folios": str(len({row["physical_folio"] for row in selected_rows})),
            "loci": str(len({row["locus"] for row in selected_rows})), "registers": str(len(registers)),
            "predecessor_slot_direction": direction, "predecessor_slot_tier": tier,
        }
        state_prior = state_by_surface.get(surface)
        for field in ("state_pair_id", "state_pair_role", "state_prior_candidate_de",
                      "state_prior_confidence", "state_prior_counterevidence"):
            expected[field] = state_prior[field] if state_prior else "NONE"
        expected["later_rival_source"] = "GDT737" if surface == "olaiin" else "NONE"
        expected["later_rival_candidate_de"] = later_olaiin["concrete_body_role_de"] if surface == "olaiin" else "NONE"
        expected["later_rival_counterevidence"] = later_olaiin["counterevidence"] if surface == "olaiin" else "NONE"
        for field, value in expected.items():
            check(actual[field] == value, f"role registry differs {surface}:{field}")
    check(role_by_surface["daiin"]["scope_status"] == "GDT775_EXPLORATORY_SCOPE_EXTENSION"
          and role_by_surface["daiin"]["construction_confidence"].startswith("C0_"), "daiin scope extrapolation hidden")
    check("GDT737" in role_by_surface["olaiin"]["specific_counterevidence_de"]
          and role_by_surface["olaiin"]["construction_confidence"].startswith("C0_"), "olaiin later rival hidden")
    check("GDT762" in role_by_surface["cheey"]["specific_counterevidence_de"], "cheey later rival hidden")
    check(len(slot) == 4 and sum(int(row["selected_occurrences"]) for row in slot) == 8, "slot extension differs")
    slot_by_surface = {row["surface"]: row for row in slot}
    for surface, spec in extension_by.items():
        actual = slot_by_surface[surface]
        selected_rows = [row for row in atlas if row["dispatch_branch"] == "SLOT_ONLY_WHOLE_EXTENSION"
                         and row["right_surface"] == surface]
        direction, tier = slot_evidence(surface)
        expected = {
            "semantic_class": spec["semantic_class"], "portable_span_de": spec["portable_span_de"],
            "fluent_span_de": spec["fluent_span_de"], "strongest_rival_de": spec["strongest_rival_de"],
            "whole_default_de": cards[surface]["v99r7_spoken_default_de"],
            "whole_level": cards[surface]["working_model_level"],
            "selected_occurrences": str(len(selected_rows)),
            "pages": str(len({row["page"] for row in selected_rows})),
            "physical_folios": str(len({row["physical_folio"] for row in selected_rows})),
            "predecessor_slot_direction": direction, "predecessor_slot_tier": tier,
            "construction_confidence": spec["construction_confidence"], "scope_status": spec["scope_status"],
            "specific_counterevidence_de": spec["specific_counterevidence_de"],
        }
        for field, value in expected.items():
            check(actual[field] == value, f"slot extension differs {surface}:{field}")
    check(slot_by_surface["dain"]["scope_status"] == "GDT775_EXPLORATORY_SCOPE_EXTENSION"
          and slot_by_surface["dain"]["construction_confidence"].startswith("C0_"), "dain scope extrapolation hidden")
    check({(row["surface"], row["predecessor_slot_direction"], row["predecessor_slot_tier"]) for row in slot} == {
        ("al", "NOMINAL_HEAD", "TIER_A_STABLE"), ("dain", "NOMINAL_HEAD", "TIER_A_STABLE"),
        ("or", "NOMINAL_HEAD", "TIER_A_STABLE"), ("chol", "FIELD_OPERATOR", "TIER_A_STABLE")}, "slot directions differ")
    check(len(dictionary) == 18, "working dictionary row count differs")
    check(len(holdouts) == 110 and all(row["winner"] == "NOMINAL_HEAD" for row in holdouts), "folio holdouts differ")
    holdout_by_key = {(row["held_physical_folio"], row["deck"]): row for row in holdouts}
    expected_holdout_keys: set[tuple[str, str]] = set()
    for folio in sorted({str(row["physical_folio"]) for row in target_clean}):
        target = Counter(str(row["right_surface"]) for row in target_clean if row["physical_folio"] != folio)
        for deck, deck_classes in classes.items():
            expected_holdout_keys.add((folio, deck))
            scores: dict[str, float] = {}
            for anchor_class, surfaces in deck_classes.items():
                control = Counter(str(row["right_surface"]) for row in anchor_edges
                                  if row["physical_folio"] != folio and row["predecessor_surface"] in surfaces)
                scores[anchor_class] = cosine(target, control)
            actual = holdout_by_key[(folio, deck)]
            check(int(actual["remaining_target_edges"]) == sum(target.values()), f"sensitivity edge count differs {folio}:{deck}")
            check(abs(float(actual["nominal_raw_cosine"]) - scores["NOMINAL_HEAD"]) <= 5e-9,
                  f"sensitivity nominal score differs {folio}:{deck}")
            check(abs(float(actual["operator_raw_cosine"]) - scores["FIELD_OPERATOR"]) <= 5e-9,
                  f"sensitivity operator score differs {folio}:{deck}")
            check(abs(float(actual["delta_nominal_minus_operator"]) -
                      (scores["NOMINAL_HEAD"] - scores["FIELD_OPERATOR"])) <= 5e-9,
                  f"sensitivity delta differs {folio}:{deck}")
    check(set(holdout_by_key) == expected_holdout_keys, "sensitivity key universe differs")

    drop_scenarios = {
        "BASELINE": frozenset(), "DROP_DAIIN": frozenset({"daiin"}),
        "DROP_DAIIN_AND_AIIN": frozenset({"daiin", "aiin"}),
        "DROP_FIXED_13_FAMILY": FAMILY,
    }
    drop_by_key = {(row["scenario"], row["deck"]): row for row in drop_audit}
    check(len(drop_audit) == 8 and len(drop_by_key) == 8, "target-drop audit row count differs")
    for scenario, dropped in drop_scenarios.items():
        retained = [row for row in target_clean if row["right_surface"] not in dropped]
        vector = Counter(str(row["right_surface"]) for row in retained)
        for deck, deck_classes in classes.items():
            scores = {anchor_class: cosine(vector, mean_surface_vector(anchor_edges, surfaces))
                      for anchor_class, surfaces in deck_classes.items()}
            actual = drop_by_key[(scenario, deck)]
            check(int(actual["dropped_target_tokens"]) == len(target_clean) - len(retained)
                  and int(actual["remaining_target_edges"]) == len(retained)
                  and int(actual["remaining_right_types"]) == len(vector), f"target-drop counts differ {scenario}:{deck}")
            check(abs(float(actual["nominal_surface_equalized_cosine"]) - scores["NOMINAL_HEAD"]) <= 5e-9,
                  f"target-drop nominal score differs {scenario}:{deck}")
            check(abs(float(actual["operator_surface_equalized_cosine"]) - scores["FIELD_OPERATOR"]) <= 5e-9,
                  f"target-drop operator score differs {scenario}:{deck}")
            expected_winner = "NOMINAL_HEAD" if scores["NOMINAL_HEAD"] > scores["FIELD_OPERATOR"] else "FIELD_OPERATOR"
            check(actual["winner"] == expected_winner, f"target-drop winner differs {scenario}:{deck}")
    check(drop_by_key[("DROP_DAIIN", "CORE_6_PLUS_6")]["winner"] == "FIELD_OPERATOR"
          and drop_by_key[("DROP_FIXED_13_FAMILY", "CORE_6_PLUS_6")]["winner"] == "FIELD_OPERATOR"
          and drop_by_key[("DROP_FIXED_13_FAMILY", "EXPANDED_8_PLUS_8")]["winner"] == "FIELD_OPERATOR",
          "target-type sensitivity is hidden")
    boundary_by_id = {row["target_occurrence_id"]: row for row in boundary_artifact}
    expected_boundary_ids: set[str] = set()
    for source_row in ol_rows:
        right, right_is_exact = neighbor(source_row, context, 1)
        if right not in BOUNDARY:
            continue
        target_id = source_row["target_occurrence_id"]
        expected_boundary_ids.add(target_id)
        actual = boundary_by_id[target_id]
        source = cross[source_row["locus"]]
        modes = {name: boundary_mode(source[name + "_clean"], right) for name in ("zl3b", "it2a", "rf1b")}
        variant = int(modes["zl3b"] == "SEPARATED_EXACT" and
                      sorted((modes["it2a"], modes["rf1b"])) == ["FUSED_EXACT", "SEPARATED_EXACT"])
        all_sep = int(set(modes.values()) == {"SEPARATED_EXACT"})
        selected = right_is_exact and target_id in clean_ids
        expected = {
            "right_ordinal": str(int(source_row["ordinal"]) + 1), "right_surface": right,
            "right_reader_exact": str(int(right_is_exact)),
            "automatic_fallback": str(int(source_row["automatic_contextual"] == "0")),
            "clean_305_member": str(int(target_id in clean_ids)), "family_66_member": str(int(selected)),
            "all_three_present": source["all_three_present"], "zl3b_mode": modes["zl3b"],
            "it2a_mode": modes["it2a"], "rf1b_mode": modes["rf1b"],
            "one_sided_fusion_variant": str(variant), "all_three_separated": str(all_sep),
            "interpretation": "LOCAL_BOUNDARY_UNCERTAINTY" if variant else "STABLE_SEPARATION",
            "pair_search_scope": "LINE_GLOBAL_SINGLE_FORM", "independent_witness_count": "1",
        }
        for field, value in expected.items():
            check(actual[field] == value, f"boundary audit differs {target_id}:{field}")
    check(set(boundary_by_id) == expected_boundary_ids, "boundary target universe differs")
    check(sum(row["family_66_member"] == "1" for row in boundary_artifact) == 14
          and not any(row["one_sided_fusion_variant"] == "1" and row["family_66_member"] == "1"
                      for row in boundary_artifact), "selected boundary fusion claim differs")
    check(sum(row["construction_confidence"] == "C0_ADJACENT_OL_COLLISION__FAMILY_RETAINED" for row in renderer) == 3, "adjacent-ol family collisions not exposed")
    models = {row["model_id"]: row for row in read_tsv(artifacts / "RIGHT_COMPLEMENT_MODEL_SCORE.tsv")}
    check(models["M02_STATUS_FORM_CONNECTOR"]["core_predecessor_cosine"] == "NOT_SCORED"
          and models["M02_STATUS_FORM_CONNECTOR"]["expanded_predecessor_cosine"] == "NOT_SCORED", "unscored connector encoded as zero")
    check(models["M01_NOMINAL_HEAD_PLUS_COMPLETE_WHOLE"]["selection_basis"] == "EXPLORATORY_THROUGHPUT_RENDERER_CONVENTION"
          and models["M01_NOMINAL_HEAD_PLUS_COMPLETE_WHOLE"]["robustness_status"] == "NOT_ROBUST_TO_DAIIN_OR_FIXED_FAMILY_TARGET_DROP",
          "selected renderer model hides diagnostic status")
    check(all(row["selected_exact_fusion_variants"] == "0" for row in models.values()), "fusion incorrectly credited to selected spans")
    ol_dictionary = next(row for row in dictionary if row["entry"] == "ol")
    check(ol_dictionary["confidence"] == "C2_STRUCTURAL_C0_SEMANTIC_RENDERER"
          and "positionskonfundiert" in ol_dictionary["counterevidence"]
          and "nicht score-ready" in ol_dictionary["counterevidence"], "ol dictionary caveat differs")

    for path in artifacts.glob("*.tsv"):
        rows = read_tsv(path)
        for row in rows:
            for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit", "voynich_identity_credit", "lexeme_credit"):
                if field in row:
                    check(row[field] == "0", f"semantic credit in {path.name}:{field}")

    packet_path = artifacts / "GDT775_GDT388_RELATION_PACKET.tsv"
    packet_rows = read_tsv(packet_path)
    check(len(packet_rows) == 572 and len({row["edge_id"] for row in packet_rows}) == 572, "relation packet rows differ")
    check(len(crosswalk) == 572 and len({row["edge_id"] for row in crosswalk}) == 572, "relation crosswalk rows differ")
    expected_material = [("TARGET_SLOT", row) for row in target_clean] + [("ANCHOR_SLOT", row) for row in anchor_edges]
    expected_material.sort(key=lambda item: (str(item[1]["page"]), str(item[1]["locus"]),
                                             int(item[1]["predecessor_ordinal"]), item[0]))
    packet_by_id = {row["edge_id"]: row for row in packet_rows}
    crosswalk_by_id = {row["edge_id"]: row for row in crosswalk}
    for number, (batch, source_edge) in enumerate(expected_material, 1):
        edge_id = f"G775-E{number:04d}"
        packet_row, crosswalk_row = packet_by_id[edge_id], crosswalk_by_id[edge_id]
        expected_source = (source_edge["target_occurrence_id"] if batch == "TARGET_SLOT"
                           else f"ANCHOR:{source_edge['locus']}@{source_edge['predecessor_ordinal']}")
        expected = {
            "batch_id": f"GDT775_{batch}", "source_row_id": expected_source,
            "page": str(source_edge["page"]), "physical_folio": str(source_edge["physical_folio"]),
            "locus": str(source_edge["locus"]), "predecessor_ordinal": str(source_edge["predecessor_ordinal"]),
            "right_ordinal": str(source_edge["right_ordinal"]),
            "predecessor_surface": str(source_edge["predecessor_surface"]),
            "right_surface": str(source_edge["right_surface"]), "score_eligible": "0",
        }
        for field, value in expected.items():
            check(crosswalk_row[field] == value, f"relation crosswalk differs {edge_id}:{field}")
        check(packet_row["batch_id"] == f"GDT775_{batch}"
              and packet_row["page"] == str(source_edge["page"])
              and packet_row["physical_folio"] == str(source_edge["physical_folio"])
              and packet_row["pivot_locus"] == f"{source_edge['locus']}@{source_edge['predecessor_ordinal']}"
              and packet_row["target_locus"] == f"{source_edge['locus']}@{source_edge['right_ordinal']}",
              f"relation packet source binding differs {edge_id}")
    check(Counter(row["batch_id"] for row in crosswalk) == {"GDT775_TARGET_SLOT": 203, "GDT775_ANCHOR_SLOT": 369},
          "relation crosswalk batch counts differ")
    intake_done = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)], cwd=ROOT, text=True, capture_output=True, check=True)
    intake = json.loads(intake_done.stdout)
    check(intake["status"] == "VALID_ACQUISITION_NOT_SCORE_READY" and intake["packet_rows"] == 572 and intake["eligible_edges"] == 0 and not intake["errors"], "relation packet intake differs")
    check(json.loads((artifacts / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8")) == intake, "stored relation intake differs")

    result = json.loads((artifacts / "RESULT.json").read_text(encoding="utf-8"))
    check(result["status"] == "PASS__RENDERER_THROUGHPUT_66_PLUS_8__PREDECESSOR_DIAGNOSTIC_NOT_SCORE_READY__NO_PLAINTEXT", "result status differs")
    check(result["renderer"] == {"gdt774_automatic_contextual": 49, "family_contextual": 115, "family_fallback": 261,
                                 "throughput_contextual": 123, "throughput_fallback": 253,
                                 "hybrid_throughput_contextual": 129, "hybrid_throughput_fallback": 247}, "result renderer summary differs")
    check(result["right_family"]["right_exact"] == 77 and type(result["right_family"]["right_exact"]) is int,
          "result right-exact aggregate differs")
    check(result["right_family"]["orientation_status"] ==
          "DESCRIPTIVE_SELECTION_AWARE__FAMILY_AUTHORED_AS_RIGHT_COMPLEMENTS",
          "result selection-aware orientation label differs")
    check({key: result["right_family"][key] for key in (
        "individual_nominal_surfaces", "individual_nominal_tokens", "individual_operator_surfaces",
        "individual_operator_tokens", "individual_uninformative_surfaces", "individual_uninformative_tokens")
    } == {"individual_nominal_surfaces": 6, "individual_nominal_tokens": 33,
          "individual_operator_surfaces": 1, "individual_operator_tokens": 5,
          "individual_uninformative_surfaces": 6, "individual_uninformative_tokens": 28},
          "result individual slot summary differs")
    check(result["predecessor"]["comparison_status"] == "DESCRIPTIVE_NOT_SCORE_READY__POSITION_AND_TARGET_TYPE_SENSITIVE"
          and result["predecessor"]["position_confound_status"] == "SEVERE_FIRST_MIDDLE_CLASS_IMBALANCE"
          and result["predecessor"]["target_drop_robust"] is False
          and result["predecessor"]["decks_independent"] is False, "result predecessor caveat differs")
    check(result["predecessor"]["nominal_label_scope"] ==
          "AUTHORED_CONTENT_OR_RECORD_HEAD_MIX__INCLUDES_DAIR_MEASURE_FIELD_AND_POL_HEADINGS",
          "result nominal-label scope differs")
    check(result["predecessor"]["target_drop_audit"]["DROP_DAIIN__CORE_6_PLUS_6"]["winner"] == "FIELD_OPERATOR"
          and result["predecessor"]["target_drop_audit"]["DROP_FIXED_13_FAMILY__EXPANDED_8_PLUS_8"]["winner"] == "FIELD_OPERATOR",
          "result target-drop summary differs")
    check(result["boundary"]["selected_audited_pairs"] == 14
          and result["boundary"]["selected_fusion_variants"] == 0, "result selected boundary summary differs")
    check(result["relation_packet"]["score_ready"] is False and result["relation_packet"]["eligible_edges"] == 0,
          "result relation readiness differs")
    check(all(result[field] == 0 for field in ("confirmed_lexemes", "confirmed_plaintext_clauses", "component_exports", "new_pages", "new_images", "new_ocr", "new_transcriptions")), "result grants forbidden credit")

    replay_hashes: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="gdt775_replay_", dir=EXP) as temp_name:
        temp = Path(temp_name)
        replay_artifacts = temp / "artifacts"
        replay_report = temp / "REPORT.md"
        done = subprocess.run([
            "python3", "-B", str(RUN), "--artifacts-dir", str(replay_artifacts),
            "--report-path", str(replay_report),
        ], cwd=ROOT, text=True, capture_output=True)
        check(done.returncode == 0, "runner replay failed")
        for name in outputs:
            actual, replay = artifacts / name, replay_artifacts / name
            check(replay.is_file(), f"replay missing {name}")
            if actual.is_file() and replay.is_file():
                check(actual.read_bytes() == replay.read_bytes(), f"replay bytes differ {name}")
                replay_hashes[name] = sha256(replay)
        check(replay_report.is_file() and REPORT.read_bytes() == replay_report.read_bytes(), "report replay differs")

    status = "PASS" if not failures else "FAIL"
    validation = {
        "experiment_id": "GDT775", "status": status, "checks": checks,
        "failures": failures, "source_locks": len(locks), "runner_outputs": len(outputs),
        "runner_replay_byte_identical": not any("replay" in failure for failure in failures),
        "replay_sha256": replay_hashes,
        "independent_counts": {
            "ol": len(ol_rows), "fallback": len(fallback), "no_signature": len(no_signature),
            "clean": len(clean), "exact_right_all": len(target_all), "exact_right_clean": len(target_clean),
            "family": sum(family_counts.values()), "primary": sum(family_counts[s] for s in expected_primary),
            "family_extension": sum(family_counts[s] for s in FAMILY - expected_primary),
            "bigram_edges": len(bigrams), "boundary_pairs": audited, "boundary_fusions": variants,
        },
        "claim_ceiling_respected": not any(
            "semantic credit" in failure or "forbidden" in failure for failure in failures
        ),
    }
    write_target = validation_path
    write_target.parent.mkdir(parents=True, exist_ok=True)
    write_target.write_text(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
