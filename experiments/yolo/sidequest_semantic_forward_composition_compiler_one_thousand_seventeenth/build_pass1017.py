#!/usr/bin/env python3
"""Build Pass 1017: a forward composition compiler for the nineteen portable cores."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1013 = ROOT / "experiments/yolo/sidequest_semantic_embedded_stem_resegmentation_one_thousand_thirteenth"
PASS1016 = ROOT / "experiments/yolo/sidequest_semantic_local_channel_compression_one_thousand_sixteenth"
SOURCE_CONTRACT = PASS1013 / "PASS1013_46_SIGN_SEMANTIC_CONTRACT.tsv"
SOURCE_STATEMENTS = PASS1013 / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"
SOURCE_CHANNELS = PASS1016 / "PASS1016_FOUR_LOCAL_CHANNELS.tsv"


ROLE_RULES = {
    "Y": ("REFERENT_TAIL", "DIES", "Schließe die lokale Form mit dem aktuell gemeinten Posten; Y ist kein Schlusszeichen."),
    "OK": ("ACTION_HEAD", "SETZEN", "Setze den rechts folgenden Posten, Grad, die Menge oder Adresse in Gang."),
    "OL": ("CONTINUATION_FRAME", "FORTSETZEN", "Führe die rechts folgende Handlung oder den allein stehenden aktiven Gang fort."),
    "OT": ("NEXT_FRAME", "DANACH", "Lies die rechts folgende Handlung, Adresse oder den Grad als nächsten Schritt."),
    "AL": ("TARGET_TAIL", "ZIELORT", "Binde die vorherige Handlung an den bezeichneten Zielort."),
    "CH": ("ACTION_HEAD", "NEHMEN", "Nimm den rechts bezeichneten Posten, die Menge, Adresse oder Folgehandlung."),
    "SH": ("ACTION_HEAD", "HALTEN", "Halte den rechts bezeichneten Posten oder Ansatz im folgenden Grad."),
    "AR": ("SOURCE_TAIL", "AUSGANG", "Binde die vorherige Handlung an den bezeichneten Ausgang; keine Richtung erfinden."),
    "K": ("TRANSFER_HEAD_OR_BRIDGE", "GEBEN", "Gib den rechts bezeichneten Posten weiter oder verbinde zwei Handlungsteile durch Übergabe."),
    "AIIN": ("QUANTITY_TAIL", "MASS", "Lies die vorherige Handlung nach dem vorgegebenen Maß."),
    "S": ("CHOICE_HEAD", "WÄHLEN", "Wähle den rechts bezeichneten Posten, die Portion oder Adresse."),
    "CHD": ("TRANSFER_HEAD", "UMSETZEN", "Setze den aktiven Posten in den nächsten lokalen Arbeitszustand um."),
    "OR": ("PREPARATION_TAIL", "ANSATZ", "Beziehe die vorherige Handlung auf den laufenden Ansatz."),
    "L": ("CONNECTION_FRAME", "VERBINDUNG", "Führe die eingeschlossene oder rechts folgende Handlung über eine lokale Verbindung; keine Richtung."),
    "T": ("SETTING_HEAD", "EINSTELLEN", "Stelle den rechts folgenden Posten, Grad oder die Menge ein."),
    "AIN": ("QUANTITY_TAIL", "PORTION", "Lies die vorherige Handlung mit einer Portion."),
    "R": ("MARK_HEAD_OR_TAIL", "MARKIEREN", "Markiere den rechts folgenden Wert oder den soeben gesetzten lokalen Platz."),
    "P": ("ENTRY_HEAD", "EINSETZEN", "Setze den rechts bezeichneten Posten oder die Menge in den laufenden Gang ein."),
    "AIR": ("PATH_TAIL", "LAUF", "Binde die Handlung an den bezeichneten Lauf; Wasser oder Richtung kommen nur vom Besitzer."),
}

PREDICTIONS = [
    (1, "CH", "AIN", "chain", "eine Portion nehmen", "HOCH", "CH+AIIN ist häufig, AIN ist produktiv; die kurze Form bleibt frei."),
    (2, "P", "AIN", "pain", "eine Portion einsetzen", "MITTEL", "P setzt Posten ein; die Portionskarte ist produktiv, aber die direkte Paarung fehlt."),
    (3, "P", "AIIN", "paiin", "nach Maß einsetzen", "MITTEL", "P setzt Posten ein; die Maßkarte ist produktiv, aber die direkte Paarung fehlt."),
    (4, "L", "AIR", "lair", "Verbindung im bezeichneten Lauf", "NIEDRIG", "Beide Kerne sind räumlich; die direkte Form wäre redundant, bleibt aber eindeutig lesbar."),
]


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    _, contract = read_tsv(SOURCE_CONTRACT)
    _, statements = read_tsv(SOURCE_STATEMENTS)
    _, local_channels = read_tsv(SOURCE_CHANNELS)
    portable_rows = [row for row in contract if row["pass1012_class"] == "PORTABLE_CORE_MEANING"]
    roots = [row["sign"] for row in portable_rows]
    values = {row["sign"]: row["single_core_value_de"] for row in portable_rows}
    if set(roots) != set(ROLE_RULES):
        raise SystemExit("role rules do not cover the nineteen portable roots exactly")

    events = []
    for statement in statements:
        surfaces = statement["surface_sequence"].split()
        component_events = [event.split("+") for event in statement["component_sequence"].split(" | ")]
        for index, (surface, tokens) in enumerate(zip(surfaces, component_events)):
            events.append(
                {
                    "event_id": f"{statement['statement_id']}@{index + 1}",
                    "statement_id": statement["statement_id"],
                    "page": statement["physical_page"],
                    "register": statement["register"],
                    "surface": surface,
                    "tokens": tokens,
                }
            )

    usage = {
        root: {
            "mentions": 0, "events": set(), "statements": set(), "pages": set(), "registers": set(),
            "positions": Counter(), "left": Counter(), "right": Counter(), "recipes": Counter(), "surfaces": Counter(),
        }
        for root in roots
    }
    for event in events:
        tokens = event["tokens"]
        recipe = "+".join(tokens)
        for index, token in enumerate(tokens):
            if token not in usage:
                continue
            info = usage[token]
            info["mentions"] += 1
            info["events"].add(event["event_id"])
            info["statements"].add(event["statement_id"])
            info["pages"].add(event["page"])
            info["registers"].add(event["register"])
            info["positions"]["FIRST" if index == 0 else "LAST" if index == len(tokens) - 1 else "MIDDLE"] += 1
            if index:
                info["left"][tokens[index - 1]] += 1
            if index + 1 < len(tokens):
                info["right"][tokens[index + 1]] += 1
            info["recipes"][recipe] += 1
            info["surfaces"][event["surface"]] += 1

    valency_rows = []
    for root in roots:
        info = usage[root]
        role, value, rule = ROLE_RULES[root]
        valency_rows.append(
            {
                "root": root,
                "fixed_value_de": value,
                "composition_role": role,
                "running_mentions": str(info["mentions"]),
                "event_count": str(len(info["events"])),
                "statement_count": str(len(info["statements"])),
                "page_count": str(len(info["pages"])),
                "registers": "|".join(sorted(info["registers"])),
                "token_position_counts": "|".join(f"{key}:{info['positions'][key]}" for key in ("FIRST", "MIDDLE", "LAST")),
                "left_neighbors": "|".join(f"{key}:{value}" for key, value in info["left"].most_common(8)) or "NONE",
                "right_neighbors": "|".join(f"{key}:{value}" for key, value in info["right"].most_common(8)) or "NONE",
                "top_component_recipes": "|".join(f"{key}:{value}" for key, value in info["recipes"].most_common(8)),
                "surface_examples": "|".join(key for key, _ in info["surfaces"].most_common(10)),
                "forward_rule_de": rule,
                "repair_policy_de": "Bei Konflikt Gesamtkarte oder lokale Erweiterung annehmen; den Kernwert nicht ändern.",
            }
        )
    valency_path = HERE / "PASS1017_19_CORE_VALENCY.tsv"
    write_tsv(valency_path, list(valency_rows[0]), valency_rows)

    pair_rows = []
    pair_status_counts: Counter[str] = Counter()
    for left in roots:
        for right in roots:
            adjacent_events = []
            gapped_events = []
            adjacent_surfaces: Counter[str] = Counter()
            gapped_surfaces: Counter[str] = Counter()
            pages = set()
            registers = set()
            for event in events:
                tokens = event["tokens"]
                adjacent = any(a == left and b == right for a, b in zip(tokens, tokens[1:]))
                ordered_gap = any(
                    tokens[i] == left and tokens[j] == right
                    for i in range(len(tokens)) for j in range(i + 2, len(tokens))
                )
                if adjacent:
                    adjacent_events.append(event["event_id"])
                    adjacent_surfaces[event["surface"]] += 1
                    pages.add(event["page"])
                    registers.add(event["register"])
                if ordered_gap:
                    gapped_events.append(event["event_id"])
                    gapped_surfaces[event["surface"]] += 1
                    pages.add(event["page"])
                    registers.add(event["register"])
            status = "ADJACENT_ATTESTED" if adjacent_events else "GAPPED_ATTESTED" if gapped_events else "UNSEEN_ORDERED_PAIR"
            pair_status_counts[status] += 1
            pair_rows.append(
                {
                    "left_root": left,
                    "right_root": right,
                    "literal_prediction_de": f"{values[left]} + {values[right]}",
                    "pair_status": status,
                    "adjacent_event_count": str(len(adjacent_events)),
                    "gapped_event_count": str(len(gapped_events)),
                    "page_count": str(len(pages)),
                    "registers": "|".join(sorted(registers)) if registers else "NONE",
                    "adjacent_surface_examples": "|".join(key for key, _ in adjacent_surfaces.most_common(10)) or "NONE",
                    "gapped_surface_examples": "|".join(key for key, _ in gapped_surfaces.most_common(10)) or "NONE",
                    "forward_rule_de": f"{ROLE_RULES[left][2]} Danach {ROLE_RULES[right][2]}",
                }
            )
    pair_path = HERE / "PASS1017_361_ORDERED_CORE_PAIRS.tsv"
    write_tsv(pair_path, list(pair_rows[0]), pair_rows)

    pair_by_key = {(row["left_root"], row["right_root"]): row for row in pair_rows}
    prediction_rows = []
    for rank, left, right, surface, reading, priority, rationale in PREDICTIONS:
        pair = pair_by_key[(left, right)]
        prediction_rows.append(
            {
                "prediction_rank": str(rank),
                "left_root": left,
                "right_root": right,
                "candidate_surface": surface,
                "predicted_reading_de": reading,
                "priority": priority,
                "current_adjacent_events": pair["adjacent_event_count"],
                "current_gapped_events": pair["gapped_event_count"],
                "decision_rule_de": "Wenn die neue Form im laufenden Text erscheint, zuerst genau diese Komposition lesen.",
                "rationale_de": rationale,
                "failure_condition_de": "Scheitert, wenn Besitzer und Nachbarn die feste Wurzelsumme wiederholt unbrauchbar machen.",
            }
        )
    prediction_path = HERE / "PASS1017_FOUR_FRESH_COMPOSITION_PREDICTIONS.tsv"
    write_tsv(prediction_path, list(prediction_rows[0]), prediction_rows)

    report = f"""# Pass 1017 — Vorwärts-Compiler für die Wortkomposition

