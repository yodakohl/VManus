#!/usr/bin/env python3
"""Compress the remaining learned technical surfaces into a small nomenclator."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_human_dictionary_thirty_fifth_edition/THIRTY_FIFTH_487_SURFACE_TEACHING_DICTIONARY.tsv"


LESSONS = [
    ("N01_CFH", "LEARNED_BODY", ("cfhy",), "AUSWRINGEN", "CFH+Y", "wie ein gelerntes Press- oder Auswringkürzel im Rezeptbuch"),
    ("N02_CPH", "LEARNED_BODY", ("cphy", "ocphy"), "ZWEITER_DURCHGANG", "CPH+Y; Astro O+CPH+Y", "wie ein Kürzel für einen zweiten Arbeits- oder Lesedurchgang"),
    ("N03_PARTITION", "LEARNED_BODY", ("ches", "chety", "chty"), "ABTEILEN", "PARTITION oder PARTITION+TY", "wie ein festes Teilungszeichen neben produktiven Mengenzeichen"),
    ("N04_HO", "LEARNED_BODY", ("cho", "sho", "tshol"), "EINGANGSPOSTEN", "HO; HO+L", "wie ein gelernter Nomenklatorwert für den einzusetzenden Stoff oder Tabelleninput"),
    ("N05_DCHE", "LEARNED_BODY", ("dchey",), "UNTERER_PFLANZENTEIL", "DCHE+Y", "wie ein bildregistergebundenes Kürzel für den am Bild gezeigten unteren Teil"),
    ("N06_PREV", "LEARNED_BODY", ("dchol", "schol"), "VORIGER_POSTEN", "PREV+OL", "wie ein festes Wiederaufnahmezeichen: das Vorige weiter"),
    ("N07_WASH", "LEARNED_BODY", ("lshedy", "lsho", "rshedy"), "WASCHGANG", "WASH+START oder WASH+CLOSE", "wie ein gelernter Arbeitskörper mit Anfangs- und Schlussform"),
    ("N08_LDDY", "LEARNED_BODY", ("qokylddy",), "FESTMACHEN_UND_SCHLIESSEN", "OK+Y+LDDY", "wie ein unteilbarer Werkstattbefehl für Befestigung samt Abschluss"),
    ("N09_SK", "LEARNED_BODY", ("skar",), "AUSGIESSEN", "SK+AR", "wie ein kurzes Ausgusszeichen mit sichtbarer Quellenadresse"),
    ("N10_DAN", "LEARNED_BODY", ("sotodan",), "ANWENDEN", "OT+DAN", "wie ein gelerntes Applikationskürzel nach einem Reihenfolgenmarker"),
    ("N11_DL", "WHOLE_CARD", ("dl",), "ZUSATZ", "DL", "wie ein Nomenklatorzeichen für einen lokal bekannten Zusatz"),
    ("N12_TALAM", "WHOLE_CARD", ("talam",), "AM_ZIEL_VERWAHREN", "TALAM", "wie eine ausgeschriebene feste Werkstattformel im Kürzelregister"),
    ("S01_DAIN", "REGISTER_SPLIT", ("dain",), "PROSA_TUCH__ASTRO_PORTION", "Prosa DAIN whole; Astro AIN", "wie ein gleiches Zeichen mit getrennten Fachregisterwerten"),
    ("S02_ODY", "REGISTER_SPLIT", ("ody",), "PROSA_KUEHLEN__ASTRO_MARKIEREN", "Prosa ODY whole; Astro OD+Y", "wie ein Nomenklatorwert, der nur in der lokalen Tabelle produktiv zerfällt"),
    ("S03_OS", "REGISTER_SPLIT", ("os",), "PROSA_GEFAESS__ASTRO_FELD", "Prosa OS whole; Astro OS field", "wie ein homographes Fachkürzel in zwei Werkstattregistern"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    all_surfaces = read_tsv(SURFACES)
    selected = [row for row in all_surfaces if row["teaching_class"] in {
        "LEARNED_TECHNICAL_BODY", "MEMORIZED_WHOLE_CARD", "REGISTER_SPLIT"
    }]
    by_surface = {row["visible_surface"]: row for row in selected}
    surface_to_lesson: dict[str, tuple[str, str, str, str, str]] = {}
    for lesson_id, kind, surfaces, value, composition, analogy in LESSONS:
        for surface in surfaces:
            if surface in surface_to_lesson:
                raise RuntimeError(f"surface assigned twice: {surface}")
            surface_to_lesson[surface] = (lesson_id, kind, value, composition, analogy)
    if set(surface_to_lesson) != set(by_surface):
        raise RuntimeError(f"lesson coverage mismatch: {set(by_surface) ^ set(surface_to_lesson)}")

    surface_rows: list[dict[str, object]] = []
    for row in selected:
        lesson_id, kind, value, composition, analogy = surface_to_lesson[row["visible_surface"]]
        surface_rows.append({
            "surface_id": row["surface_id"],
            "visible_surface": row["visible_surface"],
            "lesson_id": lesson_id,
            "lesson_kind": kind,
            "register_status": row["register_status"],
            "observed_groups": row["observed_groups"],
            "pages": row["pages"],
            "selected_small_value_de": value,
            "surface_composition": composition,
            "current_atom_sequence": row["atom_sequence"],
            "current_spoken_value_de": row["short_spoken_value_de"],
            "owner_rule_de": row["owner_rule_de"],
            "historical_workshop_analogue_de": analogy,
            "example_group": row["example_group"],
            "example_owner": row["example_owner"],
            "memory_instruction_de": "Lektionswert zuerst lernen; produktive Argumente erst danach anhängen",
            "do_not_split_de": "keine Bedeutung aus einzelnen Buchstaben dieses gelernten Körpers ableiten",
        })
    write_tsv(OUT / "FORTY_THIRD_23_SPECIAL_SURFACES.tsv", surface_rows)

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in surface_rows:
        grouped[str(row["lesson_id"])].append(row)
    lesson_rows: list[dict[str, object]] = []
    for order, (lesson_id, kind, surfaces, value, composition, analogy) in enumerate(LESSONS, 1):
        rows = grouped[lesson_id]
        lesson_rows.append({
            "teaching_order": order,
            "lesson_id": lesson_id,
            "lesson_kind": kind,
            "learned_value_de": value,
            "registered_surfaces": "|".join(surfaces),
            "surface_count": len(surfaces),
            "visible_group_count": sum(int(row["observed_groups"]) for row in rows),
            "pages": "|".join(sorted({page for row in rows for page in str(row["pages"]).split("|")})),
            "composition_rule": composition,
            "workshop_analogue_de": analogy,
            "apprentice_recitation_de": f"{lesson_id}: {value}; Formen {', '.join(surfaces)}.",
        })
    write_tsv(OUT / "FORTY_THIRD_15_NOMENCLATOR_LESSONS.tsv", lesson_rows)

    lines = [
        "# Der kleine Nomenklator",
        "",
        "Die 23 sichtbaren Sonderformen brauchen nicht 23 unabhängige Satzglossen.",
        "Sie werden als zwölf gelernte Werte und drei Registertrennungen unterrichtet.",
        "Produktive Argumente wie Y, AR, OL, OT oder CLOSE werden erst nach dem",
        "gelernten Körper gelesen; einzelne Buchstaben im Körper bleiben stumm.",
        "",
    ]
    for row in lesson_rows:
        lines.extend([
            f"## {row['lesson_id']} — {row['learned_value_de']}",
            "",
            f"Formen: `{row['registered_surfaces']}` · Gruppen: {row['visible_group_count']} · Seiten: {row['pages']}.",
            "",
            f"Regel: {row['composition_rule']}. Vergleich: {row['workshop_analogue_de']}.",
            "",
        ])
    (OUT / "FORTY_THIRD_SMALL_NOMENCLATOR.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    counts = Counter(row["teaching_class"] for row in selected)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "special_surfaces": len(surface_rows),
            "special_groups": sum(int(row["observed_groups"]) for row in surface_rows),
            "nomenclator_lessons": len(lesson_rows),
            "learned_value_lessons": sum(row["lesson_kind"] != "REGISTER_SPLIT" for row in lesson_rows),
            "register_split_lessons": sum(row["lesson_kind"] == "REGISTER_SPLIT" for row in lesson_rows),
            "source_classes": dict(counts),
        },
        "source": {str(SURFACES.relative_to(ROOT)): sha256(SURFACES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
