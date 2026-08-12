#!/usr/bin/env python3
"""Run target-free LTG001 latent-channel synthetic calibration."""

from __future__ import annotations

import hashlib
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from ltg001_latent_channel_core import Panel, evaluate_panel, load_panel, panel_from_arrays


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CAPACITY = RESULTS / "ltg001_latent_channel_capacity.json"
OUT_JSON = RESULTS / "ltg001_latent_channel_calibration.json"
OUT_REPORT = RESULTS / "ltg001_latent_channel_calibration_report.md"
V1 = RESULTS / "ltg001_latent_channel_calibration_v1.json"
V2 = RESULTS / "ltg001_latent_channel_calibration_v2.json"
WORLD_FAMILIES = (
    ("NULL_DIRECT", 16),
    ("SHARED_CHANNEL", 16),
    ("ONE_FOLIO_CHANNEL", 8),
    ("FAMILY_PRIVATE_CHANNEL", 8),
    ("DOMINANT_POLICY_ONLY", 8),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rng_for(label: str) -> np.random.Generator:
    seed = int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:8], "big")
    return np.random.default_rng(seed)


def draw_categorical(rng: np.random.Generator, probabilities: np.ndarray) -> np.ndarray:
    cumulative = np.cumsum(probabilities, axis=-1)
    values = rng.random(probabilities.shape[0])
    return np.sum(values[:, None] > cumulative, axis=1).astype(np.int16)


def shared_observations(base: Panel, label: str, k: int, strength: float = 0.70) -> np.ndarray:
    rng = rng_for(label)
    f_count = len(base.family_names)
    s_count = len(base.symbol_names)
    family_pi = rng.gamma(0.55, 1.0, size=(f_count, k)) + 0.05
    family_pi /= family_pi.sum(axis=1, keepdims=True)
    state = draw_categorical(rng, family_pi[base.family])
    observations = np.empty((len(base.family), 3), dtype=np.int16)
    for edition in range(3):
        order = rng.permutation(s_count)
        emissions = np.empty((k, s_count), dtype=np.float64)
        for hidden in range(k):
            noise = rng.gamma(0.7, 1.0, size=s_count)
            noise[order[hidden]] = 0.0
            noise /= noise.sum()
            emissions[hidden] = noise * (1.0 - strength)
            emissions[hidden, order[hidden]] = strength
        observations[:, edition] = draw_categorical(rng, emissions[state])
    return observations


def null_direct_observations(base: Panel, label: str) -> np.ndarray:
    rng = rng_for(label)
    f_count = len(base.family_names)
    s_count = len(base.symbol_names)
    prototype_count = 28
    prototypes = rng.integers(0, s_count, size=(f_count, prototype_count, 3), dtype=np.int16)
    weights = rng.gamma(0.35, 1.0, size=(f_count, prototype_count)) + 0.001
    weights /= weights.sum(axis=1, keepdims=True)
    choice = draw_categorical(rng, weights[base.family])
    output = prototypes[base.family, choice].copy()
    # Low independent noise prevents a degenerate memorization-only fixture.
    noise = rng.random(output.shape) < 0.015
    output[noise] = rng.integers(0, s_count, size=int(np.sum(noise)), dtype=np.int16)
    return output


def family_private_observations(base: Panel, label: str) -> np.ndarray:
    rng = rng_for(label)
    f_count = len(base.family_names)
    s_count = len(base.symbol_names)
    k = 4
    family_pi = rng.gamma(0.7, 1.0, size=(f_count, k)) + 0.05
    family_pi /= family_pi.sum(axis=1, keepdims=True)
    state = draw_categorical(rng, family_pi[base.family])
    output = np.empty((len(base.family), 3), dtype=np.int16)
    mapping = np.empty((f_count, 3, k), dtype=np.int16)
    for fam in range(f_count):
        for edition in range(3):
            mapping[fam, edition] = rng.choice(s_count, size=k, replace=False)
    for edition in range(3):
        output[:, edition] = mapping[base.family, edition, state]
    noise = rng.random(output.shape) < 0.04
    output[noise] = rng.integers(0, s_count, size=int(np.sum(noise)), dtype=np.int16)
    return output


def dominant_policy_observations(base: Panel, label: str) -> np.ndarray:
    output = null_direct_observations(base, label + "|BACKGROUND")
    selected_family = int(hashlib.sha256(label.encode()).digest()[0]) % len(base.family_names)
    mask = base.family == selected_family
    output[mask, 0] = 1
    output[mask, 1] = 1
    output[mask, 2] = 2
    return output


def make_world(base: Panel, family_name: str, index: int) -> tuple[Panel, int | None]:
    label = f"LTG001_SYNTH_V1|{family_name}|{index:02d}"
    planted_k: int | None = None
    if family_name == "NULL_DIRECT":
        observations = null_direct_observations(base, label)
    elif family_name == "SHARED_CHANNEL":
        planted_k = 2 + index % 5
        observations = shared_observations(base, label, planted_k)
    elif family_name == "ONE_FOLIO_CHANNEL":
        observations = null_direct_observations(base, label + "|NULL")
        planted = shared_observations(base, label + "|PLANT", 4, 0.80)
        folios = sorted(set(base.folio))
        selected = folios[index % len(folios)]
        mask = np.asarray([value == selected for value in base.folio])
        observations[mask] = planted[mask]
    elif family_name == "FAMILY_PRIVATE_CHANNEL":
        observations = family_private_observations(base, label)
    elif family_name == "DOMINANT_POLICY_ONLY":
        observations = dominant_policy_observations(base, label)
    else:
        raise ValueError(family_name)
    panel = panel_from_arrays(
        base.family, observations, base.folio, base.currier,
        len(base.family_names), len(base.symbol_names),
    )
    if family_name == "DOMINANT_POLICY_ONLY":
        selected_family = int(hashlib.sha256(label.encode()).digest()[0]) % len(base.family_names)
        marker = []
        for fam, values in zip(base.family.tolist(), observations.tolist()):
            if fam == selected_family:
                marker.append(("B", "B1", "B1", "Ba"))
            else:
                marker.append((panel.family_names[fam], *(panel.symbol_names[value] for value in values)))
        panel = Panel(
            family=panel.family, observations=panel.observations, folio=panel.folio,
            fold=panel.fold, currier=panel.currier, triplet=tuple(marker),
            family_names=panel.family_names, symbol_names=panel.symbol_names,
        )
    return panel, planted_k


