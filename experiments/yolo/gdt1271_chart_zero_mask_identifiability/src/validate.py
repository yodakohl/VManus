import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
ALPHABET='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
SOURCE=list('ABCDEFGHIJKLMNOPQRSTUV #')
def choices(w,p,width):
    nearest={}
    for index,g in enumerate(w):
        distance=(index-p)%len(w)
        if g not in nearest or distance<nearest[g][0]:nearest[g]=(distance,index)
    return [index for distance,index in sorted(nearest.values())[:width]]
def main():
    for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    r=json.loads((P/'artifacts/RESULT.json').read_text());assert r['artificial_only'] is True and r['native_data_read'] is False and r['source_alphabet']==SOURCE
    assert [row['source'] for row in r['records']]==['HEAT OIL#','HEAT GIN#']
    assert r['records'][0]['chart']!=r['records'][1]['chart']
    expected_classes={'zero_zero':[0],'zero_nonzero':[1,2,3],'nonzero_zero':[4,8,12,16,20],'nonzero_nonzero':[v for v in range(24) if v//4 and v%4]};assert r['source_classes']==expected_classes
    all_masks=[];stepcount=0
    for row in r['records']:
        w=row['chart'];assert set(w)==set(ALPHABET) and w[0]==r['initial_label']=='o'
        assert len(w)==row['positions']==r['equal_chart_positions']
        p=0;digits=[];output=[]
        for i,t in enumerate(row['trace']):
            width=4 if i%2 else 6;opts=choices(w,p,width);g=r['cipher'][i]
            matches=[k for k,j in enumerate(opts) if w[j]==g];assert len(matches)==1
            rank=matches[0];dest=opts[rank]
            assert t==dict(step=i,width=width,rank=rank,start=p,destination=dest,label=g)
            if rank:
                assert dest>p and dest-p==rank
                fill=w[p+1:dest];assert len(set(fill))==len(fill) and all(x not in [w[p],g] for x in fill)
            else:assert dest==p
            digits.append(rank);output.append(g);p=dest;stepcount+=1
        assert output==r['cipher'] and digits==row['digits']
        values=[4*digits[j]+digits[j+1] for j in range(0,len(digits),2)];assert values==row['source_values']
        decoded=''.join(SOURCE[v] for v in values);assert decoded==row['source']==row['decoded'] and decoded.count('#')==1 and decoded.endswith('#')
        mask=[int(x==y) for x,y in zip([w[0]]+output,output)];assert mask==[int(d==0) for d in digits]==r['equality_mask'];all_masks.append(mask)
        assert p==row['last_used_constructed_position']
        used=w[:p+1];missing=[g for g in ALPHABET if g not in used]
        assert w[p+1:row['unpadded_positions']]==missing
        assert row['unpadded_positions']==len(used)+len(missing)<=1+sum(digits)+22
        assert all(g=='o' for g in w[row['unpadded_positions']:])
    assert all_masks[0]==all_masks[1] and len(r['cipher'])==18
    assert r['equal_chart_positions']==max(x['unpadded_positions'] for x in r['records'])
    out=dict(status='PASS',distinct_charts=2,same_artificial_cipher=True,different_complete_source_messages=True,steps_checked=stepcount,source_class_sizes=[1,3,5,15],method='independent nearest-occurrence distances, integer inverse, filler and equal-cost verification; no primary imports',native_claim=False)
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
