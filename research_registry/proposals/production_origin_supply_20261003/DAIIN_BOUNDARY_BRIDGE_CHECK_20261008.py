"""Check five old boundary examples, not a new fusion or meaning experiment."""
import csv,json,hashlib
from pathlib import Path
B=Path('research_registry/proposals/production_origin_supply_20261003')
p=B/'DAIIN_BOUNDARY_BRIDGES_20261008.tsv'
rows=list(csv.DictReader(p.open(),delimiter='\t')); cases=[]
assert len(rows)==149
for reader in ['ZL3b','IT2a','RF1b']:
    def line(locus):
        return sorted([r for r in rows if r['edition']==reader and r['locus']==locus],key=lambda r:int(r['source_group_index']))
    for locus in ['f49r.6','f100r.22']:
        rs=line(locus);words=[r['ivtff_group_raw'] for r in rs]
        if reader=='IT2a':
            inds=[i for i in range(len(words)-1) if words[i:i+2]==['chol','daiin']];assert len(inds)==1
            i=inds[0];assert rs[i]['right_separator']==rs[i+1]['left_separator']=='DEFINITE_SPACE'
            span=rs[i:i+2]
        else:
            span=[r for r in rs if r['ivtff_group_raw']=='choldaiin'];assert len(span)==1
        cases.append({'reader':reader,'locus':locus,'raw_span':span,'concatenation':'choldaiin'})
        assert ''.join(r['ivtff_group_raw'] for r in span)=='choldaiin'
    rs=line('f105r.24');ws=[r['ivtff_group_raw'] for r in rs]
    inds=[i for i in range(len(ws)-2) if ws[i:i+3]==['pcheey','dal','daiin']];assert len(inds)==1
    i=inds[0];span=rs[i:i+3]
    assert all(span[j]['right_separator']==span[j+1]['left_separator']=='DEFINITE_SPACE' for j in [0,1])
    cases.append({'reader':reader,'locus':'f105r.24','raw_span':span,'concatenation':'pcheeydaldaiin'})
    a=line('f103v.1')[-1];b=line('f103v.2')[0]
    assert [a['ivtff_group_raw'],b['ivtff_group_raw']]==['dal','daiin']
    assert a['right_separator']=='LINE_END' and b['left_separator']=='LINE_START'
    cases.append({'reader':reader,'locus':'f103v.1–2','raw_span':[a,b],'concatenation':'daldaiin'})
inputs=[p,Path(__file__),B/'DAIIN_FAMILY_PROFILES_20261008.json']
result={'status':'OLD_BOUNDARY_EXAMPLES_RAW_VERIFIED','cases':cases,'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'claim_ceiling':'Old observations reconnected, not discovery. No same-meaning claim, universal word boundary, physical-image inspection, numeral, stem identity, grammar or independent reader replication.'}
(B/'DAIIN_BOUNDARY_BRIDGE_RESULT_20261008.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'cases':len(cases),'physical_scope':'five old loci, three alternative readings'}))
