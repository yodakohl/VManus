#!/usr/bin/env python3
"""Public/manual source audit of the uncertain f68r2 Sun-ring ending."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "semantic_assumptions" / "results"
JSON_PATH = RESULTS / "f68r2_sun_ring_cleartext_audit.json"
REPORT_PATH = RESULTS / "f68r2_sun_ring_cleartext_audit.md"

URLS = {
    "public_q09_catalogue": "https://www.voynich.nu/q09/index.html",
    "public_transcription_special_topics": "https://www.voynich.nu/extra/sp_transcr.html",
}
MANUAL_PATHS = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
STA_PATHS = {
    "ZL3b": ROOT / "transcription" / "sources" / "sta" / "ZL3b.txt",
    "IT2a": ROOT / "transcription" / "sources" / "sta" / "IT2a.txt",
    "RF1b": ROOT / "transcription" / "sources" / "sta" / "RF1b.txt",
}
LOCUS_RE = re.compile(r"^<f68r2\.31,@Cc>\s+(.*?)\s*$", re.MULTILINE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "VManus-public-source-audit/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def visible_text(data: bytes) -> str:
    text = data.decode("utf-8", "replace")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def extract_locus(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    match = LOCUS_RE.search(data.decode("utf-8"))
    if not match:
        raise RuntimeError(f"missing f68r2.31 in {path}")
    return match.group(1), sha256_bytes(data)


def build_report(result: dict) -> str:
    readings = result["manual_readings"]
    return (
        "# Public f68r2 Sun-ring cleartext audit\n\n"
        "Decision: **STOP_NO_READABLE_CLEARTEXT_ANCHOR**.\n\n"
        "The public Quire 9 catalogue says that the Sun-ring text only "
        "*appears* to contain non-Voynich characters and is almost impossible "
        "to read. The public transcription guidance is stronger: at this "
        "exact location it cannot determine which marks belong to the unknown "
        "script and which, if any, are cleartext.\n\n"
        "The three native manual readings do not supply a consensus plaintext "
        "ending. ZL3b and RF1b preserve four special illegible marks, mapped "
        "by STA to `Ys Yp Yn Yd`; IT2a instead reads an ordinary final "
        f"`{readings['IT2a']['ending']}` group. These are alternate readings "
        "of one locus, not independent votes.\n\n"
        "Therefore proposed readings such as `Suna` are not admissible anchors. "
        "No SUN word, language, sound value, cipher, plaintext, or translation "
        "follows. Reopen only if a qualified human palaeographic source reads "
        "the complete sequence with explicit uncertainty and independent "
        "manuscript support.\n\n"
        "Public sources: [Quire 9 catalogue](https://www.voynich.nu/q09/index.html) "
        "and [transcription special topics](https://www.voynich.nu/extra/sp_transcr.html).\n"
    )


def main() -> None:
    public = {name: fetch(url) for name, url in URLS.items()}
    public_text = {name: visible_text(data) for name, data in public.items()}

    q09_required = (
        "The text around the sun appears to have some non-Voynich characters, perhaps cleartext.",
        "As always it is almost impossible to read.",
    )
    special_required = (
        "part of the text around the sun face at the bottom of folio f68r2",
        "we can't even decide which part of the text is in the unknown script, and which part is 'cleartext'",
    )
    for phrase in q09_required:
        if phrase not in public_text["public_q09_catalogue"]:
            raise RuntimeError(f"public Q9 phrase missing: {phrase}")
    for phrase in special_required:
        if phrase not in public_text["public_transcription_special_topics"]:
            raise RuntimeError(f"public transcription phrase missing: {phrase}")

    manual: dict[str, dict] = {}
    sta: dict[str, dict] = {}
    for edition, path in MANUAL_PATHS.items():
        row, digest = extract_locus(path)
        manual[edition] = {
            "raw_locus_text": row,
            "source_sha256": digest,
            "special_illegible_entity_count": len(re.findall(r"@23[1-4];", row)),
        }
    for edition, path in STA_PATHS.items():
        row, digest = extract_locus(path)
        sta[edition] = {
            "raw_locus_text": row,
            "source_sha256": digest,
            "ends_in_four_Y_family_codes": bool(re.search(r"YsYpYnYd$", row)),
        }

    if manual["ZL3b"]["special_illegible_entity_count"] != 4:
        raise RuntimeError("ZL3b does not preserve the four expected illegible entities")
    if manual["RF1b"]["special_illegible_entity_count"] != 4:
        raise RuntimeError("RF1b does not preserve the four expected illegible entities")
    if manual["IT2a"]["special_illegible_entity_count"] != 0:
        raise RuntimeError("IT2a unexpectedly contains the ZL/RF illegible entity sequence")
    if not manual["IT2a"]["raw_locus_text"].endswith(".koiin"):
        raise RuntimeError("IT2a final group changed")
    if not sta["ZL3b"]["ends_in_four_Y_family_codes"] or not sta["RF1b"]["ends_in_four_Y_family_codes"]:
        raise RuntimeError("official STA projection no longer preserves four Y-family codes")
    if sta["IT2a"]["ends_in_four_Y_family_codes"]:
        raise RuntimeError("IT2a unexpectedly ends in four Y-family codes")

    manual["ZL3b"]["ending"] = "FOUR_ILLEGIBLE_MARKS"
    manual["RF1b"]["ending"] = "FOUR_ILLEGIBLE_MARKS"
    manual["IT2a"]["ending"] = "koiin"

    result = {
        "experiment": "F68CL001_PUBLIC_SUN_RING_CLEARTEXT_AUDIT",
        "status": "STOP_NO_READABLE_CLEARTEXT_ANCHOR",
        "physical_locus": "f68r2.31",
        "public_sources": {
            name: {
                "url": URLS[name],
                "sha256": sha256_bytes(data),
                "required_claims_found": True,
            }
            for name, data in public.items()
        },
        "manual_readings": manual,
        "sta_readings": sta,
        "gates": {
            "public_source_identifies_exact_sun_ring": True,
            "public_source_calls_cleartext_only_possible": True,
            "public_source_says_script_identity_unresolved": True,
            "all_readings_supply_compatible_readable_plaintext": False,
            "ocr_or_automated_vision_used": False,
            "machine_language_guess_used_as_evidence": False,
        },
        "decision": "STOP_NO_READABLE_CLEARTEXT_ANCHOR",
        "claim_ceiling": (
            "The presently documented f68r2 Sun-ring ending is not an admissible "
            "readable plaintext anchor: public human sources leave script identity "
            "unresolved, ZL3b and RF1b preserve four illegible marks, and IT2a reads "
            "an ordinary koiin ending. No SUN word, language, sound, cipher, plaintext, "
            "or translation follows."
        ),
    }
    report = build_report(result)
    RESULTS.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
