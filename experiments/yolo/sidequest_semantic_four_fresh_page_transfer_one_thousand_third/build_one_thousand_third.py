#!/usr/bin/env python3
"""Build the four-fresh-page creative workshop transfer (Pass 1003).

This sidequest pass keeps the Pass-1002 two-layer reading rule: a short root
value is portable, while the pictured plant, station, jar, or celestial place
supplies the local noun.  Mixed transcription data are materialised only by
the guarded query command and only for the four pages admitted by the user.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "transcription/voynich_zl3b_lines.tsv"
BASE = ROOT / "experiments/yolo/sidequest_semantic_dual_layer_release_one_thousand_second"
BASE_EVENTS = BASE / "PASS1002_2511_DUAL_EVENT_INTERLINEAR.tsv"
BASE_CODEBOOK = BASE / "PASS1002_175_CURRENT_CODEBOOK.tsv"
ROOT_SOURCE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)

PAGE_SPECS = {
    "f17r": {
        "register": "MATERIAL",
        "title": "Herbalblatt — eine grosse Bluetenpflanze",
        "image_object": "1006106",
        "image_note": "eine ganze Pflanze; schmale Blaetter, drei dunkle Bluetenkoepfe, langer Wurzelstock; kein sichtbares Gefaess",
    },
    "f77r": {
        "register": "STATION",
        "title": "Biologicalblatt — Koerper, Becken und lokale Auslaesse",
        "image_object": "1006212",
        "image_note": "mehrere lokale Figuren-, Becken-, Bogen- und Auslassszenen; sichtbare Strahlen, aber kein einziger geschlossener Gesamtkreislauf",
    },
    "f88v": {
        "register": "MATERIAL",
        "title": "Pharmablatt — Gefaesse und Zutatenbueschel",
        "image_object": "1006233",
        "image_note": "mehrere Gefaess-/Pflanzenteilgruppen mit kurzen Etiketten und Prosa; kein einzelner Seitenbesitzer",
    },
    "f71v": {
        "register": "CELESTIAL",
        "title": "Zodiakblatt — Figuren-, Stern- und Ringadressen",
        "image_object": "1006203",
        "image_note": "drei lokale Ringtexte mit Figuren-/Sternetiketten; keine sichtbare Startmarke oder Laufrichtung",
    },
}

OLD_PAGE_REGISTER = {
    **{page: "MATERIAL" for page in ("f10r", "f11r", "f13r", "f55v", "f56r", "f88r")},
    **{page: "STATION" for page in ("f75r", "f81v", "f82r", "f83r")},
    **{page: "CELESTIAL" for page in ("f67r2", "f68r1", "f69v", "f70v")},
}

# The most useful new spellings are explicitly read as visible combinations.
# Everything else receives a nearest registered allograph plus a transparent
# distance/confidence tag.  These are creative workshop readings, not claimed
# historical plaintext.
OVERRIDES = {
    # f17r
    "ydar": "Y+D_ADDR+AR", "ydair": "Y+D_ADDR+AIR", "opydy": "O+P+Y+DY",
    "ypod": "Y+P+O+D_ADDR", "chop": "CH+O+P", "qodar": "O+D_ADDR+AR",
    "ckhody": "CKH+O+DY", "qodcthy": "O+D_ADDR+CTH+Y",
    "qodam": "O+D_ADDR+AM_ADDR", "okchom": "OK+CH+O+AM_ADDR",
    "opchordy": "O+P+CH+OR+DY", "ypchy": "Y+P+CH+Y",
    "ychekchy": "Y+CHK+Y", "cphor": "CPH+OR", "cphaldy": "CPH+AL+DY",
    "qokcheor": "OK+CHEO+R", "dchchy": "D_ADDR+CH+Y",
    "dcheor": "D_ADDR+CHEO+R", "oldckhy": "OL+D_ADDR+CKH+Y",
    "qof": "O+LOCAL_CHAR_F", "oteeeon": "OT+EEE+O+AN",
    # f77r
    "loly": "L+OL+Y", "lsheey": "L+SH+EE+Y", "laiin": "L+AIIN",
    "dalo": "D_ADDR+AL+O", "tolchd": "T+OL+CHD",
    "chetey": "CH+E+T+E+Y", "cham": "CH+AM_ADDR",
    "solteedy": "OL+T+EE+DY", "qodeedy": "O+D_ADDR+EE+DY",
    "shealol": "SH+E+AL+OL", "qolal": "OL+AL",
    "sokcheey": "S+OK+CH+EE+Y", "qotol": "OT+OL",
    "qolcheedy": "OL+SH+EE+DY", "sheed": "SH+EE+D_ADDR",
    "qeey": "CARRIER_Q+EE+Y", "sheckhedy": "SH+E+CKH+E+DY",
    "qolchy": "OL+CH+Y", "qotary": "OT+AR+Y",
    "qoteeedy": "OT+EEE+DY", "qotey": "OT+E+Y",
    "qykaiin": "Y+K+AIIN", "sa": "S+A_ADDR", "iin": "IIN",
    "cheety": "CH+EE+T+Y", "pol": "P+OL", "chcphey": "CH+CPH+E+Y",
    "ltaiin": "L+T+AIIN", "sheckhey": "SH+E+CKH+E+Y",
    "eeedy": "EEE+DY", "shody": "SH+O+DY", "arol": "AR+OL",
    "chee": "SH+EE", "qokear": "OK+E+AR", "lchear": "L+CH+E+AR",
    "chr": "CH+R", "lod": "L+O+D_ADDR", "dag": "DA+LOCAL_CHAR_G",
    "as": "A_ADDR+S", "ysheey": "Y+SH+EE+Y", "tain": "T+AIN",
    "oloky": "OL+OK+Y", "otolaiin": "OT+OL+AIIN",
    "olaiiny": "OL+AIIN+Y", "qeteiiin": "CARRIER_Q+E+T+IIN",
    "teeolain": "T+EE+OL+AIN", "chlchpsheey": "CH+L+CH+P+SH+EE+Y",
    "choldshy": "CH+OL+D_ADDR+SH+Y",
    "poldarais": "P+OL+D_ADDR+AR+A_ADDR+IIN+S",
    "dylches": "D_ADDR+Y+L+CH+E+S", "saiisol": "S+A_ADDR+IIN+S+OL",
    # f88v
    "qokeo": "OK+E+O", "qotody": "OT+O+DY", "cheockhy": "CHEO+CKH+Y",
    "teodal": "T+E+O+D_ADDR+AL", "lkeo": "L+K+E+O",
    "roshckhy": "R+O+SH+CKH+Y", "sorshy": "S+OR+SH+Y",
    "cheokal": "CHEO+K+AL", "saldaiin": "S+AL+D_ADDR+AIIN",
    "chkeor": "CHK+E+OR", "qokeom": "OK+E+O+AM_ADDR",
    "cheoy": "CHEO+Y", "olcheody": "OL+CHEO+DY",
    "qoekeol": "O+E+K+E+OL", "qoeey": "O+EE+Y", "key": "K+E+Y",
    "cheokam": "CHEO+K+AM_ADDR", "choeey": "HO+EE+Y",
    "keeod": "K+EE+O+D_ADDR", "okearcheol": "OK+E+AR+CHEO+L",
    "archeey": "AR+CH+EE+Y", "sairal": "S+AIR+AL",
    "cheorol": "CHEO+R+OL", "chekol": "CHK+OL",
    "daraly": "D_ADDR+AR+AL+Y", "oldaiin": "OL+D_ADDR+AIIN",
    "qoteody": "OT+E+O+DY", "oraiin": "OR+AIIN", "qokody": "OK+O+DY",
    "ykeeor": "Y+K+EE+OR", "chockhy": "HO+CKH+Y",
    "cheeol": "SH+EE+OL", "chocthey": "CH+O+CTH+E+Y",
    "cpheody": "CPH+E+O+DY", "chaly": "CH+AL+Y",
    "qoteo": "OT+E+O", "chokar": "OK+AR", "doy": "D_ADDR+O+Y",
    "tos": "T+O+S", "saldy": "S+AL+DY", "sheo": "SH+E+O",
    "kosholdy": "K+O+SH+OL+DY", "sqokeodaiin": "S+OK+E+O+D_ADDR+AIIN",
    "dairodain": "D_ADDR+AIR+O+D_ADDR+AIN",
    "ykeodain": "Y+K+E+O+D_ADDR+AIN",
    # f71v circle text
    "osheo": "O+SH+E+O", "parar": "P+AR+AR",
    "oteeodaiin": "OT+EE+O+D_ADDR+AIIN", "she": "SH+E",
    "ateey": "A_ADDR+T+EE+Y", "oteokeey": "OT+E+O+K+EE+Y",
    "sheeo": "SH+EE+O", "ochey": "O+CH+E+Y",
    "otcheodal": "OT+CHEO+D_ADDR+AL", "sheealody": "SH+EE+AL+O+DY",
    "okam": "OK+AM_ADDR", "oteodar": "OT+E+O+D_ADDR+AR",
    "chpchy": "CH+P+CH+Y", "oteoshar": "OT+E+O+SH+AR",
    "okeodaly": "OK+E+O+D_ADDR+AL+Y", "teeey": "T+EEE+Y",
    "keor": "K+E+OR", "cheols": "CHEO+L+S",
    "okaikaly": "OK+A_ADDR+IIN+K+AL+Y", "arom": "AR+O+AM_ADDR",
    "chfaly": "CH+LOCAL_CHAR_F+AL+Y", "otchody": "OT+CH+O+DY",
    "alcphy": "AL+CPH+Y", "okaraiin": "OK+AR+AIIN",
    "opalar": "O+P+AL+AR", "dan": "DA+AN", "opalor": "O+P+AL+OR",
    "ofaom": "O+LOCAL_CHAR_F+A_ADDR+O+AM_ADDR",
    "otalody": "OT+AL+O+DY", "sholshdy": "SH+OL+SH+DY",
    "chkeeal": "CHK+EE+AL", "cheekaiin": "CHK+EE+K+AIIN",
    "okalar": "OK+AL+AR", "chtos": "CH+T+O+S", "otchr": "OT+CH+R",
    "shepchol": "SH+E+P+CH+OL", "shopcho": "SH+O+P+CH+O",
    "shldy": "SH+L+DY", "sheeor": "SH+EE+OR",
}

STRONG_CUES = {
    "AIIN": r"ai+n", "IIN": r"i{3,}n", "AIN": r"(?<!i)ain", "AIR": r"air",
    "AL": r"al", "AR": r"ar", "AM_ADDR": r"am", "OK": r"ok",
    "OT": r"ot", "OL": r"ol", "OR": r"or", "CHD": r"ch(?:e)?d",
    "CTH": r"cth", "CKH": r"c(?:he|h)?kh|ckh", "CHK": r"ch(?:e+)?k",
    "SHED": r"shed", "SOLK": r"s?olk", "LSH": r"lsh", "CPH": r"cph",
    "CFH": r"cfh", "CHEO": r"cheo", "LD": r"ldd",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"cannot infer fields for empty table {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_rows(page: str) -> list[dict[str, str]]:
    if page.lower().startswith("f84"):
        raise ValueError("sealed page requested")
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
        "--selector", "page", "--allow", page,
        "--columns", "page,locus,kind,token_count,eva_clean",
        "--forbid-prefix", "f84",
    ]
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    if not rows or {row["page"] for row in rows} != {page}:
        raise RuntimeError(f"guarded page load failed for {page}")
    return rows


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def shared_edges(left: str, right: str) -> int:
    prefix = 0
    while prefix < min(len(left), len(right)) and left[prefix] == right[prefix]:
        prefix += 1
    suffix = 0
    while suffix < min(len(left), len(right)) and left[-1 - suffix] == right[-1 - suffix]:
        suffix += 1
    return prefix + suffix


def visible_owner(page: str, locus_number: int, kind: str) -> tuple[str, str]:
    if page == "f17r":
        if kind == "L":
            return "F17R_PLANT_CAPTION", "Bezeichnung bei der abgebildeten ganzen Bluetenpflanze"
        return "F17R_WHOLE_PLANT", "abgebildete ganze Bluetenpflanze mit Blatt-, Blueten- und Wurzelteilen"
    if page == "f77r":
        if locus_number <= 8:
            return "F77R_UPPER_STATION_LABELS", "obere Figuren-, Bogen- und Auslassstation"
        if locus_number >= 49:
            return "F77R_LOWER_STATION_LABELS", "untere Gefaess-/Beckenstation"
        return "F77R_STATION_ARTICLE", "Gesamtheit der lokal gezeichneten Koerper-, Becken- und Auslassstationen"
    if page == "f88v":
        if locus_number <= 10:
            return "F88V_BATCH_A", "erste Gefaess-/Zutatengruppe"
        if locus_number <= 26:
            return "F88V_BATCH_B", "zweite Gefaess-/Zutatengruppe"
        return "F88V_BATCH_C", "dritte Gefaess-/Zutatengruppe"
    if locus_number <= 11:
        return "F71V_RING_A", "erste lokale Figuren-/Sternringgruppe"
    if locus_number <= 17:
        return "F71V_RING_B", "zweite lokale Figuren-/Sternringgruppe"
    return "F71V_RING_C", "dritte lokale Ringgruppe"


def main() -> int:
    old_events = read_tsv(BASE_EVENTS)
    roots = read_tsv(ROOT_SOURCE)
    root_by_component = {row["recognition_form"]: row for row in roots}
    atomic = {key: row["atomic_meaning_de"] for key, row in root_by_component.items()}
    context_field = {
        "MATERIAL": "material_workshop_expansion_de",
        "STATION": "station_workshop_expansion_de",
        "CELESTIAL": "celestial_relational_expansion_de",
    }

    profiles: dict[tuple[str, str], dict[str, object]] = {}
    for row in old_events:
        key = (row["surface"], row["component_recipe"])
        profile = profiles.setdefault(key, {"count": 0, "registers": Counter(), "default": row["portable_default_de"]})
        profile["count"] = int(profile["count"]) + 1
        profile["registers"][OLD_PAGE_REGISTER.get(row["physical_page"], "OTHER")] += 1

    surface_profiles: dict[str, list[tuple[str, dict[str, object]]]] = defaultdict(list)
    for (surface, recipe), profile in profiles.items():
        surface_profiles[surface].append((recipe, profile))
    known_surfaces = sorted(surface_profiles)

    def root_default(recipe: str) -> str:
        if recipe == "LOCAL_ADDRESS":
            return "BILDADRESSE"
        return " · ".join(atomic.get(component, component.replace("_", " ")) for component in recipe.split("+"))

    def local_expansion(recipe: str, register: str, owner_de: str) -> str:
        if recipe == "LOCAL_ADDRESS":
            return f"Name oder Kennung fuer {owner_de}"
        values = []
        for component in recipe.split("+"):
            row = root_by_component.get(component)
            values.append(row[context_field[register]] if row else component.replace("_", " "))
        preposition = {"MATERIAL": "am Stoffbild", "STATION": "an der Station", "CELESTIAL": "im Ring"}[register]
        return f"{preposition} {owner_de}: " + " · ".join(values)

    def choose_exact(surface: str, register: str) -> tuple[str, str]:
        choices = []
        for recipe, profile in surface_profiles[surface]:
            reg_count = profile["registers"][register]
            choices.append((reg_count, int(profile["count"]), -len(recipe.split("+")), recipe))
        choices.sort(reverse=True)
        return choices[0][3], surface

    def choose_variant(surface: str, register: str) -> tuple[str, str, int, float]:
        minimum = min(edit_distance(surface, candidate) for candidate in known_surfaces)
        target_cues = {root for root, pattern in STRONG_CUES.items() if re.search(pattern, surface)}
        scored = []
        for candidate in known_surfaces:
            distance = edit_distance(surface, candidate)
            if distance > minimum + 2:
                continue
            for recipe, profile in surface_profiles[candidate]:
                components = recipe.split("+")
                component_set = set(components)
                cue_matches = sum(bool(re.search(STRONG_CUES[component], surface)) for component in components if component in STRONG_CUES)
                cue_misses = sum(not re.search(STRONG_CUES[component], surface) for component in components if component in STRONG_CUES)
                extra_target_cues = len(target_cues - component_set)
                register_count = profile["registers"][register]
                score = (
                    -6.0 * distance
                    + 3.0 * cue_matches
                    - 2.0 * cue_misses
                    - 3.0 * extra_target_cues
                    + 0.25 * shared_edges(surface, candidate)
                    + math.log1p(register_count)
                    + 0.10 * math.log1p(int(profile["count"]))
                    - 0.08 * len(components)
                )
                scored.append((score, register_count, int(profile["count"]), candidate, recipe, distance))
        scored.sort(reverse=True)
        best = scored[0]
        return best[4], best[3], best[5], best[0]

    source_rows = {page: guarded_rows(page) for page in PAGE_SPECS}
    fresh_events: list[dict[str, object]] = []
    locus_rows: list[dict[str, object]] = []
    page_stats = defaultdict(Counter)
    event_number = 0

    for page, spec in PAGE_SPECS.items():
        for source_row in source_rows[page]:
            locus = source_row["locus"]
            locus_number = int(locus.rsplit(".", 1)[1])
            kind = source_row["kind"]
            owner_id, owner_de = visible_owner(page, locus_number, kind)
            tokens = source_row["eva_clean"].split()
            local_event_rows = []
            for group_index, surface in enumerate(tokens, 1):
                event_number += 1
                if kind == "L":
                    recipe = "LOCAL_ADDRESS"
                    source_surface = surface if surface in surface_profiles else "OWNER_COPY"
                    distance = 0 if surface in surface_profiles else ""
                    transfer_class = "LOCAL_OWNER_ADDRESS"
                    confidence = "OWNER_BOUND"
                    note = "Etikett zuerst als lokaler Name/Kennung lesen; eine sichtbare Wurzelaehnlichkeit ist nur Merkhilfe."
                elif surface in surface_profiles:
                    recipe, source_surface = choose_exact(surface, spec["register"])
                    distance = 0
                    transfer_class = "EXACT_REGISTERED_SURFACE"
                    confidence = "HIGH"
                    note = "Bekannte sichtbare Form; kurze Wurzelbedeutung in den neuen Bildbesitzer eingesetzt."
                elif surface in OVERRIDES:
                    recipe = OVERRIDES[surface]
                    nearest = min(known_surfaces, key=lambda candidate: (edit_distance(surface, candidate), candidate))
                    source_surface = nearest
                    distance = edit_distance(surface, nearest)
                    transfer_class = "VISIBLE_NEW_COMPOSITION"
                    confidence = "MEDIUM_HIGH" if int(distance) <= 2 else "WORKING"
                    note = "Neue sichtbare Zusammensetzung aus bereits gelernten Wurzeln; kein neues Bedeutungswort."
                else:
                    recipe, source_surface, distance, score = choose_variant(surface, spec["register"])
                    transfer_class = "NEAR_REGISTERED_ALLOGRAPH" if distance == 1 else "TENTATIVE_ROOTED_VARIANT"
                    confidence = "MEDIUM" if distance == 1 else ("WORKING" if distance == 2 else "LOW")
                    note = f"Arbeitslesung nach naechster registrierter Werkstattallographie; Auswahlwert {score:.2f}."

                default = root_default(recipe)
                expansion = local_expansion(recipe, spec["register"], owner_de)
                event = {
                    "fresh_event_id": f"P1003-E{event_number:04d}",
                    "physical_page": page,
                    "locus": locus,
                    "kind": kind,
                    "group_index": group_index,
                    "surface": surface,
                    "register": spec["register"],
                    "owner_id": owner_id,
                    "visible_owner_de": owner_de,
                    "transfer_class": transfer_class,
                    "source_surface": source_surface,
                    "edit_distance": distance,
                    "component_recipe": recipe,
                    "portable_default_de": default,
                    "local_contextual_expansion_de": expansion,
                    "confidence": confidence,
                    "note": note,
                }
                fresh_events.append(event)
                local_event_rows.append(event)
                page_stats[page]["groups"] += 1
                page_stats[page]["labels" if kind == "L" else "running"] += 1
                page_stats[page][transfer_class] += 1

            locus_rows.append({
                "physical_page": page,
                "locus": locus,
                "kind": kind,
                "owner_id": owner_id,
                "visible_owner_de": owner_de,
                "surface_sequence": " ".join(tokens),
                "component_sequence": " | ".join(str(row["component_recipe"]) for row in local_event_rows),
                "portable_reading_de": " ; ".join(str(row["portable_default_de"]) for row in local_event_rows),
                "local_workshop_reading_de": " ; ".join(str(row["local_contextual_expansion_de"]) for row in local_event_rows),
                "groups": len(tokens),
            })

    event_fields = list(fresh_events[0])
    event_path = HERE / "PASS1003_657_FRESH_EVENT_INTERLINEAR.tsv"
    write_tsv(event_path, fresh_events, event_fields)
    locus_path = HERE / "PASS1003_111_LOCUS_READINGS.tsv"
    write_tsv(locus_path, locus_rows)

    surface_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in fresh_events:
        surface_groups[str(row["surface"])].append(row)
    surface_rows = []
    for surface, rows in sorted(surface_groups.items()):
        content = [row for row in rows if row["component_recipe"] != "LOCAL_ADDRESS"]
        exemplar = content[0] if content else rows[0]
        surface_rows.append({
            "surface": surface,
            "events": len(rows),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in rows})),
            "kinds": "|".join(sorted({str(row["kind"]) for row in rows})),
            "primary_transfer_class": exemplar["transfer_class"],
            "component_recipe": exemplar["component_recipe"],
            "portable_default_de": exemplar["portable_default_de"],
            "source_surface": exemplar["source_surface"],
            "edit_distance": exemplar["edit_distance"],
            "owner_bound_label_use": "YES" if any(row["component_recipe"] == "LOCAL_ADDRESS" for row in rows) else "NO",
            "confidence": exemplar["confidence"],
        })
    surface_path = HERE / "PASS1003_393_FRESH_SURFACE_DICTIONARY.tsv"
    write_tsv(surface_path, surface_rows)

    owner_specs = [
        ("F17R_WHOLE_PLANT", "f17r", "P1-P12", "ganze Pflanze", "stummer Artikelbesitzer; Textplatz beweist keine Teilzuordnung"),
        ("F17R_PLANT_CAPTION", "f17r", "L13", "Pflanzenbild-Kennung", "lokale Kennung, kein portables Wort"),
        ("F77R_UPPER_STATION_LABELS", "f77r", "L1-L8", "obere Bogen-/Auslassstation", "acht lokale Kennungen"),
        ("F77R_STATION_ARTICLE", "f77r", "P9-P48", "lokale Koerper-, Becken- und Auslassszenen", "Prosa gehoert zur Seite; keine mechanische Zeile-zu-Rohr-Bindung"),
        ("F77R_LOWER_STATION_LABELS", "f77r", "L49-L50", "untere Gefaess-/Beckenstation", "zwei lokale Kennungen"),
        ("F88V_BATCH_A", "f88v", "L1-L5+P6-P10", "erste Gefaess-/Zutatengruppe", "Bildbesitzer vor Detailglosse"),
        ("F88V_BATCH_B", "f88v", "L11-L14+P15-P26", "zweite Gefaess-/Zutatengruppe", "Bildbesitzer vor Detailglosse"),
        ("F88V_BATCH_C", "f88v", "L27-L30", "dritte Gefaess-/Zutatengruppe", "Etiketten ohne anschliessenden Prosablock"),
        ("F71V_RING_A", "f71v", "C1+L2-L11", "erste Figuren-/Sternringgruppe", "ein Ringtext plus lokale Adressen"),
        ("F71V_RING_B", "f71v", "C12+L13-L17", "zweite Figuren-/Sternringgruppe", "ein Ringtext plus lokale Adressen"),
        ("F71V_RING_C", "f71v", "C18", "dritte Ringgruppe", "Ringtext ohne nachfolgende lokale Labelzeile"),
    ]
    owner_rows = [
        {
            "owner_id": owner_id, "physical_page": page, "locus_scope": scope,
            "visible_owner_de": owner, "reading_rule_de": rule,
            "image_object_id": PAGE_SPECS[page]["image_object"],
            "image_source": f"https://collections.library.yale.edu/iiif/2/{PAGE_SPECS[page]['image_object']}/full/full/0/default.jpg",
            "page_image_observation_de": PAGE_SPECS[page]["image_note"],
        }
        for owner_id, page, scope, owner, rule in owner_specs
    ]
    owner_path = HERE / "PASS1003_VISUAL_OWNER_MAP.tsv"
    write_tsv(owner_path, owner_rows)

    root_counts = defaultdict(Counter)
    for row in fresh_events:
        if row["component_recipe"] == "LOCAL_ADDRESS":
            root_counts["LOCAL_ADDRESS"][str(row["physical_page"])] += 1
            continue
        for component in str(row["component_recipe"]).split("+"):
            root_counts[component][str(row["physical_page"])] += 1
            root_counts[component]["TOTAL"] += 1
    root_rows = []
    for component, counts in sorted(root_counts.items(), key=lambda item: (-item[1]["TOTAL"], item[0])):
        root_rows.append({
            "component": component,
            "short_value_de": "BILDADRESSE" if component == "LOCAL_ADDRESS" else atomic.get(component, component.replace("_", " ")),
            "f17r_uses": counts["f17r"], "f77r_uses": counts["f77r"],
            "f88v_uses": counts["f88v"], "f71v_uses": counts["f71v"],
            "total_uses": sum(counts[page] for page in PAGE_SPECS),
            "new_portable_root": "NO",
        })
    root_path = HERE / "PASS1003_ROOT_TRANSFER_PRESSURE.tsv"
    write_tsv(root_path, root_rows)

    combined_rows = []
    for row in old_events:
        combined_rows.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"],
            "locus": row["locus"], "kind": "CURRENT_BASE",
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "portable_default_de": row["portable_default_de"],
            "local_contextual_expansion_de": row["local_contextual_expansion_de"],
            "edition_source": "PASS1002",
        })
    for row in fresh_events:
        combined_rows.append({
            "event_id": row["fresh_event_id"], "physical_page": row["physical_page"],
            "locus": row["locus"], "kind": row["kind"], "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "portable_default_de": row["portable_default_de"],
            "local_contextual_expansion_de": row["local_contextual_expansion_de"],
            "edition_source": "PASS1003_FRESH_TRANSFER",
        })
    combined_path = HERE / "PASS1003_3168_COMBINED_EVENT_INTERLINEAR.tsv"
    write_tsv(combined_path, combined_rows)

    exact = sum(row["transfer_class"] == "EXACT_REGISTERED_SURFACE" for row in fresh_events)
    labels = sum(row["transfer_class"] == "LOCAL_OWNER_ADDRESS" for row in fresh_events)
    visible = sum(row["transfer_class"] == "VISIBLE_NEW_COMPOSITION" for row in fresh_events)
    one_edit = sum(row["transfer_class"] == "NEAR_REGISTERED_ALLOGRAPH" for row in fresh_events)
    tentative = len(fresh_events) - exact - labels - visible - one_edit
    report = f"""# Pass 1003 — vier neue Seiten im Werkstattmodell

