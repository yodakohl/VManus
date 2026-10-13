"""Independent rolling exact-form counts, fixed cohort and order-reference replay."""
from pathlib import Path
from collections import Counter,defaultdict,deque
import gzip,json,math,random,re,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'
EVENTS=ROOT/'experiments/yolo/gdt1316_fixed_half_form_prediction/artifacts/EVENTS.json.gz'
TOL=1e-10

def near(a,b):
    assert math.isfinite(a) and math.isfinite(b) and abs(a-b)<=TOL,(a,b)

class Rolling:
    def __init__(self):self.queue=deque();self.counts=defaultdict(Counter);self.sizes=Counter()
    def predict(self,word,p):
        n=len(word);size=self.sizes[n];hits=self.counts[n][word]
        q=p if not size else (7*p+hits/size)/8
        return size,hits,q,math.log(q/p)
    def add(self,word):
        self.queue.append(word);n=len(word);self.sizes[n]+=1;self.counts[n][word]+=1
        if len(self.queue)>4:
            old=self.queue.popleft();n=len(old);self.sizes[n]-=1;self.counts[n][old]-=1

def controls():
    r=Rolling();a=('a',);b=('b',)
    assert r.predict(a,.25)==(0,0,.25,0.0)
    for w in (a,b,a):r.add(w)
    qa=r.predict(a,.25)[2];qb=r.predict(b,.75)[2];near(qa+qb,1.0)
    assert r.predict(('a','b'),.5)[0]==0
    r=Rolling();r.add(('a','b'))
    for _ in range(4):r.add(a)
    assert r.predict(('a','b'),.5)[0]==0
    assert Rolling().predict(a,.5)[0]==0
    def gain(words):
        history=Rolling();values=[]
        for w in words:
            values.append(history.predict((w,),.5)[3]);history.add((w,))
        return math.fsum(values)
    assert gain('aabb')!=gain('abab')
    assert sum(math.log(.5) for w in 'aabb')==sum(math.log(.5) for w in 'abab')
    return {'normalized_fixed_mixture':True,'empty_and_gap_reset_fallback':True,'no_current_future_word':True,'all_four_groups_not_four_length_matches':True,'length_conditioning':True,'bag_preserved_base_changed_cache_gain':True}

def parse(raw,signs):
    paths={0:[()]}
    for i in range(len(raw)):
        for prefix in paths.get(i,[]):
            for sign in signs:
                if raw.startswith(sign,i):paths.setdefault(i+len(sign),[]).append(prefix+(sign,))
    assert len(paths.get(len(raw),[]))==1
    return paths[len(raw)][0]

def setup():
    events=json.loads(gzip.decompress(EVENTS.read_bytes()));byid={e['id']:e for e in events};assert len(byid)==len(events)
    packet=json.loads(gzip.decompress((OLD/'artifacts/GROUPS.json.gz').read_bytes()))
    spec=json.loads((OLD/'src/SPEC.json').read_text());signs=spec['signs'];allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    output={};covered=set()
    for ed,rows in packet.items():
        lines=defaultdict(dict);parsed={};seen=set()
        for r in rows:
            assert r['edition']==ed and r['page'] in allowed and r['kind']=='P'
            assert r['page'] not in ('f1r','f116v') and not r['page'].startswith('f84')
            assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE' and r['locus'].split('.')[0]==r['page']
            index=int(r['source_group_index']);identifier=f"{ed}|{r['locus']}|G{index:03d}";assert identifier==r['id'] and identifier not in seen;seen.add(identifier)
            raw=r['ivtff_group_raw'];assert raw and all('a'<=c<='z' for c in raw)
            if raw not in parsed:parsed[raw]=parse(raw,signs)
            assert list(parsed[raw])==r['units']
            match=re.fullmatch(r'f(\d+)[rv]\d*',r['page']);assert match;leaf=int(match.group(1))
            if leaf%2:continue
            event=byid.get(identifier)
            if len(r['units'])>=4:
                assert event is not None and event['reader']==ed and event['leaf']==leaf and event['units']==r['units'];covered.add(identifier)
            else:assert event is None
            line=lines[r['page'],r['locus']];assert index not in line
            line[index]={'id':identifier,'leaf':leaf,'word':tuple(r['units']),'p':None if event is None else event['mix_h'],'c':None if event is None else event['c']}
        runs=[]
        for key in sorted(lines):
            current=[];previous=None
            for i,row in sorted(lines[key].items()):
                if previous is not None and i!=previous+1:runs.append(current);current=[]
                current.append(row);previous=i
            if current:runs.append(current)
        pools=[]
        for ri,run in enumerate(runs):
            assert len({r['c'] for r in run if r['p'] is not None})<=1
            grouped=defaultdict(list)
            for i,row in enumerate(run):
                if row['p'] is not None:grouped[len(row['word'])].append(i)
            for n,positions in sorted(grouped.items()):pools.append((ri,n,positions))
        output[ed]=(runs,pools)
    assert covered==set(byid)
    return events,output

