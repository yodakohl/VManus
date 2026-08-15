#!/usr/bin/env python3
"""GDT112: exact PAGE_HOST page-association preservation across O/OT frames."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PAGES = ROOT / "experiments/semantic_assumptions/results/existing_human_page_role_matrix.tsv"
METHOD = ROOT / "GDT112_O_OT_EXTERNAL_PRESERVATION_METHOD.md"
REPORT = ROOT / "GDT112_O_OT_EXTERNAL_PRESERVATION_REPORT.md"
UNITS = ROOT / "gdt112_o_ot_units.tsv"
SCORES = ROOT / "gdt112_o_ot_scores.tsv"
TAGS = ROOT / "gdt112_o_ot_tag_scores.tsv"
FOLDS = ROOT / "gdt112_o_ot_folio_scores.tsv"
RESULT = ROOT / "gdt112_result.json"

MODES = ("CROSS_FRAME", "SAME_FRAME", "ANY_FRAME")
SHRINK = 4.0


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    source = read(SOURCE); assert len(source) == 15592 and not any(row["page"].startswith("f84r") for row in source)
    pages = {row["page"]: row for row in read(PAGES) if not row["page"].startswith("f84r")}
    units_by_key = {}
    for row in source:
        if row["page"] not in pages or row["local_frame"] not in {"O", "OT"}: continue
        key = row["page"], row["page_host"], row["local_frame"]
        units_by_key[key] = {"page": row["page"], "physical_folio": row["physical_folio"],
                             "page_host": row["page_host"], "frame": row["local_frame"],
                             "register": row["register"], "tags": {tag for tag in pages[row["page"]]["source_tags"].split(";") if tag}}
    units = [units_by_key[key] for key in sorted(units_by_key)]
    assert len(units) == 1033 and len({row["page"] for row in units}) == 189 and len({row["physical_folio"] for row in units}) == 92
    page_counts = Counter(row["page"] for row in units)
    unique_pages = sorted({row["page"] for row in units})
    candidates = sorted({tag for row in units for tag in row["tags"]})
    tags = [tag for tag in candidates if 10 <= sum(tag in pages[page]["source_tags"].split(";") for page in unique_pages) <= len(unique_pages) - 10]
    assert len(tags) == 5

    unit_rows = [{"page": row["page"], "physical_folio": row["physical_folio"], "page_host": row["page_host"],
                  "frame": row["frame"], "register": row["register"], "page_weight": 1 / page_counts[row["page"]],
                  "source_tags": ";".join(sorted(row["tags"])), "semantic_role": "UNASSIGNED"} for row in units]
    write(UNITS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in unit_rows])

    score_rows = []; tag_rows = []; fold_rows = []
    for mode in MODES:
        base = model = weighted_mass = 0.0; predictions = 0; folio = defaultdict(lambda: [0.0, 0.0, 0, 0.0]); per_tag = defaultdict(lambda: [0.0, 0.0, 0, 0.0])
        for target in units:
            train_pages = {row["page"] for row in units if row["physical_folio"] != target["physical_folio"] and row["register"] == target["register"]}
            if mode == "CROSS_FRAME":
                related = {row["page"] for row in units if row["physical_folio"] != target["physical_folio"] and row["page_host"] == target["page_host"] and row["frame"] != target["frame"]}
            elif mode == "SAME_FRAME":
                related = {row["page"] for row in units if row["physical_folio"] != target["physical_folio"] and row["page_host"] == target["page_host"] and row["frame"] == target["frame"]}
            else:
                related = {row["page"] for row in units if row["physical_folio"] != target["physical_folio"] and row["page_host"] == target["page_host"]}
            if len(train_pages) < 2 or not related: continue
            weight = 1 / page_counts[target["page"]]; predictions += 1; weighted_mass += weight
            for tag in tags:
                p = (sum(tag in pages[page]["source_tags"].split(";") for page in train_pages) + .5) / (len(train_pages) + 1)
                q = (sum(tag in pages[page]["source_tags"].split(";") for page in related) + SHRINK * p) / (len(related) + SHRINK)
                y = tag in target["tags"]
                baseline_loss = -math.log2(p if y else 1 - p) * weight
                model_loss = -math.log2(q if y else 1 - q) * weight
                base += baseline_loss; model += model_loss
                f = folio[target["physical_folio"]]; f[0] += baseline_loss; f[1] += model_loss; f[2] += 1; f[3] += weight
                t = per_tag[tag]; t[0] += baseline_loss; t[1] += model_loss; t[2] += 1; t[3] += weight
        gains = [values[0] - values[1] for values in folio.values()]
        score_rows.append({"mode": mode, "unique_units": len(units), "scored_predictions": predictions,
                           "scored_weighted_page_mass": weighted_mass, "external_tags": len(tags),
                           "nuisance_bits": base, "held_bits": model, "gain_bits": base - model,
                           "selector_paid_gain_bits": base - model - math.log2(len(MODES)),
                           "positive_gain_folios": sum(value > 0 for value in gains), "scored_folios": len(gains),
                           "min_folio_gain": min(gains), "max_folio_gain": max(gains)})
        for tag, values in sorted(per_tag.items()):
            tag_rows.append({"mode": mode, "external_tag": tag, "predictions": values[2], "weighted_page_mass": values[3],
                             "nuisance_bits": values[0], "held_bits": values[1], "gain_bits": values[0] - values[1]})
        for held, values in sorted(folio.items()):
            fold_rows.append({"mode": mode, "held_folio": held, "tag_predictions": values[2], "weighted_page_mass": values[3],
                              "nuisance_bits": values[0], "held_bits": values[1], "gain_bits": values[0] - values[1]})
    score_rows.sort(key=lambda row: (-float(row["gain_bits"]), row["mode"]))
    write(SCORES, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in score_rows])
    write(TAGS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in tag_rows])
    write(FOLDS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in fold_rows])

    by_mode = {row["mode"]: row for row in score_rows}; cross = by_mode["CROSS_FRAME"]; same = by_mode["SAME_FRAME"]; any_frame = by_mode["ANY_FRAME"]
    status = "O_OT_EXACT_HOST_EXTERNAL_ASSOCIATION_NOT_PRESERVED" if float(cross["gain_bits"]) <= 0 else "O_OT_EXACT_HOST_EXTERNAL_ASSOCIATION_PROVISIONAL"
    REPORT.write_text(f"""# GDT112 — O/OT external-association preservation

