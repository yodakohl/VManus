#!/usr/bin/env python3
"""GDT109: transfer HPR2 representations to unused legacy plant annotations."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/semantic_assumptions/results"
LABELS = RESULTS / "existing_human_label_annotations.tsv"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
ANN = ROOT / "gdt012_annotated_core_inventory.tsv"
PARSED = ROOT / "gdt059_hpr2_external_inventory.tsv"
PROSE = ROOT / "gdt016_group_state_inventory.tsv"
MANIFEST = ROOT / "gdt095_descriptor_token_manifest.tsv"
METHOD = ROOT / "GDT109_LEGACY_OUT_OF_PANEL_DESCRIPTOR_TRANSFER_METHOD.md"
REPORT = ROOT / "GDT109_LEGACY_OUT_OF_PANEL_DESCRIPTOR_TRANSFER_REPORT.md"
TARGETS = ROOT / "gdt109_target_inventory.tsv"
SCORES = ROOT / "gdt109_representation_scores.tsv"
TOKENS = ROOT / "gdt109_token_scores.tsv"
NULL = ROOT / "gdt109_null_results.tsv"
VARIANTS = ROOT / "gdt109_variant_log.tsv"
RESULT = ROOT / "gdt109_result.json"

PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
RIGHT = ("aiin", "air", "ain", "ar", "al")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
MODES = ("AVERAGED",) + EDITIONS
REPS = (
    "RAW_CHAR3", "RESIDUAL_HOST_CHAR3", "PAGE_HOST_CHAR3",
    "EDGE_STRIPPED_CHAR3", "EDGE_ONLY", "COMPILER_ACTIVE",
    "PAGE_HOST_PLUS_COMPILER_ACTIVE", "STA_FAMILY_CHAR3",
)
K = 5
SHRINK = 4.0
WORLDS = 10000
SEED = 109001
STOP = set("a an and are as at be been being but by for from has have in into is it its label labels labeled near next no not of on or page panel plant plants row since that the their them there these they this to under used was we were with word words kluge kluges petersen petersens grove groves latham perhaps seems likely associated actually between east west north south left right above below top bottom middle mid height side first second third fourth fifth sixth one two three four five six seven eight nine ten".split())


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    return match.group(1) if match else page


def descriptor_tokens(text: str) -> set[str]:
    text = text.split("||", 1)[-1].lower()
    text = re.sub(r"<[^>]*>|&[^;]*;|\bf\d+[rv]\w*\b", " ", text)
    output = []
    for word in re.findall(r"[a-z]+", text):
        if word in STOP or len(word) < 3:
            continue
        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"
        elif word.endswith("ves") and len(word) > 4:
            word = word[:-3] + "f"
        elif word.endswith("s") and len(word) > 4:
            word = word[:-1]
        if word not in STOP:
            output.append(word)
    return set(output)


def strip_layers(token: str) -> tuple[str, str, int]:
    wrapper = "NONE"; host = token
    for prefix in PREFIXES:
        if host.startswith(prefix) and len(host) > len(prefix):
            wrapper = prefix; host = host[len(prefix):]; break
    dy = int(host.endswith("dy") and len(host) > 2)
    if dy:
        host = host[:-2]
    return wrapper, host, dy


def preparse(wrapper: str, residual: str) -> tuple[str, int, str, int]:
    host = residual
    b3 = int(host.endswith("m") and len(host) > 1)
    if b3:
        host = host[:-1]
    right = "NONE"
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host = host[:-len(suffix)]; right = suffix; break
    inner = int(wrapper in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1)
    if inner:
        host = host[1:]
    return host, b3, right, inner


def licensed_hosts() -> set[str]:
    counts = Counter()
    for row in read(PROSE):
        host, _, _, _ = preparse(row["stripped_prefix"], row["residual_host"])
        counts[host] += 1
    return {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}


def parse_token(token: str, licensed: set[str]) -> dict[str, object]:
    wrapper, residual, dy = strip_layers(token)
    host, b3, right, inner = preparse(wrapper, residual)
    frame = "NONE"
    if host.startswith("ot") and host[2:] in licensed:
        host = host[2:]; frame = "OT"
    elif host.startswith("o") and host[1:] in licensed:
        host = host[1:]; frame = "O"
    return {"token": token, "residual": residual, "wrapper": wrapper, "dy": dy,
            "page_host": host or "EMPTY", "b3": b3, "right": right,
            "inner": inner, "frame": frame}


def add_char3(counter: Counter[str], value: str, prefix: str = "") -> None:
    padded = "^" + value + "$"
    for i in range(max(1, len(padded) - 2)):
        counter[prefix + padded[i:i + 3]] += 1.0


def feature_bundle(tokens: list[str], families: list[str], licensed: set[str]) -> dict[str, Counter[str]]:
    parsed = [parse_token(token, licensed) for token in tokens]
    output = {rep: Counter() for rep in REPS}
    for item in parsed:
        add_char3(output["RAW_CHAR3"], str(item["token"]))
        add_char3(output["RESIDUAL_HOST_CHAR3"], str(item["residual"]))
        add_char3(output["PAGE_HOST_CHAR3"], str(item["page_host"]))
        core = str(item["page_host"])[:-1] if len(str(item["page_host"])) > 1 else "EMPTY"
        add_char3(output["EDGE_STRIPPED_CHAR3"], core)
        output["EDGE_ONLY"]["EDGE=" + str(item["page_host"])[-1:]] += 1.0
        active = []
        if item["wrapper"] != "NONE": active.append("W=" + str(item["wrapper"]))
        if item["inner"]: active.append("D=1")
        if item["frame"] != "NONE": active.append("F=" + str(item["frame"]))
        if item["right"] != "NONE": active.append("R=" + str(item["right"]))
        if item["dy"]: active.append("DY=1")
        if item["b3"]: active.append("B3=1")
        output["COMPILER_ACTIVE"].update(active)
    output["PAGE_HOST_PLUS_COMPILER_ACTIVE"].update(output["PAGE_HOST_CHAR3"])
    output["PAGE_HOST_PLUS_COMPILER_ACTIVE"].update(output["COMPILER_ACTIVE"])
    for family in families:
        add_char3(output["STA_FAMILY_CHAR3"], family, "F:")
    return output


def average_bundles(bundles: list[dict[str, Counter[str]]]) -> dict[str, Counter[str]]:
    output = {rep: Counter() for rep in REPS}
    for bundle in bundles:
        for rep in REPS:
            for key, value in bundle[rep].items():
                output[rep][key] += value / len(bundles)
    return output


def distance(a: Counter[str], b: Counter[str]) -> float:
    keys = set(a) | set(b)
    denominator = sum(max(a[key], b[key]) for key in keys)
    if not denominator:
        return 1.0
    return 1.0 - sum(min(a[key], b[key]) for key in keys) / denominator


def main() -> None:
    annotations = {row["source_record_id"]: row for row in read(LABELS)}
    used_loci = {row["locus"] for row in read(ANN)}
    targets = []
    for row in read(CROSSWALK):
        source = annotations.get(row["source_record_id"])
        if not source or row["primary_eligible"] != "1" or row["current_locus"] in used_loci:
            continue
        if row["current_locus"].startswith("f84r"):
            continue
        if source["certainty"] == "UNHEDGED" and source["object_class"] == "P":
            targets.append({"source_record_id": row["source_record_id"], "locus": row["current_locus"],
                            "page": row["current_page"], "physical_folio": physical_folio(row["current_page"]),
                            "description": source["comments"], "descriptor_tokens": descriptor_tokens(source["comments"])})
    targets.sort(key=lambda row: row["locus"])
    assert len(targets) == len({row["locus"] for row in targets}) == 44
    assert len({row["physical_folio"] for row in targets}) == 6
    assert not any(row["locus"].startswith("f84r") for row in targets)
    wanted = {row["locus"] for row in targets}

    alignment: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    # Retain only the fixed non-holdout target whitelist before parsing formal fields.
    with ALIGN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            locus = row["locus"]
            if locus.startswith("f84r") or locus not in wanted:
                continue
            alignment[locus][row["edition"]].append(row)
    assert set(alignment) == wanted
    assert all(set(alignment[locus]) == set(EDITIONS) for locus in wanted)
    licensed = licensed_hosts()

    target_rows = []
    for target in targets:
        locus = target["locus"]
        edition_bundles = {}
        edition_forms = {}
        for edition in EDITIONS:
            rows = sorted(alignment[locus][edition], key=lambda row: int(row["source_group_index"]))
            tokens = [row["nearest_basic_eva_primary"] for row in rows]
            families = [row["primary_sta_families"] for row in rows]
            edition_forms[edition] = "|".join(tokens)
            edition_bundles[edition] = feature_bundle(tokens, families, licensed)
        target["features"] = {edition: edition_bundles[edition] for edition in EDITIONS}
        target["features"]["AVERAGED"] = average_bundles(list(edition_bundles.values()))
        exact_surface = len(set(edition_forms.values())) == 1
        family_sequences = {edition: "|".join(row["primary_sta_families"] for row in sorted(alignment[locus][edition], key=lambda row: int(row["source_group_index"]))) for edition in EDITIONS}
        exact_family = len(set(family_sequences.values())) == 1
        target_rows.append({"source_record_id": target["source_record_id"], "locus": locus,
                            "page": target["page"], "physical_folio": target["physical_folio"],
                            "descriptor_tokens": ";".join(sorted(target["descriptor_tokens"])) or "NONE",
                            "zl3b_forms": edition_forms["ZL3b"], "it2a_forms": edition_forms["IT2a"],
                            "rf1b_forms": edition_forms["RF1b"], "all_reading_surface_agreement": int(exact_surface),
                            "all_reading_family_agreement": int(exact_family),
                            "formal_use": "THREE_READING_AVERAGE_PRIMARY;EDITION_SENSITIVITIES_RETAINED",
                            "semantic_role": "UNASSIGNED", "provenance": "EXISTING_HUMAN_ANNOTATION_ARCHIVE"})
    write(TARGETS, target_rows)

    ann_rows = read(ANN); parsed_rows = read(PARSED)
    assert len(ann_rows) == len(parsed_rows) == 671
    grouped: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for annotation, parsed in zip(ann_rows, parsed_rows):
        assert annotation["locus"] == parsed["locus"] and annotation["group_index"] == parsed["group_index"]
        if annotation["kind"] == "L" and annotation["annotation_certainty"] == "UNHEDGED" and annotation["section"] == "P" and "PLANT" in annotation["object_tags"].split(";"):
            grouped[annotation["locus"]].append((annotation, parsed))
    training = []
    for locus, pairs in sorted(grouped.items()):
        pairs.sort(key=lambda pair: int(pair[0]["group_index"]))
        first = pairs[0][0]
        tokens = descriptor_tokens(first["raw_source_description"])
        features = {rep: Counter() for rep in REPS}
        for annotation, parsed in pairs:
            add_char3(features["RAW_CHAR3"], annotation["token"])
            add_char3(features["RESIDUAL_HOST_CHAR3"], annotation["residual_host"])
            add_char3(features["PAGE_HOST_CHAR3"], parsed["page_host"])
            core = parsed["page_host"][:-1] if len(parsed["page_host"]) > 1 else "EMPTY"
            add_char3(features["EDGE_STRIPPED_CHAR3"], core)
            features["EDGE_ONLY"]["EDGE=" + parsed["page_host"][-1:]] += 1
            active = []
            if parsed["wrapper"] != "NONE": active.append("W=" + parsed["wrapper"])
            if parsed["inner_d"] == "1": active.append("D=1")
            if parsed["local_frame"] != "NONE": active.append("F=" + parsed["local_frame"])
            if parsed["right_family"] != "NONE": active.append("R=" + parsed["right_family"])
            if annotation["dy_closure"] == "1": active.append("DY=1")
            if parsed["b3"] == "1": active.append("B3=1")
            features["COMPILER_ACTIVE"].update(active)
            add_char3(features["STA_FAMILY_CHAR3"], annotation["family_surface"], "F:")
        features["PAGE_HOST_PLUS_COMPILER_ACTIVE"].update(features["PAGE_HOST_CHAR3"])
        features["PAGE_HOST_PLUS_COMPILER_ACTIVE"].update(features["COMPILER_ACTIVE"])
        training.append({"locus": locus, "folio": first["physical_folio"], "tokens": tokens, "features": features})
    assert len(training) == 83 and len({row["folio"] for row in training}) == 5

    vocab = [row["descriptor_token"] for row in read(MANIFEST)]
    assert len(vocab) == 19
    y = np.array([[int(token in target["descriptor_tokens"]) for token in vocab] for target in targets], dtype=float)
    token_counts = y.sum(axis=0).astype(int)
    capacity_indexes = [index for index, count in enumerate(token_counts) if 3 <= count <= len(targets) - 3]
    panels = {"ALL_GDT095_TOKENS": list(range(len(vocab))), "TARGET_CAPACITY_GE3": capacity_indexes}
    target_folios = sorted({target["physical_folio"] for target in targets})
    folio_indexes = {folio: np.array([index for index, target in enumerate(targets) if target["physical_folio"] == folio], dtype=int) for folio in target_folios}

    probabilities: dict[tuple[str, str], np.ndarray] = {}
    baselines = np.zeros((len(targets), len(vocab)))
    for index, target in enumerate(targets):
        train = [row for row in training if row["folio"] != target["physical_folio"]]
        for token_index, token in enumerate(vocab):
            baselines[index, token_index] = (sum(token in row["tokens"] for row in train) + .5) / (len(train) + 1)
        for mode in MODES:
            for rep in REPS:
                candidates = []
                for row in train:
                    d = distance(target["features"][mode][rep], row["features"][rep])
                    if d < 1 - 1e-12:
                        candidates.append((d, row["locus"], row))
                candidates.sort(key=lambda item: (item[0], item[1]))
                nearest = candidates[:K]
                weights = np.array([1 / (.1 + item[0]) for item in nearest])
                denominator = weights.sum() + SHRINK
                pred = SHRINK * baselines[index] / denominator
                for weight, (_, _, row) in zip(weights, nearest):
                    pred += weight * np.array([int(token in row["tokens"]) for token in vocab]) / denominator
                probabilities.setdefault((mode, rep), np.zeros_like(y))[index] = pred

    def losses(labels: np.ndarray, probability: np.ndarray) -> np.ndarray:
        probability = np.clip(probability, 1e-12, 1 - 1e-12)
        return -np.log2(np.where(labels > 0, probability, 1 - probability))

    baseline_losses = losses(y, baselines)
    score_rows = []
    token_rows = []
    for panel, indexes in panels.items():
        for mode in MODES:
            for rep in REPS:
                model_losses = losses(y, probabilities[mode, rep])
                gain = float((baseline_losses[:, indexes] - model_losses[:, indexes]).sum())
                folio_gains = [float((baseline_losses[np.ix_(rows, indexes)] - model_losses[np.ix_(rows, indexes)]).sum()) for rows in folio_indexes.values()]
                score_rows.append({"panel": panel, "reading_mode": mode, "representation": rep,
                                   "target_loci": len(targets), "descriptor_tokens": len(indexes),
                                   "positive_cells": int(y[:, indexes].sum()),
                                   "baseline_bits": float(baseline_losses[:, indexes].sum()),
                                   "held_bits": float(model_losses[:, indexes].sum()), "gain_bits": gain,
                                   "selector_paid_gain_bits": gain - math.log2(len(REPS)) if mode == "AVERAGED" else "NOT_PRIMARY",
                                   "positive_gain_folios": sum(value > 0 for value in folio_gains),
                                   "min_folio_gain": min(folio_gains), "max_folio_gain": max(folio_gains)})
                for token_index in indexes:
                    token_rows.append({"panel": panel, "reading_mode": mode, "representation": rep,
                                       "descriptor_token": vocab[token_index], "positive_loci": int(token_counts[token_index]),
                                       "gain_bits": float((baseline_losses[:, token_index] - model_losses[:, token_index]).sum()),
                                       "positive_gain_folios": sum(float((baseline_losses[rows, token_index] - model_losses[rows, token_index]).sum()) > 0 for rows in folio_indexes.values())})
    score_rows.sort(key=lambda row: (row["panel"], row["reading_mode"], -float(row["gain_bits"]), row["representation"]))
    token_rows.sort(key=lambda row: (row["panel"], row["reading_mode"], row["representation"], -float(row["gain_bits"]), row["descriptor_token"]))

    rng = np.random.default_rng(SEED)
    observed = {(panel, rep): next(float(row["gain_bits"]) for row in score_rows if row["panel"] == panel and row["reading_mode"] == "AVERAGED" and row["representation"] == rep) for panel in panels for rep in REPS}
    local_counts = Counter(); max_counts = Counter()
    for _ in range(WORLDS):
        permuted = y.copy()
        for rows in folio_indexes.values():
            permuted[rows] = permuted[rng.permutation(rows)]
        base = losses(permuted, baselines)
        for panel, indexes in panels.items():
            gains = {}
            for rep in REPS:
                model = losses(permuted, probabilities["AVERAGED", rep])
                gains[rep] = float((base[:, indexes] - model[:, indexes]).sum())
                local_counts[panel, rep] += gains[rep] >= observed[panel, rep] - 1e-12
            max_counts[panel] += max(gains.values()) >= max(observed[panel, rep] for rep in REPS) - 1e-12
    null_rows = []
    for panel in panels:
        for rep in REPS:
            null_rows.append({"panel": panel, "representation": rep, "worlds": WORLDS, "seed": SEED,
                              "observed_gain_bits": observed[panel, rep],
                              "local_inclusive_p": (local_counts[panel, rep] + 1) / (WORLDS + 1),
                              "max_representation_inclusive_p": (max_counts[panel] + 1) / (WORLDS + 1),
                              "preserves": "target_physical_folio;complete_19_token_vector;formal_predictions"})
    by_null = {(row["panel"], row["representation"]): row for row in null_rows}
    for row in score_rows:
        if row["reading_mode"] == "AVERAGED":
            nrow = by_null[row["panel"], row["representation"]]
            row["local_permutation_p"] = nrow["local_inclusive_p"]
            row["max_representation_p"] = nrow["max_representation_inclusive_p"]
        else:
            row["local_permutation_p"] = "SENSITIVITY_NOT_PERMUTED"
            row["max_representation_p"] = "SENSITIVITY_NOT_PERMUTED"
    write(SCORES, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in score_rows])
    write(TOKENS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in token_rows])
    write(NULL, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in null_rows])
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "All 19 frozen GDT095 endpoints; three-reading averaged formal features."},
        {"variant_id": "V01", "status": "RUN_SENSITIVITY", "description": "Target-capacity endpoints with at least three positive and three negative target loci."},
        {"variant_id": "V02", "status": "RUN_SENSITIVITY", "description": "ZL3b-only formal rendering."},
        {"variant_id": "V03", "status": "RUN_SENSITIVITY", "description": "IT2a-only formal rendering."},
        {"variant_id": "V04", "status": "RUN_SENSITIVITY", "description": "RF1b-only formal rendering."},
        {"variant_id": "V05", "status": "NOT_RUN", "description": "No target-token selection, semantic gloss, image reopening, f84r access, or new parser search."},
    ]
    write(VARIANTS, variants)

    primary = [row for row in score_rows if row["panel"] == "ALL_GDT095_TOKENS" and row["reading_mode"] == "AVERAGED"]
    primary.sort(key=lambda row: (-float(row["gain_bits"]), row["representation"]))
    capacity = [row for row in score_rows if row["panel"] == "TARGET_CAPACITY_GE3" and row["reading_mode"] == "AVERAGED"]
    capacity.sort(key=lambda row: (-float(row["gain_bits"]), row["representation"]))
    host = next(row for row in primary if row["representation"] == "PAGE_HOST_CHAR3")
    raw = next(row for row in primary if row["representation"] == "RAW_CHAR3")
    compiler = next(row for row in primary if row["representation"] == "COMPILER_ACTIVE")
    stripped = next(row for row in primary if row["representation"] == "EDGE_STRIPPED_CHAR3")
    best = primary[0]
    status = "LEGACY_OUT_OF_PANEL_HPR2_TRANSFER_NO_SELECTOR_PAID_WINNER"
    if float(best["selector_paid_gain_bits"]) > 0 and float(best["max_representation_p"]) <= .05:
        status = "LEGACY_OUT_OF_PANEL_HPR2_TRANSFER_PROVISIONAL"
    elif float(best["gain_bits"]) > 0:
        status = "LEGACY_OUT_OF_PANEL_HPR2_TRANSFER_WEAK"

    REPORT.write_text(f"""# GDT109 — legacy out-of-panel descriptor transfer

