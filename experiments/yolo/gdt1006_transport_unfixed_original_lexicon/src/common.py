import hashlib,importlib.util,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(path,name):
    ms=importlib.util.spec_from_file_location(name,R/path);m=importlib.util.module_from_spec(ms);ms.loader.exec_module(m);return m
def checklock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p

def evaluate(parsed,g,s,independent=False,keep_full=False):
    model=load(s['model'],'model993') if not independent else None
    bit=load(s['independent_replay'],'bit1006') if independent else None
    binding=load(s['binding_checker'],'binding994') if independent else None
    variants=[dict(zip(g['variants'],v)) for v in itertools.product(*g['variants'].values())]
    summaries=[];full=[];coherent=[]
    for vi,v in enumerate(variants):
        if independent:
            error=binding.binding_error(parsed,v)
            if error:detail=dict(status='BINDING_CONTRADICTION',error=error,paths=[])
            else:
                paths,hazards,refs=bit.replay(parsed,v);cargo=sorted({x for p in parsed for x in p['symbols'] if x in ('W','G','C')})
                for path in paths:
                    for state in [path,*path['trace']]:state['positions']={k:a for k,a in state['positions'].items() if k in set(cargo)|{'M','B'}}
                detail=dict(cargo=cargo,hazards=hazards,references=refs,paths=paths)
        else:
            try:
                program=model.compile_reading(parsed,v);detail=dict(cargo=program['cargo'],hazards=program['hazards'],references=program['references'],paths=model.execute(program,v))
            except ValueError as error:detail=dict(status='BINDING_CONTRADICTION',error=str(error),paths=[])
        if 'status' not in detail:
            req=s['source_world_requirements'];content=len(detail['cargo'])==req['named_cargos'] and len(detail['hazards'])==req['distinct_hazard_pairs']
            okay=[p for p in detail['paths'] if p['consistent'] and len(p['trace'])-1==req['complete_voyages']]
            detail['status']='SOURCE_CONTENT_MISMATCH' if not content else 'COHERENT' if okay else 'CONTRADICTED'
        summary=dict(variant_index=vi,variant=v,status=detail['status'],detail_sha256=digest(detail))
        if 'error' in detail:summary['error']=detail['error']
        else:
            summary.update(named_cargos=detail['cargo'],hazards=detail['hazards'],paths=len(detail['paths']),physical_complete=sum(p['physical_complete'] for p in detail['paths']),consistent_paths=sum(p['consistent'] for p in detail['paths']),first_failures=[p['physical_failure'] for p in detail['paths'] if p['physical_failure']],assertion_failures=[p['assertions'] for p in detail['paths'] if p['assertions']],safety_violations=sum(len(p['safety_violations']) for p in detail['paths']))
        summaries.append(summary)
        if detail['status']=='COHERENT':coherent.append(vi)
        if keep_full:full.append(dict(variant_index=vi,variant=v,**detail))
    return dict(coherent_variants=coherent,replays=summaries,full=full)
