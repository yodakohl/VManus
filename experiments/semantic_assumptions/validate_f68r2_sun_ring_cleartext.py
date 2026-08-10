#!/usr/bin/env python3
"""Independent validator for F68CL001; imports no production module."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
PRODUCTION = RESULTS / "f68r2_sun_ring_cleartext_audit.json"
VALIDATION = RESULTS / "f68r2_sun_ring_cleartext_validation.json"
REPORT = RESULTS / "f68r2_sun_ring_cleartext_validation.md"
URLS = {
    "public_q09_catalogue": "https://www.voynich.nu/q09/index.html",
    "public_transcription_special_topics": "https://www.voynich.nu/extra/sp_transcr.html",
}
NATIVE = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
STA = {k: ROOT / "transcription" / "sources" / "sta" / f"{k}.txt" for k in NATIVE}
ROW = re.compile(r"^<f68r2\.31,@Cc>\s+(.*?)\s*$", re.MULTILINE)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "VManus-public-source-validator/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def text(data: bytes) -> str:
    value = data.decode("utf-8", "replace")
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def locus(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    found = ROW.findall(data.decode("utf-8"))
    if len(found) != 1:
        raise AssertionError((path, len(found)))
    return data, found[0]


def main() -> None:
    prod = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    checks = 0

    def check(value: bool, label: str) -> None:
        nonlocal checks
        if not value:
            raise AssertionError(label)
        checks += 1

    check(prod["experiment"] == "F68CL001_PUBLIC_SUN_RING_CLEARTEXT_AUDIT", "experiment")
    check(prod["status"] == "STOP_NO_READABLE_CLEARTEXT_ANCHOR", "status")
    check(prod["decision"] == prod["status"], "decision")
    check(prod["physical_locus"] == "f68r2.31", "locus")

    live = {name: download(url) for name, url in URLS.items()}
    live_text = {name: text(data) for name, data in live.items()}
    for name, data in live.items():
        check(prod["public_sources"][name]["url"] == URLS[name], f"{name} url")
        check(prod["public_sources"][name]["sha256"] == sha(data), f"{name} hash")
        check(prod["public_sources"][name]["required_claims_found"] is True, f"{name} flag")
    check("perhaps cleartext" in live_text["public_q09_catalogue"], "Q9 perhaps")
    check("almost impossible to read" in live_text["public_q09_catalogue"], "Q9 unreadable")
    check("we can't even decide which part" in live_text["public_transcription_special_topics"], "special undecidable")
    check("unknown script" in live_text["public_transcription_special_topics"], "special unknown")

    native_rows = {}
    for edition, path in NATIVE.items():
        data, value = locus(path)
        native_rows[edition] = value
        stored = prod["manual_readings"][edition]
        check(stored["source_sha256"] == sha(data), f"{edition} native hash")
        check(stored["raw_locus_text"] == value, f"{edition} native row")
        check(stored["special_illegible_entity_count"] == len(re.findall(r"@23[1-4];", value)), f"{edition} entities")
    check(native_rows["ZL3b"].endswith("@231;@232;@233;@234;"), "ZL ending")
    check(native_rows["RF1b"].endswith("@231;@232;@233;@234;"), "RF ending")
    check(native_rows["IT2a"].endswith(".koiin"), "IT ending")

    for edition, path in STA.items():
        data, value = locus(path)
        stored = prod["sta_readings"][edition]
        check(stored["source_sha256"] == sha(data), f"{edition} STA hash")
        check(stored["raw_locus_text"] == value, f"{edition} STA row")
        check(stored["ends_in_four_Y_family_codes"] == value.endswith("YsYpYnYd"), f"{edition} STA ending")
    check(prod["sta_readings"]["ZL3b"]["ends_in_four_Y_family_codes"] is True, "ZL Y")
    check(prod["sta_readings"]["RF1b"]["ends_in_four_Y_family_codes"] is True, "RF Y")
    check(prod["sta_readings"]["IT2a"]["ends_in_four_Y_family_codes"] is False, "IT not Y")

    gates = prod["gates"]
    check(gates["all_readings_supply_compatible_readable_plaintext"] is False, "plaintext gate")
    check(gates["ocr_or_automated_vision_used"] is False, "OCR exclusion")
    check(gates["machine_language_guess_used_as_evidence"] is False, "machine guess exclusion")
    check("No SUN word" in prod["claim_ceiling"], "ceiling")

    validation = {
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "production_sha256": sha(PRODUCTION.read_bytes()),
        "decision": prod["decision"],
        "target_plaintext_anchor_confirmed": False,
        "ocr_or_automated_vision_used": False,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# F68CL001 independent validation\n\n"
        f"PASS: **{checks}** checks independently bind both live public sources, "
        "the three native manual rows, the three official STA rows, the four "
        "illegible ZL/RF ending marks, the incompatible IT `koiin` ending, the "
        "decision, exclusions, and claim ceiling.\n\n"
        "This confirms only that the documented f68r2 Sun-ring ending is not a "
        "readable plaintext anchor. It supplies no SUN word, language, sound, "
        "cipher, plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
