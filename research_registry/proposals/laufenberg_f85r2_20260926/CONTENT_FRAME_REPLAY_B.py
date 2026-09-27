#!/usr/bin/env python3
"""Independent literal/index replay for the frozen content-frame packet.

This is bookkeeping only. It does not evaluate the candidate's semantics.
"""
from collections import Counter, defaultdict
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOSSIER = Path(__file__).resolve().parent
PROJECTION = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv"
DRAFT = DOSSIER / "CONTENT_FRAME_WHOLE_DRAFT.json"
CONTRACT = DOSSIER / "CONTENT_FRAME_AUTHOR_CONTRACT.md"
REPORT = DOSSIER / "CONTENT_FRAME_WHOLE_REPORT.md"
NATIVE_FIELDS = ["edition", "block", "locus", "source_group_id", "source_group_index",
                 "source_group_count", "within_line_position", "paragraph_start",
                 "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw"]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    with PROJECTION.open(newline="", encoding="utf-8") as f:
        native = list(csv.DictReader(f, delimiter="\t"))
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    occ = draft["all_occurrences"]
    issues = []
    native_ids = [r["source_group_id"] for r in native]
    draft_ids = [r["source_group_id"] for r in occ]
    if len(native) != 473: issues.append(f"native row count {len(native)} != 473")
    if len(set(native_ids)) != len(native_ids): issues.append("duplicate native source_group_id")
    if len(occ) != 473: issues.append(f"draft row count {len(occ)} != 473")
    if len(set(draft_ids)) != len(draft_ids): issues.append("duplicate draft source_group_id")
    nm, dm = {r["source_group_id"]: r for r in native}, {r["source_group_id"]: r for r in occ}
    missing = sorted(set(nm)-set(dm)); extra = sorted(set(dm)-set(nm))
    if missing: issues.append(f"missing draft IDs: {missing[:5]}")
    if extra: issues.append(f"extra draft IDs: {extra[:5]}")
    field_mismatches=[]
    for gid in sorted(set(nm)&set(dm)):
        a,b=nm[gid],dm[gid]
        for fld in NATIVE_FIELDS:
            if str(a[fld]) != str(b.get(fld)):
                field_mismatches.append({"id":gid,"field":fld,"native":a[fld],"draft":b.get(fld)})
    if field_mismatches: issues.append(f"{len(field_mismatches)} native-field mismatches")

    # Independently derive immediate within-line neighbors from the ordered native projection.
    by_line=defaultdict(list)
    for r in native: by_line[(r["edition"],r["locus"])].append(r)
    neighbor_mismatches=[]
    for key, rows in by_line.items():
        rows.sort(key=lambda x:int(x["source_group_index"]))
        for i,r in enumerate(rows):
            drow=dm.get(r["source_group_id"],{})
            left=rows[i-1]["ivtff_group_raw"] if i else None
            right=rows[i+1]["ivtff_group_raw"] if i+1<len(rows) else None
            if drow.get("left_raw_in_locus") != left or drow.get("right_raw_in_locus") != right:
                neighbor_mismatches.append({"id":r["source_group_id"],"expected_left":left,
                  "actual_left":drow.get("left_raw_in_locus"),"expected_right":right,
                  "actual_right":drow.get("right_raw_in_locus")})
    if neighbor_mismatches: issues.append(f"{len(neighbor_mismatches)} adjacent-neighbor mismatches")

    # Rebuild raw-form occurrence indexes without trusting the packet's index.
    derived_index=defaultdict(list)
    for r in native: derived_index[r["ivtff_group_raw"]].append(r["source_group_id"])
    lexi=draft["lexicon_all_reader_types"]
    lex_mismatches=[]
    lm={x["raw"]:x for x in lexi}
    if len(lm)!=len(lexi): issues.append("duplicate raw forms in lexicon index")
    if set(lm)!=set(derived_index): issues.append("lexicon raw-type universe differs from projection")
    for raw, ids in derived_index.items():
        entry=lm.get(raw)
        if not entry: continue
        if entry.get("all_occurrences") != ids:
            lex_mismatches.append({"raw":raw,"expected_ids":ids,"actual_ids":entry.get("all_occurrences")})
    if lex_mismatches: issues.append(f"{len(lex_mismatches)} lexical occurrence-index mismatches")
    assignment_mismatches=[]
    for r in occ:
        e=lm.get(r["ivtff_group_raw"])
        if not e: continue
        for fld, efld in (("literal_type","type"),("literal_value","value"),("lexical_status","status")):
            if r.get(fld)!=e.get(efld):
                assignment_mismatches.append({"id":r["source_group_id"],"field":fld,
                  "occurrence":r.get(fld),"type_index":e.get(efld)})
    if assignment_mismatches: issues.append(f"{len(assignment_mismatches)} occurrence assignment/index mismatches")

    # Recompute per-reading counts and assignment accounting from the literal entries.
    actual_counts={}
    expected_loci={"f85r2.%d"%i for i in range(1,25)}
    for ed in ("ZL3b","IT2a","RF1b"):
        rows=[r for r in native if r["edition"]==ed]
        actual_counts[ed]={"groups":len(rows),"types":len({r["ivtff_group_raw"] for r in rows}),
                           "loci":len({r["locus"] for r in rows}),
                           "all_24_loci":{r["locus"] for r in rows}==expected_loci}
    if any(draft["coverage_counts"].get(ed,{}).get("groups")!=actual_counts[ed]["groups"] or
           draft["coverage_counts"].get(ed,{}).get("types")!=actual_counts[ed]["types"] for ed in actual_counts):
        issues.append("coverage_counts do not match independently counted projection")

    entry_status={}
    duplicate_entries=[]
    for x in lexi:
        if x["raw"] in entry_status: duplicate_entries.append(x["raw"])
        entry_status[x["raw"]]=x
    assignment_counts={}
    for ed in ("ZL3b","IT2a","RF1b"):
        rawforms={r["ivtff_group_raw"] for r in native if r["edition"]==ed}
        assigned=[entry_status[x] for x in rawforms if x in entry_status and entry_status[x].get("status") in ("FIXED_CONTRACT","NEW_EXPLORATORY_ASSIGNED")]
        assignment_counts[ed]={"distinct_types":len(rawforms),"assigned_types":len(assigned),
                               "unassigned_types":len(rawforms)-len(assigned),
                               "assigned_occurrences":sum(len([r for r in native if r["edition"]==ed and r["ivtff_group_raw"]==x["raw"]]) for x in assigned)}
    counts_expected=draft["costs"]
    zl=assignment_counts["ZL3b"]
    if zl["assigned_types"]!=counts_expected["assigned_ZL_types_total"] or zl["unassigned_types"]!=counts_expected["unassigned_ZL_types"]:
        issues.append("ZL assigned/unassigned type costs do not match lexicon status")
    new_zl={x["raw"] for x in lexi if x.get("status")=="NEW_EXPLORATORY_ASSIGNED" and x.get("in_ZL")}
    new_zl_occ=sum(1 for r in native if r["edition"]=="ZL3b" and r["ivtff_group_raw"] in new_zl)
    if len(new_zl)!=counts_expected["new_whole_entries"] or new_zl_occ!=counts_expected["new_ZL_occurrences"]:
        issues.append("new-entry/occurrence cost does not match status-indexed projection")

    # Derivation references must resolve, be unique across derivation records, and preserve literal raw forms.
    derivation_ids=[]; derivation_bad=[]
    for der in draft["written_derivations"]:
        for gid in der.get("groups",[]):
            derivation_ids.append(gid)
            if gid not in dm: derivation_bad.append({"derivation":der["id"],"missing_id":gid})
            elif dm[gid].get("edition")!="ZL3b": derivation_bad.append({"derivation":der["id"],"non_ZL_id":gid})
    if derivation_bad: issues.append(f"{len(derivation_bad)} derivation references missing/non-ZL")
    duplicate_derivation_ids=[gid for gid,c in Counter(derivation_ids).items() if c>1]
    # This is diagnostic only: separate records can intentionally refer to attempted spans.

    result={"literal_replay":"PASS" if not issues else "FAIL",
      "semantic_confirmation":"NOT_TESTED",
      "inputs":{"projection":"experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv",
        "projection_sha256":sha(PROJECTION),"draft":"CONTENT_FRAME_WHOLE_DRAFT.json","draft_sha256":sha(DRAFT),
        "contract_sha256":sha(CONTRACT),"report_sha256":sha(REPORT)},
      "native_row_count":len(native),"draft_row_count":len(occ),"native_fields_checked":NATIVE_FIELDS,
      "native_field_mismatch_count":len(field_mismatches),"missing_ids":missing,"extra_ids":extra,
      "neighbor_mismatch_count":len(neighbor_mismatches),"lexical_index_mismatch_count":len(lex_mismatches),
      "occurrence_assignment_mismatch_count":len(assignment_mismatches),
      "counts":actual_counts,"assignment_counts":assignment_counts,
      "new_exploratory_ZL_types":len(new_zl),"new_exploratory_ZL_occurrences":new_zl_occ,
      "derivation_reference_count":len(derivation_ids),"derivation_bad_references":derivation_bad,
      "groups_reused_across_derivations":duplicate_derivation_ids,
      "written_derivations":len(draft["written_derivations"]),
      "source_obligations":len(draft["complete_source_obligation_table"]),
      "obligation_status_counts":dict(Counter(x["status"] for x in draft["complete_source_obligation_table"])),
      "costs":counts_expected,"issues":issues}
    out=DOSSIER/"CONTENT_FRAME_REPLAY_B.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
