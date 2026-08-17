#!/usr/bin/env python3
"""Independent validation of the GDT216 source and prediction freeze."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKS: list[str] = []


def check(value: bool, name: str) -> None:
    if not value:
        raise AssertionError(name)
    CHECKS.append(name)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    result_path = ROOT / "gdt216_prediction_freeze.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    sources = rows("gdt216_wound_man_source_manifest.tsv")
    pairs = rows("gdt216_positive_control_pairs.tsv")

    check(result["experiment"] == "GDT216_WOUND_MAN_TERMINAL_KEY_SOURCE_FREEZE", "experiment")
    check(result["status"] == "EXTERNAL_TERMINAL_KEY_MECHANISM_FROZEN_BEFORE_VOYNICH_SCORE", "status")
    check(result["mechanism"] == "DIAGRAM_DESCRIPTIVE_PHRASE_PLUS_TERMINAL_KEY_TO_PROSE_INITIAL_KEY", "mechanism")
    check(len(sources) == 2, "two_sources")
    check({r["source_id"] for r in sources} == {"WELLCOME_MS49", "HARTNELL_2017"}, "source_ids")
    check(sum(r["source_class"] == "PRIMARY_INSTITUTIONAL_CATALOGUE_AND_DIGITAL_MANUSCRIPT" for r in sources) == 1, "one_primary")
    check(sum(r["source_class"] == "PEER_REVIEWED_SCHOLARLY_ARTICLE" for r in sources) == 1, "one_scholarly")
    check(all(r["url"].startswith("https://") for r in sources), "https_sources")
    check(len(pairs) == 3, "three_pairs")
    check({r["terminal_key"] for r in pairs} == {"14", "19", "41"}, "keys_14_19_41")
    check(all(r["terminal_key"] == r["prose_entry_key"] for r in pairs), "three_exact_key_matches")
    check(all(r["exact_key_match"] == "1" for r in pairs), "match_flags")
    check(all(r["full_phrase_match_expected"] == "0" for r in pairs), "phrase_nonidentity")
    check(result["positive_control"] == {"pairs": 3, "exact_terminal_to_initial_matches": 3, "full_phrase_exact_matches_expected": 0}, "positive_control_counts")
    target = result["target_prediction"]
    check(target["pages"] == 23 and target["physical_folios"] == 11, "frozen_panel")
    check(target["null_worlds"] == 432 and target["max_family"] == 3, "frozen_null")
    check(len(target["representations"]) == 3, "three_representations")
    check(target["score_run"] is False, "score_not_run")
    check(result["f84"] == {"accessed": False, "input": False, "output": False}, "f84_flags")

    for name, expected in result["outputs_sha256"].items():
        check(sha(ROOT / name) == expected, f"output_hash:{name}")
    for name, expected in result["documents_sha256"].items():
        check(sha(ROOT / name) == expected, f"document_hash:{name}")
    check(sha(ROOT / "freeze_gdt216_wound_man_terminal_key.py") == result["implementation_sha256"], "implementation_hash")
    check(sha(Path(__file__)) == result["validator_sha256"], "validator_hash")
    payload = dict(result)
    observed = payload.pop("content_sha256")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    check(hashlib.sha256(canonical.encode()).hexdigest() == observed, "content_hash")

    validation = {
        "experiment": result["experiment"],
        "status": "PASS",
        "checks_passed": len(CHECKS),
        "checks": CHECKS,
        "result_sha256": sha(result_path),
        "validator_sha256": sha(Path(__file__)),
    }
    (ROOT / "gdt216_freeze_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__":
    main()
