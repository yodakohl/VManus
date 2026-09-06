"""Acquire fixed original or package root's actual native observation."""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from PIL import Image

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--acquire', action='store_true')
    args = parser.parse_args()
    for path, expected in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():
        assert digest(ROOT/path) == expected, path
    spec = json.loads((E/'src/SPEC.json').read_text())
    source = json.loads((E/'SOURCES.json').read_text())
    if args.acquire:
        path = E/spec['image_path']
        path.parent.mkdir(exist_ok=True)
        if not path.exists():
            with urllib.request.urlopen(source['image_url'], timeout=60) as response:
                data = response.read()
            path.write_bytes(data)
        with Image.open(path) as im:
            assert im.size == (source['width'], source['height']), im.size
            assert im.format == 'JPEG', im.format
        write(E/'artifacts/IMAGE_METADATA.json', {
            'canvas_id': source['canvas_id'], 'image_url': source['image_url'],
            'width': source['width'], 'height': source['height'],
            'bytes': path.stat().st_size, 'sha256': digest(path),
            'viewed_at_acquisition': False,
        })
        print('ACQUIRED_METADATA_ONLY_NOT_VIEWED')
        return
    observation = json.loads((E/'artifacts/OBSERVATION.json').read_text())
    metadata = json.loads((E/'artifacts/IMAGE_METADATA.json').read_text())
    assert observation['observer'] == 'ROOT'
    assert observation['viewed'] is True
    assert observation['mode'] == 'NATIVE_FULL_ORIGINAL'
    assert observation['claim_ceiling'] == spec['claim_ceiling']
    assert observation['source_sha256'] == metadata['sha256']
    write(E/'artifacts/RESULT.json', {
        'status': 'COMPLETE_PERSONAL_ORIENTATION_SOURCE_BOUNDARY',
        'source_sha256': metadata['sha256'], 'claim_ceiling': spec['claim_ceiling'],
    })
    print('COMPLETE_PERSONAL_ORIENTATION_SOURCE_BOUNDARY')

if __name__ == '__main__':
    main()
