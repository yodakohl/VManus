from pathlib import Path
import argparse
import datetime
import hashlib
import json

E = Path(__file__).resolve().parents[1]
R = E.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


p = argparse.ArgumentParser()
p.add_argument('--register', action='store_true')
a = p.parse_args()
d = 'research_registry/work_batches/ten_hours_20260915/'
up = [d + n for n in ['ROTA_CONTENT_DECISION.md', 'ROTA_SOURCE_EVENTS.md', 'ROTA_SOURCE_EVENTS.json', 'ROTA_SOURCE_EVENTS_PRECOMPARISON.json', 'ROTA_PES_RULES_INDEPENDENT.md', 'ROTA_PES_RULES_INDEPENDENT.json', 'ROTA_SOURCE_VALIDATION.json', 'ROTA_VARIABLE_CODE_REVIEW.md', 'rota_source_events.py', 'validate_rota_source.py']]
prior = 'experiments/yolo/gdt915_terminal_lr_phrase_transfer/'
up += [prior + 'src/SPEC.json'] + [prior + 'artifacts/SOURCE_' + phase + '_' + ed + '.json' for phase in ['DISCOVERY', 'EVALUATION'] for ed in ['ZL3b', 'IT2a', 'RF1b']]
up += ['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/' + n for n in ['src/run.py', 'PREREG_LOCK.json', 'PREREGISTRATION.md']]
up += ['docs/VOYNICH_DATA_SCOPE.md']
lock = E / 'PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    own = ['README.md', 'METHOD.md', 'PREREGISTRATION.md', 'src/run.py', 'src/bind.py', 'artifacts/SOURCE_CONSEQUENCES.json', 'artifacts/PREFLIGHT.json']
    paths = [E / n for n in own] + [R / n for n in up]
    write(lock, {'registered_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'stage': 'SOURCE_AND_SYNTHETICS_ONLY_BEFORE_TARGET_CYCLE_CENSUS', 'files': {f.relative_to(R).as_posix(): sha(f) for f in paths}})
for name, expected in json.loads(lock.read_text())['files'].items():
    assert sha(R / name) == expected, name
manifest = json.loads((E / 'experiment.json').read_text())
result = E / 'artifacts/RESULT.json'
validation = E / 'artifacts/VALIDATION.json'
v = json.loads(validation.read_text())['status'] if validation.exists() else 'NOT_RUN'
if v == 'PASS_REGISTRATION_ONLY':
    v = 'NOT_RUN'
rel = E.relative_to(R).as_posix()
manifest.update(title='Complete musical-part cyclic consequence', question='Do any distinct complete literal paragraphs have the necessary glyph conjugacy of the two whole Reading Rota pes parts under one global variable-width event code?', claim_ceiling='Necessary structural consequence only; no full code, musical identity, confirmed word, significance or independent meaning confirmation.', status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED', dependencies=['GDT607', 'GDT608', 'GDT898', 'GDT901', 'GDT915', 'GDT928'], inputs=[{'path': n, 'sha256': sha(R / n), 'role': 'fixed_scope_source_or_review'} for n in up], outputs=[{'path': f.relative_to(R).as_posix(), 'sha256': sha(f), 'role': 'primary_report' if f.name == 'REPORT.md' else 'source_or_artifact'} for f in sorted(E.rglob('*')) if f.is_file() and f.name != 'experiment.json' and not {'runtime', '__pycache__'}.intersection(f.relative_to(E).parts)], validation={'status': v, 'artifact': rel + '/artifacts/VALIDATION.json' if validation.exists() else None})
manifest['commands'] = {'run': 'python3 ' + rel + '/src/run.py', 'validate': 'python3 ' + rel + '/src/validate.py'}
manifest['artifact_policy']['large_artifact_justification'] = 'Complete paragraph provenance, prediction rows and all equal-length pair consequences; unequal lengths exhaustively represented by the full length partition. No images or reserve data.'
write(E / 'experiment.json', manifest)
print(manifest['status'])
