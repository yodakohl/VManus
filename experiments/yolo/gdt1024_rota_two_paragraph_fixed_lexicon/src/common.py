import hashlib,json,importlib.util
from datetime import datetime,timezone
from pathlib import Path
from fractions import Fraction
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
OLD=R/'experiments/yolo/gdt1022_rota_complete_persistent_performance'
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def source():return read(E/'src/SOURCE.json')
def score():return read(R/'research_registry/work_batches/ten_hours_20260915/ROTA_SOURCE_EVENTS.json')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def check_lock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
def parts_for(sc,b):
    out={p:[] for p in ('M','P1','P2')}
    for e in sc['events']:
        t=2*Fraction(b['changes'].get(e['id'],sc['baseline_conditional_duration_breves'][e['id']]))
        assert t.denominator==1
        out[e['part']].append(dict(id=e['id'],ticks=int(t),kind='rest' if e['kind']=='pause' else e['kind'],pitch=(e.get('pitch_reading') or {}).get('midi_under_c4_octave_convention')))
    return out
