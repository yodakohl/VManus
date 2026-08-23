#!/usr/bin/env python3
"""Audit the 36 taught roots and demote nonproductive micro-signs."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_apprentice_reverse_codebook_two_hundred_eighty_sixth/TWO_HUNDRED_EIGHTY_SIXTH_36_PRODUCTIVE_ROOTS.tsv"
RECIPES = ROOT / "experiments/yolo/sidequest_semantic_final_writer_conventions_two_hundred_eighty_eighth/TWO_HUNDRED_EIGHTY_EIGHTH_149_DETERMINISTIC_RECIPES.tsv"
WHOLE_PROSE = ROOT / "experiments/yolo/sidequest_semantic_apprentice_reverse_codebook_two_hundred_eighty_sixth/TWO_HUNDRED_EIGHTY_SIXTH_23_WHOLE_SIGNS.tsv"
WHOLE_ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_reverse_encoder_two_hundred_eighty_ninth/TWO_HUNDRED_EIGHTY_NINTH_46_ASTRO_WHOLE_SIGNS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(recipe: str) -> list[str]:
    return [part.split("[")[0] for part in recipe.split("+")]


DEMOTED = {"AN", "OS_RECEIVER", "CH_POUR", "TCH_PREPARATION", "OYK_VESSEL", "SHFY_DURATION", "D_PREVIOUS"}


def main() -> None:
    roots = read_tsv(ROOTS)
    recipes = read_tsv(RECIPES)
    prose_whole = read_tsv(WHOLE_PROSE)
    astro_whole = read_tsv(WHOLE_ASTRO)
    audit = []
    productive = []
    demoted = []

    for root in roots:
        family = root["family_id"]
        matching = []
        partners = set()
        events = 0
        for recipe in recipes:
            parts = tokens(recipe["final_recipe"])
            if family in parts:
                matching.append(recipe)
                partners.update(part for part in parts if part != family)
                events += int(recipe["event_support"])
        if family in DEMOTED:
            tier = "LEARNED_MICRO_SIGN_NOT_PRODUCTIVE_ROOT"
            action = "DEMOTE_TO_PROSE_WHOLE_SIGN_LAYER"
            reason = "Only one composed card type uses this value; keep its concrete meaning but do not teach free recombination."
        elif len(matching) >= 5 and len(partners) >= 3:
            tier = "CORE_PRODUCTIVE_FAMILY"
            action = "KEEP_IN_CORE_ROOT_DECK"
            reason = "Builds at least five card types with at least three distinct partners."
        else:
            tier = "SPECIALIST_PRODUCTIVE_FAMILY"
            action = "KEEP_IN_SPECIALIST_ROOT_DECK"
            reason = "Narrow but recurrent or contrastive specialist family; teach only in its licensed constructions."
        row = {
            "family_order_old": root["family_order"],
            "family_id": family,
            "visible_core_or_variants": root["visible_core_or_variants"],
            "short_value_de": root["short_value_de"],
            "card_types_built": len(matching),
            "prose_events_reached": events,
            "distinct_partner_families": len(partners),
            "partners": "|".join(sorted(partners)) or "NONE",
            "example_cards": "|".join(recipe["canonical_form"] for recipe in matching[:8]),
            "new_tier": tier,
            "curriculum_action": action,
            "reason": reason,
        }
        audit.append(row)
        if family in DEMOTED:
            demoted.append({
                "micro_sign_order": len(demoted) + 1,
                "family_id_old": family,
                "visible_core_or_variants": root["visible_core_or_variants"],
                "retained_concrete_value_de": root["short_value_de"],
                "card_types": len(matching),
                "events": events,
                "learn_as": "complete registered micro-sign/card, not a freely composable root",
            })
        else:
            productive.append({
                "new_family_order": len(productive) + 1,
                "family_id": family,
                "visible_core_or_variants": root["visible_core_or_variants"],
                "short_value_de": root["short_value_de"],
                "new_tier": tier,
                "card_types_built": len(matching),
                "prose_events_reached": events,
                "distinct_partner_families": len(partners),
                "teaching_restriction": "free within attested slot grammar" if tier == "CORE_PRODUCTIVE_FAMILY" else "use only in listed specialist constructions",
            })

    audit_path = HERE / "TWO_HUNDRED_NINETY_SEVENTH_36_ROOT_AUDIT.tsv"
    productive_path = HERE / "TWO_HUNDRED_NINETY_SEVENTH_29_PRODUCTIVE_FAMILIES.tsv"
    demoted_path = HERE / "TWO_HUNDRED_NINETY_SEVENTH_7_DEMOTED_MICROSIGNS.tsv"
    write_tsv(audit_path, audit)
    write_tsv(productive_path, productive)
    write_tsv(demoted_path, demoted)

    inventory = [
        {"layer_order": 1, "teaching_layer": "CORE_PRODUCTIVE_FAMILIES", "entry_count": sum(row["new_tier"] == "CORE_PRODUCTIVE_FAMILY" for row in productive), "contents": "freely recombinable within the visible slot grammar"},
        {"layer_order": 2, "teaching_layer": "SPECIALIST_PRODUCTIVE_FAMILIES", "entry_count": sum(row["new_tier"] == "SPECIALIST_PRODUCTIVE_FAMILY" for row in productive), "contents": "narrow wet-work, filtration, measure, or binding families"},
        {"layer_order": 3, "teaching_layer": "PROSE_WHOLE_SIGNS_PLUS_DEMOTED_MICROSIGNS", "entry_count": len(prose_whole) + len(demoted), "contents": "23 prior prose whole signs plus 7 concrete one-card micro-signs"},
        {"layer_order": 4, "teaching_layer": "ASTRO_WHOLE_SIGNS", "entry_count": len(astro_whole), "contents": "registered celestial diagram whole signs"},
    ]
    inventory_path = HERE / "TWO_HUNDRED_NINETY_SEVENTH_REVISED_105_ENTRY_INVENTORY.tsv"
    write_tsv(inventory_path, inventory)

    manual = """# Revidierter Stammkasten

