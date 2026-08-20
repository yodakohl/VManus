"""Command line entry point for structured VManus experiments."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.repository_preflight import run as preflight
from tools.guarded_tsv_query import query as query_guarded_tsv, resolve_repo_file
from tools.vmanus_experiment import ROOT, load_manifest, verify_manifest_bindings


def resolve_experiment(value: str) -> Path:
    path = (ROOT / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    if path.is_file() and path.name == "experiment.json":
        path = path.parent
    if not (path / "experiment.json").is_file():
        raise SystemExit(f"experiment manifest not found: {path}")
    return path


def run_manifest_command(experiment: Path, key: str) -> int:
    manifest = load_manifest(experiment / "experiment.json")
    errors = verify_manifest_bindings(manifest)
    if errors:
        raise SystemExit("manifest binding failure: " + "; ".join(errors))
    command = shlex.split(manifest["commands"][key])
    return subprocess.run(command, cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(prog="vmanus-exp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new = subparsers.add_parser("new", help="scaffold the next structured experiment")
    new.add_argument("slug")
    new.add_argument("--id", type=int)
    new.add_argument("--dry-run", action="store_true")

    for name in ("run", "validate", "manifest"):
        command = subparsers.add_parser(name)
        command.add_argument("experiment")

    check = subparsers.add_parser("check", help="run repository/pre-push gates")
    check.add_argument("--require-staged", action="store_true")
    check.add_argument("--all", action="store_true")

    publish = subparsers.add_parser("publish", help="preflight an exact staged tree; does not push")
    publish.add_argument("experiment", nargs="?")

    query_tsv = subparsers.add_parser(
        "query-tsv",
        help="inspect explicit rows/columns through the sealed-data TSV guard",
    )
    query_tsv.add_argument("path")
    query_tsv.add_argument("--selector", required=True)
    query_tsv.add_argument("--allow", action="append", required=True)
    query_tsv.add_argument("--columns", required=True)
    query_tsv.add_argument("--forbid-prefix", action="append")
    query_tsv.add_argument("--count-only", action="store_true")

    args = parser.parse_args()
    if args.command == "new":
        command = [sys.executable, "tools/new_yolo_experiment.py", args.slug]
        if args.id is not None:
            command.extend(["--id", str(args.id)])
        if args.dry_run:
            command.append("--dry-run")
        return subprocess.run(command, cwd=ROOT).returncode
    if args.command == "query-tsv":
        try:
            columns = [column.strip() for column in args.columns.split(",") if column.strip()]
            forbidden = tuple(args.forbid_prefix or ["f84"])
            return query_guarded_tsv(
                path=resolve_repo_file(args.path),
                selector=args.selector,
                allowed_values=set(args.allow),
                columns=columns,
                forbidden_prefixes=forbidden,
                count_only=args.count_only,
            )
        except ValueError as exc:
            parser.error(str(exc))
    if args.command in {"run", "validate"}:
        return run_manifest_command(resolve_experiment(args.experiment), args.command)
    if args.command == "manifest":
        experiment = resolve_experiment(args.experiment)
        manifest = load_manifest(experiment / "experiment.json")
        errors = verify_manifest_bindings(manifest)
        if errors:
            for error in errors:
                print("FAIL", error)
            return 1
        print("MANIFEST_PASS", manifest["experiment_id"], experiment.relative_to(ROOT))
        return 0
    if args.command == "check":
        errors = preflight(require_staged=args.require_staged, all_files=args.all)
    else:
        errors = preflight(require_staged=True, all_files=True)
        if args.experiment:
            experiment = resolve_experiment(args.experiment)
            manifest = load_manifest(experiment / "experiment.json")
            if not manifest["question"].strip():
                errors.append("experiment question is empty")
            if not manifest["claim_ceiling"].strip():
                errors.append("experiment claim ceiling is empty")
            unbound_inputs = [
                binding["path"] for binding in manifest["inputs"] if binding["sha256"] is None
            ]
            if unbound_inputs:
                errors.append("publication has unbound inputs: " + ", ".join(unbound_inputs))
            if manifest["validation"]["status"] == "PASS":
                return_code = run_manifest_command(experiment, "validate")
                if return_code:
                    errors.append(f"manifest validator exited {return_code}")
            prefix = experiment.relative_to(ROOT).as_posix() + "/"
            staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.splitlines()
            allowed_global = {
                "experiments/EXPERIMENT_INDEX.md",
                "experiments/EXPERIMENT_INDEX.tsv",
                "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv",
                "VOYNICH_CURRENT_ROUTE.md",
            }
            unrelated = [path for path in staged if not path.startswith(prefix) and path not in allowed_global]
            if unrelated:
                errors.append("staged files outside experiment publication scope: " + ", ".join(unrelated))
    if errors:
        for error in errors:
            print("FAIL", error)
        return 1
    if args.command == "publish":
        print("PUBLISH_PREFLIGHT_PASS (no commit or push performed)")
    else:
        print("REPOSITORY_PREFLIGHT_PASS")
    return 0
