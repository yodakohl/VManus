#!/usr/bin/env python3
"""Independently reconstruct the GDT1082 whole-batch capacity decision."""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
ANN = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
SELECTORS = BASE / "src/SELECTORS.tsv"
STRICT = {"REL_EXPLICIT_ATTACHMENT", "REL_DIRECT_ENCLOSURE", "REL_EXPLICIT_IDENTITY"}


def table(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def guarded(path, selectors, columns):
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for selector in selectors:
        cmd.extend(("--allow", selector))
    cmd.extend(("--columns", columns, "--forbid-prefix", "f84"))
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    assert "skipped_forbidden" in result.stderr
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    assert all(r["page"] in selectors and not r["page"].startswith("f84") for r in rows)
    return rows


def main():
    result = json.loads((BASE / "artifacts/RESULT.json").read_text(encoding="utf-8"))
    selectors = sorted(r["source_selector"] for r in table(SELECTORS))
    assert len(selectors) == len(set(selectors)) == 11
    assert result["method_sha256"] == hashlib.sha256((BASE / "METHOD.md").read_bytes()).hexdigest()
    for name, digest in result["input_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    annotations = guarded(ANN, selectors, "page,locus,certainty,context_class,local_relation_tags,unit_relation_tags")
    groups = guarded(SOURCE, selectors, "edition,locus,page,kind,source_group_index,ivtff_group_raw")
    assert result["annotation_rows"] == len(annotations) == 122
    assert result["source_group_rows_all_readers"] == len(groups)
    assert result["source_selectors"] == result["physical_pages"] == 11

    ann_by_locus = defaultdict(list)
    for a in annotations:
        ann_by_locus[a["locus"]].append(a)
    local = defaultdict(list)
    running = defaultdict(Counter)
    for g in groups:
        if g["edition"] != "ZL3b":
            continue
        if g["kind"] in {"C", "L"}:
            local[g["locus"]].append(g)
        elif g["kind"] == "P":
            running[g["ivtff_group_raw"]][g["page"]] += 1
    labels = table(BASE / "artifacts/LABELS.tsv")
    expected_loci = {loc for loc, entries in local.items() if len(entries) == 1}
    assert {r["locus"] for r in labels} == expected_loci
    strict_count = 0
    expected_same = set()
    for label in labels:
        locus = label["locus"]
        raw = local[locus][0]
        assert raw["ivtff_group_raw"] == label["surface"] and raw["page"] == label["page"]
        strict = any(
            a["certainty"] == "UNHEDGED" and a["context_class"] == "OBJECT_BEARING"
            and bool(STRICT.intersection(a["local_relation_tags"].split(";")))
            for a in ann_by_locus[locus]
        )
        assert int(label["strict_owner"]) == int(strict)
        strict_count += int(strict)
        same_count = running[label["surface"]][label["page"]]
        other_count = sum(running[label["surface"]].values()) - same_count
        assert int(label["same_page_occurrences"]) == same_count
        assert int(label["other_page_occurrences"]) == other_count
        if same_count and len(label["surface"]) >= 2:
            expected_same.add((label["page"], locus, label["surface"], same_count))
    assert len(labels) == result["single_group_local_loci"] == 80
    assert strict_count == result["strict_single_group_loci"] == 0
    assert result["primary_candidates"] == [] and result["reader_sensitivity"] == []
    assert result["strict_same_page_loci"] == [] and result["strict_other_page_loci"] == []
    assert result["status"] == "NO_NEW_STRICT_SAME_PAGE_CANDIDATE"
    expected = {
        ("f75v", "f75v.25", "qokal", 6),
        ("f75v", "f75v.31", "dal", 5),
        ("f75v", "f75v.52", "olol", 1),
        ("f75v", "f75v.54", "otedy", 3),
        ("f75v", "f75v.55", "oteey", 1),
        ("f75v", "f75v.56", "qotedy", 2),
        ("f99v", "f99v.31", "doldam", 1),
        ("f99v", "f99v.4", "oldy", 1),
    }
    assert expected_same == expected
    matches = table(BASE / "artifacts/MATCHES.tsv")
    assert len(matches) == sum(sum(running[r["surface"]].values()) for r in labels)
    assert all(m["label_locus"] in expected_loci and int(m["strict_owner"]) == 0 for m in matches)
    validation = {
        "status": "PASS", "selectors": len(selectors), "annotation_rows": len(annotations),
        "all_reader_group_rows": len(groups), "one_group_zl_local_loci": len(labels),
        "strict_local_loci": strict_count, "nonstrict_same_page_loci": len(expected_same),
        "match_rows": len(matches), "meaning_validated": False,
    }
    (BASE / "artifacts/VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))


if __name__ == '__main__':
    main()
