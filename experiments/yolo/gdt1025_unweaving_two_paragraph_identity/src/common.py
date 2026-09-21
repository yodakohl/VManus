import json,hashlib,importlib.util
from pathlib import Path
from datetime import datetime,timezone
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
OLD=R/'experiments/yolo/gdt1020_unweaving_complete_assertion_graph'
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
temporal_witness=module('old_temporal_common',OLD/'src/common.py').temporal_witness
def check_lock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
def source():return read(E/'src/SOURCE.json')
def spec():return read(E/'src/SPEC.json')
