"""Bounded whole-world queries and unchanged full-executor checks."""
from common import *
import subprocess,sys,resource

def bounded(mode,payload):
    s,g=inputs();seconds=s['meaning_worker_seconds'] if mode=='replay' else s['query_worker_seconds']
    started=time.monotonic()
    try:
        p=subprocess.run([sys.executable,str(E/'src/worker.py'),mode],input=json.dumps(payload),text=True,capture_output=True,timeout=seconds)
        if p.returncode:return dict(status='UNKNOWN_WORKER_EXIT',exit_code=p.returncode,wall_seconds=time.monotonic()-started)
        out=json.loads(p.stdout);out['wall_seconds']=time.monotonic()-started;return out
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_WALL_LIMIT',wall_seconds=time.monotonic()-started)
    except json.JSONDecodeError:return dict(status='UNKNOWN_WORKER_OUTPUT',wall_seconds=time.monotonic()-started)

def main():
    s,g=inputs();resource.setrlimit(resource.RLIMIT_AS,(s['worker_memory_bytes'],s['worker_memory_bytes']));mode=sys.argv[1];j=json.load(sys.stdin)
    try:
        if mode=='primary':
            import world
            out=world.solve(j['paragraph'],j['lexicon'],g,j['variant'],s['query_milliseconds'],j.get('fixed_layout'))
        elif mode=='independent':
            import independent
            out=independent.check(j['paragraph'],j['lexicon'],g,j['variant'],s['independent_milliseconds'],j.get('fixed_layout'))
        else:
            assert mode=='replay';out=dict(status='COMPLETE',result=replay(j['parse'],j['variant'],s,j.get('independent',False)))
        print(json.dumps(out))
    except MemoryError:print(json.dumps(dict(status='UNKNOWN_MEMORY_LIMIT')))
if __name__=='__main__':main()
