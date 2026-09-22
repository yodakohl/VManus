#!/usr/bin/env python3
"""Run the frozen GDT1039 reference policies after preregistration only."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent
DEFAULT_SPEC = HERE / "SPEC.json"
DEFAULT_LOCK = HERE.parent / "PREREG_LOCK.json"
DEFAULT_PUBLIC = HERE.parent / "artifacts" / "PUBLIC_REGISTRATION.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_spec(path: Path = DEFAULT_SPEC) -> dict[str, Any]:
    spec = read_json(path)
    if not isinstance(spec, dict) or spec.get("schema_version") != 1:
        raise ValueError("SPEC.json must have schema_version 1")
    ids = [p.get("id") for p in spec.get("policies", [])]
    expected = ["DEFERRED_CONSUMING", "DEFERRED_NONCONSUMING", "EAGER_CONSUMING",
                "EAGER_NONCONSUMING", "UNTYPED_RECENT", "GLOBAL_CONSUMPTION"]
    if ids != expected or len(spec.get("fetches", [])) != 7 or len(spec.get("event_inventory", [])) != 26:
        raise ValueError("SPEC frozen policy/event/fetch inventory is incomplete")
    if spec.get("frozen_contract", {}).get("constructions") != 12:
        raise ValueError("SPEC construction count is not twelve")
    return spec


def check_preregistration(spec: dict[str, Any], lock_path: Path, public_path: Path) -> dict[str, Any]:
    if not lock_path.is_file() or not public_path.is_file():
        raise RuntimeError("--execute requires PREREG_LOCK.json and PUBLIC_REGISTRATION.json")
    lock, public = read_json(lock_path), read_json(public_path)
    if lock.get("status") != "REGISTERED_BEFORE_EXECUTION" or not isinstance(lock.get("files"), list):
        raise RuntimeError("PREREG_LOCK.json is not a root registration receipt")
    if (public.get("registered_before_execution") is not True or public.get("public_ref") != "origin/main"
            or not re.fullmatch(r"[0-9a-f]{40}", str(public.get("commit", "")))):
        raise RuntimeError("PUBLIC_REGISTRATION.json is not a confirmed public registration")
    locked = {item.get("path"): item.get("sha256") for item in lock["files"] if isinstance(item, dict)}
    for relative, expected in locked.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise RuntimeError("invalid locked path/hash")
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"locked hash stale: {relative}")
    required = list(spec["inputs"].values()) + [spec["inputs"]["spec"], spec["inputs"]["runner"]]
    for relative in required:
        path = ROOT / relative
        if relative not in locked or locked[relative] != digest(path):
            raise RuntimeError(f"locked hash missing or stale: {relative}")
    return {"lock": lock, "public": public}


class Resolver:
    """Selection receives only required type, recency and used identities."""

    def __init__(self, spec: dict[str, Any], policy: dict[str, Any]):
        self.spec, self.policy = spec, policy
        self.records = {r["id"]: dict(r, visible=False, recency=-1) for r in spec["registry"]["records"]}
        self.used: set[str] = set()
        self.clock = 0
        self.construction: str | None = None
        self.stopped: str | None = None
        self.fetches: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.selected: dict[str, str] = {}
        self.fetch_by_id = {f["id"]: f for f in spec["fetches"]}

    def _begin(self, construction: str) -> None:
        if construction != self.construction:
            self.construction = construction
            if self.policy["reset"] == "local":
                self.used = set()

    def _publish(self, record_id: str, event: dict[str, Any]) -> None:
        record = self.records[record_id]
        record["visible"] = True
        self.clock += 1
        record["recency"] = self.clock
        self.events.append({"event": event["id"], "operation": "publish", "record": record_id,
                            "status": "PUBLISHED", "used": sorted(self.used)})

    def _touch(self, record_id: str, event: dict[str, Any]) -> None:
        record = self.records[record_id]
        self.clock += 1
        record["recency"] = self.clock
        self.events.append({"event": event["id"], "operation": "touch", "record": record_id,
                            "status": "TOUCHED", "used": sorted(self.used)})

    def _fetch(self, fetch_id: str, event: dict[str, Any]) -> None:
        fetch = self.fetch_by_id[fetch_id]
        required = fetch["required_type"]
        candidates = [r for r in self.records.values() if r["visible"] and r["eligible"]
                      and r["id"] not in self.used and (not self.policy["typed"] or r["type"] == required)]
        candidates.sort(key=lambda r: r["recency"], reverse=True)
        before = sorted(self.used)
        registry_before = [{"id": r["id"], "type": r["type"], "recency": r["recency"]}
                           for r in sorted(self.records.values(), key=lambda r: r["recency"], reverse=True)
                           if r["visible"] and r["eligible"]]
        selection_state = {"eligible": [r["id"] for r in candidates], "registry_before": registry_before}
        if not candidates:
            self.stopped = fetch["construction"]
            item = {**selection_state, "fetch": fetch_id, "required_type": required, "selected": None,
                    "status": "STOP_UNBOUND", "stop_reason": "UNBOUND",
                    "used_before": before, "used_after": before}
            self.fetches.append(item)
            self.events.append({"event": event["id"], "operation": "fetch", **item})
            return
        selected = candidates[0]
        status = "FETCHED"
        if selected["type"] != required:
            status = "STOP_WRONG_TYPE"
            self.stopped = fetch["construction"]
        else:
            self.selected[fetch_id] = selected["id"]
            if self.policy["consuming"]:
                self.used.add(selected["id"])
            self.clock += 1
            selected["recency"] = self.clock
        item = {**selection_state, "fetch": fetch_id, "required_type": required, "selected": selected["id"],
                "selected_type": selected["type"], "status": status,
                **({"stop_reason": "TYPE_CONFLICT"} if status == "STOP_WRONG_TYPE" else {}),
                "used_before": before, "used_after": sorted(self.used)}
        self.fetches.append(item)
        self.events.append({"event": event["id"], "operation": "fetch", **item})

    def run(self) -> dict[str, Any]:
        for event in self.spec["event_inventory"]:
            self._begin(event["construction"])
            if self.stopped:
                self.events.append({"event": event["id"], "operation": event["op"], "status": "SKIPPED_AFTER_STOP"})
                continue
            op = event["op"]
            if op == "publish":
                self._publish(event["record"], event)
            elif op == "touch":
                self._touch(event["record"], event)
            elif op == "prepare":
                self.events.append({"event": event["id"], "operation": op, "record": event["record"], "status": "PRIVATE"})
            elif op == "fetch":
                self._fetch(event["fetch"], event)
            elif op == "publish_eager_or_fetch":
                if self.policy["publication"] == "eager":
                    self._publish("B", event)
                    self._publish("RB", event)
                self._fetch(event["fetch"], event)
            elif op == "publish_deferred":
                if self.policy["publication"] == "deferred":
                    self._publish(event["record"], event)
                else:
                    self.events.append({"event": event["id"], "operation": op, "status": "NOT_APPLICABLE"})
            else:
                raise ValueError(f"unknown event operation: {op}")
        return {"policy": self.policy["id"], "stop": self.stopped, "fetches": self.fetches,
                "events": self.events, "selected": self.selected, "complete": self.stopped is None}


def truth_row(trace: dict[str, Any], a: int, b: int) -> dict[str, Any]:
    if not trace["complete"]:
        return {"c11": None, "c12": None, "joint": None}
    values = {"A": a, "RA": a, "B": b, "RB": b}
    chosen = trace["selected"]
    c11 = b == values[chosen["F5"]]
    c12 = values[chosen["F6"]] == values[chosen["F7"]]
    return {"c11": c11, "c12": c12, "joint": c11 and c12}


def build_coverage(source: dict[str, Any], source_path: str) -> dict[str, Any]:
    positions, number = [], 0
    for record in source["records"]:
        for word in record["raw"].split():
            number += 1
            positions.append({"position": number, "locus": record["locus"], "word": word, "inherited_source": source_path})
    if number != 80:
        raise ValueError(f"inherited source has {number} positions, expected 80")
    return {"status": "INHERITED_SOURCE_COVERAGE", "position_count": number, "source": source_path,
            "source_sha256": digest(ROOT / source_path), "positions": positions}


def execute(spec_path: Path, lock_path: Path, public_path: Path) -> dict[str, Any]:
    spec = load_spec(spec_path)
    receipt = check_preregistration(spec, lock_path, public_path)
    source = read_json(ROOT / spec["inputs"]["source"])
    rows = read_json(ROOT / spec["inputs"]["rows"])
    if not isinstance(rows, list) or len(rows) != 357:
        raise ValueError("old GDT1015 ROWS must contain exactly 357 rows")
    traces = {p["id"]: Resolver(spec, p).run() for p in spec["policies"]}
    table = []
    for row_index, old in enumerate(rows):
        equal = old["method_a_ruler_index"] == old["method_b_ruler_index"]
        for policy in spec["policies"]:
            trace = traces[policy["id"]]
            table.append({"row_index": row_index, "policy": policy["id"], "equal_pair": equal,
                          "truth": truth_row(trace, old["method_a_ruler_index"], old["method_b_ruler_index"]), "first_stop": trace["stop"],
                          "reference_override": old.get("candidate") == "SAME_METHOD_REFERENCE",
                          "inherited_numeric": {
                              "setting": old.get("setting"), "candidate": old.get("candidate"),
                              "daylight_hours": old.get("daylight_hours"), "initial_phase": old.get("initial_phase"),
                              "method_a_hour_offset": old.get("method_a_hour_offset"),
                              "method_a_ruler_index": old.get("method_a_ruler_index"),
                              "method_b_steps": old.get("method_b_steps"),
                              "method_b_ruler_index": old.get("method_b_ruler_index"),
                              "complete_cycles_removed": old.get("complete_cycles_removed"),
                              "remainder": old.get("remainder"), "old_c11_same": old.get("C11_same"),
                              "old_c12_agrees": old.get("C12_agrees"),
                              "old_argument_coherent": old.get("argument_coherent"),
                              "source_continuous_hours": old.get("source_continuous_hours")
                          },
                          "nonreference_costs": {
                              "extra_scope_assumptions": old.get("extra_scope_assumptions", []),
                              "new_word_changes": old.get("new_word_changes", {})
                          }})
    coverage = build_coverage(source, spec["inputs"]["source"])
    artifact_dir = ROOT / spec["outputs"]["directory"]
    artifact_dir.mkdir(parents=True, exist_ok=True)
    def save(name: str, value: Any) -> None:
        (artifact_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    save(spec["outputs"]["event_traces"], traces)
    save(spec["outputs"]["comparison_table"], table)
    save(spec["outputs"]["coverage"], coverage)
    result = {"experiment": "GDT1039", "status": "COMPLETE_CONDITIONAL_REFERENCE_AUDIT",
              "claim_ceiling": spec["claim_ceiling"], "rows": len(rows), "policies": len(spec["policies"]),
              "comparison_rows": len(table), "fetches": 7,
              "policy_stops": {key: value["stop"] for key, value in traces.items()},
              "registered_commit": receipt["public"]["commit"], "source_coverage": coverage["position_count"],
              "semantic_confirmation": 0, "complete_coherence_claim": False}
    save(spec["outputs"]["result"], result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--public", type=Path, default=DEFAULT_PUBLIC)
    parser.add_argument("--schema", action="store_true", help="read and summarize SPEC only")
    parser.add_argument("--execute", action="store_true", help="run only after root preregistration receipts")
    args = parser.parse_args(argv)
    try:
        spec = load_spec(args.spec)
        if args.schema:
            print(json.dumps({"experiment": spec["experiment"], "policies": [p["id"] for p in spec["policies"]],
                              "fetches": len(spec["fetches"]), "constructions": spec["frozen_contract"]["constructions"]}, indent=2))
            return 0
        if not args.execute:
            raise RuntimeError("refusing execution without explicit --execute")
        print(json.dumps(execute(args.spec, args.lock, args.public), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "NOT_EXECUTED", "reason": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