## Ergebnis

Das System hat jetzt nicht nur ein Wörterbuch, sondern eine ausführbare Leserichtung. Die 19 portablen Kerne verteilen sich auf sechs praktische Rollen:

- **Handlungsköpfe:** `OK SETZEN`, `CH NEHMEN`, `SH HALTEN`, `S WÄHLEN`, `P EINSETZEN`, `T EINSTELLEN`, `K GEBEN`, `CHD UMSETZEN`, `R MARKIEREN`;
- **Reihenfolgerahmen:** `OT DANACH`, `OL FORTSETZEN`;
- **Mengen und Arbeitsstoff:** `AIIN MASS`, `AIN PORTION`, `OR ANSATZ`;
- **Orts-/Wegebezug:** `AL ZIELORT`, `AR AUSGANG`, `L VERBINDUNG`, `AIR LAUF`;
- **Referent:** `Y DIES / AKTIVER POSTEN`;
- **danach erst** Grad, lokale Kanäle und Schluss aus dem bestehenden Kontrollblatt.

Der Compiler arbeitet so:

> **längste bekannte Grafik erkennen → eingebettete Kerne entfalten → von links nach rechts feste Kernwerte einsetzen → lokale HIER/VARIANTE/KLASSE/VORBEZUG-Kanäle ergänzen → Grad und Ende lesen**

