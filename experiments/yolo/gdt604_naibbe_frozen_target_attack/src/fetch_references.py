#!/usr/bin/env python3
"""Fetch only hash-pinned public language-model inputs for GDT604."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path


SOURCES = {
    "caesar_la.txt": (
        "https://raw.githubusercontent.com/lrozanova/voynich-units/"
        "956a7c4fc39981f4d116fa3f4edfccce6d065571/"
        "voynich_decipherment_repro_bundle/decipherment_attack_v6/"
        "lm_corpora/caesar_la.txt",
        "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
    ),
    "divina_commedia.txt": (
        "https://raw.githubusercontent.com/greshko/naibbe-cipher/"
        "f2675ec5dd275268bc64dd48ea64fc0e0e9827a2/"
        "input/examples/divina_commedia.txt",
        "aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e",
    ),
    "mhg/Erec-conll.txt": (
        "https://raw.githubusercontent.com/NoraKet/MHG4SNA/"
        "3eddc3dc1620cf400c152d9ed8915416cb8d6d7a/"
        "conll%20downloads/Erec-conll.txt",
        "367cc2e9d0b60aadee501c187864dea97c77af41303f216986cfa35575f43675",
    ),
    "mhg/Iwein-conll.txt": (
        "https://raw.githubusercontent.com/NoraKet/MHG4SNA/"
        "3eddc3dc1620cf400c152d9ed8915416cb8d6d7a/"
        "conll%20downloads/Iwein-conll.txt",
        "5b43f962da24d5b438ff93f64f30036087fe37d1cd5863c0bd29e764957b6a6f",
    ),
    "mhg/Parzival-conll.txt": (
        "https://raw.githubusercontent.com/NoraKet/MHG4SNA/"
        "3eddc3dc1620cf400c152d9ed8915416cb8d6d7a/"
        "conll%20downloads/Parzival-conll.txt",
        "9d7ef5fd1842f6197121b654eb3c57a307ff01a9698768e27be069732afdf5cf",
    ),
    "mhg/Rolandslied-conll.txt": (
        "https://raw.githubusercontent.com/NoraKet/MHG4SNA/"
        "3eddc3dc1620cf400c152d9ed8915416cb8d6d7a/"
        "conll%20downloads/Rolandslied-conll.txt",
        "46b078128c6932759d56a6a4bf13f9c3bf84d88f7a8d0e35fca31670cc0191fa",
    ),
    "mhg/Willehalm-conll.txt": (
        "https://raw.githubusercontent.com/NoraKet/MHG4SNA/"
        "3eddc3dc1620cf400c152d9ed8915416cb8d6d7a/"
        "conll%20downloads/Willehalm-conll.txt",
        "abee7d5d1aee54fa944e0d311d4645455503d4fc0bbd9ef919c46a9cfd10e7fe",
    ),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    for relative, (url, expected) in SOURCES.items():
        target = args.output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
            print("verified", relative, expected)
            continue
        with urllib.request.urlopen(url) as response:
            data = response.read()
        observed = hashlib.sha256(data).hexdigest()
        if observed != expected:
            raise RuntimeError(f"hash mismatch for {relative}: {observed}")
        target.write_bytes(data)
        print("fetched", relative, observed)


if __name__ == "__main__":
    main()
