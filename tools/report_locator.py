"""Find tracked Markdown names by exact ID, without reading their contents."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"[A-Za-z]+[0-9]+", re.ASCII)
PRIVATE_COMPONENT = re.compile(r"(?:^|[^a-z0-9])(?:private|secret|secrets|credentials)(?:$|[^a-z0-9])", re.IGNORECASE)
NAVIGATION_NOTE = (
    "Navigation only: tracked Markdown filenames, not reviewed content or current claims. "
    "Listed paths grant no permission to open sealed data; no latest-valid report is selected."
)


def locate_report_paths(identifier: str, *, root: Path = ROOT) -> list[str]:
    """Return safe repository-relative pathname matches from Git's tracked index."""
    if not ID_RE.fullmatch(identifier) or int(re.search(r"[0-9]+$", identifier)[0]) == 0:
        raise ValueError("expected a simple ID such as DIC001 or GDT184")
    pattern = re.compile(r"(?<![A-Za-z0-9])" + re.escape(identifier) + r"(?![A-Za-z0-9])", re.IGNORECASE)
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "-z"], cwd=root,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    matches: set[str] = set()
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        try:
            name = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or any(ord(c) < 32 or ord(c) == 127 for c in name):
            continue
        if any(part.startswith(".") or part.lower() == "runtime" or PRIVATE_COMPONENT.search(part) for part in path.parts):
            continue
        if path.suffix.lower() == ".md" and pattern.search(path.name):
            matches.add(path.as_posix())
    return sorted(matches)


def render_locations(identifier: str, paths: list[str]) -> str:
    lines = [NAVIGATION_NOTE, f"{identifier.upper()}: {len(paths)} matching tracked path(s)", *paths]
    return "\n".join(lines) + "\n"
