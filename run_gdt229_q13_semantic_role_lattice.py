#!/usr/bin/env python3
"""Build a transparent provisional semantic lattice over the GDT227 q13 interlinear."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INTERLINEAR = ROOT / "gdt227_q13_abstract_interlinear.tsv"
PROJECTION = ROOT / "gdt224_field_role_projection.tsv"
VISUAL = ROOT / "gdt228_visual_feature_manifest.tsv"
BATH = ROOT / "gdt211_de_balneis_entry_inventory.tsv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, data: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_hash(payload: dict[str, object]) -> str:
    clean = dict(payload)
    clean.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    inter = rows(INTERLINEAR)
    projection = [r for r in rows(PROJECTION) if r["scope"] == "Q13"]
    visual = rows(VISUAL)
    bath = [r for r in rows(BATH) if r["record_class"] == "BATH_RECORD"]
    for table in (inter, projection, visual):
        assert all(not r.get("page", "").startswith("f84") and not r.get("locus", "").startswith("f84") for r in table)
    assert len(inter) == len(projection) == 701
    assert len(visual) == 18 and len(bath) == 32

    proj = {(r["page"], r["record_id"], r["field_ordinal"], r["locus"]): r for r in projection}
    vis = {r["page"]: r for r in visual}
    assert len(proj) == 701 and set(vis) == {r["page"] for r in inter}

    lattice: list[dict[str, object]] = []
    for r in inter:
        key = (r["page"], r["record_id"], r["field_ordinal"], r["locus"])
        p = proj[key]
        v = vis[r["page"]]
        role = p["predicted_role_like"]
        multi = v["multiple_bounded_regions"] == "1"
        path = v["explicit_linear_path"] == "1"
        if role == "OPENER":
            lead = "IDENTITY_OR_LOCATION_ACCESS_HEADER"
            alternatives = "CASE_OR_INDICATION_HEADER;GENERIC_RECORD_OPEN"
            modifier = "NONE"
        elif role == "OPERATION":
            lead = "SETTING_OR_HYDRAULIC_DESCRIPTION" if path else "PRACTICAL_DESCRIPTION_OR_INDICATION"
            alternatives = "PRACTICAL_DESCRIPTION_OR_INDICATION;SETTING_OR_HYDRAULIC_DESCRIPTION;PROCEDURE_OR_CAUTION"
            modifier = "PAGE_HAS_EXPLICIT_LINEAR_PATH_WEAK_EXTERNAL_HYDRAULIC_PRIOR" if path else "NONE"
        elif role in {"INGREDIENT", "TOOL"}:
            lead = "COMPONENT_PARAMETER_OR_LOCAL_STATE" if multi else "MATERIAL_CASE_OR_QUANTITY_ARGUMENT"
            alternatives = "MATERIAL_OR_SUBSTANCE;COMPONENT_OR_LOCAL_STATE;CASE_OR_CONDITION;LOCATION_OR_ACCESS;QUANTITY_OR_DEGREE"
            modifier = "PAGE_HAS_MULTIPLE_BOUNDED_REGIONS_POSTSELECTED_SHORT_ARGUMENT_LEAD" if multi else "NONE"
        elif role == "CLOSER":
            lead = "CAUTION_OUTCOME_OR_FORMAL_CLOSE"
            alternatives = "PROCEDURE_CAUTION;OUTCOME_TESTIMONY;GENERIC_RENDERER_CLOSE"
            modifier = "NONE"
        else:
            lead = "IDENTITY_SETTING_OR_GENERIC_EDGE"
            alternatives = "IDENTITY_OR_LOCATION_ACCESS_HEADER;CASE_OR_INDICATION_HEADER;GENERIC_RECORD_EDGE"
            modifier = "NONE"
        probs = [float(p[f"p_{x}"]) for x in ("opener", "operation", "ingredient", "tool", "closer")]
        ordered = sorted(probs, reverse=True)
        margin = ordered[0] - ordered[1]
        lattice.append({
            "page": r["page"], "physical_folio": r["physical_folio"], "record_id": r["record_id"],
            "field_ordinal": r["field_ordinal"], "record_field_count": r["record_field_count"],
            "relative_position": r["relative_position"], "field_group_count": r["field_group_count"],
            "locus": r["locus"], "line_field_end": r["line_field_end"],
            "source_tokens": r["source_tokens"], "page_hosts": r["page_hosts"],
            "compiler_cells": r["compiler_cells"], "abstract_role_like": r["abstract_role_like"],
            "external_five_way_role_like": role, "external_top_probability": f"{max(probs):.9f}",
            "external_top_margin": f"{margin:.9f}", "multiple_bounded_regions": int(multi),
            "explicit_linear_path": int(path), "leading_latent_document_role": lead,
            "mandatory_alternatives": alternatives, "page_level_visual_modifier": modifier,
            "evidence_grade": "FORMAL_PLACEMENT_SUPPORTED_SEMANTIC_ROLE_SPECULATIVE",
            "claim_state": "LATENT_ROLE_HYPOTHESIS_ONLY_NO_GLOSS",
        })

    write_tsv(ROOT / "gdt229_q13_semantic_role_lattice.tsv", lattice)
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for r in lattice:
        by_record[str(r["record_id"])].append(r)
    summaries: list[dict[str, object]] = []
    for record_id, rr in sorted(by_record.items()):
        counts = Counter(str(r["leading_latent_document_role"]) for r in rr)
        summaries.append({
            "record_id": record_id, "page": rr[0]["page"], "physical_folio": rr[0]["physical_folio"],
            "fields": len(rr), "leading_role_sequence": "|".join(str(r["leading_latent_document_role"]) for r in rr),
            "role_counts_json": json.dumps(dict(sorted(counts.items())), sort_keys=True, separators=(",", ":")),
            "claim_state": "PROVISIONAL_RECORD_ROLE_SEQUENCE_NO_FIELD_MEANING",
        })
    write_tsv(ROOT / "gdt229_q13_record_role_summaries.tsv", summaries)

    worlds = [
        {"rank": 1, "world_id": "W1_HYBRID_THERAPEUTIC_HYDRAULIC_RECORD", "status": "LEADING_ABDUCTIVE_WORLD", "content_architecture": "setting/hydraulic description plus practical/indication clauses and short component/material/state values", "supports": "readable bath schema; weak visual hydraulics calibration; q13 recipe-like role balance; multi-region short-argument lead", "costs": "no singular field ownership; unstable closure; exact host dictionary does not transfer", "semantic_claim": "NONE"},
        {"rank": 2, "world_id": "W2_THERAPEUTIC_INDICATION_LIST", "status": "LIVE_ALTERNATIVE", "content_architecture": "identity/case header plus indication clauses and body-condition/case values", "supports": "indication occurs in all readable bath entries; short values are abundant", "costs": "readable illustrations do not expose indications; no body-condition ownership", "semantic_claim": "NONE"},
        {"rank": 3, "world_id": "W3_HYDRAULIC_COMPONENT_KEY", "status": "LIVE_ALTERNATIVE", "content_architecture": "system header plus component/relation descriptions and local state/parameter values", "supports": "schematic connected geometry; component-key format historically attested; multi-region short-argument lead", "costs": "only one q13 connected-component text locus; key and local-assembly tests mostly fail", "semantic_claim": "NONE"},
        {"rank": 4, "world_id": "W4_NONSEMANTIC_RECORD_RENDERER", "status": "MANDATORY_NULL_WORLD", "content_architecture": "record-like formal organization without recoverable content roles", "supports": "strong compiler and placement structure; semantic transfer failures", "costs": "does not explain the medical/balneological document prior or weak geometry-role alignment", "semantic_claim": "NONE"},
    ]
    write_tsv(ROOT / "gdt229_candidate_worlds.tsv", worlds)

    bath_prevalence = {k: sum(int(r[k]) for r in bath) for k in ("identity", "location_access", "hydraulic_physical", "indication", "procedure_caution", "outcome_testimony")}
    lead_counts = Counter(str(r["leading_latent_document_role"]) for r in lattice)
    result: dict[str, object] = {
        "experiment": "GDT229_Q13_SEMANTIC_ROLE_LATTICE",
        "status": "PROVISIONAL_Q13_SEMANTIC_LATTICE_BUILT_NO_LEXICAL_KEY",
        "fields": len(lattice), "records": len(summaries), "pages": len(vis),
        "leading_world": worlds[0]["world_id"], "worlds": len(worlds),
        "leading_role_counts": dict(sorted(lead_counts.items())),
        "readable_bath_role_prevalence_of_32": bath_prevalence,
        "interpretation": "The strongest working parse is a hybrid therapeutic/hydraulic practical record, but individual fields retain broad alternatives and no PAGE_HOST has a meaning.",
        "claim_ceiling": "A public hypothesis lattice over abstract document roles; no field ownership, word, morpheme, sound, language, plaintext, or translation.",
        "f84": {"retained": False, "joined": False, "scored": False, "new_access": False},
        "inputs": {p.name: sha(p) for p in (INTERLINEAR, PROJECTION, VISUAL, BATH)},
        "documents": {}, "outputs": {}, "implementation": {},
    }
    for name in ("GDT229_Q13_SEMANTIC_ROLE_LATTICE_METHOD.md", "GDT229_Q13_SEMANTIC_ROLE_LATTICE_REPORT.md"):
        path = ROOT / name
        if path.exists(): result["documents"][name] = sha(path)
    for name in ("gdt229_q13_semantic_role_lattice.tsv", "gdt229_q13_record_role_summaries.tsv", "gdt229_candidate_worlds.tsv"):
        result["outputs"][name] = sha(ROOT / name)
    result["implementation"][Path(__file__).name] = sha(Path(__file__))
    result["content_hash"] = content_hash(result)
    (ROOT / "gdt229_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "fields": len(lattice), "records": len(summaries), "leading_world": result["leading_world"]}, sort_keys=True))


if __name__ == "__main__":
    main()
