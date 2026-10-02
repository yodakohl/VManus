#!/usr/bin/env python3
"""Independent protocol/accounting check for GDT1144; does not judge pixels."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


def repo_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "AGENTS.md").is_file() and (p / ".git").exists():
            return p
    raise RuntimeError("repository root not found")


ROOT = repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt1144_shadow_axis_native_capacity"
OUT = EXP / "artifacts/VALIDATION.json"
PANELS = ("left", "right")
ITEMS = ("M1", "M2", "M3", "M4")
STATUSES = {"PRESENT", "ABSENT_AT_SUPPLIED_SCALE", "UNRESOLVED"}
CLAIM_LIMIT = "Recorded local visible prerequisites only; no semantic refutation or scored inscription edges"
CHECK_COUNT = 0


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(condition: bool, label: str, failures: list[str]) -> None:
    global CHECK_COUNT
    CHECK_COUNT += 1
    if not condition:
        failures.append(label)


def timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    failures: list[str] = []
    lock = read_json(EXP / "src/PREREG_LOCK.json")
    source_path = EXP / "src/SOURCE.json"
    source = read_json(source_path)
    manifest = read_json(EXP / "experiment.json")
    method_path = EXP / "METHOD.md"
    prereg_path = EXP / "PREREGISTRATION.md"
    pins = lock.get("files", {})
    check(set(pins) == {
        "experiments/yolo/gdt1144_shadow_axis_native_capacity/METHOD.md",
        "experiments/yolo/gdt1144_shadow_axis_native_capacity/PREREGISTRATION.md",
        "experiments/yolo/gdt1144_shadow_axis_native_capacity/src/SOURCE.json",
    }, "lock has exact registered input key set", failures)
    for rel, expected in pins.items():
        check((ROOT / rel).is_file() and sha(ROOT / rel) == expected,
              f"lock pin matches {rel}", failures)
    check(pins.get("experiments/yolo/gdt1144_shadow_axis_native_capacity/METHOD.md") ==
          pins.get("experiments/yolo/gdt1144_shadow_axis_native_capacity/PREREGISTRATION.md"),
          "METHOD and PREREGISTRATION are the same frozen bytes", failures)
    image = ROOT / source.get("cache", "")
    check(image.is_file() and sha(image) == source.get("sha256"),
          "registered cached canvas bytes match source hash", failures)
    check(source.get("canvas") == "1006194" and source.get("width") == 4972 and
          source.get("height") == 3738 and source.get("represented_selectors") == ["f67r1", "f67r2"] and
          source.get("panels") == list(PANELS) and source.get("items") == list(ITEMS),
          "registered source identity and full two-panel scope", failures)
    declared_inputs = manifest.get("inputs", [])
    check(manifest.get("experiment_id") == "GDT1144" and
          manifest.get("dependencies") == ["GDT871"] and len(declared_inputs) == 5,
          "manifest identity, dependency, and registered input roster", failures)
    for item in declared_inputs:
        declared_path = ROOT / item.get("path", "")
        check(declared_path.is_file() and sha(declared_path) == item.get("sha256"),
              f"manifest input pin matches {item.get('path')}", failures)
    seals = manifest.get("sealed_data", {})
    check(seals.get("f84") == "FORBIDDEN" and seals.get("f84r") == "FORBIDDEN" and
          seals.get("f116v") == "UNADMITTED" and seals.get("reserves") == "CLOSED",
          "manifest preserves sealed, unadmitted, and reserve boundaries", failures)
    check(manifest.get("claim_ceiling") == "Local visual prerequisites only; no meaning selection or scored inscription edges",
          "manifest claim ceiling remains within the registered visual-capacity scope", failures)
    check(manifest.get("status") == "NO_OWNED_CONSTRUCTION_CAPACITY_IN_FIXED_CANVAS",
          "manifest status matches the independently rebuilt decision", failures)

    root = read_json(EXP / "artifacts/ROOT.json")
    root_freeze = read_json(EXP / "artifacts/ROOT_FREEZE.json")
    observer = read_json(EXP / "artifacts/OBSERVER.json")
    observer_freeze = read_json(EXP / "artifacts/OBSERVER_FREEZE.json")
    check(root_freeze.get("sha256") == sha(EXP / "artifacts/ROOT.json"),
          "root freeze receipt binds exact root record", failures)
    check(observer_freeze.get("sha256") == sha(EXP / "artifacts/OBSERVER.json"),
          "observer freeze receipt binds exact observer record", failures)
    check(root.get("source_sha256") == source.get("sha256") and
          observer.get("source_sha256") == source.get("sha256"),
          "both records name the registered canvas", failures)
    check(observer.get("status") == "FROZEN_BEFORE_COMPARISON" and
          observer_freeze.get("sha256") == sha(EXP / "artifacts/OBSERVER.json"),
          "observer record is frozen before comparison", failures)
    check(root.get("informed") is True and root.get("view_mode") == "native full complete image, original detail",
          "root record states required full-native observation mode", failures)
    inv = observer.get("view_inventory", [])
    check(len(inv) == 1 and inv[0].get("complete_canvas") is True and
          inv[0].get("dimensions") == [4972, 3738] and inv[0].get("panels") == list(PANELS) and
          inv[0].get("view_count") == 1 and inv[0].get("detail") == "original",
          "observer inventory is exactly one complete native canvas view", failures)
    check(timestamp(root_freeze["utc"]) < timestamp(observer.get("utc")) and
          timestamp(observer.get("utc")) <= timestamp(observer_freeze["received_utc"]),
          "observer's declared observation follows root freeze and precedes its receipt", failures)
    check(timestamp(lock["utc"]) <= timestamp(root_freeze["utc"]) and
          timestamp(lock["utc"]) <= timestamp(observer.get("utc")),
          "preregistration lock predates both observations", failures)

    expected_keys = {(p, i) for p in PANELS for i in ITEMS}

    def index_observations(record, who):
        rows = record.get("observations", [])
        keys = [(r.get("panel"), r.get("item")) for r in rows]
        check(len(rows) == 8 and len(set(keys)) == 8 and set(keys) == expected_keys,
              f"{who} has exactly one row for every panel/item cell", failures)
        result = {}
        for row in rows:
            key = (row.get("panel"), row.get("item"))
            check(row.get("status") in STATUSES, f"{who} {key} has allowed status", failures)
            check(bool(str(row.get("location", "")).strip()) and
                  bool(str(row.get("description", "")).strip()),
                  f"{who} {key} retains location and literal description", failures)
            if key in expected_keys:
                result[key] = row
        return result

    rr = index_observations(root, "root")
    oo = index_observations(observer, "observer")
    result = read_json(EXP / "artifacts/RESULT.json")
    result_rows = result.get("cells", [])
    rkeys = [(r.get("panel"), r.get("item")) for r in result_rows]
    check(len(result_rows) == 8 and len(set(rkeys)) == 8 and set(rkeys) == expected_keys,
          "comparison result has exactly one row for every panel/item cell", failures)

    joint = {}
    for key in expected_keys:
        a, b = rr[key].get("status"), oo[key].get("status")
        merged = a if a == b else "UNRESOLVED"
        joint[key] = merged
        row = next((x for x in result_rows if (x.get("panel"), x.get("item")) == key), {})
        check(row.get("root") == a and row.get("observer") == b and row.get("joint") == merged,
              f"comparison preserves independent statuses and unresolved disagreement at {key}", failures)

    construction_panels = []
    street_panels = []
    for panel in PANELS:
        construction_items = ("M1", "M2", "M4")
        if all(rr[(panel, x)].get("status") == "PRESENT" and
               oo[(panel, x)].get("status") == "PRESENT" for x in construction_items):
            construction_panels.append(panel)
        if all(rr[(panel, x)].get("status") == "PRESENT" and
               oo[(panel, x)].get("status") == "PRESENT" for x in ("M3", "M4")):
            street_panels.append(panel)
    candidates = sorted(set(construction_panels + street_panels))
    # The fixed rule additionally requires shared located ownership. In this packet no panel
    # satisfies even the necessary jointly-PRESENT statuses, so no subjective linkage test is needed.
    decision = "NO_OWNED_CONSTRUCTION_CAPACITY_IN_FIXED_CANVAS" if not candidates else "CANDIDATE_REQUIRES_SAME_CONNECTION_REVIEW"
    check(not construction_panels and not street_panels,
          "no panel meets both observers' fixed positive prerequisites", failures)
    check(result.get("candidate_panels_requiring_same_connection_review") == [] and
          result.get("status") == decision,
          "result decision and candidate list follow preregistered rule", failures)
    check(result.get("source_sha256") == source.get("sha256"),
          "result remains bound to registered image", failures)
    check(result.get("confirmed_words") == 0 and result.get("independent_meaning_confirmation_capacity") == 0 and
          result.get("claim_ceiling") == CLAIM_LIMIT,
          "result preserves fixed claim ceiling", failures)
    check("no semantic refutation" in result.get("claim_ceiling", "").lower(),
          "negative result is not a semantic refutation and makes no sealed-data claim", failures)

    payload = {
        "experiment": "GDT1144",
        "validator": "independent protocol/accounting check; no visual truth assessment",
        "status": "PASS" if not failures else "FAIL",
        "checks_passed": CHECK_COUNT - len(failures),
        "checks_run": CHECK_COUNT,
        "checks_failed": len(failures),
        "failures": failures,
        "registered_source_sha256": source.get("sha256"),
        "root_observer_cells": 16,
        "comparison_cells": len(result_rows),
        "disagreement_cells_retained_as_unresolved": sorted(
            [f"{p}/{i}" for (p, i), value in joint.items()
             if rr[(p, i)].get("status") != oo[(p, i)].get("status") and value == "UNRESOLVED"]
        ),
        "rebuilt_decision": decision,
        "construction_candidate_panels_before_same_connection_review": construction_panels,
        "street_candidate_panels_before_same_connection_review": street_panels,
        "meaning_confirmation_capacity": 0,
        "claim_limit": CLAIM_LIMIT,
        "validation_scope": "hashes, freezes, complete cell accounting, disagreement retention, and preregistered decision arithmetic only",
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
