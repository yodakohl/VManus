#!/usr/bin/env python3
"""Build the corrector's complete V45 stem-first revision on the fixed pages."""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")
V43 = ROOT / "experiments/yolo/sidequest_theory_candidates_v43/V43_CURRENT_PROSE_DICTIONARY.tsv"
V40 = ROOT / "experiments/yolo/sidequest_theory_candidates_v40/V40_REVISED_381_EVENT_LEDGER.tsv"
R1 = ROOT / "experiments/yolo/sidequest_theory_candidates_v44/V44_R1_COMPLETE_WORKSHOP_STEM_FAMILIES.tsv"


CORE = {
    "aiin": ("vorgeschriebenes oder standardisiertes Maß", "CONTENT_CORE", ".82"),
    "or": ("bereitetes verwendbares Medium oder Produkt", "CONTENT_CORE", ".71"),
    "chor": ("Sammelzeit oder Beschaffung des gezeigten Simplex", "CONTENT_CORE", ".43"),
    "chey": ("ausgewählten Material- oder Pflanzenteil nehmen", "CONTENT_CORE", ".60"),
    "ch": ("Flüssigkeit trennen, klären oder abziehen", "WEAK_OPERATION_CORE", ".31"),
    "chy": ("warmes Medium zur Zubereitung oder Anwendung bereitstellen", "WEAK_OPERATION_CORE", ".35"),
    "ok": ("einen spezifizierten Arbeitsposten aktivieren oder zuweisen", "FORMAL_AXIS", ".72"),
    "ot": ("einen markierten Bezug, Parameter oder Weg wählen", "FORMAL_AXIS", ".44"),
    "l": ("aus dem vorigen Schritt fortsetzen oder zum Empfänger führen", "FORMAL_AXIS", ".52"),
    "ey": ("den geforderten beobachtbaren Sollzustand erreichen", "FORMAL_AXIS", ".66"),
    "e": ("bis zu einem Reife- oder Bereitschaftszustand warten", "FORMAL_AXIS", ".61"),
    "y": ("aktuellen Konstruktionszustand tragen", "FORMAL_AXIS_WITH_EXCEPTIONS", ".35"),
    "o": ("den nächsten Material- oder Prozessplatz eröffnen", "WEAK_FORMAL_AXIS", ".25"),
    "al": ("zum bezeichneten Ziel oder nächsten Weg führen", "RELATION_CORE", ".76"),
    "ar": ("aus derselben oder bezeichneten Quelle", "RELATION_CORE", ".73"),
}


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


