#!/usr/bin/env python3
"""Build the GDT735 historical semantic-bridge atlas.

EVA characters remain modern transcription labels. This experiment compares
architectures and opaque distributional classes; it never turns an EVA label
into a Latin initial, sound, glyph value, or lexeme.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas"
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

CORE_GRID = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/CONCRETE_FOUR_HEAD_PARADIGMS.tsv"
RESIDUAL_GRID = ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/RESIDUAL_76_FORM_GRID.tsv"
HEAD_PROFILE = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/INITIAL_HEAD_SCOPE_PROFILE.tsv"

HEADS = ("p", "s", "r", "l")
OPAQUE_HEAD = {
    "p": ("H1", "H_EVA_P"),
    "s": ("H2", "H_EVA_S"),
    "r": ("H3", "H_EVA_R"),
    "l": ("H4", "H_EVA_L"),
}
LATIN_FIELDS = ("PULVIS", "SEMEN", "RADIX", "LIGNUM")
INVALID_INITIAL_MATCH = {
    "p": "PULVIS",
    "s": "SEMEN",
    "r": "RADIX",
    "l": "LIGNUM",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_slots(value: str) -> set[str]:
    if not value or value == "NONE":
        return set()
    return {part for part in value.split("|") if part and part != "NONE"}


def evidence_tier(row: dict[str, str]) -> str:
    text = " ".join((row.get("locator", ""), row.get("caveat", ""))).lower()
    if "catalogue" in text or "catalog" in text:
        return "CATALOGUE_ARCHITECTURE_ONLY"
    if "ocr" in text or "edition" in text:
        return "EDITED_OR_OCR_OBSERVATION"
    return "TARGETED_DIRECT_OBSERVATION"


def tv_distance(target_counts: dict[str, int], source_counts: dict[str, int], mapping: dict[str, str]) -> float:
    target_total = sum(target_counts.values())
    source_total = sum(source_counts.values())
    return 0.5 * sum(
        abs(target_counts[head] / target_total - source_counts[mapping[head]] / source_total)
        for head in HEADS
    )


def opaque_grid() -> tuple[list[dict[str, object]], dict[str, int]]:
    rows: list[dict[str, object]] = []
    core = read_tsv(CORE_GRID)
    residual = read_tsv(RESIDUAL_GRID)

    for source_id, source_rows in (("GDT635_CORE", core), ("GDT636_RESIDUAL", residual)):
        for old in source_rows:
            head = old["head"]
            if head not in OPAQUE_HEAD:
                raise AssertionError(f"unexpected head {head!r}")
            opaque_id, eva_class = OPAQUE_HEAD[head]
            body_role = old.get("body_value_de") or old.get("body_default_de") or "UNRESOLVED_BODY_ROLE"
            rows.append(
                {
                    "bridge_cell_id": f"G735-C{len(rows) + 1:03d}",
                    "source_experiment": source_id,
                    "source_cell_id": old["cell_id"],
                    "eva_transcription_label": head,
                    "opaque_head_id": opaque_id,
                    "opaque_source_class": eva_class,
                    "distributional_subclass": "ENTRY_BIASED" if head in {"p", "s"} else "INTERNAL_OR_FINAL_BIASED",
                    "body": old["body"],
                    "form": old["form"],
                    "occurrences": int(old["occurrences"]),
                    "reader_exact_occurrences": int(old["reader_exact_occurrences"]),
                    "inherited_body_role_de": body_role,
                    "opaque_bridge_reading_de": f"{opaque_id}: {body_role}",
                    "literal_head_lexeme": "UNRESOLVED",
                    "eva_initial_credit": 0,
                    "relation_credit": 0,
                    "status": "OPAQUE_HEAD_PLUS_INHERITED_BODY_ROLE_ONLY",
                }
            )

    forms = [str(row["form"]) for row in rows]
    if len(rows) != 96 or len(set(forms)) != 96:
        raise AssertionError(f"expected 96 unique target forms, got {len(rows)} rows/{len(set(forms))} forms")
    expected_heads = Counter({"H1": 24, "H2": 24, "H3": 24, "H4": 24})
    if Counter(str(row["opaque_head_id"]) for row in rows) != expected_heads:
        raise AssertionError("opaque head grid is not balanced 24 x 4")

    metrics = {
        "cells": len(rows),
        "bodies": len({str(row["body"]) for row in rows}),
        "forms": len(set(forms)),
        "occurrences": sum(int(row["occurrences"]) for row in rows),
        "reader_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in rows),
    }
    return rows, metrics


def permutation_diagnostic(field_rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    profiles = {row["head"]: row for row in read_tsv(HEAD_PROFILE) if row["head"] in HEADS}
    target_counts = {head: int(profiles[head]["initial_occurrences"]) for head in HEADS}

    by_source: dict[str, dict[str, int]] = defaultdict(dict)
    for row in field_rows:
        if row["field_stem"] in LATIN_FIELDS:
            by_source[row["source_id"]][row["field_stem"]] = int(row["mention_count"])
    if any(set(counts) != set(LATIN_FIELDS) for counts in by_source.values()):
        raise AssertionError("each historical frequency dataset must contain the four diagnostic fields")
    if len(by_source) != 2:
        raise AssertionError(f"expected two OCR diagnostic datasets, found {len(by_source)}")

    raw: list[dict[str, object]] = []
    for permutation in itertools.permutations(LATIN_FIELDS):
        mapping = dict(zip(HEADS, permutation))
        distances = {source_id: tv_distance(target_counts, counts, mapping) for source_id, counts in by_source.items()}
        raw.append(
            {
                "mapping": mapping,
                "distances": distances,
                "mean_distance": sum(distances.values()) / len(distances),
                "mapping_key": "|".join(f"{OPAQUE_HEAD[h][0]}={mapping[h]}" for h in HEADS),
                "invalid_initial": int(mapping == INVALID_INITIAL_MATCH),
            }
        )

    source_ranks: dict[str, dict[str, int]] = {}
    for source_id in sorted(by_source):
        ranked = sorted(raw, key=lambda row: (float(row["distances"][source_id]), str(row["mapping_key"])))
        source_ranks[source_id] = {str(row["mapping_key"]): rank for rank, row in enumerate(ranked, 1)}
    joint_ranked = sorted(raw, key=lambda row: (float(row["mean_distance"]), str(row["mapping_key"])))
    joint_ranks = {str(row["mapping_key"]): rank for rank, row in enumerate(joint_ranked, 1)}

    output: list[dict[str, object]] = []
    for row in sorted(raw, key=lambda item: joint_ranks[str(item["mapping_key"])]):
        mapping = row["mapping"]
        out: dict[str, object] = {
            "joint_rank": joint_ranks[str(row["mapping_key"])],
            "mapping_id": f"G735-P{joint_ranks[str(row['mapping_key'])]:02d}",
            "H1_eva_p_field": mapping["p"],
            "H2_eva_s_field": mapping["s"],
            "H3_eva_r_field": mapping["r"],
            "H4_eva_l_field": mapping["l"],
            "target_structural_cells_explained": 96,
            "structural_fit_rank": 1,
            "structural_tie_size": 24,
        }
        for source_id in sorted(by_source):
            out[f"{source_id}_tv"] = f"{row['distances'][source_id]:.6f}"
            out[f"{source_id}_rank"] = source_ranks[source_id][str(row["mapping_key"])]
        out.update(
            {
                "mean_tv": f"{row['mean_distance']:.6f}",
                "is_anachronistic_eva_initial_match": row["invalid_initial"],
                "eva_letter_or_initial_credit": 0,
                "semantic_identification_credit": 0,
                "status": "FREQUENCY_COMPATIBILITY_DIAGNOSTIC_ONLY__ALL_24_STRUCTURALLY_TIED",
            }
        )
        output.append(out)

    invalid = next(row for row in output if int(row["is_anachronistic_eva_initial_match"]) == 1)
    summary: dict[str, object] = {
        "target_counts": target_counts,
        "sources": sorted(by_source),
        "invalid_joint_rank": int(invalid["joint_rank"]),
        "invalid_source_ranks": {source_id: int(invalid[f"{source_id}_rank"]) for source_id in sorted(by_source)},
        "best_joint_mapping": next(row for row in output if int(row["joint_rank"]) == 1),
    }
    return output, summary


def historical_atlas(
    registry: list[dict[str, str]], observations: list[dict[str, str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    registry_by_id = {row["source_id"]: row for row in registry}
    atlas: list[dict[str, object]] = []
    for row in observations:
        if row["source_id"] not in registry_by_id:
            raise AssertionError(f"observation points to unknown source {row['source_id']}")
        atlas.append(
            {
                **row,
                "evidence_tier": evidence_tier(row),
                "architecture_channel": (
                    "DESCRIPTIVE"
                    if row["record_mode"].startswith("DESCRIPTIVE")
                    else "PRESCRIPTIVE"
                    if row["record_mode"].startswith("PRESCRIPTIVE")
                    else "MIXED_REFERENCE"
                ),
                "voynich_mapping_credit": 0,
                "one_letter_four_head_code_attested": 0,
            }
        )

    by_source: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in atlas:
        by_source[str(row["source_id"])].append(row)

    source_matrix: list[dict[str, object]] = []
    direct_both_sources: list[str] = []
    for source_id, rows in sorted(by_source.items()):
        reg = registry_by_id[source_id]
        modes = {str(row["architecture_channel"]) for row in rows}
        all_slots = set().union(*(split_slots(str(row["observed_slots"])) for row in rows))
        descriptive_slots = set().union(*(split_slots(str(row["descriptive_slots"])) for row in rows))
        prescriptive_slots = set().union(*(split_slots(str(row["prescriptive_slots"])) for row in rows))
        has_direct_descriptive = any(
            row["architecture_channel"] == "DESCRIPTIVE" and row["evidence_tier"] == "TARGETED_DIRECT_OBSERVATION"
            for row in rows
        )
        has_direct_prescriptive = any(
            row["architecture_channel"] == "PRESCRIPTIVE" and row["evidence_tier"] == "TARGETED_DIRECT_OBSERVATION"
            for row in rows
        )
        if has_direct_descriptive and has_direct_prescriptive:
            direct_both_sources.append(source_id)
        source_matrix.append(
            {
                "source_id": source_id,
                "work": reg["work"],
                "date_band": reg["date_band"],
                "observation_rows": len(rows),
                "record_channels": "|".join(sorted(modes)),
                "observed_slots": "|".join(sorted(all_slots)),
                "descriptive_slots": "|".join(sorted(descriptive_slots)) or "NONE",
                "prescriptive_slots": "|".join(sorted(prescriptive_slots)) or "NONE",
                "direct_descriptive_observation": int(has_direct_descriptive),
                "direct_prescriptive_observation": int(has_direct_prescriptive),
                "direct_two_channel_same_source": int(has_direct_descriptive and has_direct_prescriptive),
                "actual_four_head_one_letter_code_attested": 0,
                "voynich_relation_credit": 0,
                "claim_ceiling": "HISTORICAL_ARCHITECTURE_ONLY",
            }
        )

    slot_rows: list[dict[str, object]] = []
    all_slots = sorted(set().union(*(split_slots(row["observed_slots"]) for row in observations)))
    for slot in all_slots:
        matching = [row for row in observations if slot in split_slots(row["observed_slots"])]
        slot_rows.append(
            {
                "slot": slot,
                "observation_rows": len(matching),
                "unique_sources": len({row["source_id"] for row in matching}),
                "source_ids": "|".join(sorted({row["source_id"] for row in matching})),
                "descriptive_rows": sum(slot in split_slots(row["descriptive_slots"]) for row in matching),
                "prescriptive_rows": sum(slot in split_slots(row["prescriptive_slots"]) for row in matching),
                "relation_credit": 0,
            }
        )

    mode_counts = Counter(str(row["architecture_channel"]) for row in atlas)
    hist_summary: dict[str, object] = {
        "registry_sources": len(registry),
        "observation_rows": len(atlas),
        "observed_sources": len(by_source),
        "mode_counts": dict(sorted(mode_counts.items())),
        "direct_two_channel_sources": direct_both_sources,
        "actual_four_head_one_letter_code_sources": 0,
    }
    return atlas, source_matrix, slot_rows, hist_summary


def model_comparison(models: list[dict[str, str]]) -> list[dict[str, object]]:
    disposition = {
        "M01": ("REJECTED_ANACHRONISTIC_NEGATIVE_CONTROL", 0, 0, "EVA labels are modern transcription labels, not Latin initials."),
        "M02": ("RETAINED_NONIDENTIFYING_24_WAY_DIAGNOSTIC", 96, 0, "All 24 assignments tie on target structure; frequency ecology cannot identify a head."),
        "M03": ("DIRECTLY_ATTESTED_DESCRIPTIVE_SUBMODEL", 36, 0, "Learned name plus quality and degree is historically direct; target axis labels remain unresolved."),
        "M04": ("SELECTED_HISTORICAL_CONTENT_ARCHITECTURE_PRIOR", 96, 0, "Descriptive and prescriptive record modes coexist historically; their Voynich linkage remains untested."),
        "M05": ("RETAINED_STRUCTURAL_VALUE_SUBMODEL", 28, 0, "Bound degrees and amounts are historical; target ladders have order but no fixed dimension."),
        "M06": ("SELECTED_GENERAL_ENCODING_ARCHITECTURE", 96, 0, "Mixed learned wholes and bound specialist abbreviations best span the historical evidence."),
        "M07": ("RETAINED_REQUIRED_WHOLE_WORD_FALLBACK", 96, 0, "Historical glossaries require memorized names alongside productive fields."),
        "M08": ("UNRESOLVED_OPAQUE_H4_ROLE_DIAGNOSTIC", 24, 0, "No historical or target evidence selects wood, liquor, extract, liquid, or weight for H4."),
    }
    rows: list[dict[str, object]] = []
    for row in models:
        model_id = row["model_id"]
        state, compatible, identified, reason = disposition[model_id]
        rows.append(
            {
                "model_id": model_id,
                "model_family": row["model_family"],
                "target_96_compatible_cells": compatible,
                "target_literal_head_cells_identified": identified,
                "historical_actual_four_head_code_sources": 0,
                "eva_letter_or_initial_credit": 0,
                "component_export_credit": row["component_export_credit"],
                "literal_lexeme_claim_allowed": row["literal_lexeme_claim_allowed"],
                "disposition": state,
                "reason": reason,
                "claim_ceiling": row["claim_ceiling"],
            }
        )
    return rows


def role_dictionary(seeds: list[dict[str, str]], profiles: list[dict[str, str]]) -> list[dict[str, object]]:
    profile_by_class = {OPAQUE_HEAD[row["head"]][1]: row for row in profiles if row["head"] in OPAQUE_HEAD}
    rows: list[dict[str, object]] = []
    for seed in seeds:
        surface = seed["surface_or_class"]
        opaque_id = ""
        form_confidence = "MEDIUM"
        semantic_confidence = "UNRESOLVED"
        evidence = seed["minimum_support_for_role"]
        if surface in profile_by_class:
            profile = profile_by_class[surface]
            opaque_id = OPAQUE_HEAD[profile["head"]][0]
            form_confidence = "HIGH_CONTRASTIVE_HEAD_CLASS"
            semantic_confidence = "ZERO_LITERAL_IDENTIFICATION"
            evidence = (
                f"{profile['initial_occurrences']} token-initial occurrences; "
                f"{profile['initial_types']} types; line first/middle/last "
                f"{profile['line_first']}/{profile['line_middle']}/{profile['line_last']}; "
                "24 shared four-head bodies in the GDT735 target grid"
            )
        elif surface in {"k", "t", "ch", "sh"}:
            form_confidence = "MEDIUM_HIGH_BOUND_CONTRAST"
            semantic_confidence = "LOW_WORKING_ROLE_ONLY"
        elif surface in {"aiin", "ain", "ar", "or"}:
            form_confidence = "MEDIUM_HIGH_BOUND_LADDER_OR_CARRIER"
            semantic_confidence = "UNRESOLVED_DIMENSION"
        elif surface in {"dy", "q"}:
            form_confidence = "MEDIUM_CONTEXT_BOUND"
            semantic_confidence = "UNRESOLVED_NO_FREE_LEXEME"
        elif surface == "LEARNED_LONG_CORES":
            form_confidence = "HIGH_ARCHITECTURAL_ROLE"
            semantic_confidence = "UNRESOLVED_INDIVIDUAL_NAMES"
        rows.append(
            {
                "seed_id": seed["seed_id"],
                "surface_or_class": surface,
                "opaque_head_id": opaque_id,
                "broad_role_family": seed["role_family"],
                "working_role_seed": seed["primary_role_seed"],
                "licensed_rivals": seed["licensed_rivals"],
                "form_confidence": form_confidence,
                "semantic_confidence": semantic_confidence,
                "literal_lexeme_status": seed["literal_lexeme_status"],
                "evidence": evidence,
                "portable_policy": seed["portable_default_policy"],
                "falsifier": seed["falsifier"],
                "historical_field_analogy": seed["historical_field_analogy"],
                "eva_letter_or_initial_credit": 0,
                "component_export_credit": 0,
                "claim_ceiling": seed["claim_ceiling"],
            }
        )
    return rows


def decision_register(permutation_summary: dict[str, object], hist_summary: dict[str, object]) -> list[dict[str, object]]:
    invalid_source_ranks = permutation_summary["invalid_source_ranks"]
    return [
        {
            "decision_id": "G735-D01", "subject": "EVA_P_S_R_L_AS_LATIN_INITIALS", "decision": "REJECT",
            "effect": "Replace literal head nouns with opaque H1-H4 in the bridge dictionary.",
            "evidence": "EVA labels are modern transliteration labels; no historical source attests the proposed four-head one-letter code.",
            "confidence": "DECISIVE_CATEGORY_ERROR",
        },
        {
            "decision_id": "G735-D02", "subject": "FOUR_CONTRASTIVE_HEAD_CLASSES", "decision": "RETAIN_FORMALLY",
            "effect": "Preserve exact head-plus-body contrasts and H1/H2 versus H3/H4 placement subclasses.",
            "evidence": "96 unique cells over 24 complete bodies; 24 cells per opaque head.",
            "confidence": "HIGH_FORMAL",
        },
        {
            "decision_id": "G735-D03", "subject": "PULVIS_SEMEN_RADIX_LIGNUM_ASSIGNMENT",
            "decision": "DEMOTE_TO_INVALID_INITIAL_MATCH_CONTROL",
            "effect": "No renderer may speak powder, seed, root, or wood from the head alone.",
            "evidence": (
                f"All 24 assignments tie structurally; the invalid EVA-initial match ranks "
                f"{invalid_source_ranks} in two OCR mention-frequency controls, which themselves carry zero mapping credit."
            ),
            "confidence": "HIGH_DEMOTION_ZERO_IDENTIFICATION",
        },
        {
            "decision_id": "G735-D04", "subject": "HISTORICAL_DESCRIPTIVE_RECORD",
            "decision": "RETAIN_AS_ARCHITECTURE_PRIOR",
            "effect": "Permit learned whole/name plus part/form, quality, and degree fields as a comparison grammar.",
            "evidence": "Clm667 and MS542 directly attest learned names with compact quality/degree fields.",
            "confidence": "HIGH_HISTORICAL_ARCHITECTURE",
        },
        {
            "decision_id": "G735-D05", "subject": "HISTORICAL_PRESCRIPTIVE_RECORD",
            "decision": "RETAIN_AS_ARCHITECTURE_PRIOR",
            "effect": "Keep command, ingredient, amount, and unit distinct from descriptive name/quality fields.",
            "evidence": "MS542, MS307, MS683, Manchester404, and Salzburg MI89 supply targeted prescriptive combinations.",
            "confidence": "HIGH_HISTORICAL_ARCHITECTURE",
        },
        {
            "decision_id": "G735-D06", "subject": "TWO_CHANNEL_PHARMACEUTICAL_HANDBOOK",
            "decision": "SELECT_AS_BEST_HISTORICAL_BRIDGE",
            "effect": "Use descriptive microentries and prescriptive recipe records as separate channels inside one mixed whole-plus-abbreviation model.",
            "evidence": f"Direct two-channel sources: {hist_summary['direct_two_channel_sources']}; MS542 is the strongest direct same-manuscript witness.",
            "confidence": "HIGH_HISTORICAL__TARGET_LINK_UNTESTED",
        },
        {
            "decision_id": "G735-D07", "subject": "ACTUAL_FOUR_HEAD_ONE_LETTER_CODEBOOK",
            "decision": "NOT_FOUND",
            "effect": "Do not infer any H1-H4 lexeme from historical vocabulary resemblance.",
            "evidence": f"{hist_summary['registry_sources']} registered sources and {hist_summary['observation_rows']} observations contain zero comparable four-head one-letter systems.",
            "confidence": "HIGH_WITHIN_INSPECTED_ATLAS",
        },
    ]


def report_text(metrics: dict[str, int], permutation_summary: dict[str, object], hist_summary: dict[str, object]) -> str:
    invalid_ranks = permutation_summary["invalid_source_ranks"]
    return f"""# GDT735 — historische Semantikbrücke ohne EVA-Initialentrick

