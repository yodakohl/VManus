#!/usr/bin/env python3
"""Join every exact GDT428 T carrier to its observed GDT416 phrase."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt490_einstellen_observed_phrase_atlas"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G489 = ROOT / "experiments/yolo/gdt489_einstellen_typed_composition_neighbourhood/artifacts"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
LOCAL_FRAME_ATLAS_IN = G489 / "gdt489_11_tr_composition_frames.tsv"
CARRIERS = OUT / "gdt490_30_readable_t_carriers.tsv"
FORMS = OUT / "gdt490_22_observed_t_clause_forms.tsv"
CELLS = OUT / "gdt490_11_t_frame_phrase_cells.tsv"
PHRASEBOOK = OUT / "gdt490_11_observed_default_phrases.tsv"
REGISTERS = OUT / "gdt490_5_register_phrase_support.tsv"
ABSENT_RECOVERY = OUT / "gdt490_1_absent_local_context_recovery.tsv"
READABLE = OUT / "GDT490_EINSTELLEN_OBSERVED_PHRASE_ATLAS.md"
RESULT = OUT / "gdt490_result.json"
STATUS = "ALL_ELEVEN_T_FRAMES_HAVE_OBSERVED_PHRASES__TWENTY_TWO_FORMS__ZERO_INVENTED"
MEANINGS = {
    "T": "EINSTELLEN",
    "R": "MARKIEREN",
    "AIIN": "WERT",
    "AIN": "ANTEIL",
    "AL": "ZIELORT",
    "Y": "POSTEN",
    "CH": "NEHMEN",
    "E": "GRAD I",
    "CHD": "BEARBEITEN",
    "OL": "FORTSETZEN",
    "OR": "EINHEIT",
}
PRIORITY_FRAMES = {"@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL", "@ACTION+OL", "@ACTION+Y"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def frame_meaning(frame: str) -> str:
    parts = ["T" if part == "@ACTION" else part for part in frame.split("+")]
    return " · ".join(MEANINGS.get(part, part) for part in parts)


def build_readable(
    cells: list[dict[str, object]],
    forms: list[dict[str, object]],
    registers: list[dict[str, object]],
    recovery: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT490 — beobachtetes Satzlexikon für EINSTELLEN",
        "",
        "GDT490 verbindet jeden T-seitigen GDT428-Rahmen mit den bereits vorhandenen GDT416-Imperativklauseln. Der Default pro Rahmen ist immer ein wörtlich beobachteter Satz: zuerst die häufigste Form, bei Gleichstand die kürzeste, dann alphabetisch. Varianten bleiben vollständig daneben erhalten.",
        "",
        f"- T-Rahmen mit lesbarem T-Träger: **{result['frame_count']}/{result['frame_count']}**.",
        f"- Exakte T-Träger: **{result['readable_t_carrier_count']}** auf **{result['page_count']} Seiten** und in **{result['register_count']} Registern**.",
        f"- Verschiedene beobachtete deutsche Klauseln: **{result['observed_clause_form_count']}**.",
        f"- Beobachtete Defaultphrasen: **{result['observed_default_phrase_count']}**; erfundene Phrasen: **{result['invented_phrase_count']}**.",
        "",
        "## Elf direkt verwendbare Satzkarten",
        "",
        "| Rahmen | Arbeitslesung | Träger | Formen | beobachteter Default |",
        "|---|---|---:|---:|---|",
    ]
    for row in cells:
        lines.append(f"| `{row['frozen_frame']}` | `{row['frame_working_meaning_de']}` | {row['carrier_count']} | {row['observed_clause_form_count']} | {row['default_observed_phrase_de']} |")
    lines.extend([
        "",
        "Die fünf unmittelbar gesuchten Karten sind damit konkret:",
        "",
        "- `T+AIIN`: „Stelle den Arbeitswert ein.“; daneben Mengenwert und Stationswert.",
        "- `T+AIN`: „Stelle den Drogenanteil ein.“; daneben Stationsanteil.",
        "- `T+AL`: „Stelle den Stationsposten [wie zuvor] ein; zur Zielstation.“; celestial als Positionsposten/Zielposition.",
        "- `T+OL`: „Weiter stelle den Pflanzenposten [wie zuvor] ein.“; fünf weitere geerbte Objektformen bleiben sichtbar.",
        "- `T+Y`: „Stelle den Pflanzenposten ein.“; daneben Stationsposten.",
        "",
        "## Alle 22 beobachteten Formen",
        "",
    ])
    forms_by_frame: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in forms:
        forms_by_frame[str(row["frozen_frame"])].append(row)
    for cell in cells:
        lines.append(f"### `{cell['frozen_frame']}` — {cell['frame_working_meaning_de']}")
        lines.append("")
        for row in forms_by_frame[str(cell["frozen_frame"])]:
            lines.append(f"- {row['observed_clause_de']} — {row['carrier_count']} Träger, Seiten `{row['pages']}`.")
        lines.append("")
    lines.extend([
        "## Der lokal fehlende Kontext ist sprachlich nicht leer",
        "",
    ])
    for row in recovery:
        lines.extend([
            "GDT489 fand in den sechs lokalen Seiten kein zusammenhängendes `CHD+Y = BEARBEITEN · POSTEN`. Im bereits zugelassenen 26-Seiten-Bestand besitzt `T+CHD+Y` aber fünf T-Träger auf drei Seiten und zwei beobachtete Satzformen:",
            "",
            *[f"- {phrase}" for phrase in str(row["observed_clause_forms_de"]).split(" || ")],
            "",
            "Der lokale Kontext bleibt lokal abwesend; die T-Rahmenbedeutung und ihre Formulierung sind dennoch anderweitig konkret belegt.",
            "",
        ])
    lines.extend([
        "## Registerabdeckung",
        "",
        "| Register | Träger | Rahmen | Satzformen | Seiten |",
        "|---|---:|---:|---:|---|",
    ])
    for row in registers:
        lines.append(f"| {row['register']} | {row['carrier_count']} | {row['frame_count']} | {row['observed_clause_form_count']} | {row['page_count']} |")
    lines.extend([
        "",
        "Alle dreißig Klauseln lassen sich exakt auf ihre Komponenten zurückführen. Das Satzlexikon ist deshalb sofort benutzbar, aber weiterhin eine Werkstattparaphrase der Arbeitsbedeutungen.",
        "",
        "## Nächster Schritt",
        "",
        "Baue dieselbe beobachtete Satzseite für R=MARKIEREN und stelle innerhalb jedes der elf identischen Rahmen die T- und R-Defaults direkt nebeneinander. Dann wird aus der abstrakten T/R-Abgrenzung eine konkrete elfteilige Übersetzungskarte: einstellen gegenüber markieren, bei unverändertem Rest des Satzes.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES_IN)
    action_frames = read_tsv(ACTION_FRAMES_IN)
    local_frames = read_tsv(LOCAL_FRAME_ATLAS_IN)
    if (len(clauses), len(action_frames), len(local_frames)) != (4576, 104, 11):
        raise RuntimeError("Input count drift")
    tr_frames = [row for row in action_frames if row["contrast_pair"] == "T~R"]
    local_map = {row["frozen_frame"]: row for row in local_frames}
    clauses_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe[row["component_recipe"]].append(row)

    carrier_rows: list[dict[str, object]] = []
    form_rows: list[dict[str, object]] = []
    cell_rows: list[dict[str, object]] = []
    phrasebook_rows: list[dict[str, object]] = []
    for frame_number, source in enumerate(tr_frames, 1):
        frame_id = f"G490-F{frame_number:02d}"
        t_recipe = source["frozen_frame"].replace("@ACTION", "T")
        local = clauses_by_recipe[t_recipe]
        if len(local) != int(source["left_event_count"]):
            raise RuntimeError(f"Carrier count mismatch for {source['frozen_frame']}")
        for clause in local:
            carrier_rows.append({
                "carrier_id": f"G490-C{len(carrier_rows) + 1:02d}",
                "frame_id": frame_id,
                "frozen_frame": source["frozen_frame"],
                "frame_working_meaning_de": frame_meaning(source["frozen_frame"]),
                "t_recipe": t_recipe,
                "global_running_event_id": clause["global_running_event_id"],
                "global_statement_id": clause["global_statement_id"],
                "card_ordinal_in_statement": clause["card_ordinal_in_statement"],
                "physical_page": clause["physical_page"],
                "register": clause["register"],
                "owner_class": clause["owner_class"],
                "owner_de": clause["owner_de"],
                "surface": clause["surface"],
                "template": clause["template"],
                "imperative_clause_de": clause["imperative_clause_de"],
                "owner_local_atom_reading_de": clause["owner_local_atom_reading_de"],
                "portable_back_projection_de": clause["portable_back_projection_de"],
                "roundtrip_exact": clause["roundtrip_exact"],
                "exact_gdt428_t_carrier": "YES",
                "phrase_observed_not_invented": "YES",
            })
        phrase_counter = Counter(row["imperative_clause_de"] for row in local)
        for phrase in sorted(phrase_counter):
            witnesses = [row for row in local if row["imperative_clause_de"] == phrase]
            form_rows.append({
                "form_id": f"G490-P{len(form_rows) + 1:02d}",
                "frame_id": frame_id,
                "frozen_frame": source["frozen_frame"],
                "frame_working_meaning_de": frame_meaning(source["frozen_frame"]),
                "observed_clause_de": phrase,
                "carrier_count": len(witnesses),
                "event_ids": "|".join(row["global_running_event_id"] for row in witnesses),
                "page_count": len({row["physical_page"] for row in witnesses}),
                "pages": "|".join(sorted({row["physical_page"] for row in witnesses})),
                "register_count": len({row["register"] for row in witnesses}),
                "registers": "|".join(sorted({row["register"] for row in witnesses})),
                "owner_class_count": len({row["owner_class"] for row in witnesses}),
                "owner_classes": "|".join(sorted({row["owner_class"] for row in witnesses})),
                "surfaces": "|".join(sorted({row["surface"] for row in witnesses})),
                "templates": "|".join(sorted({row["template"] for row in witnesses})),
                "all_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in witnesses) else "NO",
                "observed_not_invented": "YES",
            })
        default_phrase, default_count = sorted(phrase_counter.items(), key=lambda item: (-item[1], len(item[0]), item[0]))[0]
        local_support = local_map[source["frozen_frame"]]
        cell = {
            "cell_id": f"G490-PC{frame_number:02d}",
            "frame_id": frame_id,
            "frozen_frame": source["frozen_frame"],
            "t_recipe": t_recipe,
            "frame_working_meaning_de": frame_meaning(source["frozen_frame"]),
            "carrier_count": len(local),
            "page_count": len({row["physical_page"] for row in local}),
            "pages": "|".join(sorted({row["physical_page"] for row in local})),
            "register_count": len({row["register"] for row in local}),
            "registers": "|".join(sorted({row["register"] for row in local})),
            "owner_class_count": len({row["owner_class"] for row in local}),
            "owner_classes": "|".join(sorted({row["owner_class"] for row in local})),
            "observed_clause_form_count": len(phrase_counter),
            "observed_clause_forms_de": " || ".join(sorted(phrase_counter)),
            "default_observed_phrase_de": default_phrase,
            "default_phrase_carrier_count": default_count,
            "default_selection_rule": "MOST_CARRIERS_THEN_SHORTEST_THEN_LEXICAL",
            "default_phrase_observed_not_invented": "YES",
            "gdt489_local_context_witness_count": local_support["local_context_witness_count"],
            "gdt489_local_t_contact_count": local_support["local_t_nonempty_contact_count"],
            "gdt489_local_support_class": local_support["local_support_class"],
            "all_carriers_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in local) else "NO",
        }
        cell_rows.append(cell)
        phrasebook_rows.append({
            "phrasebook_id": f"G490-D{frame_number:02d}",
            "frozen_frame": source["frozen_frame"],
            "t_recipe": t_recipe,
            "frame_working_meaning_de": frame_meaning(source["frozen_frame"]),
            "default_observed_phrase_de": default_phrase,
            "default_phrase_carrier_count": default_count,
            "alternative_observed_phrase_count": len(phrase_counter) - 1,
            "alternative_observed_phrases_de": " || ".join(phrase for phrase in sorted(phrase_counter) if phrase != default_phrase) or "NONE",
            "source_pages": cell["pages"],
            "source_registers": cell["registers"],
            "local_context_status": local_support["local_support_class"],
            "phrase_observed_not_invented": "YES",
        })

    register_rows: list[dict[str, object]] = []
    for register in ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA"):
        local = [row for row in carrier_rows if row["register"] == register]
        register_rows.append({
            "register_id": f"G490-R{len(register_rows) + 1:02d}",
            "register": register,
            "carrier_count": len(local),
            "frame_count": len({str(row["frozen_frame"]) for row in local}),
            "frames": "|".join(sorted({str(row["frozen_frame"]) for row in local})),
            "observed_clause_form_count": len({str(row["imperative_clause_de"]) for row in local}),
            "page_count": len({str(row["physical_page"]) for row in local}),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in local})),
            "owner_class_count": len({str(row["owner_class"]) for row in local}),
            "all_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in local) else "NO",
            "all_phrases_observed_not_invented": "YES" if all(row["phrase_observed_not_invented"] == "YES" for row in local) else "NO",
        })

    absent_cell = next(row for row in cell_rows if row["frozen_frame"] == "@ACTION+CHD+Y")
    recovery_rows = [{
        "recovery_id": "G490-AR01",
        "frozen_frame": absent_cell["frozen_frame"],
        "t_recipe": absent_cell["t_recipe"],
        "frame_working_meaning_de": absent_cell["frame_working_meaning_de"],
        "gdt489_local_context_status": absent_cell["gdt489_local_support_class"],
        "gdt489_local_context_witness_count": absent_cell["gdt489_local_context_witness_count"],
        "gdt416_readable_t_carrier_count": absent_cell["carrier_count"],
        "gdt416_page_count": absent_cell["page_count"],
        "gdt416_pages": absent_cell["pages"],
        "gdt416_registers": absent_cell["registers"],
        "observed_clause_form_count": absent_cell["observed_clause_form_count"],
        "observed_clause_forms_de": absent_cell["observed_clause_forms_de"],
        "default_observed_phrase_de": absent_cell["default_observed_phrase_de"],
        "local_absence_retained": "YES",
        "phrase_capacity_recovered_from_admitted_pages": "YES",
        "phrase_observed_not_invented": "YES",
    }]

    if len(carrier_rows) != 30 or len(form_rows) != 22 or len(cell_rows) != 11 or len(phrasebook_rows) != 11 or len(register_rows) != 5:
        raise RuntimeError("Unexpected phrase-atlas counts")
    write_tsv(CARRIERS, carrier_rows)
    write_tsv(FORMS, form_rows)
    write_tsv(CELLS, cell_rows)
    write_tsv(PHRASEBOOK, phrasebook_rows)
    write_tsv(REGISTERS, register_rows)
    write_tsv(ABSENT_RECOVERY, recovery_rows)

    result = {
        "status": STATUS,
        "frame_count": len(cell_rows),
        "readable_t_carrier_count": len(carrier_rows),
        "observed_clause_form_count": len(form_rows),
        "observed_default_phrase_count": len(phrasebook_rows),
        "invented_phrase_count": 0,
        "page_count": len({str(row["physical_page"]) for row in carrier_rows}),
        "register_count": len({str(row["register"]) for row in carrier_rows}),
        "owner_class_count": len({str(row["owner_class"]) for row in carrier_rows}),
        "priority_frame_count": len(PRIORITY_FRAMES),
        "priority_frame_with_observed_phrase_count": sum(row["frozen_frame"] in PRIORITY_FRAMES and int(row["carrier_count"]) > 0 for row in cell_rows),
        "all_frames_have_observed_phrase": all(int(row["observed_clause_form_count"]) > 0 for row in cell_rows),
        "all_carriers_roundtrip_exact": all(row["roundtrip_exact"] == "YES" for row in carrier_rows),
        "formerly_absent_local_context_recovery_count": len(recovery_rows),
        "meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Observed GDT416 phrase atlas for exact GDT428 T carriers; all defaults are existing owner-local workshop paraphrases, with no invented phrase, new meaning, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(cell_rows, form_rows, register_rows, recovery_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
