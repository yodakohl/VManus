#!/usr/bin/env python3
"""Leave-one-page replay for the Pass1023 Biological/Celestial subset."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTDIR = Path(__file__).resolve().parent
VCLI = ROOT / "vmanus-exp"

BIO_PAGES = ("f75r", "f76r", "f77r", "f81v", "f82r", "f83r")
CELESTIAL_PAGES = ("f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r")
PAGES = BIO_PAGES + CELESTIAL_PAGES
PAGE_RANK = {page: index for index, page in enumerate(PAGES)}
PANEL = {page: "BIOLOGICAL" for page in BIO_PAGES} | {page: "CELESTIAL" for page in CELESTIAL_PAGES}

PASS1023 = ROOT / "experiments/yolo/sidequest_semantic_scope_ambiguity_resolution_one_thousand_twenty_third"
PASS1022 = ROOT / "experiments/yolo/sidequest_semantic_argument_scope_stack_one_thousand_twenty_second"
PASS1006 = ROOT / "experiments/yolo/sidequest_semantic_eighteen_page_unified_workshop_edition_one_thousand_sixth"

ATTACHMENT_SOURCE = PASS1023 / "PASS1023_4345_SCOPE_ATTACHMENTS.tsv"
STATEMENT_SOURCE = PASS1023 / "PASS1023_627_STATEMENT_SCOPE_EDITION.tsv"
EVENT_SOURCE = PASS1022 / "PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv"
LABEL_SOURCE = PASS1006 / "PASS1006_550_LOCAL_ADDRESS_LEDGER.tsv"

FULL_OUT = OUTDIR / "BIO_CELESTIAL_REPLAY_FULL.tsv"
PAGE_OUT = OUTDIR / "BIO_CELESTIAL_REPLAY_PAGE_SUMMARY.tsv"
RULE_OUT = OUTDIR / "BIO_CELESTIAL_REPLAY_RULE_SUPPORT.tsv"
SUMMARY_OUT = OUTDIR / "BIO_CELESTIAL_REPLAY_SUMMARY.json"

ATTACHMENT_COLUMNS = [
    "attachment_id", "focus_core", "focus_value_de", "focus_family", "event_id",
    "book_event_ordinal", "physical_page", "register", "statement_id",
    "card_ordinal_in_statement", "locus", "owner_de", "surface_card",
    "component_recipe", "focus_atom_ordinal", "chosen_attachment_class",
    "chosen_action", "chosen_action_value_de", "chosen_action_event_id",
    "chosen_action_card_ordinal", "bracket_reading_de", "duplicate_scope_mode",
    "pass1023_resolution_status", "pass1023_ambiguity_classes", "pass1023_decisions",
    "pass1023_selected_attachment_de", "pass1023_scope_de", "pass1023_rule_ids",
    "pass1023_changed_from_pass1022", "pass1023_note_de",
]

STATEMENT_COLUMNS = [
    "book_statement_ordinal", "statement_id", "physical_page", "register", "owner_de",
    "event_count", "predicate_realization", "seed_action_de",
    "inheritance_source_statement_id", "action_chain_de", "arguments_de", "relations_de",
    "grades_de", "end_mode", "binding_origins", "scope_skeleton_de", "scope_result",
    "focus_attachment_count", "pass1022_open_attachment_count",
    "pass1023_resolved_attachment_count", "pass1023_changed_attachment_count",
    "pass1023_resolution_classes", "pass1023_decision_trace_de", "pass1023_scope_result",
]

EVENT_COLUMNS = [
    "running_event_ordinal", "event_id", "statement_id", "physical_page", "register",
    "owner_de", "locus", "surface", "component_recipe", "action_heads_de",
    "active_head_before_de", "arguments_de", "relations_de", "grades_de", "sequence_de",
    "local_channels_de", "binding_trace_de", "active_head_after_de", "closes_gang",
    "duplicate_rule", "scope_status",
]

LABEL_COLUMNS = [
    "book_event_ordinal", "event_id", "physical_page", "register", "locus", "kind",
    "surface", "component_recipe", "portable_default_de", "local_contextual_expansion_de",
    "event_role", "statement_id", "source_release",
]

RULE_FAMILIES = {
    "PASS1022_CLEAR_ATTACHMENT": ("BASE_LOCAL_ATTACHMENT",),
    "CLOSE_OPEN_HEAD_BEFORE_NEXT_HEAD": ("NEAREST_HEAD_LEFT_ON_TIE",),
    "OT_SIBLING_FORWARD": ("ONE_CARD_BOUNDED_FORWARD",),
    "OPENING_ARGUMENT_FORWARD": ("ONE_CARD_BOUNDED_FORWARD",),
    "OPENING_ARGUMENT_TO_NEXT_Q_PACKET": ("ONE_CARD_BOUNDED_FORWARD",),
    "GRADE_TO_NEXT_COMPATIBLE_HEAD": ("ONE_CARD_BOUNDED_FORWARD",),
    "Q_PACKET_FORWARD": ("ONE_CARD_BOUNDED_FORWARD",),
    "L_OR_AIR_RIGHT_FRAME": ("RIGHT_RELATION_FRAME",),
    "FORWARD_RELATION_FRAME": ("RIGHT_RELATION_FRAME",),
    "AR_AL_DEFAULT_OWNER": ("OWNER_ADDRESS_FALLBACK",),
    "R1_HEAD_WITH_LOCAL_RIGHT": ("R_POSITIONAL_HEAD",),
    "R1_HEAD_STANDALONE": ("R_POSITIONAL_HEAD",),
    "R1_HEAD_IN_RIGHT_FRAME": ("RIGHT_RELATION_FRAME", "R_POSITIONAL_HEAD"),
    "R3_TAIL_AFTER_ACTION": ("R_POSITIONAL_TAIL",),
    "R4_TAIL_BEFORE_OL": ("R_POSITIONAL_TAIL",),
    "LABEL_ONLY_OWNER_ADDRESS_GATE": ("OWNER_ADDRESS_ONLY_GATE",),
}

BOUNDARY_FAMILY = {
    "LICENSED_DY_CLOSE": "LICENSED_CLOSE",
    "NONPROSE_OWNER_OR_DIAGRAM_BOUNDARY": "VISIBLE_OWNER_OR_PROSEBLOCK_RESET",
    "VISIBLE_PARAGRAPH_BOUNDARY": "VISIBLE_OWNER_OR_PROSEBLOCK_RESET",
    "VISIBLE_RING_OR_OWNER_BOUNDARY": "VISIBLE_OWNER_OR_PROSEBLOCK_RESET",
    "RING_NAMESPACE_RESET_A_TO_B": "VISIBLE_OWNER_OR_PROSEBLOCK_RESET",
    "RING_NAMESPACE_RESET_B_TO_C": "VISIBLE_OWNER_OR_PROSEBLOCK_RESET",
    "OWNER_RESET_TO_LOWER_STATION_LABELS": "VISIBLE_OWNER_OR_PROSEBLOCK_RESET",
    "PAGE_END_OPEN": "TRUE_OPEN_END",
    "TRUE_OPEN_FINAL_RING": "TRUE_OPEN_END",
}

FULL_FIELDS = [
    "replay_row_id", "row_kind", "panel", "physical_page", "source_id", "statement_id",
    "event_id", "locus", "owner_de", "surface_card", "component_recipe", "focus_core",
    "focus_value_de", "pass1023_resolution_status", "pass1023_decision",
    "pass1023_selected_attachment_de", "pass1023_changed_from_pass1022",
    "exact_rule_signature", "normalized_rule_families", "exact_other_pages",
    "family_support_same_panel_pages", "family_support_other_panel_pages",
    "family_support_any_other_pages", "leave_one_page_support",
    "owner_address_load", "scope_reading_de", "new_rule_required",
]

PAGE_FIELDS = [
    "physical_page", "panel", "page_mode", "running_event_count", "statement_count",
    "scope_attachment_count", "resolved_attachment_count", "changed_attachment_count",
    "label_address_count", "label_locus_count", "label_rows_with_address_core",
    "label_rows_with_action_core", "running_owner_count", "top_owner_de",
    "top_owner_attachment_count", "owner_bound_attachment_count", "owner_bound_rate",
    "hier_event_count", "variante_event_count", "klasse_event_count",
    "vorbezug_event_count", "q_push_count", "ot_switch_count", "ol_continue_count",
    "os_restore_count", "dy_close_count", "carried_scope_event_count",
    "multihead_card_count", "max_heads_on_card", "max_statement_event_count",
    "end_modes", "attachment_rule_families", "stack_rule_families",
    "page_private_exact_attachment_signatures", "page_private_exact_end_modes",
    "same_panel_missing_families", "global_missing_families", "local_owner_load_de",
    "replay_verdict",
]

RULE_FIELDS = [
    "rule_inventory_id", "source_layer", "exact_signature", "normalized_families",
    "occurrence_count", "pages", "page_count", "panels", "other_page_exists",
    "exact_support_status", "family_support_pages", "new_rule_family_required", "note_de",
]


def query(path: Path, pages: tuple[str, ...], columns: list[str]) -> tuple[list[dict[str, str]], str, str]:
    command = [str(VCLI), "query-tsv", str(path), "--selector", "physical_page"]
    for page in pages:
        command.extend(("--allow", page))
    command.extend(("--forbid-prefix", "f84", "--columns", ",".join(columns)))
    result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    return rows, hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(), result.stderr.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_rules(signature: str) -> tuple[str, ...]:
    rules = tuple(signature.split("+"))
    assert all(rule in RULE_FAMILIES for rule in rules), signature
    return rules


def families(signature: str) -> tuple[str, ...]:
    found = {family for rule in exact_rules(signature) for family in RULE_FAMILIES[rule]}
    return tuple(sorted(found))


def joined(values) -> str:
    values = sorted(set(values), key=lambda value: (PAGE_RANK.get(value, 999), value))
    return "|".join(values) if values else "NONE"


def other_support(page: str, required: tuple[str, ...], family_pages: dict[str, set[str]]) -> tuple[set[str], set[str], set[str]]:
    candidates = set(PAGES) - {page}
    for family in required:
        candidates &= family_pages[family]
    same = {candidate for candidate in candidates if PANEL[candidate] == PANEL[page]}
    cross = candidates - same
    return same, cross, candidates


def stack_presence(events: list[dict[str, str]], statements: list[dict[str, str]]) -> dict[str, set[str]]:
    result = {page: set() for page in PAGES}
    for row in events:
        page = row["physical_page"]
        tokens = set(row["component_recipe"].split("+"))
        if "CARRIER_Q" in tokens:
            result[page].add("Q_PUSH")
        if "OT" in tokens:
            result[page].add("OT_SWITCH")
        if "OL" in tokens:
            result[page].add("OL_CONTINUE")
        if "OS" in tokens or "VORBEZUG" in row["local_channels_de"]:
            result[page].add("OWNER_RESTORE")
        if row["closes_gang"] == "YES":
            result[page].add("DY_CLOSE_AFTER_CARD")
        if row["scope_status"] == "CARRIED_SCOPE":
            result[page].add("RUNNING_HEAD_CARRY")
        if row["action_heads_de"] != "NONE" and len(row["action_heads_de"].split("+")) > 1:
            result[page].add("MULTIHEAD_NEST")
    for row in statements:
        result[row["physical_page"]].add(BOUNDARY_FAMILY[row["end_mode"]])
    result["f69v"].add("OWNER_ADDRESS_ONLY_GATE")
    result["f70v"].add("OWNER_ADDRESS_ONLY_GATE")
    return result


def main() -> None:
    attachments, attachment_hash, attachment_guard = query(ATTACHMENT_SOURCE, PAGES, ATTACHMENT_COLUMNS)
    statements, statement_hash, statement_guard = query(STATEMENT_SOURCE, PAGES, STATEMENT_COLUMNS)
    events, event_hash, event_guard = query(EVENT_SOURCE, PAGES, EVENT_COLUMNS)
    labels, label_hash, label_guard = query(LABEL_SOURCE, ("f69v", "f70v"), LABEL_COLUMNS)

    assert len(attachments) == 3096
    assert len(statements) == 559
    assert len(events) == 2684
    assert len(labels) == 358
    assert {row["physical_page"] for row in attachments} <= set(PAGES)
    assert {row["physical_page"] for row in statements} <= set(PAGES)
    assert {row["physical_page"] for row in events} <= set(PAGES)
    assert {row["physical_page"] for row in labels} == {"f69v", "f70v"}
    assert all(row["event_role"] == "LOCAL_ADDRESS_OR_LABEL" for row in labels)

    signature_pages: dict[str, set[str]] = defaultdict(set)
    signature_counts: Counter[str] = Counter()
    atomic_pages: dict[str, set[str]] = defaultdict(set)
    atomic_counts: Counter[str] = Counter()
    family_pages: dict[str, set[str]] = defaultdict(set)
    for row in attachments:
        signature = row["pass1023_rule_ids"]
        page = row["physical_page"]
        signature_pages[signature].add(page)
        signature_counts[signature] += 1
        for rule in exact_rules(signature):
            atomic_pages[rule].add(page)
            atomic_counts[rule] += 1
        for family in families(signature):
            family_pages[family].add(page)
    signature_pages["LABEL_ONLY_OWNER_ADDRESS_GATE"] = {"f69v", "f70v"}
    signature_counts["LABEL_ONLY_OWNER_ADDRESS_GATE"] = len(labels)
    atomic_pages["LABEL_ONLY_OWNER_ADDRESS_GATE"] = {"f69v", "f70v"}
    atomic_counts["LABEL_ONLY_OWNER_ADDRESS_GATE"] = len(labels)
    family_pages["OWNER_ADDRESS_ONLY_GATE"] = {"f69v", "f70v"}

    page_events = {page: [row for row in events if row["physical_page"] == page] for page in PAGES}
    page_statements = {page: [row for row in statements if row["physical_page"] == page] for page in PAGES}
    page_attachments = {page: [row for row in attachments if row["physical_page"] == page] for page in PAGES}
    page_labels = {page: [row for row in labels if row["physical_page"] == page] for page in PAGES}

    stack_by_page = stack_presence(events, statements)
    stack_family_pages: dict[str, set[str]] = defaultdict(set)
    for page, page_families in stack_by_page.items():
        for family in page_families:
            stack_family_pages[family].add(page)
    stack_family_counts: Counter[str] = Counter()
    for row in events:
        tokens = set(row["component_recipe"].split("+"))
        if "CARRIER_Q" in tokens:
            stack_family_counts["Q_PUSH"] += 1
        if "OT" in tokens:
            stack_family_counts["OT_SWITCH"] += 1
        if "OL" in tokens:
            stack_family_counts["OL_CONTINUE"] += 1
        if "OS" in tokens or "VORBEZUG" in row["local_channels_de"]:
            stack_family_counts["OWNER_RESTORE"] += 1
        if row["closes_gang"] == "YES":
            stack_family_counts["DY_CLOSE_AFTER_CARD"] += 1
        if row["scope_status"] == "CARRIED_SCOPE":
            stack_family_counts["RUNNING_HEAD_CARRY"] += 1
        if row["action_heads_de"] != "NONE" and len(row["action_heads_de"].split("+")) > 1:
            stack_family_counts["MULTIHEAD_NEST"] += 1
    for row in statements:
        stack_family_counts[BOUNDARY_FAMILY[row["end_mode"]]] += 1
    stack_family_counts["OWNER_ADDRESS_ONLY_GATE"] = len(labels)

    boundary_mode_pages: dict[str, set[str]] = defaultdict(set)
    boundary_mode_counts: Counter[str] = Counter()
    boundary_family_pages: dict[str, set[str]] = defaultdict(set)
    for row in statements:
        mode = row["end_mode"]
        page = row["physical_page"]
        boundary_mode_pages[mode].add(page)
        boundary_mode_counts[mode] += 1
        boundary_family_pages[BOUNDARY_FAMILY[mode]].add(page)

    full_rows: list[dict[str, str]] = []
    for row in attachments:
        page = row["physical_page"]
        signature = row["pass1023_rule_ids"]
        normalized = families(signature)
        same, cross, any_other = other_support(page, normalized, family_pages)
        exact_other = signature_pages[signature] - {page}
        if same:
            support = "SUPPORTED_OTHER_SAME_PANEL_PAGE"
        elif any_other:
            support = "SUPPORTED_OTHER_PANEL_PAGE"
        else:
            support = "PAGE_PRIVATE_RULE_REQUIRED"
        full_rows.append({
            "replay_row_id": "",
            "row_kind": "RUNNING_SCOPE_ATTACHMENT",
            "panel": PANEL[page],
            "physical_page": page,
            "source_id": row["attachment_id"],
            "statement_id": row["statement_id"],
            "event_id": row["event_id"],
            "locus": row["locus"],
            "owner_de": row["owner_de"],
            "surface_card": row["surface_card"],
            "component_recipe": row["component_recipe"],
            "focus_core": row["focus_core"],
            "focus_value_de": row["focus_value_de"],
            "pass1023_resolution_status": row["pass1023_resolution_status"],
            "pass1023_decision": row["pass1023_decisions"],
            "pass1023_selected_attachment_de": row["pass1023_selected_attachment_de"],
            "pass1023_changed_from_pass1022": row["pass1023_changed_from_pass1022"],
            "exact_rule_signature": signature,
            "normalized_rule_families": joined(normalized),
            "exact_other_pages": joined(exact_other),
            "family_support_same_panel_pages": joined(same),
            "family_support_other_panel_pages": joined(cross),
            "family_support_any_other_pages": joined(any_other),
            "leave_one_page_support": support,
            "owner_address_load": "OWNER_BOUND" if row["pass1023_selected_attachment_de"].startswith("BESITZER=") else "ACTION_OR_PACKAGE_BOUND",
            "scope_reading_de": row["pass1023_scope_de"],
            "new_rule_required": "YES" if support == "PAGE_PRIVATE_RULE_REQUIRED" else "NO",
        })

    for row in labels:
        page = row["physical_page"]
        normalized = ("OWNER_ADDRESS_ONLY_GATE",)
        same, cross, any_other = other_support(page, normalized, family_pages)
        full_rows.append({
            "replay_row_id": "",
            "row_kind": "LABEL_OWNER_ADDRESS_GATE",
            "panel": "CELESTIAL",
            "physical_page": page,
            "source_id": row["event_id"],
            "statement_id": "NONE",
            "event_id": row["event_id"],
            "locus": row["locus"],
            "owner_de": "LOCAL_CELESTIAL_REGISTER",
            "surface_card": row["surface"],
            "component_recipe": row["component_recipe"],
            "focus_core": "NONE",
            "focus_value_de": "NONE",
            "pass1023_resolution_status": "NOT_IN_RUNNING_PASS1023",
            "pass1023_decision": "OWNER_ADDRESS_ONLY",
            "pass1023_selected_attachment_de": "LOKALER_BESITZER_ODER_ADRESSE",
            "pass1023_changed_from_pass1022": "NOT_APPLICABLE",
            "exact_rule_signature": "LABEL_ONLY_OWNER_ADDRESS_GATE",
            "normalized_rule_families": "OWNER_ADDRESS_ONLY_GATE",
            "exact_other_pages": joined({"f69v", "f70v"} - {page}),
            "family_support_same_panel_pages": joined(same),
            "family_support_other_panel_pages": joined(cross),
            "family_support_any_other_pages": joined(any_other),
            "leave_one_page_support": "SUPPORTED_OTHER_SAME_PANEL_PAGE",
            "owner_address_load": "LABEL_OR_ADDRESS_ONLY",
            "scope_reading_de": "OWNER/ADDRESS_ONLY; KEIN PROSE- ODER HANDLUNGSSTACK",
            "new_rule_required": "NO",
        })

    def full_sort(row: dict[str, str]):
        ordinal = row["event_id"]
        return PAGE_RANK[row["physical_page"]], row["row_kind"], ordinal, row["source_id"]

    full_rows.sort(key=full_sort)
    for index, row in enumerate(full_rows, start=1):
        row["replay_row_id"] = f"BCREPLAY-{index:04d}"
    with FULL_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=FULL_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(full_rows)

    page_rows: list[dict[str, str]] = []
    for page in PAGES:
        att = page_attachments[page]
        evt = page_events[page]
        stm = page_statements[page]
        lab = page_labels[page]
        owners = Counter(row["owner_de"] for row in att)
        top_owner, top_owner_count = owners.most_common(1)[0] if owners else ("NONE", 0)
        attachment_families = {family for row in att for family in families(row["pass1023_rule_ids"])}
        if lab:
            attachment_families.add("OWNER_ADDRESS_ONLY_GATE")
        required_families = set(attachment_families) | set(stack_by_page[page])
        same_panel_missing = []
        global_missing = []
        for family in sorted(required_families):
            source_pages = family_pages.get(family, set()) | stack_family_pages.get(family, set()) | boundary_family_pages.get(family, set())
            other = source_pages - {page}
            if not other:
                global_missing.append(family)
            if not {candidate for candidate in other if PANEL[candidate] == PANEL[page]}:
                same_panel_missing.append(family)
        private_signatures = sorted(
            {row["pass1023_rule_ids"] for row in att if len(signature_pages[row["pass1023_rule_ids"]]) == 1}
        )
        private_end_modes = sorted({row["end_mode"] for row in stm if len(boundary_mode_pages[row["end_mode"]]) == 1})
        token_event_counts = Counter(
            token for token in ("CARRIER_Q", "OT", "OL", "OS")
            for row in evt if token in row["component_recipe"].split("+")
        )
        local_event_counts = Counter(
            token for token in ("HIER", "VARIANTE", "KLASSE", "VORBEZUG")
            for row in evt if token in row["local_channels_de"].split("+")
        )
        head_counts = [0 if row["action_heads_de"] == "NONE" else len(row["action_heads_de"].split("+")) for row in evt]
        owner_bound = sum(row["pass1023_selected_attachment_de"].startswith("BESITZER=") for row in att)
        address_cores = {"AR", "AL", "L", "AIR"}
        action_cores = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
        label_with_address = sum(bool(set(row["component_recipe"].split("+")) & address_cores) for row in lab)
        label_with_action = sum(bool(set(row["component_recipe"].split("+")) & action_cores) for row in lab)
        if lab:
            owner_load = f"{len(lab)} lokale Label-/Adressgruppen in {len({row['locus'] for row in lab})} Loci; {label_with_action} tragen handlungsaehnliche Kerne, aber keine wird als Prosehandlung geoeffnet."
            page_mode = "LABEL_ONLY_OWNER_ADDRESS"
        else:
            owner_load = f"{owner_bound}/{len(att)} Fokusanschluesse direkt am Besitzer; {len(owners)} dokumentierte laufende Besitzer."
            page_mode = "RUNNING_SCOPE"
        if global_missing:
            verdict = "FAIL_PAGE_PRIVATE_RULE_REQUIRED"
        elif same_panel_missing:
            verdict = "PASS_WITH_OTHER_PANEL_RULE_SUPPORT"
        elif lab:
            verdict = "PASS_OWNER_ADDRESS_ONLY_GATE"
        else:
            verdict = "PASS_WITHIN_PANEL_SHARED_RULES"
        end_modes = Counter(row["end_mode"] for row in stm)
        page_rows.append({
            "physical_page": page,
            "panel": PANEL[page],
            "page_mode": page_mode,
            "running_event_count": str(len(evt)),
            "statement_count": str(len(stm)),
            "scope_attachment_count": str(len(att)),
            "resolved_attachment_count": str(sum(row["pass1023_resolution_status"] == "RESOLVED_BY_WORKSHOP_RULE" for row in att)),
            "changed_attachment_count": str(sum(row["pass1023_changed_from_pass1022"] == "YES" for row in att)),
            "label_address_count": str(len(lab)),
            "label_locus_count": str(len({row["locus"] for row in lab})),
            "label_rows_with_address_core": str(label_with_address),
            "label_rows_with_action_core": str(label_with_action),
            "running_owner_count": str(len(owners)),
            "top_owner_de": top_owner,
            "top_owner_attachment_count": str(top_owner_count),
            "owner_bound_attachment_count": str(owner_bound),
            "owner_bound_rate": f"{owner_bound / len(att):.6f}" if att else "NOT_APPLICABLE",
            "hier_event_count": str(local_event_counts["HIER"]),
            "variante_event_count": str(local_event_counts["VARIANTE"]),
            "klasse_event_count": str(local_event_counts["KLASSE"]),
            "vorbezug_event_count": str(local_event_counts["VORBEZUG"]),
            "q_push_count": str(token_event_counts["CARRIER_Q"]),
            "ot_switch_count": str(token_event_counts["OT"]),
            "ol_continue_count": str(token_event_counts["OL"]),
            "os_restore_count": str(token_event_counts["OS"]),
            "dy_close_count": str(sum(row["closes_gang"] == "YES" for row in evt)),
            "carried_scope_event_count": str(sum(row["scope_status"] == "CARRIED_SCOPE" for row in evt)),
            "multihead_card_count": str(sum(count > 1 for count in head_counts)),
            "max_heads_on_card": str(max(head_counts, default=0)),
            "max_statement_event_count": str(max((int(row["event_count"]) for row in stm), default=0)),
            "end_modes": "+".join(f"{mode}:{count}" for mode, count in sorted(end_modes.items())) if end_modes else "NONE",
            "attachment_rule_families": joined(attachment_families),
            "stack_rule_families": joined(stack_by_page[page]),
            "page_private_exact_attachment_signatures": joined(private_signatures),
            "page_private_exact_end_modes": joined(private_end_modes),
            "same_panel_missing_families": joined(same_panel_missing),
            "global_missing_families": joined(global_missing),
            "local_owner_load_de": owner_load,
            "replay_verdict": verdict,
        })

    with PAGE_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=PAGE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(page_rows)

    rule_rows: list[dict[str, str]] = []

    def add_rule(source_layer: str, signature: str, normalized: tuple[str, ...], count: int, pages: set[str], note: str) -> None:
        support_pages = set(PAGES)
        for family in normalized:
            support_pages &= family_pages.get(family, set()) | stack_family_pages.get(family, set()) | boundary_family_pages.get(family, set())
        other_exists = len(pages) > 1
        family_other_exists = all((family_pages.get(family, set()) | stack_family_pages.get(family, set()) | boundary_family_pages.get(family, set())) - pages for family in normalized) if len(pages) == 1 else True
        if other_exists:
            status = "EXACT_SIGNATURE_SHARED"
        elif family_other_exists:
            status = "PAGE_PRIVATE_SIGNATURE_SHARED_RULE_FAMILY"
        else:
            status = "PAGE_PRIVATE_RULE_FAMILY"
        rule_rows.append({
            "rule_inventory_id": "",
            "source_layer": source_layer,
            "exact_signature": signature,
            "normalized_families": joined(normalized),
            "occurrence_count": str(count),
            "pages": joined(pages),
            "page_count": str(len(pages)),
            "panels": joined({PANEL[page] for page in pages}),
            "other_page_exists": "YES" if other_exists else "NO",
            "exact_support_status": status,
            "family_support_pages": joined(support_pages),
            "new_rule_family_required": "YES" if status == "PAGE_PRIVATE_RULE_FAMILY" else "NO",
            "note_de": note,
        })

    for signature in sorted(signature_pages):
        add_rule(
            "ATTACHMENT_EXACT_SIGNATURE" if signature != "LABEL_ONLY_OWNER_ADDRESS_GATE" else "LABEL_GATE",
            signature,
            families(signature),
            signature_counts[signature],
            signature_pages[signature],
            "Exakte Pass1023-Signatur; seitenprivate Form ist nur dann neu, wenn auch ihre normalisierte Familie privat bleibt.",
        )
    for rule in sorted(atomic_pages):
        add_rule(
            "ATTACHMENT_ATOMIC_RULE",
            rule,
            RULE_FAMILIES[rule],
            atomic_counts[rule],
            atomic_pages[rule],
            "Atomarer Pass1023-Regeltyp nach Aufspaltung kombinierter Signaturen.",
        )
    for family in sorted(stack_family_pages):
        add_rule(
            "STACK_FAMILY",
            family,
            (family,),
            stack_family_counts[family],
            stack_family_pages[family],
            "Normalisierte Stack-/Kontrollfamilie; Auftretenszahl zaehlt ihre ausloesenden Ereignisse, Statements oder Labelzeilen.",
        )
    for mode in sorted(boundary_mode_pages):
        add_rule(
            "BOUNDARY_EXACT_MODE",
            mode,
            (BOUNDARY_FAMILY[mode],),
            boundary_mode_counts[mode],
            boundary_mode_pages[mode],
            "Lokaler sichtbarer Endmodus; die Werkstattregel ist die normalisierte Abschluss-/Resetfamilie.",
        )

    rule_rows.sort(key=lambda row: (row["source_layer"], row["exact_signature"]))
    for index, row in enumerate(rule_rows, start=1):
        row["rule_inventory_id"] = f"BC-RULE-{index:03d}"
    with RULE_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=RULE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rule_rows)

    all_outputs = FULL_OUT.read_text(encoding="utf-8") + PAGE_OUT.read_text(encoding="utf-8") + RULE_OUT.read_text(encoding="utf-8")
    assert "f84" not in all_outputs.lower()
    assert len(full_rows) == 3454
    assert sum(row["pass1023_resolution_status"] == "RESOLVED_BY_WORKSHOP_RULE" for row in full_rows) == 270
    assert sum(row["pass1023_changed_from_pass1022"] == "YES" for row in full_rows) == 125
    assert not [row for row in full_rows if row["new_rule_required"] == "YES"]
    assert not [row for row in page_rows if row["global_missing_families"] != "NONE"]

    summary = {
        "result": "PASS_ALL_TWELVE_PAGES_REPLAY_WITH_OTHER_PAGE_RULE_SUPPORT",
        "scope": {"biological_pages": list(BIO_PAGES), "celestial_pages": list(CELESTIAL_PAGES)},
        "counts": {
            "pages": len(PAGES),
            "running_pages": sum(bool(page_events[page]) for page in PAGES),
            "label_only_pages": sum(bool(page_labels[page]) for page in PAGES),
            "running_events": len(events),
            "statements": len(statements),
            "scope_attachments": len(attachments),
            "resolved_attachments": sum(row["pass1023_resolution_status"] == "RESOLVED_BY_WORKSHOP_RULE" for row in attachments),
            "changed_attachments": sum(row["pass1023_changed_from_pass1022"] == "YES" for row in attachments),
            "label_address_rows": len(labels),
            "full_replay_rows": len(full_rows),
            "new_rule_required_rows": sum(row["new_rule_required"] == "YES" for row in full_rows),
            "page_private_exact_attachment_signatures": sum(len(pages) == 1 for pages in signature_pages.values()),
            "page_private_atomic_attachment_rules": sum(len(pages) == 1 for pages in atomic_pages.values()),
            "page_private_rule_families": sum(row["new_rule_family_required"] == "YES" for row in rule_rows),
        },
        "page_verdicts": {row["physical_page"]: row["replay_verdict"] for row in page_rows},
        "same_panel_exceptions": {
            row["physical_page"]: row["same_panel_missing_families"]
            for row in page_rows if row["same_panel_missing_families"] != "NONE"
        },
        "page_private_exact_attachment_signatures": {
            signature: joined(pages) for signature, pages in signature_pages.items() if len(pages) == 1
        },
        "guards": {
            "attachments": attachment_guard,
            "statements": statement_guard,
            "events": event_guard,
            "labels": label_guard,
        },
        "selected_input_hashes": {
            "attachments": attachment_hash,
            "statements": statement_hash,
            "events": event_hash,
            "labels": label_hash,
        },
        "output_hashes": {
            FULL_OUT.name: sha256(FULL_OUT),
            PAGE_OUT.name: sha256(PAGE_OUT),
            RULE_OUT.name: sha256(RULE_OUT),
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
