import gzip
import hashlib
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
PACKET = ROOT / 'research_registry/proposals/production_origin_supply_20261003/source_rule_package'
BOOKS = ('b4', 'b6', 'br1', 'bs1', 'gr1', 'w1')
ARMS = ('U', 'C', 'S')
START = '\x02' * 4


def load(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       indent=None if path.suffix == '.gz' else 2) + '\n').encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def objhash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def alternatives(ch, classes):
    return sorted(set(classes.get(ch, {'alternatives': [ch]})['alternatives']))


def segments(groups, field):
    out, current, previous = [], [], object()
    for w in groups:
        value = w[field]
        unknown = value is None
        record = w['record']
        if unknown or record is None or record != previous:
            if current:
                out.append(current)
            current = []
        if not unknown:
            current.append(w)
        if record is None:
            if current:
                out.append(current)
            current = []
        previous = record
    if current:
        out.append(current)
    return out
