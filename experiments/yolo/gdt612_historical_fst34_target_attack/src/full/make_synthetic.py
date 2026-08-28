#!/usr/bin/env python3
from __future__ import annotations

import os

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path(os.environ.get("GDT612_WORK", Path(__file__).resolve().parent)).resolve()
PREP = WORK / "prepared"
OUT = WORK / "synthetic"
ROLE_COUNTS = {
    "literal_carrier": 18,
    "syllabic_carrier": 4,
    "prefix_operator": 3,
    "suffix_operator": 3,
    "connector": 2,
    "context_abbreviation_mark": 2,
    "wholeform_logogram": 1,
    "null_layout": 1,
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    primitives = read_tsv(PREP / "primitives.tsv")
    units = read_tsv(PREP / "units.tsv")
    candidates = defaultdict(list)
    for row in read_tsv(PREP / "packs/latin_real_candidates.tsv"):
        candidates[row["category"]].append(row["value"])
    words = (PREP / "packs/latin_real_words.txt").read_text(encoding="ascii").splitlines()
    frequency = Counter("".join(words))
    common_letters = [x for x, _ in sorted(frequency.items(), key=lambda x: (-x[1], x[0]))[:18]]

    # Fixed, public generation seed. The role partition is deliberately unrelated
    # to target statistics; only the original <=3% null eligibility gate is used.
    eligible_null = [r for r in primitives if float(r["leaf_train_fraction"]) <= .03]
    null_pid = int(sorted(eligible_null, key=lambda r: (float(r["leaf_train_fraction"]), r["primitive"]))[0]["primitive_id"])
    remaining = [int(r["primitive_id"]) for r in primitives if int(r["primitive_id"]) != null_pid]
    random.Random(340608).shuffle(remaining)
    role_order = []
    for role in (
        "literal_carrier", "syllabic_carrier", "prefix_operator", "suffix_operator",
        "connector", "context_abbreviation_mark", "wholeform_logogram",
    ):
        role_order.extend([role] * ROLE_COUNTS[role])
    truth = {null_pid: ("null_layout", "")}
    pools = {
        "literal_carrier": common_letters,
        "syllabic_carrier": candidates["syllabic"][:4],
        "prefix_operator": candidates["prefix"][:3],
        "suffix_operator": candidates["suffix"][:3],
        "connector": candidates["connector"][:2],
        "context_abbreviation_mark": candidates["context"][:2],
        "wholeform_logogram": candidates["whole"][:1],
    }
    cursor = Counter()
    for pid, role in zip(remaining, role_order):
        truth[pid] = (role, pools[role][cursor[role]])
        cursor[role] += 1

    unit_by_id = {int(r["unit_id"]): r for r in units}
    primitive_uid = {int(r["primitive_id"]): int(r["unit_id"]) for r in units if r["is_primitive"] == "1"}
    merges = [r for r in units if r["is_primitive"] == "0"]
    # Eight exact exceptions: four short components and four wholeforms.
    chosen_merges = sorted(
        (r for r in merges if r["unit"] != "qok"),
        key=lambda r: (int(r["merge_rank"]), int(r["unit_id"])),
    )[:8]
    overrides = {}
    short_values = candidates["override_short"][5:9]
    whole_values = candidates["override_whole"][5:9]
    for i, row in enumerate(chosen_merges):
        uid = int(row["unit_id"])
        if i < 4:
            overrides[uid] = ("short", short_values[i])
        else:
            overrides[uid] = ("wholeform", whole_values[i - 4])

    # Build plaintext emissions. Short overrides act like syllabic cores; whole
    # carriers and connectors delimit a word exactly as the decoder does.
    core_items = []
    prefix_items, suffix_items, context_items, whole_items = [], [], [], []
    for pid, (role, output) in truth.items():
        uid = primitive_uid[pid]
        item = (output, uid, role)
        if role in ("literal_carrier", "syllabic_carrier"):
            core_items.append(item)
        elif role == "prefix_operator":
            prefix_items.append(item)
        elif role == "suffix_operator":
            suffix_items.append(item)
        elif role == "context_abbreviation_mark":
            context_items.append(item)
        elif role in ("connector", "wholeform_logogram"):
            whole_items.append(item)
    for uid, (kind, output) in overrides.items():
        (whole_items if kind == "wholeform" else core_items).append((output, uid, kind))
    exact_whole = {text: uid for text, uid, _ in whole_items}

    def core_dp(text):
        best = [None] * (len(text) + 1)
        best[0] = []
        # Prefer multi-character/exact items but make the result deterministic.
        items = sorted(core_items, key=lambda item: (-len(item[0]), item[1]))
        for pos in range(len(text)):
            if best[pos] is None:
                continue
            for output, uid, _role in items:
                if text.startswith(output, pos):
                    candidate = best[pos] + [uid]
                    end = pos + len(output)
                    if best[end] is None or len(candidate) < len(best[end]) or (len(candidate) == len(best[end]) and candidate < best[end]):
                        best[end] = candidate
        return best[-1]

    def encode_word(word):
        if word in exact_whole:
            return [exact_whole[word]]
        choices = []
        pref = [("", None)] + [(x[0], x[1]) for x in prefix_items if word.startswith(x[0])]
        suff = [("", None)] + [(x[0], x[1]) for x in suffix_items if word.endswith(x[0])]
        for ptext, puid in pref:
            for stext, suid in suff:
                if len(ptext) + len(stext) >= len(word):
                    continue
                middle = word[len(ptext):len(word) - len(stext) if stext else len(word)]
                encoded = core_dp(middle)
                if encoded is not None:
                    seq = ([] if puid is None else [puid]) + encoded + ([] if suid is None else [suid])
                    # Prefer structural use when token count is tied.
                    structural = int(puid is not None) + int(suid is not None)
                    choices.append((len(seq), -structural, seq))
        if not choices:
            return None
        return min(choices)[2]

    encoded = []
    for index, word in enumerate(words[:80000]):
        seq = encode_word(word)
        if seq:
            # Exercise the null without exceeding 3% of source events.
            if index % 97 == 0:
                insert = (index // 97) % (len(seq) + 1)
                seq = seq[:insert] + [primitive_uid[null_pid]] + seq[insert:]
            encoded.append((word, seq))
    if len(encoded) < 10000:
        raise RuntimeError("synthetic coverage unexpectedly low")

    # Add deterministic examples containing each context mark adjacent to a core.
    for output, uid, _ in context_items:
        for word, seq in list(encoded):
            where = word.find(output)
            if where > 0:
                left = core_dp(word[:where])
                right = core_dp(word[where + len(output):])
                if left and right:
                    encoded.extend([(word, left + [uid] + right)] * 60)
                    break

    split = min(50000, int(len(encoded) * .8))
    train_events = encoded[:split]
    held_events = encoded[split:min(len(encoded), split + 10000)]

    counts = Counter(tuple(seq) for _word, seq in train_events)
    train_rows = []
    for chunk_id, (seq, count) in enumerate(sorted(counts.items(), key=lambda x: (-x[1], x[0]))):
        train_rows.append({
            "chunk_id": chunk_id,
            "count": count,
            "weight": f"{math.sqrt(count):.12f}",
            "units": ",".join(map(str, seq)),
            "unit_names": " ".join(unit_by_id[x]["unit"] for x in seq),
        })
    write_tsv(OUT / "train_chunks.tsv", ["chunk_id", "count", "weight", "units", "unit_names"], train_rows)
    write_tsv(OUT / "held.tsv", ["record_id", "plaintext", "units", "unit_names"], [
        {
            "record_id": i,
            "plaintext": word,
            "units": ",".join(map(str, seq)),
            "unit_names": " ".join(unit_by_id[x]["unit"] for x in seq),
        }
        for i, (word, seq) in enumerate(held_events)
    ])
    write_tsv(OUT / "truth_primitives.tsv", ["primitive_id", "primitive", "role", "output"], [
        {
            "primitive_id": pid,
            "primitive": primitives[pid]["primitive"],
            "role": truth[pid][0],
            "output": truth[pid][1] or "<EMPTY>",
        }
        for pid in range(34)
    ])
    write_tsv(OUT / "truth_overrides.tsv", ["unit_id", "unit", "type", "output"], [
        {"unit_id": uid, "unit": unit_by_id[uid]["unit"], "type": kind, "output": output}
        for uid, (kind, output) in sorted(overrides.items())
    ])
    manifest = {
        "schema": "historical34-synthetic-v1",
        "seed": 340608,
        "role_counts": ROLE_COUNTS,
        "override_count": len(overrides),
        "wholeform_override_count": sum(kind == "wholeform" for kind, _ in overrides.values()),
        "train_events": len(train_events),
        "train_types": len(train_rows),
        "held_events": len(held_events),
        "encodable_word_fraction": len(encoded) / min(80000, len(words)),
        "source_hashes": {
            "primitives.tsv": sha(PREP / "primitives.tsv"),
            "units.tsv": sha(PREP / "units.tsv"),
            "latin_real_candidates.tsv": sha(PREP / "packs/latin_real_candidates.tsv"),
        },
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
