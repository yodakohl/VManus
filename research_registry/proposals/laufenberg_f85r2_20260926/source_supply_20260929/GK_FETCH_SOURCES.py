"""Retrieve only the seven pinned external historical images; no Voynich access."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    receipt = json.loads(Path(__file__).with_name('GK_SOURCE_RECEIPT.json').read_text())
    args.directory.mkdir(parents=True, exist_ok=True)
    results = []
    for row in receipt['images']:
        destination = args.directory / row['file']
        if not args.verify_only:
            with urlopen(row['url'], timeout=40) as response:
                payload = response.read()
            if hashlib.sha256(payload).hexdigest() != row['sha256']:
                raise ValueError('Provider bytes changed: ' + row['key'])
            destination.write_bytes(payload)
        payload = destination.read_bytes()
        valid = len(payload) == row['bytes'] and hashlib.sha256(payload).hexdigest() == row['sha256']
        results.append({'key': row['key'], 'pinned_bytes_match': valid})
    print(json.dumps({'scope':'Delivery bytes only, not source interpretation', 'results':results}, indent=2))
    if not all(row['pinned_bytes_match'] for row in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