## Outcome

**{status}**

The page catalogue supplies {len(units):,} unique page×PAGE_HOST×frame units
on {len(unique_pages)} pages and 92 physical folios. Five mechanically
capacity-eligible external page tags are scored. Reciprocal unit weights limit
each page to total mass one.

Exact PAGE_HOST transfer across the opposite O/OT frame covers
{int(cross['scored_predictions']):,} units ({float(cross['scored_weighted_page_mass']):.3f}
weighted pages) and changes held code by {float(cross['gain_bits']):+.3f} bits,
with positive gain on {int(cross['positive_gain_folios'])}/92 folios. Same-frame
transfer changes it by {float(same['gain_bits']):+.3f}; either-frame transfer by
{float(any_frame['gain_bits']):+.3f}. All five tag and folio contributions are
exported.

Thus exact PAGE_HOST identity does not preserve these broad external page
associations across O/OT beyond register. CROSS_FRAME is less harmful than the
same/any-frame alternatives, but a negative codelength gain is not evidence
for preserved content. This weakens the content-address reading of exact
PAGE_HOST while leaving its strong page-local formal vocabulary role intact.

The catalogue tags are broad and archive-exposed; this does not prove that O/OT
changes meaning or that PAGE_HOST lacks finer content. f84r was filtered before
the join and not opened, parsed, retained, queried, joined, scored, or targeted.
No semantic role, gloss, word, morpheme, POS, sound, language, plaintext,
meaning, or translation is assigned.
""", encoding="utf-8")
    result = {"schema": "GDT112_O_OT_EXTERNAL_PRESERVATION_RESULT_V1", "status": status,
              "units": len(units), "pages": len(unique_pages), "physical_folios": 92, "external_tags": tags,
              "scores": score_rows, "cross_frame": cross, "same_frame": same, "any_frame": any_frame,
              "interpretation": "Broad archive page association does not transfer for exact PAGE_HOST across O/OT after register control.",
              "claim_ceiling": "No semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
              "f84r": {"opened": False, "parsed": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
              "inputs": {SOURCE.name: sha(SOURCE), str(PAGES.relative_to(ROOT)): sha(PAGES), "gdt059_result.json": sha(ROOT / "gdt059_result.json"), "gdt108_result.json": sha(ROOT / "gdt108_result.json")},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "outputs": {path.name: sha(path) for path in (UNITS, SCORES, TAGS, FOLDS)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "cross": cross, "same": same, "any": any_frame}, sort_keys=True))


if __name__ == "__main__":
    main()
