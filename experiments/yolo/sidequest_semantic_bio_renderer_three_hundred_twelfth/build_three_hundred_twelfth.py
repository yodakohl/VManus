#!/usr/bin/env python3
"""Turn the fixed-page GDT327 wrapper model into a Biological scribe manual."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
GDT = ROOT / "gdt327_joint_tuple_interlinear.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
VISUAL = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_R3_281_EVENT_INTERLINEAR.tsv"
WRITER = ROOT / "experiments/yolo/sidequest_semantic_bio_roundtrip_three_hundred_eleventh/THREE_HUNDRED_ELEVENTH_124_CARD_FORWARD_WRITER.tsv"
PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")
BIO_PAGES = {"f81v", "f82r", "f83r"}
WRAPPERS = ("NONE", "q", "s", "ch", "che", "sh", "d", "t")


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def modal(counter: Counter[str]) -> str:
    return sorted(counter, key=lambda key: (-counter[key], key))[0]


def locus_number(value: str) -> int:
    match = re.search(r"\.(\d+)$", value)
    if not match:
        raise ValueError(value)
    return int(match.group(1))


def guarded_renderer_rows() -> tuple[list[dict[str, str]], str]:
    columns = (
        "page,locus,group_index,joint_tuple_id,observed_wrapper,line_first,prev_dy,"
        "hand,register,currier,field_ordinal,within_field_position,renderer_state,"
        "wrapper_probabilities_json,observed_wrapper_probability,observed_wrapper_surprisal_bits"
    )
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(GDT), "--selector", "page",
    ]
    for page in PAGES:
        command += ["--allow", page]
    command += ["--columns", columns, "--forbid-prefix", "f84"]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return rows, completed.stderr.strip()


def main() -> None:
    gdt_rows, guard_stats = guarded_renderer_rows()
    events = read(EVENTS)
    visual = {f"E{int(row['event_serial']):03d}": row for row in read(VISUAL)}
    writer = {row["master_card_id"]: row for row in read(WRITER)}

    # Align each guarded GDT327 row with the already fixed event order.  The
    # direct V74 tuple IDs provide an independent equality check on all Bio rows.
    joined: list[dict[str, str]] = []
    for page in PAGES:
        page_events = sorted(
            (row for row in events if row["page"] == page),
            key=lambda row: int(row["event_id"][1:]),
        )
        page_gdt = sorted(
            (row for row in gdt_rows if row["page"] == page),
            key=lambda row: (locus_number(row["locus"]), int(row["group_index"])),
        )
        assert len(page_events) == len(page_gdt)
        for event, renderer in zip(page_events, page_gdt):
            row = {**renderer, **event}
            row["gdt_joint_tuple_id"] = renderer["joint_tuple_id"]
            joined.append(row)
            if page in BIO_PAGES:
                assert visual[event["event_id"]]["joint_tuple_id"] == renderer["joint_tuple_id"]

    master_to_tuple: dict[str, set[str]] = defaultdict(set)
    wrapper_surface: dict[tuple[str, str], set[str]] = defaultdict(set)
    wrapper_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in joined:
        master_to_tuple[row["master_card_id"]].add(row["gdt_joint_tuple_id"])
        wrapper_surface[(row["master_card_id"], row["observed_wrapper"])].add(row["visible_surface"])
        wrapper_counts[row["master_card_id"]][row["observed_wrapper"]] += 1
    assert all(len(values) == 1 for values in master_to_tuple.values())
    assert all(len(values) == 1 for values in wrapper_surface.values())

    bio = [row for row in joined if row["page"] in BIO_PAGES]
    assert len(bio) == 281
    local_counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    for row in bio:
        local_counts[(row["master_card_id"], row["record_unit_id"], row["within_field_position"])][row["visible_surface"]] += 1

    trace_rows: list[dict[str, object]] = []
    for row in bio:
        card_id = row["master_card_id"]
        palette = set(wrapper_counts[card_id])
        if row["wrapper_probabilities_json"]:
            probabilities = json.loads(row["wrapper_probabilities_json"])
            unrestricted = sorted(probabilities, key=lambda key: (-probabilities[key], key))[0]
            predicted_wrapper = sorted(
                palette,
                key=lambda key: (-probabilities[key], -wrapper_counts[card_id][key], key),
            )[0]
            renderer_mode = "POWERED_CELL_PLUS_CARD_PALETTE"
        else:
            probabilities = {}
            unrestricted = "UNLICENSED"
            predicted_wrapper = modal(wrapper_counts[card_id])
            renderer_mode = "CARD_PALETTE_MODAL_FALLBACK"
        predicted_surface = next(iter(wrapper_surface[(card_id, predicted_wrapper)]))
        local_surface = modal(local_counts[(card_id, row["record_unit_id"], row["within_field_position"])])
        vis = visual[row["event_id"]]
        trace_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "locus": row["locus"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "field_id": row["field_id"],
            "master_card_id": card_id,
            "joint_tuple_id": row["gdt_joint_tuple_id"],
            "short_value_de": writer[card_id]["source_short_value_de"],
            "observed_surface": row["visible_surface"],
            "observed_wrapper": row["observed_wrapper"],
            "card_wrapper_palette": "|".join(sorted(palette)),
            "line_first": row["line_first"],
            "prev_dy": row["prev_dy"],
            "within_field_position": row["within_field_position"],
            "owner_status": vis["local_owner_status"],
            "owner_reset_or_break": "YES" if any(x in vis["incoming_contact_and_reset"] for x in ("RESET", "BREAK")) else "NO",
            "renderer_state": row["renderer_state"],
            "unrestricted_model_wrapper": unrestricted,
            "palette_constrained_wrapper": predicted_wrapper,
            "palette_constrained_surface": predicted_surface,
            "palette_renderer_match": "YES" if predicted_surface == row["visible_surface"] else "NO",
            "record_position_surface": local_surface,
            "record_position_match": "YES" if local_surface == row["visible_surface"] else "NO",
            "copy_instruction": "WRITE_BY_PALETTE" if local_surface == row["visible_surface"] else "COPY_LOCAL_ALLOGRAPH_FROM_MASTER",
        })

    trace_path = HERE / "THREE_HUNDRED_TWELFTH_281_RENDERER_TRACE.tsv"
    write(trace_path, trace_rows)

    multi_cards = [row for row in writer.values() if int(row["surface_form_count"]) > 1]
    palette_rows: list[dict[str, object]] = []
    for card in sorted(multi_cards, key=lambda row: row["master_card_id"]):
        card_id = card["master_card_id"]
        selected = [row for row in trace_rows if row["master_card_id"] == card_id]
        fixed_selected = [row for row in joined if row["master_card_id"] == card_id]
        surface_counts = Counter(row["observed_surface"] for row in selected)
        mappings = [
            f"{wrapper}->{next(iter(wrapper_surface[(card_id, wrapper)]))}"
            for wrapper in sorted(wrapper_counts[card_id])
        ]
        palette_rows.append({
            "master_card_id": card_id,
            "short_value_de": card["source_short_value_de"],
            "registered_surfaces": card["registered_surface_forms"],
            "wrapper_to_surface": " | ".join(mappings),
            "fixed_page_wrapper_counts": "|".join(f"{key}:{value}" for key, value in sorted(wrapper_counts[card_id].items())),
            "fixed_page_modal_wrapper": modal(wrapper_counts[card_id]),
            "bio_events": len(selected),
            "bio_surface_counts": "|".join(f"{key}:{value}" for key, value in sorted(surface_counts.items())),
            "distinct_bio_surfaces": len(surface_counts),
            "bio_line_first_events": sum(row["line_first"] == "1" for row in selected),
            "bio_prev_dy_events": sum(row["prev_dy"] == "1" for row in selected),
            "powered_events": sum(row["renderer_state"] == "EXECUTABLE_POWERED_CELL" for row in selected),
            "palette_renderer_hits": sum(row["palette_renderer_match"] == "YES" for row in selected),
            "record_position_hits": sum(row["record_position_match"] == "YES" for row in selected),
            "writer_rule_de": "Nimm die kartenlokale Wrapperpalette; gib s am Zeilenanfang und q nach DY nur einen Vorzug, keine neue Bedeutung.",
            "fixed_page_events": len(fixed_selected),
        })
    palette_path = HERE / "THREE_HUNDRED_TWELFTH_30_MULTISURFACE_PALETTES.tsv"
    write(palette_path, palette_rows)

    wrapper_rows: list[dict[str, object]] = []
    roles = {
        "NONE": "unmarkierte Grundrealisierung der Kartenpalette",
        "q": "nach einer DY-Grenze bevorzugte Eintrittsrealisierung",
        "s": "am physischen Zeilenanfang bevorzugte Eintrittsrealisierung",
        "ch": "kartenlokale kurze Werkstattrealisierung",
        "che": "kartenlokale ausgebaute Werkstattrealisierung",
        "sh": "kartenlokale alternative Werkstattrealisierung",
        "d": "kartenlokale markierte Werkstattrealisierung",
        "t": "kartenlokale markierte Werkstattrealisierung",
    }
    for wrapper in WRAPPERS:
        selected = [row for row in trace_rows if row["observed_wrapper"] == wrapper]
        wrapper_rows.append({
            "wrapper": wrapper,
            "working_role_de": roles[wrapper],
            "bio_events": len(selected),
            "card_types": len({row["master_card_id"] for row in selected}),
            "line_first_events": sum(row["line_first"] == "1" for row in selected),
            "prev_dy_events": sum(row["prev_dy"] == "1" for row in selected),
            "powered_events": sum(row["renderer_state"] == "EXECUTABLE_POWERED_CELL" for row in selected),
            "palette_model_hits": sum(row["palette_renderer_match"] == "YES" for row in selected),
            "semantic_contribution": "NONE",
        })
    wrapper_path = HERE / "THREE_HUNDRED_TWELFTH_EIGHT_WRAPPER_RULES.tsv"
    write(wrapper_path, wrapper_rows)

    residual_rows = [
        {
            "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "statement_id": row["statement_id"],
            "field_id": row["field_id"], "master_card_id": row["master_card_id"], "short_value_de": row["short_value_de"],
            "observed_surface": row["observed_surface"], "record_position_surface": row["record_position_surface"],
            "wrapper_palette": row["card_wrapper_palette"], "owner_status": row["owner_status"],
            "instruction_de": "Diese lokale Schreibform aus dem Masterexemplar kopieren; Bedeutung unverändert.",
        }
        for row in trace_rows if row["record_position_match"] == "NO"
    ]
    residual_path = HERE / "THREE_HUNDRED_TWELFTH_12_LOCAL_COPY_EXCEPTIONS.tsv"
    write(residual_path, residual_rows)

    manual_path = HERE / "THREE_HUNDRED_TWELFTH_RENDERER_MANUAL.md"
    manual_path.write_text(
        "# Kurzes Bio-Renderer-Handbuch für die Werkstatt\n\n"
        "1. Wähle zuerst die Bedeutungs-/Kartenidentität; der Wrapper ändert die Bedeutung nicht.\n"
        "2. Jede Karte besitzt eine kleine gelernte Palette aus NONE, q, s, ch, che, sh, d oder t.\n"
        "3. Am physischen Zeilenanfang bekommt s Vorzug, sofern es zur Palette gehört.\n"
        "4. Nach einer DY-Grenze bekommt q Vorzug, sofern es zur Palette gehört.\n"
        "5. Sonst verwende die häufigste Kartenform; innerhalb eines Records und derselben Feldposition bleibt die lokale Wahl möglichst gleich.\n"
        "6. Nur zwölf konkrete Stellen müssen für die exakte historische Oberfläche aus dem Master kopiert werden. Eine freie Neuschrift darf dort jede registrierte Form derselben Karte wählen.\n\n"
        "Diese Regeln rekonstruieren 227/281 sichtbare Wrapper allein aus formaler Palette und GDT327-Bias. Die lokale Record×Feldpositions-Konvention trifft 269/281; die restlichen zwölf sind echte Kopierdetails, keine zwölf neuen Wörter.\n",
        encoding="utf-8",
    )
    report_path = HERE / "THREE_HUNDRED_TWELFTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 312: Bio-Allographen als Werkstatt-Renderer\n\n"
        "Die drei Bio-Seiten gehören vollständig zu Hand 2 und Register OTHER_B. Dreißig der 124 Karten besitzen auf den sieben festen Prosaseiten mehr als eine registrierte Oberfläche; 27 wechseln tatsächlich innerhalb der Bio-Seiten. Die acht Wrapperklassen verändern keine Kartenbedeutung.\n\n"
        "Von 281 Bio-Ereignissen liegen 210 in einer GDT327-Zelle mit ausführbarem Wrapperprofil. Wenn das Profil auf die tatsächlich gelernte Kartenpalette beschränkt wird, wählt es 157/210 sichtbare Wrapper richtig. Für die 71 nicht lizenzierten Zellen trifft die häufigste feste Kartenform 70/71. Zusammen sind das 227/281. Eine einfache lokale Gewohnheit aus Record und Feldposition trifft 269/281; nur zwölf Oberflächen müssen für eine buchstabengetreue Kopie einzeln angesehen werden.\n\n"
        "Die richtige Werkstattlehre ist daher nicht, q/s/ch/... als neue Wörter zu übersetzen. Sie sind Rendererentscheidungen über einer bereits gewählten Karte. s erhält den bekannten Zeilenanfangsbonus, q den Bonus nach DY; die übrige Wahl kommt aus der kleinen kartenlokalen Palette. Für eine neue passende Handschrift darf der Schreiber frei innerhalb dieser Palette variieren.\n",
        encoding="utf-8",
    )

    summary = {
        "status": "PASS",
        "guard_stats": guard_stats,
        "fixed_prose_events": len(joined),
        "bio_events": len(trace_rows),
        "bio_card_types": len(writer),
        "multisurface_bio_cards": len(palette_rows),
        "cards_switching_surface_inside_bio": sum(int(row["distinct_bio_surfaces"]) > 1 for row in palette_rows),
        "wrapper_classes": len(wrapper_rows),
        "powered_events": sum(row["renderer_state"] == "EXECUTABLE_POWERED_CELL" for row in trace_rows),
        "unlicensed_events": sum(row["renderer_state"] != "EXECUTABLE_POWERED_CELL" for row in trace_rows),
        "palette_renderer_hits": sum(row["palette_renderer_match"] == "YES" for row in trace_rows),
        "record_position_hits": sum(row["record_position_match"] == "YES" for row in trace_rows),
        "local_copy_exceptions": len(residual_rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (GDT, EVENTS, VISUAL, WRITER)},
        "output_hashes": {path.name: sha(path) for path in (trace_path, palette_path, wrapper_path, residual_path, manual_path, report_path)},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
