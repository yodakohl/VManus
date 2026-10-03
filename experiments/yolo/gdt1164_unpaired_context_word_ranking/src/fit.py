#!/usr/bin/env python3
"""Anonymous numeric fitter for the fixed GDT1164 contract.

Inputs contain only Dw, De, p, q, written_rates and reference_rates. This module
never reads source tables, lexical strings, site truth or candidate audit joins.
Call fit_payload(mapping, models=("F", "B", "G")), or use --input/--output.
--self-test uses tiny invented arrays only. Real fitting requires root release;
this module does not itself establish source capacity or authorize fitting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np
import torch

KEYS = ("Dw", "De", "p", "q", "written_rates", "reference_rates")
MODELS = ("F", "B", "G")
SEEDS = (0, 1, 2)
STEPS = 200
QUANTILES = np.array([i / 15 for i in range(16)], dtype=np.float64)
_THREAD_SETUP_DONE = False


class InvalidNumerics(ValueError):
    """A nonfinite or invalid numeric payload/optimization, never repaired."""


def _threads() -> None:
    global _THREAD_SETUP_DONE
    if not _THREAD_SETUP_DONE:
        torch.set_num_threads(1)
        # If an embedding caller already began interop work, it controls that
        # pool. No numerical or optimizer setting changes in this circumstance.
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
        _THREAD_SETUP_DONE = True


def _digest(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array, dtype=np.float64)
    return hashlib.sha256(value.tobytes(order="C")).hexdigest()


def validate_payload(payload: Mapping[str, object]) -> dict[str, np.ndarray]:
    if set(payload) != set(KEYS):
        raise InvalidNumerics("packet must contain exactly the six numeric keys")
    arrays = {}
    for key in KEYS:
        raw = np.asarray(payload[key])
        if raw.dtype != np.dtype(np.float64):
            raise InvalidNumerics(f"{key}: float64 required, without silent conversion")
        if not np.isfinite(raw).all():
            raise InvalidNumerics(f"{key}: nonfinite input")
        arrays[key] = np.ascontiguousarray(raw)
    n, m = arrays["p"].size, arrays["q"].size
    if n < 2 or m < 2:
        raise InvalidNumerics("each space needs at least two nodes")
    for key, size in (("p", n), ("q", m), ("written_rates", n), ("reference_rates", m)):
        if arrays[key].shape != (size,) or (arrays[key] <= 0).any():
            raise InvalidNumerics(f"{key}: positive one-dimensional vector required")
    for key in ("p", "q"):
        if not np.isclose(arrays[key].sum(), 1.0, rtol=0, atol=1e-12):
            raise InvalidNumerics(f"{key}: masses must sum to one")
    for rate_key, mass_key in (("written_rates", "p"), ("reference_rates", "q")):
        rates = arrays[rate_key]
        if rates.sum() > 1 + 1e-12 or (rates > 1).any():
            raise InvalidNumerics(f"{rate_key}: full-panel occurrence rates required")
        if not np.allclose(rates / rates.sum(), arrays[mass_key], rtol=1e-12, atol=1e-14):
            raise InvalidNumerics(f"{rate_key}: rates and selected transport masses disagree")
    for key, size in (("Dw", n), ("De", m)):
        distance = arrays[key]
        if distance.shape != (size, size) or (distance < 0).any():
            raise InvalidNumerics(f"{key}: nonnegative square matrix required")
        if not np.array_equal(np.diag(distance), np.zeros(size)):
            raise InvalidNumerics(f"{key}: diagonal must be exactly zero")
        if not np.allclose(distance, distance.T, rtol=0, atol=1e-12):
            raise InvalidNumerics(f"{key}: distance symmetry required")
        offdiag = distance[~np.eye(size, dtype=bool)]
        if offdiag.mean() <= 0 or not np.isclose(offdiag.mean(), 1.0, rtol=0, atol=1e-10):
            raise InvalidNumerics(f"{key}: positive offdiagonal mean normalized to one required")
    return arrays


def fingerprints(distance: np.ndarray) -> np.ndarray:
    """Sixteen declared linear quantiles, excluding each row's diagonal."""
    size = distance.shape[0]
    offdiag = distance[~np.eye(size, dtype=bool)].reshape(size, size - 1)
    return np.quantile(offdiag, QUANTILES, axis=1, method="linear").T


