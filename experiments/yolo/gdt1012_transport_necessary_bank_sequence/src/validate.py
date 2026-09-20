from common import *
from worker import bounded
from preflight import ground
import collections,concurrent.futures,csv,itertools

def extension_check(args):
    row,original=args;s,g=inputs();p=read(A/'PANEL.json')[row['context_index']]
    other=bounded('independent',dict(paragraphs=[p],lexicon=original['code']))
    assert {row['status'].lower(),other['status']}!={'sat','unsat'}
    semantic=[]
    for witness in row['witnesses']:
        code=witness['aliases'];assert all(code[w]==v for w,v in original['code'].items())
        assert set(code)==set(original['code'])|set(p['words']) and witness['parses'][0]==original['parse']
        cursor=0;parsed=witness['parses'][1]
        for clause in parsed:
            pattern=g['patterns'][clause['kind']];assert clause['start']==cursor and clause['end']==cursor+len(pattern);cursor=clause['end']
            assert clause['symbols']==[code[w] for w in p['words'][clause['start']:clause['end']]]
            for t,value in zip(pattern,clause['symbols']):assert value in (g['types'][t[1:]] if t.startswith('@') else [t])
        assert cursor==len(p['words']) and parsed[0]['kind']=='INITIAL' and parsed[-1]['kind']=='CONCLUSION'
        for k in ['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION']:assert sum(c['kind']==k for c in parsed)==1
        bank=0
        for node in parsed:
            bank=ground(node['kind'],bank);assert bank is not None
        assert bank==1
        other_meaning=bounded('meaning',dict(witness=dict(aliases=code,parses=witness['parses']),independent=True));primary=witness['meaning_check']
        if primary['status']==other_meaning['status']=='COMPLETE':
            assert primary['variants']==other_meaning['variants']
            assert all(v['variant_index'] in original['valid_variants'] for v in primary['variants'] if v['status']=='COHERENT_COMMON_READING')
        semantic.append(dict(primary=primary['status'],independent=other_meaning['status']))
    return dict(id=row['id'],primary=row['status'],independent=other['status'],semantic=semantic)

def main():
    checklock();s,g=inputs();panel=read(A/'PANEL.json');assert panel==read(R/s['source_panel'])
    prior=read(R/s['source_original_rows']);expected=[{k:r[k] for k in ['id','code','parse','valid_variants']} for r in prior if r['valid_variants']]
    originals=read(A/'ORIGINAL_CANDIDATES.json');assert originals==expected and len(originals)==36
    originals={r['id']:r for r in originals};rows=read(A/'ROWS.json');pred=read(A/'PREDICTIONS.json');result=read(A/'RESULT.json')
    assert {(r['original_id'],r['context_index']) for r in rows}==set(itertools.product(originals,[2,4])) and len(rows)==72
    for p,r in zip(pred,rows):
        assert p['id']==r['id'] and p['context']==r['context'] and p['original_id']==r['original_id']
        assert r['original_valid_variants']==originals[r['original_id']]['valid_variants']
        context=panel[r['context_index']]
        assert p['shared_values']=={w:originals[r['original_id']]['code'][w] for w in sorted(set(context['words'])&originals[r['original_id']]['code'].keys())}
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:checks=list(pool.map(extension_check,[(r,originals[r['original_id']]) for r in rows]))
    assert result['counts']==dict(collections.Counter(r['status'] for r in rows))
    assert result['sampled_extension_maps']==sum(len(r['witnesses']) for r in rows)
    assert result['coherent_common_witness_settings']==sum(v['status']=='COHERENT_COMMON_READING' for r in rows for w in r['witnesses'] for v in w['meaning_check'].get('variants',[]))
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(rows)
    for t,r in zip(table,rows):assert t['candidate']==r['id'] and t['bank_grammar']==r['status']
    out=dict(status='PASS',cases=len(checks),checks=checks,independent_unknowns=sum(c['independent'] not in ('sat','unsat') for c in checks),unverified_negatives=sum(c['primary']=='UNSAT' and c['independent']!='unsat' for c in checks),meaning_unknowns=sum(x['primary']!='COMPLETE' or x['independent']!='COMPLETE' for c in checks for x in c['semantic']),confirmed_words=0,independent_meaning_capacity=0)
    put('VALIDATION.json',out);print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
