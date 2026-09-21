"""Bind immutable scientific inputs and the evolving public result artifacts."""
from common import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--lock', action='store_true')
parser.add_argument('--status', default='REGISTERED_UNSCORED')
args = parser.parse_args()
s, g = inputs()
inputs_ = list(dict.fromkeys(v for k, v in s.items()
                            if k.startswith('source_') or k in ('grammar', 'model', 'bit_replay', 'binding_checker')))


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    science = ['DECISION.md', 'METHOD.md', 'PREREGISTRATION.md', 'requirements.txt',
               'artifacts/PANEL.json', 'artifacts/PREDICTIONS.json',
               'artifacts/ORIGINAL_CANDIDATES.json', 'artifacts/SOURCE_GRAPH_CHECK.json',
               'artifacts/MODEL_DELTA.json', 'artifacts/PREPUBLIC_CORRECTIONS.json',
               'artifacts/PREFLIGHT.json']
    science += [str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file()]
    write(E/'PREREG_LOCK.json', dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                    files={x: sha(R/x) for x in inputs_ + [str((E/x).relative_to(R)) for x in science]}))
m = read(E/'experiment.json')
m.update(question='Which complete paired transport readings preserve both directions of a shared positive cargo-type hazard union?',
         claim_ceiling='Conditional complete candidate consequences only; no independently confirmed meaning or significance; older laws and positive worlds retained.',
         dependencies=['GDT928', 'GDT993', 'GDT994', 'GDT1006', 'GDT1011', 'GDT1012', 'GDT1013'],
         status=args.status,
         inputs=[dict(path=x, role='fixed_input', sha256=sha(R/x)) for x in inputs_], outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name != 'experiment.json' and '__pycache__' not in p.parts:
        m['outputs'].append(dict(path=str(p.relative_to(R)), role='primary_report' if p.name == 'REPORT.md' else 'source_or_artifact', sha256=sha(p)))
if (A/'VALIDATION.json').exists():
    m['validation'] = dict(status=read(A/'VALIDATION.json')['status'], artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json', m)