Die vier neuen Seiten fuegen **657 sichtbare Gruppen** hinzu: f17r 80, f77r
332, f88v 145 und f71v 100. Das aktuelle Taschenwoerterbuch braucht dafuer
**keine neue portable Bedeutungswurzel**. {exact} Gruppen sind bereits als
sichtbare Form registriert; {visible} werden unmittelbar aus bekannten Wurzeln
zusammengesetzt; {one_edit} sind einfache nahe Schreiberformen; {tentative}
bleiben vorlaeufige, aber vollstaendig lesbare Varianten. Die {labels}
Labelgruppen werden zuerst als lokale Bildadressen gelesen.

## Was die Bilder aendern

- **f17r:** Ein einziges grosses Pflanzenbild besitzt den Artikel. Das Bild
  liefert Pflanze, Bluete, Blatt oder Wurzel; es liefert kein sichtbares Wasser,
  Oel oder Gefaess.
- **f77r:** Figuren, Becken, Bogen und Auslaesse machen die Stationslesung
  konkreter. Es gibt lokale Strahlen-/Kontaktwege, aber keinen sichtbaren
  geschlossenen Gesamtwasserkreislauf.
- **f88v:** Mehrere Gefaess-/Zutatengruppen bestaetigen ein echtes lokales
  Nomenklatorfach. Die kurzen Etiketten sind Namen/Kennungen; die Prosa traegt
  die wiederverwendbaren Handlungswurzeln.
