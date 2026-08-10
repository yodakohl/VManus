#!/usr/bin/env python3
"""Fast deterministic concordance for the source-native structural edition."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
SOURCE = BASE / "results" / "source_native_structural_interlinear_v1.tsv"
SOURCE_SHA256 = "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af"
TAG_FIELDS = (
    "opening_feature_hits", "closing_feature_hits", "favored_transition_hits",
    "disfavored_transition_hits", "unresolved_transition_hits",
    "favored_path_hits", "longest_opening_path", "longest_path_anywhere",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_re(value: str | None, label: str) -> re.Pattern[str] | None:
    if value is None:
        return None
    try:
        return re.compile(value)
    except re.error as exc:
        raise SystemExit(f"invalid {label} regular expression: {exc}") from exc


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--page-regex")
    p.add_argument("--locus-regex")
    p.add_argument("--surface-regex", help="regex searched against each complete family surface")
    p.add_argument("--contains", help="literal internal family substring within one complete group")
    p.add_argument("--locus-sequence-regex", help="regex on space-separated complete family surfaces")
    p.add_argument("--member-regex", help="regex on any exact ZL/IT/RF STA member-code string")
    p.add_argument("--eva-regex", help="regex on any explicitly lossy ZL/IT/RF basic-EVA string")
    p.add_argument("--position", choices=("FIRST", "CORE", "LAST", "SINGLE"))
    p.add_argument("--scope", choices=("CONFIRMED_PROSE", "DIAGNOSTIC_NONPROSE"))
    p.add_argument("--kind", choices=("P", "L", "C", "R"))
    p.add_argument("--currier", choices=("A", "B", ""))
    p.add_argument("--section")
    p.add_argument("--first-last-label")
    p.add_argument("--edge-core-label")
    p.add_argument("--tag-regex", help="regex on validated feature/transition/path fields")
    p.add_argument("--boundary-regex", help="regex on left or right manual boundary profiles")
    p.add_argument("--max-loci", type=int, default=50)
    p.add_argument("--format", choices=("text", "json", "tsv"), default="text")
    p.add_argument("--count-only", action="store_true")
    return p


def load_rows() -> list[dict[str, str]]:
    if sha(SOURCE) != SOURCE_SHA256:
        raise SystemExit("frozen source-native structural interlinear drift")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 23281 or len({row["consensus_group_id"] for row in rows}) != len(rows):
        raise SystemExit("source-native structural row identity drift")
    return rows


def query(args: argparse.Namespace, rows: list[dict[str, str]]) -> dict:
    if args.max_loci < 0:
        raise SystemExit("--max-loci must be nonnegative")
    regex = {
        "page": compile_re(args.page_regex, "page"),
        "locus": compile_re(args.locus_regex, "locus"),
        "surface": compile_re(args.surface_regex, "surface"),
        "sequence": compile_re(args.locus_sequence_regex, "locus-sequence"),
        "member": compile_re(args.member_regex, "member"),
        "eva": compile_re(args.eva_regex, "eva"),
        "tag": compile_re(args.tag_regex, "tag"),
        "boundary": compile_re(args.boundary_regex, "boundary"),
    }
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_locus[row["locus"]].append(row)
    matched: list[dict] = []
    group_hits = 0
    for locus, locus_rows in by_locus.items():
        locus_rows.sort(key=lambda row: int(row["group_index"]))
        first = locus_rows[0]
        if regex["page"] and not regex["page"].search(first["page"]): continue
        if regex["locus"] and not regex["locus"].search(locus): continue
        if args.scope is not None and first["grammar_scope"] != args.scope: continue
        if args.kind is not None and first["kind"] != args.kind: continue
        if args.currier is not None and first["currier"] != args.currier: continue
        if args.section is not None and first["section"] != args.section: continue
        surfaces = [row["family_surface"] for row in locus_rows]
        sequence = " ".join(surfaces)
        sequence_indices: set[int] | None = None
        if regex["sequence"]:
            sequence_matches = [match for match in regex["sequence"].finditer(sequence) if match.end() > match.start()]
            if not sequence_matches: continue
            sequence_indices = set()
            offset = 0
            spans = []
            for index, surface in enumerate(surfaces, 1):
                spans.append((index, offset, offset + len(surface)))
                offset += len(surface) + 1
            for match in sequence_matches:
                sequence_indices.update(index for index, start, end in spans if start < match.end() and end > match.start())
        hit_indices: list[int] = []
        for row in locus_rows:
            tests = []
            if regex["surface"]: tests.append(bool(regex["surface"].search(row["family_surface"])))
            if args.contains is not None: tests.append(args.contains in row["family_surface"])
            if regex["member"]:
                tests.append(any(regex["member"].search(row[field]) for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")))
            if regex["eva"]:
                tests.append(any(regex["eva"].search(row[field]) for field in ("zl_basic_eva_lossy", "it_basic_eva_lossy", "rf_basic_eva_lossy")))
            if args.position is not None: tests.append(row["factual_position"] == args.position)
            if args.first_last_label is not None: tests.append(row["exact_first_last_label"] == args.first_last_label)
            if args.edge_core_label is not None: tests.append(row["exact_edge_core_label"] == args.edge_core_label)
            if regex["tag"]: tests.append(bool(regex["tag"].search(";".join(row[field] for field in TAG_FIELDS))))
            if regex["boundary"]:
                tests.append(bool(regex["boundary"].search(row["left_boundary_profile"]) or regex["boundary"].search(row["right_boundary_profile"])))
            index = int(row["group_index"])
            if (sequence_indices is None or index in sequence_indices) and (not tests or all(tests)):
                hit_indices.append(index)
        if not hit_indices: continue
        group_hits += len(hit_indices)
        matched.append({
            "locus": locus, "page": first["page"], "section": first["section"],
            "currier": first["currier"], "hand": first["hand"], "code": first["code"],
            "kind": first["kind"], "scope": first["grammar_scope"],
            "hit_group_indices": hit_indices, "family_sequence": sequence,
            "groups": [{key: row[key] for key in (
                "group_index", "factual_position", "family_surface", "zl_sta_codes",
                "it_sta_codes", "rf_sta_codes", "zl_basic_eva_lossy", "it_basic_eva_lossy",
                "rf_basic_eva_lossy", "left_boundary_profile", "right_boundary_profile",
                "exact_first_last_label", "exact_edge_core_label", *TAG_FIELDS,
            )} for row in locus_rows],
        })
    metadata = {
        "source_sha256": SOURCE_SHA256, "total_source_groups": len(rows),
        "total_source_loci": len(by_locus), "matching_loci": len(matched),
        "matching_groups": group_hits, "returned_loci": min(len(matched), args.max_loci),
        "truncated": len(matched) > args.max_loci,
        "claim_ceiling": "Concordance hits only; no word, morpheme, sound, POS, meaning, plaintext, language, cipher, or translation.",
    }
    return {"metadata": metadata, "matches": matched[:args.max_loci]}


def emit(result: dict, args: argparse.Namespace) -> None:
    meta, matches = result["metadata"], result["matches"]
    if args.count_only:
        print(json.dumps(meta, sort_keys=True, separators=(",", ":")))
        return
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.format == "tsv":
        print("locus\tpage\tsection\tcurrier\thand\tcode\tkind\tscope\thit_group_indices\tfamily_sequence")
        for item in matches:
            print("\t".join(str(item[key]) if key != "hit_group_indices" else ",".join(map(str, item[key])) for key in (
                "locus", "page", "section", "currier", "hand", "code", "kind", "scope", "hit_group_indices", "family_sequence"
            )))
        return
    print(f"matches: {meta['matching_loci']} loci / {meta['matching_groups']} groups; returned {meta['returned_loci']}" + (" (truncated)" if meta["truncated"] else ""))
    for item in matches:
        hit = set(item["hit_group_indices"])
        body = " · ".join(("*" if int(group["group_index"]) in hit else "") + f"{group['factual_position'][0]}:{group['family_surface']}" for group in item["groups"])
        print(f"{item['locus']} [{item['section']}/{item['currier'] or '-'}/{item['kind']}/{item['scope']}] {body}")
    print(meta["claim_ceiling"])


def main() -> None:
    args = parser().parse_args()
    emit(query(args, load_rows()), args)


if __name__ == "__main__":
    main()
