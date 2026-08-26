#!/usr/bin/env python3
"""Resolve GDT474 grammatical ties where GDT475 exposes a multi-locus record."""

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
BASE = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution"
OUT = BASE / "artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
BUNDLES = G474 / "gdt474_146_locus_bundle_meaning_triptych.tsv"
BOUNDARIES = G475 / "gdt475_146_bundle_boundary_roles.tsv"
RECORDS = G475 / "gdt475_135_page_microrecords.tsv"
CHAINS = G475 / "gdt475_8_cross_locus_continuation_chains.tsv"

DECISIONS_OUT = OUT / "gdt476_64_tie_context_decisions.tsv"
RECORD_READINGS_OUT = OUT / "gdt476_8_contextual_record_readings.tsv"
PAGE_SUMMARY_OUT = OUT / "gdt476_6_page_tie_summary.tsv"
READABLE_OUT = OUT / "GDT476_CONTEXTUAL_TIE_WORKING_EDITION.md"
RESULT_OUT = OUT / "gdt476_result.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def best_models(bundle: dict[str, str]) -> list[str]:
    return bundle["best_models"].split("|")


def is_tied(bundle: dict[str, str]) -> bool:
    return len(best_models(bundle)) > 1


def reading(bundle: dict[str, str], model: str) -> str:
    return bundle[f"{model.lower()}_bundle_reading_de"]


def repairs(bundle: dict[str, str], model: str) -> int:
    return int(bundle[f"{model.lower()}_repair_count"])


def record_head(
    record: dict[str, str],
    bundle_map: dict[str, dict[str, str]],
) -> tuple[str, str, str, str]:
    first = bundle_map[record["bundle_ids"].split("|")[0]]
    first_best = best_models(first)
    if first_best == ["INSTRUCTION"]:
        return "INSTRUCTION", first["bundle_id"], "UNIQUE_INSTRUCTION_HEAD", "DIRECT_HEAD_ANCHOR"
    if int(first["explicit_action_root_count"]) > 0 and "INSTRUCTION" in first_best:
        return "INSTRUCTION", first["bundle_id"], "VISIBLE_ACTION_HEAD", "ACTION_HEADED_WORKING_CHOICE"
    if first_best == ["COORDINATE"]:
        return "COORDINATE", first["bundle_id"], "UNIQUE_COORDINATE_HEAD", "DIRECT_HEAD_ANCHOR"
    if first["selected_model"] == "CATALOGUE" and int(first["learned_name_event_count"]) > 0:
        return "CATALOGUE", first["bundle_id"], "LEARNED_NAME_CATALOGUE_HEAD", "CATALOGUE_HEADED_WORKING_CHOICE"
    return first["selected_model"], first["bundle_id"], "GDT474_SELECTED_RECORD_HEAD", "SELECTED_HEAD_WORKING_CHOICE"


