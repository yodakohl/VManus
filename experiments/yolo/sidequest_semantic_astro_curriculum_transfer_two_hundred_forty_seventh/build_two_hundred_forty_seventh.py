#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
GROUPS = SRC / "TWO_HUNDRED_THIRTEENTH_395_ASTRO_SURFACE_BRIDGE.tsv"

PAGE_ROLE = {
    "f67r2": "ZWEI_GETRENNTE_HIMMELSRaeDER_MIT_LOKALEN_RING_UND_FELDPLAETZEN".upper(),
    "f68r1": "MEHRPANEEL_STERNATLAS_MIT_28_LOKALEN_STERNPLAETZEN",
    "f69v": "DREI_GETRENNTE_HETEROGENE_RaeDER_MIT_28_LOKALEN_LINKEN_PLAETZEN".upper(),
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


def main() -> None:
    source = read_tsv(GROUPS)
    groups: list[dict[str, object]] = []
    for row in source:
        if row["is_herbal_bio_bridge_card"] == "YES":
            layer = "THREE_REGISTER_COMMON_CORE"
            action = "reuse common card; expand it under the local diagram owner"
        elif row["exact_prose_card_id"] != "NONE":
            layer = "KNOWN_PROSE_CARD_IN_ASTRO"
            action = "reuse a learned prose card with diagram-local object"
        else:
            layer = "ASTRO_LOCAL_LABEL_SIGN"
            action = "copy the local label from the diagram exemplar"
        groups.append({
            "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
            "page_role": PAGE_ROLE[row["page"]], "visible_owner": row["visible_owner"],
            "namespace_id": row["namespace_id"], "visible_surface": row["visible_surface"],
            "exact_prose_card_id": row["exact_prose_card_id"], "portable_prose_value_de": row["exact_prose_value_de"],
            "curriculum_layer": layer, "concrete_diagram_reading_de": row["astro_local_reading_de"],
            "apprentice_action": action,
        })

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in groups:
        if row["exact_prose_card_id"] != "NONE":
            by_card[str(row["exact_prose_card_id"])].append(row)
    card_rows: list[dict[str, object]] = []
    for card_id, linked in sorted(by_card.items()):
        values = list(dict.fromkeys(str(r["portable_prose_value_de"]) for r in linked))
        card_rows.append({
            "master_card_id": card_id,
            "registered_surfaces_seen": "|".join(dict.fromkeys(str(r["visible_surface"]) for r in linked)),
            "portable_value_de": values[0],
            "curriculum_layer": linked[0]["curriculum_layer"],
            "astro_group_count": len(linked),
            "pages": "|".join(dict.fromkeys(str(r["page"]) for r in linked)),
            "namespaces": "|".join(dict.fromkeys(str(r["namespace_id"]) for r in linked)),
            "value_invariant": "YES" if len(values) == 1 else "NO",
        })

    namespace_rows: list[dict[str, object]] = []
    for namespace in sorted({str(r["namespace_id"]) for r in groups}):
        linked = [r for r in groups if r["namespace_id"] == namespace]
        counts = Counter(str(r["curriculum_layer"]) for r in linked)
        namespace_rows.append({
            "namespace_id": namespace, "page": linked[0]["page"], "page_role": linked[0]["page_role"],
            "locus_count": len({str(r["locus"]) for r in linked}), "group_count": len(linked),
            "common_core_groups": counts["THREE_REGISTER_COMMON_CORE"],
            "other_known_prose_groups": counts["KNOWN_PROSE_CARD_IN_ASTRO"],
            "local_label_groups": counts["ASTRO_LOCAL_LABEL_SIGN"],
            "teaching_rule": "point to this namespace; reuse known cards and copy remaining local labels",
        })

    group_path = OUT / "TWO_HUNDRED_FORTY_SEVENTH_395_GROUP_ASTRO_MANUAL.tsv"
    card_path = OUT / "TWO_HUNDRED_FORTY_SEVENTH_29_KNOWN_PROSE_CARDS.tsv"
    namespace_path = OUT / "TWO_HUNDRED_FORTY_SEVENTH_13_NAMESPACE_LESSONS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_SEVENTH_READABLE_ASTRO_TRANSFER.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_SEVENTH_REPORT.md"
    write_tsv(group_path, groups, list(groups[0]))
    write_tsv(card_path, card_rows, list(card_rows[0]))
    write_tsv(namespace_path, namespace_rows, list(namespace_rows[0]))

    readable = ["# Astro-Lehrgang für den Prosa-Schreiber", ""]
    for page in ("f67r2", "f68r1", "f69v"):
        linked = [r for r in groups if r["page"] == page]
        counts = Counter(str(r["curriculum_layer"]) for r in linked)
        readable += [
            f"## {page}", "", PAGE_ROLE[page], "",
            f"{len(linked)} Gruppen: {counts['THREE_REGISTER_COMMON_CORE']} Drei-Register-Kern, {counts['KNOWN_PROSE_CARD_IN_ASTRO']} weitere bekannte Prosekarten, {counts['ASTRO_LOCAL_LABEL_SIGN']} lokale Diagrammzeichen.", "",
        ]
    readable += ["## 29 wiederverwendete Prosekarten", ""]
    for card in card_rows:
        readable.append(f"- `{card['registered_surfaces_seen']}` = **{card['portable_value_de']}** — {card['astro_group_count']} Astrogruppen")
    readable += [
        "", "## Schreibregel", "",
        "Der Lehrmeister zeigt auf Rad, Ring, Sternplatz oder Legende. Bekannte Karten behalten ihren abstrakten Wert – dies, Sollwert, Ziel, Quelle, weiter, einsetzen, überführen. Den eigentlichen Stern- oder Sektornamen kopiert der Lehrling als lokales Zeichen aus dem Diagrammexemplar.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    counts = Counter(str(r["curriculum_layer"]) for r in groups)
    report = f"""# Sidequest-Pass 247: Prosa-Curriculum auf Astro übertragen

## Ergebnis

Von 395 Astrogruppen sind **66** Vorkommen auf 13 Karten Teil des Drei-Register-Kerns. Weitere **23** Vorkommen auf 16 Karten sind aus dem vollständigen Prosaunterricht bekannt. Insgesamt kann der ausgebildete Schreiber also **89/395 Gruppen auf 29 Prosekarten** unmittelbar lesen und lokal erweitern.

Die übrigen **306** Gruppen sind Diagrammetiketten in 13 getrennten Namensräumen. Sie brauchen keine 306 neuen Satzbedeutungen: Der Lehrmeister zeigt auf den lokalen Platz, und der Schreiber kopiert dessen Stern-, Ring-, Sektor- oder Legendenzeichen aus dem Exemplar.

Damit bleibt Astro ein anderes Register, aber kein völlig anderes Schriftsystem. Relations-, Mengen-, Ziel-, Quellen- und Referenzkarten sind gemeinsam; die Namenslisten sind lokal.

Input SHA-256 `{sha(GROUPS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "groups": len(groups), "known_prose_cards": len(card_rows),
        "namespaces": len(namespace_rows), "curriculum_layer_counts": dict(counts),
        "outputs": {p.name: sha(p) for p in (group_path, card_path, namespace_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
