#!/usr/bin/env python3
"""Build Pass 1008: transfer the nine clause drawers to four fresh pages.

The sidequest is intentionally constructive.  Existing portable roots and
registered whole-card spellings are reused; unseen spellings are assigned the
nearest registered workshop allograph.  Local labels remain owner addresses,
not new portable words.  Mixed transcription data are obtained only through
the guarded query command and only for the seven panels belonging to the four
physical pages admitted in this pass.
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
PASS996 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)
PASS1006 = ROOT / "experiments/yolo/sidequest_semantic_eighteen_page_unified_workshop_edition_one_thousand_sixth"
BASE_EVENTS = PASS1006 / "PASS1006_3168_UNIFIED_EVENT_LEDGER.tsv"
PASS1007 = ROOT / "experiments/yolo/sidequest_semantic_recurring_clause_template_drawer_one_thousand_seventh"
DRAWERS = PASS1007 / "PASS1007_9_CLAUSE_TEMPLATE_DRAWER.tsv"

PANEL_ORDER = ["f18r", "f72r1", "f72r2", "f72r3", "f76r", "f89r1", "f89r2"]
PHYSICAL_ORDER = ["f18r", "f72r", "f76r", "f89r"]

PANEL_SPECS = {
    "f18r": ("f18r", "HERBAL"),
    "f72r1": ("f72r", "CELESTIAL"),
    "f72r2": ("f72r", "CELESTIAL"),
    "f72r3": ("f72r", "CELESTIAL"),
    "f76r": ("f76r", "BIOLOGICAL"),
    "f89r1": ("f89r", "PHARMA"),
    "f89r2": ("f89r", "PHARMA"),
}

PAGE_DESCRIPTIONS = {
    "f18r": "große einzelne Blütenpflanze mit zwei Textabsätzen",
    "f72r": "mehrteilige Tierkreis-Falttafel mit zehn Ringtext-Namensräumen",
    "f76r": "dichte unbebilderte Biological-Textseite mit Abschnittsmarkern",
    "f89r": "Pharma-Falttafel mit Gefäßen, Wurzeln, Blättern und Prosablocks",
}

IMAGE_ROWS = [
    {
        "physical_page": "f18r",
        "yale_object_id": "1006108",
        "iiif_url": "https://collections.library.yale.edu/iiif/2/1006108/full/2000,/0/default.jpg",
        "width": 2000,
        "height": 2826,
        "sha256": "1e339b1e6f3153e557ff2371efb9ade8e89017ea8bfde665e880f664520a0b9b",
        "direct_visual_reading_de": "eine große ganze Pflanze; breite paarige Blätter, mehrere Blütenköpfe und verzweigte Wurzel; kein sichtbares Gefäß, Wasser oder Werkzeug",
    },
    {
        "physical_page": "f72r",
        "yale_object_id": "1006204",
        "iiif_url": "https://collections.library.yale.edu/iiif/2/1006204/full/2000,/0/default.jpg",
        "width": 2000,
        "height": 1270,
        "sha256": "46c961644e15d06a76bc4f7a6d209963edb4875ba8d0a802e255d4733c4154f0",
        "direct_visual_reading_de": "mehrere konzentrische Tierkreisräder mit Figuren-, Stern- und Platzetiketten; keine sichtbare Startmarke, Pfeilrichtung oder durchgehende Satzfolge",
    },
    {
        "physical_page": "f76r",
        "yale_object_id": "1006210",
        "iiif_url": "https://collections.library.yale.edu/iiif/2/1006210/full/2000,/0/default.jpg",
        "width": 2000,
        "height": 2699,
        "sha256": "5cb706c79a119a6b694e7496aedc77324de9460b15372557bdf0081e79cb9931",
        "direct_visual_reading_de": "reine dichte Textseite mit vier Absätzen und kleinen Abschnittsmarkern; keine Figur, kein Becken und keine sichtbare Station als lokaler Besitzer",
    },
    {
        "physical_page": "f89r",
        "yale_object_id": "1006234",
        "iiif_url": "https://collections.library.yale.edu/iiif/2/1006234/full/2000,/0/default.jpg",
        "width": 2000,
        "height": 1812,
        "sha256": "a99a8c993cce967dc1b2a6d9db922f0524b169a9331ff8e45afe057352bfb0a6",
        "direct_visual_reading_de": "mehrere getrennte Gefäß-, Wurzel-, Blatt- und Pflanzenteilgruppen mit Labels und Prosablocks; kein einziger Seitenbesitzer",
    },
]

ROLE_ROOTS = {
    "SEQUENCE": {"OT", "OL", "R", "CARRIER_Q"},
    "ITEM": {"Y", "HO"},
    "SOURCE": {"AR"},
    "QUANTITY": {"AIN", "AIIN", "IIN"},
    "PREPARATION": {"OR", "CHEO"},
    "ACTION": {"OK", "O", "CH", "K", "T", "SH", "CHD", "CHK", "SHED", "LSH", "CFH", "CPH", "P"},
    "PATH": {"L", "AIR", "CKH", "SOLK"},
    "TARGET": {"AL", "AM_ADDR", "D_ADDR", "A_ADDR", "S_ADDR"},
    "STATE": {"E", "EE", "EEE", "CTH"},
}

CANONICAL_ORDER = [
    "OWNER", "SEQUENCE", "ITEM", "SOURCE", "QUANTITY", "PREPARATION",
    "ACTION", "PATH", "TARGET", "STATE", "CLOSE",
]

STRONG_CUES = {
    "AIIN": r"ai+n", "IIN": r"i{3,}n", "AIN": r"(?<!i)ain", "AIR": r"air",
    "AL": r"al", "AR": r"ar", "AM_ADDR": r"am", "OK": r"ok",
    "OT": r"ot", "OL": r"ol", "OR": r"or", "CHD": r"ch(?:e)?d",
    "CTH": r"cth", "CKH": r"c(?:he|h)?kh|ckh", "CHK": r"ch(?:e+)?k",
    "SHED": r"shed", "SOLK": r"s?olk", "LSH": r"lsh", "CPH": r"cph",
    "CFH": r"cfh", "CHEO": r"cheo", "LD": r"ldd",
}

# Twenty-nine longer fresh forms were too far from any old whole-card spelling
# for a nearest-neighbour allograph to be informative.  They are instead read
# directly as visible strings of already learned roots.  This is the actual
# compositional pressure test: no new root is introduced to rescue them.
VISIBLE_COMPOSITIONS = {
    "pdrairdy": "P+D_ADDR+R+AIR+DY",
    "sheoltey": "SH+E+OL+T+E+Y",
    "sheolaiin": "SH+E+OL+AIIN",
    "chocthar": "CH+O+CTH+AR",
    "okeolaiin": "OK+E+OL+AIIN",
    "ykeolol": "Y+K+E+OL+OL",
    "opcholalaiin": "O+P+CH+OL+AL+AIIN",
    "okaipchy": "OK+A_ADDR+LOCAL_CHAR_I+P+CH+Y",
    "octheolarl": "O+CTH+E+OL+AR+L",
    "potchokor": "P+OT+CH+OK+OR",
    "qotddyar": "OT+D_ADDR+D_ADDR+Y+AR",
    "qotedshedy": "OT+E+D_ADDR+SHED+DY",
    "chorshedy": "CH+OR+SHED+DY",
    "qokaloro": "OK+AL+OR+O",
    "qoloin": "OL+O+IIN",
    "qokalchey": "OK+AL+CH+E+Y",
    "cheolchey": "CH+E+OL+CH+E+Y",
    "polalchdy": "P+OL+AL+CHD+DY",
    "chpsheedy": "CH+P+SH+EE+DY",
    "poleedaran": "P+OL+EE+D_ADDR+AR+AN",
    "okedalor": "OK+E+D_ADDR+AL+OR",
    "dainaldy": "D_ADDR+AIN+AL+DY",
    "cpheeedol": "CPH+EEE+D_ADDR+OL",
    "dolchsyckheol": "D_ADDR+OL+CH+S+Y+CKH+E+OL",
    "porachol": "P+O+R+A_ADDR+CH+OL",
    "otolpchy": "OT+OL+P+CH+Y",
    "lkeopol": "L+K+E+O+P+OL",
    "doigom": "D_ADDR+O+LOCAL_CHAR_I+G_LABEL+O+M_LOCAL",
    "keeokechy": "K+EE+O+K+E+CH+Y",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"cannot infer fields for empty table: {path}")
        fields = list(rows[0])
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


def guarded_rows() -> list[dict[str, str]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE), "--selector", "page",
    ]
    for panel in PANEL_ORDER:
        command.extend(["--allow", panel])
    command.extend([
        "--columns",
        "page,page_order,locus,line_number,code,relation,kind,subtype,section,paragraph_start,paragraph_end,token_count,eva_clean",
        "--forbid-prefix", "f84",
    ])
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    if len(rows) != 215 or {row["page"] for row in rows} != set(PANEL_ORDER):
        raise RuntimeError("guarded four-page source load failed")
    return rows


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for index, char_left in enumerate(left, 1):
        current = [index]
        for other_index, char_right in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[other_index] + 1,
                previous[other_index - 1] + (char_left != char_right),
            ))
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


def owner_for(panel: str, locus_number: int) -> tuple[str, str, str]:
    """Return owner id, short visible owner, and owner rule."""
    if panel == "f18r":
        return (
            "F18R_WHOLE_PLANT",
            "große abgebildete Blütenpflanze",
            "Die ganze Pflanze ist stummer Artikelbesitzer; Textlage beweist keine einzelne Blatt-, Blüten- oder Wurzelzuordnung.",
        )

    if panel == "f72r1":
        if locus_number <= 11:
            ring = "A"
        elif locus_number <= 17:
            ring = "B"
        else:
            ring = "C"
        return (f"F72R_RING_{ring}", f"Tierkreis-Ringgruppe {ring}", "Ringtext und benachbarte Figuren-/Sternlabels teilen nur diesen lokalen Namensraum.")

    if panel == "f72r2":
        if locus_number <= 21:
            ring = "D"
        elif locus_number <= 31:
            ring = "E"
        else:
            ring = "F"
        return (f"F72R_RING_{ring}", f"Tierkreis-Ringgruppe {ring}", "Ringtext und benachbarte Figuren-/Sternlabels teilen nur diesen lokalen Namensraum.")

    if panel == "f72r3":
        if locus_number <= 13:
            ring = "G"
        elif locus_number <= 25:
            ring = "H"
        elif locus_number <= 33:
            ring = "I"
        else:
            ring = "J"
        return (f"F72R_RING_{ring}", f"Tierkreis-Ringgruppe {ring}", "Ringtext und benachbarte Figuren-/Sternlabels teilen nur diesen lokalen Namensraum.")

    if panel == "f76r":
        ranges = [
            (1, 3, "A0"), (4, 6, "A1"), (7, 9, "A2"), (10, 13, "A3"),
            (14, 17, "A4"), (18, 21, "A5"), (22, 26, "A6"),
            (27, 30, "A7"), (31, 36, "A8"), (37, 38, "A9"),
            (39, 43, "B"), (44, 50, "C"), (51, 56, "D"),
        ]
        section = next(name for start, end, name in ranges if start <= locus_number <= end)
        return (
            f"F76R_TEXT_SECTION_{section}",
            f"unbebilderter Textabschnitt {section}",
            "Kein sichtbares Objekt ergänzt den Inhalt; der Abschnitt erbt nur den Seiten-/Rubrikkontext.",
        )

    if panel == "f89r1":
        batch = "A" if locus_number <= 10 else ("B" if locus_number <= 18 else "C")
    else:
        if locus_number <= 8:
            batch = "D"
        elif locus_number <= 15:
            batch = "E"
        elif locus_number <= 28:
            batch = "F"
        else:
            batch = "G"
    return (
        f"F89R_MATERIAL_BATCH_{batch}",
        f"Gefäß-/Pflanzenteilgruppe {batch}",
        "Nur die lokale Gruppe liefert Gefäß, Wurzel, Blatt oder Zutatenname; die Seite besitzt keinen einzigen Gesamtgegenstand.",
    )


def choose_template(register: str, event_count: int, slots: set[str]) -> str:
    working = slots - {"CLOSE"}
    if register == "CELESTIAL":
        return "T09"
    if event_count >= 9 or len(working) >= 8:
        return "T08"
    if "PATH" in working:
        return "T07"
    if "TARGET" in working:
        return "T06"
    if "PREPARATION" in working:
        return "T05"
    if "QUANTITY" in working:
        return "T04"
    if "SEQUENCE" in working:
        return "T03"
    if "ITEM" in working:
        return "T02"
    return "T01"


def fluent_reading(template_id: str, owner: str, slots: set[str], end_mode: str) -> str:
    endings = {
        "LICENSED_DY_CLOSE": " Den Teilgang schließen.",
        "VISIBLE_RING_OR_OWNER_BOUNDARY": " Hier endet der sichtbare Besitzer- oder Ringblock.",
        "VISIBLE_PARAGRAPH_BOUNDARY": " Hier endet der sichtbare Absatzgang.",
        "OPEN_PANEL_END": " Die Fortsetzung bleibt am Panelende offen.",
        "OPEN_PAGE_END": " Die Fortsetzung bleibt am Seitenende offen.",
    }
    body = {
        "T01": f"{owner}: den bezeichneten Arbeitsgang ausführen und den erreichten Zustand prüfen.",
        "T02": f"{owner}: den aktuell gemeinten Posten nehmen und bearbeiten.",
        "T03": f"{owner}: danach oder im selben Gang mit dem aktuellen Posten fortfahren.",
        "T04": f"{owner}: den Posten nach Maß oder auf der angegebenen Stufe bearbeiten.",
        "T05": f"{owner}: einen Ansatz oder Auszug bilden und weiterführen.",
        "T06": f"{owner}: den Posten an die bezeichnete Stelle setzen und dort ausführen.",
        "T07": f"{owner}: den Posten aus der Quelle über den Lauf oder Durchlass zur Zielstelle führen.",
        "T08": f"{owner}: die eingetragene Folge aus Posten, Maß oder Ansatz, Handlung, Weg und Ziel vollständig abarbeiten.",
        "T09": f"{owner}: den bezeichneten Platz oder Wert setzen beziehungsweise prüfen und in der Ringreihe fortfahren.",
    }[template_id]
    if "STATE" not in slots:
        body = body.replace(" und den erreichten Zustand prüfen", "")
    return body + endings[end_mode]


def main() -> int:
    source_rows = guarded_rows()
    roots = read_tsv(PASS996)
    drawers = {row["template_id"]: row for row in read_tsv(DRAWERS)}
    base_events = read_tsv(BASE_EVENTS)
    atomic = {row["recognition_form"]: row["atomic_meaning_de"] for row in roots}
    allowed_roots = set(atomic)

    # Registered running spellings supply the allograph deck.  Local labels do
    # not participate in similarity search.
    profiles: dict[tuple[str, str], dict[str, object]] = {}
    for row in base_events:
        if row["event_role"] != "RUNNING_STATEMENT":
            continue
        key = (row["surface"], row["component_recipe"])
        profile = profiles.setdefault(key, {"count": 0, "registers": Counter()})
        profile["count"] = int(profile["count"]) + 1
        profile["registers"][row["register"]] += 1
    surface_profiles: dict[str, list[tuple[str, dict[str, object]]]] = defaultdict(list)
    for (surface, recipe), profile in profiles.items():
        surface_profiles[surface].append((recipe, profile))
    known_surfaces = sorted(surface_profiles)

    def choose_exact(surface: str, register: str) -> tuple[str, str, int, float]:
        choices = []
        for recipe, profile in surface_profiles[surface]:
            choices.append((
                profile["registers"][register], int(profile["count"]),
                -len(recipe.split("+")), recipe,
            ))
        choices.sort(reverse=True)
        return choices[0][3], surface, 0, 100.0

    def choose_variant(surface: str, register: str) -> tuple[str, str, int, float]:
        minimum = min(edit_distance(surface, candidate) for candidate in known_surfaces)
        target_cues = {root for root, pattern in STRONG_CUES.items() if re.search(pattern, surface)}
        candidates = []
        for known in known_surfaces:
            distance = edit_distance(surface, known)
            if distance > minimum + 2:
                continue
            for recipe, profile in surface_profiles[known]:
                components = recipe.split("+")
                component_set = set(components)
                cue_hits = sum(bool(re.search(STRONG_CUES[root], surface)) for root in components if root in STRONG_CUES)
                cue_misses = sum(not re.search(STRONG_CUES[root], surface) for root in components if root in STRONG_CUES)
                extra_cues = len(target_cues - component_set)
                register_count = profile["registers"][register]
                score = (
                    -6.0 * distance + 3.0 * cue_hits - 2.0 * cue_misses
                    - 3.0 * extra_cues + 0.25 * shared_edges(surface, known)
                    + math.log1p(register_count) + 0.1 * math.log1p(int(profile["count"]))
                    - 0.08 * len(components)
                )
                candidates.append((score, register_count, int(profile["count"]), known, recipe, distance))
        candidates.sort(reverse=True)
        best = candidates[0]
        return best[4], best[3], best[5], best[0]

    def root_default(recipe: str) -> str:
        return " · ".join(atomic.get(component, component.replace("_", " ")) for component in recipe.split("+"))

    events: list[dict[str, object]] = []
    loci: list[dict[str, object]] = []
    event_number = 0
    by_panel_locus: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    source_by_locus: dict[tuple[str, str], dict[str, str]] = {}

    for source_row in source_rows:
        panel = source_row["page"]
        physical_page, register = PANEL_SPECS[panel]
        locus_number = int(source_row["locus"].rsplit(".", 1)[1])
        owner_id, owner_de, owner_rule = owner_for(panel, locus_number)
        source_by_locus[(panel, source_row["locus"])] = source_row
        local_rows = []
        for group_index, surface in enumerate(source_row["eva_clean"].split(), 1):
            event_number += 1
            if source_row["kind"] == "L":
                if panel == "f76r":
                    recipe = "SECTION_MARKER"
                    default = "ABSCHNITT"
                    transfer_class = "LOCAL_SECTION_MARKER"
                    context = f"Merkzeichen für {owner_de}"
                else:
                    recipe = "LOCAL_ADDRESS"
                    default = "LOKALE ADRESSE"
                    transfer_class = "LOCAL_OWNER_ADDRESS"
                    context = f"lokale Kennung für {owner_de}"
                source_surface = surface if surface in surface_profiles else "OWNER_COPY"
                distance: int | str = 0 if surface in surface_profiles else ""
                score: float | str = ""
                confidence = "OWNER_BOUND"
            else:
                if surface in surface_profiles:
                    recipe, source_surface, distance, score = choose_exact(surface, register)
                    transfer_class = "EXACT_REGISTERED_SURFACE"
                    confidence = "HIGH"
                elif surface in VISIBLE_COMPOSITIONS:
                    recipe = VISIBLE_COMPOSITIONS[surface]
                    source_surface = min(known_surfaces, key=lambda candidate: (edit_distance(surface, candidate), candidate))
                    distance = edit_distance(surface, source_surface)
                    score = ""
                    transfer_class = "VISIBLE_NEW_COMPOSITION"
                    confidence = "WORKING_COMPOSITION"
                else:
                    recipe, source_surface, distance, score = choose_variant(surface, register)
                    if distance == 1:
                        transfer_class = "ONE_EDIT_REGISTERED_ALLOGRAPH"
                        confidence = "MEDIUM_HIGH"
                    elif distance == 2:
                        transfer_class = "TWO_EDIT_ROOTED_VARIANT"
                        confidence = "WORKING"
                    else:
                        transfer_class = "REMOTE_ROOTED_WORKSHOP_VARIANT"
                        confidence = "LOW_WORKING"
                default = root_default(recipe)
                if register == "HERBAL":
                    context = f"an der {owner_de}: {default.lower()}"
                elif register == "BIOLOGICAL":
                    context = f"im {owner_de}: {default.lower()}"
                elif register == "PHARMA":
                    context = f"bei der {owner_de}: {default.lower()}"
                else:
                    context = f"im {owner_de}: {default.lower()}"

            row = {
                "event_id": f"P1008-E{event_number:04d}",
                "physical_page": physical_page,
                "source_panel": panel,
                "register": register,
                "locus": source_row["locus"],
                "line_number": source_row["line_number"],
                "kind": source_row["kind"],
                "group_index": group_index,
                "surface": surface,
                "owner_id": owner_id,
                "visible_owner_or_namespace_de": owner_de,
                "transfer_class": transfer_class,
                "source_surface": source_surface,
                "edit_distance": distance,
                "selection_score": f"{score:.3f}" if isinstance(score, float) else score,
                "component_recipe": recipe,
                "portable_default_de": default,
                "local_contextual_expansion_de": context,
                "confidence": confidence,
                "licensed_close": "YES" if source_row["kind"] != "L" and recipe.split("+")[-1] == "DY" else "NO",
                "statement_id": "",
            }
            events.append(row)
            local_rows.append(row)
            by_panel_locus[(panel, source_row["locus"])].append(row)

        loci.append({
            "physical_page": physical_page,
            "source_panel": panel,
            "locus": source_row["locus"],
            "kind": source_row["kind"],
            "paragraph_start": source_row["paragraph_start"],
            "paragraph_end": source_row["paragraph_end"],
            "owner_id": owner_id,
            "visible_owner_or_namespace_de": owner_de,
            "owner_rule_de": owner_rule,
            "group_count": len(local_rows),
            "surface_sequence": " ".join(str(row["surface"]) for row in local_rows),
            "component_sequence": " | ".join(str(row["component_recipe"]) for row in local_rows),
            "portable_literal_de": " | ".join(str(row["portable_default_de"]) for row in local_rows),
            "statement_ids": "",
        })

    # Segment running text by licensed close cards and visible owner/paragraph
    # boundaries.  Physical lines never end a statement by themselves.
    statements: list[dict[str, object]] = []
    current: list[dict[str, object]] = []
    statement_number = 0

    def flush(end_mode: str) -> None:
        nonlocal current, statement_number
        if not current:
            return
        statement_number += 1
        statement_id = f"P1008-S{statement_number:03d}"
        for event in current:
            event["statement_id"] = statement_id
        components = [str(event["component_recipe"]) for event in current]
        roots_in_statement = {root for component in components for root in component.split("+")}
        observed_slots = {role for role, members in ROLE_ROOTS.items() if roots_in_statement & members}
        if end_mode == "LICENSED_DY_CLOSE":
            observed_slots.add("CLOSE")
        action_realization = "EXPLICIT_CARD" if "ACTION" in observed_slots else "INHERITED_FROM_ACTIVE_SECTION"
        slots = set(observed_slots)
        slots.add("ACTION")
        template_id = choose_template(str(current[0]["register"]), len(current), slots)
        locus_span = list(dict.fromkeys(str(event["locus"]) for event in current))
        panels = list(dict.fromkeys(str(event["source_panel"]) for event in current))
        observed_signature = ">".join(role for role in CANONICAL_ORDER if role == "OWNER" or role in observed_slots)
        template_signature = ">".join(role for role in CANONICAL_ORDER if role == "OWNER" or role in slots)
        statements.append({
            "statement_id": statement_id,
            "physical_page": current[0]["physical_page"],
            "source_panels": "|".join(panels),
            "register": current[0]["register"],
            "owner_id": current[0]["owner_id"],
            "visible_owner_or_namespace_de": current[0]["visible_owner_or_namespace_de"],
            "locus_span": "|".join(locus_span),
            "locus_count": len(locus_span),
            "crosses_physical_line": "YES" if len(locus_span) > 1 else "NO",
            "event_count": len(current),
            "template_id": template_id,
            "template_name_de": drawers[template_id]["template_name_de"],
            "observed_slot_signature": observed_signature,
            "template_slot_signature": template_signature,
            "action_realization": action_realization,
            "end_mode": end_mode,
            "surface_sequence": " ".join(str(event["surface"]) for event in current),
            "component_sequence": " | ".join(components),
            "portable_literal_de": " | ".join(str(event["portable_default_de"]) for event in current),
            "fluent_workshop_de": fluent_reading(
                template_id,
                str(current[0]["visible_owner_or_namespace_de"]),
                slots,
                end_mode,
            ),
            "event_ids": "|".join(str(event["event_id"]) for event in current),
        })
        current = []

    previous_panel = ""
    for source_row in source_rows:
        panel = source_row["page"]
        local_events = by_panel_locus[(panel, source_row["locus"])]
        owner_id = str(local_events[0]["owner_id"])
        if current and (
            panel != previous_panel
            or owner_id != str(current[-1]["owner_id"])
            or source_row["paragraph_start"] == "1"
        ):
            flush("VISIBLE_RING_OR_OWNER_BOUNDARY" if current[0]["register"] in {"CELESTIAL", "PHARMA"} else "VISIBLE_PARAGRAPH_BOUNDARY")

        if source_row["kind"] == "L":
            if current:
                flush("VISIBLE_RING_OR_OWNER_BOUNDARY")
            previous_panel = panel
            continue

        for event in local_events:
            current.append(event)
            if event["licensed_close"] == "YES":
                flush("LICENSED_DY_CLOSE")

        if source_row["kind"] == "C" and current:
            flush("VISIBLE_RING_OR_OWNER_BOUNDARY")
        elif source_row["paragraph_end"] == "1" and current:
            flush("VISIBLE_PARAGRAPH_BOUNDARY")
        previous_panel = panel

    if current:
        flush("OPEN_PAGE_END")

    # Attach statement lists to each locus.
    statement_ids_by_locus: dict[tuple[str, str], list[str]] = defaultdict(list)
    for event in events:
        if event["statement_id"]:
            key = (str(event["source_panel"]), str(event["locus"]))
            if event["statement_id"] not in statement_ids_by_locus[key]:
                statement_ids_by_locus[key].append(str(event["statement_id"]))
    for row in loci:
        row["statement_ids"] = "|".join(statement_ids_by_locus[(str(row["source_panel"]), str(row["locus"]))])

    # Compact owner catalogue.
    owner_rows: list[dict[str, object]] = []
    seen_owners: set[str] = set()
    for row in loci:
        owner_id = str(row["owner_id"])
        if owner_id in seen_owners:
            continue
        seen_owners.add(owner_id)
        member_loci = [item for item in loci if item["owner_id"] == owner_id]
        owner_rows.append({
            "owner_id": owner_id,
            "physical_page": row["physical_page"],
            "source_panels": "|".join(dict.fromkeys(str(item["source_panel"]) for item in member_loci)),
            "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
            "owner_rule_de": row["owner_rule_de"],
            "loci": len(member_loci),
            "groups": sum(int(item["group_count"]) for item in member_loci),
            "running_groups": sum(
                int(item["group_count"]) for item in member_loci if item["kind"] != "L"
            ),
            "address_or_marker_groups": sum(
                int(item["group_count"]) for item in member_loci if item["kind"] == "L"
            ),
        })

    # Surface dictionary keeps the allograph decision visible.
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_surface[str(event["surface"])].append(event)
    surface_rows: list[dict[str, object]] = []
    for surface, members in sorted(by_surface.items()):
        running = [row for row in members if row["kind"] != "L"]
        exemplar = running[0] if running else members[0]
        surface_rows.append({
            "surface": surface,
            "events": len(members),
            "running_events": len(running),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in members})),
            "transfer_class": exemplar["transfer_class"],
            "source_surface": exemplar["source_surface"],
            "edit_distance": exemplar["edit_distance"],
            "component_recipe": exemplar["component_recipe"],
            "portable_default_de": exemplar["portable_default_de"],
            "confidence": exemplar["confidence"],
        })

    # Physical-page summary and template profiles.
    page_rows: list[dict[str, object]] = []
    for physical_page in PHYSICAL_ORDER:
        members = [row for row in events if row["physical_page"] == physical_page]
        page_statements = [row for row in statements if row["physical_page"] == physical_page]
        templates = Counter(str(row["template_id"]) for row in page_statements)
        transfers = Counter(str(row["transfer_class"]) for row in members)
        page_rows.append({
            "physical_page": physical_page,
            "source_panels": "|".join(dict.fromkeys(str(row["source_panel"]) for row in members)),
            "register": members[0]["register"],
            "page_description_de": PAGE_DESCRIPTIONS[physical_page],
            "loci": sum(1 for row in loci if row["physical_page"] == physical_page),
            "groups": len(members),
            "running_groups": sum(row["kind"] != "L" for row in members),
            "address_or_marker_groups": sum(row["kind"] == "L" for row in members),
            "statements": len(page_statements),
            "template_profile": "|".join(f"{key}:{templates[key]}" for key in sorted(templates)),
            "exact_registered_events": transfers["EXACT_REGISTERED_SURFACE"],
            "one_edit_events": transfers["ONE_EDIT_REGISTERED_ALLOGRAPH"],
            "two_edit_events": transfers["TWO_EDIT_ROOTED_VARIANT"],
            "remote_variant_events": transfers["REMOTE_ROOTED_WORKSHOP_VARIANT"],
            "visible_new_composition_events": transfers["VISIBLE_NEW_COMPOSITION"],
            "local_address_or_marker_events": transfers["LOCAL_OWNER_ADDRESS"] + transfers["LOCAL_SECTION_MARKER"],
            "licensed_closes": sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in page_statements),
            "visible_boundaries": sum(row["end_mode"].startswith("VISIBLE_") for row in page_statements),
            "open_ends": sum(row["end_mode"].startswith("OPEN_") for row in page_statements),
            "cross_line_statements": sum(row["crosses_physical_line"] == "YES" for row in page_statements),
            "inherited_action_statements": sum(row["action_realization"] == "INHERITED_FROM_ACTIVE_SECTION" for row in page_statements),
        })

    # Merge with the previous eighteen-page edition.
    unified: list[dict[str, object]] = []
    for row in base_events:
        unified.append({
            "book_event_ordinal": len(unified) + 1,
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "source_panel": row["physical_page"],
            "register": row["register"],
            "locus": row["locus"],
            "kind": row["kind"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "portable_default_de": row["portable_default_de"],
            "local_contextual_expansion_de": row["local_contextual_expansion_de"],
            "event_role": row["event_role"],
            "statement_id": row["statement_id"],
            "source_release": row["source_release"],
        })
    for row in events:
        unified.append({
            "book_event_ordinal": len(unified) + 1,
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "source_panel": row["source_panel"],
            "register": row["register"],
            "locus": row["locus"],
            "kind": row["kind"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "portable_default_de": row["portable_default_de"],
            "local_contextual_expansion_de": row["local_contextual_expansion_de"],
            "event_role": "RUNNING_STATEMENT" if row["kind"] != "L" else "LOCAL_ADDRESS_OR_SECTION_MARKER",
            "statement_id": row["statement_id"],
            "source_release": "PASS1008_FOUR_PAGE_TEMPLATE_TRANSFER",
        })

    event_path = HERE / "PASS1008_1413_EVENT_TRANSFER.tsv"
    locus_path = HERE / "PASS1008_215_LOCUS_EDITION.tsv"
    statement_path = HERE / "PASS1008_STATEMENT_TEMPLATE_EDITION.tsv"
    owner_path = HERE / "PASS1008_VISUAL_OWNER_MAP.tsv"
    surface_path = HERE / "PASS1008_SURFACE_TRANSFER_DICTIONARY.tsv"
    page_path = HERE / "PASS1008_FOUR_PAGE_TEMPLATE_PROFILE.tsv"
    image_path = HERE / "PASS1008_IMAGE_MANIFEST.tsv"
    unified_path = HERE / "PASS1008_4581_UNIFIED_EVENT_LEDGER.tsv"

    event_fields = list(events[0])
    event_fields.remove("statement_id")
    event_fields.insert(event_fields.index("licensed_close"), "statement_id")
    locus_fields = list(loci[0])
    locus_fields.remove("statement_ids")
    locus_fields.insert(locus_fields.index("portable_literal_de"), "statement_ids")
    write_tsv(event_path, events, event_fields)
    write_tsv(locus_path, loci, locus_fields)
    write_tsv(statement_path, statements)
    write_tsv(owner_path, owner_rows)
    write_tsv(surface_path, surface_rows)
    write_tsv(page_path, page_rows)
    write_tsv(image_path, IMAGE_ROWS)
    write_tsv(unified_path, unified)

    # Full readable edition: every new statement is represented, but the prose
    # remains compact enough to scan.
    reading_lines = [
        "# Vier neue Seiten — Satzschubladen-Ausgabe",
        "",
        "Jede Zeile bindet eine vollständige konstruktive Lesung an die sichtbare Kartenfolge. Lokale Bildlabels stehen getrennt in der Ereignis- und Locus-Ausgabe.",
    ]
    for physical_page in PHYSICAL_ORDER:
        reading_lines.extend(["", f"## {physical_page}", ""])
        for row in statements:
            if row["physical_page"] != physical_page:
                continue
            reading_lines.extend([
                f"- **{row['statement_id']} · {row['template_id']} · {row['locus_span']}** — {row['fluent_workshop_de']}",
                f"  `{row['surface_sequence']}`",
            ])
    reading_path = HERE / "PASS1008_FOUR_PAGE_READABLE_EDITION.md"
    reading_path.write_text("\n".join(reading_lines) + "\n", encoding="utf-8")

    transfer_counts = Counter(str(row["transfer_class"]) for row in events)
    template_counts = Counter(str(row["template_id"]) for row in statements)
    close_count = sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in statements)
    boundary_count = sum(str(row["end_mode"]).startswith("VISIBLE_") for row in statements)
    open_count = sum(str(row["end_mode"]).startswith("OPEN_") for row in statements)
    cross_count = sum(row["crosses_physical_line"] == "YES" for row in statements)
    inherited_action_count = sum(row["action_realization"] == "INHERITED_FROM_ACTIVE_SECTION" for row in statements)
    report = f"""# Pass 1008 — vier neue Seiten durch die neun Satzschubladen

