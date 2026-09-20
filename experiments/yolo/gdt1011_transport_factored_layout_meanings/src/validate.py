from common import *
from evaluate import evaluate
from worker import bounded
import collections,concurrent.futures,csv,itertools,math

def original_check(row):
    candidate={k:row[k] for k in ['id','layout','code','parse','bijective']}
    independent=evaluate(candidate,True);assert independent==row,row['id']
    return row['id']

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
        other_meaning=bounded('meaning',dict(witness=dict(aliases=code,parses=witness['parses']),independent=True));primary=witness['meaning_check']
        if primary['status']==other_meaning['status']=='COMPLETE':
            assert primary['variants']==other_meaning['variants']
            assert all(v['variant_index'] in original['valid_variants'] for v in primary['variants'] if v['status']=='COHERENT_COMMON_READING')
        semantic.append(dict(primary=primary['status'],independent=other_meaning['status']))
    return dict(id=row['id'],primary=row['status'],independent=other['status'],semantic=semantic)

def main():
    checklock();s,g=inputs();coverage=read(A/'COVERAGE.json');assert coverage['complete'] and coverage['primary']['status']=='UNSAT' and coverage['independent']['status']=='unsat'
    panel=read(A/'PANEL.json');originals=read(A/'ORIGINAL_ROWS.json');layouts=read(A/'LAYOUTS.json');rows=read(A/'ROWS.json');result=read(A/'RESULT.json')
    assert panel[0]==read(R/s['source_previous_panel'])[0]
    keep=[r['paragraph_ids'][1] for r in read(R/s['source_long_rows']) if r['status']=='SAT'];assert keep==[p['id'] for p in panel[1:]]
    prior_panel=read(R/s['source_long_panel'])
    for p in panel[1:]:assert p==next(q for q in prior_panel if q['id']==p['id'])
    alphabet={v for pat in g['patterns'].values() for t in pat for v in (g['types'][t[1:]] if t.startswith('@') else [t])};raw=panel[0]['words'];seen=[]
    for layout in layouts:
        cursor=0;domains={w:set(alphabet) for w in raw};kinds=[]
        for c in layout['layout']:
            pat=g['patterns'][c['kind']];assert c['start']==cursor and c['end']==cursor+len(pat);cursor=c['end'];kinds.append(c['kind'])
            for w,t in zip(raw[c['start']:c['end']],pat):domains[w]&=set(g['types'][t[1:]]) if t.startswith('@') else {t}
        assert cursor==63 and kinds[0]=='INITIAL' and kinds[-1]=='CONCLUSION'
        for k in g['patterns']:assert kinds.count(k)==1+int(k=='THEN')
        assert {w:sorted(v) for w,v in domains.items()}==layout['domains'] and math.prod(map(len,domains.values()))==225
        local=[r for r in originals if r['layout']==layout['id']];assert len(local)==225
        names=sorted(domains);expected={tuple(values) for values in itertools.product(*(sorted(domains[w]) for w in names))}
        observed=set()
        for row in local:
            assert set(row['code'])==set(names);observed.add(tuple(row['code'][w] for w in names))
            assert row['bijective']==(len(set(row['code'].values()))==47)
            assert [{k:c[k] for k in ['start','end','kind']} for c in row['parse']]==layout['layout']
            assert all(c['symbols']==[row['code'][w] for w in raw[c['start']:c['end']]] for c in row['parse'])
        assert observed==expected
    assert len(originals)==1800
    with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:checked=list(pool.map(original_check,originals,chunksize=10))
    valid={r['id']:r for r in originals if r['valid_variants']}
    assert {(r['original_id'],r['context_index']) for r in rows}==set(itertools.product(valid,range(1,5))) and len(rows)==len(valid)*4
    for r in rows:assert r['original_valid_variants']==valid[r['original_id']]['valid_variants'] and r['context']==panel[r['context_index']]['id']
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:checks=list(pool.map(extension_check,[(r,valid[r['original_id']]) for r in rows]))
    assert result['extension_counts']==dict(collections.Counter(r['status'] for r in rows))
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==1800
    for t,r in zip(table,originals):assert t['candidate']==r['id'] and t['valid_variants']==','.join(map(str,r['valid_variants']))
    with (A/'EXTENSIONS.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(rows)
    for t,r in zip(table,rows):assert t['candidate']==r['id'] and t['grammar']==r['status']
    out=dict(status='PASS',layout_domains_reconstructed=8,all_original_maps_checked=len(checked),all_original_settings_checked=57600,extension_checks=checks,independent_unknowns=sum(c['independent'] not in ('sat','unsat') for c in checks),unverified_negatives=sum(c['primary']=='UNSAT' and c['independent']!='unsat' for c in checks),meaning_unknowns=sum(x['primary']!='COMPLETE' or x['independent']!='COMPLETE' for c in checks for x in c['semantic']),confirmed_words=0,independent_meaning_capacity=0)
    put('VALIDATION.json',out);print(json.dumps({k:v for k,v in out.items() if k!='extension_checks'},indent=2))
if __name__=='__main__':main()