def contextual_selection(
    bundle: dict[str, str],
    boundary: dict[str, str],
    record: dict[str, str],
    head_model: str,
    head_id: str,
    head_evidence: str,
    strength: str,
) -> dict[str, object]:
    local_best = best_models(bundle)
    old_model = bundle["selected_model"]
    multi = int(record["bundle_count"]) > 1
    chosen = old_model
    source = "GDT474_LOCAL_DEFAULT_RETAINED"
    decided = "NO"
    credit = 0

    if multi:
        if head_model in local_best:
            chosen = head_model
            source = "RECORD_HEAD_SELECTS_LOCAL_TIE"
            decided = "YES"
        elif (
            head_model == "INSTRUCTION"
            and boundary["boundary_role"] == "EXPLICIT_CONTINUATION_OL"
            and repairs(bundle, "INSTRUCTION") == 1
        ):
            chosen = "INSTRUCTION"
            source = "INHERITED_ACTION_SUPPLIES_IMPLICIT_VERB"
            decided = "YES"
            credit = 1
        else:
            source = "RECORD_CONTEXT_INSUFFICIENT__LOCAL_DEFAULT_RETAINED"

    if decided == "YES":
        context_class = {
            "INSTRUCTION": "SAME_WORKING_OPERATION",
            "COORDINATE": "SAME_ADDRESS_TRACE",
            "CATALOGUE": "SAME_CATALOGUE_ENTRY",
        }[chosen]
    else:
        context_class = "LOCAL_DEFAULT_WITHOUT_RECORD_CUE"

    chosen_reading = reading(bundle, chosen)
    line_reading = chosen_reading
    if decided == "NO":
        line = f"Lokaler Default — {chosen_reading}"
    elif chosen == "INSTRUCTION":
        prefix = "Arbeitskopf" if bundle["bundle_id"] == head_id else "Im selben Arbeitsgang"
        line = f"{prefix} — {chosen_reading}"
    elif chosen == "COORDINATE":
        prefix = "Adresskopf" if bundle["bundle_id"] == head_id else "Dieselbe Adressspur"
        if line_reading.startswith("Adressspur: "):
            line_reading = line_reading.removeprefix("Adressspur: ")
        line = f"{prefix} — {line_reading}"
    else:
        prefix = "Listenkopf" if bundle["bundle_id"] == head_id else "Fortgesetzter Katalogeintrag"
        line = f"{prefix} — {chosen_reading}"

    local_repair = repairs(bundle, chosen)
    alternatives = [model for model in local_best if model != chosen]
    if chosen not in local_best:
        alternatives = local_best
    return {
        "context_decided": decided,
        "context_class": context_class,
        "context_selected_model": chosen,
        "selection_source": source,
        "record_head_model": head_model if multi else "NONE",
        "record_head_bundle_id": head_id if multi else "NONE",
        "record_head_evidence": head_evidence if multi else "NONE",
        "context_strength": strength if multi else "NO_MULTI_LOCUS_CONTEXT",
        "local_selected_repair_count": local_repair,
        "inherited_context_repair_credit": credit,
        "net_context_repair_count": local_repair - credit,
        "model_changed_from_gdt474": "YES" if chosen != old_model else "NO",
        "context_selected_reading_de": chosen_reading,
        "contextual_line_de": line,
        "local_best_alternatives_preserved": "|".join(alternatives) or "NONE",
    }


def continuation_prefix(model: str) -> str:
    return {
        "INSTRUCTION": "Im selben Arbeitsgang",
        "COORDINATE": "Dazugehörige Adressspur",
        "CATALOGUE": "Fortgesetzter Katalogeintrag",
    }[model]


