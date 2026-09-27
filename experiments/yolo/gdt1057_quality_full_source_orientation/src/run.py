#!/usr/bin/env python3
"""Whole-source complexion frequency control; no new Voynich extraction."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
ART = HERE / "artifacts"
RUNTIME = HERE / "runtime"
URL = "https://celt.ucc.ie/published/G600005.html"
SOURCE = RUNTIME / "G600005.html"
TARGET = ROOT / "experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/ORIENTATION_FREQUENCY_COMPARISON.tsv"
QUADS = ("hot_dry", "hot_moist", "cold_dry", "cold_moist")


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_bytes() -> bytes:
    RUNTIME.mkdir(exist_ok=True)
    if not SOURCE.exists():
        with urllib.request.urlopen(URL, timeout=30) as response:
            SOURCE.write_bytes(response.read())
    return SOURCE.read_bytes()


def extract(raw: bytes) -> list[dict]:
    source = raw.decode("latin1")
    heads = list(re.finditer(r"<h2>An Irish Materia Medica</h2>", source))
    if len(heads) != 3:
        raise ValueError(f"expected three work headings, found {len(heads)}")
    start = heads[2].end()
    starts = list(re.finditer(r"<p>\s*(\d+)\.\s*", source[start:], re.I))
    if len(starts) != 286:
        raise ValueError(f"expected 286 entry starts, found {len(starts)}")
    rows = []
    for index, local in enumerate(starts):
        begin = start + local.end()
        end = start + starts[index + 1].start() if index + 1 < len(starts) else len(source)
        visible = html.unescape(re.sub(r"<[^>]*>", " ", source[begin:end]))
        opening = re.sub(r"\s+", " ", visible).strip()[:320]
        thermal = re.findall(r"\b(?:hot|cold)\b", opening, re.I)
        humidity = re.findall(r"\b(?:dry|moist|wet)\b", opening, re.I)
        category = ""
        if len(thermal) == len(humidity) == 1:
            category = thermal[0].lower() + "_" + ("dry" if humidity[0].lower() == "dry" else "moist")
        rows.append({
            "ordinal": index + 1,
            "source_number": local.group(1),
            "source_line": source.count("\n", 0, start + local.start()) + 1,
            "auto_category": category,
            "thermal_hits": len(thermal),
            "humidity_hits": len(humidity),
            "opening_sha256": hashlib.sha256(opening.encode("utf-8")).hexdigest(),
        })
    return rows


def smoothed(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values()) + 2.0
    return {key: (counts.get(key, 0) + 0.5) / total for key in QUADS}


def score(accepted: list[str]) -> list[dict]:
    source_p = smoothed(Counter(accepted))
    with TARGET.open(newline="", encoding="utf-8") as handle:
        old = list(csv.DictReader(handle, delimiter="\t"))
    old = [row for row in old if row["scope"] == "ALL_SAFE_NO_F1R" and row["mode"] == "EXACT_Y_EY"]
    if len(old) != 8 or any(sum(int(row[q]) for q in QUADS) != 192 for row in old):
        raise ValueError("GDT623 frozen eight-row 192-token deck changed")
    scored = []
    for row in old:
        counts = {q: int(row[q]) for q in QUADS}
        target_p = smoothed(counts)
        tv = 0.5 * sum(abs(source_p[q] - target_p[q]) for q in QUADS)
        scored.append({"assignment_id": row["assignment_id"], "k": row["k"], "t": row["t"], "ch": row["ch"], "sh": row["sh"], **counts, "total_variation_smoothed": f"{tv:.6f}"})
    scored.sort(key=lambda row: (float(row["total_variation_smoothed"]), row["assignment_id"]))
    for rank, row in enumerate(scored, 1):
        row["rank"] = rank
    return scored


def main() -> None:
    ART.mkdir(exist_ok=True)
    raw = source_bytes()
    rows = extract(raw)
    write_tsv(ART / "SOURCE_ENTRIES.tsv", rows, list(rows[0]))
    candidates = [row for row in rows if row["auto_category"]]
    write_tsv(ART / "AUTO_CANDIDATES.tsv", candidates, list(rows[0]))
    audit = {}
    manual_path = ART / "MANUAL_AUDIT.tsv"
    if manual_path.exists():
        with manual_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                ordinal = int(row["ordinal"])
                if ordinal in audit or row["decision"] not in ("ACCEPT", "EXCLUDE"):
                    raise ValueError(f"invalid manual row {ordinal}")
                audit[ordinal] = row
    if audit and set(audit) != {row["ordinal"] for row in candidates}:
        raise ValueError("manual audit must cover every auto candidate")
    accepted = [row["auto_category"] for row in candidates if audit.get(row["ordinal"], {}).get("decision") == "ACCEPT"]
    missing_numbers = sorted(set(range(1, 293)) - {int(row["source_number"]) for row in rows})
    output = {
        "source_url": URL,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_encoding": "latin1",
        "target_artifact": str(TARGET.relative_to(ROOT)),
        "target_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "entry_count": len(rows),
        "printed_entry_range": [1, 292],
        "missing_numbered_starts": missing_numbers,
        "automatic_candidates": len(candidates),
        "manual_audited": len(audit),
        "accepted_count": len(accepted),
        "source_counts": dict(Counter(accepted)),
        "status": "COMPLETE_NUMBERED_CENSUS_PARTIAL_SOURCE" if audit else "AWAITING_MANUAL_AUDIT",
    }
    if audit:
        table = score(accepted)
        write_tsv(ART / "ORIENTATION_RECHECK.tsv", table, list(table[0]))
        output["orientation_rank"] = [{"assignment_id": row["assignment_id"], "rank": row["rank"], "tv": row["total_variation_smoothed"]} for row in table]
        output["dry_fraction"] = (output["source_counts"].get("hot_dry", 0) + output["source_counts"].get("cold_dry", 0)) / len(accepted) if accepted else None
        output["dry_fraction_lower_bound_all_292"] = (output["source_counts"].get("hot_dry", 0) + output["source_counts"].get("cold_dry", 0)) / 292
    (ART / "RESULT.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: output[key] for key in ("status", "entry_count", "automatic_candidates", "manual_audited", "accepted_count")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
