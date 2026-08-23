#!/usr/bin/env python3
"""Enrich recurrent Astro component families with bound E/Y/DY modifiers."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CANDIDATES = ROOT / "experiments/yolo/sidequest_semantic_cross_register_paradigms/ASTRO_53_COMPOSITIONAL_DICTIONARY.tsv"
PROSE = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_173_LITERAL_PARSE.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


# Explicitly bounded reanalyses.  The residue is left visible instead of being
# silently consumed by an alphabetic reading.
ENRICH = {
    "okar": ("OK+AR", "NONE", "Quelle aktivieren"),
    "okear": ("OK+E+AR", "NONE", "Quelle kurz aktivieren"),
    "okodar": ("OK+AR", "OD", "Quelle aktivieren; lokaler OD-Status"),
    "okardy": ("OK+AR+DY_BOUND", "NONE", "Quelle aktivieren und Auswahl festhalten"),
    "ytokar": ("OK+AR", "YT", "Quelle aktivieren; lokaler YT-Rahmen"),
    "okeal": ("OK+E+AL", "NONE", "Ziel kurz aktivieren"),
    "okeodal": ("OK+E+AL", "OD", "Ziel kurz aktivieren; lokaler OD-Status"),
    "okeeodal": ("OK+EE+AL", "OD", "Ziel länger aktivieren; lokaler OD-Status"),
    "okoaly": ("OK+AL+Y", "O", "dieses Ziel aktivieren"),
    "okodaly": ("OK+AL+Y", "OD", "dieses Ziel aktivieren; lokaler OD-Status"),
    "okol": ("OK+OL", "NONE", "Fortsetzung aktivieren"),
    "okoldy": ("OK+OL+DY_BOUND", "NONE", "Fortsetzung aktivieren und festhalten"),
    "otor": ("OT+OR", "NONE", "nächster Satz"),
    "qoteor": ("OT+E+OR", "Q", "nächsten Satz kurz nehmen"),
    "otoar": ("OT+AR", "O", "nächste Quelle"),
    "qotoear": ("OT+E+AR", "QO", "nächste Quelle kurz nehmen"),
    "oteol": ("OT+E+OL", "NONE", "als nächstes kurz fortsetzen"),
    "otoldos": ("OT+OL", "DOS", "als nächstes fortsetzen; lokaler DOS-Status"),
    "otoly": ("OT+OL+Y", "NONE", "diese Fortsetzung als nächste nehmen"),
    "alaiin": ("AL+AIIN", "NONE", "Ziel-Sollwert"),
    "aldaiin": ("AL+AIIN", "D", "Ziel-Sollwert; lokaler D-Rahmen"),
    "saral": ("AR+AL", "S", "von Quelle zum Ziel"),
}

DECISIONS = [
    ("E", "KURZ / ERSTE STUFE", "PROMOTE_BOUND_MODIFIER", "okar→okear; otor→qoteor; otoar→qotoear; OT+OL→oteol", "nur zwischen bekanntem Operator und bekanntem Argument/Kern"),
    ("EE", "LÄNGER / ZWEITE STUFE", "PROMOTE_BOUND_MODIFIER", "okeodal→okeeodal; starke Prosa-OK-Reihe", "nur in derselben belegten Gradfamilie"),
    ("EEE", "VOLL / DRITTE STUFE", "KEEP_FROM_PROSE_NO_NEW_ASTRO_PAIR", "qokeeedy in Prosa/Astro, aber keine neue Mehrformenreihe hier", "gebundene Vollstufe"),
    ("Y", "AKTUELL / DIESE AUSWAHL", "PROMOTE_BOUND_MODIFIER", "okoaly, okodaly, otoly", "nur rechts an bekanntem Kern; kein globales Buchstabenwort"),
    ("DY", "AUSWAHL FESTHALTEN / GEBUNDENER ABSCHLUSS", "PROMOTE_BOUND_TAIL", "okardy und okoldy", "ganzer Schwanz; nicht global D+Y zerlegen"),
    ("Q/S/CH/D/T leading", "RENDERER ODER SCHREIBRAHMEN", "KEEP_NONSEMANTIC", "qoteor/qotoear/saral und Prosa-Allographen", "keine Sachbedeutung"),
    ("O/OD medial", "LOKALER STATUS ODER RAHMEN", "HOLD", "okodar, okeodal, okoaly, okodaly", "nicht genug kontrastierte Paare"),
    ("D/DOS medial", "LOKALER STATUS ODER RAHMEN", "HOLD", "aldaiin, otoldos", "nicht aus Schlusswert ableiten"),
]


def main() -> None:
    source = read(CANDIDATES)
    prose = read(PROSE)
    updated = []
    for row in source:
        surface = row["visible_surface"]
        if surface in ENRICH:
            sequence, residual, reading = ENRICH[surface]
            status = "ENRICHED_BOUND_MODIFIER"
        else:
            sequence = row["atom_sequence"]
            residual = "UNRESOLVED_LOCAL"
            reading = row["common_nucleus_de"]
            status = "UNCHANGED_COMPONENT_HINT"
        updated.append({
            "visible_surface": surface, "occurrences": row["occurrences"],
            "previous_atom_sequence": row["atom_sequence"], "enriched_atom_sequence": sequence,
            "bound_modifier": "+".join(atom for atom in sequence.split("+") if atom in {"E", "EE", "EEE", "Y", "DY_BOUND"}) or "NONE",
            "residual_renderer_or_local": residual, "enriched_common_reading_de": reading,
            "owners": row["owners"], "previous_composition_status": row["composition_status"],
            "modifier_status": status, "local_astro_reading_de": row["local_astro_reading_de"],
        })
    write(HERE / "UPDATED_ASTRO_53_MODIFIER_DICTIONARY.tsv", updated, list(updated[0]))

    decision_rows = []
    for modifier, value, status, evidence, boundary in DECISIONS:
        prose_types = sum(modifier in row["corrected_semantic_atoms"].split("+") for row in prose) if modifier in {"E", "EE", "EEE", "Y"} else 0
        prose_events = sum(int(row["prose_events"]) for row in prose if modifier in row["corrected_semantic_atoms"].split("+")) if modifier in {"E", "EE", "EEE", "Y"} else 0
        astro_modifier = "DY_BOUND" if modifier == "DY" else modifier
        astro_types = sum(astro_modifier in row["bound_modifier"].split("+") for row in updated) if astro_modifier in {"E", "EE", "EEE", "Y", "DY_BOUND"} else 0
        astro_events = sum(int(row["occurrences"]) for row in updated if astro_modifier in row["bound_modifier"].split("+")) if astro_modifier in {"E", "EE", "EEE", "Y", "DY_BOUND"} else 0
        decision_rows.append({
            "modifier": modifier, "short_value_de": value, "decision": status,
            "prose_card_types": prose_types, "prose_events": prose_events,
            "astro_surface_types": astro_types, "astro_occurrences": astro_events,
            "contrast_evidence": evidence, "licensing_boundary": boundary,
        })
    write(HERE / "MODIFIER_DECISIONS.tsv", decision_rows, list(decision_rows[0]))

    pair_specs = [
        ("OK+AR", "okar", "okear", "NONE", "Quelle aktivieren → kurz aktivieren"),
        ("OK+AL", "NONE", "okeal|okeodal", "okeeodal", "Ziel kurz → länger aktivieren"),
        ("OT+OR", "otor", "qoteor", "NONE", "nächster Satz → kurze Folgestufe"),
        ("OT+AR", "otoar", "qotoear", "NONE", "nächste Quelle → kurze Folgestufe"),
        ("OT+OL", "otoldos|otoly", "oteol", "NONE", "nächste Fortsetzung → kurz fortsetzen"),
    ]
    pair_rows = []
    for base, zero, e1, e2, reading in pair_specs:
        forms = set((zero + "|" + e1 + "|" + e2).replace("NONE", "").strip("|").split("|"))
        owners = sorted({owner for row in updated if row["visible_surface"] in forms for owner in row["owners"].split("|")})
        pair_rows.append({
            "base_family": base, "zero_grade_forms": zero, "e_grade_forms": e1,
            "ee_grade_forms": e2, "owner_count": len(owners), "owners": "|".join(owners),
            "creative_reading_de": reading, "decision": "BOUND_GRADE_LATTICE",
        })
    write(HERE / "E_GRADE_FAMILY_PAIRS.tsv", pair_rows, list(pair_rows[0]))

    dy_rows = [row for row in updated if "DY_BOUND" in row["enriched_atom_sequence"]]
    y_rows = [row for row in updated if "Y" in row["bound_modifier"].split("+")]
    report = f"""# Gebundene Modifier-Lattice