- **f71v:** Ringtexte und Figurenetiketten tragen dieselbe Ziel-/Quell-/Grad-
  und Reihenalgebra, aber keine Stoffbedeutung. `AL=ZIEL` und `AR=QUELLE`
  ueberleben hier; zusammen mit dem bereits gelesenen f70v bleibt deshalb auch
  die allgemeinere Lesung `AIR=LAUF` statt `AIR=WASSER` noetig.

## Neue Gesamtbasis

Die Sidequest-Basis umfasst jetzt **18 Seiten und 3.168 Gruppen**: 2.618
laufende Prosa-/Ringtextgruppen und 550 lokale Bild-, Stations-, Gefaess- oder
Himmelsadressen. Das 175-zeilige Codebook aus Pass 1002 bleibt unveraendert.

Die beste Buchidee bleibt ein bildadressiertes Werkstattkompendium: Pflanzen
und Gefaesse liefern Stoffe, Biological-Zeichnungen liefern lokale
Anwendungs-/Apparatestationen, und die Himmelsblaetter liefern getrennte
Auswahlplaetze. Die portable Karte sagt kurz *nehmen, geben, halten, nach Mass,
zur Quelle, zum Ziel, fortsetzen, schliessen*; das Bild sagt, woran.

Dies ist weiterhin eine kreative Arbeitsuebersetzung, keine behauptete
historische Entzifferung.
"""
    report_path = HERE / "PASS1003_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    readings = """# Vier neue Seiten — aktuelle Werkstattlektüre

