#!/usr/bin/env python3
"""GPU-proposed, int8-exported and CPU-rescored neural hard-null for GDT001."""

from __future__ import annotations

import base64
import math
import random
import time
from typing import Any, Sequence

import numpy as np

from gdt001_core import SOURCE_ALPHABET, LatticeLine, PathObservation, fixed_costs, score_record, universal_uint_bits


def training_arrays(paths: Sequence[PathObservation]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xs: list[int] = []; ys: list[int] = []; resets: list[int] = []
    bos = len(SOURCE_ALPHABET)
    for path in paths:
        previous = bos
        first = True
        for token in path.source_ids:
            xs.append(previous); ys.append(token); resets.append(int(first))
            previous = token; first = False
    return np.asarray(xs, np.int64), np.asarray(ys, np.int64), np.asarray(resets, np.int64)


def quantize(tensor) -> tuple[np.ndarray, float]:
    values = tensor.detach().cpu().numpy().astype(np.float32)
    scale = max(float(np.max(np.abs(values))) / 127.0, 1e-9)
    return np.clip(np.rint(values / scale), -127, 127).astype(np.int8), scale


def numpy_logsumexp(values: np.ndarray) -> float:
    maximum = float(np.max(values))
    return maximum + math.log(float(np.exp(values - maximum).sum()))


def cpu_score(paths: Sequence[PathObservation], arrays: dict[str, np.ndarray], scales: dict[str, float]) -> float:
    def value(name: str) -> np.ndarray:
        return arrays[name].astype(np.float32) * scales[name]

    embedding = value("embedding")
    weight_ih = value("weight_ih")
    weight_hh = value("weight_hh")
    bias_ih = value("bias_ih")
    bias_hh = value("bias_hh")
    output_w = value("output_w")
    output_b = value("output_b")
    hidden_size = weight_hh.shape[1]
    bits = 0.0
    for path in paths:
        hidden = np.zeros(hidden_size, dtype=np.float32)
        previous = len(SOURCE_ALPHABET)
        for target in path.source_ids:
            gi = weight_ih @ embedding[previous] + bias_ih
            gh = weight_hh @ hidden + bias_hh
            ri, zi, ni = np.split(gi, 3); rh, zh, nh = np.split(gh, 3)
            reset = 1.0 / (1.0 + np.exp(-(ri + rh)))
            update = 1.0 / (1.0 + np.exp(-(zi + zh)))
            candidate = np.tanh(ni + reset * nh)
            hidden = (1.0 - update) * candidate + update * hidden
            logits = output_w @ hidden + output_b
            bits += (numpy_logsumexp(logits) - float(logits[target])) / math.log(2.0)
            previous = target
    return bits


def train_candidate(
    lines: Sequence[LatticeLine], seed: int = 71, hidden_size: int = 48,
    epochs: int = 80, learning_rate: float = 0.01,
) -> dict[str, Any]:
    import torch
    from torch import nn

    torch.manual_seed(seed); np.random.seed(seed); random.seed(seed)
    torch.use_deterministic_algorithms(True)
    vocab = len(SOURCE_ALPHABET) + 1
    output_size = len(SOURCE_ALPHABET)

    class Model(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embedding = nn.Embedding(vocab, hidden_size)
            self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
            self.output = nn.Linear(hidden_size, output_size)

        def forward(self, values):
            encoded = self.embedding(values)
            hidden, _ = self.gru(encoded)
            return self.output(hidden)

    selected = [line.paths[0] for line in lines]
    model = Model().cuda()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.0)
    # One line per batch item; zero padding is excluded from the loss.
    sequences = [list(path.source_ids) for path in selected if path.source_ids]
    batch_size = 256
    started = time.perf_counter()
    trace = []
    for epoch in range(epochs):
        order = np.random.default_rng(seed + epoch).permutation(len(sequences))
        total_loss = 0.0; total_tokens = 0
        for start in range(0, len(order), batch_size):
            batch = [sequences[index] for index in order[start:start + batch_size]]
            width = max(len(sequence) for sequence in batch)
            inputs = torch.full((len(batch), width), len(SOURCE_ALPHABET), dtype=torch.long, device="cuda")
            targets = torch.full((len(batch), width), -100, dtype=torch.long, device="cuda")
            for row, sequence in enumerate(batch):
                inputs[row, 1:len(sequence)] = torch.tensor(sequence[:-1], device="cuda")
                targets[row, :len(sequence)] = torch.tensor(sequence, device="cuda")
            optimizer.zero_grad(set_to_none=True)
            logits = model(inputs)
            loss = nn.functional.cross_entropy(logits.reshape(-1, output_size), targets.reshape(-1), ignore_index=-100, reduction="sum")
            loss.backward(); optimizer.step()
            total_loss += float(loss); total_tokens += sum(len(sequence) for sequence in batch)
        trace.append(total_loss / total_tokens / math.log(2.0))

    state = model.state_dict()
    tensors = {
        "embedding": state["embedding.weight"], "weight_ih": state["gru.weight_ih_l0"],
        "weight_hh": state["gru.weight_hh_l0"], "bias_ih": state["gru.bias_ih_l0"],
        "bias_hh": state["gru.bias_hh_l0"], "output_w": state["output.weight"],
        "output_b": state["output.bias"],
    }
    arrays: dict[str, np.ndarray] = {}; scales: dict[str, float] = {}
    exported = {}
    parameter_bits = 0.0
    for name, tensor in tensors.items():
        array, scale = quantize(tensor)
        arrays[name] = array; scales[name] = scale
        data = array.tobytes()
        exported[name] = {"shape": list(array.shape), "dtype": "int8", "scale_float32": scale, "base64": base64.b64encode(data).decode()}
        parameter_bits += 8.0 * array.size + 32.0 + universal_uint_bits(array.ndim) + sum(universal_uint_bits(n) for n in array.shape)
    source_bits = cpu_score(selected, arrays, scales)
    fixed = fixed_costs(selected)
    decoder = {
        "schema": "GDT001_QUANTIZED_GRU_NULL_V1", "alphabet": SOURCE_ALPHABET,
        "hidden_size": hidden_size, "line_reset": True, "quantization": "per-tensor symmetric int8",
        "tensors": exported, "cpu_reconstruction": "explicit NumPy GRU equations in gdt001_neural_null.py",
        "decoded_output": "source-symbol probability stream; no plaintext asserted",
    }
    return score_record(
        candidate_id=f"nonsemantic_neural_gru_h{hidden_size}_s{seed:04d}", model_class="NONSEMANTIC_GENERATOR",
        system=f"QUANTIZED_GRU_H{hidden_size}", seed=seed,
        config={"stage": 1, "hidden_size": hidden_size, "epochs": epochs, "learning_rate": learning_rate, "quantization": "int8"},
        paths=selected, key_bits=parameter_bits, latent_bits=0.0,
        reconstruction_bits=source_bits + sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    ) | {"gpu_training_seconds": time.perf_counter() - started, "training_bits_per_symbol_trace": trace, "cpu_quantized_source_bits": source_bits}
