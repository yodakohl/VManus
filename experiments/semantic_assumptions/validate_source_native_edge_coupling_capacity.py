#!/usr/bin/env python3
"""Independent reconstruction of the target-masked edge-coupling panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CONSENSUS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
ORDER_VALIDATION = RESULTS / "source_native_internal_order_validation.json"
SPEC = BASE / "SOURCE_NATIVE_EDGE_COUPLING_CAPACITY_SPEC.md"
PRODUCER = BASE / "build_source_native_edge_coupling_capacity.py"
PRODUCTION = RESULTS / "source_native_edge_coupling_capacity.json"
PANEL = RESULTS / "source_native_edge_coupling_masked.tsv"
PRODUCTION_REPORT = RESULTS / "source_native_edge_coupling_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_edge_coupling_capacity_validation.json"
REPORT = RESULTS / "source_native_edge_coupling_capacity_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CONSENSUS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    ORDER_VALIDATION: "f41e44fda5d05fbd44a4fabdcfbec077dccdf045cdbbd6c90dad30794c5cf53a",
    SPEC: "b018f4c7601a53f614d26082c4df536d41307faa62e2fcdc1cf088e61e409917",
    PRODUCER: "b7d4cd2e3649ed98328b4ef2bf0d89163a1bb6df19dd50fd9bcfe902337b5e26",
    PRODUCTION: "e3b7d7bf6f59472a0ecbfb1987d76f6943a21dcba13d19baab7c61075ab7e547",
    PANEL: "db78519f12283f6ac2ae30e0e8898c769f1491f8d48dae1733b5de703154e82c",
    PRODUCTION_REPORT: "3a09f261a87d052b57d62e78f1d32e3ecacee157143136eea3034c7c3ca11d05",
}
FIELDS = [
    "unit_id", "consensus_group_id", "locus", "page", "physical_folio",
    "section", "currier", "hand", "kind", "locus_position", "symbol_count",
    "length_bin", "opening_family", "core_first_family", "core_last_family",
    "baseline_cell", "full_cell", "masked_family_surface",
    "outside_folio_baseline_support", "outside_folio_full_support", "target_eligible",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return stream.getvalue().encode()


def main():
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite edge-coupling validation")
    checks = 0
    def require(value, label):
        nonlocal checks
        checks += 1
        if not value: raise AssertionError(label)
    for path, expected in HASHES.items(): require(sha(path) == expected, f"hash {path.name}")
    require(json.loads(CONSENSUS_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION", "consensus validation")
    require(json.loads(EDGE_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION", "edge validation")
    require(json.loads(ORDER_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_INTERNAL_ORDER_NONCONFIRM_RECONSTRUCTION", "order validation")

    rows = []
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            surface = source["family_surface"]
            if source["strict_zero_alternative"] != "1" or source["grammar_scope"] != "CONFIRMED_PROSE" or len(surface) < 3: continue
            match = re.match(r"f\d+", source["page"])
            if not match: continue
            index, count = int(source["consensus_group_index"]), int(source["consensus_group_count"])
            position = "SINGLE" if count == 1 else ("FIRST" if index == 1 else ("LAST" if index == count else "MIDDLE"))
            length_bin = min(len(surface), 8)
            baseline = (surface[1], surface[-2], length_bin, position, source["currier"])
            full = (*baseline, surface[0])
            rows.append({
                "unit_id": source["consensus_group_id"], "consensus_group_id": source["consensus_group_id"],
                "locus": source["locus"], "page": source["page"], "physical_folio": match.group(),
                "section": source["section"], "currier": source["currier"], "hand": source["hand"], "kind": source["kind"],
                "locus_position": position, "symbol_count": len(surface), "length_bin": length_bin,
                "opening_family": surface[0], "core_first_family": surface[1], "core_last_family": surface[-2],
                "baseline_cell": "|".join(map(str, baseline)), "full_cell": "|".join(map(str, full)),
                "masked_family_surface": surface[:-1]+"#",
            })
    rows.sort(key=lambda row: row["unit_id"])
    require(len({row["unit_id"] for row in rows}) == len(rows), "unit IDs")
    total_base, total_full = Counter(row["baseline_cell"] for row in rows), Counter(row["full_cell"] for row in rows)
    folio_base = Counter((row["physical_folio"],row["baseline_cell"]) for row in rows)
    folio_full = Counter((row["physical_folio"],row["full_cell"]) for row in rows)
    for row in rows:
        bs = total_base[row["baseline_cell"]]-folio_base[row["physical_folio"],row["baseline_cell"]]
        fs = total_full[row["full_cell"]]-folio_full[row["physical_folio"],row["full_cell"]]
        row["outside_folio_baseline_support"] = bs; row["outside_folio_full_support"] = fs
        row["target_eligible"] = int(bs >= 20 and fs >= 5)
        require(row["masked_family_surface"].count("#") == 1, "mask count")
    require(render(rows) == PANEL.read_bytes(), "panel bytes")
    eligible = [row for row in rows if row["target_eligible"]]
    require(len(rows)==19203 and len(eligible)==14955, "row counts")
    require(len({row["physical_folio"] for row in eligible})==94, "folios")
    require(all(row["outside_folio_baseline_support"]>=20 and row["outside_folio_full_support"]>=5 for row in eligible), "supports")

    production=json.loads(PRODUCTION.read_text())
    require(production["status"]=="PASS_TARGET_MASKED_EDGE_COUPLING_CAPACITY", "status")
    require(production["inputs"]=={path.name:sha(path) for path in (GROUPS,CONSENSUS_VALIDATION,EDGE_VALIDATION,ORDER_VALIDATION,SPEC,PRODUCER)}, "inputs")
    expected={
        "all_masked_groups":len(rows), "all_physical_folios":len({r['physical_folio'] for r in rows}),
        "eligible_groups":len(eligible), "eligible_physical_folios":len({r['physical_folio'] for r in eligible}),
        "eligible_by_currier":dict(sorted(Counter(r['currier'] for r in eligible).items())),
        "eligible_opening_families":len({r['opening_family'] for r in eligible}),
        "eligible_baseline_cells":len({r['baseline_cell'] for r in eligible}), "panel_sha256":sha(PANEL), "schema":FIELDS,
    }
    for key,value in expected.items(): require(production[key]==value,f"production {key}")
    require(all(production["gates"].values()), "gates")
    require(production["target_outcomes_stored"]==production["target_scores_computed"]==production["english_glosses"]==0,"zero target")
    expected_report=f"""# Source-native opening/closing edge-coupling capacity

