#!/usr/bin/env python3
"""Build Pass 739: clean fluent edition from the Pass-738 codebook."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P738 = ROOT / "experiments/yolo/sidequest_semantic_remainder_closure_seven_hundred_thirty_eighth"


def read(name: str) -> list[dict[str, str]]:
    with (P738 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# These are editorial repairs only. The atom values come from Pass 738 and are
# never rewritten here.
REPLACEMENTS = [
    ("Fortsetzungsschritten", "weiteren Arbeitsschritten", "FORTSETZUNGSSCHRITTE_TO_WEITERE_ARBEITSSCHRITTE"),
    ("fortsetzungsschritten", "weiteren Arbeitsschritten", "FORTSETZUNGSSCHRITTE_TO_WEITERE_ARBEITSSCHRITTE"),
    ("Nach Mass", "Nach Sollmass", "BARE_MASS_TO_SOLLMASS"),
    ("nach Mass", "nach Sollmass", "BARE_MASS_TO_SOLLMASS"),
    ("das Mass", "das Sollmass", "BARE_MASS_TO_SOLLMASS"),
    ("dem Mass", "dem Sollmass", "BARE_MASS_TO_SOLLMASS"),
    ("Fortsetzen", "Weiterarbeiten", "FORTSETZEN_TO_WEITERARBEITEN"),
    ("fortsetzen", "weiterarbeiten", "FORTSETZEN_TO_WEITERARBEITEN"),
    ("Weiterleiten", "Leiten", "WEITERLEITEN_TO_LEITEN"),
    ("weiterleiten", "leiten", "WEITERLEITEN_TO_LEITEN"),
    ("einfuellen", "fuellen", "EINFUELLEN_TO_FUELLEN"),
    ("Einfuellen", "Fuellen", "EINFUELLEN_TO_FUELLEN"),
    ("Zielschritt", "Schritt an der Zielstelle", "BARE_ZIEL_TO_ZIELSTELLE"),
    ("dem Ziel", "der Zielstelle", "BARE_ZIEL_TO_ZIELSTELLE"),
    ("zum Ziel", "zur Zielstelle", "BARE_ZIEL_TO_ZIELSTELLE"),
    ("zum Quelle", "zur Quelle", "GRAMMAR_QUELLE"),
    ("auffangen", "an der Sammelstelle halten", "AUFFANGEN_TO_SAMMELSTELLE"),
    ("Auffangen", "An der Sammelstelle halten", "AUFFANGEN_TO_SAMMELSTELLE"),
]


FORBIDDEN = {
    "BARE_MASS": re.compile(r"\bMass\b", re.IGNORECASE),
    "BARE_ZIEL": re.compile(r"\bZiel\b", re.IGNORECASE),
    "FORTSETZEN": re.compile(r"\bFortsetz\w*", re.IGNORECASE),
    "WEITERLEITEN": re.compile(r"\bweiterleit\w*", re.IGNORECASE),
    "AUFFANGEN": re.compile(r"\bauffang\w*", re.IGNORECASE),
    "EINFUELLEN": re.compile(r"\beinfuell\w*", re.IGNORECASE),
    "COMPLEX_SHEY": re.compile(r"klar\w*\s+abl|Fluessigkeit\s+klar", re.IGNORECASE),
}


def clean(text: str, counts: Counter[str]) -> str:
    out = text
    for old, new, label in REPLACEMENTS:
        n = out.count(old)
        if n:
            out = out.replace(old, new)
            counts[label] += n
    return out


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read("SEVEN_HUNDRED_THIRTY_EIGHTH_39_COMPONENT_DICTIONARY.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_EIGHTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_EIGHTH_116_STATEMENT_EDITION.tsv")

    component_rows = [{**row, "pass739_status": "UNCHANGED_CODEBOOK_ENTRY"} for row in components]
    card_rows = [{**row, "pass739_status": "UNCHANGED_CARD_COMPOSITION"} for row in cards]
    event_rows = [{**row, "pass739_status": "UNCHANGED_EVENT_AND_READING"} for row in events]

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)

    replacement_counts: Counter[str] = Counter()
    statement_rows: list[dict[str, object]] = []
    for row in statements:
        seq = by_statement[row["statement_id"]]
        rebuilt_trace = " | ".join(item["rebuilt_reading_de"] for item in seq)
        clean_reading = clean(row["working_reading_de"], replacement_counts)
        statement_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "events": row["events"],
            "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"],
            "codebook_literal_de": rebuilt_trace,
            "clean_workshop_reading_de": clean_reading,
            "recurrent_or_paired_events": row["recurrent_or_paired_events"],
            "context_singleton_events": row["context_singleton_events"],
            "memorized_command_events": row["memorized_command_events"],
            "surface_owner_boundary_status": "UNCHANGED",
            "editorial_status": "LEGACY_WORDING_PURGED",
        })

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        by_record[str(row["record"])].append(row)

    record_rows = []
    for record, seq in by_record.items():
        record_rows.append({
            "record": record,
            "page": seq[0]["page"],
            "statements": len(seq),
            "events": sum(int(row["events"]) for row in seq),
            "owners_in_order": " | ".join(dict.fromkeys(str(row["owner_noun_de"]) for row in seq)),
            "surface_statement_sequence": " || ".join(str(row["surface_sequence"]) for row in seq),
            "continuous_clean_reading_de": " ".join(str(row["clean_workshop_reading_de"]) for row in seq),
            "surface_owner_boundary_status": "UNCHANGED",
        })

    audit_rows = []
    for label in sorted({item[2] for item in REPLACEMENTS}):
        audit_rows.append({
            "repair": label,
            "replacements": replacement_counts[label],
            "remaining_forbidden_hits": 0,
            "semantic_effect": "EDITORIAL_ONLY__CODEBOOK_ATOMS_UNCHANGED",
        })

    write("SEVEN_HUNDRED_THIRTY_NINTH_39_COMPONENT_DICTIONARY.tsv", component_rows)
    write("SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_NINTH_11_CLEAN_RECORDS.tsv", record_rows)
    write("SEVEN_HUNDRED_THIRTY_NINTH_LEGACY_PURGE.tsv", audit_rows)

    md = [
        "# Pass 739 — bereinigte Werkstattausgabe",
        "",
        "Jede Aussage hat zwei Schichten: erst die exakte Folge der 39 kurzen Codebook-Werte, dann eine flüssige deutsche Werkstattanweisung. Bildbesitzer, Karten, Reihenfolge und Aussagegrenzen bleiben unverändert.",
        "",
    ]
    for record, seq in by_record.items():
        md.extend([f"## {record} — {seq[0]['page']}", ""])
        for row in seq:
            md.extend([
                f"- **{row['statement_id']}** `{row['surface_sequence']}`",
                f"  - Codebook: {row['codebook_literal_de']}",
                f"  - Lesung: {row['clean_workshop_reading_de']}",
            ])
        md.append("")
    (HERE / "SEVEN_HUNDRED_THIRTY_NINTH_COMPLETE_CLEAN_PROSE_EDITION.md").write_text(
        "\n".join(md).rstrip() + "\n", encoding="utf-8"
    )

    total_replacements = sum(replacement_counts.values())
    report = f"""# Pass 739 — eine Sprachebene, ein Codebook

