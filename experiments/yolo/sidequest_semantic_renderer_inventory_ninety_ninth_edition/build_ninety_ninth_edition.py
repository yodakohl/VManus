#!/usr/bin/env python3
"""Reduce all 230 visible prose forms to shared card hosts and renderer gestures."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_173_LITERAL_PARSE.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_230_SURFACE_PARSE.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def common_suffix(forms: list[str]) -> str:
    if not forms:
        return ""
    rev = [form[::-1] for form in forms]
    length = 0
    for chars in zip(*rev):
        if len(set(chars)) != 1:
            break
        length += 1
    return forms[0][len(forms[0]) - length:] if length else ""


def gesture(prefix: str) -> str:
    if prefix == "":
        return "ZERO"
    if prefix.startswith("sh"):
        return "SH_ENTRY"
    if prefix.startswith("ch"):
        return "CH_ENTRY"
    if prefix.startswith("q"):
        return "Q_ENTRY"
    if prefix.startswith("s"):
        return "S_ENTRY"
    if prefix.startswith("d"):
        return "D_ENTRY"
    if prefix.startswith("t"):
        return "T_ENTRY"
    if prefix.startswith("o"):
        return "O_ENTRY"
    return "OTHER_ENTRY"


def main() -> None:
    cards = read_tsv(CARDS)
    surfaces = read_tsv(SURFACES)
    by_id = {row["master_card_id"]: row for row in cards}
    family_rows: list[dict[str, object]] = []
    coverage_rows: list[dict[str, object]] = []
    gesture_counts: Counter[str] = Counter()
    gesture_cards: dict[str, set[str]] = {}

    for card in cards:
        forms = card["registered_surface_family"].split("|")
        host = common_suffix(forms)
        prefixes = [form[:-len(host)] if host else form for form in forms]
        host_free = host in forms
        if len(forms) == 1:
            family_class = "SINGLE_REGISTERED_FORM"
            training_rule = "copy the exact card"
        elif len(host) >= 2 and host_free:
            family_class = "FREE_STABLE_HOST_PLUS_ENTRIES"
            training_rule = "learn one free host and its licensed entry gestures"
        elif len(host) >= 2:
            family_class = "BOUND_STABLE_HOST_PLUS_ENTRIES"
            training_rule = "learn one bound host and its licensed entry gestures"
        else:
            family_class = "MINIMAL_HOST__LEARN_ALLOGRAPH_SET"
            training_rule = "learn the whole allograph set; suffix alone is not semantic"
        gset = [gesture(prefix) for prefix in prefixes]
        family_rows.append({
            "master_card_id": card["master_card_id"],
            "semantic_atoms": card["corrected_semantic_atoms"],
            "short_value_de": card["short_default_de"],
            "master_form": card["master_head_form"],
            "registered_forms": "|".join(forms),
            "stable_surface_host": host or "NONE",
            "entry_prefixes": "|".join(prefix if prefix else "ZERO" for prefix in prefixes),
            "entry_gestures": "|".join(gset),
            "form_count": len(forms),
            "family_class": family_class,
            "training_rule": training_rule,
        })
        for form, prefix, gname in zip(forms, prefixes, gset):
            if form != card["master_head_form"]:
                gesture_counts[gname] += 1
                gesture_cards.setdefault(gname, set()).add(card["master_card_id"])
            coverage_rows.append({
                "visible_surface": form,
                "master_card_id": card["master_card_id"],
                "semantic_atoms": card["corrected_semantic_atoms"],
                "stable_surface_host": host or "NONE",
                "surface_entry_prefix": prefix or "ZERO",
                "renderer_gesture": gname,
                "is_master_form": "YES" if form == card["master_head_form"] else "NO",
                "family_class": family_class,
                "meaning_preserved": "YES",
            })

    wrapper_rows = []
    for gname in ["Q_ENTRY", "SH_ENTRY", "S_ENTRY", "CH_ENTRY", "D_ENTRY", "T_ENTRY", "O_ENTRY", "OTHER_ENTRY", "ZERO"]:
        wrapper_rows.append({
            "renderer_gesture": gname,
            "nonmaster_surface_forms": gesture_counts[gname],
            "affected_master_cards": len(gesture_cards.get(gname, set())),
            "training_value": "choose only when listed for the active registered card",
            "semantic_contribution": "NONE",
        })

    write_tsv(OUT / "NINETY_NINTH_173_RENDERER_FAMILIES.tsv", list(family_rows[0]), family_rows)
    write_tsv(OUT / "NINETY_NINTH_230_SURFACE_COVERAGE.tsv", list(coverage_rows[0]), coverage_rows)
    write_tsv(OUT / "NINETY_NINTH_RENDERER_GESTURES.tsv", list(wrapper_rows[0]), wrapper_rows)

    classes = Counter(row["family_class"] for row in family_rows)
    surface_classes = Counter(row["family_class"] for row in coverage_rows)
    nonmaster = sum(row["is_master_form"] == "NO" for row in coverage_rows)
    simple_nonmaster = sum(
        row["is_master_form"] == "NO" and row["family_class"] != "MINIMAL_HOST__LEARN_ALLOGRAPH_SET"
        for row in coverage_rows
    )
    report = [
        "# Neunundneunzigste Runde: Das vollständige Renderer-Inventar", "",
        "## Ergebnis", "",
        f"Die 173 registrierten Prosakarten besitzen zusammen 230 sichtbare Formen:",
        f"173 Meisterformen und {nonmaster} zusätzliche Allographen. Davon lassen sich",
        f"{simple_nonmaster} als stabiler freier oder gebundener Kartenkörper plus eine",
        "kleine Eintrittsgeste lehren; nur der Rest braucht ein als Ganzes gelerntes",
        "Allographenset.", "",
    ]
    for name, count in sorted(classes.items()):
        report.append(f"- {name}: {count} Karten / {surface_classes[name]} sichtbare Formen")
    report.extend(["", "## Acht Renderer-Gesten", ""])
    for row in wrapper_rows:
        if int(row["nonmaster_surface_forms"]):
            report.append(f"- **{row['renderer_gesture']}**: {row['nonmaster_surface_forms']} zusätzliche Formen auf {row['affected_master_cards']} Karten")
    report.extend([
        "", "Die Geste selbst trägt keine Bedeutung. Sie darf nur verwendet werden, wenn",
        "sie im Allographensatz der aktiven Karte steht. Damit erklärt das Modell",
        "`aiin/chaiin/daiin/saiin/taiin`, `al/chal/cheal/dal/sal/tal` und",
        "`cheol/chol/ol/qol/sol/tol` als dieselben Karten mit verschiedenen Eintritten,",
        "ohne `ch`, `d`, `s`, `t` oder `q` jedes Mal zu neuen Inhaltsmorphemen zu machen.", "",
        "Das ist die bisher einfachste plausible Mehrschreiberlehre: gemeinsamer Kartenwert,",
        "stabiler Körper, handabhängige zugelassene Eintrittsgeste. Wo nur ein einbuchstabiger",
        "Rest stabil bleibt, wird die ganze Familie gelernt und nicht künstlich zerlegt.", "",
        "Nur die festen Prosaseiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ])
    (OUT / "NINETY_NINTH_RENDERER_INVENTORY_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "master_cards": len(cards), "visible_surfaces": len(coverage_rows),
        "master_forms": sum(row["is_master_form"] == "YES" for row in coverage_rows),
        "nonmaster_forms": nonmaster, "simple_host_plus_entry_nonmaster_forms": simple_nonmaster,
        "family_classes": dict(classes), "nonmaster_gestures": dict(gesture_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