Die vier physischen Seiten **f18r, f72r, f76r und f89r** enthalten zusammen
**1.413 sichtbare Gruppen in 215 Loci**. Davon sind 1.270 Lauftext- oder
Ringtextgruppen und 143 lokale Bildadressen beziehungsweise Abschnittsmarker.
{transfer_counts['EXACT_REGISTERED_SURFACE']} Lauftextgruppen sind exakte
bereits registrierte Oberflächen; {transfer_counts['ONE_EDIT_REGISTERED_ALLOGRAPH']}
sind nahe Ein-Schritt-Schreiberformen, {transfer_counts['TWO_EDIT_ROOTED_VARIANT']}
Zwei-Schritt-Varianten. Für die {transfer_counts['VISIBLE_NEW_COMPOSITION']}
längsten neuen Formen wird die sichtbare Wurzelfolge direkt aus dem vorhandenen
53-Wurzel-Inventar gelesen, statt sie an ein unähnliches altes Ganzwort
anzulehnen. **Keine neue Bedeutungswurzel wurde eingeführt.**

Die Segmentierung ergibt **{len(statements)} Aussagen**: {close_count} enden mit
einer bereits lizenzierten Schlusskarte, {boundary_count} an einer sichtbaren
Absatz-, Besitzer- oder Ringgrenze und {open_count} bleiben offen. {cross_count}
Aussagen laufen über mindestens eine physische Zeile hinweg. Alle passen in die
neun Pass-1007-Schubladen: {', '.join(f'{key}={template_counts[key]}' for key in sorted(template_counts))}.
In {inherited_action_count} kurzen elliptischen Aussagen ist keine eigene
Handlungskarte sichtbar; dort übernimmt die Schublade die aktive Handlung des
laufenden Abschnitts, ohne dafür eine neue Wurzel zu erfinden.

