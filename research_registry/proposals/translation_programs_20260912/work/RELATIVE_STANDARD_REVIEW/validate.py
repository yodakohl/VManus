"""Check source hashes and five-line copy; inequality proof is in REPORT.md."""
import hashlib,json
from pathlib import Path
b=Path(__file__).resolve().parent;r=b.parents[4]
s=json.loads((b/'SOURCE.json').read_text())
for p,h in s['sources'].items():assert hashlib.sha256((r/p).read_bytes()).hexdigest()==h
p=r/'research_registry/proposals/translation_programs_20260912/work/P11/INPUT.json'
expected=[l for l in json.loads(p.read_text())['lines'] if l['locus'].startswith('f21r.')]
assert json.loads((b/'INPUT.json').read_text())['lines']==expected and len(expected)==5
assert next(l for l in expected if l['locus']=='f21r.11')['groups'][:3]==['shol','chol','shol']
print('PASS: source hashes and complete five-line copy; not semantic validation')
