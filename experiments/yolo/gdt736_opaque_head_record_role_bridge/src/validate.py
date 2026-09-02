#!/usr/bin/env python3
"""Independent validator for GDT736."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt736_opaque_head_record_role_bridge")
EXP = ROOT / BASE_REL
ART = EXP / "artifacts"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
STATUS = (
    "RECORD_LOCATION_X_BODY_AFFINITY_2X2_SELECTED__PARAGRAPH_SUBENTRY_SPLIT_STRONG__"
    "FREE_FORM_AXIS_SUPPORTING_PROXY_ONLY__96_SCOPED_ROLE_RENDERINGS__"
    "ZERO_HEAD_LEXEMES__NO_NEW_PAGE"
)
GENERATED = (
    "OPAQUE_1166_OCCURRENCE_CONTEXTS.tsv", "HEAD_RECORD_ROLE_PROFILE.tsv",
    "BODY_CONTROLLED_POSITION_CONTRAST.tsv", "PAIR_POSITION_BY_SECTION.tsv",
    "RECORD_ROLE_2X2_GRID.tsv", "GLYPH_CLASS_AND_READER_AUDIT.tsv",
    "BODY_ROLE_DICTIONARY_V2.tsv", "OPAQUE_96_CONCRETE_ROLE_GRID.tsv",
    "CORRECTED_ROLE_TRANSLATION_EXAMPLES.tsv", "HISTORICAL_RECORD_MODEL_COMPARISON.tsv",
    "HEAD_BODY_AFFINITY_PROFILE.tsv", "HEAD_PAIR_BODY_COSINE.tsv", "ROLE_AXIS_TESTS.tsv",
    "RESULT.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT736", "manifest experiment id")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed pages forbidden")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["validation"]["status"] == "PASS", "manifest validation state")
    check(manifest["validation"]["artifact"] == str(VALIDATION_REL), "manifest validation path")
    for item in manifest["inputs"]:
        check((ROOT / item["path"]).is_file(), f"input exists: {item['path']}")
        check(sha256(ROOT / item["path"]) == item["sha256"], f"input hash: {item['path']}")
    for item in manifest["outputs"]:
        path = ROOT / item["path"]
        check(path.is_file(), f"output exists: {item['path']}")
        if item["path"] != str(VALIDATION_REL):
            check(sha256(path) == item["sha256"], f"output hash: {item['path']}")

    heads = read_tsv(EXP / "src/HEAD_ROLE_SPECS.tsv")
    bodies_src = read_tsv(EXP / "src/BODY_ROLE_SPECS.tsv")
    models_src = read_tsv(EXP / "src/HISTORICAL_RECORD_MODEL_SPECS.tsv")
    sources = read_tsv(EXP / "src/HISTORICAL_ARCHITECTURE_SOURCES.tsv")
    examples_src = read_tsv(EXP / "src/CORRECTED_EXAMPLE_SPECS.tsv")
    check(len(heads) == 4 and {row["opaque_head_id"] for row in heads} == {"H1", "H2", "H3", "H4"}, "four head specs")
    check(len(bodies_src) == 24 and len({row["body"] for row in bodies_src}) == 24, "twenty-four body specs")
    check(len(models_src) == 8 and models_src[0]["model_id"] == "HRM01", "eight historical models")
    check(len(sources) == 12, "twelve historical architecture sources")
    check(len(examples_src) == 24, "twenty-four corrected source examples")
    old_635 = {
        row["span_id"]: row["working_translation_de"]
        for row in read_tsv(ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/MATCHED_SPAN_TRANSLATIONS.tsv")
    }
    old_636 = {
        row["span_id"]: row["working_translation_de"]
        for row in read_tsv(ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/CONCRETE_RESIDUAL_SPAN_TRANSLATIONS.tsv")
    }
    check(all(
        row["old_translation_de"] == ({"GDT635": old_635, "GDT636": old_636}[row["source_experiment"]][row["span_id"]])
        for row in examples_src
    ), "old example translations preserve source artifacts")
    check(all(int(row["head_lexeme_credit"]) == 0 for row in models_src + sources), "historical head lexeme credit zero")
    check(all(row["glyphshape_credit"] == "UNOBSERVED" for row in models_src + sources), "historical glyph shapes unobserved")
    check(all(int(row["component_export_credit"]) == 0 for row in heads + models_src), "source component export zero")

    occurrences = read_tsv(ART / "OPAQUE_1166_OCCURRENCE_CONTEXTS.tsv")
    check(len(occurrences) == 1166, "1166 occurrence rows")
    check(len({row["occurrence_id"] for row in occurrences}) == 1166, "unique occurrence ids")
    check(len({(row["locus"], row["token_index"]) for row in occurrences}) == 1166, "unique occurrence positions")
    check(len({row["form"] for row in occurrences}) == 96, "96 occurrence forms")
    check(len({row["body"] for row in occurrences}) == 24, "24 occurrence bodies")
    check(len({row["page"] for row in occurrences}) == 141, "141 target pages")
    check(len({row["locus"] for row in occurrences}) == 946, "946 target loci")
    check(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in occurrences), "no forbidden target page")
    check(Counter(row["opaque_head_id"] for row in occurrences) == Counter({"H1": 135, "H2": 440, "H3": 197, "H4": 394}), "head occurrence totals")
    check(Counter(row["source_experiment"] for row in occurrences) == Counter({"GDT635_CORE": 639, "GDT636_RESIDUAL": 527}), "core residual provenance totals")
    check(sum(int(row["all_readers_exact"]) for row in occurrences) == 875, "875 reader-exact occurrences")
    check(all(row["literal_head_lexeme"] == "UNRESOLVED" for row in occurrences), "occurrence head lexemes unresolved")
    check(all(int(row["eva_initial_credit"]) == int(row["sound_credit"]) == int(row["component_export_credit"]) == 0 for row in occurrences), "occurrence credits zero")
    check(all(row["physical_attachment"].startswith("UNKNOWN") for row in occurrences), "physical attachment unknown")

    profiles = read_tsv(ART / "HEAD_RECORD_ROLE_PROFILE.tsv")
    check(len(profiles) == 4, "four head profiles")
    by_head = {row["opaque_head_id"]: row for row in profiles}
    expected_sta = {"H1": "P1", "H2": "C2", "H3": "C1", "H4": "B2"}
    check({head: row["sta_code"] for head, row in by_head.items()} == expected_sta, "STA codes P1 C2 C1 B2")
    expected_position = {"H1": (72, 61, 2), "H2": (222, 159, 59), "H3": (4, 146, 47), "H4": (35, 281, 78)}
    for head, values in expected_position.items():
        check(tuple(int(by_head[head][field]) for field in ("target_line_first", "target_line_middle", "target_line_last")) == values, f"{head} target positions")
    check((int(by_head["H1"]["target_paragraph_first_token"]), int(by_head["H2"]["target_paragraph_first_token"])) == (49, 3), "H1 versus H2 paragraph first")
    check((int(by_head["H3"]["target_paragraph_first_token"]), int(by_head["H4"]["target_paragraph_first_token"])) == (0, 0), "internal heads never paragraph first")
    check([int(by_head[head]["target_split_only"]) for head in ("H1", "H2", "H3", "H4")] == [0, 21, 11, 10], "split-only head totals")
    check([int(by_head[head]["full_standalone_occurrences"]) for head in ("H1", "H2", "H3", "H4")] == [5, 272, 129, 163], "standalone proxy totals")

    contrasts = read_tsv(ART / "BODY_CONTROLLED_POSITION_CONTRAST.tsv")
    check(len(contrasts) == 24, "twenty-four body-controlled contrasts")
    check(Counter(row["direction"] for row in contrasts) == Counter({"ENTRY_EARLIER": 21, "INTERNAL_EARLIER": 3}), "21 of 24 entry earlier")
    section = read_tsv(ART / "PAIR_POSITION_BY_SECTION.tsv")
    check(len(section) == 6 and all(row["direction"] == "ENTRY_EARLIER" for row in section), "all represented sections same direction")

    role_grid = read_tsv(ART / "RECORD_ROLE_2X2_GRID.tsv")
    check(len(role_grid) == 4, "four-cell role grid")
    expected_axes = {
        "H1": ("ENTRY", "CLUSTER_A_FORM_STATE_HEAVY", "LOW_FREE_FORM_PROXY"),
        "H2": ("ENTRY", "CLUSTER_B_MATERIA_VALUE_HEAVY", "HIGH_FREE_FORM_PROXY"),
        "H3": ("INTERNAL_OR_FINAL", "CLUSTER_B_MATERIA_VALUE_HEAVY", "HIGH_FREE_FORM_PROXY"),
        "H4": ("INTERNAL_OR_FINAL", "CLUSTER_A_FORM_STATE_HEAVY", "LOW_FREE_FORM_PROXY"),
    }
    for row in role_grid:
        check((row["record_location_axis"], row["body_affinity_axis"], row["free_form_proxy_axis"]) == expected_axes[row["opaque_head_id"]], f"{row['opaque_head_id']} 2x2 axes")
        check(row["literal_lexeme_status"].startswith("UNRESOLVED") and int(row["component_export_credit"]) == 0, f"{row['opaque_head_id']} role ceiling")

    affinity = read_tsv(ART / "HEAD_BODY_AFFINITY_PROFILE.tsv")
    cosines = read_tsv(ART / "HEAD_PAIR_BODY_COSINE.tsv")
    check(len(affinity) == 4 and len(cosines) == 6, "body affinity artifact sizes")
    selected = [row for row in cosines if int(row["selected_cross_axis_pair"]) == 1]
    check({frozenset((row["head_a"], row["head_b"])) for row in selected} == {frozenset(("H1", "H4")), frozenset(("H2", "H3"))}, "selected body-affinity pairs")
    check(abs(float(next(row["occurrence_cosine"] for row in selected if {row["head_a"], row["head_b"]} == {"H1", "H4"})) - 0.919004) < 0.000001, "H1 H4 occurrence cosine")
    check(abs(float(next(row["occurrence_cosine"] for row in selected if {row["head_a"], row["head_b"]} == {"H2", "H3"})) - 0.934429) < 0.000001, "H2 H3 occurrence cosine")
    check(max(float(row["occurrence_cosine"]) for row in cosines if int(row["selected_cross_axis_pair"]) == 0) < 0.47, "other pair cosines below 0.47")

    tests = {row["test_id"]: row for row in read_tsv(ART / "ROLE_AXIS_TESTS.tsv")}
    check(len(tests) == 8, "eight role-axis tests")
    check(abs(float(tests["T01_FIRST_ENTRY_VS_INTERNAL"]["odds_ratio"]) - 14.808650) < 0.000001, "unadjusted first-position OR")
    check((tests["T01_FIRST_ENTRY_VS_INTERNAL"]["ci95_low"], tests["T01_FIRST_ENTRY_VS_INTERNAL"]["ci95_high"]) == ("10.294590", "21.302074"), "unadjusted first-position CI")
    check(abs(float(tests["T06_FIRST_EXACT_RESIDUAL"]["odds_ratio"]) - 9.762467) < 0.000001, "exact residual position OR")
    check(abs(float(tests["T07_MH_BODY_SECTION"]["odds_ratio"]) - 16.681983) < 0.000001, "body-section adjusted OR")
    check(abs(float(tests["T08_MH_BODY_SECTION_LANGUAGE"]["odds_ratio"]) - 18.018192) < 0.000001, "body-section-language adjusted OR")
    check(float(tests["T04_SPLIT_HIGH_FREE_VS_LOW_FREE"]["ci95_low"]) > 1, "split-only proxy CI above one")
    check(float(tests["T05_READER_EXACT_ENTRY_VS_INTERNAL"]["ci95_low"]) < 1 < float(tests["T05_READER_EXACT_ENTRY_VS_INTERNAL"]["ci95_high"]), "exactness role comparison crosses one")

    reader = read_tsv(ART / "GLYPH_CLASS_AND_READER_AUDIT.tsv")
    check(len(reader) == 4, "four reader audit rows")
    check(all(row["physical_graph_description"] == "UNOBSERVED_IN_ADMITTED_CACHE" and row["historical_shape_match"] == "NOT_SCORED" for row in reader), "no manufactured glyph shape match")
    check(all(int(row["eva_letter_sound_or_initial_credit"]) == int(row["literal_lexeme_credit"]) == 0 for row in reader), "reader audit credits zero")

    body_dictionary = read_tsv(ART / "BODY_ROLE_DICTIONARY_V2.tsv")
    check(len(body_dictionary) == 24 and sum(int(row["target_occurrences"]) for row in body_dictionary) == 1166, "body dictionary coverage")
    air = next(row for row in body_dictionary if row["body"] == "air")
    check(air["revised_concrete_default_de"] == "Teil- oder Fraktionsstufe II", "air formal default")
    check("Wurzel- oder Untergrundteil" in air["herbal_visual_override_de"], "air inherited Herbal override")
    visual = next(row for row in read_tsv(ROOT / "experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/VISUAL_OBSERVATIONS.tsv") if row["observation_id"] == "VIS006")
    check("five Herbal page heads" in visual["manual_observation"], "air override binds GDT623 VIS006")
    check(all(int(row["confirmed_lexeme"]) == int(row["component_export_credit"]) == 0 for row in body_dictionary), "body lexeme and export credit zero")

    grid96 = read_tsv(ART / "OPAQUE_96_CONCRETE_ROLE_GRID.tsv")
    check(len(grid96) == len({row["form"] for row in grid96}) == 96, "96 unique role cells")
    check(Counter(row["opaque_head_id"] for row in grid96) == Counter({"H1": 24, "H2": 24, "H3": 24, "H4": 24}), "24 cells per head")
    check(sum(int(row["occurrences"]) for row in grid96) == 1166 and sum(int(row["reader_exact_occurrences"]) for row in grid96) == 875, "role grid count totals")
    check(all(row["literal_head_lexeme"] == "UNRESOLVED" and int(row["eva_initial_credit"]) == int(row["sound_credit"]) == int(row["component_export_credit"]) == 0 for row in grid96), "role grid claim ceiling")
    check(sum(row["herbal_visual_override_de"] != "NONE" for row in grid96) == 1, "single scoped Herbal air override")

    examples = read_tsv(ART / "CORRECTED_ROLE_TRANSLATION_EXAMPLES.tsv")
    check(len(examples) == 24 and Counter(row["source_experiment"] for row in examples) == Counter({"GDT635": 10, "GDT636": 14}), "corrected example provenance")
    retired = ("pulver", "samen", "saat", "wurzel", "holz", "drogenholz")
    check(not any(word in row["corrected_translation_de"].lower() for row in examples for word in retired), "retired head nouns absent from corrected translations")
    check(all(row["old_head_noun_status"] == "REMOVED" and int(row["component_export_credit"]) == 0 for row in examples), "corrected example ceiling")

    models = read_tsv(ART / "HISTORICAL_RECORD_MODEL_COMPARISON.tsv")
    check(len(models) == 8, "eight generated model rows")
    check(models[0]["model_id"] == "HRM01" and models[0]["status"] == "SELECTED_PRIMARY_NONLEXICAL_ARCHITECTURE", "selected nonlexical architecture")
    check(models[-1]["model_id"] == "HRM08" and models[-1]["status"] == "REJECTED_ANACHRONISTIC_INELIGIBLE", "EVA initialism rejected")
    check(all(int(row["literal_head_lexemes_identified"]) == int(row["eva_letter_or_sound_credit"]) == int(row["physical_shape_match_credit"]) == int(row["component_export_credit"]) == 0 for row in models), "model output credits zero")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["inherited_allowlist_pages"] == 179 and result["scope"]["target_pages_with_occurrences"] == 141, "result scope pages")
    check(result["scope"]["new_pages_used"] == 0 and not result["scope"]["f84_used"] and not result["scope"]["f84r_used"], "result sealed scope")
    check(result["target"] == {"bodies": 24, "forms": 96, "head_occurrences": {"H1": 135, "H2": 440, "H3": 197, "H4": 394}, "occurrences": 1166, "reader_exact": 875}, "result target block")
    check(result["claims"]["literal_head_lexemes_identified"] == result["claims"]["literal_body_lexemes_confirmed"] == result["claims"]["component_export_credit"] == 0, "result zero lexeme and export claims")
    for relative, expected in result["artifact_hashes"].items():
        check(sha256(ROOT / relative) == expected, f"result artifact hash: {relative}")

    with tempfile.TemporaryDirectory(prefix="gdt736-replay-") as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(EXP / "src/run.py"), "--output-dir", str(replay)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        check(completed.returncode == 0, "builder replay exits zero")
        for name in GENERATED:
            check((replay / name).read_bytes() == (ART / name).read_bytes(), f"byte-identical replay: {name}")

    validation = {
        "schema": "GDT736_VALIDATION_V1", "status": "PASS", "experiment_id": "GDT736",
        "checks_passed": len(checks), "checks": checks,
        "validated_result_sha256": sha256(ART / "RESULT.json"),
        "builder_replay": "BYTE_IDENTICAL",
        "claim_ceiling": (
            "Formal record-location and opaque body-affinity axes only; pharmaceutical wording is a replaceable "
            "working renderer. No head/body lexeme, EVA letter/sound/Latin initial, physical glyph shape, species, "
            "plaintext translation, component export, new page, f84, or f84r claim."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "checks_passed": len(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
