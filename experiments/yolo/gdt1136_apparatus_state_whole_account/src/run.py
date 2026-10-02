#!/usr/bin/env python3
"""Run the finite authored GDT1136 account; no search or manuscript intake."""
import json
import runpy
from pathlib import Path


def main():
    author = Path(__file__).with_name("author.py")
    if not author.is_file():
        print(json.dumps({"status": "REGISTERED_AUTHOR_NOT_YET_FROZEN", "semantic_result": None}))
        return
    runpy.run_path(str(author), run_name="__main__")


if __name__ == "__main__":
    main()
