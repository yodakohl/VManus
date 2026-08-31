#!/usr/bin/env python3
"""Build the exhaustive GDT684 V57 semantic-specificity census."""

from __future__ import annotations

import csv
import hashlib
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
EXP = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census"
ART = EXP / "artifacts"
V57_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/V57_51_LINE_READER.tsv"
GDT683_RESULT_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/RESULT.json"
OL_LINE_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/OL_417_LINE_RERENDER.tsv"
GDT664_STEM_PATH = ROOT / "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts/STEM_MODEL_V41.tsv"
ANCHOR_PATH = EXP / "src/ANCHOR_DRIFT_SPECS.tsv"

LOW_CONFIDENCE_CARD_PATHS = [
    ("GDT671", ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/V48_WORKING_TOKEN_GLOSSARY.tsv"),
    ("GDT674", ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/src/F81R_TRANSFER_CARDS.tsv"),
    ("GDT677", ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion/artifacts/TARGET_FAMILY_CARDS.tsv"),
    ("GDT678", ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion/artifacts/TARGET_FAMILY_CARDS.tsv"),
    ("GDT679", ROOT / "experiments/yolo/gdt679_eight_three_hole_family_completion/artifacts/TARGET_FAMILY_CARDS.tsv"),
    ("GDT680", ROOT / "experiments/yolo/gdt680_eight_four_hole_family_completion/artifacts/TARGET_FAMILY_CARDS.tsv"),
    ("GDT681", ROOT / "experiments/yolo/gdt681_six_five_hole_family_completion/artifacts/TARGET_FAMILY_CARDS.tsv"),
]


SIGNAL_RULES = [
    ("IDENTITY_WATER", r"Wasser", "explicit water identity"),
    ("IDENTITY_ROOT", r"Wurzel", "root or root-drug identity"),
    ("IDENTITY_SEED", r"Samen|Saatgut", "seed identity"),
    ("IDENTITY_FLOWER_FRUIT", r"Blüt|Frucht|Reproduktion", "flower, fruit or reproductive-part identity"),
    ("IDENTITY_WOOD", r"Holz", "wood identity"),
    ("IDENTITY_POWDER", r"Pulver", "powder form identity"),
    ("IDENTITY_LEAF_HERB", r"Blatt|Kraut|CTH", "leaf, herb or CTH material identity"),
    ("IDENTITY_SALT", r"Salz", "salt identity"),
    (
        "MATERIAL_ROLE",
        r"Ansatz|Droge|Arznei|Rohstoff|Zubereitung|Kompositum|Species|Fraktion|Portion|Charge|Posten|Absud|Auszug|Gut|Material|Stoff|Substanz",
        "functional material or preparation role without necessarily naming an ingredient",
    ),
    ("STATE_HOT", r"heiß|erhitz|wärm", "hot or heated state"),
    ("STATE_COLD", r"kalt|kühl|abgekühl", "cold or cooled state"),
    ("STATE_DRY", r"trocken|trockn|getrocknet", "dry or drying state"),
    ("STATE_WET", r"feucht|einweich|eingeweicht|Mazeration", "wet or soaked state"),
    ("STATE_FINISHED", r"fertig|abgeschlossen|schließ", "finished or closed state"),
    ("VALUE_GRADE", r"Grad|Stufe", "grade or stage value"),
    ("VALUE_QUANTITY", r"Maß|Menge|Dosis|Teil|Einheit|Portion|Fraktion|Bündel|Handvoll", "quantity or division value"),
    (
        "STRUCTURAL_META",
        r"Eigenschafts-/Zustands-/Materialträger|Qualitäts-/Wertfeld|Eintrag/Bezug|Zubereitungsrahmen|Ansatzrahmen|hierzu:",
        "renderer or register label rather than a plaintext meaning",
    ),
    ("UNRESOLVED_COMPONENT", r"offen|unsicher", "the published gloss itself retains an unresolved component"),
    ("AMBIGUOUS_ALTERNATIVE", r"/", "slash-separated alternatives or fused role labels"),
    ("REGISTER_CONNECTIVE", r"hierzu|anschließend|Eintrag|Bezug", "record linkage or connective wording"),
]


ACTION_RULES = [
    ("ACT_TAKE", r"\b(?:nimm|nehmen)\b", "take"),
    ("ACT_MEASURE", r"\b(?:abmessen|messe(?:n)?\b[^.;]{0,20}\bab)\b", "measure"),
    ("ACT_ADD", r"\b(?:zugeben|hinzugeben|dazugeben|zusammengeben|geben|gib\b[^.;]{0,20}\bzu)\b", "add"),
    ("ACT_HEAT", r"\b(?:erhitze|erhitzen|anwärmen|nachwärmen)\b", "heat"),
    ("ACT_COOL", r"\b(?:abkühlen|kühlen|kühle)\b", "cool"),
    ("ACT_DRY", r"\b(?:trocknen|trockne|nachtrocknen)\b", "dry"),
    ("ACT_SOAK", r"\b(?:einweichen|einweiche)\b", "soak"),
    ("ACT_STRAIN", r"\b(?:abseihen|abseihe)\b", "strain"),
    ("ACT_SET", r"\b(?:ansetzen|setze\b[^.;]{0,20}\ban)\b", "set or prepare"),
    ("ACT_PREPARE", r"\b(?:aufbereiten|bereite|bereiten)\b", "prepare"),
    ("ACT_FINISH", r"\b(?:abschließen|schließe|schließen|fertigstellen|stelle\b[^.;]{0,20}\bfertig)\b", "finish"),
    ("ACT_DIVIDE", r"\b(?:abteilen|teile\b[^.;]{0,20}\bab)\b", "divide"),
    ("ACT_FILL", r"\babfüllen\b", "fill"),
    ("ACT_CONNECT", r"\bverbinden\b", "combine"),
    ("ACT_BRING", r"\bbringen\b", "bring to a stage"),
    ("ACT_HOLD", r"\bhalten\b", "hold"),
    ("ACT_DRAW_OFF", r"\babziehen\b", "draw off"),
    ("ACT_TREAT", r"\bbehandeln\b", "treat"),
    ("ACT_LEAD", r"\bführen\b", "lead to a stage"),
    ("ACT_USE", r"\bverwenden\b", "use"),
    ("ACT_MIX", r"\bmischen\b", "mix"),
    ("ACT_TRANSFER", r"\büberführen\b", "transfer"),
    ("ACT_FORM", r"\bbilden\b", "form"),
    ("ACT_REMOVE", r"\babnehmen\b", "remove"),
]

# Frozen lemma deck used only to compare free practical prose against the
# literal glosses at declared action ordinals.  It is intentionally separate
# from ACTION_RULES, which classify token information.
PRACTICAL_OPERATION_RULES = [
    ("abmessen", r"\b(?:abmessen|abzumessen|miss)\b"),
    ("abteilen", r"\babteilen\b"),
    ("abnehmen", r"\babnehmen\b"),
    ("abfüllen", r"\babfüllen\b"),
    ("abkühlen", r"\b(?:abkühlen|kühle)\b"),
    ("abziehen", r"\babziehen\b"),
    ("ansetzen", r"\bansetzen\b"),
    ("abschließen", r"\b(?:abschließen|schließe)\b"),
    ("bereitstellen", r"\bbereitstellen\b"),
    ("bereiten", r"\b(?:bereiten|bereite)\b"),
    ("bilden", r"\bbilden\b"),
    ("bringen", r"\bbringen\b"),
    ("einweichen", r"\b(?:einweichen|weiche)\b"),
    ("erhitzen", r"\b(?:erhitzen|erhitze)\b"),
    ("fertigstellen", r"\b(?:fertigstellen|stelle)\b"),
    ("führen", r"\bführen\b"),
    ("halten", r"\bhalten\b"),
    ("herstellen", r"\bherstellen\b"),
    ("hinzugeben", r"\bhinzugeben\b"),
    ("kühlen", r"\b(?:kühlen|kühle)\b"),
    ("mischen", r"\bmischen\b"),
    ("nachtrocknen", r"\bnachtrocknen\b"),
    ("nehmen", r"\b(?:nehmen|nimm)\b"),
    ("ruhen", r"\bruhen\b"),
    ("trocknen", r"\b(?:trocknen|trockne)\b"),
    ("überführen", r"\büberführen\b"),
    ("verwenden", r"\bverwenden\b"),
    ("verbinden", r"\bverbinden\b"),
    ("zugeben", r"\bzugeben\b"),
    ("zusammengeben", r"\bzusammengeben\b"),
    ("stellen", r"\bstellen\b"),
]
COMPILED_PRACTICAL_OPERATION_RULES = [
    (lemma, re.compile(pattern, re.IGNORECASE)) for lemma, pattern in PRACTICAL_OPERATION_RULES
]


IDENTITY_SIGNALS = {name for name, _, _ in SIGNAL_RULES if name.startswith("IDENTITY_")}
STATE_SIGNALS = {name for name, _, _ in SIGNAL_RULES if name.startswith("STATE_")}
VALUE_SIGNALS = {name for name, _, _ in SIGNAL_RULES if name.startswith("VALUE_")}
ACTION_SIGNALS = {name for name, _, _ in ACTION_RULES}
COMPILED_RULES = [(name, re.compile(pattern, re.IGNORECASE), description) for name, pattern, description in [*SIGNAL_RULES, *ACTION_RULES]]

# This strict queue is intentionally narrower than the exhaustive information
# classes.  It captures cards that still contain meta-language, an unresolved
# axis/head, or an explicitly open alternative.  The broader classification
# separately records every identity-less role/state/value position.
STRICT_DEBT_SURFACES = {
    "GENERIC_CARRIER": {"chol", "tol", "shol", "qochedain", "sheeey"},
    "VALUE_DIMENSION_OPEN": {"aiin", "aiiin", "dain", "daiin", "qodaiin"},
    "UNRESOLVED_BINDING": {"olkar", "olam"},
    "STRUCTURAL_META_CARD": {"dy", "y", "ychedy", "yteody", "yey", "qotain"},
    "OPEN_TAXONOMY_OR_MATERIAL_ALTERNATIVE": {
        "dshees", "raiin", "cthoor", "sain", "solchedy", "cthororaiin", "chor",
        "ram", "checthy", "checthedy", "shor", "shoral", "dshor",
    },
    "GENERIC_DRUG_HEAD": {
        "ches", "cheol", "cholches", "ckhol", "dold", "dolkain", "olchdy", "olkchdy",
        "qockhol", "qoekol", "qol", "qolky", "qolsheedy", "shkeol", "tolg", "tshol", "ytol",
    },
    "RAW_CLASS_WITHOUT_IDENTITY": {
        "al", "qoal", "chal", "okal", "kal", "qokal", "otal", "tal", "shal", "dal", "oidal", "shedal", "shdal",
    },
    "OPAQUE_FORM_CODE": {"fchoky", "olpcheey", "lcheey", "chpcheey", "cphy", "oidal", "chs", "okiin", "olal", "chepy", "opchey"},
    "QUANTITY_OR_UNIT_WITHOUT_HEAD": {"oror", "or", "da", "am", "dol"},
}
STRICT_CRITICAL = {"GENERIC_CARRIER", "UNRESOLVED_BINDING", "STRUCTURAL_META_CARD"}

# Independent, deliberately literal debt selectors.  Unlike the curated strict
# repair queue above, these flags ask only whether the currently printed card
# visibly exposes one of five failure modes.
OBJECT_WORD = re.compile(
    r"(?:Ansatz|Stoff|Material|Droge|Zubereitung|Kompositum|Fraktion|Portion|Charge|Pulver|Holz|Roh|Blüt|Samen|Saatgut|Wurzel|Gut|Species|Teil)",
    re.IGNORECASE,
)

MECHANICAL_DEBT_DEFINITIONS = {
    "OPEN_COMPOSITION": "published literal gloss contains the explicit word offen",
    "NON_SINGLE_GLOSS": "published literal gloss contains a slash or the word oder",
    "STRUCTURAL_META_AS_VALUE": "published literal gloss contains Eintrag, Bezug, a frame label or Qualitäts-/Wertfeld",
    "HARD_GENERIC_CARRIER": "published literal gloss contains the standalone head Gut, Material, Drogenmaterial, Ansatzmaterial, Drogenstoff, Ansatzstoff, Pulverstoff, Holzstoff or Rohstoff",
    "STATE_ONLY_NO_OBJECT": "published literal gloss starts hot/cold/dry/wet and contains none of the frozen object-head words",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signals(text: str) -> set[str]:
    return {name for name, regex, _ in COMPILED_RULES if regex.search(text)}


def practical_operation_labels(text: str) -> set[str]:
    return {lemma for lemma, regex in COMPILED_PRACTICAL_OPERATION_RULES if regex.search(text)}


def generic_carrier(text: str, found: set[str]) -> bool:
    if found & IDENTITY_SIGNALS:
        return False
    return bool(re.search(r"Gut/Material|\b(?:Gut|Material|Stoff|Substanz)\b|(?:Drogen|Ansatz|Rohstoff)(?:gut|material|stoff)\b", text, re.IGNORECASE))


def classify(gloss: str, found: set[str], action_licensed: bool) -> tuple[str, str, int, str]:
    has_identity = bool(found & IDENTITY_SIGNALS)
    has_action_wording = bool(found & ACTION_SIGNALS)
    has_role = "MATERIAL_ROLE" in found
    has_state = bool(found & STATE_SIGNALS)
    has_value = bool(found & VALUE_SIGNALS)
    if action_licensed and generic_carrier(gloss, found):
        return "B1_LICENSED_OPERATION_WITH_GENERIC_OBJECT", "MAJOR", 3, "OBJECT_IDENTITY_BINDING"
    if action_licensed and ("STRUCTURAL_META" in found or "REGISTER_CONNECTIVE" in found):
        return "B2_LICENSED_OPERATION_WITH_REGISTER_WRAPPER", "MAJOR", 3, "REGISTER_WRAPPER_DISPATCH"
    if action_licensed:
        return "A1_LICENSED_OPERATION", "NONE", 4, "NONE"
    if "UNRESOLVED_COMPONENT" in found:
        return "D1_UNRESOLVED_COMPONENT", "CRITICAL", 0, "BOUNDARY_OR_COMPONENT_RECONCILIATION"
    if "STRUCTURAL_META" in found or "REGISTER_CONNECTIVE" in found:
        return "D2_STRUCTURAL_OR_REGISTER_META", "CRITICAL", 0, "STRUCTURAL_TO_PRACTICAL_CARD"
    if generic_carrier(gloss, found):
        return "D3_GENERIC_CARRIER", "CRITICAL", 0, "PRODUCTIVE_CARRIER_COMPOSITION"
    if has_action_wording and not action_licensed:
        return "D4_UNLICENSED_LITERAL_ACTION", "CRITICAL", 0, "ACTION_SCOPE_REVIEW"
    if has_identity:
        return "A2_IDENTITY_BEARING_ENTITY", "NONE", 4, "NONE"
    if has_role:
        return "C1_FUNCTIONAL_MATERIAL_ROLE_ONLY", "MAJOR", 2, "INGREDIENT_IDENTITY_SEARCH"
    if has_state:
        return "C2_STATE_WITHOUT_OBJECT", "MAJOR", 1, "STATE_HOST_BINDING"
    if has_value:
        return "C3_VALUE_WITHOUT_AXIS_OR_OBJECT", "MAJOR", 1, "VALUE_AXIS_BINDING"
    return "D5_OPAQUE_OR_OTHER", "CRITICAL", 0, "EXACT_FAMILY_CONTEXT_CIRCUIT"


def strict_debt_categories(surface: str) -> list[str]:
    return sorted(category for category, surfaces in STRICT_DEBT_SURFACES.items() if surface in surfaces)


def mechanical_debt_flags(surface: str, gloss: str) -> list[str]:
    found: list[str] = []
    if re.search(r"\boffen\b", gloss, re.IGNORECASE):
        found.append("OPEN_COMPOSITION")
    if "/" in gloss or re.search(r"\boder\b", gloss, re.IGNORECASE):
        found.append("NON_SINGLE_GLOSS")
    if re.search(r"(?:Eintrag|Bezug|(?:Zubereitungs|Ansatz|qo)-?rahmen|Qualitäts-/Wertfeld)", gloss, re.IGNORECASE):
        found.append("STRUCTURAL_META_AS_VALUE")
    if re.search(r"\b(?:Gut|Material|Drogenmaterial|Ansatzmaterial|Drogenstoff|Ansatzstoff|Pulverstoff|Holzstoff|Rohstoff)\b", gloss, re.IGNORECASE):
        found.append("HARD_GENERIC_CARRIER")
    if re.search(r"^(?:heiß|kalt|trocken|feucht)(?:\b|-)", gloss, re.IGNORECASE) and not OBJECT_WORD.search(gloss):
        found.append("STATE_ONLY_NO_OBJECT")
    return sorted(found)


def split_field(raw: str, delimiter: str) -> list[str]:
    return raw.split(delimiter) if raw else []


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    v57 = read_tsv(V57_PATH)
    gdt683_result = json.loads(GDT683_RESULT_PATH.read_text(encoding="utf-8"))
    ol_lines = read_tsv(OL_LINE_PATH)
    gdt664_stems = read_tsv(GDT664_STEM_PATH)
    anchors = read_tsv(ANCHOR_PATH)
    anchor_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in anchors:
        anchor_by_locus[row["locus"]].append(row)

    assert len(v57) == 51
    assert sum(int(row["token_count"]) for row in v57) == 479
    assert all(not row["page"].lower().startswith("f84") for row in v57)
    assert gdt683_result["v57_reader"]["lines"] == 51
    assert gdt683_result["v57_reader"]["tokens"] == 479
    learned_ol_cards = [row for row in gdt664_stems if row["stem"] == "ol" and row["structural_role"] == "LEARNED_OL_BASE"]
    assert len(learned_ol_cards) == 1
    learned_ol_card = learned_ol_cards[0]
    assert learned_ol_card["practical_default_de"] == "Grundansatz"
    assert learned_ol_card["strength"] == "MEDIUM"

    low_card_by_pair: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for source_experiment, source_path in LOW_CONFIDENCE_CARD_PATHS:
        for source_card in read_tsv(source_path):
            confidence = source_card.get("confidence") or source_card.get("strength", "")
            if confidence not in {"LOW", "LOW_EXPLORATORY"} and "EXPLORATORY" not in confidence:
                continue
            source_card = dict(source_card)
            source_card["source_experiment"] = source_experiment
            source_card["source_path"] = str(source_path.relative_to(ROOT))
            source_card["normalized_confidence"] = confidence
            low_card_by_pair[(source_card["surface"], source_card["working_meaning_de"])].append(source_card)

    position_rows: list[dict[str, object]] = []
    line_rows: list[dict[str, object]] = []
    card_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    primary_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()
    extra_operation_pairs = 0

    for line in v57:
        tokens = line["zl3b_line"].split()
        literals = split_field(line["literal_token_glosses_de"], " | ")
        aligned = line["aligned_line_de"].rstrip(".").split(" · ")
        if not (len(tokens) == len(literals) == len(aligned) == int(line["token_count"])):
            raise RuntimeError(f"V57 alignment mismatch at {line['locus']}")
        action_ordinals = set() if line["action_ordinals"] == "NONE" else {int(value) for value in line["action_ordinals"].split("|")}
        licensed_operation_signals: set[str] = set()
        line_class_counts: Counter[str] = Counter()
        line_severity_counts: Counter[str] = Counter()
        line_identity_positions = 0
        line_specificity_open_positions = 0
        line_strict_debt_positions = 0
        line_specificity = 0
        for ordinal, (surface, literal, aligned_chunk) in enumerate(zip(tokens, literals, aligned), 1):
            literal_signals = signals(literal)
            aligned_signals = signals(aligned_chunk)
            action_licensed = ordinal in action_ordinals
            if action_licensed:
                licensed_operation_signals.update(literal_signals & ACTION_SIGNALS)
            primary_class, severity, score, repair_route = classify(literal, literal_signals, action_licensed)
            strict_categories = strict_debt_categories(surface)
            mechanical_flags = mechanical_debt_flags(surface, literal)
            low_confidence_cards = low_card_by_pair.get((surface, literal), [])
            identity = sorted(literal_signals & IDENTITY_SIGNALS)
            actions = sorted(literal_signals & ACTION_SIGNALS)
            lost_to_aligned = sorted(
                signal for signal in literal_signals - aligned_signals
                if signal in IDENTITY_SIGNALS | STATE_SIGNALS | VALUE_SIGNALS | {"UNRESOLVED_COMPONENT", "STRUCTURAL_META", "REGISTER_CONNECTIVE"}
            )
            specificity_open = severity != "NONE"
            strict_debt = bool(strict_categories)
            anchor_ids = [
                anchor["anchor_id"] for anchor in anchor_by_locus.get(line["locus"], [])
                if int(anchor["start_ordinal"]) <= ordinal <= int(anchor["end_ordinal"])
            ]
            row: dict[str, object] = {
                "page": line["page"], "locus": line["locus"], "section": line["section"],
                "language": line["language"], "hand": line["hand"], "line_mode": line["line_mode"],
                "ordinal": ordinal, "surface": surface, "literal_gloss_de": literal,
                "aligned_chunk_de": aligned_chunk, "action_licensed": int(action_licensed),
                "signals": "|".join(sorted(literal_signals)) or "NONE",
                "identity_signals": "|".join(identity) or "NONE",
                "action_signals": "|".join(actions) or "NONE",
                "lost_signals_literal_to_aligned": "|".join(lost_to_aligned) or "NONE",
                "primary_class": primary_class, "debt_severity": severity,
                "specificity_score": score, "specificity_open": int(specificity_open),
                "strict_card_debt": int(strict_debt),
                "strict_debt_categories": "|".join(strict_categories) or "NONE",
                "mechanical_debt": int(bool(mechanical_flags)),
                "mechanical_debt_flags": "|".join(mechanical_flags) or "NONE",
                "low_or_exploratory_card": int(bool(low_confidence_cards)),
                "low_confidence_sources": "|".join(sorted({card["source_experiment"] for card in low_confidence_cards})) or "NONE",
                "low_confidence_labels": "|".join(sorted({card["normalized_confidence"] for card in low_confidence_cards})) or "NONE",
                "repair_route": repair_route, "anchor_drift_ids": "|".join(anchor_ids) or "NONE",
                "practical_translation_de": line["practical_translation_de"],
            }
            position_rows.append(row)
            card_groups[(surface, literal)].append(row)
            primary_counts[primary_class] += 1
            severity_counts[severity] += 1
            line_class_counts[primary_class] += 1
            line_severity_counts[severity] += 1
            line_identity_positions += int(bool(identity))
            line_specificity_open_positions += int(specificity_open)
            line_strict_debt_positions += int(strict_debt)
            line_specificity += score

        licensed_operation_text = " ".join(literals[ordinal - 1] for ordinal in sorted(action_ordinals))
        licensed_practical_operations = practical_operation_labels(licensed_operation_text)
        practical_operations = practical_operation_labels(line["practical_translation_de"])
        extra_operations = sorted(practical_operations - licensed_practical_operations)
        extra_operation_pairs += len(extra_operations)
        line_rows.append({
            "page": line["page"], "locus": line["locus"], "section": line["section"],
            "language": line["language"], "hand": line["hand"], "line_mode": line["line_mode"],
            "token_count": len(tokens), "licensed_action_positions": len(action_ordinals),
            "identity_positions": line_identity_positions,
            "specificity_open_positions": line_specificity_open_positions,
            "strict_card_debt_positions": line_strict_debt_positions,
            "critical_positions": line_severity_counts["CRITICAL"], "major_positions": line_severity_counts["MAJOR"],
            "specificity_points": line_specificity,
            "licensed_operation_signals": "|".join(sorted(licensed_operation_signals)) or "NONE",
            "licensed_practical_operation_labels": "|".join(sorted(licensed_practical_operations)) or "NONE",
            "practical_operation_labels": "|".join(sorted(practical_operations)) or "NONE",
            "extra_practical_operation_labels": "|".join(extra_operations) or "NONE",
            "extra_practical_operation_count": len(extra_operations),
            "anchor_drift_count": len(anchor_by_locus.get(line["locus"], [])),
            "class_counts": "|".join(f"{key}:{value}" for key, value in sorted(line_class_counts.items())),
            "practical_translation_de": line["practical_translation_de"],
        })

    assert len(position_rows) == 479
    assert sum(int(row["action_licensed"]) for row in position_rows) == 86
    assert sum(primary_counts.values()) == 479

    severity_weight = {"CRITICAL": 3, "MAJOR": 2, "NONE": 0}
    card_rows: list[dict[str, object]] = []
    for (surface, gloss), members in card_groups.items():
        classes = Counter(str(row["primary_class"]) for row in members)
        severities = Counter(str(row["debt_severity"]) for row in members)
        maximum_severity = max(severities, key=lambda value: severity_weight[value])
        strict_categories = sorted({
            category for row in members for category in str(row["strict_debt_categories"]).split("|") if category != "NONE"
        })
        strict_severity = (
            "CRITICAL" if any(category in STRICT_CRITICAL for category in strict_categories)
            else "MAJOR" if strict_categories else "NONE"
        )
        strict_positions = sum(int(row["strict_card_debt"]) for row in members)
        anchor_positions = sum(row["anchor_drift_ids"] != "NONE" for row in members)
        card_rows.append({
            "surface": surface, "literal_gloss_de": gloss, "positions": len(members),
            "loci": len({str(row["locus"]) for row in members}), "pages": len({str(row["page"]) for row in members}),
            "action_licensed_positions": sum(int(row["action_licensed"]) for row in members),
            "specificity_open_positions": sum(int(row["specificity_open"]) for row in members),
            "strict_card_debt_positions": strict_positions,
            "strict_debt_categories": "|".join(strict_categories) or "NONE",
            "maximum_severity": maximum_severity,
            "strict_severity": strict_severity,
            "anchor_drift_positions": anchor_positions,
            "priority_score": severity_weight[strict_severity] * strict_positions + 4 * anchor_positions,
            "primary_classes": "|".join(f"{key}:{value}" for key, value in sorted(classes.items())),
            "identity_signals": "|".join(sorted({signal for row in members for signal in str(row["identity_signals"]).split("|") if signal != "NONE"})) or "NONE",
            "repair_routes": "|".join(sorted({str(row["repair_route"]) for row in members if row["repair_route"] != "NONE"})) or "NONE",
            "sample_keys": "|".join(f"{row['locus']}#{row['ordinal']}" for row in members[:8]),
        })
    card_rows.sort(key=lambda row: (-int(row["priority_score"]), -int(row["positions"]), str(row["surface"]), str(row["literal_gloss_de"])))
    for rank, row in enumerate(card_rows, 1):
        row["priority_rank"] = rank

    specificity_rows = [row for row in position_rows if int(row["specificity_open"])]
    debt_rows = [row for row in position_rows if int(row["strict_card_debt"])]
    mechanical_debt_rows = [row for row in position_rows if int(row["mechanical_debt"])]
    low_confidence_rows = [row for row in position_rows if int(row["low_or_exploratory_card"])]
    v57_by_locus = {row["locus"]: row for row in v57}
    provisional_watch_rows: list[dict[str, object]] = []
    for row in position_rows:
        if row["surface"] != "ol" or row["literal_gloss_de"] != learned_ol_card["practical_default_de"]:
            continue
        source_line = v57_by_locus[str(row["locus"])]
        provisional_watch_rows.append({
            "page": row["page"], "locus": row["locus"], "ordinal": row["ordinal"],
            "surface": row["surface"], "working_gloss_de": row["literal_gloss_de"],
            "primary_class": row["primary_class"], "specificity_open": row["specificity_open"],
            "source_experiment": "GDT664", "source_role": learned_ol_card["structural_role"],
            "source_strength": learned_ol_card["strength"], "source_scope": learned_ol_card["scope"],
            "v57_dispatch": source_line["v57_ol_decision"], "reader_support": source_line["v57_reader_support"],
            "watch_reason": "learned whole-word preparation role without independently identified substance or carrier liquid",
            "strict_debt_inclusion": "NO__BROAD_SPECIFICITY_AND_CONFIDENCE_WATCH_ONLY",
            "decision": "KEEP_REPLACEABLE_WORKING_CARD__DO_NOT_CALL_CONFIRMED_LEXEME",
        })
    assert len(provisional_watch_rows) == 5
    assert all(int(row["specificity_open"]) == 1 for row in provisional_watch_rows)
    assert len(mechanical_debt_rows) == 172
    assert len(low_confidence_rows) == 30
    assert len({(row["surface"], row["literal_gloss_de"]) for row in low_confidence_rows}) == 28
    class_summary_rows: list[dict[str, object]] = []
    for primary_class, count in sorted(primary_counts.items()):
        members = [row for row in position_rows if row["primary_class"] == primary_class]
        class_summary_rows.append({
            "primary_class": primary_class, "positions": count,
            "unique_surfaces": len({str(row["surface"]) for row in members}),
            "loci": len({str(row["locus"]) for row in members}),
            "debt_severity": members[0]["debt_severity"],
            "mean_specificity": f"{sum(int(row['specificity_score']) for row in members) / len(members):.3f}",
            "top_surfaces": "|".join(surface for surface, _ in Counter(str(row["surface"]) for row in members).most_common(12)),
            "repair_routes": "|".join(sorted({str(row["repair_route"]) for row in members if row["repair_route"] != "NONE"})) or "NONE",
        })

    strict_category_rows: list[dict[str, object]] = []
    for category, surfaces in STRICT_DEBT_SURFACES.items():
        members = [row for row in position_rows if str(row["surface"]) in surfaces]
        strict_category_rows.append({
            "strict_debt_category": category, "positions": len(members),
            "unique_surfaces": len({str(row["surface"]) for row in members}),
            "loci": len({str(row["locus"]) for row in members}),
            "severity": "CRITICAL" if category in STRICT_CRITICAL else "MAJOR",
            "surfaces": "|".join(surface for surface, _ in Counter(str(row["surface"]) for row in members).most_common()),
            "next_route": {
                "GENERIC_CARRIER": "PRODUCTIVE_CARRIER_COMPOSITION",
                "VALUE_DIMENSION_OPEN": "VALUE_AXIS_BINDING",
                "UNRESOLVED_BINDING": "BOUNDARY_OR_COMPONENT_RECONCILIATION",
                "STRUCTURAL_META_CARD": "STRUCTURAL_CHANNEL_DISPATCH",
                "OPEN_TAXONOMY_OR_MATERIAL_ALTERNATIVE": "EXACT_CARRIER_CENSUS",
                "GENERIC_DRUG_HEAD": "ACTION_OBJECT_HEAD_BINDING",
                "RAW_CLASS_WITHOUT_IDENTITY": "INGREDIENT_IDENTITY_SEARCH",
                "OPAQUE_FORM_CODE": "FORM_AXIS_CALIBRATION",
                "QUANTITY_OR_UNIT_WITHOUT_HEAD": "LOCAL_HEAD_SCOPE_BINDING",
            }[category],
        })
    assert len(debt_rows) == 139

    mechanical_summary_rows: list[dict[str, object]] = []
    mechanical_expected = {
        "OPEN_COMPOSITION": 20,
        "NON_SINGLE_GLOSS": 44,
        "STRUCTURAL_META_AS_VALUE": 18,
        "HARD_GENERIC_CARRIER": 47,
        "STATE_ONLY_NO_OBJECT": 65,
    }
    for debt_class, expected in mechanical_expected.items():
        members = [row for row in position_rows if debt_class in str(row["mechanical_debt_flags"]).split("|")]
        assert len(members) == expected
        mechanical_summary_rows.append({
            "mechanical_debt_class": debt_class,
            "positions": len(members),
            "unique_surfaces": len({str(row["surface"]) for row in members}),
            "loci": len({str(row["locus"]) for row in members}),
            "selector_definition": MECHANICAL_DEBT_DEFINITIONS[debt_class],
            "surfaces": "|".join(surface for surface, _ in Counter(str(row["surface"]) for row in members).most_common()),
        })

    debt_crosswalk_rows: list[dict[str, object]] = []
    for strict in (0, 1):
        for broad in (0, 1):
            for mechanical in (0, 1):
                members = [
                    row for row in position_rows
                    if int(row["strict_card_debt"]) == strict
                    and int(row["specificity_open"]) == broad
                    and int(row["mechanical_debt"]) == mechanical
                ]
                debt_crosswalk_rows.append({
                    "strict_curated_queue": strict,
                    "broad_specificity_open": broad,
                    "mechanical_visible_alarm": mechanical,
                    "positions": len(members),
                    "unique_surfaces": len({str(row["surface"]) for row in members}),
                    "sample_keys": "|".join(f"{row['locus']}#{row['ordinal']}" for row in members[:12]) or "NONE",
                })

    companion_line = next(row for row in ol_lines if row["locus"] == "f111v.18")
    companion_tokens = companion_line["zl3b_line"].split()
    companion_glosses = companion_line["token_debt_dispatch_de"].split(" | ")
    assert companion_tokens[10] == "l"
    assert "Eigenschafts-/Zustands-/Materialträger" in companion_glosses[10]
    companion_rows = [{
        "scope": "OUTSIDE_V57_GLOBAL_COMPANION", "page": "f111v", "locus": "f111v.18",
        "ordinal": 11, "surface": "l", "working_gloss_de": companion_glosses[10],
        "debt_class": "STALE_STRUCTURAL_META_GLOSS", "in_v57": 0,
        "reader_note": "ZL3b/IT2a/RF1b preserve free l at this position; GDT663's weight rival must remain visible",
        "next_route": "FREE_L_CONTEXT_CIRCUIT_SEPARATE_FROM_V57",
    }]

    rule_rows = [
        {"signal": name, "regex": pattern, "description": description, "channel": "ACTION" if name.startswith("ACT_") else "SEMANTIC"}
        for name, pattern, description in [*SIGNAL_RULES, *ACTION_RULES]
    ]

    fields = list(position_rows[0].keys())
    write_tsv(output_dir / "V57_479_POSITION_INFORMATION_AUDIT.tsv", position_rows, fields)
    write_tsv(output_dir / "V57_SEMANTIC_DEBT_POSITIONS.tsv", debt_rows, fields)
    write_tsv(output_dir / "V57_SPECIFICITY_OPEN_POSITIONS.tsv", specificity_rows, fields)
    write_tsv(output_dir / "V57_MECHANICAL_SEMANTIC_DEBT_POSITIONS.tsv", mechanical_debt_rows, fields)
    write_tsv(output_dir / "V57_LOW_CONFIDENCE_CARD_POSITIONS.tsv", low_confidence_rows, fields)
    write_tsv(output_dir / "V57_CARD_INFORMATION_INVENTORY.tsv", card_rows, list(card_rows[0].keys()))
    write_tsv(output_dir / "V57_51_LINE_INFORMATION_SUMMARY.tsv", line_rows, list(line_rows[0].keys()))
    write_tsv(output_dir / "SEMANTIC_CLASS_SUMMARY.tsv", class_summary_rows, list(class_summary_rows[0].keys()))
    write_tsv(output_dir / "STRICT_DEBT_CATEGORY_SUMMARY.tsv", strict_category_rows, list(strict_category_rows[0].keys()))
    write_tsv(output_dir / "MECHANICAL_DEBT_CLASS_SUMMARY.tsv", mechanical_summary_rows, list(mechanical_summary_rows[0].keys()))
    write_tsv(output_dir / "DEBT_LAYER_CROSSWALK.tsv", debt_crosswalk_rows, list(debt_crosswalk_rows[0].keys()))
    write_tsv(output_dir / "SEMANTIC_SIGNAL_RULES.tsv", rule_rows, list(rule_rows[0].keys()))
    practical_rule_rows = [
        {"operation_lemma": lemma, "regex": pattern, "use": "PRACTICAL_PROSE_MINUS_DECLARED_ACTION_LITERAL_GLOSSES"}
        for lemma, pattern in PRACTICAL_OPERATION_RULES
    ]
    write_tsv(output_dir / "PRACTICAL_OPERATION_RULES.tsv", practical_rule_rows, list(practical_rule_rows[0].keys()))
    write_tsv(output_dir / "ANCHOR_LAYER_DRIFTS.tsv", anchors, list(anchors[0].keys()))
    write_tsv(output_dir / "OUTSIDE_V57_COMPANION_DEBTS.tsv", companion_rows, list(companion_rows[0].keys()))
    write_tsv(
        output_dir / "V57_PROVISIONAL_SEMANTIC_CONFIDENCE_WATCH.tsv",
        provisional_watch_rows,
        list(provisional_watch_rows[0].keys()),
    )

    carrier_counts = Counter(
        str(row["surface"]) for row in position_rows
        if row["surface"] in {"chol", "shol", "tol"}
    )
    top_debt_cards = [row for row in card_rows if int(row["strict_card_debt_positions"]) or int(row["anchor_drift_positions"])][:20]
    reader_doc = [
        "# GDT684 — V57 semantic debt priority reader",
        "",
        f"V57 remains formally complete at 479/479 positions. The strict repair queue contains {len(debt_rows)}/479 card positions; the broader information audit marks {len(specificity_rows)}/479 positions as identity-, object-, axis-, register- or resolution-open.",
        f"An independent five-selector literal audit flags {len(mechanical_debt_rows)}/479 positions. Across all three layers, {sum(int(row['strict_card_debt']) or int(row['specificity_open']) or int(row['mechanical_debt']) for row in position_rows)}/479 positions carry at least one debt signal and only {sum(not (int(row['strict_card_debt']) or int(row['specificity_open']) or int(row['mechanical_debt'])) for row in position_rows)}/479 carry none.",
        "",
        "## Disjoint position classes",
        "",
    ]
    for row in class_summary_rows:
        reader_doc.append(f"- `{row['primary_class']}`: {row['positions']} positions / {row['unique_surfaces']} surfaces; route `{row['repair_routes']}`.")
    reader_doc.extend([
        "",
        "## Highest-priority debt cards",
        "",
        "| rank | surface | positions | class | current gloss | route |",
        "|---:|---|---:|---|---|---|",
    ])
    for row in top_debt_cards:
        reader_doc.append(
            f"| {row['priority_rank']} | `{row['surface']}` | {row['strict_card_debt_positions']} | {row['primary_classes']} | {row['literal_gloss_de']} | `{row['repair_routes']}` |"
        )
    reader_doc.extend([
        "",
        "## Action-layer warning",
        "",
        f"The source ledger licenses 86 action positions. Practical prose adds {extra_operation_pairs} operation-label-by-line pairs on {sum(int(row['extra_practical_operation_count']) > 0 for row in line_rows)} lines that are absent from the licensed token-action glosses. These are audit targets, not automatically valid inferred syntax.",
        "",
        "## Provisional learned-base warning",
        "",
        "Five free V57 `ol` positions retain the GDT664 working card `Grundansatz`. GDT664 marks that learned whole-word card MEDIUM, not confirmed. All five already sit inside the broad specificity-open census and now appear in `V57_PROVISIONAL_SEMANTIC_CONFIDENCE_WATCH.tsv`; they do not enlarge the narrower 139-position renderer-repair queue.",
        "",
        "## Low-confidence card provenance",
        "",
        f"Exact surface-plus-current-gloss joins recover {len(low_confidence_rows)} V57 positions / {len({(row['surface'], row['literal_gloss_de']) for row in low_confidence_rows})} cards whose published source is LOW or EXPLORATORY. Ten of these positions had no signal in the strict, broad or mechanical layers, so adding confidence provenance leaves only {sum(not (int(row['strict_card_debt']) or int(row['specificity_open']) or int(row['mechanical_debt']) or int(row['low_or_exploratory_card'])) for row in position_rows)}/479 positions without a current debt or low-confidence flag.",
        "",
        "## Next repair family",
        "",
        f"The shortest productive repair is the state+OL carrier family: `chol` {carrier_counts['chol']}×, `shol` {carrier_counts['shol']}×, `tol` {carrier_counts['tol']}×. GDT683 supplies `ol = Grundansatz`; the next occurrence circuit must test whether CH/SH/T predict dry/wet/cold preparation cards at every admitted exact occurrence before rewriting V57.",
        "",
        "The free `l` on f111v.18 is not counted in V57. It is retained in `OUTSIDE_V57_COMPANION_DEBTS.tsv` as a separate global route.",
    ])
    (output_dir / "GDT684_SEMANTIC_DEBT_PRIORITY_READER.md").write_text("\n".join(reader_doc).rstrip() + "\n", encoding="utf-8")

    result: dict[str, object] = {
        "status": "PASS_479_POSITION_INFORMATION_CENSUS__FORMAL_COMPLETENESS_NOT_SEMANTIC_COMPLETENESS",
        "basis": {
            "v57_lines": 51, "v57_positions": 479, "unique_surfaces": len({row["surface"] for row in position_rows}),
            "unique_surface_gloss_cards": len(card_rows), "licensed_action_positions": 86,
            "new_pages_opened": 0, "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
        },
        "position_classes": dict(sorted(primary_counts.items())),
        "severity": dict(sorted(severity_counts.items())),
        "strict_card_debt_positions": len(debt_rows),
        "strict_debt_category_memberships": sum(int(row["positions"]) for row in strict_category_rows),
        "broad_specificity_open_positions": len(specificity_rows),
        "mechanical_visible_debt": {
            "union_positions": len(mechanical_debt_rows),
            "class_memberships": sum(row["positions"] for row in mechanical_summary_rows),
            "classes": {row["mechanical_debt_class"]: row["positions"] for row in mechanical_summary_rows},
        },
        "three_debt_layer_union_positions": sum(
            int(row["strict_card_debt"]) or int(row["specificity_open"]) or int(row["mechanical_debt"])
            for row in position_rows
        ),
        "four_layer_union_with_low_confidence_positions": sum(
            int(row["strict_card_debt"]) or int(row["specificity_open"]) or int(row["mechanical_debt"])
            or int(row["low_or_exploratory_card"])
            for row in position_rows
        ),
        "no_debt_or_low_confidence_signal_positions": sum(
            not (
                int(row["strict_card_debt"]) or int(row["specificity_open"])
                or int(row["mechanical_debt"]) or int(row["low_or_exploratory_card"])
            )
            for row in position_rows
        ),
        "provisional_semantic_confidence_watch_positions": len(provisional_watch_rows),
        "low_or_exploratory_card_positions": len(low_confidence_rows),
        "low_or_exploratory_surface_gloss_cards": len({(row["surface"], row["literal_gloss_de"]) for row in low_confidence_rows}),
        "strict_semantic_debt_with_provisional_ol_positions": len(debt_rows) + len(provisional_watch_rows),
        "mechanical_plus_provisional_ol_union_positions": len(mechanical_debt_rows) + len(provisional_watch_rows),
        "action_layer": {
            "lines_with_extra_practical_operations": sum(int(row["extra_practical_operation_count"]) > 0 for row in line_rows),
            "extra_practical_operation_label_line_pairs": extra_operation_pairs,
            "anchor_layer_drifts": len(anchors),
        },
        "next_repair_family": {
            "family": "CH_SH_T_PLUS_OL_STATE_CARRIER",
            "v57_positions": dict(sorted(carrier_counts.items())),
            "provisional_predictions": {"chol": "Trockenansatz", "shol": "Feuchtansatz", "tol": "Kaltansatz"},
            "status": "PREDICTION_TO_TEST__NOT_YET_EXPORTED",
        },
        "outside_v57_companion_debts": 1,
        "claim_ceiling": (
            "Every one of V57's 479 positions is classified by information content and repair route. A narrow exact card queue contains 139 positions, while the broader specificity audit keeps every identity-less role, objectless state and unbound value visible. "
            "An independent literal five-selector audit flags 172 overlapping positions and prevents open, multi-valued, structural, generic-carrier and objectless-state cards from passing merely because they sound fluent. "
            "Thirty positions join exactly to 28 source cards explicitly marked LOW or EXPLORATORY; this provenance remains visible rather than being promoted by fluent prose. "
            "Formal assignment is rejected as a proxy for semantic completeness: structural labels, unresolved components, generic heads and prose operations remain explicit debt. "
            "The census does not itself replace any V57 card. CH/SH/T+OL dry/wet/cold preparation meanings are forward predictions for the next occurrence circuit, not accepted plaintext. "
            "The five free V57 ol positions retain the MEDIUM learned Grundansatz working card but remain explicitly open under the broad specificity census and a separate semantic-confidence watch. "
            "The f111v.18 free-l debt is explicitly outside V57 and is not added to the 479 denominator. No language, phonetics, plant, disease, patient, cure, carrier liquid, historical codebook or new page is identified."
        ),
        "files": {},
    }
    artifact_names = [
        "V57_479_POSITION_INFORMATION_AUDIT.tsv", "V57_SEMANTIC_DEBT_POSITIONS.tsv", "V57_SPECIFICITY_OPEN_POSITIONS.tsv",
        "V57_MECHANICAL_SEMANTIC_DEBT_POSITIONS.tsv", "MECHANICAL_DEBT_CLASS_SUMMARY.tsv", "DEBT_LAYER_CROSSWALK.tsv",
        "V57_LOW_CONFIDENCE_CARD_POSITIONS.tsv", "PRACTICAL_OPERATION_RULES.tsv",
        "V57_CARD_INFORMATION_INVENTORY.tsv", "V57_51_LINE_INFORMATION_SUMMARY.tsv",
        "SEMANTIC_CLASS_SUMMARY.tsv", "STRICT_DEBT_CATEGORY_SUMMARY.tsv", "SEMANTIC_SIGNAL_RULES.tsv", "ANCHOR_LAYER_DRIFTS.tsv",
        "OUTSIDE_V57_COMPANION_DEBTS.tsv", "GDT684_SEMANTIC_DEBT_PRIORITY_READER.md",
        "V57_PROVISIONAL_SEMANTIC_CONFIDENCE_WATCH.tsv",
    ]
    result["files"] = {name: sha256(output_dir / name) for name in artifact_names}
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    build(ART)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
