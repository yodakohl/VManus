#!/usr/bin/env python3
"""Join two frozen image-only readers only after map release."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
SRC = HERE / "src"
ART = HERE / "artifacts"
MAP_HASH = "1c2b7cf7d33caf92a179964e6c74e9498f1c6c8a3cf3c4d89a2f31e0d63ec170"
FEATURES = ("BLUE_FRINGED_CUP", "OPEN_CUP_TERMINAL", "MULTI_UNIT_SPIKE", "SPINY_ROUND_HEAD")
FOLIOS = {"f22r", "f26v", "f31r", "f32r", "f33v", "f39v", "f40v", "f42v", "f43v"}
TARGETS = {"f26v", "f39v"}
CONTROLS = {"f31r", "f33v", "f40v", "f43v"}
REFS = {"f32r", "f42v"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def compute():
    mapping_path = SRC / "BLIND_MAP.tsv"
    assert sha(mapping_path) == MAP_HASH, "blind map commitment mismatch"
    mapping = read(mapping_path)
    assert len(mapping) == 9
    by_id = {r["blind_id"]: r for r in mapping}
    assert set(by_id) == {f"B{i:02d}" for i in range(1, 10)}
    assert {r["folio"] for r in mapping} == FOLIOS
    a_path, b_path = ART / "BLIND_A.tsv", ART / "BLIND_B.tsv"
    readers = {}
    for key, path in (("A", a_path), ("B", b_path)):
        rows = read(path)
        assert len(rows) == 9
        tab = {r["blind_id"]: r for r in rows}
        assert set(tab) == set(by_id)
        for r in rows:
            assert all(r[f] in {"YES", "NO", "UNKNOWN"} for f in FEATURES)
            assert r["NOTE"].strip()
        readers[key] = tab
    source_path = SRC / "SOURCE.tsv"
    sources = read(source_path)
    assert len(sources) == 9 and {r["blind_id"] for r in sources} == set(by_id)
    for row in sources:
        assert row["canvas_id"] == by_id[row["blind_id"]]["canvas_id"]
        assert row["image_url"].startswith("https://collections.library.yale.edu/iiif/2/")
        assert len(row["sha256"]) == 64 and int(row["bytes"]) > 0
    joined = []
    for bid, owner in sorted(by_id.items(), key=lambda x: x[1]["folio"]):
        row = {"folio": owner["folio"], "blind_id": bid, "role": owner["role"]}
        for f in FEATURES:
            va, vb = readers["A"][bid][f], readers["B"][bid][f]
            row[f + "_A"] = va
            row[f + "_B"] = vb
            row[f + "_CONSENSUS"] = va if va == vb else "DISAGREE"
        joined.append(row)
    by_folio = {r["folio"]: r for r in joined}
    strict = {p: by_folio[p]["BLUE_FRINGED_CUP_CONSENSUS"] for p in FOLIOS}
    target_values = [strict[p] for p in sorted(TARGETS)]
    control_values = [strict[p] for p in sorted(CONTROLS)]
    ref_values = [strict[p] for p in sorted(REFS)]
    uncertain = {"UNKNOWN", "DISAGREE"}
    if strict["f22r"] != "YES":
        decision = "RUBRIC_CALIBRATION_FAIL"
    elif any(v in uncertain for v in target_values + control_values + ref_values):
        decision = "CAPACITY_INDETERMINATE"
    elif target_values == ["YES", "YES"] and control_values.count("YES") <= 1 and ref_values == ["NO", "NO"]:
        decision = "CUP_DIFFERENTIAL_COMPATIBLE"
    elif target_values == ["YES", "YES"] and control_values.count("YES") >= 2:
        decision = "NONDISCRIMINATING_COMMON_CUP"
    elif target_values == ["YES", "NO"] or target_values == ["NO", "YES"]:
        decision = "PARTIAL_ONE_TARGET"
    elif target_values == ["NO", "NO"]:
        decision = "NO_TARGET_SUPPORT"
    else:
        decision = "OTHER_REGISTERED_CONTRADICTION"
    result = {
        "experiment": "GDT1091", "decision": decision, "strict_cup_by_folio": strict,
        "strict_target_yes": target_values.count("YES"),
        "strict_control_yes": control_values.count("YES"),
        "strict_schor_only_reference_yes": ref_values.count("YES"),
        "consensus_by_feature": {f: {p: by_folio[p][f + "_CONSENSUS"] for p in sorted(FOLIOS)}
                                 for f in FEATURES},
        "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (mapping_path, a_path, b_path, source_path)},
        "claim_ceiling": "Exploratory two-field image compatibility; no text-to-organ pointer, species, significance or translated word."
    }
    return joined, result


def main():
    joined, result = compute()
    with (ART / "JOINED.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(joined[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(joined)
    (ART / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
