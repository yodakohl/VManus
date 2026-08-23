#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R268 = ROOT / "experiments/yolo/sidequest_semantic_air_path_revision_two_hundred_sixty_eighth"
ASTRO = R268 / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_395_ASTRO_GROUPS.tsv"

MATCH = {
    "saral": ("AR|AL", "S_FRAME+AR+AL", "vom Ausgangssektor zum Zielsektor"),
    "olar": ("AR|OL", "OL+AR", "vom Ausgangssektor im selben Lauf weiter"),
    "okolar": ("AR|OL", "OK+OL+AR", "vom Ausgangssektor den gleichen Lauf aktivieren"),
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
    astro = read_tsv(ASTRO)
    matches = []
    revised = []
    for row in astro:
        new = dict(row)
        if row["exact_prose_card_id"] == "NONE" and row["visible_surface"] in MATCH:
            pair, parse, meaning = MATCH[row["visible_surface"]]
            matches.append({
                "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
                "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"], "relation_pair": pair,
                "component_parse": parse, "composed_short_value_de": meaning,
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
                "register_rule": "Astro composes the formal address pair directly; prose may use a learned operation sign",
            })
            new["curriculum_layer"] = "ASTRO_COMPOSED_RELATION_PAIR"
            new["portable_card_core_de"] = meaning
            new["portable_card_role"] = "COMPOSED_ASTRO_RELATION_CARD"
            new["apprentice_action"] = "compose the source/target or source/continuation relation directly"
            new["revision_269"] = "RELATION_GAP_MATCH"
        else:
            new["revision_269"] = "UNCHANGED"
        revised.append(new)

    matrix = [
        {"prose_gap_pair": "AR|AL", "astro_status": "PRODUCTIVE_MATCH", "astro_forms": "saral", "astro_group_count": 2, "prose_strategy": "SSHKCHDY learned whole sign", "working_meaning_de": "von Quelle zu Ziel / übertragen", "register_conclusion": "formal diagram address composes; physical transfer lexicalizes"},
        {"prose_gap_pair": "AR|OL", "astro_status": "PRODUCTIVE_MATCH", "astro_forms": "olar|okolar", "astro_group_count": 2, "prose_strategy": "LKEDY learned whole sign", "working_meaning_de": "von Quelle aus weiter / weiter abziehen", "register_conclusion": "formal ring continuation composes; physical withdrawal lexicalizes"},
        {"prose_gap_pair": "AR|OR", "astro_status": "NO_DIRECT_MATCH", "astro_forms": "NONE", "astro_group_count": 0, "prose_strategy": "SCHOAL learned whole sign", "working_meaning_de": "Ansatz aus Quelle / Sudansatz", "register_conclusion": "learned batch sign remains the current route"},
        {"prose_gap_pair": "AL|OL", "astro_status": "NO_DIRECT_MATCH", "astro_forms": "NONE", "astro_group_count": 0, "prose_strategy": "SOTODAN learned whole sign", "working_meaning_de": "zum Ziel weiter / Folgeanwendung", "register_conclusion": "learned follow-up sign remains the current route"},
    ]

    match_path = OUT / "TWO_HUNDRED_SIXTY_NINTH_FOUR_ASTRO_MATCH_GROUPS.tsv"
    matrix_path = OUT / "TWO_HUNDRED_SIXTY_NINTH_FOUR_GAP_OUTCOMES.tsv"
    revised_path = OUT / "TWO_HUNDRED_SIXTY_NINTH_REVISED_395_ASTRO_GROUPS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTY_NINTH_READABLE_REGISTER_ALGEBRA.md"
    report_path = OUT / "TWO_HUNDRED_SIXTY_NINTH_REPORT.md"
    write_tsv(match_path, matches, list(matches[0]))
    write_tsv(matrix_path, matrix, list(matrix[0]))
    write_tsv(revised_path, revised, list(revised[0]))

    readable = [
        "# Prosa-Ganzzeichen, Astro-Komposition", "",
        "## Quelle → Ziel", "",
        "`saral = AR+AL` steht auf f67r2 und f69v. Es liest sich: **vom Ausgangssektor zum Zielsektor**. Im praktischen Text übernimmt `sshkchdy` dieselbe Gesamtfunktion als gelerntes ÜBERTRAGEN-Zeichen.", "",
        "## Quelle + Fortgang", "",
        "`olar = OL+AR` und `okolar = OK+OL+AR` lesen sich: **vom Ausgangssektor im selben Lauf weiter** bzw. **diesen Lauf aktivieren**. Im praktischen Text ersetzt `lkedy` die Kombination durch das Ganzzeichen WEITERABZUG.", "",
        "## Zwei verbleibende Ganzzeichen", "",
        "Für AR+OR und AL+OL gibt es weiterhin keine direkte Astroform. SUDANSATZ und FOLGEANWENDUNG bleiben gelernte Ganzzeichen.", "",
        "Die Werkstatt nutzt also dasselbe Komponentenwissen verschieden: Diagramme kombinieren abstrakte Adressen frei; körperliche oder stoffliche Routinen bekommen kompakte Fachzeichen.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 269: Relation-Gaps im Astro-Register

## Ergebnis

Zwei der vier auf Prosa fehlenden Paare erscheinen produktiv in Astro. SARAL realisiert AR+AL zweimal auf f67r2/f69v; OLAR und OKOLAR realisieren AR+OL je einmal. Die vorhandenen Diagrammlesungen entsprechen Quelle→Ziel und Fortgang aus Quelle.

In Prosa werden diese Funktionen durch die Fachganzzeichen SSHKCHDY=ÜBERTRAGEN und LKEDY=WEITERABZUG lexicalisiert. AR+OR und AL+OL bleiben auch in Astro ohne direkte Form; SCHOAL und SOTODAN bleiben ihre Ganzzeichenrouten. Das gemischte Codebuch ist somit registerabhängig: freie formale Adressen, kompakte physische Routinen.

Input Astro `{sha(ASTRO)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (match_path, matrix_path, revised_path, readable_path, report_path)
    summary = {
        "status": "PASS", "matched_groups": len(matches), "matched_forms": len({r["visible_surface"] for r in matches}),
        "matched_gap_pairs": len({r["relation_pair"] for r in matches}), "remaining_gap_pairs": 2,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