Bei einer schlechten lokalen Form darf die Werkstatt eine Gesamtkarte oder Besitzererweiterung lernen. Sie darf dafür keinen Kern umbenennen.

## Was die 3.888 Ereignisse lehren

- Es gibt **912** verschiedene Komponentenrezepte.
- Die vollständige 19×19-Tafel enthält {pair_status_counts['ADJACENT_ATTESTED']} direkt belegte, {pair_status_counts['GAPPED_ATTESTED']} nur eingebettet/geordnet belegte und {pair_status_counts['UNSEEN_ORDERED_PAIR']} noch ungesehene Paare.
- `Y` ist der große Referenzschluss innerhalb einer Karte, aber kein Aussagenende; `DY` bleibt der separate lizenzierte Schluss.
- `OK`, `CH` und `SH` sind die produktivsten Handlungsköpfe. `AIIN`, `AIN`, `AL`, `AR`, `OR` und `Y` sind bevorzugte Argumente oder Enden.
- `CHK` und `C<K>H` behalten denselben Kern `CH+K`; die lineare Form eröffnet gewöhnlich die Handlung, die eingebettete Form sitzt im äußeren Rahmen.

## Vier feste Vorhersagen für später freigegebene Seiten

1. **`chain = CH+AIN = eine Portion nehmen`** — stärkste Vorhersage.
2. **`pain = P+AIN = eine Portion einsetzen`**.
3. **`paiin = P+AIIN = nach Maß einsetzen`**.
4. **`lair = L+AIR = Verbindung im bezeichneten Lauf`** — bewusst schwächer und möglicherweise absichtlich vermieden.