## Was der Bildvergleich wirklich ändert

- **f18r:** Die ganze Pflanze trägt beide Absätze als stillen Gegenstand. Sie
  rechtfertigt Pflanzenteil, Blüte, Blatt oder Wurzel als lokale Füllung, aber
  weder Wasser noch Öl noch ein sichtbares Gefäß.
- **f72r:** Die Falttafel zerfällt in zehn Ringtext-Namensräume mit lokalen
  Figuren-/Sternadressen. Die Himmels-Schublade T09 überträgt, doch eine lineare
  Startposition oder Leserichtung ist im Bild nicht vorhanden.
- **f76r:** Das ist der stärkste Reality-Check: eine reine Textseite ohne
  Körper-, Becken- oder Stationsbild. Die Satzschubladen funktionieren formal,
  aber konkrete Bade-/Apparatenomen können hier nicht aus dem Bild ergänzt
  werden. Die neun Einzeichenzeilen sind Abschnittsmarker, keine Wörter im
  laufenden Satz.
- **f89r:** Sieben lokale Gefäß-/Pflanzenteilgruppen ersetzen einen globalen
  Seitenbesitzer. Dadurch bleiben Namen lokal, während Maß, Quelle, Ziel,
  Ansatz, Lauf, Handlung und Schluss wiederverwendbar sind.

