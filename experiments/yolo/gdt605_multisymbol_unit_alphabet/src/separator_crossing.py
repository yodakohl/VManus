#!/usr/bin/env python3
"""Measure which source separator classes are crossed by train-only BPE units.

This diagnostic never opens the mixed transcription directly.  It consumes the
already guarded GDT605 row export, whose selector was materialised through
``vmanus-exp query-tsv`` with the GDT327 page allow-list and an f84 prefix ban.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path


EXPECTED_GUARDED_SHA256 = (
    "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9"
)
SUBSTITUTIONS = (
    ("cth", "T"), ("ckh", "K"), ("cph", "P"), ("cfh", "F"),
    ("ch", "C"), ("sh", "S"), ("iin", "N"), ("in", "I"),
    ("ee", "E"),
)
SEPARATOR_MARKS = {".": "certain", ",": "uncertain", "§": "drawing", "¶": "drawing"}
SEPARATOR_PRIORITY = {"certain": 0, "uncertain": 1, "drawing": 2}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collapse(token: str) -> str:
    token = token.lower().strip()
    for old, new in SUBSTITUTIONS:
        token = token.replace(old, new)
    return token


def clean_source_line(raw: str) -> tuple[list[str], list[str]]:
    """Return raw-EVA tokens and separator classes without guessing @ cuts.

    ``<->`` and ``<~>`` are retained as drawing interruptions.  Editorial
    comments, alternate readings, uncertainty marks and location markers are
    treated exactly as the cleaner does, then the result must agree token for
    token with the guarded ``eva_clean`` field before it is scored.
    """
    value = raw.replace("<->", "§").replace("<~>", "¶")
    value = re.sub(r"<[^>]*>", "", value)
    value = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", value)
    value = re.sub(r"\{[^}]*\}", "", value)
    value = re.sub(r"@\d+;", "", value)
    value = value.replace("'", "").replace("?", "").strip("-= ")

    tokens: list[str] = []
    separators: list[str] = []
    current: list[str] = []
    pending: list[str] = []

    def emit() -> None:
        nonlocal current, pending
        token = "".join(current).strip().lower()
        if not token:
            current = []
            return
        if tokens:
            if not pending:
                raise ValueError("retained tokens without a source separator")
            separators.append(max(pending, key=SEPARATOR_PRIORITY.__getitem__))
        tokens.append(token)
        current = []
        pending = []

    for character in value:
        separator = SEPARATOR_MARKS.get(character)
        if separator is None:
            current.append(character)
        else:
            emit()
            pending.append(separator)
    emit()
    return tokens, separators


def learn_bpe(lines: list[str], merge_count: int):
    frequency = collections.Counter(lines)
    segmentations = {line: tuple(line) for line in frequency}
    rules = []
    for _ in range(merge_count):
        pairs = collections.Counter()
        for line, units in segmentations.items():
            weight = frequency[line]
            for pair in zip(units, units[1:]):
                pairs[pair] += weight
        if not pairs:
            break
        (left, right), count = max(pairs.items(), key=lambda item: (item[1], item[0]))
        if count < 2:
            break
        merged = left + right
        rules.append((left, right, merged, count))
        for line, units in list(segmentations.items()):
            output = []
            index = 0
            while index < len(units):
                if index + 1 < len(units) and units[index:index + 2] == (left, right):
                    output.append(merged)
                    index += 2
                else:
                    output.append(units[index])
                    index += 1
            segmentations[line] = tuple(output)
    return rules, segmentations


def apply_bpe(text: str, rules) -> tuple[str, ...]:
    units = tuple(text)
    for left, right, merged, _count in rules:
        output = []
        index = 0
        while index < len(units):
            if index + 1 < len(units) and units[index:index + 2] == (left, right):
                output.append(merged)
                index += 2
            else:
                output.append(units[index])
                index += 1
        units = tuple(output)
    return units


def unit_boundaries(units: tuple[str, ...]) -> set[int]:
    position = 0
    boundaries = set()
    for unit in units[:-1]:
        position += len(unit)
        boundaries.add(position)
    return boundaries


def source_boundaries(tokens: list[str], classes: list[str]):
    position = 0
    output = []
    for token, separator in zip(tokens[:-1], classes):
        position += len(collapse(token))
        output.append((position, separator))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guarded-rows", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--merges", type=int, default=64)
    args = parser.parse_args()
    if sha256_path(args.guarded_rows) != EXPECTED_GUARDED_SHA256:
        raise SystemExit("guarded row hash changed")

    with args.guarded_rows.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["page"].lower().startswith("f84") for row in rows):
        raise SystemExit("forbidden selector present")

    train_lines = [
        "".join(collapse(token) for token in row["eva_clean"].split())
        for row in rows if row["split"] == "train"
    ]
    rules, train_segmentations = learn_bpe(train_lines, args.merges)

    counts = {
        split: {
            name: {"crossed": 0, "retained": 0, "total": 0}
            for name in ("certain", "uncertain", "drawing")
        }
        for split in ("train", "held", "all")
    }
    folio_counts: dict[str, dict[str, dict[str, int]]] = {}
    aligned_rows = 0
    unresolved = []
    crossed_examples = {name: collections.Counter() for name in ("certain", "uncertain", "drawing")}
    for row in rows:
        raw_tokens, classes = clean_source_line(row["ivtff_raw"])
        clean_tokens = row["eva_clean"].split()
        if raw_tokens != clean_tokens or len(classes) != max(0, len(clean_tokens) - 1):
            unresolved.append(row["locus"])
            continue
        aligned_rows += 1
        text = "".join(collapse(token) for token in clean_tokens)
        units = (
            train_segmentations[text]
            if row["split"] == "train" and text in train_segmentations
            else apply_bpe(text, rules)
        )
        learned = unit_boundaries(units)
        by_position = source_boundaries(clean_tokens, classes)
        for index, (position, separator) in enumerate(by_position):
            crossed = position not in learned
            for split in (row["split"], "all"):
                counts[split][separator]["total"] += 1
                counts[split][separator]["crossed" if crossed else "retained"] += 1
            folio = row["physical_folio"]
            folio_cell = folio_counts.setdefault(
                folio,
                {
                    name: {"crossed": 0, "total": 0}
                    for name in ("certain", "uncertain", "drawing")
                },
            )[separator]
            folio_cell["total"] += 1
            folio_cell["crossed"] += int(crossed)
            if crossed:
                left = clean_tokens[index]
                right = clean_tokens[index + 1]
                crossed_examples[separator][f"{left}|{right}"] += 1

    for split in counts.values():
        for cell in split.values():
            cell["crossing_fraction"] = cell["crossed"] / cell["total"] if cell["total"] else None

    folio_rows = []
    for folio, cells in sorted(folio_counts.items()):
        record = {
            "physical_folio": folio,
            "split": next(row["split"] for row in rows if row["physical_folio"] == folio),
        }
        for name, cell in cells.items():
            record[f"{name}_crossed"] = cell["crossed"]
            record[f"{name}_total"] = cell["total"]
            record[f"{name}_fraction"] = (
                cell["crossed"] / cell["total"] if cell["total"] else None
            )
        folio_rows.append(record)

    held_comparable = [
        row for row in folio_rows
        if row["split"] == "held"
        and row["certain_total"]
        and row["uncertain_total"]
    ]
    held_folio_sign = {
        "comparable": len(held_comparable),
        "uncertain_above_certain": sum(
            row["uncertain_fraction"] > row["certain_fraction"]
            for row in held_comparable
        ),
        "uncertain_equal_certain": sum(
            row["uncertain_fraction"] == row["certain_fraction"]
            for row in held_comparable
        ),
        "uncertain_below_certain": sum(
            row["uncertain_fraction"] < row["certain_fraction"]
            for row in held_comparable
        ),
    }
    held_certain = counts["held"]["certain"]
    held_uncertain = counts["held"]["uncertain"]
    held_crossing_ratio = (
        held_uncertain["crossing_fraction"] / held_certain["crossing_fraction"]
    )
    held_crossing_odds_ratio = (
        held_uncertain["crossed"] * held_certain["retained"]
        / (held_uncertain["retained"] * held_certain["crossed"])
    )

    result = {
        "schema": "gdt605-separator-crossing-v1",
        "guarded_rows_sha256": EXPECTED_GUARDED_SHA256,
        "rows": len(rows),
        "aligned_rows": aligned_rows,
        "unresolved_rows": len(unresolved),
        "unresolved_loci": unresolved,
        "configuration": {
            "merges": args.merges,
            "composites": SUBSTITUTIONS,
            "training": "68 physical folios only",
        },
        "rules": [
            {"left": left, "right": right, "merged": merged, "train_count": count}
            for left, right, merged, count in rules
        ],
        "counts": counts,
        "held_summary": {
            "uncertain_to_certain_crossing_ratio": held_crossing_ratio,
            "uncertain_to_certain_odds_ratio": held_crossing_odds_ratio,
            "folio_sign": held_folio_sign,
        },
        "physical_folios": folio_rows,
        "top_crossed_examples": {
            name: counter.most_common(25) for name, counter in crossed_examples.items()
        },
        "claim_ceiling": (
            "Learned collapsed-glyph units crossing source separator classes only; "
            "no word boundary, plaintext, language, lexeme, sound or meaning assignment."
        ),
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "aligned_rows": aligned_rows,
        "unresolved_rows": len(unresolved),
        "counts": counts,
        "output_sha256": sha256_path(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
