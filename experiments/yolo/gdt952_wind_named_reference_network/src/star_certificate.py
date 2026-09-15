"""Necessary six-body/three-center source consequence, independently enumerated."""
from itertools import combinations
from pathlib import Path
import json

E=Path(__file__).resolve().parents[1]

def certificate(adj):
    n=len(adj);rows=[]
    for centers in combinations(range(n),3):
        slots=[c for c in centers for _ in range(2)];owners={}
        def augment(slot,seen):
            for body in range(n):
                if body in centers or body in seen or not adj[body][slots[slot]]:continue
                seen.add(body)
                if body not in owners or augment(owners[body],seen):
                    owners[body]=slot;return True
            return False
        matched=sum(augment(s,set()) for s in range(6))
        rows.append({'center_sectors_1based':[c+1 for c in centers],'maximum_distinct_body_obligations':matched})
    return {'required':6,'actual_maximum':max(r['maximum_distinct_body_obligations'] for r in rows),
            'all_220_center_sets':rows}

if __name__=='__main__':
    data=json.loads((E/'artifacts/corrected/GRAPHS.json').read_text())
    out={g['model']:certificate(g['adjacency']) for g in data['graphs'] if g['edition']=='IT2a' and g['bound']=='upper'}
    (E/'artifacts/corrected/IT_CONTRADICTION_CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:(v['actual_maximum'],v['required']) for k,v in out.items()}))