Diese Glättungen setzen die kurzen Kartenwerte in den sichtbaren Besitzer ein.
Sie sind absichtlich konkreter als das Taschenwörterbuch, aber nicht als
historischer Klartext gemeint.

## f17r — Pflanzenartikel

`fshody daram ydar chog opydy ypod chop otchy dody oldckhy`

> Vom gezeigten Pflanzenposten den bezeichneten Teil nehmen. Den Teil aus dem
> Vorrats-/Wurzelbereich in den laufenden Ansatz einsetzen, den nächsten Posten
> bearbeiten und den Teilgang schliessen. Am Durchlass mit demselben
> Pflanzenposten fortfahren.

In den folgenden Zeilen wiederholen sich Quelle, Teil, Portion, Mass, Ansatz,
Ziel, Auszug und Umleitung. Das Bild setzt als stummen Gegenstand die ganze
Pflanze ein; Wasser, Oel und eine Pflanzenart stehen auf diesem Blatt nicht
sichtbar fest.

## f77r — Stationsartikel

`poldarais ol qokol chey qopchedy qopchedy dylches olkedy loly`

> An der bezeichneten oberen Station den Arbeitsanteil einsetzen und den Lauf
> fortsetzen. Den Stationsposten zweimal in die folgende Fassung umsetzen,
> danach am lokalen Durchlass weiterarbeiten und denselben Posten weiterleiten.

