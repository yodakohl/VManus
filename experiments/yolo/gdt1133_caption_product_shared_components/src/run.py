#!/usr/bin/env python3
"""Replay the frozen author account in isolation, preserving original artifacts."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parents[1]


def main():
    receipt = json.loads((BASE / "artifacts/AUTHOR_FINAL_FREEZE_RECEIPT.json").read_text())
    for relative, expected in receipt["files"].items():
        actual = hashlib.sha256((BASE / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit("Frozen author hash mismatch: " + relative)
    files = (
        "src/AUTHOR_MATERIALIZE.py", "src/CORE.json", "src/EXTENSIONS.json",
        "src/SOURCE.json", "artifacts/AUTHOR_INITIAL_FREEZE_RECEIPT.json",
    )
    with tempfile.TemporaryDirectory(prefix="vmanus_1133_replay_") as directory:
        target = Path(directory)
        for relative in files:
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BASE / relative, destination)
        subprocess.run(
            [sys.executable, str(target / "src/AUTHOR_MATERIALIZE.py")],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        replay = (target / "artifacts/AUTHOR_ACCOUNT.json").read_bytes()
        expected = (BASE / "artifacts/AUTHOR_ACCOUNT.json").read_bytes()
        if replay != expected:
            raise SystemExit("Frozen account replay differs")
    print(json.dumps({
        "status": "FROZEN_AUTHOR_REPLAY_PASS",
        "account_sha256": hashlib.sha256(replay).hexdigest(),
        "author_files_written": False,
        "semantic_validation": False,
    }, indent=2))


if __name__ == "__main__":
    main()