def evaluate(ed,runs,assignments=None,keep=False):
    leaf=defaultdict(list);records={};base_logs=[];available=0;cacheleaves=set()
    for ri,run in enumerate(runs):
        history=Rolling()
        for i,target in enumerate(run):
            origin=run[assignments[ri][i]] if assignments is not None else target
            word=origin['word'];p=origin['p']
            assert len(word)==len(target['word']) and (p is None)==(target['p'] is None)
            if p is not None:
                assert p>0 and origin['c']==target['c']
                size,hits,q,gain=history.predict(word,p);leaf[target['leaf']].append(gain);base_logs.append(math.log(p))
                if size:available+=1;cacheleaves.add(target['leaf'])
                if keep:records[target['id']]={'id':target['id'],'reader':ed,'leaf':target['leaf'],'cache_size':size,'cache_hits':hits,'base_probability':p,'new_probability':q,'gain':gain}
            history.add(word)
    per={str(k):{'words':len(values),'gain':math.fsum(values)/len(values)} for k,values in sorted(leaf.items())}
    info={'words':sum(v['words'] for v in per.values()),'leaves':len(per),'cache_available':available,'cache_leaves':len(cacheleaves),'positive_leaves':sum(v['gain']>0 for v in per.values()),'equal_leaf_gain':math.fsum(v['gain'] for v in per.values())/len(per),'token_gain':math.fsum(g for values in leaf.values() for g in values)/sum(map(len,leaf.values())),'per_leaf':per}
    return info,records,math.fsum(base_logs)

def recursive_compare(a,b,path=''):
    if isinstance(b,dict):
        assert set(a)==set(b),(path,set(a),set(b))
        for k,v in b.items():recursive_compare(a[k],v,path+'/'+str(k))
    elif isinstance(b,list):
        assert len(a)==len(b),(path,len(a),len(b))
        for i,(x,y) in enumerate(zip(a,b)):recursive_compare(x,y,path+'/'+str(i))
    elif isinstance(b,float):near(a,b)
    else:assert a==b,(path,a,b)

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    fixture=controls();events,inputs=setup();records={};expected={}
    for ed,(runs,pools) in inputs.items():
        observed,scores,baseline=evaluate(ed,runs,keep=True);records.update(scores);null=[]
        capacity=observed['cache_available']>=100 and observed['cache_leaves']>=10
        if capacity:
            rng=random.Random(1373)
            for rep in range(199):
                assignment=[list(range(len(run))) for run in runs]
                for ri,n,positions in pools:
                    perm=positions.copy();rng.shuffle(perm)
                    for dest,source in zip(positions,perm):assignment[ri][dest]=source
                value,_,logsum=evaluate(ed,runs,assignment);near(logsum,baseline)
                assert value['words']==observed['words'] and value['leaves']==observed['leaves']
                null.append(value['equal_leaf_gain'])
        expected[ed]={**observed,'null_scores':null}
    result=json.loads((D/'artifacts/RESULT.json').read_text());assert result['status']=='FROZEN_WHOLE_CACHE_ORDER_INCREMENT'
    assert set(result['readers'])==set(expected);tie_notes=[]
    for ed,want in expected.items():
        actual=result['readers'][ed]
        for field,value in want.items():recursive_compare(actual[field],value,ed+'/'+field)
        capacity=actual['cache_available']>=100 and actual['cache_leaves']>=10
        null=actual['null_scores'];p=None
        if not capacity:status='NO_CAPACITY'
        elif max(null)-min(null)<=1e-12:status='NO_SCORE_MOBILITY'
        else:
            p=(1+sum(v>=actual['equal_leaf_gain'] for v in null))/200
            material=actual['equal_leaf_gain']>=.01 and actual['positive_leaves']*3>=2*actual['leaves']
            status='NO_RETAINED_CACHE_GAIN' if not material else ('ORDER_SENSITIVE_PREDICTIVE_INCREMENT' if p<=.05/3 else 'GAIN_WITHOUT_DEMONSTRATED_ORDER_EXCESS')
            close=[i for i,v in enumerate(null) if abs(v-actual['equal_leaf_gain'])<=TOL]
            if close:tie_notes.append({'reader':ed,'null_indices_within_tolerance':close})
        assert actual['status']==status
        if p is None:assert actual['p_or_null'] is None
        else:near(actual['p_or_null'],p)
    saved=json.loads(gzip.decompress((D/'artifacts/SCORES.json.gz').read_bytes()));recursive_compare(saved,[records[e['id']] for e in events])
    receipt={'status':'PASS','controls':fixture,'events':len(events),'reader_cases':len(expected),'null_draws':sum(len(r['null_scores']) for r in expected.values()),'floating_tie_review':tie_notes,'independence':'Rolling deque/frequencycounters distinct from primarylist-horizon implementation. Sourcecohort/units/gaps preserved; same declared PRNG/seed reused, everycache recomputed. Savedpvalues checked from savedindependentlymatched scores to avoid floatingtie asymmetry.','scope':'Fixedpredictivecomparison/conditionalbagreference only; no historicalcopying,memory,language or meaning. Alloldheldevents and leafdenominators retained.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
