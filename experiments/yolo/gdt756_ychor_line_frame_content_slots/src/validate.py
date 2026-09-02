#!/usr/bin/env python3
"""Independent invariants and byte-identical replay for GDT756."""

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
BASE_REL = Path("experiments/yolo/gdt756_ychor_line_frame_content_slots")
EXP = ROOT / BASE_REL
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
GENERATED = (
    "YCHOR_13_LINE_ATLAS.tsv",
    "YCHOR_71_BODY_TOKEN_CANDIDATES.tsv",
    "YCHOR_53_BODY_WHOLE_CANDIDATES.tsv",
    "YCHOR_247_MATCHED_CONTINUATION_CONTROLS.tsv",
    "YCHOR_FRAME_FEATURE_COMPARISON.tsv",
    "LINE_INITIAL_RECIPE_TRIAD_RANKING.tsv",
    "YCHOR_FORMULA_CANDIDATE_RANKING.tsv",
    "GDT756_YCHOR_FRAME_READER.md",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__YCHOR_ITEM_LEAD__13_OF13_LINE_INITIAL_0_OF13_PARAGRAPH_INITIAL__"
    "4_OF13_RECIPE_TRIADS_VS22_OF247_MATCHED__RANK4_OF113_INITIAL_FRAME_FORMS__"
    "71_OF71_BODY_TOKENS_CANDIDATE_RENDERED__53_BODY_WHOLES__"
    "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)
EXPECTED_FEATURES = {
    "CONTENT_PRESENT": (9, 148, "1.155405"),
    "AMOUNT_OR_LEVEL_PRESENT": (6, 91, "1.252747"),
    "PROCESS_PRESENT": (4, 40, "1.900000"),
    "QUALITY_OR_STAGE_PRESENT": (6, 151, "0.754967"),
    "CONTENT_AMOUNT_PROCESS_TRIAD": (4, 22, "3.454545"),
}
EXPECTED_FORMULAE = {
    "YF001": (1, 96, "Item", "ferner / ebenso"),
    "YF002": (2, 80, "Recipe / Accipe", "nimm"),
    "YF003": (3, 76, "Item take / Item accipe", "ferner: nimm"),
    "YF004": (4, 52, "De / Ad / For", "für / gegen"),
}


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

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    lines = read_tsv(ART / GENERATED[0])
    body = read_tsv(ART / GENERATED[1])
    wholes = read_tsv(ART / GENERATED[2])
    controls = read_tsv(ART / GENERATED[3])
    features = read_tsv(ART / GENERATED[4])
    initial = read_tsv(ART / GENERATED[5])
    formulae = read_tsv(ART / GENERATED[6])
    historical = read_tsv(EXP / "src/HISTORICAL_ITEM_COMPARATORS.tsv")
    formula_priors = read_tsv(EXP / "src/YCHOR_FORMULA_PRIORS.tsv")
    body_priors = read_tsv(EXP / "src/YCHOR_BODY_CANDIDATE_PRIORS.tsv")

    check(manifest["experiment_id"] == "GDT756", "manifest experiment id")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(result["status"] == STATUS, "result status")

    check(len(historical) == 3 and len({row["source_id"] for row in historical}) == 3, "three historical Item sources")
    check(all(row["primary_url"].startswith("https://") for row in historical), "historical source urls")
    check(all("Item" in row["attested_expression"] for row in historical), "Item exact expressions")
    check(len(formula_priors) == 4 and {row["candidate_id"] for row in formula_priors} == set(EXPECTED_FORMULAE), "four formula priors")
    check(len(body_priors) == 53 and len({row["surface"] for row in body_priors}) == 53, "53 body priors")
    for row in body_priors:
        check(row["working_candidate_de"] != "", f"body primary {row['surface']}")
        check(row["alternate_1_de"] != "" and row["alternate_2_de"] != "", f"body rivals {row['surface']}")
        check(len({row["working_candidate_de"], row["alternate_1_de"], row["alternate_2_de"]}) == 3, f"distinct body candidates {row['surface']}")
        check(row["confidence"] in {"C0_FORCED_CONTEXT", "C1_FRAME_CONSTRAINED"}, f"body confidence {row['surface']}")

    check(len(lines) == 13 and len({row["locus"] for row in lines}) == 13, "13 unique ychor lines")
    check(len({row["page"] for row in lines}) == 13, "13 ychor pages")
    check({row["section"] for row in lines} == {"H", "P", "S", "T"}, "four ychor sections")
    check(all(row["written_line_eva"].startswith("ychor ") for row in lines), "all ychor line initial")
    check(all(row["paragraph_start"] == "0" for row in lines), "zero ychor paragraph initial")
    check(sum(row["paragraph_end"] == "1" for row in lines) == 3, "three paragraph final lines")
    check(min(int(row["paragraph_line_index"]) for row in lines) == 2, "minimum paragraph line two")
    check(max(int(row["paragraph_line_index"]) for row in lines) == 28, "maximum paragraph line twenty eight")
    check(sum(int(row["body_token_count"]) for row in lines) == 71, "line body sum 71")
    check(sum(int(row["reader_exact_body_tokens"]) for row in lines) == 56, "56 exact body tokens")
    check(sum(int(row["independent_axis_body_tokens"]) for row in lines) == 17, "17 independent axis body tokens")
    check(sum(row["recipe_content_amount_process_triad"] == "1" for row in lines) == 4, "four ychor recipe triads")
    check(all(row["all_written_tokens_have_candidate_default"] == "1" for row in lines), "all line tokens rendered")
    check(all(row["selected_item_marker_render_de"].startswith("ferner: ") for row in lines), "Item renderer present")
    check(all(row["recipe_command_rival_render_de"].startswith("nimm: ") for row in lines), "Recipe rival renderer present")
    check(all(row["item_plus_command_rival_render_de"].startswith("ferner, nimm: ") for row in lines), "Item take rival renderer present")
    check(all("?" not in row["selected_item_marker_render_de"] for row in lines), "no question marks in renderer")
    check(all(not row["page"].lower().startswith("f84") for row in lines), "no sealed target page")

    check(len(body) == 71 and len({row["gdt756_body_token_id"] for row in body}) == 71, "71 body token rows")
    check(len({row["surface"] for row in body}) == 53, "53 body surfaces")
    check({row["surface"] for row in body} == {row["surface"] for row in body_priors}, "body prior coverage exact")
    check(sum(row["reader_exact"] == "1" for row in body) == 56, "body exact count")
    check(sum(row["gdt754_suspect_surface"] == "1" for row in body) == 2, "two suspect qokeol body rows")
    check(sum(row["independent_axes_at_position"] != "NONE" for row in body) == 17, "seventeen independently axed body rows")
    for row in body:
        check(row["working_candidate_de"] != "", f"body occurrence candidate {row['gdt756_body_token_id']}")
        check(row["alternate_1_de"] != "" and row["alternate_2_de"] != "", f"body occurrence rivals {row['gdt756_body_token_id']}")
        check(row["candidate_not_plaintext"] == "1", f"body occurrence boundary {row['gdt756_body_token_id']}")
        check(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0", f"body occurrence lexeme boundary {row['gdt756_body_token_id']}")
        check(row["component_export_credit"] == "0", f"body occurrence component boundary {row['gdt756_body_token_id']}")
        check(not row["page"].lower().startswith("f84"), f"body occurrence sealed page {row['gdt756_body_token_id']}")

    check(len(wholes) == 53 and len({row["surface"] for row in wholes}) == 53, "53 whole candidate rows")
    check(sum(int(row["ychor_body_occurrences"]) for row in wholes) == 71, "whole occurrence sum")
    check(sum(int(row["ychor_immediate_follower_occurrences"]) for row in wholes) == 13, "thirteen immediate followers")
    check(Counter(row["working_confidence"] for row in wholes) == Counter({
        "C0_FORCED_CONTEXT": 26,
        "C1_FRAME_CONSTRAINED": 26,
        "C1_CONSTRAINED_CANDIDATE": 1,
    }), "whole confidence counts")
    expected_selected = {
        "chor": "Blätter", "cthy": "Wurzel", "s": "Samen",
        "sheol": "eingeweichtes Kraut", "sheeor": "Wein",
        "chshoty": "weiche ein", "qokeol": "heiß im zweiten Grad",
    }
    for surface, value in expected_selected.items():
        row = next(item for item in wholes if item["surface"] == surface)
        check(row["working_candidate_de"] == value, f"selected body candidate {surface}")
        check(row["eva_spelling_used_to_select_candidate"] == "0", f"no spelling selection {surface}")
        check(row["confirmed_lexeme"] == "0", f"no body lexeme {surface}")

    check(len(controls) == 247, "247 matched control rows")
    check(len({row["control_locus"] for row in controls}) == 236, "236 unique control lines")
    check(len({row["target_ychor_locus"] for row in controls}) == 13, "all thirteen targets controlled")
    control_counts = Counter(row["target_ychor_locus"] for row in controls)
    check(sorted(control_counts.values()) == [7] + [20] * 12, "control multiplicities")
    for row in controls:
        check(row["same_section_language_hand"] == "1", f"control stratum {row['gdt756_control_id']}")
        check(row["both_paragraph_continuations"] == "1", f"control continuation {row['gdt756_control_id']}")
        check(int(row["line_length_delta"]) <= 1, f"control length {row['gdt756_control_id']}")
        check(row["control_initial_surface"] != "ychor", f"control initial exclusion {row['gdt756_control_id']}")
        check(row["comparison_uses_initial_surface_meaning"] == "0", f"control semantic independence {row['gdt756_control_id']}")
        check(not row["control_page"].lower().startswith("f84"), f"control sealed page {row['gdt756_control_id']}")

    check(len(features) == 5 and {row["feature"] for row in features} == set(EXPECTED_FEATURES), "five feature comparisons")
    for row in features:
        target_hits, control_hits, ratio = EXPECTED_FEATURES[row["feature"]]
        check(row["ychor_line_hits"] == str(target_hits), f"feature target {row['feature']}")
        check(row["ychor_lines"] == "13", f"feature target denominator {row['feature']}")
        check(row["matched_control_hits"] == str(control_hits), f"feature control {row['feature']}")
        check(row["matched_control_rows"] == "247", f"feature control denominator {row['feature']}")
        check(row["descriptive_rate_ratio"] == ratio, f"feature ratio {row['feature']}")
        check(row["initial_surface_semantics_used"] == "0", f"feature semantic independence {row['feature']}")

    check(len(initial) == 113 and len({row["initial_surface"] for row in initial}) == 113, "113 initial groups")
    check(all(int(row["reader_exact_initial_lines"]) >= 5 for row in initial), "initial minimum five")
    ychor_initial = next(row for row in initial if row["initial_surface"] == "ychor")
    check(ychor_initial["recipe_triad_rate_rank"] == "4", "ychor triad rank four")
    check(ychor_initial["recipe_triad_lines"] == "4" and ychor_initial["reader_exact_initial_lines"] == "13", "ychor initial triad count")
    check(ychor_initial["global_reader_exact_occurrences"] == "13" and ychor_initial["global_line_initial_purity"] == "1.000000", "ychor global initial purity")
    check([row["initial_surface"] for row in initial[:4]] == ["pchor", "ykar", "yteedy", "ychor"], "top four initial triad surfaces")
    check(all(row["comparison_uses_initial_surface_meaning"] == "0" for row in initial), "initial comparator semantic free")

    check(len(formulae) == 4 and {row["candidate_id"] for row in formulae} == set(EXPECTED_FORMULAE), "four formula result rows")
    for row in formulae:
        rank, score, expression, gloss = EXPECTED_FORMULAE[row["candidate_id"]]
        check(row["candidate_rank"] == str(rank), f"formula rank {row['candidate_id']}")
        check(row["fit_score_0_100_diagnostic"] == str(score), f"formula score {row['candidate_id']}")
        check(row["historical_expression"] == expression and row["working_candidate_de"] == gloss, f"formula value {row['candidate_id']}")
        check(row["selected_primary"] == str(int(rank == 1)), f"formula selection {row['candidate_id']}")
        check(row["historical_graphic_match_claimed"] == "0", f"formula no graphic match {row['candidate_id']}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"formula boundary {row['candidate_id']}")

    check(result["scope"] == {
        "body_tokens_with_candidate_default": 71,
        "formula_candidates": 4,
        "historical_item_sources": 3,
        "initial_surface_groups_min5": 113,
        "matched_control_rows": 247,
        "matched_control_unique_lines": 236,
        "post_ychor_body_tokens": 71,
        "post_ychor_unique_body_wholes": 53,
        "ychor_exact_occurrences": 13,
        "ychor_pages": 13,
        "ychor_sections": 4,
    }, "result scope")
    check(result["primary_formula_candidate"] == {
        "confidence": "C2_STRONG_EXPLORATORY",
        "fit_score_0_100_diagnostic": 96,
        "historical_expression": "Item",
        "line_initial_occurrences": 13,
        "paragraph_final_occurrences": 3,
        "paragraph_initial_occurrences": 0,
        "previous_primary_retained_as_rival": "Recipe / Accipe = nimm",
        "reader_exact_occurrences": 13,
        "sections": "H:9|P:2|S:1|T:1",
        "surface": "ychor",
        "working_candidate_de": "ferner / ebenso",
    }, "result primary formula")
    check(result["frame_result"] == {
        "descriptive_rate_ratio": "3.454545",
        "initial_form_groups": 113,
        "matched_control_rows": 247,
        "matched_control_triad_rows": 22,
        "ychor_content_amount_process_triad_lines": 4,
        "ychor_total_lines": 13,
        "ychor_triad_rank_among_initial_forms_min5": 4,
    }, "result frame")
    check(result["body_candidate_confidence_counts"] == {
        "C0_FORCED_CONTEXT": 26,
        "C1_CONSTRAINED_CANDIDATE": 1,
        "C1_FRAME_CONSTRAINED": 26,
    }, "result confidence")
    check(result["guard"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard exact")
    check(result["claim_boundary"] == {
        "component_export_credit": 0,
        "confirmed_lexemes": 0,
        "confirmed_literal_content_words": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
        "new_pages": 0,
        "plaintext_lines": 0,
    }, "result claim boundary")

    banned = ("work item", "working material", "Arbeitsgut", "Arbeitschritt", "destination vessel")
    for name in GENERATED:
        data = (ART / name).read_text(encoding="utf-8")
        check(not any(term in data for term in banned), f"no generic filler in {name}")

    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")
    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt756_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT756_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "primary_formula_candidate": result["primary_formula_candidate"],
        "frame_result": result["frame_result"],
        "claim_ceiling": (
            "Item/ferner is a strong exploratory complete-form candidate; all "
            "thirteen line bodies are candidate-filled, with zero confirmed "
            "lexemes, plaintext, component values, new pages, f84 or f84r access."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