## Ergebnis

Die historische Brücke ist real, aber sie liegt **eine Ebene höher als ein
Wörterbuchgleichnis**. Spätmittelalterliche pharmazeutische Handschriften
belegen zwei komplementäre Recordtypen:

1. **deskriptiv:** gelernter Drogenname oder Lemma, optional Pflanzenteil oder
   Stoffform, Qualität/Zustand und Grad;
2. **präskriptiv:** Befehl, benannte Zutat oder Zubereitung, gebundene Menge,
   Einheit und Prozess/Produkt.

Der beste historische Arbeitsrahmen ist deshalb ein gemischtes System aus
gelernten Ganzformen und gebundenen Fachfeldern, das beide Recordtypen getrennt
hält. Das ist eine bessere Architektur als ein flaches Wort-für-Wort-Lexikon.

## Die notwendige Korrektur

`p/s/r/l` sind moderne EVA-Transkriptionslabels, keine vom Schreiber gesetzten
lateinischen Buchstabenwerte. Die alte Merkhilfe
`p=pulvis, s=semen, r=radix, l=lignum` ist daher ein anachronistischer
Initialismus und erhält exakt null Buchstaben-, Laut-, Relations- oder
Übersetzungskredit.

Was formal erhalten bleibt, ist stark: {metrics['cells']} eindeutige Formen auf
{metrics['bodies']} vollständigen Restkörpern, je 24 unter vier kontrastiven
Kopfklassen. Sie heißen hier nur `H1-H4`; die zugehörigen EVA-Transkriptionslabels stehen
separat als Herkunftslabels. Zusammen tragen sie {metrics['occurrences']}
Vorkommen, davon {metrics['reader_exact_occurrences']} oberflächenexakt in den
drei alternativen Lesungen. H1/H2 sind häufiger eintragsinitial, H3/H4 häufiger
intern oder final. Auch **vier kontrastive Köpfe** bedeutet daher noch nicht
**vier gleichartige Materialnamen**.

