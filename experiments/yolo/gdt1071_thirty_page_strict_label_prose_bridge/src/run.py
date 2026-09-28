#!/usr/bin/env python3
"""Selector-guarded complete strict-label/prose capacity census."""
import csv
import hashlib
import io
import json
import subprocess
from collections import defaultdict
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path(__file__).resolve().parents[1]
SPINE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
SPECS = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv"
ANN = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
EXPECTED = {
    SPINE: "4075ffca8e7a8b9cefda62c9ec6997fb6c518dba8f86790f5309bfe2a8574707",
    SPECS: "69e5463f7ce6c22bd83fe35e4fdc0601731a3c470b5c510a15ac3befa1716bae",
    ANN: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
}
STRICT = {"REL_EXPLICIT_ATTACHMENT", "REL_DIRECT_ENCLOSURE", "REL_EXPLICIT_IDENTITY"}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    for path, digest in EXPECTED.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path
    specs = read_tsv(SPECS)
    allowed = {r["source_selector"] for r in specs if r["physical_page"] != "f1r"}
    pages = {r["physical_page"] for r in specs if r["physical_page"] != "f1r"}
    assert len(allowed) == 34 and len(pages) == 29
    columns = "page,locus,certainty,context_class,local_relation_tags,unit_relation_tags"
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(ANN), "--selector", "page"]
    for selector in sorted(allowed):
        cmd += ["--allow", selector]
    cmd += ["--columns", columns, "--forbid-prefix", "f84"]
    result = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    assert "skipped_forbidden" in result.stderr
    annotations = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    assert all(r["page"] in allowed for r in annotations)
    ann_by_locus = defaultdict(list)
    for r in annotations:
        ann_by_locus[r["locus"]].append(r)

    spine = [r for r in read_tsv(SPINE) if r["source_selector"] in allowed]
    assert all(r["physical_page"] in pages for r in spine)
    local = defaultdict(list)
    running = defaultdict(list)
    for r in spine:
        if r["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL":
            local[r["locus"]].append(r)
        elif r["occurrence_kind"] == "RUNNING_EVENT":
            running[r["surface"]].append(r)
        else:
            raise AssertionError(r["occurrence_kind"])

    labels = []
    matches = []
    for locus in sorted(local):
        cards = local[locus]
        if len(cards) != 1:
            continue
        card = cards[0]
        surface = card["surface"]
        rows = ann_by_locus.get(locus, [])
        strict = any(
            r["certainty"] == "UNHEDGED"
            and r["context_class"] == "OBJECT_BEARING"
            and bool(STRICT.intersection(set((r["local_relation_tags"] + ";" + r["unit_relation_tags"]).split(";"))))
            for r in rows
        )
        contacts = running.get(surface, [])
        same = [r for r in contacts if r["physical_page"] == card["physical_page"]]
        other = [r for r in contacts if r["physical_page"] != card["physical_page"]]
        labels.append({
            "locus": locus, "page": card["physical_page"], "surface": surface,
            "annotated": int(bool(rows)), "strict_owner": int(strict),
            "same_page_occurrences": len(same), "other_page_occurrences": len(other),
            "same_panel_occurrences": sum(1 for r in same if card["panel_id"] != "NONE" and r["panel_id"] == card["panel_id"]),
        })
        for prose in contacts:
            matches.append({
                "label_locus": locus, "label_page": card["physical_page"],
                "surface": surface, "strict_owner": int(strict),
                "prose_locus": prose["locus"], "prose_page": prose["physical_page"],
                "prose_ordinal": prose["token_ordinal_in_line"],
                "same_page": int(prose["physical_page"] == card["physical_page"]),
                "label_panel": card["panel_id"], "prose_panel": prose["panel_id"],
                "prose_record": prose["record_id"],
            })
    labels.sort(key=lambda r: (r["page"], r["locus"]))
    matches.sort(key=lambda r: (r["label_page"], r["label_locus"], r["prose_page"], r["prose_locus"], int(r["prose_ordinal"])))
    candidate = [r for r in labels if r["strict_owner"] and len(r["surface"]) >= 2]
    summary = {
        "source_selectors": len(allowed), "physical_pages": len(pages),
        "annotation_rows": len(annotations), "spine_occurrences": len(spine),
        "single_group_local_loci": len(labels), "strict_single_group_loci": sum(r["strict_owner"] for r in labels),
        "strict_candidate_types": len({r["surface"] for r in candidate}),
        "strict_same_page_types": sorted({r["surface"] for r in candidate if r["same_page_occurrences"]}),
        "strict_other_page_types": sorted({r["surface"] for r in candidate if r["other_page_occurrences"]}),
        "strict_same_page_loci": [r["locus"] for r in candidate if r["same_page_occurrences"]],
        "strict_other_page_loci": [r["locus"] for r in candidate if r["other_page_occurrences"]],
        "non_strict_same_page_types": sorted({r["surface"] for r in labels if not r["strict_owner"] and len(r["surface"]) >= 2 and r["same_page_occurrences"]}),
        "non_strict_other_page_types": sorted({r["surface"] for r in labels if not r["strict_owner"] and len(r["surface"]) >= 2 and r["other_page_occurrences"]}),
    }
    out = BASE / "artifacts"
    out.mkdir(exist_ok=True)
    write_tsv(out / "LABELS.tsv", labels, list(labels[0]))
    write_tsv(out / "MATCHES.tsv", matches, list(matches[0]) if matches else ["label_locus", "label_page", "surface", "strict_owner", "prose_locus", "prose_page", "prose_ordinal", "same_page", "label_panel", "prose_panel", "prose_record"])
    (out / "RESULT.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "GUARD.txt").write_text(result.stderr, encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
