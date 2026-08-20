#!/usr/bin/env python3
"""Build the decoder-visible, record-local adversarial pair views.

This program reads blind observation files only.  It never opens oracle,
codebook, genealogy, design, or Voynich data.  Raw visible types are replaced
by a corpus-local injective fixed-width code; equality and recurrence are
therefore invariant while glyph-internal morphology is intentionally removed.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
from collections import Counter, defaultdict
from pathlib import Path

from world_api import OBS_FIELDS

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
MATCHES = EXP / "artifacts/gdt395_pair_matched_records.tsv"
ALPHABET = "bcdfghklmnpr"
CODE_WIDTH = 16
SENTINEL = "NONCOMPARABLE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_gzip_tsv(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_gzip_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, OBS_FIELDS, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)


def base_code(index: int) -> str:
    chars = []
    for _ in range(CODE_WIDTH):
        chars.append(ALPHABET[index % len(ALPHABET)])
        index //= len(ALPHABET)
    if index:
        raise RuntimeError("fixed pair-view alphabet exhausted")
    return "".join(reversed(chars))


def selected_records() -> dict[tuple[str, int], list[dict]]:
    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    with MATCHES.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            seed = int(row["corpus_seed"])
            for side in ("left", "right"):
                grouped[(row[f"{side}_world"], seed)].append({
                    "pair_id": row["pair_id"],
                    "pair_ordinal": int(row["pair_ordinal"]),
                    "record_id": row[f"{side}_record_id"],
                })
    return grouped


def canonical_rows(source: list[dict], choices: list[dict], type_map: dict[str, str]) -> list[dict]:
    by_record: dict[str, list[dict]] = defaultdict(list)
    for row in source:
        by_record[row["record_id"]].append(row)
    output = []
    for choice in sorted(choices, key=lambda row: row["pair_ordinal"]):
        raw = sorted(by_record[choice["record_id"]], key=lambda row: int(row["event_index"]))
        line_ids = []
        for row in raw:
            if row["line_id"] not in line_ids:
                line_ids.append(row["line_id"])
        line_rank = {value: index for index, value in enumerate(line_ids)}
        line_members: dict[str, list[int]] = defaultdict(list)
        for index, row in enumerate(raw):
            line_members[row["line_id"]].append(index)
        for index, row in enumerate(raw):
            line_positions = line_members[row["line_id"]]
            within_line = line_positions.index(index)
            if within_line == 0:
                line_bin = "B0"
            elif within_line == len(line_positions) - 1:
                line_bin = "B2"
            else:
                line_bin = "B1"
            record_bin = "B0" if index < len(raw) / 3 else ("B2" if index >= 2 * len(raw) / 3 else "B1")
            new = dict(row)
            new.update({
                "page_id": SENTINEL,
                "paragraph_id": SENTINEL,
                "record_id": f"{choice['pair_id']}::S{row['corpus_seed']}::R{choice['pair_ordinal']:02d}",
                "line_id": f"{choice['pair_id']}::S{row['corpus_seed']}::R{choice['pair_ordinal']:02d}::L{line_rank[row['line_id']]:02d}",
                "visible_group": type_map[row["visible_group"]],
                "separator_before": "RECORD" if index == 0 else row["separator_before"],
                "separator_after": "RECORD" if index == len(raw) - 1 else row["separator_after"],
                "register_id": SENTINEL,
                "hand_id": SENTINEL,
                "layout_role": SENTINEL,
                "line_position_bin": line_bin,
                "record_position_bin": record_bin,
                "group_index": index,
            })
            output.append(new)
    for index, row in enumerate(output):
        row["event_index"] = index
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-dir", type=Path, default=EXP / ".work/corpora")
    parser.add_argument("--output-dir", type=Path, default=EXP / ".work/pair_blind")
    args = parser.parse_args()
    selection = selected_records()
    available = {}
    raw_types: dict[str, set[str]] = defaultdict(set)
    for (world, seed), choices in sorted(selection.items()):
        path = args.corpus_dir / "blind" / world / f"seed_{seed:02d}.tsv.gz"
        if not path.is_file():
            continue
        rows = read_gzip_tsv(path)
        wanted = {choice["record_id"] for choice in choices}
        selected = [row for row in rows if row["record_id"] in wanted]
        available[(world, seed)] = (rows, choices, selected)
        raw_types[world].update(row["visible_group"] for row in selected)
    type_maps = {}
    for world, tokens in raw_types.items():
        capacity = len(ALPHABET) ** CODE_WIDTH
        mapping = {
            token: base_code(int(hashlib.sha256((world + "\x1f" + token).encode()).hexdigest(), 16) % capacity)
            for token in tokens
        }
        if len(set(mapping.values())) != len(mapping):
            raise AssertionError("pair surface map not injective")
        type_maps[world] = mapping
    manifest = []
    for (world, seed), (source, choices, selected) in sorted(available.items()):
        output = canonical_rows(source, choices, type_maps[world])
        raw_partition = {token: code for token, code in type_maps[world].items() if token in {r["visible_group"] for r in selected}}
        if len(raw_partition) != len(set(raw_partition.values())):
            raise AssertionError("equality partition changed")
        pair_id = choices[0]["pair_id"]
        path = args.output_dir / pair_id / world / f"seed_{seed:02d}.tsv.gz"
        write_gzip_tsv(path, output)
        manifest.append({
            "pair_id": pair_id,
            "world_id": world,
            "corpus_seed": seed,
            "events": len(output),
            "records": len(choices),
            "visible_types": len({r["visible_group"] for r in output}),
            "fixed_code_width": CODE_WIDTH,
            "page_paragraph_register_hand_layout": "NONCOMPARABLE_MASKED",
            "glyph_internal_properties": "NONCOMPARABLE_FIXED_WIDTH_INJECTIVE_RECODE",
            "observation_relpath": str(path.relative_to(args.output_dir)),
            "observation_sha256": sha(path),
        })
    manifest_path = args.output_dir / "pair_blind_manifest.tsv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "pair_id", "world_id", "corpus_seed", "events", "records", "visible_types",
        "fixed_code_width", "page_paragraph_register_hand_layout", "glyph_internal_properties",
        "observation_relpath", "observation_sha256",
    )
    with manifest_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    print({"views": len(manifest), "status": "PASS"})


if __name__ == "__main__":
    main()
