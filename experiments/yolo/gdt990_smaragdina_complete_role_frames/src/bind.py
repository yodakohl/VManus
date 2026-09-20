#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
B = 'research_registry/work_batches/ten_hours_20260915/'
INPUTS = [B + x for x in ('SMARAGDINA_MEDIEVAL_SOURCE_COLLATION_20260920.md',
    'SMARAGDINA_MEDIEVAL_SOURCE_COLLATION_20260920.json', 'SMARAGDINA_CONTENT_TREES_DRAFT_20260920.json',
    'SMARAGDINA_CONTENT_TREE_SOURCE_AUDIT_20260920.md', 'SMARAGDINA_FIXED_CONTENT_SOURCE_CHECK_20260920.md')]
INPUTS += ['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/' + x for x in ('artifacts/PARAGRAPHS.json', 'REPORT.md', 'PREREGISTRATION.md')]
INPUTS += ['GDT282_OUTER_WRAPPER_CLASS_TRANSFER_REPORT.md']
INPUTS += ['experiments/yolo/' + x + '/REPORT.md' for x in (
    'gdt608_compositional_stem_orientation', 'gdt901_solmization_joint_relational_lexicon',
    'gdt915_terminal_lr_phrase_transfer', 'gdt958_wind_fixed_form_variation',
    'gdt982_reciprocal_flow_clause_readings', 'gdt986_anastasia_complete_condition_trees',
    'gdt987_anastasia_finite_word_proof')]
SCIENCE = ['DECISION.md', 'METHOD.md', 'PREREGISTRATION.md', 'src/SOURCE.json',
    'src/compile_source.py', 'src/model.py', 'src/run.py', 'src/validate.py', 'src/fixtures.py',
    'artifacts/PRE_RUN_FIXTURES.json', 'artifacts/SOURCE_VALIDATION.json']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--register', action='store_true')
    p.add_argument('--status', default='REGISTERED_UNSCORED')
    args = p.parse_args()
    lock = E / 'PREREG_LOCK.json'
    if args.register:
        assert not lock.exists()
        names = INPUTS + [str((E / x).relative_to(ROOT)) for x in SCIENCE]
        lock.write_text(json.dumps(dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            files={n: sha(ROOT / n) for n in names}), indent=2) + '\n')
    else:
        for n, digest in json.loads(lock.read_text())['files'].items():
            assert sha(ROOT / n) == digest, n
    m = json.loads((E / 'experiment.json').read_text())
    m.update(title='Complete medieval Tabula content with shared argument frames',
        question='Does a complete admitted paragraph realize any of the six declared Tabula branches under any of the four shared lexical-root/terminal-role writers?',
        status=args.status, claim_ceiling='Conditional full writing compatibility only; no unique inverse parser, confirmed word, search significance or independent meaning test.',
        dependencies=['GDT282', 'GDT608', 'GDT901', 'GDT915', 'GDT928', 'GDT958', 'GDT982', 'GDT986', 'GDT987'],
        inputs=[dict(path=n, role='fixed_input', sha256=sha(ROOT / n)) for n in INPUTS], outputs=[])
    for f in sorted(E.rglob('*')):
        if f.is_file() and f.name != 'experiment.json' and '__pycache__' not in f.parts and 'runtime' not in f.parts:
            m['outputs'].append(dict(path=str(f.relative_to(ROOT)), role='primary_report' if f.name == 'REPORT.md' else 'source_or_artifact', sha256=sha(f)))
    validation = E / 'artifacts/VALIDATION.json'
    if validation.exists():
        m['validation'] = dict(status=json.loads(validation.read_text())['status'], artifact=str(validation.relative_to(ROOT)))
    (E / 'experiment.json').write_text(json.dumps(m, indent=2) + '\n')
    print(json.dumps(dict(status=m['status'], inputs=len(m['inputs']), outputs=len(m['outputs']))))


if __name__ == '__main__':
    main()
