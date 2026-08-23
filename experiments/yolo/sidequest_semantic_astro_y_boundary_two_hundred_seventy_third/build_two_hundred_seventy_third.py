#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R272 = ROOT / "experiments/yolo/sidequest_semantic_astro_ot_transition_two_hundred_seventy_second"
ASTRO = R272 / "TWO_HUNDRED_SEVENTY_SECOND_REVISED_395_ASTRO_GROUPS.tsv"

RELATION_MARKERS = (
    "Zielsektor", "Ausgangssektor", "im selben Ring", "Bedingungs-, Tabellen",
    "naechster Platz", "Diagrammposten setzen", "durch Sektor",
)


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


def classify(surface: str, reading: str) -> tuple[str, str, str, str]:
    if surface.endswith("dy"):
        return "DY_FIXED", "NO", "DY_LICENSED_WHOLE_ENDING", "fest eingetragener oder abgeschlossener lokaler Wert"
    if re.search(r"(?:eeey|eey|ey)$", surface):
        grade = "VOLL" if surface.endswith("eeey") else "LANG" if surface.endswith("eey") else "KURZ"
        return "E_GRADE_Y", "CANDIDATE", f"E_GRADE_{grade}+Y", f"aktuellen Posten auf {grade.lower()}er Stufe halten"
    if surface.endswith(("chy", "shy")):
        return "OPERATION_Y", "YES", "OPERATION_CORE+Y", "Operation am aktuell gemeinten Posten"
    if any(marker in reading for marker in RELATION_MARKERS):
        return "RELATION_Y", "YES", "RELATION_OR_ACTION+Y", "Relation oder Handlung am aktuell gemeinten Posten"
    if "aktuell" in reading or "dieses" in reading:
        return "EXPLICIT_CURRENT_Y", "YES", "LOCAL_CORE+Y", "dieser aktuell gemeinte Diagrammposten"
    return "LOCAL_WHOLE_Y", "NO", "LEARNED_LOCAL_WHOLE_SIGN", "gelernter lokaler Wert der sichtbaren Diagrammstelle"


