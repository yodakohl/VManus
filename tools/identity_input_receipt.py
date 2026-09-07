"""Read-only set/hash receipt for explicitly declared identity-review inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

MANIFEST = 'research_registry/IDENTITY_REVIEW_INPUTS.json'
MEANING = ('Input receipt only: no novelty, proposition identity, semantic approval, '
           'scientific verdict, or rerun authorization. File membership is not proof of reading.')


def _path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('expected repository-relative public JSON path')
    parts = PurePosixPath(value).parts
    if (PurePosixPath(value).is_absolute() or str(PurePosixPath(value)) != value
            or any(p.startswith('.') or p in {'runtime', 'private'} for p in parts)
            or not value.endswith('.json')):
        raise ValueError('expected repository-relative public JSON path')
    path = root / value
    # No symlink traversal, including symlinks that happen to stay inside root.
    if any((root.joinpath(*parts[:i])).is_symlink() for i in range(1, len(parts) + 1)):
        raise ValueError('symlink input is not allowed')
    return path


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _entries(root: Path, rows: object) -> dict[str, str]:
    if not isinstance(rows, list):
        raise ValueError('declared inputs must be an explicit list of path/sha256 objects')
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('input row must contain path and sha256')
        name, digest = row.get('path'), row.get('sha256')
        _path(root, name)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('input sha256 must be 64 lowercase hexadecimal characters')
        if name in result:
            raise ValueError('duplicate declared input path')
        result[name] = digest
    return result


def check(root: Path, declared: list[dict]) -> dict:
    """Compare required manifest membership and both sets of hashes to file bytes."""
    manifest_path = _path(root, MANIFEST)
    manifest_bytes = manifest_path.read_bytes()
    document = json.loads(manifest_bytes)
    required = _entries(root, document['inputs'])
    if not required:
        raise ValueError('authoritative input manifest must not be empty')
    supplied = _entries(root, declared)
    missing = sorted(required.keys() - supplied.keys())
    extras = sorted(supplied.keys() - required.keys())
    absent, stale_required, stale_supplied = [], [], []
    verified = []
    for name in sorted(required.keys() | supplied.keys()):
        path = _path(root, name)
        if not path.is_file():
            absent.append(name)
            continue
        actual = _digest(path)
        if name in required and required[name] != actual:
            stale_required.append(dict(path=name, expected=required[name], actual=actual))
        if name in supplied and supplied[name] != actual:
            stale_supplied.append(dict(path=name, expected=supplied[name], actual=actual))
        if name in required and name in supplied and required[name] == supplied[name] == actual:
            verified.append(name)
    complete = not (missing or absent or stale_required or stale_supplied)
    return dict(status='INPUT_COVERAGE_PASS' if complete else 'INPUT_COVERAGE_INCOMPLETE',
                meaning=MEANING, manifest=dict(path=MANIFEST, sha256=hashlib.sha256(manifest_bytes).hexdigest()),
                required_count=len(required), declared_count=len(supplied),
                required_verified_count=len(verified), required_verified=verified,
                required_set_covered=not missing, exact_set_match=not missing and not extras,
                all_required_current=len(verified) == len(required),
                missing_required=missing, extra_declared=extras, missing_files=absent,
                stale_manifest_hashes=stale_required, stale_declared_hashes=stale_supplied)


def main(argv: list[str] | None = None, *, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(prog='vmanus-work identity-inputs', description=MEANING)
    parser.add_argument('--declared', required=True, help='explicit public JSON file; list or object containing inputs')
    parser.add_argument('--field', help='explicit dot-separated object field containing the list, e.g. prior_identity_screen.paths_and_hashes')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1] if root is None else root
    try:
        path = _path(root, args.declared)
        declaration_bytes = path.read_bytes()
        data = json.loads(declaration_bytes)
        default_field = 'inputs' if isinstance(data, dict) else None
        if args.field:
            for key in args.field.split('.'):
                data = data[key]
        elif isinstance(data, dict):
            data = data['inputs']
        receipt = check(root, data)
        receipt['declaration'] = dict(path=args.declared, sha256=hashlib.sha256(declaration_bytes).hexdigest(), field=args.field or default_field)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Do not echo exception text: filesystem errors may contain private paths.
        print(json.dumps(dict(status='INVALID_INPUT_DECLARATION', meaning=MEANING,
                              error=type(exc).__name__), sort_keys=True))
        return 2
    # CLI stays bounded; check() retains complete arrays for machine receipts.
    receipt.pop('required_verified', None)
    receipt['diagnostic_limit'] = 20
    receipt['truncated_fields'] = []
    for field in ('missing_required', 'extra_declared', 'missing_files',
                  'stale_manifest_hashes', 'stale_declared_hashes'):
        receipt[field + '_count'] = len(receipt[field])
        if len(receipt[field]) > 20:
            receipt['truncated_fields'].append(field)
            receipt[field] = receipt[field][:20]
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt['status'] == 'INPUT_COVERAGE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
