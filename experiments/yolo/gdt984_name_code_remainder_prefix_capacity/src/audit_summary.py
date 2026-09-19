"""Post-result descriptive audit; does not alter registered selection."""
import collections,csv,gzip,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(path):
    if str(path).endswith('.gz'):
        with gzip.open(path,'rt') as f:return json.load(f)
    return json.loads(Path(path).read_text())
s=read(E/'src/SPEC.json');rows=list(csv.DictReader((A/'CANDIDATE_TABLE.tsv').open(),delimiter='\t'));live=[r for r in rows if r['status']=='PARTIAL_PREFIX_COMPATIBLE']
names={}
for k in ['iris_code','xiphion_code']:
    before={r[k] for r in rows};after={r[k] for r in live};names[k]=dict(before=len(before),remaining=len(after),eliminated=sorted(before-after))
source=read(R/s['source']);domains=read(R/s['domains']);witnesses=read(A/'BOUNDARY_WITNESSES.json.gz');counts=collections.Counter()
for w in witnesses:
    code=collections.defaultdict(set)
    for record in source['records']:
        rid=record['id'];part=w['records'][rid];text=next(p['text'] for p in domains[w['edition']][rid] if p['page']==part['page']);bounds=part['boundaries']
        for i,a in enumerate(record['atoms']):code[a].add(text[bounds[i]:bounds[i+1]])
    counts['REPEATED_ATOM_HAS_DIFFERENT_VALUES' if any(len(v)>1 for v in code.values()) else 'SINGLE_VALUED_WITNESS']+=1
case=rows[65];assert case['iris_code']=='pch' and case['xiphion_code']=='o' and case['iris_page']=='f17v'
text=next(p['text'] for p in domains['IT2a']['I.1'] if p['page']=='f17v');assert text.startswith('pcho')
atoms=next(r['atoms'] for r in source['records'] if r['id']=='I.1');assert atoms[:2]==['IRIS','ILLYRIA']
assert not atoms[1] in ['IRIS','XIPHION']
out=dict(stage='POST_RESULT_DESCRIPTIVE_AUDIT_NO_RESELECTION',name_domains=names,boundary_witness_equality=dict(counts),example=dict(base_id=65,class_id=888,page='f17v',target_prefix=text[:18],source_atoms=atoms[:3],IRIS='pch',XIPHION='o',contradiction='After exact IRIS=pch the ILLYRIA code would start with complete XIPHION=o, violating prefix incomparability.'),claim_ceiling='These deterministic partition witnesses are not shared full codes; their equality failure does not disprove a different full witness.')
(A/'INTERPRETATION_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
