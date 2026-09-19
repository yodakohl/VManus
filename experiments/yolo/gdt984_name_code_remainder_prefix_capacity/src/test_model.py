"""Source-only exhaustive short strings; no manuscript inputs."""
import itertools,json
from pathlib import Path
from model import segment
from check_model import decide,ground

def brute(atoms,text,codes):
    reach={0}
    for a in atoms:
        new=set()
        for b in reach:
            for end in range(b+1,len(text)+1):
                v=text[b:end]
                valid=v==codes[a] if a in codes else all(not v.startswith(c) and not c.startswith(v) for c in codes.values())
                if valid:new.add(end)
        reach=new
    return len(text) in reach

def main():
    count=0;positive=0
    assignments=[{'A':'a','B':'b'},{'A':'a','B':'bb'},{'A':'ab','B':'aa'},{'A':'ab','B':'ba'},{'A':'aa','B':'bba'}]
    patterns=[list(p) for n in range(1,4) for p in itertools.product('ABX',repeat=n)]
    strings=[''.join(t) for n in range(7) for t in itertools.product('ab',repeat=n)]
    for codes in assignments:
        for p in patterns:
            for t in strings:
                expected=brute(p,t,codes);x=segment(p,t,codes,witness=True);y=decide(p,t,codes)
                assert (x['status']=='PARTIAL_PREFIX_PARTITION')==y[0]==expected,(p,t,codes,x,y,expected)
                if expected:
                    ground(p,t,codes,x['boundaries']);z=decide(p,t,codes,bounds=True);ground(p,t,codes,z[3]);positive+=1
                else:assert (x['failed_atom'],x['reason'])==y[1:]
                count+=1
    result=dict(status='PASS',exhaustive_fixture_cases=count,positive_cases=positive,negative_cases=count-positive,manuscript_data=False)
    p=Path(__file__).resolve().parents[1]/'artifacts/PRE_RUN_TESTS.json';p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
