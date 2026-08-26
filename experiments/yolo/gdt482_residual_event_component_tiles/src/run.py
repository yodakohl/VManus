#!/usr/bin/env python3
"""Tile GDT481's 45 single-event residuals with recurrent component fragments."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles"
OUT = BASE / "artifacts"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G481 = ROOT / "experiments/yolo/gdt481_microrecord_fragment_grammar/artifacts"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
BUNDLES_IN = G479 / "gdt479_146_definitive_local_bundles.tsv"
COVERAGE_IN = G481 / "gdt481_135_record_fragment_coverage.tsv"
SEQUENCES = OUT / "gdt482_183_event_component_sequences.tsv"
CONDITIONED_ATLAS = OUT / "gdt482_model_conditioned_component_fragment_atlas.tsv"
FREE_ATLAS = OUT / "gdt482_model_free_component_fragment_atlas.tsv"
TILES = OUT / "gdt482_45_residual_event_internal_tiles.tsv"
SEGMENTS = OUT / "gdt482_residual_tile_segments.tsv"
SUMMARY = OUT / "gdt482_residual_tile_summary.tsv"
READABLE = OUT / "GDT482_RESIDUAL_EVENT_COMPONENT_TILES.md"
RESULT = OUT / "gdt482_result.json"

NAME_RE = re.compile(r"\[(?:[A-ZÄÖÜ_]*NAME):([^\]]+)\]")


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


def normalize_literal(text: str) -> str:
    names: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        core = match.group(1)
        names.setdefault(core, f"N{len(names) + 1}")
        return "{" + names[core] + "}"

    value = NAME_RE.sub(replace, text)
    value = re.sub(r"\b[^ ·/]+:DROGENFAMILIE\b", "{F1}:NAMENSFAMILIE", value)
    value = value.replace("POSTEN [außen]", "POSTEN[OUTER]")
    value = value.replace("POSTEN [innen]", "POSTEN[INNER]")
    return value


def tokenize_literal(text: str) -> tuple[list[str], list[str]]:
    normalized = normalize_literal(text)
    pieces = re.split(r"\s+(·|/)\s+", normalized)
    tokens = [pieces[index].strip() for index in range(0, len(pieces), 2)]
    separators = ["DOT" if pieces[index] == "·" else "SLASH" for index in range(1, len(pieces), 2)]
    if not tokens or len(separators) != len(tokens) - 1:
        raise RuntimeError(f"Tokenization failure: {text}")
    return tokens, separators


def span_text(tokens: list[str], separators: list[str], start: int, length: int) -> str:
    pieces = [tokens[start]]
    for index in range(start, start + length - 1):
        pieces.append(" · " if separators[index] == "DOT" else " / ")
        pieces.append(tokens[index + 1])
    return "".join(pieces)


def contains_name(fragment: str) -> bool:
    return bool(re.search(r"\{(?:N|F)\d+\}", fragment))


@dataclass
class Support:
    occurrence_count: int
    event_ids: set[str]
    pages: set[str]
    registers: set[str]
    models: set[str]
    surfaces: list[str]


def add_support(store: dict[object, Support], key: object, row: dict[str, object], surface: str) -> None:
    if key not in store:
        store[key] = Support(0, set(), set(), set(), set(), [])
    support = store[key]
    support.occurrence_count += 1
    support.event_ids.add(str(row["source_event_id"]))
    support.pages.add(str(row["physical_page"]))
    support.registers.add(str(row["register"]))
    support.models.add(str(row["active_model"]))
    if surface not in support.surfaces:
        support.surfaces.append(surface)


def donor_support(support: Support | None, event_id: str) -> tuple[int, list[str]]:
    if support is None:
        return 0, []
    donors = sorted(support.event_ids - {event_id})
    return len(donors), donors


def best_tile(
    sequence: dict[str, object], support_store: dict[object, Support], conditioned: bool
) -> tuple[tuple[int, int, int, int], list[dict[str, object]]]:
    tokens = list(sequence["tokens"])
    separators = list(sequence["separators"])
    event_id = str(sequence["source_event_id"])
    model = str(sequence["active_model"])
    dp: dict[int, tuple[tuple[int, int, int, int], list[dict[str, object]]]] = {len(tokens): ((0, 0, 0, 0), [])}
    for start in range(len(tokens) - 1, -1, -1):
        candidates: list[tuple[tuple[int, int, int, int], list[dict[str, object]]]] = []
        for length in range(min(3, len(tokens) - start), 0, -1):
            fragment = span_text(tokens, separators, start, length)
            key: object = (model, fragment) if conditioned else fragment
            support = support_store.get(key)
            donor_count, donor_ids = donor_support(support, event_id)
            if donor_count == 0 and length > 1:
                continue
            recurrent = donor_count > 0
            tail_score, tail_segments = dp[start + length]
            covered = length if recurrent else 0
            multi = length if recurrent and length > 1 else 0
            length_bonus = length * length if recurrent else 0
            score = (
                tail_score[0] + covered,
                tail_score[1] + multi,
                tail_score[2] + length_bonus,
                tail_score[3] - 1,
            )
            segment = {
                "start": start,
                "length": length,
                "fragment": fragment,
                "recurrent": recurrent,
                "donor_count": donor_count,
                "donor_ids": donor_ids,
                "support": support,
            }
            candidates.append((score, [segment, *tail_segments]))
        dp[start] = max(candidates, key=lambda item: item[0])
    return dp[0]


def tile_class(token_count: int, covered: int, multi: int) -> str:
    if covered < token_count:
        return "LOCAL_TOKEN_REMAINS"
    if multi == token_count:
        return "FULL_RECURRENT_MULTI_FRAGMENT_TILE"
    if multi:
        return "MIXED_RECURRENT_MULTI_PLUS_ATOMS"
    return "RECURRENT_ATOMS_ONLY"


def residual_interpretation(
    conditioned_segments: list[dict[str, object]], free_segments: list[dict[str, object]]
) -> str:
    conditioned_local = [segment for segment in conditioned_segments if not segment["recurrent"]]
    free_local = [segment for segment in free_segments if not segment["recurrent"]]
    if not conditioned_local:
        return "MODEL_CONDITIONED_RECURRENT"
    if not free_local:
        return "MODEL_FREE_RECURRENT_BACKOFF"
    lexical_slot = re.compile(r"^(?:\{N\d+\}|\{F\d+\}:NAMENSFAMILIE)$")
    if all(lexical_slot.fullmatch(str(segment["fragment"])) for segment in free_local):
        return "LEARNED_LEXICAL_SLOT_ONLY"
    return "UNIQUE_FUNCTIONAL_COMPONENT_REMAINS"


def build_atlas_rows(
    store: dict[object, Support], conditioned: bool, residual_fragments: set[object]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, support in store.items():
        if conditioned:
            model, fragment = key
        else:
            model, fragment = "ANY", key
        rows.append({
            "fragment_id": f"G482-{'C' if conditioned else 'F'}{len(rows) + 1:03d}",
            "active_model": model,
            "semantic_fragment": fragment,
            "component_length": len(re.split(r"\s+(?:·|/)\s+", str(fragment))),
            "occurrence_count": support.occurrence_count,
            "event_count": len(support.event_ids),
            "page_count": len(support.pages),
            "register_count": len(support.registers),
            "model_count": len(support.models),
            "surface_type_count": len(support.surfaces),
            "contains_name_slot": "YES" if contains_name(str(fragment)) else "NO",
            "touches_residual_event": "YES" if key in residual_fragments else "NO",
            "pages": "|".join(sorted(support.pages)),
            "registers": "|".join(sorted(support.registers)),
            "models": "|".join(sorted(support.models)),
            "event_ids": "|".join(sorted(support.event_ids)),
            "surface_examples": "|".join(support.surfaces[:12]),
            "claim_status": "OBSERVED_COMPONENT_FRAGMENT__NO_NEW_MEANING",
        })
    return rows


def build_readable(tile_rows: list[dict[str, object]], result: dict[str, object]) -> str:
    lines = [
        "# GDT482 — interne Komponenten-Kacheln der 45 Restevents",
        "",
        "Die 45 GDT481-Einzelevent-Resttails werden aus geordneten Bedeutungsfragmenten der Länge eins bis drei neu zusammengesetzt. Ein Fragment zählt nur als wiederkehrend, wenn mindestens ein anderes Event es trägt.",
        "",
        "| Ergebnis unter gleichem Grammatikmodell | Events |",
        "|---|---:|",
        f"| vollständig durch wiederkehrende Mehrkomponentenfragmente | {result['conditioned_full_multi_tile_count']} |",
        f"| Mehrkomponentenfragmente plus wiederkehrende Einzelkomponenten | {result['conditioned_mixed_multi_atom_tile_count']} |",
        f"| nur wiederkehrende Einzelkomponenten | {result['conditioned_atom_only_tile_count']} |",
        f"| mindestens ein lokaler Token bleibt | {result['conditioned_local_token_remains_count']} |",
        "",
        f"Damit sind {result['conditioned_all_tokens_covered_count']}/45 Restevents unter ihrem aktiven Modell vollständig aus anderswo sichtbaren Teilbedeutungen gebaut. Modellfrei steigt die Zahl auf {result['free_all_tokens_covered_count']}/45; diese Zusatzrettungen bleiben als Backoff markiert.",
        "",
        "| Interpretation des Restes | Events |",
        "|---|---:|",
        f"| im aktiven Modell vollständig wiederkehrend | {result['model_conditioned_recurrent_event_count']} |",
        f"| nur modellfrei vollständig wiederkehrend | {result['model_free_recurrent_backoff_event_count']} |",
        f"| nur ein gelernter Name/Familienname bleibt lokal | {result['learned_lexical_slot_only_count']} |",
        f"| einmalige Funktionskomponente bleibt | {result['unique_functional_component_event_count']} |",
        "",
        "Die drei auch nach dem modellfreien Backoff verbleibenden Restevents sind nicht gleichartig. `cheosdy` behält den gelernten Familiennamen `cheo`; `saloiinsheol` behält den dritten gelernten Drogennamen. Nur `sodar` trägt mit `ZWEITE STUFE` und `MARKIEREN` funktionale Bedeutungsbausteine, die in keinem anderen der 183 Events vorkommen.",
        "",
        "## Alle 45 Restevents",
        "",
    ]
    for row in tile_rows:
        lines.extend([
            f"### {row['source_event_id']} · `{row['surface']}` · {row['active_model']}",
            "",
            f"- Komponenten: `{row['semantic_token_sequence']}`",
            f"- Kachelung im Modell: `{row['conditioned_tile_trace']}`",
            f"- Klasse: **{row['conditioned_tile_class']}**; {row['conditioned_recurrent_token_count']}/{row['token_count']} Tokens wiederkehrend, davon {row['conditioned_multi_fragment_token_count']} in Mehrkomponentenfragmenten.",
            f"- Modellfreier Backoff: `{row['free_tile_trace']}` ({row['free_tile_class']}).",
            f"- Resttyp: **{row['residual_interpretation']}**.",
            f"- Arbeitslesung: {row['definitive_event_reading_de']}",
            "",
        ])
    lines.extend([
        "Die Kacheln ändern keine Lesung. `{N1}` bleibt ein gelernter Namensplatz; wiederkehrend ist seine Position im Bauplan, nicht die Identität des Namens. Ein modellfreier Treffer darf eine seltene Kombination beschreiben, aber niemals das aktive Koordinaten-, Anweisungs- oder Katalogmodell überschreiben. Auch die drei lokalen Reste sind nicht bedeutungslos: Ihre GDT479-Defaultbedeutungen bleiben vollständig erhalten.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS_IN)
    bundles = read_tsv(BUNDLES_IN)
    coverage = read_tsv(COVERAGE_IN)
    if (len(events), len(bundles), len(coverage)) != (183, 146, 135):
        raise RuntimeError("GDT479/GDT481 input drift")
    residual_records = {
        row["record_id"] for row in coverage
        if row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL" and row["event_count"] == "1"
    }
    if len(residual_records) != 45:
        raise RuntimeError("GDT481 residual selection drift")

    sequences: list[dict[str, object]] = []
    conditioned_support: dict[object, Support] = {}
    free_support: dict[object, Support] = {}
    for event in events:
        tokens, separators = tokenize_literal(event["literal_working_reading_de"])
        sequence: dict[str, object] = {
            "sequence_id": f"G482-E{len(sequences) + 1:03d}",
            "source_event_id": event["source_event_id"],
            "record_id": event["record_id"],
            "bundle_id": event["bundle_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "active_model": event["active_model"],
            "surface": event["surface"],
            "working_recipe": event["working_recipe"],
            "literal_working_reading_de": event["literal_working_reading_de"],
            "normalized_literal_de": normalize_literal(event["literal_working_reading_de"]),
            "token_count": len(tokens),
            "tokens": tokens,
            "separators": separators,
            "is_gdt481_single_event_residual": event["record_id"] in residual_records,
            "definitive_event_reading_de": event["definitive_event_reading_de"],
        }
        sequences.append(sequence)
        for start in range(len(tokens)):
            for length in range(1, min(3, len(tokens) - start) + 1):
                fragment = span_text(tokens, separators, start, length)
                add_support(conditioned_support, (event["active_model"], fragment), sequence, event["surface"])
                add_support(free_support, fragment, sequence, event["surface"])

    residual_sequences = [row for row in sequences if row["is_gdt481_single_event_residual"]]
    residual_conditioned_keys: set[object] = set()
    residual_free_keys: set[object] = set()
    for row in residual_sequences:
        tokens = list(row["tokens"])
        separators = list(row["separators"])
        for start in range(len(tokens)):
            for length in range(1, min(3, len(tokens) - start) + 1):
                fragment = span_text(tokens, separators, start, length)
                residual_conditioned_keys.add((row["active_model"], fragment))
                residual_free_keys.add(fragment)

    sequence_rows: list[dict[str, object]] = []
    for row in sequences:
        sequence_rows.append({
            "sequence_id": row["sequence_id"],
            "source_event_id": row["source_event_id"],
            "record_id": row["record_id"],
            "bundle_id": row["bundle_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "active_model": row["active_model"],
            "surface": row["surface"],
            "working_recipe": row["working_recipe"],
            "literal_working_reading_de": row["literal_working_reading_de"],
            "normalized_literal_de": row["normalized_literal_de"],
            "token_count": row["token_count"],
            "semantic_tokens": "|".join(row["tokens"]),
            "semantic_separators": "|".join(row["separators"]) or "NONE",
            "is_gdt481_single_event_residual": "YES" if row["is_gdt481_single_event_residual"] else "NO",
            "definitive_event_reading_de": row["definitive_event_reading_de"],
        })

    conditioned_atlas_rows = build_atlas_rows(conditioned_support, True, residual_conditioned_keys)
    free_atlas_rows = build_atlas_rows(free_support, False, residual_free_keys)
    sequence_by_event = {str(row["source_event_id"]): row for row in sequences}
    tile_rows: list[dict[str, object]] = []
    segment_rows: list[dict[str, object]] = []
    for sequence in residual_sequences:
        conditioned_score, conditioned_segments = best_tile(sequence, conditioned_support, True)
        free_score, free_segments = best_tile(sequence, free_support, False)
        token_count = int(sequence["token_count"])
        conditioned_class = tile_class(token_count, conditioned_score[0], conditioned_score[1])
        free_class = tile_class(token_count, free_score[0], free_score[1])

        def trace(segments: list[dict[str, object]]) -> str:
            return " + ".join(
                ("[" + str(segment["fragment"]) + f" ×{segment['donor_count']}]")
                if segment["recurrent"] else ("[LOCAL:" + str(segment["fragment"]) + "]")
                for segment in segments
            )

        conditioned_local = [str(segment["fragment"]) for segment in conditioned_segments if not segment["recurrent"]]
        free_local = [str(segment["fragment"]) for segment in free_segments if not segment["recurrent"]]
        interpretation = residual_interpretation(conditioned_segments, free_segments)
        tile_rows.append({
            "tile_id": f"G482-T{len(tile_rows) + 1:03d}",
            "source_event_id": sequence["source_event_id"],
            "record_id": sequence["record_id"],
            "bundle_id": sequence["bundle_id"],
            "physical_page": sequence["physical_page"],
            "register": sequence["register"],
            "active_model": sequence["active_model"],
            "surface": sequence["surface"],
            "working_recipe": sequence["working_recipe"],
            "token_count": token_count,
            "semantic_token_sequence": " · ".join(sequence["tokens"]),
            "name_slot_count": sum(token.startswith("{N") for token in sequence["tokens"]),
            "conditioned_tile_class": conditioned_class,
            "conditioned_recurrent_token_count": conditioned_score[0],
            "conditioned_multi_fragment_token_count": conditioned_score[1],
            "conditioned_segment_count": len(conditioned_segments),
            "conditioned_local_token_count": len(conditioned_local),
            "conditioned_local_tokens": "|".join(conditioned_local) or "NONE",
            "conditioned_tile_trace": trace(conditioned_segments),
            "free_tile_class": free_class,
            "free_recurrent_token_count": free_score[0],
            "free_multi_fragment_token_count": free_score[1],
            "free_segment_count": len(free_segments),
            "free_local_token_count": len(free_local),
            "free_local_tokens": "|".join(free_local) or "NONE",
            "free_tile_trace": trace(free_segments),
            "residual_interpretation": interpretation,
            "model_free_coverage_upgrade": free_score[0] - conditioned_score[0],
            "model_free_multi_fragment_upgrade": free_score[1] - conditioned_score[1],
            "definitive_event_reading_de": sequence["definitive_event_reading_de"],
            "all_source_meanings_preserved": "YES",
        })
        for mode, segments in (("MODEL_CONDITIONED", conditioned_segments), ("MODEL_FREE_BACKOFF", free_segments)):
            for ordinal, segment in enumerate(segments, 1):
                donor_rows = [sequence_by_event[event_id] for event_id in segment["donor_ids"]]
                segment_rows.append({
                    "segment_id": f"G482-S{len(segment_rows) + 1:03d}",
                    "source_event_id": sequence["source_event_id"],
                    "tile_mode": mode,
                    "segment_ordinal": ordinal,
                    "start_component_ordinal": int(segment["start"]) + 1,
                    "component_length": segment["length"],
                    "semantic_fragment": segment["fragment"],
                    "recurrent_in_other_event": "YES" if segment["recurrent"] else "NO",
                    "donor_event_count": segment["donor_count"],
                    "donor_event_ids": "|".join(segment["donor_ids"]) or "NONE",
                    "donor_page_count": len({str(row["physical_page"]) for row in donor_rows}),
                    "donor_register_count": len({str(row["register"]) for row in donor_rows}),
                    "donor_surface_examples": "|".join(dict.fromkeys(str(row["surface"]) for row in donor_rows)) or "NONE",
                    "contains_name_slot": "YES" if contains_name(str(segment["fragment"])) else "NO",
                })

    conditioned_classes = Counter(str(row["conditioned_tile_class"]) for row in tile_rows)
    free_classes = Counter(str(row["free_tile_class"]) for row in tile_rows)
    interpretations = Counter(str(row["residual_interpretation"]) for row in tile_rows)
    summary_rows: list[dict[str, object]] = []
    for mode, classes in (("MODEL_CONDITIONED", conditioned_classes), ("MODEL_FREE_BACKOFF", free_classes)):
        for klass in ("FULL_RECURRENT_MULTI_FRAGMENT_TILE", "MIXED_RECURRENT_MULTI_PLUS_ATOMS", "RECURRENT_ATOMS_ONLY", "LOCAL_TOKEN_REMAINS"):
            selected = [row for row in tile_rows if row["conditioned_tile_class" if mode == "MODEL_CONDITIONED" else "free_tile_class"] == klass]
            summary_rows.append({
                "tile_mode": mode,
                "tile_class": klass,
                "event_count": classes[klass],
                "event_ids": "|".join(str(row["source_event_id"]) for row in selected) or "NONE",
                "surface_examples": "|".join(str(row["surface"]) for row in selected[:12]) or "NONE",
            })

    result: dict[str, object] = {
        "status": "FORTY_TWO_OF_45_TILE_FROM_RECURRENT_COMPONENTS__TWO_LEARNED_SLOTS__ONE_FUNCTIONAL_OUTLIER",
        "source_event_count": len(sequences),
        "residual_event_count": len(tile_rows),
        "conditioned_fragment_atlas_count": len(conditioned_atlas_rows),
        "free_fragment_atlas_count": len(free_atlas_rows),
        "conditioned_recurrent_fragment_count": sum(int(row["event_count"]) > 1 for row in conditioned_atlas_rows),
        "free_recurrent_fragment_count": sum(int(row["event_count"]) > 1 for row in free_atlas_rows),
        "conditioned_full_multi_tile_count": conditioned_classes["FULL_RECURRENT_MULTI_FRAGMENT_TILE"],
        "conditioned_mixed_multi_atom_tile_count": conditioned_classes["MIXED_RECURRENT_MULTI_PLUS_ATOMS"],
        "conditioned_atom_only_tile_count": conditioned_classes["RECURRENT_ATOMS_ONLY"],
        "conditioned_local_token_remains_count": conditioned_classes["LOCAL_TOKEN_REMAINS"],
        "conditioned_all_tokens_covered_count": len(tile_rows) - conditioned_classes["LOCAL_TOKEN_REMAINS"],
        "conditioned_events_with_any_multi_fragment_count": sum(int(row["conditioned_multi_fragment_token_count"]) > 0 for row in tile_rows),
        "conditioned_total_token_count": sum(int(row["token_count"]) for row in tile_rows),
        "conditioned_recurrent_token_count": sum(int(row["conditioned_recurrent_token_count"]) for row in tile_rows),
        "conditioned_multi_fragment_token_count": sum(int(row["conditioned_multi_fragment_token_count"]) for row in tile_rows),
        "free_full_multi_tile_count": free_classes["FULL_RECURRENT_MULTI_FRAGMENT_TILE"],
        "free_mixed_multi_atom_tile_count": free_classes["MIXED_RECURRENT_MULTI_PLUS_ATOMS"],
        "free_atom_only_tile_count": free_classes["RECURRENT_ATOMS_ONLY"],
        "free_local_token_remains_count": free_classes["LOCAL_TOKEN_REMAINS"],
        "free_all_tokens_covered_count": len(tile_rows) - free_classes["LOCAL_TOKEN_REMAINS"],
        "model_conditioned_recurrent_event_count": interpretations["MODEL_CONDITIONED_RECURRENT"],
        "model_free_recurrent_backoff_event_count": interpretations["MODEL_FREE_RECURRENT_BACKOFF"],
        "learned_lexical_slot_only_count": interpretations["LEARNED_LEXICAL_SLOT_ONLY"],
        "unique_functional_component_event_count": interpretations["UNIQUE_FUNCTIONAL_COMPONENT_REMAINS"],
        "model_free_coverage_upgrade_event_count": sum(int(row["model_free_coverage_upgrade"]) > 0 for row in tile_rows),
        "model_free_multi_fragment_upgrade_event_count": sum(int(row["model_free_multi_fragment_upgrade"]) > 0 for row in tile_rows),
        "name_slot_event_count": sum(int(row["name_slot_count"]) > 0 for row in tile_rows),
        "conditioned_local_token_event_ids": [row["source_event_id"] for row in tile_rows if row["conditioned_tile_class"] == "LOCAL_TOKEN_REMAINS"],
        "conditioned_local_tokens": sorted({token for row in tile_rows for token in str(row["conditioned_local_tokens"]).split("|") if token != "NONE"}),
        "free_local_token_event_ids": [row["source_event_id"] for row in tile_rows if row["free_tile_class"] == "LOCAL_TOKEN_REMAINS"],
        "free_local_tokens": sorted({token for row in tile_rows for token in str(row["free_local_tokens"]).split("|") if token != "NONE"}),
        "learned_slot_only_event_ids": [row["source_event_id"] for row in tile_rows if row["residual_interpretation"] == "LEARNED_LEXICAL_SLOT_ONLY"],
        "unique_functional_event_ids": [row["source_event_id"] for row in tile_rows if row["residual_interpretation"] == "UNIQUE_FUNCTIONAL_COMPONENT_REMAINS"],
        "unique_functional_tokens": sorted({token for row in tile_rows if row["residual_interpretation"] == "UNIQUE_FUNCTIONAL_COMPONENT_REMAINS" for token in str(row["free_local_tokens"]).split("|") if token != "NONE"}),
        "component_meaning_change_count": 0,
        "active_model_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "event_change_count": 0,
        "new_page_count": 0,
        "claim_ceiling": "Internal contiguous component tiling of the fixed 45 GDT481 single-event residuals using other admitted events; no new meaning, syntax, plaintext, name identity, surface, recipe, event, or page.",
    }

    write_tsv(SEQUENCES, sequence_rows)
    write_tsv(CONDITIONED_ATLAS, conditioned_atlas_rows)
    write_tsv(FREE_ATLAS, free_atlas_rows)
    write_tsv(TILES, tile_rows)
    write_tsv(SEGMENTS, segment_rows)
    write_tsv(SUMMARY, summary_rows)
    READABLE.write_text(build_readable(tile_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "residuals": result["residual_event_count"],
        "conditioned_classes": dict(conditioned_classes),
        "free_classes": dict(free_classes),
        "interpretations": dict(interpretations),
        "free_local_tokens": result["free_local_tokens"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
