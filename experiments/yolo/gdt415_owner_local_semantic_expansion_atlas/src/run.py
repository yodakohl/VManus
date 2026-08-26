#!/usr/bin/env python3
"""Build a concrete owner-local expansion atlas without admitting new pages."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
OUT = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
EVENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_4576_event_semantic_edition.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_715_statement_semantic_edition.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
CORES = ROOT / "experiments/yolo/gdt412_chd_process_core_completion/artifacts/gdt412_final_19_core_dictionary.tsv"
FAILURE_DECK = ROOT / "experiments/yolo/gdt414_next_page_semantic_failure_deck/artifacts/gdt414_19_core_semantic_failure_deck.tsv"
GUARDRAILS = ROOT / "experiments/yolo/gdt414_next_page_semantic_failure_deck/artifacts/gdt414_95_root_register_guardrails.tsv"

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")

# Each phrase is deliberately concrete enough to read, but still projects back
# to exactly one of the nineteen portable cores. It is not a second dictionary.
EXPANSIONS = {
    "SOURCE_SECTION_T": {
        "Y": "LAUFENDER EINTRAG", "OK": "EINTRAGEN", "OL": "WEITERFÜHREN",
        "OT": "NÄCHSTER EINTRAG", "AL": "ZIELSPALTE", "AR": "AUSGANGSZEILE",
        "AIIN": "KENNWERT", "AIN": "TEILWERT", "OR": "EINTRAGSEINHEIT",
        "L": "EINTRAGSVERBINDUNG", "AIR": "LESEBAHN", "CH": "ENTNEHMEN",
        "SH": "FESTHALTEN", "K": "ZUORDNEN", "S": "AUSWÄHLEN",
        "CHD": "EINTRAG BEARBEITEN", "T": "FESTLEGEN", "R": "KENNZEICHNEN",
        "P": "IN EINTRAG EINSETZEN",
    },
    "HERBAL": {
        "Y": "PFLANZENPOSTEN", "OK": "ARBEITSGANG ANSETZEN",
        "OL": "PFLANZENBEHANDLUNG FORTSETZEN", "OT": "NÄCHSTER BEHANDLUNGSGANG",
        "AL": "ZIELSTELLE", "AR": "AUSGANGSMATERIAL", "AIIN": "ARBEITSWERT",
        "AIN": "MATERIALANTEIL", "OR": "ARBEITSEINHEIT",
        "L": "VERBINDUNG IM PFLANZENARTIKEL", "AIR": "VERARBEITUNGSBAHN",
        "CH": "PFLANZENTEIL NEHMEN", "SH": "MATERIAL HALTEN",
        "K": "MATERIAL ZUGEBEN", "S": "PFLANZENTEIL WÄHLEN",
        "CHD": "MATERIAL BEARBEITEN", "T": "ARBEITSSTUFE EINSTELLEN",
        "R": "TEIL MARKIEREN", "P": "MATERIAL EINSETZEN",
    },
    "BIOLOGICAL": {
        "Y": "STATIONSPOSTEN", "OK": "STATIONSGANG ANSETZEN",
        "OL": "STATION WEITERFÜHREN", "OT": "NÄCHSTE STATION",
        "AL": "ZIELSTATION", "AR": "AUSGANGSSTATION", "AIIN": "STATIONSWERT",
        "AIN": "STATIONSANTEIL", "OR": "STATIONSEINHEIT",
        "L": "SICHTBARE VERBINDUNG", "AIR": "STATIONSBAHN",
        "CH": "POSTEN ENTNEHMEN", "SH": "POSTEN HALTEN", "K": "POSTEN ZUFÜHREN",
        "S": "STATION WÄHLEN", "CHD": "POSTEN BEARBEITEN",
        "T": "STATIONSWERT EINSTELLEN", "R": "STATION MARKIEREN",
        "P": "POSTEN EINSETZEN",
    },
    "CELESTIAL": {
        "Y": "POSITIONSPOSTEN", "OK": "POSITION SETZEN",
        "OL": "RINGFOLGE FORTSETZEN", "OT": "NÄCHSTE POSITION",
        "AL": "ZIELPOSITION", "AR": "AUSGANGSPOSITION", "AIIN": "POSITIONSWERT",
        "AIN": "SEKTORANTEIL", "OR": "POSITIONSEINHEIT", "L": "RINGVERBINDUNG",
        "AIR": "RINGBAHN", "CH": "POSITION AUFNEHMEN", "SH": "POSITION HALTEN",
        "K": "WERT ZUORDNEN", "S": "POSITION WÄHLEN",
        "CHD": "EINTRAG BEARBEITEN", "T": "WERT EINSTELLEN",
        "R": "POSITION MARKIEREN", "P": "EINTRAG EINSETZEN",
    },
    "PHARMA": {
        "Y": "DROGENPOSTEN", "OK": "ANSATZ ANSETZEN", "OL": "ANSATZ FORTSETZEN",
        "OT": "NÄCHSTER ANSATZ", "AL": "ZIELGEFÄSS", "AR": "AUSGANGSGEFÄSS",
        "AIIN": "MENGENWERT", "AIN": "DROGENANTEIL", "OR": "ANSATZEINHEIT",
        "L": "GEFÄSSVERBINDUNG", "AIR": "TRANSFERBAHN",
        "CH": "DROGENPOSTEN NEHMEN", "SH": "ANSATZ HALTEN",
        "K": "ZUTAT ZUGEBEN", "S": "DROGENPOSTEN WÄHLEN",
        "CHD": "ANSATZ BEARBEITEN", "T": "ANSATZWERT EINSTELLEN",
        "R": "POSTEN MARKIEREN", "P": "ZUTAT EINSETZEN",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def owner_class(register: str, owner: str) -> str:
    low = owner.lower()
    if register == "SOURCE_SECTION_T":
        return "TEXTBLOCK"
    if register == "HERBAL":
        if any(key in low for key in ("wurzel", "knoll", "soden")):
            return "WURZEL_UND_GANZPFLANZE"
        if any(key in low for key in ("blüt", "bluete", "dolden")):
            return "BLÜTEN_UND_GANZPFLANZE"
        if any(key in low for key in ("kopf", "reifest")):
            return "KOPFSTADIEN_UND_GANZPFLANZE"
        return "GANZPFLANZE"
    if register == "BIOLOGICAL":
        if "unbebildert" in low:
            return "TEXTBLOCK_MIT_SEITENBESITZER"
        if any(key in low for key in ("bad", "pool")):
            return "BAD_ODER_BECKENFELD"
        return "LOKALE_STATIONSGRUPPE"
    if register == "CELESTIAL":
        if "tierkreis" in low:
            return "TIERKREISRING"
        if "stern" in low:
            return "STERNTAFEL_ODER_STERNRING"
        if "himmels" in low:
            return "HIMMELSRAD_UND_TABELLE"
        return "LOKALE_RINGGRUPPE"
    if "droge" in low:
        return "DROGEN_UND_GEFÄSSPOSTEN"
    return "GEFÄSS_UND_ZUTATGRUPPE"


def compact(values: list[str], limit: int = 5) -> str:
    return "|".join(dict.fromkeys(values[:limit])) or "NONE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    components = {row["atom"]: row for row in read_tsv(COMPONENTS)}
    cores = read_tsv(CORES)
    core_by_root = {row["root"]: row for row in cores}
    deck = {row["root"]: row for row in read_tsv(FAILURE_DECK)}
    guardrail_counts = {
        (row["root"], row["register"]): int(row["mention_count"])
        for row in read_tsv(GUARDRAILS)
    }

    event_rows: list[dict[str, object]] = []
    root_mentions: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    owner_mentions: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)

    for event in events:
        register = event["register"]
        atoms = event["component_recipe"].split("+")
        local_atoms: list[str] = []
        back_atoms: list[str] = []
        for atom in atoms:
            if atom in core_by_root:
                local_atoms.append(EXPANSIONS[register][atom])
                back_atoms.append(core_by_root[atom]["selected_minimal_value_de"])
                root_mentions[(atom, register)].append(event)
                owner_mentions[(atom, register, event["owner_de"], owner_class(register, event["owner_de"]))].append(event)
            else:
                local_atoms.append(components[atom]["working_value_de"])
                back_atoms.append(components[atom]["working_value_de"])
        back = " · ".join(back_atoms)
        row = {
            **event,
            "owner_class": owner_class(register, event["owner_de"]),
            "owner_local_reading_de": " · ".join(local_atoms),
            "back_projected_core_reading_de": back,
            "roundtrip_exact": "YES" if back == event["working_core_reading_de"] else "NO",
            "local_expansion_rule": "PORTABLER KERN + SICHTBARER BESITZER; KEINE ZWEITE KERNBEDEUTUNG",
        }
        event_rows.append(row)
        events_by_statement[event["source_statement_id"]].append(row)

    register_rows: list[dict[str, object]] = []
    for root in core_by_root:
        for register in REGISTERS:
            occurrences = root_mentions[(root, register)]
            register_rows.append({
                "root": root,
                "portable_default_de": core_by_root[root]["selected_minimal_value_de"],
                "structural_category": core_by_root[root]["structural_category"],
                "register": register,
                "owner_local_expansion_de": EXPANSIONS[register][root],
                "back_projection_de": core_by_root[root]["selected_minimal_value_de"],
                "mention_count": len(occurrences),
                "guardrail_mention_count": guardrail_counts[(root, register)],
                "event_count": len({r["global_running_event_id"] for r in occurrences}),
                "page_count": len({r["physical_page"] for r in occurrences}),
                "owner_count": len({r["owner_de"] for r in occurrences}),
                "sample_pages": compact(sorted({r["physical_page"] for r in occurrences})),
                "sample_owners": compact(sorted({r["owner_de"] for r in occurrences}), 3),
                "sample_surfaces": compact([r["surface"] for r in occurrences]),
                "do_not_overread_de": deck[root]["do_not_overread_de"],
                "status": "SAME_CORE__OWNER_LOCAL_EXPANSION",
            })

    owner_rows: list[dict[str, object]] = []
    for (root, register, owner, klass), occurrences in sorted(owner_mentions.items()):
        owner_rows.append({
            "root": root,
            "portable_default_de": core_by_root[root]["selected_minimal_value_de"],
            "register": register,
            "owner_class": klass,
            "owner_de": owner,
            "owner_local_expansion_de": EXPANSIONS[register][root],
            "mention_count": len(occurrences),
            "event_count": len({r["global_running_event_id"] for r in occurrences}),
            "statement_count": len({r["source_statement_id"] for r in occurrences}),
            "sample_surfaces": compact([r["surface"] for r in occurrences]),
            "sample_statement_ids": compact([r["source_statement_id"] for r in occurrences], 3),
            "back_projection_de": core_by_root[root]["selected_minimal_value_de"],
            "status": "OWNER_LOCAL_ONLY",
        })

    statement_rows: list[dict[str, object]] = []
    action_roots = {r["root"] for r in cores if r["structural_category"] == "HANDLUNG"}
    event_by_ordinal = {int(row["global_running_ordinal"]): row for row in event_rows}
    running_cursor = 1
    for statement in statements:
        event_count = int(statement["event_count"])
        seq = [event_by_ordinal[ordinal] for ordinal in range(running_cursor, running_cursor + event_count)]
        running_cursor += event_count
        action_chain: list[str] = []
        for event in seq:
            for atom in event["component_recipe"].split("+"):
                if atom in action_roots:
                    action_chain.append(EXPANSIONS[statement["register"]][atom])
        local_sequence = " | ".join(str(row["owner_local_reading_de"]) for row in seq)
        statement_rows.append({
            "global_statement_ordinal": statement["global_statement_ordinal"],
            "global_statement_id": statement["global_statement_id"],
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "owner_class": owner_class(statement["register"], statement["owner_de"]),
            "owner_de": statement["owner_de"],
            "event_count": statement["event_count"],
            "event_ids": "|".join(str(row["global_running_event_id"]) for row in seq),
            "surface_sequence": statement["surface_sequence"],
            "portable_core_reading_de": statement["working_core_reading_de"],
            "owner_local_reading_de": local_sequence,
            "owner_local_action_chain_de": " > ".join(action_chain) or "GEERBTER ARBEITSGANG",
            "owner_local_workshop_paraphrase_de": f"Bei {statement['owner_de']}: {local_sequence}",
            "back_projection_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in seq) else "NO",
            "end_mode": statement["end_mode"],
            "claim_status": "KONKRETE ARBEITSLESUNG; BESITZERLOKAL, NICHT ZWEITE WORTBEDEUTUNG",
        })
    if running_cursor != len(event_rows) + 1:
        raise RuntimeError("statement/event running-order coverage mismatch")

    write_tsv(OUT / "gdt415_95_register_expansion_atlas.tsv", register_rows, [
        "root", "portable_default_de", "structural_category", "register",
        "owner_local_expansion_de", "back_projection_de", "mention_count",
        "guardrail_mention_count", "event_count", "page_count", "owner_count",
        "sample_pages", "sample_owners", "sample_surfaces", "do_not_overread_de", "status",
    ])
    write_tsv(OUT / "gdt415_owner_specific_expansion_atlas.tsv", owner_rows, [
        "root", "portable_default_de", "register", "owner_class", "owner_de",
        "owner_local_expansion_de", "mention_count", "event_count", "statement_count",
        "sample_surfaces", "sample_statement_ids", "back_projection_de", "status",
    ])
    write_tsv(OUT / "gdt415_4576_event_owner_local_edition.tsv", event_rows, list(events[0]) + [
        "owner_class", "owner_local_reading_de", "back_projected_core_reading_de",
        "roundtrip_exact", "local_expansion_rule",
    ])
    write_tsv(OUT / "gdt415_715_statement_owner_local_edition.tsv", statement_rows, [
        "global_statement_ordinal", "global_statement_id", "physical_page", "register",
        "owner_class", "owner_de", "event_count", "event_ids", "surface_sequence",
        "portable_core_reading_de", "owner_local_reading_de", "owner_local_action_chain_de",
        "owner_local_workshop_paraphrase_de", "back_projection_exact", "end_mode", "claim_status",
    ])

    handbook = [
        "# Besitzerlokales Bedeutungswörterbuch für die 26 Seiten", "",
        "Die linke Spalte ist der portable Kern. Die fünf Folgespalten sind konkrete",
        "Arbeitslesungen, die **keine neuen Wortbedeutungen** darstellen. Jede lässt sich",
        "verlustfrei auf den Kern zurückführen.", "",
        "| Kern | SOURCE | HERBAL | BIO | HIMMEL | PHARMA |", "|---|---|---|---|---|---|",
    ]
    for root, core in core_by_root.items():
        handbook.append(
            f"| `{root}` = {core['selected_minimal_value_de']} | "
            + " | ".join(EXPANSIONS[register][root] for register in REGISTERS)
            + " |"
        )
    handbook += [
        "", "## Rückleseregel", "",
        "Beim Wechsel der Bildgattung fällt nur das konkrete Nomen weg: `RINGBAHN`,",
        "`STATIONSBAHN`, `TRANSFERBAHN`, `VERARBEITUNGSBAHN` und `LESEBAHN` werden",
        "alle wieder `AIR=BAHN`. Entsprechend werden `PFLANZENPOSTEN`,",
        "`STATIONSPOSTEN`, `POSITIONSPOSTEN`, `DROGENPOSTEN` und `LAUFENDER EINTRAG`",
        "wieder `Y=POSTEN`. Das ist der Schutz gegen spätere Bedeutungswanderung.", "",
        "## Ganze Ausgabe", "",
        f"- {len(event_rows):,} Ereignisse besitzen eine konkrete Registerlesung.",
        f"- {len(statement_rows):,} Aussagen besitzen eine besitzerlokale Arbeitslesung.",
        f"- {len(owner_rows):,} tatsächlich belegte Kern×Besitzer-Kombinationen sind inventarisiert.",
        "- Keine neue Seite und kein neuer Kern wurde verwendet.",
    ]
    (OUT / "OWNER_LOCAL_EXPANSION_DICTIONARY.md").write_text("\n".join(handbook) + "\n", encoding="utf-8")

    result = {
        "status": "OWNER_LOCAL_EXPANSION_ATLAS_COMPLETE",
        "root_count": len(core_by_root),
        "register_expansion_count": len(register_rows),
        "owner_specific_pair_count": len(owner_rows),
        "event_count": len(event_rows),
        "statement_count": len(statement_rows),
        "running_page_count": len({r["physical_page"] for r in events}),
        "exact_roundtrip_event_count": sum(r["roundtrip_exact"] == "YES" for r in event_rows),
        "exact_roundtrip_statement_count": sum(r["back_projection_exact"] == "YES" for r in statement_rows),
        "new_portable_meanings": 0,
        "new_pages": 0,
    }
    (OUT / "gdt415_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
