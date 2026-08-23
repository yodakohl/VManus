#!/usr/bin/env python3
"""Build the creative minimal-pair teaching book for the fixed ten pages."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_487_SURFACE_DICTIONARY.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"


# id, axis, left atoms, right atoms, left reading, right reading,
# changed slot, compact teaching rule, verdict
PAIRS = [
    ("Q01", "MENGE", "AIIN", "AIN", "Sollwert", "Portion", "AIIN↔AIN", "AIIN gibt die Vorgabe, AIN den abgeteilten Stoff", "STARK"),
    ("Q02", "MENGE", "AIIN", "IIN", "Sollwert", "Arbeitsstufe", "AIIN↔IIN", "AIIN beantwortet wie viel, IIN welche Stufe", "STARK"),
    ("Q03", "MENGE", "OK+AIIN", "OK+AIN", "auf Sollwert ansetzen", "eine Portion ansetzen", "AIIN↔AIN", "OK bleibt gleich; nur Vorgabe gegen Teilmenge wechselt", "STARK"),
    ("Q04", "MENGE", "Y+AIIN", "Y+AIN", "Sollwert dieses Postens", "Portion dieses Postens", "AIIN↔AIN", "Y hält denselben Gegenstand, die Mengenart wechselt", "STARK"),
    ("Q05", "MENGE", "AL+AIIN", "AL+AIN", "Sollwert am Ziel", "Portion am Ziel", "AIIN↔AIN", "Zieladresse bleibt; Mengenart wechselt", "MITTEL"),
    ("Q06", "MENGE", "OD+IIN", "OD+AIN", "markierte Stufe", "markierte Portion", "IIN↔AIN", "OD markiert, aber bestimmt nicht selbst die Mengenart", "MITTEL"),
    ("D01", "RICHTUNG", "AL", "AR", "Ziel", "Quelle", "AL↔AR", "AL blickt hin, AR blickt her", "STARK"),
    ("D02", "RICHTUNG", "AR", "AIR", "Quelle", "Lauf oder Bahn", "AR↔AIR", "AIR ist der Weglauf zwischen Adressen, nicht bloß eine zweite Quelle", "MITTEL"),
    ("D03", "RICHTUNG", "OK+AL", "OK+AR", "am Ziel ansetzen", "von der Quelle ansetzen", "AL↔AR", "OK bleibt gleich; nur Ziel gegen Quelle wechselt", "STARK"),
    ("D04", "RICHTUNG", "OT+AL", "OT+AR", "danach zum Ziel", "danach von der Quelle", "AL↔AR", "OT ordnet nur; AL und AR tragen die Richtung", "STARK"),
    ("D05", "RICHTUNG", "YK+AL", "YK+AR", "Ziel der Klasse", "Quelle der Klasse", "AL↔AR", "dieselbe Tabellenklasse kann Quelle oder Ziel adressieren", "STARK"),
    ("D06", "RICHTUNG", "CHD+AL", "CHD+AR", "zum Ziel umsetzen", "von der Quelle umsetzen", "AL↔AR", "CHD ist die Bewegung, AL oder AR ihre Adresse", "STARK"),
    ("D07", "RICHTUNG", "L+CHD+AL", "L+CHD+AR", "zum nachgeordneten Ziel führen", "aus der nachgeordneten Quelle abführen", "AL↔AR", "L+CHD bleibt; die letzte Adresse kehrt den Blick", "MITTEL"),
    ("O01", "REIHENFOLGE", "OL", "OT", "fortsetzen", "danach oder nächster", "OL↔OT", "OL hält denselben Gang, OT eröffnet den Folgeposten", "STARK"),
    ("O02", "REIHENFOLGE", "OL+OR", "OT+OR", "Fortsetzungsansatz", "Folgeansatz", "OL↔OT", "OR bleibt derselbe Ansatzkörper; Ordnung wechselt", "STARK"),
    ("O03", "REIHENFOLGE", "OL+AR", "OT+AR", "von der Quelle weiter", "danach von der Quelle", "OL↔OT", "AR bleibt Quelle; OL setzt fort, OT schaltet weiter", "MITTEL"),
    ("O04", "REIHENFOLGE", "OL+Y", "OT+Y", "diesen Posten weiterführen", "nächsten Posten nehmen", "OL↔OT", "Y bleibt der Postenträger; Ordnung entscheidet derselbe oder nächster", "STARK"),
    ("O05", "REIHENFOLGE", "OL+CHD+CLOSE", "OT+CHD+CLOSE", "weiter umsetzen und schließen", "folgenden Posten umsetzen und schließen", "OL↔OT", "Operation und Schluss bleiben; nur Kontinuität gegen Folge wechselt", "STARK"),
    ("G01", "GRAD", "OK+E+Y", "OK+EE+Y", "kurz ansetzen", "länger ansetzen", "E↔EE", "ein E-Schritt verlängert denselben offenen OK-Gang", "STARK"),
    ("G02", "GRAD", "OK+E+CLOSE", "OK+EE+CLOSE", "kurz ansetzen und schließen", "länger ansetzen und schließen", "E↔EE", "derselbe geschlossene OK-Gang bekommt längere Dauer", "STARK"),
    ("G03", "GRAD", "OK+EE+CLOSE", "OK+EEE+CLOSE", "länger ansetzen und schließen", "vollständig ansetzen und schließen", "EE↔EEE", "das dritte E steigert länger zu vollständig", "DÜNN_ABER_SAUBER"),
    ("G04", "GRAD", "OT+E+CLOSE", "OT+EE+CLOSE", "kurze Folge und Schluss", "lange Folge und Schluss", "E↔EE", "OT und Schluss bleiben, nur der Grad wächst", "STARK"),
    ("G05", "GRAD", "SOLK+E+Y", "SOLK+EE+Y", "kurz sammeln", "länger sammeln", "E↔EE", "dieselbe Sammelstelle hält den Posten länger", "MITTEL"),
    ("G06", "GRAD", "SHED+E+CLOSE", "SHED+EE+CLOSE", "kurz absetzen und schließen", "länger absetzen und schließen", "E↔EE", "derselbe Absetzgang wird verlängert", "STARK"),
    ("G07", "GRAD", "CHK+E+Y", "CHK+EE+Y", "kurz wärmen", "länger warm halten", "E↔EE", "der Wärmekern bleibt, die Haltestufe wächst", "STARK"),
    ("G08", "GRAD", "YK+E+OD+Y", "YK+EE+OD+Y", "Klassenposten kurz markieren", "Klassenposten länger markieren", "E↔EE", "Grad wirkt auch in der lokalen Tabelle gleich", "MITTEL"),
    ("G09", "GRAD", "OK+E+OD+AL", "OK+EE+OD+AL", "markiertes Ziel kurz aktivieren", "markiertes Ziel länger aktivieren", "E↔EE", "Ziel und Markierung bleiben; Aktivierungsgrad wächst", "MITTEL"),
    ("X01", "ENDPUNKT", "CHD+Y", "CHD+CLOSE", "laufenden Posten umsetzen", "umsetzen und den Schritt schließen", "Y↔CLOSE", "gleicher Prozesskörper, offener Referent gegen Abschluss", "STARK"),
    ("X02", "ENDPUNKT", "OK+E+Y", "OK+E+CLOSE", "kurz ansetzen und offen lassen", "kurz ansetzen und schließen", "Y↔CLOSE", "gleicher kurzer OK-Gang, nur Fortsetzbarkeit wechselt", "STARK"),
    ("X03", "ENDPUNKT", "OK+EE+Y", "OK+EE+CLOSE", "länger ansetzen und offen lassen", "länger ansetzen und schließen", "Y↔CLOSE", "gleicher langer OK-Gang, nur Fortsetzbarkeit wechselt", "STARK"),
    ("X04", "ENDPUNKT", "SOLK+EE+Y", "SOLK+EE+CLOSE", "länger sammeln und offen lassen", "länger sammeln und schließen", "Y↔CLOSE", "Sammelkern und Grad bleiben, nur der Endpunkt wechselt", "MITTEL"),
    ("X05", "ENDPUNKT", "OL", "OL+CLOSE", "fortsetzen", "Fortsetzung abschließen", "+CLOSE", "OL allein hält offen; die lizenzierte Schlusskarte beendet", "STARK"),
    ("X06", "ENDPUNKT", "L+Y", "L+CLOSE", "aktuellen Posten abführen", "abführen und beenden", "Y↔CLOSE", "L bleibt Abgang; offener Posten gegen Abschluss", "MITTEL"),
    ("P01", "ARGUMENT", "CTH+Y", "CTH+AIIN", "diesen Posten bereit halten", "Bereitsollwert", "Y↔AIIN", "CTH nimmt entweder den Gegenstand oder seine Vorgabe", "MITTEL"),
    ("P02", "ARGUMENT", "KCH+Y", "KCH+AL", "diesen Posten bearbeiten", "am Ziel bearbeiten", "Y↔AL", "KCH bleibt Handlung; Argument wechselt Gegenstand gegen Ort", "STARK"),
    ("P03", "ARGUMENT", "HO+Y", "HO+AL", "diese Zutat oder Eingabe", "Eingabe zum Ziel", "Y↔AL", "HO benennt den Eingangsposten, AL gibt ihm ein Ziel", "MITTEL"),
    ("P04", "ARGUMENT", "Y+CHEEY", "OT+CHEEY", "aktuelles sichtbares Ergebnis", "nächstes sichtbares Ergebnis", "Y↔OT", "CHEEY bleibt Ablese- oder Sichtresultat; Bezug wechselt", "MITTEL"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(values: set[str] | list[str]) -> str:
    return "|".join(sorted(v for v in values if v and v != "NONE"))


def main() -> None:
    dictionary = read_tsv(DICTIONARY)
    ledger = read_tsv(LEDGER)
    surfaces: dict[str, list[dict[str, str]]] = defaultdict(list)
    events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dictionary:
        atoms = row["common_atom_sequences"]
        if "|" not in atoms and ":" not in atoms:
            surfaces[atoms].append(row)
    for row in ledger:
        events[row["atom_sequence"]].append(row)

    output = []
    for pair_id, axis, left, right, left_reading, right_reading, slot, rule, verdict in PAIRS:
        if left not in surfaces or right not in surfaces or left not in events or right not in events:
            missing = [x for x in (left, right) if x not in surfaces or x not in events]
            raise RuntimeError(f"{pair_id}: missing atom sequence(s): {missing}")
        lsur = surfaces[left]
        rsur = surfaces[right]
        lev = events[left]
        rev = events[right]
        output.append({
            "pair_id": pair_id,
            "axis": axis,
            "left_atoms": left,
            "right_atoms": right,
            "changed_slot": slot,
            "left_surface_types": compact({r["visible_surface"] for r in lsur}),
            "right_surface_types": compact({r["visible_surface"] for r in rsur}),
            "left_occurrences": len(lev),
            "right_occurrences": len(rev),
            "left_pages": compact({r["page"] for r in lev}),
            "right_pages": compact({r["page"] for r in rev}),
            "left_example": f"{lev[0]['source_group_id']}:{lev[0]['visible_surface']}:{lev[0]['visible_owner']}",
            "right_example": f"{rev[0]['source_group_id']}:{rev[0]['visible_surface']}:{rev[0]['visible_owner']}",
            "left_reading_de": left_reading,
            "right_reading_de": right_reading,
            "teaching_rule_de": rule,
            "verdict": verdict,
        })

    pair_fields = list(output[0])
    write_tsv(OUT / "THIRTY_THIRD_MINIMAL_PAIRS.tsv", output, pair_fields)

    axis_order = ["MENGE", "RICHTUNG", "REIHENFOLGE", "GRAD", "ENDPUNKT", "ARGUMENT"]
    lines = [
        "# Lehrbuch der kleinsten Bedeutungsunterschiede",
        "",
        "Der Lehrling sieht jeweils zwei tatsächlich vorhandene Kartenfamilien. Der Meister",
        "ändert nur eine gelehrte Achse und spricht den kleinsten Bedeutungsunterschied.",
        "Rendererformen dürfen wechseln; die atomare Kontrastregel bleibt gleich.",
        "",
    ]
    for axis in axis_order:
        lines.extend([f"## {axis.title()}", ""])
        for row in [r for r in output if r["axis"] == axis]:
            lines.extend([
                f"### {row['pair_id']}: `{row['left_atoms']}` ↔ `{row['right_atoms']}`",
                "",
                f"- links: **{row['left_reading_de']}** — Formen `{row['left_surface_types']}`; Beispiel `{row['left_example']}`; {row['left_occurrences']} Vorkommen;",
                f"- rechts: **{row['right_reading_de']}** — Formen `{row['right_surface_types']}`; Beispiel `{row['right_example']}`; {row['right_occurrences']} Vorkommen;",
                f"- Lehrsatz: {row['teaching_rule_de']};",
                f"- Arbeitsurteil: `{row['verdict']}`.",
                "",
            ])
    (OUT / "THIRTY_THIRD_APPRENTICE_CONTRAST_BOOK.md").write_text("\n".join(lines), encoding="utf-8")

    stem_specs = [
        ("AIIN", "SOLLWERT", "PORTABEL", "nicht mit AIN oder IIN verschmelzen"),
        ("AIN", "PORTION", "PORTABEL", "abgeteilte Menge, kein Sollwert"),
        ("IIN", "STUFE", "PORTABEL", "Prozess- oder Tabellenstufe"),
        ("AL", "ZIEL", "PORTABEL", "hin zur bezeichneten Adresse"),
        ("AR", "QUELLE", "PORTABEL", "her von der bezeichneten Adresse"),
        ("AIR", "LAUF_BAHN", "BESITZER_EXPANDIERT", "nasser Besitzer: Flüssigkeitslauf; Rad: Bahn"),
        ("OL", "FORTSETZEN", "PORTABEL", "derselbe aktive Gang"),
        ("OT", "FOLGEND", "PORTABEL", "nächster Gang oder Posten"),
        ("E", "KURZ", "GEBUNDEN", "nur in lizenzierten Gradfamilien"),
        ("EE", "LAENGER", "GEBUNDEN", "nur in lizenzierten Gradfamilien"),
        ("EEE", "VOLL", "DÜNN_GEBUNDEN", "sauber, aber nur zwei Gruppen"),
        ("Y", "DIESER_POSTEN", "PORTABEL_GEBUNDEN", "Referent, nicht automatisch offen"),
        ("CLOSE", "SCHLUSS", "KARTENGEBUNDEN", "kein freies sichtbares dy-Morphem"),
        ("OK", "ANSETZEN", "PORTABEL", "Argument und Grad folgen"),
        ("CHEEY", "SICHTBARES_ERGEBNIS", "BESITZER_EXPANDIERT", "Klarauszug oder Tabellenablesung"),
        ("HO", "EINGANGSPOSTEN", "BESITZER_EXPANDIERT", "Zutat oder Tabelleneingabe"),
    ]
    stem_rows = []
    for symbol, value, status, caution in stem_specs:
        related = [r for r in output if symbol in r["left_atoms"].split("+") or symbol in r["right_atoms"].split("+")]
        stem_rows.append({
            "symbol": symbol,
            "atomic_value_de": value,
            "status": status,
            "minimal_pair_count": len(related),
            "pair_ids": compact({r["pair_id"] for r in related}),
            "caution_de": caution,
        })
    write_tsv(
        OUT / "THIRTY_THIRD_STEM_VERDICTS.tsv",
        stem_rows,
        ["symbol", "atomic_value_de", "status", "minimal_pair_count", "pair_ids", "caution_de"],
    )

    summary = {
        "status": "PASS",
        "counts": {
            "minimal_pairs": len(output),
            "axes": len({r["axis"] for r in output}),
            "stem_verdicts": len(stem_rows),
            "strong_pairs": sum(r["verdict"] == "STARK" for r in output),
            "medium_pairs": sum(r["verdict"] == "MITTEL" for r in output),
            "thin_clean_pairs": sum(r["verdict"] == "DÜNN_ABER_SAUBER" for r in output),
        },
        "sources": {
            str(DICTIONARY.relative_to(ROOT)): sha256(DICTIONARY),
            str(LEDGER.relative_to(ROOT)): sha256(LEDGER),
        },
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
