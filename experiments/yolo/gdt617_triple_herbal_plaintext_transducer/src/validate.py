#!/usr/bin/env python3
"""Validate the GDT617 prospective source registration and local freeze."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from acquire_sources import (
    EXPERIMENT,
    REGISTRY_PATH,
    ROOT,
    network_guard_selftest,
    verify_existing,
)


REPORT_PATH = EXPERIMENT / "artifacts" / "REGISTERED_VALIDATION.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_HOSTS = {
    "alexandrine-bibnum.beauxartsparis.fr",
    "bl.digirati.io",
    "gallica.bnf.fr",
    "searcharchives.bl.uk",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"check": name, "detail": detail, "pass": bool(condition)})

    try:
        cfg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        check("registry_schema", cfg.get("schema_version") == 1)
        check("experiment_id", cfg.get("experiment_id") == "GDT617")
        check("six_sources", len(cfg.get("sources", [])) == 6)
        check(
            "three_witnesses",
            len({source["witness_id"] for source in cfg["sources"]}) == 3,
        )
        check(
            "catalog_and_manifest_per_witness",
            all(
                {
                    source["source_kind"]
                    for source in cfg["sources"]
                    if source["witness_id"] == witness
                }
                == {"OFFICIAL_CATALOGUE_METADATA", "OFFICIAL_IIIF_MANIFEST"}
                for witness in {source["witness_id"] for source in cfg["sources"]}
            ),
        )
        check(
            "official_https_hosts",
            all(
                urlsplit(source["url"]).scheme == "https"
                and urlsplit(source["url"]).hostname in ALLOWED_HOSTS
                for source in cfg["sources"]
            ),
        )
        check(
            "binding_hashes",
            all(HEX64.fullmatch(source["expected_binding_sha256"]) for source in cfg["sources"]),
        )
        check(
            "response_size_ceiling",
            cfg.get("max_bytes_per_response") == 1_000_000
            and all(source["expected_binding_bytes"] <= 1_000_000 for source in cfg["sources"]),
        )
        check(
            "canvas_counts",
            sorted(
                source["expected_canvas_count"]
                for source in cfg["sources"]
                if source["source_kind"] == "OFFICIAL_IIIF_MANIFEST"
            )
            == [187, 235, 513],
        )
        gate = cfg["downstream_gate"]
        check("five_target_folios", gate["minimum_distinct_target_physical_folios"] == 5)
        check("four_discovery", gate["discovery_folios"] == 4)
        check("one_held", gate["held_folios"] == 1)
        check("twelve_held_words", gate["held_content_words"] == 12)
        check("three_source_witnesses", gate["source_witnesses_per_entry"] == 3)
        check("global_short_transducer", "ZERO_THROUGH_THREE" in gate["model"])
        check("no_macros", gate["no_macros"] is True)
        check("no_context_keys", gate["no_context_keys"] is True)
        check("no_page_keys", gate["no_page_or_folio_keys"] is True)

        manifest = json.loads((EXPERIMENT / "experiment.json").read_text(encoding="utf-8"))
        check("manifest_id", manifest.get("experiment_id") == "GDT617")
        check("sealed_f84", manifest.get("sealed_data", {}).get("f84") == "FORBIDDEN")
        check("sealed_f84r", manifest.get("sealed_data", {}).get("f84r") == "FORBIDDEN")
        check("registered_status", manifest.get("status") == "SOURCE_REGISTERED_UNSCORED")
        validation_relative = str(REPORT_PATH.relative_to(ROOT))
        bound_files = [
            row
            for section in ("inputs", "outputs")
            for row in manifest.get(section, [])
            if row.get("path") != validation_relative
        ]
        manifest_hash_failures = [
            row.get("path")
            for row in bound_files
            if not (ROOT / str(row.get("path"))).is_file()
            or sha256_file(ROOT / str(row.get("path"))) != row.get("sha256")
        ]
        check("manifest_bound_file_hashes", not manifest_hash_failures, manifest_hash_failures)

        prereg = (EXPERIMENT / "PREREGISTRATION.md").read_text(encoding="utf-8")
        method = (EXPERIMENT / "METHOD.md").read_text(encoding="utf-8")
        check("target_unopened_text", "SOURCE_BINDING_PASS__TARGET_UNOPENED" in prereg)
        check("exact_held_text", "exact heading plus twelve content words" in prereg.lower())
        check("no_macro_text", "No macro" in prereg)
        check("deterministic_panel_rule", "GDT617_PANEL_V1" in method and "GDT617_HELD_V1" in method)
        check("canonical_solver_rule", "total output length" in method and "ASCII lexicographic" in method)

        image_suffixes = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".gif"}
        image_files = [
            str(path.relative_to(ROOT))
            for path in EXPERIMENT.rglob("*")
            if path.is_file() and path.suffix.lower() in image_suffixes
        ]
        check("no_image_files", not image_files, image_files)

        replay = verify_existing()
        check("source_freeze_replay", replay["decision"] == "SOURCE_BINDING_PASS__TARGET_UNOPENED")
        audit = replay["request_audit"]
        registered_urls = [source["url"] for source in cfg["sources"]]
        logged_urls = [event["url"] for event in audit["request_log"]]
        check(
            "exact_six_allowlisted_requests",
            audit["requests_started"] == 6
            and audit["requests_completed"] == 6
            and audit["allowlisted_initial_requests"] == 6
            and logged_urls == registered_urls,
        )
        check(
            "zero_redirects",
            audit["redirect_attempts"] == 0
            and audit["redirect_followed"] == 0
            and audit["redirect_log"] == [],
        )
        check("zero_non_allowlisted_requests", audit["non_allowlisted_requests"] == 0)
        check("zero_canvas_requests", replay["canvas_requests"] == 0)
        check("zero_image_requests", replay["image_requests"] == 0)
        check("zero_target_requests", replay["target_requests"] == 0)
        check("source_count_replay", replay["source_count"] == 6)
        check("witness_count_replay", replay["witness_count"] == 3)
        guard = network_guard_selftest()
        check("guard_clean_exact_six", guard["clean_exact_six"])
        check("guard_unknown_url_rejected", guard["unknown_url_rejected"])
        check("guard_redirect_rejected", guard["redirect_rejected"])
        check("guard_redirect_never_followed", guard["redirect_marked_unfollowed"])
    except Exception as exc:  # validator must publish the exact local failure
        check("validator_exception", False, f"{type(exc).__name__}: {exc}")

    passed = sum(1 for row in checks if row["pass"])
    payload = {
        "checks": checks,
        "decision": "PASS" if passed == len(checks) else "FAIL",
        "experiment_id": "GDT617",
        "passed": passed,
        "registry_sha256": sha256_file(REGISTRY_PATH),
        "total": len(checks),
    }
    REPORT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"GDT617_REGISTRATION_{payload['decision']} {passed}/{len(checks)}")
    return 0 if payload["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