## Alle 24 Bedeutungszuordnungen

Alle 24 Permutationen von Pulver, Samen, Wurzel und Holz auf H1-H4 erklären
dieselben 96 Strukturzellen exakt gleich gut. Keine gewinnt Voynich-intern.
Der zusätzliche OCR-Häufigkeitsvergleich ist nur ein absichtlich schwacher
Negativkontrollwert: Die an EVA-Buchstaben angelehnte alte Zuordnung liegt bei
Alphita (HSR019) auf Rang {invalid_ranks['HSR019']} und bei Sinonoma (HSR020)
auf Rang {invalid_ranks['HSR020']} von 24. Die jeweils besten Zuordnungen
wechseln zwischen den Glossaren. Das
identifiziert **keine** Alternative; es zeigt, dass Vokabelhäufigkeit den
Kopfwert nicht retten kann.

## Historischer Befund

Das Atlasmaterial umfasst {hist_summary['registry_sources']} deduplizierte
Quellen, {hist_summary['observation_rows']} kompakte Eintragsbeobachtungen und
zwei OCR-Frequenzkontrollen. Die stärksten direkten Muster sind:

- Clm 667: gelernter Drogenname plus kompakter Heiß/Kalt-, Trocken/Feucht- und
  Gradcode;
- Wellcome MS.542: `Aloes lignum` beziehungsweise `Eleborus radix` plus
  heiß/trocken und Grad II/III; in derselben Handschrift außerdem knappe
  Rezeptbefehle und gezählte Tropfen;
