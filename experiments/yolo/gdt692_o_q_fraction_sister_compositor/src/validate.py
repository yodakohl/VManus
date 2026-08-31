#!/usr/bin/env python3
"""Independent validator for GDT692 V65 fraction-sister compositor."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt692_o_q_fraction_sister_compositor"
ART = BASE / "artifacts"
SRC = BASE / "src"
RUN_PATH = SRC / "run.py"
RESULT_PATH = ART / "RESULT.json"
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(glosses: list[str]) -> str:
    text = ""
    for gloss in glosses:
        if gloss in {";", "."}:
            text = text.rstrip(" ,;.") + gloss
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator + gloss
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:] if text else text


def has_root(text: str, root: str) -> bool:
    return any(root in word.casefold() for word in WORD_RE.findall(text))


def fold_bound_units(
    locus: str,
    locus_tokens: list[dict[str, str]],
    bound_by_start: dict[tuple[str, int], dict[str, str]],
) -> list[str]:
    units: list[str] = []
    ordinal = 1
    while ordinal <= len(locus_tokens):
        bound = bound_by_start.get((locus, ordinal))
        if bound:
            units.append(bound["combined_v65_gloss_de"])
            ordinal = int(bound["end_ordinal"]) + 1
        else:
            units.append(locus_tokens[ordinal - 1]["v65_token_gloss_de"])
            ordinal += 1
    return units


def main() -> int:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    checks: list[str] = []

    assert result["status"] == "PASS_V65_16_SURFACE_41_OCCURRENCE_COMPOSITOR__32_TOKEN_REVISIONS__AUSZUG_32_TO_7_EXPLICIT_WORKFLOW_ONLY"
    checks.append("result_status")

    for rel, expected in result["inputs"].items():
        assert sha256(ROOT / rel) == expected, rel
    for name, expected in result["files"].items():
        assert sha256(ART / name) == expected, name
    checks.append("all_input_and_output_hashes")

    components = read_tsv(SRC / "V65_COMPONENT_LEXICON.tsv")
    rules = read_tsv(SRC / "V65_FRACTION_SURFACE_RULES.tsv")
    carries = read_tsv(SRC / "V65_CONTEXT_CARRY_RULES.tsv")
    bound_sources = read_tsv(SRC / "V65_BOUND_SPAN_RULES.tsv")
    rival_sources = read_tsv(SRC / "V65_CONTEXTUAL_PRODUCT_RIVALS.tsv")
    historical_sources = read_tsv(SRC / "V65_HISTORICAL_HEAD_ANALOGUES.tsv")
    targets = read_tsv(ART / "V64_41_FRACTION_SISTER_OCCURRENCES.tsv")
    lattice = read_tsv(ART / "V65_16_SURFACE_SISTER_LATTICE.tsv")
    revisions = read_tsv(ART / "V64_V65_32_TOKEN_REVISIONS.tsv")
    tokens = read_tsv(ART / "V65_479_TOKEN_READER.tsv")
    lines = read_tsv(ART / "V65_51_LINE_COMPOSITIONAL_READER.tsv")
    verbs = read_tsv(ART / "V65_113_VERB_PRESERVATION.tsv")
    terms = read_tsv(ART / "V64_V65_TERM_COMPARISON.tsv")
    workflow = read_tsv(ART / "V65_7_EXPLICIT_WORKFLOW_AUSZUGS.tsv")
    component_summary = read_tsv(ART / "V65_COMPONENT_USE_SUMMARY.tsv")
    bound_spans = read_tsv(ART / "V65_2_BOUND_MULTI_TOKEN_SPANS.tsv")
    contextual_rivals = read_tsv(ART / "V65_6_CONTEXTUAL_PRODUCT_RIVALS.tsv")
    historical_analogues = read_tsv(ART / "V65_2_HISTORICAL_HEAD_ANALOGUES.tsv")

    assert len(components) == 9 and len(rules) == 16 and len(carries) == 2
    assert len(bound_sources) == len(bound_spans) == 2
    assert len(rival_sources) == len(contextual_rivals) == 6
    assert len(historical_sources) == len(historical_analogues) == 2
    assert len(targets) == 41 and len(lattice) == 16 and len(revisions) == 32
    assert len(tokens) == 479 and len(lines) == 51 and len(verbs) == 113
    assert len(workflow) == 7 and len(component_summary) == 9
    checks.append("population_51_479__16_surfaces_41_occurrences__32_revisions__2_bound_spans__6_rivals")

    component_ids = {row["component"] for row in components}
    assert len(component_ids) == 9
    literal_by_component = {row["component"]: row["surface_literal"] for row in components}
    rule_counts = Counter(row["rule_id"] for row in targets)
    expected_counts = {row["rule_id"]: int(row["expected_positions"]) for row in rules}
    assert rule_counts == expected_counts
    for rule in rules:
        assert set(rule["composition"].split("+")) <= component_ids
        rebuilt_surface = "".join(literal_by_component[item] for item in rule["composition"].split("+")) + rule["visible_tail"]
        assert rebuilt_surface == rule["surface"], (rule["surface"], rebuilt_surface)
    assert all(int(row["surface_rules"]) > 0 and int(row["weighted_occurrences"]) > 0 for row in component_summary)
    checks.append("all_9_components_used__all_16_rules_exact_counts")

    expected_compositions = {
        "oar": "O_PREP+AR_FRACTION_I",
        "oair": "O_PREP+AIR_FRACTION_II",
        "okar": "O_PREP+K_HOT+AR_FRACTION_I",
        "otar": "O_PREP+T_COLD+AR_FRACTION_I",
        "otair": "O_PREP+T_COLD+AIR_FRACTION_II",
        "olkar": "O_PREP+L_WOOD+K_HOT+AR_FRACTION_I",
        "olkaiir": "O_PREP+L_WOOD+K_HOT+AIIR_FRACTION_III",
        "otarar": "O_PREP+T_COLD+AR_FRACTION_I+AR_FRACTION_I",
        "otardy": "O_PREP+T_COLD+AR_FRACTION_I",
        "qokar": "QO_FRAME+K_HOT+AR_FRACTION_I",
        "qotar": "QO_FRAME+T_COLD+AR_FRACTION_I",
        "qodar": "QO_FRAME+D_MEASURE+AR_FRACTION_I",
        "qokaiir": "QO_FRAME+K_HOT+AIIR_FRACTION_III",
    }
    rule_by_surface = {row["surface"]: row for row in rules}
    assert all(rule_by_surface[surface]["composition"] == composition for surface, composition in expected_compositions.items())
    assert rule_by_surface["otarar"]["whole_extension"] == "SECOND_AR_RECURSIVE_SUBFRACTION"
    assert rule_by_surface["otardy"]["whole_extension"] == "EXACT_OTARDY_FINISHED_RESULT_TAIL"
    assert rule_by_surface["otardy"]["visible_tail"] == "dy"
    assert rule_by_surface["qokaiir"]["whole_extension"] == "EXACT_QOKAIIR_ACTION_OVERRIDE"
    assert rule_by_surface["qokaiir"]["visible_tail"] == ""
    assert not ({"QO_SCOPE", "QO_COMMAND", "AR_SUBFRACTION_I", "DY_FINISHED"} & component_ids)
    checks.append("independent_9_component_o_q_sister_replay__exact_whole_extensions")

    assert all(has_root(row["v65_gloss_de"], "fraktion") for row in targets)
    for row in targets:
        composition = row["composition"]
        gloss = row["v65_gloss_de"].casefold()
        if "K_HOT" in composition:
            assert "heiss" in gloss or "erhitz" in gloss
        if "T_COLD" in composition:
            assert "kalt" in gloss
        if "L_WOOD" in composition:
            assert "holz" in gloss
        if "AIR_FRACTION_II" in composition:
            assert "ii" in row["v65_gloss_de"].casefold()
        if "AIIR_FRACTION_III" in composition:
            assert "iii" in row["v65_gloss_de"].casefold()
    checks.append("fraction_head_41_of_41__temperature_material_and_level_retained")

    revision_keys = {(row["locus"], row["token_ordinal"]) for row in revisions}
    assert len(revision_keys) == 32
    assert Counter(row["rule_id"][0] for row in revisions) == {"F": 30, "C": 2}
    assert {(row["locus"], row["token_ordinal"]) for row in carries} <= revision_keys
    checks.append("30_surface_plus_2_carry_revisions")

    tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        assert not row["page"].startswith("f84") and not row["locus"].startswith("f84")
        tokens_by_locus[row["locus"]].append(row)
    line_by_locus = {row["locus"]: row for row in lines}
    bound_by_start = {(row["locus"], int(row["start_ordinal"])): row for row in bound_spans}
    assert len(bound_by_start) == 2
    assert set(tokens_by_locus) == set(line_by_locus)
    for locus, locus_tokens in tokens_by_locus.items():
        locus_tokens.sort(key=lambda row: int(row["token_ordinal"]))
        assert [int(row["token_ordinal"]) for row in locus_tokens] == list(range(1, len(locus_tokens) + 1))
        rebuilt = render(fold_bound_units(locus, locus_tokens, bound_by_start))
        assert rebuilt == line_by_locus[locus]["v65_compositional_translation_de"]
        changed = sum(int(row["v65_changed"]) for row in locus_tokens)
        assert changed == int(line_by_locus[locus]["v65_changed_token_positions"])
    assert sum(int(row["v65_changed"]) for row in tokens) == 32
    checks.append("line_replay_51_479__2_bound_spans__no_f84")

    expected_bound_text = {
        ("f86v3.13", "5", "6"): "drei Portionen der Fraktion I des heißen Holzansatzes",
        ("f86v6.5", "4", "5"): "Fraktion I des heißen Holzansatzes; drei Portionen davon",
    }
    assert {
        (row["locus"], row["start_ordinal"], row["end_ordinal"]): row["combined_v65_gloss_de"]
        for row in bound_spans
    } == expected_bound_text
    assert all(row["validated"] == "1" for row in bound_spans)
    assert {row["rival_id"] for row in contextual_rivals} == {"R001", "R002", "R003", "R004", "R005", "R006"}
    assert all(row["selected_status"] == "CONTEXTUAL_RIVAL_RETAINED__NOT_GLOBAL_DEFAULT" for row in contextual_rivals)
    assert all(row["validated"] == "1" for row in contextual_rivals)
    checks.append("gdt686_head_bindings_and_six_strong_local_product_rivals")

    assert {row["analogue_id"] for row in historical_analogues} == {"H001", "H002"}
    assert all(row["url"].startswith("https://") for row in historical_analogues)
    assert "separation" in historical_analogues[0]["implication_for_v65"]
    assert "quality grades" in historical_analogues[1]["implication_for_v65"]
    checks.append("two_period_head_analogues_preserved")

    allowed_auszug = {"qoteed", "olord", "oteed", "okeeodar", "qokeod", "kchod", "keeod"}
    selected_auszug = [row for row in tokens if has_root(row["v65_token_gloss_de"], "auszug")]
    assert len(selected_auszug) == 7
    assert {row["surface"] for row in selected_auszug} == allowed_auszug
    assert {row["surface"] for row in workflow} == allowed_auszug
    assert not any(has_root(row["v65_gloss_de"], "auszug") for row in targets)
    checks.append("auszug_32_to_7__explicit_workflow_surfaces_only")

    term_by_root = {row["root"]: row for row in terms}
    assert int(term_by_root["auszug"]["v64_occurrences"]) == 32
    assert int(term_by_root["auszug"]["v65_occurrences"]) == 7
    assert int(term_by_root["fraktion"]["v64_occurrences"]) == 55
    assert int(term_by_root["fraktion"]["v65_occurrences"]) == 79
    assert int(term_by_root["ansatz"]["v64_occurrences"]) == 75
    assert int(term_by_root["ansatz"]["v65_occurrences"]) == 97
    checks.append("term_shift_auszug_minus25__fraktion_plus24__ansatz_relations_plus22")

    assert all(int(row["preserved_exact_ordinal"]) == 1 for row in verbs)
    assert all(int(row["gdt692_additional_verb_form_loss"]) == 0 for row in verbs)
    assert sum(int(row["v64_exact_form_present"]) for row in verbs) == 110
    assert sum(int(row["v65_exact_form_present"]) for row in verbs) == 110
    for row in verbs:
        assert int(row["v64_exact_form_present"]) == int(row["v65_exact_form_present"])
    checks.append("all_113_action_ordinals_preserved__exact_forms_110_to_110")

    assert result["inherited_debt"] == {"strict": 106, "mechanical_union": 152, "four_layer_union": 330}
    assert result["basis"]["new_pages"] == 0 and result["basis"]["f84_access"] == 0 and result["basis"]["f84r_access"] == 0
    checks.append("inherited_debt_and_sealed_scope_unchanged")

    spec = importlib.util.spec_from_file_location("gdt692_run", RUN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="gdt692_replay_") as temporary:
        replay_dir = Path(temporary)
        replay_result = module.build(replay_dir)
        assert replay_result == result
        for name in result["files"]:
            assert (replay_dir / name).read_bytes() == (ART / name).read_bytes(), name
    checks.append("exact_byte_replay_all_generated_files")

    validation = {
        "experiment": "GDT692", "status": "PASS",
        "checks_passed": len(checks), "checks": checks,
        "result_sha256": sha256(RESULT_PATH),
        "validator_sha256": sha256(Path(__file__).resolve()),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