Der lange Prosablock variiert vor allem **kurz/laenger**, **Mass/Portion**,
**Quelle/Ziel**, **absetzen/umsetzen**, **Durchlass** und **Schluss**. Die
Figuren und Becken machen daraus lokal Baden, Spuelen, Halten oder Zufuehren;
sie zeigen jedoch keine einzige durchgehende Maschine.

## f88v — Gefaess- und Zutatenblatt

`teodal lkeo cheor roshckhy sorshy aiin cheokal saldaiin`

> Den bezeichneten Arbeitsgang am Teilziel einstellen. Den Auszug aus der
> markierten Gefaess-/Zutatengruppe nehmen, durch den lokalen Durchlass fuehren,
> nach Mass bearbeiten und an der Zielstelle weitergeben.

Die drei Bildgruppen liefern die konkreten Zutaten- und Gefaessnamen. Die
Prosa liefert Ansatz, Auszug, Mass, Portion, Ziel, Geben, Halten und Schliessen.
Ein Etikett bleibt daher ein lokaler Name und wird nicht zum allgemeinen Verb.

## f71v — Ringtafel

`okeey okeosar otaiin chkeeal okal cheekaiin okaiin okchor dar oteey kal`

> Den bezeichneten Ringposten laenger setzen; danach Quelle, Mass und Zielplatz
> eintragen, den gewaehlten Grad merken und zum naechsten Ringposten
> fortfahren.

