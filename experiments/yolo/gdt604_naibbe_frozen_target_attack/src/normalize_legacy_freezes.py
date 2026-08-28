#!/usr/bin/env python3
"""Normalize machine-local legacy metadata into path-free bundle artifacts."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from common import sha256_path
from pipeline import REFERENCE_HASHES


BYTE_IDENTICAL = (
    "GDT604_TARGET_ATTACK_PREREG.md",
    "GDT604_TOP_LINES_FULL.md",
    "gdt604_folio_split.json",
    "gdt604_reference_calibration.json",
    "gdt604_target_segmentation_u115.json",
    "gdt604_target_segmentation_u132.json",
    "gdt604_target_segmentation_u138.json",
    "gdt604_target_segmentation_u138_trainonly.json",
    "gdt604_top_lines_latin.tsv",
    "gdt604_top_lines_middle_high_german.tsv",
    "gdt604_top_lines_old_italian.tsv",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name in BYTE_IDENTICAL:
        shutil.copyfile(args.legacy_dir / name, args.output_dir / name)

    segmentation = json.loads(
        (args.legacy_dir / "gdt604_target_segmentation_freeze.json").read_text()
    )
    segmentation["primary"] = Path(segmentation["primary"]).name
    segmentation["navigation"] = [Path(path).name for path in segmentation["navigation"]]
    for record in segmentation["outputs"]:
        record["path"] = Path(record["path"]).name
    (args.output_dir / "gdt604_target_segmentation_freeze.json").write_text(
        json.dumps(segmentation, indent=2, sort_keys=True) + "\n"
    )

    keys = json.loads((args.legacy_dir / "gdt604_target_key_freeze.json").read_text())
    observed_hashes = set(keys["reference_sources"].values())
    if observed_hashes != set(REFERENCE_HASHES.values()):
        raise RuntimeError("legacy reference bindings do not match portable inventory")
    keys["reference_sources"] = REFERENCE_HASHES
    key_path = args.output_dir / "gdt604_target_key_freeze.json"
    key_path.write_text(json.dumps(keys, sort_keys=True, separators=(",", ":")) + "\n")

    result = json.loads((args.legacy_dir / "gdt604_target_result.json").read_text())
    result["key_freeze_sha256"] = sha256_path(key_path)
    for language in result["languages"].values():
        language["top_lines_path"] = Path(language["top_lines_path"]).name
    for record in result["top_line_artifacts"]:
        record["path"] = Path(record["path"]).name
    result_path = args.output_dir / "gdt604_target_result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    report = (args.legacy_dir / "GDT604_TARGET_ATTACK_REPORT.md").read_text()
    old_key_hash = "e6742b374985dbac4b8734b8d20e74d6c3a55362f88befb8f34d8b7ad4bade76"
    old_result_hash = "7ab3801571f878f5c30a6ae90e379ee2b269a33125f9ebd2c5dd04a6c5357f70"
    report = report.replace("standalone `/tmp` pass", "standalone scratch-work pass")
    report = report.replace("/" + "tmp" + "/", "")
    report = report.replace(old_key_hash, sha256_path(key_path))
    report = report.replace(old_result_hash, sha256_path(result_path))
    report = report.replace(
        "`gdt604_guarded_materialize.py`,\n  `gdt604_segment_target.py`, "
        "`gdt604_fit_target_keys.py`, and\n  `gdt604_evaluate_held.py`",
        "`src/run_all.py`, `src/pipeline.py`,\n  `src/portable_factorizer.py`, "
        "and `src/portable_keylib.py`",
    )
    (args.output_dir / "GDT604_TARGET_ATTACK_REPORT.md").write_text(report)

    print(json.dumps({
        "portable_key_freeze_sha256": sha256_path(key_path),
        "portable_result_sha256": sha256_path(result_path),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
