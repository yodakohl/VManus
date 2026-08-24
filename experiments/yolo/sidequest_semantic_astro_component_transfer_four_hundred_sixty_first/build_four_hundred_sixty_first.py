#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CARDS = ROOT / "experiments/yolo/sidequest_semantic_whole_card_reduction_four_hundred_fifty_eighth/FOUR_HUNDRED_FIFTY_EIGHTH_173_CARD_REVISED_DICTIONARY.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_R1_395_GROUP_CELESTIAL_INTERLINEAR.tsv"

ATOMIC_VALUE = {
    "AIIN": "Mass", "AIN": "Portion", "AIR": "Wasser", "AL": "Stelle", "AR": "von dort",
    "CH": "abziehen", "CHD": "umsetzen", "CHK": "waermen", "CKH": "Durchlass", "CKHE": "seihen",
    "CTH": "bereit", "DY": "Schluss", "E": "kurz", "EE": "laenger", "EEE": "vollstaendig",
    "IIN": "Sollstufe", "K": "zufuehren", "L": "fuehren", "LDDY": "befestigen und schliessen",
    "LS": "abfuehren", "LSH": "Waschgang", "O": "Arbeitsgang", "OK": "ansetzen",
    "OL": "fortsetzen", "OR": "Ansatz", "OT": "danach", "P": "hinein", "R": "abkuehlen",
    "SH": "halten", "SHED": "absetzen", "SOLK": "auffangen", "T": "fuellen", "Y": "dies",
    "HO": "Zutat", "CHEO": "Auszug",
}

