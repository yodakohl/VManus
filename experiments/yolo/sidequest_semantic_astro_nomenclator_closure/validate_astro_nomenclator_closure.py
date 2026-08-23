#!/usr/bin/env python3
"""Validate the creative Astro nomenclator family closure."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent / "sidequest_semantic_ten_page_register_bridge"

INPUTS = {
    "groups": BRIDGE / "ASTRO_395_BRIDGED_GROUPS.tsv",
    "loci": BRIDGE / "ASTRO_142_BRIDGED_LOCI.tsv",
    "unified": BRIDGE / "TEN_PAGE_776_UNIFIED_READING.tsv",
}
OUTPUTS = {
    "families": HERE / "LOCAL_ASTRO_10_FAMILIES.tsv",
    "resolution": HERE / "LOCAL_ASTRO_63_RESOLUTION.tsv",
    "groups": HERE / "ASTRO_395_NOMENCLATOR_CLOSED.tsv",
    "loci": HERE / "ASTRO_142_NOMENCLATOR_CLOSED_LOCI.tsv",
    "unified": HERE / "TEN_PAGE_776_NOMENCLATOR_CLOSED.tsv",
    "card": HERE / "ASTRO_APPRENTICE_CARD.md",
    "summary": HERE / "BUILD_SUMMARY.json",
}
VALIDATION_OUT = HERE / "VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source_groups = read_tsv(INPUTS["groups"])
    source_loci = read_tsv(INPUTS["loci"])
    source_unified = read_tsv(INPUTS["unified"])
    families = read_tsv(OUTPUTS["families"])
    resolution = read_tsv(OUTPUTS["resolution"])
    groups = read_tsv(OUTPUTS["groups"])
    loci = read_tsv(OUTPUTS["loci"])
    unified = read_tsv(OUTPUTS["unified"])
    card = OUTPUTS["card"].read_text(encoding="utf-8")

    check("source_inventory", (len(source_groups), len(source_loci), len(source_unified)) == (395, 142, 776),
          f"groups={len(source_groups)}, loci={len(source_loci)}, unified={len(source_unified)}")
    check("family_inventory", len(families) == 10 and len({r["family_id"] for r in families}) == 10,
          f"families={len(families)}")
    check("family_support", all(int(r["supporting_occurrences"]) > 0 for r in families),
          ", ".join(f"{r['family_id']}={r['supporting_occurrences']}" for r in families))

    source_local = [r for r in source_groups if r["bridge_class"] == "LOCAL_ASTRO_NOMENCLATOR"]
    check("source_local_inventory", len(source_local) == 63 and len({r["surface_display"] for r in source_local}) == 53,
          f"occurrences={len(source_local)}, types={len({r['surface_display'] for r in source_local})}")
    check("resolution_inventory", len(resolution) == 63 and len({r["opaque_local_id"] for r in resolution}) == 63,
          f"rows={len(resolution)}, ids={len({r['opaque_local_id'] for r in resolution})}")
    source_local_keys = {(r["opaque_local_id"], r["page"], r["locus"], r["surface_display"]) for r in source_local}
    resolution_keys = {(r["opaque_local_id"], r["page"], r["locus"], r["surface_display"]) for r in resolution}
    check("resolution_binding", resolution_keys == source_local_keys, "all 63 local occurrences bind to the selected bridge rows")
    forbidden = ("UNKNOWN", "EXEMPLAR", "FORMAL", "gelerntes lokales Namen- oder Wertsegment")
    check("concrete_defaults", all(r["compact_default_de"] and not any(x in r["compact_default_de"] for x in forbidden) for r in resolution),
          "all 63 rows have short concrete defaults")
    check("complete_segmentations", all(r["segmentation"] and "?" not in r["segmentation"] for r in resolution),
          "all 53 forms have explicit family segmentations")
    check("family_assignment", {r["family_id"] for r in resolution} <= {r["family_id"] for r in families},
          f"primary_families={len({r['family_id'] for r in resolution})}")
    family_occurrences = Counter(r["family_id"] for r in resolution)
    check("primary_family_counts", family_occurrences == Counter({
        "N01_VALUE_SIGNS": 17, "N02_AM_ASPECT": 5, "N03_TO_TE_PLACE_PHASE": 12,
        "N04_K_HOUSE_CLASS": 12, "N05_CHE_READOUT": 5, "N06_CH_CTH_CONDITION": 6,
        "N07_IIR_INDEX": 2, "N08_P_RELATION_SELECTION": 2, "N09_FY_YG_LIGHT_GRADE": 2,
    }), str(dict(sorted(family_occurrences.items()))))

    check("closed_group_inventory", len(groups) == 395 and len({r["opaque_local_id"] for r in groups}) == 395,
          f"rows={len(groups)}")
    source_group_keys = [(r["opaque_local_id"], r["surface_display"], r["page"], r["locus"]) for r in source_groups]
    closed_group_keys = [(r["opaque_local_id"], r["surface_display"], r["page"], r["locus"]) for r in groups]
    check("closed_group_binding", source_group_keys == closed_group_keys, "group identity and order unchanged")
    statuses = Counter(r["nomenclator_status"] for r in groups)
    check("closed_group_status", statuses == Counter({"COMMON_BRIDGE_RETAINED": 332, "FAMILY_RESOLVED": 63}), str(dict(statuses)))
    check("closed_group_readings", all(r["closed_workshop_reading_de"] and not (
        r["nomenclator_status"] == "FAMILY_RESOLVED" and any(x in r["closed_workshop_reading_de"] for x in forbidden)
    ) for r in groups), "all 395 groups retain or receive a usable reading")
    check("diagram_guards", all(r["orientation_rule"] == "LOCAL_OWNER_ONLY__NO_START_OR_DIRECTION" and
                                r["crosspage_rule"] == "NO_F68_F69_KEY__NO_IMPLICIT_NAMESPACE_JOIN" for r in groups),
          "no start, direction, rotation, or f68-f69 join introduced")

    check("locus_inventory", len(loci) == 142 and sum(int(r["group_count"]) for r in loci) == 395,
          f"loci={len(loci)}, member_groups={sum(int(r['group_count']) for r in loci)}")
    check("locus_binding", [(r["page"], r["locus"], r["surface_sequence"]) for r in loci] ==
          [(r["page"], r["locus"], r["surface_sequence"]) for r in source_loci],
          "all locus sequences unchanged")
    check("locus_resolution_count", sum(int(r["family_resolved_groups"]) for r in loci) == 63,
          f"family_resolved={sum(int(r['family_resolved_groups']) for r in loci)}")

    check("unified_inventory", len(unified) == 776 and Counter(r["register"] for r in unified) ==
          Counter({"PROSE_WORKSHOP": 381, "ASTRO_DIAGRAM": 395}), str(dict(Counter(r["register"] for r in unified))))
    old_prose = [r for r in source_unified if r["register"] == "PROSE_WORKSHOP"]
    new_prose = [{k: v for k, v in r.items() if k != "nomenclator_layer"} for r in unified if r["register"] == "PROSE_WORKSHOP"]
    check("prose_unchanged", old_prose == new_prose, "all 381 prose rows byte-field identical apart from the new layer column")
    astro_layers = Counter(r["nomenclator_layer"] for r in unified if r["register"] == "ASTRO_DIAGRAM")
    check("unified_astro_layers", astro_layers == Counter({"COMMON_22_COMPONENT_BRIDGE": 332, "LOCAL_ASTRO_FAMILY": 63}), str(dict(astro_layers)))
    fixed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    check("fixed_page_scope", {r["page"] for r in unified} == fixed_pages, ",".join(sorted({r["page"] for r in unified})))
    check("card_contract", all(text in card for text in ["Y+TO+DY", "Y+KE+ODY", "D+O+IIR", "keine ausgesprochenen Sternnamen"]),
          "apprentice card teaches the principal compositions and local-owner rule")

    anchors = {r["surface_display"]: r["compact_default_de"] for r in resolution}
    check("anchor_readings", anchors["am"] == "Aspektwert" and anchors["ytody"] == "Platz fest eingetragen" and
          anchors["ykeody"] == "Klassenplatz fest eingetragen" and anchors["doiir"] == "fester Grundindex" and
          anchors["ycheody"] == "aktueller Ablesewert fest", "five central family anchors exact")

    before = {name: digest(path) for name, path in OUTPUTS.items() if name != "summary"}
    run = subprocess.run([sys.executable, str(HERE / "build_astro_nomenclator_closure.py")], capture_output=True, text=True)
    after = {name: digest(path) for name, path in OUTPUTS.items() if name != "summary"}
    check("deterministic_rebuild", run.returncode == 0 and before == after, "all family artifacts rebuilt byte-identically")

    staged_text = "\n".join(path.read_text(encoding="utf-8") for path in OUTPUTS.values())
    check("sealed_page_scope", "f84\t" not in staged_text and "f84r\t" not in staged_text and "`f84`" not in staged_text,
          "no sealed page selector appears in the family artifacts")

    failed = [row for row in checks if not row["passed"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "counts": {
            "families": len(families), "local_occurrences": len(resolution),
            "local_surface_types": len({r["surface_display"] for r in resolution}),
            "astro_groups": len(groups), "astro_loci": len(loci), "unified_rows": len(unified),
        },
        "checks": checks,
        "artifact_sha256": {name: digest(path) for name, path in OUTPUTS.items()},
    }
    VALIDATION_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
