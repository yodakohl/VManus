#!/usr/bin/env python3
"""Invariant and byte-replay validator for GDT758."""

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
BASE_REL = Path("experiments/yolo/gdt758_ychor_follower_global_content_census")
EXP = ROOT / BASE_REL
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
GENERATED = (
    "FOLLOWER_11_1141_OCCURRENCE_ATLAS.tsv",
    "FOLLOWER_11_GLOBAL_CENSUS.tsv",
    "FOLLOWER_11_CLEAN_WHOLE_ANALOGY.tsv",
    "FOLLOWER_11_EXACT_ADJACENCY_ATLAS.tsv",
    "ORDERED_VALUE_FOLLOWER_COMPARATOR.tsv",
    "HISTORICAL_FOLLOWER_COMPARATORS.tsv",
    "YCHOR_71_REVISED_BODY_TOKENS.tsv",
    "YCHOR_13_REVISED_READER.tsv",
    "GDT758_WORKING_DICTIONARY.md",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__11_YCHOR_FOLLOWER_WHOLES__1141_EXACT_OCCURRENCES__"
    "13_DIRECT_YCHOR_POSITIONS__S_EQUAL_AMOUNT_LEAD_25_OF99_ORDERED_VALUE_"
    "FOLLOWERS__23_S_TO_AIIN_BIGRAMS__8_EXACT_SPAN_RENDER_RULES__"
    "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)
EXPECTED_DICTIONARY = {
    "ar": "Teil / Anteil",
    "chol": "trocken / getrocknet",
    "chor": "Pflanzenteil, wahrscheinlich Blüten-/Samenstand",
    "chshoty": "kalte Trockenzubereitung",
    "cthy": "Blattgut / Blattdroge",
    "odol": "abgemessene Zubereitung",
    "oky": "erste Wärmestufe / heiß zu Beginn",
    "ols": "abgeseihtes Endprodukt",
    "qokchol": "erhitzt und getrocknet",
    "s": "je / zu gleichen Teilen",
    "sheol": "feucht / eingeweicht",
}
EXPECTED_COUNTS = {
    "ar": 242, "chol": 303, "chor": 176, "chshoty": 1,
    "cthy": 85, "odol": 2, "oky": 80, "ols": 12,
    "qokchol": 15, "s": 154, "sheol": 71,
}
EXPECTED_ANALOGY = {
    "ar": "PART|MATERIAL",
    "chol": "DRY",
    "chor": "DRY",
    "chshoty": "COLD|DRY|PREPARATION",
    "cthy": "NONE",
    "odol": "AMOUNT|PREPARATION",
    "oky": "NONE",
    "ols": "NONE",
    "qokchol": "HOT|DRY",
    "s": "PART",
    "sheol": "MOIST",
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
    census = read_tsv(ART / GENERATED[1])
    analogy = read_tsv(ART / GENERATED[2])
    adjacency = read_tsv(ART / GENERATED[3])
    values = read_tsv(ART / GENERATED[4])
    historical = read_tsv(ART / GENERATED[5])
    body = read_tsv(ART / GENERATED[6])
    lines = read_tsv(ART / GENERATED[7])
    priors = read_tsv(EXP / "src/FOLLOWER_CANDIDATE_PRIORS.tsv")
    spans = read_tsv(EXP / "src/YCHOR_EXACT_SPAN_RENDER_RULES.tsv")

    check(manifest["experiment_id"] == "GDT758", "manifest id")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(result["status"] == STATUS, "result status")

    check(len(priors) == 11 and len({row["surface"] for row in priors}) == 11, "eleven unique priors")
    check({row["surface"]: row["primary_candidate_de"] for row in priors} == EXPECTED_DICTIONARY, "prior dictionary")
    check(all(row["alternate_1_de"] and row["alternate_2_de"] for row in priors), "two prior rivals present")
    check(all(len({row["primary_candidate_de"], row["alternate_1_de"], row["alternate_2_de"]}) == 3 for row in priors), "three distinct candidates each")
    check(all(row["claim_scope"] == "EXACT_WHOLE_REPLACEABLE_DEFAULT" for row in priors), "whole-only prior scope")
    check(len(spans) == 8 and len({row["span_id"] for row in spans}) == 8, "eight unique span rules")
    check(all(row["claim_scope"] == "EXACT_OBSERVED_YCHOR_SPAN_ONLY" for row in spans), "span scope")

    check(len(occurrences) == 1141, "1141 target occurrences")
    check(len({row["gdt758_occurrence_id"] for row in occurrences}) == 1141, "unique occurrence ids")
    check(Counter(row["surface"] for row in occurrences) == Counter(EXPECTED_COUNTS), "target occurrence counts")
    check(len({row["page"] for row in occurrences}) == 175, "175 target pages")
    check(len({row["locus"] for row in occurrences}) == 907, "907 target loci")
    check(sum(int(row["directly_after_ychor"]) for row in occurrences) == 13, "thirteen direct ychor positions")
    check({row["surface"] for row in occurrences if row["directly_after_ychor"] == "1"} == set(EXPECTED_DICTIONARY), "all eleven direct follower forms represented")
    check(all(row["reader_exact_target"] == "1" and row["exact_whole_only"] == "1" for row in occurrences), "reader exact whole occurrences")
    check(all(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0" for row in occurrences), "occurrence claim boundary")
    check(not any(row["page"].startswith("f84") for row in occurrences), "no forbidden page in occurrence atlas")

    check(len(census) == 11 and {row["surface"] for row in census} == set(EXPECTED_DICTIONARY), "eleven census rows")
    check({row["surface"]: row["gdt758_primary_candidate_de"] for row in census} == EXPECTED_DICTIONARY, "census dictionary")
    check({row["surface"]: row["analogy_consensus_axes"] for row in census} == EXPECTED_ANALOGY, "expected analogy axes")
    check(sum(int(row["reader_exact_occurrences"]) for row in census) == 1141, "census occurrence total")
    check(sum(int(row["direct_ychor_predecessor_occurrences"]) for row in census) == 13, "census direct total")
    check(next(row for row in census if row["surface"] == "cthy")["gdt758_renderer_value_de"] == "Blattgut", "cthy leaf-drug repair")
    check(next(row for row in census if row["surface"] == "chol")["gdt758_renderer_value_de"] == "trocken/getrocknet", "chol carrier removal")
    check(next(row for row in census if row["surface"] == "s")["gdt756_candidate_de"] == "Samen", "s retired source recorded")
    check(next(row for row in census if row["surface"] == "s")["gdt758_renderer_value_de"] == "je", "s replacement recorded")
    check(all(row["positive_evidence"] and row["counterevidence"] for row in census), "evidence and counterevidence each")
    check(all(row["eva_spelling_used"] == "0" and row["confirmed_lexeme"] == "0" for row in census), "census claim boundary")

    check(len(analogy) == 80 and len({row["analogy_id"] for row in analogy}) == 80, "80 unique analogy relations")
    check(all(row["relation_scope"] == "EXACT_WHOLE_EDIT_ANALOGY_ONLY" for row in analogy), "analogy whole-only scope")
    check(all(row["literal_identity_credit"] == "0" and row["component_export_credit"] == "0" for row in analogy), "analogy claim boundary")

    check(len(adjacency) == 1225, "1225 exact adjacency relations")
    s_aiin = next(row for row in adjacency if row["surface"] == "s" and row["neighbor_side"] == "RIGHT" and row["neighbor_surface"] == "aiin")
    check(s_aiin["exact_pair_count"] == "23", "23 exact s aiin pairs")
    check(s_aiin["target_exact_neighbor_contexts"] == "99", "99 exact right contexts for s")
    check(s_aiin["descriptive_lift"] == "14.493663", "s aiin exact lift")
    check(s_aiin["side_frequency_rank"] == "1", "aiin top s follower")
    check(all(row["semantic_equivalence_inferred"] == "0" and row["component_export_credit"] == "0" for row in adjacency), "adjacency claim boundary")

    check(len(values) == 100 and len({row["surface"] for row in values}) == 100, "100 value follower comparator forms")
    s_value = next(row for row in values if row["surface"] == "s")
    check((s_value["ordered_value_follower_hits"], s_value["exact_right_contexts"]) == ("25", "99"), "s ordered values 25 of 99")
    check(s_value["ordered_value_follower_counts"] == "ain:1|aiin:23|aiiin:1", "s ordered value detail")
    check(s_value["ordered_value_descriptive_lift"] == "11.684203", "s ordered value lift")
    check(s_value["ordered_value_hit_count_rank"] == "3", "s value hit rank three")
    check(s_value["ordered_value_share_rank_min20_right_contexts"] == "3", "s value share rank three")
    check(s_value["aiin_hit_count_rank"] == "2", "s aiin hit rank two")
    check(values[0]["surface"] == "or" and values[1]["surface"] == "ar" and values[2]["surface"] == "s", "or ar s leading value ecology")
    check(all(row["numeric_value_or_unit_confirmed"] == "0" for row in values), "value comparator no numeric confirmation")

    check(len(historical) == 24 and len({row["candidate_id"] for row in historical}) == 24, "24 historical comparators")
    check({"E004", "E005", "E006", "E015", "E022", "E023", "E032"}.issubset({row["candidate_id"] for row in historical}), "decisive historical classes present")
    check(all(url.startswith("https://") for row in historical for url in row["primary_urls"].split(" || ")), "historical urls")
    check(all(row["voynich_spelling_match_scored"] == "0" and row["historical_expression_identified_with_target"] == "0" for row in historical), "historical claim boundary")

    check(len(body) == 71 and len({row["gdt756_body_token_id"] for row in body}) == 71, "71 revised body tokens")
    check(sum(int(row["candidate_changed"]) for row in body) == 23, "23 body token revisions")
    check(all(row["gdt758_candidate_de"] for row in body), "no missing body default")
    check(all(row["candidate_not_plaintext"] == "1" and row["component_export_credit"] == "0" for row in body), "body claim boundary")
    check(next(row for row in body if row["locus"] == "f93r.28" and row["surface"] == "s")["gdt758_candidate_de"] == "zu gleichen Teilen", "line-final s grammatical rendering")

    check(len(lines) == 13 and len({row["locus"] for row in lines}) == 13, "thirteen revised lines")
    check(sum(int(row["body_token_count"]) for row in lines) == 71, "line body token total")
    check(all(row["all_body_tokens_have_candidate_default"] == "1" for row in lines), "all line defaults present")
    used_spans = {item for row in lines for item in row["applied_span_rule_ids"].split("|") if item != "NONE"}
    check(used_spans == {row["span_id"] for row in spans}, "all eight span rules used")
    check("je eine Handvoll" in next(row for row in lines if row["locus"] == "f24r.8")["span_composed_candidate_render_de"], "s om span rendering")
    check("trockenes Blattgut" in next(row for row in lines if row["locus"] == "f45v.9")["span_composed_candidate_render_de"], "cthy chol span rendering")
    check("drei Anteile" in next(row for row in lines if row["locus"] == "f86v5.20")["span_composed_candidate_render_de"], "ar aiin span rendering")
    check("zu gleichen Teilen" in next(row for row in lines if row["locus"] == "f93r.28")["span_composed_candidate_render_de"], "line-final s rendering")
    check(all(row["candidate_line_not_plaintext"] == "1" and row["confirmed_lexeme"] == "0" for row in lines), "line claim boundary")

    check(result["scope"] == {
        "changed_ychor_body_tokens": 23,
        "clean_whole_analogy_relations": 80,
        "direct_ychor_follower_positions": 13,
        "exact_adjacency_relations": 1225,
        "exact_span_render_rules": 8,
        "historical_expression_classes": 24,
        "ordered_value_comparator_forms": 100,
        "reader_exact_loci": 907,
        "reader_exact_occurrences": 1141,
        "reader_exact_pages": 175,
        "revised_ychor_body_tokens": 71,
        "revised_ychor_lines": 13,
        "target_complete_forms": 11,
    }, "result scope")
    check(result["primary_working_dictionary"] == EXPECTED_DICTIONARY, "result dictionary")
    check(result["strongest_correction"]["new_candidate"] == "je / zu gleichen Teilen", "result s correction")
    check(result["strongest_correction"]["s_aiin_exact_pairs"] == 23, "result s aiin count")
    check(result["legacy_evidence"] == {
        "gdt625_cthy_herbal_occurrences": 90,
        "gdt625_cthy_zl3b_occurrences": 92,
        "gdt629_triple_exact_chor_chol_daiin_clauses": 2,
    }, "legacy evidence")
    check(result["guard"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard exact")
    check(result["claim_boundary"] == {
        "component_values": 0,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
        "historical_graphic_matches": 0,
        "new_images": 0,
        "new_pages": 0,
        "new_transcriptions": 0,
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

    with tempfile.TemporaryDirectory(prefix=".gdt758_replay_", dir=EXP) as temporary:
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
        "schema": "GDT758_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "primary_working_dictionary": result["primary_working_dictionary"],
        "strongest_correction": result["strongest_correction"],
        "claim_ceiling": (
            "Eleven exact-whole follower defaults and eight observed span "
            "renderings remain replaceable candidates; zero confirmed lexemes, "
            "plaintext clauses, graphic matches, component values or new pages."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
