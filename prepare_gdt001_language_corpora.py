#!/usr/bin/env python3
"""Prepare pinned, human-authored historical language packs for GDT001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".gdt001"
OUT = LOCAL / "language_packs"
MANIFEST = ROOT / "gdt001_language_pack_manifest.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    output = []
    pending_space = False
    for char in text:
        if unicodedata.category(char).startswith("M"):
            continue
        if "a" <= char <= "z":
            if pending_space and output:
                output.append(" ")
            output.append(char)
            pending_space = False
        elif char.isalpha():
            # Explicitly exclude characters that do not reduce to Latin ASCII.
            pending_space = True
        else:
            pending_space = True
    return "".join(output).strip()


def conllu_text(paths: Iterable[Path]) -> list[str]:
    sentences: list[str] = []
    for path in sorted(paths):
        pending_forms: list[str] = []
        explicit = ""
        for line in path.read_text(encoding="utf-8").splitlines() + [""]:
            if line.startswith("# text = "):
                explicit = line[9:]
            elif line and not line.startswith("#"):
                fields = line.split("\t")
                if len(fields) >= 2 and fields[0].isdigit():
                    pending_forms.append(fields[1])
            elif not line:
                value = normalized(explicit or " ".join(pending_forms))
                if value:
                    sentences.append(value)
                pending_forms = []
                explicit = ""
    return sentences


def rem_text(directory: Path) -> list[str]:
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    lines: list[str] = []
    for path in sorted(directory.glob("*.xml")):
        root = ET.parse(path).getroot()
        current: list[str] = []
        for element in root.findall(".//tei:text/tei:body//tei:w", ns):
            value = normalized("".join(element.itertext()))
            if value:
                current.append(value)
            if len(current) >= 40:
                lines.append(" ".join(current))
                current = []
        if current:
            lines.append(" ".join(current))
    return lines


def old_hungarian(paths: Iterable[Path]) -> list[str]:
    lines: list[str] = []
    for path in sorted(paths):
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames == ["masked", "src"]:
                values = (row["src"] for row in reader)
            elif reader.fieldnames and len(reader.fieldnames) == 1:
                values = iter([reader.fieldnames[0], *(row[reader.fieldnames[0]] for row in reader)])
            else:
                raise ValueError(f"Old Hungarian schema drift: {path}")
            for source in values:
                value = normalized(source.replace("[MASK]", " "))
                if value:
                    lines.append(value)
    return lines


def czech_diakorp(archive: Path) -> list[str]:
    output: list[str] = []
    with zipfile.ZipFile(archive) as bundle:
        names = sorted(name for name in bundle.namelist() if name.endswith(".txt"))
        for name in names:
            years = [int(value) for value in re.findall(r"(?<!\d)(1[3-5]\d{2})(?!\d)", Path(name).stem)]
            if not years or min(years) > 1550:
                continue
            raw = bundle.read(name).decode("utf-8")
            body = "\n".join(line for line in raw.splitlines() if not line.startswith("#"))
            for paragraph in re.split(r"\n\s*\n", body):
                value = normalized(paragraph)
                if value:
                    output.append(value)
    return output


def write_pack(name: str, sentences: list[str]) -> dict[str, object]:
    if not sentences:
        raise ValueError(f"empty pack: {name}")
    data = ("\n".join(sentences) + "\n").encode()
    path = OUT / f"{name}.txt"
    path.write_bytes(data)
    chars = sum(len(line.replace(" ", "")) for line in sentences)
    words = sum(len(line.split()) for line in sentences)
    return {"prepared_sha256": sha(path), "prepared_bytes": len(data), "sentences": len(sentences), "words": words, "letters": chars}


def git_files(repository: Path, glob: str) -> list[Path]:
    return sorted(repository.glob(glob))


def file_inventory(paths: Iterable[Path]) -> list[dict[str, object]]:
    return [{"name": path.name, "sha256": sha(path), "bytes": path.stat().st_size} for path in sorted(paths)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ud = LOCAL / "repos"
    latin_files = git_files(ud / "latin_llct", "*.conllu")
    french_files = git_files(ud / "middle_french", "*.conllu")
    italian_files = git_files(ud / "old_italian", "*.conllu")
    hungarian_files = [
        ud / "sigtyp_st2024" / "fill_mask_word" / split / f"ohu_{split}.tsv"
        for split in ("train", "valid", "test")
    ]
    rem_archive = LOCAL / "corpora/rem-v2.1-tei.zip"
    rem_dir = LOCAL / "corpora/rem/ReM-v2.1_tei/tei"
    czech_archive = LOCAL / "corpora/czech-diakorp-txt.zip"
    sources = {
        "latin": {
            "system": "UD_Latin-LLCT", "period": "774-897", "genre": "Tuscan legal charters",
            "url": "https://github.com/UniversalDependencies/UD_Latin-LLCT",
            "commit": "173cd1133e70f1a95a8608091792f91ebe001157", "license": "CC BY-SA 4.0",
            "files": file_inventory(latin_files), "sentences": conllu_text(latin_files),
        },
        "middle_high_german": {
            "system": "Referenzkorpus Mittelhochdeutsch 2.1", "period": "1050-1350", "genre": "balanced historical texts",
            "url": "https://zenodo.org/records/13982324/files/ReM-v2.1_tei.zip?download=1",
            "archive_sha256": sha(rem_archive), "archive_bytes": rem_archive.stat().st_size, "license": "CC BY-SA 4.0",
            "sentences": rem_text(rem_dir),
        },
        "middle_french": {
            "system": "UD_Middle_French-PROFITEROLE", "period": "late 14th-late 15th century", "genre": "fiction and nonfiction",
            "url": "https://github.com/UniversalDependencies/UD_Middle_French-PROFITEROLE",
            "commit": "5da2c5fbda07262193cc4b7f3bdf45e845209625", "license": "CC BY-NC-SA 4.0",
            "files": file_inventory(french_files), "sentences": conllu_text(french_files),
        },
        "old_italian_tuscan": {
            "system": "UD_Italian-Old", "period": "1306-1321 composition", "genre": "Florentine poetry",
            "url": "https://github.com/UniversalDependencies/UD_Italian-Old",
            "commit": "a82abc49afb8b3605eda5b85a9c3a23f480d82a7", "license": "CC BY-SA 4.0",
            "files": file_inventory(italian_files), "sentences": conllu_text(italian_files),
        },
        "medieval_czech": {
            "system": "DIAKORP diplomatic subset through 1550", "period": "1350-1550 selected by source filename date", "genre": "mixed",
            "url": "https://zenodo.org/records/10013189/files/czech-diakorp-txt.zip?download=1",
            "archive_sha256": sha(czech_archive), "archive_bytes": czech_archive.stat().st_size,
            "license": "CC BY-NC-SA 4.0", "sentences": czech_diakorp(czech_archive),
        },
        "old_hungarian": {
            "system": "SIGTYP ACHILLES Old Hungarian diplomatic codices", "period": "1440-1521", "genre": "five codices",
            "url": "https://github.com/sigtyp/ST2024",
            "commit": "cf54342c0942fb63692485049ca5db3b42d15a04", "license": "research dataset; source citations retained",
            "files": file_inventory(hungarian_files), "sentences": old_hungarian(hungarian_files),
        },
    }
    manifest: dict[str, object] = {
        "schema": "GDT001_LANGUAGE_PACK_MANIFEST_V1",
        "status": "FROZEN_EXTERNAL_HUMAN_TEXT_EVIDENCE",
        "normalization": "Unicode NFKD; casefold; delete combining marks; retain only Latin ASCII a-z; collapse all other spans to one space",
        "packs": {},
        "claim_ceiling": "Human-authored historical or near-historical character language models for exploratory scoring; corpus fit is not evidence that Voynich is any listed language.",
    }
    for name, record in sources.items():
        sentences = record.pop("sentences")
        manifest["packs"][name] = {**record, **write_pack(name, sentences)}
    MANIFEST.write_bytes(canonical(manifest))
    print(json.dumps({"manifest_sha256": sha(MANIFEST), "packs": {name: data["letters"] for name, data in manifest["packs"].items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