- MS.307/MS.683: Zutat beziehungsweise `ana`, Einheit und Zahl als getrennte
  Rezeptslots;
- Salzburg M I 89: Rezeptbefehl mit ausgeschriebenem Pulver- oder Samenmaterial;
- Alphita/Sinonoma: gelernte Hauptwörter, Synonyme und Querverweise, nicht ein
  Vierbuchstaben-Code.

In keiner der {hist_summary['registry_sources']} Quellen wurde ein tatsächlich
vergleichbares System aus vier austauschbaren Einbuchstaben-Materialköpfen
gefunden. Historisch belegt ist die **Feldarchitektur**, nicht H1-H4.

## Neue Arbeitsbasis

Die Brückenschreibweise lautet nun beispielsweise:

```text
pchedy  -> H1 + [ererbter Zustandskörper: getrocknet]
schedy  -> H2 + [ererbter Zustandskörper: getrocknet]
rchedy  -> H3 + [ererbter Zustandskörper: getrocknet]
lchedy  -> H4 + [ererbter Zustandskörper: getrocknet]
```

Nicht mehr zulässig ist, daraus ohne zusätzliche Evidenz „getrocknetes Pulver“,
„getrocknete Saat“, „getrocknete Wurzel“ oder „getrocknetes Holz“ zu sprechen.
Die Körperrollen bleiben ausdrücklich geerbte Working Roles; GDT735 bestätigt
keine davon als Lexem.

