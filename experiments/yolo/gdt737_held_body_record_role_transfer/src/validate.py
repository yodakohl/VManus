#!/usr/bin/env python3
"""Independent audit for GDT737."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
BASE = Path("experiments/yolo/gdt737_held_body_record_role_transfer")
EXP = ROOT / BASE
ART = EXP / "artifacts"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "HELD_120_LOCATION_AXIS_REPLICATES_STRONGLY__FROZEN_BODY_AFFINITY_2X2_FAILS_TRANSFER__"
    "H1_H4_DOWNGRADED_TO_WEAK_OCCUPANCY_ASSOCIATION__H2_H3_PARTIAL_AND_AIN_DOMINATED__"
    "REGISTER_GATED_HEAD_ROLES__EXACT_WHOLE_FALLBACK_REQUIRED__ZERO_LEXEMES__NO_NEW_PAGE"
)
GENERATED = (
    "HELD_811_OCCURRENCE_CONTEXTS.tsv", "HELD_120_BODY_REGISTRY.tsv", "HELD_273_FORM_ROLE_BRIDGE.tsv",
    "HELD_HEAD_TRANSFER_PROFILE.tsv", "HELD_BODY_CONTROLLED_POSITION.tsv", "HELD_PAGE_CONTROLLED_POSITION.tsv",
    "HELD_SECTION_POSITION.tsv", "HELD_ROLE_AXIS_TESTS.tsv", "HELD_HEAD_PAIR_AFFINITY.tsv",
    "AFFINITY_SENSITIVITY.tsv", "TRANSFER_MODEL_UPDATE.tsv", "V99R7_HELD_WHOLE_QUARANTINE.tsv",
    "HELD_BODY_WORKING_CANDIDATES.tsv", "RESULT.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT737", "manifest experiment id")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed pages forbidden")
    check(manifest["validation"] == {"status": "PASS", "artifact": str(VALIDATION_REL)}, "manifest validation contract")
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists: {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash: {binding['path']}")
    for binding in manifest["outputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists: {binding['path']}")
        if binding["path"] != str(VALIDATION_REL):
            check(sha256(path) == binding["sha256"], f"output hash: {binding['path']}")

    specs = read_tsv(EXP / "src/BODY_WORKING_SPECS.tsv")
    check(len(specs) == len({row["body"] for row in specs}) == 120, "120 unique body candidate specs")
    check(sum(int(row["occurrence_total"]) for row in specs) == 811, "body spec occurrence total 811")
    check({row["body"] for row in specs if row["confidence"] == "UNKNOWN"} == {"chr", "oiir", "oiis"}, "three honest unknown bodies")
    check(sum(row["confidence"] == "STRUCTURE_ONLY" for row in specs) == 6, "six structure-only bodies")
    retired = ("pulver", "samen", "saat", "wurzel", "holz")
    check(not any(word in row["concrete_body_role_de"].lower() for row in specs for word in retired), "no retired head noun in body candidate specs")

    occurrences = read_tsv(ART / "HELD_811_OCCURRENCE_CONTEXTS.tsv")
    check(len(occurrences) == 811, "811 occurrence rows")
    check(len({row["occurrence_id"] for row in occurrences}) == 811, "unique occurrence ids")
    check(len({(row["locus"], row["token_index"]) for row in occurrences}) == 811, "unique occurrence positions")
    check(len({row["form"] for row in occurrences}) == 273, "273 occurrence forms")
    check(len({row["body"] for row in occurrences}) == 120, "120 occurrence bodies")
    check(len({row["page"] for row in occurrences}) == 134, "134 occurrence pages")
    check(len({row["locus"] for row in occurrences}) == 697, "697 occurrence loci")
    check(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in occurrences), "no forbidden occurrence page")
    check(Counter(row["opaque_head_id"] for row in occurrences) == Counter({"H1": 147, "H2": 181, "H3": 91, "H4": 392}), "head occurrence totals")
    check(sum(int(row["all_readers_exact"]) for row in occurrences) == 619, "619 reader-exact occurrences")
    check(Counter(row["reader_status"] for row in occurrences) == Counter({"EXACT": 619, "SPLIT_ONLY": 20, "OTHER_VARIANT_OR_OMISSION": 172}), "reader status partition")
    check(all(int(row["body_candidate_renderer_license"]) == int(row["component_export_credit"]) == 0 for row in occurrences), "occurrence body candidates unlicensed")
    check(all(row["literal_head_lexeme"] == row["literal_body_lexeme"] == "UNRESOLVED" for row in occurrences), "occurrence lexemes unresolved")

    profiles = {row["opaque_head_id"]: row for row in read_tsv(ART / "HELD_HEAD_TRANSFER_PROFILE.tsv")}
    check(len(profiles) == 4, "four head profiles")
    expected_positions = {"H1": (108, 35, 4), "H2": (91, 67, 23), "H3": (8, 54, 29), "H4": (16, 309, 67)}
    expected_exact = {"H1": (80, 23, 1), "H2": (72, 46, 18), "H3": (3, 36, 18), "H4": (14, 252, 56)}
    for head in ("H1", "H2", "H3", "H4"):
        check(tuple(int(profiles[head][field]) for field in ("line_first", "line_middle", "line_last")) == expected_positions[head], f"{head} all positions")
        check(tuple(int(profiles[head][field]) for field in ("exact_line_first", "exact_line_middle", "exact_line_last")) == expected_exact[head], f"{head} exact positions")
    check([profiles[head]["mean_normalized_position"] for head in ("H1", "H2", "H4", "H3")] == ["0.148428", "0.324907", "0.574910", "0.665316"], "four-head mean position order")
    check((int(profiles["H1"]["paragraph_first"]), int(profiles["H2"]["paragraph_first"])) == (98, 3), "H1 H2 paragraph split")
    check([int(profiles[head]["split_only"]) for head in ("H1", "H2", "H3", "H4")] == [2, 6, 6, 6], "split-only head totals")

    bodies = read_tsv(ART / "HELD_BODY_CONTROLLED_POSITION.tsv")
    check(len(bodies) == 95, "95 bodies contain both location pairs")
    check(Counter(row["direction"] for row in bodies) == Counter({"ENTRY_EARLIER": 72, "INTERNAL_EARLIER": 19, "TIE": 4}), "body direction partition")
    reverse = {row["body"] for row in bodies if row["direction"] == "INTERNAL_EARLIER"}
    check(reverse == set("aiiin alol aral ary chdal chear cheos chos kain kchdy ky okeey oldy olkaiin os oty paiin shar shod".split()), "nineteen reverse bodies")
    check({row["body"] for row in bodies if row["direction"] == "TIE"} == {"aram", "okar", "olkeedy", "sheodar"}, "four tied bodies")
    pages = read_tsv(ART / "HELD_PAGE_CONTROLLED_POSITION.tsv")
    check(len(pages) == 62 and Counter(row["direction"] for row in pages) == Counter({"ENTRY_EARLIER": 52, "INTERNAL_EARLIER": 8, "TIE": 2}), "page-controlled direction partition")
    sections = read_tsv(ART / "HELD_SECTION_POSITION.tsv")
    check(len(sections) == 6 and {row["section"] for row in sections} == set("BCHPST"), "six represented sections")
    check({row["section"] for row in sections if row["direction"] == "INTERNAL_EARLIER"} == {"C"}, "section C only all-data reversal")
    check({row["section"] for row in sections if row["exact_direction"] == "INTERNAL_EARLIER"} == {"C"}, "section C only exact reversal")

    tests = {row["test_id"]: row for row in read_tsv(ART / "HELD_ROLE_AXIS_TESTS.tsv")}
    check(len(tests) == 13, "thirteen location and reader tests")
    expected_or = {"T01_ENTRY_FIRST": 29.502907, "T02_ENTRY_FIRST_EXACT": 36.780749,
                   "T03_ENTRY_FIRST_EXACT_NON_SINGLE": 40.862121, "T04_H1_H2_PARAGRAPH": 118.666667,
                   "T05_H1_H2_PARAGRAPH_EXACT": 157.774194, "T06_H3_H4_FINAL": 2.268897,
                   "T07_SPLIT_H2H3_H1H4": 3.063462, "T08_MH_BODY_SECTION": 10.922153,
                   "T09_MH_BODY_SECTION_LANGUAGE": 11.899427, "T10_OCC2_ALL": 27.487103,
                   "T11_OCC2_EXACT": 31.609756, "T12_OCC3_ALL": 34.545455, "T13_OCC3_EXACT": 57.468085}
    for test_id, expected in expected_or.items():
        check(abs(float(tests[test_id]["odds_ratio"]) - expected) < .000001, f"{test_id} odds ratio")

    affinity = read_tsv(ART / "HELD_HEAD_PAIR_AFFINITY.tsv")
    check(len(affinity) == 6, "six head-pair affinity rows")
    by_pair = {frozenset((row["head_a"], row["head_b"])): row for row in affinity}
    h23, h14 = by_pair[frozenset(("H2", "H3"))], by_pair[frozenset(("H1", "H4"))]
    check((h23["held_raw_count_cosine"], h23["held_reader_exact_cosine"], h23["held_raw_rank"], h23["held_exact_rank"]) == ("0.915084", "0.863550", "1", "1"), "H2 H3 partial affinity")
    check((h14["held_raw_count_cosine"], h14["held_reader_exact_cosine"], h14["held_raw_rank"], h14["held_exact_rank"]) == ("0.156632", "0.125962", "3", "4"), "H1 H4 frozen-test failure")
    check({frozenset((row["head_a"], row["head_b"])) for row in affinity if row["held_raw_rank"] in ("1", "2")} == {frozenset(("H2", "H3")), frozenset(("H3", "H4"))}, "raw top two violate frozen selected pair set")
    check((h14["held_binary_rank"], h23["held_binary_rank"]) == ("1", "2"), "selected pairs top two binary supporting diagnostic")
    check(abs(float(h23["held_binary_phi"]) - .028294) < .000001, "H2 H3 binary phi near zero")
    check(all(int(row["semantic_cluster_export"]) == 0 for row in affinity), "no affinity semantic export")
    sensitivity = {(row["pair"], row["excluded_bodies"]): row for row in read_tsv(ART / "AFFINITY_SENSITIVITY.tsv")}
    check(sensitivity[("H2-H3", "ain")]["raw_count_cosine"] == "0.620056", "H2 H3 without ain")
    check(sensitivity[("H2-H3", "ain|o|kar")]["raw_count_cosine"] == "0.522092", "H2 H3 without top three")

    registry = read_tsv(ART / "HELD_120_BODY_REGISTRY.tsv")
    candidates = read_tsv(ART / "HELD_BODY_WORKING_CANDIDATES.tsv")
    bridge = read_tsv(ART / "HELD_273_FORM_ROLE_BRIDGE.tsv")
    check(len(registry) == len(candidates) == 120, "120 body registry and candidate rows")
    check(Counter(int(row["head_occupancy"]) for row in registry) == Counter({2: 87, 3: 33}), "registry occupancy partition")
    check(len(bridge) == len({row["form"] for row in bridge}) == 273, "273 unique form role rows")
    check(sum(int(row["atlas_occurrences"]) for row in bridge) == 811 and sum(int(row["atlas_reader_exact"]) for row in bridge) == 619, "form bridge totals")
    check(all(int(row["body_candidate_renderer_license"]) == int(row["semantic_cluster_export"]) == int(row["component_export_credit"]) == 0 for row in bridge), "form bridge zero export")

    quarantine = read_tsv(ART / "V99R7_HELD_WHOLE_QUARANTINE.tsv")
    check(len(quarantine) == 82, "82 inherited held whole cards")
    check(Counter(row["gdt737_decision"] for row in quarantine) == Counter({"QUARANTINE_RETIRED_HEAD_NOUN_DERIVATION": 80, "RETAIN_CURRENT_EXACT_WHOLE_WORKING_DEFAULT": 2}), "80 to 2 whole quarantine split")
    retained = {row["surface"]: row["retained_exact_whole_meaning_de"] for row in quarantine if row["gdt737_decision"].startswith("RETAIN")}
    check(retained == {"solaiin": "drei Portionen Salz", "sols": "fertige Salzspecies"}, "two retained exact-whole working defaults")
    check({row["form"] for row in bridge if row["default_precedence"] == "CURRENT_CLEAN_EXACT_WHOLE"} == {"solaiin", "sols"}, "exact-whole form precedence")
    sain = next(row for row in quarantine if row["surface"] == "sain")
    lain = next(row for row in quarantine if row["surface"] == "lain")
    check(sain["retired_head_words_detected"] == "samen" and lain["retired_head_words_detected"] == "holz", "sain lain obsolete patients quarantined")

    updates = {row["claim_id"]: row for row in read_tsv(ART / "TRANSFER_MODEL_UPDATE.tsv")}
    check(len(updates) == 7 and updates["C04"]["held_result"] == "FAIL_FROZEN_FALSIFIER", "explicit GDT736 falsifier activation")
    check(updates["C07"]["new_live_status"] == "CLEAN_EXACT_WHOLE_THEN_OBSERVED_POSITION_ROLE_THEN_UNKNOWN", "corrected renderer precedence")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["inherited_allowlist_pages"] == 179 and result["scope"]["held_target_pages"] == 134, "result scope")
    check(result["scope"]["new_pages_used"] == 0 and not result["scope"]["f84_used"] and not result["scope"]["f84r_used"], "result sealed scope")
    check(result["target"]["held_bodies"] == 120 and result["target"]["held_forms"] == 273 and result["target"]["held_occurrences"] == 811, "result target")
    check(result["location_transfer"]["decision"] == "PASS_STRONG", "result location pass")
    check(result["affinity_transfer"]["decision"].startswith("FROZEN_FULL_2X2_FAIL"), "result affinity failure")
    check(result["renderer_repair"]["body_candidates_licensed_for_export"] == 0, "result candidate export zero")
    check(result["claims"]["head_or_body_lexemes_identified"] == result["claims"]["plaintext_translations_claimed"] == result["claims"]["component_export_credit"] == 0, "result claim ceiling")
    for relative, digest in result["artifact_hashes"].items():
        check(sha256(ROOT / relative) == digest, f"result artifact hash: {relative}")

    for path in [EXP / name for name in ("README.md", "METHOD.md", "PREREGISTRATION.md", "REPORT.md") if (EXP / name).exists()] + list(ART.glob("*")):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            check(re.search(r"/(?:home|Users)/[^/\s]+/", text) is None, f"no absolute local path: {path.name}")

    with tempfile.TemporaryDirectory(prefix="gdt737-replay-") as temporary:
        replay = Path(temporary)
        completed = subprocess.run([sys.executable, str(EXP / "src/run.py"), "--output-dir", str(replay)],
                                   cwd=ROOT, text=True, capture_output=True, check=False)
        check(completed.returncode == 0, "builder replay exits zero")
        for name in GENERATED:
            check((replay / name).read_bytes() == (ART / name).read_bytes(), f"byte-identical replay: {name}")

    validation = {
        "schema": "GDT737_VALIDATION_V1", "status": "PASS", "experiment_id": "GDT737",
        "checks_passed": len(checks), "checks": checks,
        "validated_result_sha256": sha256(ART / "RESULT.json"), "builder_replay": "BYTE_IDENTICAL",
        "claim_ceiling": (
            "The held transfer generalizes occurrence-conditioned record-location roles only. The frozen full body-affinity "
            "2x2 fails; H2-H3 is a partial frequency lead and H1-H4 an occupancy hint. Body candidates are exploratory and "
            "unlicensed. No head/body lexeme, plaintext, component export, physical-glyph, new-page, f84, or f84r claim."
        ),
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "checks_passed": len(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
