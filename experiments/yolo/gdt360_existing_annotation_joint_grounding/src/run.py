#!/usr/bin/env python3
"""GDT360: permissive joint discovery over existing visual annotations only."""
from __future__ import annotations

import csv
import hashlib
import itertools
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

INPUTS = {
    "exact_human": BASE / "existing_human_exact_locus_annotations.tsv",
    "crosswalk": BASE / "existing_human_current_locus_crosswalk.tsv",
    "consensus_loci": BASE / "source_sta_family_consensus_loci.tsv",
    "consensus_groups": BASE / "source_sta_family_consensus_groups.tsv",
    "gdt327": ROOT / "gdt327_joint_tuple_interlinear.tsv",
    "gdt002_join": ROOT / "gdt002_exploratory_visual_formal_join.tsv",
    "clothing": BASE / "zcv001_zodiac_clothing_state_projection.tsv",
    "tail": BASE / "zst001_zodiac_star_tail_state_projection.tsv",
    "barrel": BASE / "zbv001_zodiac_barrel_native_visual_capacity.tsv",
    "ray_owner": BASE / "sre001_special_circle_star_ray_extension_result.tsv",
    "special_circle": BASE / "special_circle_text_blind_array_inventory.tsv",
    "facing": ROOT / "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition/artifacts/gdt349_observations.tsv",
    "gdt002_result": ROOT / "gdt002_exploratory_discovery_results.json",
    "bfe_result": BASE / "bfe001_bio_figure_enclosure_capacity.json",
    "clothing_result": BASE / "zcv001_zodiac_clothing_formal_marker_target.json",
    "tail_result": BASE / "zst001_zodiac_star_tail_native_visual_capacity.json",
    "facing_result": ROOT / "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition/artifacts/gdt349_result.json",
}

WORLD_COUNT = 1024
SEED_LABEL = "GDT360_EXISTING_ANNOTATION_JOINT_GROUNDING_V1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows and not fieldnames:
        raise ValueError(f"empty table without schema: {path}")
    names = fieldnames or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def guarded(path: Path, selector: str = "page", allowed: set[str] | None = None) -> tuple[list[dict[str, str]], object]:
    reader = GuardedTSV(path, selector_column=selector, allowed_values=allowed, forbidden_prefixes=("f84",), forbidden_action="skip")
    return list(reader), reader.stats


def folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise ValueError(f"bad page: {page}")
    return match.group(1)


def feature_set(meta: dict[str, object]) -> set[str]:
    groups: list[str] = meta["groups"]  # type: ignore[assignment]
    out: set[str] = set()
    for group in groups:
        for char in set(group):
            out.add(f"FAMILY_COMPONENT:{char}")
        for n in (2, 3):
            if len(group) >= n:
                for i in range(len(group) - n + 1):
                    out.add(f"FAMILY_{n}GRAM:{group[i:i+n]}")
    if groups:
        for n in (1, 2, 3):
            if len(groups[0]) >= n:
                out.add(f"FIRST_GROUP_PREFIX_{n}:{groups[0][:n]}")
            if len(groups[-1]) >= n:
                out.add(f"LAST_GROUP_SUFFIX_{n}:{groups[-1][-n:]}")
        out.add("EXACT_FAMILY_EXPRESSION:" + "|".join(groups))
    symbols = int(meta["symbol_count"])
    for threshold in (3, 4, 5):
        if symbols <= threshold:
            out.add(f"SYMBOL_COUNT_LE_{threshold}")
    for threshold in (6, 8, 10):
        if symbols >= threshold:
            out.add(f"SYMBOL_COUNT_GE_{threshold}")
    count = len(groups)
    if count >= 2:
        out.add("GROUP_COUNT_GE_2")
    if count >= 3:
        out.add("GROUP_COUNT_GE_3")
    if meta["strict_zero_alternative"] == "0":
        out.add("READING_ALTERNATIVE_PRESENT")
    for boundary in meta["internal_boundaries"]:  # type: ignore[assignment]
        out.add("INTERNAL_BOUNDARY:" + boundary)
    if meta.get("gdt327_tuple_ids"):
        for tuple_id in meta["gdt327_tuple_ids"]:  # type: ignore[assignment]
            out.add("GDT327_EXACT_TUPLE:" + tuple_id)
    return out


def cmh_z(F: np.ndarray, y: np.ndarray, strata: list[str]) -> np.ndarray:
    m = F.shape[1]
    u = np.zeros(m, dtype=float)
    v = np.zeros(m, dtype=float)
    by: dict[str, list[int]] = defaultdict(list)
    for i, key in enumerate(strata):
        by[key].append(i)
    for idxs in by.values():
        idx = np.asarray(idxs, dtype=int)
        n = len(idx)
        if n < 2:
            continue
        ys = y[idx]
        k = float(ys.sum())
        if k <= 0 or k >= n:
            continue
        fs = F[idx].astype(float)
        counts = fs.sum(axis=0)
        u += fs.T @ ys - counts * k / n
        v += k * (n - k) * counts * (n - counts) / (n * n * (n - 1))
    z = np.zeros(m, dtype=float)
    ok = v > 1e-12
    z[ok] = u[ok] / np.sqrt(v[ok])
    return z


