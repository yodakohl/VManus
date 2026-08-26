#!/usr/bin/env python3
"""Build GDT404's frozen random four-page transfer and first-pass admission.

The builder separates source extraction, neutral image ownership, exact
old-surface transfer, and new-surface morphology. New surfaces are not silently
assigned the recipe of a nearest neighbour: the corrected Pass-1026 visible-
edit transform must yield the same recipe from every supporting source before
a provisional recipe is admitted automatically.
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
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
ZL3B = ROOT / "transcription/voynich_zl3b_lines.tsv"
PASS1026 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_visible_allograph_resegmentation_one_thousand_twenty_sixth"
    / "PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv"
)
PASS1026_BUILDER = PASS1026.with_name("build_pass1026.py")

SEED_HEX = "2c3b94fccfaa6aa88e557bbd03730d9a"
SELECTED_PHYSICAL = ("f1r", "f24v", "f81r", "f95v")
SELECTED_VALUES = ("f1r", "f24v", "f81r", "f95v1", "f95v2")
SOURCE_COLUMNS = (
    "page,page_order,locus,line_number,code,relation,kind,subtype,section,"
    "language,hand,quire,folio_type,paragraph_start,paragraph_end,token_count,eva_clean"
)

ATOM_VALUE = {
    "Y": "AKTIVER POSTEN", "OK": "SETZEN", "OL": "FORTSETZEN",
    "OT": "DANACH", "AL": "ZIELORT", "CH": "NEHMEN",
    "SH": "HALTEN", "AR": "AUSGANG", "K": "GEBEN",
    "AIIN": "WERT", "S": "WÄHLEN", "CHD": "UMSETZEN",
    "OR": "EINHEIT", "L": "VERBINDUNG", "T": "EINSTELLEN",
    "AIN": "ANTEIL", "R": "MARKIEREN", "P": "EINSETZEN",
    "AIR": "LAUF", "E": "GRAD I", "EE": "GRAD II",
    "EEE": "GRAD III", "DY": "SCHLUSS", "O": "AUSFÜHRUNG",
    "CARRIER_Q": "BEGINNMARKER", "IIN": "STUFE", "DA": "ZWEITE STUFE",
    "D_ADDR": "HIER", "AM_ADDR": "HIER", "A_ADDR": "HIER",
    "S_ADDR": "HIER", "LOCAL_CHAR_F": "HIER", "D_LABEL": "HIER",
    "S_LABEL": "HIER", "M_LOCAL": "HIER", "Z_ADDR": "HIER",
    "G_LABEL": "VARIANTE", "LOCAL_CHAR_G": "VARIANTE",
    "LOCAL_CHAR_I": "VARIANTE", "LOCAL_CHAR_B": "VARIANTE",
    "LOCAL_CHAR_J": "VARIANTE", "LOCAL_CHAR_Z": "VARIANTE",
    "HO": "KLASSE", "AN": "KLASSE", "OS": "VORBEZUG",
    "RESUME_CARD": "VORBEZUG",
}

IMAGE_ROWS = [
    {
        "physical_page": "f1r", "image_url": "https://www.voynich.com/folios/color/001r.jpg",
        "sha256": "c0f11e98eb472063c812876a0dafec1e1344f0be92c7847e2e22e294b2253e17",
        "width": 1116, "height": 1536,
        "neutral_visual_reading": "vier getrennte Prosabloecke mit roten Abschnittszeichen; kein sicherer Gegenstandsbesitzer",
        "connection_constraint": "Textblockgrenzen sichtbar; blasse Farbspuren sind kein Besitzerbeleg",
    },
    {
        "physical_page": "f24v", "image_url": "https://www.voynich.com/folios/color/024v.jpg",
        "sha256": "e224cf1a478ea0f5cf044eb2473a00d6bf78d2d28cff44bcba65a187d8c3a091",
        "width": 1141, "height": 1536,
        "neutral_visual_reading": "eine ganzseitige Pflanze mit Wurzel, Blattwerk und blauen Blueten",
        "connection_constraint": "beide Prosaabschnitte koennen denselben Ganzpflanzenbesitzer erben",
    },
    {
        "physical_page": "f81r", "image_url": "https://www.voynich.com/folios/color/081r.jpg",
        "sha256": "968a949a435de9bd2d316c271e5a88f41dc56869ba0f2c0e131e09843a549d67",
        "width": 1150, "height": 1536,
        "neutral_visual_reading": "oberes und unteres Figurenbecken mit seitlichem gezeichnetem Lauf",
        "connection_constraint": "zwei lokale Besitzer; Verbindung sichtbar, Flussrichtung und serielle Prozessfolge nicht sichtbar",
    },
    {
        "physical_page": "f95v", "image_url": "https://www.voynich.com/folios/color/095v.jpg",
        "sha256": "5513aca39cacafecf110e623f30c075ab492ac3ceecc316b684ac4a2bb5997db",
        "width": 1246, "height": 1536,
        "neutral_visual_reading": "eine grosse verzweigte Ganzpflanze mit gelappten Blaettern und vielen blauen Koepfen",
        "connection_constraint": "f95v1 und f95v2 sind getrennte Textpaneele desselben sichtbaren Pflanzenbesitzers",
    },
]

# One explicit visible recipe for every surface that was absent from the
# 3,888-event Pass-1026 deck.  These are not word translations.  They are the
# card-level decompositions frozen after looking at the four selected pages.
# Every atom is already on the 46-sign sheet; no old atom receives a new value.
MANUAL_NEW_RECIPE = {
    "alched": "AL+CHD",
    "alfshed": "AL+LOCAL_CHAR_F+SH+E+D_ADDR",
    "alkain": "AL+K+AIN",
    "archytaiin": "AR+CH+Y+T+AIIN",
    "arsa": "AR+S+A_ADDR",
    "ase": "A_ADDR+S+E",
    "ataiin": "A_ADDR+T+AIIN",
    "cfhaiin": "CH+LOCAL_CHAR_F+AIIN",
    "cfhoaiin": "CH+LOCAL_CHAR_F+O+AIIN",
    "cfhol": "CH+LOCAL_CHAR_F+OL",
    "cha": "CH+A_ADDR",
    "chals": "CH+AL+S",
    "chcth": "CH+CH+T",
    "chcthykedy": "CH+CH+T+Y+K+E+DY",
    "chdykain": "CHD+Y+K+AIN",
    "chdyty": "CHD+Y+T+Y",
    "cheeodam": "CH+EE+O+D_ADDR+AM_ADDR",
    "chefar": "CH+E+LOCAL_CHAR_F+AR",
    "chetyry": "CH+E+T+Y+R+Y",
    "chocfhey": "CH+O+CH+LOCAL_CHAR_F+E+Y",
    "chodain": "CH+O+D_ADDR+AIN",
    "chotey": "CH+OT+E+Y",
    "chtaiin": "CH+T+AIIN",
    "chtal": "CH+T+AL",
    "chtor": "CH+T+OR",
    "ckhar": "CH+K+AR",
    "ckhor": "CH+K+OR",
    "ckhyds": "CH+K+Y+D_ADDR+S",
    "cphar": "CH+P+AR",
    "cphealy": "CH+P+E+AL+Y",
    "cphesaiin": "CH+P+E+S+AIIN",
    "cpho": "CH+P+O",
    "cphodaiils": "CH+P+O+D_ADDR+AIIN+L+S",
    "cphodal": "CH+P+O+D_ADDR+AL",
    "cphoy": "CH+P+O+Y",
    "ctheod": "CH+T+E+O+D_ADDR",
    "cthes": "CH+T+E+S",
    "cthiar": "CH+T+LOCAL_CHAR_I+AR",
    "cthoary": "CH+T+O+AR+Y",
    "ctholdar": "CH+T+OL+D_ADDR+AR",
    "cthols": "CH+T+OL+S",
    "cthres": "CH+T+R+E+S",
    "daid": "AIN+D_ADDR",
    "daiy": "D_ADDR+A_ADDR+LOCAL_CHAR_I+Y",
    "dan": "AIN",
    "daraiin": "D_ADDR+AR+AIIN",
    "dchaiin": "D_ADDR+CH+AIIN",
    "dchal": "D_ADDR+CH+AL",
    "dchar": "D_ADDR+CH+AR",
    "dcheo": "D_ADDR+CH+E+O",
    "dchody": "D_ADDR+CH+O+DY",
    "dkshey": "D_ADDR+K+SH+E+Y",
    "dloo": "D_ADDR+L+O+O",
    "dlos": "D_ADDR+L+O+S",
    "dn": "D_ADDR+AN",
    "do": "D_ADDR+O",
    "dolkain": "D_ADDR+OL+K+AIN",
    "dolkchy": "D_ADDR+OL+K+Y",
    "dshees": "D_ADDR+SH+EE+S",
    "dshey": "D_ADDR+SH+E+Y",
    "dydyd": "Y+DY+D_LABEL",
    "eo": "E+O",
    "eses": "E+S+E+S",
    "ety": "E+T+Y",
    "fachys": "LOCAL_CHAR_F+A_ADDR+CH+Y+S",
    "far": "LOCAL_CHAR_F+AR",
    "fcheey": "LOCAL_CHAR_F+CH+EE+Y",
    "fchodaiin": "LOCAL_CHAR_F+CH+O+D_ADDR+AIIN",
    "foar": "LOCAL_CHAR_F+O+AR",
    "kaipy": "K+A_ADDR+LOCAL_CHAR_I+P+Y",
    "kchod": "K+CH+O+D_ADDR",
    "kdchy": "K+D_ADDR+Y",
    "kochky": "K+O+CH+K+Y",
    "kod": "K+O+D_ADDR",
    "kodaiin": "K+O+D_ADDR+AIIN",
    "kodshey": "K+O+D_ADDR+SH+E+Y",
    "koeam": "K+O+E+AM_ADDR",
    "kokaiin": "K+OK+AIIN",
    "kos": "K+O+S",
    "koshey": "K+O+SH+E+Y",
    "kshed": "K+SH+E+D_ADDR",
    "kshedy": "K+SH+E+DY",
    "ksho": "K+SH+O",
    "kshoy": "K+SH+O+Y",
    "lchl": "L+CH+L",
    "lshee": "L+SH+EE",
    "lshl": "L+SH+L",
    "ochdy": "O+CHD+Y",
    "ochedar": "O+CHD+AR",
    "ocphoraiin": "O+CH+P+OR+AIIN",
    "octhyl": "O+CH+T+Y+L",
    "odaiim": "O+D_ADDR+AIIN+M_LOCAL",
    "odchees": "O+D_ADDR+CH+EE+S",
    "odor": "O+D_ADDR+OR",
    "oeeedy": "O+EEE+DY",
    "oeeey": "O+EEE+Y",
    "oekshy": "O+E+K+SH+Y",
    "oeor": "O+E+OR",
    "oepaiin": "O+E+P+AIIN",
    "oesearies": "O+E+S+E+AR+LOCAL_CHAR_I+E+S",
    "ofchdy": "O+LOCAL_CHAR_F+CHD+Y",
    "ofshdy": "O+LOCAL_CHAR_F+SH+D_ADDR+Y",
    "okady": "OK+A_ADDR+Y",
    "okalody": "OK+AL+O+DY",
    "okan": "OK+AN",
    "okcho": "OK+CH+O",
    "okchoy": "OK+CH+O+Y",
    "okodaiin": "OK+O+D_ADDR+AIIN",
    "okoeor": "OK+O+E+OR",
    "okshey": "OK+SH+E+Y",
    "oksho": "OK+SH+O",
    "olam": "OL+AM_ADDR",
    "olkaiin": "OL+K+AIIN",
    "olkal": "OL+K+AL",
    "olkchdy": "OL+K+CHD+Y",
    "olkshdy": "OL+K+SH+D_ADDR+Y",
    "olpchedy": "OL+P+CHD+DY",
    "olsain": "OL+S+AIN",
    "olshey": "OL+SH+E+Y",
    "olteedy": "OL+T+EE+DY",
    "opol": "O+P+OL",
    "opom": "O+P+O+AM_ADDR",
    "opshody": "O+P+SH+O+DY",
    "oraiiin": "OR+LOCAL_CHAR_I+AIIN",
    "oraisy": "OR+AIN+S+Y",
    "oro": "OR+O",
    "oror": "OR+OR",
    "osheedy": "O+SH+EE+DY",
    "otaiir": "OT+IIN+R",
    "otairin": "OT+AIR+IIN",
    "otalain": "OT+AL+AIN",
    "otaldy": "OT+AL+DY",
    "otardy": "OT+AR+DY",
    "otchos": "OT+CH+O+S",
    "otolodal": "OT+OL+O+D_ADDR+AL",
    "oydar": "O+Y+D_ADDR+AR",
    "podar": "P+O+D_ADDR+AR",
    "polchdy": "P+OL+CHD+DY",
    "polchoy": "P+OL+CH+O+Y",
    "pshedar": "P+SH+E+D_ADDR+AR",
    "pydeey": "P+Y+D_ADDR+EE+Y",
    "qcthdys": "CH+T+D_ADDR+Y+S",
    "qodain": "CARRIER_Q+O+AIN",
    "qodom": "CARRIER_Q+O+D_ADDR+O+AM_ADDR",
    "qofaiin": "CARRIER_Q+O+LOCAL_CHAR_F+AIIN",
    "qofchdaiin": "CARRIER_Q+O+LOCAL_CHAR_F+CHD+AIIN",
    "qokch": "OK+CH",
    "qokechedy": "OK+E+CHD+DY",
    "qokeeod": "OK+EE+O+D_ADDR",
    "qokesdy": "OK+E+S+DY",
    "qoko": "OK+O",
    "qoksh": "OK+SH",
    "qokshy": "OK+SH+Y",
    "qolsheedy": "OL+SH+EE+DY",
    "qopchol": "CARRIER_Q+O+P+CH+OL",
    "qotaldar": "OT+AL+D_ADDR+AR",
    "qotches": "OT+CH+E+S",
    "qotchey": "OT+CHD+Y",
    "qoteesy": "OT+EE+S+Y",
    "ro": "R+O",
    "roloty": "R+OL+OT+Y",
    "sckhey": "S+CH+K+E+Y",
    "shcthaiin": "SH+CH+T+AIIN",
    "shecphy": "SH+E+CH+P+Y",
    "shedain": "SH+E+AIN",
    "shekaiin": "SH+E+K+AIIN",
    "shekoiin": "SH+E+K+O+IIN",
    "shekshey": "SH+E+K+SH+E+Y",
    "shekydy": "SH+E+K+Y+DY",
    "sheos": "SH+E+O+S",
    "sheyk": "SH+E+Y+K",
    "shoaiin": "SH+O+AIIN",
    "shod": "SH+O+D_ADDR",
    "shodain": "SH+O+D_ADDR+AIN",
    "shodan": "SH+O+D_ADDR+AN",
    "shodary": "SH+O+D_ADDR+AR+Y",
    "shok": "SH+OK",
    "shokcheey": "SH+OK+CH+EE+Y",
    "shory": "SH+OR+Y",
    "shos": "SH+O+S",
    "shoshy": "SH+O+SH+Y",
    "shotshey": "SH+OT+SH+E+Y",
    "shoyfar": "SH+O+Y+LOCAL_CHAR_F+AR",
    "skchdy": "S+K+CHD+DY",
    "soiin": "S+O+IIN",
    "sory": "S+OR+Y",
    "syaiir": "S+Y+IIN+R",
    "tchar": "T+CH+AR",
    "tchdaiin": "T+CHD+AIIN",
    "tchey": "T+CH+E+Y",
    "tchodar": "T+CH+O+D_ADDR+AR",
    "teody": "T+E+O+DY",
    "tochol": "T+O+CH+OL",
    "tshdal": "T+SH+D_ADDR+AL",
    "tshes": "T+SH+E+S",
    "tshodeesy": "T+SH+O+D_ADDR+EE+S+Y",
    "tshor": "T+SH+OR",
    "ychedy": "Y+CHD+Y",
    "ycheey": "Y+SH+EE+Y",
    "ycheol": "Y+CH+E+O+L",
    "ycho": "Y+CH+O",
    "ychol": "Y+OL",
    "ydals": "Y+AL+S",
    "ydaraishy": "Y+D_ADDR+AR+A_ADDR+LOCAL_CHAR_I+SH+Y",
    "ydoin": "Y+D_ADDR+O+IIN",
    "ykal": "Y+K+AL",
    "ykaly": "Y+K+AL+Y",
    "ytar": "Y+T+AR",
    "ytasal": "Y+T+A_ADDR+S+AL",
    "ytchdy": "Y+T+CHD+Y",
    "ytshedy": "Y+T+SH+E+DY",
}

# These remain readable with the fixed atoms, but more than one renderer
# boundary is plausible.  They stay amber even when a useful working recipe is
# selected, so the experiment cannot turn editorial confidence into evidence.
AMBIGUOUS_NEW = {
    "alfshed", "arsa", "chdyty", "cheeodam", "chetyry", "ckhyds",
    "cphodaiils", "cthres", "daid", "daiy", "dloo", "dlos", "dn",
    "dydyd", "eses", "fachys", "kaipy", "kochky", "odchees",
    "oesearies", "okady", "oraiiin", "oraisy", "otaiir", "otairin",
    "otolodal", "pydeey", "qcthdys", "qodom", "qokeeod", "qokesdy",
    "qopchol", "qotchey", "qoteesy", "roloty", "shekoiin", "shekshey",
    "shekydy", "shodary", "shotshey", "shoyfar", "syaiir", "tchey",
    "tshodeesy", "ychedy", "ydaraishy", "ydoin", "ytasal", "ytchdy",
}

ACTIONS = {
    "OK": "SETZEN", "CH": "NEHMEN", "SH": "HALTEN", "K": "GEBEN",
    "S": "WÄHLEN", "T": "EINSTELLEN", "CHD": "UMSETZEN",
    "R": "MARKIEREN", "P": "EINSETZEN",
}
FOCI = {
    "AIIN": ("WERT", "ARGUMENT"), "AIN": ("ANTEIL", "ARGUMENT"),
    "OR": ("EINHEIT", "ARGUMENT"), "Y": ("AKTIVER POSTEN", "ARGUMENT"),
    "E": ("GRAD I", "GRADE"), "EE": ("GRAD II", "GRADE"),
    "EEE": ("GRAD III", "GRADE"), "AL": ("ZIELORT", "RELATION"),
    "AR": ("AUSGANG", "RELATION"), "L": ("VERBINDUNG", "RELATION"),
    "AIR": ("LAUF", "RELATION"),
}
FORWARD_FOCI = {"L", "AIR"}
R_COMPLEMENTS = {"Y", "AIIN", "AIN", "OR", "AL", "AR", "AIR", "L"}
FIXED_SELECTORS = {
    "AL_AR_ORDERED_FALLBACK", "INHERITED_ACTION_STACK",
    "L_AIR_RIGHT_FALLBACK", "NEAREST_HEAD_LEFT_TIE", "ONE_CARD_FORWARD",
    "OWNER_CONTEXT", "PREVIOUS_CARD_STACK", "Q_OT_PACKAGE_FORWARD",
}
FIXED_GEOMETRIES = {
    "BOUNDED_NEXT_CARD_ACTION", "INHERITED_ACTION", "OWNER_ONLY",
    "PREVIOUS_CARD_ACTION", "SAME_CARD_LEFT_ACTION", "SAME_CARD_RIGHT_ACTION",
}
FIXED_HEADS = {*ACTIONS, "OWNER"}
FIXED_R_TOPOLOGIES = {
    "NONE", "R_POSITIONAL_HEAD", "R_POSITIONAL_NESTED", "R_POSITIONAL_TAIL",
}
FIXED_DUPLICATE_MODES = {
    "SINGLE", "FREE_PLURAL_OR_REPEAT", "PACKAGE_SCOPE_DESCENT",
}


def register_for(section: str) -> str:
    return {
        "H": "HERBAL", "B": "BIOLOGICAL", "T": "SOURCE_SECTION_T",
    }.get(section, f"SOURCE_SECTION_{section or 'UNKNOWN'}")


def action_marks(atoms: list[str]) -> list[tuple[int, str]]:
    return [(index + 1, atom) for index, atom in enumerate(atoms) if atom in ACTIONS]


def duplicate_scope(atoms: list[str], atom_index: int, focus: str) -> tuple[str, str, str]:
    paired: int | None = None
    if atom_index and atoms[atom_index - 1] == focus:
        paired = atom_index - 1
    elif atom_index + 1 < len(atoms) and atoms[atom_index + 1] == focus:
        paired = atom_index + 1
    if paired is None:
        return "SINGLE", "SINGLE", "NONE"
    first = min(atom_index, paired)
    if focus == "OR":
        role = "PACKAGE_OUTER" if atom_index == first else "PACKAGE_INNER"
        return "PACKAGE_SCOPE_DESCENT", role, str(paired + 1)
    role = "FREE_PEER_1" if atom_index == first else "FREE_PEER_2"
    return "FREE_PLURAL_OR_REPEAT", role, str(paired + 1)


def local_r_resolution(
    atoms: list[str], r_position: int, active_before: dict[str, object] | None,
) -> tuple[str, int | None, str, dict[str, object] | None]:
    left = [
        (index + 1, atom)
        for index, atom in enumerate(atoms[: r_position - 1])
        if atom in ACTIONS
    ]
    right = atoms[r_position:]
    next_action = next((index for index, atom in enumerate(right) if atom in ACTIONS), len(right))
    complements = [atom for atom in right[:next_action] if atom in R_COMPLEMENTS]
    if left and complements:
        return "R", r_position, "R_POSITIONAL_NESTED", None
    if left:
        position, action = left[-1]
        return action, position, "R_POSITIONAL_TAIL", None
    if complements or "L" in atoms[: r_position - 1]:
        return "R", r_position, "R_POSITIONAL_HEAD", None
    if "OL" in right[:next_action] and active_before:
        return str(active_before["action"]), None, "R_POSITIONAL_TAIL", active_before
    return "R", r_position, "R_POSITIONAL_HEAD", None


def active_after_card(
    atoms: list[str], event: dict[str, object], card_ordinal: int,
    active_before: dict[str, object] | None,
) -> dict[str, object] | None:
    actions = action_marks(atoms)
    if not actions:
        return active_before
    position, action = actions[-1]
    r_mode = "NONE"
    if action == "R":
        action, new_position, r_mode, inherited = local_r_resolution(atoms, position, active_before)
        if inherited:
            return dict(inherited)
        position = int(new_position or position)
    return {
        "action": action, "event_id": event["event_id"],
        "card_ordinal": card_ordinal, "atom_ordinal": position, "r_mode": r_mode,
    }


def choose_attachment(
    focus: str, focus_position: int, atoms: list[str], event: dict[str, object],
    card_ordinal: int, active_before: dict[str, object] | None,
    next_event: dict[str, object] | None, next_atoms: list[str],
) -> dict[str, object]:
    actions = action_marks(atoms)
    left = [(position, action) for position, action in actions if position < focus_position]
    right = [(position, action) for position, action in actions if position > focus_position]
    nearest_left = left[-1] if left else None
    nearest_right = right[0] if right else None
    chosen: tuple[int, str] | None = None
    if focus in {"AL", "AR"}:
        if nearest_left:
            chosen = nearest_left
        elif not active_before and nearest_right:
            chosen = nearest_right
    elif focus in FORWARD_FOCI:
        chosen = nearest_right or nearest_left
    elif nearest_left and nearest_right:
        chosen = nearest_left if (
            focus_position - nearest_left[0] <= nearest_right[0] - focus_position
        ) else nearest_right
    else:
        chosen = nearest_left or nearest_right

    r_mode = "NONE"
    if chosen:
        position, action = chosen
        if action == "R":
            action, new_position, r_mode, inherited = local_r_resolution(
                atoms, position, active_before
            )
            if inherited:
                active_before = inherited
                chosen = None
            else:
                position = int(new_position or position)
        if chosen:
            return {
                "class": "SAME_CARD_LEFT_ACTION" if position < focus_position else "SAME_CARD_RIGHT_ACTION",
                "action": action, "source_event": event["event_id"],
                "source_card": card_ordinal, "source_atom": position,
                "lookahead": 0, "r_mode": r_mode,
            }

    if active_before:
        return {
            "class": "PREVIOUS_CARD_ACTION" if int(active_before["card_ordinal"]) == card_ordinal - 1 else "INHERITED_ACTION",
            "action": str(active_before["action"]), "source_event": str(active_before["event_id"]),
            "source_card": int(active_before["card_ordinal"]),
            "source_atom": int(active_before["atom_ordinal"]), "lookahead": 0,
            "r_mode": str(active_before.get("r_mode", "NONE")),
        }

    tokens = set(atoms)
    next_actions = action_marks(next_atoms)
    forward = bool(next_actions and "DY" not in tokens and "OS" not in tokens)
    if focus in {"AL", "AR"} and not (tokens & {"CARRIER_Q", "OT", "L", "AIR"}):
        forward = False
    if forward and next_event:
        position, action = next_actions[0]
        if action == "R":
            action, new_position, r_mode, _ = local_r_resolution(next_atoms, position, None)
            position = int(new_position or position)
        return {
            "class": "BOUNDED_NEXT_CARD_ACTION", "action": action,
            "source_event": next_event["event_id"], "source_card": card_ordinal + 1,
            "source_atom": position, "lookahead": 1, "r_mode": r_mode,
        }
    return {
        "class": "OWNER_ONLY", "action": None, "source_event": "OWNER",
        "source_card": 0, "source_atom": 0, "lookahead": 0, "r_mode": r_mode,
    }


def selector_rule(focus: str, selection: dict[str, object], atoms: list[str]) -> str:
    kind = str(selection["class"])
    if focus in {"AL", "AR"}:
        return "AL_AR_ORDERED_FALLBACK"
    if focus in FORWARD_FOCI:
        return "L_AIR_RIGHT_FALLBACK"
    if kind in {"SAME_CARD_LEFT_ACTION", "SAME_CARD_RIGHT_ACTION"}:
        return "NEAREST_HEAD_LEFT_TIE"
    if kind == "PREVIOUS_CARD_ACTION":
        return "PREVIOUS_CARD_STACK"
    if kind == "INHERITED_ACTION":
        return "INHERITED_ACTION_STACK"
    if kind == "BOUNDED_NEXT_CARD_ACTION":
        return "Q_OT_PACKAGE_FORWARD" if set(atoms) & {"CARRIER_Q", "OT"} else "ONE_CARD_FORWARD"
    return "OWNER_CONTEXT"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def guarded_source_rows() -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(ZL3B),
        "--selector", "page",
    ]
    for value in SELECTED_VALUES:
        command.extend(("--allow", value))
    command.extend(("--forbid-prefix", "f84", "--columns", SOURCE_COLUMNS))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    lines = result.stdout.splitlines()
    stat_lines = [line for line in (*lines, *result.stderr.splitlines()) if line.startswith("GUARD_STATS ")]
    if not lines or len(stat_lines) != 1:
        raise RuntimeError("guarded query did not return GUARD_STATS")
    stats = json.loads(stat_lines[0].removeprefix("GUARD_STATS "))
    data_lines = [line for line in lines if not line.startswith("GUARD_STATS ")]
    rows = list(csv.DictReader(io.StringIO("\n".join(data_lines) + "\n"), delimiter="\t"))
    return rows, stats


def load_transform_module():
    spec = importlib.util.spec_from_file_location("pass1026_visible_transform", PASS1026_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Pass-1026 visible transform")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def physical_page(page: str) -> str:
    return "f95v" if page.startswith("f95v") else page


def owner_for(row: dict[str, str]) -> tuple[str, str, str]:
    page = row["page"]
    line = int(row["line_number"])
    if page == "f1r":
        starts = [(22, "D"), (11, "C"), (7, "B"), (1, "A")]
        block = next(label for start, label in starts if line >= start)
        return f"F1R_TEXT_BLOCK_{block}", "VISIBLE_RUBRICATED_TEXT_BLOCK", "no_object_owner"
    if page == "f24v":
        block = "A" if line <= 5 else "B"
        return "F24V_WHOLE_PLANT", "DIRECT_VISIBLE_WHOLE_PLANT", f"paragraph_{block}"
    if page == "f81r":
        if line <= 15:
            return "F81R_UPPER_POOL", "DIRECT_VISIBLE_UPPER_FIGURE_POOL", "upper_pool"
        return "F81R_LOWER_POOL", "DIRECT_VISIBLE_LOWER_FIGURE_POOL", "lower_pool"
    if page == "f95v2":
        return "F95V_WHOLE_PLANT", "DIRECT_VISIBLE_WHOLE_PLANT", "panel_f95v2"
    if page == "f95v1":
        return "F95V_WHOLE_PLANT", "DIRECT_VISIBLE_WHOLE_PLANT", "panel_f95v1"
    raise RuntimeError(f"owner not frozen for {page}")


def one_edit_candidates(surface: str, known: dict[str, str], counts: Counter[str], transform) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source, source_recipe in known.items():
        try:
            operation, old_char, new_char, edit_index = transform.one_edit(source, surface)
        except ValueError:
            continue
        prefix = 0
        while prefix < min(len(source), len(surface)) and source[prefix] == surface[prefix]:
            prefix += 1
        suffix = 0
        while (
            suffix < min(len(source), len(surface)) - prefix
            and source[len(source) - suffix - 1] == surface[len(surface) - suffix - 1]
        ):
            suffix += 1
        licensed_close = "YES" if source.endswith("dy") and source_recipe.split("+")[-1:] == ["DY"] else "NO"
        try:
            recipe, rule, reason = transform.transform_recipe(
                source, surface, source_recipe, licensed_close
            )
        except (AssertionError, KeyError, ValueError):
            continue
        rows.append({
            "source_surface": source,
            "source_recipe": source_recipe,
            "source_event_count": counts[source],
            "edit_operation": operation,
            "old_char": old_char,
            "new_char": new_char,
            "edit_index": edit_index,
            "shared_context_score": prefix + suffix,
            "candidate_recipe": recipe,
            "transform_rule": rule,
            "transform_reason": reason,
            "licensed_close_assumption": licensed_close,
        })
    return rows


def literal(recipe: str) -> str:
    return " · ".join(ATOM_VALUE.get(atom, f"[{atom}]") for atom in recipe.split("+"))


def assign_prose_blocks(source_rows: list[dict[str, str]]) -> dict[str, str]:
    counters: Counter[str] = Counter()
    result: dict[str, str] = {}
    current_page = ""
    current_block = ""
    for row in source_rows:
        page = row["page"]
        if page != current_page or row["paragraph_start"] == "1":
            counters[page] += 1
            current_page = page
            current_block = f"{page.upper()}_PROSE_{counters[page]:02d}"
        if not current_block:
            raise RuntimeError(f"prose block missing at {row['locus']}")
        result[row["locus"]] = current_block
    return result


def segment_statements(
    events: list[dict[str, object]], ignored_close_event_ids: set[str] | None = None,
) -> list[dict[str, object]]:
    ignored_close_event_ids = ignored_close_event_ids or set()
    statements: list[dict[str, object]] = []
    current: list[dict[str, object]] = []
    current_block = ""

    def flush(end_mode: str) -> None:
        nonlocal current
        if not current:
            return
        statement_id = f"G404-S{len(statements) + 1:03d}"
        for ordinal, event in enumerate(current, 1):
            event["statement_id"] = statement_id
            event["card_ordinal_in_statement"] = ordinal
        pages = {str(event["physical_page"]) for event in current}
        blocks = {str(event["prose_block_id"]) for event in current}
        owners = {str(event["owner_id"]) for event in current}
        registers = {str(event["register"]) for event in current}
        if len(pages) != 1 or len(blocks) != 1 or len(owners) != 1 or len(registers) != 1:
            raise RuntimeError(f"statement crosses frozen boundary: {statement_id}")
        atoms = [
            atom for event in current for atom in str(event["visible_recipe"]).split("+")
        ]
        actions = [atom for atom in atoms if atom in ACTIONS]
        arguments = [atom for atom in atoms if atom in {"AIIN", "AIN", "OR", "Y"}]
        relations = [atom for atom in atoms if atom in {"AL", "AR", "L", "AIR"}]
        grades = [atom for atom in atoms if atom in {"E", "EE", "EEE"}]
        color = "AMBER" if any(event["admission_color"] == "AMBER" for event in current) else "GREEN"
        statements.append({
            "statement_ordinal": len(statements) + 1,
            "statement_id": statement_id,
            "physical_page": next(iter(pages)),
            "source_page_values": "|".join(dict.fromkeys(str(event["source_page_value"]) for event in current)),
            "register": next(iter(registers)),
            "prose_block_id": next(iter(blocks)),
            "owner_id": next(iter(owners)),
            "owner_evidence": str(current[0]["owner_evidence"]),
            "locus_start": str(current[0]["locus"]),
            "locus_end": str(current[-1]["locus"]),
            "line_start": int(current[0]["line_number"]),
            "line_end": int(current[-1]["line_number"]),
            "crosses_physical_line": "YES" if current[0]["locus"] != current[-1]["locus"] else "NO",
            "event_count": len(current),
            "surface_sequence": " ".join(str(event["surface"]) for event in current),
            "recipe_sequence": " | ".join(str(event["visible_recipe"]) for event in current),
            "literal_core_sequence_de": " | ".join(str(event["literal_core_reading_de"]) for event in current),
            "action_chain_de": " > ".join(ACTIONS[action] for action in actions) or "BESITZERGETRAGEN",
            "argument_inventory_de": " | ".join(ATOM_VALUE[atom] for atom in arguments) or "KEIN_EXPLIZITES_ARGUMENT",
            "relation_inventory_de": " | ".join(ATOM_VALUE[atom] for atom in relations) or "KEINE_EXPLIZITE_RELATION",
            "grade_inventory_de": " | ".join(ATOM_VALUE[atom] for atom in grades) or "KEIN_EXPLIZITER_GRAD",
            "end_mode": end_mode,
            "admission_color": color,
            "microform_event_count": sum(event["admission_color"] == "AMBER" for event in current),
        })
        current = []

    for event in events:
        block = str(event["prose_block_id"])
        if current and block != current_block:
            flush("PROSE_BLOCK_OPEN_END")
        current_block = block
        current.append(event)
        atoms = str(event["visible_recipe"]).split("+")
        if atoms and atoms[-1] == "DY" and str(event["event_id"]) not in ignored_close_event_ids:
            flush("LICENSED_DY_CLOSE")
    flush("PROSE_BLOCK_OPEN_END")
    return statements


def build_factorized_attachments(
    statements: list[dict[str, object]], events: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_statement[str(event["statement_id"])].append(event)
    old_factorized = read_tsv(
        ROOT / "experiments/yolo/gdt402_factorized_scope_selector_head_license/artifacts/gdt402_4374_factorized_replay.tsv"
    )
    selector_pages: dict[str, set[str]] = defaultdict(set)
    selector_registers: dict[str, set[str]] = defaultdict(set)
    head_pages: dict[str, set[str]] = defaultdict(set)
    head_registers: dict[str, set[str]] = defaultdict(set)
    for row in old_factorized:
        selector_pages[row["selector_rule"]].add(row["physical_page"])
        selector_registers[row["selector_rule"]].add(row["register"])
        head_pages[row["action_core"]].add(row["physical_page"])
        head_registers[row["action_core"]].add(row["register"])

    attachments: list[dict[str, object]] = []
    for statement in statements:
        statement_events = by_statement[str(statement["statement_id"])]
        active: dict[str, object] | None = None
        for card_index, event in enumerate(statement_events, 1):
            atoms = str(event["visible_recipe"]).split("+")
            next_event = statement_events[card_index] if card_index < len(statement_events) else None
            next_atoms = str(next_event["visible_recipe"]).split("+") if next_event else []
            focus_seen: Counter[str] = Counter()
            for atom_index, focus in enumerate(atoms):
                if focus not in FOCI:
                    continue
                focus_seen[focus] += 1
                value, family = FOCI[focus]
                selection = choose_attachment(
                    focus, atom_index + 1, atoms, event, card_index, active,
                    next_event, next_atoms,
                )
                selector = selector_rule(focus, selection, atoms)
                duplicate_mode, duplicate_role, paired = duplicate_scope(atoms, atom_index, focus)
                action = str(selection["action"] or "OWNER")
                geometry = str(selection["class"])
                r_mode = str(selection["r_mode"])
                valid = (
                    selector in FIXED_SELECTORS
                    and geometry in FIXED_GEOMETRIES
                    and action in FIXED_HEADS
                    and r_mode in FIXED_R_TOPOLOGIES
                    and duplicate_mode in FIXED_DUPLICATE_MODES
                    and int(selection["lookahead"]) <= 1
                )
                page = str(statement["physical_page"])
                register = str(statement["register"])
                attachments.append({
                    "factorized_id": f"G404-A{len(attachments) + 1:05d}",
                    "statement_id": statement["statement_id"],
                    "event_id": event["event_id"],
                    "physical_page": page,
                    "register": register,
                    "prose_block_id": statement["prose_block_id"],
                    "owner_id": statement["owner_id"],
                    "card_ordinal_in_statement": card_index,
                    "surface": event["surface"],
                    "visible_recipe": event["visible_recipe"],
                    "focus_atom_ordinal": atom_index + 1,
                    "focus_occurrence_ordinal": focus_seen[focus],
                    "focus_core": focus,
                    "focus_value_de": value,
                    "focus_family": family,
                    "selector_rule": selector,
                    "attachment_geometry": geometry,
                    "selected_action_event_id": selection["source_event"],
                    "selected_action_card_ordinal": selection["source_card"],
                    "selected_action_atom_ordinal": selection["source_atom"],
                    "target_card_offset": int(selection["source_card"]) - card_index if int(selection["source_card"]) else 0,
                    "action_core": action,
                    "action_value_de": ACTIONS.get(action, "BESITZER"),
                    "head_kind": "OWNER_HEAD" if action == "OWNER" else "R_ACTION_HEAD" if action == "R" else "ORDINARY_ACTION_HEAD",
                    "r_topology": r_mode,
                    "duplicate_mode": duplicate_mode,
                    "duplicate_role": duplicate_role,
                    "paired_focus_atom_ordinal": paired,
                    "lookahead_cards": selection["lookahead"],
                    "owner_boundary_crossed": "NO",
                    "statement_boundary_crossed": "NO",
                    "selector_supported_outside_page": "YES" if selector_pages[selector] - {page} else "NO",
                    "selector_supported_outside_register": "YES" if selector_registers[selector] - {register} else "NO",
                    "head_supported_outside_page": "YES" if head_pages[action] - {page} else "NO",
                    "head_supported_outside_register": "YES" if head_registers[action] - {register} else "NO",
                    "event_admission_color": event["admission_color"],
                    "factorized_result": "PASS_FIXED_FACTORS" if valid else "RED_NEW_AXIS_OR_BOUNDARY",
                })
            active = active_after_card(atoms, event, card_index, active)
    return attachments


def image_expansion(owner_id: str) -> str:
    if owner_id.startswith("F1R_"):
        return "BILDLOKAL: kein sicherer Gegenstand; rubrizierter Textblock bleibt Besitzer"
    if owner_id == "F24V_WHOLE_PLANT":
        return "BILDLOKAL: abgebildete Ganzpflanze"
    if owner_id == "F81R_UPPER_POOL":
        return "BILDLOKAL: oberes Figurenbecken; keine Flussrichtung ergänzt"
    if owner_id == "F81R_LOWER_POOL":
        return "BILDLOKAL: unteres Figurenbecken; keine Verbindung zum oberen ergänzt"
    if owner_id == "F95V_WHOLE_PLANT":
        return "BILDLOKAL: abgebildete verzweigte Ganzpflanze"
    return "BILDLOKAL: Besitzer unbekannt"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_rows, guard_stats = guarded_source_rows()
    if len(source_rows) != 95 or guard_stats.get("selected") != 95:
        raise RuntimeError(f"unexpected source row count: {len(source_rows)} / {guard_stats}")

    old_rows = read_tsv(PASS1026)
    old_recipe_sets: dict[str, set[str]] = defaultdict(set)
    old_counts: Counter[str] = Counter()
    for row in old_rows:
        old_recipe_sets[row["surface"]].add(row["pass1026_recipe"])
        old_counts[row["surface"]] += 1
    if any(len(values) != 1 for values in old_recipe_sets.values()):
        raise RuntimeError("Pass-1026 violates one-surface/one-recipe")
    known = {surface: next(iter(values)) for surface, values in old_recipe_sets.items()}
    transform = load_transform_module()

    source_fields = list(source_rows[0])
    write_tsv(OUT / "gdt404_95_guarded_source_lines.tsv", source_rows, source_fields)
    write_tsv(
        OUT / "gdt404_image_first_owner_manifest.tsv", IMAGE_ROWS,
        ["physical_page", "image_url", "sha256", "width", "height", "neutral_visual_reading", "connection_constraint"],
    )
    write_tsv(
        OUT / "gdt404_random_selection.tsv",
        [{
            "seed_hex": SEED_HEX, "candidate_physical_page_count": 178,
            "draw_ordinal": index, "selected_physical_page": page,
            "resampled": "NO", "selection_order_locked": "YES",
        } for index, page in enumerate(SELECTED_PHYSICAL, 1)],
        ["seed_hex", "candidate_physical_page_count", "draw_ordinal", "selected_physical_page", "resampled", "selection_order_locked"],
    )

    events: list[dict[str, object]] = []
    prose_blocks = assign_prose_blocks(source_rows)
    unknown_occurrence_counts: Counter[str] = Counter()
    for source in source_rows:
        tokens = source["eva_clean"].split()
        if len(tokens) != int(source["token_count"]):
            raise RuntimeError(f"token mismatch at {source['locus']}")
        owner_id, owner_evidence, owner_subblock = owner_for(source)
        for ordinal, surface in enumerate(tokens, 1):
            event_id = f"G404-E{len(events) + 1:04d}"
            recipe = known.get(surface, "")
            if recipe:
                status = "EXACT_SURFACE_ONE_RECIPE"
                support = f"PASS1026::{surface}::{old_counts[surface]}_events"
                candidate_count = 1
                color = "GREEN"
                stop = "NONE"
            else:
                unknown_occurrence_counts[surface] += 1
                status = "PENDING_NEW_SURFACE_AUDIT"
                support = "PENDING"
                candidate_count = 0
                color = "PENDING"
                stop = "PENDING"
            events.append({
                "event_id": event_id,
                "physical_page": physical_page(source["page"]),
                "source_page_value": source["page"],
                "locus": source["locus"],
                "line_number": source["line_number"],
                "paragraph_start": source["paragraph_start"],
                "paragraph_end": source["paragraph_end"],
                "card_ordinal_in_line": ordinal,
                "surface": surface,
                "register": register_for(source["section"]),
                "prose_block_id": prose_blocks[source["locus"]],
                "owner_id": owner_id,
                "owner_evidence": owner_evidence,
                "owner_subblock": owner_subblock,
                "surface_status": status,
                "visible_recipe": recipe,
                "literal_core_reading_de": literal(recipe) if recipe else "",
                "recipe_support": support,
                "candidate_recipe_count": candidate_count,
                "admission_color": color,
                "stop_reason_code": stop,
            })

    novel_rows: list[dict[str, object]] = []
    selected_recipe: dict[str, str] = {}
    selected_support: dict[str, str] = {}
    selected_status: dict[str, str] = {}
    candidate_detail_rows: list[dict[str, object]] = []
    if set(MANUAL_NEW_RECIPE) != set(unknown_occurrence_counts):
        missing = sorted(set(unknown_occurrence_counts) - set(MANUAL_NEW_RECIPE))
        extra = sorted(set(MANUAL_NEW_RECIPE) - set(unknown_occurrence_counts))
        raise RuntimeError(f"manual new-surface inventory mismatch: missing={missing} extra={extra}")
    for surface in sorted(unknown_occurrence_counts):
        candidates = one_edit_candidates(surface, known, old_counts, transform)
        best_context = max((int(row["shared_context_score"]) for row in candidates), default=-1)
        candidates = [row for row in candidates if int(row["shared_context_score"]) == best_context]
        recipe_weight: Counter[str] = Counter()
        recipe_sources: dict[str, list[str]] = defaultdict(list)
        recipe_rules: dict[str, set[str]] = defaultdict(set)
        for candidate in candidates:
            recipe = str(candidate["candidate_recipe"])
            recipe_weight[recipe] += int(candidate["source_event_count"])
            recipe_sources[recipe].append(str(candidate["source_surface"]))
            recipe_rules[recipe].add(str(candidate["transform_rule"]))
            candidate_detail_rows.append({"target_surface": surface, **candidate})
        recipes = sorted(recipe_weight, key=lambda value: (-recipe_weight[value], value))
        choice = MANUAL_NEW_RECIPE[surface]
        if any(atom not in ATOM_VALUE for atom in choice.split("+")):
            bad = [atom for atom in choice.split("+") if atom not in ATOM_VALUE]
            raise RuntimeError(f"new atom in {surface}: {bad}")
        status = (
            "NEW_MICROFORM_OLD_FACTORS"
            if surface in AMBIGUOUS_NEW
            else "NEW_VISIBLE_COMPOSITION"
        )
        selected_recipe[surface] = choice
        selected_support[surface] = "|".join(sorted(recipe_sources.get(choice, []))) or "DIRECT_VISIBLE_SEGMENTATION"
        selected_status[surface] = status
        novel_rows.append({
            "surface": surface,
            "occurrence_count": unknown_occurrence_counts[surface],
            "one_edit_source_count": len(candidates),
            "best_shared_context_score": best_context,
            "distinct_candidate_recipe_count": len(recipes),
            "selected_recipe": choice,
            "selection_status": status,
            "manual_recipe_seen_in_one_edit_candidates": "YES" if choice in recipe_weight else "NO",
            "candidate_recipes_by_weight": " | ".join(f"{recipe}::{recipe_weight[recipe]}" for recipe in recipes),
            "supporting_surfaces_for_selection": "|".join(sorted(recipe_sources.get(choice, []))),
            "transform_rules_for_selection": "|".join(sorted(recipe_rules.get(choice, set()))),
        })

    for event in events:
        if event["visible_recipe"]:
            continue
        surface = str(event["surface"])
        if surface in selected_recipe:
            recipe = selected_recipe[surface]
            event["visible_recipe"] = recipe
            event["literal_core_reading_de"] = literal(recipe)
            event["surface_status"] = selected_status[surface]
            event["recipe_support"] = selected_support[surface]
            event["candidate_recipe_count"] = 1
            event["admission_color"] = "AMBER" if surface in AMBIGUOUS_NEW else "GREEN"
            event["stop_reason_code"] = "NEW_MICROFORM_OLD_FACTORS" if surface in AMBIGUOUS_NEW else "NONE"

    statements = segment_statements(events)
    attachments = build_factorized_attachments(statements, events)
    attachments_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for attachment in attachments:
        attachments_by_statement[str(attachment["statement_id"])].append(attachment)
    for statement in statements:
        rows = attachments_by_statement[str(statement["statement_id"])]
        selectors = list(dict.fromkeys(str(row["selector_rule"]) for row in rows))
        heads = list(dict.fromkeys(str(row["action_core"]) for row in rows))
        factorized_failures = sum(row["factorized_result"] != "PASS_FIXED_FACTORS" for row in rows)
        if factorized_failures:
            statement["admission_color"] = "RED"
        statement["focus_attachment_count"] = len(rows)
        statement["bounded_forward_count"] = sum(row["attachment_geometry"] == "BOUNDED_NEXT_CARD_ACTION" for row in rows)
        statement["owner_only_count"] = sum(row["attachment_geometry"] == "OWNER_ONLY" for row in rows)
        statement["selector_inventory"] = "|".join(selectors) or "NONE"
        statement["head_inventory"] = "|".join(heads) or "OWNER"
        statement["image_local_expansion_de"] = image_expansion(str(statement["owner_id"]))
        statement["scope_skeleton_de"] = (
            f"BESITZER[{statement['owner_id']}] > HANDLUNG[{statement['action_chain_de']}] > "
            f"ARG[{statement['argument_inventory_de']}] > REL[{statement['relation_inventory_de']}] > "
            f"GRAD[{statement['grade_inventory_de']}] > {statement['end_mode']}"
        )
        statement["factorized_result"] = (
            "PASS_FIXED_FACTORS" if factorized_failures == 0 else "RED_NEW_AXIS_OR_BOUNDARY"
        )

    ambiguous_close_ids = {
        str(event["event_id"])
        for event in events
        if event["surface_status"] == "NEW_MICROFORM_OLD_FACTORS"
        and str(event["visible_recipe"]).split("+")[-1] == "DY"
    }
    alternate_events = [dict(event) for event in events]
    alternate_statements = segment_statements(alternate_events, ambiguous_close_ids)
    alternate_attachments = build_factorized_attachments(alternate_statements, alternate_events)
    primary_by_focus = {
        (str(row["event_id"]), str(row["focus_core"]), str(row["focus_occurrence_ordinal"])): row
        for row in attachments
    }
    alternate_by_focus = {
        (str(row["event_id"]), str(row["focus_core"]), str(row["focus_occurrence_ordinal"])): row
        for row in alternate_attachments
    }
    if set(primary_by_focus) != set(alternate_by_focus):
        raise RuntimeError("amber-close sensitivity changed focus inventory")
    sensitivity_rows: list[dict[str, object]] = []
    for key in sorted(primary_by_focus):
        primary = primary_by_focus[key]
        alternate = alternate_by_focus[key]
        changed = any(
            str(primary[field]) != str(alternate[field])
            for field in (
                "selector_rule", "attachment_geometry",
                "selected_action_event_id", "selected_action_atom_ordinal",
                "action_core", "r_topology", "duplicate_mode",
            )
        )
        if not changed:
            continue
        sensitivity_rows.append({
            "event_id": key[0], "surface": primary["surface"],
            "focus_core": key[1], "focus_occurrence_ordinal": key[2],
            "primary_statement_id": primary["statement_id"],
            "merged_statement_id": alternate["statement_id"],
            "primary_selector": primary["selector_rule"],
            "merged_selector": alternate["selector_rule"],
            "primary_geometry": primary["attachment_geometry"],
            "merged_geometry": alternate["attachment_geometry"],
            "primary_action_event_id": primary["selected_action_event_id"],
            "merged_action_event_id": alternate["selected_action_event_id"],
            "primary_action_core": primary["action_core"],
            "merged_action_core": alternate["action_core"],
            "merged_factorized_result": alternate["factorized_result"],
        })

    event_fields = [
        "event_id", "physical_page", "source_page_value", "locus", "line_number",
        "paragraph_start", "paragraph_end", "card_ordinal_in_line", "surface",
        "register", "prose_block_id", "owner_id", "owner_evidence", "owner_subblock",
        "statement_id", "card_ordinal_in_statement",
        "surface_status", "visible_recipe", "literal_core_reading_de", "recipe_support",
        "candidate_recipe_count", "admission_color", "stop_reason_code",
    ]
    write_tsv(OUT / "gdt404_688_event_first_pass.tsv", events, event_fields)
    write_tsv(
        OUT / "gdt404_211_new_surface_audit.tsv", novel_rows,
        ["surface", "occurrence_count", "one_edit_source_count", "best_shared_context_score", "distinct_candidate_recipe_count", "selected_recipe", "selection_status", "manual_recipe_seen_in_one_edit_candidates", "candidate_recipes_by_weight", "supporting_surfaces_for_selection", "transform_rules_for_selection"],
    )
    write_tsv(
        OUT / "gdt404_one_edit_candidate_detail.tsv", candidate_detail_rows,
        ["target_surface", "source_surface", "source_recipe", "source_event_count", "edit_operation", "old_char", "new_char", "edit_index", "shared_context_score", "candidate_recipe", "transform_rule", "transform_reason", "licensed_close_assumption"],
    )

    statement_fields = list(statements[0])
    write_tsv(OUT / "gdt404_statement_edition.tsv", statements, statement_fields)
    attachment_fields = list(attachments[0])
    write_tsv(OUT / "gdt404_factorized_attachments.tsv", attachments, attachment_fields)
    if sensitivity_rows:
        write_tsv(
            OUT / "gdt404_amber_close_sensitivity.tsv",
            sensitivity_rows, list(sensitivity_rows[0]),
        )
    else:
        write_tsv(
            OUT / "gdt404_amber_close_sensitivity.tsv",
            [{
                "event_id": "NONE", "surface": "NONE", "focus_core": "NONE",
                "focus_occurrence_ordinal": 0, "primary_statement_id": "NONE",
                "merged_statement_id": "NONE", "primary_selector": "NONE",
                "merged_selector": "NONE", "primary_geometry": "NONE",
                "merged_geometry": "NONE", "primary_action_event_id": "NONE",
                "merged_action_event_id": "NONE", "primary_action_core": "NONE",
                "merged_action_core": "NONE", "merged_factorized_result": "PASS_FIXED_FACTORS",
            }],
            [
                "event_id", "surface", "focus_core", "focus_occurrence_ordinal",
                "primary_statement_id", "merged_statement_id", "primary_selector",
                "merged_selector", "primary_geometry", "merged_geometry",
                "primary_action_event_id", "merged_action_event_id",
                "primary_action_core", "merged_action_core", "merged_factorized_result",
            ],
        )

    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_surface[str(event["surface"])].append(event)
    recurrence_rows: list[dict[str, object]] = []
    for surface, selected in sorted(by_surface.items()):
        pages = sorted({str(event["physical_page"]) for event in selected})
        if len(pages) < 2:
            continue
        recipes = {str(event["visible_recipe"]) for event in selected}
        statuses = {str(event["surface_status"]) for event in selected}
        if len(recipes) != 1 or len(statuses) != 1:
            raise RuntimeError(f"cross-page surface not invariant: {surface}")
        recurrence_rows.append({
            "surface": surface, "event_count": len(selected),
            "physical_page_count": len(pages), "physical_pages": "|".join(pages),
            "surface_status": next(iter(statuses)),
            "visible_recipe": next(iter(recipes)),
            "portable_recipe_result": "SAME_RECIPE_ACROSS_RANDOM_PAGES",
        })
    write_tsv(
        OUT / "gdt404_cross_page_surface_recurrence.tsv",
        recurrence_rows, list(recurrence_rows[0]),
    )

    core_rows: list[dict[str, object]] = []
    for atom, value in ATOM_VALUE.items():
        selected_events = [
            event for event in events if atom in str(event["visible_recipe"]).split("+")
        ]
        pages_with_atom = sorted({str(event["physical_page"]) for event in selected_events})
        if atom in ACTIONS:
            family = "ACTION_HEAD"
        elif atom in FOCI:
            family = FOCI[atom][1]
        elif atom in {"OL", "OT"}:
            family = "ORDER_CONTROL"
        elif atom in {"E", "EE", "EEE", "DY", "O", "CARRIER_Q", "IIN", "DA"}:
            family = "FORMAL_CONTROL"
        else:
            family = "LOCAL_OR_CLASS_SIGN"
        core_rows.append({
            "atom": atom, "working_value_de": value, "factor_family": family,
            "atom_occurrence_count": sum(str(event["visible_recipe"]).split("+").count(atom) for event in selected_events),
            "event_count": len(selected_events),
            "physical_page_count": len(pages_with_atom),
            "physical_pages": "|".join(pages_with_atom) or "NONE",
            "exact_known_event_count": sum(event["surface_status"] == "EXACT_SURFACE_ONE_RECIPE" for event in selected_events),
            "new_composition_event_count": sum(event["surface_status"] != "EXACT_SURFACE_ONE_RECIPE" for event in selected_events),
            "transfer_result": "OBSERVED_WITH_FIXED_VALUE" if selected_events else "ABSENT_FROM_RANDOM_BATCH",
        })
    write_tsv(
        OUT / "gdt404_core_transfer_summary.tsv", core_rows, list(core_rows[0]),
    )

    page_rows: list[dict[str, object]] = []
    for page in SELECTED_PHYSICAL:
        page_events = [event for event in events if event["physical_page"] == page]
        page_statements = [statement for statement in statements if statement["physical_page"] == page]
        page_attachments = [row for row in attachments if row["physical_page"] == page]
        page_color = (
            "RED" if any(statement["admission_color"] == "RED" for statement in page_statements)
            else "AMBER" if any(statement["admission_color"] == "AMBER" for statement in page_statements)
            else "GREEN"
        )
        page_rows.append({
            "physical_page": page,
            "register": "|".join(dict.fromkeys(str(event["register"]) for event in page_events)),
            "source_line_count": len({str(event["locus"]) for event in page_events}),
            "owner_count": len({str(event["owner_id"]) for event in page_events}),
            "prose_block_count": len({str(event["prose_block_id"]) for event in page_events}),
            "event_count": len(page_events),
            "unique_surface_count": len({str(event["surface"]) for event in page_events}),
            "exact_known_event_count": sum(event["surface_status"] == "EXACT_SURFACE_ONE_RECIPE" for event in page_events),
            "new_visible_composition_event_count": sum(event["surface_status"] == "NEW_VISIBLE_COMPOSITION" for event in page_events),
            "amber_microform_event_count": sum(event["surface_status"] == "NEW_MICROFORM_OLD_FACTORS" for event in page_events),
            "statement_count": len(page_statements),
            "licensed_close_statement_count": sum(statement["end_mode"] == "LICENSED_DY_CLOSE" for statement in page_statements),
            "open_end_statement_count": sum(statement["end_mode"] == "PROSE_BLOCK_OPEN_END" for statement in page_statements),
            "focus_attachment_count": len(page_attachments),
            "bounded_forward_count": sum(row["attachment_geometry"] == "BOUNDED_NEXT_CARD_ACTION" for row in page_attachments),
            "owner_only_count": sum(row["attachment_geometry"] == "OWNER_ONLY" for row in page_attachments),
            "selector_inventory": "|".join(sorted({str(row["selector_rule"]) for row in page_attachments})),
            "head_inventory": "|".join(sorted({str(row["action_core"]) for row in page_attachments})),
            "factorized_failure_count": sum(row["factorized_result"] != "PASS_FIXED_FACTORS" for row in page_attachments),
            "page_decision": page_color,
        })
    write_tsv(OUT / "gdt404_page_summary.tsv", page_rows, list(page_rows[0]))

    decision_rows = [
        {
            "priority": 1, "color": "GREEN", "code": "EXACT_SURFACE_ONE_RECIPE",
            "surface_count": len({str(event["surface"]) for event in events if event["surface_status"] == "EXACT_SURFACE_ONE_RECIPE"}),
            "event_or_attachment_count": sum(event["surface_status"] == "EXACT_SURFACE_ONE_RECIPE" for event in events),
            "decision": "READ_WITH_EXISTING_RECIPE",
        },
        {
            "priority": 2, "color": "GREEN", "code": "NEW_VISIBLE_COMPOSITION",
            "surface_count": sum(row["selection_status"] == "NEW_VISIBLE_COMPOSITION" for row in novel_rows),
            "event_or_attachment_count": sum(event["surface_status"] == "NEW_VISIBLE_COMPOSITION" for event in events),
            "decision": "COMPOSE_FROM_FIXED_CORE_VALUES",
        },
        {
            "priority": 3, "color": "AMBER", "code": "NEW_MICROFORM_OLD_FACTORS",
            "surface_count": sum(row["selection_status"] == "NEW_MICROFORM_OLD_FACTORS" for row in novel_rows),
            "event_or_attachment_count": sum(event["surface_status"] == "NEW_MICROFORM_OLD_FACTORS" for event in events),
            "decision": "KEEP_WORKING_RECIPE_AND_ALTERNATIVE_BOUNDARY_VISIBLE",
        },
        {
            "priority": 4, "color": "GREEN", "code": "PASS_FIXED_FACTORS",
            "surface_count": 0,
            "event_or_attachment_count": sum(row["factorized_result"] == "PASS_FIXED_FACTORS" for row in attachments),
            "decision": "KEEP_EIGHT_SELECTORS_SIX_GEOMETRIES_TEN_HEADS",
        },
        {
            "priority": 5, "color": "RED", "code": "NEW_AXIS_OR_BOUNDARY",
            "surface_count": 0,
            "event_or_attachment_count": sum(row["factorized_result"] != "PASS_FIXED_FACTORS" for row in attachments),
            "decision": "STOP_BATCH_IF_NONZERO",
        },
    ]
    write_tsv(OUT / "gdt404_admission_decisions.tsv", decision_rows, list(decision_rows[0]))

    readable: list[str] = [
        "# Vier zufällig gezogene Seiten: vollständige Kernlesung", "",
        f"Seed: `{SEED_HEX}`. Reihenfolge: `{' | '.join(SELECTED_PHYSICAL)}`.", "",
        "Die Zeilen unten sind keine Klartextübersetzung. Vor dem Gedankenstrich steht die vollständige sichtbare Kartenfolge; danach folgen nur die festen Kernwerte und eine getrennte Bildadresse.", "",
    ]
    for page in SELECTED_PHYSICAL:
        readable.extend([f"## {page}", ""])
        for statement in [row for row in statements if row["physical_page"] == page]:
            readable.extend([
                f"- **{statement['statement_id']}** (`{statement['surface_sequence']}`)",
                f"  - {statement['scope_skeleton_de']}",
                f"  - {statement['image_local_expansion_de']}",
                f"  - Ende: `{statement['end_mode']}`; Aufnahme: `{statement['admission_color']}`.",
            ])
        readable.append("")
    (HERE / "FOUR_RANDOM_PAGES_READABLE_CORE_EDITION.md").write_text(
        "\n".join(readable).rstrip() + "\n", encoding="utf-8"
    )

    summary = {
        "experiment_id": "GDT404",
        "seed_hex": SEED_HEX,
        "candidate_physical_page_count": 178,
        "selected_physical_pages": list(SELECTED_PHYSICAL),
        "source_page_values": list(SELECTED_VALUES),
        "guard_stats": guard_stats,
        "source_line_count": len(source_rows),
        "event_count": len(events),
        "unique_surface_count": len({str(event["surface"]) for event in events}),
        "exact_known_event_count": sum(event["surface_status"] == "EXACT_SURFACE_ONE_RECIPE" for event in events),
        "exact_known_surface_count": len({str(event["surface"]) for event in events if event["surface_status"] == "EXACT_SURFACE_ONE_RECIPE"}),
        "new_surface_count": len(novel_rows),
        "new_visible_composition_surface_count": sum(row["selection_status"] == "NEW_VISIBLE_COMPOSITION" for row in novel_rows),
        "amber_microform_surface_count": sum(row["selection_status"] == "NEW_MICROFORM_OLD_FACTORS" for row in novel_rows),
        "new_visible_composition_event_count": sum(event["surface_status"] == "NEW_VISIBLE_COMPOSITION" for event in events),
        "amber_microform_event_count": sum(event["surface_status"] == "NEW_MICROFORM_OLD_FACTORS" for event in events),
        "manual_recipe_supported_by_one_edit_count": sum(row["manual_recipe_seen_in_one_edit_candidates"] == "YES" for row in novel_rows),
        "unresolved_new_surface_count": sum(not row["selected_recipe"] for row in novel_rows),
        "prose_block_count": len({str(event["prose_block_id"]) for event in events}),
        "statement_count": len(statements),
        "licensed_close_statement_count": sum(statement["end_mode"] == "LICENSED_DY_CLOSE" for statement in statements),
        "open_end_statement_count": sum(statement["end_mode"] == "PROSE_BLOCK_OPEN_END" for statement in statements),
        "cross_line_statement_count": sum(statement["crosses_physical_line"] == "YES" for statement in statements),
        "focus_attachment_count": len(attachments),
        "scope_selector_count": len({str(row["selector_rule"]) for row in attachments}),
        "attachment_geometry_count": len({str(row["attachment_geometry"]) for row in attachments}),
        "action_head_count": len({str(row["action_core"]) for row in attachments}),
        "r_topology_count": len({str(row["r_topology"]) for row in attachments}),
        "duplicate_mode_count": len({str(row["duplicate_mode"]) for row in attachments}),
        "bounded_forward_count": sum(row["attachment_geometry"] == "BOUNDED_NEXT_CARD_ACTION" for row in attachments),
        "owner_only_count": sum(row["attachment_geometry"] == "OWNER_ONLY" for row in attachments),
        "maximum_lookahead_cards": max(int(row["lookahead_cards"]) for row in attachments),
        "owner_boundary_crossing_count": sum(row["owner_boundary_crossed"] != "NO" for row in attachments),
        "statement_boundary_crossing_count": sum(row["statement_boundary_crossed"] != "NO" for row in attachments),
        "factorized_failure_count": sum(row["factorized_result"] != "PASS_FIXED_FACTORS" for row in attachments),
        "cross_page_recurrent_surface_count": len(recurrence_rows),
        "cross_page_recurrent_new_surface_count": sum(row["surface_status"] != "EXACT_SURFACE_ONE_RECIPE" for row in recurrence_rows),
        "fixed_atom_inventory_count": len(core_rows),
        "observed_fixed_atom_count": sum(row["transfer_result"] == "OBSERVED_WITH_FIXED_VALUE" for row in core_rows),
        "ambiguous_close_event_count": len(ambiguous_close_ids),
        "ambiguous_close_primary_statement_count": len(statements),
        "ambiguous_close_merged_statement_count": len(alternate_statements),
        "ambiguous_close_changed_attachment_count": len(sensitivity_rows),
        "ambiguous_close_merged_factorized_failure_count": sum(
            row["factorized_result"] != "PASS_FIXED_FACTORS" for row in alternate_attachments
        ),
        "batch_decision": (
            "PASS_WITH_AMBER_MICROFORMS"
            if not any(row["factorized_result"] != "PASS_FIXED_FACTORS" for row in attachments)
            else "STOP_RED_FACTORIZED_FAILURE"
        ),
        "source_sha256": sha256(OUT / "gdt404_95_guarded_source_lines.tsv"),
        "upstream_pass1026_sha256": sha256(PASS1026),
    }
    write_json(OUT / "gdt404_first_pass_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
