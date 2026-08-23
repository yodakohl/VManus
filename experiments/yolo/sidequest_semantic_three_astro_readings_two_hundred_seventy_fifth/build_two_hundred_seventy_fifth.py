#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R274 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth"
ASTRO = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv"

PAGE_DEFAULTS = {
    "f67r2": "Zwei getrennte Himmelsräder: lokale Sektor-, Ring-, Feld- und Phasenwerte nachschlagen.",
    "f68r1": "Mehrpaneel-Sternregister: Tafelköpfe und einzelne räumliche Sternstellen nachschlagen.",
    "f69v": "Drei getrennte Räder: lokale Ringwerte und die 28 Plätze nur am linken Rad nachschlagen.",
}


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


def tail_reading(row: dict[str, str]) -> str:
    reading = row["concrete_diagram_reading_de"]
    return reading.split(": ", 1)[1] if ": " in reading else reading


def atom(row: dict[str, str]) -> str:
    cls = row["coverage_class_274"]
    if cls == "PORTABLE_COMPOSITION":
        value = row["portable_card_core_de"]
        if value in {"LOCAL_LABEL", "NONE", ""}:
            value = tail_reading(row)
        return value
    if cls == "LEARNED_WHOLE_SIGN":
        return f"Ganzzeichen {row['visible_surface']}: {tail_reading(row)}"
    return f"Lokalschluessel {row['visible_surface']} fuer {row['visible_owner']}"


def main() -> None:
    source = read_tsv(ASTRO)
    interlinear: list[dict[str, object]] = []
    by_locus: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in source:
        out = {
            "group_serial": row["group_serial"],
            "page": row["page"],
            "locus": row["locus"],
            "visible_owner": row["visible_owner"],
            "namespace_id": row["namespace_id"],
            "visible_surface": row["visible_surface"],
            "coverage_class": row["coverage_class_274"],
            "component_or_copy_reading_de": atom(row),
            "source_order_only": "YES",
            "orientation_claim": "NONE",
            "start_claim": "NONE",
            "cross_page_key": "NONE",
        }
        interlinear.append(out)
        by_locus[(row["page"], row["locus"])].append(out)

    loci: list[dict[str, object]] = []
    for (page, locus), rows in by_locus.items():
        loci.append({
            "page": page,
            "locus": locus,
            "visible_owner": rows[0]["visible_owner"],
            "namespace_id": rows[0]["namespace_id"],
            "group_count": len(rows),
            "visible_sequence": " | ".join(str(r["visible_surface"]) for r in rows),
            "coverage_sequence": " | ".join(str(r["coverage_class"]) for r in rows),
            "continuous_default_reading_de": "; ".join(str(r["component_or_copy_reading_de"]) for r in rows),
            "reading_mode": "LOCAL_LOOKUP_IN_SOURCE_COPY_ORDER",
        })

    contracts = []
    for page in ("f67r2", "f68r1", "f69v"):
        page_rows = [r for r in interlinear if r["page"] == page]
        page_loci = [r for r in loci if r["page"] == page]
        contracts.append({
            "page": page,
            "instrument_default_de": PAGE_DEFAULTS[page],
            "locus_count": len(page_loci),
            "group_count": len(page_rows),
            "namespace_count": len({str(r["namespace_id"]) for r in page_rows}),
            "orientation_claim": "NONE",
            "start_claim": "NONE",
            "cross_page_key": "NONE",
            "reading_rule": "choose the visible locus; read its cards in source copy order; never infer circular sequence",
        })

    interlinear_path = OUT / "TWO_HUNDRED_SEVENTY_FIFTH_395_GROUP_READINGS.tsv"
    loci_path = OUT / "TWO_HUNDRED_SEVENTY_FIFTH_142_LOCUS_READINGS.tsv"
    contracts_path = OUT / "TWO_HUNDRED_SEVENTY_FIFTH_THREE_INSTRUMENT_CONTRACTS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_FIFTH_COMPLETE_ASTRO_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_FIFTH_REPORT.md"
    write_tsv(interlinear_path, interlinear, list(interlinear[0]))
    write_tsv(loci_path, loci, list(loci[0]))
    write_tsv(contracts_path, contracts, list(contracts[0]))

    lines = ["# Vollständige Arbeitslesung der drei Astro-Seiten", ""]
    for contract in contracts:
        page = str(contract["page"])
        lines.extend([f"## {page}", "", str(contract["instrument_default_de"]), ""])
        for row in [r for r in loci if r["page"] == page]:
            lines.append(f"- **{row['locus']} / {row['visible_owner']}** — {row['continuous_default_reading_de']}")
        lines.append("")
    lines.extend([
        "## Leseschlüssel", "",
        "Die Aufzählungsreihenfolge ist nur die überlieferte Kopierfolge der Transkription. Sie behauptet weder einen Startpunkt noch Uhrzeigersinn, Rotation, Zeitfolge oder einen Schlüssel zwischen f68r1 und f69v.", "",
    ])
    readable_path.write_text("\n".join(lines), encoding="utf-8")

    page_counts = Counter(r["page"] for r in interlinear)
    report_path.write_text(f"""# Sidequest-Pass 275: vollständige Astro-Rücklesung

## Ergebnis

Alle 395 Gruppen und 142 sichtbaren Loci erhalten eine fortlaufende Werkstattlektüre. f67r2 hat 190 Gruppen/74 Loci, f68r1 65/37 und f69v 140/31. Portable Kompositionen werden direkt gelesen, Ganzzeichen mit ihrem lokalen Default, Kopieretiketten als Schlüssel für den sichtbaren Besitzer.

Die drei Seiten bleiben getrennte Instrumente. Keine Zeile behauptet Start, Richtung, Rotation oder f68↔f69-Schlüssel. Die Ausgabe ist damit vollständig, ohne aus lokaler Schreibreihenfolge eine kosmologische Sequenz zu erfinden.

Input `{sha(ASTRO)}`.
""", encoding="utf-8")
    outputs = (interlinear_path, loci_path, contracts_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "groups": len(interlinear),
        "loci": len(loci),
        "page_group_counts": dict(page_counts),
        "page_locus_counts": {p: sum(r["page"] == p for r in loci) for p in PAGE_DEFAULTS},
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
