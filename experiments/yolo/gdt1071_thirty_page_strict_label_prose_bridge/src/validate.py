#!/usr/bin/env python3
"""Independent row-level checks for the GDT1071 complete projection."""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path(__file__).resolve().parents[1]
ART = BASE / "artifacts"


def rows(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> int:
    source = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
    specs = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv"
    annotation = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
    expected_hashes = {
        source: "4075ffca8e7a8b9cefda62c9ec6997fb6c518dba8f86790f5309bfe2a8574707",
        specs: "69e5463f7ce6c22bd83fe35e4fdc0601731a3c470b5c510a15ac3befa1716bae",
        annotation: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    }
    for path, digest in expected_hashes.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    selectors = sorted({r["source_selector"] for r in rows(specs) if r["physical_page"] != "f1r"})
    assert len(selectors) == 34 and all(not x.startswith("f84") for x in selectors)
    query = [str(ROOT / "vmanus-exp"), "query-tsv", str(annotation), "--selector", "page"]
    for selector in selectors:
        query.extend(["--allow", selector])
    query.extend(["--columns", "page,locus,certainty,context_class,local_relation_tags,unit_relation_tags", "--forbid-prefix", "f84"])
    guarded = subprocess.run(query, cwd=ROOT, capture_output=True, text=True, check=True)
    assert "skipped_forbidden" in guarded.stderr
    assert (ART / "GUARD.txt").read_text(encoding="utf-8") == guarded.stderr
    raw_annotations = list(csv.DictReader(io.StringIO(guarded.stdout), delimiter="\t"))
    by_locus = defaultdict(list)
    for r in raw_annotations:
        assert r["page"] in selectors
        by_locus[r["locus"]].append(r)

    all_rows = [r for r in rows(source) if r["source_selector"] in selectors]
    local_count = Counter(r["locus"] for r in all_rows if r["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL")
    local_single = {r["locus"]: r for r in all_rows if r["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL" and local_count[r["locus"]] == 1}
    prose = [r for r in all_rows if r["occurrence_kind"] == "RUNNING_EVENT"]
    prose_by_surface = defaultdict(list)
    for r in prose:
        prose_by_surface[r["surface"]].append(r)
    label_rows = rows(ART / "LABELS.tsv")
    match_rows = rows(ART / "MATCHES.tsv")
    assert len(label_rows) == len(local_single) == 313
    assert {r["locus"] for r in label_rows} == set(local_single)
    checked = 0
    for label in label_rows:
        loc = label["locus"]
        s = local_single[loc]
        ann = by_locus[loc]
        strict = any(
            a["certainty"] == "UNHEDGED"
            and a["context_class"] == "OBJECT_BEARING"
            and any(t in (a["local_relation_tags"] + ";" + a["unit_relation_tags"]).split(";") for t in ("REL_EXPLICIT_ATTACHMENT", "REL_DIRECT_ENCLOSURE", "REL_EXPLICIT_IDENTITY"))
            for a in ann
        )
        assert label["surface"] == s["surface"] and label["page"] == s["physical_page"]
        assert int(label["strict_owner"]) == strict
        assert int(label["annotated"]) == bool(ann)
        contacts = prose_by_surface[s["surface"]]
        assert int(label["same_page_occurrences"]) == sum(r["physical_page"] == s["physical_page"] for r in contacts)
        assert int(label["other_page_occurrences"]) == sum(r["physical_page"] != s["physical_page"] for r in contacts)
        assert int(label["same_panel_occurrences"]) == sum(s["panel_id"] != "NONE" and r["panel_id"] == s["panel_id"] and r["physical_page"] == s["physical_page"] for r in contacts)
        expected_contacts = Counter((r["locus"], r["physical_page"], r["token_ordinal_in_line"]) for r in contacts)
        actual_contacts = Counter((r["prose_locus"], r["prose_page"], r["prose_ordinal"]) for r in match_rows if r["label_locus"] == loc)
        assert expected_contacts == actual_contacts
        checked += 1
    assert len(match_rows) == sum(len(prose_by_surface[r["surface"]]) for r in label_rows)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    strict_candidates = [r for r in label_rows if int(r["strict_owner"]) and len(r["surface"]) >= 2]
    assert result["strict_single_group_loci"] == sum(int(r["strict_owner"]) for r in label_rows) == 34
    assert result["strict_same_page_types"] == sorted({r["surface"] for r in strict_candidates if int(r["same_page_occurrences"])})
    assert result["strict_other_page_types"] == sorted({r["surface"] for r in strict_candidates if int(r["other_page_occurrences"])})
    assert result["strict_same_page_loci"] == sorted(r["locus"] for r in strict_candidates if int(r["same_page_occurrences"]))
    validation = {"status": "PASS", "label_rows_checked": checked, "match_rows_checked": len(match_rows), "guarded_annotations": len(raw_annotations), "strict_same_page_types": result["strict_same_page_types"]}
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
