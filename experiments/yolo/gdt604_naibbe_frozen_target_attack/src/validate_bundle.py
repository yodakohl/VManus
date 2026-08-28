#!/usr/bin/env python3
"""Independent structural, binding, gate, and privacy validator for GDT604."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import tempfile
from collections import Counter
from pathlib import Path

from common import sha256_path
from pipeline import (
    EXPECTED_GDT327_SAFE,
    EXPECTED_HELD,
    EXPECTED_SEGMENTS,
    EXPECTED_TARGET,
    EXPECTED_TRAIN,
    EXPECTED_TRAIN_ONLY_SEGMENT,
    PREREG_SHA256,
    REFERENCE_HASHES,
    materialize_guarded,
    split_guarded,
)
from portable_keylib import LATIN_LETTERS


EXPECTED_PORTABLE_KEY = "4409cb99beded2c5ffb7a94c48d82bb895ac4dfafccb3498c5a921af50958a2d"
EXPECTED_PORTABLE_RESULT = "ddf807c856f314320ff118b047a165d8add38162682f57f427789d500267dcfc"
EXPECTED_CALIBRATION = "86ea19d54adbcd814b0b20925f7a9e7038b3d38b111e76d088c978aef8a18a1d"
EXPECTED_TOP = {
    "latin": "8d6f0c1e33e817a5cbb3b63175a5daebeb0184f7dba3188f857d01b08769d5ba",
    "old_italian": "e8c63a795d3bdfeabb56061242251066d21aa759a7acf82760675a13b05a36c0",
    "middle_high_german": "db4260999e3af50a17b47b33bf93416c9bce69a25f3365180697d6d69a304afa",
}
EXPECTED_APPENDIX = "01cc06f5b1e94adab78128c31e8dbc96eee79ead413defe70a342f509efdf43b"
LANGUAGES = {"latin", "old_italian", "middle_high_german"}
SEEDS = {11, 29, 47}
RESTARTS = {0, 1}


class Validator:
    def __init__(self):
        self.checks: list[str] = []

    def require(self, condition, label):
        if not condition:
            raise AssertionError(label)
        self.checks.append(label)


def load_json(path: Path):
    return json.loads(path.read_text())


def target_selector_safe(value: str) -> bool:
    lowered = value.lower()
    return not (lowered.startswith("f84") or lowered.startswith("f84r"))


def validate_split(v: Validator, artifacts: Path):
    path = artifacts / "gdt604_folio_split.json"
    split = load_json(path)
    pages = split["pages"]
    page_map = split["page_to_physical_folio"]
    train, held = set(split["train_folios"]), set(split["held_folios"])
    v.require(split["schema"] == "gdt604-physical-folio-split-v1", "split schema")
    v.require(split["gdt327_safe_sha256"] == EXPECTED_GDT327_SAFE, "GDT327 binding")
    v.require(len(pages) == 180 and len(page_map) == 180, "180-page allow-list")
    v.require(len(train) == 68 and len(held) == 23 and train.isdisjoint(held), "68/23 folio split")
    v.require(set(page_map.values()) == train | held and len(train | held) == 91, "91 mapped folios")
    v.require(all(target_selector_safe(page) for page in pages), "allow-list excludes sealed page prefix")
    v.require(all(target_selector_safe(folio) for folio in page_map.values()), "folio map excludes sealed prefix")
    ranked = sorted(
        train | held,
        key=lambda folio: hashlib.sha256(
            ("gdt604-held-v1|" + folio).encode()
        ).hexdigest(),
    )
    v.require(set(ranked[:23]) == held, "held split algorithm recomputed")


def validate_segmentation(v: Validator, artifacts: Path):
    manifest = load_json(artifacts / "gdt604_target_segmentation_freeze.json")
    v.require(manifest["primary"] == "gdt604_target_segmentation_u138.json", "relative primary segmentation path")
    v.require(manifest["navigation"] == [
        "gdt604_target_segmentation_u115.json",
        "gdt604_target_segmentation_u132.json",
    ], "relative navigation segmentation paths")
    listed = {record["path"]: record["sha256"] for record in manifest["outputs"]}
    for u_size in (115, 132, 138):
        name = f"gdt604_target_segmentation_u{u_size}.json"
        path = artifacts / name
        v.require(sha256_path(path) == EXPECTED_SEGMENTS[u_size], f"U={u_size} byte binding")
        v.require(listed[name] == EXPECTED_SEGMENTS[u_size], f"U={u_size} manifest binding")
        data = load_json(path)
        v.require(data["u_size"] == u_size, f"U={u_size} parameter")
        v.require(data["confirmatory"] == (u_size == 138), f"U={u_size} confirmatory flag")
        v.require(data["target_sha256"] == EXPECTED_TARGET, f"U={u_size} guarded-target binding")
        dictionaries = data["train_dictionaries"]
        v.require(dictionaries["U"] == u_size and dictionaries["P"] <= 138 and dictionaries["S"] <= 138, f"U={u_size} public dictionary capacity")
        v.require(0 <= data["train_parsed_occurrence_fraction"] <= 1, f"U={u_size} train occurrence coverage range")
        v.require(0 <= data["held_parsed_occurrence_fraction"] <= 1, f"U={u_size} held occurrence coverage range")
    train_only_path = artifacts / "gdt604_target_segmentation_u138_trainonly.json"
    train_only = load_json(train_only_path)
    v.require(sha256_path(train_only_path) == EXPECTED_TRAIN_ONLY_SEGMENT, "train-only segmentation byte binding")
    v.require(not any(key.startswith("held_") for key in train_only), "train-only segmentation has no held fields")
    v.require(train_only["target_sha256"] == EXPECTED_TARGET, "train-only target binding")


def validate_keys(v: Validator, artifacts: Path):
    path = artifacts / "gdt604_target_key_freeze.json"
    data = load_json(path)
    v.require(sha256_path(path) == EXPECTED_PORTABLE_KEY, "portable key-freeze byte binding")
    v.require(data["schema"] == "gdt604-train-only-key-freeze-v1", "key-freeze schema")
    v.require(data["prereg_sha256"] == PREREG_SHA256, "key preregistration binding")
    v.require(data["train_rows_sha256"] == EXPECTED_TRAIN, "key train-row binding")
    v.require(data["segmentation_sha256"] == EXPECTED_TRAIN_ONLY_SEGMENT, "key train-only segmentation binding")
    v.require(data["reference_sources"] == REFERENCE_HASHES, "logical reference-source bindings")
    v.require(data["mhg_commit"] == "3eddc3dc1620cf400c152d9ed8915416cb8d6d7a", "MHG commit binding")
    v.require(data["held_material_opened"] is False, "held material closed during fit")
    config = data["configuration"]
    v.require(set(config["languages"]) == LANGUAGES, "three predeclared languages")
    v.require(set(config["seeds"]) == SEEDS and set(config["restarts"]) == RESTARTS, "3x2 restart grid")
    v.require(config["iterations"] == 50_000 and config["state_letter_capacity"] == 6, "50k/capacity key configuration")
    v.require(config["order"] == 4 and config["alpha"] == 0.25 and config["chunk"] == 90, "char-4 model configuration")
    v.require(data["code_types"] == 414 and data["state_code_types"] == {"U": 138, "P": 138, "S": 138}, "414 state-coded types")
    jobs = data["jobs"]
    identities = {
        (job["language"], job["model"], job["seed"], job["restart"])
        for job in jobs
    }
    expected_identities = {
        (language, model, seed, restart)
        for language in LANGUAGES for model in ("real", "destroyed")
        for seed in SEEDS for restart in RESTARTS
    }
    v.require(len(jobs) == 36 and identities == expected_identities, "complete unique 36-job grid")
    code_sets = [set(job["key"]) for job in jobs]
    v.require(all(len(codes) == 414 for codes in code_sets) and all(codes == code_sets[0] for codes in code_sets), "all keys cover identical 414 codes")
    for job in jobs:
        key = job["key"]
        v.require(all(code[:2] in {"U|", "P|", "S|"} for code in key), f"coded-state syntax {job['language']}/{job['model']}/s{job['seed']}r{job['restart']}")
        v.require(set(key.values()) <= set(LATIN_LETTERS), f"active-letter renderer {job['language']}/{job['model']}/s{job['seed']}r{job['restart']}")
        allocations = Counter((code[0], letter) for code, letter in key.items())
        v.require(max(allocations.values()) <= 6, f"six-homophone capacity {job['language']}/{job['model']}/s{job['seed']}r{job['restart']}")
    v.require(all(meta["rendered_chars"] == 120_000 for meta in data["reference_models"].values()), "120k rendered characters per language")


def recompute_gates(language):
    real = language["real_restart_metrics"]
    paired = language["paired_real_minus_destroyed_key_lr_bits_per_char"]
    pairs = language["key_pair_agreement"]
    return {
        "coverage_ge_0_80": language["held_token_coverage"] >= 0.80,
        "every_order_z_ge_5": min(record["held_order_z"] for record in real) >= 5,
        "every_positive_folios_ge_16": min(record["positive_order_folios"] for record in real) >= 16,
        "every_paired_lr_advantage_ge_0_10": min(paired.values()) >= 0.10,
        "min_type_agreement_ge_0_70": min(pair["type_agreement"] for pair in pairs) >= 0.70,
        "min_weighted_agreement_ge_0_85": min(pair["held_weighted_agreement"] for pair in pairs) >= 0.85,
        "all_six_occurrence_consensus_ge_0_90": language["all_six_occurrence_consensus"] >= 0.90,
    }


def validate_result(v: Validator, artifacts: Path):
    path = artifacts / "gdt604_target_result.json"
    data = load_json(path)
    v.require(sha256_path(path) == EXPECTED_PORTABLE_RESULT, "portable result byte binding")
    v.require(data["prereg_sha256"] == PREREG_SHA256, "result preregistration binding")
    v.require(data["held_rows_sha256"] == EXPECTED_HELD, "result held-row binding")
    v.require(data["segmentation_sha256"] == EXPECTED_SEGMENTS[138], "result segmentation binding")
    v.require(data["key_freeze_sha256"] == EXPECTED_PORTABLE_KEY, "result key-freeze binding")
    v.require(set(data["languages"]) == LANGUAGES, "result contains three languages")
    computed_passers = []
    for name, language in data["languages"].items():
        gates = recompute_gates(language)
        v.require(gates == language["gates"], f"{name} gates recomputed")
        v.require(language["all_gates_pass"] == all(gates.values()), f"{name} aggregate gate")
        v.require(len(language["real_restart_metrics"]) == 6 and len(language["destroyed_restart_metrics"]) == 6, f"{name} held metrics complete")
        v.require(len(language["key_pair_agreement"]) == 15, f"{name} all restart pairs")
        v.require(Path(language["top_lines_path"]).name == language["top_lines_path"], f"{name} relative top-line path")
        if all(gates.values()):
            computed_passers.append(name)
    v.require(sorted(data["passing_languages"]) == sorted(computed_passers), "passing-language list recomputed")
    expected_decision = "LANGUAGE_LIKE_READING" if len(computed_passers) == 1 else "LM_DRIVEN_PSEUDOTEXT_NO_READING"
    v.require(data["decision"] == expected_decision and data["decision"] == "LM_DRIVEN_PSEUDOTEXT_NO_READING", "hard decision recomputed")
    listed = {record["path"]: record["sha256"] for record in data["top_line_artifacts"]}
    for language, expected in EXPECTED_TOP.items():
        name = f"gdt604_top_lines_{language}.tsv"
        v.require(listed[name] == expected, f"{language} result top-line binding")


def validate_top_lines(v: Validator, artifacts: Path):
    decoded_fields = [
        f"decoded_s{seed}_r{restart}"
        for seed in (11, 29, 47) for restart in (0, 1)
    ]
    total = 0
    for language, expected in EXPECTED_TOP.items():
        path = artifacts / f"gdt604_top_lines_{language}.tsv"
        v.require(sha256_path(path) == expected, f"{language} top-line byte binding")
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        v.require(len(rows) == 20 and [int(row["rank"]) for row in rows] == list(range(1, 21)), f"{language} complete ranks 1..20")
        v.require(all(target_selector_safe(row["page"]) and target_selector_safe(row["physical_folio"]) and target_selector_safe(row["locus"]) for row in rows), f"{language} top lines exclude sealed selectors")
        v.require(all(row["eva_clean"] and all(row[field] for field in decoded_fields) for row in rows), f"{language} EVA and six outputs complete")
        total += len(rows)
    v.require(total == 60, "all 60 top lines present")
    appendix = artifacts / "GDT604_TOP_LINES_FULL.md"
    v.require(sha256_path(appendix) == EXPECTED_APPENDIX, "full top-line appendix binding")


def validate_calibration(v: Validator, artifacts: Path):
    path = artifacts / "gdt604_reference_calibration.json"
    v.require(sha256_path(path) == EXPECTED_CALIBRATION, "reference calibration byte binding")
    data = load_json(path)
    v.require(set(data) == LANGUAGES, "calibration language set")
    v.require(all(record["real_minus_destroyed_bits_per_char"] > 0 for record in data.values()), "positive held-reference calibration")


def validate_inventory(v: Validator, bundle: Path):
    path = bundle / "bindings" / "gdt604_binding_inventory.json"
    inventory = load_json(path)
    v.require(inventory["schema"] == "gdt604-binding-inventory-v1", "binding-inventory schema")
    for record in inventory["files"]:
        target = bundle / record["path"]
        v.require(target.is_file(), f"inventory file exists: {record['path']}")
        v.require(sha256_path(target) == record["sha256"], f"inventory hash: {record['path']}")
    v.require(inventory["reference_sources"] == REFERENCE_HASHES, "inventory reference hashes")


def validate_privacy(v: Validator, bundle: Path):
    forbidden = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "file" + "://",
        "C:" + "\\" + "Users" + "\\",
    )
    scanned = 0
    for area in ("src", "artifacts", "reports", "bindings"):
        base = bundle / area
        for path in sorted(base.rglob("*")):
            if path.is_dir():
                v.require(path.name != "__pycache__", "no bytecode-cache directory")
                continue
            if path.suffix in {".pyc", ".pyo"}:
                raise AssertionError(f"bytecode cache file: {path.name}")
            data = path.read_bytes()
            text = data.decode("utf-8", errors="ignore")
            v.require(not any(marker in text for marker in forbidden), f"no private absolute path: {path.relative_to(bundle)}")
            scanned += 1
    v.require(scanned > 10, "privacy scan covered bundle sources and artifacts")
    source_text = "\n".join(path.read_text() for path in (bundle / "src").glob("*.py"))
    scratch_key = "naibbe" + "_blind_key"
    scratch_segment = "naibbe" + "_blind_segment"
    v.require(scratch_key not in source_text and scratch_segment not in source_text, "no external scratch keylib dependency")


def validate_live_target(v: Validator, artifacts: Path):
    with tempfile.TemporaryDirectory(prefix="gdt604-validator-") as temporary:
        work = Path(temporary) / "work"
        output = Path(temporary) / "artifacts"
        work.mkdir(parents=True)
        output.mkdir(parents=True)
        target, split = materialize_guarded(work, output)
        train, held = split_guarded(target, work)
        v.require(sha256_path(target) == EXPECTED_TARGET, "live guarded target query")
        v.require(sha256_path(train) == EXPECTED_TRAIN, "live train-row split")
        v.require(sha256_path(held) == EXPECTED_HELD, "live held-row split")
        v.require(split.read_bytes() == (artifacts / "gdt604_folio_split.json").read_bytes(), "live split matches freeze")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bundle-root", type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--live-target-check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    bundle = args.bundle_root.resolve()
    artifacts = (args.artifact_dir or bundle / "artifacts").resolve()
    v = Validator()
    v.require(sha256_path(artifacts / "GDT604_TARGET_ATTACK_PREREG.md") == PREREG_SHA256, "preregistration byte binding")
    validate_split(v, artifacts)
    validate_segmentation(v, artifacts)
    validate_keys(v, artifacts)
    validate_result(v, artifacts)
    validate_top_lines(v, artifacts)
    validate_calibration(v, artifacts)
    validate_inventory(v, bundle)
    validate_privacy(v, bundle)
    if args.live_target_check:
        validate_live_target(v, artifacts)
    result = {
        "schema": "gdt604-validation-v1",
        "status": "PASS",
        "checks_passed": len(v.checks),
        "live_target_check": args.live_target_check,
        "portable_key_freeze_sha256": EXPECTED_PORTABLE_KEY,
        "portable_result_sha256": EXPECTED_PORTABLE_RESULT,
        "decision": "LM_DRIVEN_PSEUDOTEXT_NO_READING",
        "known_limit": "Legacy segmentation refit has insertion-sensitive tie ordering; exact reproduction starts from the published pre-key segmentation freeze.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
