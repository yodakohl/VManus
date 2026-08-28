#!/usr/bin/env python3
"""Build the non-circular SHA-256 inventory for sources and result artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXCLUDE = {"binding_inventory.json", "validation.json"}


def main():
    files = sorted(
        path for path in HERE.iterdir()
        if path.is_file() and path.name not in EXCLUDE
    )
    inventory = {
        path.name: {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in files
    }
    (HERE / "binding_inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    )
    print(f"inventoried {len(inventory)} files")


if __name__ == "__main__":
    main()
