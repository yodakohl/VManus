#!/usr/bin/env python3
"""Freeze the separate medieval scholastic Latin ITTB language pack."""

import json

from gdt001_core import ROOT, canonical, sha256_file
from prepare_gdt001_language_corpora import conllu_text, write_pack


COMMIT = "b19bcbd3ab66914570b5bb0616a9066d56d5e7ea"


def main():
    repo = ROOT / ".gdt001/repos/latin_ittb"; files = sorted(repo.glob("*.conllu"))
    prepared = write_pack("latin_scholastic", conllu_text(files))
    manifest = {"schema": "GDT001_LATIN_SCHOLASTIC_PACK_V1", "status": "FROZEN_EXTERNAL_HUMAN_TEXT_EVIDENCE",
                "system": "UD_Latin-ITTB", "period": "medieval scholastic Latin; source is Index Thomisticus Treebank",
                "genre": "philosophical and theological prose", "url": "https://github.com/UniversalDependencies/UD_Latin-ITTB",
                "commit": COMMIT, "license": "CC BY-NC-SA 3.0",
                "files": [{"name": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in files],
                "normalization": "Unicode NFKD; casefold; delete combining marks; retain only Latin ASCII a-z; collapse all other spans to one space",
                **prepared,
                "claim_ceiling": "Human-authored medieval scholastic Latin scoring prior only; corpus fit cannot establish Voynich language, plaintext, or translation."}
    (ROOT / "gdt001_latin_scholastic_pack.json").write_bytes(canonical(manifest)); print(json.dumps(prepared))


if __name__ == "__main__":
    main()
