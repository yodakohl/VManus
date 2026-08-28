#!/usr/bin/env python3
from __future__ import annotations

import os

import csv
import hashlib
import json
import math
import random
import shutil
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path(os.environ.get("GDT612_WORK", Path(__file__).resolve().parent)).resolve()
REPO = Path(os.environ.get("VMANUS_REPO_ROOT", Path.cwd())).resolve()
G605 = REPO / "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts"
G606 = REPO / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"
G608 = REPO / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts"
REF = WORK / "references"
OUT = WORK / "prepared"
PACKS = OUT / "packs"
ACTIVE = "abcdefghilmnopqrstuvxyz"

EXPECTED = {
    G605 / "gdt605_bpe_merges.tsv": "4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539",
    G606 / "guarded_rows.tsv": "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9",
    G606 / "unit_sequences.json": "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf",
    G608 / "merge_tree.tsv": "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a",
}
REFERENCE_HASHES = {
    "caesar_la.txt": "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
    "divina_commedia.txt": "aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e",
    "mhg/Erec-conll.txt": "367cc2e9d0b60aadee501c187864dea97c77af41303f216986cfa35575f43675",
    "mhg/Iwein-conll.txt": "5b43f962da24d5b438ff93f64f30036087fe37d1cd5863c0bd29e764957b6a6f",
    "mhg/Parzival-conll.txt": "9d7ef5fd1842f6197121b654eb3c57a307ff01a9698768e27be069732afdf5cf",
    "mhg/Rolandslied-conll.txt": "46b078128c6932759d56a6a4bf13f9c3bf84d88f7a8d0e35fca31670cc0191fa",
    "mhg/Willehalm-conll.txt": "abee7d5d1aee54fa944e0d311d4645455503d4fc0bbd9ef919c46a9cfd10e7fe",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_word(word: str) -> str:
    value = word.lower().replace("æ", "ae").replace("œ", "oe").replace("ß", "ss")
    value = "".join(
        char for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    value = value.replace("j", "i").replace("k", "c").replace("w", "uu")
    return "".join(char for char in value if char in ACTIVE)


def words_from_text(text: str):
    words, buffer = [], []
    for char in text:
        if char.isalpha() or char in "æœß":
            buffer.append(char)
        elif buffer:
            value = normalize_word("".join(buffer))
            if value:
                words.append(value)
            buffer = []
    if buffer:
        value = normalize_word("".join(buffer))
        if value:
            words.append(value)
    return words


def reference_words():
    for relative, expected in REFERENCE_HASHES.items():
        path = REF / relative
        if sha(path) != expected:
            raise RuntimeError(f"reference drift: {relative}")
    caesar = (REF / "caesar_la.txt").read_text(encoding="utf-8", errors="replace")
    start = caesar.find("GALLIA est omnis")
    if start >= 0:
        caesar = caesar[start:]
    footer = "*** END OF THE PROJECT GUTENBERG"
    if footer in caesar:
        caesar = caesar[:caesar.find(footer)]
    italian = (REF / "divina_commedia.txt").read_text(encoding="utf-8", errors="replace")
    mhg = []
    for relative in sorted(REFERENCE_HASHES):
        if not relative.startswith("mhg/"):
            continue
        for line in (REF / relative).read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                token = normalize_word(line.split("\t", 1)[0])
                if token:
                    mhg.append(token)
    return {
        "latin": words_from_text(caesar),
        "old_italian": words_from_text(italian),
        "middle_high_german": mhg,
    }


def fixed_prefix(words, character_limit=240_000):
    selected, chars = [], 0
    for word in words:
        if chars >= character_limit:
            break
        selected.append(word)
        chars += len(word) + 1
    return selected


def destroy_words(words, language):
    output = []
    for index, word in enumerate(words):
        seed = int(hashlib.sha256(f"historical34-order-null|{language}|{index}".encode()).hexdigest()[:16], 16)
        chars = list(word)
        random.Random(seed).shuffle(chars)
        output.append("".join(chars))
    return output


def ranked_affixes(counter, side, limit=256):
    tables = {length: Counter() for length in (1, 2, 3)}
    for word, count in counter.items():
        for length in tables:
            if len(word) >= length:
                value = word[:length] if side == "prefix" else word[-length:]
                tables[length][value] += count
    ordered = {
        length: [value for value, _count in sorted(table.items(), key=lambda item: (-item[1], item[0]))]
        for length, table in tables.items()
    }
    result = []
    for index in range(limit):
        for length in (2, 3, 1):
            if index < len(ordered[length]) and ordered[length][index] not in result:
                result.append(ordered[length][index])
                if len(result) >= limit:
                    return result
    return result


def ranked_ngrams(counter, lengths=(2, 3), limit=256):
    tables = {length: Counter() for length in lengths}
    for word, count in counter.items():
        for length in lengths:
            for index in range(len(word) - length + 1):
                tables[length][word[index:index + length]] += count
    ordered = {
        length: [value for value, _count in sorted(table.items(), key=lambda item: (-item[1], item[0]))]
        for length, table in tables.items()
    }
    result = []
    for index in range(limit * 2):
        for length in lengths:
            if index < len(ordered[length]) and ordered[length][index] not in result:
                result.append(ordered[length][index])
                if len(result) >= limit:
                    return result
    return result


def make_candidates(words):
    counter = Counter(words)
    whole = [
        word for word, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        if 2 <= len(word) <= 8 and count >= 2
    ][:512]
    connectors = [
        word for word, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        if 1 <= len(word) <= 3 and count >= 2
    ][:256]
    ngrams = ranked_ngrams(counter, (2, 3), 384)
    context = ranked_ngrams(counter, (1, 2, 3), 384)
    return {
        "literal": list(ACTIVE),
        "syllabic": ngrams,
        "prefix": ranked_affixes(counter, "prefix", 384),
        "suffix": ranked_affixes(counter, "suffix", 384),
        "connector": connectors,
        "context": context,
        "whole": whole,
        "override_short": context,
        "override_whole": whole,
    }


def make_packs():
    meta = {}
    for language, all_words in reference_words().items():
        real = fixed_prefix(all_words)
        destroyed = destroy_words(real, language)
        meta[language] = {}
        for kind, words in (("real", real), ("destroyed", destroyed)):
            words_path = PACKS / f"{language}_{kind}_words.txt"
            words_path.write_text("\n".join(words) + "\n", encoding="ascii")
            candidates = make_candidates(words)
            rows = []
            for category in (
                "literal", "syllabic", "prefix", "suffix", "connector",
                "context", "whole", "override_short", "override_whole",
            ):
                rows.extend(
                    {"category": category, "rank": rank, "value": value}
                    for rank, value in enumerate(candidates[category], 1)
                )
            candidate_path = PACKS / f"{language}_{kind}_candidates.tsv"
            write_tsv(candidate_path, ["category", "rank", "value"], rows)
            meta[language][kind] = {
                "words": len(words),
                "characters": sum(map(len, words)),
                "words_sha256": sha(words_path),
                "candidates_sha256": sha(candidate_path),
                "candidate_counts": {key: len(value) for key, value in candidates.items()},
            }
    (OUT / "reference_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PACKS.mkdir(parents=True, exist_ok=True)
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise RuntimeError(f"input drift: {path}")

    guarded = read_tsv(G606 / "guarded_rows.tsv")
    if any(row["page"].lower().startswith("f84") or row["physical_folio"].lower().startswith("f84") for row in guarded):
        raise RuntimeError("sealed selector in published stream")
    data = json.loads((G606 / "unit_sequences.json").read_text())
    inventory = data["inventory"]
    merge_rows = read_tsv(G605 / "gdt605_bpe_merges.tsv")
    rule = {row["merged"]: (row["left"], row["right"]) for row in merge_rows}
    primitives = sorted(set(inventory) - set(rule))
    if len(inventory) != 98 or len(rule) != 64 or len(primitives) != 34:
        raise RuntimeError("capacity mismatch")

    def leaves(unit):
        if unit not in rule:
            return [unit]
        left, right = rule[unit]
        return leaves(left) + leaves(right)

    train = data["sequences"]["train"]
    held = data["sequences"]["held"]
    direct_n = Counter()
    direct_initial = Counter()
    direct_final = Counter()
    leaf_n = Counter()
    total_leaves = 0
    for record in train:
        units = record["units"]
        for index, unit in enumerate(units):
            direct_n[unit] += 1
            direct_initial[unit] += index == 0
            direct_final[unit] += index + 1 == len(units)
            for primitive in leaves(unit):
                leaf_n[primitive] += 1
                total_leaves += 1

    primitive_rows = []
    for pid, primitive in enumerate(primitives):
        primitive_rows.append({
            "primitive_id": pid,
            "primitive": primitive,
            "direct_train_n": direct_n[primitive],
            "direct_chunk_initial_rate": direct_initial[primitive] / direct_n[primitive] if direct_n[primitive] else 0.0,
            "direct_chunk_final_rate": direct_final[primitive] / direct_n[primitive] if direct_n[primitive] else 0.0,
            "leaf_train_occurrences": leaf_n[primitive],
            "leaf_train_fraction": leaf_n[primitive] / total_leaves,
        })
    write_tsv(
        OUT / "primitives.tsv",
        ["primitive_id", "primitive", "direct_train_n", "direct_chunk_initial_rate", "direct_chunk_final_rate", "leaf_train_occurrences", "leaf_train_fraction"],
        primitive_rows,
    )

    unit_id = {unit: index for index, unit in enumerate(inventory)}
    primitive_id = {unit: index for index, unit in enumerate(primitives)}
    unit_rows = []
    for unit in inventory:
        unit_rows.append({
            "unit_id": unit_id[unit],
            "unit": unit,
            "is_primitive": int(unit in primitive_id),
            "primitive_id": primitive_id.get(unit, -1),
            "left_unit_id": unit_id[rule[unit][0]] if unit in rule else -1,
            "right_unit_id": unit_id[rule[unit][1]] if unit in rule else -1,
            "merge_rank": next((int(row["rank"]) for row in merge_rows if row["merged"] == unit), -1),
            "leaves": ",".join(leaves(unit)),
        })
    write_tsv(
        OUT / "units.tsv",
        ["unit_id", "unit", "is_primitive", "primitive_id", "left_unit_id", "right_unit_id", "merge_rank", "leaves"],
        unit_rows,
    )

    chunk_counts = Counter(tuple(record["units"]) for record in train)
    train_rows = []
    for chunk_id, (units, count) in enumerate(sorted(chunk_counts.items(), key=lambda item: (-item[1], item[0]))):
        train_rows.append({
            "chunk_id": chunk_id,
            "count": count,
            "weight": f"{math.sqrt(count):.12f}",
            "units": ",".join(str(unit_id[unit]) for unit in units),
            "unit_names": " ".join(units),
        })
    write_tsv(OUT / "train_chunks.tsv", ["chunk_id", "count", "weight", "units", "unit_names"], train_rows)

    held_rows = []
    for record_id, record in enumerate(held):
        held_rows.append({
            "record_id": record_id,
            "page": record["page"],
            "physical_folio": record["physical_folio"],
            "locus": record["locus"],
            "chunk_index": record["chunk_index"],
            "section": record["section"],
            "units": ",".join(str(unit_id[unit]) for unit in record["units"]),
            "unit_names": " ".join(record["units"]),
        })
    write_tsv(
        OUT / "held_chunks.tsv",
        ["record_id", "page", "physical_folio", "locus", "chunk_index", "section", "units", "unit_names"],
        held_rows,
    )

    page_active = {}
    page_counter = Counter()
    paragraph_loci = defaultdict(list)
    line_meta = {}
    for row in guarded:
        page, raw = row["page"], row["ivtff_raw"]
        starts = "<%>" in raw[:32]
        ends = "<$>" in raw
        if starts or page not in page_active:
            page_counter[page] += 1
            page_active[page] = f"{page}:p{page_counter[page]}"
        paragraph_id = page_active[page]
        paragraph_loci[paragraph_id].append(row["locus"])
        line_meta[row["locus"]] = {**row, "paragraph_id": paragraph_id}
        if ends:
            page_active.pop(page, None)
    line_rows = []
    for paragraph_id, loci in paragraph_loci.items():
        for index, locus in enumerate(loci):
            row = line_meta[locus]
            if row["split"] != "held":
                continue
            line_rows.append({
                "paragraph_id": paragraph_id,
                "paragraph_line_index": index,
                "paragraph_line_count": len(loci),
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": locus,
                "line_number": row["line_number"],
                "section": row["section"],
                "hand": row["hand"],
                "currier": row["language"],
            })
    write_tsv(
        OUT / "held_lines.tsv",
        ["paragraph_id", "paragraph_line_index", "paragraph_line_count", "page", "physical_folio", "locus", "line_number", "section", "hand", "currier"],
        line_rows,
    )

    make_packs()
    model_source = REPO / "experiments/yolo/gdt609_historical_mixed_abbreviation_prior/artifacts/model_v1.json"
    shutil.copyfile(model_source, OUT / "model_v1.json")
    manifest = {
        "schema": "historical34-e2e-prepared-v1",
        "input_hashes": {str(path.relative_to(REPO)): sha(path) for path in EXPECTED},
        "reference_hashes": REFERENCE_HASHES,
        "model_sha256": sha(OUT / "model_v1.json"),
        "counts": {
            "primitives": len(primitives),
            "merges": len(rule),
            "units": len(inventory),
            "train_chunks": len(train),
            "train_chunk_types": len(train_rows),
            "held_chunks": len(held),
            "held_folios": len({record["physical_folio"] for record in held}),
            "held_paragraphs": len({row["paragraph_id"] for row in line_rows}),
        },
        "fit_contract": "Only train_chunks.tsv and reference packs may enter optimization; held files are evaluation-only.",
        "sealed_selectors": "FORBIDDEN_AND_ABSENT",
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