## Outcome

**{status}**

The fixed target contains {len(targets)} current loci on
{len(target_folios)} physical folios, all absent from the GDT012/GDT095 formal
annotation panel. It is not fresh visual evidence: the source descriptions are
legacy human annotations already archived in the repository. Nine loci have
identical display forms across all three readings and
{sum(int(row['all_reading_family_agreement']) for row in target_rows)} have an
identical STA-family sequence; primary formal features average all three
edition-specific readings rather than treating them as replications.

On all 19 frozen GDT095 descriptor endpoints, the best representation is
`{best['representation']}` at {float(best['gain_bits']):+.3f} held bits over the
folio-excluded prevalence code, {float(best['selector_paid_gain_bits']):+.3f}
after the eight-way representation selector, and max-over-representation
p={float(best['max_representation_p']):.4f}. PAGE_HOST scores
{float(host['gain_bits']):+.3f} bits, raw character trigrams
{float(raw['gain_bits']):+.3f}, edge-stripped PAGE_HOST
{float(stripped['gain_bits']):+.3f}, and compiler-only active state
{float(compiler['gain_bits']):+.3f}.

The target-capacity sensitivity retains {capacity[0]['descriptor_tokens']}
tokens. Its best representation is `{capacity[0]['representation']}` at
{float(capacity[0]['gain_bits']):+.3f} bits and
p(max)={float(capacity[0]['max_representation_p']):.4f}. The complete token,
representation, reading, and folio sensitivities are exported; no attractive
descriptor or form was selected away.

