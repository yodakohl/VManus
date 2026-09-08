#!/usr/bin/env python3
"""Independent source, packet, and preregistered-decision validator for GDT881."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "AGENTS.md").is_file() and (p / ".git").exists())
ART = EXP / "artifacts"
SOURCE_REL = "experiments/yolo/gdt881_f99v_text_graphic_stroke_interface/artifacts/SOURCE.json"
IMAGE_REL = "experiments/yolo/gdt881_f99v_text_graphic_stroke_interface/runtime/1006247.jpg"
ADMISSION_REL = "experiments/yolo/gdt881_f99v_text_graphic_stroke_interface/src/PAGE_ADMISSIONS.tsv"
PREREG_SHA = "479ebaf93282d36ffc0abb90844cb9fd1ed005b789ebcc67ef61325c06064cc9"
IMAGE_SHA = "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5"
ROOT_SHA = "94169b61548f1908f5a8af5c71421103007aa4f7f474b380be1b9a6b4ecf2635"
B_SHA = "38f68fa254a3c0f7b5ed9e91c0384d5b4f6bd7286486718aaccf67aec8a77218"
PAGE = "f99v"
ADMISSION_FIELDS = ["admission_batch", "physical_page", "source_selector", "status", "reason"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def packet_checks(packet: dict, observer: str, expected_source: str) -> tuple[list[str], int]:
    errors = []
    if packet.get("observer") != observer:
        errors.append(f"{observer}: observer identity mismatch")
    if packet.get("source_sha256") != expected_source:
        errors.append(f"{observer}: source binding mismatch")
    if packet.get("scene_located") not in {"yes", "no", "uncertain"}:
        errors.append(f"{observer}: invalid scene_located")
    if packet.get("inside_writing") not in {"yes", "no", "uncertain"}:
        errors.append(f"{observer}: invalid inside_writing")
    if packet.get("ordinary_lines") not in {"yes", "no", "uncertain"}:
        errors.append(f"{observer}: invalid ordinary_lines")
    locator = packet.get("scene_locator")
    if not isinstance(locator, list) or len(locator) != 4 or not all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in locator):
        errors.append(f"{observer}: invalid normalized scene locator")
    interfaces = packet.get("interfaces")
    if not isinstance(interfaces, list):
        errors.append(f"{observer}: interfaces must be a list")
        interfaces = []
    clear = 0
    for item in interfaces:
        if not isinstance(item, dict):
            errors.append(f"{observer}: malformed interface")
            continue
        if not isinstance(item.get("dual_role"), bool):
            errors.append(f"{observer}: interface dual_role must be boolean")
        if item.get("certainty") not in {"clear", "uncertain", "absent"}:
            errors.append(f"{observer}: invalid interface certainty")
        if item.get("dual_role") is True and item.get("certainty") == "clear":
            clear += 1
        locator = item.get("locator")
        if (not isinstance(locator, list) or len(locator) != 4 or
                not all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in locator) or
                locator[0] > locator[2] or locator[1] > locator[3]):
            errors.append(f"{observer}: invalid ordered interface locator")
    rule = packet.get("construction_rule")
    if rule is not None and (not isinstance(rule, str) or not rule.strip()):
        errors.append(f"{observer}: construction_rule must be null or nonempty text")
    return errors, clear


def admission_checks() -> list[str]:
    path = ROOT / ADMISSION_REL
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            rows = list(reader)
    except OSError as exc:
        return [f"page admission unreadable: {exc}"]
    errors = []
    if reader.fieldnames != ADMISSION_FIELDS:
        errors.append("page admission header mismatch")
    command = [str(ROOT / "vmanus-exp"), "query-tsv", ADMISSION_REL, "--selector", "source_selector", "--allow", PAGE,
               "--columns", ",".join(ADMISSION_FIELDS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
        guard = [line for line in proc.stderr.decode().splitlines() if line.startswith("GUARD_STATS ")]
        projection = csv.DictReader(io.StringIO(proc.stdout.decode()), delimiter="\t")
        queried = list(projection)
        if len(guard) != 1 or projection.fieldnames != ADMISSION_FIELDS or len(queried) != 1:
            errors.append("guarded f99v admission query mismatch")
        rows = queried
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"guarded f99v admission query failed: {exc}")
        rows = []
    matches = [row for row in rows if row.get("source_selector") == PAGE]
    if len(matches) != 1 or matches[0].get("physical_page") != PAGE or matches[0].get("status") != "ADMITTED":
        errors.append("exact f99v admission is not uniquely ADMITTED")
    return errors


def derive_result(root_packet: dict, b_packet: dict) -> dict:
    root_clear = sum(item.get("dual_role") is True and item.get("certainty") == "clear" for item in root_packet.get("interfaces", []) if isinstance(item, dict))
    b_clear = sum(item.get("dual_role") is True and item.get("certainty") == "clear" for item in b_packet.get("interfaces", []) if isinstance(item, dict))
    root_rule = root_packet.get("construction_rule")
    b_rule = b_packet.get("construction_rule")
    shared_rule = isinstance(root_rule, str) and bool(root_rule.strip()) and root_rule == b_rule
    nomination = root_clear >= 2 and b_clear >= 2 and shared_rule
    quarantine = root_packet.get("inside_writing") != "yes" or b_packet.get("inside_writing") != "yes"
    return {
        "root_clear_dual_role_interfaces": root_clear,
        "b_clear_dual_role_interfaces": b_clear,
        "shared_nonnull_construction_rule": shared_rule,
        "inside_writing_quarantined": quarantine,
        "status": "DISCOVERY_INTERFACE_NOMINATED" if nomination else "STOP_NO_SHARED_STROKE_CONSTRUCTION",
        "historical_inside_body_status": "UNRESOLVED_QUARANTINED" if quarantine else "RETAINED_LOCAL_OBSERVATION_ONLY",
    }


def result_checks(result: dict, derived: dict, root_packet: dict, b_packet: dict) -> list[str]:
    errors = []
    if result.get("experiment") != "GDT881":
        errors.append("RESULT experiment mismatch")
    if result.get("status") != derived["status"]:
        errors.append("RESULT status disagrees with packet-derived gate")
    if result.get("clear_dual_role_interfaces") != {"ROOT": derived["root_clear_dual_role_interfaces"], "B": derived["b_clear_dual_role_interfaces"]}:
        errors.append("RESULT clear_dual_role_interfaces disagrees with packets")
    if result.get("historical_single_inside_body_positive") != derived["historical_inside_body_status"]:
        errors.append("RESULT historical inside-body status disagrees with packets")
    if result.get("packet_sha256") != {"ROOT": ROOT_SHA, "B": B_SHA}:
        errors.append("RESULT packet hashes do not match frozen packets")
    for field, expected in (("scene_located", {"ROOT": root_packet.get("scene_located"), "B": b_packet.get("scene_located")}),
                            ("inside_writing", {"ROOT": root_packet.get("inside_writing"), "B": b_packet.get("inside_writing")}),
                            ("ordinary_lines", {"ROOT": root_packet.get("ordinary_lines"), "B": b_packet.get("ordinary_lines")})):
        if result.get(field) != expected:
            errors.append(f"RESULT {field} disagrees with packets")
    if result.get("new_visual_keys") != 1 or result.get("total_visual_keys") != 46 or result.get("total_visual_selectors") != 52 or result.get("remaining_discretionary_keys") != 4:
        errors.append("RESULT admission counts mismatch")
    if result.get("source_sha256") != IMAGE_SHA:
        errors.append("RESULT source hash mismatch")
    if not isinstance(result.get("claim_ceiling"), str) or "meaning assignment" not in result["claim_ceiling"].lower():
        errors.append("RESULT claim ceiling does not preserve the no-meaning-assignment limit")
    return errors


def main() -> int:
    errors = []
    source_path = ART / "SOURCE.json"
    image_path = ROOT / IMAGE_REL
    prereg_path = EXP / "PREREGISTRATION.md"
    try:
        source = load(source_path)
        root_packet = load(ART / "ROOT.json")
        b_packet = load(ART / "B.json")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"packet/source load: {exc}")
        source = root_packet = b_packet = {}
    if (source.get("page") != PAGE or source.get("canvas_id") != "1006247" or
            source.get("url") != "https://collections.library.yale.edu/iiif/2/1006247/full/full/0/default.jpg" or
            source.get("sha256") != IMAGE_SHA or source.get("bytes") != 2543597 or source.get("dimensions") != [2802, 3697] or
            source.get("prereg_sha256") != PREREG_SHA):
        errors.append("SOURCE.json does not bind the fixed f99v image")
    if not image_path.is_file():
        errors.append("runtime source image missing")
    else:
        if sha(image_path) != IMAGE_SHA or image_path.stat().st_size != 2543597:
            errors.append("source image hash/byte mismatch")
        if Image is None:
            errors.append("Pillow unavailable for source dimension check")
        else:
            with Image.open(image_path) as image:
                if list(image.size) != [2802, 3697]:
                    errors.append("source image dimensions mismatch")
    if sha(prereg_path) != PREREG_SHA:
        errors.append("frozen preregistration hash mismatch")
    errors.extend(admission_checks())
    e_root, root_clear = packet_checks(root_packet, "ROOT", IMAGE_SHA)
    e_b, b_clear = packet_checks(b_packet, "B", IMAGE_SHA)
    errors.extend(e_root + e_b)
    if sha(ART / "ROOT.json") != ROOT_SHA:
        errors.append("ROOT.json actual bytes do not match frozen hash")
    if sha(ART / "B.json") != B_SHA:
        errors.append("B.json actual bytes do not match frozen hash")
    derived = derive_result(root_packet, b_packet)
    result_path = ART / "RESULT.json"
    result = None
    if result_path.is_file():
        try:
            result = load(result_path)
            errors.extend(result_checks(result, derived, root_packet, b_packet))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"RESULT load: {exc}")
    else:
        errors.append("RESULT.json missing")
    validation = {
        "schema_version": 1,
        "experiment_id": "GDT881",
        "status": "PASS" if not errors else "FAIL",
        "checks": {
            "source_bytes_dimensions": not any("source image" in e or "SOURCE.json" in e for e in errors),
            "page_admission": not any("admission" in e for e in errors),
            "packet_schema": not bool(e_root + e_b),
            "packet_derived": derived,
            "result_checked": result is not None,
        },
        "errors": errors,
        "claim_ceiling": "validator checks source and packet contracts only; it does not validate native visual perception or translation",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
