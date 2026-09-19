"""Preserve the registered binder; select the disclosed corrected validator."""
import json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
subprocess.run([sys.executable,str(E/'src/bind.py')],check=True)
p=E/'experiment.json';m=json.loads(p.read_text());m['commands']['validate']='python3 '+(E/'src/validate_projection.py').relative_to(R).as_posix()+' --full';p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