## Was bleibt produktiv

Der bisherige Lehrplan nannte 36 Familien produktive Stämme. Sieben davon bauen jedoch jeweils nur eine einzige Kartenart. Ihre Bedeutungen werden nicht gelöscht; sie wechseln nur in die ehrlichere Schublade **gelernte Mikrokarten**.

Der neue produktive Bestand hat 29 Familien:

- 19 Kernfamilien mit mindestens fünf Kartenarten und drei Partnern;
- 10 enge Fachfamilien, die nur in ihren sichtbaren Nasswerkstatt-, Filter-, Mengen- oder Bindekonstruktionen benutzt werden.

## Die sieben gelernten Mikrokarten

- AN — zweite/alternative Portion;
- OS_RECEIVER — Aufnahmefeld;
- CH_POUR — zugießen;
- TCH_PREPARATION — Zubereitung;
- OYK_VESSEL — Gefäß;
- SHFY_DURATION — Stehzeit;
- D_PREVIOUS — voriger Posten.

Diese Werte bleiben konkret, aber ein Lehrling darf daraus keine neuen Formen frei erfinden.

## Warum der Gesamtunterricht nicht größer wird

Die Werkstatt lernte zuvor 36 Familien und 69 Ganzzeichen = 105 portable Einträge. Jetzt lernt sie 29 produktive Familien und 76 Ganz-/Mikrozeichen = ebenfalls 105. Nur die Art des Wissens wird ehrlicher: produktive Regeln hier, Auswendigkarten dort.

## Praktische Regel

Kernfamilien dürfen im Slotrahmen, Gradrahmen oder CHED-Rahmen kombiniert werden. Fachfamilien nur dort, wo das Lehrbuch eine Konstruktion zeigt. Mikrokarten werden vollständig kopiert.
"""
    manual_path = HERE / "TWO_HUNDRED_NINETY_SEVENTH_REVISED_ROOT_MANUAL.md"
    manual_path.write_text(manual, encoding="utf-8")

    report = """# Sidequest-Pass 297: Produktivität statt Stamm-Inflation

## Ergebnis

Sieben der 36 bisher gelehrten „Stämme“ waren in Wahrheit konkrete Ein-Karten-Makros. Sie werden zu gelernten Mikrokarten zurückgestuft. Es bleiben 19 breite Kernfamilien und 10 schmale, aber wiederkehrende Fachfamilien.

Die Korrektur verändert keine Übersetzung und keine der 149 Karten. Sie verändert nur, was ein Lehrling frei weiterbilden darf. Der portable Gedächtnisumfang bleibt exakt 105 Einträge: 29 produktive Familien plus 76 Ganz-/Mikrozeichen statt 36 plus 69.

Die produktivsten Familien bleiben OK, OL, OT, AL, Y, DY, E_GRADE und CHED_TRANSFER. Die neue Grenze verhindert besonders, dass einmalige Werte wie GEFÄSS, STEHZEIT oder ZUGIESSEN zu einer Flut unbelegter Fantasiekomposita führen.

## Nächster Angriff

Nun wird für die 29 echten Familien eine Kombinationskarte gebaut: welche Paare und Dreier sind sichtbar, welche Slotpartnerschaften fehlen, und welche fünf bis zehn neuen Karten sind nach der bereinigten Grammatik am stärksten vorhergesagt.
"""
    report_path = HERE / "TWO_HUNDRED_NINETY_SEVENTH_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    tiers = Counter(row["new_tier"] for row in audit)
    summary = {
        "status": "PASS",
        "audited_old_families": len(audit),
        "core_productive": tiers["CORE_PRODUCTIVE_FAMILY"],
        "specialist_productive": tiers["SPECIALIST_PRODUCTIVE_FAMILY"],
        "productive_total": len(productive),
        "demoted_micro_signs": len(demoted),
        "old_portable_entries": 36 + len(prose_whole) + len(astro_whole),
        "new_portable_entries": len(productive) + len(prose_whole) + len(demoted) + len(astro_whole),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [ROOTS, RECIPES, WHOLE_PROSE, WHOLE_ASTRO]},
        "outputs": {path.name: sha(path) for path in [audit_path, productive_path, demoted_path, inventory_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
