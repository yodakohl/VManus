#!/usr/bin/env python3
"""Project the 94 V99R4 defaults onto their 1,039 cached V48 occurrences."""
from __future__ import annotations

import csv, hashlib, json, re, sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("VManus repository root not found")

ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt731_v99r4_occurrence_passage_impact"
SRC, ART = EXP / "src", EXP / "artifacts"
G671 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G696 = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts"
G729 = ROOT / "experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/artifacts"
G730 = ROOT / "experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch"
LINES = G671 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
PAGES = G671 / "PAGE_ALLOWLIST.tsv"
OLD_DICT = G729 / "V99R3_COMPLETE_WORD_CONFIDENCE.tsv"
NEW_DICT = G730 / "artifacts/V99R4_COMPLETE_WORD_CONFIDENCE.tsv"
SPECS = G730 / "src/V99R4_94_AMBIGUITY_DEFAULT_SPECS.tsv"
RULES = SRC / "PRACTICAL_BLOCKER_RULES.tsv"
OVERLAY_LINE = G696 / "V69_51_LINE_RELATION_OVERLAY.tsv"
OVERLAY_TOKEN = G696 / "V69_479_TOKEN_RELATION_OVERLAY.tsv"
OVERLAY_READER = G696 / "GDT696_V69_LOCAL_OBJECT_CARRY_READER.md"
STATUS = ("PASS_94_SURFACES_1039_POSITIONS_911_LINES__351_COMPLETE_LINES__50_TARGET_DENSE_"
          "PASSAGES__GDT696_OVERLAYS_BYTE_STABLE__CACHED_DEFAULT_IMPACT_ONLY__NO_POLISHED_"
          "TRANSLATION_OR_NEW_PAGE")

def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))

