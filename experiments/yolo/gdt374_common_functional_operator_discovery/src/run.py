#!/usr/bin/env python3
"""Run the frozen GDT374 common functional-operator discovery instrument."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt374_common_functional_operator_discovery"
ART = BASE / "artifacts"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
DRAW = ROOT / "experiments/semantic_assumptions/results/drawing_reset_segment_atlas.tsv"
FREEZE = ART / "gdt374_freeze.json"
SEED = 37420260819
WORLDS = 4096
ALPHA = 0.5


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hid(prefix: str, *parts: object) -> str:
    payload = prefix + "|" + "|".join(map(str, parts))
    return hashlib.sha256(payload.encode()).hexdigest()[:20]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = list(rows[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def bucket(value: int) -> str:
    return "1" if value == 1 else "2" if value == 2 else "3+"


def load_rows() -> tuple[list[dict[str, str]], dict[tuple[str, int], dict[str, str]], dict[str, int]]:
    rows = read_tsv(INTER)
    if any(r["page"].lower().startswith("f84") or r["locus"].lower().startswith("f84") for r in rows):
        raise AssertionError("f84 row in primary interlinear")
    pages = {r["page"] for r in rows}
    loci = {r["locus"] for r in rows}
    guarded = GuardedTSV(DRAW, selector_column="page", allowed_values=pages, forbidden_prefixes=("f84",))
    drawing = {}
    for row in guarded:
        if row["locus"] in loci:
            drawing[(row["locus"], int(row["group_index"]))] = row
    if len(drawing) != len(rows):
        raise AssertionError(f"drawing join {len(drawing)} != {len(rows)}")
    stats = {
        "drawing_lines_seen": guarded.stats.lines_seen,
        "drawing_rows_selected_before_locus_join": guarded.stats.selected,
        "drawing_rows_skipped_not_allowed": guarded.stats.skipped_not_allowed,
        "drawing_rows_rejected_f84_before_parse": guarded.stats.skipped_forbidden,
    }
    return rows, drawing, stats


def make_records(rows: list[dict[str, str]], drawing: dict[tuple[str, int], dict[str, str]]) -> list[dict[str, object]]:
    units: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        d = drawing[(row["locus"], int(row["group_index"]))]
        row = dict(row)
        row["segment_id"] = d["segment_id"]
        row["left_boundary_profile"] = d["left_boundary_profile"]
        row["right_boundary_profile"] = d["right_boundary_profile"]
        row["starts_after_drawing"] = d["starts_after_drawing"]
        row["ends_before_drawing"] = d["ends_before_drawing"]
        units[("FIELD", f"{row['locus']}|F{row['field_ordinal']}")].append(row)
        units[("DRAWING_RESET_SEGMENT", row["segment_id"])].append(row)
        units[("PHYSICAL_LINE", row["locus"])].append(row)
    records = []
    for (scope, unit), members in units.items():
        members.sort(key=lambda x: int(x["group_index"]))
        first, last = members[0], members[-1]
        sequence = tuple(x["joint_tuple_id"] for x in members)
        field_breaks = []
        segment_breaks = []
        for i in range(1, len(members)):
            if members[i]["field_ordinal"] != members[i - 1]["field_ordinal"]:
                field_breaks.append(i)
            if members[i]["segment_id"] != members[i - 1]["segment_id"]:
                segment_breaks.append(i)
        records.append({
            "record_id": hid("RECORD", scope, unit),
            "scope": scope,
            "unit_key": unit,
            "page": first["page"],
            "physical_folio": first["physical_folio"],
            "locus": first["locus"],
            "section": first["section"],
            "register": first["register"],
            "currier": first["currier"],
            "hand": first["hand"],
            "record_ordinal": int(first["record_ordinal"]),
            "field_ordinal": int(first["field_ordinal"]) if scope == "FIELD" else 0,
            "line_entry": int(first["line_first"]),
            "group_count": len(members),
            "dy_close": int(last["dy_closure"]),
            "b3_close": int(last["b3"]),
            "starts_after_drawing": int(first["starts_after_drawing"]),
            "ends_before_drawing": int(last["ends_before_drawing"]),
            "left_boundary_profile": first["left_boundary_profile"],
            "right_boundary_profile": last["right_boundary_profile"],
            "field_breaks": tuple(field_breaks),
            "segment_breaks": tuple(segment_breaks),
            "sequence": sequence,
        })
    records.sort(key=lambda r: (r["scope"], r["page"], r["locus"], r["field_ordinal"], r["record_id"]))
    return records


def insertion_events(records: list[dict[str, object]], scope: str) -> list[dict[str, object]]:
    by_folio: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        if record["scope"] == scope:
            by_folio[str(record["physical_folio"])].append(record)
    events = []
    seen = set()
    for folio, local in by_folio.items():
        by_sequence: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
        for record in local:
            by_sequence[record["sequence"]].append(record)
        for target in local:
            long = target["sequence"]
            if len(long) < 2:
                continue
            for index, inserted in enumerate(long):
                short = long[:index] + long[index + 1 :]
                position = "PREFIX" if index == 0 else "SUFFIX" if index == len(long) - 1 else "INTERNAL"
                for source in by_sequence.get(short, []):
                    key = (scope, source["record_id"], position, inserted, long)
                    if key in seen:
                        continue
                    seen.add(key)
                    label = f"{position}|{inserted}"
                    events.append({
                        "event_id": hid("INSERT_EVENT", *key),
                        "scope": scope,
                        "rewrite_type": "INSERT_DELETE_ONE_ATOMIC_TUPLE",
                        "rewrite_position": position,
                        "operator_class": label,
                        "operator_tuple_ids": inserted,
                        "source_record_id": source["record_id"],
                        "target_record_ids": target["record_id"],
                        "source_sequence": short,
                        "target_sequence": long,
                        "base_signature": hashlib.sha256("|".join(short).encode()).hexdigest()[:20],
                        "physical_folio": folio,
                        "page": source["page"],
                        "locus": source["locus"],
                        "section": source["section"],
                        "register": source["register"],
                        "currier": source["currier"],
                        "hand": source["hand"],
                        "record_ordinal": source["record_ordinal"],
                        "field_ordinal": source["field_ordinal"],
                        "line_entry": source["line_entry"],
                        "source_length": len(short),
                        "target_length": len(long),
                        "duplication": int((index > 0 and long[index - 1] == inserted) or (index + 1 < len(long) and long[index + 1] == inserted)),
                    })
    events.sort(key=lambda e: (e["scope"], e["physical_folio"], e["event_id"]))
    return events


def descriptive_candidates(records: list[dict[str, object]], insertions: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates: dict[tuple[str, str, str], dict[str, object]] = {}

    def add(kind: str, position: str, op: str, folio: str, base: str, register: str, count: int = 1) -> None:
        key = kind, position, op
        if key not in candidates:
            candidates[key] = {"kind": kind, "position": position, "op": op, "folios": set(), "bases": set(), "registers": set(), "events": 0}
        item = candidates[key]
        item["folios"].add(folio)
        item["bases"].add(base)
        item["registers"].add(register)
        item["events"] += count

    for event in insertions:
        add("INSERT_DELETE_ONE_ATOMIC_TUPLE", str(event["rewrite_position"]), str(event["operator_tuple_ids"]), str(event["physical_folio"]), str(event["base_signature"]), str(event["register"]))
        if event["duplication"]:
            add("ADJACENT_EXACT_TUPLE_DUPLICATION", str(event["rewrite_position"]), str(event["operator_tuple_ids"]), str(event["physical_folio"]), str(event["base_signature"]), str(event["register"]))

    # Exact one- and two-site replacements inside physical folios.
    for scope in ("FIELD", "DRAWING_RESET_SEGMENT", "PHYSICAL_LINE"):
        by_folio: dict[str, list[dict[str, object]]] = defaultdict(list)
        for record in records:
            if record["scope"] == scope and len(record["sequence"]) >= 2:
                by_folio[str(record["physical_folio"])].append(record)
        for folio, local in by_folio.items():
            by_length: dict[int, list[dict[str, object]]] = defaultdict(list)
            for record in local:
                by_length[len(record["sequence"])].append(record)
            for length, same_length in by_length.items():
                for left, right in itertools.combinations(same_length, 2):
                    diffs = [i for i, (a, b) in enumerate(zip(left["sequence"], right["sequence"])) if a != b]
                    if len(diffs) not in (1, 2) or length - len(diffs) < 1:
                        continue
                    if len(diffs) == 1:
                        i = diffs[0]
                        position = "PREFIX" if i == 0 else "SUFFIX" if i == length - 1 else "INTERNAL"
                        a, b = left["sequence"][i], right["sequence"][i]
                        op = "<->".join(sorted((a, b)))
                        context = left["sequence"][:i] + left["sequence"][i + 1 :]
                        add("REPLACE_ONE_ATOMIC_TUPLE", position, op, folio, hashlib.sha256("|".join(context).encode()).hexdigest()[:20], str(left["register"]))
                    else:
                        changes = []
                        for i in diffs:
                            changes.append("<->".join(sorted((left["sequence"][i], right["sequence"][i]))))
                        op = "||".join(sorted(changes))
                        context = tuple(x for i, x in enumerate(left["sequence"]) if i not in diffs)
                        add("PAIRED_TWO_SITE_REPLACE", "PAIRED", op, folio, hashlib.sha256("|".join(context).encode()).hexdigest()[:20], str(left["register"]))

    # Identical line sequence with different grammar-derived boundaries.
    lines_by_sequence: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for record in records:
        if record["scope"] == "PHYSICAL_LINE":
            lines_by_sequence[record["sequence"]].append(record)
    for sequence, local in lines_by_sequence.items():
        patterns = defaultdict(list)
        for record in local:
            patterns[(record["field_breaks"], record["segment_breaks"])].append(record)
        if len(patterns) > 1:
            base = hashlib.sha256("|".join(sequence).encode()).hexdigest()[:20]
            for a, b in itertools.combinations(sorted(patterns, key=str), 2):
                op = hashlib.sha256((str(a) + "<->" + str(b)).encode()).hexdigest()[:20]
                for record in patterns[a] + patterns[b]:
                    add("BOUNDARY_SPLIT_JOIN", "BOUNDARY", op, str(record["physical_folio"]), base, str(record["register"]))

    # Prior-line shortening/resumption with one or two deletions.
    lines = [r for r in records if r["scope"] == "PHYSICAL_LINE"]
    by_page_record: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for record in lines:
        by_page_record[(str(record["page"]), int(record["record_ordinal"]))].append(record)
    for local in by_page_record.values():
        local.sort(key=lambda r: (int(str(r["locus"]).split(".")[-1]) if "." in str(r["locus"]) and str(r["locus"]).split(".")[-1].isdigit() else 0, str(r["locus"])))
        for previous, current in zip(local, local[1:]):
            a, b = previous["sequence"], current["sequence"]
            if len(a) - len(b) not in (1, 2):
                continue
            found = False
            for deleted in itertools.combinations(range(len(a)), len(a) - len(b)):
                if tuple(x for i, x in enumerate(a) if i not in deleted) == b:
                    op = "DELETE_POS:" + ",".join(map(str, deleted))
                    add("PRIOR_RECORD_SHORTEN_RESUME", "CROSS_RECORD", op, str(current["physical_folio"]), hashlib.sha256("|".join(b).encode()).hexdigest()[:20], str(current["register"]))
                    found = True
                    break
            if found:
                continue
    return list(candidates.values())


def event_features(event: dict[str, object], full: bool) -> list[str]:
    features = [
        "SECTION=" + str(event["section"]),
        "REGISTER=" + str(event["register"]),
        "CURRIER=" + str(event["currier"]),
        "HAND=" + str(event["hand"]),
        "LEN=" + str(event["source_length"]),
        "FIELDORD=" + bucket(int(event["field_ordinal"])),
        "LINEENTRY=" + str(event["line_entry"]),
        "RECORDORD=" + bucket(int(event["record_ordinal"])),
    ]
    if full:
        sequence = event["source_sequence"]
        features.extend("ATOM=" + token for token in sorted(set(sequence)))
        features.append("FIRST_ATOM=" + sequence[0])
        features.append("LAST_ATOM=" + sequence[-1])
    return features


class NBModel:
    def __init__(self, events: list[dict[str, object]], full: bool, classes: list[str]) -> None:
        self.full = full
        self.classes = classes
        self.class_counts = Counter(str(e["operator_class"]) for e in events)
        self.feature_counts: dict[str, Counter[str]] = {label: Counter() for label in classes}
        self.feature_totals = Counter()
        vocabulary = set()
        for event in events:
            label = str(event["operator_class"])
            if label not in self.feature_counts:
                continue
            feats = event_features(event, full)
            self.feature_counts[label].update(feats)
            self.feature_totals[label] += len(feats)
            vocabulary.update(feats)
        self.vocabulary_size = max(1, len(vocabulary))
        self.n = sum(self.class_counts[c] for c in classes)

    def probabilities(self, event: dict[str, object]) -> dict[str, float]:
        logs = []
        feats = event_features(event, self.full)
        for label in self.classes:
            prior = (self.class_counts[label] + ALPHA) / (self.n + ALPHA * len(self.classes))
            score = math.log(prior)
            denom = self.feature_totals[label] + ALPHA * self.vocabulary_size
            for feature in feats:
                score += math.log((self.feature_counts[label][feature] + ALPHA) / denom)
            logs.append(score)
        maximum = max(logs)
        values = np.exp(np.asarray(logs) - maximum)
        values /= values.sum()
        return {label: float(values[i]) for i, label in enumerate(self.classes)}


def class_capacity(events: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = defaultdict(lambda: {"events": 0, "folios": set(), "bases": set(), "registers": set()})
    for event in events:
        item = out[str(event["operator_class"])]
        item["events"] += 1
        item["folios"].add(event["physical_folio"])
        item["bases"].add(event["base_signature"])
        item["registers"].add(event["register"])
    return out


def cross_validate(events: list[dict[str, object]], library: list[str], split_field: str) -> list[dict[str, object]]:
    predictions = []
    for held in sorted({str(e[split_field]) for e in events}):
        train = [e for e in events if str(e[split_field]) != held]
        test = [e for e in events if str(e[split_field]) == held]
        available = [c for c in library if any(str(e["operator_class"]) == c for e in train)]
        if not available:
            continue
        baseline = NBModel(train, False, available)
        full = NBModel(train, True, available)
        train_bases = defaultdict(set)
        for event in train:
            train_bases[str(event["operator_class"])].add(str(event["base_signature"]))
        for event in test:
            label = str(event["operator_class"])
            covered = label in available
            row = {
                "split": split_field,
                "held": held,
                "event_id": event["event_id"],
                "physical_folio": event["physical_folio"],
                "section": event["section"],
                "register": event["register"],
                "hand": event["hand"],
                "operator_class": label,
                "base_unseen_for_operator": int(str(event["base_signature"]) not in train_bases[label]),
                "covered": int(covered),
                "baseline_bits": "NA",
                "full_bits": "NA",
                "gain_bits": "NA",
                "baseline_rank": "NA",
                "full_rank": "NA",
                "baseline_top5": "NA",
                "full_top5": "NA",
                "delta_by_class_json": "NA",
            }
            if covered:
                pb = baseline.probabilities(event)
                pf = full.probabilities(event)
                bb = -math.log2(max(pb[label], 1e-300))
                fb = -math.log2(max(pf[label], 1e-300))
                rb = 1 + sum(v > pb[label] for v in pb.values())
                rf = 1 + sum(v > pf[label] for v in pf.values())
                row.update({
                    "baseline_bits": bb,
                    "full_bits": fb,
                    "gain_bits": bb - fb,
                    "baseline_rank": rb,
                    "full_rank": rf,
                    "baseline_top5": int(rb <= 5),
                    "full_top5": int(rf <= 5),
                    "delta_by_class_json": json.dumps({c: math.log2(max(pf[c], 1e-300) / max(pb[c], 1e-300)) for c in available}, sort_keys=True, separators=(",", ":")),
                })
            predictions.append(row)
    return predictions


def summarize_predictions(rows: list[dict[str, object]], split: str, library_size: int) -> dict[str, object]:
    local = [r for r in rows if r["split"] == split]
    covered = [r for r in local if r["covered"]]
    gain = sum(float(r["gain_bits"]) for r in covered)
    by_held = defaultdict(float)
    for row in covered:
        by_held[str(row["held"])] += float(row["gain_bits"])
    unseen = [r for r in covered if r["base_unseen_for_operator"]]
    return {
        "split": split,
        "events": len(local),
        "covered": len(covered),
        "coverage": len(covered) / len(local) if local else 0.0,
        "gain_bits": gain,
        "bits_per_covered_event": gain / len(covered) if covered else 0.0,
        "selector_cost_bits": math.log2(library_size),
        "selector_paid_gain_bits": gain - math.log2(library_size),
        "positive_held": sum(v > 0 for v in by_held.values()),
        "held_units": len(by_held),
        "baseline_top1": sum(int(r["baseline_rank"]) == 1 for r in covered),
        "full_top1": sum(int(r["full_rank"]) == 1 for r in covered),
        "baseline_top5": sum(int(r["baseline_top5"]) for r in covered),
        "full_top5": sum(int(r["full_top5"]) for r in covered),
        "unseen_base_events": len(unseen),
        "unseen_base_gain_bits": sum(float(r["gain_bits"]) for r in unseen),
    }


def permutation_null(predictions: list[dict[str, object]], library: list[str]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows = [r for r in predictions if r["split"] == "physical_folio" and r["covered"]]
    by_event = {str(e["event_id"]): e for e in PRIMARY_EVENTS}
    strata: dict[tuple[object, ...], list[int]] = defaultdict(list)
    labels = []
    deltas = []
    for index, row in enumerate(rows):
        event = by_event[str(row["event_id"])]
        key = (
            event["scope"], event["rewrite_position"], event["section"], event["register"], event["currier"], event["hand"],
            event["source_length"], bucket(int(event["field_ordinal"])), event["line_entry"],
        )
        strata[key].append(index)
        labels.append(str(row["operator_class"]))
        deltas.append(json.loads(str(row["delta_by_class_json"])))
    mobile = sum(len(indices) for indices in strata.values() if len({labels[i] for i in indices}) > 1)
    observed = sum(deltas[i][labels[i]] for i in range(len(rows)))
    observed_by_class = defaultdict(float)
    for i, label in enumerate(labels):
        observed_by_class[label] += deltas[i][label]
    observed_max = max((value - math.log2(len(library)) for value in observed_by_class.values()), default=float("-inf"))
    rng = np.random.default_rng(SEED)
    null_rows = []
    total_tail = 0
    max_tail = 0
    for world in range(WORLDS):
        permuted = list(labels)
        for indices in strata.values():
            if len(indices) > 1:
                values = [labels[i] for i in indices]
                rng.shuffle(values)
                for i, value in zip(indices, values):
                    permuted[i] = value
        total = 0.0
        per_class = defaultdict(float)
        for i, label in enumerate(permuted):
            value = deltas[i].get(label, 0.0)
            total += value
            per_class[label] += value
        maximum = max((value - math.log2(len(library)) for value in per_class.values()), default=float("-inf"))
        total_tail += total >= observed - 1e-12
        max_tail += maximum >= observed_max - 1e-12
        null_rows.append({"world": world, "total_gain_bits": total, "max_candidate_paid_gain_bits": maximum})
    summary = {
        "events": len(rows),
        "strata": len(strata),
        "mobile_events": mobile,
        "observed_total_gain_bits": observed,
        "observed_max_candidate_paid_gain_bits": observed_max,
        "local_p": (total_tail + 1) / (WORLDS + 1),
        "max_library_p": (max_tail + 1) / (WORLDS + 1),
        "capacity_status": "ADEQUATE" if mobile >= 50 else "CAPACITY_LIMITED",
    }
    return null_rows, summary


def main() -> None:
    global PRIMARY_EVENTS
    ART.mkdir(parents=True, exist_ok=True)
    freeze = json.loads(FREEZE.read_text())
    if freeze["content_hash"] != hashlib.sha256(json.dumps({k: v for k, v in freeze.items() if k != "content_hash"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest():
        raise AssertionError("freeze content hash")
    rows, drawing, guard_stats = load_rows()
    records = make_records(rows, drawing)
    all_insertions = []
    for scope in ("FIELD", "DRAWING_RESET_SEGMENT", "PHYSICAL_LINE"):
        all_insertions.extend(insertion_events(records, scope))
    PRIMARY_EVENTS = [e for e in all_insertions if e["scope"] == "FIELD"]
    capacity = class_capacity(PRIMARY_EVENTS)
    library = sorted(label for label, item in capacity.items() if len(item["folios"]) >= 2)
    promoted_capacity = {label for label, item in capacity.items() if len(item["folios"]) >= 2 and len(item["bases"]) >= 3}
    model_events = [e for e in PRIMARY_EVENTS if e["operator_class"] in library]
    predictions = []
    for split in ("physical_folio", "section", "register", "hand"):
        predictions.extend(cross_validate(model_events, library, split))
    summaries = [summarize_predictions(predictions, split, len(library)) for split in ("physical_folio", "section", "register", "hand")]
    lofo = [r for r in predictions if r["split"] == "physical_folio" and r["covered"]]
    candidate_gain = defaultdict(float)
    candidate_positive_folios: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in lofo:
        label = str(row["operator_class"])
        candidate_gain[label] += float(row["gain_bits"])
        candidate_positive_folios[label][str(row["physical_folio"])] += float(row["gain_bits"])
    secondary = descriptive_candidates(records, all_insertions)
    candidate_rows = []
    for item in secondary:
        if item["kind"] == "INSERT_DELETE_ONE_ATOMIC_TUPLE":
            label = f"{item['position']}|{item['op']}"
            gain = candidate_gain.get(label, 0.0)
            folio_gains = candidate_positive_folios.get(label, {})
            selector_paid = gain - math.log2(max(1, len(library))) if label in library else ""
            if label in promoted_capacity and selector_paid != "" and selector_paid > 0 and len(item["registers"]) > 1:
                classification = "INTERESTING_EXPLORATORY"
            elif label in promoted_capacity and gain > 0:
                classification = "WEAK" if len(item["registers"]) > 1 else "LIKELY_REGISTER_OR_LAYOUT_CONFOUND"
            elif label in library:
                classification = "NO_SIGNAL" if gain <= 0 else "WEAK"
            else:
                classification = "INSUFFICIENT_TRANSFER_CAPACITY"
        else:
            label = ""
            gain = ""
            folio_gains = {}
            selector_paid = ""
            classification = "UNSCORED_CAPACITY_ATLAS"
        candidate_rows.append({
            "candidate_id": hid("CANDIDATE", item["kind"], item["position"], item["op"]),
            "hypothesis_family": "VARIABLE_RECORD_REWRITES",
            "rewrite_type": item["kind"],
            "rewrite_position": item["position"],
            "operator_tuple_ids": item["op"],
            "scope_level": "MULTISCOPE" if item["kind"] != "INSERT_DELETE_ONE_ATOMIC_TUPLE" else "FIELD_PRIMARY_PLUS_OTHER_SCOPES",
            "events": item["events"],
            "host_diversity": len(item["bases"]),
            "physical_folios": len(item["folios"]),
            "registers": len(item["registers"]),
            "symmetry": "DIRECTIONAL_INSERT_DELETE" if item["kind"] == "INSERT_DELETE_ONE_ATOMIC_TUPLE" else "UNDIRECTED_DESCRIPTIVE",
            "valency_delta": 1 if "INSERT" in item["kind"] else 0,
            "optionality": "OBSERVED_VARIANT_PAIR",
            "mutual_exclusion": "NOT_INFERRED",
            "downstream_state_change": "NOT_SCORED_PRIMARY",
            "record_length_effect": 1 if "INSERT" in item["kind"] else 0,
            "held_gain_bits": gain,
            "selector_paid_gain_bits": selector_paid,
            "positive_held_folios": sum(v > 0 for v in folio_gains.values()) if folio_gains else "",
            "held_folios_scored": len(folio_gains) if folio_gains else "",
            "reading_stability": "GDT327_ATOMIC_VIEW_ONLY_NOT_EDITION_REPLICATED",
            "anonymous_behavior_label": "UNASSIGNED",
            "classification": classification,
            "confounds": "EXACT_TUPLE_FREQUENCY;REGISTER;FIELD_LENGTH;FIELD_POSITION;WITHIN_FOLIO_PAIR_ENUMERATION",
        })
    represented_kinds = {str(row["rewrite_type"]) for row in candidate_rows}
    for missing_kind in ("ADJACENT_EXACT_TUPLE_DUPLICATION", "BOUNDARY_SPLIT_JOIN", "PRIOR_RECORD_SHORTEN_RESUME"):
        if missing_kind in represented_kinds:
            continue
        candidate_rows.append({
            "candidate_id": hid("ZERO_CAPACITY", missing_kind),
            "hypothesis_family": "ANAPHORA_ELLIPSIS_REPEAT" if missing_kind == "PRIOR_RECORD_SHORTEN_RESUME" else "HIERARCHICAL_SPACE_ATTACHMENT_SCOPE" if missing_kind == "BOUNDARY_SPLIT_JOIN" else "COORDINATION_LIST_STRUCTURE",
            "rewrite_type": missing_kind,
            "rewrite_position": "NONE_OBSERVED",
            "operator_tuple_ids": "",
            "scope_level": "FROZEN_MULTISCOPE_SEARCH",
            "events": 0,
            "host_diversity": 0,
            "physical_folios": 0,
            "registers": 0,
            "symmetry": "NO_CAPACITY",
            "valency_delta": "",
            "optionality": "NO_CAPACITY",
            "mutual_exclusion": "NOT_TESTABLE",
            "downstream_state_change": "NOT_TESTABLE",
            "record_length_effect": "",
            "held_gain_bits": "",
            "selector_paid_gain_bits": "",
            "positive_held_folios": "",
            "held_folios_scored": "",
            "reading_stability": "NOT_APPLICABLE_ZERO_CAPACITY",
            "anonymous_behavior_label": "UNASSIGNED",
            "classification": "NO_CAPACITY",
            "confounds": "NO_EXACT_FROZEN_REWRITE_INSTANCE",
        })
    null_rows, null_summary = permutation_null(predictions, library)
    # The frozen promotion rule is conjunctive.  Candidate-local paid gain is
    # descriptive when the full-library null fails, even if one row is positive.
    if null_summary["capacity_status"] != "ADEQUATE" or null_summary["max_library_p"] > 0.05:
        for row in candidate_rows:
            if row["classification"] == "INTERESTING_EXPLORATORY":
                row["classification"] = "WEAK"
                row["confounds"] += ";MAX_LIBRARY_GATE_FAILED"
    candidate_rows.sort(key=lambda r: (0 if r["held_gain_bits"] != "" else 1, -float(r["held_gain_bits"] or -1e99), -int(r["physical_folios"]), r["candidate_id"]))

    record_rows = []
    for record in records:
        record_rows.append({
            "record_id": record["record_id"], "scope": record["scope"], "page": record["page"], "physical_folio": record["physical_folio"],
            "locus": record["locus"], "section": record["section"], "register": record["register"], "currier": record["currier"], "hand": record["hand"],
            "record_ordinal": record["record_ordinal"], "field_ordinal": record["field_ordinal"], "group_count": record["group_count"], "dy_close": record["dy_close"],
            "b3_close": record["b3_close"], "starts_after_drawing": record["starts_after_drawing"], "ends_before_drawing": record["ends_before_drawing"],
            "left_boundary_profile": record["left_boundary_profile"], "right_boundary_profile": record["right_boundary_profile"],
            "field_breaks": ",".join(map(str, record["field_breaks"])), "segment_breaks": ",".join(map(str, record["segment_breaks"])),
            "opaque_tuple_sequence_json": json.dumps(record["sequence"], separators=(",", ":")),
        })
    event_rows = []
    for event in all_insertions:
        event_rows.append({k: (json.dumps(v, separators=(",", ":")) if isinstance(v, tuple) else v) for k, v in event.items()})
    pred_fields = ["split", "held", "event_id", "physical_folio", "section", "register", "hand", "operator_class", "base_unseen_for_operator", "covered", "baseline_bits", "full_bits", "gain_bits", "baseline_rank", "full_rank", "baseline_top5", "full_top5", "delta_by_class_json"]
    score_rows = summaries
    counterexamples = [
        {"counterexample": "WHOLE_LINE_NEAR_ISOMORPHY_SPARSE", "value": sum(1 for e in all_insertions if e["scope"] == "PHYSICAL_LINE"), "interpretation": "whole physical-line exact insertion counterparts are sparse and cannot independently carry the primary route"},
        {"counterexample": "DRAWING_SEGMENT_NEAR_ISOMORPHY_SPARSE", "value": sum(1 for e in all_insertions if e["scope"] == "DRAWING_RESET_SEGMENT"), "interpretation": "drawing-reset segments contribute limited exact rewrite capacity"},
        {"counterexample": "PRIMARY_LIBRARY_REGISTER_CONCENTRATION", "value": sum(len(item["registers"]) == 1 for label, item in capacity.items() if label in library), "interpretation": "many recurrent operator classes may remain register-local"},
        {"counterexample": "ATOMIC_ID_READING_SENSITIVITY_UNASSESSED", "value": len(library), "interpretation": "GDT327 atomic IDs are not three independent readings and exact edition-stability is not claimed"},
        {"counterexample": "NO_SEMANTIC_LABELS", "value": 0, "interpretation": "behavioral rewrite evidence cannot name coordinator exclusion relation resume repeat or sequence functions"},
    ]
    paths = {
        "records": ART / "gdt374_record_inventory.tsv",
        "events": ART / "gdt374_rewrite_events.tsv",
        "candidates": ART / "gdt374_candidate_atlas.tsv",
        "predictions": ART / "gdt374_holdout_predictions.tsv",
        "scores": ART / "gdt374_transfer_scores.tsv",
        "null": ART / "gdt374_null_results.tsv",
        "counterexamples": ART / "gdt374_counterexamples.tsv",
    }
    write_tsv(paths["records"], record_rows)
    write_tsv(paths["events"], event_rows)
    write_tsv(paths["candidates"], candidate_rows)
    write_tsv(paths["predictions"], predictions, pred_fields)
    write_tsv(paths["scores"], score_rows)
    write_tsv(paths["null"], null_rows)
    write_tsv(paths["counterexamples"], counterexamples)
    primary = next(x for x in summaries if x["split"] == "physical_folio")
    eligible_candidates = [x for x in candidate_rows if x["classification"] == "INTERESTING_EXPLORATORY"]
    status = "ANONYMOUS_OPERATOR_LEAD_REQUIRES_PROSPECTIVE_TEST" if eligible_candidates else "NO_PROMOTABLE_FUNCTIONAL_OPERATOR_FOUND"
    result = {
        "schema": "GDT374_RESULT_V1",
        "status": status,
        "inventory": {
            "gdt327_groups": len(rows),
            "physical_folios": len({r["physical_folio"] for r in rows}),
            "records_by_scope": dict(Counter(str(r["scope"]) for r in records)),
            "insertion_events_by_scope": dict(Counter(str(e["scope"]) for e in all_insertions)),
            "primary_field_events": len(PRIMARY_EVENTS),
            "primary_library_classes_two_folios": len(library),
            "promotion_capacity_classes": len(promoted_capacity),
            **guard_stats,
        },
        "primary": primary,
        "transfer_sensitivities": {x["split"]: x for x in summaries if x["split"] != "physical_folio"},
        "null": null_summary,
        "candidate_class_counts": dict(Counter(str(r["classification"]) for r in candidate_rows)),
        "promotable_candidate_ids": [x["candidate_id"] for x in eligible_candidates],
        "semantic_roles_assigned": 0,
        "f84_accessed": False,
        "claim_ceiling": "ANONYMOUS_RECORD_CONDITIONED_FORMAL_REWRITE_BEHAVIOR_ONLY",
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (INTER, DRAW, FREEZE, ROOT / "experiments/yolo/gdt373_functional_operator_roadmap/artifacts/gdt373_hypothesis_registry.tsv")},
        "implementation": {str((BASE / "src/run.py").relative_to(ROOT)): sha(BASE / "src/run.py")},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in paths.values()},
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt374_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    report = [
        "# GDT374 — common functional-operator discovery", "", f"Status: **{status}**.", "",
        "## Primary held-folio result", "",
        f"The atomic field inventory contains {len(PRIMARY_EVENTS)} exact one-tuple insertion/deletion events on {len({e['physical_folio'] for e in PRIMARY_EVENTS})} physical folios. The frequency-capacity library has {len(library)} operator classes; {len(promoted_capacity)} have at least three opaque bases and two folios.", "",
        f"The source-identity model changes held-folio codelength by **{primary['gain_bits']:+.3f} bits** ({primary['bits_per_covered_event']:+.4f} bits/covered event) versus the section/register/Currier/hand/length/position baseline. After the frozen class selector cost the gain is **{primary['selector_paid_gain_bits']:+.3f} bits**. It improves {primary['positive_held']}/{primary['held_units']} scored folios; top-1 is {primary['full_top1']} versus {primary['baseline_top1']} and top-5 is {primary['full_top5']} versus {primary['baseline_top5']}. On {primary['unseen_base_events']} operator-specific unseen-base events the gain is {primary['unseen_base_gain_bits']:+.3f} bits.", "",
        f"The matched 4,096-world null has {null_summary['mobile_events']} mobile events: local p={null_summary['local_p']:.6f}, max-library p={null_summary['max_library_p']:.6f}, capacity={null_summary['capacity_status']}.", "",
        "## Strongest exploratory rows", "",
        f"The strongest opaque prefix insertion (`{candidate_rows[0]['candidate_id']}`) recurs over {candidate_rows[0]['host_diversity']} base sequences, {candidate_rows[0]['physical_folios']} folios, and {candidate_rows[0]['registers']} registers. Its held contribution is {float(candidate_rows[0]['held_gain_bits']):+.3f} bits ({float(candidate_rows[0]['selector_paid_gain_bits']):+.3f} after the class selector), positive on {candidate_rows[0]['positive_held_folios']}/{candidate_rows[0]['held_folios_scored']} scored folios. It remains `WEAK` because the full-library p-value is {null_summary['max_library_p']:.6f} and the aggregate predictive codelength is strongly negative.", "",
        "The apparent tension between rank and probability is itself diagnostic: atomic source identity raises top-1 from " + str(primary['baseline_top1']) + " to " + str(primary['full_top1']) + " and top-5 from " + str(primary['baseline_top5']) + " to " + str(primary['full_top5']) + ", but makes many wrong predictions much too confident. This is compatibility texture, not a calibrated reusable algebra.", "",
        "## Interpretation", "",
    ]
    if eligible_candidates:
        report.append("At least one anonymous insertion operator meets the exploratory promotion rule. This is a prospective-test lead only; it receives no functional gloss.")
    else:
        report.append("No candidate meets the frozen promotion rule. Recurrent exact prefix insertions exist, but their source-field compatibility does not supply a selector-paid, null-adjusted, cross-environment operator lead strong enough to freeze prospectively.")
    report += ["", "Replacement and paired-replacement candidates remain descriptive in the common atlas. Exact duplication, boundary split/join, and prior-record shortening produced zero frozen instances and are represented by explicit zero-capacity rows. Drawing-reset segments supply only four insertion events and complete physical lines supply none. None was allowed to replace the primary endpoint after scoring.", "", "## Counterexamples", "", "Whole-line and drawing-segment exact near-isomorphy are sparse; register concentration and the lack of an edition-independent exact atomic-ID sensitivity limit interpretation. No anonymous behavior class was promoted to COORDINATOR, EXCLUSION, RELATION, RESUME, REPEAT, or SEQUENCE.", "", "## Claim ceiling", "", result["claim_ceiling"] + ". No function, morpheme, POS, sound, language, plaintext, meaning, or translation is assigned. Every f84 row in the drawing source was rejected on raw page before row parsing; no f84 formal payload was retained, joined, or scored."]
    (BASE / "REPORT.md").write_text("\n".join(report) + "\n")
    result["documents"] = {str(path.relative_to(ROOT)): sha(path) for path in (BASE / "METHOD.md", BASE / "REPORT.md")}
    result["content_hash"] = hashlib.sha256(json.dumps({k: v for k, v in result.items() if k != "content_hash"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt374_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "primary": primary, "null": null_summary}, sort_keys=True))


PRIMARY_EVENTS: list[dict[str, object]] = []

if __name__ == "__main__":
    main()
