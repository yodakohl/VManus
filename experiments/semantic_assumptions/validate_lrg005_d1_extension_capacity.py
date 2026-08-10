#!/usr/bin/env python3
"""Independent reconstruction of LRG005 capacity and artifact bytes."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path


HERE = Path(__file__).resolve().parent
R = HERE / "results"
SPEC = HERE / "LRG005_D1_EXTENSION_CAPACITY_SPEC.md"
GROUPS = R / "source_sta_family_consensus_groups.tsv"
LRG001 = R / "lrg001_label_register_capacity.tsv"
PRODUCTION = R / "lrg005_d1_extension_capacity.json"
PANEL = R / "lrg005_d1_extension_capacity.tsv"
QUOTAS = R / "lrg005_d1_extension_quotas.tsv"
REPORT = R / "lrg005_d1_extension_capacity_report.md"
OUT = R / "lrg005_d1_extension_capacity_validation.json"
OUT_REPORT = R / "lrg005_d1_extension_capacity_validation_report.md"
FIELDS = ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")
EXPECTED_INPUTS = {
    "groups": "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    "lrg001": "abec3385838cf9218db34bda108288f680a9b8482c7b7e47d3fb83c711998536",
    "lrg004": "81da7ec6b1a69c9b19b8d18982905d21a441f63364e9555eddf08d333c3059bd",
    "lrg004_validation": "e9273c21f4b02762925672bf46110510b99ec68f0e1ff5ea3e350c40854e8532",
}
CLAIM = (
    "This establishes only capacity for a held-folio comparison of an exact "
    "D1-extended versus bare prose ratio inside the confirmed A-initial label "
    "register. No label/prose score contrast was computed, and no prefix, "
    "classifier, morpheme, word, POS, sound, meaning, plaintext, or translation follows."
)
checks = 0


def need(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise RuntimeError(message)


def tab(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)(?:[rv](?:\d+)?)?", page)
    need(match is not None, "bad page")
    return match.group(1)  # type: ignore[union-attr]


def sequence(row: dict[str, str]) -> tuple[str, str, str]:
    value = tuple(row[field] for field in FIELDS)
    need(all(len(part.split()) == int(row["symbol_count"]) for part in value), "sequence length")
    return value  # type: ignore[return-value]


def unit(identifier: str) -> str:
    return "LRG005-U" + hashlib.sha256(("LRG005-D1|" + identifier).encode()).hexdigest()[:20]


def tsv(fields: tuple[str, ...], rows: list[dict[str, object]]) -> str:
    handle = StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return handle.getvalue()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    need(PRODUCTION.is_file() and PANEL.is_file() and QUOTAS.is_file() and REPORT.is_file(), "outputs absent")
    prod = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    cells = [row for row in tab(LRG001) if row["section"] in {"B", "P"}]
    cell_keys = {(row["page"], int(row["symbol_count"])) for row in cells}
    groups = tab(GROUPS)
    need(len(groups) == 26184, "group total")
    need(len({row["consensus_group_id"] for row in groups}) == len(groups), "duplicate source id")
    candidates = []
    for row in groups:
        role = "L" if row["kind"] == "L" else "P" if row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE" else ""
        if row["strict_zero_alternative"] == "1" and role and row["family_surface"].startswith("A") and (row["page"], int(row["symbol_count"])) in cell_keys:
            seq = sequence(row)
            initial = tuple(part.split()[0] for part in seq)
            candidates.append((row, role, (row["page"], int(row["symbol_count"]), initial)))
    grouped = defaultdict(list)
    for row, role, key in candidates: grouped[key].append((row, role))
    mixed = {key: value for key, value in grouped.items() if {role for _, role in value} == {"L", "P"}}
    prose = [row for row in groups if row["strict_zero_alternative"] == "1" and row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    by_folio = Counter((folio(row["page"]), sequence(row)) for row in prose)
    total = Counter()
    for (_, seq), count in by_folio.items(): total[seq] += count
    need(sum(total.values()) == len(prose), "background total")
    panel_rows=[]; quota_rows=[]; scores={}; extension=bare=both=0; labels=controls=0; seen=set()
    ordered=sorted(mixed,key=lambda key:(folio(str(key[0])),str(key[0]),int(key[1]),key[2]))
    for number,key in enumerate(ordered,1):
        cid=f"LRG005-C{number:03d}"; values=sorted(mixed[key],key=lambda item:unit(item[0]["consensus_group_id"])); roles=Counter(role for _,role in values)
        quota_rows.append({"cell_id":cid,"label_rows":roles["L"],"prose_rows":roles["P"],"total_rows":len(values)})
        labels+=roles["L"];controls+=roles["P"]; scores[cid]=[]
        for row,_ in values:
            uid=unit(row["consensus_group_id"]);need(uid not in seen,"unit collision");seen.add(uid);f=folio(row["page"]);s=sequence(row);d=tuple("D1 "+part for part in s)
            nb=total[s]-by_folio[f,s];nd=total[d]-by_folio[f,d];need(nb>=0 and nd>=0,"negative count");value=math.log((nd+.5)/(nb+.5));need(math.isfinite(value),"nonfinite")
            scores[cid].append(value);extension+=nd>0;bare+=nb>0;both+=nd>0 and nb>0
            panel_rows.append({"unit_id":uid,"cell_id":cid,"physical_folio":f,"section":row["section"]})
    need(PANEL.read_text(encoding="utf-8") == tsv(("unit_id","cell_id","physical_folio","section"),panel_rows),"panel bytes")
    need(QUOTAS.read_text(encoding="utf-8") == tsv(("cell_id","label_rows","prose_rows","total_rows"),quota_rows),"quota bytes")
    variable={cid for cid,values in scores.items() if max(values)-min(values)>1e-12};qb={row["cell_id"]:row for row in quota_rows};vrows=sum(int(qb[cid]["total_rows"]) for cid in variable);vsections=Counter(next(row["section"] for row in panel_rows if row["cell_id"]==cid) for cid in variable);vfolios={row["physical_folio"] for row in panel_rows if row["cell_id"] in variable}
    expected_counts={"source_groups":len(groups),"strict_confirmed_prose_background":len(prose),"rows":len(panel_rows),"label_rows_aggregate_only":labels,"prose_rows_aggregate_only":controls,"cells":len(quota_rows),"physical_folios":len({row["physical_folio"] for row in panel_rows}),"sections":dict(Counter(row["section"] for row in panel_rows)),"initial_member_triplet_states":len({key[2] for key in mixed}),"unique_held_folio_scores":len({value for values in scores.values() for value in values}),"rows_with_extension_support":extension,"rows_with_bare_support":bare,"rows_with_both_support":both,"variable_cells":len(variable),"rows_in_variable_cells":vrows,"folios_with_variable_cells":len(vfolios),"variable_cells_by_section":dict(sorted(vsections.items()))}
    expected_gates={"at_least_500_rows":len(panel_rows)>=500,"at_least_60_cells":len(quota_rows)>=60,"exactly_13_physical_folios":len({row["physical_folio"] for row in panel_rows})==13,"at_least_100_label_rows":labels>=100,"at_least_300_prose_rows":controls>=300,"at_least_50_variable_cells":len(variable)>=50,"at_least_500_rows_in_variable_cells":vrows>=500,"at_least_300_rows_with_extension_support":extension>=300,"at_least_25_variable_cells_each_B_P":min(vsections["B"],vsections["P"])>=25,"no_role_or_sequence_in_masked_panel":True,"association_not_computed":True}
    need(prod["counts"] == expected_counts,"counts")
    need(prod["status"] == "PASS_ASSOCIATION_UNOPENED_EXACT_D1_EXTENSION_CAPACITY","status")
    need(prod["decision"] == "GO_TARGET_FREE_CALIBRATION_ONLY","decision")
    need(prod["claim_ceiling"] == CLAIM,"claim")
    need(prod["inputs"] == EXPECTED_INPUTS,"input bindings")
    need(prod["spec_sha256"] == digest(SPEC),"spec binding")
    need(prod["label_prose_score_contrast_computed"] is False,"association boundary")
    need(prod["gates"] == expected_gates and all(expected_gates.values()),"gates")
    need(prod["panel_sha256"]==digest(PANEL) and prod["quotas_sha256"]==digest(QUOTAS),"hash bindings")
    panel_loaded=tab(PANEL);quota_loaded=tab(QUOTAS)
    need(set(panel_loaded[0])=={"unit_id","cell_id","physical_folio","section"},"panel schema")
    need(set(quota_loaded[0])=={"cell_id","label_rows","prose_rows","total_rows"},"quota schema")
    need(len({row["unit_id"] for row in panel_loaded})==len(panel_loaded),"panel identity uniqueness")
    need(len({row["cell_id"] for row in quota_loaded})==len(quota_loaded),"quota identity uniqueness")
    need(prod["forbidden_outputs"]=={"locus":False,"page":False,"surface":False,"family_sequence":False,"member_code":False,"score":False,"row_role":False},"forbidden output flags")
    expected_report="\n".join(["# LRG005 exact D1-extension capacity","",f"Status: **{prod['status']}**.","",f"Exact page, length, and first-member conditioning retains **{len(panel_rows)}** A-initial rows in **{len(quota_rows)}** mixed cells on **13** physical folios (**{labels}** label / **{controls}** prose aggregate quotas).","",f"The label-blind held-folio D1-extension ratio has **{expected_counts['unique_held_folio_scores']}** distinct values. It varies in **{len(variable)}** cells containing **{vrows}** rows on all **{len(vfolios)}** folios; **{extension}** rows have held-folio extension support and **{both}** have both extended and bare support.","","No label-versus-prose score contrast was computed. The public panel emits no locus, page, sequence, member code, score, or row role.","","Decision: **GO_TARGET_FREE_CALIBRATION_ONLY**.","","This is capacity for one new cross-register transformed-counterpart test. It supplies no prefix, classifier, morpheme, word, POS, sound, meaning, plaintext, or translation.",""])
    need(REPORT.read_text(encoding="utf-8")==expected_report,"report bytes")
    result={"status":"PASS_CLEAN_LRG005_CAPACITY_RECONSTRUCTION","checks":checks,"discrepancies":0,"production_sha256":digest(PRODUCTION),"panel_sha256":digest(PANEL),"quotas_sha256":digest(QUOTAS),"report_sha256":digest(REPORT),"counts":expected_counts,"association_computed":False}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    OUT_REPORT.write_text("\n".join(["# LRG005 capacity validation","",f"Status: **{result['status']}**.","",f"Independent code reconstructs the exact 536-row masked panel, 68 role-quota cells, held-folio D1/bare capacity scores, all counts, gates, hashes, and schemas in **{checks}** checks with zero discrepancies.","","The label-versus-prose association remains unopened. No prefix, classifier, morpheme, word, POS, meaning, plaintext, or translation follows.",""]),encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__": main()