def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    data = list(rows); fields = fields or (list(data[0]) if data else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n"); writer.writeheader()
        for row in data: writer.writerow({field: row.get(field, "") for field in fields})

def file_sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def ambiguity_flags(text: str) -> tuple[int, int, int]:
    return (int("/" in text), int(bool(re.search(r"(?i)(?<!\w)oder(?!\w)", text))), int("menge" in text.casefold()))

def practicalize_cells(cells: list[str]) -> str:
    # Editorial cleanup only: no word insertion, deletion, inflection or semantic dispatch.
    cells = [re.sub(r"\s+", " ", cell).strip(" ;") for cell in cells]
    text = "; ".join(cells)
    text = re.sub(r"\s+", " ", text).replace(".;", ";").replace(":;", ":")
    return re.sub(r";{2,}", ";", text).strip()

def build_maps():
    old_rows, new_rows, specs = read_tsv(OLD_DICT), read_tsv(NEW_DICT), read_tsv(SPECS)
    old = {r["surface"]: r for r in old_rows if r["current_layer"] == "GLOBAL_V48_DEFAULT"}
    new = {r["surface"]: r for r in new_rows if r["current_layer"] == "GLOBAL_V48_DEFAULT"}
    spec = {r["surface"]: r for r in specs}
    assert len(spec) == 94 and set(spec) <= set(old) and set(spec) <= set(new)
    for surface, card in spec.items():
        assert old[surface]["reading_id"] == new[surface]["reading_id"] == card["reading_id"]
        assert old[surface]["working_meaning_de"] == card["expected_old_meaning_de"]
        assert new[surface]["working_meaning_de"] == card["new_meaning_de"]
        assert new[surface]["v99_context_realizations_de"] == card["new_meaning_de"]
    return old, new, spec, new_rows

def build_projection(lines, old, new, specs):
    occurrence, comparisons = [], []
    total_tokens = non_target = 0
    for line in lines:
        tokens = line["zl3b_line"].split()
        inherited = line["token_glosses_de"].split(" | ")
        assert len(tokens) == len(inherited) == int(line["token_count"]), line["locus"]
        total_tokens += len(tokens); before = list(inherited); after = list(inherited); changed = []
        for index, surface in enumerate(tokens):
            if surface not in specs:
                non_target += 1; continue
            card = specs[surface]; before[index] = old[surface]["working_meaning_de"]
            after[index] = new[surface]["working_meaning_de"]
            assert before[index] != after[index]
            changed.append(index + 1)
            occurrence.append({"occurrence_id": f"G731-P{len(occurrence)+1:04d}", "page": line["page"],
              "locus": line["locus"], "token_ordinal": index + 1, "surface": surface,
              "reading_id": card["reading_id"], "family": card["family"],
              "v99r3_meaning_de": before[index], "v99r4_meaning_de": after[index],
              "inherited_v48_gloss_de": inherited[index], "token_retained": 1, "ordinal_retained": 1,
              "strongest_rival_de": card["strongest_rival_de"], "source_evidence": card["source_evidence"],
              "working_model_score_0_100_not_probability": new[surface]["working_model_score_0_100_not_probability"],
              "working_model_level": new[surface]["working_model_level"],
              "positive_evidence_de": new[surface]["positive_evidence_de"],
              "counterevidence_de": new[surface]["counterevidence_de"],
              "semantic_scope": new[surface]["semantic_scope"],
              "historical_confirmation": new[surface]["historical_confirmation"],
              "component_relation_credit": 0})
        if not changed: continue
        old_flags = [sum(x) for x in zip(*(ambiguity_flags(before[i-1]) for i in changed))]
        new_flags = [sum(x) for x in zip(*(ambiguity_flags(after[i-1]) for i in changed))]
        comparisons.append({"page": line["page"], "locus": line["locus"], "section": line["section"],
          "language": line["language"], "hand": line["hand"], "token_count": line["token_count"],
          "unknown_tokens": line["unknown_tokens"], "complete_v48": int(line["unknown_tokens"] == "0"),
          "target_count": len(changed), "target_ordinals": "|".join(map(str, changed)),
          "target_surfaces": "|".join(tokens[i-1] for i in changed), "zl3b_line": line["zl3b_line"],
          "v99r3_token_glosses_de": " | ".join(before),
          "v99r4_token_glosses_de": " | ".join(after),
          "v99r3_target_glosses_de": " | ".join(before[i-1] for i in changed),
          "v99r4_target_glosses_de": " | ".join(after[i-1] for i in changed),
          "v99r3_render_de": practicalize_cells(before), "v99r4_render_de": practicalize_cells(after),
          "old_slash_occurrences": old_flags[0], "new_slash_occurrences": new_flags[0],
          "old_standalone_oder_occurrences": old_flags[1], "new_standalone_oder_occurrences": new_flags[1],
          "old_casefold_menge_occurrences": old_flags[2], "new_casefold_menge_occurrences": new_flags[2],
          "non_target_cells_unchanged": len(tokens) - len(changed), "exact_tokens_and_ordinals_retained": 1})
    assert total_tokens == 32339 and non_target == 31300
    assert len(occurrence) == 1039 and len(comparisons) == 911
    complete = [r for r in comparisons if r["complete_v48"] == 1]
    assert len(complete) == 351 and sum(r["target_count"] for r in complete) == 409
    return occurrence, comparisons, complete

def build_blockers(rules, dictionary_rows, comparisons):
    out = []
    passage_cells = []
    for line in comparisons:
        tokens = line["zl3b_line"].split()
        cells = line["v99r4_token_glosses_de"].split(" | ")
        assert len(tokens) == len(cells) == int(line["token_count"])
        for ordinal, (surface, cell) in enumerate(zip(tokens, cells, strict=True), 1):
            status = "UNKNOWN" if re.fullmatch(r"\[[^]]+:\?]", cell) else "RESOLVED"
            passage_cells.append((line["locus"], ordinal, surface, cell, status))
    for rule in rules:
        pattern = re.compile(rule["regex"], re.IGNORECASE)
        scope = rule["field_scope"]
        assert scope in {"working_meaning_de", "surface", "passage_cell_status"}
        if scope == "working_meaning_de":
            dictionary = [r for r in dictionary_rows if pattern.search(r["working_meaning_de"])]
            passages = [x for x in passage_cells if pattern.search(x[3])]
        elif scope == "surface":
            dictionary = [r for r in dictionary_rows if pattern.search(r["surface"])]
            passages = [x for x in passage_cells if pattern.search(x[2])]
        else:
            dictionary = []
            passages = [x for x in passage_cells if pattern.search(x[4])]
        if scope != "passage_cell_status":
            observed_occurrences = sum(int(r["occurrence_count"]) for r in dictionary)
            assert len(dictionary) == int(rule["expected_dictionary_rows"]), (
                rule["blocker_class"], len(dictionary), rule["expected_dictionary_rows"])
            assert observed_occurrences == int(rule["expected_dictionary_occurrences"]), (
                rule["blocker_class"], observed_occurrences, rule["expected_dictionary_occurrences"])
        out.append({**rule, "matched_dictionary_rows": len(dictionary),
          "matched_dictionary_occurrences": sum(int(r["occurrence_count"]) for r in dictionary),
          "matched_affected_passage_cells": len(passages),
          "matched_affected_passage_lines": len({x[0] for x in passages}),
          "sample_dictionary_surfaces": "|".join(r["surface"] for r in dictionary[:12]) or "NONE",
          "sample_passage_loci": "|".join(dict.fromkeys(x[0] for x in passages[:12])) or "NONE",
          "automatic_failure_triggered": int(rule["automatic_failure"] == "1" and bool(
              passages if scope == "passage_cell_status" else dictionary))})
    return out

def quality_summary(occurrence, comparisons, blockers):
    before = [r["v99r3_meaning_de"] for r in occurrence]; after = [r["v99r4_meaning_de"] for r in occurrence]
    metrics = [
      ("target_surfaces", 94, 94), ("target_occurrences", 1039, 1039), ("affected_lines", 911, 911),
      ("affected_complete_v48_lines", 351, 351),
      ("slash_marker_occurrences", sum("/" in x for x in before), sum("/" in x for x in after)),
      ("standalone_oder_occurrences", sum(bool(re.search(r"(?i)(?<!\w)oder(?!\w)", x)) for x in before), sum(bool(re.search(r"(?i)(?<!\w)oder(?!\w)", x)) for x in after)),
      ("casefold_menge_occurrences", sum("menge" in x.casefold() for x in before), sum("menge" in x.casefold() for x in after)),
      ("mean_target_words", sum(len(x.split()) for x in before)/len(before), sum(len(x.split()) for x in after)/len(after)),
      # The blocker deck is applied only to V99R4.  Do not imply that V99R3
      # had zero blockers when no equivalent before-census was performed.
      ("automatic_blocker_rules_triggered", "NA", sum(r["automatic_failure_triggered"] for r in blockers)),
    ]
    assert metrics[4][1:] == (823, 0) and metrics[5][1:] == (76, 0) and metrics[6][1:] == (251, 0)
    return [{"metric": name, "v99r3_before": old, "v99r4_after": new,
             "delta_after_minus_before": new-old if isinstance(old, (int, float)) else "NA",
             "interpretation": "cached projection metric; not plaintext accuracy"}
            for name, old, new in metrics]

def overlay_parity():
    rows = []
    for path, expected in ((OVERLAY_LINE, 51), (OVERLAY_TOKEN, 479), (OVERLAY_READER, None)):
        count = len(read_tsv(path)) if path.suffix == ".tsv" else sum(line.startswith("## ") for line in path.read_text(encoding="utf-8").splitlines())
        if expected is not None: assert count == expected
        rows.append({"source_artifact": str(path.relative_to(ROOT)), "row_or_section_count": count,
          "sha256": file_sha(path), "gdt731_rewrite_count": 0, "parity_status": "BYTE_STABLE_NOT_REWRITTEN"})
    return rows

def main() -> int:
    if not RULES.is_file(): raise FileNotFoundError(f"required blocker rule deck not found: {RULES}")
    ART.mkdir(parents=True, exist_ok=True)
    pages = [r["page"] for r in read_tsv(PAGES)]
    assert len(pages) == len(set(pages)) == 179 and not any(p.startswith(("f84", "f84r")) for p in pages)
    lines = read_tsv(LINES)
    assert len(lines) == 4128 and {r["page"] for r in lines} <= set(pages)
    old, new, specs, complete_dictionary = build_maps()
    occurrence, comparisons, complete = build_projection(lines, old, new, specs)
    observed_counts = Counter(row["surface"] for row in occurrence)
    assert observed_counts == Counter({surface: int(new[surface]["occurrence_count"]) for surface in specs})
    dense = sorted(comparisons, key=lambda r: (-r["target_count"], -r["complete_v48"], r["locus"]))[:50]
    dense = [{"rank": i, **row} for i, row in enumerate(dense, 1)]
    blockers = build_blockers(read_tsv(RULES), complete_dictionary, comparisons)
    quality = quality_summary(occurrence, comparisons, blockers); parity = overlay_parity()
    write_tsv(ART / "V99R3_V99R4_1039_OCCURRENCE_DELTA.tsv", occurrence)
    write_tsv(ART / "V99R3_V99R4_911_LINE_RENDER_COMPARISON.tsv", comparisons)
    write_tsv(ART / "V99R3_V99R4_351_COMPLETE_LINE_COMPARISON.tsv", complete)
    write_tsv(ART / "V99R4_50_TARGET_DENSE_PASSAGES.tsv", dense)
    write_tsv(ART / "V99R4_BLOCKER_CENSUS.tsv", blockers)
    write_tsv(ART / "V99R4_RENDER_QUALITY_SUMMARY.tsv", quality)
    write_tsv(ART / "V99R4_GDT696_OVERLAY_PARITY.tsv", parity)
    md = ["# GDT731 — 50 target-dense cached passages", "", "These are deterministic V99R3/V99R4 default projections, not polished translations or plaintext. The ranking measures changed target cells, not semantic importance.", ""]
    for row in dense:
        md += [f"## {row['rank']}. {row['locus']} ({row['target_count']} changes)", "",
               f"Voynich: `{row['zl3b_line']}`", "", f"Before: {row['v99r3_render_de']}", "",
               f"After: {row['v99r4_render_de']}", ""]
    (ART / "GDT731_V99R4_50_TARGET_DENSE_READER.md").write_text("\n".join(md).rstrip()+"\n", encoding="utf-8")
    result = {"experiment_id": "GDT731", "status": STATUS, "allowed_pages": 179,
      "cached_lines": 4128, "aligned_tokens": 32339, "target_surfaces": 94,
      "target_positions": 1039, "affected_lines": 911, "affected_complete_v48_lines": 351,
      "non_target_positions_unchanged": 31300, "target_dense_passages": 50,
      "old_slash_occurrences": 823, "new_slash_occurrences": 0,
      "old_standalone_oder_occurrences": 76, "new_standalone_oder_occurrences": 0,
      "old_casefold_menge_occurrences": 251, "new_casefold_menge_occurrences": 0,
      "mean_target_words_before": next(r["v99r3_before"] for r in quality if r["metric"] == "mean_target_words"),
      "mean_target_words_after": next(r["v99r4_after"] for r in quality if r["metric"] == "mean_target_words"),
      "blocker_rules": len(blockers), "automatic_blocker_rules_triggered": sum(r["automatic_failure_triggered"] for r in blockers),
      "gdt696_overlay_artifacts_byte_stable": len(parity), "new_pages": 0,
      "claim_ceiling": "cached whole-default impact; no polished translation or plaintext"}
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
