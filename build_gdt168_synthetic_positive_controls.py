#!/usr/bin/env python3
"""Build two frozen synthetic architectures from one medieval medical corpus."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt159_diplomatic_corpora.json.gz"
PROVENANCE = ROOT / "gdt159_diplomatic_source_provenance.json"
METHOD = ROOT / "GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_METHOD.md"
BLIND = ROOT / "gdt168_blind_synthetic_corpora.json.gz"
TRUTH = ROOT / "gdt168_synthetic_ground_truth.json.gz"
CODEBOOK = ROOT / "gdt168_codebook_truth.tsv"
FREEZE = ROOT / "gdt168_source_encoder_freeze.json"

SOURCE_ID = "LATIN_MEDICAL_GRAPHEMATIC"
HOST_ALPHABET = "abcdefghijkmnprstuv"
COMPILER_ALPHABET = "loqwxyz"
REGISTERS = tuple(f"R{i}" for i in range(1, 6))
SCRIBES = ("S1", "S2")
RECORD_SIZE, LINE_SIZE = 18, 6


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    text = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def hid(text, size=16):
    return hashlib.sha256(text.encode()).hexdigest()[:size]


def base_code(number, width, alphabet=HOST_ALPHABET):
    out = []
    for _ in range(width):
        out.append(alphabet[number % len(alphabet)])
        number //= len(alphabet)
    assert number == 0
    return "".join(reversed(out))


def permutation(register, scribe, alphabet, layer):
    values = list(alphabet)
    rng = random.Random(int(hashlib.sha256(f"GDT168_RENDER_V1|{register}|{scribe}|{layer}".encode()).hexdigest()[:16], 16))
    rng.shuffle(values)
    return dict(zip(alphabet, values))


def render(text, mapping):
    return "".join(mapping[x] for x in text)


def write_gzip(path, payload):
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with Path(path).open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle:
            handle.write(raw)


def write_tsv(path, rows):
    fields = list(rows[0])
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    assert len(HOST_ALPHABET) == 19 and len(COMPILER_ALPHABET) == 7 and set(HOST_ALPHABET).isdisjoint(COMPILER_ALPHABET)
    with gzip.open(SOURCE, "rt", encoding="utf-8") as handle:
        rows = [x for x in json.load(handle)["records"] if x["corpus_id"] == SOURCE_ID]
    assert len(rows) == 12000
    freq = Counter(x["form"] for x in rows)
    concepts = sorted(freq, key=lambda x: (-freq[x], hid(x, 64)))
    assert len(concepts) == 6175 and len(concepts) <= 4 * 4 * 4 * 100
    concept_index = {form: i for i, form in enumerate(concepts)}
    canonical_a = {}
    for i, form in enumerate(concepts):
        canonical_a[form] = base_code(i, 2) if i < len(HOST_ALPHABET) ** 2 else base_code(i, 3)

    ordered = defaultdict(list)
    for row in rows:
        ordered[row["unit_id"]].append(row)
    occurrences = []
    for unit in sorted(ordered):
        values = sorted(ordered[unit], key=lambda x: (int(x["occurrence_index"]), x["fold_id"], x["form"]))
        unit_tag = "U" + hid(unit, 12)
        for offset in range(0, len(values), RECORD_SIZE):
            record = values[offset:offset + RECORD_SIZE]
            record_id = f"{unit_tag}:R{offset // RECORD_SIZE:04d}"
            for slot, row in enumerate(record):
                occurrences.append({**row, "unit_tag": unit_tag, "record_id": record_id, "slot": slot,
                                    "line_index": slot // LINE_SIZE, "position_in_line": slot % LINE_SIZE,
                                    "record_length": len(record)})

    blind_rows, truth_rows = [], []
    for system in ("SYSTEM_A", "SYSTEM_B"):
        for register in REGISTERS:
            for scribe in SCRIBES:
                hm = permutation(register, scribe, HOST_ALPHABET, "HOST")
                cm = permutation(register, scribe, COMPILER_ALPHABET, "COMPILER")
                renderer = f"{register}_{scribe}"
                for occurrence_ordinal, row in enumerate(occurrences):
                    form, slot = row["form"], row["slot"]
                    concept = concept_index[form]
                    line_start = row["position_in_line"] == 0
                    line_end = row["position_in_line"] == LINE_SIZE - 1 or slot == row["record_length"] - 1
                    record_end = slot == row["record_length"] - 1
                    if system == "SYSTEM_A":
                        canonical_host = canonical_a[form]
                        wrapper_digit = (row["line_index"] + (0 if line_start else 1)) % 4
                        right_digit = row["position_in_line"] % 4
                        closure_digit = 0
                    else:
                        mixed = (concept + 137 * slot) % len(concepts)
                        host_digit = mixed % 100
                        wrapper_digit = (mixed // 100) % 4
                        right_digit = (mixed // 400) % 4
                        closure_digit = (mixed // 1600) % 4
                        canonical_host = base_code(host_digit, 2)
                    wrapper_raw = COMPILER_ALPHABET[wrapper_digit]
                    frame_raw = COMPILER_ALPHABET[4] if line_start else ""
                    right_raw = COMPILER_ALPHABET[right_digit]
                    closure_value_raw = COMPILER_ALPHABET[closure_digit] if system == "SYSTEM_B" else ""
                    dy_raw = COMPILER_ALPHABET[5] if line_end and not record_end else ""
                    b3_raw = COMPILER_ALPHABET[6] if record_end else ""
                    host = render(canonical_host, hm)
                    wrapper, frame, right = render(wrapper_raw, cm), render(frame_raw, cm), render(right_raw, cm)
                    closure_value = render(closure_value_raw, cm)
                    dy, b3 = render(dy_raw, cm), render(b3_raw, cm)
                    surface = wrapper + frame + host + right + closure_value + dy + b3
                    blind_id = "B" + hid(f"{system}|{renderer}|{row['record_id']}|{slot}|{occurrence_ordinal}", 20)
                    common = {
                        "blind_id": blind_id, "corpus_view": "CONTROL_X" if system == "SYSTEM_A" else "CONTROL_Y",
                        "renderer": renderer, "register": register, "scribe": scribe,
                        "source_unit_id": row["unit_tag"], "record_id": row["record_id"],
                        "line_id": f"{row['record_id']}:L{row['line_index']:02d}", "fold_id": row["fold_id"],
                        "slot": slot, "line_index": row["line_index"], "position_in_line": row["position_in_line"],
                        "record_length": row["record_length"], "surface": surface, "page_host": host,
                        "wrapper": wrapper, "local_frame": frame, "right_family": right,
                        "closure_value": closure_value, "dy_closure": int(bool(dy)), "b3": int(bool(b3)),
                    }
                    blind_rows.append(common)
                    truth_rows.append({"blind_id": blind_id, "system": system, "source_unit_full": row["unit_id"],
                                       "plaintext_form": form, "concept_index": concept, "slot": slot,
                                       "canonical_a_code": canonical_a[form], "canonical_host": canonical_host,
                                       "wrapper_digit": wrapper_digit, "right_digit": right_digit,
                                       "closure_digit": closure_digit})

    codebook_rows = []
    for form in concepts:
        concept = concept_index[form]
        codebook_rows.append({"concept_index": concept, "plaintext_form": form, "source_frequency": freq[form],
                              "system_a_canonical_code": canonical_a[form],
                              "system_b_host_digit_at_slot0": concept % 100,
                              "system_b_wrapper_digit_at_slot0": (concept // 100) % 4,
                              "system_b_right_digit_at_slot0": (concept // 400) % 4,
                              "system_b_closure_digit_at_slot0": (concept // 1600) % 4})
    write_tsv(CODEBOOK, codebook_rows)
    write_gzip(BLIND, {"schema": "GDT168_BLIND_SYNTHETIC_CORPORA_V1", "rows": blind_rows})
    write_gzip(TRUTH, {"schema": "GDT168_SYNTHETIC_GROUND_TRUTH_V1", "rows": truth_rows})
    freeze = {
        "schema": "GDT168_SOURCE_ENCODER_FREEZE_V1", "status": "FROZEN_BEFORE_BLIND_DIAGNOSTIC_SCORING",
        "source": {"corpus_id": SOURCE_ID, "rows": len(rows), "concept_types": len(concepts),
                   "source_units": len(ordered), "gdt159_diplomatic_corpora_sha256": sha(SOURCE),
                   "gdt159_diplomatic_source_provenance_sha256": sha(PROVENANCE)},
        "layout": {"record_size": RECORD_SIZE, "line_size": LINE_SIZE, "records": len({x['record_id'] for x in occurrences}),
                   "registers": list(REGISTERS), "scribes": list(SCRIBES), "aligned_renderers": 10},
        "renderer_keys": {
            f"{register}_{scribe}": {
                "host": permutation(register, scribe, HOST_ALPHABET, "HOST"),
                "compiler": permutation(register, scribe, COMPILER_ALPHABET, "COMPILER"),
            }
            for register in REGISTERS for scribe in SCRIBES
        },
        "encoder_a": {"architecture": "FIXED_INJECTIVE_2_3_CHARACTER_CONCEPT_CODEBOOK",
                      "two_character_codes": len(HOST_ALPHABET) ** 2, "three_character_codes": len(concepts) - len(HOST_ALPHABET) ** 2,
                      "concept_bits_outside_host": 0},
        "encoder_b": {"architecture": "SLOT_WRAPPER_HOST_RIGHT_CLOSURE_DISTRIBUTED_MIXED_RADIX",
                      "host_values": 100, "wrapper_values": 4, "right_values": 4, "closure_values": 4,
                      "joint_capacity": 6400, "slot_rotation": 137, "host_independently_lexical": False},
        "no_voynich_tuning": True,
        "inputs": {SOURCE.name: sha(SOURCE), PROVENANCE.name: sha(PROVENANCE)},
        "documents": {METHOD.name: sha(METHOD)}, "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {BLIND.name: sha(BLIND), TRUTH.name: sha(TRUTH), CODEBOOK.name: sha(CODEBOOK)},
        "commitments": {"blind_content_sha256": csha(blind_rows), "truth_content_sha256": csha(truth_rows),
                        "codebook_content_sha256": csha(codebook_rows)},
        "counts": {"source_occurrences": len(occurrences), "blind_rows": len(blind_rows), "truth_rows": len(truth_rows)},
        "f84r": {"voynich_inputs": 0, "opened": False, "queried": False, "retained": False, "scored": False},
        "claim_ceiling": "Synthetic instrument calibration only; no Voynich word, code value, language, meaning, plaintext, or translation.",
    }
    freeze["freeze_content_sha256"] = csha(freeze)
    FREEZE.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], "concepts": len(concepts), "blind_rows": len(blind_rows),
                      "records": freeze["layout"]["records"]}, sort_keys=True))


if __name__ == "__main__":
    main()
