#!/usr/bin/env python3
"""Freeze a period-matched CoReMA semantic-role calibration panel.

This program has no Voynich inputs.  It downloads the public CoReMA recipe
index and six collection-level annotated-detail TEI files, verifies their
audited byte hashes, and exports only structural/semantic annotation metadata.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

INDEX = {
    "url": "https://gams.uni-graz.at/archive/objects/query:corema.recipeindex/datastreams/RESULT/content",
    "name": "corema_recipe_index.json",
    "size": 4284376,
    "sha256": "b95fbb39fb939bc96e741e19f946eafba0efb5a645583b3704e8cfc4c8ba41ac",
}

# Frozen after a source-only audit.  Selection did not inspect any Voynich row:
# normalized manuscript date wholly inside 1350--1500, >=30 index records,
# collection-level annotated-detail TEI available, >=30 recipe elements, and
# >=30 explicit CoReMA <instruction> elements.
SOURCES = (
    ("b4", 433533, "59bf0cf97fc21623a7683cc8059a150644bff313488939222fd200969b7b0afd"),
    ("b6", 63668, "d475072e62701bea6b058729b5f4b988e0eb93fe00878d2831f62e431573e3dd"),
    ("br1", 94541, "8f142085e1a67c1e854992b1f35a3e8afa9476407789e8029b95bfe639b639ba"),
    ("bs1", 511977, "d4fc0b986404cb423b99137678a879d3df94b15602740dbfb1fd56b25bc74eb6"),
    ("gr1", 559924, "41c603f445a15bcb914eb0d090c80754ad1747821b7556dd77e31c1273a12ff5"),
    ("w1", 421396, "a56639c7e8795a2afe76aa7cd950a8a68ade7231e1e68170034bc30002ab48e6"),
)

NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
ROLE_TAGS = (
    "title", "opener", "instruction", "ingredient", "tool", "dish", "name",
    "closer", "kitchenTip", "householdTip", "servingTip", "time", "dietetics",
    "alternative", "ref", "unclear",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fetch(url: str, path: Path, size: int, expected: str) -> bytes:
    if path.exists():
        data = path.read_bytes()
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "VManus-GDT176-source-freeze/1"})
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read()
        path.write_bytes(data)
    if len(data) != size or sha256_bytes(data) != expected:
        raise RuntimeError(f"source drift for {path.name}: {len(data)} {sha256_bytes(data)}")
    return data


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def word_count(element: ET.Element) -> int:
    return len(" ".join(element.itertext()).split())


def first_english_date(root: ET.Element) -> str:
    for date in root.findall(".//t:origDate/t:date", NS):
        if date.get("{http://www.w3.org/XML/1998/namespace}lang") == "en":
            return " ".join(date.itertext()).strip()
    return ""


def recipe_rows(collection: str, root: ET.Element) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    summaries: list[dict[str, object]] = []
    roles: list[dict[str, object]] = []
    recipes = root.findall('.//*[@type="recipe"]', NS)
    for recipe_ordinal, recipe in enumerate(recipes, 1):
        recipe_id = recipe.get(XML_ID, f"{collection}.ordinal{recipe_ordinal}")
        instruction_map = {id(node): i for i, node in enumerate(recipe.findall(".//t:instruction", NS), 1)}
        parent = {id(child): node for node in recipe.iter() for child in node}
        role_nodes = [node for node in recipe.iter() if local_name(node.tag) in ROLE_TAGS]
        role_counts = {role: 0 for role in ROLE_TAGS}
        for element_ordinal, node in enumerate(role_nodes, 1):
            role = local_name(node.tag)
            role_counts[role] += 1
            ancestor = parent.get(id(node))
            while ancestor is not None and local_name(ancestor.tag) != "instruction":
                ancestor = parent.get(id(ancestor))
            parent_instruction = instruction_map.get(id(ancestor), 0) if ancestor is not None else 0
            roles.append({
                "collection_id": collection,
                "recipe_id": recipe_id,
                "recipe_ordinal": recipe_ordinal,
                "element_ordinal": element_ordinal,
                "role": role.upper(),
                "parent_instruction_ordinal": parent_instruction,
                "token_count": word_count(node),
                "relative_element_position": f"{element_ordinal / max(1, len(role_nodes)):.9f}",
                "concept_id": node.get("commodity") or "NONE",
                "editor_english_label": node.get("en") or node.get("key") or "NONE",
                "annotation_flags": node.get("ana") or "NONE",
            })
        summaries.append({
            "collection_id": collection,
            "recipe_id": recipe_id,
            "recipe_ordinal": recipe_ordinal,
            "source_token_count": word_count(recipe),
            **{f"{role}_count": role_counts[role] for role in ROLE_TAGS},
        })
    return summaries, roles


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def content_hash(obj: dict[str, object]) -> str:
    clean = dict(obj)
    clean.pop("content_hash", None)
    return sha256_bytes(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=Path(".gdt176/corema"))
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    index_data = fetch(INDEX["url"], args.cache_dir / INDEX["name"], INDEX["size"], INDEX["sha256"])
    index_rows = json.loads(index_data)
    manifest: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    roles: list[dict[str, object]] = []

    for collection, size, expected in SOURCES:
        url = f"https://gams.uni-graz.at/o:corema.{collection}.recipes/TEI_SOURCE"
        data = fetch(url, args.cache_dir / f"{collection}.recipes.xml", size, expected)
        root = ET.fromstring(data)
        collection_summaries, collection_roles = recipe_rows(collection, root)
        summaries.extend(collection_summaries)
        roles.extend(collection_roles)
        counts = {tag: len(root.findall(f".//t:{tag}", NS)) for tag in ROLE_TAGS}
        manifest.append({
            "collection_id": collection,
            "public_url": f"https://gams.uni-graz.at/o:corema.{collection}.recipes",
            "tei_url": url,
            "date_statement": first_english_date(root),
            "text_license": "CC-BY-4.0",
            "size_bytes": size,
            "sha256": expected,
            "recipe_count": len(collection_summaries),
            **{f"{tag}_count": counts[tag] for tag in ROLE_TAGS},
        })

    manifest_fields = list(manifest[0])
    summary_fields = list(summaries[0])
    role_fields = list(roles[0])
    write_tsv(Path("gdt176_corema_collection_manifest.tsv"), manifest, manifest_fields)
    write_tsv(Path("gdt176_corema_recipe_inventory.tsv"), summaries, summary_fields)
    write_tsv(Path("gdt176_corema_role_oracle.tsv"), roles, role_fields)

    result: dict[str, object] = {
        "experiment": "GDT176_COREMA_ROLE_SOURCE_FREEZE",
        "status": "EXTERNAL_ROLE_CALIBRATION_SOURCE_FROZEN",
        "selection_rule": {
            "normalized_date": "interval wholly inside 1350-1500",
            "minimum_index_records": 30,
            "collection_annotated_detail_tei_required": True,
            "minimum_recipe_elements": 30,
            "minimum_instruction_elements": 30,
            "voynich_inputs_consulted": 0,
        },
        "source_index": {**INDEX, "row_count": len(index_rows)},
        "collection_count": len(manifest),
        "recipe_count": len(summaries),
        "role_element_count": len(roles),
        "role_counts": {role.upper(): sum(1 for row in roles if row["role"] == role.upper()) for role in ROLE_TAGS},
        "outputs": {
            name: sha256_file(Path(name)) for name in (
                "gdt176_corema_collection_manifest.tsv",
                "gdt176_corema_recipe_inventory.tsv",
                "gdt176_corema_role_oracle.tsv",
            )
        },
        "f84r_accessed": False,
        "voynich_scored": False,
        "claim_ceiling": "external semantic-role instrument only; no Voynich role, meaning, plaintext, language, or translation",
    }
    result["content_hash"] = content_hash(result)
    Path("gdt176_source_freeze.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"collections": len(manifest), "recipes": len(summaries), "roles": len(roles)}, sort_keys=True))


if __name__ == "__main__":
    main()
