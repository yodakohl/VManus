"""Validate exact correction scope and every exported cell/marginal."""
from pathlib import Path
import csv,json
E=Path(__file__).resolve().parents[1]
def read(p):
    with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
original=(E/'src/run.py').read_text()
expected=original.replace("=='.' for a,b in zip(gs,gs[1:])","=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:])")
expected=expected.replace("E/'artifacts/ALL_","E/'artifacts/corrected/ALL_")
for name in ['COMPLETE_RECORDS.tsv','CANDIDATE_TABLE.tsv','GRAPHS.json','RESULT.json']:
    expected=expected.replace("E/'artifacts/"+name+"'","E/'artifacts/corrected/"+name+"'")
expected=expected.replace('"""Complete label/body census; exact conditional named-reference consistency."""','"""Post-exposure separator-enum correction; original locked run and results preserved."""')
assert expected==(E/'src/run_corrected.py').read_text()
source=json.loads((E/'src/SOURCE.json').read_text());checks=[]
for folder in ['artifacts','artifacts/corrected']:
    out=E/folder;g=json.loads((out/'GRAPHS.json').read_text())
    gs={(r['edition'],r['model'],r['bound']):r for r in g['graphs']}
    rows=read(out/'ALL_TITLE_BODY_CONSEQUENCES.tsv');assert len(rows)==864
    assert len({(r['edition'],r['model'],r['body_sector'],r['title_sector']) for r in rows})==864
    for r in rows:
        a,b=int(r['body_sector'])-1,int(r['title_sector'])-1
        assert gs[(r['edition'],r['model'],'lower')]['adjacency'][a][b]==(r['status']=='PRESENT')
        assert gs[(r['edition'],r['model'],'upper')]['adjacency'][a][b]==(r['status']!='ABSENT')
    rs=read(out/'ALL_NAME_CANDIDATES.tsv');assert len(rs)==864
    assert len({(r['edition'],r['model'],r['name_hypothesis'],r['sector']) for r in rs})==864
    for r in rs:
        a,b=source['names'].index(r['name_hypothesis']),int(r['sector'])-1
        assert int(r['definite_assignments'])==gs[(r['edition'],r['model'],'lower')]['marginals'][a][b]
        assert int(r['possible_assignments_upper'])==gs[(r['edition'],r['model'],'upper')]['marginals'][a][b]
    checks.append({'folder':folder,'consequence_cells':len(rows),'candidate_cells':len(rs)})
report={'status':'PASS','correction_scope_exact':True,'export_checks':checks,'confirmed_meanings':0}
(E/'artifacts/EXPORT_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
