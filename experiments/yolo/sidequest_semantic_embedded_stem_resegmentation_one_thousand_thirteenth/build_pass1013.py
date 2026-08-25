#!/usr/bin/env python3
"""Build Pass 1013: collapse ten specialist roots into existing components."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1012 = ROOT / "experiments/yolo/sidequest_semantic_core_contract_one_thousand_twelfth"
PASS1010 = ROOT / "experiments/yolo/sidequest_semantic_ot_grade_and_concept_review_one_thousand_tenth"
PASS1011 = ROOT / "experiments/yolo/sidequest_semantic_manual_optical_passage_audit_one_thousand_eleventh"

SOURCE_CONTRACT = PASS1012 / "PASS1012_56_SIGN_SEMANTIC_CONTRACT.tsv"
SOURCE_CODEBOOK = PASS1010 / "PASS1010_175_GRADE_REVISED_CODEBOOK.tsv"
SOURCE_STATEMENTS = PASS1011 / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"

PORTABLE = "PORTABLE_CORE_MEANING"
FORMAL = "FORMAL_CONTROL_NOT_CONTENT_WORD"
LOCAL = "LOCAL_ADDRESS_OR_MEMORIZED_SIGN"

CONTENT_CORES = {"OK", "CH", "SH", "K", "AIIN", "S", "CHD", "OR", "T", "AIN", "R", "P"}
RELATION_CORES = {"Y", "OL", "OT", "AL", "AR", "L", "AIR"}

# These are semantic resegmentations, not claims that the manuscript encodes
# ordinary alphabetic morphemes.  The surface topology is preserved separately.
RESEGMENT: dict[str, tuple[str, ...]] = {
    "CTH": ("CH", "T"),
    "CKH": ("CH", "K"),
    "CHEO": ("CH", "E", "O"),
    "CHK": ("CH", "K"),
    "CPH": ("CH", "P"),
    "SHED": ("SH", "E"),
    "SOLK": ("OL", "K"),
    "LSH": ("L", "SH"),
    "CFH": ("CH", "LOCAL_CHAR_F"),
    "LD": ("L", "D_ADDR"),
}

RESEGMENT_META = [
    ("CTH", "C<T>H", "CH+T", "NEHMEN + EINSTELLEN", "BEREIT", "eingeschobene T-Variante des C_H-Rahmens"),
    ("CKH", "C<K>H", "CH+K", "NEHMEN + GEBEN", "DURCHLASS", "eingeschobene K-Variante; lokaler Weg bleibt Besitzerlesung"),
    ("CHEO", "CH+E+O", "CH+E+O", "NEHMEN + GRAD I + AUSFÜHRUNG", "AUSZUG", "lineare vorhandene Kerne; kein eigener Stoffstamm"),
    ("CHK", "CH+K", "CH+K", "NEHMEN + GEBEN", "BEARBEITEN", "lineare CH/K-Folge; nicht mit C<K>H gleichsetzen"),
    ("CPH", "C<P>H", "CH+P", "NEHMEN + EINSETZEN", "UMLEITEN", "eingeschobene P-Variante; Gegenstelle bleibt lokale Expansion"),
    ("SHED", "SH+E", "SH+E", "HALTEN + GRAD I", "ABSETZEN", "Grad-I-Halteform; DY schließt separat"),
    ("SOLK", "[S-renderer]+OL+K", "OL+K", "FORTSETZEN + GEBEN", "AUFFANGEN", "s ist bei den Rendererformen nicht semantisch erforderlich"),
    ("LSH", "L+SH", "L+SH", "VERBINDUNG + HALTEN", "SPÜLEN", "reguläre Kombination zweier vorhandener Kerne"),
    ("CFH", "C<F>H", "CH+LOCAL_CHAR_F", "NEHMEN + NEBENADRESSE", "TRENNEN", "eingeschobene lokale F-Adresse; Trennen bleibt mögliche Ausführung"),
    ("LD", "L+D", "L+D_ADDR", "VERBINDUNG + TEILADRESSE", "BEFESTIGEN", "nur einmal in qokylddy; kein eigener portabler Stamm"),
]


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand_tokens(tokens: list[str]) -> list[str]:
    return [part for token in tokens for part in RESEGMENT.get(token, (token,))]


def parse_sequence(value: str) -> list[list[str]]:
    return [expand_tokens(part.split("+")) for part in value.split(" | ")]


def main() -> None:
    _, old_contract = read_tsv(SOURCE_CONTRACT)
    _, codebook = read_tsv(SOURCE_CODEBOOK)
    statement_fields, statements = read_tsv(SOURCE_STATEMENTS)

    old_by_sign = {row["sign"]: row for row in old_contract}
    if set(RESEGMENT) - set(old_by_sign):
        raise SystemExit("resegmentation token absent from Pass 1012 contract")

    kept = {sign: row for sign, row in old_by_sign.items() if sign not in RESEGMENT}
    air = kept["AIR"]
    air.update(
        {
            "pass1012_class": PORTABLE,
            "semantic_kind": "REFERENT_SEQUENCE_OR_RELATION_CORE",
            "single_core_value_de": "LAUF",
            "allowed_contextual_realization_de": "Arbeitslauf, Flüssigkeitslauf oder Ringlauf",
            "forbidden_rescue_de": "kein universelles Wasser, Rohr, Einlass oder Richtung",
        }
    )

    values = {sign: row["single_core_value_de"] for sign, row in kept.items()}
    classes = {sign: row["pass1012_class"] for sign, row in kept.items()}
    unknown = {part for parts in RESEGMENT.values() for part in parts} - set(kept)
    if unknown:
        raise SystemExit(f"replacement uses unknown core(s): {sorted(unknown)}")
    if any(status == "SPECIALIST_MEANING_CANDIDATE" for status in classes.values()):
        raise SystemExit("specialist token unexpectedly survives")

    usage = {
        sign: {
            "root_mentions": 0,
            "event_occurrences": 0,
            "statements": set(),
            "pages": set(),
            "registers": set(),
            "surfaces": Counter(),
        }
        for sign in kept
    }
    replacement_mentions: Counter[str] = Counter()
    event_index: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    statement_statuses: Counter[str] = Counter()
    event_statuses: Counter[str] = Counter()
    pressure_rows: list[dict[str, str]] = []

    for statement in statements:
        surfaces = statement["surface_sequence"].split()
        old_events = [part.split("+") for part in statement["component_sequence"].split(" | ")]
        if len(surfaces) != len(old_events):
            raise SystemExit(f"surface/component mismatch {statement['statement_id']}")
        new_events: list[list[str]] = []
        per_event: Counter[str] = Counter()
        mention_counts: Counter[str] = Counter()
        literal_events: list[str] = []

        for surface, old_tokens in zip(surfaces, old_events):
            for token in old_tokens:
                if token in RESEGMENT:
                    replacement_mentions[token] += 1
            tokens = expand_tokens(old_tokens)
            if any(token not in kept for token in tokens):
                raise SystemExit(f"unknown expanded token in {statement['statement_id']}: {tokens}")
            new_events.append(tokens)
            for token in tokens:
                mention_counts[token] += 1
                info = usage[token]
                info["root_mentions"] += 1
                info["statements"].add(statement["statement_id"])
                info["pages"].add(statement["physical_page"])
                info["registers"].add(statement["register"])
                info["surfaces"][surface] += 1
            for token in set(tokens):
                usage[token]["event_occurrences"] += 1

            event_classes = {classes[token] for token in tokens}
            if LOCAL in event_classes:
                event_class = "LOCAL_OWNER_DEPENDENT"
            elif PORTABLE in event_classes:
                event_class = "PORTABLE_CORE_COMPOSITION"
            else:
                event_class = "FORMAL_CONTROL_ONLY"
            per_event[event_class] += 1
            event_statuses[event_class] += 1
            literal_events.append(" + ".join(values[token] for token in tokens))
            event_index[surface].append(
                ("+".join(tokens), statement["physical_page"], statement["statement_id"], statement["register"])
            )

        if per_event["LOCAL_OWNER_DEPENDENT"]:
            status = "LOCAL_OWNER_REQUIRED"
        elif per_event["PORTABLE_CORE_COMPOSITION"]:
            status = "PORTABLE_CORE_READABLE"
        else:
            status = "FORMAL_CONTROL_ONLY"
        statement_statuses[status] += 1

        pressure_rows.append(
            {
                **statement,
                "component_sequence": " | ".join("+".join(tokens) for tokens in new_events),
                "pass1013_statement_status": status,
                "portable_core_mentions": str(sum(mention_counts[t] for t in kept if classes[t] == PORTABLE)),
                "content_or_operation_core_mentions": str(sum(mention_counts[t] for t in CONTENT_CORES)),
                "referent_sequence_relation_mentions": str(sum(mention_counts[t] for t in RELATION_CORES)),
                "formal_control_mentions": str(sum(mention_counts[t] for t in kept if classes[t] == FORMAL)),
                "local_sign_mentions": str(sum(mention_counts[t] for t in kept if classes[t] == LOCAL)),
                "portable_event_count": str(per_event["PORTABLE_CORE_COMPOSITION"]),
                "formal_only_event_count": str(per_event["FORMAL_CONTROL_ONLY"]),
                "local_event_count": str(per_event["LOCAL_OWNER_DEPENDENT"]),
                "contract_literal_de": " | ".join(literal_events),
                "pass1013_working_translation_de": statement["optically_revised_translation"],
                "working_translation_status": (
                    "MANUAL_IMAGE_REPAIR"
                    if statement["optical_review_status"] == "MANUALLY_REVIEWED_ORIGINAL_IMAGE"
                    else "LEGACY_FLUENT_READING_NOT_YET_MANUALLY_REPAIRED"
                ),
            }
        )

    contract_rows: list[dict[str, str]] = []
    for sign, row in kept.items():
        info = usage[sign]
        updated = dict(row)
        updated.update(
            {
                "pass1012_class": classes[sign],
                "semantic_kind": row["semantic_kind"],
                "single_core_value_de": values[sign],
                "root_mentions": str(info["root_mentions"]),
                "event_occurrences": str(info["event_occurrences"]),
                "statement_count": str(len(info["statements"])),
                "page_count": str(len(info["pages"])),
                "register_count": str(len(info["registers"])),
                "pages": "|".join(sorted(info["pages"])),
                "registers": "|".join(sorted(info["registers"])),
                "surface_examples": "|".join(surface for surface, _ in info["surfaces"].most_common(8)),
                "forward_rule_de": (
                    "Neues Kompositum wörtlich mit diesem Kern lesen; bei Konflikt die Gesamtkarte aussondern."
                    if classes[sign] == PORTABLE
                    else "Nur als Steuer- oder Lokalzeichen verwenden; daraus kein neues Inhaltswort erzeugen."
                ),
            }
        )
        if sign == "AIR":
            updated["pass1010_value_de"] = "LAUF"
            updated["allowed_contextual_realization_de"] = "Arbeitslauf, Flüssigkeitslauf oder Ringlauf"
            updated["forbidden_rescue_de"] = "kein universelles Wasser, Rohr, Einlass oder Richtung"
        contract_rows.append(updated)

    contract_fields = list(old_contract[0].keys())
    contract_path = HERE / "PASS1013_46_SIGN_SEMANTIC_CONTRACT.tsv"
    write_tsv(contract_path, contract_fields, contract_rows)

    resegmentation_rows = []
    for token, surface_shape, replacement, literal, withdrawn, rationale in RESEGMENT_META:
        old = old_by_sign[token]
        resegmentation_rows.append(
            {
                "old_specialist_token": token,
                "surface_composition_shape": surface_shape,
                "replacement_recipe": replacement,
                "replacement_literal_de": literal,
                "withdrawn_portable_gloss_de": withdrawn,
                "running_mentions": str(replacement_mentions[token]),
                "pages": old["pages"],
                "registers": old["registers"],
                "decision": "RESEGMENT_INTO_EXISTING_CORES",
                "reason_de": rationale,
            }
        )
    resegmentation_fields = list(resegmentation_rows[0])
    resegmentation_path = HERE / "PASS1013_10_RESEGMENTATIONS.tsv"
    write_tsv(resegmentation_path, resegmentation_fields, resegmentation_rows)

    composition_rows: list[dict[str, str]] = []
    composition_units = [
        row for row in codebook if row["unit_type"] in {"FORMULA_CARD", "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD"}
    ]
    for unit in composition_units:
        if unit["unit_type"] == "FORMULA_CARD":
            old_target = unit["recognition_forms"]
            target_recipe = "+".join(expand_tokens(old_target.split("+")))
            matches = [
                (surface, page, statement_id, register)
                for surface, events in event_index.items()
                for recipe, page, statement_id, register in events
                if recipe == target_recipe
            ]
            recipes = {target_recipe}
        else:
            target_surfaces = set((unit["specialist_surface_forms"] or unit["recognition_forms"]).split("|"))
            events = [event for surface in target_surfaces for event in event_index.get(surface, [])]
            recipes = {recipe for recipe, _, _, _ in events}
            matches = [
                (surface, page, statement_id, register)
                for surface in target_surfaces
                for recipe, page, statement_id, register in event_index.get(surface, [])
            ]
        tokens = sorted({token for recipe in recipes for token in recipe.split("+")})
        token_classes = {classes[token] for token in tokens}
        if LOCAL in token_classes:
            decision = "LOCAL_COMPOSITION_ONLY"
        elif PORTABLE in token_classes:
            decision = "PORTABLE_COMPOSITION"
        else:
            decision = "FORMAL_COMPOSITION_ONLY"
        readings = {" + ".join(values[token] for token in recipe.split("+")) for recipe in recipes}
        composition_rows.append(
            {
                "teaching_unit_id": unit["teaching_unit_id"],
                "unit_type": unit["unit_type"],
                "surface_forms": "|".join(sorted({surface for surface, _, _, _ in matches})),
                "observed_events_in_627": str(len(matches)),
                "pages": "|".join(sorted({page for _, page, _, _ in matches})),
                "component_recipes": "|".join(sorted(recipes)),
                "pass1013_contract_reading_de": " || ".join(sorted(readings)),
                "composition_decision": decision,
                "content_core_count": str(sum(token in CONTENT_CORES for token in tokens)),
                "relation_core_count": str(sum(token in RELATION_CORES for token in tokens)),
                "formal_control_count": str(sum(classes[token] == FORMAL for token in tokens)),
                "local_sign_count": str(sum(classes[token] == LOCAL for token in tokens)),
                "pass1010_spoken_value_de": unit["spoken_value_de"],
                "pass1010_local_expansion_de": unit["concrete_context_values_de"],
                "local_expansion_status": (
                    "OWNER_BOUND_PARAPHRASE_ONLY"
                    if unit["unit_type"] == "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD"
                    else "ROOT_SUM_ONLY"
                ),
                "forward_prediction_de": "Zuerst die resegmentierte Kernsumme lesen; konkretere Verfahren bleiben lokal.",
            }
        )

    composition_fields = list(composition_rows[0])
    composition_path = HERE / "PASS1013_102_COMPOSITION_CONTRACTS.tsv"
    write_tsv(composition_path, composition_fields, composition_rows)

    pressure_fields = statement_fields + [
        "pass1013_statement_status",
        "portable_core_mentions",
        "content_or_operation_core_mentions",
        "referent_sequence_relation_mentions",
        "formal_control_mentions",
        "local_sign_mentions",
        "portable_event_count",
        "formal_only_event_count",
        "local_event_count",
        "contract_literal_de",
        "pass1013_working_translation_de",
        "working_translation_status",
    ]
    pressure_path = HERE / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"
    write_tsv(pressure_path, pressure_fields, pressure_rows)

    outputs = [contract_path, resegmentation_path, composition_path, pressure_path]
    summary = {
        "pass": 1013,
        "pages_unchanged": 22,
        "statements": len(statements),
        "visible_sign_entries": len(contract_rows),
        "specialist_candidates_remaining": 0,
        "resegmented_tokens": len(RESEGMENT),
        "resegmented_mentions": dict(sorted(replacement_mentions.items())),
        "contract_classes": dict(sorted(Counter(row["pass1012_class"] for row in contract_rows).items())),
        "event_statuses": dict(sorted(event_statuses.items())),
        "statement_statuses": dict(sorted(statement_statuses.items())),
        "composition_decisions": dict(sorted(Counter(row["composition_decision"] for row in composition_rows).items())),
        "outputs_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    (HERE / "PASS1013_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
