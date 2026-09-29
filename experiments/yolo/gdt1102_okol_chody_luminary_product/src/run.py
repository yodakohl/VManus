"""Execute one frozen exact headed-construction consequence; no decoding."""
import csv,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    model=json.loads((HERE/'src/MODEL.json').read_text())
    lock=json.loads((HERE/'PREREG_LOCK.json').read_text())
    for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
    source=ROOT/model['source'];inventory=ROOT/model['inventory']
    assert sha(source)==model['source_sha256'] and sha(inventory)==model['inventory_sha256']
    data=json.loads(source.read_text());old=json.loads(inventory.read_text())
    # Owned, originally guarded cache: inspect every selector before contents.
    for reader in model['readers']:
        assert len(data[reader])==model['expected_source_paragraphs'][reader]
        for p in data[reader]:assert not p['page'].startswith('f84')
    lookup={(r,p['id']):p for r in model['readers'] for p in data[r]}
    matches=[];contexts={}
    for h in old['hits']:
        if h['immediate_left']!=model['header'][0]:continue
        p=lookup[h['reader'],h['paragraph_id']];seq=[]
        for line in p['lines']:
            assert len(line['words'])==len(line['source_ids'])
            seq.extend((w,sid,line['locus']) for w,sid in zip(line['words'],line['source_ids']))
        i=h['position_1based']-1
        assert [seq[i-1][0],seq[i][0]]==model['header']
        nxt=seq[i+1][0] if i+1<len(seq) else None
        assert nxt==h['immediate_right']
        leaf=re.match(r'(f\d+)',p['page']).group(1)
        record={'reader':h['reader'],'page':p['page'],'physical_leaf':leaf,'paragraph_id':p['id'],'locus':h['locus'],'source_id':h['source_id'],'chody_position_1based':i+1,'next_raw':nxt,'decision':'MATCHES_FIXED_PRODUCT' if nxt in model['accepted_followers'] else 'CONTRADICTS_FIXED_CONSTRUCTION','partition':'SELECTION' if leaf==model['selection_physical_leaf'] else 'OTHER_LEAF_TRANSFER_EXPOSED'}
        matches.append(record);contexts[h['reader'],p['id']]={'reader':h['reader'],'paragraph':p}
    contradictions=[x for x in matches if x['decision'].startswith('CONTRADICTS')]
    leaves=sorted({x['physical_leaf'] for x in matches if x['partition']!='SELECTION'})
    decision='REJECTED_FIXED_HEADED_CONSTRUCTION' if contradictions else ('NO_OTHER_LEAF_CAPACITY' if not leaves else 'LITERAL_COMPATIBILITY_NO_MEANING_SELECTION')
    result={'decision':decision,'records':matches,'reader_counts':{r:sum(x['reader']==r for x in matches) for r in model['readers']},'contradiction_count':len(contradictions),'other_physical_leaves':leaves,'independent_semantic_confirmation_leaves':0,'confirmed_words':0,'significance':False,'meanings_selected':False,'source_sha256':model['source_sha256'],'inventory_sha256':model['inventory_sha256'],'prior_exposure':'All179 selectors historically project-exposed. f89 provided the known seed; other leaves are structural transfer only.','rule':'Every exact consecutive stored okol chody must be followed by unwrapped okaiin or okoaiin in the same complete paragraph.'}
    (HERE/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (HERE/'artifacts/COMPLETE_PARAGRAPHS.json').write_text(json.dumps(list(contexts.values()),ensure_ascii=False,indent=2)+'\n')
    with (HERE/'artifacts/PREDICTIONS.tsv').open('w') as f:
        fields=list(matches[0]) if matches else ['reader','locus','next_raw','decision'];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(matches)
    print(json.dumps({k:result[k] for k in ('decision','reader_counts','contradiction_count','other_physical_leaves')},ensure_ascii=False))
if __name__=='__main__':main()
