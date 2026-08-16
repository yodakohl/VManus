#!/usr/bin/env python3
"""Freeze external-referent candidates without reading Voynich formal data."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
HP = R / "gdt151_relation_inventory.tsv"
MHI = R / "experiments/semantic_assumptions/cache/existing_human_annotations/manual_herbal_internal_relations.tsv"
JSP = R / "experiments/semantic_assumptions/cache/existing_human_annotations/stolfi_2025_internal_plant_pairs.tsv"
LOCAL = R / "gdt152_relation_queries.tsv"
OUT = R / "gdt169_external_referent_candidates.tsv"
AUDIT = R / "gdt169_external_referent_source_audit.json"
CORRECTION = R / "gdt169_source_access_correction.json"


def read(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def folio(page):
    out = []
    for char in page:
        if char == "f" and not out:
            out.append(char)
        elif out and char.isdigit():
            out.append(char)
        elif out:
            break
    return "".join(out)


def write(path, rows):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    hp = [x for x in read(HP) if not x["source_page"].startswith("f84") and not x["target_page"].startswith("f84")]
    assert len(hp) == 32 and len({x["relation_id"] for x in hp}) == 32

    mhi_all = [x for x in read(MHI) if not x["page_a"].startswith("f84") and not x["page_b"].startswith("f84")]
    by_mhi = defaultdict(list)
    for row in mhi_all:
        by_mhi[row["relation_id"]].append(row)
    assert len(by_mhi) == 8
    mhi = []
    for rid in sorted(by_mhi):
        rows = by_mhi[rid]
        assert {x["edition"] for x in rows} == {"ZL3b", "IT2a", "RF1b"}
        keys = ("page_a", "page_b", "source_statement", "relation_class", "component", "strength", "panel_class")
        assert all(len({x[k] for x in rows}) == 1 for k in keys)
        mhi.append(rows[0])

    good_jsp = [x for x in read(JSP) if x["match_kind"].startswith("GOOD_") and not x["first_page"].startswith("f84") and not x["second_page_current"].startswith("f84")]
    assert len(good_jsp) == 10
    jsp_by_pair = {(x["first_page"], x["second_page_current"]): x for x in good_jsp}

    local_all = [x for x in read(LOCAL) if not x["label_locus"].startswith("f84") and not x["target_page"].startswith("f84")]
    by_local = defaultdict(list)
    for row in local_all:
        by_local[row["relation_id"]].append(row)
    assert len(by_local) == 5 and all({x["edition"] for x in rows} == {"ZL3b", "IT2a", "RF1b"} for rows in by_local.values())
    local_by_pair = {}
    for rows in by_local.values():
        x = rows[0]
        # GDT152 is label-on-pharma -> Herbal; reverse to the human census orientation.
        pharma = x["label_locus"].split(".", 1)[0]
        local_by_pair[(x["target_page"], pharma)] = x["label_locus"]

    candidates = []
    for x in hp:
        pair = (x["source_page"], x["target_page"])
        same = x["relation_class"] == "SAME_PLANT_FRAGMENT_ASSERTION"
        corroborated = pair in jsp_by_pair
        statement = x["raw_human_illustration_description"]
        candidates.append({
            "candidate_id": x["relation_id"], "evidence_panel": "HERBAL_TO_PHARMA",
            "source_page": pair[0], "target_page": pair[1],
            "source_physical_folio": folio(pair[0]), "target_physical_folio": folio(pair[1]),
            "relation_class": x["relation_class"], "component": "WHOLE_PLANT_OR_FRAGMENT",
            "assertion_strength": "ASSERTED_SAME" if same else "SIMILARITY_ONLY",
            "primary_provenance": "EXISTING_HUMAN_ANNOTATION_VOYNICH_NU",
            "primary_source_url": x["source_url"], "human_statement_sha256": hashlib.sha256(statement.encode()).hexdigest(),
            "cross_source_corroborated": int(corroborated),
            "corroboration_id": jsp_by_pair[pair]["relation_id"] if corroborated else "NONE",
            "corroboration_independence": "POTENTIALLY_DERIVED_UNKNOWN" if corroborated else "ONE_SOURCE_ONLY",
            "local_query_locus": local_by_pair.get(pair, "NONE"),
            "local_ownership_tier": "PUBLISHED_SINGULAR_OR_PROVISIONAL" if pair in local_by_pair else "WHOLE_PAGE_ONLY",
            "scoring_status_prior": x["scoring_status"], "selected_from_voynich_text": 0,
            "semantic_role": "UNASSIGNED",
        })

    for x in mhi:
        pair = (x["page_a"], x["page_b"])
        corroborated = pair in jsp_by_pair
        statement = x["source_statement"]
        candidates.append({
            "candidate_id": x["relation_id"], "evidence_panel": "INTERNAL_HERBAL",
            "source_page": pair[0], "target_page": pair[1],
            "source_physical_folio": folio(pair[0]), "target_physical_folio": folio(pair[1]),
            "relation_class": x["relation_class"], "component": x["component"],
            "assertion_strength": x["strength"], "primary_provenance": "EXISTING_HUMAN_ANNOTATION_VOYNICH_NU",
            "primary_source_url": "SOURCE_BOUND_MANUAL_HERBAL_ATLAS_NO_INLINE_URL", "human_statement_sha256": hashlib.sha256(statement.encode()).hexdigest(),
            "cross_source_corroborated": int(corroborated),
            "corroboration_id": jsp_by_pair[pair]["relation_id"] if corroborated else "NONE",
            "corroboration_independence": "POTENTIALLY_DERIVED_UNKNOWN" if corroborated else "ONE_SOURCE_ONLY",
            "local_query_locus": "NONE", "local_ownership_tier": "WHOLE_PAGE_ONLY",
            "scoring_status_prior": x["held_lexical_status"], "selected_from_voynich_text": 0,
            "semantic_role": "UNASSIGNED",
        })

    assert len(candidates) == 40 and len({(x["source_page"], x["target_page"]) for x in candidates}) == 40
    class_counts = defaultdict(set)
    for x in candidates:
        key = x["relation_class"] + "|" + x["component"]
        class_counts[key].add((x["source_physical_folio"], x["target_physical_folio"]))
    for x in candidates:
        key = x["relation_class"] + "|" + x["component"]
        x["relation_class_distinct_pair_replications"] = len(class_counts[key])
        local = x["local_query_locus"] != "NONE"
        same = x["assertion_strength"] in {"ASSERTED_SAME", "STRONG"} or x["relation_class"] == "SAME_PLANT_ASSERTION"
        # Provenance-only rank; formal outcomes are intentionally absent.
        x["evidence_priority_score"] = (
            4 * int(x["cross_source_corroborated"]) + 3 * int(local) + 2 * int(same)
            + int(x["source_physical_folio"] != x["target_physical_folio"])
            + min(3, int(math.log2(max(1, x["relation_class_distinct_pair_replications"]))) + 1)
        )
    candidates.sort(key=lambda x: (-int(x["evidence_priority_score"]), x["candidate_id"]))
    for rank, row in enumerate(candidates, 1): row["evidence_priority_rank"] = rank
    write(OUT, candidates)

    audit = {
        "schema": "GDT169_EXTERNAL_REFERENT_SOURCE_AUDIT_V1",
        "status": "CORRECTED_FROZEN_40_SOURCE_BOUND_RELATION_PAIRS_BEFORE_FORMAL_SCORING",
        "candidate_pairs": 40, "herbal_pharma_pairs": 32, "internal_herbal_pairs": 8,
        "cross_source_corroborated_pairs": sum(int(x["cross_source_corroborated"]) for x in candidates),
        "locally_owned_query_pairs": sum(x["local_query_locus"] != "NONE" for x in candidates),
        "alternate_readings_collapsed_not_replicated": True,
        "selection_used_voynich_strings": False,
        "new_visual_observations": 0,
        "inadmissible_layout_near_misses": {
            "f40v_two_similar_plants": "ONE_PAGE_PROSE_WITH_NO_SEPARATELY_OWNED_RECORD_PAIR",
            "f75v_spout_array": "LABELS_PRIMARILY_FIGURE_ASSOCIATED_NOT_SPOUT_IDENTITIES",
            "f80r_f82r_repeated_figures": "PROXIMITY_ONLY_WITH_NO_REPEATED_REFERENT_IDENTITY",
            "f106r_star_paragraphs": "NO_AUTHORIAL_ONE_TO_ONE_STAR_TO_PARAGRAPH_BINDING",
        },
        "f84": {
            "corrected_final_inputs_contain_f84_rows": False,
            "rows_retained_or_used_for_selection": 0,
            "formal_payload_accessed": False,
            "image_accessed": False,
            "superseded_builder_transient_human_catalogue_read": True,
            "superseded_read_used_for_selection_or_scoring": False,
        },
        "source_access_correction": {"artifact": CORRECTION.name, "sha256": sha(CORRECTION)},
        "inputs": {str(p.relative_to(R)): sha(p) for p in (HP, MHI, JSP, LOCAL, CORRECTION)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {OUT.name: sha(OUT)},
        "claim_ceiling": "Source-bound external-referent candidate ranking only; no identity, role, word, code value, meaning, plaintext, or translation.",
    }
    audit["result_content_sha256"] = csha(audit)
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({k: audit[k] for k in ("status", "candidate_pairs", "cross_source_corroborated_pairs", "locally_owned_query_pairs")}, sort_keys=True))


if __name__ == "__main__":
    main()