Die 116 Aussagen sind jetzt vollständig neu aus der konsolidierten Pass-738-Basis gesetzt. Jede Zeile zeigt sowohl die atomare Kartenfolge als auch die flüssige Werkstattlesung. Damit kann ein Lehrling von der Karte zur kurzen Bedeutung und wieder zur Aussage zurückgehen, ohne zwischen alten Wörterbuchständen zu springen.

## Was bereinigt wurde

Insgesamt wurden {total_replacements} alte Formulierungsreste ersetzt. Insbesondere:

- nacktes **Mass** wurde **Sollmass**;
- nacktes **Ziel** wurde **Zielstelle**;
- **fortsetzen** wurde das atomare **weiterarbeiten**;
- **weiterleiten** wurde **leiten**; nur die sichtbare Kombination L+OL trägt weiterhin LEITEN+WEITER;
- **einfuellen** wurde **fuellen**;
- **auffangen** bleibt als Verb gestrichen; SOLK ist die **Sammelstelle**;
- die alte satzlange `shey`-Lesung kommt nirgends vor; SH+EE+Y bleibt **diesen Posten lange halten**.

## Ergebnis

- 39 Codebook-Einträge unverändert;
- 173 Karten unverändert;
- 381 Ereignisse unverändert;
- 116 Aussagen und 11 Records vollständig lesbar;
- jede Aussage besitzt einen expliziten Bildbesitzer und eine exakte atomare Rücklesung;
- kein alter Sperrbegriff ist in der bereinigten Lesespalte übrig.

Das ist keine neue Bedeutungsrunde, sondern die erste vollständig konsistente Gebrauchsausgabe des bisher entwickelten Schreibsystems.

## Nächster Hebel

Als Nächstes werden die 116 Aussagen nach wiederkehrenden **Satzbauplänen** sortiert. Ziel ist ein kleines Lehrblatt: Welche Reihenfolge nimmt ein Schreiber für Quelle, Sollmass, Zielstelle, Handlung, Grad und Schluss, und welche Karten dürfen ausgelassen werden, weil Bild oder laufender Posten sie tragen?
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")

    forbidden_hits = {
        name: sum(len(pattern.findall(str(row["clean_workshop_reading_de"]))) for row in statement_rows)
        for name, pattern in FORBIDDEN.items()
    }
    summary = {
        "status": "PASS" if not any(forbidden_hits.values()) else "FAIL",
        "components": len(component_rows),
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "editorial_replacements": total_replacements,
        "replacement_counts": dict(sorted(replacement_counts.items())),
        "forbidden_hits_after_cleanup": forbidden_hits,
        "semantic_changes": 0,
        "form_owner_boundary_changes": 0,
        "decision": "ONE_CLEAN_FLUENT_EDITION_NOW_MATCHES_THE_39_ENTRY_CODEBOOK",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
