#!/usr/bin/env python3
"""Validate and byte-replay GDT630."""

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
BASE = ROOT / "experiments/yolo/gdt630_outer_carrier_attachment"
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V6 = ROOT / "experiments/yolo/gdt629_part_quality_degree_clause/artifacts/WORKING_DICTIONARY_V6.tsv"

GENERATED = (
    ART / "PAGE_ALLOWLIST.tsv",
    ART / "VALUE_EXPRESSION_OCCURRENCES.tsv",
    ART / "CROSS_READER_MODE_EQUIVALENCE.tsv",
    ART / "FUSED_CELL_SEPARATE_COUNTERPARTS.tsv",
    ART / "KNOWN_OUTER_PART_CONTACTS.tsv",
    ART / "IMMEDIATE_PART_QUALITY_ATTACHMENTS.tsv",
    ART / "OUTER_NEIGHBOR_SUMMARY.tsv",
    ART / "BOUNDARY_MODE_SUMMARY.tsv",
    ART / "CLAUSE_ORDER_SUMMARY.tsv",
    ART / "CONCRETE_CLAUSES_V2.tsv",
    ART / "OUTER_ATTACHMENT_ROLE_RANKING.tsv",
    ART / "OPEN_OUTER_HEAD_CANDIDATES.tsv",
    ART / "WORKING_DICTIONARY_V7.tsv",
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
    expected_summary = "GDT630 built: expressions=135 modes={'FUSED_D_VALUE': 15, 'SEPARATE_D_VALUE': 120} classes={'CORE_BEARING_OL_QUALITY': 86, 'BARE_OL_CARRIER': 19, 'OR_NOMINAL_OR_PART_CARRIER': 30} contacts=33 attachments=11 cases=9 dictionary=38"
    check(completed.stdout.strip() == expected_summary, "builder summary")
    check(all(path.read_bytes() == before[path] for path in GENERATED), "builder replay is byte-identical")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT630_OUTER_CARRIER_ATTACHMENT_RESULT_V1", "result schema")
    check(result["status"] == "BILATERAL_PART_QUALITY_DEGREE_FRAMES__F8_MOIST_III_REPRODUCTIVE_PART_BOUNDARY_BRIDGE", "result status")
    content_hash = result.pop("content_sha256")
    check(content_hash == canonical_hash(result), "canonical result hash")
    result["content_sha256"] = content_hash

    guard = result["guard"]
    check(guard == {
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

    expressions = read_tsv(ART / "VALUE_EXPRESSION_OCCURRENCES.tsv")
    check(len(expressions) == 135, "135 fused and separate occurrences")
    check(Counter(row["realization_mode"] for row in expressions) == Counter({"SEPARATE_D_VALUE": 120, "FUSED_D_VALUE": 15}), "expression mode partition")
    check(Counter(row["expression_class"] for row in expressions) == Counter({"CORE_BEARING_OL_QUALITY": 86, "OR_NOMINAL_OR_PART_CARRIER": 30, "BARE_OL_CARRIER": 19}), "expression semantic class partition")
    fused = [row for row in expressions if row["realization_mode"] == "FUSED_D_VALUE"]
    separate = [row for row in expressions if row["realization_mode"] == "SEPARATE_D_VALUE"]
    check(Counter(row["expression_class"] for row in fused) == Counter({"BARE_OL_CARRIER": 8, "CORE_BEARING_OL_QUALITY": 6, "OR_NOMINAL_OR_PART_CARRIER": 1}), "fused class partition")
    check(Counter(row["expression_class"] for row in separate) == Counter({"CORE_BEARING_OL_QUALITY": 80, "OR_NOMINAL_OR_PART_CARRIER": 29, "BARE_OL_CARRIER": 11}), "separate class partition")
    check(sum(int(row["expression_triple_reader_stable"]) for row in expressions) == 102, "102 exact expression-stable occurrences")
    check(Counter(row["working_roman"] for row in fused) == Counter({"III": 14, "II": 1}), "fusion is limited to II and III")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in expressions), "expression rows exclude forbidden folios")
    for key in ("left_1", "left_2", "left_3", "right_1", "right_2", "right_3"):
        check(all(row[key] != "" for row in expressions), f"complete context window {key}")

    reader_modes = read_tsv(ART / "CROSS_READER_MODE_EQUIVALENCE.tsv")
    check(len(reader_modes) == 135, "one reader-mode row per expression")
    check({row["expression_id"] for row in reader_modes} == {row["expression_id"] for row in expressions}, "reader-mode expression coverage")
    for mode, exact, normalized, alternate, stable_variant in (
        ("FUSED_D_VALUE", 9, 13, 5, 4),
        ("SEPARATE_D_VALUE", 93, 98, 4, 4),
    ):
        selected = [row for row in reader_modes if row["source_mode"] == mode]
        check(sum(int(row["exact_source_mode_triple_reader"]) for row in selected) == exact, f"{mode} exact reader stability")
        check(sum(int(row["boundary_normalized_triple_reader"]) for row in selected) == normalized, f"{mode} normalized reader stability")
        check(sum(int(row["alternate_boundary_reader_present"]) for row in selected) == alternate, f"{mode} alternate boundary count")
        check(sum(int(row["boundary_variant_with_normalized_support"]) for row in selected) == stable_variant, f"{mode} stable boundary variants")
    reader_by_locus = {row["locus"]: row for row in reader_modes}
    check(reader_by_locus["f8r.9"]["zl3b_mode"] == "FUSED_D_VALUE" and reader_by_locus["f8r.9"]["it2a_mode"] == "SEPARATE_D_VALUE" and reader_by_locus["f8r.9"]["rf1b_mode"] == "FUSED_D_VALUE", "f8 fused-separate-fused bridge")
    check(reader_by_locus["f55v.1"]["boundary_normalized_triple_reader"] == "0", "f55 d-loss warning")
    for locus in ("f49r.6", "f100r.22", "f88v.15"):
        check(reader_by_locus[locus]["boundary_variant_with_normalized_support"] == "1", f"stable fused-source boundary bridge {locus}")
    for locus in ("f4v.11", "f19v.3", "f42r.10", "f51v.6"):
        check(reader_by_locus[locus]["source_mode"] == "SEPARATE_D_VALUE" and reader_by_locus[locus]["alternate_boundary_reader_present"] == "1", f"separate-source fusion variant {locus}")

    cells = read_tsv(ART / "FUSED_CELL_SEPARATE_COUNTERPARTS.tsv")
    check(len(cells) == 6, "six fused base-value cells")
    check(sum(int(row["fused_occurrences"]) for row in cells) == 15, "fifteen fused occurrences in cell table")
    check(sum(int(row["separate_occurrences"]) for row in cells) == 56, "fifty-six same-cell separate counterparts")
    check(all(int(row["separate_occurrences"]) > 0 for row in cells), "every fused cell has separate counterpart")
    check(all(row["shared_lexical_immediate_neighbors"] == "NONE" for row in cells), "no same-cell lexical outer neighbor crosses modes")
    cell_by_surface = {row["fused_surface"]: row for row in cells}
    check(cell_by_surface["choldaiin"]["separate_occurrences"] == "29", "chol III counterpart count")
    check(cell_by_surface["sholdaiin"]["fused_immediate_part_attachments"] == "1", "shol III fused part contact")
    check(cell_by_surface["otoldaiin"]["fused_boundary_normalized_triple_reader"] == "0", "otol III fused instability retained")

    contacts = read_tsv(ART / "KNOWN_OUTER_PART_CONTACTS.tsv")
    attachments = read_tsv(ART / "IMMEDIATE_PART_QUALITY_ATTACHMENTS.tsv")
    check(len(contacts) == 33, "thirty-three known part contacts within three")
    check(len(attachments) == 11, "eleven immediate concrete part attachments")
    check(all(row["distance"] == "1" and row["core_quality_concrete"] == "1" for row in attachments), "attachments require immediate core quality")
    check(all(row["evidence_class"] == "IMMEDIATE_CONCRETE_PART_QUALITY_DEGREE_CLAUSE" for row in attachments), "attachment evidence class")
    check(Counter(row["realization_mode"] for row in attachments) == Counter({"SEPARATE_D_VALUE": 10, "FUSED_D_VALUE": 1}), "attachment mode partition")
    check(Counter(row["order"] for row in attachments) == Counter({"VALUE_EXPRESSION_BEFORE_PART": 6, "PART_BEFORE_VALUE_EXPRESSION": 5}), "bilateral clause order")
    check(sum(int(row["exact_clause_triple_reader_stable"]) for row in attachments) == 8, "eight exact triple-reader clauses")
    check(sum(int(row["boundary_normalized_clause_triple_reader_stable"]) for row in attachments) == 9, "nine boundary-normalized clauses")
    check(Counter(row["part_surface"] for row in attachments) == Counter({"cthy": 4, "chor": 3, "ctheol": 1, "cthey": 1, "cthor": 1, "shor": 1}), "attachment part surface partition")
    immediate_fused = [row for row in attachments if row["realization_mode"] == "FUSED_D_VALUE"]
    check(len(immediate_fused) == 1 and immediate_fused[0]["locus"] == "f8r.9" and immediate_fused[0]["part_surface"] == "shor", "only fused visible part is f8 shor")
    check(all("Arbeitsgut" not in row["working_reading_de"] and "ausführen" not in row["working_reading_de"] for row in contacts), "no generic filler in contacts")
    check(all(row["dose_rival_de"] != "NONE" for row in attachments), "dose rival remains explicit")

    attachment_by_locus = {row["locus"]: row for row in attachments}
    for locus, surface, part, base, exact, normalized in (
        ("f8r.9", "sholdaiin shor", "shor", "shol", "0", "1"),
        ("f3r.3", "chol daiin cthy", "cthy", "chol", "1", "1"),
        ("f15v.11", "chol daiin cthy", "cthy", "chol", "1", "1"),
        ("f21v.3", "chor qotol daiin", "chor", "qotol", "1", "1"),
        ("f22v.8", "cthy qokol daiin", "cthy", "qokol", "1", "1"),
        ("f44v.3", "otol daiin cthy", "cthy", "otol", "1", "1"),
    ):
        row = attachment_by_locus[locus]
        check(row["surface_clause"] == surface and row["part_surface"] == part and row["base_surface"] == base, f"concrete clause surface {locus}")
        check(row["exact_clause_triple_reader_stable"] == exact and row["boundary_normalized_clause_triple_reader_stable"] == normalized, f"concrete clause reader status {locus}")

    neighbors = read_tsv(ART / "OUTER_NEIGHBOR_SUMMARY.tsv")
    neighbor_by_key = {(row["surface"], row["side"]): row for row in neighbors}
    check(neighbor_by_key[("cthy", "RIGHT")]["occurrences"] == "4", "cthy repeated on right")
    check(neighbor_by_key[("chor", "LEFT")]["occurrences"] == "3", "chor repeated on left")
    check(neighbor_by_key[("chol", "LEFT")]["cross_mode"] == "1" and neighbor_by_key[("chol", "LEFT")]["occurrences"] == "7", "chol cross-mode outer candidate")
    check(neighbor_by_key[("chcthy", "LEFT")]["occurrences"] == "2", "chcthy repeated candidate")
    check(neighbor_by_key[("qotor", "LEFT")]["occurrences"] == "2", "qotor repeated candidate")

    modes = read_tsv(ART / "BOUNDARY_MODE_SUMMARY.tsv")
    check(len(modes) == 6 and sum(int(row["occurrences"]) for row in modes) == 135, "six-row mode summary")
    orders = read_tsv(ART / "CLAUSE_ORDER_SUMMARY.tsv")
    check(len(orders) == 3 and sum(int(row["clauses"]) for row in orders) == 11, "three-row order summary")

    cases = read_tsv(ART / "CONCRETE_CLAUSES_V2.tsv")
    check(len(cases) == 9, "nine concrete clause records")
    check(Counter(row["reader_status"] for row in cases) == Counter({"TRIPLE_EXACT": 8, "TRIPLE_BOUNDARY_NORMALIZED": 1}), "case reader status partition")
    check({row["locus"] for row in cases} == {"f100r.25", "f15v.11", "f21r.12", "f21v.3", "f22v.8", "f32v.10", "f3r.3", "f44v.3", "f8r.9"}, "concrete case loci")
    check(all("OPEN" in row["residual_policy"] for row in cases), "case residuals stay open")

    ranking = read_tsv(ART / "OUTER_ATTACHMENT_ROLE_RANKING.tsv")
    check(len(ranking) == 4 and [row["rank"] for row in ranking] == ["1", "2", "3", "4"], "four ranked attachment models")
    check(ranking[0]["model"] == "BILATERAL_PART_QUALITY_DEGREE_CELLS", "bilateral model ranks first")
    check(ranking[1]["disposition"] == "LIVE_LAYOUT_RIVAL", "layout-cell rival stays live")
    check(ranking[2]["disposition"] == "LIVE_SEPARATE_FORM_RIVAL", "dose rival stays live")
    check(ranking[3]["disposition"] == "REJECTED_AS_DEFAULT", "generic operation prose rejected")

    open_candidates = read_tsv(ART / "OPEN_OUTER_HEAD_CANDIDATES.tsv")
    check(len(open_candidates) == 4, "four open outer-head candidates")
    check(open_candidates[0]["surface"] == "chcthy" and open_candidates[0]["disposition"] == "NEXT_COMPOSITION_TARGET", "chcthy next composition target")
    check(open_candidates[1]["surface"] == "qotor" and "offen" in open_candidates[1]["working_hypothesis_de"], "qotor remains open")
    check(open_candidates[2]["surface"] == "chol" and open_candidates[2]["disposition"] == "MULTI_CELL_NOT_NEW_NOUN", "chol not silently promoted to new outer noun")
    check(open_candidates[3]["surface"] == "dy" and open_candidates[3]["disposition"] == "STRUCTURAL_OPEN", "dy stays structurally open")

    old_dictionary = read_tsv(V6)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V7.tsv")
    check(len(old_dictionary) == 32 and len(dictionary) == 38, "V7 consolidates thirty-two plus six entries")
    check(dictionary[:32] == old_dictionary, "all V6 entries retained byte-for-field")
    new_entries = {row["entry"]: row for row in dictionary[32:]}
    for entry in ("sholdaiin|shol daiin", "sholdaiin shor|shol daiin shor", "chol daiin cthy", "cthy qokol daiin", "OL_QUALITY dN CTH_PART", "CTH_PART OL_QUALITY dN"):
        check(entry in new_entries, f"V7 entry {entry}")

    check(result["value_expressions"]["occurrences"] == 135, "result expression total")
    check(result["cross_reader_boundary"]["separate_counterpart_occurrences"] == 56, "result counterpart total")
    check(result["cross_reader_boundary"]["cells_with_shared_lexical_immediate_neighbor"] == 0, "result same-cell neighbor result")
    check(result["outer_attachment"]["immediate_concrete_attachments"] == 11, "result attachment total")
    check(result["working_dictionary"] == {"entries": 38, "inherited_v6": 32, "new_v7": 6}, "result dictionary summary")
    check(result["manual_models"] == {"concrete_cases": 9, "open_outer_head_candidates": 4, "role_rankings": 4}, "result manual model summary")

    privacy_pattern = re.compile(
        "/" + r"home/|/" + r"tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|AKIA[0-9A-Z]{16}|"
        r"gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|password\s*[=:]|api[_-]?key\s*[=:]|secret\s*[=:]",
        re.IGNORECASE,
    )
    required = (
        BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json",
        ART / "README.md", *GENERATED, RUN, BASE / "src/validate.py",
    )
    for path in required:
        check(path.is_file(), f"required file {rel(path)}")
        check(not privacy_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {rel(path)}")

    payload = {
        "schema": "GDT630_VALIDATION_V1",
        "experiment_id": "GDT630",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "result_sha256": sha256(RESULT),
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