def permutation_z(
    F: np.ndarray, y: np.ndarray, strata: list[str], worlds: int, rng: np.random.Generator
) -> tuple[np.ndarray, int]:
    n, m = F.shape
    Y = np.repeat(y[:, None], worlds, axis=1)
    by: dict[str, list[int]] = defaultdict(list)
    for i, key in enumerate(strata):
        by[key].append(i)
    mobile = 0
    for idxs in by.values():
        idx = np.asarray(idxs, dtype=int)
        k = int(y[idx].sum())
        if 0 < k < len(idx):
            mobile += len(idx)
            base = y[idx].copy()
            for w in range(worlds):
                Y[idx, w] = base[rng.permutation(len(idx))]
    u = np.zeros((m, worlds), dtype=float)
    v = np.zeros(m, dtype=float)
    for idxs in by.values():
        idx = np.asarray(idxs, dtype=int)
        n_s = len(idx)
        if n_s < 2:
            continue
        k = float(y[idx].sum())
        if k <= 0 or k >= n_s:
            continue
        fs = F[idx].astype(float)
        counts = fs.sum(axis=0)
        u += fs.T @ Y[idx] - counts[:, None] * k / n_s
        v += k * (n_s - k) * counts * (n_s - counts) / (n_s * n_s * (n_s - 1))
    z = np.zeros_like(u)
    ok = v > 1e-12
    z[ok] = u[ok] / np.sqrt(v[ok, None])
    return z, mobile


