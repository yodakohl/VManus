#!/usr/bin/env python3
"""Independent exactness, renderer, provenance, packet, and replay audit for GDT777."""

from __future__ import annotations

import ast
import csv
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Iterable, Mapping

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt777_ol_registered_split_fusion_composer"
SRC, ART = EXP / "src", EXP / "artifacts"
RUN, REPORT = SRC / "run.py", EXP / "REPORT.md"
G776 = ROOT / "experiments/yolo/gdt776_ol_h4_h3_medial_register_bridge/artifacts/GDT776_376_RENDERER.tsv"
G736 = ROOT / "experiments/yolo/gdt736_opaque_head_record_role_bridge/artifacts/OPAQUE_96_CONCRETE_ROLE_GRID.tsv"
G737 = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv"
G759_BOUND = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/QUANTITY_7_EXACT_BOUNDARY_BRIDGES.tsv"
G769_CORE = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py"
HEADS = frozenset({"p", "s", "r", "l"})
BANNED = re.compile(r"(?i)(pulver|samen|wurzel|holz|drogen)")

EXPECTED_SELECTED = frozenset({
    "G769-T0017", "G769-T0041", "G769-T0056", "G769-T0063", "G769-T0076",
    "G769-T0083", "G769-T0084", "G769-T0142", "G769-T0150", "G769-T0151",
    "G769-T0172", "G769-T0232", "G769-T0255", "G769-T0303", "G769-T0312",
    "G769-T0345", "G769-T0380", "G769-T0420", "G769-T0422", "G769-T0436",
    "G769-T0451", "G769-T0461", "G769-T0506",
})
EXPECTED_EXCLUDED = frozenset({
    "G769-T0014", "G769-T0131", "G769-T0139", "G769-T0295", "G769-T0387",
    "G769-T0419", "G769-T0435",
})
EXPECTED_OUTPUTS = (
    "REGISTERED_17_FIELD_REGISTRY.tsv", "GDT777_23_SPAN_ATLAS.tsv",
    "GDT777_EXACTNESS_EXCLUSIONS.tsv", "SPLIT_FUSION_PROFILE.tsv",
    "SAL_SPLIT_NEGATIVE_CONTROL.tsv", "GDT777_376_RENDERER.tsv",
    "GDT777_WORKING_DICTIONARY.tsv", "GDT777_PASSAGE_PATCHES.tsv",
    "GDT777_GDT388_RELATION_PACKET.tsv", "GDT777_RELATION_EDGE_CROSSWALK.tsv",
    "RELATION_PACKET_INTAKE.json", "RESULT.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def split_ids(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def position_class(start: int, end: int, count: int) -> str:
    if start == 1 and end == count:
        return "ONLY"
    if start == 1:
        return "FIRST"
    if end == count:
        return "FINAL"
    return "MIDDLE"


def cosine(left: Mapping[str, int], right: Mapping[str, int]) -> float:
    keys = set(left) | set(right)
    numerator = sum(left.get(key, 0) * right.get(key, 0) for key in keys)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def main() -> int:
    checks = 0
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(label)

    # Locked inputs are independently hashed rather than trusted through run.py.
    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    check(len(locks) == 14, "source-lock count")
    for row in locks:
        relative = Path(row["path"])
        check(not relative.is_absolute() and ".." not in relative.parts, f"safe source path {relative}")
        check((ROOT / relative).is_file(), f"source exists {relative}")
        if (ROOT / relative).is_file():
            check(sha256(ROOT / relative) == row["expected_sha256"], f"source hash {relative}")

    specs = read_tsv(SRC / "REGISTERED_FIELD_SPECS.tsv")
    spec_by_form = {row["registered_form"]: row for row in specs}
    check(len(specs) == len(spec_by_form) == 17, "17 unique registered specs")
    expected_forms = frozenset({
        "lchedy", "lcheol", "lcheor", "lchey", "lcho", "lkain", "lkar", "lom",
        "lor", "pchedy", "raiin", "rain", "rar", "rol", "rsheedy", "saiin", "schey",
    })
    check(frozenset(spec_by_form) == expected_forms, "registered form fingerprint")

    # Verify that each authored whole is registered with the declared head/body source.
    registry: dict[str, tuple[str, str, str]] = {}
    for row in read_tsv(G736):
        registry[row["form"]] = (row["opaque_head_id"], row["body"], "GDT736_TRAINING")
    for row in read_tsv(G737):
        check(row["form"] not in registry, f"registry disjoint {row['form']}")
        registry[row["form"]] = (row["opaque_head_id"], row["body"], "GDT737_HELD")
    for form, row in spec_by_form.items():
        check(form in registry, f"registered source {form}")
        if form in registry:
            check(registry[form] == (row["expected_head_id"], row["expected_body"], row["source_mode"]),
                  f"head/body/source binding {form}")
        visible = " ".join(row[key] for key in (
            "selected_whole_field_de", "selected_split_field_de", "alternate_1_de", "alternate_2_de"
        ))
        check(BANNED.search(visible) is None, f"retired literal absent from defaults {form}")

    core = load_module("gdt769_core_for_gdt777_validation", G769_CORE)
    _, environment = core.load_guarded_environment(ROOT)
    check(dict(environment["guard"]) == {
        "selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150,
    }, "guard fingerprint")
    context = environment["context"]
    base = read_tsv(G776)
    check(len(base) == 376, "base renderer rows")
    check(sum(int(row["gdt776_renderer_contextual"]) for row in base) == 149, "base contextual count")

    # Reconstruct the surface-only cohort without importing any GDT777 function.
    selected: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    for source in base:
        locus, ol_ordinal = source["locus"], int(source["ordinal"])
        line = context.by_line[locus]
        check(str(line[ol_ordinal - 1]["eva"]) == "ol", f"pivot surface {source['target_occurrence_id']}")
        if ol_ordinal >= len(line):
            continue
        right = line[ol_ordinal]
        right_surface = str(right["eva"])
        right_exact = bool(context.exact[(locus, int(right["token_index"]))])
        check(right_surface == source["right_surface"], f"right surface {source['target_occurrence_id']}")
        check(int(right_exact) == int(source["right_reader_exact"]), f"right exactness {source['target_occurrence_id']}")
        candidate: tuple[str, str, int, bool] | None = None
        if right_surface in registry:
            candidate = ("REGISTERED_COMPLETE_WHOLE", right_surface, ol_ordinal + 1, right_exact)
        if right_surface in HEADS and ol_ordinal + 1 < len(line):
            successor = line[ol_ordinal + 1]
            fused = right_surface + str(successor["eva"])
            if fused in registry:
                successor_exact = bool(context.exact[(locus, int(successor["token_index"]))])
                candidate = ("REGISTERED_SPLIT_FIELD", fused, ol_ordinal + 2, right_exact and successor_exact)
        if candidate is None:
            continue
        branch, form, end_ordinal, eligible = candidate
        record = {
            "target_occurrence_id": source["target_occurrence_id"], "locus": locus,
            "ol_ordinal": ol_ordinal, "branch": branch, "form": form,
            "end_ordinal": end_ordinal, "source": source,
        }
        (selected if eligible else excluded).append(record)

    check(frozenset(str(row["target_occurrence_id"]) for row in selected) == EXPECTED_SELECTED,
          "selected occurrence fingerprint")
    check(frozenset(str(row["target_occurrence_id"]) for row in excluded) == EXPECTED_EXCLUDED,
          "excluded occurrence fingerprint")
    check(Counter(str(row["branch"]) for row in selected) == Counter({
        "REGISTERED_COMPLETE_WHOLE": 16, "REGISTERED_SPLIT_FIELD": 7,
    }), "16 whole plus 7 split")
    check(len({str(row["form"]) for row in selected}) == 17, "17 selected form types")
    check(sum(1 - int(row["source"]["gdt776_renderer_contextual"]) for row in selected) == 14,
          "14 fallback replacements")
    check(sum(int(row["source"]["gdt776_renderer_contextual"]) for row in selected) == 9,
          "9 contextual sharpenings")
    selected_tokens = [
        f"{row['locus']}@{ordinal}" for row in selected
        for ordinal in range(int(row["ol_ordinal"]) + 1, int(row["end_ordinal"]) + 1)
    ]
    check(len(selected_tokens) == len(set(selected_tokens)) == 30, "30 unique selected tokens")

    atlas = read_tsv(ART / "GDT777_23_SPAN_ATLAS.tsv")
    exclusions = read_tsv(ART / "GDT777_EXACTNESS_EXCLUSIONS.tsv")
    check(len(atlas) == 23 and len(exclusions) == 7, "atlas and exclusion lengths")
    derived_keys = {(str(row["locus"]), int(row["ol_ordinal"]), str(row["branch"]), str(row["form"])) for row in selected}
    artifact_keys = {(row["locus"], int(row["ol_ordinal"]), row["branch"], row["registered_fused_form"]) for row in atlas}
    check(derived_keys == artifact_keys, "atlas equals reconstructed cohort")
    check(sum(int(row["fallback_replacement"]) for row in atlas) == 14, "atlas replacements")
    check(sum(int(row["contextual_sharpening"]) for row in atlas) == 9, "atlas sharpenings")
    for row in atlas:
        check(row["selection_rule"].endswith("NO_OCCURRENCE_ID"), f"surface rule {row['span_id']}")
        check(row["default_is_translation"] == row["confirmed_lexeme"] == row["confirmed_plaintext"] ==
              row["component_export_credit"] == "0", f"claim ceiling {row['span_id']}")

    # Global split/fused counts are counted again from the guarded token cache.
    fused_exact: Counter[str] = Counter()
    split_raw: Counter[tuple[str, str]] = Counter()
    split_exact: Counter[tuple[str, str]] = Counter()
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if bool(context.exact[(locus, int(token["token_index"]))]):
                fused_exact[surface] += 1
            if index + 1 < len(line):
                following = line[index + 1]
                pair = (surface, str(following["eva"]))
                split_raw[pair] += 1
                if (bool(context.exact[(locus, int(token["token_index"]))]) and
                        bool(context.exact[(locus, int(following["token_index"]))])):
                    split_exact[pair] += 1

    profiles = read_tsv(ART / "SPLIT_FUSION_PROFILE.tsv")
    check(len(profiles) == 17, "17 split/fused profiles")
    for row in profiles:
        form, pair = row["registered_form"], (row["opaque_head_surface"], row["body_surface"])
        check(int(row["guarded_fused_exact_occurrences"]) == fused_exact[form], f"fused count {form}")
        check(int(row["guarded_split_exact_occurrences"]) == split_exact[pair], f"split exact count {form}")
        fused_records: list[dict[str, str]] = []
        split_records: list[dict[str, str]] = []
        for locus, line in context.by_line.items():
            for index, token in enumerate(line):
                exact = bool(context.exact[(locus, int(token["token_index"]))])
                if str(token["eva"]) == form and exact:
                    fused_records.append({
                        "register": f"{token['section']}|{token['language']}|{token['hand']}",
                        "position": position_class(index + 1, index + 1, len(line)),
                        "left": (str(line[index - 1]["eva"]) if index > 0 and
                                 context.exact[(locus, int(line[index - 1]["token_index"]))]
                                 else "EDGE_OR_NONEXACT"),
                        "right": (str(line[index + 1]["eva"]) if index + 1 < len(line) and
                                  context.exact[(locus, int(line[index + 1]["token_index"]))]
                                  else "EDGE_OR_NONEXACT"),
                    })
                if index + 1 >= len(line) or str(token["eva"]) != pair[0] or str(line[index + 1]["eva"]) != pair[1]:
                    continue
                following = line[index + 1]
                if not exact or not context.exact[(locus, int(following["token_index"]))]:
                    continue
                split_records.append({
                    "register": f"{token['section']}|{token['language']}|{token['hand']}",
                    "position": position_class(index + 1, index + 2, len(line)),
                    "left": (str(line[index - 1]["eva"]) if index > 0 and
                             context.exact[(locus, int(line[index - 1]["token_index"]))]
                             else "EDGE_OR_NONEXACT"),
                    "right": (str(line[index + 2]["eva"]) if index + 2 < len(line) and
                              context.exact[(locus, int(line[index + 2]["token_index"]))]
                              else "EDGE_OR_NONEXACT"),
                })
        for artifact_field, feature in (("register_cosine_fused_split", "register"),
                                        ("line_position_cosine_fused_split", "position")):
            expected = cosine(Counter(item[feature] for item in fused_records),
                              Counter(item[feature] for item in split_records))
            check(abs(float(row[artifact_field]) - expected) <= 5e-9, f"independent {artifact_field} {form}")
        fused_neighbors = Counter(side + ":" + item[side] for item in fused_records for side in ("left", "right"))
        split_neighbors = Counter(side + ":" + item[side] for item in split_records for side in ("left", "right"))
        expected_neighbor = cosine(fused_neighbors, split_neighbors)
        check(abs(float(row["outer_neighbor_cosine_fused_split"]) - expected_neighbor) <= 5e-9,
              f"independent outer-neighbor cosine {form}")
    check(fused_exact["saiin"] == 89 and split_exact[("s", "aiin")] == 23, "saiin 89/23 profile")
    bridges = [row for row in read_tsv(G759_BOUND) if row["head_surface"] == "s" and row["value_surface"] == "aiin"]
    check(len(bridges) == 4 and all(row["same_manuscript_alternate_readings"] == "1" for row in bridges),
          "four alternate-reader saiin bridges")
    sal = read_tsv(ART / "SAL_SPLIT_NEGATIVE_CONTROL.tsv")
    check(len(sal) == 1, "one sal negative control")
    if sal:
        check(fused_exact["sal"] == int(sal[0]["guarded_fused_exact_occurrences"]) == 33, "sal fused 33")
        check(split_raw[("s", "al")] == int(sal[0]["guarded_raw_split_occurrences"]) == 5, "s al raw 5")
        check(split_exact[("s", "al")] == int(sal[0]["guarded_reader_exact_split_occurrences"]) == 0,
              "s al exact zero")

    renderer = read_tsv(ART / "GDT777_376_RENDERER.tsv")
    check(len(renderer) == 376, "renderer rows")
    check(sum(int(row["gdt777_renderer_contextual"]) for row in renderer) == 163, "renderer contextual 163")
    check(sum(1 - int(row["gdt777_renderer_contextual"]) for row in renderer) == 213, "renderer fallback 213")
    selected_render = [row for row in renderer if row["gdt777_branch"].startswith("GDT777_REGISTERED_")]
    check({row["target_occurrence_id"] for row in selected_render} == EXPECTED_SELECTED, "renderer selected IDs")
    selected_by_id = {str(row["target_occurrence_id"]): row for row in selected}
    for row in selected_render:
        expected = selected_by_id[row["target_occurrence_id"]]
        expected_tokens = [
            f"{expected['locus']}@{ordinal}"
            for ordinal in range(int(expected["ol_ordinal"]) + 1, int(expected["end_ordinal"]) + 1)
        ]
        expected_default = spec_by_form[str(expected["form"])][
            "selected_split_field_de" if expected["branch"] == "REGISTERED_SPLIT_FIELD" else "selected_whole_field_de"
        ]
        check(row["gdt777_branch"] == f"GDT777_{expected['branch']}",
              f"renderer branch binding {row['target_occurrence_id']}")
        check(row["gdt777_registered_form"] == expected["form"],
              f"renderer form binding {row['target_occurrence_id']}")
        check(row["gdt777_default_de"] == expected_default,
              f"renderer default binding {row['target_occurrence_id']}")
        check(split_ids(row["gdt777_consumed_token_ids"]) == expected_tokens,
              f"renderer consumption binding {row['target_occurrence_id']}")
    all_consumed = [token for row in renderer for token in split_ids(row["gdt777_consumed_token_ids"])]
    check(len(all_consumed) == len(set(all_consumed)) == 120, "120 globally unique consumed tokens")
    for row in renderer:
        check(row["gdt777_default_is_translation"] == row["gdt777_confirmed_lexeme"] ==
              row["gdt777_confirmed_plaintext"] == row["gdt777_component_export_credit"] == "0",
              f"renderer ceiling {row['target_occurrence_id']}")
        check(BANNED.search(row["gdt777_default_de"]) is None, f"renderer retired literal {row['target_occurrence_id']}")

    registry_art = read_tsv(ART / "REGISTERED_17_FIELD_REGISTRY.tsv")
    dictionary = read_tsv(ART / "GDT777_WORKING_DICTIONARY.tsv")
    passages = read_tsv(ART / "GDT777_PASSAGE_PATCHES.tsv")
    check(len(registry_art) == len(dictionary) == 17, "registry and dictionary 17")
    check(len(passages) == 23, "23 passage patches")
    for rows, label in ((registry_art, "registry"), (dictionary, "dictionary")):
        for row in rows:
            defaults = " ".join(value for key, value in row.items() if "default" in key)
            check(BANNED.search(defaults) is None, f"{label} retired default {next(iter(row.values()))}")
            check(row.get("component_export_credit", "0") == "0", f"{label} component zero")

    packet = ART / "GDT777_GDT388_RELATION_PACKET.tsv"
    packet_rows = read_tsv(packet)
    crosswalk = read_tsv(ART / "GDT777_RELATION_EDGE_CROSSWALK.tsv")
    check(len(packet_rows) == len(crosswalk) == 23, "packet and crosswalk rows")
    check(all(row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION" for row in packet_rows),
          "packet edges ineligible")
    intake_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet)], cwd=ROOT,
        text=True, capture_output=True, check=True,
    )
    intake = json.loads(intake_run.stdout)
    stored_intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    check(intake == stored_intake, "packet intake replay")
    check(intake["status"] == "VALID_ACQUISITION_NOT_SCORE_READY" and not intake["score_ready"],
          "packet not score-ready")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result["cohort"] == {
        "contextual_sharpenings": 9, "exactness_exclusions": 7,
        "fallback_replacements": 14, "registered_fused_form_types": 17,
        "registered_split_spans": 7, "registered_whole_spans": 16,
        "renderer_rows": 376, "selected_spans": 23,
    }, "result cohort")
    check(result["renderer"]["gdt776_contextual"] == 149 and
          result["renderer"]["gdt777_contextual"] == 163 and
          result["renderer"]["total_consumed_right_tokens"] == 120, "result renderer summary")
    check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] ==
          result["component_exports"] == result["sealed_pages_accessed"] == 0, "result claim ceiling")
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed manifest")

    # AST audit: the cohort function may carry IDs, but no ID or locus may dispatch selection.
    source_text = RUN.read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_span_cohort"]
    check(len(functions) == 1, "one cohort builder")
    if functions:
        predicate_text: list[str] = []
        for node in ast.walk(functions[0]):
            if isinstance(node, (ast.If, ast.IfExp, ast.While)):
                predicate_text.append(ast.get_source_segment(source_text, node.test) or ast.dump(node.test))
            elif isinstance(node, ast.comprehension):
                predicate_text.extend(ast.get_source_segment(source_text, item) or ast.dump(item) for item in node.ifs)
        check(not any("target_occurrence_id" in text for text in predicate_text), "no occurrence-ID selection predicate")

    # Byte replay all runner outputs and report into an isolated temporary tree.
    replayed = 0
    with tempfile.TemporaryDirectory(prefix="gdt777_validate_", dir=EXP) as temporary:
        temp = Path(temporary)
        generated = temp / "artifacts"
        generated.mkdir()
        generated_report = temp / "REPORT.md"
        completed = subprocess.run(
            [sys.executable, "-B", str(RUN), "--artifacts-dir", str(generated),
             "--report-path", str(generated_report)],
            cwd=ROOT, text=True, capture_output=True,
        )
        check(completed.returncode == 0, "runner replay exit")
        for name in EXPECTED_OUTPUTS:
            check((generated / name).is_file(), f"replay output exists {name}")
            if (generated / name).is_file():
                check((generated / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")
                replayed += 1
        check(generated_report.is_file(), "replay output exists REPORT.md")
        if generated_report.is_file():
            check(generated_report.read_bytes() == REPORT.read_bytes(), "byte replay REPORT.md")
            replayed += 1

    validation = {
        "experiment_id": "GDT777", "status": "PASS" if not failures else "FAIL",
        "checks": checks, "failures": failures, "source_locks": len(locks),
        "independent_selected_spans": len(selected), "independent_exclusions": len(excluded),
        "runner_outputs_plus_report_replayed": replayed,
        "relation_packet_status": intake["status"],
        "claim_ceiling": "Exact-span working fields only; no component, lexeme, plaintext, language, or substance identity.",
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
