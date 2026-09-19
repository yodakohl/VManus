"""Bind post-result diagnostics in addition to the unchanged registered inputs."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

E=Path(__file__).resolve().parents[1]; R=E.parents[2]
subprocess.run([sys.executable,str(E/'src/bind.py')],check=True)
m=json.loads((E/'experiment.json').read_text())
extra=json.loads((E/'artifacts/SUPPLEMENT_INPUTS.json').read_text())
for name in ['tools/relation_edge_intake.py','tools/vmanus_experiment.py']:
    extra.append(dict(path=name,sha256=hashlib.sha256((R/name).read_bytes()).hexdigest(),role='post_result_gate_implementation'))
for item in extra:
    assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']
    assert item['path'] not in {i['path'] for i in m['inputs']}
    m['inputs'].append(item)
(E/'experiment.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
