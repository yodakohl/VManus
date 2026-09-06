#!/usr/bin/env python3
"""Source/record validation only. Never renders or analyzes image content."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
URL = 'https://collections.library.yale.edu/iiif/2/1006199/full/full/0/default.jpg'
SELECTORS = ['f69v', 'f70r1', 'f70r2']
CEILING = 'Personal orientation only; no slot count, traversal, glyph, ownership, semantic or translation claim'
COMPLETE = 'COMPLETE_PERSONAL_ORIENTATION_SOURCE_BOUNDARY'
LIMIT = 'Software validates source identity, file metadata and record declarations only; it does not validate image content, native perception, or the truth of the observational notes.'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fixed_source(source):
    require(source['canvas_id'] == '1006199', 'wrong canvas')
    require(source['image_url'] == URL, 'wrong original image URL')
    require(source['width'] == 8886 and source['height'] == 3876, 'wrong registered dimensions')
    require(source['represented_selectors'] == SELECTORS, 'wrong represented selectors')


def check_observation(observation, sha):
    require(observation['observer'] == 'ROOT', 'observer must be ROOT')
    require(observation['viewed'] is True, 'viewed must be true')
    require(observation['mode'] == 'NATIVE_FULL_ORIGINAL', 'wrong viewing mode')
    require(observation['source_sha256'] == sha, 'observation source mismatch')
    require(isinstance(observation['viewed_at_utc'], str) and observation['viewed_at_utc'].strip(), 'view timestamp required')
    require(observation['claim_ceiling'] == CEILING, 'observation claim ceiling mismatch')
    require(isinstance(observation['notes'], list) and bool(observation['notes'])
            and all(isinstance(n, str) and n.strip() for n in observation['notes']), 'nonempty text notes required')


def controls():
    source = dict(canvas_id='1006199', image_url=URL, width=8886, height=3876, represented_selectors=SELECTORS)
    fixed_source(source)
    observation = dict(observer='ROOT', viewed=True, mode='NATIVE_FULL_ORIGINAL', source_sha256='fixture', viewed_at_utc='2026-09-06T00:00:00Z', notes=['Synthetic metadata fixture.'], claim_ceiling=CEILING)
    check_observation(observation, 'fixture')
    for key, value in [('observer', 'AGENT'), ('viewed', False), ('mode', 'CROP'), ('source_sha256', 'other'), ('claim_ceiling', 'Translation')]:
        bad = dict(observation, **{key: value})
        try:
            check_observation(bad, 'fixture')
        except ValueError:
            pass
        else:
            raise AssertionError('negative metadata control accepted: ' + key)
    print(json.dumps({'status': 'CONTROLS_PASS', 'scope': 'SYNTHETIC_METADATA_ONLY', 'limitation': LIMIT}, sort_keys=True))


def check_lock():
    lock_path = EXP / 'src/PREREG_LOCK.json'
    lock = read(lock_path)
    require(isinstance(lock, dict) and bool(lock), 'empty preregistration lock')
    for relative, expected in lock.items():
        require(isinstance(relative, str) and isinstance(expected, str), 'flat path/hash lock required')
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'invalid locked path')
        require(digest(path) == expected, 'locked file hash mismatch: ' + relative)
    required = {str((EXP / p).relative_to(ROOT)) for p in ['METHOD.md', 'src/SPEC.json', 'SOURCES.json', 'src/PAGE_ADMISSIONS.tsv', 'src/run.py', 'src/validate.py']}
    require(required <= set(lock), 'required preregistered source/code missing from lock')
    return len(lock)


def validate():
    observation_path = EXP / 'artifacts/OBSERVATION.json'
    if not observation_path.is_file():
        return {'status': 'NOT_RUN', 'reason': 'MISSING_OBSERVATION', 'image_content_validated': False, 'limitation': LIMIT}
    locked = check_lock()
    source = read(EXP / 'SOURCES.json')
    fixed_source(source)
    spec = read(EXP / 'src/SPEC.json')
    require(spec['experiment_id'] == 'GDT867', 'wrong experiment')
    require(spec['source_scope'] == SELECTORS and spec['sealed_data'] == ['f84', 'f84r'], 'spec source/sealed scope')
    require(spec['mode'] == 'NATIVE_FULL_ORIGINAL' and spec['observer'] == 'ROOT' and spec['claim_ceiling'] == CEILING, 'spec observer/mode/ceiling')
    require(spec['new_physical_key'] == 'f70r' and spec['image_path'] == 'runtime/1006199.jpg', 'spec new key/image path')
    with (EXP / 'src/PAGE_ADMISSIONS.tsv').open(newline='') as handle:
        admissions = list(csv.DictReader(handle, delimiter='\t'))
    require(len(admissions) == 2, 'exactly two new selector mappings required')
    require({(r['physical_page'], r['source_selector']) for r in admissions} == {('f70r', 'f70r1'), ('f70r', 'f70r2')}, 'new admission mapping mismatch')
    require(all(r['decision'] == 'ADMITTED' for r in admissions), 'admission decision mismatch')
    metadata = read(EXP / 'artifacts/IMAGE_METADATA.json')
    require(metadata['viewed_at_acquisition'] is False, 'acquisition must not claim a native view')
    path = EXP / 'runtime/1006199.jpg'
    require(path.is_file(), 'original file missing')
    size = path.stat().st_size
    sha = digest(path)
    require(metadata['sha256'] == sha and metadata['bytes'] == size, 'original bytes/hash mismatch')
    from PIL import Image
    with Image.open(path) as original:
        dimensions, image_format = original.size, original.format
    require(dimensions == (8886, 3876) and image_format == 'JPEG', 'original header dimensions/format mismatch')
    for field in ('canvas_id', 'image_url', 'width', 'height'):
        require(metadata[field] == source[field], 'acquisition metadata mismatch: ' + field)
    check_observation(read(observation_path), sha)
    result_path = EXP / 'artifacts/RESULT.json'
    if not result_path.is_file():
        return {'status': 'NOT_RUN', 'reason': 'MISSING_RESULT', 'image_content_validated': False, 'limitation': LIMIT}
    result = read(result_path)
    require(result['status'] == COMPLETE, 'result status mismatch')
    require(result['source_sha256'] == sha and result['claim_ceiling'] == CEILING, 'result provenance/ceiling mismatch')
    return {'status': 'PASS', 'locked_files_checked': locked, 'canvas_id': '1006199', 'source_sha256': sha,
            'bytes': size, 'dimensions': list(dimensions), 'new_admission_mappings': 2,
            'image_content_validated': False, 'limitation': LIMIT}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--no-write', action='store_true')
    args = parser.parse_args()
    if args.controls:
        controls()
        return 0
    try:
        result = validate()
    except (ValueError, KeyError, OSError, TypeError) as error:
        result = {'status': 'FAIL', 'reason': str(error), 'image_content_validated': False, 'limitation': LIMIT}
    payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if not args.no_write:
        (EXP / 'artifacts/VALIDATION.json').write_text(payload)
    print(payload, end='')
    return 0 if result['status'] == 'PASS' else 2 if result['status'] == 'NOT_RUN' else 1


if __name__ == '__main__':
    raise SystemExit(main())
