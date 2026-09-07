"""Read-only verification of the session's append-only history preservation."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
baseline = 'e76e60a255f6c3ddf1d83c971d035fb995f1428c'
paths = [
    'research_registry/curation.jsonl',
    'research_registry/ideas.jsonl',
    'research_registry/semantic_identity_decisions.jsonl',
    'research_registry/semantic_failure_decisions.jsonl',
    'research_registry/semantic_claim_corrections.jsonl',
    'research_registry/semantic_priority_decisions.jsonl',
    'experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv',
]
checks = []
for path in paths:
    old = subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=root)
    current = (root / path).read_bytes()
    assert current.startswith(old), path
    checks.append({
        'path': path,
        'baseline_bytes': len(old),
        'baseline_prefix_exact': True,
        'appended_bytes': len(current) - len(old),
        'current_sha256': hashlib.sha256(current).hexdigest(),
    })
print(json.dumps({
    'status': 'ALL_SEVEN_DECISION_AND_LEDGER_PREFIXES_BYTE_PRESERVED',
    'baseline_commit': baseline,
    'checks': checks,
    'scope': 'Exact byte prefix preservation for append-only decisions, authored proposals and material ledger. Derived import/card views use their separate reconstruction/source-case tests.',
}, indent=2))
