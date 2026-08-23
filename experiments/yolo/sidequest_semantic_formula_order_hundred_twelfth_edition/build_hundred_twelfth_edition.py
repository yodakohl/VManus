#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_116_CURRENT_STATEMENTS.tsv"

CONTRASTS = [
    ("OC01", "Y", "AIIN", "Posten vor Maß: das Maß gilt rückwärts für den aktuellen Posten", "AIIN vor Y: das Maß eröffnet den folgenden Posten"),
    ("OC02", "OR", "Y", "Ansatz vor Y bildet den aktuellen Ansatz", "Y vor Ansatz wäre ein Wechsel vom Posten zum neuen Ansatz"),
    ("OC03", "AL", "OL", "Ziel vor Fortsetzung: am gesetzten Ziel weiterführen", "Fortsetzung vor Ziel wäre eine noch offene Zielzuweisung"),
    ("OC04", "OT+OL", "OL", "Folge-Fortsetzung eröffnet danach den weiterlaufenden Schritt", "umgekehrt wäre die Folge erst nachträglich markiert"),
    ("OC05", "OL", "SHED+E+CLOSE", "Fortsetzung vor Absetzen: weiterführen, kurz absetzen, schließen", "umgekehrt würde ein geschlossener Schritt unzulässig weiterlaufen"),
    ("OC06", "CHD+Y", "OL", "umgesetzten Posten weiterführen", "umgekehrt würde die Fortsetzung vor ihrem Posten stehen"),
    ("OC07", "OL+AIN", "AL", "weitere Portion vor Ziel: Portion zum Ziel geben", "umgekehrt wäre das Ziel vor der neuen Menge gesetzt"),
    ("OC08", "OL+OR", "OL", "vorigen Ansatz weiterführen", "umgekehrt würde Fortsetzung ohne benannten Ansatz beginnen"),
]

PREDICTIONS = [
    ("PX01", ("Y", "AIIN", "AL"), "diesen Posten nach Sollmaß zum Ziel bringen"),
    ("PX02", ("OR", "Y", "AIIN"), "den aktuellen Ansatz auf Sollmaß bringen"),
    ("PX03", ("OT+OL", "OL", "SHED+E+CLOSE"), "den nächsten Schritt weiterführen, kurz absetzen und schließen"),
    ("PX04", ("OL+AIN", "AL", "OL"), "eine weitere Portion zum Ziel geben und dort weiterführen"),
    ("PX05", ("CHD+Y", "OL", "SHED+E+CLOSE"), "den umgesetzten Posten weiterführen, kurz absetzen und schließen"),
    ("PX06", ("AIIN", "Y", "AL"), "das Sollmaß für den folgenden Posten am Ziel eröffnen"),
    ("PX07", ("OR", "Y", "AL"), "den aktuellen Ansatz an die Zielstelle geben"),
    ("PX08", ("Y", "AL", "CHD+CLOSE"), "diesen Posten am Ziel umsetzen und schließen"),
    ("PX09", ("OK+AIIN", "CTH+Y"), "Sollmaß einstellen und den Posten bereit halten"),
    ("PX10", ("Y", "AIIN", "Y"), "zwei Posten unter dasselbe Sollmaß stellen"),
    ("PX11", ("OT+OL", "OL+OR", "OL"), "danach den vorigen Ansatz weiterführen"),
    ("PX12", ("OK+EE+Y", "OK+E+CLOSE"), "länger ansetzen, kurz nachführen und schließen"),
]


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def occurrences(rows, pattern):
    hits = []
    for row in rows:
        sequence = row["semantic_atom_program"].split(" | ")
        surfaces = row["visible_surface_sequence"].split()
        for start in range(len(sequence) - len(pattern) + 1):
            if tuple(sequence[start:start+len(pattern)]) == tuple(pattern):
                hits.append((row["statement_id"], " ".join(surfaces[start:start+len(pattern)])))
    return hits


