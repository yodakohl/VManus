from common import *
import itertools
def fixtures():
    s,g=inputs()
    def node(kind,**over):
        sy=[g['types'][x[1:]][0] if x.startswith('@') else x for x in g['patterns'][kind]]
        for k,v in over.items():sy[int(k)]=v
        return dict(kind=kind,symbols=sy)
    def n(kind,*pairs):return node(kind,**dict(pairs))
    headers=[n(k) for k in ('INITIAL','GOAL','SAFETY','CAPACITY')];end=n('CONCLUSION')
    ferry=lambda c:n('FERRY',('1',c));ex=lambda c:n('EXCLUDE',('1',c));ret=lambda c:n('WITH_RETURN',('1',c))
    pair=lambda a,b:n('PAIR',('0',a),('3',b))
    bodies=[
      ('ONE',[ferry('W')],'SUFFICIENT'),
      ('FORCED_EMPTY',[ferry('G'),ex('G'),ferry('W')],'SUFFICIENT'),
      ('SAFE_BAD_FINAL',[ferry('G'),ex('W'),ferry('W')],'INSUFFICIENT'),
      ('NO_AVAILABLE_DIRECTION',[ex('W'),ferry('W')],'INSUFFICIENT'),
      ('FIXED_MISSING_CARGO',[ferry('G'),ret('W'),ferry('W')],'INSUFFICIENT'),
      ('STAY_NO_LOAD',[n('STAY'),ferry('W')],'INSUFFICIENT'),
      ('FIXED_THREE',[ferry('G'),ex('G'),ferry('W'),ret('G'),ferry('C'),n('ALONE'),ferry('G')],None),
      ('FILTER_AND_LATER_FAIL',[ferry('G'),ex('G'),ferry('W'),ex('C'),ferry('C'),n('ALONE'),ferry('G')],None),
      ('FILTER_FORCES_GOOD',[ferry('G'),ex('G'),ferry('W'),ex('W'),ferry('C'),n('ALONE'),ferry('G')],None),
      ('STAY_THEN_CHOICE',[ferry('G'),n('STAY'),ex('W'),ferry('W')],None),
      ('AFTER_FINAL',[n('FINAL_TRIP',('4','W')),n('ALONE'),ferry('W')],'INSUFFICIENT'),
      ('RESULT_BAD',[ferry('W'),n('RESULT',('3','W'))],'INSUFFICIENT')]
    variants=[dict(zip(g['variants'],v)) for v in itertools.product(*g['variants'].values())]
    records=[]
    for label,body,expected in bodies:
        available=sorted({s for c in headers+body for s in c['symbols'] if s in ('W','G','C')})
        edges=list(itertools.combinations(available,2))
        for mask in range(1<<len(edges)):
            declarations=[pair(a,b) for i,(a,b) in enumerate(edges) if mask&(1<<i)]
            parsed=[];pos=0
            for c in headers+body+declarations+[end]:
                parsed.append(dict(c,start=pos,end=pos+len(c['symbols'])));pos+=len(c['symbols'])
            for vi,v in enumerate(variants):
                records.append(dict(id=f'{label}_H{mask}_V{vi}',parse=parsed,variant=v,expected=expected if mask==0 and vi==0 else None))
    return records
