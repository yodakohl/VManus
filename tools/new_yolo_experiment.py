#!/usr/bin/env python3
"""Create the required directory skeleton for a new YOLO GDT experiment."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GDT_RE = re.compile(r"(?i)gdt(\d{3,})(?!\d)")
MIN_STRUCTURED_ID = 337


def next_id() -> int:
    output = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    seen = [int(value) for value in GDT_RE.findall(output)]
    return max([MIN_STRUCTURED_ID - 1, *seen]) + 1


def repo_root_source() -> str:
    return '''def find_repo_root(start: Path) -> Path:\n    for candidate in (start, *start.parents):\n        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():\n            return candidate\n    raise RuntimeError("VManus repository root not found")\n\n\nROOT = find_repo_root(Path(__file__).resolve())\n'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="lower-case experiment slug")
    parser.add_argument("--id", type=int, default=None, help="numeric GDT ID; default is next tracked ID")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    number = args.id or next_id()
    if number < MIN_STRUCTURED_ID:
        parser.error(f"structured layout starts at GDT{MIN_STRUCTURED_ID:03d}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", args.slug):
        parser.error("slug must contain only lower-case letters, digits, underscores, or hyphens")

    experiment = ROOT / "experiments/yolo" / f"gdt{number:03d}_{args.slug}"
    relative = experiment.relative_to(ROOT).as_posix()
    today = date.today().isoformat()
    manifest = {
        "schema_version": 1,
        "experiment_id": f"GDT{number:03d}",
        "slug": args.slug,
        "title": args.slug.replace("_", " ").replace("-", " "),
        "status": "REGISTERED_UNSCORED",
        "created": today,
        "updated": today,
        "question": "",
        "claim_ceiling": "",
        "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "commands": {
            "run": f"python3 {relative}/src/run.py",
            "validate": f"python3 {relative}/src/validate.py",
        },
        "dependencies": [],
        "inputs": [],
        "outputs": [],
        "validation": {"status": "NOT_RUN", "artifact": None},
        "artifact_policy": {
            "max_inline_bytes": 5000000,
            "large_artifact_justification": "",
        },
    }
    files = {
        experiment / "README.md": f"# GDT{number:03d} — {args.slug.replace('_', ' ')}\n\nStatus: `REGISTERED_UNSCORED`\n\nSee `METHOD.md` and `experiment.json`.\n",
        experiment / "METHOD.md": f"# GDT{number:03d} method\n\n## Question\n\nTODO\n\n## Inputs\n\nTODO\n\n## Method\n\nTODO\n\n## Decision rule and claim ceiling\n\nTODO\n",
        experiment / "experiment.json": json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        experiment / "src/run.py": "#!/usr/bin/env python3\nfrom pathlib import Path\n\n" + repo_root_source() + "\n\ndef main() -> int:\n    raise NotImplementedError\n\n\nif __name__ == '__main__':\n    raise SystemExit(main())\n",
        experiment / "src/validate.py": "#!/usr/bin/env python3\nfrom pathlib import Path\n\n" + repo_root_source() + "\n\ndef main() -> int:\n    raise NotImplementedError\n\n\nif __name__ == '__main__':\n    raise SystemExit(main())\n",
        experiment / "artifacts/README.md": "# Artifacts\n\nCommit compact, reproducible results here. Large exhaustive tables require an explicit retention justification.\n",
    }
    if experiment.exists():
        parser.error(f"destination already exists: {experiment.relative_to(ROOT)}")
    print(experiment.relative_to(ROOT))
    for path in files:
        print(f"  {path.relative_to(ROOT)}")
    if args.dry_run:
        return 0
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
