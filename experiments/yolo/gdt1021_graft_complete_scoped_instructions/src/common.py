import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
A = E / 'artifacts'

def read(p):
    return json.loads(Path(p).read_text())

def write(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def inputs():
    return read(E / 'src/SPEC.json'), read(E / 'src/SOURCE.json')

def check_lock():
    lock = read(E / 'PREREG_LOCK.json')
    for p, h in lock['files'].items():
        assert sha(R / p) == h, p
