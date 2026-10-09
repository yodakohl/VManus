"""Explicit post-result incoming/outgoing consequence; primary result unchanged."""
import json,itertools,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def landings(w,p,k):
    seen=set();out=[]
    for distance in range(len(w)):
        j=(p+distance)%len(w)
        if w[j] not in seen:seen.add(w[j]);out.append(j)
        if len(out)==k:return out
    raise ValueError()
def controls():
    cases=0
    for n in range(3,7):
        for w in itertools.product('abc',repeat=n):
            if set(w)!=set('abc'):continue
            for width in [2,3]:
                incoming=[set() for _ in w]
                for p in range(n):
                    for q in landings(w,p,width):
                        if w[p]!=w[q]:incoming[q].add(w[p])
                assert all(len(labels)<=width-1 for labels in incoming);cases+=1
    return cases

def main():
    checked=controls();src=P/'artifacts/RESULT.json';original=json.loads(src.read_text());panels=[]
    for old in original['panels']:
        outgoing={u['unit']:set(u['nonself_successors']) for u in old['units']};incoming={u:set() for u in outgoing}
        for a,bs in outgoing.items():
            for b in bs:incoming[b].add(a)
        units=[]
        for u in sorted(outgoing):
            out=old['units'][list(outgoing).index(u)]['minimum_positions'];inc=max(1,(len(incoming[u])+4)//5)
            units.append(dict(unit=u,incoming_nonself=sorted(incoming[u]),outgoing_nonself=sorted(outgoing[u]),outgoing_bound=out,incoming_bound=inc,combined_bound=max(out,inc)))
        panels.append(dict(reader=old['reader'],panel=old['panel'],original_outgoing_bound=old['minimum_necessary_positions'],combined_necessary_bound=sum(u['combined_bound'] for u in units),units=units))
    r=dict(status='POST_RESULT_BIDIRECTIONAL_NECESSARY_BOUND',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_registered_result_unchanged=True,original_result_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),proof='For any landing position labeledh, all nonself predecessor labels lie among the last5distinct non-h labels before it; otherwise the source-to-destination arc contains at least6non-h labels and h cannot be in the first6distinct list. Earlier h occurrences only restrict selection further. Take max of incoming/outgoing costs perlabel, not sum, then sum acrosslabels.',review='bounded_idea_supply source-free messages after outgoing result; no result/data reading by reviewer',synthetic_incoming_position_checks=checked,panels=panels,scope='Later theorem/cost consequence, not a new preregistered endpoint or actual circular chart. Exact destination occurrence must be the first encountered label occurrence; arbitrary jumps among copies are excluded.')
    (P/'artifacts/POSTRESULT_DUAL_BOUND.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'status':r['status'],'panels':[{k:v for k,v in p.items() if k!='units'} for p in panels]}))
if __name__=='__main__':main()