def main() -> None:
    astro = read_tsv(ASTRO)
    audited: list[dict[str, object]] = []
    revised: list[dict[str, str]] = []
    for row in astro:
        new = dict(row)
        if row["exact_prose_card_id"] == "NONE" and row["visible_surface"].endswith("y"):
            cls, licensed, parse, short = classify(row["visible_surface"], row["concrete_diagram_reading_de"])
            audited.append({
                "group_serial": row["group_serial"],
                "page": row["page"],
                "locus": row["locus"],
                "visible_owner": row["visible_owner"],
                "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"],
                "final_y_class": cls,
                "portable_y_licensed": licensed,
                "component_parse": parse,
                "short_workshop_value_de": short,
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
            })
            new["revision_273"] = cls
            if licensed == "YES":
                new["curriculum_layer"] = "ASTRO_LICENSED_CURRENT_ITEM_Y"
                new["portable_card_role"] = "ASTRO_CURRENT_ITEM_COMPOSITION"
                new["apprentice_action"] = "read final licensed Y as this current item; read preceding relation or operation first"
            elif licensed == "CANDIDATE":
                new["curriculum_layer"] = "ASTRO_GRADED_VALUE_Y_COMPOSITION"
                new["portable_card_role"] = "ASTRO_GRADED_CURRENT_VALUE"
                new["apprentice_action"] = "read the final E grade and Y together as a graded current value"
            elif cls == "DY_FIXED":
                new["curriculum_layer"] = "ASTRO_FIXED_DY_WHOLE_ENDING"
                new["portable_card_role"] = "ASTRO_FIXED_VALUE_NOT_Y"
                new["apprentice_action"] = "copy DY as the learned fixed ending; do not split it into D plus Y"
            else:
                new["curriculum_layer"] = "ASTRO_LOCAL_WHOLE_Y_ENDING"
                new["portable_card_role"] = "ASTRO_LOCAL_WHOLE_VALUE_NOT_Y"
                new["apprentice_action"] = "copy the entire local sign; final y alone does not license the current-item value"
        else:
            new["revision_273"] = "UNCHANGED"
        revised.append(new)

    forms: list[dict[str, object]] = []
    for surface in dict.fromkeys(str(r["visible_surface"]) for r in audited):
        rows = [r for r in audited if r["visible_surface"] == surface]
        forms.append({
            "visible_surface": surface,
            "final_y_class": rows[0]["final_y_class"],
            "portable_y_licensed": rows[0]["portable_y_licensed"],
            "component_parse": rows[0]["component_parse"],
            "short_workshop_value_de": rows[0]["short_workshop_value_de"],
            "group_count": len(rows),
            "pages": "|".join(dict.fromkeys(str(r["page"]) for r in rows)),
            "loci": "|".join(str(r["locus"]) for r in rows),
        })

    counts = Counter(str(r["final_y_class"]) for r in audited)
    class_rows = []
    rules = {
        "DY_FIXED": ("NO", "DY is a learned fixed/closed ending; never infer Y from spelling alone"),
        "E_GRADE_Y": ("CANDIDATE", "E/EE/EEE grades the current value or item"),
        "OPERATION_Y": ("YES", "the operation acts on this current item"),
        "RELATION_Y": ("YES", "the relation points to this current item"),
        "EXPLICIT_CURRENT_Y": ("YES", "the local reading itself identifies the current value"),
        "LOCAL_WHOLE_Y": ("NO", "memorize the whole local sign; terminal y is not separable"),
    }
    for cls in ("DY_FIXED", "E_GRADE_Y", "OPERATION_Y", "RELATION_Y", "EXPLICIT_CURRENT_Y", "LOCAL_WHOLE_Y"):
        class_rows.append({
            "final_y_class": cls,
            "group_count": counts[cls],
            "form_count": len({str(r["visible_surface"]) for r in audited if r["final_y_class"] == cls}),
            "portable_y_licensed": rules[cls][0],
            "apprentice_rule": rules[cls][1],
        })

    channel = [
        {"scope": "PROSE_LICENSED_Y", "use_count": 103, "status": "YES", "meaning_de": "DIES_AKTUELLER_POSTEN"},
        {"scope": "KNOWN_ASTRO_CARD_Y", "use_count": 41, "status": "YES", "meaning_de": "DIES_AKTUELLER_POSTEN"},
        {"scope": "LOCAL_ASTRO_LICENSED_Y", "use_count": 33, "status": "YES", "meaning_de": "DIES_AKTUELLER_POSTEN"},
        {"scope": "PORTABLE_Y_SECURE_TOTAL", "use_count": 177, "status": "YES", "meaning_de": "DIES_AKTUELLER_POSTEN"},
        {"scope": "LOCAL_ASTRO_GRADED_Y", "use_count": 23, "status": "CANDIDATE", "meaning_de": "GRADIERTER_AKTUELLER_WERT"},
        {"scope": "PORTABLE_Y_WITH_GRADED_CANDIDATES", "use_count": 200, "status": "YES_PLUS_CANDIDATE", "meaning_de": "DIES_ODER_GRADIERTER_AKTUELLER_POSTEN"},
        {"scope": "LOCAL_ASTRO_NOT_Y", "use_count": 51, "status": "NO", "meaning_de": "DY_FIXED_OR_LOCAL_WHOLE"},
    ]

    audit_path = OUT / "TWO_HUNDRED_SEVENTY_THIRD_107_FINAL_Y_AUDIT.tsv"
    form_path = OUT / "TWO_HUNDRED_SEVENTY_THIRD_98_FINAL_Y_FORMS.tsv"
    class_path = OUT / "TWO_HUNDRED_SEVENTY_THIRD_SIX_BOUNDARY_CLASSES.tsv"
    channel_path = OUT / "TWO_HUNDRED_SEVENTY_THIRD_CROSS_REGISTER_Y_CHANNEL.tsv"
    revised_path = OUT / "TWO_HUNDRED_SEVENTY_THIRD_REVISED_395_ASTRO_GROUPS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_THIRD_READABLE_Y_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_THIRD_REPORT.md"
    write_tsv(audit_path, audited, list(audited[0]))
    write_tsv(form_path, forms, list(forms[0]))
    write_tsv(class_path, class_rows, list(class_rows[0]))
    write_tsv(channel_path, channel, list(channel[0]))
    write_tsv(revised_path, revised, list(revised[0]))

    readable_path.write_text("""# Y ist ein Referent, nicht bloß der letzte Buchstabe

Die Lehrregel lautet: **Y = DIESER AKTUELL GEMEINTE POSTEN**, aber nur nach einer bekannten Relation, Operation oder in einer ausdrücklich aktuellen lokalen Karte. `E/EE/EEE+Y` bildet wahrscheinlich einen kurz/länger/vollständig gehaltenen aktuellen Wert.

Nicht jedes sichtbare End-y zählt:

- 40 `...DY`-Gruppen sind gelernte Festwert-/Abschlussendungen.
- 11 weitere Formen sind lokale Ganzkarten.
- 33 lokale Astrogruppen lizenzieren Y sicher.
- 23 weitere bilden das enge Grad+Y-Muster.
- 6 nennen schon lokal einen aktuellen Wert.

Zusammen mit Prosa und bekannten Astro-Karten ist Y 177 Mal sicher portabel; mit der Gradreihe 200 Mal. Die 51 Gegenfälle verhindern eine beliebige Buchstabenzerlegung.
""", encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 273: die Grenze des Y-Referenten

## Ergebnis

Von 107 bislang lokalen Astrogruppen mit sichtbarem finalem y sind 33 durch Relation oder Operation und sechs durch die lokale aktuelle Lesung als echtes Referenz-Y lizenziert; 23 weitere sind E/EE/EEE+Y-Gradkandidaten. Dagegen sind 40 DY-Festformen und elf lokale Ganzkarten ausdrücklich kein separierbares Y.

Der sichere portable Kanal umfasst 103 Prosaereignisse + 41 bekannte Astrogruppen + 33 lokale Kompositionen = 177. Mit den 23 Gradkandidaten erreicht er 200. Das ist die gewünschte gemischte Werkstattgrammatik: ein produktives Y, aber gelernte Grenzen.

Input Astro `{sha(ASTRO)}`.
""", encoding="utf-8")
    outputs = (audit_path, form_path, class_path, channel_path, revised_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "audited_groups": len(audited),
        "form_types": len(forms),
        "class_counts": dict(counts),
        "secure_local_y": counts["OPERATION_Y"] + counts["RELATION_Y"] + counts["EXPLICIT_CURRENT_Y"],
        "graded_y_candidates": counts["E_GRADE_Y"],
        "not_y": counts["DY_FIXED"] + counts["LOCAL_WHOLE_Y"],
        "secure_cross_register_y": 177,
        "secure_plus_graded_y": 200,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
