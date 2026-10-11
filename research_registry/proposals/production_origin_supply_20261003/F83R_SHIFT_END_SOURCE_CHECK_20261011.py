from pathlib import Path
import gzip,hashlib,json
P=Path(__file__).resolve().parent;R=P.parents[2]
def main():
    a=json.loads((P/'F83R_SHIFT_END_ADOPTION_AUDIT_20261011.json').read_text())
    review=json.loads((P/'SOURCE_WRITER_ADOPTION_REVIEW_20261011.json').read_text())
    for name,expected in review['primary_hashes'].items():
        assert hashlib.sha256((R/name).read_bytes()).hexdigest()==expected,name
    source=R/a['source']['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==a['source']['sha256']
    rows=json.loads(gzip.decompress(source.read_bytes()))['rows']
    endings=['f83r.8','f83r.17','f83r.24','f83r.30','f83r.44','f83r.49','f83r.55']
    expected=[]
    for ed in ['ZL3b','IT2a','RF1b']:
        for locus in endings:
            line=[x for x in rows if x['edition']==ed and x['locus']==locus]
            assert line
            last=max(line,key=lambda x:int(x['source_group_index']))
            assert last['source_group_index']==last['source_group_count']
            expected.append(last)
    key=lambda x:(x['edition'],x['locus'])
    assert sorted(expected,key=key)==sorted(a['exact_cached_rows'],key=key)
    by={key(x):x for x in expected}
    for ed in ['ZL3b','IT2a']:
        x,y=by[ed,'f83r.8'],by[ed,'f83r.55']
        assert x['paragraph_end']==y['paragraph_end']=='1'
        assert x['right_separator']==y['right_separator']=='LINE_END'
        assert x['ivtff_group_raw']=='chary'
        assert y['ivtff_group_raw']==('cthal' if ed=='ZL3b' else 'cthol')
        assert x['ivtff_group_raw'][-1]!=y['ivtff_group_raw'][-1]
    assert by['ZL3b','f83r.30']['paragraph_end']=='1'
    assert by['IT2a','f83r.30']['paragraph_end']=='0'
    assert all(x['paragraph_end']=='0' for x in expected if x['edition']=='RF1b')
    result={'status':'PASS','endpoint_rows':len(expected),'eligible_counterpair_readings':['ZL3b','IT2a'],'RF1b':'UNSCORED','meaning':'Source/hash/endpoint fidelity only; proof conditional on the new adoption premises; no meanings or original-source-model rescore.'}
    (P/'F83R_SHIFT_END_SOURCE_VALIDATION_20261011.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
