#!/usr/bin/env python3
"""Independent contract validator for GDT878 observation packets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - validation reports a clear error
    Image = None

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt878_text_picture_combination_feasibility"
ART = EXP / "artifacts"
PROTOCOL = [EXP / "PREREGISTRATION.md", EXP / "METHOD.md"]
ANCHORS = ["f69v.14", "f69v.18", "f69v.27", "f72r2.9", "f72r2.10", "f72r2.11", "f72r2.18"]
FROZEN_PREREG_SHA256 = "efd9ab515904e00d9d4dc2c60ef6bfb14d239ef1d488074af189e38c87251736"
FORBIDDEN_KEYS = {"meaning", "translation", "phonetic", "semantic_verdict", "p_value", "pvalue", "score", "directed_edge"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def forbidden_keys(value, path="root"):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_KEYS and child is not None:
                found.append(f"{path}.{key}")
            found.extend(forbidden_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_keys(child, f"{path}[{index}]"))
    return found


def packet_branch(packet):
    if packet.get("branch") in {"root", "geometry_b"}:
        return packet["branch"]
    if packet.get("observer") == "B":
        return "geometry_b"
    if packet.get("observer") in {"A", "ROOT", "root"}:
        return "root"
    return None


def packet_observations(packet):
    for key in ("observations", "anchors", "medallions"):
        if isinstance(packet.get(key), list):
            return packet[key]
    return []


def check_packet(packet, branch):
    errors = []
    if packet.get("schema_version", 1) != 1:
        errors.append(f"{branch}: schema_version must be 1")
    if packet_branch(packet) != branch:
        errors.append(f"{branch}: branch field mismatch")
    has_binding_list = isinstance(packet.get("source_bindings"), list) and packet["source_bindings"]
    has_single_binding = packet.get("source_path") and packet.get("source_sha256")
    if not has_binding_list and not has_single_binding:
        errors.append(f"{branch}: source_bindings must be nonempty")
    observations = packet_observations(packet)
    if not observations:
        errors.append(f"{branch}: observations must be a list")
    if not isinstance(packet.get("decision"), (dict, str)):
        errors.append(f"{branch}: decision must be an object")
    if branch == "root":
        ids = {item.get("anchor", item.get("id", item.get("locus"))) for item in observations if isinstance(item, dict)}
        missing = [anchor for anchor in ANCHORS if anchor not in ids]
        if missing:
            errors.append(f"root: missing fixed anchors {missing}")
    if branch == "geometry_b":
        scope = packet.get("scope") if isinstance(packet.get("scope"), dict) else {}
        if scope.get("page", packet.get("page", "f67r2")) != "f67r2" and packet.get("source_canvas") != "1006194":
            errors.append("geometry_b: scope.page must be f67r2")
        if not observations:
            errors.append("geometry_b: no medallion observations")
        decision = packet.get("decision")
        capacity = decision.get("capacity") if isinstance(decision, dict) else decision
        allowed = {"PERMITS_FUTURE_TEST", "CLOSES_CONCRETE_ENTRY", "DEFERS_UNCERTAIN_VISIBILITY", "STOP_THIS_JOINT_ENTRY"}
        if not (isinstance(capacity, str) and any(capacity == item or capacity.startswith(item + ":") for item in allowed)):
            errors.append("geometry_b: invalid preregistered capacity decision")
    errors.extend(forbidden_keys(packet, branch))
    return errors


def check_sources(manifest, root_packet, geometry_packet):
    errors = []
    images = manifest.get("images") if isinstance(manifest, dict) else None
    if not isinstance(images, list):
        return ["SOURCES.json: images must be a list"]
    by_id = {item.get("source_id"): item for item in images}
    required = {"source_id", "canvas_id", "path", "url", "sha256", "width", "height", "bytes", "represented_selectors"}
    for item in images:
        if not required.issubset(item):
            errors.append(f"source manifest missing fields for {item.get('source_id')}")
            continue
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"missing source runtime: {item['path']}")
            continue
        raw = path.read_bytes()
        if digest(path) != item["sha256"] or len(raw) != item["bytes"]:
            errors.append(f"source bytes/hash mismatch: {item['source_id']}")
        if Image is None:
            errors.append("Pillow unavailable for source dimensions")
        else:
            try:
                with Image.open(path) as image:
                    if image.size != (item["width"], item["height"]):
                        errors.append(f"source dimensions mismatch: {item['source_id']}")
            except Exception as exc:
                errors.append(f"source image unreadable: {item['source_id']}: {exc}")
    for binding in root_packet.get("source_bindings", []):
        item = by_id.get(binding.get("source_id"))
        if item is None or binding.get("path") != item.get("path") or binding.get("sha256") != item.get("sha256"):
            errors.append(f"root source binding mismatch: {binding.get('source_id')}")
    geometry_id = "F67_ORIGINAL"
    if geometry_packet.get("source_path") != by_id.get(geometry_id, {}).get("path") or geometry_packet.get("source_sha256") != by_id.get(geometry_id, {}).get("sha256"):
        errors.append("geometry B source binding mismatch for F67_ORIGINAL")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", type=Path, default=ART)
    ap.add_argument("--package", type=Path, default=None)
    args = ap.parse_args()
    art = args.artifacts.resolve()
    package_path = (args.package or art / "RUN_PACKAGE.json").resolve()
    errors = []
    try:
        package = load(package_path)
        root_obs = package["branches"]["root"]
        geometry_obs = package["branches"]["geometry_b"]
        source_manifest = package["source_manifest"]
        frozen_root = load(art / "ROOT_OBSERVATION.json")
        frozen_geometry = load(art / "GEOMETRY_B_OBSERVATION.json")
        frozen_sources = load(art / "SOURCES.json")
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load package: {exc}")
        package, root_obs, geometry_obs, source_manifest = {}, {}, {}, {}
        frozen_root, frozen_geometry, frozen_sources = {}, {}, {}
    if root_obs != frozen_root:
        errors.append("package ROOT_OBSERVATION does not exactly match frozen JSON")
    if geometry_obs != frozen_geometry:
        errors.append("package GEOMETRY_B_OBSERVATION does not exactly match frozen JSON")
    if source_manifest != frozen_sources:
        errors.append("package SOURCES does not exactly match frozen JSON")
    expected_protocol = {p.name: digest(p) for p in PROTOCOL}
    if package.get("protocol_sha256") != expected_protocol:
        errors.append("protocol hash mismatch")
    if package.get("frozen_preregistration_sha256") != FROZEN_PREREG_SHA256:
        errors.append("frozen preregistration hash mismatch")
    for filename, path in (("SOURCES.json", art / "SOURCES.json"), ("ROOT_OBSERVATION.json", art / "ROOT_OBSERVATION.json"), ("GEOMETRY_B_OBSERVATION.json", art / "GEOMETRY_B_OBSERVATION.json")):
        expected = package.get("input_packet_sha256", {}).get(filename)
        if expected != (digest(path) if path.is_file() else None):
            errors.append(f"input packet hash mismatch: {filename}")
    if package.get("fixed_scope", {}).get("root_anchors") != ANCHORS:
        errors.append("fixed root anchor scope mismatch")
    if package.get("fixed_scope", {}).get("forbidden_prefixes") != ["f84", "f84r"]:
        errors.append("forbidden prefix scope mismatch")
    errors.extend(check_packet(root_obs, "root"))
    errors.extend(check_packet(geometry_obs, "geometry_b"))
    errors.extend(check_sources(source_manifest, root_obs, geometry_obs))
    if isinstance(geometry_obs.get("medallions"), list):
        ids = [item.get("id") for item in geometry_obs["medallions"]]
        if len(ids) != 12 or len(set(ids)) != 12:
            errors.append("geometry B must contain exactly 12 unique medallion IDs")
        expected_capacity = bool(geometry_obs.get("three_fraction_states_capacity")) and bool(geometry_obs.get("reusable_binding"))
        if geometry_obs.get("combined_capacity") is not expected_capacity:
            errors.append("geometry B combined_capacity does not equal component booleans")
        decision = geometry_obs.get("decision", "")
        if not expected_capacity and isinstance(decision, str) and decision.startswith("PERMITS_FUTURE_TEST"):
            errors.append("geometry B cannot permit future test when combined capacity is false")
    if not isinstance(source_manifest, (dict, list)):
        errors.append("source_manifest must be an object or list")
    result = {"schema_version": 1, "experiment_id": "GDT878", "status": "PASS" if not errors else "FAIL", "errors": errors, "protocol_sha256": expected_protocol, "claim_ceiling": "contract validation cannot independently prove native vision"}
    out = art / "VALIDATION.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