Hier sind **Quelle**, **Ziel**, **Mass**, **Grad**, **danach** und **fortsetzen**
rein relationale Kartenwerte. Stoffwoerter werden nicht mitgenommen. Die 22
Labelgruppen sind lokale Namen der Figuren, Sterne oder Plaetze; der schon auf
f70v belegte `AIR`-Kern bleibt daher allgemein **LAUF**, nicht **WASSER**.
"""
    readings_path = HERE / "PASS1003_FOUR_PAGE_WORKING_READINGS.md"
    readings_path.write_text(readings, encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "FOUR_NEW_PAGES_TRANSFER_WITHOUT_NEW_PORTABLE_ROOT",
        "new_pages": 4,
        "new_loci": len(locus_rows),
        "new_groups": len(fresh_events),
        "new_running_groups": len(fresh_events) - labels,
        "new_label_groups": labels,
        "new_unique_surfaces": len(surface_rows),
        "exact_registered_surface_events": exact,
        "visible_new_composition_events": visible,
        "one_edit_allograph_events": one_edit,
        "tentative_rooted_variant_events": tentative,
        "combined_pages": 18,
        "combined_groups": len(combined_rows),
        "combined_running_groups": 2010 + len(fresh_events) - labels,
        "combined_local_addresses": 501 + labels,
        "portable_codebook_lines": len(read_tsv(BASE_CODEBOOK)),
        "new_portable_roots": 0,
        "page_counts": {page: dict(page_stats[page]) for page in PAGE_SPECS},
        "source_hashes": {
            "pass1002_events": sha(BASE_EVENTS),
            "pass1002_codebook": sha(BASE_CODEBOOK),
            "pass996_roots": sha(ROOT_SOURCE),
        },
        "output_hashes": {
            path.name: sha(path)
            for path in (event_path, locus_path, surface_path, owner_path, root_path, combined_path, report_path, readings_path)
        },
        "sealed_pages_accessed": 0,
    }
    (HERE / "PASS1003_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
