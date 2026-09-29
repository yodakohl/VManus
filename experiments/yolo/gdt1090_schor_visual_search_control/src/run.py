#!/usr/bin/env python3
"""Guarded complete-word audit against frozen two-reader image codes."""
import csv
import hashlib
import io
import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
OLD = ROOT / "experiments/yolo/gdt1089_head_edit1_organ_blind_holdfolio"
LIST = OLD / "src/BLIND_IMAGE_LIST.tsv"
A = OLD / "artifacts/BLIND_A.tsv"
B = OLD / "artifacts/BLIND_B.tsv"
COLS = "edition,page,locus,kind,source_group_index,left_separator,right_separator,ivtff_group_raw"
FIELDS = ["word", "admitted_folios", "image_folios", "union_yes", "all_image_yes",
          "line_initial_image_folios", "all_folios", "image_folio_ids", "yes_folio_ids"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def image_codes():
    roster = {r["folio"] for r in read_tsv(LIST)}
    assert len(roster) == 38 and not any(p.startswith("f84") for p in roster)
    tables = [{r["folio"]: r for r in read_tsv(path)} for path in (A, B)]
    assert all(set(tab) == roster for tab in tables)
    yes = {page for page in roster if all(any(tab[page][feature] == "YES"
            for feature in ("MULTI_UNIT_SPIKE", "SPINY_ROUND_HEAD")) for tab in tables)}
    return roster, yes


def query():
    allowed = [r["page"] for r in read_tsv(ALLOW)]
    assert len(allowed) == len(set(allowed)) == 179
    assert not any(p.startswith("f84") for p in allowed)
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
           "--selector", "page", "--columns", COLS, "--forbid-prefix", "f84"]
    for page in allowed:
        cmd.extend(["--allow", page])
    got = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(got.stdout), delimiter="\t"))
    assert not any(r["page"].startswith("f84") for r in rows)
    return set(allowed), rows, got.stderr.strip()


def compute():
    roster, yes = image_codes()
    allowed, rows, guard = query()
    covered = roster & allowed
    folios = defaultdict(set)
    initial = defaultdict(set)
    for r in rows:
        if r["edition"] != "ZL3b" or r["kind"] != "P":
            continue
        if r["left_separator"] not in {"LINE_START", "DEFINITE_SPACE", "DRAWING_INTERRUPTION"} or \
                r["right_separator"] not in {"DEFINITE_SPACE", "LINE_END", "DRAWING_INTERRUPTION"}:
            continue
        word = r["ivtff_group_raw"]
        if not word or any(c.isspace() for c in word):
            continue
        page = r["page"]
        folios[word].add(page)
        if r["left_separator"] == "LINE_START":
            initial[word].add(page)
    deck = []
    for word, all_pages in sorted(folios.items()):
        ims = all_pages & covered
        if len(ims) < 3:
            continue
        hits = ims & yes
        deck.append(dict(word=word, admitted_folios=len(all_pages), image_folios=len(ims),
                         union_yes=len(hits), all_image_yes=int(ims == hits),
                         line_initial_image_folios=len(initial[word] & ims),
                         all_folios=";".join(sorted(all_pages)),
                         image_folio_ids=";".join(sorted(ims)),
                         yes_folio_ids=";".join(sorted(hits)) or "-"))
    primary = [r for r in deck if r["admitted_folios"] == 3 and r["image_folios"] == 3]
    secondary = [r for r in deck if r["image_folios"] == 3]
    target = next((r for r in deck if r["word"] == "schor"), None)
    assert target is not None
    alternate = {edition: sorted({r["page"] for r in rows if r["edition"] == edition
        and r["kind"] == "P" and r["ivtff_group_raw"] == "schor"
        and r["left_separator"] in {"LINE_START", "DEFINITE_SPACE", "DRAWING_INTERRUPTION"}
        and r["right_separator"] in {"DEFINITE_SPACE", "LINE_END", "DRAWING_INTERRUPTION"}})
        for edition in ("IT2a", "RF1b")}
    result = {
        "experiment": "GDT1090", "guard": guard, "input_sha256": {
            str(p.relative_to(ROOT)): sha(p) for p in (SOURCE, ALLOW, LIST, A, B)},
        "admitted_page_selectors": len(allowed), "image_folios": len(roster),
        "image_folios_with_text": len(covered), "image_folios_missing_text": sorted(roster - allowed),
        "union_yes_folios": sorted(yes), "all_qualifying_words": len(deck),
        "primary_words": len(primary), "primary_3of3": [r["word"] for r in primary if r["all_image_yes"]],
        "primary_3of3_with_at_least_two_line_initial": [r["word"] for r in primary
            if r["all_image_yes"] and r["line_initial_image_folios"] >= 2],
        "secondary_words": len(secondary),
        "secondary_3of3": [r["word"] for r in secondary if r["all_image_yes"]],
        "words_with_at_least_three_image_folios_all_yes": [r["word"] for r in deck if r["all_image_yes"]],
        "schor": target,
        "schor_alternate_readers_same_manuscript": alternate,
        "claim_ceiling": "Retrospective search multiplicity only; no p-value, word owner or confirmed meaning."
    }
    return deck, primary, secondary, result


def write(rows, path):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    deck, primary, secondary, result = compute()
    out = HERE / "artifacts"
    out.mkdir(exist_ok=True)
    write(deck, out / "ALL_WORDS.tsv")
    write(primary, out / "PRIMARY.tsv")
    write(secondary, out / "SECONDARY.tsv")
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
