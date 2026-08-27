#!/usr/bin/env python3
"""Admit the second random four-page batch into the working edition.

Exact GDT405 recipes, new visible compositions, and owner-local name/sign
cores stay separate.  The selected-page source is materialised only through
``vmanus-exp query-tsv``.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission"
ART = BASE / "artifacts"
ZL3B = ROOT / "transcription/voynich_zl3b_lines.tsv"
G404_RUN = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/src/run.py"
G405 = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G513 = ROOT / "experiments/yolo/gdt513_remaining_local_group_semantic_census/artifacts"
G514 = ROOT / "experiments/yolo/gdt514_second_random_four_page_selection_owner_map/artifacts"
PASS1026_RUN = (
    ROOT
    / "experiments/yolo/sidequest_semantic_visible_allograph_resegmentation_one_thousand_twenty_sixth"
    / "build_pass1026.py"
)

SELECTED_PAGES = ("f31r", "f66r", "f20v", "f4r")
SOURCE_COLUMNS = (
    "page,page_order,locus,line_number,code,relation,kind,subtype,section,"
    "language,hand,quire,folio_type,paragraph_start,paragraph_end,token_count,eva_clean"
)
STATUS = "PASS_FOUR_PAGES_ADMITTED_WITH_TWO_LOCAL_X_CORES"
GUARD = "COMPLETE_WORKING_DEFAULTS_ONLY__NO_CONFIRMED_LEXEME_OR_PLAINTEXT"

LOCK_IN = G405 / "gdt405_426_locked_surface_dictionary.tsv"
RUNNING_IN = G407 / "gdt407_4576_running_event_edition.tsv"
LOCAL_IN = G407 / "gdt407_693_local_group_edition.tsv"
UNIFIED_IN = G407 / "gdt407_5269_unified_group_ledger.tsv"
PAGE26_IN = G407 / "gdt407_26_page_summary.tsv"
DICT_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
EXPECTATION_IN = G513 / "gdt513_5_new_page_expectations.tsv"
OWNER_IN = G514 / "gdt514_4_image_owner_map.tsv"

SOURCE_OUT = ART / "gdt515_122_guarded_source_lines.tsv"
EVENT_OUT = ART / "gdt515_597_complete_event_edition.tsv"
SURFACE_OUT = ART / "gdt515_377_surface_dictionary.tsv"
NOVEL_RUNNING_OUT = ART / "gdt515_169_running_absent_surface_audit.tsv"
NOVEL_ALL_OUT = ART / "gdt515_159_genuinely_new_surface_audit.tsv"
LABEL_OUT = ART / "gdt515_51_f66r_label_sign_edition.tsv"
STATEMENT_OUT = ART / "gdt515_prose_statement_edition.tsv"
ATTACHMENT_OUT = ART / "gdt515_factorized_attachments.tsv"
SENSITIVITY_OUT = ART / "gdt515_amber_close_sensitivity.tsv"
PAGE_OUT = ART / "gdt515_4_page_summary.tsv"
EXPECTATION_OUT = ART / "gdt515_5_expectation_scorecard.tsv"
RUNNING30_OUT = ART / "gdt515_5122_running_event_edition.tsv"
LOCAL30_OUT = ART / "gdt515_744_local_group_edition.tsv"
UNIFIED30_OUT = ART / "gdt515_5866_unified_group_ledger.tsv"
PAGE30_OUT = ART / "gdt515_30_page_summary.tsv"
READING_OUT = ART / "GDT515_FOUR_PAGE_COMPLETE_WORKING_READING.md"
RESULT_OUT = ART / "gdt515_result.json"

# Direct visible defaults for every selected surface absent from the old
# running deck.  Only the 46 current atoms and three explicit local tags occur.
MANUAL_NEW_RECIPE = {
    "aiicthy": "A_ADDR+LOCAL_CHAR_I+LOCAL_CHAR_I+CH+T+Y",
    "akar": "A_ADDR+K+AR",
    "alkey": "AL+K+E+Y",
    "axor": "A_ADDR+LOCAL_NAME_CORE_X+OR",
    "chady": "CH+A_ADDR+DY",
    "chap": "CH+A_ADDR+P",
    "chckhedy": "CH+CH+K+E+DY",
    "chcpheor": "CH+CH+P+E+OR",
    "chctho": "CH+CH+T+O",
    "cheda": "CHD+A_ADDR",
    "chedaiir": "CHD+IIN+R",
    "cheeo": "CH+EE+O",
    "chefchy": "CH+E+LOCAL_CHAR_F+CH+Y",
    "chekchy": "CH+K+CH+Y",
    "chekeey": "CH+K+EE+Y",
    "chekeody": "CH+K+E+O+DY",
    "chekey": "CH+K+E+Y",
    "cheod": "CH+E+O+D_ADDR",
    "chepakeo": "CH+E+P+A_ADDR+K+E+O",
    "chepos": "CH+E+P+O+S",
    "cheta": "CH+E+T+A_ADDR",
    "choekeey": "CH+O+E+K+EE+Y",
    "choiin": "CH+O+IIN",
    "cholpchd": "OL+P+CHD",
    "choraiin": "CH+OR+AIIN",
    "choraly": "CH+OR+AL+Y",
    "chory": "CH+OR+Y",
    "chpady": "CH+P+A_ADDR+DY",
    "chxar": "CH+LOCAL_NAME_CORE_X+AR",
    "ckhochy": "CH+K+O+CH+Y",
    "cphaiin": "CH+P+AIIN",
    "cpholdy": "CH+P+OL+DY",
    "cthdy": "CH+T+D_ADDR+Y",
    "cthom": "CH+T+O+M_LOCAL",
    "da": "DA",
    "daiir": "DA+IIN+R",
    "dairal": "D_ADDR+AIR+AL",
    "dairody": "D_ADDR+AIR+O+DY",
    "dairykodas": "D_ADDR+AIR+Y+K+O+D_ADDR+A_ADDR+S",
    "dalalshedy": "AL+AL+SH+E+DY",
    "dalcheeeky": "AL+CH+EEE+K+Y",
    "dalky": "AL+K+Y",
    "dalol": "AL+OL",
    "dard": "D_ADDR+AR+D_ADDR",
    "dcheey": "D_ADDR+CH+EE+Y",
    "dcheol": "D_ADDR+CH+E+O+L",
    "dkar": "D_ADDR+K+AR",
    "doiiin": "D_ADDR+O+IIN",
    "dolarshy": "D_ADDR+OL+AR+SH+Y",
    "dsholdaiir": "D_ADDR+SH+OL+D_ADDR+IIN+R",
    "dyky": "D_ADDR+Y+K+Y",
    "dytcheey": "D_ADDR+Y+T+CH+EE+Y",
    "faiis": "LOCAL_CHAR_F+IIN+S",
    "fchdar": "LOCAL_CHAR_F+CHD+AR",
    "fchedyr": "LOCAL_CHAR_F+CHD+Y+R",
    "folchol": "LOCAL_CHAR_F+OL+OL",
    "fshodchy": "LOCAL_CHAR_F+SH+O+D_ADDR+CH+Y",
    "kardy": "K+AR+DY",
    "kcheeky": "K+CH+EE+K+Y",
    "kcheody": "K+CH+E+O+Y",
    "kchody": "K+CH+O+D_ADDR+Y",
    "kechody": "K+E+CH+O+D_ADDR+Y",
    "keedey": "K+EE+D_ADDR+E+Y",
    "keeol": "K+EE+O+L",
    "keody": "K+E+O+D_ADDR+Y",
    "kodalchy": "K+O+D_ADDR+AL+CH+Y",
    "kodary": "K+O+D_ADDR+AR+Y",
    "kody": "K+O+DY",
    "ld": "L+D_ADDR",
    "lkeol": "L+K+E+OL",
    "lodaiin": "L+O+D_ADDR+AIIN",
    "lpchees": "L+P+CH+EE+S",
    "lsheody": "L+SH+E+O+D_ADDR+Y",
    "ltsholy": "L+T+SH+OL+Y",
    "odair": "O+D_ADDR+AIR",
    "ofaram": "O+LOCAL_CHAR_F+AR+AM_ADDR",
    "okalchedy": "OK+AL+CHD+Y",
    "okedals": "OK+AL+S",
    "okedam": "OK+E+D_ADDR+AM_ADDR",
    "okoy": "OK+O+Y",
    "okyd": "OK+Y+D_ADDR",
    "olsheor": "OL+SH+E+OR",
    "otalor": "OT+AL+OR",
    "otcheo": "OT+CH+E+O",
    "oteochey": "OT+E+O+CH+E+Y",
    "pchof": "P+CH+O+LOCAL_CHAR_F",
    "pdaiin": "P+AIIN",
    "pofochey": "P+O+LOCAL_CHAR_F+O+CH+E+Y",
    "psheody": "P+SH+E+O+D_ADDR+Y",
    "pydaiin": "P+Y+D_ADDR+AIIN",
    "qef": "E+LOCAL_CHAR_F",
    "qocthedy": "CARRIER_Q+O+CH+T+E+Y",
    "qoekedy": "CARRIER_Q+O+E+K+E+DY",
    "qokaiir": "OK+IIN+R",
    "qokchey": "OK+CH+E+Y",
    "qokee": "OK+EE",
    "qokeedar": "OK+EE+D_ADDR+AR",
    "qokees": "OK+EE+S",
    "qokshd": "OK+SH+D_ADDR",
    "qopaiin": "CARRIER_Q+O+P+AIIN",
    "qotchoiin": "OT+CH+O+IIN",
    "qotedal": "OT+E+AL",
    "qoteeod": "OT+EE+O+D_ADDR",
    "qoteoly": "OT+E+OL+Y",
    "rotaiin": "R+OT+AIIN",
    "saiir": "S+IIN+R",
    "saiis": "S+IIN+S",
    "shain": "SH+AIN",
    "shckhar": "SH+CH+K+AR",
    "shckheody": "SH+CH+K+E+O+DY",
    "shd": "SH+D_ADDR",
    "shddy": "SH+D_ADDR+DY",
    "shedshey": "SH+E+D_ADDR+SH+E+Y",
    "shee": "SH+EE",
    "sheeody": "SH+EE+O+D_ADDR+Y",
    "shekair": "SH+E+K+AIR",
    "shekaly": "SH+E+K+AL+Y",
    "shekeefy": "SH+E+K+EE+LOCAL_CHAR_F+Y",
    "shekeey": "SH+E+K+EE+Y",
    "shekey": "SH+E+K+E+Y",
    "shekol": "SH+E+K+OL",
    "sheocthy": "SH+E+O+CH+T+Y",
    "sheod": "SH+E+O+D_ADDR",
    "sheodaiin": "SH+E+O+D_ADDR+AIIN",
    "sheoy": "SH+E+O+Y",
    "shofol": "SH+O+LOCAL_CHAR_F+OL",
    "shokaiir": "SH+OK+IIN+R",
    "sholfordaiin": "SH+OL+LOCAL_CHAR_F+OR+D_ADDR+AIIN",
    "shso": "SH+S+O",
    "shtchy": "SH+T+CH+Y",
    "shyshol": "SH+Y+SH+OL",
    "shytchy": "SH+Y+T+CH+Y",
    "soaiin": "S+O+AIIN",
    "sos": "S+O+S",
    "tcheo": "T+CH+E+O",
    "tocpheey": "T+O+CH+P+EE+Y",
    "todeeey": "T+O+D_ADDR+EEE+Y",
    "tolchedy": "T+OL+CHD+DY",
    "tolshy": "T+OL+SH+Y",
    "tosheo": "T+O+SH+E+O",
    "tshokeody": "T+SH+OK+E+O+D_ADDR+Y",
    "tydy": "T+Y+DY",
    "yches": "Y+CH+E+S",
    "ykady": "Y+K+A_ADDR+DY",
    "ykeedar": "Y+K+EE+D_ADDR+AR",
    "ykeeody": "Y+K+EE+O+DY",
    "ykesho": "Y+K+E+SH+O",
    "ykoiin": "Y+K+O+IIN",
    "ykshedy": "Y+K+SH+E+DY",
    "ypches": "Y+P+CH+E+S",
    "yshedair": "Y+SH+E+D_ADDR+AIR",
    "ysheeod": "Y+SH+EE+O+D_ADDR",
    "ytarody": "Y+T+AR+O+DY",
    "ytoy": "Y+T+O+Y",
    "rary": "R+AR+Y",
    "rals": "R+AL+S",
    "ykeol": "Y+K+E+OL",
    "saly": "S+AL+Y",
    "salf": "S+AL+LOCAL_CHAR_F",
    "fary": "LOCAL_CHAR_F+AR+Y",
    "qotesy": "OT+E+S+Y",
    "doly": "D_ADDR+OL+Y",
    "qolsa": "OL+S+A_ADDR",
    "raral": "R+AR+AL",
    "f": "LOCAL_CHAR_F",
    "x": "LOCAL_SIGN_X",
    "c": "LOCAL_SIGN_C",
    "p": "P",
    "ykees": "Y+K+EE+S",
}

LOCAL_OPAQUE_ATOMS = {
    "LOCAL_NAME_CORE_X": "LOKALER NAMENSKERN X",
    "LOCAL_SIGN_X": "LOKALE X-KENNMARKENFORM",
    "LOCAL_SIGN_C": "LOKALE C-KENNMARKENFORM",
}
AMBIGUOUS_MANUAL = {"axor", "chxar", "cthdy", "okedam", "qocthedy", "ykady"}
ACTION_HEADS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ORDER_CONTROLS = {"OL", "OT"}
RELATIONS = {"AL", "AR", "L", "AIR"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: list[dict[str, object]], fields: list[str] | None = None,
) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def join_sorted(values) -> str:
    cleaned = sorted(
        {str(value) for value in values if value not in {None, "", "NONE"}},
    )
    return "|".join(cleaned) if cleaned else "NONE"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_source_rows() -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(ZL3B),
        "--selector", "page",
    ]
    for page in SELECTED_PAGES:
        command.extend(("--allow", page))
    command.extend(("--forbid-prefix", "f84", "--columns", SOURCE_COLUMNS))
    result = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=True,
    )
    lines = result.stdout.splitlines()
    stat_lines = [
        line
        for line in (*lines, *result.stderr.splitlines())
        if line.startswith("GUARD_STATS ")
    ]
    if len(stat_lines) != 1:
        raise RuntimeError("guarded query did not yield one GUARD_STATS record")
    stats = json.loads(stat_lines[0].removeprefix("GUARD_STATS "))
    data = [line for line in lines if not line.startswith("GUARD_STATS ")]
    rows = list(
        csv.DictReader(io.StringIO("\n".join(data) + "\n"), delimiter="\t"),
    )
    return rows, stats


def assign_prose_blocks(source_rows: list[dict[str, str]]) -> dict[str, str]:
    counters: Counter[str] = Counter()
    current: dict[str, str] = {}
    result: dict[str, str] = {}
    for row in source_rows:
        if row["kind"] != "P":
            continue
        page = row["page"]
        if page not in current or row["paragraph_start"] == "1":
            counters[page] += 1
            current[page] = f"{page.upper()}_PROSE_{counters[page]:02d}"
        result[row["locus"]] = current[page]
    return result


def owner_for(
    row: dict[str, str], prose_block: str,
) -> tuple[str, str, str]:
    page = row["page"]
    if row["kind"] == "L":
        if row["subtype"] == "x":
            return (
                "F66R_LATE_BOTTOM_ADDITION",
                "separater spaeter unterer Nachtrag mit kleiner Zeichnung",
                "SEPARATE_LATE_ADDITION",
            )
        if int(row["line_number"]) <= 15:
            return (
                "F66R_MARGIN_LABEL_ZONE",
                "sichtbare Randkennungszone von f66r",
                "MARGINAL_LABEL",
            )
        return (
            "F66R_MARGIN_SIGN_ZONE",
            "sichtbare Folge einzelner Randzeichen von f66r",
            "MARGINAL_SIGN",
        )
    if page in {"f4r", "f20v", "f31r"}:
        return (
            f"{page.upper()}_WHOLE_PLANT",
            f"abgebildete Ganzpflanze auf {page}",
            prose_block,
        )
    if page == "f66r":
        number = int(prose_block.rsplit("_", 1)[1])
        return (
            f"F66R_TEXT_BLOCK_{number:02d}",
            f"sichtbarer Prosablock {number} auf f66r ohne Gegenstandsbesitzer",
            prose_block,
        )
    raise RuntimeError(f"owner not defined for {page}")


def atom_trace(atom: str, dictionary: dict[str, dict[str, str]]) -> str:
    if atom in LOCAL_OPAQUE_ATOMS:
        return f"[{atom}:LOKALSTRUKTUR={LOCAL_OPAQUE_ATOMS[atom]}]"
    entry = dictionary[atom]
    value = entry["working_value_de"]
    if entry["semantic_layer"] == "PORTABLE_BROAD_WORKING_CORE":
        return value
    if entry["factor_family"] in {"GRADE", "FORMAL_CONTROL"}:
        return f"[{atom}:STEUERUNG={value}]"
    return f"[{atom}:LOKALSTRUKTUR={value}]"


def literal(recipe: str, dictionary: dict[str, dict[str, str]]) -> str:
    return " · ".join(
        atom_trace(atom, dictionary) for atom in recipe.split("+")
    )


def label_trace(recipe: str, dictionary: dict[str, dict[str, str]]) -> str:
    values = []
    for atom in recipe.split("+"):
        if atom in LOCAL_OPAQUE_ATOMS:
            values.append(atom_trace(atom, dictionary))
        else:
            values.append(
                f"[{atom}:FORMSPUR={dictionary[atom]['working_value_de']}]",
            )
    return " · ".join(values)


def record_role(
    atoms: list[str], kind: str, subtype: str, line_number: int,
) -> str:
    if kind == "L":
        if subtype == "x":
            return "LATE_ADDITION_CARD"
        return "MARGINAL_LABEL_CARD" if line_number <= 15 else "MARGINAL_SIGN_CARD"
    aset = set(atoms)
    if aset & set(LOCAL_OPAQUE_ATOMS):
        return "LOCAL_NAME_WITH_FUNCTION_SHELL_CARD"
    if aset & ACTION_HEADS:
        return "ORDERED_INSTRUCTION_CARD"
    if aset & ORDER_CONTROLS:
        return "ITINERARY_OR_ADDRESS_CARD"
    if aset & (RELATIONS | ARGUMENTS):
        return "COORDINATE_OR_CATALOGUE_CARD"
    return "LOCAL_CLASS_OR_NAME_CARD"


def default_reading(
    role: str,
    owner_de: str,
    surface: str,
    recipe: str,
    dictionary: dict[str, dict[str, str]],
) -> str:
    del surface
    if role == "MARGINAL_LABEL_CARD":
        return f"RANDKENNUNG BEI {owner_de}: {label_trace(recipe, dictionary)}"
    if role == "MARGINAL_SIGN_CARD":
        return (
            f"LOKALE RANDKENNMARKENKARTE BEI {owner_de}: "
            f"{label_trace(recipe, dictionary)}"
        )
    if role == "LATE_ADDITION_CARD":
        return (
            f"KARTE IM GETRENNTEN SPAETEN NACHTRAG BEI {owner_de}: "
            f"{label_trace(recipe, dictionary)}"
        )
    prefix = {
        "ORDERED_INSTRUCTION_CARD": "ANWEISUNG",
        "ITINERARY_OR_ADDRESS_CARD": "ADRESSE/FORTSETZUNG",
        "COORDINATE_OR_CATALOGUE_CARD": "KOORDINATE/KATALOGEINTRAG",
        "LOCAL_CLASS_OR_NAME_CARD": "LOKALE KENNUNG",
        "LOCAL_NAME_WITH_FUNCTION_SHELL_CARD": (
            "LOKALER NAMENSKERN MIT FUNKTIONSRAHMEN"
        ),
    }[role]
    return f"{prefix} BEI {owner_de}: {literal(recipe, dictionary)}"


def current_statement_fields(
    statement: dict[str, object],
    events: list[dict[str, object]],
    dictionary: dict[str, dict[str, str]],
) -> None:
    atoms = [
        atom
        for event in events
        for atom in str(event["visible_recipe"]).split("+")
    ]
    actions = [atom for atom in atoms if atom in ACTION_HEADS]
    arguments = [atom for atom in atoms if atom in ARGUMENTS]
    relations = [atom for atom in atoms if atom in RELATIONS]
    grades = [atom for atom in atoms if atom in {"E", "EE", "EEE"}]
    statement["literal_core_sequence_de"] = " | ".join(
        str(event["literal_core_reading_de"]) for event in events
    )
    statement["action_chain_de"] = (
        " > ".join(dictionary[atom]["working_value_de"] for atom in actions)
        or "BESITZERGETRAGEN"
    )
    statement["argument_inventory_de"] = (
        " | ".join(dictionary[atom]["working_value_de"] for atom in arguments)
        or "KEIN_EXPLIZITES_ARGUMENT"
    )
    statement["relation_inventory_de"] = (
        " | ".join(dictionary[atom]["working_value_de"] for atom in relations)
        or "KEINE_EXPLIZITE_RELATION"
    )
    statement["grade_inventory_de"] = (
        " | ".join(dictionary[atom]["working_value_de"] for atom in grades)
        or "KEIN_EXPLIZITER_GRAD"
    )


def image_expansion(owner_id: str) -> str:
    if owner_id.endswith("_WHOLE_PLANT"):
        return (
            "BILDLOKAL: die abgebildete Ganzpflanze liefert das konkrete Sachnomen"
        )
    if owner_id.startswith("F66R_TEXT_BLOCK_"):
        return (
            "BILDLOKAL: sichtbarer Prosablock; kein Gegenstandsname wird ergaenzt"
        )
    return "BILDLOKAL: getrennte lokale Rand- oder Nachtragszone"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    g404 = load_module("gdt404_admission", G404_RUN)
    transform = load_module("pass1026_transform", PASS1026_RUN)
    source_rows, guard_stats = guarded_source_rows()
    if len(source_rows) != 122 or guard_stats.get("selected") != 122:
        raise RuntimeError(
            f"selected-page source drift: {len(source_rows)} / {guard_stats}",
        )
    if {row["page"] for row in source_rows} != set(SELECTED_PAGES):
        raise RuntimeError("guarded source page set drift")
    if any(row["page"].startswith("f84") for row in source_rows):
        raise RuntimeError("forbidden selector materialised")

    dictionary_rows = read_tsv(DICT_IN)
    if len(dictionary_rows) != 46:
        raise RuntimeError("current component dictionary no longer has 46 rows")
    dictionary = {row["atom"]: row for row in dictionary_rows}
    portable_atoms = {
        row["atom"]
        for row in dictionary_rows
        if row["semantic_layer"] == "PORTABLE_BROAD_WORKING_CORE"
    }
    if len(portable_atoms) != 19:
        raise RuntimeError("portable working core no longer has 19 atoms")

    lock_rows = read_tsv(LOCK_IN)
    running_rows = read_tsv(RUNNING_IN)
    local_rows = read_tsv(LOCAL_IN)
    unified_rows = read_tsv(UNIFIED_IN)
    old_page_rows = read_tsv(PAGE26_IN)
    expectation_source = read_tsv(EXPECTATION_IN)
    owner_rows = read_tsv(OWNER_IN)
    expected_counts = (426, 4576, 693, 5269, 26, 5)
    actual_counts = (
        len(lock_rows), len(running_rows), len(local_rows),
        len(unified_rows), len(old_page_rows), len(expectation_source),
    )
    if actual_counts != expected_counts:
        raise RuntimeError(f"upstream row-count drift: {actual_counts}")
    if len(owner_rows) != 4 or {
        row["physical_page"] for row in owner_rows
    } != set(SELECTED_PAGES):
        raise RuntimeError("GDT514 owner-map drift")
    lock = {row["surface"]: row for row in lock_rows}

    running_recipe_sets: dict[str, set[str]] = defaultdict(set)
    running_counts: Counter[str] = Counter()
    running_colors: dict[str, set[str]] = defaultdict(set)
    for row in running_rows:
        running_recipe_sets[row["surface"]].add(row["component_recipe"])
        running_counts[row["surface"]] += 1
        running_colors[row["surface"]].add(row["admission_color"])
    if any(len(recipes) != 1 for recipes in running_recipe_sets.values()):
        raise RuntimeError("current running deck violates one-surface/one-recipe")
    running_recipe = {
        surface: next(iter(recipes))
        for surface, recipes in running_recipe_sets.items()
    }

    old_local_recipes: dict[str, set[str]] = defaultdict(set)
    old_all_surfaces: set[str] = set()
    for row in unified_rows:
        old_all_surfaces.add(row["surface"])
        if row["group_kind"] != "RUNNING_EVENT":
            old_local_recipes[row["surface"]].add(row["component_recipe"])

    prose_blocks = assign_prose_blocks(source_rows)
    write_tsv(SOURCE_OUT, source_rows, list(source_rows[0]))
    selected_counts: Counter[str] = Counter()
    selected_kinds: dict[str, set[str]] = defaultdict(set)
    for source in source_rows:
        tokens = source["eva_clean"].split()
        if len(tokens) != int(source["token_count"]):
            raise RuntimeError(f"token mismatch at {source['locus']}")
        selected_counts.update(tokens)
        for token in tokens:
            selected_kinds[token].add(f"{source['kind']}/{source['subtype']}")

    running_absent = set(selected_counts) - set(running_recipe)
    if set(MANUAL_NEW_RECIPE) != running_absent:
        missing = sorted(running_absent - set(MANUAL_NEW_RECIPE))
        extra = sorted(set(MANUAL_NEW_RECIPE) - running_absent)
        raise RuntimeError(
            f"manual surface inventory mismatch: missing={missing}, extra={extra}",
        )
    allowed_atoms = set(dictionary) | set(LOCAL_OPAQUE_ATOMS)
    for surface, recipe in MANUAL_NEW_RECIPE.items():
        bad = [atom for atom in recipe.split("+") if atom not in allowed_atoms]
        if bad:
            raise RuntimeError(f"unlicensed atom in {surface}: {bad}")

    events: list[dict[str, object]] = []
    for source in source_rows:
        prose_block = prose_blocks.get(source["locus"], "NONE")
        owner_id, owner_de, owner_subblock = owner_for(source, prose_block)
        for ordinal, surface in enumerate(source["eva_clean"].split(), start=1):
            if surface in lock:
                recipe = lock[surface]["locked_recipe"]
                status = "EXACT_GDT405_LOCK"
                support = f"GDT405::{lock[surface]['lock_id']}"
                color = (
                    "AMBER"
                    if lock[surface]["amber_boundary"] == "YES"
                    else "GREEN"
                )
            elif surface in running_recipe:
                recipe = running_recipe[surface]
                status = "EXACT_CURRENT_RUNNING_RECIPE"
                support = f"GDT407::{running_counts[surface]}_RUNNING_EVENTS"
                color = "AMBER" if "AMBER" in running_colors[surface] else "GREEN"
            else:
                recipe = MANUAL_NEW_RECIPE[surface]
                if "LOCAL_NAME_CORE_X" in recipe:
                    status = "NEW_LOCAL_NAME_CORE_WITH_VISIBLE_SHELL"
                elif recipe in {"LOCAL_SIGN_X", "LOCAL_SIGN_C"}:
                    status = "NEW_OWNER_LOCAL_SIGN"
                elif surface in old_local_recipes:
                    status = (
                        "OLD_LOCAL_SURFACE_NEW_RUNNING_CONTEXT_"
                        "VISIBLE_RESEGMENTATION"
                    )
                else:
                    status = "NEW_VISIBLE_COMPOSITION"
                support = "DIRECT_VISIBLE_COMPOSITION"
                color = "AMBER" if surface in AMBIGUOUS_MANUAL else "GREEN"
            atoms = recipe.split("+")
            role = record_role(
                atoms, source["kind"], source["subtype"],
                int(source["line_number"]),
            )
            event_id = f"G515-E{len(events) + 1:04d}"
            trace = literal(recipe, dictionary)
            events.append({
                "event_id": event_id,
                "physical_page": source["page"],
                "source_page_value": source["page"],
                "locus": source["locus"],
                "line_number": int(source["line_number"]),
                "source_kind": source["kind"],
                "source_subtype": source["subtype"],
                "paragraph_start": source["paragraph_start"],
                "paragraph_end": source["paragraph_end"],
                "card_ordinal_in_line": ordinal,
                "surface": surface,
                "register": g404.register_for(source["section"]),
                "prose_block_id": prose_block,
                "owner_id": owner_id,
                "owner_de": owner_de,
                "owner_evidence": "GDT514_IMAGE_FIRST_OWNER_MAP",
                "owner_subblock": owner_subblock,
                "statement_id": "NONE",
                "card_ordinal_in_statement": 0,
                "content_role": role,
                "surface_status": status,
                "visible_recipe": recipe,
                "literal_core_reading_de": trace,
                "default_working_reading_de": default_reading(
                    role, owner_de, surface, recipe, dictionary,
                ),
                "recipe_support": support,
                "old_running_event_count": running_counts[surface],
                "old_local_surface_contact": (
                    "YES" if surface in old_local_recipes else "NO"
                ),
                "old_local_recipes": join_sorted(
                    old_local_recipes.get(surface, set()),
                ),
                "genuinely_new_to_old_26_pages": (
                    "NO" if surface in old_all_surfaces else "YES"
                ),
                "admission_color": color if source["kind"] == "P" else "LOCAL",
                "portable_atom_count": sum(atom in portable_atoms for atom in atoms),
                "formal_or_local_atom_count": sum(
                    atom not in portable_atoms for atom in atoms
                ),
                "new_portable_atom_count": 0,
                "opaque_local_atom_count": sum(
                    atom in LOCAL_OPAQUE_ATOMS for atom in atoms
                ),
                "portable_meaning_changed": "NO",
                "structural_tag_promoted_to_word": "NO",
                "guard": GUARD,
            })
    if len(events) != 597 or len({event["surface"] for event in events}) != 377:
        raise RuntimeError("selected event or surface count drift")

    prose_events = [event for event in events if event["source_kind"] == "P"]
    label_events = [event for event in events if event["source_kind"] == "L"]
    if len(prose_events) != 546 or len(label_events) != 51:
        raise RuntimeError("prose/local split drift")

    statements = g404.segment_statements(prose_events)
    for statement in statements:
        old_id = str(statement["statement_id"])
        new_id = old_id.replace("G404-S", "G515-S")
        statement["statement_id"] = new_id
        for event in prose_events:
            if event["statement_id"] == old_id:
                event["statement_id"] = new_id
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in prose_events:
        events_by_statement[str(event["statement_id"])].append(event)
    for statement in statements:
        current_statement_fields(
            statement,
            events_by_statement[str(statement["statement_id"])],
            dictionary,
        )

    attachments = g404.build_factorized_attachments(statements, prose_events)
    current_actions = {
        atom: dictionary[atom]["working_value_de"] for atom in ACTION_HEADS
    }
    for ordinal, attachment in enumerate(attachments, start=1):
        attachment["factorized_id"] = f"G515-A{ordinal:05d}"
        focus = str(attachment["focus_core"])
        action = str(attachment["action_core"])
        attachment["focus_value_de"] = dictionary[focus]["working_value_de"]
        attachment["action_value_de"] = current_actions.get(action, "BESITZER")

    attachments_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for attachment in attachments:
        attachments_by_statement[str(attachment["statement_id"])].append(attachment)
    for statement in statements:
        rows = attachments_by_statement[str(statement["statement_id"])]
        failures = sum(
            row["factorized_result"] != "PASS_FIXED_FACTORS" for row in rows
        )
        if failures:
            statement["admission_color"] = "RED"
        statement["focus_attachment_count"] = len(rows)
        statement["bounded_forward_count"] = sum(
            row["attachment_geometry"] == "BOUNDED_NEXT_CARD_ACTION"
            for row in rows
        )
        statement["owner_only_count"] = sum(
            row["attachment_geometry"] == "OWNER_ONLY" for row in rows
        )
        statement["selector_inventory"] = join_sorted(
            row["selector_rule"] for row in rows
        )
        statement["head_inventory"] = join_sorted(
            row["action_core"] for row in rows
        )
        statement["image_local_expansion_de"] = image_expansion(
            str(statement["owner_id"]),
        )
        statement["scope_skeleton_de"] = (
            f"BESITZER[{statement['owner_id']}] > "
            f"HANDLUNG[{statement['action_chain_de']}] > "
            f"ARG[{statement['argument_inventory_de']}] > "
            f"REL[{statement['relation_inventory_de']}] > "
            f"GRAD[{statement['grade_inventory_de']}] > {statement['end_mode']}"
        )
        owner = events_by_statement[str(statement["statement_id"])][0]["owner_de"]
        statement["default_working_reading_de"] = (
            f"BEI {owner}: {statement['action_chain_de']}; "
            f"{statement['argument_inventory_de']}; "
            f"{statement['relation_inventory_de']}; "
            f"{statement['grade_inventory_de']}"
        )
        statement["factorized_result"] = (
            "PASS_FIXED_FACTORS"
            if failures == 0
            else "RED_NEW_AXIS_OR_BOUNDARY"
        )
        statement["guard"] = GUARD

    ambiguous_close_ids = {
        str(event["event_id"])
        for event in prose_events
        if event["surface"] in AMBIGUOUS_MANUAL
        and str(event["visible_recipe"]).split("+")[-1] == "DY"
    }
    alternate_events = [dict(event) for event in prose_events]
    alternate_statements = g404.segment_statements(
        alternate_events, ambiguous_close_ids,
    )
    for statement in alternate_statements:
        old_id = str(statement["statement_id"])
        new_id = old_id.replace("G404-S", "G515-X")
        statement["statement_id"] = new_id
        for event in alternate_events:
            if event["statement_id"] == old_id:
                event["statement_id"] = new_id
    alternate_attachments = g404.build_factorized_attachments(
        alternate_statements, alternate_events,
    )
    primary_by_focus = {
        (
            str(row["event_id"]), str(row["focus_core"]),
            str(row["focus_occurrence_ordinal"]),
        ): row
        for row in attachments
    }
    alternate_by_focus = {
        (
            str(row["event_id"]), str(row["focus_core"]),
            str(row["focus_occurrence_ordinal"]),
        ): row
        for row in alternate_attachments
    }
    if set(primary_by_focus) != set(alternate_by_focus):
        raise RuntimeError("amber close changed focus inventory")
    sensitivity_rows: list[dict[str, object]] = []
    for key in sorted(primary_by_focus):
        primary = primary_by_focus[key]
        alternate = alternate_by_focus[key]
        changed_fields = [
            field
            for field in (
                "selector_rule", "attachment_geometry",
                "selected_action_event_id", "selected_action_atom_ordinal",
                "action_core", "r_topology", "duplicate_mode",
            )
            if str(primary[field]) != str(alternate[field])
        ]
        if changed_fields:
            sensitivity_rows.append({
                "event_id": key[0],
                "surface": primary["surface"],
                "focus_core": key[1],
                "focus_occurrence_ordinal": key[2],
                "primary_statement_id": primary["statement_id"],
                "alternate_statement_id": alternate["statement_id"],
                "changed_fields": "|".join(changed_fields),
                "primary_selector": primary["selector_rule"],
                "alternate_selector": alternate["selector_rule"],
                "primary_action_core": primary["action_core"],
                "alternate_action_core": alternate["action_core"],
                "alternate_factorized_result": alternate["factorized_result"],
            })
    if not sensitivity_rows:
        sensitivity_rows = [{
            "event_id": "NONE",
            "surface": "NONE",
            "focus_core": "NONE",
            "focus_occurrence_ordinal": 0,
            "primary_statement_id": "NONE",
            "alternate_statement_id": "NONE",
            "changed_fields": "NONE",
            "primary_selector": "NONE",
            "alternate_selector": "NONE",
            "primary_action_core": "NONE",
            "alternate_action_core": "NONE",
            "alternate_factorized_result": "PASS_FIXED_FACTORS",
        }]

    novel_rows: list[dict[str, object]] = []
    for surface in sorted(running_absent):
        candidates = g404.one_edit_candidates(
            surface, running_recipe, running_counts, transform,
        )
        best_context = max(
            (int(row["shared_context_score"]) for row in candidates),
            default=-1,
        )
        best = [
            row for row in candidates
            if int(row["shared_context_score"]) == best_context
        ]
        weights: Counter[str] = Counter()
        supports: dict[str, set[str]] = defaultdict(set)
        for candidate in best:
            recipe = str(candidate["candidate_recipe"])
            weights[recipe] += int(candidate["source_event_count"])
            supports[recipe].add(str(candidate["source_surface"]))
        recipes = sorted(weights, key=lambda recipe: (-weights[recipe], recipe))
        direct = MANUAL_NEW_RECIPE[surface]
        surface_events = [
            event for event in events if event["surface"] == surface
        ]
        novel_rows.append({
            "surface": surface,
            "occurrence_count": selected_counts[surface],
            "physical_pages": join_sorted(
                event["physical_page"] for event in surface_events
            ),
            "source_kinds": join_sorted(selected_kinds[surface]),
            "direct_visible_recipe": direct,
            "selection_status": surface_events[0]["surface_status"],
            "admission_color": surface_events[0]["admission_color"],
            "genuinely_new_to_old_26_pages": (
                "NO" if surface in old_all_surfaces else "YES"
            ),
            "old_local_surface_contact": (
                "YES" if surface in old_local_recipes else "NO"
            ),
            "old_local_recipes": join_sorted(
                old_local_recipes.get(surface, set()),
            ),
            "direct_recipe_matches_old_local_recipe": (
                "YES" if direct in old_local_recipes.get(surface, set()) else "NO"
            ),
            "best_shared_context_score": best_context,
            "best_context_source_count": len(best),
            "distinct_best_candidate_recipe_count": len(recipes),
            "direct_recipe_seen_in_best_candidates": (
                "YES" if direct in weights else "NO"
            ),
            "candidate_recipes_by_weight": " | ".join(
                f"{recipe}::{weights[recipe]}" for recipe in recipes
            ) or "NONE",
            "supporting_surfaces_for_direct_recipe": join_sorted(
                supports.get(direct, set()),
            ),
            "new_portable_atom_count": 0,
            "local_opaque_atoms": join_sorted(
                atom
                for atom in direct.split("+")
                if atom in LOCAL_OPAQUE_ATOMS
            ),
            "working_policy": "DIRECT_VISIBLE_DEFAULT_RETAINED_UNTIL_BETTER_PARSE",
            "guard": GUARD,
        })
    genuinely_new_rows = [
        row for row in novel_rows
        if row["genuinely_new_to_old_26_pages"] == "YES"
    ]
    if len(novel_rows) != 169 or len(genuinely_new_rows) != 159:
        raise RuntimeError("new-surface census drift")

    surface_rows: list[dict[str, object]] = []
    for ordinal, surface in enumerate(sorted(selected_counts), start=1):
        rows = [event for event in events if event["surface"] == surface]
        recipes = {str(event["visible_recipe"]) for event in rows}
        if len(recipes) != 1:
            raise RuntimeError(f"selected surface has multiple recipes: {surface}")
        surface_rows.append({
            "gdt515_surface_id": f"G515-W{ordinal:04d}",
            "surface": surface,
            "event_count": len(rows),
            "physical_pages": join_sorted(
                row["physical_page"] for row in rows
            ),
            "source_kinds": join_sorted(
                f"{row['source_kind']}/{row['source_subtype']}" for row in rows
            ),
            "content_roles": join_sorted(row["content_role"] for row in rows),
            "visible_recipe": next(iter(recipes)),
            "literal_core_reading_de": rows[0]["literal_core_reading_de"],
            "default_working_readings_de": " || ".join(
                dict.fromkeys(
                    str(row["default_working_reading_de"]) for row in rows
                ),
            ),
            "surface_status": rows[0]["surface_status"],
            "admission_colors": join_sorted(
                row["admission_color"] for row in rows
            ),
            "old_running_event_count": running_counts[surface],
            "old_local_surface_contact": rows[0]["old_local_surface_contact"],
            "genuinely_new_to_old_26_pages": rows[0][
                "genuinely_new_to_old_26_pages"
            ],
            "new_portable_atom_count": 0,
            "portable_meaning_changed": "NO",
            "structural_tag_promoted_to_word": "NO",
            "guard": GUARD,
        })

    page_rows: list[dict[str, object]] = []
    for page in SELECTED_PAGES:
        page_events = [
            event for event in events if event["physical_page"] == page
        ]
        page_prose = [
            event for event in page_events if event["source_kind"] == "P"
        ]
        page_labels = [
            event for event in page_events if event["source_kind"] == "L"
        ]
        page_statements = [
            statement
            for statement in statements
            if statement["physical_page"] == page
        ]
        page_attachments = [
            row for row in attachments if row["physical_page"] == page
        ]
        page_rows.append({
            "physical_page": page,
            "registers": join_sorted(event["register"] for event in page_events),
            "source_line_count": sum(
                source["page"] == page for source in source_rows
            ),
            "visible_group_count": len(page_events),
            "running_event_count": len(page_prose),
            "local_group_count": len(page_labels),
            "distinct_surface_count": len(
                {str(event["surface"]) for event in page_events}
            ),
            "exact_gdt405_event_count": sum(
                event["surface_status"] == "EXACT_GDT405_LOCK"
                for event in page_events
            ),
            "exact_other_running_event_count": sum(
                event["surface_status"] == "EXACT_CURRENT_RUNNING_RECIPE"
                for event in page_events
            ),
            "genuinely_new_event_count": sum(
                event["genuinely_new_to_old_26_pages"] == "YES"
                for event in page_events
            ),
            "local_name_core_event_count": sum(
                event["surface_status"]
                == "NEW_LOCAL_NAME_CORE_WITH_VISIBLE_SHELL"
                for event in page_events
            ),
            "local_sign_event_count": sum(
                event["surface_status"] == "NEW_OWNER_LOCAL_SIGN"
                for event in page_events
            ),
            "statement_count": len(page_statements),
            "open_statement_count": sum(
                statement["end_mode"] == "PROSE_BLOCK_OPEN_END"
                for statement in page_statements
            ),
            "focus_attachment_count": len(page_attachments),
            "factorized_failure_count": sum(
                row["factorized_result"] != "PASS_FIXED_FACTORS"
                for row in page_attachments
            ),
            "complete_default_count": len(page_events),
            "page_decision": (
                "ADMIT_WITH_LOCAL_SIGN_TRACK"
                if page_labels
                else "ADMIT_WORKING_EDITION"
            ),
            "guard": GUARD,
        })

    lock_events = [event for event in events if event["surface"] in lock]
    lock_mismatches = [
        event
        for event in lock_events
        if event["visible_recipe"] != lock[str(event["surface"])]["locked_recipe"]
    ]
    role_counts = Counter(str(event["content_role"]) for event in events)
    expectation_rows = [
        {
            "expectation_id": "G513-P1",
            "expectation_de": expectation_source[0]["new_page_expectation_de"],
            "observed_result": "SEEN_STRONGLY",
            "observed_count": sum(
                event["surface"] in running_recipe for event in events
            ),
            "denominator": len(events),
            "reading_de": (
                "Bekannte laufende Oberflaechen kehren mit ihrem vorhandenen "
                "Einzelrezept wieder."
            ),
        },
        {
            "expectation_id": "G513-P2",
            "expectation_de": expectation_source[1]["new_page_expectation_de"],
            "observed_result": "SEEN_WITH_LOCAL_TAIL",
            "observed_count": len(genuinely_new_rows),
            "denominator": len(genuinely_new_rows),
            "reading_de": (
                "Alle neuen Oberflaechen erhalten sichtbare Rezepte; nur X in "
                "axor/chxar und zwei Randzeichen bleiben lokal und undurchsichtig."
            ),
        },
        {
            "expectation_id": "G513-P3",
            "expectation_de": expectation_source[2]["new_page_expectation_de"],
            "observed_result": "SEEN",
            "observed_count": len(
                {event["content_role"] for event in prose_events}
            ),
            "denominator": 5,
            "reading_de": (
                "Die Prosa verteilt sich auf Anweisung, Fortsetzung/Adresse, "
                "Koordinate/Katalog, lokale Kennung und Namenskern mit Rahmen."
            ),
        },
        {
            "expectation_id": "G513-P4",
            "expectation_de": expectation_source[3]["new_page_expectation_de"],
            "observed_result": "SEEN_WITH_TEXT_PAGE_QUALIFICATION",
            "observed_count": len(portable_atoms),
            "denominator": 19,
            "reading_de": (
                "Alle 19 portablen Werte bleiben unveraendert; drei Seiten "
                "liefern eine Ganzpflanze, f66r nur Textblockbesitzer."
            ),
        },
        {
            "expectation_id": "G513-P5",
            "expectation_de": expectation_source[4]["new_page_expectation_de"],
            "observed_result": "SEEN",
            "observed_count": len(lock_events) - len(lock_mismatches),
            "denominator": len(lock_events),
            "reading_de": (
                "Jeder GDT405-Kontakt behaelt sein Rezept; X/C-Randzeichen "
                "und die zwei X-Namenskerne bleiben lokale Tags statt Woerter."
            ),
        },
    ]

    running30 = [dict(row) for row in running_rows]
    for event in prose_events:
        ordinal = len(running30) + 1
        running30.append({
            "global_running_ordinal": ordinal,
            "global_running_event_id": f"G515-R{ordinal:04d}",
            "source_layer": "GDT515_SECOND_RANDOM4_RUNNING",
            "source_event_id": event["event_id"],
            "source_replay_event_id": event["event_id"],
            "physical_page": event["physical_page"],
            "source_panel": event["source_page_value"],
            "register": event["register"],
            "locus": event["locus"],
            "source_order": int(
                str(event["event_id"]).removeprefix("G515-E")
            ),
            "source_statement_id": event["statement_id"],
            "owner_de": event["owner_de"],
            "surface": event["surface"],
            "component_recipe": event["visible_recipe"],
            "literal_core_reading_de": event["literal_core_reading_de"],
            "surface_status": event["surface_status"],
            "admission_color": event["admission_color"],
        })
    if len(running30) != 5122:
        raise RuntimeError("30-page running count drift")

    local30 = [dict(row) for row in local_rows]
    for event in label_events:
        local30.append({
            "source_layer": "GDT515_SECOND_RANDOM4_LOCAL",
            "source_event_id": event["event_id"],
            "physical_page": event["physical_page"],
            "source_panel": event["source_page_value"],
            "register": event["register"],
            "locus": event["locus"],
            "source_order": int(
                str(event["event_id"]).removeprefix("G515-E")
            ),
            "owner_de": event["owner_de"],
            "surface": event["surface"],
            "component_recipe": event["visible_recipe"],
            "literal_core_reading_de": event["literal_core_reading_de"],
            "local_contextual_expansion_de": event[
                "default_working_reading_de"
            ],
            "source_local_role": event["content_role"],
            "surface_status": event["surface_status"],
            "admission_color": "LOCAL_ONLY",
        })
    if len(local30) != 744:
        raise RuntimeError("30-page local count drift")

    unified30 = [dict(row) for row in unified_rows]
    for event in events:
        ordinal = len(unified30) + 1
        is_running = event["source_kind"] == "P"
        unified30.append({
            "global_group_ordinal": ordinal,
            "global_group_id": f"G515-G{ordinal:04d}",
            "group_kind": (
                "RUNNING_EVENT" if is_running else "LOCAL_ADDRESS_OR_LABEL"
            ),
            "source_layer": (
                "GDT515_SECOND_RANDOM4_RUNNING"
                if is_running
                else "GDT515_SECOND_RANDOM4_LOCAL"
            ),
            "source_event_id": event["event_id"],
            "physical_page": event["physical_page"],
            "source_panel": event["source_page_value"],
            "register": event["register"],
            "locus": event["locus"],
            "source_order": int(
                str(event["event_id"]).removeprefix("G515-E")
            ),
            "source_statement_id": (
                event["statement_id"] if is_running else "NONE"
            ),
            "owner_de": event["owner_de"],
            "surface": event["surface"],
            "component_recipe": event["visible_recipe"],
            "literal_core_reading_de": event["literal_core_reading_de"],
            "surface_status": event["surface_status"],
            "admission_color": (
                event["admission_color"] if is_running else "LOCAL_ONLY"
            ),
            "source_local_role": (
                "NONE" if is_running else event["content_role"]
            ),
        })
    if len(unified30) != 5866:
        raise RuntimeError("30-page unified count drift")

    page30 = [dict(row) for row in old_page_rows]
    for page_row in page_rows:
        page = str(page_row["physical_page"])
        page30.append({
            "page_ordinal": len(page30) + 1,
            "physical_page": page,
            "registers": page_row["registers"],
            "visible_group_count": page_row["visible_group_count"],
            "running_event_count": page_row["running_event_count"],
            "local_group_count": page_row["local_group_count"],
            "statement_count": page_row["statement_count"],
            "focus_attachment_count": page_row["focus_attachment_count"],
            "open_statement_count": page_row["open_statement_count"],
            "amber_event_count": sum(
                event["admission_color"] == "AMBER"
                for event in events
                if event["physical_page"] == page
            ),
            "distinct_surface_count": page_row["distinct_surface_count"],
        })
    if len(page30) != 30:
        raise RuntimeError("30-page summary drift")

    event_fields = list(events[0])
    write_tsv(EVENT_OUT, events, event_fields)
    write_tsv(SURFACE_OUT, surface_rows)
    write_tsv(NOVEL_RUNNING_OUT, novel_rows)
    write_tsv(NOVEL_ALL_OUT, genuinely_new_rows)
    write_tsv(LABEL_OUT, label_events, event_fields)
    write_tsv(STATEMENT_OUT, statements)
    write_tsv(ATTACHMENT_OUT, attachments)
    write_tsv(SENSITIVITY_OUT, sensitivity_rows)
    write_tsv(PAGE_OUT, page_rows)
    write_tsv(EXPECTATION_OUT, expectation_rows)
    write_tsv(RUNNING30_OUT, running30, list(running_rows[0]))
    write_tsv(LOCAL30_OUT, local30, list(local_rows[0]))
    write_tsv(UNIFIED30_OUT, unified30, list(unified_rows[0]))
    write_tsv(PAGE30_OUT, page30, list(old_page_rows[0]))

    reading = [
        "# GDT515 — Vollständige Arbeitslesung der vier neuen Seiten",
        "",
        f"Status: `{STATUS}`",
        "",
        (
            "Jede der 597 sichtbaren Karten besitzt unten eine konkrete "
            "Default-Lesung. Diese Lesungen sind keine behauptete "
            "Klartextübersetzung: Portable Funktionswerte stehen als "
            "Arbeitswörter, formale und lokale Zeichen bleiben sichtbar "
            "geklammerte Tags. Die 51 Rand- und Nachtragskarten von f66r "
            "werden nicht an Prosasätze angehängt."
        ),
        "",
        "## Kurzbefund",
        "",
        (
            f"- 546 Prosakarten und 51 Rand-/Nachtragskarten; "
            f"{len(statements)} Arbeitsaussagen."
        ),
        (
            f"- {sum(event['surface'] in running_recipe for event in events)}"
            "/597 Karten wiederholen eine alte laufende Oberfläche."
        ),
        (
            f"- {len(genuinely_new_rows)} Oberflächen sind gegenüber allen "
            "alten 26 Seiten neu; keine verlangt einen neuen portablen Wert."
        ),
        (
            "- `axor` und `chxar` behalten einen lokalen X-Namenskern; die "
            "alleinstehenden `x` und `c` bleiben Randzeichen."
        ),
        "",
        "## Aussagen in kompakter Arbeitslesung",
        "",
    ]
    for page in SELECTED_PAGES:
        reading.extend([f"### {page}", ""])
        for statement in [
            row for row in statements if row["physical_page"] == page
        ]:
            reading.extend([
                f"- **{statement['statement_id']}** "
                f"(`{statement['surface_sequence']}`)",
                f"  - {statement['default_working_reading_de']}",
                f"  - `{statement['scope_skeleton_de']}`",
            ])
        if page == "f66r":
            reading.append(
                "- Randkennungen, Einzelzeichen und der spaete Nachtrag "
                "stehen separat in der vollstaendigen Kartenlesung unten."
            )
        reading.append("")
    reading.extend(["## Vollständige Kartenlesung", ""])
    for page in SELECTED_PAGES:
        reading.extend([f"### {page}", ""])
        page_loci = list(dict.fromkeys(
            str(event["locus"])
            for event in events
            if event["physical_page"] == page
        ))
        for locus in page_loci:
            locus_events = [event for event in events if event["locus"] == locus]
            reading.extend([f"#### {locus}", ""])
            for event in locus_events:
                reading.append(
                    f"- `{event['surface']}` → "
                    f"{event['default_working_reading_de']} "
                    f"(Rezept `{event['visible_recipe']}`; "
                    f"`{event['surface_status']}`)"
                )
            reading.append("")
    reading.extend([
        "## Grenze",
        "",
        (
            "Die Ausgabe ist die derzeit vollständigste Arbeitsbedeutung "
            "innerhalb des Mischmodells aus Funktionskürzeln, formalen "
            "Kontrollen, sichtbaren Besitzern und lokalen Namen-/Zeichenresten. "
            "Sie bestätigt weder deutsche Wörter noch Pflanzenarten, Sprache "
            "oder historischen Klartext."
        ),
    ])
    READING_OUT.write_text(
        "\n".join(reading).rstrip() + "\n", encoding="utf-8",
    )

    result = {
        "experiment_id": "GDT515",
        "status": STATUS,
        "selected_pages": list(SELECTED_PAGES),
        "guard_stats": guard_stats,
        "source_line_count": len(source_rows),
        "event_count": len(events),
        "prose_event_count": len(prose_events),
        "local_label_sign_event_count": len(label_events),
        "unique_surface_count": len(surface_rows),
        "gdt405_exact_event_count": sum(
            event["surface_status"] == "EXACT_GDT405_LOCK" for event in events
        ),
        "gdt405_lock_mismatch_count": len(lock_mismatches),
        "old_running_exact_event_count": sum(
            event["surface"] in running_recipe for event in events
        ),
        "old_any_surface_event_count": sum(
            event["surface"] in old_all_surfaces for event in events
        ),
        "running_absent_surface_count": len(novel_rows),
        "genuinely_new_surface_count": len(genuinely_new_rows),
        "genuinely_new_event_count": sum(
            event["genuinely_new_to_old_26_pages"] == "YES"
            for event in events
        ),
        "old_local_only_contact_surface_count": sum(
            row["old_local_surface_contact"] == "YES" for row in novel_rows
        ),
        "manual_recipe_seen_in_best_one_edit_count": sum(
            row["direct_recipe_seen_in_best_candidates"] == "YES"
            for row in novel_rows
        ),
        "new_portable_atom_count": 0,
        "local_name_core_surface_count": 2,
        "owner_local_new_sign_surface_count": 2,
        "portable_meaning_changed_count": 0,
        "structural_tag_promoted_to_word_count": 0,
        "complete_default_count": sum(
            bool(event["default_working_reading_de"]) for event in events
        ),
        "prose_block_count": len(
            {event["prose_block_id"] for event in prose_events}
        ),
        "statement_count": len(statements),
        "licensed_close_statement_count": sum(
            statement["end_mode"] == "LICENSED_DY_CLOSE"
            for statement in statements
        ),
        "open_statement_count": sum(
            statement["end_mode"] == "PROSE_BLOCK_OPEN_END"
            for statement in statements
        ),
        "focus_attachment_count": len(attachments),
        "factorized_failure_count": sum(
            row["factorized_result"] != "PASS_FIXED_FACTORS"
            for row in attachments
        ),
        "maximum_lookahead_cards": max(
            int(row["lookahead_cards"]) for row in attachments
        ),
        "owner_boundary_crossing_count": sum(
            row["owner_boundary_crossed"] != "NO" for row in attachments
        ),
        "statement_boundary_crossing_count": sum(
            row["statement_boundary_crossed"] != "NO" for row in attachments
        ),
        "ambiguous_close_event_count": len(ambiguous_close_ids),
        "ambiguous_close_changed_attachment_count": (
            0
            if sensitivity_rows[0]["event_id"] == "NONE"
            else len(sensitivity_rows)
        ),
        "record_role_counts": dict(sorted(role_counts.items())),
        "expectations_seen_count": sum(
            str(row["observed_result"]).startswith("SEEN")
            for row in expectation_rows
        ),
        "extended_running_event_count": len(running30),
        "extended_local_group_count": len(local30),
        "extended_unified_group_count": len(unified30),
        "extended_page_count": len(page30),
        "source_sha256": sha256(SOURCE_OUT),
        "component_dictionary_sha256": sha256(DICT_IN),
        "guard": GUARD,
    }
    write_json(RESULT_OUT, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