def held_gain(x: np.ndarray, y: np.ndarray, rows: list[dict[str, object]], hold_key: str) -> tuple[float, int, int, str]:
    holds = sorted({str(r[hold_key]) for r in rows})
    total_gain = 0.0
    positive = 0
    details: list[str] = []
    for held in holds:
        train = [i for i, r in enumerate(rows) if str(r[hold_key]) != held]
        test = [i for i, r in enumerate(rows) if str(r[hold_key]) == held]
        if not train or not test:
            continue
        global_p = (float(y[train].sum()) + 1.0) / (len(train) + 2.0)
        base_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        full_counts: dict[tuple[str, int], list[int]] = defaultdict(lambda: [0, 0])
        for i in train:
            s = str(rows[i]["nuisance_stratum"])
            base_counts[s][0] += int(y[i])
            base_counts[s][1] += 1
            full_counts[(s, int(x[i]))][0] += int(y[i])
            full_counts[(s, int(x[i]))][1] += 1
        gain = 0.0
        for i in test:
            s = str(rows[i]["nuisance_stratum"])
            bp, bn = base_counts[s]
            p0 = (bp + 4.0 * global_p) / (bn + 4.0)
            fp, fn = full_counts[(s, int(x[i]))]
            p1 = (fp + 4.0 * p0) / (fn + 4.0)
            yy = int(y[i])
            gain += math.log2((p1 if yy else 1 - p1) / (p0 if yy else 1 - p0))
        total_gain += gain
        if gain > 0:
            positive += 1
        details.append(f"{held}:{gain:.6f}")
    return total_gain, positive, len(holds), ";".join(details)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)

    exact, exact_stats = guarded(INPUTS["exact_human"])
    loci, loci_stats = guarded(INPUTS["consensus_loci"])
    groups, groups_stats = guarded(INPUTS["consensus_groups"])
    gdt327, gdt327_stats = guarded(INPUTS["gdt327"])
    old_join, old_join_stats = guarded(INPUTS["gdt002_join"])
    crosswalk, crosswalk_stats = guarded(INPUTS["crosswalk"], selector="source_page")
    clothing, clothing_stats = guarded(INPUTS["clothing"])
    tail, tail_stats = guarded(INPUTS["tail"])
    barrel, barrel_stats = guarded(INPUTS["barrel"])
    ray_owner, ray_stats = guarded(INPUTS["ray_owner"])
    special, special_stats = guarded(INPUTS["special_circle"])
    facing, facing_stats = guarded(INPUTS["facing"])

    group_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        group_by_locus[row["locus"]].append(row)
    gdt_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in gdt327:
        gdt_by_locus[row["locus"]].append(row)
    locus_meta: dict[str, dict[str, object]] = {}
    for row in loci:
        gs = sorted(group_by_locus.get(row["locus"], []), key=lambda x: int(x["consensus_group_index"]))
        if not gs:
            continue
        tuples = sorted(gdt_by_locus.get(row["locus"], []), key=lambda x: int(x["group_index"]))
        locus_meta[row["locus"]] = {
            **row,
            "groups": [x["family_surface"] for x in gs],
            "group_rows": gs,
            "internal_boundaries": sorted({x["right_boundary_profile"] for x in gs[:-1] if x["right_boundary_profile"]}),
            "gdt327_tuple_ids": [x["joint_tuple_id"] for x in tuples],
            "gdt327_renderer_states": [x["renderer_state"] for x in tuples],
        }

    cross_by_id = {
        row["source_record_id"]: row
        for row in crosswalk
        if row.get("primary_eligible") == "1"
        and row.get("current_locus")
        and not row.get("current_page", "").startswith("f84")
    }

    case_map: dict[tuple[str, str], dict[str, object]] = {}

    def add_case(
        channel: str,
        state: str,
        page: str,
        locus: str,
        array_id: str,
        provenance: str,
        source_id: str,
        confidence: str,
        detail: str,
        evidence_family: str,
    ) -> None:
        if page.startswith("f84") or locus.startswith("f84"):
            raise RuntimeError("f84 selector reached case builder")
        key = (channel, locus)
        row = {
            "case_id": hashlib.sha256((channel + "|" + locus).encode()).hexdigest()[:16],
            "channel": channel,
            "visual_state": state,
            "page": page,
            "physical_folio": folio(page),
            "locus": locus,
            "array_id": array_id or page,
            "provenance": provenance,
            "source_id": source_id,
            "confidence": confidence or "UNSPECIFIED",
            "evidence_family": evidence_family,
            "evidence_lineage": "STOLFI_EXACT_HUMAN_ATLAS" if evidence_family in {"EXACT_HUMAN_RELATION", "EXACT_HUMAN_OBJECT_CONTEXT"} or channel == "HUMAN_LAYOUT" else evidence_family,
            "evidence_cluster": f"MANUSCRIPT_LOCUS:{locus}",
            "visual_detail": detail,
        }
        if key in case_map and case_map[key]["visual_state"] != state:
            case_map[key]["visual_state"] = "CONFLICT_UNCERTAIN"
            case_map[key]["visual_detail"] = str(case_map[key]["visual_detail"]) + " | CONFLICT: " + detail
            case_map[key]["confidence"] = "UNCERTAIN"
        else:
            case_map[key] = row

    exact_by_locus = {row["locus"]: row for row in exact}
    exact_joined = [row for row in exact if row["locus"] in locus_meta]
    proximity_only = {
        row["locus"]
        for row in exact_joined
        if row["relation_scope"] == "EXACT_LOCAL_COMMENT"
        and set(filter(None, row["local_relation_tags"].split(";"))) == {"REL_PROXIMITY"}
    }
    relation_channels = {
        "HUMAN_REL_ATTACHMENT": "REL_EXPLICIT_ATTACHMENT",
        "HUMAN_REL_ENCLOSURE": "REL_ENCLOSURE",
        "HUMAN_REL_CONTACT": "REL_OVERLAP_OR_CONTACT",
        "HUMAN_REL_ARRAY_GROUP": "REL_ARRAY_OR_GROUP",
    }
    for channel, tag in relation_channels.items():
        for row in exact_joined:
            if row["relation_scope"] != "EXACT_LOCAL_COMMENT":
                continue
            tags = set(filter(None, row["local_relation_tags"].split(";")))
            if tag in tags:
                state = tag
            elif row["locus"] in proximity_only:
                state = "PROXIMITY_ONLY"
            else:
                continue
            add_case(channel, state, row["page"], row["locus"], row["page"] + ":" + row["unit"],
                     "EXISTING_HUMAN_ANNOTATION", row["source_path"], row["certainty"],
                     row["local_comment"], "EXACT_HUMAN_RELATION")

    object_tags = ("PLANT", "FIGURE", "STAR_OR_SKY", "WATER_OR_APPARATUS")
    for target in object_tags:
        channel = "HUMAN_OBJECT_" + target
        for row in exact_joined:
            tags = set(filter(None, row["object_tags"].split(";"))) & set(object_tags)
            if not tags:
                continue
            state = target if target in tags else "OTHER_EXPLICIT_OBJECT"
            add_case(channel, state, row["page"], row["locus"], row["page"] + ":" + row["unit"],
                     "EXISTING_HUMAN_ANNOTATION", row["source_path"], row["certainty"],
                     row["unit_description"], "EXACT_HUMAN_OBJECT_CONTEXT")

    for row in old_join:
        locus = row.get("locus", "")
        if not locus:
            continue
        add_case(row["channel"], row["visual_state"], row["page"], locus, row["array_id"],
                 row["observation_provenance"], row["observation_source"], row["review_confidence"],
                 row["visual_detail"], "GDT002_EXISTING_CHANNEL")

    for source_rows, channel, state_field, family in (
        (clothing, "ZODIAC_CLOTHING", "clothing_state", "ZODIAC_CLOTHING"),
        (tail, "ZODIAC_STAR_TAIL", "tail_state", "ZODIAC_STAR_TAIL"),
    ):
        for row in source_rows:
            cross = cross_by_id.get(row["source_record_id"])
            if not cross:
                continue
            locus = cross["current_locus"]
            add_case(channel, row[state_field], row["page"], locus, row["page"] + ":" + row.get("ring", ""),
                     row.get("state_provenance", row.get("grade_source", "EXISTING_OBSERVATION")),
                     row["source_record_id"], row.get("confidence", row.get("grade_confidence", "")),
                     row.get("observation_basis", row.get("visual_basis", "")), family)

    for row in barrel:
        if row["strict_eligible"] != "1":
            continue
        add_case("ZODIAC_BARREL", row["barrel_state"], row["page"], row["current_locus"],
                 row["page"] + ":" + row["ring"], row["state_provenance"], row["source_record_id"],
                 "STRICT_ELIGIBLE", row["exclusion_reason"], "ZODIAC_BARREL")

    for row in facing:
        state = "PROFILE" if row["review_state"] in {"PROFILE_LEFT", "PROFILE_RIGHT"} else "NON_DIRECTIONAL"
        add_case("ZODIAC_FACING", state, row["page"], row["current_locus"], row["page"] + ":" + row["ring_scope"],
                 row["review_provenance"], row["source_record_id"], row["review_confidence"],
                 row["neutral_note"], "ZODIAC_FACING")

    for row in ray_owner:
        add_case("SPECIAL_CIRCLE_RAY_OWNER", row["outcome"], row["page"], row["locus"],
                 row["page"] + ":" + row["unit"], "PRIOR_AI_DIRECT_VISUAL_OBSERVATION", row["opaque_id"],
                 "PUBLISHED", row["visible_basis"], "SPECIAL_CIRCLE_RAY_OWNER")

    inventory_rows = sorted(case_map.values(), key=lambda r: (str(r["channel"]), str(r["page"]), str(r["locus"])))
    for row in inventory_rows:
        meta = locus_meta.get(str(row["locus"]))
        row["formal_coverage"] = "SOURCE_NATIVE_FAMILY_CONSENSUS" if meta else "NO_EXACT_FAMILY_CONSENSUS"
        row["gdt327_coverage"] = "YES" if meta and meta.get("gdt327_tuple_ids") else "NO"

    formal_loci = {str(r["locus"]) for r in inventory_rows if str(r["locus"]) in locus_meta}
    locus_features = {locus: feature_set(locus_meta[locus]) for locus in formal_loci}
    feature_support: dict[str, set[str]] = defaultdict(set)
    feature_folios: dict[str, set[str]] = defaultdict(set)
    for locus, feats in locus_features.items():
        for feat in feats:
            feature_support[feat].add(locus)
            feature_folios[feat].add(folio(str(locus_meta[locus]["page"])))
    n_loci = len(formal_loci)
    raw_features = sorted(
        feat for feat, support in feature_support.items()
        if 4 <= len(support) <= n_loci - 4 and len(feature_folios[feat]) >= 2
    )
    ordered_loci = sorted(formal_loci)
    mask_aliases: dict[tuple[bool, ...], list[str]] = defaultdict(list)
    for feat in raw_features:
        mask_aliases[tuple(feat in locus_features[locus] for locus in ordered_loci)].append(feat)
    feature_aliases: dict[str, list[str]] = {}
    features: list[str] = []
    for aliases in mask_aliases.values():
        canonical = min(aliases, key=lambda value: (len(value), value))
        features.append(canonical)
        feature_aliases[canonical] = sorted(x for x in aliases if x != canonical)
    features.sort()

    channel_states = {
        "CONTACT_GAP": ("CONTACT", "CLEAR_GAP"),
        "BFE_ENCLOSURE": ("INDIVIDUAL_BOUNDED", "OPEN_OR_COMMUNAL"),
        "HUMAN_LAYOUT": ("APPARATUS_POSITION", "FIGURE_POSITION"),
        "HUMAN_REL_ATTACHMENT": ("REL_EXPLICIT_ATTACHMENT", "PROXIMITY_ONLY"),
        "HUMAN_REL_ENCLOSURE": ("REL_ENCLOSURE", "PROXIMITY_ONLY"),
        "HUMAN_REL_CONTACT": ("REL_OVERLAP_OR_CONTACT", "PROXIMITY_ONLY"),
        "HUMAN_REL_ARRAY_GROUP": ("REL_ARRAY_OR_GROUP", "PROXIMITY_ONLY"),
        "HUMAN_OBJECT_PLANT": ("PLANT", "OTHER_EXPLICIT_OBJECT"),
        "HUMAN_OBJECT_FIGURE": ("FIGURE", "OTHER_EXPLICIT_OBJECT"),
        "HUMAN_OBJECT_STAR_OR_SKY": ("STAR_OR_SKY", "OTHER_EXPLICIT_OBJECT"),
        "HUMAN_OBJECT_WATER_OR_APPARATUS": ("WATER_OR_APPARATUS", "OTHER_EXPLICIT_OBJECT"),
        "ZODIAC_CLOTHING": ("DRESSED", "UNDRESSED"),
        "ZODIAC_STAR_TAIL": ("TAIL", "NO_TAIL"),
        "ZODIAC_BARREL": ("PRESENT", "ABSENT"),
        "ZODIAC_FACING": ("PROFILE", "NON_DIRECTIONAL"),
        "SPECIAL_CIRCLE_RAY_OWNER": ("NON_STAR_OBJECT", "SLOT_OR_GROUP_ONLY"),
    }

    join_rows: list[dict[str, object]] = []
    for row in inventory_rows:
        locus = str(row["locus"])
        meta = locus_meta.get(locus)
        if not meta:
            continue
        groups_here: list[str] = meta["groups"]  # type: ignore[assignment]
        gdt_tuples: list[str] = meta["gdt327_tuple_ids"]  # type: ignore[assignment]
        out = dict(row)
        out.update({
            "section": meta["section"], "currier": meta["currier"], "hand": meta["hand"],
            "code": meta["code"], "kind": meta["kind"], "grammar_scope": meta["grammar_scope"],
            "family_expression": "|".join(groups_here), "symbol_count": meta["symbol_count"],
            "group_count": len(groups_here), "strict_zero_alternative": meta["strict_zero_alternative"],
            "alternative_sites": meta["alternative_sites"],
            "boundary_expression": "|".join(meta["internal_boundaries"]),
            "gdt327_tuple_count": len(gdt_tuples), "gdt327_tuple_sequence": "|".join(gdt_tuples),
            "semantic_role": "UNASSIGNED", "interpretation": "NONE",
        })
        out["nuisance_stratum"] = "|".join(str(out[k]) for k in ("section", "currier", "hand", "kind", "code"))
        join_rows.append(out)

    score_rows: list[dict[str, object]] = []
    channel_summary: list[dict[str, object]] = []
    case_loci_by_channel: dict[str, set[str]] = defaultdict(set)
    endpoint_count = 0
    rng_master = np.random.default_rng(int(hashlib.sha256(SEED_LABEL.encode()).hexdigest()[:16], 16))

    for channel, (positive_state, negative_state) in channel_states.items():
        rows = [r for r in join_rows if r["channel"] == channel and r["visual_state"] in {positive_state, negative_state}]
        if len(rows) < 4:
            continue
        y = np.asarray([1 if r["visual_state"] == positive_state else 0 for r in rows], dtype=np.int8)
        if y.sum() < 2 or (len(y) - y.sum()) < 2:
            continue
        endpoint_count += 1
        case_loci_by_channel[channel] = {str(r["locus"]) for r in rows}
        variable_raw = [feat for feat in features if 2 <= sum(feat in locus_features[str(r["locus"])] for r in rows) <= len(rows) - 2]
        channel_masks: dict[tuple[bool, ...], list[str]] = defaultdict(list)
        for feat in variable_raw:
            channel_masks[tuple(feat in locus_features[str(r["locus"])] for r in rows)].append(feat)
        channel_aliases: dict[str, list[str]] = {}
        variable: list[str] = []
        for aliases in channel_masks.values():
            canonical = min(aliases, key=lambda value: (len(value), value))
            variable.append(canonical)
            channel_aliases[canonical] = sorted(set(feature_aliases.get(canonical, []) + [x for x in aliases if x != canonical]))
        variable.sort()
        F = np.asarray([[feat in locus_features[str(r["locus"])] for feat in variable] for r in rows], dtype=np.int8)
        nuisance = [str(r["nuisance_stratum"]) for r in rows]
        local = [str(r["array_id"]) for r in rows]
        opportunity = [f"{r['array_id']}|{r['symbol_count']}|{r['group_count']}" for r in rows]
        observed_z = cmh_z(F, y, nuisance)
        seed = int(rng_master.integers(0, 2**63 - 1))
        z_perm, nuisance_mobile = permutation_z(F, y, nuisance, WORLD_COUNT, np.random.default_rng(seed))
        z_local, local_mobile = permutation_z(F, y, local, WORLD_COUNT, np.random.default_rng(seed ^ 0x5A5A5A5A))
        z_opportunity, opportunity_mobile = permutation_z(F, y, opportunity, WORLD_COUNT, np.random.default_rng(seed ^ 0x3C3C3C3C))
        max_abs = np.max(np.abs(z_perm), axis=0) if F.shape[1] else np.zeros(WORLD_COUNT)
        channel_scores: list[dict[str, object]] = []
        for j, feat in enumerate(variable):
            x = F[:, j]
            z = float(observed_z[j])
            p_local = (1 + int(np.sum(np.abs(z_perm[j]) >= abs(z) - 1e-12))) / (WORLD_COUNT + 1)
            p_max = (1 + int(np.sum(max_abs >= abs(z) - 1e-12))) / (WORLD_COUNT + 1)
            p_topology = (1 + int(np.sum(np.abs(z_local[j]) >= abs(z) - 1e-12))) / (WORLD_COUNT + 1) if local_mobile else 1.0
            p_opportunity = (1 + int(np.sum(np.abs(z_opportunity[j]) >= abs(z) - 1e-12))) / (WORLD_COUNT + 1) if opportunity_mobile else 1.0
            gain, positive_folios, fold_count, fold_details = held_gain(x, y, rows, "physical_folio")
            section_gain, positive_sections, section_count, section_details = held_gain(x, y, rows, "section") if len({r["section"] for r in rows}) >= 2 else (0.0, 0, 1, "NOT_POWERED")
            present_pos = int(x[y == 1].sum())
            present_neg = int(x[y == 0].sum())
            confidence_rows = [i for i, r in enumerate(rows) if str(r["confidence"]) not in {"HEDGED", "UNCERTAIN", "CONFLICT_UNCERTAIN"}]
            if len(confidence_rows) >= 4 and 0 < int(y[confidence_rows].sum()) < len(confidence_rows):
                hc_gain, _, _, _ = held_gain(x[confidence_rows], y[confidence_rows], [rows[i] for i in confidence_rows], "physical_folio")
                hc_value = f"{hc_gain:.9f}"
            else:
                hc_value = "NOT_POWERED"
            selector_cost = math.log2(max(1, len(features) * len(channel_states) * 2))
            paid = gain - selector_cost
            array_parts = []
            for array_id in sorted({str(r["array_id"]) for r in rows}):
                idx = [i for i, r in enumerate(rows) if str(r["array_id"]) == array_id]
                array_parts.append(f"{array_id}:P{sum(int(y[i]) for i in idx)}/{sum(int(y[i]) and int(x[i]) for i in idx)}:N{sum(1-int(y[i]) for i in idx)}/{sum((1-int(y[i])) and int(x[i]) for i in idx)}")
            if gain >= 4 and positive_folios >= 3 and p_local <= .05 and p_max <= .20 and p_topology <= .10 and local_mobile >= 10:
                label = "INTERESTING_EXPLORATORY"
            elif p_local <= .10 and (local_mobile < 10 or p_topology > .20):
                label = "LIKELY_PAGE_CONFOUND"
            elif gain > 0 and (positive_folios >= 2 or p_local <= .10):
                label = "WEAK"
            elif abs(z) >= 1.64 and gain <= 0:
                label = "UNSTABLE"
            else:
                label = "NO_SIGNAL"
            item = {
                "channel": channel, "positive_state": positive_state, "negative_state": negative_state,
                "candidate_id": hashlib.sha256((channel + "|" + feat).encode()).hexdigest()[:14],
                "formal_feature": feat, "aliases": ";".join(channel_aliases.get(feat, [])),
                "feature_level": feat.split(":", 1)[0], "label": label,
                "n": len(rows), "positive_n": int(y.sum()), "negative_n": int(len(y) - y.sum()),
                "feature_present_n": int(x.sum()), "positive_with_feature": present_pos,
                "negative_with_feature": present_neg, "direction": "PRESENT_ENRICHED" if z > 0 else "PRESENT_DEPLETED",
                "cmh_z": f"{z:.9f}", "nuisance_permutation_worlds": WORLD_COUNT,
                "nuisance_local_p": f"{p_local:.9f}", "nuisance_maxT_p": f"{p_max:.9f}",
                "topology_local_p": f"{p_topology:.9f}", "nuisance_mobile_rows": nuisance_mobile,
                "topology_mobile_rows": local_mobile, "opportunity_local_p": f"{p_opportunity:.9f}",
                "opportunity_mobile_rows": opportunity_mobile, "lofo_gain_bits": f"{gain:.9f}",
                "selector_paid_gain_bits": f"{paid:.9f}", "positive_held_folios": positive_folios,
                "held_folios": fold_count, "held_folio_gains": fold_details,
                "leave_section_gain_bits": f"{section_gain:.9f}" if section_count >= 2 else "NOT_POWERED",
                "positive_held_sections": positive_sections if section_count >= 2 else "NOT_POWERED",
                "held_section_gains": section_details, "confidence_restricted_lofo_gain_bits": hc_value,
                "support_folios": len({str(r["physical_folio"]) for i, r in enumerate(rows) if x[i]}),
                "support_pages": len({str(r["page"]) for i, r in enumerate(rows) if x[i]}),
                "support_sections": len({str(r["section"]) for i, r in enumerate(rows) if x[i]}),
                "per_array_counts": ";".join(array_parts),
                "reading_stability": "FAMILY_LEVEL_ALL_THREE_CONSENSUS",
                "alternative_bearing_rows": sum(str(r["strict_zero_alternative"]) == "0" for r in rows),
                "obvious_confounds": ";".join(filter(None, [
                    "LOW_TOPOLOGY_MOBILITY" if local_mobile < 10 else "",
                    "LOW_OPPORTUNITY_MOBILITY" if opportunity_mobile < 10 else "",
                    "SINGLE_SECTION_SUPPORT" if len({str(r["section"]) for i, r in enumerate(rows) if x[i]}) <= 1 else "",
                    "HEDGED_SENSITIVITY" if hc_value != "NOT_POWERED" and (float(hc_value) > 0) != (gain > 0) else "",
                    "GDT327_SPARSE" if sum(str(r["gdt327_coverage"]) == "YES" for r in rows) < len(rows) // 2 else "",
                ])) or "NONE",
                "rank_score": gain + .5 * abs(z),
            }
            channel_scores.append(item)
            score_rows.append(item)
        channel_summary.append({
            "item": "CHANNEL:" + channel, "count": len(rows), "positive": int(y.sum()),
            "negative": int(len(y) - y.sum()), "uncertain_or_unscored": sum(1 for r in inventory_rows if r["channel"] == channel and r["visual_state"] not in {positive_state, negative_state}),
            "folios": len({r["physical_folio"] for r in rows}), "pages": len({r["page"] for r in rows}),
            "sections": ";".join(sorted({str(r["section"]) for r in rows})), "topology_mobile_rows": local_mobile,
            "status": "SCORED", "detail": f"{len(variable)} state-blind variable features; positive={positive_state}; negative={negative_state}",
        })

    priority = {"INTERESTING_EXPLORATORY": 0, "WEAK": 1, "LIKELY_PAGE_CONFOUND": 2, "UNSTABLE": 3, "NO_SIGNAL": 4}
    atlas_rows: list[dict[str, object]] = []
    for channel in sorted({str(r["channel"]) for r in score_rows}):
        ranked = sorted((r for r in score_rows if r["channel"] == channel), key=lambda r: (priority[str(r["label"])], -float(r["rank_score"]), str(r["formal_feature"])))
        for rank, row in enumerate(ranked[:25], 1):
            out = dict(row)
            out.pop("rank_score")
            out["channel_rank"] = rank
            atlas_rows.append(out)

    evidence_family = {
        channel: next((str(r["evidence_family"]) for r in join_rows if r["channel"] == channel), channel)
        for channel in channel_states
    }
    evidence_lineage = {
        channel: next((str(r["evidence_lineage"]) for r in join_rows if r["channel"] == channel), channel)
        for channel in channel_states
    }
    by_feature: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in score_rows:
        if (float(row["lofo_gain_bits"]) > 0 and int(row["positive_held_folios"]) >= 2
                and float(row["nuisance_local_p"]) <= .10):
            by_feature[str(row["formal_feature"])].append(row)
    worlds: list[dict[str, object]] = []
    for feat, entries in by_feature.items():
        entries = sorted(entries, key=lambda r: -float(r["lofo_gain_bits"]))
        for k in (2, 3):
            for combo in itertools.combinations(entries[:10], k):
                families = [evidence_family[str(r["channel"])] for r in combo]
                lineages = [evidence_lineage[str(r["channel"])] for r in combo]
                if len(set(families)) != k:
                    continue
                if len(set(lineages)) != k:
                    continue
                raw_gain = sum(float(r["lofo_gain_bits"]) for r in combo)
                cost = math.log2(max(1, len(features))) + math.log2(math.comb(max(endpoint_count, k), k)) + k
                loci_sets = [case_loci_by_channel[str(r["channel"])] for r in combo]
                overlap = sum(len(a & b) for a, b in itertools.combinations(loci_sets, 2))
                union = len(set().union(*loci_sets))
                paid = raw_gain - cost
                worlds.append({
                    "world_id": hashlib.sha256((feat + "|" + "|".join(str(r["channel"]) for r in combo)).encode()).hexdigest()[:14],
                    "formal_feature": feat, "rule_count": k,
                    "visual_endpoints": ";".join(str(r["channel"]) for r in combo),
                    "directions": ";".join(str(r["direction"]) for r in combo),
                    "evidence_families": ";".join(families),
                    "evidence_lineages": ";".join(lineages),
                    "raw_joint_lofo_gain_bits": f"{raw_gain:.9f}", "complexity_cost_bits": f"{cost:.9f}",
                    "selector_paid_joint_gain_bits": f"{paid:.9f}", "pairwise_locus_overlap_count": overlap,
                    "union_locus_count": union, "latent_role": "UNASSIGNED",
                    "label": "INTERESTING_EXPLORATORY" if paid > 0 and overlap == 0 and all(float(r["nuisance_maxT_p"]) <= .20 for r in combo) else "WEAK_POSTSELECTED",
                    "interpretation": "NONE",
                })
    worlds.sort(key=lambda r: (-float(r["selector_paid_joint_gain_bits"]), -float(r["raw_joint_lofo_gain_bits"]), str(r["world_id"])))
    worlds = worlds[:100]

    capacity_rows = channel_summary + [
        {"item":"SOURCE:EXACT_HUMAN_NONF84","count":len(exact),"positive":"","negative":"","uncertain_or_unscored":"","folios":len({folio(r['page']) for r in exact}),"pages":len({r['page'] for r in exact}),"sections":"","topology_mobile_rows":"","status":"AUDITED","detail":"One source lineage; not independent witnesses."},
        {"item":"SOURCE:EXACT_HUMAN_FAMILY_COVERED","count":len(exact_joined),"positive":"","negative":"","uncertain_or_unscored":"","folios":len({folio(r['page']) for r in exact_joined}),"pages":len({r['page'] for r in exact_joined}),"sections":"","topology_mobile_rows":"","status":"AUDITED","detail":"Source-native family consensus coverage."},
        {"item":"SOURCE:GDT327_COVERED_EXACT_HUMAN","count":sum(r['locus'] in gdt_by_locus for r in exact_joined),"positive":"","negative":"","uncertain_or_unscored":"","folios":"","pages":"","sections":"","topology_mobile_rows":"","status":"SPARSE","detail":"Exact joint tuples cannot cover the label atlas; no PAGE_HOST backfill."},
        {"item":"SOURCE:SPECIAL_CIRCLE_OCCUPANCY","count":len(special),"positive":sum(r['occupancy_state']=='ABSENT' for r in special),"negative":sum(r['occupancy_state']=='TRANSCRIBED' for r in special),"uncertain_or_unscored":sum(r['occupancy_state']=='UNREADABLE_TRACE' for r in special),"folios":len({r['physical_folio'] for r in special}),"pages":len({r['page'] for r in special}),"sections":"A/Z/C","topology_mobile_rows":"","status":"NO_BINARY_CAPACITY","detail":"One true absence and one unreadable trace across 504 slots; retained as capacity evidence only."},
    ]

    strong_tags = {"REL_EXPLICIT_ATTACHMENT", "REL_ENCLOSURE", "REL_OVERLAP_OR_CONTACT"}
    unit_types: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in exact_joined:
        for tag in set(filter(None, row["local_relation_tags"].split(";"))) & strong_tags:
            unit_types[(row["page"], row["unit"])].add(tag)
    mixed_units = sum(len(v) >= 2 for v in unit_types.values())
    unhedged_unit_types: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in exact_joined:
        if row["certainty"] != "UNHEDGED":
            continue
        for tag in set(filter(None, row["local_relation_tags"].split(";"))) & strong_tags:
            unhedged_unit_types[(row["page"], row["unit"])].add(tag)
    unhedged_mixed_units = sum(len(v) >= 2 for v in unhedged_unit_types.values())
    best_atlas = min(atlas_rows, key=lambda r: float(r["nuisance_maxT_p"])) if atlas_rows else None
    best_world = worlds[0] if worlds else None
    counter_rows = [
        {"counterexample_id":"C01_SHARED_SOURCE_LINEAGE","evidence":"All 1,192 exact-locus human rows descend from one Stolfi source file; derived tags/crosswalks are not independent witnesses.","implication":"Joint evidence cannot multiply source views as replications."},
        {"counterexample_id":"C02_STRONG_RELATION_UNIT_CONFOUND","evidence":f"Source-defined units containing two or more strong exact-local relation types: {mixed_units} with hedged evidence, {unhedged_mixed_units} after restricting to unhedged comments.","implication":"Strong relation types have little or no within-unit mobility; page/unit confounding remains primary."},
        {"counterexample_id":"C03_GDT327_LABEL_COVERAGE","evidence":f"Only {sum(r['locus'] in gdt_by_locus for r in exact_joined)} of {len(exact_joined)} family-covered exact annotations have GDT327 exact joint tuples.","implication":"The executable tuple grammar cannot currently carry the broad label-grounding analysis."},
        {"counterexample_id":"C04_SPECIAL_CIRCLE_ABSENCE","evidence":"The frozen 504-slot special-circle inventory has one ABSENT slot and one UNREADABLE_TRACE.","implication":"Occupancy is not a replicated binary grounding axis."},
        {"counterexample_id":"C05_BEST_MAXT","evidence":f"Best retained nuisance maxT p={best_atlas['nuisance_maxT_p'] if best_atlas else 'NA'} for {best_atlas['channel'] if best_atlas else 'NA'} / {best_atlas['formal_feature'] if best_atlas else 'NA'}.","implication":"Nominal local associations must be read against the complete state-blind search."},
        {"counterexample_id":"C06_JOINT_WORLD_COST","evidence":f"Best postselected joint paid gain={best_world['selector_paid_joint_gain_bits'] if best_world else 'NA'} bits.","implication":"A combined world may summarize dirty leads but does not become a confirmed latent-role system."},
    ]

    paths = {
        "inventory": ART / "gdt360_annotation_inventory.tsv",
        "join": ART / "gdt360_visual_formal_join.tsv",
        "atlas": ART / "gdt360_candidate_atlas.tsv",
        "worlds": ART / "gdt360_joint_worlds.tsv",
        "capacity": ART / "gdt360_capacity_gaps.tsv",
        "counter": ART / "gdt360_counterexamples.tsv",
    }
    write_tsv(paths["inventory"], inventory_rows)
    write_tsv(paths["join"], join_rows)
    write_tsv(paths["atlas"], atlas_rows)
    write_tsv(paths["worlds"], worlds, ["world_id","formal_feature","rule_count","visual_endpoints","directions","evidence_families","evidence_lineages","raw_joint_lofo_gain_bits","complexity_cost_bits","selector_paid_joint_gain_bits","pairwise_locus_overlap_count","union_locus_count","latent_role","label","interpretation"])
    write_tsv(paths["capacity"], capacity_rows)
    write_tsv(paths["counter"], counter_rows)

    interesting = sum(r["label"] == "INTERESTING_EXPLORATORY" for r in atlas_rows)
    paid_worlds = sum(float(r["selector_paid_joint_gain_bits"]) > 0 for r in worlds)
    interesting_worlds = sum(r["label"] == "INTERESTING_EXPLORATORY" for r in worlds)
    if interesting_worlds:
        status = "EXPLORATORY_MULTICHANNEL_FORMAL_LEAD"
    elif interesting:
        status = "EXPLORATORY_SINGLE_CHANNEL_LEADS_ONLY"
    else:
        status = "EXISTING_ANNOTATIONS_YIELD_ONLY_CONFOUNDED_WEAK_LEADS"

    global_ranked = sorted(atlas_rows, key=lambda r: (priority[str(r["label"])], -float(r["lofo_gain_bits"]), float(r["nuisance_maxT_p"]), str(r["candidate_id"])))
    global_top = global_ranked[0] if global_ranked else None
    result = {
        "experiment":"GDT360", "schema":"GDT360_EXISTING_ANNOTATION_JOINT_GROUNDING_V1", "status":status,
        "settings": {"permutation_worlds":WORLD_COUNT,"seed_label":SEED_LABEL,"feature_library_state_blind":True,"identical_masks_deduplicated":True,"raw_feature_descriptions":len(raw_features),"held_unit":"physical_folio","nuisance":"section|currier|hand|kind|code","new_visual_observations":0},
        "counts": {"nonf84_exact_human_rows":len(exact),"exact_human_family_covered":len(exact_joined),"gdt327_covered_exact_human":sum(r['locus'] in gdt_by_locus for r in exact_joined),"annotation_cases":len(inventory_rows),"formal_join_rows":len(join_rows),"unique_formal_loci":len(formal_loci),"state_blind_features":len(features),"scored_endpoints":endpoint_count,"full_candidate_scores":len(score_rows),"published_candidate_rows":len(atlas_rows),"joint_worlds":len(worlds),"interesting_candidate_rows":interesting,"positive_paid_joint_worlds":paid_worlds,"interesting_joint_worlds":interesting_worlds,"strong_relation_mixed_units":mixed_units,"strong_relation_unhedged_mixed_units":unhedged_mixed_units},
        "top_candidate": {k:v for k,v in (global_top.items() if global_top else []) if k in {"channel","formal_feature","aliases","label","lofo_gain_bits","selector_paid_gain_bits","nuisance_local_p","nuisance_maxT_p","topology_local_p","opportunity_local_p","opportunity_mobile_rows","positive_held_folios"}},
        "top_joint_world": best_world or {},
        "interpretation": "Existing annotations were jointly searched without new visual acquisition. Retained associations are exploratory visual/formal leads only; source lineage, topology mobility, page/register dependence, held-folio behavior, and search cost determine whether targeted acquisition is warranted.",
        "source_access": {"new_images_opened":False,"new_visual_descriptions_created":False,"catalogue_search_performed":False,"f84_rows_parsed_retained_joined_or_scored":False,"f84_images_opened":False},
        "claim_ceiling":"Neutral visual/formal association ranking only; no semantic role, object name, word, morpheme, POS, sound, language, plaintext, or translation.",
        "guard_stats": {name:{"seen":stats.lines_seen,"selected":stats.selected,"skipped_forbidden":stats.skipped_forbidden,"skipped_not_allowed":stats.skipped_not_allowed} for name,stats in (("exact",exact_stats),("loci",loci_stats),("groups",groups_stats),("gdt327",gdt327_stats),("gdt002",old_join_stats),("crosswalk",crosswalk_stats),("clothing",clothing_stats),("tail",tail_stats),("barrel",barrel_stats),("ray",ray_stats),("special",special_stats),("facing",facing_stats))},
        "inputs": {str(path.relative_to(ROOT)):sha(path) for path in INPUTS.values()},
        "outputs": {str(path.relative_to(ROOT)):sha(path) for path in paths.values()},
        "documents": {str(path.relative_to(ROOT)):sha(path) for path in (EXP/"README.md",EXP/"METHOD.md",EXP/"SOURCE_AUDIT.md",EXP/"REPORT.md",EXP/"artifacts/README.md")},
        "implementation": {str(path.relative_to(ROOT)):sha(path) for path in (Path(__file__), EXP/"src/validate.py")},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt360_result.json").write_bytes(stable(result))
    print(json.dumps({"status":status,"counts":result["counts"],"top_candidate":result["top_candidate"],"top_joint_world":result["top_joint_world"]},indent=2))


if __name__ == "__main__":
    main()