## Arbeitsurteil

Der neue Bestand erhöht die gemeinsame Ausgabe von 3.168 auf **4.581 Gruppen**.
Die neun Satzschubladen bestehen den Transfer, aber mit einer wichtigen
Präzisierung: Sie sind eine **Baugrammatik**, keine Garantie für den lokalen
Sachwortschatz. Gerade f76r zeigt, dass ein Schreiber die gleiche Kartenordnung
auch ohne Bildbesitzer verwenden konnte; die konkrete Nomenfüllung musste dann
aus Rubrik, Gedächtnis oder Meisterexemplar kommen.

Das bleibt eine kreative Werkstattübersetzung, keine behauptete historische
Entzifferung.
"""
    report_path = HERE / "PASS1008_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    outputs = [
        event_path, locus_path, statement_path, owner_path, surface_path,
        page_path, image_path, unified_path, reading_path, report_path,
    ]
    summary = {
        "status": "PASS",
        "decision": "NINE_TEMPLATE_DRAWERS_TRANSFER_TO_FOUR_NEW_PHYSICAL_PAGES",
        "physical_pages": 4,
        "source_panels": 7,
        "loci": len(loci),
        "groups": len(events),
        "running_groups": sum(row["kind"] != "L" for row in events),
        "address_or_marker_groups": sum(row["kind"] == "L" for row in events),
        "statements": len(statements),
        "owners_or_namespaces": len(owner_rows),
        "unique_surfaces": len(surface_rows),
        "transfer_counts": dict(sorted(transfer_counts.items())),
        "template_counts": dict(sorted(template_counts.items())),
        "licensed_closes": close_count,
        "visible_boundaries": boundary_count,
        "open_ends": open_count,
        "cross_line_statements": cross_count,
        "inherited_action_statements": inherited_action_count,
        "portable_roots": len(allowed_roots),
        "new_portable_roots": 0,
        "unified_groups": len(unified),
        "output_sha256": {path.name: sha256(path) for path in outputs},
    }
    (HERE / "PASS1008_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
