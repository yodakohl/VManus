#!/usr/bin/env python3
"""Independent integrity/comparison audit; never validates native visual truth."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
STATES = ("MATCH", "CONTRADICTED", "UNRESOLVED")
CANVASES = ["1006194", "1006196", "1006199", "1006200", "1006201", "1006203"]
SELECTORS = set("f67r1 f67r2 f68r1 f68r2 f68r3 f69v f70r1 f70r2 f70v1 f70v2 f71v f72r1 f72r2 f72r3".split())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def utc(value):
    require(nonempty(value), "Missing UTC timestamp")
    parsed = datetime.fromisoformat(value.replace(" UTC", "+00:00").replace("Z", "+00:00"))
    require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0,
            "Timestamp must explicitly be UTC")
    return parsed.astimezone(timezone.utc)


def compare_independently(first, second):
    """Index pairing uses frozen observation order; mismatch taints entire canvas."""
    require(len(first["images"]) == len(second["images"]), "Image-panel length mismatch")
    result = []
    for position in range(len(first["images"])):
        left, right = first["images"][position], second["images"][position]
        require(left["canvas_id"] == right["canvas_id"], "Canvas order mismatch")
        a, b = left["units"], right["units"]
        equal_count = len(a) == len(b)
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else None
            y = b[i] if i < len(b) else None
            state = "UNRESOLVED"
            if equal_count and x["status"] == y["status"]:
                state = x["status"]
            result.append({"canvas_id": left["canvas_id"], "unit_index": i + 1,
                           "joint": state, "A": x, "B": y,
                           "same_unit_count": equal_count})
    return result


def overall(rows):
    values = {row["joint"] for row in rows}
    if "MATCH" in values:
        return "CANDIDATE_FRAMEWORK_ONLY"
    if "UNRESOLVED" in values:
        return "UNRESOLVED_FRAMEWORK_CAPACITY"
    require(bool(rows), "No recorded units cannot imply complete contradiction")
    return "ALL_REPRESENTATIVE_FRAMEWORKS_CONTRADICTED"


def synthetic_checks():
    def panel(states):
        return {"images": [{"canvas_id": "fixture", "units": [{"status": s} for s in states]}]}
    fixtures = [
        (["MATCH"], ["MATCH"], ["MATCH"]),
        (["CONTRADICTED"], ["CONTRADICTED"], ["CONTRADICTED"]),
        (["UNRESOLVED"], ["UNRESOLVED"], ["UNRESOLVED"]),
        (["MATCH"], ["CONTRADICTED"], ["UNRESOLVED"]),
        (["CONTRADICTED"], ["UNRESOLVED"], ["UNRESOLVED"]),
        (["MATCH", "CONTRADICTED"], ["MATCH"], ["UNRESOLVED", "UNRESOLVED"]),
        ([], ["CONTRADICTED"], ["UNRESOLVED"]),
    ]
    for a, b, expected in fixtures:
        actual = compare_independently(panel(a), panel(b))
        require([r["joint"] for r in actual] == expected, "Synthetic aggregation failed")
        require([r["joint"] for r in compare_independently(panel(b), panel(a))] == expected,
                "Synthetic symmetry failed")
    require(overall([{"joint": "MATCH"}, {"joint": "UNRESOLVED"}]) == "CANDIDATE_FRAMEWORK_ONLY", "Match precedence")
    require(overall([{"joint": "CONTRADICTED"}, {"joint": "UNRESOLVED"}]) == "UNRESOLVED_FRAMEWORK_CAPACITY", "Unknown preservation")
    try:
        overall([])
    except AssertionError:
        pass
    else:
        raise AssertionError("Empty result incorrectly accepted")
    return len(fixtures) + 3


def fixed_sources(registration_only):
    lock = read(E / "PREREG_LOCK.json")
    bindings = lock["files"]
    require(lock["stage"] == "BEFORE_CURRENT_NATIVE_VIEWS", "Preregistration stage")
    needed = [E / "METHOD.md", E / "src/SOURCES.json", E / "src/SOURCE_REVIEW.md",
              E / "src/SOURCE_GEOMETRY.md", E / "src/DECISION.md", E / "src/run.py",
              E / "src/validate.py", R / "docs/VOYNICH_DATA_SCOPE.md"]
    for path in needed:
        require(path.relative_to(R).as_posix() in bindings, "Missing preregistration binding")
    for name, expected in sorted(bindings.items()):
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "Unsafe bound path")
        require(digest(R / name) == expected, "Frozen hash mismatch: " + name)
    spec = read(E / "src/SOURCES.json")["images"]
    require([row["canvas_id"] for row in spec] == CANVASES, "Six-source order")
    require({x for row in spec for x in row["selectors"]} == SELECTORS, "Fourteen-selector scope")
    for row in spec:
        metadata_name = row["prior_metadata"]
        require(metadata_name in bindings, "Parent metadata not bound")
        parent = read(R / metadata_name)
        candidates = parent.get("source_images", [parent])
        matches = [p for p in candidates if p.get("canvas_id") == row["canvas_id"]
                   and p.get("image_url") == row["image_url"]]
        require(len(matches) == 1, "Missing or ambiguous original rendering")
        for key in ("sha256", "bytes", "width", "height", "image_url"):
            require(row[key] == matches[0][key], "Parent rendering mismatch: " + key)
        if not registration_only:
            path = R / row["runtime"]
            require(path.stat().st_size == row["bytes"] and digest(path) == row["sha256"],
                    "Acquired image byte mismatch: " + row["canvas_id"])
    return spec, len(bindings)


def observation(identifier, spec):
    path = E / "artifacts" / (identifier + "_OBSERVATION.json")
    seal_path = E / "artifacts" / (identifier + "_SEAL.json")
    data, seal = read(path), read(seal_path)
    require(data["observer"] == seal["observer"] == identifier, "Observer identity")
    require(seal["observation_sha256"] == digest(path), "Observation seal mismatch")
    sealed = utc(seal["sealed_at_utc"])
    require([row["canvas_id"] for row in data["images"]] == CANVASES, "Observation source order")
    viewed = []
    for row, source in zip(data["images"], spec):
        require(row["source_sha256"] == source["sha256"], "Observed rendering hash")
        seen = utc(row["viewed_at_utc"])
        require(seen <= sealed, "Image observation postdates its seal")
        viewed.append(seen)
        for key in ("outside_scope", "visibility_notes"):
            require(nonempty(row[key]), "Missing image description: " + key)
        require(isinstance(row["units"], list), "Units must be a list")
        for i, unit in enumerate(row["units"], start=1):
            require(unit["unit_index"] == i, "Unit indexing must be consecutive")
            require(unit["status"] in STATES, "Unknown category")
            for key in ("region", "boundary_summary", "reason", "extra_geometry", "visibility_notes"):
                require(nonempty(unit[key]), "Missing unit description: " + key)
    return data, sealed, viewed, {"observation_sha256": digest(path), "seal_sha256": digest(seal_path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration-only", action="store_true")
    options = parser.parse_args()
    checks = synthetic_checks()
    spec, bound_count = fixed_sources(options.registration_only)
    receipt = {"status": "PASS_REGISTRATION_ONLY" if options.registration_only else "PASS",
               "registration_only": options.registration_only,
               "fixed_renderings": len(spec), "fixed_union_selectors": len(SELECTORS),
               "preregistered_files_checked": bound_count,
               "synthetic_cases": checks, "prereg_lock_sha256": digest(E / "PREREG_LOCK.json"),
               "validator_sha256": digest(Path(__file__)),
               "claim_ceiling": "File, schema, source and comparison integrity only; native visual truth and semantic meaning are not validated."}
    if not options.registration_only:
        a, seal_a, seen_a, hashes_a = observation("A", spec)
        b, seal_b, seen_b, hashes_b = observation("B", spec)
        require(seal_a <= min(seen_b), "B must view only after A is sealed")
        require(seal_a <= seal_b, "Observer seal order")
        expected = compare_independently(a, b)
        actual = read(E / "artifacts/RESULT.json")
        require(actual["joint_units"] == expected, "Complete joint record mismatch")
        counts = Counter(row["joint"] for row in expected)
        expected_counts = {key: counts[key] for key in STATES}
        require(actual["counts"] == expected_counts, "Joint counts mismatch")
        require(actual["status"] == overall(expected), "Overall conclusion mismatch")
        require(actual["confirmed_words"] == actual["independent_meaning_confirmation_capacity"] == 0,
                "Unsupported semantic confirmation")
        require(nonempty(actual["claim_ceiling"]), "Missing claim ceiling")
        receipt.update(observers={"A": hashes_a, "B": hashes_b}, joint_counts=expected_counts,
                       joint_units=len(expected), result_status=actual["status"],
                       result_sha256=digest(E / "artifacts/RESULT.json"),
                       acquired_images_checked=6, observed_unit_counts={
                           "A": [len(x["units"]) for x in a["images"]],
                           "B": [len(x["units"]) for x in b["images"]]})
    output = E / "artifacts/VALIDATION.json"
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "fixed_renderings", "synthetic_cases")}, sort_keys=True))


if __name__ == "__main__":
    main()
