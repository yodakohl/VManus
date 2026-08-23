#!/usr/bin/env python3
"""Apply the prose stem compiler to all 395 fixed-page Astro groups."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ASTRO_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_astro_nomenclator_closure/ASTRO_395_NOMENCLATOR_CLOSED.tsv"
PROSE_SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_230_SURFACE_PARSE.tsv"
PREDICTIONS = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/FORWARD_PREDICTIONS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


# Longest strings first.  Single-letter renderer material, global E grades and
# naked Y are not admitted here; they would make almost every diagram label
# look spuriously compositional.
LITERAL_CUES = [
    ("AIIN", "aiin", "Sollwert/Maß"), ("IIN", "iiin", "Stufe"),
    ("AIR", "air", "Lauf/Bahn"), ("CHEO", "cheo", "Auszug/Ausgabe"),
    ("CKHE", "ckhe", "Seihen/Trennen"), ("CHD", "ched", "Umsetzen"),
    ("CHD", "chd", "Umsetzen"), ("CTH", "cth", "Bereitwert"),
    ("SOLK", "solk", "Sammelplatz"), ("SOLK", "olk", "Sammelplatz"),
    ("SHED", "shed", "Absetz-/Ruhezustand"), ("CKH", "ckh", "Durchlauf/Bahn"),
    ("CHK", "cheek", "Wärmen/Halten"), ("CHK", "chek", "Wärmen/Halten"),
    ("KCH", "kch", "Bearbeiten"), ("HO", "cho", "Eingangsposten"),
    ("HO", "sho", "Eingangsposten"), ("AIN", "ain", "Portion"),
    ("OK", "ok", "Aktivieren"), ("OL", "ol", "Fortsetzen"),
    ("OT", "ot", "Folge"), ("OR", "or", "Ansatz/Satz"),
    ("AL", "al", "Ziel"), ("AR", "ar", "Quelle"), ("TY", "ty", "Teil"),
]


def nonoverlap_cues(surface: str) -> tuple[list[tuple[str, str, int, int, str]], str]:
    candidates = []
    for atom, literal, meaning in LITERAL_CUES:
        for match in re.finditer(re.escape(literal), surface):
            candidates.append((-(match.end() - match.start()), match.start(), match.end(), atom, literal, meaning))
    candidates.sort()
    occupied: set[int] = set()
    chosen = []
    for _neg_len, start, end, atom, literal, meaning in candidates:
        if any(pos in occupied for pos in range(start, end)):
            continue
        occupied.update(range(start, end))
        chosen.append((atom, literal, start, end, meaning))
    chosen.sort(key=lambda item: item[2])
    residual = "".join(char if idx not in occupied else "·" for idx, char in enumerate(surface))
    return chosen, residual


def main() -> None:
    astro = read_tsv(ASTRO_SOURCE)
    prose = read_tsv(PROSE_SURFACES)
    predictions = read_tsv(PREDICTIONS)
    prose_by_surface = {row["visible_surface"]: row for row in prose}

    skeleton_to_prediction: dict[str, dict[str, str]] = {}
    for prediction in predictions:
        for skeleton in prediction["predicted_surface_skeletons"].split("|"):
            skeleton_to_prediction[skeleton] = prediction

    group_rows = []
    types: dict[str, list[dict[str, object]]] = defaultdict(list)
    prediction_hits: dict[str, list[dict[str, object]]] = defaultdict(list)
    for source in astro:
        surface = source["surface_display"]
        cues, residual = nonoverlap_cues(surface)
        cue_atoms = [item[0] for item in cues]
        covered = sum(item[3] - item[2] for item in cues)
        exact_prose = prose_by_surface.get(surface)
        prediction = skeleton_to_prediction.get(surface)
        embedded_predictions = sorted({
            pred["predicted_atom_sequence"]
            for skeleton, pred in skeleton_to_prediction.items()
            if skeleton and skeleton in surface
        })
        if exact_prose:
            transfer_class = "EXACT_PROSE_SURFACE"
        elif prediction:
            transfer_class = "FORWARD_PREDICTED_EXACT"
        elif embedded_predictions:
            transfer_class = "FORWARD_PREDICTED_EMBEDDED"
        elif len(set(cue_atoms)) >= 2:
            transfer_class = "NEW_MULTI_ATOM_CANDIDATE"
        elif cue_atoms:
            transfer_class = "SINGLE_CUE_LOCAL_VALUE"
        else:
            transfer_class = "LOCAL_ASTRO_NOMENCLATOR"
        row: dict[str, object] = {
            "group_serial": source["group_serial"], "diagram_id": source["diagram_id"],
            "page": source["page"], "locus": source["locus"], "opaque_local_id": source["opaque_local_id"],
            "visible_owner": source["local_image_owner"], "visible_surface": surface,
            "namespace_id": source["namespace_id"], "local_content_class": source["local_content_class"],
            "detected_literal_atoms": "+".join(cue_atoms) if cue_atoms else "NONE",
            "detected_cues": "|".join(f"{atom}={literal}@{start}-{end}" for atom, literal, start, end, _meaning in cues) if cues else "NONE",
            "covered_characters": f"{covered}/{len(surface)}", "residual_pattern": residual,
            "transfer_class": transfer_class,
            "exact_prose_master_card_id": exact_prose["master_card_id"] if exact_prose else "NONE",
            "exact_prose_short_default_de": exact_prose["short_default_de"] if exact_prose else "NONE",
            "forward_prediction": prediction["predicted_atom_sequence"] if prediction else ("|".join(embedded_predictions) if embedded_predictions else "NONE"),
            "forward_predicted_reading_de": prediction["predicted_short_reading_de"] if prediction else "NONE",
            "existing_astro_component_parse": source["matched_component_values_de"],
            "existing_astro_reading_de": source["closed_workshop_reading_de"],
            "cross_register_reading_de": (
                f"{source['local_image_owner']}: {prediction['predicted_short_reading_de']} als Himmels-/Kalenderwert"
                if prediction else source["closed_workshop_reading_de"]
            ),
            "orientation_rule": source["orientation_rule"], "crosspage_rule": source["crosspage_rule"],
        }
        group_rows.append(row)
        types[surface].append(row)
        if prediction:
            prediction_hits[prediction["predicted_atom_sequence"]].append(row)
    write_tsv(HERE / "ASTRO_395_SURFACE_PARSE.tsv", group_rows, list(group_rows[0]))

    type_rows = []
    for surface, rows in sorted(types.items()):
        first = rows[0]
        type_rows.append({
            "visible_surface": surface, "occurrences": len(rows),
            "pages": "|".join(sorted({str(row["page"]) for row in rows})),
            "owners": "|".join(sorted({str(row["visible_owner"]) for row in rows})),
            "namespaces": "|".join(sorted({str(row["namespace_id"]) for row in rows})),
            "detected_literal_atoms": first["detected_literal_atoms"], "detected_cues": first["detected_cues"],
            "covered_characters": first["covered_characters"], "transfer_class": first["transfer_class"],
            "exact_prose_master_card_id": first["exact_prose_master_card_id"],
            "forward_prediction": first["forward_prediction"],
            "representative_astro_reading_de": first["existing_astro_reading_de"],
        })
    write_tsv(HERE / "ASTRO_301_TYPE_PARSE.tsv", type_rows, list(type_rows[0]))

    hit_rows = []
    for prediction in predictions:
        hits = prediction_hits.get(prediction["predicted_atom_sequence"], [])
        hit_rows.append({
            "predicted_atom_sequence": prediction["predicted_atom_sequence"],
            "predicted_short_reading_de": prediction["predicted_short_reading_de"],
            "prose_status": prediction["status"], "astro_exact_hit_count": len(hits),
            "astro_surfaces": "|".join(sorted({str(row["visible_surface"]) for row in hits})) if hits else "NONE",
            "astro_pages": "|".join(sorted({str(row["page"]) for row in hits})) if hits else "NONE",
            "astro_owners": "|".join(sorted({str(row["visible_owner"]) for row in hits})) if hits else "NONE",
            "existing_astro_readings": " || ".join(sorted({str(row["existing_astro_reading_de"]) for row in hits})) if hits else "NONE",
            "cross_register_decision": "FORWARD_CELL_FILLED_BY_ASTRO" if hits else "REMAINS_EMPTY",
        })
    write_tsv(HERE / "FORWARD_CELL_ASTRO_HITS.tsv", hit_rows, list(hit_rows[0]))

    candidate_rows = []
    for row in type_rows:
        if row["transfer_class"] not in {"NEW_MULTI_ATOM_CANDIDATE", "FORWARD_PREDICTED_EMBEDDED", "FORWARD_PREDICTED_EXACT"}:
            continue
        candidate_rows.append({
            "visible_surface": row["visible_surface"], "occurrences": row["occurrences"],
            "detected_literal_atoms": row["detected_literal_atoms"], "covered_characters": row["covered_characters"],
            "transfer_class": row["transfer_class"], "forward_prediction": row["forward_prediction"],
            "owners": row["owners"], "representative_astro_reading_de": row["representative_astro_reading_de"],
            "creative_default_de": " + ".join(next(meaning for atom2, _literal, meaning in LITERAL_CUES if atom2 == atom) for atom in str(row["detected_literal_atoms"]).split("+") if atom != "NONE"),
            "review_note": "owner supplies the celestial/calendar object; no direction or cross-page key inferred",
        })
    write_tsv(HERE / "NEW_MULTI_ATOM_CANDIDATES.tsv", candidate_rows, list(candidate_rows[0]))

    class_counts = Counter(str(row["transfer_class"]) for row in group_rows)
    type_class_counts = Counter(str(row["transfer_class"]) for row in type_rows)
    exact_filled = [row for row in hit_rows if int(row["astro_exact_hit_count"]) > 0]
    qotair = next((row for row in type_rows if row["visible_surface"] == "qotair"), None)
    report = f"""# Prosa-Stämme auf den drei Astrotafeln

