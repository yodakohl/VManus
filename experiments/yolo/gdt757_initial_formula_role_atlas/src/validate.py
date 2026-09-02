#!/usr/bin/env python3
"""Invariant and byte-replay validator for GDT757."""

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
BASE_REL = Path("experiments/yolo/gdt757_initial_formula_role_atlas")
EXP = ROOT / BASE_REL
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
GENERATED = (
    "INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv",
    "INITIAL_FORMULA_11_WHOLE_ROLE_ATLAS.tsv",
    "FORMULA_ROLE_CANDIDATE_RANKING.tsv",
    "LOW_PURITY_HIGH_TRIAD_COMPARATORS.tsv",
    "EDIT1_FORMULA_NEIGHBOR_ATLAS.tsv",
    "GDT757_FORMULA_ROLE_READER.md",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__11_COMPLETE_FORMULA_WHOLES__79_INITIAL_LINES__"
    "PCHOR_RECIPE_OPEN_6_OF7_PARAGRAPH_START__YCHOR_ITEM_0_OF13_START__"
    "YCHEOL_YCHOL_DCHEOL_YCHEOR_FAMILY_1_OF26_START_9_OF26_END__"
    "4_LOW_PURITY_CONTROLS_NOT_PROMOTED__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)
EXPECTED_PRIMARY = {
    "dcheol": "danach / darauf",
    "paiin": "drei Teile / dritte Menge",
    "pchor": "nimm",
    "pol": "Zubereitung / Eintrag",
    "polaiin": "Zubereitung / Rezept",
    "qokchor": "mische hinein",
    "tshol": "für / gegen",
    "ycheol": "danach",
    "ycheor": "zum Schluss",
    "ychol": "danach / als Nächstes",
    "ychor": "ferner / ebenso",
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
    occurrences = read_tsv(ART / GENERATED[0])
    wholes = read_tsv(ART / GENERATED[1])
    rankings = read_tsv(ART / GENERATED[2])
    comparators = read_tsv(ART / GENERATED[3])
    neighbors = read_tsv(ART / GENERATED[4])
    historical = read_tsv(EXP / "src/HISTORICAL_FORMULA_REGISTER.tsv")
    priors = read_tsv(EXP / "src/FORMULA_ROLE_PRIORS.tsv")

    check(manifest["experiment_id"] == "GDT757", "manifest id")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(result["status"] == STATUS, "result status")
    check(len(historical) == 8 and len({row["source_id"] for row in historical}) == 8, "eight historical sources")
    check(all(row["primary_url"].startswith("https://") for row in historical), "historical urls")
    check(len(priors) == 33, "33 candidate priors")
    check(Counter(row["surface"] for row in priors) == Counter({surface: 3 for surface in EXPECTED_PRIMARY}), "three priors each")

    check(len(occurrences) == 79 and len({row["occurrence_id"] for row in occurrences}) == 79, "79 unique occurrences")
    check(len({row["locus"] for row in occurrences}) == 79, "79 unique target lines")
    check(len({row["page"] for row in occurrences}) == 54, "54 target pages")
    check({row["section"] for row in occurrences} == {"B", "H", "P", "S", "T"}, "five target sections")
    check(sum(int(row["paragraph_start"]) for row in occurrences) == 27, "27 paragraph starts")
    check(sum(int(row["paragraph_end"]) for row in occurrences) == 15, "15 paragraph ends")
    check(all(row["written_line_eva"].split()[0] == row["surface"] for row in occurrences), "surface starts each line")
    check(all(row["body_translation_claimed"] == "0" for row in occurrences), "no body translation claim")
    check(all(row["exact_whole_only"] == "1" and row["confirmed_lexeme"] == "0" for row in occurrences), "occurrence claim boundary")

    check(len(wholes) == 11 and {row["surface"] for row in wholes} == set(EXPECTED_PRIMARY), "eleven target wholes")
    selected = {row["surface"]: row["working_candidate_de"] for row in wholes}
    check(selected == EXPECTED_PRIMARY, "expected primary dictionary")
    check(all(row["alternate_1_de"] and row["alternate_2_de"] for row in wholes), "two rivals each")
    check(all(len({row["working_candidate_de"], row["alternate_1_de"], row["alternate_2_de"]}) == 3 for row in wholes), "distinct rivals")
    check(all(row["selection_gate"] == "TRIAD_RATE_GE_0.20__INITIAL_PURITY_GE_0.70__MIN5_INITIAL" for row in wholes), "fixed target gate")
    check(all(float(row["global_line_initial_purity"]) >= 0.7 for row in wholes), "target purity gate")
    check(all(float(row["recipe_triad_rate"]) >= 0.2 for row in wholes), "target triad gate")
    check(all(row["eva_spelling_used"] == "0" and row["component_export_credit"] == "0" for row in wholes), "no spelling or component credit")
    check(next(row for row in wholes if row["surface"] == "paiin")["working_confidence"] == "C0_FORCED_EXPLORATORY", "paiin weak confidence")

    pchor = next(row for row in wholes if row["surface"] == "pchor")
    ychor = next(row for row in wholes if row["surface"] == "ychor")
    check((pchor["reader_exact_line_initial_occurrences"], pchor["paragraph_initial_occurrences"], pchor["recipe_triad_lines"]) == ("7", "6", "3"), "pchor geometry")
    check((ychor["reader_exact_line_initial_occurrences"], ychor["paragraph_initial_occurrences"], ychor["recipe_triad_lines"]) == ("13", "0", "4"), "ychor geometry")
    family = [row for row in wholes if row["surface"] in {"ycheol", "ychol", "dcheol", "ycheor"}]
    check(sum(int(row["reader_exact_line_initial_occurrences"]) for row in family) == 26, "family 26 initials")
    check(sum(int(row["paragraph_initial_occurrences"]) for row in family) == 1, "family one start")
    check(sum(int(row["paragraph_final_occurrences"]) for row in family) == 9, "family nine ends")

    check(len(rankings) == 33, "33 candidate rankings")
    check(Counter(row["surface"] for row in rankings) == Counter({surface: 3 for surface in EXPECTED_PRIMARY}), "three rankings each")
    check(sum(int(row["selected_primary"]) for row in rankings) == 11, "eleven selected primaries")
    check(all(row["candidate_rank"] in {"1", "2", "3"} for row in rankings), "candidate ranks one to three")
    check(all(row["exact_whole_only"] == "1" and row["eva_spelling_used"] == "0" for row in rankings), "ranking claim boundary")

    check(len(comparators) == 4 and {row["surface"] for row in comparators} == {"ykar", "yteedy", "qotor", "dchey"}, "four comparators")
    check(all(float(row["global_line_initial_purity"]) < 0.7 for row in comparators), "comparator purity below gate")
    check(all(row["working_translation_assigned"] == "0" for row in comparators), "comparators not translated")

    check(len(neighbors) == 6, "six edit-one pairs")
    check(all(row["levenshtein_distance"] == "1" for row in neighbors), "all neighbor distance one")
    pair = next(row for row in neighbors if {row["left_surface"], row["right_surface"]} == {"pchor", "ychor"})
    check(pair["relation"] == "OPENER_VS_CONTINUATION_CONTRAST", "pchor ychor contrast")
    check(pair["paragraph_initial_rate_delta_left_minus_right"] == "0.857143", "pchor ychor start delta")
    check(all(row["component_meaning_inferred"] == "0" and row["whole_form_prediction_only"] == "1" for row in neighbors), "neighbor whole-only boundary")

    check(result["scope"] == {
        "candidate_rows": 33,
        "edit_distance_one_pairs": 6,
        "historical_formula_sources": 8,
        "low_purity_comparator_forms": 4,
        "target_complete_forms": 11,
        "target_initial_occurrences": 79,
        "target_pages": 54,
        "target_sections": 5,
    }, "result scope")
    check(result["primary_working_dictionary"] == EXPECTED_PRIMARY, "result dictionary")
    check(result["decisive_geometry"]["edit_distance_one_pchor_ychor"] == 1, "result pchor ychor distance")
    check(result["decisive_geometry"]["internal_near_form_family"]["paragraph_starts"] == 1, "result family starts")
    check(result["guard"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard exact")
    check(result["claim_boundary"] == {
        "body_translations_claimed": 0,
        "component_values": 0,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "f84_accessed": 0,
        "f84r_accessed": 0,
        "new_images_opened": 0,
        "new_pages_opened": 0,
    }, "claim boundary")

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

    with tempfile.TemporaryDirectory(prefix=".gdt757_replay_", dir=EXP) as temporary:
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
        "schema": "GDT757_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "primary_working_dictionary": result["primary_working_dictionary"],
        "decisive_geometry": result["decisive_geometry"],
        "claim_ceiling": (
            "Eleven exact-whole formula candidates cover 79 initial lines with "
            "explicit rivals; zero confirmed lexemes, body translations, "
            "component values, new pages, f84 or f84r access."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
