#!/usr/bin/env python3
"""Replay source identity and packet bindings, never validate Latin meanings."""
import hashlib
import json
import re
from pathlib import Path


def main():
    folder = Path(__file__).resolve().parent
    receipt = json.loads((folder / "AO_FETCH.json").read_text())
    result = json.loads((folder / "AO_RESULT.json").read_text())
    checks = []

    def check(name, condition):
        checks.append({"name": name, "pass": bool(condition)})

    for name, expected in receipt["sha256"].items():
        check("source_hash:" + name,
              hashlib.sha256((folder / name).read_bytes()).hexdigest() == expected)
    for name, expected in result["reading_bindings"].items():
        check("reading_hash:" + name,
              hashlib.sha256((folder / name).read_bytes()).hexdigest() == expected)

    manifest = json.loads((folder / "AO_IIIF_MANIFEST.json").read_text())
    selected = manifest["sequences"][0]["canvases"][1]
    info = json.loads((folder / "AO_IMAGE_INFO.json").read_text())
    resource = selected["images"][0]["resource"]
    check("manuscript_identity", "Latin 18499" in manifest["label"])
    check("linked_canvas_identity", selected["@id"] ==
          receipt["canvas_selected_by_official_viewer_link"]["id"])
    check("full_image_identity", resource["@id"] ==
          receipt["image_service"]["resource_url"])
    check("native_dimensions", [selected["width"], selected["height"]] ==
          [info["width"], info["height"]] == [1920, 2952])
    viewer = (folder / "AO_MIRADOR.html").read_text()
    check("official_viewer_selection", bool(re.search(
          r'"idDoc"\s*:\s*"btv1b8101039h"\s*,\s*"numPage"\s*:\s*1', viewer)))
    public_record = (folder / "AO_BNF_RECORD_PUBLIC.html").read_text()
    check("public_record_no_session_parameters", ";jsessionid=" not in public_record)
    inventory = json.loads((folder / "AO_FIRST_NATIVE_INVENTORY.json").read_text())
    check("all_regions_in_first_inventory", {r["id"] for r in inventory["regions"]} ==
          {"FOL", "PROSE_L", "PROSE_R", "VERSE", "ROSE"})
    check("claim_ceiling_recorded", result["confirmed_voynich_words"] == 0 and
          result["complete_certified_source_cases"] == 0 and
          result["new_voynich_access"] is False and
          result["independent_meaning_confirmation"] is False)
    check("publication_exclusions", {"AO_BNF_RECORD.html", "AO_MIRADOR_BUNDLE.js"}
          <= set(result["excluded_from_publication"]))
    output = {"status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
              "scope": "source identity, hashes and recorded ceilings only; not Latin or meanings",
              "checks": checks}
    (folder / "AO_VALIDATION.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks),
                      "failed": [c["name"] for c in checks if not c["pass"]]}))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
