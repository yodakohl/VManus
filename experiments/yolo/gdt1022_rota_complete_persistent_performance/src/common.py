import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

E=Path(__file__).resolve().parents[1]
R=E.parents[2]
A=E/'artifacts'

def read(p): return json.loads(Path(p).read_text())
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def compact(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def source(): return read(E/'src/SOURCE.json')
def score(): return read(R/'research_registry/work_batches/ten_hours_20260915/ROTA_SOURCE_EVENTS.json')

def check_lock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items(): assert sha(R/p)==h,p

def source_parts(s,b):
    durations=dict(s['baseline_conditional_duration_breves'])
    durations.update(b['changes'])
    parts={k:[] for k in ('M','P1','P2')}
    for e in s['events']:
        ticks=Fraction(durations[e['id']])*2
        assert ticks.denominator==1 and ticks>0
        parts[e['part']].append(dict(id=e['id'],ticks=int(ticks),kind='rest' if e['kind']=='pause' else e['kind'],
            pitch=(e.get('pitch_reading') or {}).get('midi_under_c4_octave_convention')))
    return parts
