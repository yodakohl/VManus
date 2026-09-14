#!/usr/bin/env python3
"""GDT947 fixed exact ol-form paragraph-reference census."""
import csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
EDS = ["ZL3b", "IT2a", "RF1b"]
BOUND = {"DEFINITE_SPACE", "LINE_START", "LINE_END"}
DESIGN = {77, 80, 85}
GENERATED = {}
WRITE_ENABLED = False

def load(rel):
    return json.loads((R / rel).read_text(encoding="utf-8"))

def write(rel, value):
    p = E / "artifacts" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    GENERATED[rel] = value
    if WRITE_ENABLED:
        p.write_text(value, encoding="utf-8")

def tsv(rows, fields):
    import io
    s = io.StringIO()
    w = csv.DictWriter(s, fieldnames=fields, delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    return s.getvalue()

def leaf(page):
    m = re.match(r"f(\d+)", page)
    return int(m.group(1)) if m else -1

def definite(r):
    return r["left_separator"] in BOUND and r["right_separator"] in BOUND

def alphabetic(raw):
    return bool(re.fullmatch(r"[a-z]+", raw))

def build():
    GENERATED.clear()
    # Lock verification is deliberately the first census operation.
    lock = load("experiments/yolo/gdt947_ol_content_reference_direction/PREREG_LOCK.json")
    for rel, expected in lock["files"].items():
        got = hashlib.sha256((R / rel).read_bytes()).hexdigest()
        if got != expected:
            raise RuntimeError(f"frozen lock mismatch: {rel}: {got} != {expected}")
    model = load("experiments/yolo/gdt947_ol_content_reference_direction/src/MODEL.json")
    allow = set(load(model["allow_source"])["allowed_selectors"])
    assert len(allow) == 179
    assert not any(p.startswith("f84") or p == "f116v" for p in allow)

    lines = {}
    for rel in model["sources"]:
        src = load(rel)
        for line in src["lines"]:
            md = line["metadata"]
            assert md["page"] in allow
            key = (md["edition"], md["locus"])
            assert key not in lines
            lines[key] = [dict(md, **dict(zip(src["group_columns"], g))) for g in line["groups"]]

    forms = dict(model["primary_forms"]); forms.update(model["family_diagnostics"])
    family = {f: ("PRIMARY" if f in model["primary_forms"] else "DIAGNOSTIC") for f in forms}
    occurrences, by_locus = [], defaultdict(list)
    for key, rows in lines.items():
        for r in rows:
            raw = r["ivtff_group_raw"]
            if raw not in forms: continue
            occurrences.append({
                "source_group_id": r["source_group_id"], "edition": r["edition"], "page": r["page"],
                "locus": r["locus"], "form": raw, "core": forms[raw], "family": family[raw],
                "physical_leaf": leaf(r["page"]), "exposure": "DESIGN_LEAF" if leaf(r["page"]) in DESIGN else "OTHER_EXPOSED_LEAF",
                "paragraph_id": "", "left_separator": r["left_separator"], "right_separator": r["right_separator"]
            })
            by_locus[key].append(r)

    # Own-edition paragraphs only. RF intentionally has no paragraph capacity.
    paragraphs = load(model["paragraph_source"])
    para_by_line, selected_paras = {}, []
    target_loci = {(r["edition"], r["locus"]) for r in occurrences}
    for ed in EDS:
        for p in paragraphs.get(ed, []):
            if any((ed, line["locus"]) in target_loci for line in p["lines"]):
                selected_paras.append((ed, p))
                for line in p["lines"]: para_by_line[(ed, line["locus"])] = p["id"]
    for r in occurrences: r["paragraph_id"] = para_by_line.get((r["edition"], r["locus"]), "")

    para_groups = {}
    for ed, p in selected_paras:
        seq = []
        for line in p["lines"]:
            rr = lines[(ed, line["locus"])]
            assert line["words"] == [x["ivtff_group_raw"] for x in rr]
            assert line["source_ids"] == [x["source_group_id"] for x in rr]
            seq.extend(rr)
        para_groups[(ed, p["id"])] = seq

    cases = []
    for o in occurrences:
        para_id = o["paragraph_id"]; seq = para_groups.get((o["edition"], para_id), [])
        idx = next((i for i, x in enumerate(seq) if x["source_group_id"] == o["source_group_id"]), None)
        for direction in model["directions"]:
            anchor_ids, uncertainty_ids = [], []
            if not para_id:
                status = "NO_PARAGRAPH_CAPACITY"
            elif not definite(next(x for x in seq if x["source_group_id"] == o["source_group_id"])):
                status = "TARGET_BOUNDARY_UNCERTAIN"
            else:
                side = seq[:idx] if direction == "BACK" else seq[idx + 1:]
                for x in side:
                    if x["ivtff_group_raw"] == forms[o["form"]] and definite(x): anchor_ids.append(x["source_group_id"])
                    if not alphabetic(x["ivtff_group_raw"]) or not definite(x): uncertainty_ids.append(x["source_group_id"])
                if anchor_ids: status = "WRITTEN_ANCHOR_PRESENT"
                elif uncertainty_ids: status = "UNRESOLVED_SOURCE"
                else: status = "MISSING_WRITTEN_ANCHOR"
            cases.append({**o, "direction": direction, "status": status,
                          "anchor_ids": "|".join(anchor_ids), "uncertainty_ids": "|".join(uncertainty_ids)})

    occ_fields = ["source_group_id", "edition", "page", "locus", "form", "core", "family", "physical_leaf", "exposure", "paragraph_id", "left_separator", "right_separator"]
    case_fields = occ_fields + ["direction", "status", "anchor_ids", "uncertainty_ids"]
    write("OCCURRENCES.tsv", tsv(occurrences, occ_fields)); write("CASES.tsv", tsv(cases, case_fields))
    write("OUTSIDE_PARAGRAPH.tsv", tsv([o for o in occurrences if not o["paragraph_id"]], occ_fields))

    # Preserve every whole source line at every target locus across all six bound snapshots.
    target_locus_names = {locus for _, locus in target_loci}
    source_context = {f"{ed}|{locus}": {"edition": ed, "locus": locus, "groups": rows} for (ed, locus), rows in sorted(lines.items()) if locus in target_locus_names}
    write("SOURCE_CONTEXT.json", json.dumps(source_context, ensure_ascii=False, separators=(",", ":")) + "\n")
    para_context = []
    for ed, p in selected_paras:
        para_context.append({"edition": ed, "paragraph_id": p["id"], "page": p["page"], "leaf": p["leaf"], "lines": [{"locus": l["locus"], "row": l.get("row"), "groups": lines[(ed, l["locus"])]} for l in p["lines"]]})
    write("PARAGRAPH_CONTEXT.json", json.dumps(para_context, ensure_ascii=False, separators=(",", ":")) + "\n")

    summary, statuses = [], ["NO_PARAGRAPH_CAPACITY", "TARGET_BOUNDARY_UNCERTAIN", "WRITTEN_ANCHOR_PRESENT", "UNRESOLVED_SOURCE", "MISSING_WRITTEN_ANCHOR"]
    for form in forms:
        for ed in EDS:
            for direction in model["directions"]:
                for exposure in ["DESIGN_LEAF", "OTHER_EXPOSED_LEAF"]:
                    rows = [c for c in cases if c["form"] == form and c["edition"] == ed and c["direction"] == direction and c["exposure"] == exposure]
                    if not rows: continue
                    cc = Counter(c["status"] for c in rows)
                    if cc["MISSING_WRITTEN_ANCHOR"]: decision = "REJECT_MISSING_WRITTEN_ANCHOR"
                    elif cc["NO_PARAGRAPH_CAPACITY"]: decision = "NO_PARAGRAPH_CAPACITY"
                    elif cc["TARGET_BOUNDARY_UNCERTAIN"]: decision = "TARGET_BOUNDARY_UNCERTAIN"
                    else: decision = "COMPATIBLE_OR_UNRESOLVED"
                    summary.append({"form": form, "core": forms[form], "family": family[form], "edition": ed, "direction": direction, "exposure": exposure, "occurrence_count": len(rows), **{s.lower(): cc[s] for s in statuses}, "decision": decision})
    sum_fields = ["form", "core", "family", "edition", "direction", "exposure", "occurrence_count"] + [s.lower() for s in statuses] + ["decision"]
    write("SUMMARY.tsv", tsv(summary, sum_fields))

    # Contract-level decisions across every edition/exposure, plus the two-form conjunction.
    candidate_rows = []
    for direction in model["directions"]:
        for form in model["primary_forms"]:
            rows = [c for c in cases if c["form"] == form and c["direction"] == direction]
            cc = Counter(c["status"] for c in rows)
            decision = ("REJECT_MISSING_WRITTEN_ANCHOR" if cc["MISSING_WRITTEN_ANCHOR"] else
                        "NO_PARAGRAPH_CAPACITY" if cc["NO_PARAGRAPH_CAPACITY"] else
                        "TARGET_BOUNDARY_UNCERTAIN" if cc["TARGET_BOUNDARY_UNCERTAIN"] else
                        "COMPATIBLE_OR_UNRESOLVED")
            candidate_rows.append({"candidate": form, "forms": form, "family": "PRIMARY", "direction": direction, "occurrence_count": len(rows), **{s.lower(): cc[s] for s in statuses}, "decision": decision, "meaning_confirmed": "FALSE"})
        rows = [c for c in cases if c["form"] in model["primary_forms"] and c["direction"] == direction]
        cc = Counter(c["status"] for c in rows)
        decision = ("REJECT_MISSING_WRITTEN_ANCHOR" if cc["MISSING_WRITTEN_ANCHOR"] else
                    "NO_PARAGRAPH_CAPACITY" if cc["NO_PARAGRAPH_CAPACITY"] else
                    "TARGET_BOUNDARY_UNCERTAIN" if cc["TARGET_BOUNDARY_UNCERTAIN"] else
                    "COMPATIBLE_OR_UNRESOLVED")
        candidate_rows.append({"candidate": "JOINT_PRIMARY", "forms": "|".join(model["primary_forms"]), "family": "PRIMARY_CONJUNCTION", "direction": direction, "occurrence_count": len(rows), **{s.lower(): cc[s] for s in statuses}, "decision": decision, "meaning_confirmed": "FALSE"})
    candidate_fields = ["candidate", "forms", "family", "direction", "occurrence_count"] + [s.lower() for s in statuses] + ["decision", "meaning_confirmed"]
    write("CANDIDATE_DECISIONS.tsv", tsv(candidate_rows, candidate_fields))

    all_counts = Counter(c["status"] for c in cases)
    result = {"experiment": "GDT947", "status": "CENSUS_COMPLETE_CONDITIONAL_REFERENCE_AUDIT", "lock_verified": True, "allowed_selectors": len(allow), "sealed": ["f84", "f84r"], "source_groups": sum(len(v) for v in lines.values()), "occurrence_count": len(occurrences), "case_count": len(cases), "paragraph_count": len(selected_paras), "outside_paragraph_occurrences": len([o for o in occurrences if not o["paragraph_id"]]), "statuses": dict(all_counts), "primary_forms": list(model["primary_forms"]), "diagnostic_forms": list(model["family_diagnostics"]), "directions": model["directions"], "decision_precedence": ["NO_PARAGRAPH_CAPACITY", "TARGET_BOUNDARY_UNCERTAIN", "MISSING_WRITTEN_ANCHOR"], "confirmed_words": 0, "independent_meaning_tests": 0, "significance_claim": False, "rf_paragraph_policy": "NO_PARAGRAPH_CAPACITY; no ZL/IT paragraph borrowing", "artifacts": ["OCCURRENCES.tsv", "CASES.tsv", "SUMMARY.tsv", "CANDIDATE_DECISIONS.tsv", "OUTSIDE_PARAGRAPH.tsv", "SOURCE_CONTEXT.json", "PARAGRAPH_CONTEXT.json"]}
    write("RESULT.json", json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    write("README.md", """# GDT947 generated artifacts

`OCCURRENCES.tsv` inventories exact raw occurrences of primary `olshedy`/`olshey` and diagnostic `olkain`/`olkeedy`/`olchey`, retaining source IDs, reader, page/locus, leaf, exposure, paragraph ID, and raw separator flags. `CASES.tsv` repeats each occurrence for BACK and FORWARD; `anchor_ids` and `uncertainty_ids` are `|`-joined source IDs.

Per-case precedence is `NO_PARAGRAPH_CAPACITY`, then `TARGET_BOUNDARY_UNCERTAIN`, then written-anchor evaluation. Summary decisions reject when any missing-anchor case exists, even if other cases lack capacity. `CANDIDATE_DECISIONS.tsv` gives primary and joint-primary totals across all editions/exposures. `SOURCE_CONTEXT.json` includes complete raw lines for every target locus across all six snapshots; `PARAGRAPH_CONTEXT.json` preserves complete own-edition target paragraphs. `RESULT.json` records counts and the zero-meaning claim ceiling.
""")
    return dict(GENERATED)

def main():
    global WRITE_ENABLED
    artifacts = build()
    WRITE_ENABLED = True
    for rel, value in artifacts.items(): write(rel, value)
    WRITE_ENABLED = False
    result = json.loads(artifacts["RESULT.json"])
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__": raise SystemExit(main())
