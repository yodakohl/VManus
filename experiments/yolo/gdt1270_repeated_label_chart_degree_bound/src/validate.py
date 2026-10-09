import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];OLD=ROOT/'experiments/yolo/gdt1263_ordered_symbol_class_capacity'
def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for path,h in lock['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    manifest=json.loads((OLD/'experiment.json').read_text())
    for f in manifest['outputs']:
        if Path(f['path']).name in ['GRAPHS.json','VALIDATION.json']:
            assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
    graphs=json.loads((OLD/'artifacts/GRAPHS.json').read_text());out=json.loads((P/'artifacts/RESULT.json').read_text())
    assert out['status']=='NECESSARY_POSITION_BOUNDS_ONLY' and out['max_nonself_per_position']==5 and out['chart_constructed'] is False
    assert len(graphs)==len(out['panels'])==9
    checked=0
    for graph,report in zip(graphs,out['panels']):
        assert (report['reader'],report['panel'])==(graph['reader'],graph['panel'])
        alphabet=sorted(graph['unit_counts']);index={u:i for i,u in enumerate(alphabet)};matrix=[[0]*len(alphabet) for _ in alphabet];orig={}
        for e in graph['edges']:
            a,b=e['from'],e['to'];w=e['witness'];j=e['witness_offset']
            assert w['edition']==graph['reader'] and not w['page'].startswith('f84') and w['page']!='f116v'
            assert w['units'][j:j+2]==[a,b]
            if a!=b:matrix[index[a]][index[b]]=1;orig[(a,b)]=e
        assert report['active_units']==len(alphabet)==22
        expected=[]
        for u,row in zip(alphabet,matrix):
            degree=sum(row);positions=1
            while 5*positions<degree:positions+=1
            targets=[v for v,n in zip(alphabet,row) if n];ws=[]
            for v in targets:
                e=orig[(u,v)];w=e['witness'];ws.append(dict(to=v,id=w['id'],page=w['page'],units=w['units'],offset=e['witness_offset'],occurrences=e['occurrences'],whole_types=e['whole_types'],physical_leaves=e['physical_leaves']));checked+=1
            expected.append(dict(unit=u,nonself_successors=targets,degree=degree,minimum_positions=positions,witnesses=ws))
        assert expected==report['units']
        total=sum(x['minimum_positions'] for x in expected)
        assert report['minimum_necessary_positions']==total and report['one_position_per_label_excluded']==(total>22)
    result=dict(status='PASS',panels=9,unit_bounds=198,nonself_edge_witnesses_checked=checked,source='unchanged validated1263adjacency graphs',verification='separate adjacency matrices and repeated-subtraction capacity; direct witness check, no primary imports')
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