Status: **{production['status']}**

The target-masked panel contains **{len(rows):,}** synchronized prose groups on
**94** physical folios. Exact immediate-core, length, locus-position, Currier,
and leave-folio support gates retain **{len(eligible):,}** groups on all 94
folios, spanning both Currier registers, **{expected['eligible_opening_families']}**
opening families, and **{expected['eligible_baseline_cells']}** baseline cells.

The final STA family is replaced by `#`; no target outcome, complete surface,
score, p-value, or English gloss is stored. This authorizes synthetic
calibration only and establishes no affix, circumfix, word, language, meaning,
plaintext, or translation.
"""
    require(PRODUCTION_REPORT.read_text()==expected_report,"report")
    result={"experiment":"SOURCE_NATIVE_EDGE_COUPLING_CAPACITY_VALIDATION","status":"PASS_INDEPENDENT_TARGET_MASKED_CAPACITY_RECONSTRUCTION","checks":checks,"validator_sha256":sha(VALIDATOR),"production_sha256":sha(PRODUCTION),"panel_sha256":sha(PANEL),"all_groups":len(rows),"eligible_groups":len(eligible),"physical_folios":94,"target_outcomes_stored":0,"target_scores_computed":0,"failures":[],"claim_ceiling":production["claim_ceiling"]}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    REPORT.write_text(f"""# Source-native edge-coupling capacity validation

Status: **{result['status']}**

A nonimporting implementation reconstructed all **{len(rows):,}** masked rows,
all **{len(eligible):,}** leave-folio-eligible rows on 94 folios, every cell,
support, exact TSV and report byte, input binding, and zero-target gate in
**{checks:,}** checks. This validates calibration capacity only; no coupling,
word, meaning, plaintext, or translation follows.
""")
    print(json.dumps({"status":result["status"],"checks":checks,"eligible":len(eligible)},sort_keys=True))


if __name__=="__main__": main()
