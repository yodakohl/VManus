import datetime,hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,R/p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def checklock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
def inputs():
    s=read(E/'src/SPEC.json');g=read(R/s['grammar']);return s,g
def replay(parse,variant,s,independent=False):
    if independent:
        error=load(s['binding_checker'],'binding994').binding_error(parse,variant)
        if error:return dict(status='BINDING_CONTRADICTION',error=error)
        paths,hazards,refs=load(s['bit_replay'],'bit1006').replay(parse,variant)
        cargo=sorted({t for c in parse for t in c['symbols'] if t in ('W','G','C')})
        for p in paths:
            for state in [p,*p['trace']]:state['positions']={k:v for k,v in state['positions'].items() if k in set(cargo)|{'M','B'}}
    else:
        m=load(s['model'],'model993')
        try:program=m.compile_reading(parse,variant)
        except ValueError as e:return dict(status='BINDING_CONTRADICTION',error=str(e))
        paths=m.execute(program,variant);hazards=program['hazards'];refs=program['references'];cargo=program['cargo']
    return dict(status='COHERENT' if any(p['consistent'] for p in paths) else 'CONTRADICTED',cargo=cargo,hazards=hazards,references=refs,paths=paths)
def base_roles(candidates):
    return {w:candidates[0]['values'][w] for w in candidates[0]['values'] if len({c['values'][w] for c in candidates})==1}
