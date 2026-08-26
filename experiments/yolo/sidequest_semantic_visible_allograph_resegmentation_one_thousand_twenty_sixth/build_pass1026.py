#!/usr/bin/env python3
"""Build Pass 1026: decontaminate the old one-edit allograph assignments.

Pass 1008 copied the complete component recipe of the nearest registered
surface whenever a fresh form was one edit away.  Pass 1025 exposed two direct
failures of that shortcut.  This builder audits all 271 such events and treats
the edited visible sign as meaningful unless it belongs to a small licensed
renderer/package family.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1008 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_four_page_template_transfer_one_thousand_eighth"
    / "PASS1008_1413_EVENT_TRANSFER.tsv"
)
PASS1025 = ROOT / "experiments/yolo/sidequest_semantic_leave_one_register_replay_one_thousand_twenty_fifth"
CURRENT_EVENTS = PASS1025 / "PASS1025_3888_REGISTER_EVENT_REPLAY.tsv"


ATOM_VALUE = {
    "Y": "AKTIVER POSTEN",
    "OK": "SETZEN",
    "OL": "FORTSETZEN",
    "OT": "DANACH",
    "AL": "ZIELORT",
    "CH": "NEHMEN",
    "SH": "HALTEN",
    "AR": "AUSGANG",
    "K": "GEBEN",
    "AIIN": "WERT",
    "S": "WÄHLEN",
    "CHD": "UMSETZEN",
    "OR": "EINHEIT",
    "L": "VERBINDUNG",
    "T": "EINSTELLEN",
    "AIN": "ANTEIL",
    "R": "MARKIEREN",
    "P": "EINSETZEN",
    "AIR": "LAUF",
    "E": "GRAD I",
    "EE": "GRAD II",
    "EEE": "GRAD III",
    "DY": "SCHLUSS",
    "O": "AUSFÜHRUNG",
    "CARRIER_Q": "BEGINNMARKER",
    "IIN": "STUFE",
    "DA": "ZWEITE STUFE",
    "D_ADDR": "HIER",
    "AM_ADDR": "HIER",
    "A_ADDR": "HIER",
    "S_ADDR": "HIER",
    "LOCAL_CHAR_F": "HIER",
    "D_LABEL": "HIER",
    "S_LABEL": "HIER",
    "M_LOCAL": "HIER",
    "Z_ADDR": "HIER",
    "G_LABEL": "VARIANTE",
    "LOCAL_CHAR_G": "VARIANTE",
    "LOCAL_CHAR_I": "VARIANTE",
    "LOCAL_CHAR_B": "VARIANTE",
    "LOCAL_CHAR_J": "VARIANTE",
    "LOCAL_CHAR_Z": "VARIANTE",
    "HO": "KLASSE",
    "AN": "KLASSE",
    "OS": "VORBEZUG",
    "RESUME_CARD": "VORBEZUG",
}


# Direct package readings where a one-character edit crosses more than one
# old atom boundary.  These are short visible recipes, not contextual glosses.
MANUAL_RECIPE = {
    "cheo": "CH+E+O",
    "okeor": "OK+E+OR",
    "alchdy": "AL+CHD+DY",
    "dalaiin": "AL+AIIN",
    "daldal": "AL+AL",
    "daldaiin": "AL+AIIN",
    "doldaiin": "OL+AIIN",
    "doldy": "OL+DY",
    "qodaiin": "CARRIER_Q+O+AIIN",
    "chdam": "CHD+AM_ADDR",
    "cheodal": "CH+E+O+AL",
    "keodal": "K+E+O+AL",
    "qokeodal": "OK+E+O+AL",
    "sheodal": "SH+E+O+AL",
    "chaldy": "CH+AL+Y",
    "chealdy": "AL+Y",
    "choldy": "OL+Y",
    "qokaldy": "OK+AL+Y",
    "qockhedy": "O+CH+K+E+Y",
    "cheoldy": "CH+E+O+L+Y",
    "cheeody": "CH+EE+O+D_ADDR+Y",
    "ykeody": "Y+K+E+O+DY",
    "cheodain": "CH+E+O+D_ADDR+AIN",
    "che": "CH+E",
    "chep": "CH+E+P",
    "chepy": "CH+E+P+Y",
    "ckhal": "CH+K+AL",
    "ckhol": "CH+K+OL",
    "chykchy": "Y+K+CH+Y",
    "chckhol": "CH+K+OL",
    "chekaiin": "CH+K+AIIN",
    "cheok": "CH+E+O+K",
    "chokaiin": "OK+AIIN",
    "checkhey": "CH+E+CH+K+E+Y",
    "eteeey": "E+T+EEE+Y",
    "oeeor": "O+EE+OR",
    "okoiin": "OK+O+IIN",
    "okedor": "OK+E+D_ADDR+OR",
    "oldain": "OL+AIN",
    "oleeed": "OL+EEE+D_ADDR",
    "oteees": "OT+EEE+S_ADDR",
    "shetey": "SH+E+T+E+Y",
    "qokas": "OK+A_ADDR+S",
    "shoety": "SH+O+E+T+Y",
    "koey": "K+O+E+Y",
    "teo": "T+E+O",
    "alaiiin": "AL+AIIN+LOCAL_CHAR_I",
    "raiiin": "R+AIIN+LOCAL_CHAR_I",
    "daim": "A_ADDR+LOCAL_CHAR_I+M_LOCAL",
    "okaiir": "OK+IIN+R",
    "qoaiis": "CARRIER_Q+O+IIN+S",
    "opshdy": "O+P+SH+D_ADDR+Y",
    "chcphdy": "CH+CH+P+Y",
    "chead": "CH+E+A_ADDR+D_ADDR",
    "darod": "D_ADDR+AR+O+D_ADDR",
    "qokeodal": "OK+E+O+AL",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def one_edit(source: str, target: str) -> tuple[str, str, str, int]:
    if len(source) == len(target):
        changes = [index for index, pair in enumerate(zip(source, target)) if pair[0] != pair[1]]
        if len(changes) == 1:
            index = changes[0]
            return "SUB", source[index], target[index], index
    elif len(target) == len(source) + 1:
        for index in range(len(target)):
            if source[:index] + target[index + 1 :] == source:
                return "INS", "", target[index], index
    elif len(source) == len(target) + 1:
        for index in range(len(source)):
            if source[:index] + source[index + 1 :] == target:
                return "DEL", source[index], "", index
    raise ValueError(f"not one edit: {source!r} -> {target!r}")


def nearest_index(sequence: list[str], ratio: float, candidates: set[str]) -> int | None:
    positions = [index for index, atom in enumerate(sequence) if atom in candidates]
    if not positions:
        return None
    target = ratio * max(1, len(sequence) - 1)
    return min(positions, key=lambda index: abs(index - target))


def replace_near(
    sequence: list[str], old_atoms: set[str], new_atoms: list[str], ratio: float
) -> bool:
    index = nearest_index(sequence, ratio, old_atoms)
    if index is None:
        return False
    sequence[index : index + 1] = new_atoms
    return True


def insert_near(sequence: list[str], atom: str, ratio: float) -> None:
    index = max(0, min(len(sequence), round(ratio * len(sequence))))
    sequence.insert(index, atom)


def e_run_at(surface: str, index: int) -> int:
    probe = index if index < len(surface) and surface[index] == "e" else max(0, index - 1)
    while probe > 0 and surface[probe - 1] == "e":
        probe -= 1
    end = probe
    while end < len(surface) and surface[end] == "e":
        end += 1
    return end - probe


def changed_atom_delta(old_recipe: str, new_recipe: str) -> tuple[str, str]:
    old = old_recipe.split("+") if old_recipe else []
    new = new_recipe.split("+") if new_recipe else []
    rows = len(old) + 1
    cols = len(new) + 1
    lcs = [[0] * cols for _ in range(rows)]
    for left in range(len(old) - 1, -1, -1):
        for right in range(len(new) - 1, -1, -1):
            if old[left] == new[right]:
                lcs[left][right] = 1 + lcs[left + 1][right + 1]
            else:
                lcs[left][right] = max(lcs[left + 1][right], lcs[left][right + 1])
    left = right = 0
    removed: list[str] = []
    added: list[str] = []
    while left < len(old) and right < len(new):
        if old[left] == new[right]:
            left += 1
            right += 1
        elif lcs[left + 1][right] >= lcs[left][right + 1]:
            removed.append(old[left])
            left += 1
        else:
            added.append(new[right])
            right += 1
    removed.extend(old[left:])
    added.extend(new[right:])
    return "+".join(removed) or "NONE", "+".join(added) or "NONE"


def transform_recipe(
    source: str, target: str, source_recipe: str, licensed_close: str
) -> tuple[str, str, str]:
    """Return corrected target recipe, rule, and compact reason."""

    if target in MANUAL_RECIPE:
        return MANUAL_RECIPE[target], "DIRECT_VISIBLE_PACKAGE", "target package read directly"

    operation, old_char, new_char, index = one_edit(source, target)
    sequence = source_recipe.split("+")
    ratio = index / max(1, len(source))

    # The q wrapper is already absorbed into OK/OT/OL/OR families.  A q that
    # was itself an explicit BEGIN atom is not silently retained when deleted.
    if operation in {"INS", "DEL"} and (new_char == "q" or old_char == "q") and index == 0:
        if operation == "DEL" and "CARRIER_Q" in sequence:
            replace_near(sequence, {"CARRIER_Q"}, [], ratio)
            return "+".join(sequence), "VISIBLE_Q_REMOVAL", "explicit begin sign disappears"
        return source_recipe, "LICENSED_Q_WRAPPER", "q wrapper does not add an atom"

    # Two narrow workshop spellings really are allographic.
    if operation in {"INS", "DEL"} and (new_char == "e" or old_char == "e"):
        if re.sub("ched", "chd", source) == re.sub("ched", "chd", target):
            return source_recipe, "LICENSED_CHD_CHED", "expanded CHD spelling"
        if (
            re.sub("chek", "chk", source) == re.sub("chek", "chk", target)
            and not {"E", "EE", "EEE"}.intersection(sequence)
        ):
            return source_recipe, "LICENSED_CHK_CHEK", "expanded CHK spelling"
        if {source, target} == {"os", "oes"}:
            return source_recipe, "LICENSED_OS_OES", "same local previous-reference card"

    if operation == "INS":
        if new_char == "e":
            adjacent = (index > 0 and source[index - 1 : index] == "e") or source[index : index + 1] == "e"
            run = e_run_at(target, index)
            grade = {1: "E", 2: "EE", 3: "EEE"}.get(run, "EEE")
            if adjacent:
                if not replace_near(sequence, {"E", "EE", "EEE"}, [grade], ratio):
                    insert_near(sequence, grade, ratio)
            else:
                insert_near(sequence, "E", ratio)
            return "+".join(sequence), "VISIBLE_E_GRADE", "visible e changes the grade recipe"

        if new_char == "d":
            if index == 0 and target[1:].startswith(("al", "ol", "ain", "aiin")):
                return source_recipe, "LICENSED_D_FAMILY_WRAPPER", "initial d wraps AL/OL/AIN/AIIN"
            if target.endswith("dy") and index == len(target) - 2:
                if licensed_close == "YES":
                    replace_near(sequence, {"Y"}, ["DY"], 1.0)
                    return "+".join(sequence), "VISIBLE_DY_CLOSE", "d+y is licensed as close"
                return source_recipe, "LICENSED_OPEN_DY_WRAPPER", "d+y remains the open Y package"
            if target[index:].startswith(("dal", "dain", "daiin")):
                return source_recipe, "LICENSED_D_FAMILY_WRAPPER", "d wraps AL/AIN/AIIN"
            insert_near(sequence, "D_ADDR", ratio)
            return "+".join(sequence), "VISIBLE_D_ADDRESS", "visible d adds a local address"

        if new_char == "o" and index == 0 and source.startswith("t"):
            if not replace_near(sequence, {"T"}, ["OT"], 0.0):
                insert_near(sequence, "O", 0.0)
            return "+".join(sequence), "VISIBLE_OT_FRAME", "initial o turns T into OT"
        if new_char == "a" and index == 0 and source.startswith("l"):
            if not replace_near(sequence, {"L"}, ["AL"], 0.0):
                insert_near(sequence, "A_ADDR", 0.0)
            return "+".join(sequence), "VISIBLE_AL_FRAME", "initial a turns L into AL"
        if new_char == "h":
            if not replace_near(sequence, {"S"}, ["SH"], ratio):
                insert_near(sequence, "SH", ratio)
            return "+".join(sequence), "VISIBLE_SH_FRAME", "s+h carries the SH action"
        if new_char == "i":
            if "air" in target and "ar" in source:
                replace_near(sequence, {"AR"}, ["AIR"], ratio)
                return "+".join(sequence), "VISIBLE_AIR", "AR expands to AIR"
            insert_near(sequence, "LOCAL_CHAR_I", ratio)
            return "+".join(sequence), "VISIBLE_I_VARIANT", "extra i is a local variant mark"

        atom = {
            "a": "A_ADDR",
            "k": "K",
            "l": "L",
            "m": "M_LOCAL",
            "o": "O",
            "p": "P",
            "r": "R",
            "s": "S",
            "t": "T",
            "y": "Y",
        }[new_char]
        insert_near(sequence, atom, ratio)
        return "+".join(sequence), f"VISIBLE_INSERT_{new_char.upper()}", "inserted sign adds its atom"

    if operation == "DEL":
        if old_char == "e":
            adjacent = (index > 0 and target[index - 1 : index] == "e") or target[index : index + 1] == "e"
            grade_index = nearest_index(sequence, ratio, {"E", "EE", "EEE"})
            if grade_index is None:
                return source_recipe, "LICENSED_CONNECTIVE_E", "deleted e carried no separate grade"
            if adjacent:
                sequence[grade_index : grade_index + 1] = {
                    "EEE": ["EE"],
                    "EE": ["E"],
                    "E": [],
                }[sequence[grade_index]]
            else:
                sequence[grade_index : grade_index + 1] = []
            return "+".join(sequence), "VISIBLE_E_GRADE", "deleted e lowers or removes a grade"

        if old_char == "d":
            if index == 0 and source[1:].startswith(("al", "ol", "ain", "aiin")):
                return source_recipe, "LICENSED_D_FAMILY_WRAPPER", "initial d was only a family wrapper"
            if source.endswith("dy") and index == len(source) - 2:
                if replace_near(sequence, {"DY"}, ["Y"], 1.0):
                    return "+".join(sequence), "VISIBLE_REMOVE_CLOSE", "removing d opens DY to Y"
                replace_near(sequence, {"D_ADDR"}, [], ratio)
                return "+".join(sequence), "VISIBLE_REMOVE_D_ADDRESS", "visible local d disappears"
            replace_near(sequence, {"D_ADDR"}, [], ratio)
            return "+".join(sequence), "VISIBLE_REMOVE_D_ADDRESS", "visible local d disappears"

        if old_char == "y":
            if source.endswith("dy") and sequence[-1:] == ["DY"]:
                sequence[-1:] = ["D_ADDR"]
            else:
                replace_near(sequence, {"Y"}, [], ratio)
            return "+".join(sequence), "VISIBLE_REMOVE_Y", "visible active-posten sign disappears"

        if old_char == "i":
            if "air" in source and "ar" in target:
                replace_near(sequence, {"AIR"}, ["AR"], ratio)
            elif "aiin" in source and "ain" in target:
                replace_near(sequence, {"AIIN"}, ["AIN"], ratio)
            elif "iin" in source and "in" in target and "IIN" in sequence:
                return source_recipe, "LICENSED_SHORT_IIN", "short IIN spelling"
            else:
                replace_near(sequence, {"LOCAL_CHAR_I"}, [], ratio)
            return "+".join(sequence), "VISIBLE_I_CHANGE", "i change alters quantity/path/variant"

        if old_char == "o" and index == 0 and source.startswith("ot"):
            replace_near(sequence, {"OT"}, ["T"], 0.0)
            return "+".join(sequence), "VISIBLE_REMOVE_OT_FRAME", "OT loses its initial o"
        if old_char == "h":
            replace_near(sequence, {"SH"}, ["S"], ratio)
            return "+".join(sequence), "VISIBLE_REMOVE_H", "SH falls back to S"

        atom = {"k": "K", "l": "L", "o": "O", "p": "P", "r": "R", "t": "T"}[old_char]
        if old_char == "l" and not replace_near(sequence, {"L"}, [], ratio):
            replace_near(sequence, {"OL"}, ["O"], ratio)
        elif old_char == "o" and not replace_near(sequence, {"O"}, [], ratio):
            if not replace_near(sequence, {"OT"}, ["T"], ratio):
                if not replace_near(sequence, {"OL"}, ["L"], ratio):
                    replace_near(sequence, {"OR"}, ["R"], ratio)
        elif old_char == "r" and not replace_near(sequence, {"R"}, [], ratio):
            replace_near(sequence, {"OR"}, ["O"], ratio)
        else:
            replace_near(sequence, {atom}, [], ratio)
        return "+".join(sequence), f"VISIBLE_DELETE_{old_char.upper()}", "deleted sign removes its atom"

    # Substitutions are small root/grade/address replacements.
    assert operation == "SUB"
    if old_char == "o" and new_char == "a":
        if source[index : index + 2] == "ol":
            replace_near(sequence, {"OL"}, ["AL"], ratio)
        elif source[index : index + 2] == "or":
            replace_near(sequence, {"OR"}, ["AR"], ratio)
        elif re.search(r"ai+n", source[max(0, index - 1) :]):
            replace_near(sequence, {"AIIN", "AIN"}, ["O", "IIN"], ratio)
        elif not replace_near(sequence, {"O"}, ["A_ADDR"], ratio):
            insert_near(sequence, "A_ADDR", ratio)
    elif old_char == "a" and new_char == "o":
        if source[index : index + 2] == "al":
            replace_near(sequence, {"AL"}, ["OL"], ratio)
        elif source[index : index + 2] == "ar":
            replace_near(sequence, {"AR"}, ["OR"], ratio)
        elif re.search(r"ai+n", source[max(0, index - 1) :]):
            replace_near(sequence, {"AIIN", "AIN"}, ["O", "IIN"], ratio)
        elif not replace_near(sequence, {"A_ADDR"}, ["O"], ratio):
            insert_near(sequence, "O", ratio)
    elif (old_char, new_char) == ("k", "l"):
        if "ok" in source[max(0, index - 1) : index + 2] and "ol" in target[max(0, index - 1) : index + 2]:
            replace_near(sequence, {"OK"}, ["OL"], ratio)
        elif not replace_near(sequence, {"K"}, ["L"], ratio):
            insert_near(sequence, "L", ratio)
    elif (old_char, new_char) == ("l", "k"):
        if "ol" in source[max(0, index - 1) : index + 2] and "ok" in target[max(0, index - 1) : index + 2]:
            replace_near(sequence, {"OL"}, ["OK"], ratio)
        elif not replace_near(sequence, {"L"}, ["K"], ratio):
            insert_near(sequence, "K", ratio)
    elif (old_char, new_char) == ("l", "r"):
        if not (
            replace_near(sequence, {"AL"}, ["AR"], ratio)
            or replace_near(sequence, {"OL"}, ["OR"], ratio)
            or replace_near(sequence, {"L"}, ["R"], ratio)
        ):
            insert_near(sequence, "R", ratio)
    elif (old_char, new_char) == ("r", "l"):
        if not (
            replace_near(sequence, {"AR"}, ["AL"], ratio)
            or replace_near(sequence, {"OR"}, ["OL"], ratio)
            or replace_near(sequence, {"R"}, ["L"], ratio)
        ):
            insert_near(sequence, "L", ratio)
    elif (old_char, new_char) == ("c", "s"):
        if not (
            replace_near(sequence, {"CHD"}, ["SH", "E"], ratio)
            or replace_near(sequence, {"CH"}, ["SH"], ratio)
        ):
            insert_near(sequence, "SH", ratio)
    elif (old_char, new_char) == ("s", "c"):
        if not replace_near(sequence, {"SH"}, ["CH"], ratio):
            insert_near(sequence, "CH", ratio)
    elif old_char == "y":
        replacement = {"s": "S", "o": "O", "g": "LOCAL_CHAR_G", "p": "P"}[new_char]
        if not replace_near(sequence, {"Y", "DY"}, [replacement], ratio):
            insert_near(sequence, replacement, ratio)
    elif new_char == "y":
        old_atom = {"l": "L", "d": "D_ADDR", "o": "O"}.get(old_char, old_char.upper())
        if not replace_near(sequence, {old_atom}, ["Y"], ratio):
            insert_near(sequence, "Y", ratio)
    elif (old_char, new_char) == ("e", "o"):
        grade_index = nearest_index(sequence, ratio, {"E", "EE", "EEE"})
        if grade_index is None:
            insert_near(sequence, "O", ratio)
        elif sequence[grade_index] == "EE":
            sequence[grade_index : grade_index + 1] = ["O", "E"]
        elif sequence[grade_index] == "EEE":
            sequence[grade_index : grade_index + 1] = ["O", "EE"]
        else:
            sequence[grade_index] = "O"
    elif (old_char, new_char) == ("o", "e"):
        if not replace_near(sequence, {"O"}, ["E"], ratio):
            insert_near(sequence, "E", ratio)
    elif (old_char, new_char) == ("e", "d"):
        if "ched" in target:
            replace_near(sequence, {"CH"}, ["CHD"], ratio)
            replace_near(sequence, {"E", "EE", "EEE"}, [], ratio)
        elif target.endswith("dy") and licensed_close == "NO":
            replace_near(sequence, {"E", "EE", "EEE"}, [], ratio)
        else:
            grade_index = nearest_index(sequence, ratio, {"E", "EE", "EEE"})
            if grade_index is not None and sequence[grade_index] in {"EE", "EEE"}:
                sequence[grade_index : grade_index + 1] = [
                    {"EE": "E", "EEE": "EE"}[sequence[grade_index]],
                    "D_ADDR",
                ]
            elif grade_index is not None:
                sequence[grade_index] = "D_ADDR"
            else:
                insert_near(sequence, "D_ADDR", ratio)
    elif (old_char, new_char) == ("r", "d"):
        if not (
            replace_near(sequence, {"OR"}, ["O", "D_ADDR"], ratio)
            or replace_near(sequence, {"AR"}, ["A_ADDR", "D_ADDR"], ratio)
            or replace_near(sequence, {"R"}, ["D_ADDR"], ratio)
        ):
            insert_near(sequence, "D_ADDR", ratio)
    elif (old_char, new_char) == ("d", "p"):
        if not (
            replace_near(sequence, {"DY"}, ["P", "Y"], ratio)
            or replace_near(sequence, {"D_ADDR"}, ["P"], ratio)
        ):
            insert_near(sequence, "P", ratio)
    elif (old_char, new_char) == ("f", "e"):
        if not replace_near(sequence, {"LOCAL_CHAR_F"}, ["E"], ratio):
            insert_near(sequence, "E", ratio)
    elif (old_char, new_char) in {("t", "k"), ("k", "t"), ("k", "p"), ("p", "t"), ("k", "o"), ("o", "k")}:
        old_atom = {"t": "T", "k": "K", "p": "P", "o": "O"}[old_char]
        new_atom = {"t": "T", "k": "K", "p": "P", "o": "O"}[new_char]
        if not replace_near(sequence, {old_atom}, [new_atom], ratio):
            insert_near(sequence, new_atom, ratio)
    elif (old_char, new_char) == ("n", "m"):
        if not replace_near(sequence, {"AIIN", "AIN", "IIN"}, ["A_ADDR", "LOCAL_CHAR_I", "M_LOCAL"], ratio):
            insert_near(sequence, "M_LOCAL", ratio)
    elif (old_char, new_char) == ("n", "r"):
        if not replace_near(sequence, {"AIIN", "AIN", "IIN"}, ["IIN", "R"], ratio):
            insert_near(sequence, "R", ratio)
    elif (old_char, new_char) == ("n", "s"):
        if not replace_near(sequence, {"AIIN", "AIN", "IIN"}, ["IIN", "S"], ratio):
            insert_near(sequence, "S", ratio)
    elif (old_char, new_char) == ("q", "k"):
        if not replace_near(sequence, {"CARRIER_Q"}, ["K"], ratio):
            insert_near(sequence, "K", ratio)
    elif (old_char, new_char) == ("k", "q"):
        if not replace_near(sequence, {"K"}, ["CARRIER_Q"], ratio):
            insert_near(sequence, "CARRIER_Q", ratio)
    else:
        old_atom = {
            "a": "A_ADDR", "d": "D_ADDR", "e": "E", "h": "SH", "i": "LOCAL_CHAR_I",
            "l": "L", "m": "M_LOCAL", "o": "O", "p": "P", "q": "CARRIER_Q",
            "r": "R", "s": "S", "t": "T", "y": "Y",
        }.get(old_char, old_char.upper())
        new_atom = {
            "a": "A_ADDR", "d": "D_ADDR", "e": "E", "h": "SH", "i": "LOCAL_CHAR_I",
            "l": "L", "m": "M_LOCAL", "o": "O", "p": "P", "q": "CARRIER_Q",
            "r": "R", "s": "S", "t": "T", "y": "Y",
        }.get(new_char, new_char.upper())
        if not replace_near(sequence, {old_atom}, [new_atom], ratio):
            insert_near(sequence, new_atom, ratio)

    return "+".join(sequence), "VISIBLE_SUBSTITUTION", "substituted sign changes the visible atom"


def main() -> int:
    pass1008 = read_tsv(PASS1008)
    current_events = read_tsv(CURRENT_EVENTS)

    current_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in current_events:
        current_by_surface[row["surface"]].add(row["component_recipe"])
    if any(len(recipes) != 1 for recipes in current_by_surface.values()):
        raise RuntimeError("Pass 1025 is not surface-deterministic")
    canonical = {surface: next(iter(recipes)) for surface, recipes in current_by_surface.items()}

    targets = [row for row in pass1008 if row["transfer_class"] == "ONE_EDIT_REGISTERED_ALLOGRAPH"]
    if len(targets) != 271:
        raise RuntimeError(f"expected 271 one-edit events, got {len(targets)}")

    surface_decisions: dict[str, dict[str, object]] = {}
    audit_rows: list[dict[str, object]] = []
    for audit_number, row in enumerate(targets, 1):
        source_surface = row["source_surface"]
        target_surface = row["surface"]
        source_recipe = canonical.get(source_surface, row["component_recipe"])
        corrected, rule, reason = transform_recipe(
            source_surface, target_surface, source_recipe, row["licensed_close"]
        )
        if not corrected:
            raise RuntimeError(f"empty recipe for {target_surface}")
        operation, old_char, new_char, index = one_edit(source_surface, target_surface)
        removed, added = changed_atom_delta(source_recipe, corrected)
        old_current = canonical[target_surface]
        if corrected == source_recipe:
            decision = "LICENSED_SAME_RECIPE"
        elif corrected == old_current:
            decision = "CURRENT_ALREADY_REPAIRED"
        else:
            decision = "RESEGMENT_VISIBLE_EDIT"
        confidence = "HIGH" if rule.startswith(("LICENSED_", "DIRECT_", "VISIBLE_E_", "VISIBLE_DY_")) else "WORKING"

        existing = surface_decisions.get(target_surface)
        decision_payload = {
            "surface": target_surface,
            "old_current_recipe": old_current,
            "corrected_recipe": corrected,
            "audit_decision": decision,
            "rule": rule,
            "confidence": confidence,
        }
        if existing and existing["corrected_recipe"] != corrected:
            raise RuntimeError(
                f"source-dependent correction for {target_surface}: "
                f"{existing['corrected_recipe']} vs {corrected}"
            )
        surface_decisions[target_surface] = decision_payload

        audit_rows.append(
            {
                "audit_id": f"P1026-A{audit_number:04d}",
                "event_id": row["event_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": target_surface,
                "source_surface": source_surface,
                "edit_operation": operation,
                "old_char": old_char or "NONE",
                "new_char": new_char or "NONE",
                "edit_index": index,
                "source_current_recipe": source_recipe,
                "old_target_recipe": old_current,
                "corrected_recipe": corrected,
                "removed_atoms": removed,
                "added_atoms": added,
                "renderer_or_composition_rule": rule,
                "audit_decision": decision,
                "confidence": confidence,
                "short_reason": reason,
            }
        )

    surface_rows = sorted(surface_decisions.values(), key=lambda row: str(row["surface"]))

    corrected_events: list[dict[str, object]] = []
    affected_statements: set[str] = set()
    changed_event_count = 0
    for ordinal, row in enumerate(current_events, 1):
        decision = surface_decisions.get(row["surface"])
        corrected = str(decision["corrected_recipe"]) if decision else row["component_recipe"]
        if corrected != row["component_recipe"]:
            changed_event_count += 1
            affected_statements.add(row["statement_id"])
        atoms = corrected.split("+")
        missing = [atom for atom in atoms if atom not in ATOM_VALUE]
        if missing:
            raise RuntimeError(f"unmapped atoms for {row['surface']}: {missing}")
        corrected_events.append(
            {
                "pass1026_event_id": f"P1026-E{ordinal:04d}",
                "source_event_id": row["event_id"],
                "physical_page": row["physical_page"],
                "register": row["held_register"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": row["surface"],
                "pass1025_recipe": row["component_recipe"],
                "pass1026_recipe": corrected,
                "literal_core_reading_de": " · ".join(ATOM_VALUE[atom] for atom in atoms),
                "pass1026_change": "RESEGMENTED" if corrected != row["component_recipe"] else "UNCHANGED",
                "one_edit_audit_surface": "YES" if decision else "NO",
                "one_edit_rule": str(decision["rule"]) if decision else "NOT_IN_OLD_ONE_EDIT_SET",
            }
        )

    # Recheck the central invariant after applying the complete correction map.
    corrected_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in corrected_events:
        corrected_by_surface[str(row["surface"])].add(str(row["pass1026_recipe"]))
    if any(len(recipes) != 1 for recipes in corrected_by_surface.values()):
        raise RuntimeError("Pass 1026 introduced a surface-dependent recipe")

    statements: list[dict[str, object]] = []
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in corrected_events:
        by_statement[str(row["statement_id"])].append(row)
    for statement_id, rows in by_statement.items():
        if statement_id not in affected_statements:
            continue
        statements.append(
            {
                "statement_id": statement_id,
                "physical_page": rows[0]["physical_page"],
                "register": rows[0]["register"],
                "event_count": len(rows),
                "surface_sequence": " ".join(str(row["surface"]) for row in rows),
                "pass1025_recipe_sequence": " | ".join(str(row["pass1025_recipe"]) for row in rows),
                "pass1026_recipe_sequence": " | ".join(str(row["pass1026_recipe"]) for row in rows),
                "literal_core_reading_de": " / ".join(str(row["literal_core_reading_de"]) for row in rows),
                "changed_event_ids": "|".join(
                    str(row["source_event_id"]) for row in rows if row["pass1026_change"] == "RESEGMENTED"
                ),
            }
        )
    statements.sort(key=lambda row: int(str(row["statement_id"]).rsplit("S", 1)[1]))

    rule_counts = Counter(str(row["renderer_or_composition_rule"]) for row in audit_rows)
    decision_counts = Counter(str(row["audit_decision"]) for row in audit_rows)
    rule_rows = [
        {
            "rule": rule,
            "audited_event_count": count,
            "surface_count": sum(1 for row in surface_rows if row["rule"] == rule),
            "same_recipe_surface_count": sum(
                1 for row in surface_rows if row["rule"] == rule and row["audit_decision"] == "LICENSED_SAME_RECIPE"
            ),
            "resegmented_surface_count": sum(
                1 for row in surface_rows if row["rule"] == rule and row["audit_decision"] != "LICENSED_SAME_RECIPE"
            ),
        }
        for rule, count in sorted(rule_counts.items())
    ]

    write_tsv(
        HERE / "PASS1026_271_ONE_EDIT_EVENT_AUDIT.tsv",
        audit_rows,
        list(audit_rows[0]),
    )
    write_tsv(
        HERE / "PASS1026_226_SURFACE_RESEGMENTATION.tsv",
        surface_rows,
        ["surface", "old_current_recipe", "corrected_recipe", "audit_decision", "rule", "confidence"],
    )
    write_tsv(
        HERE / "PASS1026_EDIT_RULE_COUNTS.tsv",
        rule_rows,
        ["rule", "audited_event_count", "surface_count", "same_recipe_surface_count", "resegmented_surface_count"],
    )
    write_tsv(
        HERE / "PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv",
        corrected_events,
        list(corrected_events[0]),
    )
    write_tsv(
        HERE / "PASS1026_AFFECTED_STATEMENTS.tsv",
        statements,
        list(statements[0]),
    )

    summary = {
        "audited_one_edit_events": len(audit_rows),
        "audited_one_edit_surfaces": len(surface_rows),
        "audit_decision_event_counts": dict(sorted(decision_counts.items())),
        "surface_decision_counts": dict(sorted(Counter(str(row["audit_decision"]) for row in surface_rows).items())),
        "corrected_running_events": len(corrected_events),
        "changed_running_events": changed_event_count,
        "affected_statement_count": len(statements),
        "surface_determinism_conflicts": 0,
        "rule_count": len(rule_rows),
        "output_hashes": {},
    }
    for name in [
        "PASS1026_271_ONE_EDIT_EVENT_AUDIT.tsv",
        "PASS1026_226_SURFACE_RESEGMENTATION.tsv",
        "PASS1026_EDIT_RULE_COUNTS.tsv",
        "PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv",
        "PASS1026_AFFECTED_STATEMENTS.tsv",
    ]:
        summary["output_hashes"][name] = sha256(HERE / name)
    (HERE / "PASS1026_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