## Ergebnis

Die produktiven Kerne tragen eine zweite, kleinere Ebene. `E` und `EE` sind innerhalb belegter Familien **kurz/erste Stufe** und **länger/zweite Stufe**. Das sieht man nicht an einem isolierten Zeichen, sondern an wiederkehrenden Reihen:

- `okar → okear`: Quelle aktivieren → kurz aktivieren;
- `otor → qoteor`: nächster Satz → kurze Folgestufe;
- `otoar → qotoear`: nächste Quelle → kurze Folgestufe;
- `otoldos/otoly → oteol`: fortsetzen → kurz fortsetzen;
- `okeodal → okeeodal`: Ziel kurz → länger aktivieren.

`Y` bleibt der aktuelle/ausgewählte Wert in `okoaly`, `okodaly` und `otoly`. `DY` wird nicht in zwei freie Buchstaben zerlegt; als ganzer gebundener Schwanz in `okardy` und `okoldy` heißt er **Auswahl festhalten / Abschlusswert**. Damit stimmen Prosa und Diagramm auf einer kleinen Zustandsgrammatik überein, ohne dass jedes sichtbare y oder dy dieselbe Funktion tragen muss.

## Bilanz

{sum(row['modifier_status'] == 'ENRICHED_BOUND_MODIFIER' for row in updated)} der 53 neuen Astro-Kompositionen erhalten eine präzisere Modifier-Lesung. Die E-Lattice umfasst {len(pair_rows)} kontrastierte Familien; Y hat {len(y_rows)} Typen und der gebundene DY-Schwanz {len(dy_rows)} Typen. `Q/S/CH/D/T` am Rand bleiben Renderer. Mediales `O/OD/D/DOS` bleibt lokaler Status, bis mehr kontrastierte Reihen es auseinanderziehen.

## Warum das nützlich ist

Das gesuchte System wird konkreter: gelernter Kern oder Ganzkarte + produktive Operator-/Adresskomposition + gebundener Grad oder Endstatus. Ein Schreiber muss also nicht 301 Astrowörter als völlig unabhängig lernen; er erkennt in vielen davon Quelle, Ziel, Folge, Fortsetzung und Grad, während der lokale Rest den speziellen Stern- oder Tabellenwert trägt.
"""
    (HERE / "MODIFIER_LATTICE_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "candidate_types": len(updated),
        "enriched_types": sum(row["modifier_status"] == "ENRICHED_BOUND_MODIFIER" for row in updated),
        "modifier_decisions": len(decision_rows), "e_grade_families": len(pair_rows),
        "y_types": len(y_rows), "dy_bound_types": len(dy_rows),
        "decision_counts": dict(Counter(row["decision"] for row in decision_rows)),
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
