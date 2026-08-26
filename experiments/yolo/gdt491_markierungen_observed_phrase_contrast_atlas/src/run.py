#!/usr/bin/env python3
"""Build the observed MARKIEREN atlas and eleven T/R phrase contrasts."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt491_markierungen_observed_phrase_contrast_atlas"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G490 = ROOT / "experiments/yolo/gdt490_einstellen_observed_phrase_atlas/artifacts"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
T_FORMS_IN = G490 / "gdt490_22_observed_t_clause_forms.tsv"
T_DEFAULTS_IN = G490 / "gdt490_11_observed_default_phrases.tsv"
CARRIERS = OUT / "gdt491_46_readable_r_carriers.tsv"
FORMS = OUT / "gdt491_22_observed_r_clause_forms.tsv"
CELLS = OUT / "gdt491_11_r_frame_phrase_cells.tsv"
PHRASEBOOK = OUT / "gdt491_11_observed_r_default_phrases.tsv"
CONTRASTS = OUT / "gdt491_11_observed_tr_contrast_cards.tsv"
EXACT_RESTS = OUT / "gdt491_7_exact_german_remainder_pairs.tsv"
OWNER_VARIANTS = OUT / "gdt491_4_owner_variant_contrast_cards.tsv"
REGISTERS = OUT / "gdt491_5_register_phrase_support.tsv"
READABLE = OUT / "GDT491_MARKIEREN_OBSERVED_PHRASE_CONTRAST_ATLAS.md"
RESULT = OUT / "gdt491_result.json"
STATUS = "ALL_ELEVEN_R_FRAMES_HAVE_OBSERVED_PHRASES__SEVEN_EXACT_GERMAN_REMAINDERS__FOUR_OWNER_VARIANTS"
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
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")


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


def frame_meaning(frame: str, action: str) -> str:
    parts = [action if part == "@ACTION" else part for part in frame.split("+")]
    return " · ".join(MEANINGS.get(part, part) for part in parts)


def remainder_meaning(frame: str) -> str:
    parts = [part for part in frame.split("+") if part != "@ACTION"]
    return " · ".join(MEANINGS.get(part, part) for part in parts) if parts else "LEERER FORMALER REST"


def neutralize_action_clause(clause: str) -> str:
    """Replace only the fixed T/R German action realization, preserving the rest."""
    replacements = (
        ("Markiere.", "@ACTION."),
        ("Kennzeichne.", "@ACTION."),
        ("Stelle ein.", "@ACTION."),
        ("Weiter stelle ", "Weiter @ACTION "),
        ("Weiter markiere ", "Weiter @ACTION "),
        ("Stelle ", "@ACTION "),
        ("Markiere ", "@ACTION "),
        ("Kennzeichne ", "@ACTION "),
        ("Lege ", "@ACTION "),
        ("stelle ", "@ACTION "),
        ("markiere ", "@ACTION "),
        ("kennzeichne ", "@ACTION "),
        ("lege ", "@ACTION "),
    )
    neutral = clause
    for old, new in replacements:
        neutral = neutral.replace(old, new)
    return re.sub(r" (?:ein|fest)(?=\.|;| und)", "", neutral)


def build_readable(
    cells: list[dict[str, object]],
    forms: list[dict[str, object]],
    contrasts: list[dict[str, object]],
    registers: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT491 — MARKIEREN-Phrasen und direkte EINSTELLEN/MARKIEREN-Karten",
        "",
        "GDT491 füllt die R-Seite derselben elf GDT428-Rahmen ausschließlich mit bereits vorhandenen GDT416-Sätzen. Danach werden pro Rahmen zwei beobachtete Sätze nebeneinandergestellt. Wo möglich, wird nicht der häufigste Einzelsatz gewählt, sondern ein beobachtetes T/R-Paar mit wortgleichem deutschem Satzrest.",
        "",
        f"- R-Rahmen mit lesbarem Träger: **{result['frame_count']}/{result['frame_count']}**.",
        f"- Exakte R-Träger: **{result['readable_r_carrier_count']}** auf **{result['page_count']} Seiten** und in **{result['register_count']} Registern**.",
        f"- Verschiedene beobachtete R-Klauseln: **{result['observed_r_clause_form_count']}**.",
        f"- Beobachtete R-Defaults: **{result['observed_r_default_phrase_count']}**; erfundene Phrasen: **{result['invented_phrase_count']}**.",
        f"- Direkte T/R-Karten mit identischem deutschen Satzrest: **{result['exact_german_remainder_pair_count']}/11**; mit owner-bedingt verschiedener Wortwahl: **{result['owner_variant_contrast_count']}/11**.",
        "",
        "## Elf beobachtete MARKIEREN-Defaults",
        "",
        "| Rahmen | Arbeitslesung | Träger | Formen | beobachteter Default |",
        "|---|---|---:|---:|---|",
    ]
    for row in cells:
        lines.append(f"| `{row['frozen_frame']}` | `{row['frame_working_meaning_de']}` | {row['carrier_count']} | {row['observed_clause_form_count']} | {row['default_observed_phrase_de']} |")
    lines.extend([
        "",
        "## Elf direkte T/R-Satzkarten",
        "",
        "`RESTGLEICH` bedeutet: Nach Entfernung genau der beobachteten Aktionsform — *stelle … ein/lege … fest* gegen *markiere/kennzeichne* — ist der restliche deutsche Satz buchstabengleich. `OWNER-VARIANTE` bedeutet: Der Komponentenrahmen ist gleich, aber die vorhandenen T- und R-Träger benennen unterschiedliche Besitzerobjekte.",
        "",
    ])
    for row in contrasts:
        lines.extend([
            f"### `{row['frozen_frame']}` — {row['contrast_status']}",
            "",
            f"- T: {row['t_selected_observed_phrase_de']}",
            f"- R: {row['r_selected_observed_phrase_de']}",
            f"- unveränderter Komponentenrest: `{row['portable_remainder_meaning_de']}`",
        ])
        if row["german_sentence_remainder_match"] == "YES":
            lines.append(f"- gemeinsamer deutscher Satzrest: `{row['action_neutral_t_clause_de']}`")
        else:
            lines.append("- Der deutsche Objektwortlaut wechselt mit dem Besitzer; deshalb wird hier kein künstlich vereinheitlichter Satz erzeugt.")
        lines.append("")
    lines.extend([
        "## Alle 22 beobachteten R-Formen",
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
        "## Registerabdeckung",
        "",
        "| Register | Träger | Rahmen | Satzformen | Seiten |",
        "|---|---:|---:|---:|---|",
    ])
    for row in registers:
        lines.append(f"| {row['register']} | {row['carrier_count']} | {row['frame_count']} | {row['observed_clause_form_count']} | {row['page_count']} |")
    lines.extend([
        "",
        "Die Karten machen die bisher abstrakte Unterscheidung konkret: `T` legt einen Posten, Wert oder Bezug als Einstellung fest; `R` kennzeichnet denselben formalen Slot als Bezug. Sie bleiben Werkstattparaphrasen, aber jedes deutsche Beispiel ist tatsächlich im alten Bestand belegt.",
        "",
        "## Nächster Schritt",
        "",
        "Nutze die sieben restgleichen Paare als kleine Aktionsschablonen und zerlege die vier Owner-Varianten (`AL+Y`, `CH+E+Y`, `OR+Y`, vorangestelltes `CH`) in ihre bereits beobachteten Besitzerwörter. Ziel ist ein gemeinsames slotweises Satzmuster, das weiterhin keine neue deutsche Klausel erfindet.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES_IN)
    action_frames = read_tsv(ACTION_FRAMES_IN)
    t_forms = read_tsv(T_FORMS_IN)
    t_defaults = read_tsv(T_DEFAULTS_IN)
    if (len(clauses), len(action_frames), len(t_forms), len(t_defaults)) != (4576, 104, 22, 11):
        raise RuntimeError("Input count drift")
    tr_frames = [row for row in action_frames if row["contrast_pair"] == "T~R"]
    clauses_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe[row["component_recipe"]].append(row)

    carrier_rows: list[dict[str, object]] = []
    form_rows: list[dict[str, object]] = []
    cell_rows: list[dict[str, object]] = []
    phrasebook_rows: list[dict[str, object]] = []
    for frame_number, source in enumerate(tr_frames, 1):
        frame_id = f"G491-F{frame_number:02d}"
        r_recipe = source["frozen_frame"].replace("@ACTION", "R")
        local = clauses_by_recipe[r_recipe]
        if len(local) != int(source["right_event_count"]):
            raise RuntimeError(f"Carrier count mismatch for {source['frozen_frame']}")
        for clause in local:
            carrier_rows.append({
                "carrier_id": f"G491-C{len(carrier_rows) + 1:02d}",
                "frame_id": frame_id,
                "frozen_frame": source["frozen_frame"],
                "frame_working_meaning_de": frame_meaning(source["frozen_frame"], "R"),
                "r_recipe": r_recipe,
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
                "exact_gdt428_r_carrier": "YES",
                "phrase_observed_not_invented": "YES",
            })
        phrase_counter = Counter(row["imperative_clause_de"] for row in local)
        for phrase in sorted(phrase_counter):
            witnesses = [row for row in local if row["imperative_clause_de"] == phrase]
            form_rows.append({
                "form_id": f"G491-P{len(form_rows) + 1:02d}",
                "frame_id": frame_id,
                "frozen_frame": source["frozen_frame"],
                "frame_working_meaning_de": frame_meaning(source["frozen_frame"], "R"),
                "observed_clause_de": phrase,
                "action_neutral_clause_de": neutralize_action_clause(phrase),
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
        cell = {
            "cell_id": f"G491-PC{frame_number:02d}",
            "frame_id": frame_id,
            "frozen_frame": source["frozen_frame"],
            "r_recipe": r_recipe,
            "frame_working_meaning_de": frame_meaning(source["frozen_frame"], "R"),
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
            "all_carriers_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in local) else "NO",
        }
        cell_rows.append(cell)
        phrasebook_rows.append({
            "phrasebook_id": f"G491-D{frame_number:02d}",
            "frozen_frame": source["frozen_frame"],
            "r_recipe": r_recipe,
            "frame_working_meaning_de": frame_meaning(source["frozen_frame"], "R"),
            "default_observed_phrase_de": default_phrase,
            "default_phrase_carrier_count": default_count,
            "alternative_observed_phrase_count": len(phrase_counter) - 1,
            "alternative_observed_phrases_de": " || ".join(phrase for phrase in sorted(phrase_counter) if phrase != default_phrase) or "NONE",
            "source_pages": cell["pages"],
            "source_registers": cell["registers"],
            "phrase_observed_not_invented": "YES",
        })

    t_forms_by_frame: dict[str, list[dict[str, str]]] = defaultdict(list)
    r_forms_by_frame: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in t_forms:
        t_forms_by_frame[row["frozen_frame"]].append(row)
    for row in form_rows:
        r_forms_by_frame[str(row["frozen_frame"])].append(row)
    t_default_map = {row["frozen_frame"]: row for row in t_defaults}
    r_default_map = {str(row["frozen_frame"]): row for row in phrasebook_rows}

    contrast_rows: list[dict[str, object]] = []
    for frame_number, source in enumerate(tr_frames, 1):
        frame = source["frozen_frame"]
        matches: list[tuple[int, int, int, str, str, dict[str, str], dict[str, object]]] = []
        for t_form in t_forms_by_frame[frame]:
            t_neutral = neutralize_action_clause(t_form["observed_clause_de"])
            for r_form in r_forms_by_frame[frame]:
                if t_neutral == r_form["action_neutral_clause_de"]:
                    t_count = int(t_form["carrier_count"])
                    r_count = int(r_form["carrier_count"])
                    matches.append((
                        t_count * r_count,
                        t_count + r_count,
                        -(len(t_form["observed_clause_de"]) + len(str(r_form["observed_clause_de"]))),
                        t_form["observed_clause_de"],
                        str(r_form["observed_clause_de"]),
                        t_form,
                        r_form,
                    ))
        if matches:
            _, _, _, _, _, t_selected, r_selected = sorted(matches, reverse=True)[0]
            match = "YES"
            status = "RESTGLEICH"
            rule = "MAX_SUPPORT_PRODUCT_THEN_TOTAL_THEN_SHORTEST_AMONG_EXACT_ACTION_NEUTRAL_MATCHES"
        else:
            t_default = t_default_map[frame]
            r_default = r_default_map[frame]
            t_selected = next(row for row in t_forms_by_frame[frame] if row["observed_clause_de"] == t_default["default_observed_phrase_de"])
            r_selected = next(row for row in r_forms_by_frame[frame] if row["observed_clause_de"] == r_default["default_observed_phrase_de"])
            match = "NO"
            status = "OWNER-VARIANTE"
            rule = "INDEPENDENT_OBSERVED_DEFAULTS_WHEN_NO_EXACT_ACTION_NEUTRAL_MATCH_EXISTS"
        contrast_rows.append({
            "contrast_id": f"G491-TR{frame_number:02d}",
            "frozen_frame": frame,
            "t_recipe": frame.replace("@ACTION", "T"),
            "r_recipe": frame.replace("@ACTION", "R"),
            "t_working_meaning_de": frame_meaning(frame, "T"),
            "r_working_meaning_de": frame_meaning(frame, "R"),
            "portable_remainder_meaning_de": remainder_meaning(frame),
            "t_atlas_default_phrase_de": t_default_map[frame]["default_observed_phrase_de"],
            "r_atlas_default_phrase_de": r_default_map[frame]["default_observed_phrase_de"],
            "t_selected_observed_phrase_de": t_selected["observed_clause_de"],
            "r_selected_observed_phrase_de": r_selected["observed_clause_de"],
            "t_selected_phrase_carrier_count": t_selected["carrier_count"],
            "r_selected_phrase_carrier_count": r_selected["carrier_count"],
            "t_selected_pages": t_selected["pages"],
            "r_selected_pages": r_selected["pages"],
            "action_neutral_t_clause_de": neutralize_action_clause(t_selected["observed_clause_de"]),
            "action_neutral_r_clause_de": r_selected["action_neutral_clause_de"],
            "german_sentence_remainder_match": match,
            "contrast_status": status,
            "pair_selection_rule": rule,
            "t_selected_is_atlas_default": "YES" if t_selected["observed_clause_de"] == t_default_map[frame]["default_observed_phrase_de"] else "NO",
            "r_selected_is_atlas_default": "YES" if r_selected["observed_clause_de"] == r_default_map[frame]["default_observed_phrase_de"] else "NO",
            "unchanged_formal_frame": "YES",
            "both_phrases_observed_not_invented": "YES",
        })

    exact_rows = [row for row in contrast_rows if row["german_sentence_remainder_match"] == "YES"]
    owner_rows = [row for row in contrast_rows if row["german_sentence_remainder_match"] == "NO"]
    register_rows: list[dict[str, object]] = []
    for register in REGISTER_ORDER:
        local = [row for row in carrier_rows if row["register"] == register]
        register_rows.append({
            "register_id": f"G491-R{len(register_rows) + 1:02d}",
            "register": register,
            "carrier_count": len(local),
            "frame_count": len({str(row["frozen_frame"]) for row in local}),
            "frames": "|".join(sorted({str(row["frozen_frame"]) for row in local})),
            "observed_clause_form_count": len({(str(row["frozen_frame"]), str(row["imperative_clause_de"])) for row in local}),
            "page_count": len({str(row["physical_page"]) for row in local}),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in local})),
            "owner_class_count": len({str(row["owner_class"]) for row in local}),
            "all_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in local) else "NO",
            "all_phrases_observed_not_invented": "YES" if all(row["phrase_observed_not_invented"] == "YES" for row in local) else "NO",
        })

    if tuple(map(len, (carrier_rows, form_rows, cell_rows, phrasebook_rows, contrast_rows, exact_rows, owner_rows, register_rows))) != (46, 22, 11, 11, 11, 7, 4, 5):
        raise RuntimeError("Unexpected phrase/contrast-atlas counts")
    write_tsv(CARRIERS, carrier_rows)
    write_tsv(FORMS, form_rows)
    write_tsv(CELLS, cell_rows)
    write_tsv(PHRASEBOOK, phrasebook_rows)
    write_tsv(CONTRASTS, contrast_rows)
    write_tsv(EXACT_RESTS, exact_rows)
    write_tsv(OWNER_VARIANTS, owner_rows)
    write_tsv(REGISTERS, register_rows)

    result = {
        "status": STATUS,
        "frame_count": len(cell_rows),
        "readable_r_carrier_count": len(carrier_rows),
        "observed_r_clause_form_count": len(form_rows),
        "observed_r_default_phrase_count": len(phrasebook_rows),
        "invented_phrase_count": 0,
        "page_count": len({str(row["physical_page"]) for row in carrier_rows}),
        "register_count": len({str(row["register"]) for row in carrier_rows}),
        "owner_class_count": len({str(row["owner_class"]) for row in carrier_rows}),
        "tr_contrast_card_count": len(contrast_rows),
        "exact_german_remainder_pair_count": len(exact_rows),
        "owner_variant_contrast_count": len(owner_rows),
        "all_frames_have_observed_r_phrase": all(int(row["observed_clause_form_count"]) > 0 for row in cell_rows),
        "all_carriers_roundtrip_exact": all(row["roundtrip_exact"] == "YES" for row in carrier_rows),
        "all_contrast_phrases_observed": all(row["both_phrases_observed_not_invented"] == "YES" for row in contrast_rows),
        "all_contrast_frames_formally_unchanged": all(row["unchanged_formal_frame"] == "YES" for row in contrast_rows),
        "t_selected_default_count": sum(row["t_selected_is_atlas_default"] == "YES" for row in contrast_rows),
        "r_selected_default_count": sum(row["r_selected_is_atlas_default"] == "YES" for row in contrast_rows),
        "meaning_change_count": 0,
        "wording_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Observed GDT416 R phrase atlas and T/R contrast cards in exact GDT428 frames; seven cards share an exact German remainder and four retain owner-local wording, with no invented phrase, new meaning, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(cell_rows, form_rows, contrast_rows, register_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