## Der starke Vorwärtstreffer

Der Prosa-Compiler hatte `OT+AIR` als leere, aber lesbare Zelle vorausgesagt: **nächster Lauf / folgende Bahn**. Unter den 301 Astroformen erscheint exakt `qotair` auf `f69v`, am Besitzer `A3_RIGHT_WHEEL_RING_TEXT`. Der bestehende lokale Astrotext liest dieselbe Form bereits als *nächster Platz oder folgende Bedingung + Himmels-, Ring- oder Zeigerlauf*. Das ist die sauberste neue Brücke: nicht „Wasser“ wird in den Himmel getragen, sondern der gemeinsame Kern **Folge + Lauf/Bahn**; der sichtbare Besitzer liefert Wasserlauf oder Himmelslauf.

`qotair`-Parse: {qotair['detected_literal_atoms'] if qotair else 'missing'}, Abdeckung {qotair['covered_characters'] if qotair else 'missing'}.

## Gesamtinventar

Alle 395 Gruppen und 301 verschiedenen Oberflächen wurden mit denselben längsten Kernen gescannt. Einzelbuchstaben und globale E/Y-Lesungen sind absichtlich ausgeschlossen; sonst würde fast jedes Sternetikett scheinbar passen.

"""
    for key in sorted(class_counts):
        report += f"- `{key}`: {class_counts[key]} Gruppen / {type_class_counts[key]} Oberflächentypen\n"
    report += f"""

