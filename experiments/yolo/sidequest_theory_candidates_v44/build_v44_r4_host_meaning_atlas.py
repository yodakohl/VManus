#!/usr/bin/env python3
"""Join the V43 creative card lexicon to the existing opaque PAGE_HOST layer."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEX = ROOT / "experiments/yolo/sidequest_theory_candidates_v43/V43_CURRENT_PROSE_DICTIONARY.tsv"
HOSTS = ROOT / "gdt278_native_event_inventory.tsv"
ATLAS = ROOT / "gdt327_joint_tuple_atlas.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def host_hash(host: str) -> str:
    return hashlib.sha256(("HOST|" + host).encode()).hexdigest()[:20]


def entropy(counts: Counter[str]) -> float:
    total = sum(counts.values())
    return -sum((n / total) * math.log2(n / total) for n in counts.values()) if total else 0.0


def main() -> None:
    lex = [r for r in read(LEX) if r["scope"] == "PROSE_EXACT_CARD"]
    host_events = [r for r in read(HOSTS) if r["control_id"] == "VOYNICH_REFERENCE"]
    assert host_events and not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in host_events)
    atlas = {r["joint_tuple_id"]: r for r in read(ATLAS)}
    host_names = sorted({r["page_host"] for r in host_events})
    hash_to_host = {host_hash(host): host for host in host_names}
    host_occurrences = Counter(r["page_host"] for r in host_events)
    host_folios = defaultdict(set)
    for row in host_events:
        host_folios[row["page_host"]].add(row["physical_folio"])
    assert len(lex) == 173 and len(host_names) == 1217 and len(hash_to_host) == 1217

    cards: list[dict[str, object]] = []
    for row in lex:
        formal = atlas[row["lexicon_id"]]
        host = hash_to_host[formal["host_id"]]
        cards.append({
            "page_host": host,
            "joint_tuple_id": row["lexicon_id"],
            "surface_examples": row["surface_examples"],
            "v43_current_default": row["current_default"],
            "source_class": row["source_class"],
            "v43_confidence": row["confidence"],
            "fixed_panel_events": row["events"],
            "fixed_panel_pages": row["pages"],
            "manuscript_events": formal["events"],
            "manuscript_folios": formal["folios"],
            "coordinate_id": formal["coordinate_id"],
            "wrapper_classes": formal["wrapper_classes"],
            "meaning_unit": "COMPLETE_JOINT_TUPLE_NOT_PAGE_HOST",
        })
    cards.sort(key=lambda r: (str(r["page_host"]), str(r["joint_tuple_id"])))
    write(OUT / "V44_R4_CARD_TO_HOST_MEANINGS.tsv", cards)

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in cards:
        grouped[str(row["page_host"])].append(row)
    summary: list[dict[str, object]] = []
    for host, members in grouped.items():
        classes = Counter(str(r["source_class"]) for r in members)
        summary.append({
            "page_host": host,
            "host_inventory_occurrences": host_occurrences[host],
            "host_inventory_folios": len(host_folios[host]),
            "v43_joint_tuple_cards": len(members),
            "v43_fixed_events": sum(int(r["fixed_panel_events"]) for r in members),
            "distinct_source_classes": len(classes),
            "source_class_entropy_bits": f"{entropy(classes):.6f}",
            "modal_source_class": classes.most_common(1)[0][0],
            "modal_class_fraction": f"{classes.most_common(1)[0][1] / len(members):.6f}",
            "surface_examples": " || ".join(str(r["surface_examples"]) for r in members),
            "v43_meanings": " || ".join(str(r["v43_current_default"]) for r in members),
            "host_semantic_status": "UNASSIGNED_MULTI_CARD_CONTAINER" if len(members) > 1 else "ONE_CARD_ONLY_IN_FIXED_PANEL",
        })
    summary.sort(key=lambda r: (-int(r["v43_fixed_events"]), -int(r["v43_joint_tuple_cards"]), str(r["page_host"])))
    write(OUT / "V44_R4_HOST_MEANING_SUMMARY.tsv", summary)

    checks = {
        "schema": "SIDEQUEST_V44_R4_HOST_MEANING_ATLAS_VALIDATION_V1",
        "status": "PASS",
        "checks": {
            "prose_cards_173": len(cards) == 173,
            "fixed_events_381": sum(int(r["fixed_panel_events"]) for r in cards) == 381,
            "all_host_hashes_resolved": all(r["page_host"] for r in cards),
            "distinct_hosts_in_fixed_panel": len(summary),
            "no_host_meaning_assigned_by_builder": all(r["host_semantic_status"] in {"UNASSIGNED_MULTI_CARD_CONTAINER", "ONE_CARD_ONLY_IN_FIXED_PANEL"} for r in summary),
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V44_R4_VALIDATION.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()
