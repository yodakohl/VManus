"""Independent rational frozen probability reconstruction and log-chain check."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
from functools import lru_cache
import gzip,json,math,re,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
A=ROOT/'experiments/yolo/gdt1308_whole_form_prediction/artifacts'
B=ROOT/'experiments/yolo/gdt1316_fixed_half_form_prediction/artifacts'
TOL=1e-10

def near(a,b):
    assert math.isfinite(float(a)) and math.isfinite(float(b))
    assert abs(float(a)-float(b))<=TOL,(a,b)

def fixtures():
    # S={s}, U={u,v}; M shifts mass to S but improves u conditional on U.
    p={'s':F(1,2),'u':F(1,5),'v':F(3,10)}
    h={'s':F(9,10),'u':F(1,10),'v':F(0)}
    m={w:(p[w]+h[w])/2 for w in p}
    assert sum(p.values())==sum(m.values())==1
    raw=math.log(m['u']/p['u']);cat=math.log((m['u']+m['v'])/(p['u']+p['v']))
    conditional=math.log((m['u']/(m['u']+m['v']))/(p['u']/(p['u']+p['v'])))
    assert raw<0 and conditional>0;near(raw,cat+conditional)
    allcat=m['s']*math.log(m['s']/p['s'])+(m['u']+m['v'])*cat
    assert allcat>0 and cat<0
    return {'finite_seen_unseen_fixture':'PASS','negative_raw_U_positive_conditional_U':True,'negative_U_mass_not_negative_ALL_binary_score':True}

def reconstruct(model):
    whole={};seen=set();mcounts=defaultdict(Counter);left=defaultdict(Counter);right=defaultdict(Counter)
    for entry in model['whole']:
        cell=tuple(entry['cell']);counts={tuple(r['units']):r['count'] for r in entry['counts']}
        assert len(counts)==len(entry['counts']) and cell not in whole
        whole[cell]=counts
        for word,count in counts.items():
            assert len(word)==cell[1] and count>0;seen.add(word)
            cut=len(word)//2;left[cell][word[:cut]]+=count;right[(cell,word[cut-1])][word[cut:]]+=count
            for i,s in enumerate(word):mcounts[(cell[0],cell[1],i,'^' if i==0 else word[i-1])][s]+=count
    observed={tuple(e['context']):Counter(e['counts']) for e in model['m1']}
    assert observed==dict(mcounts)
    totals={cell:sum(counts.values()) for cell,counts in whole.items()}
    @lru_cache(None)
    def p(cell,word):
        value=F(1)
        for i,s in enumerate(word):
            counts=mcounts.get((cell[0],cell[1],i,'^' if i==0 else word[i-1]),{})
            value*=F(2*counts.get(s,0)+1,2*sum(counts.values())+22)
        return value
    @lru_cache(None)
    def h(cell,word):
        if cell not in totals:return F(0)
        cut=len(word)//2;lc=left[cell].get(word[:cut],0);rc=right[(cell,word[cut-1])]
        if not lc or not rc.get(word[cut:],0):return F(0)
        return F(lc,totals[cell])*F(rc[word[cut:]],sum(rc.values()))
    return whole,seen,totals,p,h

def aggregate(events):
    out={}
    for ed in ('IT2a','RF1b','ZL3b'):
        cohorts={}
        for name in ('ALL','GLOBAL_UNSEEN','GLOBAL_KNOWN'):
            selected=[e for e in events if e['reader']==ed and (name=='ALL' or e['unseen']==(name=='GLOBAL_UNSEEN'))]
            leaf=defaultdict(list)
            for e in selected:leaf[e['leaf']].append(e)
            per={}
            for k,rows in sorted(leaf.items()):
                per[str(k)]={'words':len(rows),**{term:math.fsum(r[term+'_gain'] for r in rows)/len(rows) for term in ('raw','category','conditional')}}
            cohorts[name]={'words':len(selected),'leaves':len(per),'per_leaf':per}
            for term in ('raw','category','conditional'):
                cohorts[name][term+'_equal_leaf']=math.fsum(r[term] for r in per.values())/len(per)
                cohorts[name][term+'_token']=math.fsum(r[term+'_gain'] for r in selected)/len(selected)
            near(cohorts[name]['raw_equal_leaf'],cohorts[name]['category_equal_leaf']+cohorts[name]['conditional_equal_leaf'])
        out[ed]=cohorts
    return out

def compute():
    models=json.loads((A/'MODEL.json').read_text());old_events=json.loads(gzip.decompress((B/'EVENTS.json.gz').read_bytes()))
    old_result=json.loads((B/'RESULT.json').read_text());fitted={ed:reconstruct(m) for ed,m in models.items()}
    cells={};exact={}
    for ed,(whole,seen,totals,p,h) in fitted.items():
        keys=sorted({(e['c'],len(e['units'])) for e in old_events if e['reader']==ed});cells[ed]=[]
        for cell in keys:
            S=sorted(w for w in seen if len(w)==cell[1]);ps=sum((p(cell,w) for w in S),F(0));pu=1-ps;assert 0<=ps<1
            trained=cell in totals
            hs=sum((h(cell,w) for w in S),F(0)) if trained else None
            assert hs is None or 0<=hs<=1
            hu=1-hs if trained else None;ms=(ps+hs)/2 if trained else ps;mu=1-ms
            row={'cell':list(cell),'train_cell':trained,'seen_types':len(S),'p_seen':float(ps),'p_unseen':float(pu),'h_seen':float(hs) if trained else None,'h_unseen':float(hu) if trained else None,'m_seen':float(ms),'m_unseen':float(mu)}
            cells[ed].append(row);exact[ed,cell]=(ps,pu,hs,hu,ms,mu)
    scores=[];seen_ids=set()
    for e in old_events:
        ed=e['reader'];word=tuple(e['units']);cell=(e['c'],len(word));whole,seen,totals,p,h=fitted[ed]
        assert len(word)>=4 and e['leaf']%2==0 and e['id'] not in seen_ids;seen_ids.add(e['id'])
        match=re.match(re.escape(ed)+r'\|f(\d+)[rv]',e['id']);assert match and int(match.group(1))==e['leaf']
        unseen=word not in seen;assert unseen==e['global_unseen'] and e['cell_train_N']==totals.get(cell,0)
        P=p(cell,word);H=h(cell,word);M=(P+H)/2 if cell in totals else P
        assert P>0 and M>0
        near(math.log(float(P)/e['p']),0);near(float(H),e['h']);near(math.log(float(M)/e['mix_h']),0)
        if H:near(math.log(float(H)/e['h']),0)
        Q=F(whole[cell].get(word,0),totals[cell]) if cell in totals else F(0);oldmix=(P+Q)/2 if cell in totals else P
        near(float(Q),e['q']);near(math.log(float(oldmix)/e['mix']),0)
        ps,pu,hs,hu,ms,mu=exact[ed,cell];pc=pu if unseen else ps;mc=mu if unseen else ms
        assert pc>0 and mc>0
        raw=math.log(M/P);category=math.log(mc/pc);conditional=math.log((M/mc)/(P/pc))
        near(raw,category+conditional);near(raw,e['gain_m1']);near(math.log(M/oldmix),e['gain_whole'])
        scores.append({'id':e['id'],'reader':ed,'leaf':e['leaf'],'cell':list(cell),'unseen':unseen,'raw_gain':raw,'category_gain':category,'conditional_gain':conditional})
    summary=aggregate(scores)
    for ed,cohorts in summary.items():
        for name,r in cohorts.items():
            old=old_result['readers'][ed]['cohorts'][name]
            assert r['words']==old['words'] and r['leaves']==old['leaves']
            near(r['raw_equal_leaf'],old['equal_leaf_gain_m1']);near(r['raw_token'],old['token_gain_m1'])
            for leaf,s in r['per_leaf'].items():near(s['raw'],old['per_leaf_gain_m1'][leaf])
    return cells,scores,summary,exact

def compare(a,b,path=''):
    if isinstance(b,dict):
        assert set(a)==set(b),(path,set(a),set(b))
        for k,v in b.items():compare(a[k],v,path+'/'+str(k))
    elif isinstance(b,list):
        assert len(a)==len(b),(path,len(a),len(b))
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
    elif isinstance(b,float):near(a,b)
    else:assert a==b,(path,a,b)

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    control=fixtures();cells,scores,summary,exact=compute()
    compare(json.loads((D/'artifacts/CELLS.json').read_text()),cells)
    compare(json.loads(gzip.decompress((D/'artifacts/SCORES.json.gz').read_bytes())),scores)
    result=json.loads((D/'artifacts/RESULT.json').read_text());assert result['status']=='FROZEN_NOVELTY_SCORE_ACCOUNTING';compare(result['readers'],summary)
    for clamp in result['clamps']:
        ed=clamp['reader'];cell=tuple(clamp['cell']);before=clamp['h_seen_before'];hs=exact[ed,cell][2]
        assert hs in (F(0),F(1)) and (before<0 or before>1) and abs(before-float(hs))<=1e-12
    report={'status':'PASS','tolerance':TOL,'controls':control,'events':len(scores),'cells':sum(map(len,cells.values())),'clamps_checked':len(result['clamps']),'independence':'FractionM1andHrebuiltfrom1308TRAINwholecounts; MODEL_Handprimarynotimported. Oldp/h/mixvalues, globalUlabels, cellmasses, allscorechainterms/cohortleafweights andoldrawmeansreconstructed.','scope':'Post-result frozenaccounting only; old1316FAILandno-retuningstopunchanged. NegativeUcategoryterm alone doesnotprove poorcalibration; ALLbinaryscore retained.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
