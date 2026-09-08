#!/usr/bin/env python3
"""Independent structural validator for GDT879 native packets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt879_plant_topology_endpoint_pilot"
ART = EXP / "artifacts"
PREREG_SHA256 = "d47c248754d3fa5b79b6f4bc07eba07f495ed55835ccced30f821a37814f7b41"
PAGES = ["f4r", "f10r", "f13r"]
DECISIONS = {"PROCEED_DESIGN_REVIEW", "STOP_UNSTABLE_ENDPOINT", "DEFER_UNCERTAIN_SOURCE"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest):
    errors = []
    images = manifest.get("images") if isinstance(manifest, dict) else None
    if not isinstance(images, list) or {x.get("page") for x in images} != set(PAGES):
        return ["source manifest page set must be exactly f4r/f10r/f13r"]
    for item in images:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"missing source {item['page']}")
            continue
        raw = path.read_bytes()
        if sha(path) != item.get("sha256") or len(raw) != item.get("bytes"):
            errors.append(f"source hash/byte mismatch {item['page']}")
        if Image is None:
            errors.append("Pillow unavailable")
        else:
            with Image.open(path) as image:
                if image.size != (item.get("width"), item.get("height")):
                    errors.append(f"source dimensions mismatch {item['page']}")
    return errors


def page_view(packet, page_name):
    """Normalize only packet shape; never match graph IDs across observers."""
    if isinstance(packet.get("pages"), list):
        for page in packet["pages"]:
            if page.get("page") == page_name:
                return page
        return None
    observations = packet.get("observations")
    if not isinstance(observations, dict):
        return None
    raw = observations.get(page_name)
    if not isinstance(raw, dict):
        return None
    interval = raw.get("terminal_count_interval")
    count = raw.get("terminal_count")
    if isinstance(count, dict):
        interval = [count.get("min"), count.get("max")]
    locators = raw.get("terminals", raw.get("counted_terminal_locators", []))
    edges = raw.get("edges", raw.get("parent_child_relations", []))
    return {
        "page": page_name,
        "terminal_count": {"min": interval[0], "max": interval[1]} if isinstance(interval, list) and len(interval) == 2 else None,
        "terminals": locators,
        "inventory_complete": raw.get("inventory_complete", raw.get("enumeration_complete", False)),
        "basal_hub_clear": raw.get("basal_hub_clear"),
        "hierarchy_clear": raw.get("hierarchy_clear"),
        "edges": edges,
        "notes": " ".join([str(raw.get("count_explanation", "")), *[str(x) for x in raw.get("ambiguities", [])]]).strip(),
    }


def page_errors(page, expected):
    errors = []
    if not isinstance(page, dict):
        return [f"{expected}: missing page packet"]
    count = page.get("terminal_count")
    terminals = page.get("terminals")
    if count is not None:
        if not isinstance(count, dict) or any(not isinstance(count.get(k), int) and count.get(k) is not None for k in ("min", "max")) or (count.get("min") is not None and count.get("max") is not None and (count["min"] < 0 or count["min"] > count["max"])):
            errors.append(f"{expected}: invalid terminal_count interval")
    if not isinstance(terminals, list):
        errors.append(f"{expected}: terminals must be a list")
        terminals = []
    ids = [x.get("id") for x in terminals if isinstance(x, dict)]
    if len(ids) != len(set(ids)):
        errors.append(f"{expected}: duplicate terminal IDs")
    for terminal in terminals:
        center = terminal.get("center", terminal.get("center_normalized")) if isinstance(terminal, dict) else None
        if not isinstance(center, list) or len(center) != 2 or not all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in center):
            errors.append(f"{expected}: invalid approximate terminal center")
    exact = count is not None and count.get("min") is not None and count.get("min") == count.get("max")
    complete = page.get("inventory_complete", False)
    if exact and complete and len(terminals) != count["min"]:
        errors.append(f"{expected}: exact count disagrees with complete terminal list")
    if count is not None and count.get("max") is not None and len(terminals) > count["max"]:
        errors.append(f"{expected}: terminal examples exceed count interval")
    if not isinstance(page.get("basal_hub_clear"), bool) or not isinstance(page.get("hierarchy_clear"), bool):
        errors.append(f"{expected}: basal_hub_clear and hierarchy_clear must be boolean")
    if not isinstance(page.get("edges"), list):
        errors.append(f"{expected}: edges must be a list")
    else:
        for edge in page["edges"]:
            if not isinstance(edge, dict) or not isinstance(edge.get("parent"), str) or not edge["parent"] or not isinstance(edge.get("children"), list) or any(not isinstance(child, str) or not child for child in edge["children"]):
                errors.append(f"{expected}: malformed parent/children edge")
    if not isinstance(page.get("notes"), str):
        errors.append(f"{expected}: notes must preserve uncertainty")
    return errors


def packet_errors(packet, observer):
    errors = []
    if packet.get("observer") != observer:
        errors.append(f"observer mismatch: expected {observer}")
    if isinstance(packet.get("pages"), list):
        labels = [x.get("page") for x in packet["pages"]]
        if labels != PAGES:
            errors.append(f"{observer}: pages must cover f4r,f10r,f13r exactly once in order")
    elif isinstance(packet.get("observations"), dict):
        if list(packet["observations"]) != PAGES:
            errors.append(f"{observer}: observations must cover f4r,f10r,f13r exactly once")
    else:
        errors.append(f"{observer}: missing pages/observations")
    for page in PAGES:
        errors.extend(page_errors(page_view(packet, page), page))
    return errors


def packet_source_errors(packet, manifest):
    records = packet.get("sources")
    if records is None:
        return []
    if not isinstance(records, list) or {item.get("page") for item in records} != set(PAGES):
        return ["packet sources must cover f4r/f10r/f13r exactly once"]
    by_page = {item.get("page"): item for item in manifest.get("images", [])}
    errors = []
    for record in records:
        expected = by_page.get(record.get("page"))
        if expected is None or record.get("path") != expected.get("path") or record.get("source_sha256") != expected.get("sha256"):
            errors.append(f"packet source binding mismatch: {record.get('page')}")
    return errors


def adjudication_errors(result):
    if not isinstance(result, dict) or result.get("decision") not in DECISIONS:
        return ["RESULT.json requires an allowed explicit decision"]
    support = result.get("support")
    if not isinstance(support, dict):
        return ["RESULT support object is required"]
    errors = []
    # Older/proceed packets may provide the count directly.  The frozen root
    # stop packet instead gives the explicit agreed-page list plus per-page
    # adjudications; derive only that declared count, never from observations.
    n = support.get("exact_compatible_page_count")
    if n is None and isinstance(support.get("agreed_pages"), list):
        n = len(support["agreed_pages"])
    if n is None and isinstance(support.get("page_adjudications"), list):
        n = sum(
            isinstance(item, dict)
            and item.get("exact_complete_inventory_agreement") is True
            and item.get("complete_compatible_rooted_graph") is True
            for item in support["page_adjudications"]
        )
    if not isinstance(n, int) or n < 0:
        errors.append("RESULT must declare compatible pages or exact_compatible_page_count")
        n = None
    if isinstance(support.get("agreed_pages"), list):
        if any(page not in PAGES for page in support["agreed_pages"]):
            errors.append("RESULT agreed_pages contains an unknown page")
        if len(set(support["agreed_pages"])) != len(support["agreed_pages"]):
            errors.append("RESULT agreed_pages contains duplicates")
    adjudications = support.get("page_adjudications")
    if adjudications is not None:
        if not isinstance(adjudications, list):
            errors.append("RESULT page_adjudications must be a list")
        else:
            labels = [item.get("page") for item in adjudications if isinstance(item, dict)]
            if set(labels) != set(PAGES) or len(labels) != len(PAGES):
                errors.append("RESULT page_adjudications must cover the three fixed pages")
            for item in adjudications:
                if not isinstance(item, dict):
                    errors.append("RESULT page_adjudications contains a malformed entry")
                    continue
                for key in ("exact_complete_inventory_agreement", "complete_compatible_rooted_graph"):
                    if not isinstance(item.get(key), bool):
                        errors.append(f"RESULT page adjudication requires boolean {key}")
    if result["decision"] == "PROCEED_DESIGN_REVIEW":
        if n is not None and n < 2:
            errors.append("proceed contradicts fewer than two exact-compatible pages")
        for key in ("exact_terminal_count_agreement", "compatible_rooted_relations", "topology_difference_beyond_size_position"):
            if support.get(key) is not True:
                errors.append(f"proceed requires explicit {key}")
    elif n is not None and n >= 2 and support.get("proceed_criterion_met") is True:
        errors.append("stop/defer contradicts explicit proceed criterion")
    if result["decision"] != "PROCEED_DESIGN_REVIEW":
        # A stop/defer is accepted only when the declared adjudication itself
        # leaves fewer than two compatible pages; a prose reason is not enough.
        if n is None or n >= 2:
            errors.append("stop/defer requires fewer than two declared compatible pages")
        if support.get("exact_terminal_count_agreement") is True and support.get("compatible_rooted_relations") is True:
            errors.append("stop/defer cannot declare exact counts and rooted relations both satisfied")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", type=Path, default=ART)
    args = ap.parse_args()
    art = args.artifacts.resolve()
    errors = []
    try:
        manifest = load(art / "SOURCES.json")
        root_packet = load(art / "ROOT_OBSERVATION.json")
        b_packet = load(art / "B_OBSERVATION.json")
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [f"packet load: {exc}"]}))
        return 1
    errors.extend(validate_manifest(manifest))
    errors.extend(packet_errors(root_packet, "ROOT"))
    errors.extend(packet_errors(b_packet, "B"))
    errors.extend(packet_source_errors(root_packet, manifest))
    errors.extend(packet_source_errors(b_packet, manifest))
    prereg = EXP / "PREREGISTRATION.md"
    if sha(prereg) != PREREG_SHA256:
        errors.append("frozen preregistration hash mismatch")
    package_path = art / "PACKET_PACKAGE.json"
    if package_path.is_file():
        package = load(package_path)
        expected = {"ROOT_OBSERVATION.json": sha(art / "ROOT_OBSERVATION.json"), "B_OBSERVATION.json": sha(art / "B_OBSERVATION.json")}
        if package.get("source_manifest_sha256") != sha(art / "SOURCES.json") or package.get("preregistration_sha256") != PREREG_SHA256 or package.get("packet_sha256") != expected:
            errors.append("packet package hash binding mismatch")
        if package.get("packets", {}).get("ROOT_OBSERVATION.json") != root_packet or package.get("packets", {}).get("B_OBSERVATION.json") != b_packet:
            errors.append("packet package contents do not match frozen packets")
    result_path = art / "RESULT.json"
    if result_path.is_file():
        result = load(result_path)
        errors.extend(adjudication_errors(result))
        capable_pages = []
        for name in PAGES:
            views = [page_view(packet, name) for packet in (root_packet, b_packet)]
            counts = [v.get("terminal_count") for v in views]
            exact = all(isinstance(c, dict) and isinstance(c.get("min"), int) and c.get("min") == c.get("max") for c in counts)
            if exact and all(v.get("inventory_complete") is True and v.get("hierarchy_clear") is True and v.get("basal_hub_clear") is True for v in views) and counts[0] == counts[1]:
                capable_pages.append(name)
        declared_pages = result.get("support", {}).get("agreed_pages", [])
        if any(name not in capable_pages for name in declared_pages):
            errors.append("declared agreement contradicts packet completeness/count/hierarchy")
        if result.get("decision") == "STOP_UNSTABLE_ENDPOINT" and len(capable_pages) >= 2:
            errors.append("this incomplete-inventory stop is not forced by packet capacity")
        declared_hashes = result.get("packet_sha256") if isinstance(result, dict) else None
        expected_hashes = {
            "ROOT_OBSERVATION.json": sha(art / "ROOT_OBSERVATION.json"),
            "B_OBSERVATION.json": sha(art / "B_OBSERVATION.json"),
        }
        if declared_hashes != expected_hashes:
            errors.append("RESULT packet_sha256 does not match frozen packets")
    else:
        errors.append("RESULT.json not present: packet checks remain pending adjudication")
    output = {"schema_version": 1, "experiment_id": "GDT879", "status": "PASS" if not errors else "FAIL", "decision_validation": "explicit-adjudication-only", "preregistration_sha256": PREREG_SHA256, "errors": errors, "claim_ceiling": "source and packet support only; validator cannot reproduce native vision"}
    print(json.dumps(output, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
