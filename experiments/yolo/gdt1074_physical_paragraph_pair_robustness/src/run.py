#!/usr/bin/env python3
"""Project physical paragraph flags to RF1b for frozen exact pX/yX pairs."""
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "artifacts"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
FROZEN = ROOT / "experiments/yolo/gdt1073_py_initial_pair_paragraph_scope/artifacts/PAIRS.tsv"
FROZEN_HASH = "114719341ea3db9afe5d2a9fd93f038dbc93c0e0b350ef28949f31c72a18f841"
COLS = "edition,page,locus,kind,source_group_index,paragraph_start,left_separator,right_separator,ivtff_group_raw"
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def write_tsv(path, rows, fields):
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    assert hashlib.sha256(FROZEN.read_bytes()).hexdigest() == FROZEN_HASH
    with FROZEN.open(newline="") as file:
        bases = sorted({r["base"] for r in csv.DictReader(file, delimiter="\t")})
    assert len(bases) == 47
    forms = {lead + base: (base, lead) for base in bases for lead in "py"}
    with ALLOW.open(newline="") as file:
        pages = [r["page"] for r in csv.DictReader(file, delimiter="\t")]
    assert len(pages) == 179 and not any(p.startswith("f84") for p in pages)
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE), "--selector", "page",
           "--columns", COLS, "--forbid-prefix", "f84"]
    for p in pages:
        cmd.extend(["--allow", p])
    got = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(got.stdout), delimiter="\t"))
    assert not any(r["page"].startswith("f84") for r in rows)
    first = [r for r in rows if r["kind"] == "P" and r["source_group_index"] == "1"]
    by_locus = defaultdict(dict)
    for r in first:
        if r["edition"] in by_locus[r["locus"]]:
            raise ValueError("duplicate edition/locus first group")
        by_locus[r["locus"]][r["edition"]] = r
    physical = {}
    for locus, ed in by_locus.items():
        if "ZL3b" in ed and "IT2a" in ed:
            z, i = ed["ZL3b"]["paragraph_start"], ed["IT2a"]["paragraph_start"]
            if z == i and z in {"0", "1"}:
                physical[locus] = z
    events = []
    for r in first:
        f = r["ivtff_group_raw"]
        if f not in forms:
            continue
        base, lead = forms[f]
        right_ok = r["right_separator"] in {"DEFINITE_SPACE", "LINE_END"}
        left_ok = r["left_separator"] == "LINE_START"
        owner_ok = r["locus"] in physical
        reason = "INCLUDED" if right_ok and left_ok and owner_ok else (
            "UNCERTAIN_BOUNDARY" if not right_ok or not left_ok else "NO_PHYSICAL_FLAG")
        events.append(dict(base=base, edition=r["edition"], form=f,
            lead=lead, locus=r["locus"], physical_folio=re.match(r"f\d+",r["page"]).group(),
            right_separator=r["right_separator"], status=reason,
            physical_paragraph_start=physical.get(r["locus"],"NA")))
    events.sort(key=lambda r:(r["base"],r["edition"],r["locus"],r["form"]))
    OUT.mkdir(exist_ok=True)
    write_tsv(OUT / "EVENTS.tsv", events, list(events[0]))
    pairs = []
    for base in bases:
        for edition in EDITIONS:
            e = [x for x in events if x["base"] == base and x["edition"] == edition]
            p = [x for x in e if x["lead"] == "p" and x["status"] == "INCLUDED"]
            y = [x for x in e if x["lead"] == "y" and x["status"] == "INCLUDED"]
            ps = sum(x["physical_paragraph_start"] == "1" for x in p)
            ys = sum(x["physical_paragraph_start"] == "1" for x in y)
            pf = len({x["physical_folio"] for x in p})
            yf = len({x["physical_folio"] for x in y})
            support = len(p)>=3 and len(y)>=3 and pf>=2 and yf>=2
            direction = "NO_PAIR" if not p or not y else (
                "P_GREATER" if ps*len(y)>ys*len(p) else
                "Y_GREATER" if ps*len(y)<ys*len(p) else "EQUAL")
            pairs.append(dict(base=base,edition=edition,p_initial=len(p),p_starts=ps,
                p_folios=pf,y_initial=len(y),y_starts=ys,y_folios=yf,
                excluded_uncertain=sum(x["status"]=="UNCERTAIN_BOUNDARY" for x in e),
                excluded_no_physical_flag=sum(x["status"]=="NO_PHYSICAL_FLAG" for x in e),
                supported=int(support),direction=direction))
    write_tsv(OUT / "PAIRS.tsv",pairs,list(pairs[0]))
    shared = [base for base in bases if all(next(r for r in pairs if r["base"]==base
              and r["edition"]==edition)["supported"] for edition in EDITIONS)]
    pass_direction = bool(len(shared)>=3 and all(r["direction"]=="P_GREATER"
        for r in pairs if r["base"] in shared))
    summary={"guard":got.stderr.strip(),"selected_rows":len(rows),
        "physical_consensus_loci":len(physical),
        "first_group_loci_without_consensus":sum(x not in physical for x in by_locus),
        "event_statuses":dict(Counter(e["status"] for e in events)),
        "fixed_bases":len(bases),"supported_by_reader":{ed:sum(r["edition"]==ed and r["supported"] for r in pairs)
                                                   for ed in EDITIONS},
        "supported_all_three_bases":shared,
        "primary_decision":"ROBUST_FORMAL_DIRECTION" if pass_direction else
                           "CAPACITY_STOP" if len(shared)<3 else "FORMAL_DIRECTION_NOT_UNIVERSAL",
        "claim_ceiling":"Same-manuscript structural robustness only; no p/y meaning or translation."}
    (OUT / "RESULT.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
