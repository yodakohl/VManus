#!/usr/bin/env python3
"""GDT617 has no registered target run yet."""

import sys


def main() -> int:
    print(
        "GDT617_TARGET_NOT_REGISTERED: run acquire_sources.py for the "
        "source-only stage; no Voynich target may be opened.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
