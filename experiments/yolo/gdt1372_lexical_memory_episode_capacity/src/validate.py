"""Independent original-token transducer and binary-run extrema capacity check."""
from pathlib import Path
from itertools import combinations,product
from collections import defaultdict
from functools import lru_cache
import gzip,json,re,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
RUNFILE=ROOT/'experiments/yolo/gdt1369_open_edge_fragment_partition/artifacts/RUNS.json.gz'
WINFILE=ROOT/'experiments/yolo/gdt1368_fragment_window_nucleus_capacity/artifacts/WINDOWS.json.gz'
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'

def transduce(units,a,b,c):
    source=[];events=[];i=0
    while i<len(units):
        if units[i]==c:
            events.append((len(source),1));source.extend((a,b));i+=1
        elif i+1<len(units) and units[i]==a and units[i+1]==b:
            events.append((len(source),0));source.extend((a,b));i+=2
        else:source.append(units[i]);i+=1
    return tuple(source),events

@lru_cache(None)
def extrema(n,ones,first,last):
    zeros=n-ones
    if first!=last:return 1,2*min(zeros,ones)-1
    other=zeros if first else ones
    same=ones if first else zeros
    if other==0:return 0,0
    return 2,2*min(other,same-1)

def controls():
    histories=0
    for n in range(2,11):
        for h in product((0,1),repeat=n):
            interior_ones=sum(h)-h[0]-h[-1];scores=[]
            for chosen in combinations(range(1,n-1),interior_ones):
                path=[h[0]]+[0]*(n-2)+[h[-1]]
                for i in chosen:path[i]=1
                scores.append(sum(a!=b for a,b in zip(path,path[1:])))
            bounds=extrema(n,sum(h),h[0],h[-1]);assert bounds==(min(scores),max(scores))
            if n<=3:assert bounds[0]==bounds[1]
            histories+=1
    assert extrema(4,2,0,1)==(1,3)
    assert extrema(4,1,0,0)==(2,2)
    source,events=transduce(('ckh','cth','ch','k','ckh'),'ch','k','ckh')
    assert source==('ch','k','cth','ch','k','ch','k') and events==[(0,1),(3,0),(5,1)]
    words=0
    for n in range(6):
        for output in product(('a','b','c','d'),repeat=n):
            source,events=transduce(output,'a','b','c');choice=dict(events);rebuilt=[];i=0
            while i<len(source):
                if i in choice:
                    assert source[i:i+2]==('a','b')
                    rebuilt.extend(('c',) if choice[i] else ('a','b'));i+=2
                else:rebuilt.append(source[i]);i+=1
            assert tuple(rebuilt)==output
            assert [pos for pos,y in events]==[j for j in range(len(source)-1) if source[j:j+2]==('a','b')]
            words+=1
    return {'binary_histories_lengths_2_to_10':histories,'closed_form_extrema_vs_all_interior_permutations':'PASS','transducer_inverse_words':words,'multiple_sites_and_other_complex_literal':True,'n2_n3_immobile':True}

def parse(raw,signs):
    paths={0:[()]}
    for i in range(len(raw)):
        for prefix in paths.get(i,[]):
            for sign in signs:
                if raw.startswith(sign,i):paths.setdefault(i+len(sign),[]).append(prefix+(sign,))
    assert len(paths.get(len(raw),[]))==1
    return paths[len(raw)][0]

