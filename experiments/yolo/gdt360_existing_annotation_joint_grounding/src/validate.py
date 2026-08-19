#!/usr/bin/env python3
"""Nonimporting reconstruction and integrity validation for GDT360."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding"
ART = EXP / "artifacts"
BASE = ROOT / "experiments/semantic_assumptions/results"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def table(name: str) -> list[dict[str, str]]:
    with (ART / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded(path: Path, selector: str = "page") -> list[dict[str, str]]:
    return list(GuardedTSV(path, selector_column=selector, forbidden_prefixes=("f84",), forbidden_action="skip"))


def folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise ValueError(page)
    return match.group(1)


def cmh_one(x: np.ndarray, y: np.ndarray, strata: list[str]) -> float:
    u = 0.0
    v = 0.0
    by: dict[str, list[int]] = defaultdict(list)
    for i, key in enumerate(strata):
        by[key].append(i)
    for idxs in by.values():
        n = len(idxs)
        if n < 2:
            continue
        ys = y[idxs]
        k = float(ys.sum())
        if k <= 0 or k >= n:
            continue
        xs = x[idxs]
        m = float(xs.sum())
        u += float(xs @ ys) - m * k / n
        v += k * (n - k) * m * (n - m) / (n * n * (n - 1))
    return u / math.sqrt(v) if v > 1e-12 else 0.0


def held_gain(x: np.ndarray, y: np.ndarray, rows: list[dict[str, str]]) -> tuple[float, int, str]:
    total = 0.0
    positive = 0
    parts = []
    for held in sorted({r["physical_folio"] for r in rows}):
        train = [i for i, r in enumerate(rows) if r["physical_folio"] != held]
        test = [i for i, r in enumerate(rows) if r["physical_folio"] == held]
        gp = (float(y[train].sum()) + 1.0) / (len(train) + 2.0)
        base: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        full: dict[tuple[str, int], list[int]] = defaultdict(lambda: [0, 0])
        for i in train:
            s = rkey(rows[i])
            base[s][0] += int(y[i]); base[s][1] += 1
            full[(s, int(x[i]))][0] += int(y[i]); full[(s, int(x[i]))][1] += 1
        gain = 0.0
        for i in test:
            s = rkey(rows[i])
            bp, bn = base[s]
            p0 = (bp + 4 * gp) / (bn + 4)
            fp, fn = full[(s, int(x[i]))]
            p1 = (fp + 4 * p0) / (fn + 4)
            yy = int(y[i])
            gain += math.log2((p1 if yy else 1 - p1) / (p0 if yy else 1 - p0))
        total += gain
        positive += gain > 0
        parts.append(f"{held}:{gain:.6f}")
    return total, positive, ";".join(parts)


def rkey(row: dict[str, str]) -> str:
    return "|".join(row[k] for k in ("section", "currier", "hand", "kind", "code"))


def mobile(y: np.ndarray, keys: list[str]) -> int:
    by: dict[str, list[int]] = defaultdict(list)
    for i, key in enumerate(keys):
        by[key].append(i)
    return sum(len(idxs) for idxs in by.values() if 0 < int(y[idxs].sum()) < len(idxs))


def main() -> None:
    checks: list[dict[str, object]] = []

    def ck(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    inventory = table("gdt360_annotation_inventory.tsv")
    joined = table("gdt360_visual_formal_join.tsv")
    atlas = table("gdt360_candidate_atlas.tsv")
    worlds = table("gdt360_joint_worlds.tsv")
    capacity = table("gdt360_capacity_gaps.tsv")
    counter = table("gdt360_counterexamples.tsv")
    result_path = ART / "gdt360_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))

    exact = guarded(BASE / "existing_human_exact_locus_annotations.tsv")
    loci = guarded(BASE / "source_sta_family_consensus_loci.tsv")
    groups = guarded(BASE / "source_sta_family_consensus_groups.tsv")
    gdt327 = guarded(ROOT / "gdt327_joint_tuple_interlinear.tsv")
    special = guarded(BASE / "special_circle_text_blind_array_inventory.tsv")
    loci_by = {r["locus"]: r for r in loci}
    groups_by: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        groups_by[row["locus"]].append(row)
    gdt_loci = {r["locus"] for r in gdt327}
    exact_joined = [r for r in exact if r["locus"] in loci_by and r["locus"] in groups_by]

    ck("exact_nonf84_count", len(exact) == 1161, str(len(exact)))
    ck("exact_family_covered", len(exact_joined) == 815, str(len(exact_joined)))
    ck("gdt327_exact_coverage", sum(r["locus"] in gdt_loci for r in exact_joined) == 27)
    ck("special_inventory", len(special) == 504 and Counter(r["occupancy_state"] for r in special) == Counter({"TRANSCRIBED":502,"ABSENT":1,"UNREADABLE_TRACE":1}))

    ck("inventory_count", len(inventory) == 4607)
    ck("join_count", len(joined) == 4536)
    ck("unique_join_loci", len({r["locus"] for r in joined}) == 771)
    ck("channels", len({r["channel"] for r in joined}) == 16)
    ck("case_uniqueness", len({(r["channel"], r["locus"]) for r in inventory}) == len(inventory))
    ck("f84_absent_inventory", all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in inventory))
    ck("f84_absent_join", all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in joined))
    ck("roles_unassigned", all(r["semantic_role"] == "UNASSIGNED" and r["interpretation"] == "NONE" for r in joined))

    group_expr = {
        locus: "|".join(x["family_surface"] for x in sorted(rows, key=lambda q: int(q["consensus_group_index"])))
        for locus, rows in groups_by.items()
    }
    ck("family_join_reconstruction", all(group_expr.get(r["locus"]) == r["family_expression"] for r in joined))
    ck("group_count_reconstruction", all(len(groups_by[r["locus"]]) == int(r["group_count"]) for r in joined))
    ck("nuisance_reconstruction", all(r["nuisance_stratum"] == rkey(r) for r in joined))
    ck("gdt_tuple_count_reconstruction", all(len([x for x in gdt327 if x["locus"] == r["locus"]]) == int(r["gdt327_tuple_count"]) for r in joined))

    hard_expected = {
        "CONTACT_GAP": (26,8,18), "BFE_ENCLOSURE": (29,16,13), "HUMAN_LAYOUT": (21,3,18),
        "HUMAN_REL_ATTACHMENT": (314,73,241), "HUMAN_REL_ENCLOSURE": (248,7,241),
        "HUMAN_REL_CONTACT": (250,9,241), "HUMAN_REL_ARRAY_GROUP": (247,6,241),
        "HUMAN_OBJECT_PLANT": (745,206,539), "HUMAN_OBJECT_FIGURE": (745,327,418),
        "HUMAN_OBJECT_STAR_OR_SKY": (745,401,344), "HUMAN_OBJECT_WATER_OR_APPARATUS": (745,104,641),
        "ZODIAC_CLOTHING": (29,14,15), "ZODIAC_STAR_TAIL": (41,16,25),
        "ZODIAC_BARREL": (138,70,68), "ZODIAC_FACING": (186,10,176),
        "SPECIAL_CIRCLE_RAY_OWNER": (22,6,16),
    }
    cap_by = {r["item"].removeprefix("CHANNEL:"): r for r in capacity if r["item"].startswith("CHANNEL:")}
    ck("capacity_channels", set(cap_by) == set(hard_expected))
    for channel, expected in hard_expected.items():
        got = cap_by[channel]
        ck("capacity:" + channel, (int(got["count"]),int(got["positive"]),int(got["negative"])) == expected)

    ck("atlas_count", len(atlas) == 400)
    ck("atlas_per_channel", all(v == 25 for v in Counter(r["channel"] for r in atlas).values()))
    ck("interesting_singleton", sum(r["label"] == "INTERESTING_EXPLORATORY" for r in atlas) == 1)
    top = next(r for r in atlas if r["label"] == "INTERESTING_EXPLORATORY")
    ck("top_identity", top["channel"] == "CONTACT_GAP" and top["formal_feature"] == "FIRST_GROUP_PREFIX_2:AQ")
    ck("top_alias", "FIRST_GROUP_PREFIX_3:AQA" in top["aliases"].split(";"))

    contact = [r for r in joined if r["channel"] == "CONTACT_GAP" and r["visual_state"] in {"CONTACT","CLEAR_GAP"}]
    y = np.asarray([r["visual_state"] == "CONTACT" for r in contact], dtype=np.int8)
    x = np.asarray([r["family_expression"].split("|")[0].startswith("AQ") for r in contact], dtype=np.int8)
    ck("top_counts", len(contact) == 26 and int(y.sum()) == 8 and int(x[y==1].sum()) == 5 and int(x[y==0].sum()) == 2)
    z = cmh_one(x, y, [rkey(r) for r in contact])
    gain, positive, details = held_gain(x, y, contact)
    ck("top_z", abs(z - float(top["cmh_z"])) < 1e-9, f"{z}")
    ck("top_lofo_gain", abs(gain - 5.613173055) < 1e-8 and abs(gain - float(top["lofo_gain_bits"])) < 1e-8, f"{gain}")
    ck("top_fold_transfer", positive == 3 and details == top["held_folio_gains"], details)
    ck("top_topology_mobile", mobile(y, [r["array_id"] for r in contact]) == 20 == int(top["topology_mobile_rows"]))
    ck("top_opportunity_mobile", mobile(y, [f"{r['array_id']}|{r['symbol_count']}|{r['group_count']}" for r in contact]) == 3 == int(top["opportunity_mobile_rows"]))
    ck("top_negative_paid", float(top["selector_paid_gain_bits"]) < 0)
    ck("top_single_section", int(top["support_sections"]) == 1)
    ck("top_two_support_folios", int(top["support_folios"]) == 2)
    ck("top_reading_level", top["reading_stability"] == "FAMILY_LEVEL_ALL_THREE_CONSENSUS")

    ck("world_count", len(worlds) == 23)
    ck("world_roles_unassigned", all(r["latent_role"] == "UNASSIGNED" and r["interpretation"] == "NONE" for r in worlds))
    ck("world_lineages_distinct", all(len(r["evidence_lineages"].split(";")) == len(set(r["evidence_lineages"].split(";"))) for r in worlds))
    ck("worlds_all_weak", all(r["label"] == "WEAK_POSTSELECTED" for r in worlds))
    ck("world_overlap_disclosed", int(worlds[0]["pairwise_locus_overlap_count"]) == 41)
    ck("counter_count", len(counter) == 6)

    ck("result_schema", result["schema"] == "GDT360_EXISTING_ANNOTATION_JOINT_GROUNDING_V1")
    ck("result_status", result["status"] == "EXPLORATORY_SINGLE_CHANNEL_LEADS_ONLY")
    ck("result_counts", result["counts"]["annotation_cases"] == len(inventory) and result["counts"]["formal_join_rows"] == len(joined) and result["counts"]["interesting_candidate_rows"] == 1 and result["counts"]["interesting_joint_worlds"] == 0)
    ck("result_no_new_visual", result["settings"]["new_visual_observations"] == 0 and result["source_access"]["new_images_opened"] is False and result["source_access"]["new_visual_descriptions_created"] is False)
    ck("result_no_catalogue", result["source_access"]["catalogue_search_performed"] is False)
    ck("result_f84_seal", result["source_access"]["f84_rows_parsed_retained_joined_or_scored"] is False and result["source_access"]["f84_images_opened"] is False)

    for rel, digest in result["inputs"].items():
        ck("input_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["outputs"].items():
        ck("output_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["documents"].items():
        ck("document_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        ck("implementation_hash:" + rel, sha(ROOT / rel) == digest)
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    ck("result_content_hash", hashlib.sha256(stable(content)).hexdigest() == claimed)

    public_text = "\n".join((ART / name).read_text(encoding="utf-8") for name in (
        "gdt360_annotation_inventory.tsv","gdt360_visual_formal_join.tsv","gdt360_candidate_atlas.tsv","gdt360_joint_worlds.tsv","gdt360_capacity_gaps.tsv","gdt360_counterexamples.tsv"))
    ck("no_private_path", re.search(r"/(?:home|Users)/[^/\s]+", public_text) is None and "BEGIN PRIVATE KEY" not in public_text)

    failed = sum(not item["pass"] for item in checks)
    validation = {
        "experiment":"GDT360", "schema":"GDT360_VALIDATION_V1",
        "status":"PASS" if failed == 0 else "FAIL",
        "scope":"Nonimporting guarded reconstruction of source counts, exact-human/family/GDT327 coverage, all channel totals, every joined family expression, the top AQ CONTACT contingency/CMH/LOFO/mobility values, evidence-lineage separation, result bindings, and f84 exclusion. Direct visual judgments and the full 1,024-world permutation matrices are not independently re-reviewed/replayed.",
        "checks_passed":len(checks)-failed, "checks_failed":failed, "checks":checks,
        "result_sha256":sha(result_path), "implementation_sha256":sha(Path(__file__)),
    }
    (ART / "gdt360_validation.json").write_bytes(stable(validation))
    print(validation["status"], validation["checks_passed"], validation["checks_failed"])
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
