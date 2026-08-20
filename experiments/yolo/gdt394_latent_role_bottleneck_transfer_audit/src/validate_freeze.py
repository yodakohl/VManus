#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt394_latent_role_bottleneck_transfer_audit"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    path = ART / "gdt394_pre_score_freeze.json"
    freeze = json.loads(path.read_text(encoding="utf-8"))
    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    content = dict(freeze)
    expected = content.pop("content_sha256")
    check(
        "content_hash",
        hashlib.sha256(
            json.dumps(content, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == expected,
    )
    check("status", freeze["status"] == "FROZEN_BEFORE_SCORING")
    check("two_domains", freeze["domains"] == ["COREMA", "PCEEC2"])
    check("dimension_one", freeze["bottleneck_dimension"] == 1)
    check("eight_models", len(freeze["models"]) == 8 and len(set(freeze["models"])) == 8)
    check("fixed_decoder", freeze["downstream_quantile_bins"] == 8)
    check("fixed_null", freeze["null_worlds"] == 512)
    check("both_domains_required", freeze["promotion"]["required_domains"] == 2)
    check("voynich_absent", freeze["voynich_inputs"] == 0)
    check("f84_sealed", not any(freeze["f84"].values()))
    for family in ("input_hashes", "document_hashes", "implementation_hashes"):
        check(
            family,
            bool(freeze[family])
            and all((ROOT / item).is_file() and sha(ROOT / item) == digest for item, digest in freeze[family].items()),
        )
    result = {
        "schema": "GDT394_FREEZE_VALIDATION_V1",
        "status": "PASS" if all(value for _, value in checks) else "FAIL",
        "checks_passed": sum(value for _, value in checks),
        "checks_total": len(checks),
        "checks": {name: value for name, value in checks},
        "freeze_sha256": sha(path),
    }
    (ART / "gdt394_pre_score_freeze_validation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