def record_class(models: list[str]) -> str:
    if all(model == "INSTRUCTION" for model in models):
        return "ACTION_CHAIN"
    if models[0] == "INSTRUCTION":
        return "ACTION_WITH_CARRIED_ARGUMENTS_OR_ADDRESS"
    if models[0] == "COORDINATE":
        return "COORDINATE_CHAIN"
    if models[-1] == "INSTRUCTION":
        return "CATALOGUE_SETUP_THEN_ACTION"
    return "CATALOGUE_CHAIN"


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_readable(
    decisions: list[dict[str, object]],
    record_rows: list[dict[str, object]],
    page_rows: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in decisions:
        by_page[str(row["physical_page"])].append(row)

    lines = [
        "# GDT476 — kontextuelle Arbeitslesung der 64 GDT474-Gleichstände",
        "",
        "Kein Eintrag bleibt ohne Default. Zwölf Gleichstände liegen in den acht echten Mehrlocus-Registern aus GDT475 und können deshalb als ein zusammenhängender Arbeitsgang, eine Adressspur oder ein Katalogeintrag gelesen werden. Die übrigen 52 behalten die lokale GDT474-Lesung; ihre Alternativen bleiben sichtbar.",
        "",
        "Sechs Arbeitsmodelle ändern sich. Vier davon waren lokal um genau ein ergänztes Verb teurer; ein vorausgehender Arbeitskopf plus recordbindendes `OL=FORTSETZEN` liefert dieses Verb nun aus dem sichtbaren Kontext. Dabei werden weder Stammdeutungen noch gelernte Namen verändert.",
        "",
        "## Die acht zusammenhängenden Mikroregister",
        "",
        "| Seite | Register | Kontexttyp | Modelle vorher → jetzt | konkrete Arbeitslesung |",
        "|---|---|---|---|---|",
    ]
    for row in record_rows:
        lines.append(
            f"| {row['physical_page']} | {row['record_id']} · {markdown_escape(row['locus_sequence'])} | {row['context_record_class']} | {markdown_escape(row['old_selected_model_sequence'])} → {markdown_escape(row['context_selected_model_sequence'])} | {markdown_escape(row['context_record_reading_de'])} |"
        )

    lines.extend([
        "",
        "## Alle 64 offenen lokalen Gleichstände",
        "",
        "`Kontext` bedeutet eine Auswahl durch ein echtes Mehrlocus-Register. `Default` bedeutet: Der Seitenkontext entscheidet noch nicht, daher bleibt die bereits vorhandene lokale Lesung aktiv.",
        "",
    ])
    page_summary = {str(row["physical_page"]): row for row in page_rows}
    for page, rows in by_page.items():
        summary = page_summary[page]
        lines.extend([
            f"### {page}",
            "",
            f"{summary['tie_count']} Gleichstände; {summary['context_decided_count']} durch Mehrlocus-Kontext geführt, {summary['local_default_count']} mit lokalem Default; {summary['model_change_count']} Modellwechsel.",
            "",
            "| Bündel · Locus | Form(en) | Grenze | Auswahl | Arbeitslesung | erhaltene lokale Alternativen |",
            "|---|---|---|---|---|---|",
        ])
        for row in rows:
            mode = "Kontext" if row["context_decided"] == "YES" else "Default"
            lines.append(
                f"| {row['bundle_id']} · {row['locus']} | `{markdown_escape(str(row['surface_sequence']).replace('|', ' · '))}` | {row['boundary_role']} | {mode}: {row['context_selected_model']} | {markdown_escape(row['contextual_line_de'])} | {markdown_escape(row['local_best_alternatives_preserved'])} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bundles = read_tsv(BUNDLES)
    boundaries = read_tsv(BOUNDARIES)
    records = read_tsv(RECORDS)
    chains = read_tsv(CHAINS)
    if len(bundles) != 146 or len(boundaries) != 146 or len(records) != 135 or len(chains) != 8:
        raise RuntimeError("GDT474/GDT475 input size drift")

    bundle_map = {row["bundle_id"]: row for row in bundles}
    boundary_map = {row["bundle_id"]: row for row in boundaries}
    record_map = {row["record_id"]: row for row in records}
    if set(bundle_map) != set(boundary_map):
        raise RuntimeError("Bundle/boundary join drift")

    head_by_record = {row["record_id"]: record_head(row, bundle_map) for row in records}
    decisions: list[dict[str, object]] = []
    decision_map: dict[str, dict[str, object]] = {}
    tie_counter = 0
    for bundle in bundles:
        if not is_tied(bundle):
            continue
        tie_counter += 1
        boundary = boundary_map[bundle["bundle_id"]]
        record = record_map[boundary["record_id"]]
        head_model, head_id, head_evidence, strength = head_by_record[record["record_id"]]
        selected = contextual_selection(bundle, boundary, record, head_model, head_id, head_evidence, strength)
        row: dict[str, object] = {
            "tie_id": f"G476-T{tie_counter:03d}",
            "bundle_id": bundle["bundle_id"],
            "record_id": boundary["record_id"],
            "physical_page": bundle["physical_page"],
            "register": bundle["register"],
            "locus": bundle["locus"],
            "owner_de": bundle["owner_de"],
            "surface_sequence": bundle["surface_sequence"],
            "recipe_sequence": bundle["recipe_sequence"],
            "boundary_role": boundary["boundary_role"],
            "record_bundle_count": record["bundle_count"],
            "local_best_models": bundle["best_models"],
            "gdt474_selected_model": bundle["selected_model"],
            **selected,
            "gdt474_selected_reading_de": bundle["selected_bundle_reading_de"],
            "root_meaning_change": "NO",
            "learned_name_change": "NO",
            "claim_status": "COMPLETE_CONTEXTUAL_WORKING_DEFAULT__ALTERNATIVES_PRESERVED",
        }
        decisions.append(row)
        decision_map[bundle["bundle_id"]] = row

    record_rows: list[dict[str, object]] = []
    for chain in chains:
        ids = chain["bundle_ids"].split("|")
        head_model, head_id, head_evidence, strength = head_by_record[chain["record_id"]]
        models: list[str] = []
        readings: list[str] = []
        changes = 0
        context_ties = 0
        for index, bundle_id in enumerate(ids):
            bundle = bundle_map[bundle_id]
            decision = decision_map.get(bundle_id)
            model = str(decision["context_selected_model"]) if decision else bundle["selected_model"]
            selected_reading = str(decision["context_selected_reading_de"]) if decision else reading(bundle, model)
            models.append(model)
            if index == 0:
                readings.append(selected_reading)
            else:
                prefix = continuation_prefix(model)
                if model == "INSTRUCTION" and head_model != "INSTRUCTION":
                    prefix = "Dazugehörige Anweisung"
                if model == "COORDINATE" and selected_reading.startswith("Adressspur: "):
                    selected_reading = selected_reading.removeprefix("Adressspur: ")
                readings.append(f"{prefix}: {selected_reading}")
            if decision:
                context_ties += int(decision["context_decided"] == "YES")
                changes += int(decision["model_changed_from_gdt474"] == "YES")
        record_rows.append({
            "context_record_id": f"G476-R{len(record_rows) + 1:02d}",
            "record_id": chain["record_id"],
            "physical_page": chain["physical_page"],
            "register": chain["register"],
            "bundle_count": chain["bundle_count"],
            "bundle_ids": chain["bundle_ids"],
            "locus_sequence": chain["locus_sequence"],
            "surface_sequence": chain["surface_sequence"],
            "record_head_model": head_model,
            "record_head_bundle_id": head_id,
            "record_head_evidence": head_evidence,
            "context_strength": strength,
            "context_record_class": record_class(models),
            "old_selected_model_sequence": chain["selected_model_sequence"],
            "context_selected_model_sequence": "|".join(models),
            "context_decided_tie_count": context_ties,
            "model_change_count": changes,
            "context_record_reading_de": " ".join(readings),
            "claim_status": "INTEGRATED_MICRORECORD_WORKING_READING__NO_PLAINTEXT_CLAIM",
        })

    page_rows: list[dict[str, object]] = []
    decisions_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in decisions:
        decisions_by_page[str(row["physical_page"])].append(row)
    for page, rows in decisions_by_page.items():
        chosen = Counter(str(row["context_selected_model"]) for row in rows)
        page_rows.append({
            "physical_page": page,
            "register": rows[0]["register"],
            "tie_count": len(rows),
            "context_decided_count": sum(row["context_decided"] == "YES" for row in rows),
            "local_default_count": sum(row["context_decided"] == "NO" for row in rows),
            "model_change_count": sum(row["model_changed_from_gdt474"] == "YES" for row in rows),
            "context_coordinate_count": chosen["COORDINATE"],
            "context_instruction_count": chosen["INSTRUCTION"],
            "context_catalogue_count": chosen["CATALOGUE"],
            "all_ties_have_working_default": "YES",
        })

    chosen_counts = Counter(str(row["context_selected_model"]) for row in decisions)
    changed_ids = [str(row["bundle_id"]) for row in decisions if row["model_changed_from_gdt474"] == "YES"]
    override_ids = [str(row["bundle_id"]) for row in decisions if str(row["context_selected_model"]) not in str(row["local_best_models"]).split("|")]
    result: dict[str, object] = {
        "status": "TWELVE_TIES_GAIN_RECORD_CONTEXT__SIX_WORKING_MODELS_CHANGE",
        "input_bundle_count": len(bundles),
        "input_record_count": len(records),
        "tie_count": len(decisions),
        "context_decided_tie_count": sum(row["context_decided"] == "YES" for row in decisions),
        "local_default_tie_count": sum(row["context_decided"] == "NO" for row in decisions),
        "model_change_count": len(changed_ids),
        "model_change_bundle_ids": changed_ids,
        "context_override_local_minimum_count": len(override_ids),
        "context_override_local_minimum_bundle_ids": override_ids,
        "inherited_action_repair_credit_total": sum(int(row["inherited_context_repair_credit"]) for row in decisions),
        "context_selected_model_counts": dict(chosen_counts),
        "multi_locus_context_record_count": len(record_rows),
        "page_count": len(page_rows),
        "all_ties_have_default_count": len(decisions),
        "component_meaning_change_count": 0,
        "learned_name_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "new_page_count": 0,
        "claim_ceiling": "Creative record-context selection among existing GDT474 readings; no plaintext, confirmed syntax, lexeme, object identity, new stem meaning, learned name, surface, recipe, event, or page.",
    }

    write_tsv(DECISIONS_OUT, decisions)
    write_tsv(RECORD_READINGS_OUT, record_rows)
    write_tsv(PAGE_SUMMARY_OUT, page_rows)
    READABLE_OUT.write_text(build_readable(decisions, record_rows, page_rows, result), encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "ties": result["tie_count"],
        "context_decided": result["context_decided_tie_count"],
        "model_changes": result["model_change_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
