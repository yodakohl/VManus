#!/usr/bin/env python3
"""One-time administrative migration of GDT362--GDT384 manifests.

This script changes no experiment artifact other than experiment.json.  It
recovers scientific input bindings from each published compact result when the
recorded input byte still exists unchanged, and binds every retained experiment
file as an output.  Historical result JSON remains the authority for any input
whose live append-only path has subsequently changed.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YOLO = ROOT / "experiments" / "yolo"

RUNNERS = {
    373: "src/build.py",
    375: "src/build.py",
    378: "src/finalize_gdt378.py",
    379: "src/finalize_gdt379.py",
    380: "src/finalize.py",
    381: "src/finalize.py",
    382: "src/finalize_gdt382.py",
    383: "src/finalize_stage_a.py",
    384: "src/finalize_stage_a.py",
}
VALIDATORS = {
    373: "src/validate_manifest_wrapper.py",
    378: "src/validate_voynich_target.py",
    379: "@tools/validate_migrated_yolo_experiment.py",
    380: "@tools/validate_migrated_yolo_experiment.py",
    381: "@tools/validate_migrated_yolo_experiment.py",
    382: "@tools/validate_migrated_yolo_experiment.py",
    383: "@tools/validate_migrated_yolo_experiment.py",
    384: "@tools/validate_migrated_yolo_experiment.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def created(path: Path) -> str:
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--follow", "--format=%as", "--", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.splitlines()
    return out[-1] if out else "2026-08-20"


def title_from(folder: Path, old: dict, number: int) -> str:
    title = old.get("title") or old.get("name")
    if isinstance(title, str) and title.strip():
        return title.strip()
    for name in ("README.md", "REPORT.md", "METHOD.md"):
        path = folder / name
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    return line[2:].strip()
    return f"GDT{number} structured experiment"


def main() -> int:
    summary = []
    for number in range(362, 385):
        folders = sorted(YOLO.glob(f"gdt{number}_*"))
        if len(folders) != 1:
            raise RuntimeError(f"GDT{number}: expected one directory, found {len(folders)}")
        folder = folders[0]
        manifest_path = folder / "experiment.json"
        old = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
        result_path = folder / "artifacts" / f"gdt{number}_result.json"
        if not result_path.is_file():
            alternatives = sorted(
                p for p in (folder / "artifacts").glob(f"gdt{number}_*result.json")
                if "validation" not in p.name and "freeze" not in p.name
            )
            if len(alternatives) != 1:
                raise RuntimeError(f"missing unambiguous compact result: {result_path}")
            result_path = alternatives[0]
        result = json.loads(result_path.read_text())
        recorded_inputs = result.get("inputs") if isinstance(result.get("inputs"), dict) else {}
        inputs = []
        historical_drift = []
        for raw_path, recorded_hash in sorted(recorded_inputs.items()):
            path = ROOT / raw_path
            if not path.is_file():
                historical_drift.append(f"MISSING:{raw_path}:{recorded_hash}")
                continue
            current = sha(path)
            if current != recorded_hash:
                historical_drift.append(f"ADVANCED:{raw_path}:{recorded_hash}:{current}")
                continue
            inputs.append({"path": raw_path, "role": "hash-bound published scientific input", "sha256": current})
        outputs = []
        for path in sorted(p for p in folder.rglob("*") if p.is_file() and p != manifest_path):
            rel = path.relative_to(ROOT).as_posix()
            outputs.append({"path": rel, "role": "retained published experiment file", "sha256": sha(path)})
        runner = RUNNERS.get(number, "src/run.py")
        validator = VALIDATORS.get(number, "src/validate.py")
        validator_path = ROOT / validator[1:] if validator.startswith("@") else folder / validator
        if not (folder / runner).is_file() or not validator_path.is_file():
            raise RuntimeError(f"GDT{number}: missing command entry point")
        if validator.startswith("@"):
            rel_validator = validator_path.relative_to(ROOT).as_posix()
            inputs.append({"path": rel_validator, "role": "administrative structured-manifest validator", "sha256": sha(validator_path)})
            validator_command = f"./vpy {rel_validator} {folder.relative_to(ROOT).as_posix()}"
        else:
            validator_command = f"./vpy {folder.relative_to(ROOT).as_posix()}/{validator}"
        validation_path = folder / "artifacts" / f"gdt{number}_validation.json"
        if not validation_path.is_file():
            alternatives = sorted(
                p for p in (folder / "artifacts").glob(f"gdt{number}_*validation.json")
                if "freeze" not in p.name
            )
            if len(alternatives) != 1:
                raise RuntimeError(f"GDT{number}: missing unambiguous final validation artifact")
            validation_path = alternatives[0]
        validation = json.loads(validation_path.read_text())
        dependencies = old.get("dependencies") if isinstance(old.get("dependencies"), list) else []
        if not dependencies:
            dependency_text = json.dumps(result, sort_keys=True)
            dependencies = sorted(
                x for x in set(re.findall(r"GDT\d{3}", dependency_text)) if x != f"GDT{number}"
            )
        status = result.get("status") or old.get("status") or "PUBLISHED"
        claim = result.get("claim_ceiling") or old.get("claim_ceiling") or "Published experiment result only; no semantic promotion."
        note = ""
        if historical_drift:
            note = f" {len(historical_drift)} historical live-path input binding(s) are preserved inside the compact result but omitted from the current-byte wrapper because the path advanced or disappeared."
        base_question = old.get("question") if isinstance(old.get("question"), str) and old.get("question").strip() else f"What did the published GDT{number} experiment establish under its frozen method?"
        if note.strip() and "historical live-path input binding(s)" not in base_question:
            base_question += note
        manifest = {
            "artifact_policy": {
                "large_artifact_justification": "Administrative binding of already published exhaustive artifacts; no new artifact generated.",
                "max_inline_bytes": max(5_000_000, max((p.stat().st_size for p in folder.rglob("*") if p.is_file()), default=0) + 1),
            },
            "claim_ceiling": str(claim),
            "commands": {
                "run": f"./vpy {folder.relative_to(ROOT).as_posix()}/{runner}",
                "validate": validator_command,
            },
            "created": old.get("created") if isinstance(old.get("created"), str) else created(result_path),
            "dependencies": dependencies,
            "experiment_id": f"GDT{number}",
            "inputs": inputs,
            "outputs": outputs,
            "question": base_question,
            "schema_version": 1,
            "sealed_data": {"f84r": "FORBIDDEN"},
            "slug": folder.name.split("_", 1)[1],
            "status": str(status),
            "title": title_from(folder, old, number),
            "updated": "2026-08-20",
            "validation": {
                "artifact": validation_path.relative_to(ROOT).as_posix(),
                "status": "PASS" if validation.get("status") == "PASS" else str(validation.get("status", "NOT_RUN")),
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        summary.append((number, len(inputs), len(outputs), len(historical_drift)))
    for row in summary:
        print("GDT%d inputs=%d outputs=%d historic_drift=%d" % row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
