#!/usr/bin/env python3
"""Replay saved target accounting and existing admission metadata only."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = json.loads((BASE / "F_ROOT_RESULT.json").read_text())
    raw_path = BASE / "F_TARGET_RAW.tsv"
    assert sha(raw_path) == result["target_projection_sha256"]
    with raw_path.open() as stream:
        raw = list(csv.DictReader(stream, delimiter="\t"))
    assert len(raw) == result["raw_group_count"] == 891
    assert dict(Counter(r["edition"] for r in raw)) == result["per_reader_groups"]
    assert {r["page"] for r in raw} == {"f22r", "f32r", "f42v"}
    byline = defaultdict(list)
    for row in raw:
        byline[row["edition"], row["locus"]].append(row)
    expected = []
    for (ed, loc), rs in byline.items():
        assert [int(r["source_group_index"]) for r in rs] == list(range(1, len(rs) + 1))
        expected.append(dict(edition=ed, locus=loc, raw_groups=" ".join(r["ivtff_group_raw"] for r in rs),
                             group_count=str(len(rs)), paragraph_start=rs[0]["paragraph_start"],
                             paragraph_end=rs[-1]["paragraph_end"],
                             schor_positions=",".join(r["source_group_index"] for r in rs if r["ivtff_group_raw"] == "schor")))
    with (BASE / "F_CONTEXT_LINES.tsv").open() as stream:
        assert list(csv.DictReader(stream, delimiter="\t")) == expected
    assert len(expected) == result["line_reader_rows"] == 144
    targets = [r for r in raw if r["ivtff_group_raw"] == "schor"]
    assert len(targets) == 9
    assert Counter(r["locus"] for r in targets) == {"f22r.4": 3, "f32r.4": 3, "f42v.10": 3}
    for row in targets:
        assert row["right_separator"] == "DEFINITE_SPACE"
        assert row["left_separator"] == ("DRAWING_INTERRUPTION" if row["page"] == "f22r" else "LINE_START")
    scope = json.loads((BASE / "F_SCOPE_COUNT_CORRECTION.json").read_text())
    reconstructed = []
    for contract in scope["contracts"]:
        path = ROOT / contract["path"]
        assert sha(path) == contract["sha256"]
        if path.suffix == ".tsv":
            with path.open() as stream:
                for row in csv.DictReader(stream, delimiter="\t"):
                    selector = row.get("source_selector") or row.get("selector") or row.get("folio")
                    key = row.get("physical_page") or row.get("folio") or row.get("selector")
                    assert selector and key and not selector.startswith("f84")
                    reconstructed.append(dict(contract=contract["path"], legacy_image_key=key, selector=selector))
        else:
            selector = "f2r" if path.name == "F2R_USER_QUESTION_ADMISSION.md" else "f25v"
            assert selector in path.read_text()
            reconstructed.append(dict(contract=contract["path"], legacy_image_key=selector, selector=selector))
    assert reconstructed == scope["rows"]
    assert len({r["legacy_image_key"] for r in reconstructed}) == scope["distinct_legacy_image_keys"] == 92
    assert len({r["selector"] for r in reconstructed}) == scope["distinct_selectors"] == 98
    assert scope["new_admissions_created"] == result["confirmed_lexemes"] == result["complete_target_readings"] == 0
    assert result["sealed"] == ["f84", "f84r"] and not result["reserves_opened"]
    output = dict(status="PASS", raw_groups_replayed=891, complete_line_reader_rows=144,
                  existing_scope_keys=92, existing_scope_selectors=98, new_admissions=0,
                  visual_judgments_verified=False, meaning_verified=False,
                  authorship="same-author separate replay executable")
    (BASE / "F_ROOT_VALIDATION.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))


if __name__ == "__main__":
    main()
