#!/usr/bin/env python3
"""Build GDT586: complete running/local reader with the GDT585 name layer."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt586_complete_name_layer_reader"
OUT = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts"
G585 = ROOT / "experiments/yolo/gdt585_learned_name_compound_atlas/artifacts"

INPUTS = {
    "complete_defaults": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "statements_582": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards_582": G582 / "gdt582_744_concrete_local_card_edition.tsv",
    "statements_584": G584 / "gdt584_591_polished_statement_edition.tsv",
    "local_cards_584": G584 / "gdt584_158_polished_local_card_edition.tsv",
    "assignments_585": G585 / "gdt585_109_owner_content_slot_assignments.tsv",
    "labels_585": G585 / "gdt585_89_concrete_name_label_edition.tsv",
    "groups_585": G585 / "gdt585_19_compound_and_pair_readings.tsv",
}

STATUS = (
    "PASS_109_EXACT_NAME_OVERRIDES__793_RUNNING_STATEMENTS__744_LOCAL_CARDS__"
    "107_LOCAL_NAMES_PLUS_2_LOCAL_X__19_CONTEXT_REREADINGS__"
    "SOURCE_ORDER_AND_STAR_RIVAL_REPAIRS"
)


GROUP_REREADINGS: dict[str, tuple[str, str, str, str]] = {
    "GDT585-C001": (
        "SOURCE_ORDER_REPAIRED__VISUAL_PAIR_RETAINED",
        "ORDER_CORRECTION",
        "In Quellreihenfolge steht zuerst die rechte Blütenform mit Folgevermerk und danach die linke Blütenform. In der getrennten Bildspur bleibt die natürliche Links-rechts-Lesung linke plus rechte Blütenform derselben Pflanze die beste Arbeitshypothese.",
        "Der gemeinsame Record endet nach genau diesen zwei Labels; er erlaubt keine laufende Satzlesung und entscheidet noch nicht zwischen zwei Blütenformen und Hauptname plus Beiname.",
    ),
    "GDT585-C002": (
        "KEEP_ONE_FIGURE_TWO_VALUES",
        "SUPPORTS",
        "Die eine Anweisung hält O und ODADY gemeinsam. Am besten liest sich das als ein Figuren- oder Ringeintrag mit Primärwert und mitgeführtem Zweitwert, nicht als zwei zufällig nebeneinanderstehende Einzelwörter.",
        "Der Record ist ein Singleton; außerhalb dieser Karte gibt es keinen zusätzlichen Textkontext.",
    ),
    "GDT585-C003": (
        "KEEP_ORDERED_VALUE_PAIR_TO_TARGET",
        "SUPPORTS",
        "YT und DY bilden unter derselben Halteanweisung ein geordnetes Wertepaar, das gemeinsam zur Zielposition gehört. Welche realen Kalenderwerte dahinterstehen, bleibt offen.",
        "Der Record ist ein Singleton; die Zielrelation stammt aus der sichtbaren technischen Hülle derselben Karte.",
    ),
    "GDT585-C004": (
        "KEEP_TWO_FIELD_RING_ENTRY",
        "SUPPORTS",
        "L und DY werden gemeinsam entlang der Ringbahn gesetzt. Die brauchbarste Lesung ist ein zweifeldriger Ring- oder Figureneintrag, nicht ein zerlegtes natürlichsprachliches Wort.",
        "Der Record ist ein Singleton; die Ringbahn ist die einzige zusätzliche Funktionsangabe.",
    ),
    "GDT585-C005": (
        "KEEP_CATALOGUE_PAIR_WITH_ORIGIN",
        "NEUTRAL",
        "EE und Y bleiben zwei katalogisierte Werte derselben Stelle; OT und AR kennzeichnen Folge und Ausgangszuordnung. Der Kontext erzwingt weder ein Compound noch zwei unabhängige Objekte.",
        "Der Record ist ein Singleton und liefert keine weitere Karte zur Entscheidung.",
    ),
    "GDT585-C006": (
        "KEEP_CARRIED_PAIR_FROM_SOURCE",
        "SUPPORTS",
        "OS und EEEO werden gemeinsam von einer Ausgangsposition gehalten. Das passt weiterhin am besten zu Primärwert plus mitgeführtem Wert innerhalb eines Ringeintrags.",
        "Der Record ist ein Singleton; mehr als die gemeinsame Handlung und Ausgangsrelation ist nicht vorhanden.",
    ),
    "GDT585-C007": (
        "KEEP_CONTINUED_RECORD_PAIR",
        "STRONGLY_SUPPORTS",
        "Der volle Record führt erst A, dann einen Positionswert und AY und endet mit der Anweisung, F und EOR weiter zur Zielposition zu halten. F/EOR ist daher am ehesten das zweifeldrige Schlussglied eines fortgesetzten Ringrecords.",
        "Dies ist einer von nur zwei Fällen mit echtem Mehrkartenkontext; die vier Karten und drei Bundles bleiben in Quellreihenfolge sichtbar.",
    ),
    "GDT585-C008": (
        "KEEP_CATALOGUE_PAIR_WITH_ORIGIN",
        "NEUTRAL",
        "YF und Y bleiben ein geordnetes Katalogpaar mit Ausgangszuordnung. Eine inhaltliche Kalender- oder Sternidentität lässt sich aus dem Singleton nicht ergänzen.",
        "Der Record ist ein Singleton.",
    ),
    "GDT585-C009": (
        "KEEP_SAME_VALUE_TWO_ROLES",
        "STRONGLY_SUPPORTS",
        "Der identische Kurzwert O erscheint zweimal in technisch getrennten Rollen derselben Aufnahme- und Einstellanweisung. Das ist der klarste Gruppenfall für einen wiederholten Wert statt zweier verschieden benannter Sterne.",
        "Der Record ist ein Singleton; die Wiederholung ist vollständig innerhalb derselben festen Karte sichtbar.",
    ),
    "GDT585-C010": (
        "KEEP_LEFT_TERMINAL_CHAIN",
        "STRONGLY_SUPPORTS",
        "Endfigur D und linker Speiseanschluss CHD bilden den ersten Katalogkopf; unmittelbar danach folgt KCHS als linker Anschlusskopf. Der volle Record stärkt damit eine linke Endstellen- und Anschlussfolge.",
        "Dies ist der zweite echte Mehrkartenkontext; beide Loci und Bundles bleiben getrennt und geordnet.",
    ),
    "GDT585-C011": (
        "KEEP_RIGHT_TERMINAL_PACKAGE",
        "SUPPORTS",
        "D plus EDY liest sich weiterhin am besten als Endfigur mit rechtem Entnahme- oder Endanschluss. Der Folgevermerk gehört zur Karte, nicht zu einem neuen Lauftextsatz.",
        "Der Record ist ein Singleton; die Rechtszuordnung bleibt bild- und ownergebunden.",
    ),
    "GDT585-C012": (
        "KEEP_ROOT_AND_BASE_PAIR",
        "SUPPORTS",
        "D und AM bilden ein geordnetes Drogenpaar zwischen Ausgangs- und Zielzuordnung. Wurzeldroge in oder mit einer Salben- oder Fettgrundlage ist die konkreteste aktuelle Lesung, aber noch kein bestätigtes Mischrezept.",
        "Der Record ist ein Singleton; die alte Wasser-Schmalz-Lesung bleibt vollständig als Rivalenspur erhalten.",
    ),
    "GDT585-C013": (
        "KEEP_REPEATED_PLANT_REFERENCE",
        "STRONGLY_SUPPORTS",
        "Y erscheint zweimal in derselben Namensklasse und derselben Karte. Das spricht eher für denselben Kraut- oder Pflanzenreferenten in zwei technischen Rollen als für zwei verschiedene Stoffe.",
        "Der Record ist ein Singleton; die alte zweistufige Weinlesung bleibt der direkte Konkurrent.",
    ),
    "GDT585-C014": (
        "KEEP_ROOT_TO_PLANT_REFERENCE_AS_LEAD",
        "TENTATIVE",
        "D plus DA kann als Wurzelteil einer benannten langblättrigen Mutterpflanze gelesen werden. Die doppelte Ausgangszuordnung erlaubt aber weiterhin zwei katalogisierte Einträge; die possessive Lesung bleibt eine Hypothese.",
        "Der Record ist ein Singleton und entscheidet die Relation zwischen Organ und Pflanzenreferent nicht.",
    ),
    "GDT585-C015": (
        "KEEP_LEAF_ROOT_PACKAGE",
        "SUPPORTS",
        "S und D ergeben am plausibelsten ein Blatt- plus Wurzelpaket. Dass beide Teile sicher von derselben Pflanze stammen, geht über den sichtbaren Singleton hinaus und bleibt ersetzbar.",
        "Der Record ist ein Singleton; Sole oder Salzlösung bleibt als alte Gegenlesung sichtbar.",
    ),
    "GDT585-C016": (
        "KEEP_INFLORESCENCE_HERB_REFERENCE",
        "SUPPORTS",
        "SY plus Y liest sich gut als Blüten- oder Fruchtstand einer Krautform. Die technische Hülle behandelt beide weiterhin als katalogisierte Namen, nicht als automatisch segmentiertes Wort.",
        "Der Record ist ein Singleton; die vitriolhaltige Weinlösung bleibt die alte Gegenlesung.",
    ),
    "GDT585-C017": (
        "KEEP_THREE_OBJECT_INSTRUCTION",
        "GRAMMAR_DOMINATES",
        "Die Grammatik ist hier entscheidend: S, OIIN und E stehen als drei benannte Objekte unter einer Halte- und Fortsetzungsanweisung zum Zielgefäß. Eine gemeinsame Pflanzenfragment-Deutung darf danebenstehen, ersetzt aber nicht diese Dreiobjekt-Anweisung.",
        "Der Record ist ein Singleton; es gibt keinen unabhängigen Absatz, der die drei Namen zu einem lexikalischen Compound macht.",
    ),
    "GDT585-C018": (
        "KEEP_LEAF_TO_PLANT_REFERENCE_AS_LEAD",
        "TENTATIVE",
        "YT plus EM passt als Blattteil mit benannter grauwurzliger Mutterpflanze. Ebenso möglich bleiben zwei katalogisierte Drogen; der Singleton macht die Organ-von-Art-Beziehung nicht zwingend.",
        "Der Record ist ein Singleton; Salbei- und Rautenblatt bleiben als alte Gegenlesung erhalten.",
    ),
    "GDT585-C019": (
        "VISUAL_PAIR_ONLY__TEXTUAL_COMPOUND_REJECTED",
        "WEAKENS",
        "DCHOS und YOR bleiben als Bildhypothese rote Fingerwurzel neben Trockenvorrat brauchbar. Textlich sind es jedoch zwei verschiedene Singleton-Records und Owner; dazwischen steht OKAIN als eigener Record. GDT586 verbindet sie deshalb niemals zu einem Satz oder Rezept.",
        "Der exakte lokale Strom zeigt B140/R129, dann B141/R130 und erst danach B142/R131. Ingwerwurzel plus Zimtrinde bleibt eine optische Rivalenlesung, keine grammatische Paarung.",
    ),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pipe(values: Iterable[str]) -> str:
    return "|".join(str(value) for value in values) or "NONE"


def exact_override_trace(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "NONE"
    return " ".join(
        f"[{row['slot_id']}:{row['gdt582_exact_legacy_default_de']}=>{row['gdt585_primary_default_de']}]"
        for row in rows
    )


def apply_exact_running_overrides(
    base: str, overrides: list[dict[str, Any]], statement_id: str
) -> str:
    result = base
    for row in overrides:
        old = str(row["gdt582_exact_legacy_default_de"])
        new = str(row["gdt585_primary_default_de"])
        if result.count(old) != 1:
            raise RuntimeError(
                f"Running override is not exact-once in {statement_id}: {old!r}"
            )
        result = result.replace(old, new, 1)
    return result


def build_injections(
    assignments: list[dict[str, str]],
    complete_by_slot: dict[str, dict[str, str]],
    local_by_event: dict[str, dict[str, str]],
    statement_base_source: dict[str, str],
    local_base_source: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in assignments:
        slot_id = source["slot_id"]
        if slot_id not in complete_by_slot:
            raise RuntimeError(f"GDT585 slot absent from GDT582 ledger: {slot_id}")
        ledger = complete_by_slot[slot_id]
        if source["source_kind"] == "GDT581_NAME_SPAN":
            event_id = source["source_event_or_card_id"]
            card = local_by_event[event_id]
            unit_kind = "LOCAL_CARD"
            unit_id = card["local_card_host_key"]
            unit_join_key = event_id
            base_source = local_base_source[event_id]
        elif source["source_kind"] == "GDT582_OWNER_BOUND_LOCAL_X":
            unit_kind = "RUNNING_STATEMENT"
            unit_id = source["statement_or_record_id"]
            unit_join_key = unit_id
            base_source = statement_base_source[unit_id]
        else:
            raise RuntimeError(f"Unexpected GDT585 source kind: {source['source_kind']}")

        exact_old = ledger["gdt582_concrete_default_de"]
        declared_old = source["gdt582_legacy_house_alias_de"]
        alias_status = (
            "GDT585_DECLARED_ALIAS_EXACT"
            if exact_old == declared_old
            else "RESTORED_EXACT_GDT582_VALUE_WHERE_GDT585_DECLARED_NONE"
        )
        rows.append(
            {
                "injection_ordinal": len(rows) + 1,
                "slot_id": slot_id,
                "source_kind": source["source_kind"],
                "source_event_or_card_id": source["source_event_or_card_id"],
                "reader_unit_kind": unit_kind,
                "reader_unit_id": unit_id,
                "reader_unit_join_key": unit_join_key,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "locus": source["locus"],
                "surface": source["surface"],
                "raw_name_core": source["raw_name_core"],
                "content_class": source["content_class"],
                "name_slot_in_label": source["name_slot_in_label"],
                "gdt585_primary_default_de": source["gdt585_primary_default_de"],
                "gdt582_exact_legacy_default_de": exact_old,
                "gdt585_declared_legacy_alias_de": declared_old,
                "legacy_alias_reconciliation": alias_status,
                "strongest_rival_de": source["strongest_rival_de"],
                "composition_atom_de": source["composition_atom_de"],
                "base_reader_source": base_source,
                "primary_governor_key": source["primary_governor_key"],
                "guard": (
                    "EXACT_SLOT_ID_JOIN__PRIMARY_AND_EXACT_GDT582_RIVAL_BOTH_RETAINED__"
                    "NO_SUBSTRING_PROPAGATION"
                ),
            }
        )
    return rows


def build_statement_rows(
    statements_582: list[dict[str, str]],
    statements_584: list[dict[str, str]],
    injections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    polished = {row["statement_id"]: row for row in statements_584}
    by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in injections:
        if row["reader_unit_kind"] == "RUNNING_STATEMENT":
            by_statement[str(row["reader_unit_id"])].append(row)
    output: list[dict[str, Any]] = []
    for source in statements_582:
        statement_id = source["statement_id"]
        if statement_id in polished:
            layer = "GDT584_POLISHED_STATEMENT"
            base = polished[statement_id]["gdt584_polished_paragraph_de"]
            exact_trace_source = "GDT584_EXACT_SLOT_TRACE"
            exact_trace = polished[statement_id]["gdt584_exact_slot_trace_de"]
        else:
            layer = "GDT582_CONCRETE_STATEMENT"
            base = source["concrete_working_reading_de"]
            exact_trace_source = "GDT582_COMPLETE_LEDGER_BY_STATEMENT_ID"
            exact_trace = "SEE_GDT582_15889_LEDGER"
        overrides = sorted(
            by_statement.get(statement_id, []), key=lambda row: row["slot_id"]
        )
        current = apply_exact_running_overrides(base, overrides, statement_id)
        output.append(
            {
                "reader_statement_ordinal": len(output) + 1,
                "statement_id": statement_id,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner_id": source["owner_id"],
                "event_count": source["event_count"],
                "event_ids": source["event_ids"],
                "surface_sequence": source["surface_sequence"],
                "complete_slot_count": source["complete_slot_count"],
                "base_reader_source": layer,
                "base_exact_trace_source": exact_trace_source,
                "base_exact_slot_trace_de": exact_trace,
                "name_override_count": len(overrides),
                "name_override_slot_ids": pipe(row["slot_id"] for row in overrides),
                "gdt582_legacy_default_sequence": pipe(
                    row["gdt582_exact_legacy_default_de"] for row in overrides
                ),
                "gdt585_primary_default_sequence": pipe(
                    row["gdt585_primary_default_de"] for row in overrides
                ),
                "exact_name_override_trace_de": exact_override_trace(overrides),
                "legacy_reader_de": base if overrides else "SAME_AS_PRIMARY__NO_NAME_OVERRIDE",
                "gdt586_primary_reader_de": current,
                "name_layer_status": (
                    "EXACT_OWNER_BOUND_LOCAL_X_REPLACED"
                    if overrides
                    else "UNCHANGED_BY_NAME_LAYER"
                ),
                "guard": (
                    "FIXED_793_STATEMENTS__GDT584_WHERE_AVAILABLE__GDT582_OTHERWISE__"
                    "ONLY_EXACT_LOCAL_X_SLOT_VALUES_CHANGED"
                ),
            }
        )
    return output


def build_local_rows(
    local_582: list[dict[str, str]],
    local_584: list[dict[str, str]],
    labels_585: list[dict[str, str]],
    injections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    polished = {row["source_event_id"]: row for row in local_584}
    labels = {row["source_event_id"]: row for row in labels_585}
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in injections:
        if row["reader_unit_kind"] == "LOCAL_CARD":
            by_event[str(row["source_event_or_card_id"])].append(row)
    output: list[dict[str, Any]] = []
    for source in local_582:
        event_id = source["source_event_id"]
        if event_id in polished:
            legacy_source = "GDT584_POLISHED_LOCAL_CARD"
            legacy = polished[event_id]["gdt584_polished_local_clause_de"]
            trace = polished[event_id]["gdt584_exact_slot_trace_de"]
            trace_source = "GDT584_EXACT_SLOT_TRACE"
        else:
            legacy_source = "GDT582_CONCRETE_LOCAL_CARD"
            legacy = source["concrete_working_clause_de"]
            trace = source["concrete_slot_trace_de"]
            trace_source = "GDT582_EXACT_SLOT_TRACE"
        overrides = sorted(
            by_event.get(event_id, []),
            key=lambda row: (int(row["name_slot_in_label"]), row["slot_id"]),
        )
        label = labels.get(event_id)
        if label:
            if not overrides:
                raise RuntimeError(f"GDT585 label has no exact name override: {event_id}")
            primary = label["gdt585_primary_reading_de"]
            primary_source = "GDT585_GRAMMAR_AWARE_NAME_LABEL"
            raw_grammar = label["source_grammar_reading_de"]
            composition = label["composition_hypothesis_de"]
            compound_id = label["compound_group_id"]
            selected_model = label["gdt585_selected_model"]
        else:
            if overrides:
                raise RuntimeError(f"Name-bearing card absent from GDT585 label edition: {event_id}")
            primary = legacy
            primary_source = legacy_source
            raw_grammar = "NOT_APPLICABLE"
            composition = "NONE"
            compound_id = "NONE"
            selected_model = source["active_local_model"]
        output.append(
            {
                "reader_local_card_ordinal": len(output) + 1,
                "local_card_host_key": source["local_card_host_key"],
                "source_event_id": event_id,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "locus": source["locus"],
                "record_id": source["record_id"],
                "record_governor_key": source["record_governor_key"],
                "bundle_id": source["bundle_id"],
                "bundle_governor_key": source["bundle_governor_key"],
                "owner_de": source["owner_de"],
                "surface": source["surface"],
                "component_recipe": source["component_recipe"],
                "complete_slot_count": source["complete_slot_count"],
                "base_reader_source": legacy_source,
                "primary_reader_source": primary_source,
                "base_exact_trace_source": trace_source,
                "base_exact_slot_trace_de": trace,
                "name_override_count": len(overrides),
                "name_override_slot_ids": pipe(row["slot_id"] for row in overrides),
                "raw_name_core_sequence": pipe(row["raw_name_core"] for row in overrides),
                "gdt582_legacy_default_sequence": pipe(
                    row["gdt582_exact_legacy_default_de"] for row in overrides
                ),
                "gdt585_primary_default_sequence": pipe(
                    row["gdt585_primary_default_de"] for row in overrides
                ),
                "exact_name_override_trace_de": exact_override_trace(overrides),
                "gdt585_selected_model": selected_model,
                "gdt585_source_grammar_reading_de": raw_grammar,
                "gdt585_composition_hypothesis_de": composition,
                "compound_group_id": compound_id,
                "legacy_reader_de": legacy if overrides else "SAME_AS_PRIMARY__NO_NAME_OVERRIDE",
                "gdt586_primary_reader_de": primary,
                "running_statement_link_status": (
                    "NONE__LOCAL_CARD_GUARD_FORBIDS_RUNNING_SENTENCE_INHERITANCE"
                ),
                "name_layer_status": (
                    "EXACT_GDT585_NAME_LABEL_SELECTED"
                    if overrides
                    else "UNCHANGED_BY_NAME_LAYER"
                ),
                "guard": (
                    "FIXED_744_LOCAL_CARDS__OWNER_RECORD_BUNDLE_AND_LOCUS_RETAINED__"
                    "NO_RUNNING_STATEMENT_ATTACHMENT"
                ),
            }
        )
    return output


def build_group_rows(
    groups_585: list[dict[str, str]],
    local_rows: list[dict[str, Any]],
    injections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    local_by_event = {str(row["source_event_id"]): row for row in local_rows}
    by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in local_rows:
        by_record[str(row["record_id"])].append(row)
    injections_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in injections:
        if row["reader_unit_kind"] == "LOCAL_CARD":
            injections_by_event[str(row["source_event_or_card_id"])].append(row)
    output: list[dict[str, Any]] = []
    for source in groups_585:
        compound_id = source["compound_id"]
        if compound_id not in GROUP_REREADINGS:
            raise RuntimeError(f"Missing manual rereading for {compound_id}")
        disposition, effect, best_reading, context_limit = GROUP_REREADINGS[compound_id]
        declared_ids = source["source_event_ids"].split("|")
        source_order_ids = sorted(
            declared_ids,
            key=lambda event_id: int(local_by_event[event_id]["reader_local_card_ordinal"]),
        )
        record_ids: list[str] = []
        bundle_ids: list[str] = []
        for event_id in source_order_ids:
            row = local_by_event[event_id]
            if row["record_id"] not in record_ids:
                record_ids.append(str(row["record_id"]))
            if row["bundle_id"] not in bundle_ids:
                bundle_ids.append(str(row["bundle_id"]))

        if compound_id == "GDT585-C019":
            first = min(
                int(local_by_event[event_id]["reader_local_card_ordinal"])
                for event_id in source_order_ids
            )
            last = max(
                int(local_by_event[event_id]["reader_local_card_ordinal"])
                for event_id in source_order_ids
            )
            context = [
                row for row in local_rows
                if first <= int(row["reader_local_card_ordinal"]) <= last
            ]
            context_scope = "EXACT_LOCAL_STREAM_SPAN_WITH_INTERVENING_RECORD"
        else:
            context = []
            seen: set[str] = set()
            for record_id in record_ids:
                for row in by_record[record_id]:
                    event_id = str(row["source_event_id"])
                    if event_id not in seen:
                        seen.add(event_id)
                        context.append(row)
            context.sort(key=lambda row: int(row["reader_local_card_ordinal"]))
            context_scope = (
                "EXACT_MULTI_CARD_RECORD_CONTEXT"
                if len(context) > len(source_order_ids)
                else "EXACT_SOURCE_RECORD_CONTEXT"
            )

        context_ids = [str(row["source_event_id"]) for row in context]
        context_extensions = [
            event_id for event_id in context_ids if event_id not in declared_ids
        ]
        intervening = context_extensions if compound_id == "GDT585-C019" else []
        context_bundle_ids: list[str] = []
        context_record_ids: list[str] = []
        for row in context:
            if row["bundle_id"] not in context_bundle_ids:
                context_bundle_ids.append(str(row["bundle_id"]))
            if row["record_id"] not in context_record_ids:
                context_record_ids.append(str(row["record_id"]))
        group_injections: list[dict[str, Any]] = []
        for event_id in source_order_ids:
            group_injections.extend(
                sorted(
                    injections_by_event[event_id],
                    key=lambda row: (int(row["name_slot_in_label"]), row["slot_id"]),
                )
            )
        grammar_source_order = " ".join(
            str(local_by_event[event_id]["gdt586_primary_reader_de"])
            for event_id in source_order_ids
        )
        full_primary = " ".join(
            f"[{row['source_event_id']} / {row['record_id']} / {row['locus']}] "
            f"{row['gdt586_primary_reader_de']}"
            for row in context
        )
        full_legacy = " ".join(
            f"[{row['source_event_id']} / {row['record_id']} / {row['locus']}] "
            f"{row['legacy_reader_de'] if int(row['name_override_count']) else row['gdt586_primary_reader_de']}"
            for row in context
        )
        output.append(
            {
                "context_ordinal": len(output) + 1,
                "compound_id": compound_id,
                "case_scope": source["case_scope"],
                "source_kind": source["source_kind"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "locus": source["locus"],
                "declared_event_ids": source["source_event_ids"],
                "source_order_event_ids": pipe(source_order_ids),
                "source_order_status": (
                    "GDT585_VISUAL_ORDER_DIFFERS__SOURCE_ORDER_RESTORED"
                    if declared_ids != source_order_ids
                    else "GDT585_ORDER_MATCHES_SOURCE_ORDER"
                ),
                "local_card_host_keys": pipe(
                    str(local_by_event[event_id]["local_card_host_key"])
                    for event_id in source_order_ids
                ),
                "source_bundle_ids": pipe(bundle_ids),
                "source_record_ids": pipe(record_ids),
                "context_bundle_ids": pipe(context_bundle_ids),
                "context_record_ids": pipe(context_record_ids),
                "context_scope": context_scope,
                "context_card_count": len(context),
                "context_event_ids": pipe(context_ids),
                "context_extension_event_ids": pipe(context_extensions),
                "intervening_event_ids": pipe(intervening),
                "running_statement_ids": "NONE",
                "running_statement_link_status": (
                    "NONE__ALL_GROUP_EVENTS_ARE_LOCAL_CARDS__NO_SENTENCE_INHERITANCE"
                ),
                "source_order_grammar_primary_de": grammar_source_order,
                "gdt585_declared_grammar_primary_de": source["grammar_primary_reading_de"],
                "record_context_primary_de": full_primary,
                "record_context_legacy_de": full_legacy,
                "gdt585_primary_default_sequence": pipe(
                    row["gdt585_primary_default_de"] for row in group_injections
                ),
                "gdt582_exact_legacy_default_sequence": pipe(
                    row["gdt582_exact_legacy_default_de"] for row in group_injections
                ),
                "strongest_current_rival_de": source["strongest_rival_de"],
                "visual_or_composition_hypothesis_de": source["composition_hypothesis_de"],
                "context_effect": effect,
                "gdt586_disposition": disposition,
                "gdt586_best_working_reading_de": best_reading,
                "context_extension_limit": context_limit,
                "guard": (
                    "SOURCE_ORDER_GRAMMAR__VISUAL_COMPOSITION__EXACT_GDT582_RIVAL_SEPARATE__"
                    "NO_RUNNING_STATEMENT_INVENTED"
                ),
            }
        )
    return output


def build_page_profiles(
    statement_rows: list[dict[str, Any]], local_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    page_order: list[str] = []
    for row in [*statement_rows, *local_rows]:
        page = str(row["physical_page"])
        if page not in page_order:
            page_order.append(page)
    output: list[dict[str, Any]] = []
    for page in page_order:
        statements = [row for row in statement_rows if row["physical_page"] == page]
        local = [row for row in local_rows if row["physical_page"] == page]
        output.append(
            {
                "page_ordinal": len(output) + 1,
                "physical_page": page,
                "running_statement_count": len(statements),
                "polished_statement_count": sum(
                    row["base_reader_source"] == "GDT584_POLISHED_STATEMENT"
                    for row in statements
                ),
                "local_card_count": len(local),
                "polished_local_card_count": sum(
                    row["base_reader_source"] == "GDT584_POLISHED_LOCAL_CARD"
                    for row in local
                ),
                "running_name_override_slot_count": sum(
                    int(row["name_override_count"]) for row in statements
                ),
                "local_name_override_slot_count": sum(
                    int(row["name_override_count"]) for row in local
                ),
                "name_bearing_reader_unit_count": sum(
                    int(row["name_override_count"]) > 0 for row in [*statements, *local]
                ),
                "guard": (
                    "DISPLAY_GROUPING_BY_PHYSICAL_PAGE_ONLY__NO_LOCAL_TO_RUNNING_ATTACHMENT"
                ),
            }
        )
    return output


def build_reader_book(
    statement_rows: list[dict[str, Any]],
    local_rows: list[dict[str, Any]],
    page_rows: list[dict[str, Any]],
) -> str:
    statements_by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    local_by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    for row in local_rows:
        local_by_page[str(row["physical_page"])].append(row)
    lines = [
        "# GDT586 — Vollständiger Dreißig-Seiten-Leser mit Namensschicht",
        "",
        "Explorative Arbeitslesung, kein entzifferter Klartext.",
        "",
        "Die Ausgabe enthält zwei bewusst getrennte Schichten: 793 laufende Aussagen "
        "und 744 lokale Karten. Von den 109 GDT585-Werten gehören 107 auf 89 lokale "
        "Karten; nur Beschwerde und Heilmittel liegen in zwei laufenden Aussagen. "
        "Die Seitengruppierung unten ist keine künstliche Satzverknüpfung.",
        "",
        "Für jede geänderte Einheit bleibt die vollständige ältere GDT582/GDT584-Lesung "
        "im TSV als Rivalenkanal erhalten.",
    ]
    for profile in page_rows:
        page = str(profile["physical_page"])
        lines.extend(["", f"## {page}", "", "### Laufende Aussagen", ""])
        for row in statements_by_page.get(page, []):
            lines.extend(
                [
                    f"#### {row['statement_id']}",
                    "",
                    f"Oberflächen: `{row['surface_sequence']}`",
                    "",
                    str(row["gdt586_primary_reader_de"]),
                ]
            )
            if int(row["name_override_count"]):
                lines.extend(["", f"Namenslayer: {row['exact_name_override_trace_de']}"])
        lines.extend(["", "### Lokale Karten", ""])
        for row in local_by_page.get(page, []):
            lines.extend(
                [
                    f"#### {row['source_event_id']} — {row['locus']}",
                    "",
                    f"Oberfläche: `{row['surface']}`",
                    "",
                    str(row["gdt586_primary_reader_de"]),
                ]
            )
            if int(row["name_override_count"]):
                lines.extend(["", f"Namenslayer: {row['exact_name_override_trace_de']}"])
    return "\n".join(lines).rstrip() + "\n"


def build_manual_audit(
    group_rows: list[dict[str, Any]], injections: list[dict[str, Any]]
) -> str:
    restored = sum(
        row["legacy_alias_reconciliation"]
        == "RESTORED_EXACT_GDT582_VALUE_WHERE_GDT585_DECLARED_NONE"
        for row in injections
    )
    lines = [
        "# GDT586 — manueller Kontextaudit",
        "",
        "## Architekturkorrektur",
        "",
        "Die 109 Werte lassen sich nicht wörtlich in 793 Lauftextaussagen einsetzen. "
        "107 Namensspannen gehören zu 89 lokalen Karten und besitzen keine exakte "
        "Satzkante; zwei `LOCAL_X`-Werte gehören zu G515-S046 und G515-S050. Der "
        "Gesamtleser führt deshalb 793 Aussagen und 744 lokale Karten getrennt.",
        "",
        "## Wiederhergestellter Rivalenkanal",
        "",
        f"Bei {restored} Sternslots stand im GDT585-Assignment als alter Alias `NONE`. "
        "GDT586 holt den tatsächlichen alten Primärwert occurrence-genau aus dem "
        "GDT582-15.889-Slot-Ledger zurück. Dadurch bleiben Werte wie "
        "`Sternringstelle 35` und `Sternringstelle 39` wieder sichtbar.",
        "",
        "## Die 19 Gruppen nach vollständigem exaktem Kontext",
        "",
        "| Gruppe | Kontexteffekt | Disposition | beste aktuelle Lesung |",
        "|---|---|---|---|",
    ]
    for row in group_rows:
        reading = str(row["gdt586_best_working_reading_de"]).replace("|", "/")
        lines.append(
            f"| {row['compound_id']} | {row['context_effect']} | "
            f"{row['gdt586_disposition']} | {reading} |"
        )
    lines.extend(
        [
            "",
            "## Zwei konkrete Reparaturen",
            "",
            "- C001: Quellreihenfolge ist rechte Blütenform mit OT-Vermerk, dann linke "
            "Blütenform. Die umgekehrte Links-rechts-Folge bleibt ausschließlich Bildspur.",
            "- C019: DCHOS und YOR liegen in getrennten Records und Ownern; dazwischen "
            "steht OKAIN als eigener Record. Die Verbindung bleibt `VISUAL_PAIR_ONLY`.",
            "",
            "C007 und C010 sind die einzigen Gruppen, deren exakter Recordkontext über "
            "die bisherige Gruppe hinausgeht. Alle anderen Fälle enden am Singleton- oder "
            "Zweikartenrecord; zusätzlicher Lauftextkontext wurde nicht erfunden.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    expected = {
        "complete_defaults": 15889,
        "statements_582": 793,
        "local_cards_582": 744,
        "statements_584": 591,
        "local_cards_584": 158,
        "assignments_585": 109,
        "labels_585": 89,
        "groups_585": 19,
    }
    observed = {name: len(rows) for name, rows in data.items()}
    if observed != expected:
        raise RuntimeError(f"Input count drift: {observed}")
    if any(
        row.get("physical_page", "").lower().startswith("f84")
        for rows in data.values()
        for row in rows
    ):
        raise RuntimeError("Forbidden f84/f84r material reached GDT586")

    complete_by_slot = {row["slot_id"]: row for row in data["complete_defaults"]}
    if len(complete_by_slot) != 15889:
        raise RuntimeError("Complete slot IDs are not unique")
    local_by_event = {
        row["source_event_id"]: row for row in data["local_cards_582"]
    }
    polished_statement_ids = {
        row["statement_id"] for row in data["statements_584"]
    }
    statement_base_source = {
        row["statement_id"]: (
            "GDT584_POLISHED_STATEMENT"
            if row["statement_id"] in polished_statement_ids
            else "GDT582_CONCRETE_STATEMENT"
        )
        for row in data["statements_582"]
    }
    polished_local_ids = {
        row["source_event_id"] for row in data["local_cards_584"]
    }
    local_base_source = {
        row["source_event_id"]: (
            "GDT584_POLISHED_LOCAL_CARD"
            if row["source_event_id"] in polished_local_ids
            else "GDT582_CONCRETE_LOCAL_CARD"
        )
        for row in data["local_cards_582"]
    }

    injections = build_injections(
        data["assignments_585"],
        complete_by_slot,
        local_by_event,
        statement_base_source,
        local_base_source,
    )
    statements = build_statement_rows(
        data["statements_582"], data["statements_584"], injections
    )
    local = build_local_rows(
        data["local_cards_582"],
        data["local_cards_584"],
        data["labels_585"],
        injections,
    )
    groups = build_group_rows(data["groups_585"], local, injections)
    pages = build_page_profiles(statements, local)

    statement_layer_counts = Counter(row["base_reader_source"] for row in statements)
    local_base_layer_counts = Counter(row["base_reader_source"] for row in local)
    local_primary_layer_counts = Counter(row["primary_reader_source"] for row in local)
    source_kind_counts = Counter(row["source_kind"] for row in injections)
    restored_star_rivals = sum(
        row["legacy_alias_reconciliation"]
        == "RESTORED_EXACT_GDT582_VALUE_WHERE_GDT585_DECLARED_NONE"
        for row in injections
    )
    result = {
        "experiment_id": "GDT586",
        "status": STATUS,
        "complete_reader_units": len(statements) + len(local),
        "running_statements": len(statements),
        "local_cards": len(local),
        "pages": len(pages),
        "exact_name_overrides": len(injections),
        "local_name_overrides": source_kind_counts["GDT581_NAME_SPAN"],
        "running_local_x_overrides": source_kind_counts["GDT582_OWNER_BOUND_LOCAL_X"],
        "name_bearing_local_cards": sum(int(row["name_override_count"]) > 0 for row in local),
        "changed_running_statements": sum(int(row["name_override_count"]) > 0 for row in statements),
        "statement_base_layers": dict(sorted(statement_layer_counts.items())),
        "local_base_layers": dict(sorted(local_base_layer_counts.items())),
        "local_primary_layers": dict(sorted(local_primary_layer_counts.items())),
        "name_cards_by_base_layer": dict(
            sorted(
                Counter(
                    row["base_reader_source"]
                    for row in local
                    if int(row["name_override_count"])
                ).items()
            )
        ),
        "restored_exact_star_legacy_values": restored_star_rivals,
        "context_rereadings": len(groups),
        "group_name_slots": sum(
            len(row["gdt585_primary_default_sequence"].split("|")) for row in groups
        ),
        "source_order_repairs": sum(
            row["source_order_status"]
            == "GDT585_VISUAL_ORDER_DIFFERS__SOURCE_ORDER_RESTORED"
            for row in groups
        ),
        "visual_only_groups": sum(
            row["gdt586_disposition"] == "VISUAL_PAIR_ONLY__TEXTUAL_COMPOUND_REJECTED"
            for row in groups
        ),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt586_109_exact_name_injections.tsv", injections)
    write_tsv(OUT / "gdt586_793_complete_statement_reader.tsv", statements)
    write_tsv(OUT / "gdt586_744_complete_local_card_reader.tsv", local)
    write_tsv(OUT / "gdt586_19_full_context_group_readings.tsv", groups)
    write_tsv(OUT / "gdt586_30_page_reader_profiles.tsv", pages)
    (OUT / "GDT586_COMPLETE_THIRTY_PAGE_READER.md").write_text(
        build_reader_book(statements, local, pages), encoding="utf-8"
    )
    (OUT / "GDT586_MANUAL_CONTEXT_AUDIT.md").write_text(
        build_manual_audit(groups, injections), encoding="utf-8"
    )
    (OUT / "gdt586_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