This is an archive-stratum transfer of a representation ordering, not a
prospective visual confirmation. A positive result can localize information in
an HPR2 layer; it cannot assign a host meaning. f84r was excluded before formal
retention and was not opened, parsed, retained, queried, joined, scored, or
targeted. No semantic class, role, gloss, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is assigned.
""", encoding="utf-8")

    result = {
        "schema": "GDT109_LEGACY_OUT_OF_PANEL_DESCRIPTOR_TRANSFER_RESULT_V1",
        "status": status, "target_loci": len(targets), "target_physical_folios": len(target_folios),
        "training_loci": len(training), "training_physical_folios": len({row["folio"] for row in training}),
        "descriptor_tokens": len(vocab), "target_capacity_tokens": len(capacity_indexes),
        "surface_agreement_loci": sum(int(row["all_reading_surface_agreement"]) for row in target_rows),
        "family_agreement_loci": sum(int(row["all_reading_family_agreement"]) for row in target_rows),
        "primary_best": best, "page_host": host, "raw": raw, "edge_stripped": stripped,
        "compiler_only": compiler, "capacity_best": capacity[0],
        "interpretation": "Out-of-panel archived annotation-stratum transfer only; formal uncertainty averaged across the three alternate readings.",
        "selection_disclosure": "All 44 fixed crosswalk rows, all 19 GDT095 tokens, all eight predeclared representations, and all four reading modes are retained.",
        "claim_ceiling": "No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "parsed": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
        "inputs": {path.name if path.parent == ROOT else str(path.relative_to(ROOT)): sha(path) for path in (LABELS, CROSSWALK, ALIGN, ANN, PARSED, PROSE, MANIFEST, ROOT / "gdt095_result.json", ROOT / "gdt108_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in (TARGETS, SCORES, TOKENS, NULL, VARIANTS)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "best": best, "capacity_best": capacity[0], "page_host_gain": host["gain_bits"], "raw_gain": raw["gain_bits"]}, sort_keys=True))


if __name__ == "__main__":
    main()