CANONICAL_SURFACES = {
    "aiin": "AIIN", "ain": "AIN", "air": "AIR", "al": "AL", "ar": "AR", "ch": "CH",
    "chd": "CHD", "ched": "CHD", "chk": "CHK", "ckh": "CKH", "ckhe": "CKHE", "cth": "CTH",
    "dy": "DY", "e": "E", "ee": "EE", "eee": "EEE", "iin": "IIN", "k": "K", "l": "L",
    "lddy": "LDDY", "ls": "LS", "lsh": "LSH", "o": "O", "ok": "OK", "ol": "OL",
    "or": "OR", "ot": "OT", "p": "P", "r": "R", "sh": "SH", "shed": "SHED",
    "solk": "SOLK", "t": "T", "y": "Y", "cho": "HO", "sho": "HO", "cheo": "CHEO",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = read(CARDS)
    astro = read(ASTRO)
    exact_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    atom_surface: dict[str, set[str]] = defaultdict(set)
    atom_source: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        surfaces = card["surfaces"].split("|")
        for surface in surfaces:
            exact_surface[surface].append(card)
        parse = card["component_parse"]
        if "+" not in parse and not parse.startswith("WHOLE") and parse not in {"OS", "CFHY", "TALAM"}:
            for surface in surfaces:
                atom_surface[surface].add(parse)
                atom_source[surface].add("ATTESTED_SINGLE_COMPONENT_CARD")
    for surface, component in CANONICAL_SURFACES.items():
        atom_surface[surface].add(component)
        atom_source[surface].add("CANONICAL_COMPONENT_SPELLING")
    forms = sorted(atom_surface, key=lambda item: (-len(item), item))

    def minimal_parses(surface: str) -> list[tuple[str, ...]]:
        parsed_surface = surface[1:] if surface.startswith("q") else surface

        @lru_cache(None)
        def walk(index: int) -> tuple[tuple[str, ...], ...]:
            if index == len(parsed_surface):
                return ((),)
            output: list[tuple[str, ...]] = []
            for form in forms:
                if parsed_surface.startswith(form, index):
                    for component in sorted(atom_surface[form]):
                        for rest in walk(index + len(form)):
                            output.append((component,) + rest)
            return tuple(output)

        parses = list(walk(0))
        if not parses:
            return []
        minimum = min(map(len, parses))
        return sorted(set(parse for parse in parses if len(parse) == minimum))

    group_rows = []
    for row in astro:
        surface = row["surface_display_only"]
        exact = exact_surface[surface]
        parses = minimal_parses(surface) if len(exact) != 1 else []
        if len(exact) == 1:
            status = "EXACT_PROSE_SURFACE"
            selected_parse = exact[0]["component_parse"]
            candidate = exact[0]["small_value_de"]
            exact_id = exact[0]["joint_tuple_id"]
            alternatives = "NONE"
        elif len(parses) == 1:
            status = "UNIQUE_COMPONENT_SEQUENCE"
            selected_parse = "+".join(parses[0])
            candidate = " + ".join(ATOMIC_VALUE[component] for component in parses[0])
            exact_id = "NONE"
            alternatives = "NONE"
        elif parses:
            status = "AMBIGUOUS_COMPONENT_SEQUENCE"
            selected_parse = "NONE"
            candidate = "ASTRO_LOCAL_LABEL_PENDING_CHOICE"
            exact_id = "NONE"
            alternatives = " || ".join("+".join(parse) for parse in parses)
        else:
            status = "ASTRO_LOCAL_LABEL"
            selected_parse = "NONE"
            candidate = "ASTRO_LOCAL_LABEL"
            exact_id = "NONE"
            alternatives = "NONE"
        group_rows.append({
            "group_serial": row["group_serial"], "diagram_id": row["diagram_id"], "page": row["page"],
            "locus": row["locus"], "event_index": row["event_index"], "opaque_local_id": row["opaque_local_id"],
            "surface": surface, "visible_owner": row["v71_visible_owner"], "local_namespace": row["local_namespace"],
            "transfer_status": status, "exact_prose_joint_tuple_id": exact_id,
            "selected_component_parse": selected_parse, "candidate_workshop_value_de": candidate,
            "parse_alternatives": alternatives, "owner_and_namespace_preserved": "YES",
            "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_FIRST_395_ASTRO_GROUP_TRANSFER.tsv", group_rows)

    atom_rows = []
    for surface in sorted(atom_surface):
        components = sorted(atom_surface[surface])
        atom_rows.append({
            "surface_atom": surface, "components": "|".join(components),
            "values_de": "|".join(ATOMIC_VALUE[component] for component in components),
            "source": "|".join(sorted(atom_source[surface])),
            "ambiguous_atom": "YES" if len(components) > 1 else "NO",
        })
    write("FOUR_HUNDRED_SIXTY_FIRST_COMPONENT_SURFACE_LEXICON.tsv", atom_rows)

    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in group_rows:
        by_locus[str(row["locus"])].append(row)
    locus_rows = []
    for locus, rows in by_locus.items():
        transferred = sum(row["transfer_status"] in {"EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE"} for row in rows)
        if transferred == len(rows):
            locus_status = "FULL_COMPONENT_READING"
        elif transferred:
            locus_status = "MIXED_COMPONENT_AND_LOCAL_LABEL"
        else:
            locus_status = "LOCAL_LABEL_ONLY"
        locus_rows.append({
            "locus_row": len(locus_rows) + 1, "diagram_id": rows[0]["diagram_id"], "page": rows[0]["page"],
            "locus": locus, "local_namespace": rows[0]["local_namespace"],
            "visible_owners": "|".join(dict.fromkeys(str(row["visible_owner"]) for row in rows)),
            "groups": len(rows), "group_serials": "|".join(str(row["group_serial"]) for row in rows),
            "exact_surface_groups": sum(row["transfer_status"] == "EXACT_PROSE_SURFACE" for row in rows),
            "unique_component_groups": sum(row["transfer_status"] == "UNIQUE_COMPONENT_SEQUENCE" for row in rows),
            "ambiguous_groups": sum(row["transfer_status"] == "AMBIGUOUS_COMPONENT_SEQUENCE" for row in rows),
            "local_label_groups": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in rows),
            "locus_transfer_status": locus_status,
            "candidate_local_reading_de": " ; ".join(str(row["candidate_workshop_value_de"]) for row in rows),
            "orientation": "UNSPECIFIED", "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_FIRST_142_ASTRO_LOCUS_READINGS.tsv", locus_rows)

    instrument_rows = []
    for diagram_id, page, title in (
        ("A1", "f67r2", "Zwei getrennte Himmelsräder"),
        ("A2", "f68r1", "Mehrpaneel-Sterninstrument"),
        ("A3", "f69v", "Drei getrennte Radtafeln"),
    ):
        rows = [row for row in group_rows if row["diagram_id"] == diagram_id]
        loci = [row for row in locus_rows if row["diagram_id"] == diagram_id]
        instrument_rows.append({
            "diagram_id": diagram_id, "page": page, "title_de": title, "loci": len(loci), "groups": len(rows),
            "exact_surface_groups": sum(row["transfer_status"] == "EXACT_PROSE_SURFACE" for row in rows),
            "unique_component_groups": sum(row["transfer_status"] == "UNIQUE_COMPONENT_SEQUENCE" for row in rows),
            "ambiguous_groups": sum(row["transfer_status"] == "AMBIGUOUS_COMPONENT_SEQUENCE" for row in rows),
            "local_label_groups": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in rows),
            "transferred_groups": sum(row["transfer_status"] in {"EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE"} for row in rows),
            "reading_de": "Lies übertragbare Gruppen als Werkstattoperatoren; kopiere alle übrigen als lokale Himmels- oder Diagrammetiketten.",
            "orientation": "UNSPECIFIED", "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_FIRST_THREE_INSTRUMENT_READINGS.tsv", instrument_rows)

    summary = {
        "status": "PASS", "groups": len(group_rows), "loci": len(locus_rows), "instruments": len(instrument_rows),
        "exact_surface_groups": sum(row["transfer_status"] == "EXACT_PROSE_SURFACE" for row in group_rows),
        "unique_component_groups": sum(row["transfer_status"] == "UNIQUE_COMPONENT_SEQUENCE" for row in group_rows),
        "ambiguous_component_groups": sum(row["transfer_status"] == "AMBIGUOUS_COMPONENT_SEQUENCE" for row in group_rows),
        "local_label_groups": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in group_rows),
        "transferred_groups": sum(row["transfer_status"] in {"EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE"} for row in group_rows),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