def baseline_costs(arrays: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    f = np.abs(np.log(arrays["written_rates"])[:, None] - np.log(arrays["reference_rates"])[None, :])
    fw, fe = fingerprints(arrays["Dw"]), fingerprints(arrays["De"])
    b = ((fw[:, None, :] - fe[None, :, :]) ** 2).sum(axis=2)
    costs = {}
    for model, cost in (("F", f), ("B", b)):
        mean = float(cost.mean())
        costs[model] = cost / mean if mean > 0 else cost
    return costs


def gw_efficient(dw: torch.Tensor, de: torch.Tensor, coupling: torch.Tensor) -> torch.Tensor:
    """Exact four-index squared-distance GW, with actual row/column masses.

    sum(Dw_ik^2 r_i r_k) + sum(De_jl^2 c_j c_l)
      - 2 sum(G_ij * (Dw @ G @ De.T)_ij).
    No balanced-column assumption, factor 1/2, entropy constant or clipping.
    """
    r, c = coupling.sum(dim=1), coupling.sum(dim=0)
    return r @ dw.square() @ r + c @ de.square() @ c - 2 * (coupling * (dw @ coupling @ de.T)).sum()


def _objective(z: torch.Tensor, model: str, tensors: Mapping[str, torch.Tensor], cost: torch.Tensor | None):
    log_rows = torch.log_softmax(z, dim=1)
    rows = log_rows.exp()
    coupling = tensors["p"][:, None] * rows
    columns = coupling.sum(dim=0)
    # logsumexp also defines zero-mass limiting terms safely without clipping.
    log_columns = torch.logsumexp(tensors["logp"][:, None] + log_rows, dim=0)
    column_kl = (columns * (log_columns - tensors["logq"])).sum()
    joint_kl = (coupling * (log_rows - tensors["logq"][None, :])).sum()
    if model == "G":
        # Row masses are fixed to p by the parameterization; precompute this
        # constant term. The relaxed columns enter both other GW terms.
        data = tensors["gw_written_constant"] + columns @ tensors["De2"] @ columns - 2 * (coupling * (tensors["Dw"] @ coupling @ tensors["De"].T)).sum()
    else:
        data = (cost * coupling).sum()
    objective = data + column_kl + 0.01 * joint_kl
    return objective, {"data_cost": data, "column_kl": column_kl, "joint_kl": joint_kl}, coupling, rows


def fit_model(arrays: Mapping[str, np.ndarray], model: str, cost: np.ndarray | None = None) -> dict:
    if model not in MODELS:
        raise ValueError("model must be F, B or G")
    _threads()
    if model in ("F", "B") and cost is None:
        cost = baseline_costs(arrays)[model]
    tensors = {key: torch.from_numpy(value.copy()) for key, value in arrays.items()}
    tensors["logp"], tensors["logq"] = tensors["p"].log(), tensors["q"].log()
    tensors["De2"] = tensors["De"].square()
    tensors["gw_written_constant"] = tensors["p"] @ tensors["Dw"].square() @ tensors["p"]
    torch_cost = torch.from_numpy(cost.copy()) if cost is not None else None
    restarts = []
    final_plans = []
    shape = (arrays["p"].size, arrays["q"].size)
    for seed in SEEDS:
        initial = np.log(arrays["q"])[None, :] + np.random.default_rng(seed).normal(0.0, 0.1, size=shape)
        z = torch.nn.Parameter(torch.from_numpy(initial.copy()))
        optimizer = torch.optim.Adam([z], lr=0.05, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, foreach=False, fused=False)
        for step in range(STEPS):
            optimizer.zero_grad(set_to_none=True)
            loss, _, _, _ = _objective(z, model, tensors, torch_cost)
            if not torch.isfinite(loss):
                raise InvalidNumerics(f"{model} seed{seed} step{step}: nonfinite objective")
            loss.backward()
            if z.grad is None or not torch.isfinite(z.grad).all():
                raise InvalidNumerics(f"{model} seed{seed} step{step}: nonfinite gradient")
            optimizer.step()
            if not torch.isfinite(z).all():
                raise InvalidNumerics(f"{model} seed{seed} step{step + 1}: nonfinite logits")
        with torch.no_grad():
            loss, components, coupling, rows = _objective(z, model, tensors, torch_cost)
        if not torch.isfinite(loss) or not torch.isfinite(coupling).all() or not torch.isfinite(rows).all():
            raise InvalidNumerics(f"{model} seed{seed} after200: nonfinite result")
        row_array = rows.numpy().copy()
        ranking = np.argsort(-row_array, axis=1, kind="stable")
        final_plans.append((coupling.numpy().copy(), row_array, ranking))
        restarts.append({"seed": seed, "steps": STEPS, "objective_after_step200": float(loss), "components": {k: float(v) for k, v in components.items()}, "ranking": ranking.tolist(), "coupling_sha256": _digest(final_plans[-1][0]), "initial_logits_sha256": _digest(initial)})
    # Python min preserves seed order on exact floating-point ties.
    selected = min(range(len(restarts)), key=lambda index: restarts[index]["objective_after_step200"])
    coupling, rows, ranking = final_plans[selected]
    return {"model": model, "restarts": restarts, "selected_seed": restarts[selected]["seed"], "selected_objective": restarts[selected]["objective_after_step200"], "ranking": ranking.tolist(), "normalized_rows": rows.tolist(), "column_masses": coupling.sum(axis=0).tolist(), "coupling_sha256": _digest(coupling), "selection": "minimum objective after200; exact ties seed order", "pair_cost_sha256": _digest(cost) if cost is not None else None}


def fit_payload(payload: Mapping[str, object], models=MODELS) -> dict:
    arrays = validate_payload(payload)
    models = tuple(models)
    if not models or len(set(models)) != len(models) or any(model not in MODELS for model in models):
        raise ValueError("models must be a nonempty unique selection of F/B/G")
    costs = baseline_costs(arrays)
    results = {model: fit_model(arrays, model, costs.get(model)) for model in models}
    return {"schema_version": 1, "status": "FIT_COMPLETE", "input_shapes": {key: list(value.shape) for key, value in arrays.items()}, "input_sha256": {key: _digest(value) for key, value in arrays.items()}, "contract": {"dtype": "float64", "seeds": list(SEEDS), "steps": STEPS, "optimizer": "torch.optim.Adam", "learning_rate": 0.05, "betas": [0.9, 0.999], "epsilon": 1e-8, "weight_decay": 0, "column_kl_weight": 1, "joint_kl_weight": 0.01, "fingerprint_quantiles": QUANTILES.tolist(), "quantile_method": "linear", "ranking_ties": "opaque candidate index", "thread_count": torch.get_num_threads()}, "models": results, "software": {"numpy": np.__version__, "torch": torch.__version__}, "claim_ceiling": "Anonymous numerical optimization only; capacity, source binding and lexical scoring are separate."}


def _literal_gw_numpy(dw: np.ndarray, de: np.ndarray, coupling: np.ndarray) -> float:
    # Independent literal reference for tiny fixtures only: no matrix identity.
    answer = 0.0
    n, m = coupling.shape
    for i in range(n):
        for k in range(n):
            for j in range(m):
                for l in range(m):
                    answer += (dw[i, k] - de[j, l]) ** 2 * coupling[i, j] * coupling[k, l]
    return float(answer)


def self_test() -> dict:
    _threads()
    # Deliberately asymmetric arrays and nonunit, unequal marginals exercise
    # the identity without the geometry validation or balanced simplification.
    dw = np.array([[0.0, 0.7, 1.8], [0.3, 0.0, 1.1], [1.2, 0.4, 0.0]], dtype=np.float64)
    de = np.array([[0.0, 1.3], [0.9, 0.0]], dtype=np.float64)
    coupling = np.array([[0.03, 0.14], [0.07, 0.23], [0.31, 0.09]], dtype=np.float64)
    direct = _literal_gw_numpy(dw, de, coupling)
    tensor_g = torch.tensor(coupling, dtype=torch.float64, requires_grad=True)
    efficient = gw_efficient(torch.from_numpy(dw), torch.from_numpy(de), tensor_g)
    np.testing.assert_allclose(float(efficient.detach()), direct, rtol=1e-12, atol=1e-12)
    efficient.backward()
    # The independent four-index polynomial derivative remains valid for
    # nonsymmetric Dw/De; finite differences do not reuse the matrix formula.
    step = 1e-6
    literal_gradient = np.empty_like(coupling)
    for i in range(coupling.shape[0]):
        for j in range(coupling.shape[1]):
            upper, lower = coupling.copy(), coupling.copy()
            upper[i, j] += step
            lower[i, j] -= step
            literal_gradient[i, j] = (_literal_gw_numpy(dw, de, upper) - _literal_gw_numpy(dw, de, lower)) / (2 * step)
    np.testing.assert_allclose(tensor_g.grad.numpy(), literal_gradient, rtol=1e-8, atol=1e-9)
    w = np.array([[0.0, 0.4, 1.1], [0.4, 0.0, 1.6], [1.1, 1.6, 0.0]], dtype=np.float64)
    e = np.array([[0.0, 0.9, 1.4, 0.3], [0.9, 0.0, 0.5, 1.7], [1.4, 0.5, 0.0, 1.0], [0.3, 1.7, 1.0, 0.0]], dtype=np.float64)
    w /= w[~np.eye(3, dtype=bool)].mean()
    e /= e[~np.eye(4, dtype=bool)].mean()
    p = np.array([0.5, 0.3, 0.2], dtype=np.float64)
    q = np.array([0.4, 0.25, 0.2, 0.15], dtype=np.float64)
    payload = {"Dw": w, "De": e, "p": p, "q": q, "written_rates": 0.7 * p, "reference_rates": 0.5 * q}
    costs = baseline_costs(payload)
    expected_f = np.abs(np.log(payload["written_rates"])[:, None] - np.log(payload["reference_rates"])[None, :])
    np.testing.assert_allclose(costs["F"], expected_f / expected_f.mean(), rtol=0, atol=0)
    # Direct row-sorted quantile checks, not np.quantile used a second time.
    sorted_rows = [np.sort(np.delete(row, i)) for i, row in enumerate(w)]
    expected_fingerprint = np.array([[row[0] * (1 - a) + row[1] * a for a in QUANTILES] for row in sorted_rows])
    np.testing.assert_allclose(fingerprints(w), expected_fingerprint, rtol=1e-14, atol=1e-14)
    fitted = fit_payload(payload)
    for model in MODELS:
        result = fitted["models"][model]
        assert len(result["restarts"]) == 3
        assert all(restart["steps"] == 200 for restart in result["restarts"])
        assert result["selected_seed"] == min(result["restarts"], key=lambda r: r["objective_after_step200"])["seed"]
        rows = np.array(result["normalized_rows"], dtype=np.float64)
        np.testing.assert_allclose(rows.sum(axis=1), np.ones(3), rtol=0, atol=1e-14)
        assert all(sorted(row) == list(range(4)) for row in result["ranking"])
        plan = p[:, None] * rows
        columns = plan.sum(axis=0)
        direct_column_kl = float(np.sum(columns * np.log(columns / q)))
        direct_joint_kl = float(np.sum(plan * np.log(plan / (p[:, None] * q[None, :]))))
        direct_data = _literal_gw_numpy(w, e, plan) if model == "G" else float(np.sum(costs[model] * plan))
        direct_objective = direct_data + direct_column_kl + 0.01 * direct_joint_kl
        np.testing.assert_allclose(result["selected_objective"], direct_objective, rtol=1e-12, atol=1e-12)
        winner = next(r for r in result["restarts"] if r["seed"] == result["selected_seed"])
        np.testing.assert_allclose(winner["components"]["data_cost"], direct_data, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(winner["components"]["column_kl"], direct_column_kl, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(winner["components"]["joint_kl"], direct_joint_kl, rtol=1e-12, atol=1e-12)
    flat = np.zeros((2, 3), dtype=np.float64)
    assert np.argsort(-flat, axis=1, kind="stable").tolist() == [[0, 1, 2], [0, 1, 2]]
    return {"status": "SYNTHETIC_FIXTURES_PASS", "real_payloads_read": False, "gw_literal": direct, "gw_efficient": float(efficient.detach()), "gw_gradient_max_error": float(np.max(np.abs(tensor_g.grad.numpy() - literal_gradient))), "fixture_objectives": {model: [r["objective_after_step200"] for r in fitted["models"][model]["restarts"]] for model in MODELS}, "fixture_selected_seeds": {model: fitted["models"][model]["selected_seed"] for model in MODELS}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="anonymous six-array .npz packet")
    parser.add_argument("--output", type=Path, help="numeric result JSON")
    parser.add_argument("--models", "--model", nargs="+", choices=MODELS, default=list(MODELS))
    parser.add_argument("--self-test", action="store_true", help="tiny synthetic arrays only")
    args = parser.parse_args(argv)
    if args.self_test:
        if args.input:
            parser.error("--self-test does not accept a real input")
        result = self_test()
    else:
        if not args.input or not args.output:
            parser.error("real numeric fitting requires --input and --output")
        try:
            with np.load(args.input, allow_pickle=False) as packet:
                result = fit_payload({key: packet[key] for key in packet.files}, args.models)
        except InvalidNumerics as error:
            result = {"schema_version": 1, "status": "INVALID_NUMERICS", "error": str(error)}
    serialized = json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    else:
        print(serialized, end="")
    return 0 if result["status"] != "INVALID_NUMERICS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
