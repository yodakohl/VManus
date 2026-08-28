#!/usr/bin/env python3
"""Independent artifact validator for GDT603; does not import the producer."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
RESULT = OUT / "gdt603_result.json"
FREEZE = OUT / "gdt603_blind_freeze.json"
SEGMENTS = OUT / "gdt603_blind_segmentations.tsv"
KEYS = OUT / "gdt603_recovered_keys.tsv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result = json.loads(RESULT.read_text())
    freeze = json.loads(FREEZE.read_text())
    checks = []

    def check(name: str, condition: bool):
        checks.append({"check": name, "passed": bool(condition)})

    check("experiment id", result.get("experiment_id") == "GDT603")
    check(
        "decision status",
        result.get("status") == "END_TO_END_NAIBBE_CONTROL_RECOVERED_AT_PUBLIC_CAPACITY",
    )
    check("blind freeze schema", freeze.get("schema") == "gdt603-blind-freeze-v1")
    check(
        "blind freeze hash",
        result["data_separation"]["blind_freeze_sha256"] == sha256(FREEZE),
    )
    check("oracle closed in blind artifact", freeze.get("oracle_sources_opened") is False)
    check("public primary U size", freeze.get("primary_u_size") == 138)
    check("navigation sizes only", freeze.get("navigation_u_sizes") == [115, 132])
    check("public state capacity", freeze.get("state_capacity") == 138)
    check(
        "ciphertext source hash",
        freeze.get("cipher_sha256")
        == "9cdf2de12f371ac7efdb2e78713f229ada508286c1717758184238a59cd64326",
    )
    check(
        "independent Caesar hash",
        freeze.get("caesar_sha256")
        == "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
    )

    evaluations = {row["u_size"]: row for row in result["evaluations"]}
    check("three fixed variants", set(evaluations) == {115, 132, 138})
    primary = evaluations[138]
    check("34,764 control tokens", primary["token_occurrences"] == 34_764)
    check("5,600 control token types", primary["token_types"] == 5_600)
    check("52,641 true characters", primary["true_characters"] == 52_641)
    check(
        "primary exact segmentation above 95 percent",
        primary["exact_segmentation_accuracy_occurrence"] >= 0.95,
    )
    check(
        "primary end-to-end edit accuracy above 94 percent",
        primary["end_to_end_edit_accuracy"] >= 0.94,
    )
    check(
        "primary exact-token recovery above 95 percent",
        primary["exact_decoded_token_rate"] >= 0.95,
    )
    check(
        "primary key accuracy after exact segmentation above 99 percent",
        primary["key_accuracy_given_exact_segmentation"] >= 0.99,
    )
    check(
        "primary inventories within public capacity",
        primary["inventories"]["U"] == 138
        and primary["inventories"]["P"] <= 138
        and primary["inventories"]["S"] <= 138,
    )
    check(
        "U115 explicitly nonprimary",
        result["configuration"]["navigation_warning"].startswith("U=115"),
    )

    with SEGMENTS.open(newline="") as handle:
        segment_rows = list(csv.DictReader(handle, delimiter="\t"))
    segment_counts = Counter(int(row["u_size"]) for row in segment_rows)
    check("complete segmentation rows", segment_counts == Counter({115: 5600, 132: 5600, 138: 5600}))
    check(
        "segmentation primary flags",
        all((row["primary"] == "1") == (row["u_size"] == "138") for row in segment_rows),
    )
    check(
        "segmentation states and cuts",
        all(
            row["state"] in {"U", "B"}
            and (
                (
                    row["state"] == "U"
                    and row["cut"] == "-1"
                    and row["prefix"] == "NA"
                    and row["suffix"] == "NA"
                )
                or (
                    row["state"] == "B"
                    and row["cut"].isdigit()
                    and row["prefix"] != ""
                    and row["suffix"] != ""
                )
            )
            for row in segment_rows
        ),
    )

    with KEYS.open(newline="") as handle:
        key_rows = list(csv.DictReader(handle, delimiter="\t"))
    expected_key_counts = {
        int(size): len(record["key"]) for size, record in freeze["keys"].items()
    }
    actual_key_counts = Counter(int(row["u_size"]) for row in key_rows)
    check("complete recovered-key rows", dict(actual_key_counts) == expected_key_counts)
    check(
        "key rows reproduce blind freeze",
        all(
            freeze["keys"][row["u_size"]]["key"][f"{row['state']}|{row['surface']}"]
            == row["recovered"]
            for row in key_rows
        ),
    )
    check(
        "no target data source",
        set(result["sources"])
        == {"ciphertext", "caesar", "table_evaluation_only", "plaintext_evaluation_only"},
    )

    artifacts = {
        path.name: sha256(path) for path in (RESULT, FREEZE, SEGMENTS, KEYS)
    }
    validation = {
        "experiment_id": "GDT603",
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "checks": checks,
        "artifact_sha256": artifacts,
    }
    (OUT / "gdt603_validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
