#!/usr/bin/env python3
"""Validate V3 cache equivalence on fabricated observation-only rows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import run_blind_decoders as v1
import run_blind_decoders_v3 as v3

OUT = v1.EXP / "artifacts/gdt395_runner_cache_equivalence_validation.json"


def fake_rows(seed: int, n: int) -> list[dict]:
    rows = []
    for i in range(n):
        rows.append({
            "world_id": "FAKE", "corpus_seed": str(seed), "event_id": f"E{seed}_{i}",
            "page_id": f"P{i // 12}", "paragraph_id": f"Q{i // 6}",
            "record_id": f"R{i // 4}", "line_id": f"L{i // 2}",
            "event_index": str(i), "group_index": str(i % 4),
            "visible_group": ("ab", "cab", "dabx", "ef")[i % 4],
            "separator_before": ("RECORD", "SPACE", "JOIN", "LINE")[i % 4],
            "separator_after": ("SPACE", "JOIN", "LINE", "RECORD")[i % 4],
            "register_id": f"RG{i % 2}", "hand_id": f"H{i % 3}",
            "layout_role": f"Y{i % 2}", "line_position_bin": str(i % 3),
            "record_position_bin": str(i % 4), "ambiguous_boundary": str(i % 5 == 0),
        })
    return rows


def normalized(claims: list[dict]) -> list[dict]:
    claims = [dict(row) for row in claims]
    v3.repair_missing_confidence(claims)
    return claims


def main() -> None:
    train, held = fake_rows(0, 64), fake_rows(1, 16)
    freeze = json.loads(v1.FREEZE.read_text())
    checks = {}
    for frozen in freeze["decoders"]:
        path = v1.ROOT / frozen["directory"] / "decoder.py"
        base = v1.load_decoder(path, "equiv_base_" + frozen["meta"]["decoder_id"])
        cached = v3.install_training_cache(v1.load_decoder(path, "equiv_cache_" + frozen["meta"]["decoder_id"]))
        decoder_id = frozen["meta"]["decoder_id"]
        for representation in v1.REPRESENTATIONS:
            left = normalized(base.decode(train, held, representation))
            right_first = normalized(cached.decode(train, held, representation))
            right_second = normalized(cached.decode(train, held, representation))
            checks[f"{decoder_id}:{representation}"] = left == right_first == right_second
        checks[f"{decoder_id}:WORLD"] = base.classify_world(train) == cached.classify_world(train)
    result = {
        "schema": "GDT395_RUNNER_CACHE_EQUIVALENCE_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "fabricated_train_rows": len(train), "fabricated_held_rows": len(held),
        "checks": checks, "checks_passed": sum(checks.values()), "checks_total": len(checks),
        "voynich_rows": 0, "oracle_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
