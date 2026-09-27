#!/usr/bin/env python3
"""Independent literal/reference replay for frozen RAW568 author packet.

Uses only the owned, all-f85r2 GDT1042 native_groups projection and the frozen
568 packet. It checks literal/index/accounting relations, not semantic truth or
a full grammar execution.
"""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOSSIER = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926"
PROJ = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv"
DRAFT = DOSSIER / "RECIPIENT_AUTHOR_DRAFT.json"
CONTRACT = DOSSIER / "RECIPIENT_AUTHOR_CONTRACT.md"
OUT = DOSSIER / "RECIPIENT_REPLAY_B.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    d = json.loads(DRAFT.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(PROJ.open(encoding="utf-8", newline=""), delimiter="\t"))
    fields = ("edition", "block", "locus", "source_group_id", "source_group_index",
              "source_group_count", "within_line_position", "paragraph_start",
              "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw")
    checks: dict[str, bool] = {}
    errors: list[str] = []
    def check(name: str, ok: bool, detail: str = "") -> None:
        checks[name] = bool(ok)
        if not ok: errors.append(f"{name}: {detail or 'failed'}")

    proj_hash = sha(PROJ)
    check("projection_hash_matches_frozen_input", proj_hash == d["safe_projection_sha256"] == d["input_receipts"][str(PROJ.relative_to(ROOT))]["sha256"], f"actual {proj_hash}")
    check("contract_hash_matches_frozen_input", sha(CONTRACT) == d["contract_sha256"] == d["input_receipts"][str(CONTRACT.relative_to(ROOT))]["sha256"])
    check("projection_has_473_rows", len(rows) == 473, str(len(rows)))
    proj_by_id = {r["source_group_id"]: r for r in rows}
    occs = d["all_occurrences"]
    occ_by_id = {r["source_group_id"]: r for r in occs}
    check("unique_projection_ids", len(proj_by_id) == len(rows))
    check("occurrences_exact_projection_ids", set(proj_by_id) == set(occ_by_id), f"missing={sorted(set(proj_by_id)-set(occ_by_id))[:4]} extra={sorted(set(occ_by_id)-set(proj_by_id))[:4]}")
    mismatches = [(sid, f, proj_by_id[sid][f], str(occ_by_id[sid].get(f))) for sid in proj_by_id.keys() & occ_by_id.keys() for f in fields if proj_by_id[sid][f] != str(occ_by_id[sid].get(f))]
    check("all_projection_fields_match", not mismatches, repr(mismatches[:4]))
    check("unique_occurrence_ids", len(occ_by_id) == len(occs))
    selected = [x for x in occs if x["block"] != "OUTSIDE"]
    outside = [x for x in occs if x["block"] == "OUTSIDE"]
    check("selected_outside_partition", len(selected) == 324 and len(outside) == 149, f"{len(selected)}/{len(outside)}")
    by_edition = {e: [x for x in occs if x["edition"] == e] for e in ("ZL3b", "IT2a", "RF1b")}
    check("edition_counts", {e: len(v) for e,v in by_edition.items()} == {"ZL3b":156,"IT2a":157,"RF1b":160}, str({e:len(v) for e,v in by_edition.items()}))
    check("selected_counts", {e:sum(x["block"] != "OUTSIDE" for x in v) for e,v in by_edition.items()} == {"ZL3b":108,"IT2a":107,"RF1b":109})
    clause_ids = [sid for c in d["clauses"] for sid in c["source_ids"]]
    check("18_unique_clause_labels", len(d["clauses"]) == 18 and len({c["id"] for c in d["clauses"]}) == 18)
    check("clauses_cover_selected_zl_once", len(clause_ids) == 108 and len(set(clause_ids)) == 108 and set(clause_ids) == {x["source_group_id"] for x in selected if x["edition"] == "ZL3b"})
    reconstructed = [(c["id"], " ".join(proj_by_id[sid]["ivtff_group_raw"] for sid in c["source_ids"])) for c in d["clauses"]]
    check("clause_literal_spans_match_projection", all(lit == c["literal"] for (cid,lit),c in zip(reconstructed,d["clauses"])), repr([(cid,lit) for (cid,lit),c in zip(reconstructed,d["clauses"]) if lit != c["literal"]][:3]))
    check("clauses_do_not_cross_editions", all(all(occ_by_id[sid]["edition"] == "ZL3b" for sid in c["source_ids"]) for c in d["clauses"]))

    lex = d["lexicon"]
    by_form = {x["form"]: x for x in lex}
    check("85_unique_lexicon_forms", len(lex) == 85 and len(by_form) == 85)
    lex_ids = [sid for x in lex for sid in x["all_owned_literal_occurrences"]]
    row_ids = [x["source_group_id"] for x in occs if x["lexical_status"] == "assigned_exact"]
    check("lexicon_occurrence_inventory_exact", len(lex_ids) == len(set(lex_ids)) == len(row_ids) == 342 and set(lex_ids) == set(row_ids), f"lex={len(lex_ids)} rows={len(row_ids)}")
    mismatch = []
    for ent in lex:
        for sid in ent["all_owned_literal_occurrences"]:
            row = occ_by_id.get(sid)
            if row is None or row["ivtff_group_raw"] != ent["form"] or row.get("meaning") != ent["meaning"] or row.get("type") != ent["denoted_or_syntax_type"] or row.get("lexical_status") != "assigned_exact":
                mismatch.append((ent["form"], sid, None if row is None else (row["ivtff_group_raw"],row.get("meaning"),row.get("type"),row.get("lexical_status"))))
    check("each_lexicon_assignment_exact", not mismatch, repr(mismatch[:5]))
    assigned_by_ed = {e:sum(x["lexical_status"] == "assigned_exact" for x in by_edition[e]) for e in by_edition}
    unassigned_by_ed = {e:sum(x["lexical_status"] != "assigned_exact" for x in by_edition[e]) for e in by_edition}
    check("alternate_and_outside_assignment_totals", assigned_by_ed == {"ZL3b":122,"IT2a":114,"RF1b":106} and unassigned_by_ed == {"ZL3b":34,"IT2a":43,"RF1b":54}, f"assigned={assigned_by_ed}, unassigned={unassigned_by_ed}")
    # Outside lexical assignments, explicitly separate from selected unassigned alternatives.
    outside_assigned = {e:sum(x["block"]=="OUTSIDE" and x["lexical_status"]=="assigned_exact" for x in by_edition[e]) for e in by_edition}
    selected_unassigned = {e:sum(x["block"]!="OUTSIDE" and x["lexical_status"]!="assigned_exact" for x in by_edition[e]) for e in by_edition}
    check("outside47_and_selected_gaps", outside_assigned == {"ZL3b":14,"IT2a":18,"RF1b":15} and selected_unassigned == {"ZL3b":0,"IT2a":11,"RF1b":18}, f"outside={outside_assigned}; gaps={selected_unassigned}")
    check("all_unassigned_occurrences_marked", all(x.get("meaning") is None and x.get("type") is None for x in occs if x["lexical_status"] != "assigned_exact"))
    checks["meaning_or_grammar_semantically_executed"] = False
    checks["complete_source_equivalence_proven"] = False
    result = {
      "schema":"recipient_replay_b.v1",
      "inputs":{"projection":"experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv","projection_sha256":proj_hash,"draft":"research_registry/proposals/laufenberg_f85r2_20260926/RECIPIENT_AUTHOR_DRAFT.json","draft_sha256":sha(DRAFT),"contract_sha256":sha(CONTRACT)},
      "counts":{"rows":len(rows),"selected":len(selected),"outside":len(outside),"clauses":len(d["clauses"]),"lexical_types":len(lex),"assigned_occurrences":len(lex_ids),"outside_assigned":outside_assigned,"selected_unassigned":selected_unassigned,"assigned_by_edition":assigned_by_ed,"unassigned_by_edition":unassigned_by_ed},
      "checks":checks,
      "errors":errors,
      "scope":"Literal/index/reference-target bookkeeping replay only. Manual type/scope/source review is in RECIPIENT_REPLAY_B.md; this script is not a semantic parser or meaning validator."
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"all_checks_pass":not errors,"checks":checks,"errors":errors},ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)

if __name__ == "__main__": main()