def main():
    source = load(SOURCE)
    contrast_rows = []
    for contrast_id, left, right, forward_reading, reverse_reading in CONTRASTS:
        forward = occurrences(source, (left, right))
        reverse = occurrences(source, (right, left))
        contrast_rows.append({
            "contrast_id": contrast_id,
            "forward_pattern": f"{left} > {right}",
            "forward_count": str(len(forward)),
            "forward_statements": "|".join(x[0] for x in forward) or "NONE",
            "forward_working_reading_de": forward_reading,
            "reverse_pattern": f"{right} > {left}",
            "reverse_count": str(len(reverse)),
            "reverse_statements": "|".join(x[0] for x in reverse) or "NONE",
            "reverse_working_reading_de": reverse_reading,
            "order_decision": "BIDIRECTIONAL_ATTACHMENT" if forward and reverse else "ONE_WAY_WORKSHOP_ORDER",
        })
    write_tsv("HUNDRED_TWELFTH_EIGHT_ORDER_CONTRASTS.tsv", contrast_rows)

    prediction_rows = []
    for pred_id, pattern, phrase in PREDICTIONS:
        hits = occurrences(source, pattern)
        prediction_rows.append({
            "prediction_id": pred_id,
            "atom_sequence": " > ".join(pattern),
            "predicted_workshop_reading_de": phrase,
            "current_status": "ALREADY_PRESENT" if hits else "OPEN_FORWARD_SEQUENCE",
            "occurrence_count": str(len(hits)),
            "statement_ids": "|".join(x[0] for x in hits) or "NONE",
            "visible_surface_spans": "|".join(x[1] for x in hits) or "NONE",
            "longest_match_rule": "use the whole listed sequence before any nested shorter formula",
        })
    write_tsv("HUNDRED_TWELFTH_TWELVE_ORDERED_PREDICTIONS.tsv", prediction_rows)

    annotations = []
    for row in source:
        seq = row["semantic_atom_program"].split(" | ")
        tags = []
        for contrast_id, left, right, *_ in CONTRASTS:
            if any(tuple(seq[i:i+2]) == (left, right) for i in range(len(seq)-1)):
                tags.append(contrast_id + "_FORWARD")
            if any(tuple(seq[i:i+2]) == (right, left) for i in range(len(seq)-1)):
                tags.append(contrast_id + "_REVERSE")
        annotations.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface_sequence": row["visible_surface_sequence"],
            "semantic_atom_program": row["semantic_atom_program"],
            "order_tags": "|".join(tags) if tags else "NONE",
            "current_reading_de": row["current_reading_de"],
        })
    write_tsv("HUNDRED_TWELFTH_116_ORDER_ANNOTATED_STATEMENTS.tsv", annotations)

    present = sum(r["current_status"] == "ALREADY_PRESENT" for r in prediction_rows)
    report = [
        "# Hundertzwölfte Runde: Reihenfolge trägt Bedeutung", "",
        "Sechs der acht geprüften Kartenpaare laufen in der festen Auswahl nur in einer Richtung.",
        "Die erste Ausnahme ist Y/AIIN: Y–AIIN bemisst den aktuellen Posten rückwärts; AIIN–Y eröffnet",
        "das Maß für den folgenden Posten. Im Dreier Y–AIIN–Y treffen beide Bindungen zusammen und",
        "geben die Lesung ›zwei Posten unter dasselbe Sollmaß stellen‹.", "",
        "Die zweite Ausnahme ist OL / OL+OR / OL: In H2-S002 umklammert Fortsetzung den vorigen Ansatz.",
        "Das ist keine freie Umkehr, sondern eine Rahmenform ›weiter — voriger Ansatz — weiter‹.", "",
        "Die anderen Einbahnformeln ergeben eine einfache Werkstattordnung: Ansatz oder Posten zuerst,",
        "dann Maß/Ziel, danach Fortsetzung und zuletzt Absetzen/Schluss. Ein geschlossener Schritt wird",
        "nie nachträglich weitergeführt.", "",
        f"Von zwölf bewusst gebildeten längeren Satzfolgen sind {present} bereits sichtbar und",
        f"{12-present} echte offene Vorhersagen. Sie erweitern das Kartenlexikon nicht, sondern sagen",
        "voraus, wie bekannte Karten in einem neuen Eintrag geordnet würden.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_TWELFTH_FORMULA_ORDER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE", "contrasts": len(contrast_rows),
        "one_way_contrasts": sum(r["order_decision"] == "ONE_WAY_WORKSHOP_ORDER" for r in contrast_rows),
        "predictions": len(prediction_rows), "already_present": present, "open": len(prediction_rows)-present,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
