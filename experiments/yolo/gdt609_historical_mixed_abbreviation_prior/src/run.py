#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> int:
    return subprocess.run([sys.executable, str(HERE / "validate.py")], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
