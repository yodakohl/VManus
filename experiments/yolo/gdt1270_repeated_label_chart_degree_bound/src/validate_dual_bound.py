import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def main():
    original=P/'artifacts/RESULT.json';d=json.loads((P/'artifacts/POSTRESULT_DUAL_BOUND.json').read_text())
    assert d['original_result_sha256']==hashlib.sha256(original.read_bytes()).hexdigest()
    old=json.loads(original.read_text());graphs=json.loads((ROOT/'experiments/yolo/gdt1263_ordered_symbol_class_capacity/artifacts/GRAPHS.json').read_text());assert len(d['panels'])==len(graphs)==9
    for graph,primary,after in zip(graphs,old['panels'],d['panels']):
        assert (graph['reader'],graph['panel'])==(after['reader'],after['panel'])==(primary['reader'],primary['panel'])
        outgoing={u:set() for u in graph['unit_counts']};incoming={u:set() for u in outgoing}
        for edge in graph['edges']:
            if edge['from']!=edge['to']:outgoing[edge['from']].add(edge['to']);incoming[edge['to']].add(edge['from'])
        total=0
        for row in after['units']:
            u=row['unit'];assert row['incoming_nonself']==sorted(incoming[u]) and row['outgoing_nonself']==sorted(outgoing[u])
            for name,degree in [('outgoing_bound',len(outgoing[u])),('incoming_bound',len(incoming[u]))]:
                count=1
                while 5*count<degree:count+=1
                assert row[name]==count
            assert row['combined_bound']==max(row['outgoing_bound'],row['incoming_bound']);total+=row['combined_bound']
        assert total==after['combined_necessary_bound'] and after['original_outgoing_bound']==primary['minimum_necessary_positions']
    out={'status':'PASS','source':'independent direct old-edge in/out sets; original registered output preserved','panels':9,'unit_maxima':198,'meaning':'post-result bound verification only, not chart existence'}
    (P/'artifacts/DUAL_BOUND_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
