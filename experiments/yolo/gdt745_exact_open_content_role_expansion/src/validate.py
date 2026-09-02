#!/usr/bin/env python3
"""Artifact-level validation and byte replay for GDT745."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
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
BASE = Path("experiments/yolo/gdt745_exact_open_content_role_expansion")
EXP = ROOT / BASE
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__41_EXACT_OPEN_SURFACES__136_CACHE_OCCURRENCES__53_PAGES__"
    "22_CROSS_PAGE_WHOLES__136_OF_136_CENTERED_CONTEXTS_OPEN__"
    "34_MULTIWHOLE_AXIS_CONSENSUS__17_DISTANCE1_MULTIWHOLE__"
    "41_EXPLORATORY_WORKING_DEFAULTS__ZERO_LITERAL_IDENTITIES__"
    "ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "EXACT_136_OCCURRENCE_CONTEXTS.tsv",
    "GDT744_44_FIELD_MEMBERSHIPS.tsv",
    "WHOLE_NEIGHBOR_ANALOGY_DECK.tsv",
    "CONTENT_41_ROLE_CENSUS.tsv",
    "CROSS_PAGE_ROLE_CARDS.tsv",
    "FOCUS_20_CROSS_PAGE_ROLE_READER.tsv",
    "GDT745_EXACT_CONTENT_ROLE_READER.md",
    "GDT745_GDT388_CONTENT_ROLE_EDGE_PACKET.tsv",
    "GDT745_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
EXPECTED_TIERS = Counter({
    "A3_DISTANCE1_MULTIWHOLE_CONSENSUS": 17,
    "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS": 12,
    "A2_DISTANCE2_MULTIWHOLE_CONSENSUS": 5,
    "A1_MIXED_NEIGHBORHOOD": 3,
    "A1_SINGLE_NEIGHBOR_LEAD": 2,
    "A0_NO_CLEAN_NEIGHBOR": 2,
})
RETIRED = ("pulver", "samen", "saat", "wurzel", "holz")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def values(text: str) -> set[str]:
    if text in {"", "NONE", "NA", "OPEN"}:
        return set()
    return set(text.split("|"))


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + int(left_char != right_char),
            ))
        previous = current
    return previous[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT745", "manifest id")
    check(manifest["slug"] == "exact_open_content_role_expansion", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(
        manifest["dependencies"] == ["GDT734", "GDT739", "GDT743", "GDT744"],
        "manifest dependencies",
    )
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed selectors")
    check(bool(manifest["question"]) and bool(manifest["claim_ceiling"]), "manifest question ceiling")
    check(
        manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"},
        "manifest validation contract",
    )
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    candidates = read_tsv(
        ROOT / "experiments/yolo/gdt744_historical_microfield_channel_bridge/artifacts/"
        "UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv"
    )
    candidate_surfaces = {row["candidate_surface"] for row in candidates}
    check(len(candidates) == 42, "42 inherited seed cells")
    check(len(candidate_surfaces) == 41, "41 inherited seed surfaces")
    check(not any(row["page"].startswith("f84") for row in candidates), "seed sealed exclusion")

    defaults = read_tsv(SRC / "WORKING_DEFAULT_OVERRIDES.tsv")
    manual = read_tsv(SRC / "MANUAL_FOCUS_ASSESSMENTS.tsv")
    check(len(defaults) == 41 and {row["candidate_surface"] for row in defaults} == candidate_surfaces, "41 manual defaults")
    check(len(manual) == 20 and len({row["focus_id"] for row in manual}) == 20, "20 manual focus rows")
    for row in defaults:
        check(bool(row["next_working_meaning_de"]), f"default meaning {row['candidate_surface']}")
        check(bool(row["meaning_rationale_de"]), f"default rationale {row['candidate_surface']}")
        check("Arbeitsgut" not in row["next_working_meaning_de"], f"no generic work item {row['candidate_surface']}")

    occurrences = read_tsv(art / "EXACT_136_OCCURRENCE_CONTEXTS.tsv")
    check(len(occurrences) == 136, "136 occurrence contexts")
    check(len({row["cell_id"] for row in occurrences}) == 136, "unique occurrence cells")
    check(len({row["page"] for row in occurrences}) == 53, "53 occurrence pages")
    check(len({row["locus"] for row in occurrences}) == 121, "121 occurrence loci")
    check({row["candidate_surface"] for row in occurrences} == candidate_surfaces, "occurrence candidate coverage")
    check(sum(int(row["candidate_reader_exact"]) for row in occurrences) == 123, "123 reader-exact occurrences")
    check(sum(int(row["gdt744_seed_occurrence"]) for row in occurrences) == 42, "42 recovered seed occurrences")
    check(sum(int(row["external_to_gdt744_seed"]) for row in occurrences) == 94, "94 external occurrences")
    check(sum(int(row["boundary_complete"]) for row in occurrences) == 67, "67 complete centered windows")
    check(Counter(row["context_channel"] for row in occurrences) == Counter({"OPEN": 136}), "all centered channels open")
    for row in occurrences:
        address = f"{row['locus']}@{row['candidate_ordinal']}"
        check(not row["page"].startswith("f84"), f"sealed occurrence {address}")
        check(row["strong_anchor_count"] == "0", f"zero direct anchors {address}")
        check(row["strong_anchor_surfaces"] == "NONE", f"no direct anchor surfaces {address}")
        check(row["context_informative"] == "0", f"direct context explicitly open {address}")
        check(row["literal_identity"] == "OPEN", f"literal identity open {address}")
        check(row["confirmed_lexeme"] == "0", f"zero lexeme {address}")
        check(row["component_export_credit"] == "0", f"zero component {address}")
        check(row["unseen_form_export"] == "0", f"zero unseen export {address}")

    memberships = read_tsv(art / "GDT744_44_FIELD_MEMBERSHIPS.tsv")
    check(len(memberships) == 44, "44 inherited field memberships")
    check({row["candidate_surface"] for row in memberships} == candidate_surfaces, "field membership surface coverage")
    check(sum(int(row["gdt744_seed_membership"]) for row in memberships) == 42, "42 seed memberships")
    member_pages: dict[str, set[str]] = defaultdict(set)
    member_roles: dict[str, set[str]] = defaultdict(set)
    for row in memberships:
        member_pages[row["candidate_surface"]].add(row["page"])
        if row["field_role_family"] not in {"OPEN", "MATERIA_OR_INGREDIENT"}:
            member_roles[row["candidate_surface"]].add(row["field_role_family"])
        check(row["literal_identity"] == "OPEN", f"membership literal open {row['membership_id']}")
        check(row["component_export_credit"] == "0", f"membership component zero {row['membership_id']}")
    check([surface for surface, pages in member_pages.items() if len(pages) >= 2] == ["qochey"], "only qochey crosses field pages")
    check([surface for surface, roles in member_roles.items() if len(roles) > 1] == ["qochey"], "only qochey has field-role conflict")

    dictionary = read_tsv(
        ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/"
        "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
    )
    dictionary_by_id = {row["reading_id"]: row for row in dictionary}
    check(len(dictionary) == 1606 and len(dictionary_by_id) == 1606, "1606 unique dictionary readings")
    analogy = read_tsv(art / "WHOLE_NEIGHBOR_ANALOGY_DECK.tsv")
    check(len(analogy) == 213, "213 whole-neighbor relations")
    check(len({row["analogy_id"] for row in analogy}) == 213, "unique analogy ids")
    for row in analogy:
        relation = row["analogy_id"]
        check(row["candidate_surface"] in candidate_surfaces, f"candidate relation {relation}")
        check(row["candidate_surface"] != row["known_neighbor_surface"], f"nonself relation {relation}")
        distance = levenshtein(row["candidate_surface"], row["known_neighbor_surface"])
        check(distance == int(row["levenshtein_distance"]), f"independent distance {relation}")
        check(distance in {1, 2}, f"bounded edit distance {relation}")
        check(int(row["levenshtein_distance"]) <= int(row["selected_radius"]), f"selected radius {relation}")
        check(row["relation_scope"] == "EXACT_WHOLE_EDIT_ANALOGY_ONLY", f"whole relation scope {relation}")
        check(row["literal_identity_credit"] == "0", f"relation literal zero {relation}")
        check(row["component_export_credit"] == "0", f"relation component zero {relation}")
        reading_ids = row["known_neighbor_reading_ids"].split("|")
        check(bool(reading_ids), f"relation reading ids {relation}")
        for reading_id in reading_ids:
            check(reading_id in dictionary_by_id, f"dictionary reading exists {relation}:{reading_id}")
            source = dictionary_by_id[reading_id]
            check(source["surface"] == row["known_neighbor_surface"], f"dictionary surface {relation}:{reading_id}")
            check(source["working_model_level"].startswith(("W2", "W3")), f"dictionary W23 {relation}:{reading_id}")
            check(source["gdt734_composition_semantic_credit"] == "0", f"dictionary composition zero {relation}:{reading_id}")
            check(source["gdt734_component_export_allowed"] == "0", f"dictionary component zero {relation}:{reading_id}")
            check(not any(word in source["working_meaning_de"].lower() for word in RETIRED), f"retired patient excluded {relation}:{reading_id}")

    census = read_tsv(art / "CONTENT_41_ROLE_CENSUS.tsv")
    check(len(census) == 41 and {row["candidate_surface"] for row in census} == candidate_surfaces, "41-row census")
    check(Counter(row["analogy_confidence_level"] for row in census) == EXPECTED_TIERS, "exact analogy tiers")
    check(sum(row["analogy_consensus_axes"] != "NONE" for row in census) == 34, "34 consensus-axis surfaces")
    check(sum(int(row["manual_default_applied"]) for row in census) == 41, "41 manual defaults applied")
    check(sum(int(row["cache_pages"]) >= 2 for row in census) == 22, "22 cross-page surfaces")
    occurrence_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    analogy_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    default_map = {row["candidate_surface"]: row for row in defaults}
    for row in occurrences:
        occurrence_by_surface[row["candidate_surface"]].append(row)
    for row in analogy:
        analogy_by_surface[row["candidate_surface"]].append(row)
    for row in census:
        surface = row["candidate_surface"]
        source_rows = occurrence_by_surface[surface]
        check(len(source_rows) == int(row["cache_occurrences"]), f"census occurrence count {surface}")
        check(len({item["page"] for item in source_rows}) == int(row["cache_pages"]), f"census page count {surface}")
        check(sum(int(item["candidate_reader_exact"]) for item in source_rows) == int(row["reader_exact_occurrences"]), f"census exact count {surface}")
        check(row["next_working_meaning_de"] == default_map[surface]["next_working_meaning_de"], f"manual meaning join {surface}")
        check(row["meaning_rationale_de"] == default_map[surface]["meaning_rationale_de"], f"manual rationale join {surface}")
        check(row["next_renderer_scope"] == "EXACT_WHOLE_EXPLORATORY_ANALOGY_ONLY", f"census scope {surface}")
        check(row["next_literal_identity"] == "OPEN", f"census literal open {surface}")
        check(row["next_confirmed_lexeme"] == "0", f"census lexeme zero {surface}")
        check(row["next_component_export_credit"] == "0", f"census component zero {surface}")
        if row["analogy_confidence_level"] == "A0_NO_CLEAN_NEIGHBOR":
            check(not analogy_by_surface[surface], f"no-neighbor deck empty {surface}")
        else:
            check(len(analogy_by_surface[surface]) == int(row["analogy_neighbor_wholes"]), f"analogy neighbor count {surface}")
            check(values(row["analogy_neighbor_surfaces"]) == {item["known_neighbor_surface"] for item in analogy_by_surface[surface]}, f"analogy surface set {surface}")

    cards = read_tsv(art / "CROSS_PAGE_ROLE_CARDS.tsv")
    check(len(cards) == 22 and len({row["candidate_surface"] for row in cards}) == 22, "22 cross-page cards")
    census_map = {row["candidate_surface"]: row for row in census}
    check({row["candidate_surface"] for row in cards} == {row["candidate_surface"] for row in census if int(row["cache_pages"]) >= 2}, "all cross-page forms carded")
    for row in cards:
        source = census_map[row["candidate_surface"]]
        check(row["next_working_meaning_de"] == source["next_working_meaning_de"], f"card meaning {row['candidate_surface']}")
        check(row["analogy_confidence_level"] == source["analogy_confidence_level"], f"card tier {row['candidate_surface']}")
        check(row["renderer_scope"] == "EXACT_WHOLE_ROLE_CARD_ONLY_NO_LITERAL_SUBSTANCE", f"card scope {row['candidate_surface']}")
        check(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0", f"card literal ceiling {row['candidate_surface']}")
        check(row["component_export_credit"] == "0", f"card component zero {row['candidate_surface']}")

    focus = read_tsv(art / "FOCUS_20_CROSS_PAGE_ROLE_READER.tsv")
    manual_map = {row["focus_id"]: row for row in manual}
    check(len(focus) == 20 and len({row["candidate_surface"] for row in focus}) == 20, "20 distinct focus forms")
    for row in focus:
        spec = manual_map[row["focus_id"]]
        check(row["candidate_surface"] == spec["expected_surface"], f"focus surface {row['focus_id']}")
        check(row["locus"] == spec["expected_locus"], f"focus locus {row['focus_id']}")
        check(row["manual_assessment"] == spec["manual_assessment"], f"focus assessment {row['focus_id']}")
        check(row["manual_note"] == spec["manual_note"], f"focus note {row['focus_id']}")
        check(row["context_channel"] == "OPEN" and row["strong_anchor_count"] == "0", f"focus direct context open {row['focus_id']}")
        check(row["literal_identity"] == "OPEN", f"focus literal open {row['focus_id']}")

    reader_text = (art / "GDT745_EXACT_CONTENT_ROLE_READER.md").read_text(encoding="utf-8")
    check("Arbeitsgut" not in reader_text and "Arbeitszyklus" not in reader_text, "reader excludes generic work prose")
    check(reader_text.count("### G745-F") == 20, "reader contains twenty focus contexts")
    for surface in {row["candidate_surface"] for row in cards}:
        check(f"`{surface}`" in reader_text, f"reader card surface {surface}")

    edge = read_tsv(art / "GDT745_GDT388_CONTENT_ROLE_EDGE_PACKET.tsv")
    intake = json.loads((art / "GDT745_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check(len(edge) == 1 and edge[0]["relation_type"] == "EXACT_WHOLE_EDIT_NEIGHBOR_ANALOGY", "one analogy edge")
    check(edge[0]["geometry_only_selection"] == "FALSE", "edge nongeometry")
    check(edge[0]["ambiguity_state"] == "ANALOGY_ONLY_LITERAL_IDENTITY_OPEN", "edge ambiguity ceiling")
    check(intake["status"] == "INVALID_PACKET" and not intake["score_ready"], "edge intake invalid not score-ready")
    check(intake["errors"] == ["edge row 2: formal access is not sealed"], "edge fails only formal access")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT745_EXACT_OPEN_CONTENT_ROLE_EXPANSION_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["cache_occurrences"] == 136, "result occurrence scope")
    check(result["scope"]["cache_pages"] == 53, "result page scope")
    check(result["scope"]["cross_page_surfaces"] == 22, "result cross-page scope")
    check(result["scope"]["reader_exact_occurrences"] == 123, "result reader exact")
    check(result["scope"]["inherited_allowed_pages"] == 179, "result inherited allow-list")
    check(not result["scope"]["f84_used"] and not result["scope"]["f84r_used"], "result sealed exclusion")
    check(result["contexts"]["channel_counts"] == {"OPEN": 136}, "result direct context negative")
    check(result["field_membership"]["all_memberships"] == 44, "result memberships")
    check(result["whole_analogy"]["analogy_relations"] == 213, "result analogy relations")
    check(result["whole_analogy"]["manual_defaults_applied"] == 41, "result manual defaults")
    check(result["roles"]["analogy_confidence_tier_counts"] == dict(sorted(EXPECTED_TIERS.items())), "result analogy tiers")
    check(all(value == 0 for value in result["claims"].values()), "result claim ceiling zeros")
    for name in GENERATED[:-1]:
        key = str(BASE / "artifacts" / name)
        check(result["artifact_hashes"][key] == sha256(art / name), f"result artifact hash {name}")

    with tempfile.TemporaryDirectory(prefix=".gdt745_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay exits zero")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay file exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT745_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": {
            "candidate_surfaces": 41,
            "cache_occurrences": 136,
            "cache_pages": 53,
            "field_memberships": 44,
            "whole_analogy_relations": 213,
            "cross_page_cards": 22,
        },
        "claim_ceiling": {
            "confirmed_lexemes": 0,
            "literal_identifications": 0,
            "component_export_credit": 0,
            "unseen_form_predictions": 0,
        },
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