def run_world(task: tuple[str, int]) -> dict:
    family_name, index = task
    base = load_panel(GROUPS)
    world, planted_k = make_world(base, family_name, index)
    evaluation = evaluate_panel(world, f"LTG001_SYNTH_V1|{family_name}|{index:02d}")
    selected = [row["selected_k"] for row in evaluation["fold_models"]]
    return {
        "world_id": f"{family_name}_{index:02d}",
        "family": family_name,
        "index": index,
        "planted_k": planted_k,
        "selected_k_by_fold": selected,
        "selected_k_median": int(np.median(np.asarray(selected))),
        "summary": evaluation["summary"],
    }


def main() -> None:
    for output in (OUT_JSON, OUT_REPORT):
        if output.exists():
            raise SystemExit(f"refusing to overwrite {output.name}")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_IDENTIFIABLE_CROSS_FOLIO_CHANNEL":
        raise SystemExit("capacity is not PASS")
    if not V1.exists() or not V2.exists():
        raise SystemExit("the disclosed v1/v2 calibration stops are missing")
    prior = json.loads(V2.read_text(encoding="utf-8"))
    if prior["status"] != "STOP_CALIBRATION_FAILURE" or prior["world_count"] != 56:
        raise SystemExit("v1 calibration stop drift")
    worlds = [world for world in prior["worlds"] if world["family"] != "DOMINANT_POLICY_ONLY"]
    tasks = [("DOMINANT_POLICY_ONLY", index) for index in range(8)]
    with ProcessPoolExecutor(max_workers=8) as pool:
        worlds.extend(pool.map(run_world, tasks))
    order = {family: index for index, (family, _) in enumerate(WORLD_FAMILIES)}
    worlds.sort(key=lambda world: (order[world["family"]], world["index"]))
    by_family = {}
    for family, count in WORLD_FAMILIES:
        selected = [world for world in worlds if world["family"] == family]
        pass_count = sum(world["summary"]["decision"] == "PASS_REUSABLE_LATENT_CHANNEL" for world in selected)
        by_family[family] = {"worlds": count, "pass_count": pass_count}
        if family == "SHARED_CHANNEL":
            by_family[family]["k_within_one"] = sum(
                abs(world["selected_k_median"] - world["planted_k"]) <= 1 for world in selected
            )
    gates = {
        "null_direct_at_most_one": by_family["NULL_DIRECT"]["pass_count"] <= 1,
        "shared_channel_at_least_14": by_family["SHARED_CHANNEL"]["pass_count"] >= 14,
        "shared_k_within_one_at_least_12": by_family["SHARED_CHANNEL"]["k_within_one"] >= 12,
        "one_folio_at_most_one": by_family["ONE_FOLIO_CHANNEL"]["pass_count"] <= 1,
        "family_private_at_most_one": by_family["FAMILY_PRIVATE_CHANNEL"]["pass_count"] <= 1,
        "dominant_policy_at_most_one": by_family["DOMINANT_POLICY_ONLY"]["pass_count"] <= 1,
    }
    status = "PASS_TARGET_FREE_LATENT_CHANNEL_INSTRUMENT" if all(gates.values()) else "STOP_CALIBRATION_FAILURE"
    result = {
        "experiment": "LTG001_LATENT_TRANSCRIPTION_CHANNEL_CALIBRATION",
        "status": status,
        "inputs": {
            path.name: {"sha256": sha(path), "bytes": path.stat().st_size}
            for path in (GROUPS, CAPACITY, V1, V2, HERE / "LTG001_LATENT_TRANSCRIPTION_CHANNEL_METHOD.md", HERE / "ltg001_latent_channel_core.py", Path(__file__).resolve())
        },
        "world_registry": [{"family": family, "count": count} for family, count in WORLD_FAMILIES],
        "world_count": len(worlds),
        "by_family": by_family,
        "gates": gates,
        "worlds": worlds,
        "real_panel_scored": False,
        "claim_ceiling": "Target-free instrument behavior only; no preferred reading, glyph, allograph, sound, word, language, cipher, plaintext, meaning, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# LTG001 latent transcription-channel calibration",
        "",
        f"Status: **{status}** across {len(worlds)} target-free worlds.",
        "",
    ]
    for family, _ in WORLD_FAMILIES:
        item = by_family[family]
        extra = f"; planted K within one: {item['k_within_one']}" if "k_within_one" in item else ""
        lines.append(f"- `{family}`: {item['pass_count']}/{item['worlds']} positive decisions{extra}.")
    lines += [
        "",
        "No manuscript member outcome was scored in this calibration. A pass authorizes",
        "one deterministic whole-folio manuscript evaluation under the frozen method and",
        "claim ceiling.",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": status, "by_family": by_family}, sort_keys=True))


if __name__ == "__main__":
    main()
