#!/usr/bin/env python3
"""Reproduce the complete pre-decoder GDT395 world-panel freeze."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    for name in (
        "build_pair_matched_subpanels.py",
        "freeze_pair_protocol_amendment.py",
        "validate_pair_protocol_amendment.py",
        "freeze_world_panel.py",
    ):
        subprocess.run([sys.executable, str(HERE / name)], check=True)


if __name__ == "__main__":
    main()
