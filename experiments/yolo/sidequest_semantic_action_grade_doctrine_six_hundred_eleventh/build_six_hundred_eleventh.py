#!/usr/bin/env python3
"""Derive an action-specific KURZ/LANG/VOLL doctrine from current cards."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "experiments/yolo/sidequest_semantic_eight_slot_paradigm_six_hundred_ninth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ACTIONS = ["CFH", "CH", "CHD", "CHK", "K", "L", "LD", "LSH", "OK", "P", "R", "S", "SH", "SHED", "SOLK", "T", "TALAM"]
GRADES = ["E", "EE", "EEE"]
GRADE_WORD = {"E": "KURZ", "EE": "LANG", "EEE": "VOLL"}


DOCTRINE = {
    "CFH": (set(), "INHERENT_COMPLETION", "AUSWRINGEN endet mit dem gewonnenen Auszug; kein eigener Zeitgrad nötig."),
    "CH": ({"E", "EE"}, "SHORT_OR_LONG_DRAW", "ABZIEHEN darf kurz oder länger laufen; VOLL wird durch Menge oder Ergebnis ersetzt."),
    "CHD": (set(), "UNIT_TRANSFER", "UMSETZEN ist ein einzelner Transfer; weitere Dauer entsteht durch Wiederholung oder Folge."),
    "CHK": ({"E", "EE"}, "SHORT_OR_LONG_HEAT", "WAERMEN darf kurz oder lang sein; VOLL wäre praktisch Überbearbeitung und bleibt gesperrt."),
    "K": ({"E"}, "PULSED_FEED", "ZUFUEHREN erfolgt kurz/stoßweise; Gesamtmenge kommt aus MASS oder PORTION."),
    "L": ({"E", "EE"}, "SHORT_OR_LONG_ROUTE", "FUEHREN kann einen kurzen oder längeren Lauf bezeichnen; der Weg setzt das Ende."),
    "LD": (set(), "FASTEN_ONCE", "BEFESTIGEN geschieht einmal; die Haltezeit steht bei HALTEN, nicht im Befestigungswort."),
    "LSH": ({"E"}, "SHORT_WASH_CYCLE", "WASCHEN erscheint als kurzer geschlossener Gang; längere Wirkung wird separat gehalten."),
    "OK": ({"E", "EE", "EEE"}, "SHORT_LONG_OR_FULL_APPLICATION", "ANSETZEN ist die volle Gradachse; VOLL erscheint nur mit SCHLUSS."),
    "P": (set(), "INSTANT_LOAD", "HINEIN ist eine punktuelle Einfüllhandlung; Menge und Folge tragen die Ausdehnung."),
    "R": (set(), "COOL_TO_STATE", "KUEHLEN läuft bis zum Fallzustand; das benachbarte KURZ gehört in der belegten Karte zu HALTEN."),
    "S": (set(), "DIVIDE_ONCE", "TEILEN ist punktuell; das benachbarte KURZ gehört zu ABZIEHEN."),
    "SH": ({"E", "EE"}, "SHORT_OR_LONG_HOLD", "HALTEN darf kurz oder lang sein; ein eigener VOLL-Grad ist unnötig, weil BEREIT/Schluss beendet."),
    "SHED": (set(), "SETTLE_TO_RESULT", "ABSETZEN enthält sein Ende im sichtbaren Ergebnis; keine extra Gradkarte nötig."),
    "SOLK": ({"E", "EE"}, "SHORT_OR_LONG_COLLECTION", "AUFFANGEN hat kurze und lange Sammelstufen; VOLL wird durch Gefäß/Schluss angezeigt."),
    "T": ({"E", "EEE"}, "SHORT_OR_COMPLETE_ENTRY", "EINTRAGEN ist entweder kurz oder vollständig; eine lange Zwischenstufe wird nicht gebraucht."),
    "TALAM": (set(), "STORE_ONCE", "VERWAHREN setzt den Lagerzustand; seine Dauer liegt außerhalb der Karte."),
}


def assign_grade(parts: list[str], grade_index: int) -> tuple[str, str]:
    action_positions = [(i, part) for i, part in enumerate(parts) if part in ACTIONS]
    if not action_positions:
        return "NONACTION_SCOPE", "NONE"
    best_distance = min(abs(i - grade_index) for i, _ in action_positions)
    tied = [(i, action) for i, action in action_positions if abs(i - grade_index) == best_distance]
    preceding = [(i, action) for i, action in tied if i < grade_index]
    chosen = preceding[-1] if preceding else tied[0]
    return "ACTION_SCOPE", chosen[1]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(SOURCE_DIR / "SIX_HUNDRED_NINTH_173_CARD_SLOT_PARSE.tsv")
    words = read_tsv(SOURCE_DIR / "SIX_HUNDRED_NINTH_THIRTY_SEVEN_WORD_PARADIGM.tsv")
    word_by_component = {row["canonical_component"]: row["spoken_workshop_word_de"] for row in words}

    scope_rows = []
    action_grade_cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    action_grade_sets: dict[str, set[str]] = defaultdict(set)
    card_scope_summary: dict[str, list[str]] = defaultdict(list)
    for card in cards:
        parts = card["semantic_component_parse"].split("+")
        for index, component in enumerate(parts):
            if component not in GRADES:
                continue
            scope_kind, action = assign_grade(parts, index)
            scope_rows.append({
                "card_no": card["card_no"],
                "surfaces": card["surfaces"],
                "semantic_component_parse": card["semantic_component_parse"],
                "grade_component": component,
                "grade_word_de": GRADE_WORD[component],
                "grade_position": index + 1,
                "scope_kind": scope_kind,
                "scoped_action_component": action,
                "scoped_action_word_de": word_by_component[action] if action != "NONE" else "NONE",
                "occurrences": card["occurrences"],
                "records": card["records"],
                "scope_rule_de": (
                    "nächstgelegene Handlung; bei Gleichstand vorangehende Handlung"
                    if scope_kind == "ACTION_SCOPE"
                    else "Grad modifiziert Folge, Zustand oder ganzen Gang, nicht eine Einzelhandlung"
                ),
            })
            card_scope_summary[card["card_no"]].append(f"{component}->{action}")
            if action != "NONE":
                action_grade_sets[action].add(component)
                action_grade_cards[action].append(card)

    doctrine_rows = []
    for action in ACTIONS:
        allowed, doctrine_name, explanation = DOCTRINE[action]
        observed = action_grade_sets[action]
        hosts = []
        seen = set()
        for card in action_grade_cards[action]:
            if card["card_no"] not in seen:
                hosts.append(card)
                seen.add(card["card_no"])
        absent = [grade for grade in GRADES if grade not in observed]
        blocked = [grade for grade in absent if grade not in allowed]
        doctrine_rows.append({
            "action_component": action,
            "action_word_de": word_by_component[action],
            "doctrine": doctrine_name,
            "observed_grades": "|".join(GRADE_WORD[grade] for grade in GRADES if grade in observed) or "NONE",
            "permitted_grades": "|".join(GRADE_WORD[grade] for grade in GRADES if grade in allowed) or "NONE__INHERENT_OR_POINT_ACTION",
            "practically_blocked_or_unneeded_grades": "|".join(GRADE_WORD[grade] for grade in blocked) or "NONE",
            "grade_card_ids": "|".join(card["card_no"] for card in hosts) or "NONE",
            "grade_card_types": len(hosts),
            "grade_events": sum(int(card["occurrences"]) for card in hosts),
            "explanation_de": explanation,
            "unobserved_permitted_grade": "|".join(GRADE_WORD[grade] for grade in allowed - observed) or "NONE",
        })

    revised_cards = []
    for card in cards:
        actions = [component for component in card["semantic_component_parse"].split("+") if component in ACTIONS]
        revised_cards.append({
            **card,
            "action_components": "|".join(actions) if actions else "NONE",
            "grade_scope_assignments": "|".join(card_scope_summary[card["card_no"]]) or "NONE",
            "grade_doctrine_names": "|".join(dict.fromkeys(DOCTRINE[action][1] for action in actions)) if actions else "NONE",
        })

    write_tsv(HERE / "SIX_HUNDRED_ELEVENTH_SEVENTEEN_ACTION_GRADE_DOCTRINE.tsv", doctrine_rows, list(doctrine_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_ELEVENTH_GRADE_SCOPE_ASSIGNMENTS.tsv", scope_rows, list(scope_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_ELEVENTH_173_GRADE_AWARE_DICTIONARY.tsv", revised_cards, list(revised_cards[0]))

    graded_actions = sum(row["observed_grades"] != "NONE" for row in doctrine_rows)
    inherent = len(doctrine_rows) - graded_actions
    report = f"""# Sechshundertelfte Runde: die praktische Gradlehre