def checked_runs():
    runs=json.loads(gzip.decompress(RUNFILE.read_bytes()));windows=json.loads(gzip.decompress(WINFILE.read_bytes()))
    spec=json.loads((OLD/'src/SPEC.json').read_text());signs=spec['signs'];allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    for ed,rr in runs.items():
        seen=set();parsed={};rebuilt=[];keys=[]
        for run in rr:
            rows=run['sources'];assert len(rows)>=3
            assert len({(r['page'],r['locus']) for r in rows})==1
            indices=[int(r['source_group_index']) for r in rows];assert indices==list(range(indices[0],indices[0]+len(rows)))
            keys.append((rows[0]['page'],rows[0]['locus'],indices[0]))
            for r in rows:
                assert r['edition']==ed and r['page'] in allowed and r['kind']=='P'
                assert not r['page'].startswith('f84') and r['page'] not in ('f116v','f1r')
                assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE' and r['locus'].split('.')[0]==r['page']
                identifier=f"{ed}|{r['locus']}|G{int(r['source_group_index']):03d}";assert r['id']==identifier and identifier not in seen;seen.add(identifier)
                raw=r['ivtff_group_raw'];assert raw and all('a'<=ch<='z' for ch in raw)
                if raw not in parsed:parsed[raw]=parse(raw,signs)
                assert list(parsed[raw])==r['units']
            for i in range(len(rows)-2):
                src=rows[i:i+3];rebuilt.append({'sources':src,'support':sorted(set(''.join(r['ivtff_group_raw'] for r in src)))})
        assert keys==sorted(keys) and rebuilt==windows[ed]
    return runs

def compute():
    runs=checked_runs();cases={};episodes={}
    for reader,rr in runs.items():
        for order in ('BH','HB'):
            for height in ('k','t','p','f'):
                name=reader+'_'+order+'_'+height;a,b=('ch',height) if order=='BH' else (height,'ch');c='c'+height+'h'
                saved=[];opportunities=0;keys=0;singles=0;mobileleaves=set()
                for run_index,run in enumerate(rr):
                    histories=defaultdict(list)
                    for row in run['sources']:
                        source,events=transduce(tuple(row['units']),a,b,c)
                        for pos,y in events:
                            histories[source,pos].append({'id':row['id'],'index':int(row['source_group_index']),'y':y});opportunities+=1
                    keys+=len(histories)
                    for (source,position),visits in sorted(histories.items()):
                        assert visits==sorted(visits,key=lambda v:v['index'])
                        if len(visits)<2:singles+=1;continue
                        low,high=extrema(len(visits),sum(v['y'] for v in visits),visits[0]['y'],visits[-1]['y']);assert low<=high
                        remote=sum(v['index']-u['index']>1 for u,v in zip(visits,visits[1:]))
                        first=run['sources'][0];mobile=high>low
                        if mobile:mobileleaves.add(int(re.match(r'f(\d+)',first['page']).group(1)))
                        saved.append({'run_index':run_index,'page':first['page'],'locus':first['locus'],'source':list(source),'position':position,'visits':visits,'min_switches':low,'max_switches':high,'mobile':mobile,'remote_transitions':remote})
                mob=[e for e in saved if e['mobile']];remote=sum(e['remote_transitions'] for e in mob)
                cases[name]={'runs':len(rr),'opportunities':opportunities,'keys':keys,'singleton_keys':singles,'episodes':len(saved),'visits':sum(len(e['visits']) for e in saved),'mobile_episodes':len(mob),'mobile_visits':sum(len(e['visits']) for e in mob),'mobile_remote_transitions':remote,'mobile_leaves':len(mobileleaves),'status':'CAPACITY_READY' if remote>=100 and len(mobileleaves)>=10 else 'NO_CAPACITY'};episodes[name]=saved
                assert opportunities==singles+cases[name]['visits'] and keys==singles+len(saved)
    return cases,episodes

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    fixture=controls();expected,episodes=compute();result=json.loads((D/'artifacts/RESULT.json').read_text())
    assert result['status']=='LEXICAL_MEMORY_EPISODE_CAPACITY' and result['cases']==expected
    assert json.loads(gzip.decompress((D/'artifacts/EPISODES.json.gz').read_bytes()))==episodes
    report={'status':'PASS','controls':fixture,'cases':len(expected),'independence':'Direct original-token C/pair transducer; closed-form binary-run extrema, independently checked by all interior permutations. Allsourcewindowreplay,episodekeys/visits/bounds/remote counts andgates compared. No primaryimports orobservedswitchscore.','scope':'Capacityonly; assumptionsaboutsinglefusion,monotonewritingorder,rendering-independentadmission andphysicaldriftrival remain. No memory/phonetic/meaningconfirmation.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
