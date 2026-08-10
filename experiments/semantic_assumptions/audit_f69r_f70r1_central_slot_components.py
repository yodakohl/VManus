#!/usr/bin/env python3
"""Post-hoc public/manual audit of f69r-to-f70r1 central-slot containment."""

from __future__ import annotations

import hashlib
import html
import itertools
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
OUT_JSON = RESULTS / "f69r_f70r1_central_slot_component_audit.json"
OUT_MD = RESULTS / "f69r_f70r1_central_slot_component_audit.md"
MANUAL_DETAIL = ROOT / "transcription" / "sources" / "Stolfi_text25e1-52.evt"
NATIVE = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
STA = {key: ROOT / "transcription" / "sources" / "sta" / f"{key}.txt" for key in NATIVE}
PUBLIC_URLS = {
    "quire10": "https://www.voynich.nu/q10/index.html",
    "stolfi_f69r": "https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f69r.htm",
    "stolfi_f70r1": "https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f70r1.htm",
}
F69 = ["f69r.45", "f69r.46", "f69r.47", "f69r.48", "f69r.49", "f69r.44"]
F70 = ["f70r1.15", "f70r1.16", "f70r1.17", "f70r1.18", "f70r1.19", "f70r1.14"]
F69_CLOCK = ["11:30", "01:00", "03:00", "04:30", "07:30", "10:30"]
F70_CLOCK = ["11:30", "01:30", "03:30", "05:30", "08:30", "09:30"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def visible(data: bytes) -> str:
    value = data.decode("utf-8", "replace")
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "VManus-public-slot-audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def locus(path: Path, key: str) -> str:
    pattern = re.compile(rf"^<{re.escape(key)},@(?:L0|Ri)>\s+(.*?)\s*$", re.MULTILINE)
    found = pattern.findall(path.read_text(encoding="utf-8"))
    if len(found) != 1:
        raise RuntimeError((path, key, len(found)))
    return re.sub(r"^<![^>]+>", "", found[0])


def fixed_score(selectors: tuple[str, ...], words: tuple[str, ...]) -> int:
    return sum(selector in word for selector, word in zip(selectors, words))


def dihedral_max(selectors: tuple[str, ...], words: tuple[str, ...]) -> int:
    variants = []
    for base in (selectors, tuple(reversed(selectors))):
        for shift in range(6):
            variants.append(base[shift:] + base[:shift])
    return max(fixed_score(item, words) for item in variants)


def exact_assignment(selectors: tuple[str, ...], words: tuple[str, ...]) -> dict:
    permutations = list(itertools.permutations(selectors))
    physical = fixed_score(selectors, words)
    optimized = dihedral_max(selectors, words)
    fixed_tail = sum(fixed_score(item, words) >= physical for item in permutations)
    optimized_tail = sum(dihedral_max(item, words) >= optimized for item in permutations)
    return {
        "physical_matches": physical,
        "best_dihedral_matches": optimized,
        "assignment_count": len(permutations),
        "physical_tail_count": fixed_tail,
        "physical_exact_p": fixed_tail / len(permutations),
        "optimized_tail_count": optimized_tail,
        "optimized_exact_p": optimized_tail / len(permutations),
    }


def sta_tokens(value: str) -> list[str]:
    return re.findall(r"[A-Z][0-9a-z]", value)


def family_assignment(labels: tuple[str, ...], words: tuple[set[str], ...]) -> dict:
    unique = sorted(set(itertools.permutations(labels)))

    def score(item: tuple[str, ...]) -> int:
        return sum(label in word for label, word in zip(item, words))

    def maximum(item: tuple[str, ...]) -> int:
        variants = []
        for base in (item, tuple(reversed(item))):
            for shift in range(6):
                variants.append(base[shift:] + base[:shift])
        return max(score(v) for v in variants)

    physical = score(labels)
    optimized = maximum(labels)
    fixed_tail = sum(score(item) >= physical for item in unique)
    optimized_tail = sum(maximum(item) >= optimized for item in unique)
    return {
        "physical_matches": physical,
        "best_dihedral_matches": optimized,
        "assignment_count": len(unique),
        "physical_tail_count": fixed_tail,
        "physical_exact_p": fixed_tail / len(unique),
        "optimized_tail_count": optimized_tail,
        "optimized_exact_p": optimized_tail / len(unique),
    }


def report(result: dict) -> str:
    raw = result["complete_group_results"]
    fam = result["leading_sta_family_result"]
    readings = ", ".join(
        f"{edition} {values['physical_matches']}/6 (p={values['physical_exact_p']:.6f})"
        for edition, values in raw.items()
    )
    optimized = ", ".join(
        f"{edition} {values['optimized_tail_count']}/{values['assignment_count']} "
        f"(p={values['optimized_exact_p']:.6f})"
        for edition, values in raw.items()
    )
    return (
        "# f69r/f70r1 central-slot component audit\n\n"
        "Decision: **STOP_NO_FIXED_SLOT_COMPONENT_KEY**.\n\n"
        "The public human sources do support a physical comparison: K1.1--K1.6 "
        "and X1.1--X1.6 are six between-arm registers in the same clock order. "
        "They do not support the attractive 6/6 component claim.\n\n"
        f"Complete source-group containment at the human-fixed alignment is {readings}. "
        "Each reading has a best rotation/reflection score of 5/6, but that is "
        f"also nonexceptional: {optimized}.\n\n"
        f"The apparent optimized leading-family score is {fam['best_dihedral_matches']}/6. "
        f"It is even less selective: {fam['optimized_tail_count']}/{fam['assignment_count']} "
        f"family assignments attain it (p={fam['optimized_exact_p']:.1f}), while the fixed "
        "alignment is only 4/6 and every family assignment scores at least 4/6. The result "
        "is driven by common A/B families and a post-hoc rotation, not a key.\n\n"
        "This closes only the fixed component-containment idea. It supplies no glyph sound, "
        "abbreviation, planet, direction, number, word, plaintext, or translation.\n"
    )


def main() -> None:
    detail = MANUAL_DETAIL.read_bytes()
    detail_text = detail.decode("latin-1")
    for clock, key in zip(F69_CLOCK, F69):
        if f"# At {clock}." not in detail_text or f"<{key};U>" not in detail_text:
            raise RuntimeError((clock, key))
    for clock, key in zip(F70_CLOCK, F70):
        if f"# At {clock}." not in detail_text or f"<{key};U>" not in detail_text:
            raise RuntimeError((clock, key))

    public = {name: fetch(url) for name, url in PUBLIC_URLS.items()}
    public_text = {name: visible(data) for name, data in public.items()}
    required = {
        "quire10": ["six areas between the arms of the star", "six words"],
        "stolfi_f69r": ["six unequal sectors", "each labeled with a Voynichese letter"],
        "stolfi_f70r1": ["Between the star arms there are six labels"],
    }
    for name, phrases in required.items():
        for phrase in phrases:
            if phrase not in public_text[name]:
                raise RuntimeError((name, phrase))

    native_rows = {}
    complete = {}
    sta_rows = {}
    family_result = None
    for edition in NATIVE:
        f69 = tuple(locus(NATIVE[edition], key) for key in F69)
        f70 = tuple(locus(NATIVE[edition], key) for key in F70)
        native_rows[edition] = {"f69": list(f69), "f70": list(f70)}
        complete[edition] = exact_assignment(f69, f70)

        s69 = tuple(locus(STA[edition], key) for key in F69)
        s70 = tuple(locus(STA[edition], key) for key in F70)
        sta_rows[edition] = {"f69": list(s69), "f70": list(s70)}
        labels = tuple(sta_tokens(value)[0][0] for value in s69)
        word_families = tuple({token[0] for token in sta_tokens(value)} for value in s70)
        candidate = family_assignment(labels, word_families)
        if family_result is None:
            family_result = candidate
        elif family_result != candidate:
            raise RuntimeError("leading-family result differs across alternate readings")

    if {v["physical_matches"] for v in complete.values()} != {4}:
        raise RuntimeError("fixed complete-group score changed")
    if {v["best_dihedral_matches"] for v in complete.values()} != {5}:
        raise RuntimeError("optimized complete-group score changed")
    if family_result is None or family_result["physical_matches"] != 4:
        raise RuntimeError("fixed family score changed")

    result = {
        "experiment": "F69F70C001_CENTRAL_SLOT_COMPONENT_AUDIT",
        "status": "STOP_NO_FIXED_SLOT_COMPONENT_KEY",
        "post_hoc_disclosure": True,
        "physical_pairing": [
            {"slot": i + 1, "f69_locus": a, "f69_clock": ac, "f70_locus": b, "f70_clock": bc}
            for i, (a, ac, b, bc) in enumerate(zip(F69, F69_CLOCK, F70, F70_CLOCK))
        ],
        "public_sources": {
            name: {"url": PUBLIC_URLS[name], "sha256": digest(data)} for name, data in public.items()
        },
        "manual_detail_source": {"path": "transcription/sources/Stolfi_text25e1-52.evt", "sha256": digest(detail)},
        "native_source_sha256": {key: digest(path.read_bytes()) for key, path in NATIVE.items()},
        "sta_source_sha256": {key: digest(path.read_bytes()) for key, path in STA.items()},
        "native_rows": native_rows,
        "sta_rows": sta_rows,
        "complete_group_results": complete,
        "leading_sta_family_result": family_result,
        "gates": {
            "public_human_fixed_pairing_available": True,
            "fixed_alignment_exceptional_all_readings": False,
            "optimized_alignment_exceptional": False,
            "ocr_or_automated_vision_used": False,
        },
        "decision": "STOP_NO_FIXED_SLOT_COMPONENT_KEY",
        "claim_ceiling": (
            "The human-fixed f69r-to-f70r1 central-slot pairing is not exceptional under exact "
            "assignment controls. The optimized 6/6 leading-family view is a common post-hoc "
            "rotation. No shared key, glyph sound, abbreviation, planet, direction, number, "
            "word, plaintext, or translation follows."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(report(result), encoding="utf-8")


if __name__ == "__main__":
    main()