Alle vier direkten Zweierformen fehlen im aktuellen 22-Seiten-Lauf. `CH…AIN` ist aber bereits dreimal mit einem eingeschobenen Kern belegt, `P…AIIN` einmal; nur `P+AIN` und `L+AIR` sind noch völlig ungesehen. Wenn eine direkte Form später erscheint, steht ihre Erstlesung bereits fest. Wenn sie wiederholt nicht passt, verlieren wir die jeweilige Kompositionsregel; wir ändern nicht nachträglich AIN, AIIN, L oder AIR.

## Warum das für neue Seiten wichtiger ist als weitere Übersetzung

Mit Pass 1016 musste ein neuer Textteil 31 Kategorien tragen. Jetzt muss er zusätzlich die bekannten Links-/Rechtsvalenzen respektieren. Dadurch kann eine neue Oberfläche nicht mehr beliebig „medizinisch“ oder „technisch“ ausgeschmückt werden. Ihre erste Lesung folgt aus Kern, Position und Besitzer, bevor eine flüssige deutsche Fassung geschrieben wird.
"""
    report_path = HERE / "PASS1017_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "pass": 1017,
        "source_contract_sha256": sha256(SOURCE_CONTRACT),
        "source_statements_sha256": sha256(SOURCE_STATEMENTS),
        "source_channels_sha256": sha256(SOURCE_CHANNELS),
        "portable_root_count": len(roots),
        "local_channel_count": len(local_channels),
        "event_count": len(events),
        "component_recipe_count": len({tuple(event["tokens"]) for event in events}),
        "ordered_pair_count": len(pair_rows),
        "pair_status_counts": dict(sorted(pair_status_counts.items())),
        "fresh_prediction_count": len(prediction_rows),
        "new_root_count": 0,
        "result": "FORWARD_COMPOSITION_COMPILER_COMPLETE",
        "outputs": {
            valency_path.name: sha256(valency_path),
            pair_path.name: sha256(pair_path),
            prediction_path.name: sha256(prediction_path),
            report_path.name: sha256(report_path),
        },
    }
    (HERE / "PASS1017_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
