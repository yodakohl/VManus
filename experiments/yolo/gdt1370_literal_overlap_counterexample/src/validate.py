"""Independent two-record factorization by all complete cuts, not length scan."""
from pathlib import Path
from itertools import product
import gzip,json,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
PACKET=ROOT/'experiments/yolo/gdt1368_fragment_window_nucleus_capacity/artifacts/WINDOWS.json.gz'

def factors(left,right,reverse=False):
    u=left[::-1] if reverse else left;v=right[::-1] if reverse else right
    solutions={}
    for cut_u in range(1,len(u)):
        a,b=u[:cut_u],u[cut_u:]
        for cut_v in range(1,len(v)):
            bb,c=v[:cut_v],v[cut_v:]
            if b==bb:
                assert a and b and c
                assert a+b==u and b+c==v
                piece=b[::-1] if reverse else b
                solutions[len(b)]=piece
    return [{'length':n,'piece':solutions[n]} for n in sorted(solutions)]

def controls():
    words=[''.join(p) for n in range(1,5) for p in product('ab',repeat=n)];count=0
    for u in words:
        for v in words:
            direct=[{'length':n,'piece':u[-n:]} for n in range(1,min(len(u),len(v))) if u[-n:]==v[:n]]
            backwards=[{'length':n,'piece':u[:n]} for n in range(1,min(len(u),len(v))) if u[:n]==v[-n:]]
            assert factors(u,v)==direct and factors(u,v,True)==backwards
            count+=1
    assert factors('a','a')==[]
    assert factors('abc','bcd')==[{'length':2,'piece':'bc'}]
    assert factors('abc','def')==[]
    return {'binary_pair_cases':count,'both_global_orientations':True,'singletons_cannot_have_two_nonempty_pieces':True,'variable_overlap_length':True}

def compute():
    packet=json.loads(gzip.decompress(PACKET.read_bytes()))
    spec=json.loads((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/src/SPEC.json').read_text())
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    panels={}
    for reader in ('IT2a','RF1b','ZL3b'):
        found={};joint=False
        for window in packet.get(reader,[]):
            rows=window['sources']
            for row in rows:
                if row['page']=='f100r' and row['locus']=='f100r.14' and int(row['source_group_index']) in (5,6):
                    idx=int(row['source_group_index'])
                    if idx in found:assert found[idx]==row
                    else:found[idx]=row
            for a,b in zip(rows,rows[1:]):
                if a['page']==b['page']=='f100r' and a['locus']==b['locus']=='f100r.14' and [int(a['source_group_index']),int(b['source_group_index'])]==[5,6]:joint=True
        sources=[found[k] for k in sorted(found)]
        valid=joint and set(found)=={5,6}
        for r in sources:
            valid=valid and r['edition']==reader and r['page'] in allowed and r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
            valid=valid and r['id']==f"{reader}|f100r.14|G{int(r['source_group_index']):03d}"
            valid=valid and bool(r['ivtff_group_raw']) and all('a'<=c<='z' for c in r['ivtff_group_raw'])
        if not valid:
            panels[reader]={'status':'MISSING','sources':sources,'forward_overlaps':[],'reversed_record_overlaps':[]};continue
        u,v=(r['ivtff_group_raw'] for r in sources);forward=factors(u,v);reverse=factors(u,v,True)
        status='BOTH_ORIENTATIONS_EXCLUDED' if not forward and not reverse else ('PAIR_COMPATIBLE' if forward and reverse else 'ORIENTATION_SPECIFIC')
        panels[reader]={'status':status,'sources':sources,'forward_overlaps':forward,'reversed_record_overlaps':reverse}
    return panels

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    fixture=controls();expected=compute();result=json.loads((D/'artifacts/RESULT.json').read_text())
    assert result['status']=='LITERAL_OVERLAP_COUNTEREXAMPLE' and result['panels']==expected
    report={'status':'PASS','controls':fixture,'panels':len(expected),'independence':'Enumerate all nonemptyA/B and B/Cfactorizations independently; reversewholeobservedstrings and returnoverlapinobservedorientation. Sourcecopies,seams,IDsandoriginalwindowadjacencyverified. No primaryimports.','scope':'Retrospectivefixedpair, uniformliteralconcatenativeoverlaponly. No independentwordmeaning, physicalglyph or languageclaim; no arbitrarymixedorientation exclusion.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