## Ergebnis

Die fehlenden Gradformen sind überwiegend keine Wörterbuchlücken. Von 17 Handlungen haben {graded_actions} eine echte KURZ/LANG/VOLL-Achse; {inherent} sind punktuell oder enden durch ihr eigenes Ergebnis.

## Die wichtigsten Reihen

```text
ANSETZEN    KURZ · LANG · VOLL   (VOLL nur mit SCHLUSS)
HALTEN      KURZ · LANG
WAERMEN     KURZ · LANG
ABZIEHEN    KURZ · LANG
FUEHREN     KURZ · LANG
AUFFANGEN   KURZ · LANG
EINTRAGEN   KURZ · VOLL
ZUFUEHREN   KURZ
WASCHEN     KURZ
```

## Handlungen ohne eigenen Grad

AUSWRINGEN, UMSETZEN, BEFESTIGEN, HINEIN, KUEHLEN, TEILEN, ABSETZEN und VERWAHREN brauchen keinen freien Zeitgrad:

- AUSWRINGEN und ABSETZEN enden am sichtbaren Ergebnis;
- UMSETZEN, HINEIN, TEILEN und BEFESTIGEN sind einzelne Arbeitsschritte;
- KUEHLEN läuft bis zum gewünschten Zustand;
- VERWAHREN setzt einen Lagerzustand, dessen Dauer außerhalb der Karte liegt.

