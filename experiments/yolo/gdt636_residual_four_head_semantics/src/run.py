#!/usr/bin/env python3
"""Build GDT636: concrete compositional defaults for the residual four-head grid."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt636_residual_four_head_semantics")
ART = ROOT / BASE_REL / "artifacts"
G635_BASE = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps")
G635_RUN_REL = G635_BASE / "src/run.py"
G635_ALLOW_REL = G635_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G635_FOUR_WAY_REL = G635_BASE / "artifacts/FOUR_WAY_REMAINDER_ATLAS.tsv"
G635_DICT_REL = G635_BASE / "artifacts/WORKING_DICTIONARY_V12.tsv"
G635_RESULT_REL = G635_BASE / "artifacts/RESULT.json"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")

spec = importlib.util.spec_from_file_location("gdt635_builder", ROOT / G635_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT635 builder helpers")
g635 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g635)

HEAD_ORDER = ("p", "s", "r", "l")
HEAD_CLASS = {"p": "ENTRY", "s": "ENTRY", "r": "INGREDIENT", "l": "INGREDIENT"}
HEAD_NOUN = {
    "p": "Pulver", "s": "Samen/Saatgut", "r": "Wurzel/Wurzeldroge", "l": "Drogenholz",
}

RESIDUAL_ORDER = (
    "ar", "chey", "al", "y", "air", "chdy", "oiin", "shey", "am", "cheey",
    "chy", "olchedy", "chol", "odaiin", "oraiin", "ody", "cheo", "oaiin", "oral",
)

# These values are scoped to complete initial p/s/r/l+body forms.  An identical
# bare surface is never silently assigned the same value.
BODY_SPECS = {
    "ar": ("a+R[0 minims]", "Fraktionsklasse I", "PART_CLASS", "WORKING_MEDIUM",
           "unbezifferte Portion; bloßer A-R-Formcode",
           "ar→air→aiir minim ladder plus exact p/s frames; ar and or coexist in 48 lines"),
    "chey": ("ch+e+y", "Trockenform I", "DRY_STATE", "WORKING_HIGH",
             "Bindungsstufe I statt Sachform I",
             "inherited ch=trocken, e=attributive form I, y=base closure"),
    "al": ("a+L[0 minims]", "Rohstoffform I", "MATERIAL_CLASS", "WORKING_MEDIUM",
           "unangesetzter Rohstoff ohne numeral force",
           "inherited A-L material polarity; al and ol coexist in 20 lines"),
    "y": ("y", "unmarkierte Grundform", "BASE_STATE", "WORKING_MEDIUM",
          "form closure without lexical content",
          "inherited terminal-y base/result closure and 47 exact headed tokens"),
    "air": ("a+i+R", "Fraktionsklasse II", "PART_CLASS", "WORKING_MEDIUM",
            "local underground-part reading; A-R form II",
            "ar→air→aiir minim ladder; four-head distribution blocks root-only reading"),
    "chdy": ("ch+d+y", "getrocknete Kurz-/Kompaktform", "DRY_RESULT", "WORKING_HIGH",
             "resultative dry state without compactness",
             "inherited ch dry plus d-y result; five-state grid"),
    "oiin": ("o+iin", "Zubereitungsform III", "PREPARATION_CLASS", "WORKING_MEDIUM",
             "learned whole form; extract or decoction",
             "on/oin/oiin/oiiin ladder; o is the inherited preparation frame"),
    "shey": ("sh+e+y", "Feucht-/Einweichform I", "MOIST_STATE", "WORKING_HIGH",
             "moist attributive binding without numeral force",
             "inherited sh=feucht, e=form I, y=base closure"),
    "am": ("a+m", "Maß-/Einheitsform I; am Zeilenende Eintragsabschluss", "ENTRY_CLOSE", "STRUCTURAL_DEFAULT",
           "mischen/unterarbeiten; unbezifferte Schluss- oder Restmenge",
           "am/aim/aiim ladder and strong physical-line-final placement; p is the visible exception"),
    "cheey": ("ch+ee+y", "Trockenform II", "DRY_STATE", "WORKING_HIGH",
              "Bindungsstufe II statt Sachform II", "inherited ch=trocken and e/ee form ladder"),
    "chy": ("ch+y", "Trocken-Grundform", "DRY_STATE", "WORKING_HIGH",
            "ungraded dry state", "inherited ch dry plus y base closure"),
    "olchedy": ("ol+ch+e+d+y", "getrockneter Zubereitungsstoff", "DRIED_MATERIAL", "WORKING_HIGH",
                 "dry extract", "visible OL material carrier plus inherited dried-state body"),
    "chol": ("ch+ol", "trockener Stoff/Trockengut", "DRY_MATERIAL", "WORKING_HIGH",
             "dry quality without a nominal carrier", "inherited productive ch+OL quality/material form"),
    "odaiin": ("o+d+a+III", "Zubereitungsdosis III", "PREPARATION_DOSE", "WORKING_HIGH",
               "prepared state, degree III", "inherited o preparation plus explicit d+aIII dose series"),
    "oraiin": ("o+r+a+III", "Portion III", "PORTION_VALUE", "WORKING_HIGH",
               "nominal carrier, stage III", "inherited exact OR-value composition"),
    "ody": ("o+d+y", "aufbereitete/fertige Grundform", "PREPARED_RESULT", "WORKING_HIGH",
            "resultative preparation state", "o preparation plus d-y result; no k/t temperature head is present"),
    "cheo": ("ch+e+o", "trockene Zubereitung/Trockenansatz", "DRY_PREPARATION", "WORKING_HIGH",
             "dry o-frame form", "inherited ch dry, e binding and o preparation hierarchy"),
    "oaiin": ("o+a+III", "Zubereitungscharge III", "PREPARATION_VALUE", "WORKING_HIGH",
              "preparation amount III", "inherited o preparation plus aIII value series"),
    "oral": ("or+al", "Rohstoff-/Zutatenportion", "PORTIONED_MATERIAL", "WORKING_MEDIUM",
             "portionierter Stoff without numeral force",
             "composition of inherited OR part/portion and A-L material polarity"),
}

SLOT_ROWS = (
    ("p", "initial head", "Pulver/Pulverform", "only complete token-initial p+body"),
    ("s", "initial head", "Samen/Saatgut", "only complete token-initial s+body; sh excluded"),
    ("r", "initial head", "Wurzel/Wurzeldroge", "usually ingredient/internal head"),
    ("l", "initial head", "Drogenholz", "usually ingredient/internal head"),
    ("ch", "quality", "trocken", "inside registered ch-state and ch-material families"),
    ("sh", "quality", "feucht/eingeweicht", "inside registered sh-state families"),
    ("e/ee", "form ladder", "Form/Bindung I/II", "between quality head and y/o/result body"),
    ("y", "closure", "Grundform or result closure", "within registered state families"),
    ("d+y", "result", "resultative/finished state", "after quality or preparation head"),
    ("o", "preparation frame", "Zubereitung/Ansatz", "within registered o compounds"),
    ("a+minims", "value ladder", "class/quantity I-IV", "value depends on the visible carrier"),
    ("d+a+minims", "dose ladder", "dose/measure I-IV", "explicit dose head before a-value"),
    ("L", "carrier", "Stoff/Material", "A-L and OL material families only"),
    ("R", "carrier", "Teil/Portion", "A-R and OR part families only"),
    ("m", "boundary", "measure I or entry/charge close", "structural at line end; not a free noun"),
)

COEXISTENCE_SPECS = (
    ("ar", "or", "Fraktionsklasse I", "Teil-/Portionsträger", "48 shared lines force two distinct slots"),
    ("al", "ol", "Rohstoffform I", "allgemeines/zubereitetes Material", "20 shared lines force two distinct slots"),
    ("chey", "cheey", "Trockenform I", "Trockenform II", "the e/ee ladder remains contrastive"),
    ("chy", "chdy", "trockene Grundform", "durchgetrocknete Resultatform", "static and resultative dry forms coexist"),
    ("chdy", "chedy", "durchgetrocknete Kurzform", "getrockneter Zustand", "the compact and extended dry results coexist"),
    ("shey", "shedy", "feuchte Form I", "eingeweichter Resultatzustand", "moist state and soak result coexist"),
)

HISTORICAL_ROWS = (
    {
        "comparator_id": "WELLCOME_MS542_DEGREED_DRUGS",
        "date_place": "England, early fifteenth century", "source": "Wellcome MS.542",
        "url": "https://wellcomecollection.org/works/n674z2xd",
        "observed_architecture": "materia-medica entries combine radix/lignum labels with hot/dry qualities and numbered degrees",
        "use_here": "analogue for a compact drug-head + quality + grade field system, not a glyph key",
    },
    {
        "comparator_id": "HEIDELBERG_PAL_LAT_1234",
        "date_place": "central Europe, about 1400", "source": "Heidelberg Pal. lat. 1234",
        "url": "https://digi.ub.uni-heidelberg.de/diglit/bav_pal_lat_1234",
        "observed_architecture": "collection joins degrees of simples, compound medicines, dosage, oils and materia medica",
        "use_here": "genre-level analogue for mixed learned stems, quantities and preparation fields",
    },
    {
        "comparator_id": "WELLCOME_MS307_COMPACT_DOSE",
        "date_place": "northern Italy, late fourteenth century", "source": "Wellcome MS.307",
        "url": "https://wellcomecollection.org/works/rexwctzt",
        "observed_architecture": "recipes combine learned ingredient names, ana, compact numeric weights and seed vocabulary",
        "use_here": "analogue for learned whole forms plus abbreviated quantity fields in one recipe hand",
    },
    {
        "comparator_id": "SALZBURG_MI89_MIXED_HEADWORDS",
        "date_place": "Bavaria/Austria, turn of the fifteenth century", "source": "Salzburg UB M I 89",
        "url": "https://manuscripta.at/_scripts/php/msDescription2_m1_NEU.php?ID=8162&IDinitia=",
        "observed_architecture": "one technical compilation contains pulvis, semen and lignum drug vocabulary",
        "use_here": "analogue for coexistence of the proposed materia heads, not an identification",
    },
)

SPAN_SPECS = (
    ("AR_POWDER", "f86v6.17", 1, 3, ("par", "or", "aiin"),
     ("Pulverfraktion I", "Portion", "III"), "Pulverfraktion I; weitere Portion III."),
    ("AR_SEED", "f33v.9", 1, 3, ("sar", "or", "aiin"),
     ("Samenfraktion I", "Portion", "III"), "Samenfraktion I; weitere Portion III."),
    ("AR_MOIST", "f81v.1", 1, 2, ("par", "shey"),
     ("Pulverfraktion I", "feucht gebunden, Form I"), "Pulverfraktion I, anfeuchten/einweichen bis Form I."),
    ("AR_FINISHED", "f81r.24", 1, 2, ("par", "ody"),
     ("Pulverfraktion I", "fertig aufbereitet"), "Pulverfraktion I, fertig aufbereitet."),
    ("OIII_SEED", "f4r.12", 1, 3, ("soiin", "chaiin", "chaiin"),
     ("Samenzubereitung III", "trocken, Grad III", "trocken, Grad III"),
     "Samenzubereitung III; zweimal als trocken, Grad III, eingetragen."),
    ("DRY_DOSE_P", "f49r.12", 1, 5, ("podaiin", "cheo", "kcho", "daiin", "chcthy"),
     ("Pulverzubereitung, Dosis III", "Trockenansatz", "heiß-trockener Ansatz", "Dosis III", "trockenes Blatt-/Krautgut"),
     "Pulverzubereitung, Dosis III: Trockenansatz; heiß-trockener Ansatz, Dosis III, mit trockenem Blatt-/Krautgut."),
    ("DRY_DOSE_S", "f14r.13", 1, 4, ("sodaiin", "chy", "kchy", "kchy"),
     ("Samenzubereitung, Dosis III", "Trocken-Grundform", "heiß-trocken", "heiß-trocken"),
     "Samenzubereitung, Dosis III; trocken in Grundform, zweimal heiß-trocken markiert."),
    ("ROOT_PREP", "f106v.38", 8, 9, ("rody", "raiin"),
     ("aufbereitete Wurzel", "Wurzelcharge III"), "Aufbereitete Wurzel, Charge III."),
    ("DRY_P_ROOT_PORTION", "f106r.13", 8, 10, ("pcheo", "ror", "aiin"),
     ("trockener Pulveransatz", "Wurzelportion", "III"), "Trockener Pulveransatz mit Wurzelportion III."),
    ("OAIIN_CONTEXT", "f114v.33", 1, 4, ("kaiin", "sheey", "oaiin", "sheol"),
     ("heiß, Grad III", "feucht, Form II", "Zubereitungscharge III", "feuchtes Material"),
     "Heiß, Grad III; feucht in Form II; Zubereitungscharge III aus feuchtem Material."),
    ("ROOT_OIII_DOSE", "f77v.37", 5, 8, ("cheey", "roiin", "daiin", "shey"),
     ("trocken, Form II", "Wurzelzubereitung III", "Dosis III", "feucht, Form I"),
     "Wurzelzubereitung III, Dosis III: von Trockenform II in Feuchtform I."),
    ("DRIED_MATERIAL", "f83r.40", 1, 3, ("solchedy", "olchedy", "chedaiin"),
     ("getrockneter Samenstoff", "getrockneter Zubereitungsstoff", "Trockenansatz, Dosis III"),
     "Getrockneter Samenstoff; getrockneter Zubereitungsstoff; Trockenansatz, Dosis III."),
    ("WOOD_DRY_LADDER", "f114r.21", 1, 3, ("lcheey", "lchedo", "lcheo"),
     ("Drogenholz, Trockenform II", "getrocknete Holzform", "trockene Holzzubereitung"),
     "Drogenholz in Trockenform II; getrocknete Holzform; trockene Holzzubereitung."),
    ("SEED_INGREDIENT", "f77r.7", 1, 1, ("soral",),
     ("Samen-Rohstoffportion",), "Samen-Rohstoffportion."),
)

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "SLOT_COMPOSITION_MODEL.tsv", "MINIM_LADDER_EVIDENCE.tsv", "RESIDUAL_BODY_DEFAULTS.tsv",
    "RESIDUAL_76_FORM_GRID.tsv", "RESIDUAL_BODY_POSITION_PROFILE.tsv",
    "RESIDUAL_OCCURRENCE_CONTEXTS.tsv", "CONTRASTIVE_BODY_COEXISTENCE.tsv", "EXACT_RESIDUAL_NEIGHBOR_SWAPS.tsv",
    "CONCRETE_RESIDUAL_SPAN_TRANSLATIONS.tsv", "HISTORICAL_COMPOSITION_COMPARATORS.tsv",
    "WORKING_DICTIONARY_V13.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def counter_text(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def spec_fields(body: str) -> dict[str, str]:
    components, default, family, strength, rival, basis = BODY_SPECS[body]
    return {"components": components, "default": default, "family": family,
            "strength": strength, "rival": rival, "basis": basis}


def compose(head: str, body: str) -> str:
    noun = HEAD_NOUN[head]
    if body == "ar":
        return {"p": "Pulverfraktion I", "s": "Samenfraktion I", "r": "Wurzelfraktion I", "l": "Holzfraktion I"}[head]
    if body == "al":
        return {"p": "Pulverrohstoff I", "s": "Saat-Rohstoff I", "r": "Wurzelrohstoff I", "l": "Holzrohstoff I"}[head]
    if body == "y":
        return {"p": "Pulver in Grundform", "s": "Saatgut in Grundform", "r": "rohe Wurzel", "l": "rohes Drogenholz"}[head]
    if body == "air":
        return {"p": "Pulverfraktion II", "s": "Samenfraktion II", "r": "Wurzelfraktion II", "l": "Holzfraktion II"}[head]
    if body == "am":
        return f"{noun}: Maß-/Einheitsform I"
    if body == "chey":
        return f"{noun}, trocken gebunden, Form I"
    if body == "cheey":
        return f"{noun}, trocken gebunden, Form II"
    if body == "chy":
        return f"{noun}, trockene Grundform"
    if body == "chdy":
        return f"{noun}, getrocknete Kurz-/Kompaktform"
    if body == "shey":
        return {"p": "angefeuchtetes Pulver, Form I", "s": "eingeweichte Saat, Form I",
                "r": "eingeweichte Wurzel, Form I", "l": "eingeweichtes Drogenholz, Form I"}[head]
    if body == "oiin":
        return f"{noun}zubereitung, Form III"
    if body == "olchedy":
        return f"getrockneter {noun}stoff/-ansatz"
    if body == "chol":
        return f"trockener {noun}stoff/Trockengut"
    if body == "odaiin":
        return f"{noun}zubereitung, Dosis III"
    if body == "oraiin":
        return {"p": "Pulverportion III", "s": "Samenportion III", "r": "Wurzelportion III", "l": "Holzportion III"}[head]
    if body == "ody":
        return f"{noun}, fertig aufbereitet"
    if body == "cheo":
        return f"trockene {noun}zubereitung/Trockenansatz"
    if body == "oaiin":
        return f"{noun}zubereitung, Charge III"
    if body == "oral":
        return {"p": "Pulver-Rohstoffportion", "s": "Samen-Rohstoffportion",
                "r": "Wurzel-Rohstoffportion", "l": "Holz-Rohstoffportion"}[head]
    raise KeyError(body)


def position_maps(by_line: dict[str, list[dict[str, object]]]) -> dict[tuple[str, int], tuple[int, str]]:
    result: dict[tuple[str, int], tuple[int, str]] = {}
    for locus, line in by_line.items():
        for index, row in enumerate(line):
            position = "FIRST" if index == 0 else "LAST" if index + 1 == len(line) else "MIDDLE"
            result[locus, int(row["token_index"])] = (index + 1, position)
    return result


def build_slots() -> list[dict[str, object]]:
    return [
        {"slot": slot, "role": role, "working_value_de": value, "scope_rule": scope,
         "status": "SCOPED_COMPOSITION_SLOT"}
        for slot, role, value, scope in SLOT_ROWS
    ]


def build_ladders(
    token_rows: list[dict[str, str]], cells: dict[str, dict[str, list[dict[str, str]]]],
    positions: dict[tuple[str, int], tuple[int, str]], exact: dict[tuple[str, int], int],
    by_line: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    ladders = (
        ("AR_PART", ("ar", "air", "aiir", "aiiir"), "Fraktionsklasse I/II/III/IV"),
        ("ON_PREPARATION", ("on", "oin", "oiin", "oiiin"), "Zubereitungs-/Formklasse I/II/III/IV"),
        ("AM_MEASURE_CLOSE", ("am", "aim", "aiim", "aiiim"), "Maßklasse I/II/III/IV; terminal auch Abschluss"),
    )
    surface_map: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        surface_map[row["eva"]].append(row)
    rows: list[dict[str, object]] = []
    for ladder_id, stages, meaning in ladders:
        stage_set = set(stages)
        lines_with_multiple = sum(
            len(stage_set & {str(row["eva"]) for row in line}) >= 2 for line in by_line.values()
        )
        for stage, body in enumerate(stages, 1):
            bare = surface_map.get(body, [])
            headed = [row for head in HEAD_ORDER for row in cells.get(body, {}).get(head, [])]
            bare_positions = Counter(positions[row["locus"], int(row["token_index"])][1] for row in bare)
            headed_positions = Counter(positions[row["locus"], int(row["token_index"])][1] for row in headed)
            rows.append({
                "ladder_id": ladder_id, "stage": stage, "body": body,
                "working_value_de": meaning.split(";")[0].replace("I/II/III/IV", ("I", "II", "III", "IV")[stage - 1]),
                "bare_occurrences": len(bare), "headed_occurrences": len(headed),
                "headed_reader_exact": sum(exact[row["locus"], int(row["token_index"])] for row in headed),
                "bare_line_first": bare_positions["FIRST"], "bare_line_middle": bare_positions["MIDDLE"],
                "bare_line_last": bare_positions["LAST"], "headed_line_first": headed_positions["FIRST"],
                "headed_line_middle": headed_positions["MIDDLE"], "headed_line_last": headed_positions["LAST"],
                "lines_with_two_or_more_bare_stages": lines_with_multiple,
                "interpretation_de": meaning,
            })
    return rows


def build_frames(
    by_line: dict[str, list[dict[str, object]]], exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    frame_map: dict[tuple[str, str, str], dict[str, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))
    residual = set(RESIDUAL_ORDER)
    for locus, line in by_line.items():
        for index, row in enumerate(line):
            parsed = g635.split_initial(str(row["eva"]))
            if not parsed or parsed[1] not in residual:
                continue
            head, body = parsed
            previous = "<BOS>" if index == 0 else str(line[index - 1]["eva"])
            following = "<EOS>" if index + 1 == len(line) else str(line[index + 1]["eva"])
            frame_map[body, previous, following][head].append(row)
    rows: list[dict[str, object]] = []
    for (body, previous, following), heads in frame_map.items():
        if len(heads) < 2:
            continue
        ordered = [head for head in HEAD_ORDER if head in heads]
        rows.append({
            "frame_id": "", "body": body, "previous": previous, "following": following,
            "heads": "|".join(ordered), "forms": "|".join(head + body for head in ordered),
            "occurrences_by_head": "|".join(f"{head}:{len(heads[head])}" for head in ordered),
            "loci_by_head": "|".join(f"{head}:{'&'.join(sorted({str(row['locus']) for row in heads[head]}))}" for head in ordered),
            "reader_exact_by_head": "|".join(
                f"{head}:{sum(exact[row['locus'], int(row['token_index'])] for row in heads[head])}" for head in ordered
            ),
            "working_contrast_de": " ↔ ".join(compose(head, body) for head in ordered),
        })
    rows.sort(key=lambda row: (str(row["body"]), str(row["previous"]), str(row["following"])))
    for index, row in enumerate(rows, 1):
        row["frame_id"] = f"G636-F{index:02d}"
    return rows


def build_body_defaults(
    cells: dict[str, dict[str, list[dict[str, str]]]], surface_counts: Counter[str],
    positions: dict[tuple[str, int], tuple[int, str]], frames: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, body in enumerate(RESIDUAL_ORDER, 1):
        body_spec = spec_fields(body)
        members = [row for head in HEAD_ORDER for row in cells[body][head]]
        p_s = [row for head in ("p", "s") for row in cells[body][head]]
        r_l = [row for head in ("r", "l") for row in cells[body][head]]
        body_frames = [row for row in frames if row["body"] == body]
        rows.append({
            "body_id": f"G636-B{index:02d}", "body": body,
            "components": body_spec["components"], "working_default_de": body_spec["default"],
            "semantic_family": body_spec["family"], "strength": body_spec["strength"],
            "live_rival_de": body_spec["rival"], "composition_basis": body_spec["basis"],
            "forms": "|".join(head + body for head in HEAD_ORDER),
            "occurrences_by_head": "|".join(f"{head}:{len(cells[body][head])}" for head in HEAD_ORDER),
            "total_headed_occurrences": len(members),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
            "bare_body_occurrences": surface_counts[body],
            "ps_line_first": sum(positions[row["locus"], int(row["token_index"])][1] == "FIRST" for row in p_s),
            "rl_line_first": sum(positions[row["locus"], int(row["token_index"])][1] == "FIRST" for row in r_l),
            "rl_line_middle_or_last": sum(positions[row["locus"], int(row["token_index"])][1] != "FIRST" for row in r_l),
            "exact_multihead_neighbor_frames": len(body_frames),
            "scope_rule": "only the remainder inside an attested complete initial p/s/r/l+body form; bare body is not globalized",
        })
    return rows


def build_form_grid(
    cells: dict[str, dict[str, list[dict[str, str]]]],
    positions: dict[tuple[str, int], tuple[int, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    index = 0
    for body in RESIDUAL_ORDER:
        for head in HEAD_ORDER:
            index += 1
            members = cells[body][head]
            pos = Counter(positions[row["locus"], int(row["token_index"])][1] for row in members)
            rows.append({
                "cell_id": f"G636-C{index:02d}", "body": body,
                "body_default_de": spec_fields(body)["default"], "head": head,
                "head_class": HEAD_CLASS[head], "form": head + body,
                "working_default_de": compose(head, body), "occurrences": len(members),
                "pages": len({row["page"] for row in members}), "loci": len({row["locus"] for row in members}),
                "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
                "line_first": pos["FIRST"], "line_middle": pos["MIDDLE"], "line_last": pos["LAST"],
                "section_counts": counter_text(row["section"] for row in members),
                "language_counts": counter_text(row["language"] for row in members),
                "strength": spec_fields(body)["strength"], "status": "ATTESTED_SCOPED_CONCRETE_DEFAULT",
            })
    return rows


def build_position_profiles(form_grid: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for body in RESIDUAL_ORDER:
        members = [row for row in form_grid if row["body"] == body]
        ps = [row for row in members if row["head"] in ("p", "s")]
        rl = [row for row in members if row["head"] in ("r", "l")]
        rows.append({
            "body": body,
            "ps_occurrences": sum(int(row["occurrences"]) for row in ps),
            "ps_line_first": sum(int(row["line_first"]) for row in ps),
            "ps_line_middle": sum(int(row["line_middle"]) for row in ps),
            "ps_line_last": sum(int(row["line_last"]) for row in ps),
            "rl_occurrences": sum(int(row["occurrences"]) for row in rl),
            "rl_line_first": sum(int(row["line_first"]) for row in rl),
            "rl_line_middle": sum(int(row["line_middle"]) for row in rl),
            "rl_line_last": sum(int(row["line_last"]) for row in rl),
            "working_syntax_de": "p/s Eintrags- oder Stoffkopf; r/l überwiegend interner Zutaten-/Pflanzenteilkopf",
        })
    ps_rows = [row for row in form_grid if row["head"] in ("p", "s")]
    rl_rows = [row for row in form_grid if row["head"] in ("r", "l")]
    rows.append({
        "body": "ALL_19",
        "ps_occurrences": sum(int(row["occurrences"]) for row in ps_rows),
        "ps_line_first": sum(int(row["line_first"]) for row in ps_rows),
        "ps_line_middle": sum(int(row["line_middle"]) for row in ps_rows),
        "ps_line_last": sum(int(row["line_last"]) for row in ps_rows),
        "rl_occurrences": sum(int(row["occurrences"]) for row in rl_rows),
        "rl_line_first": sum(int(row["line_first"]) for row in rl_rows),
        "rl_line_middle": sum(int(row["line_middle"]) for row in rl_rows),
        "rl_line_last": sum(int(row["line_last"]) for row in rl_rows),
        "working_syntax_de": "aggregate: entry/material heads separate from internal ingredient/part heads",
    })
    return rows


def build_contexts(
    cells: dict[str, dict[str, list[dict[str, str]]]], by_line: dict[str, list[dict[str, object]]],
    positions: dict[tuple[str, int], tuple[int, str]], boundary: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for body in RESIDUAL_ORDER:
        for head in HEAD_ORDER:
            for member in sorted(cells[body][head], key=lambda row: (row["locus"], int(row["token_index"]))):
                locus = member["locus"]
                line = by_line[locus]
                ordinal, position = positions[locus, int(member["token_index"])]
                working_default = compose(head, body)
                if body == "am" and position == "LAST":
                    working_default += "; Eintrag abgeschlossen"
                rows.append({
                    "context_id": "", "page": member["page"], "locus": locus,
                    "section": member["section"], "language": member["language"], "hand": member["hand"],
                    "body": body, "head": head, "head_class": HEAD_CLASS[head], "form": member["eva"],
                    "working_default_de": working_default, "token_ordinal": ordinal,
                    "line_position": position,
                    "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                    "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                    "reader_exact": member["reader_exact"],
                    "split_normalized": boundary[locus, int(member["token_index"])],
                    "zl3b_line": " ".join(str(row["eva"]) for row in line),
                })
    for index, row in enumerate(rows, 1):
        row["context_id"] = f"G636-X{index:03d}"
    return rows


def build_coexistence(by_line: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, (left, right, left_value, right_value, inference) in enumerate(COEXISTENCE_SPECS, 1):
        loci: list[str] = []
        left_tokens = 0
        right_tokens = 0
        for locus, line in by_line.items():
            surfaces = [str(row["eva"]) for row in line]
            if left in surfaces and right in surfaces:
                loci.append(locus)
                left_tokens += surfaces.count(left)
                right_tokens += surfaces.count(right)
        rows.append({
            "contrast_id": f"G636-K{index:02d}", "left_body": left, "right_body": right,
            "left_working_value_de": left_value, "right_working_value_de": right_value,
            "shared_lines": len(loci), "left_tokens_in_shared_lines": left_tokens,
            "right_tokens_in_shared_lines": right_tokens,
            "example_loci": "|".join(loci[:12]), "semantic_consequence_de": inference,
        })
    return rows


def build_spans(
    by_line: dict[str, list[dict[str, object]]], exact: dict[tuple[str, int], int],
    boundary: dict[tuple[str, int], int], cross_by_locus: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for span_id, locus, start, end, expected, glosses, translation in SPAN_SPECS:
        line = by_line[locus]
        selected = line[start - 1:end]
        surfaces = tuple(str(row["eva"]) for row in selected)
        if surfaces != expected:
            raise RuntimeError(f"span mismatch {span_id}: {surfaces} != {expected}")
        cross = cross_by_locus[locus]
        rows.append({
            "span_id": span_id, "page": line[0]["page"], "locus": locus,
            "section": line[0]["section"], "language": line[0]["language"], "hand": line[0]["hand"],
            "start_position": start, "end_position": end, "surface_span": " | ".join(surfaces),
            "token_glosses_de": " | ".join(glosses), "working_translation_de": translation,
            "all_target_tokens_reader_exact": int(all(exact[locus, int(row["token_index"])] for row in selected)),
            "all_target_tokens_split_normalized": int(all(boundary[locus, int(row["token_index"])] for row in selected)),
            "zl3b_line": " ".join(str(row["eva"]) for row in line),
            "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
            "status": "COMPLETE_CONCRETE_WORKING_SPAN",
        })
    return rows


def build_dictionary(
    old_rows: list[dict[str, str]], defaults: list[dict[str, object]], grid: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [dict(row) for row in old_rows]
    for row in defaults:
        rows.append({
            "entry": f"{row['body']}@GDT636_REMAINDER", "kind": "SCOPED_RESIDUAL_BODY_DEFAULT",
            "working_meaning_de": row["working_default_de"], "composition": row["components"],
            "context_rule": row["scope_rule"], "status": f"NEW_V13_{row['strength']}",
        })
    for row in grid:
        form_rule = f"complete token-initial form; {row['occurrences']} occurrences; bare {row['body']} remains separate"
        if row["body"] == "am":
            form_rule += "; only line-final use additionally closes the entry"
        rows.append({
            "entry": f"{row['form']}@GDT636_HEAD_FORM", "kind": "SCOPED_RESIDUAL_HEAD_FORM",
            "working_meaning_de": row["working_default_de"], "composition": f"{row['head']}+{row['body']}",
            "context_rule": form_rule,
            "status": "NEW_V13_ATTESTED_CONCRETE_DEFAULT",
        })
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G635_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    token_rows, token_stats = g635.g634.g633.g632.g631.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = g635.g634.g633.g632.g631.guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g635.g634.stable_maps(token_rows, cross_by_locus)
    positions = position_maps(by_line)
    cells, surface_counts = g635.collect_cells(token_rows, exact)

    old_four_way = read_tsv(ROOT / G635_FOUR_WAY_REL)
    old_canonical = {"aiin", "chedy", "shedy", "ol", "or"}
    observed_residual = tuple(row["body"] for row in old_four_way if row["body"] not in old_canonical)
    if observed_residual != RESIDUAL_ORDER:
        raise RuntimeError(f"residual order drift: {observed_residual}")
    if any(set(cells[body]) != set(HEAD_ORDER) for body in RESIDUAL_ORDER):
        raise RuntimeError("one or more residual bodies no longer occupy all four heads")

    slots = build_slots()
    ladders = build_ladders(token_rows, cells, positions, exact, by_line)
    frames = build_frames(by_line, exact)
    defaults = build_body_defaults(cells, surface_counts, positions, frames)
    grid = build_form_grid(cells, positions)
    position_profiles = build_position_profiles(grid)
    contexts = build_contexts(cells, by_line, positions, boundary)
    coexistence = build_coexistence(by_line)
    spans = build_spans(by_line, exact, boundary, cross_by_locus)
    history = list(HISTORICAL_ROWS)
    old_dictionary = read_tsv(ROOT / G635_DICT_REL)
    dictionary = build_dictionary(old_dictionary, defaults, grid)

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "SLOT_COMPOSITION_MODEL.tsv", slots,
              ("slot", "role", "working_value_de", "scope_rule", "status"))
    write_tsv(output_dir / "MINIM_LADDER_EVIDENCE.tsv", ladders, (
        "ladder_id", "stage", "body", "working_value_de", "bare_occurrences", "headed_occurrences",
        "headed_reader_exact", "bare_line_first", "bare_line_middle", "bare_line_last", "headed_line_first",
        "headed_line_middle", "headed_line_last", "lines_with_two_or_more_bare_stages", "interpretation_de",
    ))
    write_tsv(output_dir / "RESIDUAL_BODY_DEFAULTS.tsv", defaults, (
        "body_id", "body", "components", "working_default_de", "semantic_family", "strength",
        "live_rival_de", "composition_basis", "forms", "occurrences_by_head", "total_headed_occurrences",
        "reader_exact_occurrences", "bare_body_occurrences", "ps_line_first", "rl_line_first",
        "rl_line_middle_or_last", "exact_multihead_neighbor_frames", "scope_rule",
    ))
    write_tsv(output_dir / "RESIDUAL_76_FORM_GRID.tsv", grid, (
        "cell_id", "body", "body_default_de", "head", "head_class", "form", "working_default_de",
        "occurrences", "pages", "loci", "reader_exact_occurrences", "line_first", "line_middle",
        "line_last", "section_counts", "language_counts", "strength", "status",
    ))
    write_tsv(output_dir / "RESIDUAL_BODY_POSITION_PROFILE.tsv", position_profiles, (
        "body", "ps_occurrences", "ps_line_first", "ps_line_middle", "ps_line_last", "rl_occurrences",
        "rl_line_first", "rl_line_middle", "rl_line_last", "working_syntax_de",
    ))
    write_tsv(output_dir / "RESIDUAL_OCCURRENCE_CONTEXTS.tsv", contexts, (
        "context_id", "page", "locus", "section", "language", "hand", "body", "head", "head_class",
        "form", "working_default_de", "token_ordinal", "line_position", "previous", "following",
        "reader_exact", "split_normalized", "zl3b_line",
    ))
    write_tsv(output_dir / "CONTRASTIVE_BODY_COEXISTENCE.tsv", coexistence, (
        "contrast_id", "left_body", "right_body", "left_working_value_de", "right_working_value_de",
        "shared_lines", "left_tokens_in_shared_lines", "right_tokens_in_shared_lines", "example_loci",
        "semantic_consequence_de",
    ))
    write_tsv(output_dir / "EXACT_RESIDUAL_NEIGHBOR_SWAPS.tsv", frames, (
        "frame_id", "body", "previous", "following", "heads", "forms", "occurrences_by_head",
        "loci_by_head", "reader_exact_by_head", "working_contrast_de",
    ))
    write_tsv(output_dir / "CONCRETE_RESIDUAL_SPAN_TRANSLATIONS.tsv", spans, (
        "span_id", "page", "locus", "section", "language", "hand", "start_position", "end_position",
        "surface_span", "token_glosses_de", "working_translation_de", "all_target_tokens_reader_exact",
        "all_target_tokens_split_normalized", "zl3b_line", "it2a_line", "rf1b_line", "status",
    ))
    write_tsv(output_dir / "HISTORICAL_COMPOSITION_COMPARATORS.tsv", history, (
        "comparator_id", "date_place", "source", "url", "observed_architecture", "use_here",
    ))
    write_tsv(output_dir / "WORKING_DICTIONARY_V13.tsv", dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    total_occurrences = sum(int(row["occurrences"]) for row in grid)
    exact_occurrences = sum(int(row["reader_exact_occurrences"]) for row in grid)
    aggregate = position_profiles[-1]
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    output_hashes = {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths}
    input_paths = (
        G635_RUN_REL, G635_ALLOW_REL, G635_FOUR_WAY_REL, G635_DICT_REL, G635_RESULT_REL, TOKENS_REL, CROSS_REL,
    )
    result_core = {
        "schema": "GDT636_RESIDUAL_FOUR_HEAD_SEMANTICS_RESULT_V1", "experiment_id": "GDT636",
        "status": "ALL_19_RESIDUAL_BODIES_HAVE_SCOPED_COMPOSITIONAL_DEFAULTS",
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
            "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats,
            "cross_query": cross_stats, "token_bearing_loci": len(by_line),
        },
        "residual_grid": {
            "bodies": len(defaults), "forms": len(grid),
            "attested_cells": sum(int(row["occurrences"]) > 0 for row in grid),
            "headed_occurrences": total_occurrences, "reader_exact_occurrences": exact_occurrences,
            "bare_body_occurrences": sum(int(row["bare_body_occurrences"]) for row in defaults),
            "occurrence_context_rows": len(contexts), "exact_neighbor_frames": len(frames),
            "frame_bodies": sorted({str(row["body"]) for row in frames}),
            "contrastive_coexistence_pairs": len(coexistence),
            "ar_or_shared_lines": next(int(row["shared_lines"]) for row in coexistence if row["left_body"] == "ar"),
            "al_ol_shared_lines": next(int(row["shared_lines"]) for row in coexistence if row["left_body"] == "al"),
        },
        "syntax_split": {
            "ps_occurrences": int(aggregate["ps_occurrences"]), "ps_line_first": int(aggregate["ps_line_first"]),
            "rl_occurrences": int(aggregate["rl_occurrences"]), "rl_line_first": int(aggregate["rl_line_first"]),
            "rl_line_middle_or_last": int(aggregate["rl_line_middle"]) + int(aggregate["rl_line_last"]),
            "interpretation": "p/s entry or material heads; r/l predominantly internal ingredient or plant-part heads",
        },
        "composition": {
            "slot_rows": len(slots), "ladder_rows": len(ladders),
            "short_body_defaults": {row["body"]: row["working_default_de"] for row in defaults},
            "ar_air_aiir_prediction": "Fraktionsklasse I/II/III",
            "oiin_ladder": "o preparation frame plus minim class III",
            "am": "measure class I with structural entry-close use; not promoted to a free object noun",
            "ody_correction": "aufbereitet/fertig; the former cooling reading is removed because no k/t temperature head is present",
        },
        "concrete_spans": {
            "count": len(spans),
            "tokens": sum(int(row["end_position"]) - int(row["start_position"]) + 1 for row in spans),
            "all_reader_exact": sum(int(row["all_target_tokens_reader_exact"]) for row in spans),
            "split_normalized": sum(int(row["all_target_tokens_split_normalized"]) for row in spans),
        },
        "working_dictionary": {
            "entries": len(dictionary), "inherited_v12_entries": len(old_dictionary),
            "new_scoped_body_entries": len(defaults), "new_scoped_form_entries": len(grid),
            "inherited_prefix_rows_preserved": len(old_dictionary),
        },
        "claim_boundary": (
            "GDT636 completes the residual four-head working grid on the unchanged GDT635 scope. All nineteen residual bodies and all seventy-six attested p/s/r/l+body forms receive short concrete defaults generated from a fifteen-row scoped field system rather than nineteen unrelated glosses. The 527 occurrences include 398 exact three-reader surfaces. Placement retains the p/s entry-material versus r/l internal-ingredient split. The values are an exploratory replaceable translation model; identical bare surfaces outside the complete head form are not silently globalized."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths}, "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return result


def main() -> int:
    result = build(ART)
    print(
        f"GDT636 built: bodies={result['residual_grid']['bodies']} forms={result['residual_grid']['forms']} "
        f"occurrences={result['residual_grid']['headed_occurrences']} exact={result['residual_grid']['reader_exact_occurrences']} "
        f"frames={result['residual_grid']['exact_neighbor_frames']} spans={result['concrete_spans']['count']} "
        f"dictionary={result['working_dictionary']['entries']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