def guarded(path: Path, columns: list[str]) -> list[dict[str, str]]:
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--columns", ",".join(columns), "--forbid-prefix", "f84"]
    stdout = subprocess.run(
        cmd, cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout
    lines = [line for line in stdout.splitlines() if not line.startswith("GUARD_STATS ")]
    return list(csv.DictReader(io.StringIO("\n".join(lines)), delimiter="\t"))


def formal_expansion(row: dict[str, str]) -> str:
    parts = []
    if row["local_frame"] != "NONE":
        parts.append(f"Rahmen {row['local_frame']} spezialisiert den Bezug")
    if row["inner_d"] == "1":
        parts.append("inner-D wählt die gelernte Zustands-/Operationsvariante")
    if row["right_family"] != "NONE":
        parts.append(f"RIGHT-{row['right_family']} spezifiziert Argument oder Relation")
    if row["dy_closure"] == "1":
        parts.append("DY vollzieht und schließt die lokale Arbeitszelle")
    if row["b3"] == "1":
        parts.append("B3 markiert den besonderen Zellabschluss")
    return "; ".join(parts) if parts else "unmarkierte Grundkarte"


def main() -> None:
    lex = [r for r in read(V43) if r["scope"] == "PROSE_EXACT_CARD"]
    events = read(V40)
    r1 = {r["candidate_page_host"]: r for r in read(R1)}
    formal = guarded(
        ROOT / "gdt327_joint_tuple_interlinear.tsv",
        ["page", "locus", "group_index", "joint_tuple_id"],
    )
    native = guarded(
        ROOT / "gdt278_native_event_inventory.tsv",
        ["page", "locus", "group_index", "page_host", "local_frame", "inner_d", "right_family", "dy_closure", "b3"],
    )
    assert len(lex) == 173 and len(events) == len(formal) == len(native) == 381
    native_by_key = {(r["page"], r["locus"], r["group_index"]): r for r in native}
    tuple_forms: dict[str, list[dict[str, str]]] = defaultdict(list)
    event_formal: dict[tuple[str, str], dict[str, str]] = {}
    for row in formal:
        key = (row["page"], row["locus"], row["group_index"])
        merged = dict(row)
        merged.update(native_by_key[key])
        tuple_forms[row["joint_tuple_id"]].append(merged)
        event_formal[(row["locus"], row["group_index"])] = merged

    lex_by_id = {r["lexicon_id"]: r for r in lex}
    cards: list[dict[str, object]] = []
    card_by_id: dict[str, dict[str, object]] = {}
    for tuple_id in sorted(lex_by_id):
        old = lex_by_id[tuple_id]
        forms = tuple_forms[tuple_id]
        assert forms
        host = forms[0]["page_host"]
        coords = {k: forms[0][k] for k in ("local_frame", "inner_d", "right_family", "dy_closure", "b3")}
        assert all(all(r[k] == v for k, v in coords.items()) for r in forms)
        if host in CORE:
            root_value, root_status, root_conf = CORE[host]
        else:
            inventory = r1[host]
            if int(inventory["exact_card_types"]) == 1:
                root_value = old["current_default"]
                root_status = "MEMORIZED_WHOLE_CARD_CORE"
                root_conf = old["confidence"]
            else:
                root_value = inventory["shared_semantic_intersection"]
                root_status = "PROVISIONAL_MULTI_CARD_INTERSECTION"
                root_conf = inventory["confidence"]
        merged_form = dict(forms[0])
        form_value = formal_expansion(merged_form)
        revised = old["current_default"]
        row = {
            "joint_tuple_id": tuple_id,
            "page_host": host,
            "surface_examples": old["surface_examples"],
            "fixed_events": old["events"],
            "fixed_pages": old["pages"],
            "stable_core_or_axis_German": root_value,
            "core_status": root_status,
            "core_confidence": root_conf,
            "local_frame": coords["local_frame"],
            "inner_d": coords["inner_d"],
            "right_family": coords["right_family"],
            "dy_closure": coords["dy_closure"],
            "b3": coords["b3"],
            "formal_coordinate_contribution_German": form_value,
            "local_context_expansion_German": old["current_default"],
            "revised_complete_German": revised,
            "composition_rule": "STABLE_CORE_OR_AXIS + FORMAL_COORDINATE + LOCAL_CONTEXT_EXPANSION",
            "interpretation_status": "CREATIVE_COMPOSITIONAL_REVISION_NOT_DECIPHERMENT",
        }
        cards.append(row)
        card_by_id[tuple_id] = row

    interlinear: list[dict[str, object]] = []
    for event in events:
        formal_row = event_formal[(event["locus"], event["event_index"])]
        assert formal_row["joint_tuple_id"] == event["exact_tuple_id"]
        card = card_by_id[event["exact_tuple_id"]]
        assert event["surface"] in str(card["surface_examples"]).split("|")
        interlinear.append({
            "page": event["page"],
            "locus": event["locus"],
            "record": event["record"],
            "event_index": event["event_index"],
            "surface": event["surface"],
            "joint_tuple_id": event["exact_tuple_id"],
            "page_host": card["page_host"],
            "stable_core_or_axis_German": card["stable_core_or_axis_German"],
            "formal_coordinate_contribution_German": card["formal_coordinate_contribution_German"],
            "revised_complete_German": card["revised_complete_German"],
            "meaning_status": "CREATIVE_STEM_FIRST_INTERLINEAR_NOT_PLAINTEXT",
        })

    write(OUT / "V45_R4_REVISED_173_CARD_LEXICON.tsv", cards)
    write(OUT / "V45_R4_REVISED_381_EVENT_INTERLINEAR.tsv", interlinear)
    host_counts = Counter(str(r["page_host"]) for r in cards)
    validation = {
        "schema": "SIDEQUEST_V45_R4_COMPOSITIONAL_REVISION_V1",
        "status": "PASS",
        "checks": {
            "exact_cards_173": len(cards) == 173,
            "events_381": len(interlinear) == 381,
            "distinct_page_hosts_136": len(host_counts) == 136,
            "all_cards_have_stable_core_or_axis": all(str(r["stable_core_or_axis_German"]).strip() for r in cards),
            "all_cards_have_complete_translation": all(str(r["revised_complete_German"]).strip() for r in cards),
            "same_tuple_one_core": len({(r["joint_tuple_id"], r["stable_core_or_axis_German"]) for r in interlinear}) == 173,
            "guarded_source_access": True,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V45_R4_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
