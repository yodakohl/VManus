import json,hashlib,itertools,datetime,sys
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
OLD=ROOT/'experiments/yolo/gdt1263_ordered_symbol_class_capacity'
def options(w,p,k,step=1):
    out=[]
    for i in range(len(w)):
        c=w[(p+step*i)%len(w)]
        if c not in out:out.append(c)
        if len(out)==k:return out
    raise ValueError('too few labels')
def controls():
    count=0
    for n in range(3,7):
        for w in itertools.product('abc',repeat=n):
            if set(w)!=set('abc'):continue
            for width in [2,3]:
                successors={g:set() for g in w}
                for i,g in enumerate(w):successors[g].update(set(options(w,i,width))-{g})
                assert all(len(v)<=(width-1)*w.count(g) for g,v in successors.items());count+=1
    w=tuple('abcdefaghijk');s=set(options(w,0,6))|set(options(w,6,6));assert len(s-{'a'})==10
    assert len(set(options(tuple('abcdefg'),0,6))|set(options(tuple('abcdefg'),0,4,-1)))-1==6
    return dict(status='PASS',circle_width_cases=count,tight_duplicate_label_nonself_degree=10,wrong_direction_union_nonself_degree=6)
def main():
    for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    graphs=json.loads((OLD/'artifacts/GRAPHS.json').read_text());rows=[]
    for graph in graphs:
        by={u:set() for u in graph['unit_counts']};witnesses={}
        for edge in graph['edges']:
            a,b=edge['from'],edge['to']
            if a==b:continue
            by[a].add(b);witnesses[(a,b)]=dict(id=edge['witness']['id'],page=edge['witness']['page'],units=edge['witness']['units'],offset=edge['witness_offset'],occurrences=edge['occurrences'],whole_types=edge['whole_types'],physical_leaves=edge['physical_leaves'])
        units=[]
        for u,targets in sorted(by.items()):
            d=len(targets);units.append(dict(unit=u,nonself_successors=sorted(targets),degree=d,minimum_positions=max(1,(d+4)//5),witnesses=[dict(to=v,**witnesses[(u,v)]) for v in sorted(targets)]))
        total=sum(u['minimum_positions'] for u in units)
        rows.append(dict(reader=graph['reader'],panel=graph['panel'],active_units=len(units),minimum_necessary_positions=total,one_position_per_label_excluded=total>len(units),units=units))
    result=dict(status='NECESSARY_POSITION_BOUNDS_ONLY',max_nonself_per_position=5,panels=rows,chart_constructed=False)
    (P/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (P/'artifacts/RUN_RECEIPT.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lock_sha256=hashlib.sha256((P/'src/REGISTRATION_LOCK.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],panels=[{k:v for k,v in r.items() if k!='units'} for r in rows]),indent=2))
if __name__=='__main__':
    if '--controls' in sys.argv:
        x=controls();(P/'artifacts/CONTROLS.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
    else:main()
