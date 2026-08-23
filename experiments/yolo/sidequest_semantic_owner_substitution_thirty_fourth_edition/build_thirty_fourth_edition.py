#!/usr/bin/env python3
"""Build owner-substitution exercises from already observed atom sequences."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"


# id, atoms, invariant nucleus, Herbal expansion, Bio expansion, Astro expansion,
# changed local nouns, warning
EXERCISES = [
    ("OS01", "AIIN", "vorgegebener Wert", "vorgeschriebenes Maß des Pflanzenansatzes", "Sollstand der Beckencharge", "Wert des gewählten Himmelsplatzes", "Maß|Sollstand|Tabellenwert", "AIIN benennt nicht selbst die Maßeinheit"),
    ("OS02", "AIN", "abgeteilte Einheit", "Portion des Pflanzenstoffs", "Teilcharge des Beckengangs", "gezählter Ring- oder Feldabschnitt", "Pflanzenportion|Teilcharge|Teilabschnitt", "AIN ist nicht AIIN und keine Zahl an sich"),
    ("OS03", "IIN", "Arbeitsstufe", "Stufe der Zubereitung", "Stufe des örtlichen Betriebs", "Stufe der Tafelauswahl", "Zubereitungsstufe|Betriebsstufe|Tafelstufe", "IIN trägt keinen konkreten Zustand ohne Besitzer"),
    ("OS04", "AL", "bezeichnetes Ziel", "Stelle für den Pflanzenansatz", "örtliche Zielstation", "Zielsektor der Tafel", "Anwendungsstelle|Station|Sektor", "AL ist keine Körperstelle aus eigener Kraft"),
    ("OS05", "AR", "bezeichnete Quelle", "Ausgang aus dem Pflanzenvorrat", "Quell- oder Einlassstation", "Ausgangssektor oder Bezugswert", "Vorrat|Einlass|Ausgangssektor", "AR benennt weder Gefäß noch Stern"),
    ("OS06", "AIR", "sichtbarer Lauf oder Bahn", "Arbeitsflüssigkeit läuft durch Pflanzenstoff", "Flüssigkeitslauf zwischen Beckenstationen", "Bahn im sichtbaren Rad", "Arbeitsflüssigkeit|Beckenlauf|Himmelsbahn", "AIR ist nicht allgemein das Wort Wasser"),
    ("OS07", "OL", "im selben Gang fortsetzen", "denselben Pflanzenansatz weiterführen", "dasselbe Stationsprogramm fortsetzen", "im selben Ring oder Band fortfahren", "Ansatz|Stationsgang|Ringband", "OL sagt nicht, was fortgesetzt wird"),
    ("OS08", "OT+AR", "danach von der bezeichneten Quelle", "danach vom Pflanzenvorrat nehmen", "danach von der Quellstation weiterarbeiten", "danach vom Ausgangssektor lesen", "Pflanzenvorrat|Quellstation|Ausgangssektor", "OT ordnet, AR adressiert; keines benennt die Sache selbst"),
    ("OS09", "OR", "laufender Arbeitssatz", "Pflanzenzubereitung als Ansatz", "örtliche Arbeitscharge", "Bedingungs- oder Tabellensatz", "Zubereitung|Charge|Tabellensatz", "OR ist weder Öl noch ein einzelner Stoff"),
    ("OS10", "HO", "Eingangsposten", "Pflanzenstoff oder Zusatz eingeben", "neue Charge in die Station geben", "Tafeleingang oder Himmelsobjekt einsetzen", "Zutat|Charge|Tafeleingang", "HO ist kein universelles Pflanzenwort"),
    ("OS11", "CHEEY", "sichtbares Ergebnis", "klaren Auszug ablesen oder nehmen", "sichtbaren Ablaufzustand prüfen", "sichtbaren Tabellenwert ablesen", "Klarauszug|Ablaufzustand|Ablesewert", "CHEEY bedeutet weder klar noch Flüssigkeit allein"),
    ("OS12", "OK+AIIN", "auf Vorgabewert setzen", "Pflanzenansatz auf Sollmaß stellen", "Beckencharge auf Sollstand setzen", "gewählten Tabellenwert aktivieren", "Sollmaß|Sollstand|Tafelwert", "OK aktiviert; AIIN liefert die Vorgabe"),
    ("OS13", "OK+AIN", "eine Einheit einsetzen", "eine Pflanzenportion zugeben", "eine Teilcharge einsetzen", "einen gezählten Abschnitt aktivieren", "Portion|Teilcharge|Abschnitt", "die Portion bleibt besitzerabhängig"),
    ("OS14", "OK+AL", "am Ziel ansetzen", "Ansatz an die sichtbare Stelle bringen", "Zielstation in Betrieb nehmen", "Zielsektor aktivieren", "Anwendungsstelle|Zielstation|Zielsektor", "kein Körperteil ist in OK oder AL enthalten"),
    ("OS15", "OK+AR", "von der Quelle ansetzen", "vom Pflanzenvorrat neu ansetzen", "Quellstation öffnen oder aktivieren", "Ausgangssektor aktivieren", "Pflanzenvorrat|Quellstation|Ausgangssektor", "kein bestimmtes Gefäß ist codiert"),
    ("OS16", "OK+OL", "Fortsetzung neu aufnehmen", "laufenden Pflanzenansatz wieder aufnehmen", "denselben Stationsgang wieder einsetzen", "Fortsetzung im Ring aktivieren", "Ansatz|Stationsgang|Ringfortsetzung", "OK+OL ist nicht automatisch wiederholen"),
    ("OS17", "OT+OL", "danach im selben Verfahren weiter", "mit der nächsten Fraktion im selben Ansatz fortfahren", "an der nächsten Station dasselbe Programm fortführen", "am nächsten Platz im selben Ring weitergehen", "Fraktion|Station|Platz", "OT wechselt den Posten, OL erhält das Verfahren"),
    ("OS18", "OL+OR", "fortgeführter Arbeitssatz", "weitergeführte Pflanzenzubereitung", "fortgesetzte Arbeitscharge", "fortgesetzter Bedingungs- oder Tabellensatz", "Zubereitung|Charge|Bedingungssatz", "der Sachbereich stammt ausschließlich vom Besitzer"),
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


def joined(values: set[str]) -> str:
    return "|".join(sorted(values))


def main() -> None:
    ledger = read_tsv(LEDGER)
    by_atoms: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        by_atoms[row["atom_sequence"]].append(row)

    rows = []
    for exercise in EXERCISES:
        exercise_id, atoms, nucleus, herbal, bio, astro, local_nouns, warning = exercise
        observed = by_atoms.get(atoms, [])
        if not observed:
            raise RuntimeError(f"unobserved atom sequence: {atoms}")
        registers = {r["register"] for r in observed}
        if registers != {"PROSE", "ASTRO"}:
            raise RuntimeError(f"{atoms} is not observed in both registers: {registers}")
        rows.append({
            "exercise_id": exercise_id,
            "invariant_atoms": atoms,
            "invariant_nucleus_de": nucleus,
            "observed_occurrences": len(observed),
            "observed_surface_types": joined({r["visible_surface"] for r in observed}),
            "observed_pages": joined({r["page"] for r in observed}),
            "herbal_owner": "sichtbare abgebildete Pflanze oder ihr laufender Ansatz",
            "herbal_expansion_de": herbal,
            "biological_owner": "sichtbares Becken, Gefäß oder örtliche Station",
            "biological_expansion_de": bio,
            "astro_owner": "sichtbarer Ring, Sternplatz oder lokales Tabellenfeld",
            "astro_expansion_de": astro,
            "changed_local_nouns": local_nouns,
            "invariant_prediction_de": f"Bei jedem Besitzer bleibt der Kern ‚{nucleus}‘ erhalten.",
            "overreading_warning_de": warning,
            "status": "CREATIVE_OWNER_SUBSTITUTION__NOT_MANUSCRIPT_TEXT",
        })

    fields = list(rows[0])
    write_tsv(OUT / "THIRTY_FOURTH_OWNER_SUBSTITUTIONS.tsv", rows, fields)

    lines = [
        "# Drei Besitzer, dieselbe Karte",
        "",
        "Diese Blätter sind Diktierübungen, keine neu entdeckten Manuskriptzeilen. Der Meister",
        "hält die Kartenfolge fest und zeigt nacheinander Pflanze, Becken und Himmelsfeld.",
        "Der Lehrling muss den gemeinsamen Kern sprechen und nur die lokalen Sachnomen ändern.",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['exercise_id']} — `{row['invariant_atoms']}`",
            "",
            f"Gemeinsamer Kern: **{row['invariant_nucleus_de']}**.",
            "",
            f"- am Pflanzenbild: {row['herbal_expansion_de']};",
            f"- am Beckenbild: {row['biological_expansion_de']};",
            f"- an der Himmelstafel: {row['astro_expansion_de']}.",
            "",
            f"Geändert werden nur `{row['changed_local_nouns']}`. Warnung: {row['overreading_warning_de']}.",
            "",
        ])
    (OUT / "THIRTY_FOURTH_THREE_OWNER_COPYBOOK.md").write_text("\n".join(lines), encoding="utf-8")

    nucleus_rows = []
    for row in rows:
        nucleus_rows.append({
            "atoms": row["invariant_atoms"],
            "portable_nucleus_de": row["invariant_nucleus_de"],
            "plant_expansion_de": row["herbal_expansion_de"],
            "station_expansion_de": row["biological_expansion_de"],
            "celestial_expansion_de": row["astro_expansion_de"],
            "not_encoded_in_nucleus": row["changed_local_nouns"],
        })
    write_tsv(
        OUT / "THIRTY_FOURTH_OWNER_NUCLEI.tsv",
        nucleus_rows,
        ["atoms", "portable_nucleus_de", "plant_expansion_de", "station_expansion_de", "celestial_expansion_de", "not_encoded_in_nucleus"],
    )

    summary = {
        "status": "PASS",
        "counts": {
            "owner_substitution_exercises": len(rows),
            "owner_realizations": len(rows) * 3,
            "cross_register_atom_sequences": len(rows),
            "source_visible_groups": len(ledger),
        },
        "source": {str(LEDGER.relative_to(ROOT)): sha256(LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
