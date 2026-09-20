"""Bounded wrappers; grammar and meaning implementations remain unchanged."""
import json,sys,time,resource,subprocess
from pathlib import Path
from common import *

def bounded(mode,payload):
    s,g=inputs();seconds=s['meaning_worker_seconds'] if mode=='meaning' else s['independent_worker_seconds'] if mode=='independent' else s['query_worker_seconds']
    started=time.monotonic()
    try:
        r=subprocess.run([sys.executable,str(Path(__file__).resolve()),mode],input=json.dumps(payload),text=True,capture_output=True,timeout=seconds)
        if r.returncode:return dict(status='UNKNOWN_WORKER_EXIT',exit_code=r.returncode,wall_seconds=time.monotonic()-started)
        out=json.loads(r.stdout);out['worker_wall_seconds']=time.monotonic()-started;return out
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_WALL_LIMIT',wall_seconds=time.monotonic()-started)
    except json.JSONDecodeError:return dict(status='UNKNOWN_WORKER_OUTPUT',wall_seconds=time.monotonic()-started)

def main():
    s,g=inputs();resource.setrlimit(resource.RLIMIT_AS,(s['worker_memory_bytes'],s['worker_memory_bytes']));j=json.load(sys.stdin);mode=sys.argv[1]
    try:
        if mode=='primary':
            import solver
            out=solver.solve(j['paragraphs'],j['lexicon'],g,timeout=s['query_milliseconds'],witness_limit=s['witness_limit'])
        elif mode=='independent':
            import independent
            out=independent.check(j['paragraphs'],j['lexicon'],g,timeout=s['independent_milliseconds'])
        else:
            from meaning import meanings
            assert mode=='meaning'
            out=dict(status='COMPLETE',variants=meanings(j['witness'],s,g,j.get('independent',False)))
        print(json.dumps(out))
    except MemoryError:print(json.dumps(dict(status='UNKNOWN_MEMORY_LIMIT')))
if __name__=='__main__':main()
