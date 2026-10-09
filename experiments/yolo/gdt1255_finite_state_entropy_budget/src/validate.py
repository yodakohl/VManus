import collections,decimal,hashlib,itertools,json,math
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
spec=json.loads((B/'src/SPEC.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text())
old=json.loads((R/spec['inputs'][0]['path']).read_text());prior=json.loads((R/spec['inputs'][1]['path']).read_text())
for i in spec['inputs']:assert hashlib.sha256((R/i['path']).read_bytes()).hexdigest()==i['sha256']
D=decimal.Decimal;decimal.getcontext().prec=50;ln2=D(2).ln()
for c in result['cases']:
    val=D(str(old['candidate_metrics'][c['orientation']]['conditional_entropy']))-D(2).ln()/ln2
    assert abs(val-D(str(c['lower_bound'])))<D('1e-12')
    for reader,margin in c['margins'].items():
        allowed=max(D(str(cell['ranges']['conditional_entropy'][1])) for cell in old['cells'] if cell['reader']==reader and cell['capacity']=='SCOREABLE')+D('.30')
        assert abs((val-allowed)-D(str(margin)))<D('1e-12') and val>allowed
        assert abs(allowed-D(str(prior['native_ceilings'][reader]['largest_allowed_H2'])))<D('1e-12')

def ent(c):
    n=sum(c.values());return math.log2(n)-sum(v*math.log2(v) for v in c.values())/n if n else 0.0

def cond(words):
    joint=collections.Counter();left=collections.Counter()
    for word in words:
        for i in range(1,len(word)):
            joint[(word[i-1],word[i])]+=1;left[word[i-1]]+=1
    return ent(joint)-ent(left)

records=json.loads((B/'artifacts/FIXTURES.json').read_text());seen=set();hsource=cond(spec['fixture_words'])
assert len(records)==9216==result['fixture_cases']
for first,second,tr,start,reset,reported in records:
    key=(tuple(first),tuple(second),tuple(tr),start,reset);assert key not in seen;seen.add(key)
    assert sorted(first)==sorted(second)==[0,1,2] and set(tr)<= {0,1} and len(tr)==6
    state=start;written=[];recovered=[]
    for sourceword in spec['fixture_words']:
        if reset=='word':state=start
        output=[];back=[]
        for x in sourceword:
            row=first if state==0 else second
            y=row[x];recovered_x=row.index(y);back.append(recovered_x);output.append(y)
            state=tr[3*state+recovered_x]
        written.append(output);recovered.append(back)
    assert recovered==spec['fixture_words']
    h=cond(written);assert abs(h-reported)<1e-12 and h+1e-12>=hsource-1
assert len(seen)==6**2*2**6*2*2
# Independently execute sharp state- and boundary-dependent example.
state=0;sharp=[]
for word in [[0,0],[0,1]]:
    sharp.append([x^state for x in word]);state=1-state
assert sharp==[[0,0],[1,0]] and cond(sharp)==0 and cond([[0,0],[0,1]])==1
assert cond([[0,0],[0,0]])==0 # noninjective constant-output countercontrol
lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h,p
out={'status':'PASS','checks':['original source result hashes','Decimal cached-H2 arithmetic','separate native ceiling reconstruction','complete9216finite-machine fixture inventory','independent joint-minus-marginal entropy','fixture inverse','sharp boundary-flip example','noninjective countercontrol','registration hashes'],'scope':'Software and cached arithmetic; analytic proof supplies universal claim. No new paleography or source entropy measurement.'}
(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
