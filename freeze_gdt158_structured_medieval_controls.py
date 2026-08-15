#!/usr/bin/env python3
"""Freeze source identities and capacity before GDT158 residual scoring."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUG_SHA = "bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def xlsx_capacity(path: Path) -> dict[str, object]:
    assert sha(path) == AUG_SHA
    with zipfile.ZipFile(path) as archive:
        strings: list[str] = []
        for _, node in ET.iterparse(archive.open("xl/sharedStrings.xml"), events=("end",)):
            if node.tag == NS + "si":
                strings.append("".join(part.text or "" for part in node.iter(NS + "t")))
                node.clear()
        rows = groups = paren_rows = 0
        years: Counter[str] = Counter()
        parents: set[tuple[str, str]] = set()
        for _, node in ET.iterparse(archive.open("xl/worksheets/sheet1.xml"), events=("end",)):
            if node.tag != NS + "row":
                continue
            values: dict[str, str] = {}
            for cell in node.findall(NS + "c"):
                column = re.match(r"[A-Z]+", cell.get("r", ""))
                value_node = cell.find(NS + "v")
                value = "" if value_node is None else (value_node.text or "")
                if cell.get("t") == "s" and value:
                    value = strings[int(value)]
                if column:
                    values[column.group()] = value
            year = values.get("A", "")
            text = values.get("D", "").strip()
            if year.isdigit() and 1402 <= int(year) <= 1425 and text:
                rows += 1
                groups += len(text.split())
                paren_rows += int(bool(re.search(r"\([^)]*\)", text)))
                years[year] += 1
                parents.add((year, values.get("B", "")))
            node.clear()
    return {
        "entries": rows,
        "groups": groups,
        "represented_years": len(years),
        "year_counts": dict(sorted(years.items())),
        "year_plus_folio_parents": len(parents),
        "rows_with_parentheses": paren_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--augsburg", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "gdt158_source_freeze.json")
    args = parser.parse_args()
    blind = ROOT / "gdt155_blinded_diplomatic.tsv"
    expanded = ROOT / "gdt155_unblinded_lines.tsv"
    manifest = ROOT / "gdt158_structured_source_manifest.tsv"
    method = ROOT / "GDT158_STRUCTURED_MEDIEVAL_RESIDUAL_METHOD.md"
    audit = ROOT / "GDT158_STRUCTURED_CONTROL_SOURCE_AUDIT.md"
    blind_rows = read(blind)
    expanded_rows = read(expanded)
    assert len(blind_rows) == len(expanded_rows) == 48_347
    corpus_counts = Counter(row["corpus"] for row in blind_rows)
    record_counts = {corpus: len({row["record_id"] for row in blind_rows if row["corpus"] == corpus}) for corpus in corpus_counts}
    group_counts = {corpus: sum(int(row["surface_group_count"]) for row in blind_rows if row["corpus"] == corpus) for corpus in corpus_counts}
    result = {
        "schema": "GDT158_STRUCTURED_MEDIEVAL_SOURCE_FREEZE_V1",
        "status": "SOURCE_PANEL_FROZEN_BEFORE_RESIDUAL_SCORING",
        "date": "2026-08-15",
        "sources": {
            "AUGSBURG_ACCOUNTS_1402_1424": xlsx_capacity(args.augsburg),
            "NUREMBERG_LETTERBOOKS_1408_1423": {"lines": corpus_counts["NUREMBERG"], "records": record_counts["NUREMBERG"], "groups": group_counts["NUREMBERG"]},
            "STE1_TECHNICAL_RECIPES_1400_1425": {"lines": corpus_counts["STE1"], "records": record_counts["STE1"], "groups": group_counts["STE1"]},
        },
        "design": {
            "corpus_selection_before_scores": True,
            "nuremberg_channel_retuned": False,
            "boundary_null": "NONZERO_CYCLIC_ROTATION_OF_LINE_OR_ENTRY_LENGTHS_WITHIN_PARENT",
            "null_worlds": 4096,
            "powered_surface_sample_groups": 12000,
            "ste1_low_capacity": True,
        },
        "f84r": {"voynich_source_inputs": 0, "opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "inputs": {blind.name: sha(blind), expanded.name: sha(expanded), manifest.name: sha(manifest), "augsburg_workbook": sha(args.augsburg)},
        "documents": {method.name: sha(method), audit.name: sha(audit)},
        "implementation": {Path(__file__).name: sha(Path(__file__)), "fetch_gdt158_structured_control_sources.py": sha(ROOT / "fetch_gdt158_structured_control_sources.py")},
        "claim_ceiling": "External structured-medieval formal control only; no Voynich language, plaintext, semantic role, meaning, origin, or translation.",
    }
    result["result_content_sha256"] = csha(result)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["sources"], sort_keys=True))


if __name__ == "__main__":
    main()
