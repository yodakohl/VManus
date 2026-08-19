#!/usr/bin/env python3
"""Apply the four frozen GDT378 signatures to the f84-free target once."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
FREEZE = ART / "gdt378_voynich_target_design_freeze.json"
SIGNATURES = ART / "gdt378_secondary_transfer_signature_freeze.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj):
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def opaque(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    if not rows:
        raise ValueError(f"No rows for {path}")
    if path.suffix == ".gz":
        raw = path.open("wb")
        gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
        handle = io.TextIOWrapper(gz, encoding="utf-8", newline="")
    else:
        handle = path.open("w", encoding="utf-8", newline="")
    with handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sigmoid(values):
    z = np.clip(values, -40, 40)
    return np.where(z >= 0, 1 / (1 + np.exp(-z)), np.exp(z) / (1 + np.exp(z)))


def rankdata(values):
    values = np.asarray(values, float)
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + j + 1) / 2
        i = j
    return ranks


def within_record_rank(scores, record_keys):
    out = np.zeros(len(scores), float)
    grouped = defaultdict(list)
    for i, key in enumerate(record_keys):
        grouped[key].append(i)
    for ids in grouped.values():
        local = rankdata(scores[ids])
        for index, rank in zip(ids, local):
            out[index] = (rank - .5) / len(ids)
    return out


def size_bucket(value):
    return "A" if value <= 4 else "B" if value <= 8 else "C" if value <= 16 else "D"


def frequency_bucket(value):
    return "0" if value == 0 else "1" if value == 1 else "2-3" if value <= 3 else "4-7" if value <= 7 else "8-15" if value <= 15 else "16+"


def closure(row, is_last_on_line=False):
    if row["dy_closure"] == "1":
        return "DY"
    if row["b3"] == "1":
        return "B3"
    return "LINE_END" if is_last_on_line else "OTHER"


def source_group_id(row):
    return opaque(["SOURCE_GROUP", row["joint_tuple_id"], row["observed_wrapper"]])


def build_elements(source, resolution):
    by_record = defaultdict(list)
    for source_index, row in enumerate(source):
        by_record[(row["page"], int(row["record_ordinal"]))].append((source_index, row))
    page_records = defaultdict(list)
    for page, record in by_record:
        page_records[page].append(record)
    for page in page_records:
        page_records[page] = sorted(set(page_records[page]))
    elements = []
    if resolution in {"ATOMIC_JOINT_TUPLE", "SOURCE_GROUP"}:
        for key in sorted(by_record, key=lambda x: (x[0], x[1])):
            values = sorted(by_record[key], key=lambda pair: pair[0])
            count = len(values)
            line_count = len({row["locus"] for _, row in values})
            max_record = max(page_records[key[0]])
            for ordinal, (source_index, row) in enumerate(values, 1):
                group_index = int(row["group_index"])
                group_count = int(row["group_count"])
                line_position = "SINGLE" if group_count == 1 else "START" if group_index == 1 else "END" if group_index == group_count else "MIDDLE"
                identity = row["joint_tuple_id"] if resolution == "ATOMIC_JOINT_TUPLE" else source_group_id(row)
                elements.append({
                    "unit_id": row["event_id_sha256"], "opaque_form_id": identity,
                    "domain": row["register"], "collection_id": row["page"],
                    "record_id": f"{row['page']}:R{row['record_ordinal']}",
                    "record_ordinal": int(row["record_ordinal"]), "element_ordinal": ordinal,
                    "record_element_count": count, "relative_position": ordinal / max(1, count),
                    "surface_length": 1, "direct_token_count": 1, "physical_line_count": line_count,
                    "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
                    "section": row["section"], "register": row["register"], "currier": row["currier"], "hand": row["hand"],
                    "line_position": line_position, "within_field_position": row["within_field_position"],
                    "unit_length": 1, "closure": closure(row, group_index == group_count),
                    "record_position_quartile": min(3, int(4 * (int(row["record_ordinal"]) - 1) / max(1, max_record))),
                    "candidate_id": identity, "candidate_family": "EXACT_ATOMIC_ID" if resolution == "ATOMIC_JOINT_TUPLE" else "EXACT_SOURCE_GROUP_ID",
                    "source_index": source_index,
                })
        return elements

    # FIELD_CONSTRUCTION_SPAN is the base observation for exact spans and slots.
    fields = defaultdict(list)
    for source_index, row in enumerate(source):
        fields[(row["page"], int(row["record_ordinal"]), row["locus"], int(row["field_ordinal"]))].append((source_index, row))
    record_fields = defaultdict(list)
    for field_key, values in fields.items():
        record_fields[field_key[:2]].append((min(index for index, _ in values), field_key, sorted(values)))
    for record_key in record_fields:
        record_fields[record_key].sort()
    for key in sorted(record_fields, key=lambda x: (x[0], x[1])):
        values = record_fields[key]
        count = len(values)
        line_count = len({field_key[2] for _, field_key, _ in values})
        max_record = max(page_records[key[0]])
        by_line = defaultdict(list)
        for position, (_, field_key, _) in enumerate(values):
            by_line[field_key[2]].append(position)
        line_order = {locus: rank for rank, locus in enumerate(dict.fromkeys(field_key[2] for _, field_key, _ in values))}
        for ordinal, (first_index, field_key, group_values) in enumerate(values, 1):
            _, _, locus, field_ordinal = field_key
            row = group_values[-1][1]
            ids = [source_group_id(item) for _, item in group_values]
            identity = opaque(["FIELD_CONSTRUCTION_SPAN", ids])
            line_fields = by_line[locus]
            field_local = line_fields.index(ordinal - 1)
            within = "SINGLE" if len(line_fields) == 1 else "FIRST" if field_local == 0 else "LAST" if field_local + 1 == len(line_fields) else "MIDDLE"
            line_rank = line_order[locus]
            line_position = "SINGLE" if line_count == 1 else "START" if line_rank == 0 else "END" if line_rank + 1 == line_count else "MIDDLE"
            close = closure(row, field_local + 1 == len(line_fields))
            start = "1" if ordinal == 1 else "2" if ordinal == 2 else "3" if ordinal == 3 else "4+"
            reverse = count - ordinal
            end = "LAST" if reverse == 0 else "PENULTIMATE" if reverse == 1 else "ANTEPENULTIMATE" if reverse == 2 else "EARLIER"
            quartile = f"Q{min(3, int(4 * (ordinal - 1) / max(1, count)))}"
            elements.append({
                "unit_id": opaque(["FIELD_EVENT", key[0], key[1], locus, field_ordinal]), "opaque_form_id": identity,
                "domain": row["register"], "collection_id": row["page"], "record_id": f"{row['page']}:R{row['record_ordinal']}",
                "record_ordinal": int(row["record_ordinal"]), "element_ordinal": ordinal,
                "record_element_count": count, "relative_position": ordinal / max(1, count),
                "surface_length": len(group_values), "direct_token_count": len(group_values), "physical_line_count": line_count,
                "page": row["page"], "physical_folio": row["physical_folio"], "locus": locus,
                "section": row["section"], "register": row["register"], "currier": row["currier"], "hand": row["hand"],
                "line_position": line_position, "within_field_position": within,
                "unit_length": len(group_values), "closure": close,
                "record_position_quartile": min(3, int(4 * (int(row["record_ordinal"]) - 1) / max(1, max_record))),
                "candidate_id": identity, "candidate_family": "EXACT_FIELD_SPAN_ID",
                "slot_values": {"FROM_START": start, "FROM_END": end, "RELATIVE_QUARTILE": quartile, "CLOSURE": close, "FROM_START_X_CLOSURE": f"{start}__{close}"},
                "source_index": first_index,
            })
    return elements


def make_features(elements, held_folio):
    n = len(elements)
    by_record = defaultdict(list)
    by_collection = defaultdict(list)
    by_domain = defaultdict(list)
    for i, row in enumerate(elements):
        record = (row["domain"], row["collection_id"], row["record_id"])
        by_record[record].append(i)
        by_collection[(row["domain"], row["collection_id"])].append(i)
        by_domain[row["domain"]].append(i)
    record_order = {}
    for collection, ids in by_collection.items():
        record_order[collection] = sorted({(elements[i]["record_ordinal"], elements[i]["record_id"]) for i in ids})
    global_stats = {}
    for domain in by_domain:
        stats = defaultdict(lambda: {"n": 0, "records": set(), "prev": set(), "next": set(), "positions": []})
        for record, ids in by_record.items():
            if record[0] != domain or elements[ids[0]]["physical_folio"] == held_folio:
                continue
            ids.sort(key=lambda i: elements[i]["element_ordinal"])
            forms = [elements[i]["opaque_form_id"] for i in ids]
            for j, i in enumerate(ids):
                item = stats[forms[j]]
                item["n"] += 1
                item["records"].add(record)
                item["positions"].append(elements[i]["relative_position"])
                if j:
                    item["prev"].add(forms[j - 1])
                if j + 1 < len(forms):
                    item["next"].add(forms[j + 1])
        global_stats[domain] = stats
    nuisance = [None] * n
    scope = [None] * n
    neighbor = [None] * n
    record_keys = [None] * n
    for record, ids in by_record.items():
        ids.sort(key=lambda i: elements[i]["element_ordinal"])
        forms = [elements[i]["opaque_form_id"] for i in ids]
        count = Counter(forms)
        positions = defaultdict(list)
        for j, form in enumerate(forms):
            positions[form].append(j)
        order = record_order[(record[0], record[1])]
        names = [item[1] for item in order]
        record_position = names.index(record[2])
        previous_ids = by_record.get((record[0], record[1], names[record_position - 1]), []) if record_position else []
        next_ids = by_record.get((record[0], record[1], names[record_position + 1]), []) if record_position + 1 < len(names) else []
        previous_set = {elements[i]["opaque_form_id"] for i in previous_ids}
        next_set = {elements[i]["opaque_form_id"] for i in next_ids}
        current_set = set(forms)
        previous_jaccard = len(current_set & previous_set) / max(1, len(current_set | previous_set))
        next_jaccard = len(current_set & next_set) / max(1, len(current_set | next_set))
        max_record = max(item[0] for item in order)
        for j, i in enumerate(ids):
            row = elements[i]
            form = forms[j]
            local_positions = positions[form]
            before = [value for value in local_positions if value < j]
            after = [value for value in local_positions if value > j]
            item = global_stats[record[0]].get(form, {"n": 0, "records": set(), "prev": set(), "next": set(), "positions": []})
            p = row["relative_position"]
            nuisance[i] = [1.0, math.log1p(row["record_element_count"]), p, p * p, math.log1p(row["surface_length"]), math.log1p(row["direct_token_count"]), float(j == 0), float(j + 1 == len(ids)), row["record_ordinal"] / max(1, max_record), math.log1p(row["physical_line_count"])]
            scope[i] = [(len(ids) - j - 1) / max(1, len(ids)), j / max(1, len(ids)), (j - before[-1]) / max(1, len(ids)) if before else 1.0, (after[0] - j) / max(1, len(ids)) if after else 1.0, len(set(forms[:j])) / max(1, len(ids)), len(set(forms[j + 1:])) / max(1, len(ids)), float(bool(before)), float(bool(after))]
            external_positions = item["positions"]
            neighbor[i] = [float(j > 0 and forms[j - 1] == form), float(j + 1 < len(ids) and forms[j + 1] == form), math.log1p(count[form]), len(current_set) / max(1, len(ids)), float(form in previous_set), float(form in next_set), previous_jaccard, next_jaccard, float(j > 0 and j + 1 < len(ids) and forms[j - 1] == forms[j + 1]), float(j >= 2 and forms[j - 2] == form), float(j + 2 < len(ids) and forms[j + 2] == form), math.log1p(item["n"]), math.log1p(len(item["records"])), math.log1p(len(item["prev"])), math.log1p(len(item["next"])), sum(external_positions) / len(external_positions) if external_positions else .5, float(np.std(external_positions)) if external_positions else 0.0]
            record_keys[i] = record
    return np.asarray(nuisance), np.asarray(scope), np.asarray(neighbor), record_keys


def apply_signature(signature, nuisance, scope, neighbor, record_keys):
    if signature["model_kind"] == "NUISANCE_PLUS_NEIGHBOR":
        x = np.column_stack([nuisance, neighbor])
    elif signature["model_kind"] == "NUISANCE_PLUS_SCOPE_PLUS_NEIGHBOR":
        x = np.column_stack([nuisance, scope, neighbor])
    else:
        raise ValueError(signature["model_kind"])
    beta = np.asarray(signature["coefficients"], float)
    mean = np.asarray(signature["standardization_mean_excluding_intercept"], float)
    scale = np.asarray(signature["standardization_scale_excluding_intercept"], float)
    z = x.copy()
    z[:, 1:] = (z[:, 1:] - mean) / scale
    score = np.clip(sigmoid(z @ beta), 1e-9, 1 - 1e-9)
    if signature["application_postprocess"] == "WITHIN_RECORD_RANK":
        score = within_record_rank(score, record_keys)
    return score


def placement_components(element, frequency):
    return (
        element["section"], element["register"], element["currier"], element["hand"],
        size_bucket(element["record_element_count"]), str(element["record_position_quartile"]),
        element["line_position"], element["within_field_position"], size_bucket(element["unit_length"]),
        element["closure"], frequency_bucket(frequency),
    )


def backoff_keys(components):
    section, register, currier, hand, record_length, record_position, line_position, within_position, unit_length, close, frequency = components
    return [
        components,
        (section, register, currier, record_length, record_position, line_position, within_position, unit_length, close, frequency),
        (section, register, record_length, record_position, line_position, within_position, unit_length, close, frequency),
        (register, record_length, record_position, line_position, within_position, unit_length, close, frequency),
        (register, line_position, within_position, unit_length, close, frequency),
        (register, close, frequency),
        (register, frequency),
        (),
    ]


def placement_residuals(elements, scores, held_folio):
    train = [i for i, row in enumerate(elements) if row["physical_folio"] != held_folio]
    test = [i for i, row in enumerate(elements) if row["physical_folio"] == held_folio]
    train_set = set(train)
    frequency = Counter((row["register"], row["opaque_form_id"]) for i, row in enumerate(elements) if i in train_set)
    keys = [backoff_keys(placement_components(row, frequency[(row["register"], row["opaque_form_id"])])) for row in elements]
    sums = [defaultdict(float) for _ in range(8)]
    counts = [Counter() for _ in range(8)]
    for i in train:
        for level, key in enumerate(keys[i]):
            sums[level][key] += float(scores[i])
            counts[level][key] += 1

    def expected(i, exclude):
        for level, key in enumerate(keys[i]):
            count = counts[level][key] - int(exclude)
            if count >= 4:
                total = sums[level][key] - (float(scores[i]) if exclude else 0.0)
                return total / count, level
        return float(np.mean(scores[train])), 8

    residual = np.zeros(len(elements), float)
    baseline = np.zeros(len(elements), float)
    level = np.zeros(len(elements), int)
    for i in train:
        baseline[i], level[i] = expected(i, True)
        residual[i] = scores[i] - baseline[i]
    for i in test:
        baseline[i], level[i] = expected(i, False)
        residual[i] = scores[i] - baseline[i]
    strata = [opaque(["NULL_STRATUM", element["physical_folio"], *keys[i][0]]) for i, element in enumerate(elements)]
    return train, test, residual, baseline, level, strata


def memberships(elements, resolution):
    if resolution != "FIELD_CONSTRUCTION_SPAN":
        return {elements[0]["candidate_family"]: [row["candidate_id"] for row in elements]}
    result = {"EXACT_FIELD_SPAN_ID": [row["candidate_id"] for row in elements]}
    for family in ("FROM_START", "FROM_END", "RELATIVE_QUARTILE", "CLOSURE", "FROM_START_X_CLOSURE"):
        result[family] = [row["slot_values"][family] for row in elements]
    return result


def main():
    freeze = json.loads(FREEZE.read_text())
    signature_freeze = json.loads(SIGNATURES.read_text())
    assert freeze["status"] == "FROZEN_BEFORE_VOYNICH_TARGET_SCORING" and not freeze["voynich_scored"]
    assert sha(SOURCE) == freeze["inputs"][str(SOURCE.relative_to(ROOT))]
    source = read(SOURCE)
    assert len(source) == 8448 and not any(any(row[key].lower().startswith("f84") for key in ("page", "physical_folio", "locus")) for row in source)
    signatures = signature_freeze["signatures"]
    folios = sorted({row["physical_folio"] for row in source})
    base_resolutions = ["ATOMIC_JOINT_TUPLE", "SOURCE_GROUP", "FIELD_CONSTRUCTION_SPAN"]
    elements_by_resolution = {resolution: build_elements(source, resolution) for resolution in base_resolutions}
    event_rows = []
    accumulator = defaultdict(lambda: {"scores": [], "residuals": [], "folios": defaultdict(list), "registers": defaultdict(list), "sections": set(), "threshold_hits": 0, "predicted_events": 0, "sse_baseline": 0.0, "sse_candidate": 0.0, "fold_gain": defaultdict(float)})
    residual_vectors = {}
    strata_vectors = {}
    membership_vectors = {resolution: memberships(elements_by_resolution[resolution], resolution) for resolution in base_resolutions}

    for held_folio in folios:
        for resolution in base_resolutions:
            elements = elements_by_resolution[resolution]
            nuisance, scope, neighbor, record_keys = make_features(elements, held_folio)
            for signature in signatures:
                signature_id = signature["anonymous_signature_id"]
                scores = apply_signature(signature, nuisance, scope, neighbor, record_keys)
                train, test, residuals, baselines, levels, strata = placement_residuals(elements, scores, held_folio)
                residual_vectors.setdefault((signature_id, resolution), np.zeros(len(elements), float))[test] = residuals[test]
                strata_vectors.setdefault(resolution, np.empty(len(elements), object))[test] = np.asarray(strata, object)[test]
                threshold = float(np.quantile(scores[train], signature["threshold_quantile"]))
                member = membership_vectors[resolution]
                train_values = {}
                for family, candidate_ids in member.items():
                    grouped = defaultdict(list)
                    for i in train:
                        grouped[candidate_ids[i]].append(float(residuals[i]))
                    train_values[family] = {candidate: (len(values), sum(values) / len(values)) for candidate, values in grouped.items()}
                for i in test:
                    element = elements[i]
                    event_rows.append({
                        "signature_id": signature_id,
                        "base_resolution": resolution,
                        "unit_id": element["unit_id"],
                        "page": element["page"], "physical_folio": element["physical_folio"], "locus": element["locus"],
                        "section": element["section"], "register": element["register"], "currier": element["currier"], "hand": element["hand"],
                        "score": f"{scores[i]:.12f}", "placement_baseline": f"{baselines[i]:.12f}", "placement_residual": f"{residuals[i]:.12f}",
                        "baseline_backoff_level": int(levels[i]), "training_threshold": f"{threshold:.12f}", "threshold_hit": int(scores[i] >= threshold),
                        "null_stratum_id": strata[i], "semantic_state": "UNASSIGNED",
                    })
                    for family, candidate_ids in member.items():
                        target_resolution = "GRAMMAR_SLOT_POSITION" if family in freeze["slot_families"] else resolution
                        candidate = candidate_ids[i]
                        key = (signature_id, target_resolution, family, candidate)
                        item = accumulator[key]
                        score = float(scores[i])
                        residual = float(residuals[i])
                        item["scores"].append(score)
                        item["residuals"].append(residual)
                        item["folios"][held_folio].append(residual)
                        item["registers"][element["register"]].append(residual)
                        item["sections"].add(element["section"])
                        item["threshold_hits"] += int(score >= threshold)
                        training = train_values[family].get(candidate)
                        if training:
                            count, mean = training
                            prediction = mean * count / (count + freeze["candidate_shrinkage"])
                            item["predicted_events"] += 1
                            item["sse_baseline"] += residual * residual
                            item["sse_candidate"] += (residual - prediction) ** 2
                            item["fold_gain"][held_folio] += residual * residual - (residual - prediction) ** 2

    candidate_rows = []
    powered_keys = set()
    for key, item in accumulator.items():
        signature_id, resolution, family, candidate = key
        event_count = len(item["scores"])
        folio_count = len(item["folios"])
        register_count = len(item["registers"])
        powered = event_count >= freeze["minimum_events"] and folio_count >= freeze["minimum_physical_folios"] and register_count >= freeze["minimum_registers"]
        if powered:
            powered_keys.add(key)
        mean_residual = float(np.mean(item["residuals"]))
        sd_residual = float(np.std(item["residuals"]))
        statistic = abs(mean_residual) / max(1e-9, sd_residual / math.sqrt(event_count))
        positive_residual_folios = sum(np.mean(values) > 0 for values in item["folios"].values())
        positive_residual_registers = sum(np.mean(values) > 0 for values in item["registers"].values())
        eligible_gain_folds = len(item["fold_gain"])
        positive_gain_folds = sum(value > 0 for value in item["fold_gain"].values())
        candidate_rows.append({
            "signature_id": signature_id, "resolution": resolution, "candidate_family": family, "candidate_id": candidate,
            "events": event_count, "predicted_events": item["predicted_events"], "physical_folios": folio_count,
            "registers": register_count, "sections": len(item["sections"]), "mean_score": f"{np.mean(item['scores']):.12f}",
            "mean_placement_residual": f"{mean_residual:.12f}", "residual_statistic_abs": f"{statistic:.12f}",
            "threshold_hit_fraction": f"{item['threshold_hits']/event_count:.12f}",
            "positive_residual_folio_fraction": f"{positive_residual_folios/folio_count:.12f}",
            "positive_residual_registers": positive_residual_registers,
            "held_sse_gain_over_placement": f"{item['sse_baseline']-item['sse_candidate']:.12f}",
            "eligible_gain_folds": eligible_gain_folds, "positive_gain_folds": positive_gain_folds,
            "positive_gain_folio_fraction": f"{positive_gain_folds/max(1,eligible_gain_folds):.12f}",
            "powered": int(powered), "max_family_p": "", "candidate_gate": "PENDING_NULL" if powered else "FAIL_POWER",
            "anonymous_class": "UNASSIGNED", "semantic_state": "UNASSIGNED",
        })

    # One shared maxT null. The same within-stratum permutation is reused across signatures.
    base_strata = {}
    mobility = {}
    for resolution, elements in elements_by_resolution.items():
        labels = strata_vectors[resolution]
        groups = defaultdict(list)
        for i, label in enumerate(labels):
            groups[label].append(i)
        base_strata[resolution] = [np.asarray(ids, int) for ids in groups.values() if len(ids) > 1]
        mobility[resolution] = sum(len(ids) for ids in base_strata[resolution])
    encoded_members = {}
    for resolution, families in membership_vectors.items():
        for family, values in families.items():
            unique = sorted(set(values))
            lookup = {value: i for i, value in enumerate(unique)}
            encoded_members[(resolution, family)] = (np.asarray([lookup[value] for value in values], int), unique, np.bincount(np.asarray([lookup[value] for value in values], int)))
    powered_codes = {}
    for (resolution, family), (_, unique, _) in encoded_members.items():
        target_resolution = "GRAMMAR_SLOT_POSITION" if family in freeze["slot_families"] else resolution
        for signature in signatures:
            signature_id = signature["anonymous_signature_id"]
            powered_codes[(signature_id, resolution, family)] = np.asarray([i for i, candidate in enumerate(unique) if (signature_id, target_resolution, family, candidate) in powered_keys], int)

    maxima = []
    for world in range(freeze["null_worlds"]):
        world_max = 0.0
        permutations = {}
        for resolution, elements in elements_by_resolution.items():
            rng = np.random.default_rng(378500000 + world * 7 + base_resolutions.index(resolution))
            permutation = np.arange(len(elements))
            for ids in base_strata[resolution]:
                permutation[ids] = rng.permutation(ids)
            permutations[resolution] = permutation
        for signature in signatures:
            signature_id = signature["anonymous_signature_id"]
            for resolution, families in membership_vectors.items():
                residual = residual_vectors[(signature_id, resolution)][permutations[resolution]]
                for family in families:
                    codes, _, counts = encoded_members[(resolution, family)]
                    eligible = powered_codes[(signature_id, resolution, family)]
                    if not len(eligible):
                        continue
                    means = np.bincount(codes, weights=residual, minlength=len(counts)) / counts
                    second = np.bincount(codes, weights=residual * residual, minlength=len(counts)) / counts
                    local_sd = np.sqrt(np.maximum(second - means * means, 1e-18))
                    stats = np.abs(means[eligible]) / (local_sd[eligible] / np.sqrt(counts[eligible]))
                    world_max = max(world_max, float(np.max(stats)))
        maxima.append(world_max)
    null_rows = [{"world": world, "max_abs_residual_statistic": f"{value:.12f}"} for world, value in enumerate(maxima)]

    row_by_key = {(row["signature_id"], row["resolution"], row["candidate_family"], row["candidate_id"]): row for row in candidate_rows}
    for key in powered_keys:
        row = row_by_key[key]
        observed = float(row["residual_statistic_abs"])
        p = (1 + sum(value >= observed for value in maxima)) / (1 + len(maxima))
        row["max_family_p"] = f"{p:.12f}"
        base_resolution = "FIELD_CONSTRUCTION_SPAN" if row["resolution"] == "GRAMMAR_SLOT_POSITION" else row["resolution"]
        capacity_ok = mobility[base_resolution] >= freeze["null_minimum_mobile_events"] and mobility[base_resolution] / len(elements_by_resolution[base_resolution]) >= freeze["null_minimum_mobile_fraction"]
        passes = (
            capacity_ok
            and float(row["held_sse_gain_over_placement"]) > 0
            and float(row["positive_gain_folio_fraction"]) >= freeze["minimum_positive_gain_folio_fraction"]
            and float(row["mean_placement_residual"]) > 0
            and float(row["positive_residual_folio_fraction"]) >= freeze["minimum_positive_residual_folio_fraction"]
            and int(row["positive_residual_registers"]) >= freeze["minimum_positive_residual_registers"]
            and p <= freeze["max_family_p_max"]
        )
        row["candidate_gate"] = "PASS" if passes else "FAIL"
        row["anonymous_class"] = f"{row['signature_id']}_CONSTRUCTION_CANDIDATE" if passes else "UNASSIGNED"
    candidate_rows.sort(key=lambda row: (row["candidate_gate"] != "PASS", not int(row["powered"]), float(row["max_family_p"] or 1), -float(row["mean_placement_residual"]), row["signature_id"], row["resolution"], row["candidate_family"], row["candidate_id"]))

    summary_rows = []
    for signature in signatures:
        signature_id = signature["anonymous_signature_id"]
        for resolution in freeze["resolutions"]:
            local = [row for row in candidate_rows if row["signature_id"] == signature_id and row["resolution"] == resolution]
            base_resolution = "FIELD_CONSTRUCTION_SPAN" if resolution == "GRAMMAR_SLOT_POSITION" else resolution
            summary_rows.append({
                "signature_id": signature_id, "resolution": resolution,
                "events": len(elements_by_resolution[base_resolution]), "candidates": len(local),
                "powered_candidates": sum(int(row["powered"]) for row in local),
                "promoted_candidates": sum(row["candidate_gate"] == "PASS" for row in local),
                "null_mobile_events": mobility[base_resolution],
                "null_mobile_fraction": f"{mobility[base_resolution]/len(elements_by_resolution[base_resolution]):.12f}",
                "null_capacity_ok": int(mobility[base_resolution] >= freeze["null_minimum_mobile_events"] and mobility[base_resolution] / len(elements_by_resolution[base_resolution]) >= freeze["null_minimum_mobile_fraction"]),
            })

    event_path = ART / "gdt378_voynich_event_scores.tsv.gz"
    candidate_path = ART / "gdt378_voynich_candidate_atlas.tsv"
    summary_path = ART / "gdt378_voynich_resolution_summary.tsv"
    null_path = ART / "gdt378_voynich_null.tsv.gz"
    write(event_path, event_rows)
    write(candidate_path, candidate_rows)
    write(summary_path, summary_rows)
    write(null_path, null_rows)
    passed = [row for row in candidate_rows if row["candidate_gate"] == "PASS"]
    powered = [row for row in candidate_rows if int(row["powered"])]
    result = {
        "schema": "GDT378_VOYNICH_TARGET_RESULT_V1",
        "status": "ANONYMOUS_CONSTRUCTION_CANDIDATES_NOMINATED" if passed else "NO_STABLE_ANONYMOUS_FUNCTIONAL_CONSTRUCTION",
        "source_groups": len(source), "records": len({(row["page"], row["record_ordinal"]) for row in source}),
        "physical_folios": len(folios), "field_spans": len(elements_by_resolution["FIELD_CONSTRUCTION_SPAN"]),
        "signatures": len(signatures), "resolutions": len(freeze["resolutions"]),
        "candidate_rows": len(candidate_rows), "powered_candidates": len(powered), "promoted_candidates": len(passed),
        "best_powered_candidate": powered[0] if powered else None,
        "null_worlds": freeze["null_worlds"], "null_mobility": mobility,
        "semantic_assignments": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [SOURCE, FREEZE, SIGNATURES]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in [event_path, candidate_path, summary_path, null_path]},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        "claim_ceiling": "ANONYMOUS_MULTI_RESOLUTION_COMPARATOR_SIGNATURE_TRANSFER_ONLY",
    }
    result["content_hash"] = content(result)
    (ART / "gdt378_voynich_target_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "powered": len(powered), "promoted": len(passed), "mobility": mobility}))


if __name__ == "__main__":
    main()