Von den 18 vorwärts gebildeten Prosa-Zellen wird {len(exact_filled)} exakt durch eine Astroform gefüllt. Daneben liefert `NEW_MULTI_ATOM_CANDIDATES.tsv` die neuen Mehrkernformen. Sie sind kreative Lesekandidaten, keine Erlaubnis, Besitzer, Richtung oder Startpunkt zu erfinden.

## Wichtigste Regeländerung

`AIR` wird jetzt registerübergreifend breiter gesprochen: **laufende Flüssigkeit / Lauf / Bahn**. In Pflanzen- und Beckenprosa ist die lokale Expansion Wasserlauf plausibel; im Diagramm ist es eine Himmels-, Ring- oder Zeigerbahn. Dadurch bleibt der Stamm kurz und die Bildrolle konkret. Dieselbe Regel gilt für `AL/AR` als Ziel-/Quelladresse und `AIIN/IIN` als Sollwert/Stufe.

## Nächster Schritt

Die neuen Mehrkernformen werden nun nach produktiven Familien geordnet. Nur Reihen, die mehr als eine Besitzerstelle sinnvoll lesen, kommen in das gemeinsame Werkstattwörterbuch; der Rest bleibt lokales Astro-Nomenklatorwort.
"""
    (HERE / "ASTRO_SURFACE_TRANSFER_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "astro_groups": len(group_rows), "astro_surface_types": len(type_rows),
        "exact_prose_surface_groups": class_counts["EXACT_PROSE_SURFACE"],
        "forward_cells": len(hit_rows), "forward_cells_filled_exactly": len(exact_filled),
        "new_multi_atom_candidate_types": len(candidate_rows),
        "group_class_counts": dict(sorted(class_counts.items())),
        "type_class_counts": dict(sorted(type_class_counts.items())),
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
