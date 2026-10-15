#!/usr/bin/env python3
"""Independent metadata/schema/decision audit; imports no runner.

JPEG dimensions are obtained from encoded frame headers without displaying or
decoding pixels. Validation cannot establish observer judgment or permissions.
"""
from collections import Counter
from datetime import datetime
import hashlib
from itertools import product
import json
from pathlib import Path


def find_repo_root(start):
    for candidate in (start, *start.parents):
        if (candidate / 'vmanus-work').is_file():
            return candidate
    raise RuntimeError('VManus tool entry point not found')


ROOT = find_repo_root(Path(__file__).resolve().parent)
B = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'middle_body': ['A_LIKE', 'O_LIKE', 'UNRESOLVED'],
    'left_seam': ['SPACE_LIKE', 'INTERNAL_LIKE', 'UNRESOLVED'],
    'right_seam': ['SPACE_LIKE', 'INTERNAL_LIKE', 'UNRESOLVED'],
}


class Invalid(Exception):
    pass


class Audit:
    def __init__(self):
        self.count = 0
        self.stages = []

    def check(self, truth, message):
        self.count += 1
        if not truth:
            raise Invalid(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timestamp(value):
    if not isinstance(value, str):
        raise Invalid('Timestamp must be a string')
    parsed = datetime.fromisoformat(value.replace(' UTC', '+00:00').replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise Invalid('Timestamp requires a timezone')
    return parsed


def jpeg_dimensions(data):
    if data[:2] != b'\xff\xd8':
        raise Invalid('Fixed input is not a JPEG stream')
    index = 2
    frames = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
              0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while index < len(data):
        if data[index] != 255:
            raise Invalid('Unexpected JPEG header boundary')
        while index < len(data) and data[index] == 255:
            index += 1
        if index >= len(data):
            break
        marker = data[index]
        index += 1
        if marker in {0xD9, 0xDA}:
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD8:
            continue
        if index + 2 > len(data):
            raise Invalid('Truncated JPEG segment length')
        length = int.from_bytes(data[index:index + 2], 'big')
        if length < 2 or index + length > len(data):
            raise Invalid('Invalid JPEG segment length')
        if marker in frames:
            if length < 8:
                raise Invalid('Truncated JPEG frame header')
            height = int.from_bytes(data[index + 3:index + 5], 'big')
            width = int.from_bytes(data[index + 5:index + 7], 'big')
            return width, height
        index += length
    raise Invalid('JPEG frame dimensions not found')


def independent_decision(records):
    """Category multiplicities, rather than importing producer comparison."""
    located = sum(record['localized'] is True for record in records) == 2
    combined = {}
    for field in CATEGORIES:
        counts = Counter(record[field] for record in records)
        accepted = [category for category, number in counts.items()
                    if number == 2 and category != 'UNRESOLVED']
        combined[field] = accepted[0] if located and len(accepted) == 1 else 'UNRESOLVED'
    middle = combined['middle_body']
    status = {'A_LIKE': 'LOCAL_AR_COMPATIBILITY',
              'O_LIKE': 'LOCAL_OR_COMPATIBILITY',
              'UNRESOLVED': 'UNRESOLVED'}[middle]
    cap = 'UNRESOLVED'
    if middle == 'A_LIKE':
        cap = 'AR_BRANCH_SUPPORTED_NOT_P2_CONFIRMED'
    if middle == 'O_LIKE' and all(combined[s] == 'SPACE_LIKE'
                                 for s in ['left_seam', 'right_seam']):
        cap = 'CONDITIONAL_THREE_OR_COUNTERCASE'
    return combined, status, cap


def controls(audit):
    def record(middle='O_LIKE', left='SPACE_LIKE', right='SPACE_LIKE', localized=True):
        return dict(middle_body=middle, left_seam=left, right_seam=right, localized=localized)
    fixtures = [
        ('ar_despite_internal_seams', [record('A_LIKE', 'INTERNAL_LIKE', 'INTERNAL_LIKE')] * 2,
         'LOCAL_AR_COMPATIBILITY', 'AR_BRANCH_SUPPORTED_NOT_P2_CONFIRMED'),
        ('or_two_spaces', [record(), record()],
         'LOCAL_OR_COMPATIBILITY', 'CONDITIONAL_THREE_OR_COUNTERCASE'),
        ('or_internal_left', [record(left='INTERNAL_LIKE')] * 2,
         'LOCAL_OR_COMPATIBILITY', 'UNRESOLVED'),
        ('or_uncertain_right', [record(), record(right='UNRESOLVED')],
         'LOCAL_OR_COMPATIBILITY', 'UNRESOLVED'),
        ('body_disagreement', [record(), record('A_LIKE')], 'UNRESOLVED', 'UNRESOLVED'),
        ('missing_localization', [record(), record(localized=False)], 'UNRESOLVED', 'UNRESOLVED'),
        ('explicit_body_unknown', [record(), record('UNRESOLVED')], 'UNRESOLVED', 'UNRESOLVED'),
    ]
    reports = []
    for name, inputs, expected_status, expected_cap in fixtures:
        combined, status, cap = independent_decision(inputs)
        audit.check((status, cap) == (expected_status, expected_cap), 'Decision control: ' + name)
        reports.append({'name': name, 'inputs': inputs, 'combined': combined,
                        'expected_status': expected_status, 'actual_status': status,
                        'expected_p2_consequence': expected_cap, 'actual_p2_consequence': cap})
    # Every field's unanimity/localization rule, including preserving unrelated
    # seam agreement when only the middle-body ratings disagree.
    for field, categories in CATEGORIES.items():
        for first, second, loc_a, loc_b in product(categories, categories, [False, True], [False, True]):
            a, b = record(localized=loc_a), record(localized=loc_b)
            a[field], b[field] = first, second
            got = independent_decision([a, b])[0][field]
            expected = first if loc_a and loc_b and first == second and first != 'UNRESOLVED' else 'UNRESOLVED'
            audit.check(got == expected, 'Field-level decision truth table')
    combined = independent_decision([record(), record('A_LIKE')])[0]
    audit.check(combined == {'middle_body': 'UNRESOLVED', 'left_seam': 'SPACE_LIKE',
                            'right_seam': 'SPACE_LIKE'}, 'Independent field combination')
    audit.stages.append('Seven named synthetic decisions and complete field-level truth tables')
    return reports


def main():
    audit = Audit()
    out = {'experiment_id': 'GDT1385', 'status': 'FAIL',
           'qualification': 'Metadata, source bytes, declared schemas, seal and mechanical decision only. '
                            'No approval of scope interpretation and no verification of visual alignment, '
                            'observer authority, actual blinding, palaeographic truth or word meaning.'}
    try:
        out['synthetic_controls'] = controls(audit)
        spec_path = B / 'src/SPEC.json'
        spec = read(spec_path)
        audit.check(spec['experiment_id'] == 'GDT1385', 'Specification experiment identity')
        audit.check(spec['ratings'] == CATEGORIES, 'Frozen category inventories')
        audit.check(spec['sealed_data'].get('f84') == 'FORBIDDEN'
                    and spec['sealed_data'].get('f84r') == 'FORBIDDEN', 'Explicit sealed folios')
        scope = B / 'SCOPE_DECISION.md'
        audit.check(sha(scope) == spec['scope_decision_sha256'], 'Recorded scope document hash')
        image_path = ROOT / spec['image']['path']
        data = image_path.read_bytes()
        actual_dimensions = jpeg_dimensions(data)
        audit.check(hashlib.sha256(data).hexdigest() == spec['image']['sha256'], 'Fixed JPEG hash')
        audit.check(len(data) == spec['image']['bytes'], 'Fixed JPEG byte count')
        audit.check(actual_dimensions == (spec['image']['width'], spec['image']['height'])
                    == (2793, 3769), 'Fixed JPEG dimensions from frame metadata')
        audit.stages.append('Source image hash/bytes/dimensions and scope-document binding, without display')
        paths = [B / 'artifacts/NATIVE_A.json', B / 'artifacts/NATIVE_B.json']
        records = [read(p) for p in paths]
        for record in records:
            audit.check(isinstance(record, dict), 'Observation object')
            audit.check(all(key in record for key in spec['required_fields']), 'Required observation fields')
            audit.check(isinstance(record['observer'], str) and bool(record['observer'].strip()), 'Named observer')
            audit.check(type(record['localized']) is bool, 'Boolean localization')
            audit.check(record['image_sha256'] == spec['image']['sha256'], 'Same fixed observed image')
            for field, categories in CATEGORIES.items():
                audit.check(record[field] in categories, 'Allowed observation category: ' + field)
            for field in ['location_note', 'middle_observation', 'spacing_observation', 'limits']:
                value = record[field]
                nonempty = ((isinstance(value, str) and bool(value.strip())) or
                            (isinstance(value, list) and bool(value)
                             and all(isinstance(x, str) and bool(x.strip()) for x in value)))
                audit.check(nonempty, 'Nonempty descriptive observation: ' + field)
            audit.check(timestamp(record['observed_utc']) >= timestamp(spec['registered_utc']),
                        'Recorded observation timestamp follows registration')
        audit.check(records[0]['observer'] != records[1]['observer'], 'Distinct observer labels')
        seal_path = B / 'artifacts/A_SEAL.json'
        seal = read(seal_path)
        audit.check(all(k in seal for k in ['path', 'sha256', 'sealed_utc']), 'A seal fields')
        declared_path = Path(seal['path'])
        audit.check(not declared_path.is_absolute(), 'Publication-safe relative seal path')
        audit.check(any((base / declared_path).resolve() == paths[0].resolve() for base in [ROOT, B, B / 'artifacts']),
                    'A seal identifies exactly NATIVE_A')
        audit.check(seal['sha256'] == sha(paths[0]), 'A sealed observation hash')
        audit.check(timestamp(seal['sealed_utc']) >= timestamp(records[0]['observed_utc']),
                    'Recorded A seal time follows observation')
        # B may observe concurrently. A-before-root-receives-B is a human
        # workflow obligation, not inferable from B's observed_utc timestamp.
        audit.stages.append('Two record schemas, same-image pins and recorded A seal chronology')
        result = read(B / 'artifacts/RESULT.json')
        combined, status, cap = independent_decision(records)
        expected = {'schema_version': 1, 'experiment_id': 'GDT1385', 'status': status,
                    'combined': combined, 'p2_consequence': cap, 'spec_sha256': sha(spec_path),
                    'scope_decision_sha256': sha(scope), 'image_sha256': spec['image']['sha256'],
                    'record_sha256': {p.name: sha(p) for p in paths},
                    'both_localized': all(r['localized'] is True for r in records)}
        for key, value in expected.items():
            audit.check(result.get(key) == value, 'Independent result reconstruction: ' + key)
        audit.check(isinstance(result.get('limits'), list) and len(result['limits']) >= 4,
                    'Result preserves epistemic limitations')
        audit.stages.append('Independent category/status/P2 consequence and provenance reconstruction')
        out.update(status='PASS', combined=combined, observation_status=status,
                   p2_consequence=cap, image_dimensions=list(actual_dimensions),
                   spec_sha256=sha(spec_path), result_sha256=sha(B / 'artifacts/RESULT.json'),
                   record_sha256=expected['record_sha256'], a_seal_sha256=sha(seal_path))
    except Invalid as exc:
        out['failure'] = str(exc)
    except Exception as exc:
        out['failure'] = 'Unexpected validation error: ' + type(exc).__name__
    out['checks'] = audit.count
    out['completed_stages'] = audit.stages
    (B / 'artifacts/VALIDATION.json').write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': out['status'], 'checks': audit.count,
                      'failure': out.get('failure')}, sort_keys=True))
    return 0 if out['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
