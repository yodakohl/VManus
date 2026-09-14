#!/usr/bin/env python3
"""Audit four exact forms in the bounded Luna pilot sources."""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / "research_registry/work_batches/luna_throughput_20260914"
PARA = ROOT / "research_registry/work_batches/luna_pilot_20260914/EXPOSED_PARAGRAPHS.json"
RF = ROOT / "research_registry/work_batches/luna_pilot_20260914/RF_VARIANTS.json"
OUT = BATCH / "FOUR_FORM_AUDIT.json"
FORMS = ("olkain", "qolkain", "ol kain", "qol kain")


def exposed_occurrences(doc):
    out = {edition: {form: [] for form in FORMS} for edition in ("ZL3b", "IT2a")}
    for paragraph in doc["paragraphs"]:
        edition = paragraph["edition"]
        for line in paragraph["lines"]:
            words = line["words"]
            ids = line["source_ids"]
            boundary = {
                "paragraph_start_line": bool(line.get("start")),
                "paragraph_end_line": bool(line.get("end")),
                "token_separators": None,
                "separator_status": "UNAVAILABLE_IN_SIMPLIFIED_ARRAY",
            }
            for i, word in enumerate(words):
                if word in ("olkain", "qolkain"):
                    out[edition][word].append({
                        "locus": line["locus"], "words": [word],
                        "source_ids": [ids[i]], "boundary_flags": boundary,
                    })
            for i in range(len(words) - 1):
                form = " ".join(words[i:i + 2])
                if form in ("ol kain", "qol kain"):
                    out[edition][form].append({
                        "locus": line["locus"], "words": words[i:i + 2],
                        "source_ids": ids[i:i + 2], "boundary_flags": boundary,
                    })
    return out


def rf_occurrences(doc):
    out = {"RF1b": {form: [] for form in FORMS}}
    for line in doc["lines"]:
        columns = {name: i for i, name in enumerate(line["columns"])}
        groups = line["groups"]
        rows = [{name: group[i] for name, i in columns.items()} for group in groups]
        for i, row in enumerate(rows):
            raw = row["ivtff_group_raw"]
            if raw in ("olkain", "qolkain"):
                out["RF1b"][raw].append({
                    "locus": line["locus"], "words": [raw],
                    "source_ids": [row["source_group_id"]],
                    "boundary_flags": {
                        "line_start": row["left_separator"] == "LINE_START",
                        "line_end": row["right_separator"] == "LINE_END",
                        "token_separators": [row["left_separator"], row["right_separator"]],
                    },
                })
            if i + 1 < len(rows):
                pair = [rows[i], rows[i + 1]]
                form = " ".join(r["ivtff_group_raw"] for r in pair)
                if form in ("ol kain", "qol kain"):
                    out["RF1b"][form].append({
                        "locus": line["locus"],
                        "words": [r["ivtff_group_raw"] for r in pair],
                        "source_ids": [r["source_group_id"] for r in pair],
                        "boundary_flags": {
                            "line_start": pair[0]["left_separator"] == "LINE_START",
                            "line_end": pair[1]["right_separator"] == "LINE_END",
                            "token_separators": [
                                pair[0]["right_separator"], pair[1]["left_separator"]
                            ],
                        },
                    })
    return out


def main():
    packet = json.loads((BATCH / "PACKET.json").read_text())
    hashes = {row["path"]: row["sha256"] for row in packet["inputs"]}
    for path in (PARA, RF):
        if hashlib.sha256(path.read_bytes()).hexdigest() != hashes[str(path.relative_to(ROOT))]:
            raise ValueError("bound source hash mismatch")
    with PARA.open(encoding="utf-8") as fh:
        exposed = exposed_occurrences(json.load(fh))
    with RF.open(encoding="utf-8") as fh:
        rf = rf_occurrences(json.load(fh))
    occurrences = {reader: forms for reader, forms in {**exposed, **rf}.items()}
    counts = {reader: {form: len(entries) for form, entries in forms.items()}
              for reader, forms in occurrences.items()}
    result = {
        "status": "POSTHOC_EXACT_FORM_AUDIT",
        "scope": {
            "readers": ["ZL3b", "IT2a", "RF1b"],
            "forms": list(FORMS),
            "exposed_records": 6,
            "rf_lines": 30,
            "source_paths": [str(PARA.relative_to(ROOT)), str(RF.relative_to(ROOT))],
            "boundary_policy": "ZL/IT simplified arrays retain unavailable separator flags; RF preserves raw separator fields; no uncertain form normalization.",
        },
        "counts": counts,
        "occurrences": occurrences,
        "crossed_shared_form_contrast": {
            "f80v": "YES: olkain occurs at .30/.31/.33/.34 in every reader; qolkain at .32; ol kain and qol kain at .35. ZL additionally has olkain after s at .32, while IT/RF have solkain there, excluded from exact olkain counts.",
            "interpretation": "Occurrence co-location supplies a crossed written-form contrast only; it does not establish semantic equivalence or independent replication.",
        },
        "evidence_paths": [str(PARA.relative_to(ROOT)), str(RF.relative_to(ROOT))],
        "root_review_corrections": "Corrected the initial all-reader .32 shorthand and renamed ZL/IT paragraph-boundary flags; added bound-source hash checks. Exact counts unchanged.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
