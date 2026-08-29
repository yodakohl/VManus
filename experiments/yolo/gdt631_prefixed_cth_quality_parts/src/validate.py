#!/usr/bin/env python3
"""Validate and byte-replay GDT631."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts"
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V7 = ROOT / "experiments/yolo/gdt630_outer_carrier_attachment/artifacts/WORKING_DICTIONARY_V7.tsv"

GENERATED = (
    ART / "PAGE_ALLOWLIST.tsv",
    ART / "PREFIXED_CTH_OCCURRENCES.tsv",
    ART / "CROSS_READER_PREFIX_REALIZATIONS.tsv",
    ART / "CROSS_READER_PREFIX_BOUNDARY_BRIDGES.tsv",
    ART / "TARGET_OUTER_BOUNDARY_BRIDGES.tsv",
    ART / "PREFIX_REMAINDER_MATRIX.tsv",
    ART / "PREFIX_REMAINDER_MINIMAL_PAIRS.tsv",
    ART / "LOCAL_PREFIX_CONTRASTS.tsv",
    ART / "SHARED_PART_SLOT_FRAMES.tsv",
    ART / "PREFIXED_CTH_QUALITY_CONTACTS.tsv",
    ART / "PREFIXED_CTH_LOCAL_QUALITY_NEIGHBORS.tsv",
    ART / "QUALITY_CONTACT_SUMMARY.tsv",
    ART / "REPEATED_CLAUSE_FRAMES.tsv",
    ART / "SECTION_PREFIX_PROFILE.tsv",
    ART / "EXTENDED_CTH_FACTOR_GRID.tsv",
    ART / "HISTORICAL_COMPOSITION_COMPARATORS.tsv",
    ART / "INHERITED_VISUAL_SCOPE.tsv",
    ART / "CONCRETE_CLAUSES_V3.tsv",
    ART / "PREFIX_ROLE_RANKING.tsv",
    ART / "WORKING_DICTIONARY_V8.tsv",
    RESULT,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    before = {path: path.read_bytes() for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False)
    check(completed.returncode == 0, "builder exits zero")
    expected = "GDT631 built: family=562 strict={'BARE': 408, 'SH': 36, 'CH': 115} prefixes={'BARE': 408, 'SH': 36, 'CH': 118} pairs={'CH': 17, 'SH': 5} bridges=1 slots=10 degree_contacts=66 local_quality=24 cases=34 dictionary=47"
    check(completed.stdout.strip() == expected, "builder summary")
    check(all(path.read_bytes() == before[path] for path in GENERATED), "builder replay is byte-identical")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT631_PREFIXED_CTH_QUALITY_PARTS_RESULT_V1", "result schema")
    check(result["status"] == "CH_SH_PRODUCTIVE_CTH_PREFIX_OPPOSITION__DRY_MOIST_DEFAULT_PROVISIONAL", "result status")
    content_hash = result.pop("content_sha256")
    check(content_hash == canonical_hash(result), "canonical result hash")
    result["content_sha256"] = content_hash
    check(result["guard"] == {
        "allowed_pages": 179,
        "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
        "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
    }, "guarded source scope")
    for path, digest in result["inputs"].items():
        check(sha256(ROOT / path) == digest, f"input hash {path}")
    for path, digest in result["outputs"].items():
        check(sha256(ROOT / path) == digest, f"output hash {path}")
    check(set(result["outputs"]) == {rel(path) for path in GENERATED if path != RESULT}, "result binds every generated evidence file")

    allow = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    check(len(allow) == 179 and len({row["page"] for row in allow}) == 179, "179-page allow-list")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in allow), "allow-list excludes forbidden folios")

    occurrences = read_tsv(ART / "PREFIXED_CTH_OCCURRENCES.tsv")
    check(len(occurrences) == 562, "562 direct cth-family occurrences")
    check(Counter(row["prefix"] for row in occurrences) == Counter({"BARE": 408, "CH": 118, "SH": 36}), "direct prefix occurrence partition")
    check(Counter(row["prefix"] for row in occurrences if row["in_inherited_cth_surface_deck"] == "1") == Counter({"BARE": 408, "CH": 115, "SH": 36}), "strict inherited-base partition")
    check(Counter(row["prefix"] for row in occurrences if row["triple_exact_token_stable"] == "1") == Counter({"BARE": 347, "CH": 102, "SH": 33}), "triple-exact prefix partition")
    for surface, count, loci, pages, stable in (("cthy", 92, 88, 50, 85), ("chcthy", 75, 74, 53, 69), ("shcthy", 29, 29, 17, 26)):
        selected = [row for row in occurrences if row["surface"] == surface]
        check(len(selected) == count and len({row["locus"] for row in selected}) == loci and len({row["page"] for row in selected}) == pages, f"primary form scope {surface}")
        check(sum(row["triple_exact_token_stable"] == "1" for row in selected) == stable, f"primary form stability {surface}")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in occurrences), "occurrences exclude forbidden folios")

    reader = read_tsv(ART / "CROSS_READER_PREFIX_REALIZATIONS.tsv")
    check(len(reader) == 154, "154 prefixed reader records")
    check(sum(row["triple_exact_token_stable"] == "1" for row in reader) == 135, "135 prefixed records triple exact")
    check(sum(row["any_split_prefix_reader"] == "1" for row in reader) == 0, "no source-prefixed chcthy token internally splits")

    matrix = read_tsv(ART / "PREFIX_REMAINDER_MATRIX.tsv")
    check(len(matrix) == 72, "72 direct remainders including extended rests")
    primary = {row["remainder"]: row for row in matrix}
    check((primary["y"]["bare_occurrences"], primary["y"]["ch_occurrences"], primary["y"]["sh_occurrences"]) == ("92", "75", "29"), "y remainder triple")
    check(all(row["k_occurrences"] == "0" and row["t_occurrences"] == "0" for row in matrix), "simple k/t null cells")
    pairs = read_tsv(ART / "PREFIX_REMAINDER_MINIMAL_PAIRS.tsv")
    check(len(pairs) == 22 and Counter(row["prefix"] for row in pairs) == Counter({"CH": 17, "SH": 5}), "twenty-two strict type pairs")
    check({row["remainder"] for row in pairs if row["prefix"] == "SH"} == {"y", "ey", "dy", "edy", "al"}, "five ch-sh shared remainders")

    bridges = read_tsv(ART / "CROSS_READER_PREFIX_BOUNDARY_BRIDGES.tsv")
    check(len(bridges) == 1, "one internal prefix boundary bridge")
    bridge = bridges[0]
    check(bridge["locus"] == "f21r.9" and bridge["fused_surface"] == "shcthey" and bridge["split_surface"] == "sh cthey", "f21 shcthey bridge")
    check((bridge["zl3b_mode"], bridge["it2a_mode"], bridge["rf1b_mode"]) == ("SPLIT_PREFIX", "FUSED", "SPLIT_PREFIX"), "f21 reader modes")
    outer = read_tsv(ART / "TARGET_OUTER_BOUNDARY_BRIDGES.tsv")
    check(len(outer) == 3 and {row["locus"] for row in outer} == {"f111r.53", "f81r.29", "f95v1.3"}, "three outer chcthy boundary bridges")

    local = read_tsv(ART / "LOCAL_PREFIX_CONTRASTS.tsv")
    check(len(local) == 5 and sum(row["both_triple_exact"] == "1" for row in local) == 4, "five local same-remainder contrasts")
    slots = read_tsv(ART / "SHARED_PART_SLOT_FRAMES.tsv")
    check(len(slots) == 10 and Counter(row["surface"] for row in slots) == Counter({"cthy": 6, "chcthy": 3, "shcthy": 1}), "shared terminal part slot partition")
    check(sum(row["target_triple_exact"] == "1" for row in slots) == 9, "nine stable terminal part slots")

    contacts = read_tsv(ART / "PREFIXED_CTH_QUALITY_CONTACTS.tsv")
    prefixed = [row for row in contacts if row["part_prefix"] != "BARE"]
    check(len(contacts) == 162 and len(prefixed) == 66, "degree contact base and prefix totals")
    check(sum(row["distance"] == "1" for row in prefixed) == 39, "thirty-nine immediate prefixed degree contacts")
    check(Counter(row["prefix_axis_relation"] for row in prefixed) == Counter({"ORTHOGONAL_AXIS": 60, "MATCHING_PREFIX_AXIS": 5, "OPPOSITE_PREFIX_AXIS": 1}), "prefixed degree-axis relation partition")
    immediate_axis = [row for row in prefixed if row["distance"] == "1" and row["prefix_axis_relation"] != "ORTHOGONAL_AXIS"]
    check(len(immediate_axis) == 4 and all(row["prefix_axis_relation"] == "MATCHING_PREFIX_AXIS" for row in immediate_axis), "all immediate same-axis degree contacts match")
    summary = {row["prefix"]: row for row in read_tsv(ART / "QUALITY_CONTACT_SUMMARY.tsv")}
    check(summary["BARE"]["part_occurrences_with_immediate_contact"] == "41", "bare immediate-contact baseline")
    check(summary["CH"]["part_occurrences_with_immediate_contact"] == "28" and summary["SH"]["part_occurrences_with_immediate_contact"] == "10", "prefixed immediate-contact targets")

    neighbors = read_tsv(ART / "PREFIXED_CTH_LOCAL_QUALITY_NEIGHBORS.tsv")
    check(len(neighbors) == 24 and Counter(row["prefix_axis_relation"] for row in neighbors) == Counter({"MATCHING_PREFIX_AXIS": 14, "OPPOSITE_PREFIX_AXIS": 6, "ORTHOGONAL_AXIS": 4}), "broader local quality-neighbor partition")
    neighbor_by_locus = {row["locus"]: row for row in neighbors}
    check(neighbor_by_locus["f24v.8"]["part_surface"] == "chcthy" and neighbor_by_locus["f24v.8"]["quality_surface"] == "shol" and neighbor_by_locus["f24v.8"]["prefix_axis_relation"] == "OPPOSITE_PREFIX_AXIS", "f24 sharp semantic warning")

    repeated = read_tsv(ART / "REPEATED_CLAUSE_FRAMES.tsv")
    check(len(repeated) == 7, "seven repeated concrete frames")
    repeated_by_clause = {row["surface_clause"]: row for row in repeated}
    for clause, count, stable in (("chcthy qokain", "4", "4"), ("qokain chcthy", "4", "3"), ("qokaiin shcthy", "3", "3"), ("qotain shcthy", "3", "3"), ("chaiin chcthy", "2", "2")):
        check(repeated_by_clause[clause]["occurrences"] == count and repeated_by_clause[clause]["triple_stable_occurrences"] == stable, f"repeated frame {clause}")
    cases = read_tsv(ART / "CONCRETE_CLAUSES_V3.tsv")
    check(len(cases) == 34 and all(row["reader_status"] == "TRIPLE_STABLE_COMPONENTS" for row in cases), "thirty-four concrete stable clauses")
    check(all("Arbeitsgut" not in row["working_reading_de"] and "ausführen" not in row["working_reading_de"] for row in cases), "no generic filler translations")

    factor = read_tsv(ART / "EXTENDED_CTH_FACTOR_GRID.tsv")
    check(len(factor) == 7, "seven occupied extended factor cells")
    factor_by_key = {(row["outer_wrapper"], row["quality_core"]): row for row in factor}
    check((factor_by_key[("BARE", "TCH")]["occurrences"], factor_by_key[("BARE", "TCH")]["triple_exact_occurrences"]) == ("1", "1"), "tchcthy singleton lead")
    check((factor_by_key[("O", "SH")]["occurrences"], factor_by_key[("O", "SH")]["triple_exact_occurrences"]) == ("1", "0"), "oshctho singleton warning")
    check(factor_by_key[("O", "NONE")]["occurrences"] == "32" and factor_by_key[("QO", "NONE")]["occurrences"] == "25", "o and qo cth wrapper leads")

    historical = read_tsv(ART / "HISTORICAL_COMPOSITION_COMPARATORS.tsv")
    check(len(historical) == 3 and {row["manuscript"].split(",")[0] for row in historical} == {"VI Fc 29", "Wellcome MS 542", "Wellcome MS 541"}, "three historical comparators")
    check(all(row["source_url"].startswith("https://") and any(marker in row["limit"] for marker in ("kein", "nicht")) for row in historical), "historical sources and limits")
    visual = read_tsv(ART / "INHERITED_VISUAL_SCOPE.tsv")
    check(len(visual) == 3 and all(row["new_image_opened"] == "0" for row in visual), "three inherited visual bounds and no new image")

    ranking = read_tsv(ART / "PREFIX_ROLE_RANKING.tsv")
    check(len(ranking) == 4 and ranking[0]["model"] == "QUALITY_PREFIX_PLUS_CTH_PART", "four-model role ranking")
    check(ranking[-1]["disposition"] == "REJECTED_AS_DEFAULT", "generic operation rejected")
    old_dictionary = read_tsv(V7)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V8.tsv")
    check(len(old_dictionary) == 38 and len(dictionary) == 47, "V8 consolidates thirty-eight plus nine entries")
    check(dictionary[:38] == old_dictionary, "all V7 entries retained byte-for-field")
    new_entries = {row["entry"]: row for row in dictionary[38:]}
    for entry in ("ch+cth*", "sh+cth*", "chcthy", "shcthy", "chcthy kchol daiin", "shol daiin shcthy", "QUALITY_PREFIX+CTH_PART", "tchcthy", "oshctho"):
        check(entry in new_entries, f"V8 entry {entry}")

    check(result["family"]["strict_inherited_base_occurrence_counts"] == {"BARE": 408, "CH": 115, "SH": 36}, "result strict family counts")
    check(result["family"]["cross_reader_prefix_boundary_bridges"] == 1 and result["family"]["target_outer_boundary_bridges"] == 3, "result bridge counts")
    check(result["quality_contacts"]["prefixed_within_three"] == 66 and result["quality_contacts"]["repeated_clause_frames"] == 7, "result quality totals")
    check(result["adjacent_quality_rivals"]["relation_counts"] == {"MATCHING_PREFIX_AXIS": 14, "OPPOSITE_PREFIX_AXIS": 6, "ORTHOGONAL_AXIS": 4}, "result broader neighbor partition")
    check(result["working_dictionary"] == {"entries": 47, "inherited_v7": 38, "new_v8": 9}, "result dictionary summary")

    privacy_pattern = re.compile(
        "/" + r"home/|/" + r"tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|AKIA[0-9A-Z]{16}|"
        r"gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|password\s*[=:]|api[_-]?key\s*[=:]|secret\s*[=:]",
        re.IGNORECASE,
    )
    required = (BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json", ART / "README.md", *GENERATED, RUN, BASE / "src/validate.py")
    for path in required:
        check(path.is_file(), f"required file {rel(path)}")
        check(not privacy_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {rel(path)}")

    payload = {
        "schema": "GDT631_VALIDATION_V1", "experiment_id": "GDT631", "status": "PASS",
        "check_count": len(checks), "checks": checks, "result_sha256": sha256(RESULT),
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