Die beste nächste Suche ist damit präzise: reale historische Systeme gegen
die den H1-H4-Klassen zugrunde liegenden **Manuskriptgrapheme,
Leservarianten, Positionen und Recordrollen** prüfen und gleichzeitig in
wiederkehrenden Voynich-Mikroeinträgen nach der
Trennung von Name/Teil/Qualität/Grad und Befehl/Zutat/Menge/Einheit suchen.
Eine passende lateinische Anfangsbuchstabenfolge zählt dabei nie wieder als
Evidenz.

## Claim-Grenze

`TWO_CHANNEL_PHARMACEUTICAL_ARCHITECTURE_ATTESTED; MIXED_WHOLE_PLUS_BOUND_FIELD_MODEL_SELECTED; FOUR_HEAD_SEMANTICS_UNIDENTIFIED; EVA_INITIALISM_REJECTED; ZERO_LEXEME_OR_GLYPH_IDENTIFICATIONS; NO_NEW_PAGE`.
"""


def build(output_dir: Path, report_path: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    registry = read_tsv(SRC / "HISTORICAL_SOURCE_REGISTRY.tsv")
    observations = read_tsv(SRC / "HISTORICAL_ENTRY_OBSERVATIONS.tsv")
    field_counts = read_tsv(SRC / "HISTORICAL_FIELD_COUNTS.tsv")
    models = read_tsv(SRC / "BRIDGE_MODEL_SPECS.tsv")
    seeds = read_tsv(SRC / "SEMANTIC_ROLE_SEEDS.tsv")
    profiles = read_tsv(HEAD_PROFILE)

    if len(registry) != 22 or len(observations) != 17 or len(field_counts) != 28 or len(models) != 8 or len(seeds) != 16:
        raise AssertionError("unexpected source deck size")
    if any(int(row["relation_credit"]) != 0 for row in registry + observations + field_counts):
        raise AssertionError("historical evidence must carry zero Voynich relation credit")
    if any(int(row["component_export_credit"]) != 0 for row in models + seeds):
        raise AssertionError("bridge specs must carry zero component export credit")
    if any(int(row["literal_lexeme_claim_allowed"]) != 0 for row in models):
        raise AssertionError("no model may claim a literal lexeme")

    grid, metrics = opaque_grid()
    permutations, permutation_summary = permutation_diagnostic(field_counts)
    atlas, source_matrix, slot_census, hist_summary = historical_atlas(registry, observations)
    models_out = model_comparison(models)
    roles = role_dictionary(seeds, profiles)
    decisions = decision_register(permutation_summary, hist_summary)

    write_tsv(
        output_dir / "OPAQUE_96_HEAD_BODY_GRID.tsv", grid,
        ["bridge_cell_id", "source_experiment", "source_cell_id", "eva_transcription_label",
         "opaque_head_id", "opaque_source_class", "distributional_subclass", "body", "form",
         "occurrences", "reader_exact_occurrences", "inherited_body_role_de", "opaque_bridge_reading_de",
         "literal_head_lexeme", "eva_initial_credit", "relation_credit", "status"],
    )
    permutation_fields = [
        "joint_rank", "mapping_id", "H1_eva_p_field", "H2_eva_s_field", "H3_eva_r_field",
        "H4_eva_l_field", "target_structural_cells_explained", "structural_fit_rank", "structural_tie_size",
    ]
    for source_id in permutation_summary["sources"]:
        permutation_fields.extend((f"{source_id}_tv", f"{source_id}_rank"))
    permutation_fields.extend(
        ("mean_tv", "is_anachronistic_eva_initial_match", "eva_letter_or_initial_credit",
         "semantic_identification_credit", "status")
    )
    write_tsv(output_dir / "HEAD_FIELD_24_PERMUTATION_DIAGNOSTIC.tsv", permutations, permutation_fields)
    write_tsv(
        output_dir / "HISTORICAL_ENTRY_ATLAS.tsv", atlas,
        list(observations[0].keys()) + ["evidence_tier", "architecture_channel", "voynich_mapping_credit", "one_letter_four_head_code_attested"],
    )
    write_tsv(
        output_dir / "HISTORICAL_SOURCE_ARCHITECTURE_MATRIX.tsv", source_matrix,
        ["source_id", "work", "date_band", "observation_rows", "record_channels", "observed_slots",
         "descriptive_slots", "prescriptive_slots", "direct_descriptive_observation",
         "direct_prescriptive_observation", "direct_two_channel_same_source",
         "actual_four_head_one_letter_code_attested", "voynich_relation_credit", "claim_ceiling"],
    )
    write_tsv(
        output_dir / "HISTORICAL_SLOT_CENSUS.tsv", slot_census,
        ["slot", "observation_rows", "unique_sources", "source_ids", "descriptive_rows", "prescriptive_rows", "relation_credit"],
    )
    write_tsv(
        output_dir / "BRIDGE_MODEL_COMPARISON.tsv", models_out,
        ["model_id", "model_family", "target_96_compatible_cells", "target_literal_head_cells_identified",
         "historical_actual_four_head_code_sources", "eva_letter_or_initial_credit", "component_export_credit",
         "literal_lexeme_claim_allowed", "disposition", "reason", "claim_ceiling"],
    )
    write_tsv(
        output_dir / "SEMANTIC_BRIDGE_ROLE_DICTIONARY.tsv", roles,
        ["seed_id", "surface_or_class", "opaque_head_id", "broad_role_family", "working_role_seed",
         "licensed_rivals", "form_confidence", "semantic_confidence", "literal_lexeme_status", "evidence",
         "portable_policy", "falsifier", "historical_field_analogy", "eva_letter_or_initial_credit",
         "component_export_credit", "claim_ceiling"],
    )
    write_tsv(
        output_dir / "BRIDGE_DECISION_REGISTER.tsv", decisions,
        ["decision_id", "subject", "decision", "effect", "evidence", "confidence"],
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text(metrics, permutation_summary, hist_summary), encoding="utf-8")

    generated_tsv = sorted(output_dir.glob("*.tsv"))
    canonical_prefix = "experiments/yolo/gdt735_historical_semantic_bridge_atlas"
    result: dict[str, object] = {
        "schema": "GDT735_HISTORICAL_SEMANTIC_BRIDGE_ATLAS_RESULT_V1",
        "status": "TWO_CHANNEL_PHARMACEUTICAL_ARCHITECTURE_ATTESTED__MIXED_WHOLE_PLUS_BOUND_FIELD_MODEL_SELECTED__FOUR_HEAD_SEMANTICS_UNIDENTIFIED__EVA_INITIALISM_REJECTED__ZERO_LEXEMES__NO_NEW_PAGE",
        "target": metrics,
        "historical": hist_summary,
        "permutation_diagnostic": permutation_summary,
        "model_dispositions": {row["model_id"]: row["disposition"] for row in models_out},
        "claims": {
            "eva_labels_are_historical_letters": False,
            "actual_four_head_one_letter_code_found": False,
            "literal_head_lexemes_identified": 0,
            "voynich_glyph_values_identified": 0,
            "new_pages_used": 0,
            "f84_used": False,
            "f84r_used": False,
        },
        "artifact_hashes": {
            **{f"{canonical_prefix}/artifacts/{path.name}": sha256(path) for path in generated_tsv},
            f"{canonical_prefix}/REPORT.md": sha256(report_path),
        },
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--report-path", type=Path, default=EXP / "REPORT.md")
    args = parser.parse_args()
    result = build(args.output_dir, args.report_path)
    print(json.dumps({"status": result["status"], "target": result["target"], "historical": result["historical"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
