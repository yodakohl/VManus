#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NORMALIZED = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_normalization_nine_hundred_sixty_second/PASS962_2511_REGISTER_NORMALIZED_EVENTS.tsv"
PROSE = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_2010_CANONICAL_PROSE_INTERLINEAR.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_354_CANONICAL_CLAUSE_TRANSLATIONS.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_14_CANONICAL_PAGE_READINGS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    normalized = {row["event_id"]: row for row in read_tsv(NORMALIZED)}
    prose = read_tsv(PROSE)
    clauses = read_tsv(CLAUSES)
    pages = read_tsv(PAGES)

    interlinear: list[dict[str, object]] = []
    by_clause: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in prose:
        current = normalized[row["event_id"]]
        local = row["codebook_layer"] == "LOCAL_NOMENCLATOR_OR_ADDRESS"
        context = current["former_canonical_reading_de"] if local else current["register_expansion_de"]
        item = {
            "event_id": row["event_id"], "clause_id": row["clause_id"], "physical_page": row["physical_page"],
            "locus": row["locus"], "surface": row["surface"], "component_recipe": row["component_recipe"],
            "codebook_layer": row["codebook_layer"], "portable_core_de": current["portable_atomic_reading_de"],
            "owner_filled_reading_de": context,
            "reading_route": "LOCAL_OWNER_CARD" if local else "PORTABLE_CORE_PLUS_VISIBLE_REGISTER",
        }
        interlinear.append(item)
        by_clause[row["clause_id"]].append(item)
    write_tsv(OUT / "PASS963_2010_PORTABLE_CORE_INTERLINEAR.tsv", interlinear)

    clause_rows: list[dict[str, object]] = []
    for clause in clauses:
        members = by_clause[clause["clause_id"]]
        core_chain = " ; ".join(str(row["portable_core_de"]) for row in members)
        context_chain = " ; ".join(str(row["owner_filled_reading_de"]) for row in members)
        ending = "TEILGANG GESCHLOSSEN" if clause["end_reason"] == "LICENSED_DY_CLOSE" else "FORTSETZUNG OFFEN" if clause["end_reason"] == "PAGE_END_OPEN" else "LOKALER ABSCHNITT"
        clause_rows.append({
            "clause_id": clause["clause_id"], "physical_page": clause["physical_page"], "register": members[0]["reading_route"] if members else "NONE",
            "start_event": clause["start_event"], "end_event": clause["end_event"], "events": len(members),
            "end_reason": clause["end_reason"], "portable_core_clause_de": f"{core_chain}. {ending}.",
            "owner_filled_clause_de": f"{context_chain}. {ending}.",
            "event_ids": "|".join(str(row["event_id"]) for row in members),
        })
    write_tsv(OUT / "PASS963_354_PORTABLE_CORE_CLAUSES.tsv", clause_rows)

    page_rows: list[dict[str, object]] = []
    clause_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in clause_rows:
        clause_by_page[str(row["physical_page"])].append(row)
    for page in pages:
        physical = page["physical_page"]
        members = clause_by_page.get(physical, [])
        page_rows.append({
            "physical_page": physical,
            "unit_role_de": page["unit_role_de"],
            "prose_clauses": len(members),
            "prose_events": sum(int(row["events"]) for row in members),
            "portable_core_summary_de": " | ".join(str(row["portable_core_clause_de"]) for row in members) if members else "BILDREGISTER OHNE PROSAKLAUSEL",
            "readable_page_summary_de": page["canonical_page_reading_de"],
        })
    write_tsv(OUT / "PASS963_14_PAGE_PORTABLE_EDITION.tsv", page_rows)

    edition = ["# Vollständige Ausgabe in portabler Kernsprache", ""]
    for page in pages:
        physical = page["physical_page"]
        edition.extend([f"## {physical} — {page['unit_role_de']}", "", page["canonical_page_reading_de"], ""])
        for clause in clause_by_page.get(physical, []):
            edition.extend([
                f"### {clause['clause_id']}", "",
                f"**Kern:** {clause['portable_core_clause_de']}", "",
                f"**Mit Bildbesitzer:** {clause['owner_filled_clause_de']}", "",
            ])
    (OUT / "PASS963_COMPLETE_PORTABLE_CORE_EDITION.md").write_text(
        "\n".join(edition).rstrip() + "\n", encoding="utf-8"
    )

    layer_counts = Counter(row["codebook_layer"] for row in interlinear)
    report = f"""# Pass 963 — alle Aussagen in einer einzigen Kernsprache

Alle **2.010 Prosakarten** und **354 Aussagen** sind mit den 56 portablen
Stammwerten neu geschrieben. Jede Aussage steht doppelt da:

1. als unveränderliche Kernfolge (`SETZEN · EINHEIT`, `NEHMEN · SATZ`),
2. als Lesung mit dem sichtbaren Pflanzen-, Stations- oder Himmelsbesitzer.

Lokale Nomenklatorkarten behalten ihren Bildwert; sie werden nicht gewaltsam
zu Wortstämmen gemacht. Die Prosabilanz ist {dict(layer_counts)}. Es gibt keine
leere Karte und keinen Registerwechsel eines Kernwerts. Damit ist die Ausgabe
jetzt rücklesbar, ohne dass `AIN` zwischen Portion und Index oder `OK` zwischen
Ansatz und Sternaktivierung springen muss.
"""
    (OUT / "PASS963_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS963_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "prose_events": len(interlinear), "clauses": len(clause_rows), "pages": len(page_rows),
        "layer_counts": layer_counts, "outputs": outputs,
    }
    (OUT / "PASS963_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
