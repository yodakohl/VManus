"""Independent full original-cache reconstruction of the fixed consequence."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]
def main():
    m=json.loads((HERE/'src/MODEL.json').read_text());s=ROOT/m['source']
    assert hashlib.sha256(s.read_bytes()).hexdigest()==m['source_sha256']
    d=json.loads(s.read_text());res=json.loads((HERE/'artifacts/RESULT.json').read_text())
    assert res['independent_semantic_confirmation_leaves']==0 and res['confirmed_words']==0 and res['meanings_selected'] is False
    for r in m['readers']:
        assert len(d[r])==m['expected_source_paragraphs'][r]
        for p in d[r]:assert not p['page'].startswith('f84')
    expected=[];retained={};chody_counts={r:0 for r in m['readers']}
    for r in m['readers']:
        for p in d[r]:
            words=[];ids=[];loci=[]
            for line in p['lines']:
                words+=line['words'];ids+=line['source_ids'];loci += [line['locus']]*len(line['words'])
            chody_counts[r]+=words.count('chody')
            for start in range(len(words)-1):
                if words[start:start+2]!=['okol','chody']:continue
                i=start+1;follower=words[i+1] if i+1<len(words) else None;leaf=re.match(r'f\d+',p['page']).group()
                expected.append({'reader':r,'page':p['page'],'physical_leaf':leaf,'paragraph_id':p['id'],'locus':loci[i],'source_id':ids[i],'chody_position_1based':i+1,'next_raw':follower,'decision':'MATCHES_FIXED_PRODUCT' if follower in ['okaiin','okoaiin'] else 'CONTRADICTS_FIXED_CONSTRUCTION','partition':'SELECTION' if leaf=='f89' else 'OTHER_LEAF_TRANSFER_EXPOSED'})
                retained[r,p['id']]=p
    assert chody_counts=={'ZL3b':78,'IT2a':82}
    key=lambda x:(x['reader'],x['paragraph_id'],x['chody_position_1based'])
    assert sorted(expected,key=key)==sorted(res['records'],key=key)
    saved=json.loads((HERE/'artifacts/COMPLETE_PARAGRAPHS.json').read_text())
    assert {(x['reader'],x['paragraph']['id']):x['paragraph'] for x in saved}==retained
    errors=sum(x['next_raw'] not in m['accepted_followers'] for x in expected)
    leaves=sorted({x['physical_leaf'] for x in expected if x['partition']!='SELECTION'})
    expected_decision='REJECTED_FIXED_HEADED_CONSTRUCTION' if errors else ('NO_OTHER_LEAF_CAPACITY' if not leaves else 'LITERAL_COMPATIBILITY_NO_MEANING_SELECTION')
    assert errors==res['contradiction_count'] and leaves==res['other_physical_leaves'] and res['decision']==expected_decision
    v={'status':'PASS','coverage':'All1349original complete paragraphs and160chody records reconstructed, all headed frames and full contexts conserved, leaf partition and fixed decision verified. Not semantic truth.','chody_counts':chody_counts,'header_records':len(expected),'semantic_validation':False}
    (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
