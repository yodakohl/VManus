#!/usr/bin/env python3
"""Clean-room reconstruction of EO001 v2 target-free calibration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_FILE = RESULTS / "eo001_exact_form_onset_capacity.tsv"
CAPACITY = RESULTS / "eo001_exact_form_onset_capacity.json"
CAPACITY_VALIDATION = RESULTS / "eo001_exact_form_onset_capacity_validation.json"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
SPEC = BASE / "EO001_EXACT_FORM_ONSET_TRANSFER_PREREGISTRATION.md"
CORE = BASE / "eo001_core.py"
RUNNER = BASE / "run_eo001_synthetic_preflight.py"
PRODUCTION = RESULTS / "eo001_synthetic_preflight_v2.json"
PRODUCTION_REPORT = RESULTS / "eo001_synthetic_preflight_v2_report.md"
VALIDATOR = Path(__file__).resolve()
OUT_JSON = RESULTS / "eo001_synthetic_preflight_v2_validation.json"
OUT_REPORT = RESULTS / "eo001_synthetic_preflight_v2_validation_report.md"

HASHES = {
    PANEL_FILE: "9bad926ec53532ca118c9bcdee82fbe5ffebe53b328b0716cc85082f72690d4c",
    CAPACITY: "1a54880f334f5d522c23d2fa0ffcae4eb45f285f4d45c89b3e88373ee8c35b85",
    CAPACITY_VALIDATION: "db22634ff99477ee52d57379dc4efc37084c514606866e4b8bda458a548137f4",
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    SPEC: "958f71457da5fff51da517e07675959cf5f94a5e952581beb845a64079cf9950",
    CORE: "10487bff3881ef936cfc325cc6657bae21988d60f7dfe5f919ab016a8fec8596",
    RUNNER: "4662738c8bdaa428c79a45fc28be11d9c9c59694cef5d6e4f9df05c70f2038c2",
    PRODUCTION: "83fb94fbe6aaf037bd406ea50aa767e8b3db91831b691e8c21740a1e643ed00d",
    PRODUCTION_REPORT: "61f9ba054e069a5d04710abbf3825c48c6af447dd10aac5d92ca72038d3df096",
}
ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
INDEX = {value: index for index, value in enumerate(ALPHABET)}
FORMS = ("AQKA", "BLJBA", "CAF", "CAG", "DAQKA", "DAQKBA", "LA", "QAC", "QKJBA")
DIMS = {"EDGE_48": 48, "BAG_24": 24, "BIGRAM_576": 576}
FIELDS = (
    "anonymous_event_id", "trigger_family_surface", "trigger_state", "physical_folio",
    "section", "currier", "hand", "code", "kind", "trigger_group_index",
    "locus_group_count", "remaining_groups_after_trigger",
)
ASSIGNMENTS = 32768
RIDGE = 1e-3
TOL = 1e-12
AMPLITUDES = (.25, .50, .75, 1.00, 1.50, 2.00)
ADVERSARIES = (
    "GENERIC", "POSITION_ONLY", "NUISANCE_ONLY", "ONE_FORM", "ONE_FOLIO",
    "ONE_STATE", "ONE_BLOCK", "REVERSED_STATE", "STATE_REMAPPED", "FOLIO_RANDOM",
)


@dataclass
class Data:
    rows: list[dict[str, str]]
    forms: np.ndarray
    states: np.ndarray
    folios: np.ndarray
    curriers: np.ndarray
    design: np.ndarray
    informative: dict[str, tuple[int, ...]]
    permutations: dict[str, np.ndarray]


DATA: Data | None = None
DONORS: list[str] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_design(rows: list[dict[str, str]]) -> np.ndarray:
    columns = [np.ones(len(rows), dtype=np.float64)]
    for field in ("currier", "section", "hand", "code"):
        for value in sorted({row[field] for row in rows}):
            columns.append(np.asarray([float(row[field] == value) for row in rows]))
    count = np.asarray([float(row["locus_group_count"]) for row in rows])
    index = np.asarray([float(row["trigger_group_index"]) for row in rows])
    remaining = np.asarray([float(row["remaining_groups_after_trigger"]) for row in rows])
    for vector in (np.log1p(count), index / (count - 1), np.log1p(remaining)):
        columns += [vector, vector * vector, vector * vector * vector]
    matrix = np.column_stack(columns).astype(np.float64)
    for column in range(1, matrix.shape[1]):
        mean, sd = matrix[:, column].mean(), matrix[:, column].std(ddof=0)
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError("bad design variance")
        matrix[:, column] = (matrix[:, column] - mean) / sd
    if matrix.shape != (1295, 32) or not np.isfinite(matrix).all():
        raise ValueError("design drift")
    return matrix


def perms(folio: str, present: tuple[int, ...]) -> np.ndarray:
    size = len(present)
    matrix = np.empty((ASSIGNMENTS, size), dtype=np.int16)
    matrix[0] = np.arange(size)
    names = [FORMS[index] for index in present]
    for assignment in range(1, ASSIGNMENTS):
        matrix[assignment] = sorted(
            range(size),
            key=lambda index: hashlib.sha256(f"EO001-PERM|{assignment}|{folio}|{names[index]}".encode()).digest(),
        )
    if not np.array_equal(np.sort(matrix, axis=1), np.broadcast_to(np.arange(size), matrix.shape)):
        raise ValueError("not permutations")
    return matrix


def build_data(rows: list[dict[str, str]]) -> Data:
    ids = [row["anonymous_event_id"] for row in rows]
    if len(rows) != 1295 or len(set(ids)) != 1295 or ids != sorted(ids):
        raise ValueError("identity/order drift")
    if tuple(sorted({row["trigger_family_surface"] for row in rows})) != FORMS:
        raise ValueError("form drift")
    if Counter(row["trigger_state"] for row in rows) != {"FIRST": 316, "CORE": 979}:
        raise ValueError("state drift")
    fmap = {value: index for index, value in enumerate(FORMS)}
    forms = np.asarray([fmap[row["trigger_family_surface"]] for row in rows], dtype=np.int64)
    states = np.asarray([0 if row["trigger_state"] == "FIRST" else 1 for row in rows], dtype=np.int8)
    folios = np.asarray([row["physical_folio"] for row in rows])
    curriers = np.asarray([row["currier"] for row in rows])
    for row in rows:
        index, count, remaining = map(int, (row["trigger_group_index"], row["locus_group_count"], row["remaining_groups_after_trigger"]))
        if remaining != count - index or remaining < 2 or ((row["trigger_state"] == "FIRST") != (index == 1)) or row["kind"] != "P":
            raise ValueError("row geometry drift")
    for folio in set(folios):
        if len(set(curriers[folios == folio])) != 1:
            raise ValueError("folio currier drift")
    informative = {}
    for folio in sorted(set(folios), key=lambda value: int(value[1:])):
        present = tuple(form for form in range(9) if np.any((folios == folio) & (forms == form) & (states == 0)) and np.any((folios == folio) & (forms == form) & (states == 1)))
        if len(present) >= 2:
            informative[folio] = present
    if len(informative) != 38 or sum(map(len, informative.values())) != 112:
        raise ValueError("informative geometry")
    return Data(rows, forms, states, folios, curriers, make_design(rows), informative, {folio: perms(folio, present) for folio, present in informative.items()})


def read_panel() -> Data:
    with PANEL_FILE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("schema")
        return build_data(list(reader))


def fp(sequence: str) -> dict[str, np.ndarray]:
    if not sequence or any(symbol not in INDEX for symbol in sequence):
        raise ValueError("bad sequence")
    edge = np.zeros(48); edge[INDEX[sequence[0]]] = 1; edge[24 + INDEX[sequence[-1]]] = 1
    bag = np.zeros(24)
    for symbol in sequence:
        bag[INDEX[symbol]] += 1 / len(sequence)
    bigram = np.zeros(576)
    for left, right in zip(sequence, sequence[1:]):
        bigram[24 * INDEX[left] + INDEX[right]] += 1 / max(1, len(sequence) - 1)
    return {"EDGE_48": edge, "BAG_24": bag, "BIGRAM_576": bigram}


def fp_matrix(sequences: list[str]) -> dict[str, np.ndarray]:
    if len(sequences) != 1295:
        raise ValueError("sequence count")
    out = {name: np.empty((1295, dimension)) for name, dimension in DIMS.items()}
    for index, sequence in enumerate(sequences):
        row = fp(sequence)
        for name in DIMS:
            out[name][index] = row[name]
    return out


def residuals(response: np.ndarray) -> np.ndarray:
    assert DATA is not None
    if response.ndim != 2 or response.shape[0] != 1295 or not np.isfinite(response).all():
        raise ValueError("response")
    result = np.empty_like(response)
    penalty = np.eye(32) * RIDGE; penalty[0, 0] = 0
    for state in (0, 1):
        smask = DATA.states == state
        for folio in DATA.informative:
            held = smask & (DATA.folios == folio)
            if not held.any():
                continue
            train = smask & (DATA.folios != folio)
            zt, zh = DATA.design[train], DATA.design[held]
            beta = np.linalg.solve(zt.T @ zt + penalty, zt.T @ response[train])
            result[held] = response[held] - zh @ beta
    used = np.isin(DATA.folios, tuple(DATA.informative))
    if not np.isfinite(result[used]).all():
        raise ValueError("residual")
    return result


def similarity(response: np.ndarray) -> dict[str, np.ndarray]:
    assert DATA is not None
    resid = residuals(response); out = {}
    for folio, present in DATA.informative.items():
        matrices = []
        for state in (0, 1):
            means = np.asarray([resid[(DATA.folios == folio) & (DATA.states == state) & (DATA.forms == form)].mean(axis=0) for form in present])
            norm = np.linalg.norm(means, axis=1)
            matrices.append(np.divide(means, norm[:, None], out=np.zeros_like(means), where=norm[:, None] > 1e-15))
        out[folio] = matrices[0] @ matrices[1].T
    return out


def orbit(response: np.ndarray) -> dict:
    assert DATA is not None
    sims = similarity(response); values = np.zeros(ASSIGNMENTS); fe = {}; fv = defaultdict(list)
    for folio, present in DATA.informative.items():
        matrix = sims[folio]; local = np.arange(len(present))[None, :]
        values += matrix[local, DATA.permutations[folio]].mean(axis=1) / 38
        diagonal = float(np.diag(matrix).mean())
        wrong = float((matrix.sum() - np.trace(matrix)) / (len(present) * (len(present) - 1)))
        fe[folio] = diagonal - wrong
        for row, form in enumerate(present):
            fv[form].append(float(matrix[row, row] - (matrix[row].sum() - matrix[row, row]) / (len(present) - 1)))
    null = values[1:]; mean = float(null.mean()); sd = float(null.std(ddof=0)); observed = float(values[0])
    if sd <= 0 or not np.isfinite(sd): raise ValueError("orbit")
    return {"orbit": values, "observed": observed, "null_mean": mean, "null_sd": sd, "raw_effect": observed - mean,
            "z": (observed - mean) / sd, "p": (1 + int((null >= observed - TOL).sum())) / ASSIGNMENTS,
            "folio_effects": fe, "form_effects": {FORMS[key]: float(np.mean(value)) for key, value in sorted(fv.items())}}


def evaluate(blocks: dict[str, np.ndarray]) -> dict:
    assert DATA is not None
    if tuple(blocks) != tuple(DIMS): raise ValueError("block order")
    for name, dimension in DIMS.items():
        if blocks[name].shape != (1295, dimension): raise ValueError("block dim")
    raw = {name: orbit(blocks[name]) for name in DIMS}
    standardized = np.vstack([(raw[name]["orbit"] - raw[name]["null_mean"]) / raw[name]["null_sd"] for name in DIMS])
    combined = standardized.mean(axis=0); observed = float(combined[0])
    pvalue = (1 + int((combined[1:] >= observed - TOL).sum())) / ASSIGNMENTS
    folio_values = {folio: float(np.mean([raw[name]["folio_effects"][folio] / raw[name]["null_sd"] for name in DIMS])) for folio in DATA.informative}
    form_values = {form: float(np.mean([raw[name]["form_effects"][form] / raw[name]["null_sd"] for name in DIMS])) for form in FORMS}
    fa = np.asarray(list(folio_values.values())); ma = np.asarray(list(form_values.values()))
    delete = (fa.sum() - fa) / 37
    currier = {}
    for label in "AB":
        selected = [effect for folio, effect in folio_values.items() if DATA.curriers[np.flatnonzero(DATA.folios == folio)[0]] == label]
        currier[label] = {"folios": len(selected), "mean": float(np.mean(selected))}
    summary = {
        "combined_observed": observed, "combined_p": pvalue, "positive_folios": int((fa > 0).sum()),
        "informative_folios": 38, "positive_forms": int((ma > 0).sum()), "minimum_delete_one_folio_mean": float(delete.min()),
        "max_abs_folio_contribution_fraction": float(np.abs(fa).max() / np.abs(fa).sum()) if np.abs(fa).sum() else 1.0,
        "max_abs_form_contribution_fraction": float(np.abs(ma).max() / np.abs(ma).sum()) if np.abs(ma).sum() else 1.0,
        "currier": currier, "folio_contributions": folio_values, "form_contributions": form_values,
    }
    blocks_out = {name: {key: value for key, value in raw[name].items() if key not in ("orbit", "folio_effects", "form_effects")} for name in DIMS}
    gates = {
        "exact_geometry": len(DATA.rows) == 1295 and len(set(DATA.folios)) == 92 and len(DATA.informative) == 38,
        "combined_material": observed >= 1.5, "combined_p_at_most_0001": pvalue <= .001,
        "all_blocks_positive": all(blocks_out[name]["raw_effect"] > 0 for name in DIMS),
        "two_blocks_p_at_most_001": sum(blocks_out[name]["p"] <= .01 for name in DIMS) >= 2,
        "positive_folio_support": summary["positive_folios"] >= 24, "positive_form_support": summary["positive_forms"] >= 7,
        "both_curriers_positive": all(currier[label]["folios"] >= 10 and currier[label]["mean"] > 0 for label in "AB"),
        "all_folio_deletions_positive": summary["minimum_delete_one_folio_mean"] > 0,
        "no_folio_concentration": summary["max_abs_folio_contribution_fraction"] <= .20,
        "no_form_concentration": summary["max_abs_form_contribution_fraction"] <= .30,
    }
    return {"blocks": blocks_out, "summary": summary, "gates": gates, "passes": all(gates.values())}


def vseed(family: str, world: int, amplitude: float | None) -> int:
    label = "NONE" if amplitude is None else f"{amplitude:.2f}"
    return int.from_bytes(hashlib.sha256(f"EO001|{family}|{world}|{label}".encode()).digest()[:8], "little")


def donor_matrix(rng: np.random.Generator) -> dict[str, np.ndarray]:
    choice = rng.choice(len(DONORS), size=1295, replace=False)
    return fp_matrix([DONORS[int(index)] for index in choice])


def gaussian(family: str, world: int, amplitude: float) -> dict[str, np.ndarray]:
    assert DATA is not None
    rng = np.random.Generator(np.random.PCG64(vseed(family, world, amplitude))); out = {}
    rel = np.asarray([int(row["trigger_group_index"]) / (int(row["locus_group_count"]) - 1) for row in DATA.rows])
    for block_index, (name, dimension) in enumerate(DIMS.items()):
        signature = rng.normal(size=(9, dimension)); noise = rng.normal(size=(1295, dimension)); signal = signature[DATA.forms].copy()
        if family == "GENERIC": signal[:] = signature[0]
        elif family == "POSITION_ONLY":
            coef = rng.normal(size=(4, dimension)); signal = np.column_stack((np.ones(1295), rel, rel * rel, rel * rel * rel)) @ coef
        elif family == "NUISANCE_ONLY": signal = DATA.design @ rng.normal(size=(32, dimension))
        elif family == "ONE_FORM": signal[DATA.forms != world % 9] = 0
        elif family == "ONE_FOLIO":
            selected = tuple(DATA.informative)[world % 38]; signal[DATA.folios != selected] = 0
        elif family == "ONE_STATE": signal[DATA.states == 1] = 0
        elif family == "ONE_BLOCK":
            if block_index != world % 3: signal[:] = 0
        elif family == "REVERSED_STATE": signal[DATA.states == 1] *= -1
        elif family == "STATE_REMAPPED":
            mask = DATA.states == 1; signal[mask] = signature[(DATA.forms[mask] + 1) % 9]
        elif family == "FOLIO_RANDOM":
            mask = DATA.states == 1
            for folio in sorted(set(DATA.folios)):
                shift = 1 + vseed(f"FOLIO_SHIFT_{folio}", world, amplitude) % 8
                chosen = mask & (DATA.folios == folio); signal[chosen] = signature[(DATA.forms[chosen] + shift) % 9]
        elif family != "PORTABLE": raise ValueError("family")
        out[name] = noise + amplitude * signal
    return out


def whole(family: str, world: int) -> dict[str, np.ndarray]:
    assert DATA is not None
    rng = np.random.Generator(np.random.PCG64(vseed(family, world, .60))); blocks = donor_matrix(rng)
    if family == "REALISTIC_NULL": return blocks
    choices = rng.choice(len(DONORS), size=9, replace=False); rows = [fp(DONORS[int(index)]) for index in choices]
    proto = {name: np.asarray([row[name] for row in rows]) for name in DIMS}; selected = rng.random(1295) < .60
    for name in DIMS: blocks[name][selected] = proto[name][DATA.forms[selected]]
    return blocks


def compact(result: dict) -> dict:
    return {"passes": result["passes"], "gates": result["gates"], "blocks": result["blocks"],
            "summary": {key: value for key, value in result["summary"].items() if key not in ("folio_contributions", "form_contributions")},
            "folio_contributions": result["summary"]["folio_contributions"], "form_contributions": result["summary"]["form_contributions"]}


def task(item: tuple[str, int, float | None]) -> dict:
    family, world, amplitude = item
    if family == "GAUSSIAN_NULL": blocks = gaussian("PORTABLE", world, 0)
    elif family in ("REALISTIC_NULL", "WHOLE_ROW_PORTABLE"): blocks = whole(family, world)
    else: blocks = gaussian(family, world, float(amplitude))
    return {"family": family, "world": world, "amplitude": amplitude, "evaluation": compact(evaluate(blocks))}


def compare(actual, expected, path="root") -> tuple[int, float]:
    if isinstance(expected, dict):
        if set(actual) != set(expected): raise AssertionError(path + " keys")
        checks = 1; delta = 0.0
        for key in expected:
            c, d = compare(actual[key], expected[key], path + "." + str(key)); checks += c; delta = max(delta, d)
        return checks, delta
    if isinstance(expected, list):
        if len(actual) != len(expected): raise AssertionError(path + " length")
        checks = 1; delta = 0.0
        for index, value in enumerate(expected):
            c, d = compare(actual[index], value, path + f"[{index}]"); checks += c; delta = max(delta, d)
        return checks, delta
    if isinstance(expected, float):
        difference = abs(float(actual) - expected)
        if difference > 1e-12: raise AssertionError(f"{path}: {actual} != {expected}")
        return 1, difference
    if actual != expected: raise AssertionError(f"{path}: {actual} != {expected}")
    return 1, 0.0


def expect_reject(rows: list[dict[str, str]]) -> None:
    try: build_data(rows)
    except (ValueError, AssertionError): return
    raise AssertionError("mutation accepted")


def main() -> None:
    global DATA, DONORS
    checks = 0
    for path, digest in HASHES.items():
        if sha(path) != digest: raise AssertionError(f"hash {path}")
        checks += 1
    DATA = read_panel(); checks += 1295
    with SOURCE.open(encoding="utf-8", newline="") as handle: source = list(csv.DictReader(handle, delimiter="\t"))
    panel_ids = {row["anonymous_event_id"] for row in DATA.rows}
    by_locus = {(row["locus"], int(row["group_index"])): row for row in source}
    excluded = set(); matched = 0
    for row in source:
        key = "EO001-" + hashlib.sha256(("EO001|" + row["consensus_group_id"]).encode()).hexdigest()[:20]
        if key in panel_ids:
            matched += 1; excluded.add(by_locus[(row["locus"], int(row["group_index"]) + 1)]["consensus_group_id"])
    DONORS = [row["family_surface"] for row in source if row["consensus_group_id"] not in excluded and row["grammar_scope"] == "CONFIRMED_PROSE"]
    if matched != 1295 or len(excluded) != 1295 or len(DONORS) != 20604: raise AssertionError("donors")
    checks += len(source)
    tasks = [("GAUSSIAN_NULL", world, None) for world in range(64)] + [("REALISTIC_NULL", world, None) for world in range(64)]
    tasks += [("PORTABLE", world, amplitude) for amplitude in AMPLITUDES for world in range(8)]
    tasks += [("WHOLE_ROW_PORTABLE", world, .60) for world in range(8)]
    tasks += [(family, world, .25) for family in ADVERSARIES for world in range(8)]
    with ProcessPoolExecutor(max_workers=32) as pool: records = list(pool.map(task, tasks, chunksize=1))
    records.sort(key=lambda row: (row["family"], -1 if row["amplitude"] is None else row["amplitude"], row["world"]))
    stored = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    c, max_delta = compare(stored["worlds"], records, "worlds"); checks += c
    portable = {f"{amplitude:.2f}": sum(row["evaluation"]["passes"] for row in records if row["family"] == "PORTABLE" and row["amplitude"] == amplitude) for amplitude in AMPLITUDES}
    pass_counts = {family: sum(row["evaluation"]["passes"] for row in records if row["family"] == family) for family in ("GAUSSIAN_NULL", "REALISTIC_NULL", "WHOLE_ROW_PORTABLE", *ADVERSARIES)}
    gates = {"gaussian_null_zero_of_64": pass_counts["GAUSSIAN_NULL"] == 0, "realistic_null_zero_of_64": pass_counts["REALISTIC_NULL"] == 0,
             "portable_at_least_seven_of_eight": portable["0.25"] >= 7, "whole_row_portable_at_least_seven_of_eight": pass_counts["WHOLE_ROW_PORTABLE"] >= 7,
             "all_adversarial_families_zero_of_eight": all(pass_counts[name] == 0 for name in ADVERSARIES),
             "target_successors_excluded_from_donors": len(excluded) == 1295 and len(DONORS) == 20604,
             "all_results_finite": all(np.isfinite(row["evaluation"]["summary"]["combined_observed"]) for row in records)}
    if stored["portable_pass_counts"] != portable or stored["pass_counts"] != pass_counts or stored["gates"] != gates or not all(gates.values()): raise AssertionError("summaries")
    checks += 3
    expected_report = (
        "# EO001 synthetic preflight v2\n\nStatus: **PASS_TARGET_FREE_CALIBRATION**.\n\n"
        "The scorer evaluated **264** target-free worlds with 32,768 within-folio assignments. The smallest portable amplitude reaching 7/8 was **0.25**. Gaussian and realistic null passes were 0/64 and 0/64; whole-row portable signals passed 8/8. All adversarial pass counts were "
        + ", ".join(f"{name}=0/8" for name in ADVERSARIES) + ".\n\n"
        "The 1,295 real successors were excluded from the realistic donor pool and zero target successor surfaces were accessed. Calibration supplies no manuscript association, embedded onset, clause, word, meaning, plaintext, or translation.\n"
    )
    if PRODUCTION_REPORT.read_text(encoding="utf-8") != expected_report: raise AssertionError("report")
    checks += 1
    # Executed fail-closed mutations.
    base = [dict(row) for row in DATA.rows]
    swapped = [dict(row) for row in base]; swapped[0], swapped[1] = swapped[1], swapped[0]; expect_reject(swapped)
    expect_reject(base[:-1]); duplicate = [dict(row) for row in base]; duplicate[-1] = dict(duplicate[0]); expect_reject(duplicate)
    state = [dict(row) for row in base]; state[0]["trigger_state"] = "CORE"; expect_reject(state)
    position = [dict(row) for row in base]; position[0]["remaining_groups_after_trigger"] = "1"; expect_reject(position)
    try: residuals(np.full((1295, 2), np.nan)); raise AssertionError("nan accepted")
    except ValueError: pass
    good = gaussian("PORTABLE", 999, .25); bad = dict(good); bad["EDGE_48"] = bad["EDGE_48"][:, :-1]
    try: evaluate(bad); raise AssertionError("dimension accepted")
    except ValueError: pass
    checks += 7
    result = {"experiment": "EO001_SYNTHETIC_PREFLIGHT_V2_VALIDATION", "status": "PASS_INDEPENDENT_264_WORLD_RECONSTRUCTION",
              "checks": checks, "max_numeric_delta": max_delta, "worlds": len(records), "pass_counts": pass_counts,
              "production_sha256": sha(PRODUCTION), "validator_sha256": sha(VALIDATOR), "target_successor_surfaces_accessed": 0,
              "failures": [], "claim_ceiling": stored["claim_ceiling"]}
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# EO001 synthetic preflight v2 validation\n\n"
        f"Status: **{result['status']}**.\n\nA nonimporting implementation reconstructed all **264** worlds, 32,768-assignment scores, gates, summaries, report bytes, source exclusions, and fail-closed mutations in **{checks:,}** checks; maximum numeric delta was **{max_delta:.3g}**.\n\n"
        "The 1,295 target successor surfaces remained unaccessed. This validates target-free calibration only and supplies no manuscript association, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