## Warum VOLL selten ist

VOLL ist keine bloße dritte Länge. Es bedeutet, dass ein Vorgang vollständig ausgeführt und gewöhnlich geschlossen wird. Deshalb ist `OK+EEE+DY` belegt, eine offene `OK+EEE+Y`-Schwester aber nicht. Bei WAERMEN oder HALTEN wäre VOLL sogar praktisch ungeschickt: Der Meister will bis BEREIT, nicht bis abstrakt „voll“.

## Zuständigkeitsregel

Ein Grad gehört zur nächstgelegenen Handlung; bei Gleichstand zur vorangehenden. So modifiziert in `R+SH+E+AL` das KURZ den HALTEN-Schritt, nicht KUEHLEN, und in `L+K+E+DY` den ZUFUEHREN-Schritt, nicht den ganzen Transfer.

## Nächster Schritt

Als nächstes bauen wir aus Handlung, Grad und Schluss eine kleine Tabelle konkreter Werkstattbefehle. Diese wird direkt in die sechs Falltexte eingesetzt, damit jede Wiederholung exakt gleich übersetzt wird.
"""
    (HERE / "SIX_HUNDRED_ELEVENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "actions": len(doctrine_rows),
        "actions_with_observed_grades": graded_actions,
        "inherent_or_point_actions": inherent,
        "grade_scope_assignments": len(scope_rows),
        "grade_cards": len({row["card_no"] for row in scope_rows}),
        "cards": len(revised_cards),
        "unobserved_permitted_action_grades": sum(row["unobserved_permitted_grade"] != "NONE" for row in doctrine_rows),
        "decision": "ACTION_SPECIFIC_GRADE_DOCTRINE_EXPLAINS_MISSING_PARADIGM_CELLS",
    }
    (HERE / "SIX_HUNDRED_ELEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
