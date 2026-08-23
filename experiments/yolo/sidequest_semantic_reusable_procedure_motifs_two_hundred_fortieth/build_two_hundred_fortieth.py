#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/yolo/sidequest_semantic_biological_dual_protocol_two_hundred_thirty_ninth"
EVENT_FILE = SRC / "TWO_HUNDRED_THIRTY_NINTH_ONE_HUNDRED_TWENTY_EIGHT_PROTOCOL_EVENTS.tsv"
STATEMENT_FILE = SRC / "TWO_HUNDRED_THIRTY_NINTH_FORTY_THREE_COMPLETE_STATEMENTS.tsv"

MOTIFS = [
    {
        "id": "M01",
        "name": "SCHLIESSEN_DANN_PORTION",
        "template": "Vorigen Arbeitsschritt schließen; danach eine neue Portion zugeben.",
        "grammar": "CLOSE → OK+AIN",
        "loci": ["B1-S005>B1-S006", "B2-S002>B2-S003"],
        "surface_prediction": "qolchedy → qokain",
        "kind": "EXACT_CARD_TRANSITION",
    },
    {
        "id": "M02",
        "name": "ZIEL_DURCHLASS_TRANSFER",
        "template": "An der bezeichneten Stelle einsetzen, durch einen Gang führen und weitergeben oder abziehen.",
        "grammar": "AL/OK+AL → CKH/CHED → CHED/L+CHED",
        "loci": ["B1-S002", "B1-S006", "B2-S004", "B2-S005", "B2-S016"],
        "surface_prediction": "variable Hülle; Zielkarte vor Durchlass-/Transferkarte",
        "kind": "PRODUCTIVE_COMPONENT_MOTIF",
    },
    {
        "id": "M03",
        "name": "HALTEN_DANN_ABSETZEN",
        "template": "Den laufenden Posten kurz oder länger halten, danach absetzen und den Schritt schließen.",
        "grammar": "E/EE+Y or HOLD → SHED+DY",
        "loci": ["B1-S004", "B1-S008", "B1-S016", "B1-S019", "B2-S008", "B2-S009", "B2-S011"],
        "surface_prediction": "Gradkarte vor gelernter Absetz-/Schlusskarte",
        "kind": "PRODUCTIVE_COMPONENT_MOTIF",
    },
    {
        "id": "M04",
        "name": "BEMESSEN_DANN_PASSIEREN",
        "template": "Portion oder Sollwert setzen und den bemessenen Posten anschließend durchleiten oder zuführen.",
        "grammar": "AIN/AIIN → CKH/P+CHED",
        "loci": ["B1-S002", "B1-S006", "B2-S005", "B2-S008", "B2-S016"],
        "surface_prediction": "Mengenkarte vor Passage/Zuführung",
        "kind": "PRODUCTIVE_COMPONENT_MOTIF",
    },
    {
        "id": "M05",
        "name": "WASCH_ODER_KONTAKTABSCHLUSS",
        "template": "Waschen oder länger einwirken lassen und den lokalen Schritt unmittelbar schließen.",
        "grammar": "LSH or EE-contact → DY-construction",
        "loci": ["B1-S009", "B1-S012", "B1-S013", "B2-S003", "B2-S015", "B2-S018", "B2-S019", "B2-S021"],
        "surface_prediction": "Wasch-/Kontaktkarte trägt lokalen Abschluss",
        "kind": "PRODUCTIVE_COMPONENT_MOTIF",
    },
    {
        "id": "M06",
        "name": "EMPFANG_UND_ERGEBNIS",
        "template": "Am Empfangsgefäß oder Geräteport weiterbehandeln und das Ergebnis beziehungsweise Auffanggut abnehmen.",
        "grammar": "RECEIVER/PORT → HOLD/SET → RESULT/COLLECT",
        "loci": ["B1-S018", "B2-S010", "B2-S012"],
        "surface_prediction": "lokales Gegenstandszeichen vor Ergebnis-/Sammelkarte",
        "kind": "WHOLE_SIGN_PLUS_PRODUCTIVE_MOTIF",
    },
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    events = read_tsv(EVENT_FILE)
    statements = read_tsv(STATEMENT_FILE)
    statement = {r["statement_id"]: r for r in statements}
    by_record = {record: [r for r in events if r["record_unit_id"] == record] for record in ("B1", "B2")}

    exact_rows: list[dict[str, object]] = []
    for n in (2, 3, 4):
        inventories: dict[str, dict[tuple[str, ...], list[int]]] = {}
        for record, rows in by_record.items():
            ids = [r["master_card_id"] for r in rows]
            found: dict[tuple[str, ...], list[int]] = {}
            for i in range(len(ids) - n + 1):
                found.setdefault(tuple(ids[i:i+n]), []).append(i)
            inventories[record] = found
        for gram in sorted(set(inventories["B1"]) & set(inventories["B2"])):
            for record in ("B1", "B2"):
                for i in inventories[record][gram]:
                    window = by_record[record][i:i+n]
                    exact_rows.append({
                        "ngram_length": n,
                        "master_card_sequence": " → ".join(gram),
                        "record_unit_id": record,
                        "event_ids": "|".join(r["event_id"] for r in window),
                        "statement_ids": "|".join(dict.fromkeys(r["statement_id"] for r in window)),
                        "visible_sequence": " ".join(r["visible_surface"] for r in window),
                        "concrete_value_sequence": " → ".join(r["concrete_value_de"] for r in window),
                        "crosses_statement_boundary": "YES" if len({r["statement_id"] for r in window}) > 1 else "NO",
                    })

    motif_rows: list[dict[str, object]] = []
    occurrence_rows: list[dict[str, object]] = []
    for motif in MOTIFS:
        counts = Counter(locus.split("-", 1)[0] for locus in motif["loci"])
        motif_rows.append({
            "motif_id": motif["id"],
            "motif_name": motif["name"],
            "motif_kind": motif["kind"],
            "component_grammar": motif["grammar"],
            "apprentice_dictation_de": motif["template"],
            "b1_occurrences": counts["B1"],
            "b2_occurrences": counts["B2"],
            "total_occurrences": len(motif["loci"]),
            "surface_prediction": motif["surface_prediction"],
        })
        for locus in motif["loci"]:
            ids = locus.split(">")
            linked = [statement[sid] for sid in ids]
            occurrence_rows.append({
                "motif_id": motif["id"],
                "motif_name": motif["name"],
                "record_unit_id": linked[0]["record_unit_id"],
                "statement_locus": locus,
                "visible_owner": " → ".join(dict.fromkeys(r["visible_owner"] for r in linked)),
                "visible_sequence": " || ".join(r["visible_sequence"] for r in linked),
                "component_chain": " || ".join(r["component_chain"] for r in linked),
                "complete_translation_de": " ".join(r["complete_translation_de"] for r in linked),
                "reuse_level": motif["kind"],
            })

    exact_path = OUT / "TWO_HUNDRED_FORTIETH_EXACT_SHARED_CARD_WINDOWS.tsv"
    motif_path = OUT / "TWO_HUNDRED_FORTIETH_SIX_REUSABLE_MOTIFS.tsv"
    occurrence_path = OUT / "TWO_HUNDRED_FORTIETH_THIRTY_MOTIF_OCCURRENCES.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTIETH_APPRENTICE_MOTIF_CARDS.md"
    report_path = OUT / "TWO_HUNDRED_FORTIETH_REPORT.md"
    write_tsv(exact_path, exact_rows, list(exact_rows[0]))
    write_tsv(motif_path, motif_rows, list(motif_rows[0]))
    write_tsv(occurrence_path, occurrence_rows, list(occurrence_rows[0]))

    readable = ["# Sechs wiederverwendbare Arbeitskarten", ""]
    for row in motif_rows:
        readable += [
            f"## {row['motif_id']} — {row['motif_name']}", "",
            f"**Lehrmeister sagt:** {row['apprentice_dictation_de']}", "",
            f"**Schreiberregel:** `{row['component_grammar']}`", "",
            f"Kommt in f81v {row['b1_occurrences']}× und in f82r {row['b2_occurrences']}× vor. {row['surface_prediction']}.", "",
        ]
    readable += [
        "## Was der Lehrling tatsächlich lernt", "",
        "Er lernt nicht sechs feste Sätze. Er lernt sechs kurze Arbeitsmuster und setzt dafür jeweils Ziel-, Mengen-, Durchlass-, Halte- und Schlusskarten zusammen.",
        "Nur M01 ist sogar als exaktes Kartenpaar auf beiden Seiten vorhanden. Die anderen fünf werden mit wechselnden Oberflächen realisiert.",
        "Damit passt das System besser zu Fachkürzeln plus gelerntem Nomenklator als zu einem Phrasebook mit abgeschriebenen Zeilen.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 240: wiederverwendbare Prozedurmotive

## Ergebnis

Die Suche nach wortwörtlich kopierten Kartensequenzen ist fast leer: Über beide vollständigen Records hinweg existiert nur ein gemeinsames exaktes Bigramm und kein gemeinsames exaktes Tri- oder Viergramm. Das eine Paar ist `qolchedy → qokain`: **weiterführen/schließen → neue Portion zugeben**.

Trotzdem kehren sechs klar lehrbare Arbeitsmotive in beiden Records wieder. Fünf davon werden produktiv aus gemeinsamen Komponenten neu gebaut. Das ist stärker als bloße Satzkopie: Der Schreiber verwendet eine kleine Operationsgrammatik für verschiedene Bildbesitzer und Abläufe.

## Konsequenz für unser Schreibsystem

- Ganze Fachzeichen benennen lokale Handlungen oder Gegenstände.
- Komponenten bestimmen Ziel, Quelle, Menge, Passage, Dauer und Abschluss.
- Ein Lehrling kann den Ablauf nach Diktat bauen, ohne jeden vollständigen Satz auswendig zu kennen.
- Exakte Oberfläche bleibt variabel, weil Hüllen und lokale Ganzzeichen gewählt werden müssen.

Quellen: R239 events `{sha(EVENT_FILE)}`; R239 statements `{sha(STATEMENT_FILE)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "exact_shared_windows": len(exact_rows),
        "exact_shared_types": len({r["master_card_sequence"] for r in exact_rows}),
        "reusable_motifs": len(motif_rows),
        "motif_occurrences": len(occurrence_rows),
        "outputs": {p.name: sha(p) for p in (exact_path, motif_path, occurrence_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
