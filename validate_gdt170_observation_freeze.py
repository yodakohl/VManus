#!/usr/bin/env python3
"""Independent integrity validator for the GDT170 observation/oracle freeze."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OLD_OBS = R / "gdt168_blind_synthetic_corpora.json.gz"
OLD_TRUTH = R / "gdt168_synthetic_ground_truth.json.gz"
OBS = R / "gdt170_observation_corpus.json.gz"
ORACLE = R / "gdt170_sealed_oracle.json.gz"
PAGES = R / "gdt170_observation_page_manifest.tsv"
SCHEMA = R / "gdt170_observation_schema.tsv"
FREEZE = R / "gdt170_observation_oracle_freeze.json"
OUT = R / "gdt170_observation_freeze_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_gzip(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle:
        return json.load(handle)


def check(condition: bool, label: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def main() -> None:
    checks: list[str] = []
    freeze = json.loads(FREEZE.read_text())
    old = load_gzip(OLD_OBS)
    old_truth = load_gzip(OLD_TRUTH)
    obs_payload = load_gzip(OBS)
    oracle_payload = load_gzip(ORACLE)
    obs = obs_payload["rows"]
    oracle = oracle_payload["rows"]

    check(obs_payload["schema"] == "GDT170_STRICT_OBSERVATION_CORPUS_V1", "observation_schema", checks)
    check(oracle_payload["schema"] == "GDT170_SEALED_ORACLE_V1", "oracle_schema", checks)
    check(len(obs) == len(oracle) == len(old["rows"]) == len(old_truth["rows"]) == 240000,
          "row_counts_240000", checks)
    allowed = set(freeze["observation_allowed_fields"])
    forbidden = set(freeze["observation_forbidden_fields"])
    check(all(set(row) == allowed for row in obs), "observation_fields_exact", checks)
    check(not any(forbidden.intersection(row) for row in obs), "oracle_fields_absent_from_observation", checks)
    check(all("f84" not in " ".join(str(v).lower() for k, v in row.items() if k != "observation_id")
              and "voynich" not in " ".join(str(v).lower() for k, v in row.items() if k != "observation_id")
              for row in obs),
          "no_voynich_or_f84_observation", checks)

    obs_ids = [row["observation_id"] for row in obs]
    oracle_ids = [row["observation_id"] for row in oracle]
    check(len(set(obs_ids)) == 240000, "observation_ids_unique", checks)
    check(set(obs_ids) == set(oracle_ids), "oracle_join_one_to_one", checks)
    check(len(set(oracle_ids)) == 240000, "oracle_ids_unique", checks)

    old_by_id = {row["blind_id"]: row for row in old["rows"]}
    truth_by_id = {row["blind_id"]: row for row in old_truth["rows"]}
    oracle_by_oid = {row["observation_id"]: row for row in oracle}
    world_counts = Counter()
    renderer_counts = Counter()
    page_lines: dict[str, set[str]] = defaultdict(set)
    page_groups = Counter()
    page_paragraphs: dict[str, set[int]] = defaultdict(set)
    line_rows: dict[str, list[dict]] = defaultdict(list)
    for row in obs:
        truth = oracle_by_oid[row["observation_id"]]
        old_row = old_by_id[truth["original_blind_id"]]
        old_true = truth_by_id[truth["original_blind_id"]]
        check(row["surface_group"] == old_row["surface"], "surface_reconstructs_old_observation", checks)
        check(truth["plaintext_form"] == old_true["plaintext_form"], "oracle_plaintext_reconstructs", checks)
        check(truth["concept_index"] == old_true["concept_index"], "oracle_concept_reconstructs", checks)
        check(truth["true_record_slot"] == old_true["slot"], "oracle_slot_reconstructs", checks)
        check(truth["canonical_host"] == old_true["canonical_host"], "oracle_host_reconstructs", checks)
        check(truth["rendered_host"] == old_row["page_host"], "oracle_rendered_host_reconstructs", checks)
        check(truth["true_wrapper"] == old_row["wrapper"], "oracle_wrapper_reconstructs", checks)
        check(truth["true_local_frame"] == old_row["local_frame"], "oracle_frame_reconstructs", checks)
        check(truth["true_right_family"] == old_row["right_family"], "oracle_right_reconstructs", checks)
        check(truth["true_closure_value"] == old_row["closure_value"], "oracle_closure_reconstructs", checks)
        check(truth["true_dy_closure"] == old_row["dy_closure"], "oracle_dy_reconstructs", checks)
        check(truth["true_b3"] == old_row["b3"], "oracle_b3_reconstructs", checks)
        world_counts[row["world_view"]] += 1
        renderer_counts[(row["world_view"], row["witness_renderer"])] += 1
        page_lines[row["folio_id"]].add(row["physical_line_id"])
        page_groups[row["folio_id"]] += 1
        page_paragraphs[row["folio_id"]].add(int(row["line_ordinal_on_folio"]) // 3)
        line_rows[row["physical_line_id"]].append(row)

    # The repeated checks above are deliberately collapsed in the validation report.
    checks = list(dict.fromkeys(checks))
    check(len(world_counts) == 2 and len(renderer_counts) == 20, "two_worlds_twenty_views", checks)
    check(len(page_lines) == 2460, "synthetic_folios_2460", checks)
    check(all(1 <= len(v) <= 18 for v in page_lines.values()), "physical_lines_per_folio_valid", checks)
    check(all(1 <= len(v) <= 6 for v in page_paragraphs.values()), "paragraphs_per_folio_valid", checks)
    for rows in line_rows.values():
        rows.sort(key=lambda x: int(x["group_index"]))
        n = int(rows[0]["group_count"])
        check(len(rows) == n and [int(x["group_index"]) for x in rows] == list(range(1, n + 1)),
              "line_group_sequence_complete", checks)
        check(rows[0]["left_separator"] == "LINE_START" and rows[-1]["right_separator"] == "LINE_END",
              "line_boundaries_exact", checks)
        check(all(x["right_separator"] == "CONFIDENT_SPACE" for x in rows[:-1]),
              "internal_right_separators_exact", checks)
        check(all(x["left_separator"] == "CONFIDENT_SPACE" for x in rows[1:]),
              "internal_left_separators_exact", checks)
    checks = list(dict.fromkeys(checks))

    with PAGES.open(encoding="utf8", newline="") as handle:
        pages = list(csv.DictReader(handle, delimiter="\t"))
    check(len(pages) == 2460, "page_manifest_count", checks)
    for row in pages:
        folio = row["folio_id"]
        check(int(row["physical_lines"]) == len(page_lines[folio]), "page_line_count_reconstructs", checks)
        check(int(row["visible_paragraphs"]) == len(page_paragraphs[folio]), "page_paragraph_count_reconstructs", checks)
        check(int(row["source_groups"]) == page_groups[folio], "page_group_count_reconstructs", checks)
    checks = list(dict.fromkeys(checks))

    with SCHEMA.open(encoding="utf8", newline="") as handle:
        schema_rows = list(csv.DictReader(handle, delimiter="\t"))
    schema_allowed = {r["field"] for r in schema_rows if r["blind_parser_allowed"] == "1"}
    schema_forbidden = {r["field"] for r in schema_rows if r["oracle_forbidden"] == "1"}
    check(schema_allowed == allowed, "schema_allowed_exact", checks)
    check(schema_forbidden == forbidden, "schema_forbidden_exact", checks)

    check(csha(obs) == freeze["commitments"]["observation_content_sha256"], "observation_content_hash", checks)
    check(csha(oracle) == freeze["commitments"]["oracle_content_sha256"], "oracle_content_hash", checks)
    check(all(sha(R / name) == digest for name, digest in freeze["outputs"].items()), "output_file_hashes", checks)
    check(all(sha(R / name) == digest for name, digest in freeze["inputs"].items()), "input_file_hashes", checks)
    stored = freeze.pop("freeze_content_sha256")
    check(csha(freeze) == stored, "freeze_content_hash", checks)

    result = {
        "schema": "GDT170_OBSERVATION_FREEZE_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_OBSERVATION_ORACLE_RECONSTRUCTION",
        "checks_passed": len(checks), "checks_failed": 0, "checks": checks,
        "observation_rows": len(obs), "oracle_rows": len(oracle),
        "synthetic_folios": len(page_lines), "worlds": len(world_counts),
        "observation_file_sha256": sha(OBS), "oracle_file_sha256": sha(ORACLE),
        "freeze_file_sha256": sha(FREEZE),
        "validator_sha256": sha(Path(__file__)), "f84r_access": False,
    }
    result["validation_content_sha256"] = csha(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
