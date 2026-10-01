"""Gated source acquisition, independent source audit and literal transfer."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    specpath = E / 'src/SPEC.json'
    openingpath = E / 'artifacts/OPEN_RECEIPT.json'
    spec = json.loads(specpath.read_text())
    opening = json.loads(openingpath.read_text())
    if spec['status'] != 'PREOPEN_FROZEN' or opening['status'] != 'ROOT_EXPLICIT_APPLICATION_GO' or opening['spec_sha256'] != sha(specpath):
        raise SystemExit('Explicit application GO/frozen specification required')
    for path, expected in spec['input_hashes'].items():
        if sha(ROOT / path) != expected:
            raise SystemExit('Frozen input changed: ' + path)
    subprocess.run([sys.executable, str(E/'src/prepare_source.py')], cwd=ROOT, check=True)
    # Add source-byte binding only. Preserve original root GO and all model pins.
    opening['source_packet_sha256'] = sha(E/'artifacts/APPLICATION_PACKET.json')
    opening['source_groups_sha256'] = sha(E/'artifacts/APPLICATION_GROUPS.tsv')
    opening['source_ready'] = True
    openingpath.write_text(json.dumps(opening, ensure_ascii=False, indent=2)+'\n')
    subprocess.run([sys.executable, str(E/'src/validate_source.py'), '--spec-sha256', sha(specpath), '--open-receipt-sha256', sha(openingpath)], cwd=ROOT, check=True)
    evidence = json.loads((E/'artifacts/SOURCE_VALIDATION.json').read_text())
    if evidence['status'] != 'PASS':
        raise SystemExit('Independent source validation failed; no model scoring')
    subprocess.run([sys.executable, str(E/'src/apply_fv.py')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(E/'src/apply_fw.py')], cwd=ROOT, check=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
