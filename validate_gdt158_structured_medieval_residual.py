#!/usr/bin/env python3
"""Independent source/output/accounting validator for GDT158."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt158_result.json"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
AUG_SHA = "bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1"
WORLDS = 4096
METRICS = ("line_open_edge_js", "line_close_edge_js", "line_reset_char3_contrast", "b3_like_closure_log2_lift")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def xlsx_counts(path: Path) -> tuple[int, int, int, int]:
    assert sha(path) == AUG_SHA
    entries = whitespace_groups = analysis_groups = 0
    parents: set[tuple[str, str]] = set()
    with zipfile.ZipFile(path) as archive:
        strings: list[str] = []
        for _, node in ET.iterparse(archive.open("xl/sharedStrings.xml"), events=("end",)):
            if node.tag == NS + "si":
                strings.append("".join(part.text or "" for part in node.iter(NS + "t")))
                node.clear()
        for _, node in ET.iterparse(archive.open("xl/worksheets/sheet1.xml"), events=("end",)):
            if node.tag != NS + "row":
                continue
            values: dict[str, str] = {}
            for cell in node.findall(NS + "c"):
                match = re.match(r"[A-Z]+", cell.get("r", "")); value_node = cell.find(NS + "v")
                value = "" if value_node is None else (value_node.text or "")
                if cell.get("t") == "s" and value:
                    value = strings[int(value)]
                if match:
                    values[match.group()] = value
            year, text = values.get("A", ""), values.get("D", "").strip()
            if year.isdigit() and 1402 <= int(year) <= 1425 and text:
                entries += 1; whitespace_groups += len(text.split()); parents.add((year, values.get("B", "")))
                analysis_groups += sum(bool("".join(ch for ch in part.lower() if ch.isalnum())) for part in text.split())
            node.clear()
    return entries, whitespace_groups, analysis_groups, len(parents)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--augsburg", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "gdt158_validation.json")
    args = parser.parse_args()
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, state: bool) -> None:
        checks.append({"check": name, "pass": bool(state)})

    check("schema", result["schema"] == "GDT158_STRUCTURED_MEDIEVAL_RESIDUAL_RESULT_V1")
    check("status", result["status"] == "DOCUMENT_STRUCTURE_GENERATES_PARTIAL_RESIDUAL_ARCHITECTURE")
    entries, whitespace, analysis, parents = xlsx_counts(args.augsburg)
    check("augsburg_source_capacity", (entries, whitespace, analysis, parents) == (22071, 281557, 281234, 1817))
    check("augsburg_result_capacity", result["counts"]["augsburg_entries"] == entries and result["counts"]["augsburg_groups"] == analysis)
    blind = read(ROOT / "gdt155_blinded_diplomatic.tsv"); expanded = read(ROOT / "gdt155_unblinded_lines.tsv")
    check("external_line_join", len(blind) == len(expanded) == 48347 and [r["line_id"] for r in blind] == [r["line_id"] for r in expanded])
    check("nuremberg_ste1_counts", sum(r["corpus"] == "NUREMBERG" for r in blind) == 48337 and sum(r["corpus"] == "STE1" for r in blind) == 10)

    for name, digest in result["inputs"].items():
        check("input_hash_" + name, sha(ROOT / name) == digest)
    check("external_hash_augsburg", sha(args.augsburg) == result["external_inputs"]["augsburg_workbook_sha256"] == AUG_SHA)
    for name, digest in result["documents"].items():
        check("document_hash_" + name, sha(ROOT / name) == digest)
    for name, digest in result["implementation"].items():
        check("implementation_hash_" + name, sha(ROOT / name) == digest)
    for name, digest in result["outputs"].items():
        check("output_hash_" + name, sha(ROOT / name) == digest)

    fps = read(ROOT / "gdt158_structural_fingerprints.tsv")
    check("fingerprint_rows", len(fps) == 4 and {r["corpus_id"] for r in fps} == {"AUGSBURG_ACCOUNTS_ORIGINAL", "NUREMBERG_EXPANDED_PLAINTEXT", "NUREMBERG_REAL_DIPLOMATIC", "VOYNICH_MATCHED"})
    by_fp = {r["corpus_id"]: r for r in fps}
    for metric, values in result["surface_algebra"].items():
        check("surface_" + metric, abs(float(by_fp["AUGSBURG_ACCOUNTS_ORIGINAL"][metric]) - values["augsburg"]) < 1e-12 and abs(float(by_fp["NUREMBERG_REAL_DIPLOMATIC"][metric]) - values["nuremberg_real"]) < 1e-12 and abs(float(by_fp["VOYNICH_MATCHED"][metric]) - values["voynich"]) < 1e-12)

    layouts = read(ROOT / "gdt158_layout_effects.tsv")
    check("layout_rows", len(layouts) == 5 and sum(r["capacity_state"] == "POWERED_BOUNDARY_ROTATION" for r in layouts) == 3)
    nulls = read(ROOT / "gdt158_null_results.tsv")
    check("null_rows", len(nulls) == 3 * WORLDS * len(METRICS))
    by_null: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0.0] * WORLDS)
    for row in nulls:
        by_null[(row["corpus_view"], row["metric"])][int(row["world"])] = float(row["value"])
    null_z: dict[tuple[str, str], list[float]] = {}
    observed_z: dict[tuple[str, str], float] = {}
    layout_map = {r["corpus_view"]: r for r in layouts}
    for row in layouts:
        if row["capacity_state"] != "POWERED_BOUNDARY_ROTATION":
            continue
        for metric in METRICS:
            values = by_null[(row["corpus_view"], metric)]; mean = statistics.mean(values); sd = statistics.pstdev(values)
            local_p = (1 + sum(value >= float(row[metric]) for value in values)) / (WORLDS + 1)
            check("null_mean_" + row["corpus_view"] + metric, abs(mean - float(row[metric + "__null_mean"])) < 1e-12)
            check("local_p_" + row["corpus_view"] + metric, abs(local_p - float(row[metric + "__local_p_greater"])) < 1e-12)
            z = (float(row[metric]) - mean) / max(sd, 1e-12); observed_z[(row["corpus_view"], metric)] = z
            null_z[(row["corpus_view"], metric)] = [(value - mean) / max(sd, 1e-12) for value in values]
    max_world = [max(values[world] for values in null_z.values()) for world in range(WORLDS)]
    strong: dict[str, int] = {}
    for row in layouts:
        if row["capacity_state"] != "POWERED_BOUNDARY_ROTATION":
            continue
        count = 0
        for metric in METRICS:
            z = observed_z[(row["corpus_view"], metric)]; adjusted = (1 + sum(value >= z for value in max_world)) / (WORLDS + 1)
            check("maxT_" + row["corpus_view"] + metric, abs(adjusted - float(row[metric + "__search_adjusted_p"])) < 1e-12)
            count += adjusted <= .05 and float(row[metric]) > float(row[metric + "__null_mean"])
        strong[row["corpus_view"]] = count
    check("strong_counts", strong == result["boundary_metrics_above_family_maxT_p_05"])
    check("decision_arithmetic", result["augsburg_residual_components"] == {"boundary_components_maxT_05": 4, "descriptive_surface_algebra_half_target_or_sign_components": 0, "components_total": 7})

    closure = read(ROOT / "gdt158_closure_folds.tsv")
    check("closure_fold_rows", len(closure) == 30)
    check("closure_fold_counts", Counter(r["corpus_view"] for r in closure) == {"AUGSBURG_ACCOUNTS:ORIGINAL_ENTRY": 18, "NUREMBERG_LETTERBOOKS:REAL_DIPLOMATIC": 4, "NUREMBERG_LETTERBOOKS:EXPANDED": 4, "STE1_RECIPES:REAL_DIPLOMATIC": 2, "STE1_RECIPES:EXPANDED": 2})
    body = dict(result); stored = body.pop("result_content_sha256")
    check("content_hash", csha(body) == stored)
    check("f84r_sealed", not any(result["f84r"].values()))
    check("no_channel_retune", json.loads((ROOT / "gdt158_source_freeze.json").read_text())["design"]["nuremberg_channel_retuned"] is False)
    passed = sum(row["pass"] for row in checks)
    validation = {
        "schema": "GDT158_STRUCTURED_MEDIEVAL_RESIDUAL_VALIDATION_V1",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent source-capacity, hashes, null summaries, maxT family, decision arithmetic, and seal reconstruction; GDT003 internals inherited from its frozen validator.",
    }
    args.output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{validation['status']} {passed}/{len(checks)}")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
