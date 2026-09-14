"""Produce a deterministic, source-bound exact qoteedy/qokeedy occurrence audit."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PACKET = "research_registry/work_batches/luna_pilot_20260914/PACKET.json"
FORMS = ("qoteedy", "qokeedy")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.luna_batch import load_packet


def _exposed_input(data: dict[str, Any]) -> tuple[str, dict[str, str]]:
    rows = [row for path, row in data["inputs"].items()
            if PurePosixPath(path).name == "EXPOSED_PARAGRAPHS.json"]
    if len(rows) != 1:
        raise ValueError("packet must bind exactly one EXPOSED_PARAGRAPHS.json")
    return rows[0]["path"], rows[0]


def _read_exposed(root: Path, path: str) -> dict[str, Any]:
    try:
        document = json.loads((root / Path(*PurePosixPath(path).parts)).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("bound EXPOSED_PARAGRAPHS.json is not valid JSON") from exc
    if not isinstance(document, dict) or not isinstance(document.get("paragraphs"), list):
        raise ValueError("exposed input must contain a paragraphs list")
    if len(document["paragraphs"]) != 6:
        raise ValueError("expected exactly six exposed paragraphs")
    return document


def audit(root: Path = ROOT, packet_arg: str = PACKET) -> dict[str, Any]:
    packet, packet_display = load_packet(packet_arg, root=root)
    exposed_path, exposed_input = _exposed_input(packet)
    source = _read_exposed(root, exposed_path)
    occurrences: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    paragraph_ids: list[str] = []
    editions: set[str] = set()
    pages: set[str] = set()
    counts: dict[tuple[str, str], dict[str, int]] = {}

    for paragraph_number, paragraph in enumerate(source["paragraphs"], 1):
        if not isinstance(paragraph, dict):
            raise ValueError("paragraph must be an object")
        edition, page, paragraph_id = (paragraph.get("edition"), paragraph.get("page"), paragraph.get("id"))
        if not all(isinstance(value, str) and value for value in (edition, page, paragraph_id)):
            raise ValueError("paragraph metadata is incomplete")
        paragraph_ids.append(paragraph_id)
        editions.add(edition)
        pages.add(page)
        key = (edition, page)
        counts.setdefault(key, {form: 0 for form in FORMS})
        lines = paragraph.get("lines")
        if not isinstance(lines, list):
            raise ValueError("paragraph lines must be a list")
        for line in lines:
            if not isinstance(line, dict) or not isinstance(line.get("locus"), str):
                raise ValueError("line metadata is incomplete")
            words, source_ids = line.get("words"), line.get("source_ids")
            if not isinstance(words, list) or not isinstance(source_ids, list) or len(words) != len(source_ids):
                raise ValueError("line words and source_ids must be aligned lists")
            positions = {form: [] for form in FORMS}
            for index, word in enumerate(words):
                if word not in FORMS:
                    continue
                source_id = source_ids[index]
                if not isinstance(source_id, str) or not source_id:
                    raise ValueError("exact occurrence has no source_id")
                positions[word].append(index)
                counts[key][word] += 1
                occurrences.append({
                    "edition": edition,
                    "page": page,
                    "paragraph": paragraph_id,
                    "locus": line["locus"],
                    "source_id": source_id,
                    "index": index,
                    "form": word,
                })
            # Retain exact per-occurrence ordering, but emit one row per
            # cooccurrence line without inferring adjacency.
            if positions["qoteedy"] and positions["qokeedy"]:
                pair_orders = [
                    ("qoteedy_before_qokeedy" if qoteedy_index < qokeedy_index
                     else "qokeedy_before_qoteedy")
                    for qoteedy_index in positions["qoteedy"]
                    for qokeedy_index in positions["qokeedy"]
                ]
                pairs.append({
                    "edition": edition,
                    "page": page,
                    "paragraph": paragraph_id,
                    "locus": line["locus"],
                    "qoteedy_indices": positions["qoteedy"],
                    "qokeedy_indices": positions["qokeedy"],
                    "order": pair_orders[0] if len(set(pair_orders)) == 1 else "mixed",
                })

    count_rows = [
        {"edition": edition, "page": page, **counts.get((edition, page), {form: 0 for form in FORMS})}
        for edition in sorted(editions)
        for page in sorted(pages)
    ]
    return {
        "audit": "exact_form_occurrence_audit",
        "purpose": "Check whether the exact qoteedy/qokeedy pair has second-page support.",
        "claim_ceiling": "Factual occurrence and same-line order inventory only; no semantic or statistical outcome.",
        "packet": packet_display,
        "bound_input": {"path": exposed_path, "sha256": exposed_input["sha256"]},
        "paragraph_count": len(paragraph_ids),
        "paragraphs": paragraph_ids,
        "forms": list(FORMS),
        "literal_difference": {
            "forms": list(FORMS),
            "position_one_indexed": 3,
            "qoteedy_character": "t",
            "qokeedy_character": "k",
        },
        "occurrence_index_base": 0,
        "occurrences": occurrences,
        "same_line_pairs": pairs,
        "counts_by_edition_page": count_rows,
        "registered_order_test": {
            "status": "NOT_RUN",
            "reason": "P01 near-adjacent range is undefined; no registered order test was run.",
        },
        "method_limits": [
            "Exact literal equality only; no fuzzy forms.",
            "Words and source_ids are read within their existing lines; no inferred spaces or cross-line binding.",
            "No null model, significance calculation, semantic interpretation, or conclusion is produced.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--packet", default=PACKET)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("EXACT_FORM_AUDIT.json"))
    args = parser.parse_args(argv)
    try:
        result = audit(args.root.resolve(), args.packet)
        rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        args.output.write_text(rendered, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, sort_keys=True))
        return 2
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
