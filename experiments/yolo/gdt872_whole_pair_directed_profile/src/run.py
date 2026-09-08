#!/usr/bin/env python3
"""Descriptive GDT872 raw-group directed whole-pair profile."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

sys.dont_write_bytecode = True

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")

ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt872_whole_pair_directed_profile"
SRC = BASE / "src"
ARTIFACTS = BASE / "artifacts"
SPEC_PATH = SRC / "SPEC.json"
G807_PATH = ROOT / "experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/src/run.py"
ATLAS_PATH = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def write_tsv(path: Path, rows: list[Mapping[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

def load_g807() -> Any:
    spec = importlib.util.spec_from_file_location("gdt807_run_for_gdt872", G807_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import GDT807 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def selector_key(value: str) -> tuple[int, int, int, str]:
    import re
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", value)
    return (int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), value) if match else (10**9, 9, 9, value)

def guarded_atlas_query(spec: Mapping[str, Any], pages: list[str]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source = spec["atlas"]
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / source["path"]), "--selector", source["selector"]]
    for page in sorted(pages, key=selector_key):
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(source["columns"]), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded ATLAS query failed")
    stats = [json.loads(line[12:]) for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats) != 1:
        raise RuntimeError("ATLAS guard statistics missing or duplicated")
    rows = list(csv.DictReader(completed.stdout.splitlines(), delimiter="\t"))
    if any(str(row.get("page", "")).startswith("f84") for row in rows):
        raise RuntimeError("sealed selector materialized")
    return rows, stats[0]

def forbidden_separator(value: str) -> bool:
    return value == "UNCERTAIN_SMALL_SPACE" or value.startswith("DRAWING_")

def require_spec(spec: Mapping[str, Any]) -> None:
    if spec.get("experiment_id") != "GDT872":
        raise RuntimeError("SPEC experiment_id must be GDT872")
    if spec.get("sealed_data") not in ({"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, ["f84", "f84r"]) and spec.get("forbidden") != ["f84", "f84r"]:
        raise RuntimeError("SPEC must seal f84 and f84r")
    source = spec.get("atlas", {})
    if not {"path", "selector", "columns"} <= set(source):
        raise RuntimeError("SPEC ATLAS source contract is incomplete")
    if source["path"] != rel(ATLAS_PATH) or source["selector"] != "page":
        raise RuntimeError("SPEC must use source_separator_transcription.tsv with page selection")
    required = {"source_group_id", "edition", "page", "locus", "source_group_index", "source_group_count", "left_separator", "right_separator", "ivtff_group_raw", "clean_ascii_fragments", "clean_ascii_fragment_count"}
    if not required <= set(source["columns"]):
        raise RuntimeError("SPEC ATLAS columns omit required raw-group fields")
    if not spec.get("anchors") or not spec.get("responses"):
        raise RuntimeError("SPEC must declare anchors and response forms")

def declarations(spec: Mapping[str, Any]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    anchors: dict[str, dict[str, str]] = {}
    for item in spec["anchors"]:
        pair_id = str(item["pair_id"])
        if pair_id in anchors:
            raise RuntimeError(f"duplicate anchor pair: {pair_id}")
        for sign in ("CH", "SH"):
            surface = str(item[sign])
            if surface in anchors:
                raise RuntimeError(f"duplicate anchor surface: {surface}")
            anchors[surface] = {"pair_id": pair_id, "sign": sign}
    responses: dict[str, dict[str, str]] = {}
    response_pairs: dict[str, dict[str, str]] = {}
    for item in spec["responses"]:
        pair_id = str(item["pair_id"])
        if pair_id in response_pairs:
            raise RuntimeError(f"duplicate response pair: {pair_id}")
        response_pairs[pair_id] = {"CH": str(item["CH"]), "SH": str(item["SH"])}
        for sign in ("CH", "SH"):
            surface = str(item[sign])
            if surface in responses or surface in anchors:
                raise RuntimeError(f"anchor/response surface overlap: {surface}")
            responses[surface] = {"pair_id": pair_id, "sign": sign}
    return anchors, responses, response_pairs

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, default=ARTIFACTS)
    args = parser.parse_args()
    if not SPEC_PATH.is_file():
        raise RuntimeError(f"missing preregistered source contract: {SPEC_PATH}")
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    require_spec(spec)
    lock = json.loads((SRC / "PREREG_LOCK.json").read_text())
    for name, expected in lock.items():
        if sha256(ROOT / name) != expected:
            raise RuntimeError("preregistered byte drift: " + name)
    anchors, responses, pair_ids = declarations(spec)
    g807 = load_g807()
    lines, _paragraphs, paragraph_by_locus, line_by_locus, query_stats, _stability, _tokens = g807.load_corpus()
    atlas, atlas_stats = guarded_atlas_query(spec, sorted({line.page for line in lines}, key=selector_key))
    edition = str(spec.get("primary_edition", "ZL3b"))
    diagnostic_editions = list(spec.get("diagnostic_editions", [edition]))
    runtime = BASE / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    atlas_fields = list(spec["atlas"]["columns"])
    write_tsv(runtime / "ATLAS.tsv", atlas, atlas_fields)
    line_records = [{"page": line.page, "locus": line.locus, "line_number": line.number, "strict_paragraph_id": paragraph_by_locus[line.locus].paragraph_id if line.locus in paragraph_by_locus else "", "in_strict_paragraph": int(line.locus in paragraph_by_locus), "token_count": len(line.tokens), "eva_clean": " ".join(line.tokens)} for line in lines]
    write_json(runtime / "LINE_RECORDS.json", {"count": len(line_records), "records": line_records})
    known_keys = {(line.page, line.locus) for line in lines}
    by_edition_line: dict[tuple[str, tuple[str, str]], list[dict[str, str]]] = defaultdict(list)
    key_order: dict[tuple[str, str], int] = {}
    for row in atlas:
        key = (row["page"], row["locus"])
        key_order.setdefault(key, len(key_order))
        by_edition_line[(row["edition"], key)].append(row)
    for key in list(by_edition_line):
        by_edition_line[key].sort(key=lambda row: int(row["source_group_index"]))
    primary_lines: dict[tuple[str, str], list[dict[str, str]]] = {}
    diagnostic_ok: dict[tuple[str, str], bool] = {}
    diagnostic_line_count = 0
    diagnostic_disagreement_count = 0
    for key in sorted({k[1] for k in by_edition_line}, key=lambda value: key_order[value]):
        sequences = {}
        for ed in diagnostic_editions:
            rows = by_edition_line.get((ed, key), [])
            if not rows:
                continue
            indices = [int(row["source_group_index"]) for row in rows]
            if indices != list(range(1, len(rows) + 1)) or {int(row["source_group_count"]) for row in rows} != {len(rows)}:
                raise RuntimeError(f"non-contiguous ATLAS source groups: {ed}:{key}")
            sequences[ed] = [row["ivtff_group_raw"] for row in rows]
        if len(sequences) == len(diagnostic_editions):
            diagnostic_line_count += 1
            diagnostic_ok[key] = len({tuple(sequence) for sequence in sequences.values()}) == 1
            if not diagnostic_ok[key]:
                diagnostic_disagreement_count += 1
        rows = by_edition_line.get((edition, key), [])
        if not rows:
            continue
        if key in known_keys:
            line = line_by_locus[key[1]]
            fragments = []
            for row in rows:
                parts = row["clean_ascii_fragments"].split() if row["clean_ascii_fragments"] else []
                if len(parts) != int(row["clean_ascii_fragment_count"]):
                    raise RuntimeError(f"fragment count mismatch: {row['source_group_id']}")
                fragments.extend(parts)
            if fragments != list(line.tokens):
                raise RuntimeError(f"clean fragment sequence mismatch: {key}")
        primary_lines[key] = rows
    if not known_keys <= set(primary_lines):
        raise RuntimeError("missing primary raw line in GDT807 population")
    flat_by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for key, rows in primary_lines.items():
        paragraph = paragraph_by_locus.get(key[1])
        for row in rows:
            flat_by_page[key[0]].append({**row, "in_gdt807": key in known_keys, "diagnostic_ok": diagnostic_ok.get(key, False), "strict": paragraph is not None, "strict_paragraph_id": paragraph.paragraph_id if paragraph else "", "atlas_line_order": int(row["source_row_index"])})
    for page, rows in flat_by_page.items():
        rows.sort(key=lambda row: (row["atlas_line_order"], int(row["source_group_index"])))
        for index, row in enumerate(rows):
            row["page_group_index"] = index

    opportunities: list[dict[str, Any]] = []
    hits: list[dict[str, Any]] = []
    anchor_counts: Counter[str] = Counter()
    for page, groups in flat_by_page.items():
        positions = {row["page_group_index"]: row for row in groups}
        for anchor_index, anchor in enumerate(groups):
            surface = anchor["ivtff_group_raw"]
            if surface not in anchors or not anchor["in_gdt807"] or not anchor["strict"] or int(anchor["clean_ascii_fragment_count"]) != 1 or anchor["clean_ascii_fragments"] != surface:
                continue
            anchor_counts[surface] += 1
            for direction, sign in (("forward", 1), ("backward", -1)):
                for lag in range(1, 9):
                    target_index = anchor_index + sign * lag
                    target = positions.get(target_index)
                    if target is None or not target["in_gdt807"] or not target["strict"]:
                        continue
                    between = groups[min(anchor_index, target_index) + 1:max(anchor_index, target_index)]
                    traversed = [anchor["right_separator"], target["left_separator"]] if sign > 0 else [anchor["left_separator"], target["right_separator"]]
                    traversed.extend(value for r in between for value in (r["left_separator"], r["right_separator"]))
                    if any(not r["in_gdt807"] or not r["strict"] for r in between) or any(forbidden_separator(value) for value in traversed):
                        continue
                    matching = responses.get(target["ivtff_group_raw"]) if int(target["clean_ascii_fragment_count"]) == 1 and target["clean_ascii_fragments"] == target["ivtff_group_raw"] else None
                    row = {"page": page, "physical_folio": re.match(r"^(f\d+)", page).group(1) if re.match(r"^(f\d+)", page) else page, "anchor_locus": anchor["locus"], "response_locus": target["locus"], "anchor_surface": surface, "response_surface": target["ivtff_group_raw"], "anchor_pair_id": anchors[surface]["pair_id"], "anchor_sign": anchors[surface]["sign"], "response_pair_id": matching["pair_id"] if matching else "NONE", "response_sign": matching["sign"] if matching else "", "direction": direction, "lag": lag, "lag_band": "NEAR" if lag <= 2 else "DISTAL", "paragraph_relation": "within_para" if anchor["strict_paragraph_id"] == target["strict_paragraph_id"] else "cross_para", "response_hit": int(matching is not None), "agreement": int(matching is not None and matching["sign"] == anchors[surface]["sign"]), "disagreement": int(matching is not None and matching["sign"] != anchors[surface]["sign"]), "anchor_page_group_index": anchor_index, "response_page_group_index": target_index}
                    row["view"] = "PRIMARY"
                    opportunities.append(row)
                    if row["response_hit"]:
                        hits.append(row)
                    if all(r["diagnostic_ok"] for r in groups[min(anchor_index,target_index):max(anchor_index,target_index)+1]):
                        diagnostic_row = dict(row, view="DIAGNOSTIC")
                        opportunities.append(diagnostic_row)
                        if diagnostic_row["response_hit"]:
                            hits.append(diagnostic_row)
    aggregates: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    anchor_cells: dict[tuple[tuple[str, ...], tuple[str, int]], Counter[str]] = defaultdict(Counter)
    for row in opportunities:
        for response_pair_id, response_sides in pair_ids.items():
            for response_sign, response_surface in response_sides.items():
                hit = int(row["response_hit"] and row["response_surface"] == response_surface)
                key = (row["view"], row["physical_folio"], row["anchor_pair_id"], row["anchor_sign"], response_pair_id, response_sign, row["direction"], row["lag_band"], row["paragraph_relation"])
                aggregates[key]["opportunities"] += 1
                aggregates[key]["response_hits"] += hit
                aggregates[key]["agreement"] += int(hit and response_sign == row["anchor_sign"])
                aggregates[key]["disagreement"] += int(hit and response_sign != row["anchor_sign"])
                anchor_cells[(key, (row["page"], row["anchor_page_group_index"]))]["opportunities"] += 1
                anchor_cells[(key, (row["page"], row["anchor_page_group_index"]))]["hits"] += hit
    aggregate_rows = []
    fields = ["view", "physical_folio", "anchor_pair_id", "anchor_sign", "response_pair_id", "response_sign", "direction", "lag_band", "paragraph_relation"]
    for key, counts in sorted(aggregates.items()):
        per_anchor = [c for (cell_key, _anchor), c in anchor_cells.items() if cell_key == key and c["opportunities"]]
        macro_rate = sum(c["hits"] / c["opportunities"] for c in per_anchor) / len(per_anchor) if per_anchor else None
        conditional = counts["agreement"] / (counts["agreement"] + counts["disagreement"]) if counts["agreement"] + counts["disagreement"] else None
        aggregate_rows.append(dict(zip(fields, key), opportunities=counts["opportunities"], response_hits=counts["response_hits"], agreement=counts["agreement"], disagreement=counts["disagreement"], macro_anchor_rate="NA" if macro_rate is None else f"{macro_rate:.12g}", conditional_concordance="NA" if conditional is None else f"{conditional:.12g}"))
    out = args.artifacts
    hit_fields = ["view", "page", "physical_folio", "anchor_locus", "response_locus", "anchor_surface", "response_surface", "anchor_pair_id", "anchor_sign", "response_pair_id", "response_sign", "direction", "lag", "lag_band", "paragraph_relation", "response_hit", "anchor_page_group_index", "response_page_group_index"]
    write_tsv(out / "GDT872_DIRECTED_HITS.tsv", hits, hit_fields)
    write_tsv(out / "GDT872_OPPORTUNITY_AGGREGATES.tsv", aggregate_rows, fields + ["opportunities", "response_hits", "agreement", "disagreement", "macro_anchor_rate", "conditional_concordance"])
    write_json(runtime / "OPPORTUNITIES.json", {"count": len(opportunities), "records": opportunities})
    write_json(out / "GDT872_QUERY_RECEIPTS.json", {"gdt807_guarded_queries": query_stats, "atlas_guarded_query": atlas_stats, "atlas_source": {"path": rel(ATLAS_PATH), "selector": "page", "columns": spec["atlas"]["columns"], "forbidden_prefixes": ["f84", "f84r"]}, "reader": rel(G807_PATH), "runtime_projections": {"atlas_tsv": {"path": rel(runtime / "ATLAS.tsv"), "sha256": sha256(runtime / "ATLAS.tsv")}, "line_records_json": {"path": rel(runtime / "LINE_RECORDS.json"), "sha256": sha256(runtime / "LINE_RECORDS.json")}, "opportunities_json": {"path": rel(runtime / "OPPORTUNITIES.json"), "sha256": sha256(runtime / "OPPORTUNITIES.json")}}})
    write_json(out / "RESULT.json", {"status": "COMPLETE_DESCRIPTIVE_DIRECTED_PROFILE", "claim_ceiling": "Raw-group directed opportunities and response hits only; no p-values, semantic winner, or meaning claim.", "atlas_edition": edition, "anchor_surface_count": len(anchors), "declared_response_pair_count": len(pair_ids), "anchor_occurrences": dict(sorted(anchor_counts.items())), "opportunity_count": sum(r["view"]=="PRIMARY" for r in opportunities), "response_hit_count": sum(r["view"]=="PRIMARY" for r in hits), "diagnostic_opportunity_count": sum(r["view"]=="DIAGNOSTIC" for r in opportunities), "diagnostic_response_hit_count": sum(r["view"]=="DIAGNOSTIC" for r in hits), "diagnostic_all_three_raw_line_count": diagnostic_line_count, "diagnostic_all_three_disagreement_count": diagnostic_disagreement_count, "diagnostic_disagreement_policy": "exclude opportunities traversing a non-identical diagnostic line; do not abort primary corpus", "atlas_loci_outside_gdt807": sum(1 for key in primary_lines if key not in known_keys), "macroanchor_rate": {"definition": "unweighted mean of per-anchor hit/opportunity rates among anchors with opportunities, within each physical-folio aggregate cell", "aggregate_cells": len(aggregate_rows)}, "query_stats": {"gdt807": query_stats, "atlas": atlas_stats}, "source_hashes": {"atlas": sha256(ATLAS_PATH), "gdt807_runner": sha256(G807_PATH)}})
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
